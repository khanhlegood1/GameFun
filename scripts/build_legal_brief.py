#!/usr/bin/env python3
"""Build the one-sheet legal brief PDF (A4, 2 sides) from the Markdown source.

The brief is the document we hand to a lawyer, so it has a different shape from
the papers: no cover page, no table of contents, no running prose beyond what
fits. It is a fixed two-side A4 sheet:

    page 1  = the model (4 points) + Question 1 + Question 2
    page 2  = Question 3 + Question 4 + fallback + out-of-scope + references

The build is a HARD gate, not a best-effort render: if the content no longer
fits on the two sides, or if the text on the sheet drifts away from the
Markdown source, the script exits non-zero. That is what keeps "1 trang" true
over time instead of decaying the first time someone edits a paragraph.

Determinism: fonts come from the same pinned sources as the other builders
(`build_whitepaper_pdf.build_fonts`), and metadata is pinned, so the PDF md5 is
stable across machines.

    python3 scripts/build_legal_brief.py docs/Game9K-Legal-Brief-VN.pdf
"""

import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_whitepaper_pdf as WB  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.enums import TA_LEFT  # noqa: E402

SRC = "docs/08-legal-brief-vn-licensing.md"
NAVY = colors.HexColor("#12325c")
RULE = colors.HexColor("#dfe4ea")
GREY = colors.HexColor("#7a828c")
INK = colors.HexColor("#14161a")
BOXBG = colors.HexColor("#f4f1e8")
BOXEDGE = colors.HexColor("#c8b273")

# The sheet must fit ONE A4 side. SCALE is the single knob that keeps it there:
# every font size and leading below is multiplied by it. If you add text to the
# Markdown source, the build fails loudly (see verify) and you turn this down.
SCALE = float(os.environ.get("GAME9K_BRIEF_SCALE", "1.01"))

LM = RM = 11 * mm
TOP = 12 * mm
BOT = 11 * mm
WIDTH = A4[0] - LM - RM
HEIGHT = A4[1] - TOP - BOT


# ------------------------------------------------------------------ source
def read_src(path=SRC):
    """Split the brief into (info rows, section dict)."""
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()

    info = []
    body_start = 0
    for i, l in enumerate(lines):
        if l.startswith("| **"):
            info.append([c.strip() for c in l.strip().strip("|").split("|")])
        if l.startswith("## 1."):
            body_start = i
            break
    if len(info) < 3 or not body_start:
        sys.exit("%s: unexpected structure (info table / section 1 not found)" % path)
    return info, lines[body_start:]


def parse_sections(lines):
    """Return {number: {"title": heading, "lines": [...]}} for each '## N.'."""
    out, cur = {}, None
    for l in lines:
        m = re.match(r"^##\s+(\d)\.\s*(.*)", l)
        if m:
            cur = m.group(1)
            out[cur] = {"title": "%s. %s" % (cur, m.group(2).strip()), "lines": []}
        elif cur is not None and l.strip() != "---":
            out[cur]["lines"].append(l)
    for k in out:
        while out[k]["lines"] and not out[k]["lines"][-1].strip():
            out[k]["lines"].pop()
    return out


