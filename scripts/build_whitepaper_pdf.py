#!/usr/bin/env python3
"""Render docs/WHITEPAPER.md to a print-quality PDF (no pandoc / LaTeX / browser).

Why this exists: this repository's whitepaper is the investor-facing artifact,
and it is regenerated whenever a section changes. A browser-less renderer keeps
that reproducible on a bare CI box.

What it produces (see docs/Game9K-Whitepaper-v1.5.pdf):
  * A4, embedded fonts, real selectable/searchable text
  * cover page built from the document-info table (single source of truth)
  * a table of contents with page numbers + a full PDF outline
  * running header/footer with page numbers
  * zebra tables that repeat their header row across page breaks
  * wide tables (>= 7 columns) placed on landscape pages, with the section
    heading moved along so nothing is stranded
  * LaTeX in the markdown is converted to Unicode (sub/superscripts kept as
    real <sub>/<super>), and glyphs the main font lacks fall back per run

Prerequisites
-------------
    python3 -m venv .venv && .venv/bin/pip install reportlab fonttools pypdf
    npm i @fontsource/noto-sans @fontsource/noto-sans-mono   # font sources
    DejaVu fonts (package `fonts-dejavu-core`)

Fonts are merged/derived at run time into a cache directory; nothing binary is
written into the repository except the produced PDF.

Usage
-----
    python3 scripts/build_whitepaper_pdf.py docs/WHITEPAPER.md docs/Game9K-Whitepaper-v1.5.pdf
"""
import html as _html
import os
import re
import sys
import unicodedata

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle, XPreformatted)
from reportlab.platypus.tableofcontents import TableOfContents

# --- font bootstrap -------------------------------------------------------
FONT_CACHE = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
                          "game9k-pdf-fonts")

DEJAVU_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/TTF", "/Library/Fonts"]
NPM_DIRS = ["node_modules/@fontsource", os.path.expanduser("~/.npm/@fontsource")]


def _find(names, dirs):
    for d in dirs:
        for root, _dirs, files in os.walk(d):
            for n in names:
                if n in files:
                    return os.path.join(root, n)
    return None


def ensure_fonts():
    """Build the derived font set this renderer needs; return its directory."""
    marker = os.path.join(FONT_CACHE, "f_sans.ttf")
    if os.path.exists(marker):
        return FONT_CACHE
    os.makedirs(FONT_CACHE, exist_ok=True)
    from fontTools.merge import Merger
    from fontTools.ttLib import TTFont
    from fontTools.ttLib.scaleUpem import scale_upem

    want = {
        "noto-sans-latin-400-normal.woff": "NotoL.ttf",
        "noto-sans-latin-700-normal.woff": "NotoLB.ttf",
        "noto-sans-latin-400-italic.woff": "NotoLI.ttf",
        "noto-sans-latin-700-italic.woff": "NotoLBI.ttf",
        "noto-sans-vietnamese-400-normal.woff": "NotoV.ttf",
        "noto-sans-vietnamese-700-normal.woff": "NotoVB.ttf",
        "noto-sans-vietnamese-400-italic.woff": "NotoVI.ttf",
        "noto-sans-vietnamese-700-italic.woff": "NotoVBI.ttf",
        "noto-sans-mono-latin-400-normal.woff": "ML.ttf",
        "noto-sans-mono-vietnamese-400-normal.woff": "MV.ttf",
        "noto-sans-mono-latin-700-normal.woff": "MLB.ttf",
        "noto-sans-mono-vietnamese-700-normal.woff": "MVB.ttf",
    }
    src_dirs = [d for d in NPM_DIRS if os.path.isdir(d)] + \
               [os.path.join(os.getcwd(), "node_modules/@fontsource")]
    missing = []
    for src_name, dst in want.items():
        p = _find([src_name], src_dirs)
        if not p:
            missing.append(src_name)
            continue
        f = TTFont(p)
        f.flavor = None
        f.save(os.path.join(FONT_CACHE, dst))
    if missing:
        sys.exit("Missing font sources (%s).\nInstall with: npm i @fontsource/noto-sans "
                 "@fontsource/noto-sans-mono" % ", ".join(missing))

    dv_dir = next((d for d in DEJAVU_DIRS if os.path.isdir(d)), None)
    if not dv_dir:
        sys.exit("DejaVu fonts not found. Install `fonts-dejavu-core`.")

    def monoify(src, dst, upem=1000, adv=600):
        f = TTFont(src)
        if f["head"].unitsPerEm != upem:
            scale_upem(f, upem)
        for g in f.getGlyphOrder():
            w, lsb = f["hmtx"][g]
            f["hmtx"][g] = (adv, min(lsb, adv - 1) if lsb > adv else lsb)
        f.save(dst)

    monoify(os.path.join(dv_dir, "DejaVuSansMono.ttf"), os.path.join(FONT_CACHE, "DVMs.ttf"))
    for a, b, out in [("NotoL.ttf", "NotoV.ttf", "f_sans.ttf"),
                      ("NotoLB.ttf", "NotoVB.ttf", "f_sansb.ttf"),
                      ("NotoLI.ttf", "NotoVI.ttf", "f_sansi.ttf"),
                      ("NotoLBI.ttf", "NotoVBI.ttf", "f_sansbi.ttf")]:
        Merger().merge([os.path.join(FONT_CACHE, a), os.path.join(FONT_CACHE, b)]) \
                .save(os.path.join(FONT_CACHE, out))
    for a, b, out in [("ML.ttf", "MV.ttf", "MNB.ttf"), ("MLB.ttf", "MVB.ttf", "MNBb.ttf")]:
        Merger().merge([os.path.join(FONT_CACHE, a), os.path.join(FONT_CACHE, b)]) \
                .save(os.path.join(FONT_CACHE, out))
    for a, out in [("MNB.ttf", "Mono.ttf"), ("MNBb.ttf", "MonoB.ttf")]:
        Merger().merge([os.path.join(FONT_CACHE, a), os.path.join(FONT_CACHE, "DVMs.ttf")]) \
                .save(os.path.join(FONT_CACHE, out))
    import shutil
    for n in ("DejaVuSans.ttf",):
        shutil.copy(os.path.join(dv_dir, n), os.path.join(FONT_CACHE, n))
    return FONT_CACHE


FONTDIR = ensure_fonts()

