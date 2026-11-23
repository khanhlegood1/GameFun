#!/usr/bin/env python3
"""Build the one-sheet "Claims Register" A4 PDF from `pm/claims-registry.json`.

Vì sao có tệp này (docs/34):
    Sổ đăng ký tuyên bố chỉ có giá trị khi nó **được đưa ra** cho người đọc, không
    phải khi nó nằm trong repo. Tờ này là bản in của sổ — đúng một tờ A4, đưa kèm
    whitepaper trong data room.

Ba tính chất, mỗi tính chất là một cổng cứng:

  1. **Sinh từ JSON, không viết tay.** Không có đường nào để tờ giấy nói khác sổ.
     Nếu `pm/claims-registry.json` đổi, tờ này đổi; và CI so md5 để bắt đúng việc đó.
  2. **Đúng một tờ A4.** Tràn trang ⇒ exit non-zero. Nội dung dài thêm thì phải cắt,
     không được để nó thành hai tờ rời (người đọc data room sẽ chỉ đọc tờ đầu).
  3. **Không in được bản đã quá hạn.** Nếu một mục `OPEN` có `review_by` < `as_of`
     thì builder **từ chối dựng**. Một tờ giấy nói "hạn 18/12" mà hôm nay đã 20/12
     là tờ giấy tự bác mình — đúng thứ tệ hơn không có tờ nào.

Determinism: font lấy từ cùng nguồn ghim như các builder khác
(`build_whitepaper_pdf.build_fonts`), metadata ghim, `invariant=1` ⇒ md5 ổn định.

    python3 scripts/build_claims_register.py docs/Game9K-Claims-Register.pdf
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_whitepaper_pdf as WB  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_LEFT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "pm", "claims-registry.json")

NAVY = colors.HexColor("#12325c")
RULE = colors.HexColor("#dfe4ea")
GREY = colors.HexColor("#7a828c")
INK = colors.HexColor("#14161a")
AMBER = colors.HexColor("#f4f1e8")
AMBER_EDGE = colors.HexColor("#c8b273")

LM = RM = 15 * mm
BOT = 13 * mm
WIDTH = A4[0] - LM - RM
HEIGHT = A4[1] - BOT - 17 * mm

# Một núm duy nhất để cả tờ co lại khi nội dung dài thêm.
SCALE = float(os.environ.get("GAME9K_REGISTER_SCALE", "1.0"))


def ss(name, size, lead, **kw):
    return ParagraphStyle(name, fontSize=size * SCALE, leading=lead * SCALE, **kw)


def styles():
    return {
        "title": ss("title", 14.5, 16.5, fontName="MetaSans-Bold", textColor=NAVY,
                    spaceAfter=1.2),
        "sub": ss("sub", 8.2, 10.4, fontName="MetaSans", textColor=GREY, spaceAfter=4),
        "h2": ss("h2", 9.0, 11.0, fontName="MetaSans-Bold", textColor=NAVY,
                 spaceBefore=5 * SCALE, spaceAfter=2 * SCALE),
        "body": ss("body", 7.8, 10.2, fontName="MetaSans", textColor=INK,
                   alignment=TA_LEFT, spaceAfter=2.4 * SCALE),
        "small": ss("small", 6.9, 8.9, fontName="MetaSans", textColor=GREY,
                    alignment=TA_LEFT, spaceAfter=1.6 * SCALE),
        "cell": ss("cell", 6.9, 8.7, fontName="MetaSans", textColor=INK, alignment=TA_LEFT),
        "cellb": ss("cellb", 6.9, 8.7, fontName="MetaSans-Bold", textColor=INK,
                    alignment=TA_LEFT),
        "cellh": ss("cellh", 6.7, 8.4, fontName="MetaSans-Bold", textColor=colors.white,
                    alignment=TA_LEFT),
        "quote": ss("quote", 7.6, 9.9, fontName="MetaSans", textColor=INK,
                    leftIndent=6, alignment=TA_LEFT),
    }


def inline(t):
    """Minimal inline Markdown -> reportlab markup (same order as the papers)."""
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = t.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    t = t.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    return t


def load():
    with open(REGISTRY, encoding="utf-8") as fh:
        reg = json.load(fh)
    person = reg.get("accountable") or {}
    claims = reg.get("claims") or []
    if not person.get("name") or not claims:
        sys.exit("build_claims_register: registry thiếu `accountable.name` hoặc `claims`")
    return reg, person, claims


def refuse_stale(reg, claims):
    """Cổng 3: không in một tờ đã quá hạn."""
    as_of = reg.get("as_of")
    if not as_of:
        sys.exit("build_claims_register: registry thiếu `as_of` — tờ giấy cần một ngày")
    stale = [c for c in claims
             if c.get("status") == "OPEN" and str(c.get("review_by", "")) < as_of]
    if stale:
        sys.exit(
            "build_claims_register: TỪ CHỐI DỰNG — %d mục đã quá hạn so với as_of=%s: %s.\n"
            "Một tờ giấy nói 'hạn 18/12' mà in ngày 20/12 là tờ giấy tự bác mình. "
            "Xử lý mục đó trước (docs/34 §4)."
            % (len(stale), as_of, ", ".join(c.get("id", "?") for c in stale))
        )
    return as_of


def table(claims, st):
    head = ["#", "Câu đang nằm trong tài liệu", "Loại", "Người chịu trách nhiệm",
            "Hạn xem lại", "Nếu quá hạn thì"]
    action = {"rewrite": "dùng câu viết lại", "remove": "gỡ câu khỏi tài liệu",
              "accept": "giữ nguyên và ghi lý do"}
    rows = [[Paragraph(h, st["cellh"]) for h in head]]
    for c in claims:
        rows.append([
            Paragraph(c.get("id", ""), st["cellb"]),
            Paragraph(inline(c.get("quote_short") or c.get("match", "")), st["cell"]),
            Paragraph(c.get("label", ""), st["cell"]),
            Paragraph(inline(c.get("owner_name", "")), st["cellb"]),
            Paragraph(str(c.get("review_by", "")), st["cellb"]),
            Paragraph(action.get(c.get("block_if_unmet"), "—"), st["cell"]),
        ])
    t = Table(rows, colWidths=[8 * mm, 0.38 * WIDTH, 0.185 * WIDTH, 0.135 * WIDTH,
                               0.12 * WIDTH, 0.13 * WIDTH], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f8fa")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
    ]))
    return t


def build_flow(reg, person, claims, st):
    flow = []
    flow.append(Paragraph("GAME9K · CLAIMS REGISTER", st["title"]))
    flow.append(Paragraph(
        "Sổ đăng ký tuyên bố về thế giới — bản in tự động từ "
        "<font face='MetaMono' size='6.4'>pm/claims-registry.json</font> · "
        "ngày lập: <b>%s</b>" % reg.get("as_of", ""), st["sub"]))

    flow.append(Paragraph(
        "Ba câu dưới đây là những câu trong whitepaper mà chúng tôi <b>chưa chứng minh "
        "được</b>. Chúng tôi không gỡ chúng khỏi tài liệu và cũng không viết chúng như "
        "sự thật: chúng tôi ghi tên người chịu trách nhiệm và một ngày cụ thể để câu "
        "trả lời trở nên kiểm được.", st["body"]))
    flow.append(table(claims, st))

    flow.append(Paragraph("Vì sao tờ này tồn tại", st["h2"]))
    flow.append(Paragraph(
        "Một tuyên bố chưa kiểm không nguy hiểm bằng một tuyên bố chưa kiểm <b>không có "
        "người ký</b>. Nhà đầu tư không thiếu trend; họ thiếu lý do để tin một con số. "
        "Tờ này đổi câu hỏi từ <i>“tin chúng tôi đi”</i> sang <i>“kiểm chúng tôi đi”</i>, "
        "và nó chỉ có giá trị vì ba điều: người ký là người thật, hạn là ngày thật, và "
        "hậu quả khi quá hạn được ghi trước.", st["body"]))

    flow.append(Paragraph("Điều tờ này <b>không</b> phải", st["h2"]))
    for line in (
        "<b>Không phải chữ ký pháp lý.</b> Đây là trách nhiệm biên tập nội bộ: ai sửa câu "
        "này, và khi nào. Không phải cam kết về kết quả, không phải đại diện phát ngôn.",
        "<b>Không phải xác nhận rằng câu viết lại sẽ đúng.</b> Câu viết lại cũng là một "
        "đề xuất, và nó được đối xử như vậy.",
        "<b>Không phải danh sách đầy đủ mọi rủi ro.</b> Nó chỉ chứa ba câu mà một cổng tự "
        "động tìm được trong toàn bộ <font face='MetaMono' size='6.4'>docs/</font> và "
        "<font face='MetaMono' size='6.4'>README.md</font>. Rủi ro thị trường, pháp lý "
        "và kỹ thuật nằm ở các tài liệu khác.",
    ):
        flow.append(Paragraph("• " + line, st["small"]))

    flow.append(Spacer(1, 3 * SCALE))
    flow.append(Paragraph(
        "Người chịu trách nhiệm: <b>%s</b> — %s. Căn cứ chỉ định: %s"
        % (person.get("name", ""), person.get("role", ""), person.get("basis", "")),
        st["small"]))
    flow.append(Paragraph(
        "Kiểm tự động: <font face='MetaMono' size='6.4'>scripts/check_claims.py</font> — "
        "mỗi mục phải có nhãn, người có tên, hạn là ngày, và hậu quả khi quá hạn. "
        "Quá hạn thì cổng đỏ. Chi tiết: docs/33, docs/34.", st["small"]))
    return flow


class Sheet(BaseDocTemplate):
    """One fixed A4 side: the whole register must fit a single frame."""

    def __init__(self, filename, **kw):
        kw.setdefault("invariant", 1)
        BaseDocTemplate.__init__(self, filename, **kw)
        self.addPageTemplates([
            PageTemplate(id="sheet", frames=[Frame(LM, BOT, WIDTH, HEIGHT, id="f",
                                                   leftPadding=0, rightPadding=0,
                                                   topPadding=0, bottomPadding=0)],
                         onPage=self._chrome, pagesize=A4),
        ])

    def _chrome(self, canv, doc):
        H, W = doc.pagesize[1], doc.pagesize[0]
        canv.saveState()
        canv.setFillColor(NAVY)
        canv.rect(0, H - 7, W, 7, stroke=0, fill=1)
        canv.setFont("MetaSans-Bold", 6.6)
        canv.setFillColor(NAVY)
        canv.drawString(LM, H - 13.5, "GAME9K LAUNCHPAD · CLAIMS REGISTER")
        canv.setFont("MetaSans", 6.6)
        canv.setFillColor(GREY)
        canv.drawRightString(W - RM, H - 13.5,
                             "Tuyên bố chưa kiểm — có người ký, có hạn")
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(LM, BOT - 4, W - RM, BOT - 4)
        canv.setFont("MetaSans", 6.2)
        canv.setFillColor(GREY)
        canv.drawString(LM, BOT - 8.5,
                        "Tài liệu nội bộ của dự án — không phải ý kiến pháp lý, "
                        "không phải bản chào bán.")
        canv.drawRightString(W - RM, BOT - 8.5, "1/1")
        canv.restoreState()


def build(out):
    reg, person, claims = load()
    refuse_stale(reg, claims)
    WB.register_fonts()
    st = styles()
    doc = Sheet(out, pagesize=A4, title="Game9K — Claims Register",
                author="Game9K (khanhlegood1/GameFun)",
                subject="Ba tuyên bố chưa kiểm chứng — người chịu trách nhiệm và hạn xem lại",
                keywords="Game9K, claims register, docs/33, docs/34")
    doc.build(build_flow(reg, person, claims, st))
    return out


def verify(pdf_path, claims):
    from pypdf import PdfReader
    r = PdfReader(pdf_path)
    if len(r.pages) != 1:
        sys.exit("build_claims_register: expected ONE A4 side, got %d pages — %r no longer "
                 "fits. Cut text, or lower GAME9K_REGISTER_SCALE." % (len(r.pages), pdf_path))
    sheet = " ".join((p.extract_text() or "") for p in r.pages)
    flat = " ".join(sheet.split())
    need = ["CLAIMS REGISTER"]
    for c in claims:
        need.append(str(c.get("review_by")))
        need.append(str(c.get("owner_name")).split()[-1])
    for k in need:
        if k not in flat:
            sys.exit("build_claims_register: %r missing from the rendered sheet" % k)
    # Bất biến: tờ giấy không được chứa một mục nào đã quá hạn so với as_of.
    return len(r.pages)


def main(argv):
    out = argv[1] if len(argv) > 1 else "docs/Game9K-Claims-Register.pdf"
    WB.load_coverage()
    WB.build_fonts(force=bool(os.environ.get("GAME9K_FONT_REBUILD")))
    _, _, claims = load()
    build(out)
    n = verify(out, claims)
    size = os.path.getsize(out)
    md5 = hashlib.md5(open(out, "rb").read()).hexdigest()
    print("built %s (%d bytes, %d pages, md5 %s)" % (out, size, n, md5))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