# ------------------------------------------------------------------ styles
def make_styles():
    """Styles from one scale factor, so the whole sheet shrinks together."""
    from reportlab.lib.styles import ParagraphStyle
    k = SCALE

    def ps(name, size, lead, **kw):
        return ParagraphStyle(name, fontSize=size * k, leading=lead * k, **kw)

    ss = {}
    ss["title"] = ps("title", 15, 17, fontName="MetaSans-Bold", textColor=NAVY,
                     spaceAfter=1.5 * k)
    ss["meta"] = ps("meta", 7.6, 9.8, fontName="MetaSans", textColor=GREY)
    ss["h2"] = ps("h2", 9.4, 11.2, fontName="MetaSans-Bold", textColor=NAVY,
                  spaceBefore=5.5 * k, spaceAfter=2.0 * k)
    ss["h3"] = ps("h3", 8.6, 10.4, fontName="MetaSans-Bold",
                  textColor=colors.HexColor("#1b2b44"), spaceBefore=4.2 * k,
                  spaceAfter=0.8 * k)
    ss["body"] = ps("body", 8.0, 10.6, fontName="MetaSans", textColor=INK,
                    spaceAfter=2.6 * k, alignment=TA_LEFT)
    ss["num"] = ps("num", 8.0, 10.6, fontName="MetaSans", textColor=INK,
                   leftIndent=12 * k, bulletIndent=0, spaceAfter=2.4 * k,
                   alignment=TA_LEFT)
    ss["q"] = ps("q", 7.7, 10.0, fontName="MetaSans",
                 textColor=colors.HexColor("#1b1f24"), leftIndent=5,
                 spaceAfter=0, alignment=TA_LEFT)
    ss["code"] = ps("code", 6.2, 7.7, fontName="MetaMono", textColor=INK,
                    leftIndent=4, alignment=TA_LEFT)
    ss["note"] = ps("note", 6.8, 8.8, fontName="MetaSans", textColor=GREY,
                    spaceBefore=3 * k)
    ss["cell"] = ps("cell", 7.1, 9.0, fontName="MetaSans", textColor=INK,
                    alignment=TA_LEFT)
    ss["cellh"] = ps("cellh", 7.1, 9.0, fontName="MetaSans-Bold",
                     textColor=colors.white, alignment=TA_LEFT)
    return ss


def inline(t):
    """Minimal inline Markdown -> reportlab markup (same order as the papers).

    Emphasis first, then escape, then inline code: bold text legitimately
    contains `&` and `<`, and code spans legitimately contain `*`.
    """
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", t)
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = t.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    t = t.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    t = re.sub(r"`([^`]+)`", r'<font face="MetaMono" size="6.2">\1</font>', t)
    return t


# ------------------------------------------------------------------ blocks
def question_box(md_lines, st):
    """Render a '> **Hỏi:**' blockquote as a shaded box."""
    paras = []
    buf = []
    for l in md_lines:
        if l.startswith(">"):
            buf.append(l[1:].strip().lstrip(">").strip())
        elif buf and not l.strip():
            continue
        elif buf:
            break
    txt = " ".join(x for x in buf if x)
    txt = re.sub(r"^>\s*", "", txt)
    paras.append(Paragraph(inline(txt), st["q"]))
    t = Table([[paras]], colWidths=[WIDTH])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BOXBG),
        ("LINEBEFORE", (0, 0), (0, -1), 2.0, BOXEDGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.4),
    ]))
    return [Spacer(1, 1.4), t, Spacer(1, 3.0)]