# Running header text; overwritten per document by build().
BRAND = {"paper": "Whitepaper v1.5",
         "tagline": "Version-Synced Game Capital Launchpad"}

#!/usr/bin/env python3
"""Markdown -> print-quality PDF renderer tuned for the Game9K whitepaper.

No pandoc/LaTeX/Chromium in this sandbox, so this builds the PDF directly with
ReportLab: real text (selectable/searchable), embedded fonts, outline bookmarks,
TOC with page numbers, running header/footer, zebra tables that repeat their
header across page breaks, and landscape pages for wide tables.
"""


# ---------------------------------------------------------------- fonts
def register_fonts():
    pdfmetrics.registerFont(RLTTFont("MetaSans", os.path.join(FONTDIR, "f_sans.ttf")))
    pdfmetrics.registerFont(RLTTFont("MetaSans-Bold", os.path.join(FONTDIR, "f_sansb.ttf")))
    pdfmetrics.registerFont(RLTTFont("MetaSans-It", os.path.join(FONTDIR, "f_sansi.ttf")))
    pdfmetrics.registerFont(RLTTFont("MetaSans-BoldIt", os.path.join(FONTDIR, "f_sansbi.ttf")))
    pdfmetrics.registerFont(RLTTFont("MetaMono", os.path.join(FONTDIR, "Mono.ttf")))
    pdfmetrics.registerFont(RLTTFont("MetaMono-Bold", os.path.join(FONTDIR, "MonoB.ttf")))
    # glyph fallback (box drawing, circled digits, arrows, warning sign)
    pdfmetrics.registerFont(RLTTFont("MetaFallback", os.path.join(FONTDIR, "DejaVuSans.ttf")))
    pdfmetrics.registerFontFamily(
        "MetaSans", normal="MetaSans", bold="MetaSans-Bold",
        italic="MetaSans-It", boldItalic="MetaSans-BoldIt")
    pdfmetrics.registerFontFamily(
        "MetaMono", normal="MetaMono", bold="MetaMono-Bold",
        italic="MetaMono", boldItalic="MetaMono-Bold")


def cmap_of(fontfile):
    from fontTools.ttLib import TTFont
    f = RLTTFont  # placate linters
    t = TTFont(fontfile)
    cov = set()
    for t2 in t["cmap"].tables:
        cov |= set(t2.cmap)
    return cov


COVER = {}
def load_coverage():
    COVER["sans"] = cmap_of(os.path.join(FONTDIR, "f_sans.ttf"))
    COVER["sansb"] = cmap_of(os.path.join(FONTDIR, "f_sansb.ttf"))
    COVER["mono"] = cmap_of(os.path.join(FONTDIR, "Mono.ttf"))

# ---------------------------------------------------------------- math
GREEK = {
    "alpha":"α","beta":"β","gamma":"γ","delta":"δ","epsilon":"ε","varepsilon":"ε",
    "zeta":"ζ","eta":"η","theta":"θ","vartheta":"ϑ","iota":"ι","kappa":"κ","lambda":"λ",
    "mu":"μ","nu":"ν","xi":"ξ","pi":"π","rho":"ρ","varrho":"ϱ","sigma":"σ","tau":"τ",
    "upsilon":"υ","phi":"φ","varphi":"φ","chi":"χ","psi":"ψ","omega":"ω",
    "Gamma":"Γ","Delta":"Δ","Theta":"Θ","Lambda":"Λ","Xi":"Ξ","Pi":"Π","Sigma":"Σ",
    "Upsilon":"Υ","Phi":"Φ","Psi":"Ψ","Omega":"Ω",
}
SYMBOLS = {
    "le":"≤","leq":"≤","ge":"≥","geq":"≥","ne":"≠","neq":"≠","approx":"≈","equiv":"≡",
    "times":"×","cdot":"·","div":"÷","pm":"±","mp":"∓","infty":"∞","partial":"∂",
    "sum":"Σ","prod":"∏","int":"∫","in":"∈","notin":"∉","subset":"⊂","subseteq":"⊆",
    "cup":"∪","cap":"∩","emptyset":"∅","forall":"∀","exists":"∃","neg":"¬",
    "land":"∧","wedge":"∧","lor":"∨","vee":"∨","to":"→","rightarrow":"→",
    "Rightarrow":"⇒","implies":"⟹","Leftrightarrow":"⇔","mapsto":"↦","uparrow":"↑",
    "succ":"≻","prec":"≺","succeq":"≽","preceq":"≼","sim":"∼","propto":"∝",
    "ldots":"…","dots":"…","cdots":"⋯","circ":"∘","ast":"∗","star":"⋆",
    "lfloor":"⌊","rfloor":"⌋","lceil":"⌈","rceil":"⌉","langle":"⟨","rangle":"⟩",
    "mid":"|","vert":"|","Vert":"‖","%":"%","#":"#","&":"&","_":"_","{":"{","}":"}",
    "prime":"′","degree":"°","surd":"√","checkmark":"✓","dagger":"†","S":"§",
}
BBOARD = {"R":"ℝ","N":"ℕ","Z":"ℤ","Q":"ℚ","C":"ℂ","E":"𝔼","P":"ℙ","1":"𝟙"}
TEXTCMD = {"text","mathrm","mathbf","mathit","mathsf","mathtt","operatorname",
           "textrm","textbf","mbox","textnormal"}
SKIPCMD = {"left","right","big","Big","bigl","bigr","Bigl","Bigr","displaystyle",
           "limits","nolimits","quad","qquad","!",";"," ",",",":","\\"}

SUB, SUBE, SUP, SUPE = "\x01", "\x02", "\x03", "\x04"
CHR_DOLLAR = "\ue000"      # private-use slot so "$" is never eaten by glyph_fix
ACCENTS = {"tilde":"\u0303","hat":"\u0302","bar":"\u0304","overline":"\u0304",
           "vec":"\u20d7","dot":"\u0307","ddot":"\u0308","widehat":"\u0302"}


def _text_arg(s, i):
    """Return (content, new_index) for a braced argument starting near i."""
    while i < len(s) and s[i] in " \t":
        i += 1
    if i < len(s) and s[i] == "{":
        depth = 0
        j = i
        while j < len(s):
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0:
                    return s[i+1:j], j+1
            j += 1
        return s[i+1:], len(s)
    if i < len(s) and s[i] == "\\":
        m = re.match(r"\\([A-Za-z]+)", s[i:])
        if m:
            return m.group(1), i + m.end()
        return s[i+1], i + 2
    return (s[i] if i < len(s) else ""), i + 1


def latex_to_text(src):
    """Best-effort LaTeX -> Unicode with <sub>/<super> sentinels."""
    s = src
    # The .md files escape every backslash, so math arrives as `\\text{...}`.
    # Collapse that to a single backslash before macro parsing (otherwise every
    # command is destroyed and subscripts swallow the macro name).
    s = s.replace("\\\\", "\\")
    s = s.replace("\\{", "\x05").replace("\\}", "\x06")
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if m:
                name = m.group(1)
                i += m.end()
                if name in ("text","mathrm","textrm","operatorname","mbox"):
                    arg, i = _text_arg(s, i)
                    out.append(latex_to_text(arg))
                elif name in TEXTCMD:
                    arg, i = _text_arg(s, i)
                    out.append(latex_to_text(arg))
                elif name in ACCENTS:
                    arg, i = _text_arg(s, i)
                    base = latex_to_text(arg)
                    acc = ACCENTS[name]
                    if len(base) > 1 and base[-1] in (SUB, SUP):
                        out.append(base)     # accent would detach: skip
                    else:
                        out.append((base[:1] + acc + base[1:]) if base else "")
                elif name == "mathbb":
                    arg, i = _text_arg(s, i)
                    out.append("".join(BBOARD.get(ch, ch) for ch in arg))
                elif name == "frac":
                    num, i = _text_arg(s, i)
                    den, i = _text_arg(s, i)
                    out.append("(%s)/(%s)" % (latex_to_text(num), latex_to_text(den)))
                elif name == "sqrt":
                    arg, i = _text_arg(s, i)
                    out.append("√(%s)" % latex_to_text(arg))
                elif name in ("ell",):
                    out.append("ℓ")
                elif name in GREEK:
                    out.append(GREEK[name])
                elif name in SYMBOLS:
                    out.append(SYMBOLS[name])
                elif name in SKIPCMD:
                    if name == "quad":
                        out.append("\u2003")
                    elif name == "qquad":
                        out.append("\u2003\u2003")
                    elif name == ",":
                        out.append("\u2009")
                    elif name == ";":
                        out.append("\u2005")
                else:
                    out.append(name)          # unknown macro: print its name
            else:
                i += 1
                nxt = s[i] if i < len(s) else ""
                if nxt == "\\":
                    out.append("\n")
                    i += 1
                elif nxt in ("{", "}", "%", "#", "&", "_", "$"):
                    out.append({"{":"{","}":"}","%":"%","#":"#","&":"&",
                                "_":"_","$":"$"}[nxt])
                    i += 1
                elif nxt in (",", ";", ":", "!", " "):
                    out.append("\u2009")
                    i += 1
                elif nxt in "[]":
                    i += 1
        elif c in "_^":
            tag_open, tag_close = (SUB, SUBE) if c == "_" else (SUP, SUPE)
            i += 1
            if i < len(s) and s[i] == "{":
                arg, i = _text_arg(s, i)
                inner = latex_to_text(arg)
            else:
                inner = latex_to_text(s[i] if i < len(s) else "")
                i += 1
            out.append(tag_open + inner + tag_close)
        elif c in "{}":
            i += 1
        elif c == "&":
            i += 1
            if i < len(s) and s[i] == "&":
                i += 1
        else:
            out.append(c)
            i += 1
    res = "".join(out)
    res = res.replace("\x00", "\n").replace("\x05", "{").replace("\x06", "}")
    res = re.sub(r"[ \t]{2,}", " ", res).strip()
    return res


def strip_math(text):
    """Replace $...$ spans with Unicode, keep everything else."""
    def repl(m):
        inner = m.group(1)
        inner = inner.strip()
        return latex_to_text(inner)
    text = re.sub(r"\$\$(.+?)\$\$", repl, text, flags=re.S)
    text = re.sub(r"\$([^$\n]+?)\$", repl, text)
    return text

# ---------------------------------------------------------------- inline
TOKEN = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*|\*[^*\s][^*]*\*|\[[^\]]+\]\([^)]+\))")

def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def glyph_fix(t, mono=False):
    """Wrap runs the current font cannot draw in the fallback font (and back)."""
    cov = COVER["mono" if mono else "sans"]
    out, buf, in_fb = [], [], False
    for ch in t:
        need = ((ord(ch) not in cov) and (not ch.isspace())
                and ord(ch) != 0xE000)   # 0xE000 is the masked "$"
        if need != in_fb:
            if buf:
                body = "".join(buf)
                out.append(('<font name="MetaFallback">%s</font>' % body)
                           if in_fb else body)
            buf, in_fb = [], need
        buf.append(ch)
    if buf:
        body = "".join(buf)
        out.append(('<font name="MetaFallback">%s</font>' % body)
                   if in_fb else body)
    return "".join(out)


def _emph(t, B="\x10b", EB="\x10B", I="\x10i", EI="\x10I"):
    """Asterisk emphasis via a nesting state machine.

    The naive regex version breaks on `**bold with *italic* inside***` (it closes
    bold on the wrong pair of stars). Runs of stars are toggled with proper
    nesting, and a run only counts as an opener/closer when it hugs non-space
    text - so prose like "x * y = k" stays literal.
    """
    out, i = [], 0
    state = {"b": False, "i": False}
    n = len(t)
    hits = list(re.finditer(r"\*+", t))
    for m in hits:
        out.append(glyph_fix(esc(t[i:m.start()])))
        i = m.end()
        run = len(m.group(0))
        nxt = t[m.end()] if m.end() < n else ""
        prev = t[m.start() - 1] if m.start() > 0 else ""
        # \x0b/\x0c hold placeholders for code/math spans: \x0c.ispace() is True,
        # which would make a closing ** look like a literal run.
        nxt_sp = (not nxt) or (nxt.isspace() and nxt not in "\x0b\x0c")
        prev_sp = (not prev) or (prev.isspace() and prev not in "\x0b\x0c")
        targets = (["b"] if run >= 2 else []) + (["i"] if run % 2 == 1 else [])
        closing = [st for st in reversed(targets) if state[st]]
        opening = [st for st in targets if not state[st]]
        if opening and nxt_sp:
            out.append("*" * run)
            continue
        if closing and prev_sp:
            out.append("*" * run)
            continue
        for st in closing:
            out.append(EI if st == "i" else EB)
            state[st] = False
        for st in opening:
            out.append(I if st == "i" else B)
            state[st] = True
    out.append(glyph_fix(esc(t[i:])))
    for st in ("i", "b"):
        if state[st]:
            out.append(EI if st == "i" else EB)
    return "".join(out)