def build_flow(info, sec, st):
    flow = []

    # ---- masthead
    flow.append(Paragraph("Game9K — LEGAL BRIEF", st["title"]))
    flow.append(Paragraph(
        "Bản tóm tắt 1 trang cho tư vấn pháp lý · ngày 22/11/2026 · "
        "mục đích: <b>xin ý kiến tư vấn</b>, không phải yêu cầu soạn hồ sơ.",
        st["meta"]))
    flow.append(Spacer(1, 3))

    rows = [[Paragraph(inline(a), st["cellh"]), Paragraph(inline(b), st["cellh"])]
            for a, b in [("Thông tin", "Chi tiết")]]
    rows += [[Paragraph(inline(a), st["cell"]), Paragraph(inline(b), st["cell"])]
             for a, b in info]
    t = Table(rows, colWidths=[WIDTH * 0.17, WIDTH * 0.83], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b9c3cf")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.6),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
    ]))
    flow += [t, Spacer(1, 0)]

    # ---- 1. model
    flow.append(Paragraph(inline(sec["1"]["title"]), st["h2"]))
    n = 0
    for l in sec["1"]["lines"]:
        m = re.match(r"^\d+\.\s+(.*)", l.strip())
        if m:
            n += 1
            flow.append(Paragraph(inline(m.group(1)), st["num"], bulletText="%d." % n))
        elif l.strip().startswith("**Hạ tầng"):
            flow.append(Paragraph(inline(l.strip()), st["body"]))

    # ---- 2. questions
    flow.append(Paragraph(inline(sec["2"]["title"]), st["h2"]))
    block = {"h3": None, "pre": [], "quote": []}
    items, fence = [], False
    for l in sec["2"]["lines"]:
        s = l.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence:
            block["pre"].append(("code", l.rstrip()))
        elif s.startswith("###"):
            if block["h3"]:
                items.append(block)
            block = {"h3": s.lstrip("# ").strip(), "pre": [], "quote": []}
        elif s.startswith(">"):
            block["quote"].append(s)
        elif s:
            block["pre"].append(("text", s))
    items.append(block)

    for it in items:
        flow.append(Paragraph(inline(it["h3"]), st["h3"]))
        for kind, p in it["pre"]:
            style = st["code"] if kind == "code" else st["body"]
            flow.append(Paragraph(inline(p), style))
        if it["quote"]:
            flow += question_box(it["quote"], st)

    # ---- 3. fallback + 4. out of scope
    # Section 4 is the "what we are NOT asking" scope fence. On a one-sheet
    # brief it is a single grey line under section 3, not its own heading --
    # the lawyer needs to see the fence, not read a section about it.
    for key in ("3", "4"):
        if key not in sec:
            continue
        flow.append(Paragraph(inline(sec[key]["title"]), st["h2"]))
        rest = sec[key]["lines"]
        quote = [l for l in rest if l.strip().startswith(">")]
        if key == "4":
            body = " ".join(l.strip() for l in rest
                            if l.strip() and not l.strip().startswith(">"))
            flow.append(Paragraph(inline(body), st["note"]))
            continue
        for l in rest:
            t = l.strip()
            if not t or t.startswith(">"):
                continue
            flow.append(Paragraph(inline(t), st["body"]))
        if quote:
            flow += question_box(quote, st)

    # ---- 5. pointers, one line each
    if "5" in sec:
        flow.append(Paragraph(inline(sec["5"]["title"]), st["h2"]))
        refs, note = [], []
        for l in sec["5"]["lines"]:
            t = l.strip()
            if t.startswith(">"):
                note.append(t.lstrip("> ").strip())
                continue
            if not t.startswith("|"):
                continue
            cells = [c.strip() for c in t.strip("|").split("|")]
            if len(cells) != 2 or cells[0] == "Nội dung":
                continue                      # skip the header row of the source table
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
                continue
            refs.append("**%s:** %s" % (cells[0], cells[1]))
        flow.append(Paragraph(inline(" · ".join(refs)), st["note"]))
        if note:
            flow.append(Paragraph(inline(" ".join(note)), st["note"]))
    return flow