def _unwrap(item):
    kind, payload = item
    if kind == "code":
        return "`%s`" % payload
    if kind == "math":
        return "$%s$" % payload
    label, url = payload
    return "%s" % label


def inline(md, color_links=True):
    """Markdown inline -> ReportLab intra-paragraph markup.

    Placeholders protect code/math/link spans first, then emphasis runs on the
    remaining text, then each placeholder is rendered with the right font. A
    single html-escape pass keeps every literal `<`/`>` safe.
    """
    md = md.replace("<br>", "\x08").replace("<br/>", "\x08").replace("<br />", "\x08")
    md = _html.unescape(md)
    md = md.replace("\\\"", '"').replace("\\'", "'")
    md = md.replace("\ufe0f", "").replace("\ufe0e", "")

    store = []

    def keep(kind, payload):
        store.append((kind, payload))
        return "\x0b%d\x0c" % (len(store) - 1)

    md = re.sub(r"`([^`]+)`", lambda m: keep("code", m.group(1)), md)
    md = re.sub(r"\$\$(.+?)\$\$", lambda m: keep("math", m.group(1)), md, flags=re.S)

    # Inline math vs. currency: this document is full of "$1.0M" and
    # "*($25M @ $250M)*", so a "$...$" pair is only math when the span actually
    # carries LaTeX (a macro, a sub/superscript or a brace group).
    def _math_or_cash(m):
        inner = m.group(1)
        if re.search(r"[\\_^{}]", inner) and not re.match(r"^[\d\s.,\u2192\u2013\u2014\-/+%xX]+$", inner):
            return keep("math", inner)
        return CHR_DOLLAR + inner + CHR_DOLLAR

    md = re.sub(r"\$([^$\n]+?)\$", _math_or_cash, md)
    md = md.replace("$", CHR_DOLLAR)          # leftover dollars are currency too
    md = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                lambda m: keep("link", (m.group(1), m.group(2))), md)

    md = _emph(md)

    def restore(m):
        kind, payload = store[int(m.group(1))]
        if kind == "code":
            return '<font name="MetaMono" size="7.5">%s</font>' % glyph_fix(
                esc(str(payload)), mono=True)
        if kind == "math":
            t = esc(latex_to_text(payload))
            t = (t.replace(SUB, "<sub>").replace(SUBE, "</sub>")
                  .replace(SUP, "<super>").replace(SUPE, "</super>"))
            return glyph_fix(t)
        label, url = payload
        # placeholders captured inside the label are already-stored spans; unwrap
        # them back to source text before re-parsing the label
        label = re.sub("\x0b(\\d+)\x0c",
                       lambda mm: _unwrap(store[int(mm.group(1))]), label)
        if "`" in label or "*" in label:
            lab = inline(label, color_links=False)   # bold/code inside the label
        else:
            lab = glyph_fix(esc(label))
        # In-document anchors (#...) and relative .md links are not renderable
        # here: keep the label, drop the (dead) link so ReportLab cannot fail.
        if color_links and re.match(r"^(https?:|mailto:)", url):
            return '<link href="%s" color="#1a4b8c">%s</link>' % (esc(url), lab)
        if color_links and re.match(r"^\.\.?/", url) and not url.startswith("./"):
            return '<link href="%s" color="#1a4b8c">%s</link>' % (esc(url), lab)
        return lab

    while "\x0b" in md and "\x0c" in md:
        new_md = re.sub("\x0b(\\d+)\x0c", restore, md)
        if new_md == md:
            break
        md = new_md
    md = (md.replace("\x10b", "<b>").replace("\x10B", "</b>")
            .replace("\x10i", "<i>").replace("\x10I", "</i>"))
    md = md.replace("\x08", "<br/>")
    md = (md.replace(SUB, "<sub>").replace(SUBE, "</sub>")
            .replace(SUP, "<super>").replace(SUPE, "</super>"))
    md = md.replace(CHR_DOLLAR, "$")
    return balance_tags(md)


TAG_RE = re.compile(r"<(/)?([A-Za-z][A-Za-z0-9]*)((?:\s[^>]*)?)(/)?>")


def balance_tags(t):
    """Guarantee well-formed nesting for ReportLab.

    Source prose such as `*(a = **16.8x**)* ... (*b* = **7.7x**)` is genuinely
    ambiguous, so instead of guessing we walk the emitted tag stream: a closer
    that is not on top of the stack closes the tags above it and reopens them
    afterwards (visually equivalent, always valid).
    """
    out, stack = [], []
    pos = 0
    for m in TAG_RE.finditer(t):
        out.append(t[pos:m.start()])
        pos = m.end()
        closing, name, attrs, selfclose = m.group(1), m.group(2), m.group(3) or "", m.group(4)
        if name.lower() == "br" or selfclose:
            out.append(m.group(0))
            continue
        if not closing:
            stack.append(name)
            out.append(m.group(0))
            continue
        if name in stack:
            reopen = []
            while stack and stack[-1] != name:
                top = stack.pop()
                out.append("</%s>" % top)
                reopen.append(top)
            if stack:
                stack.pop()
            out.append("</%s>" % name)
            for top in reversed(reopen):
                stack.append(top)
                out.append("<%s>" % top)
        # stray closer: drop it
    out.append(t[pos:])
    while stack:
        out.append("</%s>" % stack.pop())
    return "".join(out)


def finish(t):
    """Apply glyph fallback with font context (mono spans keep their metrics)."""
    out = []
    for chunk in re.split(r"(<[^>]+>)", t):
        if not chunk:
            continue
        if chunk.startswith("<"):
            out.append(chunk)
            continue
        mono = False
        for m in re.finditer(r'<font name="([^"]+)"', t[:1]):
            pass
        out.append(glyph_fix(chunk, mono=mono))
    return "".join(out)