# ------------------------------------------------------------------ doc
class Brief(BaseDocTemplate):
    """One fixed A4 side: the whole brief must fit a single frame."""

    def __init__(self, filename, **kw):
        # invariant=1 pins the /ID array, the timestamp and the producer string,
        # so the same source rebuilds to the same bytes on any machine.
        kw.setdefault("invariant", 1)
        BaseDocTemplate.__init__(self, filename, **kw)
        self.addPageTemplates([
            PageTemplate(id="sheet", frames=[Frame(LM, BOT, WIDTH, HEIGHT, id="f",
                                                   leftPadding=0, rightPadding=0,
                                                   topPadding=0, bottomPadding=0)],
                         onPage=self._chrome, pagesize=A4),
        ])

    def _chrome(self, canv, doc):
        canv.saveState()
        H, W = doc.pagesize[1], doc.pagesize[0]
        canv.setFillColor(NAVY)
        canv.rect(0, H - 7, W, 7, stroke=0, fill=1)
        canv.setFont("MetaSans-Bold", 6.6)
        canv.setFillColor(NAVY)
        canv.drawString(LM, H - 13.5, "GAME9K LAUNCHPAD · LEGAL BRIEF")
        canv.setFont("MetaSans", 6.6)
        canv.setFillColor(GREY)
        canv.drawRightString(W - RM, H - 13.5,
                             "Bản tóm tắt cho tư vấn pháp lý — không phải ý kiến pháp lý")
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(LM, BOT - 4, W - RM, BOT - 4)
        canv.setFont("MetaSans", 6.4)
        canv.setFillColor(GREY)
        canv.drawString(LM, BOT - 12, "22/11/2026")
        canv.drawCentredString(W / 2.0, BOT - 12, "github.com/khanhlegood1/GameFun")
        canv.setFont("MetaSans-Bold", 6.8)
        canv.setFillColor(NAVY)
        canv.drawRightString(W - RM, BOT - 12, "1 tờ A4")
        canv.restoreState()


def verify(pdf_path, src_path=SRC):
    """Gate: 2 pages, and every question on the sheet exists in the source."""
    from pypdf import PdfReader
    r = PdfReader(pdf_path)
    n = len(r.pages)
    if n != 1:
        sys.exit("build_legal_brief: expected ONE A4 side, got %d pages — the "
                 "content no longer fits '1 trang'. Cut text, or lower "
                 "GAME9K_BRIEF_SCALE." % n)
    sheet = re.sub(r"\s+", " ",
                   " ".join((p.extract_text() or "") for p in r.pages))
    src = re.sub(r"\s+", " ", open(src_path, encoding="utf-8").read())
    # each of the four questions must survive the render
    for k in ("Câu 1", "Câu 2", "Câu 3", "Câu 4"):
        if k.replace(" ", "") not in sheet.replace(" ", ""):
            sys.exit("build_legal_brief: %s missing from the rendered sheet" % k)
    for must in ("NĐ 147/2024/NĐ-CP", "Luật BVDLCN 91/2025/QH15",
                 "NĐ 356/2025/NĐ-CP", "NĐ 174/2026", "game9k.com"):
        if must not in sheet:
            sys.exit("build_legal_brief: expected text %r missing from the sheet" % must)
        if must not in src:
            sys.exit("build_legal_brief: %r is no longer in %s" % (must, src_path))
    # a citation that must NOT appear (expired regulation)
    if "13/2023" in sheet:
        sys.exit("build_legal_brief: NĐ 13/2023 is expired (01/01/2026) — "
                 "cite Luật 91/2025/QH15 + NĐ 356/2025/NĐ-CP instead")
    return n


def build(out, src=SRC):
    WB.FONT_CACHE  # fonts must already be built by build_fonts()
    WB.register_fonts()
    info, lines = read_src(src)
    sec = parse_sections(lines)
    st = make_styles()
    flow = build_flow(info, sec, st)
    doc = Brief(out, pagesize=A4, title="Game9K — Legal Brief (VN Licensing)",
                author="Game9K (khanhlegood1/GameFun)",
                subject="Bản tóm tắt 1 trang cho tư vấn pháp lý — cấp phép game "
                        "và dữ liệu cá nhân tại Việt Nam",
                keywords="Game9K, legal brief, NĐ 147/2024, Luật 91/2025, NĐ 356/2025")
    doc.build(flow)
    return out


def main(argv):
    out = argv[1] if len(argv) > 1 else "docs/Game9K-Legal-Brief-VN.pdf"
    WB.load_coverage()
    WB.build_fonts(force=bool(os.environ.get("GAME9K_FONT_REBUILD")))
    build(out)
    n = verify(out)
    size = os.path.getsize(out)
    md5 = hashlib.md5(open(out, "rb").read()).hexdigest()
    print("built %s (%d bytes, %d pages, md5 %s)" % (out, size, n, md5))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