# ---------------------------------------------------------------- styles
def build_styles():
    ss = {}
    base = ParagraphStyle("body", fontName="MetaSans", fontSize=9.3, leading=14.4,
                          alignment=TA_JUSTIFY, spaceAfter=5.2, textColor=colors.HexColor("#14161a"))
    ss["body"] = base
    ss["h1"] = ParagraphStyle("h1", parent=base, fontName="MetaSans-Bold", fontSize=19,
                              leading=23, alignment=TA_LEFT, spaceBefore=2, spaceAfter=9,
                              textColor=colors.HexColor("#0d1b2a"))
    ss["h2"] = ParagraphStyle("h2", parent=base, fontName="MetaSans-Bold", fontSize=14.2,
                              leading=18, alignment=TA_LEFT, spaceBefore=13, spaceAfter=6,
                              textColor=colors.HexColor("#12325c"))
    ss["h3"] = ParagraphStyle("h3", parent=base, fontName="MetaSans-Bold", fontSize=11.1,
                              leading=14.4, alignment=TA_LEFT, spaceBefore=10, spaceAfter=4,
                              textColor=colors.HexColor("#1a4b8c"))
    ss["h4"] = ParagraphStyle("h4", parent=base, fontName="MetaSans-Bold", fontSize=9.8,
                              leading=12.8, alignment=TA_LEFT, spaceBefore=8, spaceAfter=3,
                              textColor=colors.HexColor("#0f6b52"))
    for k in ("h1", "h2", "h3", "h4"):
        ss[k].keepWithNext = 1
    ss["cell"] = ParagraphStyle("cell", parent=base, fontSize=7.5, leading=10.2,
                                alignment=TA_LEFT, spaceAfter=0, spaceBefore=0)
    ss["cellh"] = ParagraphStyle("cellh", parent=ss["cell"], fontName="MetaSans-Bold",
                                 textColor=colors.white, fontSize=7.7)
    ss["quote"] = ParagraphStyle("quote", parent=base, fontName="MetaSans-It", fontSize=8.9,
                                 leading=14.0, leftIndent=0, alignment=TA_LEFT,
                                 textColor=colors.HexColor("#2b3138"))
    ss["bullet"] = ParagraphStyle("bullet", parent=base, leftIndent=13, bulletIndent=3,
                                  spaceAfter=3.4, alignment=TA_LEFT)
    ss["bullet2"] = ParagraphStyle("bullet2", parent=ss["bullet"], leftIndent=27,
                                   bulletIndent=17, fontSize=8.9)
    ss["code"] = ParagraphStyle("code", fontName="MetaMono", fontSize=6.2, leading=7.7,
                                textColor=colors.HexColor("#1b1f24"), alignment=TA_LEFT)
    return ss


# ---------------------------------------------------------------- doc
class Doc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        kw.setdefault("invariant", 1)
        BaseDocTemplate.__init__(self, filename, **kw)
        self.headings = []
        self.wide_stack = []
        self._toc_seen = 0
        fw, fh = A4
        lm = rm = 42
        self.addPageTemplates([
            PageTemplate(id="portrait", frames=[
                Frame(lm, 46, fw - lm - rm, fh - 46 - 48, id="p")],
                onPage=self._deco_portrait, pagesize=A4),
            PageTemplate(id="land", frames=[
                Frame(34, 44, landscape(A4)[0] - 68, landscape(A4)[1] - 44 - 46, id="l")],
                onPage=self._deco_land, pagesize=landscape(A4)),
        ])

    # -- chrome
    def _chrome(self, canv, doc, width, height, seed_left, seed_right):
        canv.saveState()
        # header
        canv.setStrokeColor(colors.HexColor("#dfe4ea"))
        canv.setLineWidth(0.5)
        canv.line(42, height - 34, width - 42, height - 34)
        canv.setFont("MetaSans-Bold", 6.8)
        canv.setFillColor(colors.HexColor("#12325c"))
        canv.drawString(42, height - 28, "GAME9K FUNDING PORTAL")
        canv.setFont("MetaSans", 6.8)
        canv.setFillColor(colors.HexColor("#7a828c"))
        canv.drawString(42 + pdfmetrics.stringWidth("GAME9K FUNDING PORTAL", "MetaSans-Bold", 6.8) + 6,
                        height - 28, seed_left)
        canv.drawRightString(width - 42, height - 28, seed_right)
        # footer
        canv.setLineWidth(0.5)
        canv.line(42, 38, width - 42, 38)
        canv.setFont("MetaSans", 6.8)
        canv.setFillColor(colors.HexColor("#7a828c"))
        canv.drawString(42, 27, "github.com/khanhlegood1/GameFun")
        canv.setFont("MetaSans-Bold", 7.6)
        canv.setFillColor(colors.HexColor("#12325c"))
        canv.drawCentredString(width / 2.0, 26.5, "%d" % doc.page)
        canv.restoreState()

    def _deco_portrait(self, canv, doc):
        self._chrome(canv, doc, A4[0], A4[1], BRAND["paper"], BRAND["tagline"])

    def _deco_land(self, canv, doc):
        W, H = landscape(A4)
        self._chrome(canv, doc, W, H, BRAND["paper"], BRAND["tagline"])

    # -- outline + TOC
    def notify(self, kind, stuff):
        if kind == "TOCEntry":
            self._toc_seen += 1
        BaseDocTemplate.notify(self, kind, stuff)

    def afterFlowable(self, flowable):
        # Only report TOC entries on the final pass, and only for content pages
        # (the TOC page itself must not feed itself -> would never converge).
        if getattr(self, "_freeze", False):
            return
        if isinstance(flowable, Paragraph) and flowable.style.name in ("h1", "h2", "h3"):
            txt = re.sub(r"<[^>]+>", "", flowable.getPlainText())
            txt = re.sub(r"\s+", " ", txt).strip()
            lvl = {"h1": 0, "h2": 0, "h3": 1}[flowable.style.name]
            key = "h%d_%d" % (lvl, len(self.headings))
            self.headings.append((lvl, txt, self.page, key))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(txt, key, level=min(lvl, 1), closed=lvl > 0)
            if lvl <= 1:
                self.notify("TOCEntry", (lvl, txt, self.page, key))


class NumberedCanvas(rl_canvas.Canvas):
    def __init__(self, *a, **kw):
        rl_canvas.Canvas.__init__(self, *a, **kw)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self._stamp(total)
            rl_canvas.Canvas.showPage(self)
        rl_canvas.Canvas.save(self)

    def _stamp(self, total):
        pass   # page number already drawn as "trang N"; total added below


# ---------------------------------------------------------------- blocks
SEP_RE = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$")


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    cells, buf, i = [], [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line) and line[i+1] == "|":
            buf.append("|")
            i += 2
        elif c == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
        else:
            buf.append(c)
            i += 1
    cells.append("".join(buf).strip())
    return cells


def col_widths(rows, avail, fs=7.5):
    """Weighted widths: cap each column, never break a word if avoidable."""
    ncol = max(len(r) for r in rows)
    pad = 7.2
    nat, hard = [0.0] * ncol, [12.0] * ncol
    for r in rows:
        for j, c in enumerate(r):
            plain = re.sub(r"<[^>]+>", "", inline(c))
            plain = re.sub(r"[\x00-\x08]", " ", plain)
            nat[j] = max(nat[j], pdfmetrics.stringWidth(plain, "MetaSans", fs) + pad)
            for word in re.split(r"\s+", plain):
                if word:
                    hard[j] = max(hard[j], pdfmetrics.stringWidth(word, "MetaSans", fs) + pad)
    if sum(nat) <= avail:
        extra = avail - sum(nat)
        return [n + extra * n / sum(nat) for n in nat]
    cap = max(avail * 0.34, max(hard))
    w = [min(n, cap) for n in nat]
    # make room for unbreakable words first
    deficit = sum(w) - avail
    if deficit > 0:
        flex = [i for i in range(ncol) if w[i] > hard[i]]
        while deficit > 0.5 and flex:
            share = deficit / len(flex)
            for i in list(flex):
                room = w[i] - hard[i]
                take = min(room, share)
                w[i] -= take
                deficit -= take
                if w[i] - hard[i] < 0.6:
                    flex.remove(i)
            if not flex:
                break
    if sum(w) > avail:                      # last resort: proportional shave
        k = avail / sum(w)
        w = [x * k for x in w]
    return w


def make_table(rows, st, avail, widths=None):
    ncol = max(len(r) for r in rows)
    norm = []
    for r in rows:
        r = list(r) + [""] * (ncol - len(r))
        norm.append(r)
    head = [Paragraph(inline(c), st["cellh"]) for c in norm[0]]
    body = [[Paragraph(inline(c), st["cell"]) for c in r] for r in norm[1:]]
    data = [head] + body
    widths = widths or col_widths(norm, avail)
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12325c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.6),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b9c3cf")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.HexColor("#12325c")),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#eef2f7")))
    t.setStyle(TableStyle(style))
    return t


def parse(md_lines, st, avail):
    story = []
    i, n = 0, len(md_lines)
    para_buf = []

    def flush_para():
        nonlocal para_buf
        if para_buf:
            text = " ".join(x.strip() for x in para_buf).strip()
            if text:
                story.append(Paragraph(inline(text), st["body"]))
            para_buf = []

    while i < n:
        raw = md_lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para()
            i += 1
            continue

        # fenced code
        if stripped.startswith("```"):
            flush_para()
            i += 1
            buf = []
            while i < n and not md_lines[i].strip().startswith("```"):
                buf.append(md_lines[i].rstrip("\n"))
                i += 1
            i += 1
            # long single-line pseudo-diagrams must not run off the page
            wrapped = []
            for ln in buf:
                limit = 118
                while len(ln) > limit:
                    cut = ln.rfind(" ", 0, limit)
                    if cut <= 40:
                        cut = limit
                    wrapped.append(ln[:cut])
                    ln = "  " + ln[cut:].lstrip()
                wrapped.append(ln)
            buf = wrapped
            txt = "\n".join(buf).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            txt = txt.replace("\ufe0f", "")
            box = Table([[XPreformatted(glyph_fix(txt, mono=True), st["code"])]],
                        colWidths=[avail], hAlign="LEFT")
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f6f9")),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d2dc")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(Spacer(1, 3))
            story.append(box)
            story.append(Spacer(1, 6))
            continue

        # horizontal rule
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            flush_para()
            hr = Table([[""]], colWidths=[avail], rowHeights=[2])
            hr.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.6,
                                     colors.HexColor("#c2cad4"))]))
            story.append(Spacer(1, 4))
            story.append(hr)
            story.append(Spacer(1, 6))
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_para()
            lvl = len(m.group(1))
            txt = m.group(2).strip()
            txt = re.sub(r"\s*\{#[^}]*\}\s*$", "", txt)
            key = {1: "h1", 2: "h2", 3: "h3"}.get(lvl, "h4")
            if key == "h1" and story and any(isinstance(f, Paragraph) for f in story[-4:]):
                story.append(PageBreak())
            story.append(Paragraph(inline(txt), st[key]))
            i += 1
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and SEP_RE.match(md_lines[i+1].strip()):
            flush_para()
            rows = [split_row(stripped)]
            i += 2
            while i < n and md_lines[i].strip().startswith("|"):
                rows.append(split_row(md_lines[i].strip()))
                i += 1
            ncol = max(len(r) for r in rows)
            story.append(Spacer(1, 2))
            if ncol >= 7:
                story.append(LandStart())
                story.append(make_table(rows, st, landscape(A4)[0] - 68))
                story.append(LandEnd())
            else:
                story.append(make_table(rows, st, avail))
            story.append(Spacer(1, 7))
            continue

        # blockquote
        if stripped.startswith(">"):
            flush_para()
            buf = []
            while i < n and md_lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", md_lines[i]).rstrip())
                i += 1
            body = " ".join(x.strip() for x in buf if x.strip())
            body = re.sub(r"\s{2,}", " ", body)
            inner = [Paragraph(inline(x.strip().lstrip("> ")), st["quote"])
                     for x in body.split("\x07") if x.strip()]
            if not inner:
                inner = [Paragraph(inline(body), st["quote"])]
            box = Table([[inner]], colWidths=[avail], hAlign="LEFT")
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7f4ec")),
                ("LINEBEFORE", (0, 0), (0, -1), 2.4, colors.HexColor("#c8a04a")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(Spacer(1, 2))
            story.append(box)
            story.append(Spacer(1, 7))
            continue

        # lists
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", raw)
        if m:
            flush_para()
            indent = len(m.group(1).replace("\t", "  "))
            ordered = m.group(2)[0].isdigit()
            lvl = 2 if indent >= 2 else 1
            style = st["bullet2"] if lvl == 2 else st["bullet"]
            num = m.group(2) if ordered else "•"
            body = m.group(3).strip()
            i += 1
            # continuation lines (indented, not a new bullet)
            while i < n:
                nxt = md_lines[i]
                if not nxt.strip():
                    break
                if re.match(r"^(\s*)([-*+]|\d+[.)])\s+", nxt):
                    break
                if nxt.startswith("  ") and not nxt.strip().startswith("|"):
                    body += " " + nxt.strip()
                    i += 1
                else:
                    break
            p = Paragraph(inline(body), style, bulletText=num)
            story.append(p)
            continue

        # plain paragraph text
        para_buf.append(line)
        i += 1

    flush_para()
    return story


def expand_landscape(story):
    """Turn landscape sentinels into real page-template switches.

    Wide tables need landscape, but a table must never start a page without its
    heading, and a heading must never be stranded at the bottom of a portrait
    page. So when a LandStart is met the builder looks *back* at what it has
    already emitted: the heading of that section plus everything after it moves
    onto the landscape page, leaving the previous portrait page ending cleanly
    on the preceding section. NextPageTemplate applies to the page that is
    started next, so the existing break is reused rather than doubled.
    """

    def is_heading(f):
        return isinstance(f, Paragraph) and f.style.name in ("h1", "h2", "h3", "h4")

    out, ends_with_break = [], False
    for f in story:
        if isinstance(f, LandStart):
            while out and isinstance(out[-1], Spacer):
                out.pop()
            cut = len(out)
            while cut > 0:
                cut -= 1
                if is_heading(out[cut]) and out[cut].style.name in ("h2", "h3"):
                    break
            else:
                cut = len(out)
            carry = out[cut:]
            del out[cut:]
            while carry and isinstance(carry[0], Spacer):
                carry.pop(0)
            while out and isinstance(out[-1], Spacer):
                out.pop()
            if ends_with_break and out and isinstance(out[-1], PageBreak):
                out.pop()
            # leave a short signpost on the portrait page instead of dead space
            if out and not isinstance(out[-1], PageBreak) and carry:
                out.append(Spacer(1, 8))
                out.append(Paragraph(
                    '<i>▸ Bảng dưới đây gồm nhiều cột và được trình bày trên '
                    'trang ngang (landscape) ngay sau trang này để đọc rõ.</i>',
                    ParagraphStyle("hint", fontName="MetaSans-It", fontSize=8.0,
                                   leading=11, textColor=colors.HexColor("#7a828c"))))
            out.append(NextPageTemplate("land"))
            out.append(PageBreak())
            out.extend(carry)
            ends_with_break = True
        elif isinstance(f, LandEnd):
            if ends_with_break and out and isinstance(out[-1], PageBreak):
                out.pop()
            out.append(NextPageTemplate("portrait"))
            out.append(PageBreak())
            ends_with_break = True
        else:
            out.append(f)
            ends_with_break = isinstance(f, PageBreak)
    while out and isinstance(out[-1], PageBreak):
        out.pop()
    return out


class LandStart:
    """Sentinel: switch to the landscape page template before a wide table."""


class LandEnd:
    """Sentinel: switch back to portrait after a wide table."""


class _WideTable(Table):
    """Marker flowable: forces a landscape page group."""
    def __init__(self, inner):
        Table.__init__(self, [[inner]], colWidths=[landscape(A4)[0] - 68], hAlign="LEFT")
        self.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        self._inner = inner


# ---------------------------------------------------------------- cover
def cover_story(info_rows=None, kicker="WHITEPAPER", tagline=None):
    st = build_styles()
    story = [Spacer(1, 96)]
    story.append(Paragraph(
        '<font color="#1a4b8c" size="10"><b>GAME9K FUNDING PORTAL</b></font>',
        ParagraphStyle("cv1", fontName="MetaSans", fontSize=10, leading=14, alignment=TA_LEFT)))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        kicker,
        ParagraphStyle("cv0", fontName="MetaSans-Bold", fontSize=44, leading=48,
                       textColor=colors.HexColor("#0d1b2a"), alignment=TA_LEFT)))
    rule = Table([[""]], colWidths=[132], rowHeights=[3])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1),
                               colors.HexColor("#c8a04a"))]))
    story.append(Spacer(1, 8))
    story.append(rule)
    story.append(Spacer(1, 22))
    story.append(Paragraph(
        "Game9K Funding Portal là Bệ phóng Vốn đồng bộ theo phiên bản Game đầu tiên trên Thế giới "
        "(tài trợ game phát triển thật ở cấp độ phiên bản)",
        ParagraphStyle("cvt", fontName="MetaSans-Bold", fontSize=13.4, leading=19.5,
                       textColor=colors.HexColor("#12325c"), alignment=TA_LEFT)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        tagline or ("<i>The World&rsquo;s First Version-Synced Game Capital "
                    "Launchpad — Funding Real Game Development at the Version "
                    "Level</i>"),
        ParagraphStyle("cve", fontName="MetaSans-It", fontSize=9.6, leading=14,
                       textColor=colors.HexColor("#4a545f"))))
    story.append(Spacer(1, 34))

    if not info_rows:
        info_rows = [
            ["**Phiên bản**", "`v1.5` — Investor &amp; Strategic Whitepaper"],
            ["**Ngày phát hành**", "Tháng 11 / 2026"],
            ["**Phân khúc kiến tạo**", "Version-Synced Game Capital Markets"],
            ["**Vòng gọi vốn hiện tại**",
             "**Pre-Seed $1.0M** *(Seed $3.0M → Series A $12.0M → Series B $25.0M)*"],
            ["**Hạ tầng nền tảng**",
             "Open Web (HTML5 / WebGL / WebGPU) · Cloudflare Edge · Solana (SPL Token-2022)"],
            ["**Tài liệu đi kèm**",
             "YELLOWPAPER.md · PRD.md · 04-solana-smart-contracts.md · verify_protocol_math.py"],
        ]
    data = [[Paragraph(inline(a), ParagraphStyle("k", fontName="MetaSans-Bold",
                                                 fontSize=7.9, leading=10.6,
                                                 textColor=colors.HexColor("#3d4853"))),
             Paragraph(inline(b), ParagraphStyle("v", fontName="MetaSans", fontSize=7.9,
                                                 leading=10.6,
                                                 textColor=colors.HexColor("#22282f")))]
            for a, b in info_rows]
    t = Table(data, colWidths=[104, 360], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, colors.HexColor("#dfe4ea")),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t)
    story.append(Spacer(1, 40))
    story.append(Paragraph(
        "Tài liệu trình bày tầm nhìn sản phẩm, mô hình kinh tế, phân tích thị trường và kiến trúc "
        "của Game9K Funding Portal phục vụ nghiên cứu chiến lược và thẩm định đầu tư. Không cấu thành bản cáo "
        "bạch chào bán chứng khoán hay lời khuyên đầu tư tại bất kỳ khu vực pháp lý nào.",
        ParagraphStyle("dis", fontName="MetaSans-It", fontSize=7.4, leading=10.6,
                       textColor=colors.HexColor("#6b7480"), alignment=TA_JUSTIFY)))
    return story


import os
import re
import sys



def load_body(src):
    """Split a paper into (document-info table rows, body lines).

    Both papers start with a one-line title block, then a 2-column attribute
    table, then the abstract/disclaimer blockquote, then the body. We locate
    the table by its marker row ("| Thông tin tài liệu |" in the whitepaper) or
    by the first 2-cell table (the yellow paper), and cut the body at the rule
    that follows the abstract.
    """
    lines = open(src, encoding="utf-8").read().splitlines()
    start = None
    for i, l in enumerate(lines):
        if l.startswith("| Thông tin tài liệu") or l.startswith("| Thuộc tính Đặc tả"):
            start = i
            break
    if start is None:
        sys.exit("%s: no document-info table found" % src)
    body = lines[start:]
    hr = next(i for i, l in enumerate(body) if l.strip() == "---")
    return body[:hr], body[hr + 1:]


def toc_story(entries, st, avail):
    if not entries:
        return Spacer(1, 1)
    rows = []
    for lvl, txt, page in entries:
        style = ParagraphStyle(
            "toc%d" % lvl, fontName="MetaSans-Bold" if lvl == 0 else "MetaSans",
            fontSize=9.5 if lvl == 0 else 8.3, leading=12.6 if lvl == 0 else 11.2,
            leftIndent=2 if lvl == 0 else 16,
            textColor=colors.HexColor("#12325c" if lvl == 0 else "#3b4652"))
        label = inline(txt)
        rows.append([Paragraph(label, style), Paragraph(str(page), style)])
    t = Table(rows, colWidths=[avail - 26, 26], hAlign="LEFT")
    style = [("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
             ("ALIGN", (1, 0), (1, -1), "RIGHT"),
             ("TOPPADDING", (0, 0), (-1, -1), 2.2),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
             ("LEFTPADDING", (0, 0), (-1, -1), 0),
             ("RIGHTPADDING", (1, 0), (1, -1), 0),
             ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#dfe4ea"))]
    t.setStyle(TableStyle(style))
    return t


def blank_pages(pdf_path):
    """Page numbers whose only text is the running header/footer."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(pdf_path)
    out = []
    for i in range(len(doc)):
        txt = doc[i].get_textpage().get_text_range()
        out.append(len(txt.replace("\r", "").replace("\n", " ").strip()))
    doc.close()
    return [i + 1 for i, n in enumerate(out) if n < 120]


def build(src, out, title, subject, debug=False, kicker="WHITEPAPER",
          tagline=None, paper_label="Whitepaper v1.5",
          running_tagline="Version-Synced Game Capital Launchpad"):
    BRAND["paper"] = paper_label
    BRAND["tagline"] = running_tagline
    register_fonts()
    load_coverage()
    st = build_styles()
    info_lines, body = load_body(src)

    info_rows = [split_row(r.strip()) for r in info_lines if r.strip().startswith("|")]
    info_rows = [r for r in info_rows if not re.match(r"^:?-{2,}:?$", (r[0] or "").strip())]

    def assemble(entries, shift=0):
        doc = Doc(out, pagesize=A4, title=title, author="Game9K (khanhlegood1/GameFun)",
                    subject=subject,
                    keywords="Game9K, VGBC, Version Bond, Solana, GameFi, whitepaper")
        story = cover_story(info_rows[1:], kicker=kicker,
                           tagline=tagline) + [PageBreak()]
        toc_head = ParagraphStyle("toctitle", parent=st["h2"])
        story.append(Paragraph("Mục lục", toc_head))
        story.append(Spacer(1, 4))
        story.append(toc_story(entries, st, A4[0] - 84))
        story.append(PageBreak())
        flow = parse(body, st, A4[0] - 84)
        if shift:
            # nudge the flow by a hair so a "just full" page does not produce a
            # blank page in front of the landscape template switch
            out_flow = []
            for f in flow:
                if isinstance(f, LandStart):
                    out_flow.append(Spacer(1, shift * 1.5))
                out_flow.append(f)
            flow = out_flow
        story += expand_landscape(flow)
        doc.build(story)
        return doc

    # pass 1: discard output, collect headings
    assemble([])
    doc1 = Doc(os.devnull, pagesize=A4)
    story1 = cover_story(info_rows[1:], kicker=kicker,
                         tagline=tagline) + [PageBreak(),
                                             Paragraph("Mục lục",
                                                       ParagraphStyle("toctitle", parent=st["h2"])),
                                             Spacer(1, 4),
                                             PageBreak()]
    story1 += expand_landscape(parse(body, st, A4[0] - 84))
    doc1.build(story1)
    entries = [(lvl, txt, page) for (lvl, txt, page, key) in doc1.headings]

    # pass 2: final, with TOC + bookmarks; retry with a small shift if a
    # template switch left an empty page behind
    assemble(entries)
    print("built %s (%d bytes, %d TOC entries)" % (out, os.path.getsize(out), len(entries)))
    if debug:
        with open(out + ".toc.txt", "w", encoding="utf-8") as f:
            for e in entries:
                f.write("%d\t%s\t%d\n" % e)
    return entries


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    src = argv[0]
    out = argv[1] if len(argv) > 1 else "Game9K-Whitepaper.pdf"
    build(src, out, "Game9K Whitepaper v1.5",
          "Version-Synced Game Capital Launchpad", debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
