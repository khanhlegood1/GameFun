#!/usr/bin/env python3
"""Game9K investor pitch deck -> PDF (14 slides, 16:9, reproducible).

Why this file exists
--------------------
The previous deck (`docs/Game9K-Pitch-Deck.pdf`) was exported from Google
Slides: it had no source in the repo, so every numeric fix had to be retyped by
hand, and it drifted three whitepaper revisions behind (it still sold
"$0.75M -> $72.0M, breakeven Q4 Y1"). This generator makes the deck an
*artifact* instead of a picture: every figure below is copied from
`docs/WHITEPAPER.md` §6.1/§9.3 and `docs/YELLOWPAPER.md` §4.2/§5.1/§6.1, and
`scripts/check_pitch_deck.py` fails the build if a retired number creeps back.

Design constraints honoured here
--------------------------------
* Vietnamese diacritics + subscripts are embedded (same font pipeline as
  `build_whitepaper_pdf.py`, reusing its `ensure_fonts()`).
* Every number is either (a) integer-exact from the verifying simulator, or
  (b) explicitly labelled an estimate. Anything else belongs in "Known Gaps".
* No claim is made about code that does not exist in this repository.

Usage:
    python3 scripts/build_pitch_deck.py docs/Game9K-Pitch-Deck.pdf
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

import build_whitepaper_pdf as WB  # reuse the font bootstrap

# ---------------------------------------------------------------- brand
W, H = 960.0, 540.0          # 16:9 in points
M = 42.0                     # page margin

BG = HexColor("#0A1018")
CARD = HexColor("#111A26")
CARD_ALT = HexColor("#0D151F")
BORDER = HexColor("#1E2A3A")
TEXT = HexColor("#E6EDF5")
MUTED = HexColor("#93A4B8")
DIM = HexColor("#64748B")
GREEN = HexColor("#00E08A")
BLUE = HexColor("#4C8DFF")
PURPLE = HexColor("#A855F7")
ORANGE = HexColor("#F5A524")
RED = HexColor("#F2555A")

F = "MetaSans"
FB = "MetaSans-Bold"
FM = "MetaMono"

# Noto Sans (latin) lacks arrows/≈/≥/Φ/subscripts; DejaVu has all of them, so any
# run of exotic glyphs is drawn from DejaVu while plain Latin stays in Noto.
FALLBACK = "MetaFallback"
FALLBACK_B = "MetaFallbackB"
ARROWS = "\u2190\u2191\u2192\u2193\u2194"      # ← ↑ → ↓ ↔
EXOTIC = set("\u2190\u2191\u2192\u2193\u2194\u2248\u2265\u2264\u0394\u03a3\u03a6"
             "\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089"
             "\u25b8\u2713\u2020\u00bd")

FOOTER = "GAME9K LAUNCHPAD  ·  INVESTOR PITCH DECK v1.5  ·  CONFIDENTIAL (THÁNG 11/2026)"
TOTAL = 14

# ---------------------------------------------------------------- text utils
def sw(txt: str, font: str, size: float) -> float:
    return pdfmetrics.stringWidth(txt, font, size)


def wrap(txt: str, font: str, size: float, maxw: float) -> list[str]:
    """Greedy word wrap; never breaks a word that is longer than maxw."""
    out, line = [], ""
    for word in txt.split():
        cand = word if not line else line + " " + word
        if sw_mixed(cand, font, size) <= maxw:
            line = cand
        else:
            if line:
                out.append(line)
            line = word
    if line:
        out.append(line)
    return out or [""]


def runs(txt: str) -> list[tuple[str, bool]]:
    """Split txt into (chunk, is_exotic) runs so fallback glyphs keep their shape."""
    out: list[list] = []
    for ch in txt:
        ex = ch in EXOTIC
        if out and out[-1][1] == ex:
            out[-1][0] += ch
        else:
            out.append([ch, ex])
    return [(a, b) for a, b in out]


def _font_for(bold: bool, ex: bool) -> str:
    if ex:
        return FALLBACK_B if bold else FALLBACK
    return FB if bold else F


def _cur(c, font, size, color):
    """Fall back to whatever the canvas already has set (ReportLab tracks both)."""
    font = font or getattr(c, "_fontname", F)
    size = size or getattr(c, "_fontsize", 9.0)
    color = color if color is not None else getattr(c, "_fillColor", TEXT)
    return font, size, color


def drawstr(c, x, y, txt, font=None, size=None, color=None):
    """drawString with automatic per-glyph fallback. Returns end x."""
    font, size, color = _cur(c, font, size, color)
    bold = font in (FB, FALLBACK_B, "Helvetica-Bold", "Times-Bold")
    c.setFillColor(color)
    cx = x
    for chunk, ex in runs(txt):
        f = _font_for(bold, ex)
        c.setFont(f, size)
        c.drawString(cx, y, chunk)
        cx += sw(chunk, f, size)
    return cx


def drawright(c, xr, y, txt, font=None, size=None, color=None):
    """drawRightString with fallback: measure total first, then draw left-to-right."""
    font, size, color = _cur(c, font, size, color)
    bold = font in (FB, FALLBACK_B)
    total = sum(sw(ch, _font_for(bold, ex), size) for ch, ex in runs(txt))
    drawstr(c, xr - total, y, txt, font=font, size=size, color=color)
    return xr - total


def drawcentre(c, xc, y, txt, font=None, size=None, color=None):
    font, size, color = _cur(c, font, size, color)
    bold = font in (FB, FALLBACK_B)
    total = sum(sw(ch, _font_for(bold, ex), size) for ch, ex in runs(txt))
    return drawstr(c, xc - total / 2, y, txt, font=font, size=size, color=color)


def sw_mixed(txt: str, font: str, size: float) -> float:
    bold = font in (FB, FALLBACK_B, "Helvetica-Bold")
    return sum(sw(ch, _font_for(bold, ex), size) for ch, ex in runs(txt))


def para(c, txt, x, y, w, font=F, size=9.4, lead=13.0, color=MUTED, max_lines=None):
    """Draw wrapped text top-down from y; returns the y after the last line."""
    lines = wrap(txt, font, size, w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        drawstr(c, x, y, ln, font=font, size=size, color=color)
        y -= lead
    return y


# ---------------------------------------------------------------- chrome
def slide(c, n, kicker, title, subtitle=None, accent=GREEN):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(accent)
    c.rect(0, H - 3.2, W, 3.2, stroke=0, fill=1)

    c.setFont(FB, 7.6)
    c.setFillColor(accent)
    drawstr(c, M, H - 40, kicker.upper())

    y = H - 74
    c.setFont(FB, 21.5)
    c.setFillColor(TEXT)
    for ln in wrap(title, FB, 21.5, W - 2 * M)[:2]:
        drawstr(c, M, y, ln)
        y -= 27

    if subtitle:
        y -= 3
        para(c, subtitle, M, y, W - 2 * M - 10, size=9.8, lead=13.6, color=MUTED,
             max_lines=2)

    # footer
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.6)
    c.line(M, 30, W - M, 30)
    c.setFont(F, 6.8)
    c.setFillColor(DIM)
    drawstr(c, M, 20, FOOTER)
    c.setFont(FB, 6.8)
    drawright(c, W - M, 20, f"{n:02d} / {TOTAL}")


def card(c, x, y, w, h, accent=None, fill=CARD, radius=3.0):
    c.setFillColor(fill)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
    if accent:
        c.setFillColor(accent)
        c.rect(x, y + h - 2.6, w, 2.6, stroke=0, fill=1)


def card_head(c, x, y, w, txt, color=TEXT, size=9.0, font=FB, max_lines=2):
    c.setFont(font, size)
    lines = wrap(txt, font, size, w)[:max_lines]
    c.setFillColor(color)
    for ln in lines:
        drawstr(c, x, y, ln)
        y -= size + 3.4
    return y


def _rich_lines(prefix, rest, size, w1, w2, prefix_own_line=False):
    """Greedy wrap with an unbreakable bold prefix on the first line only.

    Returning measured lines (instead of drawing and hoping) is what keeps every
    bullet inside its card: a prefix that eats more than 60% of the line width is
    promoted to its own line instead of squeezing the body into a sliver."""
    lines, cur, curw = [], [], 0.0
    if prefix:
        pfx = prefix.strip() + "  "
        pw = sw_mixed(pfx, FB, size)
        if not prefix_own_line and pw <= 0.60 * w1:
            cur.append((pfx, FB))
            curw = pw
        else:
            lines.append([(prefix.strip(), FB)])
    limit = w1
    space = sw_mixed(" ", F, size)
    for word in rest.split():
        wd = sw_mixed(word, F, size)
        add = (space if cur else 0.0) + wd
        if cur and curw + add > limit:
            lines.append(cur)
            cur, curw = [], 0.0
            limit = w2
            add = wd
        if cur:
            cur.append((" ", F))
        cur.append((word, F))
        curw += add
    if cur:
        lines.append(cur)
    return lines


def bullets(c, items, x, y, w, size=8.5, lead=11.6, gap=4.2, color=MUTED,
            mark="\u25b8", mark_color=None, bold_prefix=True, rtl=False,
            prefix_own_line=False):
    """items: list of str, or (prefix, rest) tuples.

    rtl=True renders the last bullet upward from y (used for the P&L table so a
    chart column and a 10-row table can share a slide without guessing heights)."""
    lines_total = 0
    per_item = [_rich_lines(it[0] if isinstance(it, tuple) else None,
                            it[1] if isinstance(it, tuple) else it,
                            size, w - 9, w - 9,
                            prefix_own_line=prefix_own_line) for it in items]
    if rtl:
        height = sum(len(ch) * lead for ch in per_item) + gap * (len(per_item) - 1)
        y = y + height - lead          # y is the BOTTOM: place the first baseline
    for it, blocks in zip(items, per_item):
        prefix, rest = it if isinstance(it, tuple) else (None, it)
        drawstr(c, x, y, mark, font=F, size=size, color=mark_color or GREEN)
        for chunk in blocks:
            cx = x + 9
            for txt, fnt in chunk:
                f = fnt if bold_prefix or fnt == FB else F
                drawstr(c, cx, y, txt, font=f, size=size,
                        color=TEXT if f == FB else color)
                cx += sw_mixed(txt, f, size)
            y -= lead
        y -= gap
    return y


def table(c, x, y, w, cols, rows, row_hs=None, col_w=None, head_bg=HexColor("#16222F"),
          size=8.2, row_h=19.5, head_h=21.0, aligns=None, bold_last=False,
          cell_colors=None):
    """Minimal zebra table drawn top-down from y. Returns bottom y."""
    n = len(cols)
    if col_w is None:
        col_w = [w / n] * n
    assert abs(sum(col_w) - w) < 0.01, (sum(col_w), w)
    aligns = aligns or ["l"] * n

    c.setFillColor(head_bg)
    c.rect(x, y - head_h, w, head_h, stroke=0, fill=1)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.6)
    c.rect(x, y - head_h, w, head_h, stroke=1, fill=0)
    cx = x
    HC = HexColor("#B9C7D6")
    for i, col in enumerate(cols):
        t = col
        head_pieces = t.split("\n")
        sz = size - 0.4
        while any(sw_mixed(hp, FB, sz) > col_w[i] - 12 for hp in head_pieces) and sz > 5.2:
            sz -= 0.2
        hy = y - head_h + 7.2 + (len(head_pieces) - 1) * 4.2
        for hp in head_pieces:
            hr = FB if hp is head_pieces[0] else F
            if aligns[i] == "r":
                drawright(c, cx + col_w[i] - 7, hy, hp, font=hr, size=sz if hr == FB else sz - 0.8, color=HC)
            elif aligns[i] == "c":
                drawcentre(c, cx + col_w[i] / 2, hy, hp, font=hr, size=sz if hr == FB else sz - 0.8, color=HC)
            else:
                drawstr(c, cx + 7, hy, hp, font=hr, size=sz if hr == FB else sz - 0.8, color=HC)
            hy -= 9.0
        cx += col_w[i]

    y -= head_h
    for ri, row in enumerate(rows):
        if row_hs and row_hs[ri]:
            row_h = row_hs[ri]
        last = bold_last and ri == len(rows) - 1
        if last:
            c.setFillColor(HexColor("#13251F"))
        else:
            c.setFillColor(CARD_ALT if ri % 2 == 0 else CARD)
        c.rect(x, y - row_h, w, row_h, stroke=0, fill=1)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.rect(x, y - row_h, w, row_h, stroke=1, fill=0)
        cx = x
        for ci, cell in enumerate(row):
            txt = str(cell)
            col = TEXT
            if cell_colors and (ri, ci) in cell_colors:
                col = cell_colors[(ri, ci)]
            font = FB if (ci == 0 or last) else F
            if last:
                col = GREEN if ci else TEXT
            # a cell may carry a subtitle after "\n" (rendered smaller, muted)
            pieces = txt.split("\n")
            # shrink to fit (measured with glyph fallback)
            s = size
            while any(sw_mixed(pc, font, s) > col_w[ci] - 12 for pc in pieces) and s > 5.4:
                s -= 0.2
            n_pc = len(pieces)
            for pi, piece in enumerate(pieces):
                fnt = font if pi == 0 else F
                sz = s if pi == 0 else max(5.6, s - 1.2)
                cl = col if pi == 0 else MUTED
                py = y - row_h + 6.6 + (n_pc - 1 - pi) * 9.6
                if aligns[ci] == "r":
                    drawright(c, cx + col_w[ci] - 7, py, piece, font=fnt, size=sz, color=cl)
                elif aligns[ci] == "c":
                    drawcentre(c, cx + col_w[ci] / 2, py, piece, font=fnt, size=sz, color=cl)
                else:
                    drawstr(c, cx + 7, py, piece, font=fnt, size=sz, color=cl)
            cx += col_w[ci]
        y -= row_h
    return y


def chip(c, x, y, txt, color=GREEN, size=7.2, pad=7, h=15.0):
    w = sw_mixed(txt, FB, size) + 2 * pad
    c.setFillColor(HexColor("#0F1A22"))
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, h / 2, stroke=1, fill=1)
    drawcentre(c, x + w / 2, y + h / 2 - size / 2 + 1.4, txt, font=FB, size=size, color=color)
    return x + w + 7


def box(c, x, y, w, h, title, body, accent=GREEN, title_size=9.4, body_size=8.6):
    c.setFillColor(HexColor("#0C1A16"))
    c.setStrokeColor(accent)
    c.setLineWidth(1.0)
    c.roundRect(x, y, w, h, 3, stroke=1, fill=1)
    c.setFillColor(accent)
    c.rect(x, y + h - 3.0, w, 3.0, stroke=0, fill=1)
    ty = y + h - 18
    ty = card_head(c, x + 12, ty, w - 24, title, color=accent, size=title_size)
    for chunk in body.split("\n"):
        ty = para(c, chunk, x + 12, ty - 2, w - 24, size=body_size,
                  lead=body_size * 1.55, color=MUTED)
    return y


# ---------------------------------------------------------------- slides
def s01_cover(c):
    slide(c, 1, "PITCH DECK v1.5  ·  WHITEPAPER v1.5  ·  YELLOW PAPER v1.0",
          "GAME9K LAUNCHPAD", accent=GREEN)

    y = H - 155
    c.setFont(FB, 19)
    c.setFillColor(GREEN)
    drawstr(c, M, y, "Bệ phóng Vốn đồng bộ theo phiên bản Game")
    drawstr(c, M, y - 26, "đầu tiên trên Thế giới")
    y -= 26 + 26 + 26
    para(c, "(tài trợ game phát triển thật ở cấp độ phiên bản)", M, y,
         W * 0.52, size=11, color=MUTED)

    y -= 34
    para(c, "Chuẩn Poki × Blind Arena × Version-Gated Bonding Curve trên Open Web "
            "(HTML5/WebGPU) & Solana (Token-2022).", M, y, W * 0.52,
         size=9.6, lead=14, color=MUTED)

    # slogan box
    bx, by, bw, bh = M, 120, W * 0.52, 74
    c.setFillColor(HexColor("#0C1A16"))
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.2)
    c.roundRect(bx, by, bw, bh, 3, stroke=1, fill=1)
    c.setFont(FB, 12.4)
    c.setFillColor(TEXT)
    drawstr(c, bx + 14, by + bh - 26, "“Không Tốt hơn — Không Cho Mở Thanh khoản Mới.”")
    c.setFont(F, 9.2)
    c.setFillColor(MUTED)
    drawstr(c, bx + 14, by + 22, "Gate-First Capital Formation  ·  0% Token Nền tảng  ·  Tự khóa tay On-Chain")

    # right rail: rounds
    rx, ry, rw = W - M - 330, 92, 330
    card(c, rx, ry, rw, 356, accent=GREEN)
    c.setFont(FB, 8.4)
    c.setFillColor(GREEN)
    drawstr(c, rx + 14, ry + 332, "LỘ TRÌNH GỌI VỐN ĐA VÒNG")
    rows = [
        ("PRE-SEED · ĐANG MỞ", "$1.0M", "$10M Post Cap · 10% · 8 FTE", GREEN),
        ("SEED · M12–M15", "$3.0M", "$25M Post · 12% · 16 FTE", BLUE),
        ("SERIES A · M24–M27", "$12.0M", "$80M Post · 15% · 36 FTE", PURPLE),
        ("SERIES B · M36–M42", "$25.0M", "$250M Post · 10% · 65 FTE", ORANGE),
    ]
    yy = ry + 300
    for label, amt, meta, col in rows:
        c.setFillColor(HexColor("#0E1621"))
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.6)
        c.roundRect(rx + 12, yy - 46, rw - 24, 56, 3, stroke=1, fill=1)
        c.setFont(FB, 7.0)
        c.setFillColor(col)
        drawstr(c, rx + 22, yy + 0.2, label)
        c.setFont(FB, 15)
        c.setFillColor(TEXT)
        drawright(c, rx + rw - 22, yy - 1, amt)
        c.setFont(F, 7.4)
        c.setFillColor(MUTED)
        drawstr(c, rx + 22, yy - 15, meta)
        yy -= 66

    c.setFont(F, 7.6)
    c.setFillColor(DIM)
    drawcentre(c, rx + rw / 2, ry + 14, "github.com/khanhlegood1/GameFun")

    c.setFont(F, 8.0)
    c.setFillColor(DIM)
    drawstr(c, M, 46, "Tháng 11 / 2026  ·  Tài liệu chiến lược & thẩm định đầu tư  "
                        "(Whitepaper v1.5 & Yellow Paper v1.0)")


def s02_problem(c):
    slide(c, 2, "01 · VẤN ĐỀ THỊ TRƯỜNG (THE PROBLEM)",
          "Hai Thị trường Tỷ Đô — Một Mắt xích Sống còn Đang Bị Bỏ trống",
          "Web2 có hàng trăm triệu game thủ nhưng đóng cửa gọi vốn; Web3 có hàng tỷ USD thanh khoản "
          "nhưng thiếu cổng kiểm định sản phẩm.", accent=RED)

    top, h = 392, 196
    cw = (W - 2 * M - 2 * 16) / 3
    data = [
        ("THẤT BẠI #1 · WEB2 PORTALS", "100M+ MAU", "nhưng 0% vốn cho v0.1 → v1.0",
         "Poki đạt 100M+ MAU & 1 tỷ lượt chơi/tháng (~65 FTE). CrazyGames vượt 60M MAU.",
         "Studio thiếu người test thật, thiếu dữ liệu cải tiến và thiếu $5K–$50K vốn mồi "
         "để hoàn thiện game.", BLUE),
        ("THẤT BẠI #2 · LAUNCHPAD ĐỜI 1", "85% – 98%", "dự án chết vì mở 100% curve ở v0.1",
         "Pump.fun (>$800M phí): 0,89% tốt nghiệp; 80,4% ngừng giao dịch trong 24 giờ đầu.",
         "Virtuals: 85% trên 1.232 AI agent chết — vốn vào từ ngày đầu khiến đội ngũ "
         "không cần cải thiện sản phẩm.", ORANGE),
        ("THẤT BẠI #3 · BOT & XẢ SỚM", "Block-0", "sniper biến game thủ thành khoản thoát",
         "Đầu cơ chớp nhoáng gom giá đáy trong vài giây rồi xả lên người chơi thật.",
         "Không bảo hiểm hoàn vốn: khi nhà phát triển bỏ dự án, người mua trắng tay "
         "vì không có cơ chế Ragequit.", RED),
    ]
    for i, (kicker, big, sub, p1, p2, col) in enumerate(data):
        x = M + i * (cw + 16)
        card(c, x, top - h, cw, h, accent=col)
        card_head(c, x + 14, top - 20, cw - 28, kicker, color=col, size=7.6)
        c.setFont(FB, 27)
        c.setFillColor(TEXT)
        drawstr(c, x + 14, top - 58, big)
        para(c, sub, x + 14, top - 76, cw - 28, size=8.2, color=col)
        bullets(c, [p1, p2], x + 14, top - 106, cw - 28, size=8.1, lead=11.2, gap=5)

    box(c, M, 58, W - 2 * M, 84,
        "LUẬN ĐIỂM ĐẦU TƯ: Ai đã kéo chi phí tạo game HTML5 về gần bằng 0, biến Kiểm định Chất lượng "
        "theo Phiên bản (Version Curation) và Phân bổ Vốn gắn với Giờ chơi Thật (Gate-First Capital "
        "Formation) thành một thứ có thể đạt giá nhất thấp kỷ — và Game9K sở hữu trọn vẹn nút thắt đó.",
        "Trả lời ngắn: không launchpad nào hiện có khoá được vốn theo phả hệ phiên bản đã kiểm định, "
        "vì khoá như vậy đòi hỏi đồng thời Sổ cái phiên bản, Phễu Fit và Đấu trường mù.",
        accent=GREEN, title_size=9.0, body_size=8.4)


def s03_solution(c):
    slide(c, 3, "02 · GIẢI PHÁP ĐỘT PHÁ (THE GAME9K SOLUTION)",
          "4 Nguyên tử Công nghệ – Kinh tế Lần đầu tiên Hợp nhất trên Một Nền tảng",
          "Mặt trước là cổng game tức thì chuẩn Poki (0 ví, 0 cài đặt, vào chơi <3s); mặt sau là "
          "sàn gọi vốn mở khóa theo từng phiên bản trên Solana.")

    top, h = 406, 216
    cw = (W - 2 * M - 3 * 12) / 4
    atoms = [
        ("01 · IMMUTABLE VERSION REGISTRY", "Sổ cái Phiên bản Bất biến",
         ["Mỗi bản build giải nén → sắp xếp → băm SHA-256 (bỏ timestamp ZIP).",
          "BuildDiff đo % thực chất thay đổi; dưới 8% bị gắn nhãn HOTFIX và cấm mở vốn.",
          "Neo Merkle mỗi 3.600s lên Solana."], BLUE),
        ("02 · PROOF-OF-PLAY GATE", "Cổng Mua bằng Giờ chơi Thật",
         ["Điều kiện mua nằm trong smart contract, không ở giao diện.",
          "Chứng thực 106 B ký Ed25519 gắn giờ chơi của chính ví.",
          "Bot chưa chơi thì không có chữ ký — không mua được block-0."], GREEN),
        ("03 · BLIND VERSION ARENA", "Đấu trường Mù 95% LCB",
         ["Hai phiên bản thi đấu ẩn danh, tráo trái/phải 50/50.",
          "Bản mới phải thắng bản cũ với cận tin cậy 95%.",
          "Bản Genesis (k=1) dùng ngoại lệ Φ_prog — vá lỗi kẹt cổng M2."], PURPLE),
        ("04 · MILESTONE ESCROW", "Giải ngân theo Nghiệm thu",
         ["Vốn nằm on-chain, mở dần qua M1 → M2 → M3 → M4.",
          "Trượt hạn 60–90 ngày ⇒ Stall ⇒ Ragequit hoàn SOL theo tỷ lệ, 0% phạt.",
          "0% token nền tảng — không xung đột lợi ích khi duyệt cổng."], ORANGE),
    ]
    for i, (kicker, title, pts, col) in enumerate(atoms):
        x = M + i * (cw + 12)
        card(c, x, top - h, cw, h, accent=col)
        card_head(c, x + 12, top - 18, cw - 24, kicker, color=col, size=6.9)
        yy = para(c, title, x + 12, top - 40, cw - 24, font=FB, size=10.2, lead=13.2, color=TEXT)
        bullets(c, pts, x + 12, yy - 6, cw - 24, size=7.9, lead=10.6, gap=4.4, mark_color=col)

    box(c, M, 86, W - 2 * M, 84,
        "KHÁC BIỆT CỐT LÕI: Chúng tôi không tài trợ “một tựa game” — chúng tôi tài trợ “một phiên bản cụ thể của tựa game đó”.",
        "Vì vậy mỗi phiên bản sở hữu bốn thứ độc lập, không dùng chung và không vay mượn của bản trước: "
        "điểm chất lượng riêng · dữ liệu thật riêng · Version Bond riêng · escrow riêng.",
        accent=GREEN, title_size=9.4)


def s04_why_regulatory(c):
    slide(c, 4, "03 · THỜI ĐIỂM VÀNG, KHUNG 5W1H & TUÂN THỦ",
          "Tại sao Phải là 2026–2027? Ba Làn sóng Hội tụ & Chiến lược Tách Cầu/Cung",
          "Cung game tăng 100 lần nhờ AI, nhà đầu tư khát launchpad có sản phẩm thật, và trình duyệt "
          "trở thành siêu nền tảng game không thu thuế 30%.")

    # three waves
    tw = (W - 2 * M - 2 * 12) / 3
    th = 96
    waves = [
        ("WHEN #1 · AI GAME EXPLOSION", "100× Nguồn cung Game mới",
         "1–2 lập trình viên dùng AI tạo prototype HTML5 trong vài ngày thay vì 6 tháng — "
         "bộ lọc chất lượng theo phiên bản thành hạ tầng thiết yếu.", BLUE),
        ("WHEN #2 · LAUNCHPAD RESET", "Dịch chuyển sang Chất lượng Thật",
         "Sau cú sập niềm tin (98% không tốt nghiệp; 85% agent chết), dòng vốn tìm tài sản "
         "có số liệu thật và chống rug.", ORANGE),
        ("WHEN #3 · OPEN WEB GOLDEN AGE", "WebGPU + 0% Thuế Kho App",
         "WebAssembly/WebGPU đạt hiệu năng cao trên mọi điện thoại; chia sẻ 1 link TikTok/X/Discord "
         "là chơi ngay.", PURPLE),
    ]
    y0 = 400
    for i, (k, t, b, col) in enumerate(waves):
        x = M + i * (tw + 12)
        card(c, x, y0 - th, tw, th, accent=col)
        card_head(c, x + 12, y0 - 17, tw - 24, k, color=col, size=6.9)
        yy = para(c, t, x + 12, y0 - 38, tw - 24, font=FB, size=10.4, color=TEXT)
        para(c, b, x + 12, yy - 2, tw - 24, size=8.0, lead=10.8)

    # 5W1H compact row
    y2 = 276
    c.setFont(FB, 7.6)
    c.setFillColor(GREEN)
    drawstr(c, M, y2 + 8, "TOÀN CẢNH CHIẾN LƯỢC 5W1H CỦA GAME9K")
    items = [
        ("WHAT", "Cổng web game chơi tức thì + Đấu trường mù Arena + Sàn gọi vốn khóa 4 chặng M1–M4 có Ragequit."),
        ("WHO", "Game thủ 16–32t · Studio Indie & AI · Nhà giao dịch Solana tìm sản phẩm thật · Nhãn quảng cáo."),
        ("WHERE", "Open Web toàn cầu + thành khoản Solana; Tách Cầu/Cung: VN/SEA cấp DỮ LIỆU, vốn đến từ Mỹ/EU/LATAM."),
        ("HOW", "ZIP → Inspector → Playtest/Fit 500 & Blind Arena → Oracle ký mốc → 24h PoP → M4 tự động lên DEX."),
    ]
    cw2 = (W - 2 * M - 3 * 10) / 4
    for i, (k, v) in enumerate(items):
        x = M + i * (cw2 + 10)
        card(c, x, y2 - 74, cw2, 74, accent=None, fill=CARD_ALT)
        c.setFont(FB, 7.2)
        c.setFillColor(GREEN)
        drawstr(c, x + 10, y2 - 14, k)
        para(c, v, x + 10, y2 - 27, cw2 - 20, size=7.6, lead=10.2, color=MUTED, max_lines=4)

    # regulatory box — the item-4 fix
    box(c, M, 52, W - 2 * M, 96,
        "CHIẾN LƯỢC TÁCH CẦU / CUNG (REGULATORY COMPLIANCE) — Nghị quyết 05/2025/NQ-CP",
        "Web2 (DỮ LIỆU): người chơi Việt Nam & SEA chơi MIỄN PHÍ, không ví, không token — cung cấp VPH, "
        "chấm điểm Arena, nhận thưởng theo giờ chơi đã xác minh.      "
        "Web3 (VỐN): phân khu Launchpad/Version Bond CHẶN IP + KYC với Việt Nam, chỉ nhận vốn từ nhà đầu tư "
        "quốc tế (Mỹ/EU/LATAM/Hàn Quốc).      "
        "Dòng vốn về studio là FIAT qua pháp nhân quốc tế (Off-Chain Revenue-Share) — hoạt động hợp pháp "
        "trong khung thí điểm tài sản mã hóa, không cần bán token cho công dân VN.",
        accent=ORANGE, title_size=8.8, body_size=8.2)


def s05_dual_curve(c):
    slide(c, 5, "04 · MÔ HÌNH DUAL-CURVE (PHẦN A: TOKEN)",
          "Mô hình Dual-Curve: Tối ưu Thanh khoản DEX & Vốn Phát triển Studio",
          "Hai hồ sơ hợp đồng cho hai mục tiêu khác nhau — studio tự chọn loại vốn mình cần, "
          "và nhà đầu tư nhìn thấy chính xác từng phần cung đi đâu.")

    cols = ["Hạng mục Phân bổ", "HỒ SƠ A · VGBC-4T\nTối ưu thanh khoản DEX",
            "HỒ SƠ B · VBOND-LV\nTối ưu vốn phát triển", "Cơ chế bảo vệ on-chain"]
    rows = [
        ("Đường cong Cộng đồng", "70%  (700M)", "60%  (600M)", "x·y = k; mở khóa theo M1→M4"),
        ("Quỹ Thưởng Người chơi (PoPW)", "10%  (100M) + 50% SOL phạt", "20%  (200M) + 50% SOL phạt", "Trả theo VPH, tuyến tính 21 ngày"),
        ("Nhà phát triển (Vesting)", "5%  (50M) + 10 SOL Grant M4", "15%  (150M)", "0% ở M0–M1; đóng băng nếu bỏ game"),
        ("Thanh khoản DEX Khóa (LP)", "15%  (150M) · khóa vĩnh viễn", "5%  (50M) · khóa ≥ 12 tháng", "Lên DEX ở đúng 100% giá cuối curve"),
        ("Đội ngũ Nền tảng Game9K", "0%  (0 token)", "0%  (0 token)", "Chỉ nhận phí giao dịch & ads"),
    ]
    y = 402
    table(c, M, y, W - 2 * M, cols, rows,
          col_w=[172, 190, 190, 324], size=8.4, row_h=30, head_h=34,
          bold_last=False)

    # callout: platform 0%
    by = 148
    card(c, M, by, 300, 66, accent=GREEN)
    c.setFont(FB, 22)
    c.setFillColor(GREEN)
    drawstr(c, M + 14, by + 34, "0%")
    c.setFont(FB, 8.6)
    c.setFillColor(TEXT)
    drawstr(c, M + 14, by + 18, "Token Nền tảng — cả hai hồ sơ")
    c.setFont(F, 7.4)
    c.setFillColor(MUTED)
    drawstr(c, M + 96, by + 35, "Không xung đột lợi ích khi duyệt cổng")

    box(c, M + 312, by, W - 2 * M - 312, 66,
        "ĐỌC ĐÚNG HAI TRẦN KHÁC NHAU",
        "VGBC-4T giới hạn 2% TỔNG CUNG mỗi ví (20M token). VBOND-LV giới hạn 5% LƯỢNG CURVE mỗi ví "
        "(30M token). Đây là hai tầng khác nhau — không phải hai cách viết của cùng một con số.",
        accent=BLUE, title_size=8.4, body_size=7.8)


def s06_sol_flows(c):
    slide(c, 6, "05 · MÔ HÌNH DUAL-CURVE (PHẦN B: DÒNG TIỀN SOL)",
          "Mô hình Dual-Curve: Tối ưu Thanh khoản DEX & Vốn Phát triển Studio",
          "“Vậy studio lấy tiền đâu để làm game từ M1 đến M3?” — Đây là câu trả lời đến từng lamport.",
          accent=BLUE)

    cols = ["Đại lượng Tất toán khi Tốt nghiệp", "HỒ SƠ A · VGBC-4T", "HỒ SƠ B · VBOND-LV", "Ý nghĩa"]
    rows = [
        ("Tổng SOL thực tích lũy (R_end)", "79.245283 SOL", "76.109937 SOL", "Tiền của người mua — KHÔNG phải doanh thu"),
        ("SOL đưa vào Pool DEX (S_LP)", "61.836953 SOL  (78,0%)", "14.387943 SOL  (18,9%)", "Độ sâu thanh khoản mở sàn"),
        ("Phí Tốt nghiệp Nền tảng (cố định)", "1.500000 SOL", "1.500000 SOL", "Thu khi pool DEX tạo thành công"),
        ("→ Ngân sách Phát triển cho Studio", "15.908330 SOL", "60.221994 SOL", "Vốn mồi THẬT để trả lương & máy chủ"),
        ("Quy đổi @ $150/SOL", "≈ $2.386", "≈ $9.033", "Nằm trong khoảng $5K–$50K mà studio cần"),
    ]
    y = table(c, M, 400, W - 2 * M, cols, rows,
              col_w=[196, 190, 190, 300], size=8.6, row_h=29, head_h=32,
              cell_colors={(3, 1): GREEN, (3, 2): GREEN})

    # exact subtraction
    bx, by, bw, bh = M, 196, W - 2 * M, 84
    c.setFillColor(HexColor("#0C1A16"))
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.2)
    c.roundRect(bx, by, bw, bh, 3, stroke=1, fill=1)
    c.setFont(FB, 7.8)
    c.setFillColor(GREEN)
    drawstr(c, bx + 14, by + bh - 20, "PHÉP TRỪ CHÍNH XÁC — VBOND-LV (không làm tròn, không bỏ sót khoản nào)")
    drawstr(c, bx + 14, by + 40,
            "76,109937   −   14,387943   −   1,500000   =   60,221994 SOL",
            font=FM, size=12.0, color=TEXT)
    drawstr(c, bx + 14, by + 24,
            "   (Tổng huy động)      (khoá DEX LP)      (phí tốt nghiệp cố định)         (nạp vào Creator Milestone Escrow)",
            size=8.2, color=MUTED)
    drawstr(c, bx + 14, by + 9,
            "Phí tốt nghiệp là CỐ ĐỊNH 1,50 SOL trên mỗi dự án — không phải 2% × R_end. Nếu áp 2% sẽ ra 1,522199 SOL "
            "và escrow 60,199795 SOL; luật 2% đó không tồn tại trong spec (YP §6.1).",
            font=FB, size=7.6, color=GREEN)

    # disbursement ladder
    y2 = 176
    c.setFont(FB, 7.6)
    c.setFillColor(GREEN)
    drawstr(c, M, y2, "LỘ TRÌNH GIẢI NGÂN ESCROW — 60,221994 SOL CHIA BỐN MỐC (escrow không mở sớm hơn một lamport)")
    steps = [("M1 · PLAYTEST", "5,00 SOL", "prototype & máy chủ", BLUE),
             ("M2 · PLAYER FIT", "15,00 SOL", "khi dữ liệu thật chứng minh", PURPLE),
             ("M3 · WEB FIT", "20,00 SOL", "marketing & mở rộng", ORANGE),
             ("M4 · RELEASE v1.0", "20,221994 SOL", "cùng lúc đẩy thanh khoản DEX", GREEN)]
    # each milestone is gated by data, not by a calendar — that is what makes
    # front-loading the escrow impossible, so state the gate on every card.
    gates = ["kèm trần ví 0,25–2,0 SOL", "kèm cửa sổ PoP 24 giờ",
             "kèm ngưỡng retention thật", "kèm khoá LP DEX ≥ 12 tháng"]
    sw_ = (W - 2 * M - 3 * 10) / 4
    for i, (k, amt, note, col) in enumerate(steps):
        x = M + i * (sw_ + 10)
        card(c, x, y2 - 76, sw_, 72, accent=col, fill=CARD_ALT)
        drawstr(c, x + 10, y2 - 20, k, font=FB, size=7.0, color=col)
        drawstr(c, x + 10, y2 - 40, amt, font=FB, size=13, color=TEXT)
        para(c, note, x + 10, y2 - 52, sw_ - 20, size=7.4, lead=9.6, color=MUTED, max_lines=2)
        drawstr(c, x + 10, y2 - 70, gates[i], font=F, size=6.2, color=DIM)

    drawstr(c, M, 72, "Escrow không có đường tắt: mỗi mốc khoá bằng dữ liệu, không bằng lịch — "
                      "và không mốc nào mở sớm hơn một lamport.",
            font=F, size=7.4, color=GREEN)


def s07_shield(c):
    slide(c, 7, "06 · KINH TẾ TOKEN & LÁ CHẮN CHỐNG ĐẦU CƠ XẢ SỚM",
          "Chuẩn 1 Tỷ SPL Token-2022 (0% Token Nền tảng) & Biến Kẻ Xả Sớm thành Quỹ Thưởng",
          "Mechanism Design buộc mọi tác nhân chỉ có lợi khi đồng hành cùng chất lượng dài hạn của trò chơi.",
          accent=ORANGE)

    # ladder table
    cols = ["Thời gian nắm giữ", "Tổng phí BÁN (cơ bản 1% + phụ phí)", "Bot lướt sóng lỗ ròng", "Ghi chú"]
    rows = [
        ("Hồ sơ Tăng trưởng · < 1 giờ", "12%   (1% + 11%)", "−12,88%", "Cận lý thuyết của cấu hình cực đại"),
        ("Hồ sơ Tăng trưởng · 1 – 24 giờ", "6%   (1% + 5%)", "−6,94%", ""),
        ("Hồ sơ Tăng trưởng · 1 – 7 ngày", "3%   (1% + 2%)", "−3,97%", ""),
        ("Hồ sơ Ổn định · < 7 ngày", "5%   (1% + 4%)", "−5,95%", "MẶC ĐỊNH — lỗ chắc chắn"),
        ("Cả hai · ≥ 7 ngày\nhoặc đồng hành ≥ 1 version", "1%   (chỉ phí cơ bản)", "−1,99%", "Miễn phụ phí, KHÔNG miễn phí cơ bản"),
    ]
    table(c, M, 400, W - 2 * M, cols, rows,
          col_w=[236, 250, 150, 240], size=8.6, row_h=27, head_h=32,
          cell_colors={(3, 3): GREEN})

    box(c, M, 150, (W - 2 * M - 14) / 2, 74,
        "ĐỌC ĐÚNG CON SỐ −12,88%",
        "Đây là CẬN LÝ THUYẾT của hồ sơ Tăng trưởng trong cửa sổ < 1 giờ (phụ phí 11% là mức trần của mã nguồn). "
        "Với chế độ mặc định VBOND-LV, bot mua–bán chớp nhoáng lỗ ròng CHẮC CHẮN −5,95%. "
        "Trượt giá chỉ làm khoản lỗ sâu thêm.",
        accent=ORANGE, title_size=8.4, body_size=7.9)

    box(c, M + (W - 2 * M - 14) / 2 + 14, 150, (W - 2 * M - 14) / 2, 74,
        "PHỤ PHÍ THOÁT SỚM LINH HOẠT THEO THỜI GIAN NẮM GIỮ",
        "Mức phụ phí giảm dần theo thời gian giữ: 11% → 5% → 2% → 0% (hồ sơ Tăng trưởng) và 4% → 0% (hồ sơ Ổn định). "
        "Người đồng hành qua ≥ 1 phiên bản mới chỉ chịu duy nhất phí cơ bản 1,00% ở cả hai hồ sơ.",
        accent=GREEN, title_size=8.4, body_size=7.9)

    # fee split + 3 shields
    bx = M
    c.setFont(FB, 7.6)
    c.setFillColor(GREEN)
    drawstr(c, bx, 132, "DÒNG CHẢY PHÍ PHẠT XẢ SỚM")
    splits = [("50%", "thưởng SOL cho Game thủ thật", GREEN),
              ("40%", "đắp Quỹ Giá sàn (Ragequit)", BLUE),
              ("10%", "Protocol Treasury", PURPLE)]
    for i, (pc, note, col) in enumerate(splits):
        x = bx + i * 200
        c.setFont(FB, 15)
        c.setFillColor(col)
        drawstr(c, x, 110, pc)
        c.setFont(F, 7.6)
        c.setFillColor(MUTED)
        drawstr(c, x + sw(pc, FB, 15) + 6, 112, note)

    shields = [
        ("LỚP 1 · 24h Gamer Priority Window", "24 giờ đầu mỗi mốc chỉ ví có Proof-of-Play mới được mua, trần 0,25–2,0 SOL/ví."),
        ("LỚP 2 · Pre-Graduation Custody", "Số dư gắn cứng trong PDA BuyerPosition — 100 ví ảo không thể gom về 1 ví."),
        ("LỚP 3 · Early-Exit Anti-Dump Tax", "Biến mọi vòng mua–xả chớp nhoáng thành khoản lỗ chắc chắn."),
    ]
    cw = (W - 2 * M - 2 * 12) / 3
    for i, (t, b) in enumerate(shields):
        x = M + i * (cw + 12)
        card(c, x, 44, cw, 54, accent=None, fill=CARD)
        card_head(c, x + 10, 84, cw - 20, t, color=ORANGE, size=7.0)
        para(c, b, x + 10, 66, cw - 20, size=7.2, lead=9.2, color=MUTED, max_lines=2)


def s08_competition(c):
    slide(c, 8, "07 · PHÂN TÍCH CẠNH TRANH",
          "Không Một Đối thủ Nào Sở hữu Kiểm định & Khóa Thanh khoản theo Phiên bản",
          "Khảo sát Web2 Portals, Web3 Gaming, Agent/Meme Launchpads và Social Trading Apps "
          "(số liệu thực chứng 2025–2026).")

    cols = ["Tiêu chí Cốt lõi", "Game9K", "Poki / Crazy", "B3 / BSMNT", "Virtuals", "Pump.fun", "FOMO App"]
    rows = [
        ("Chơi Web tức thì (0 ví, 0 cài)", "CÓ (chuẩn Poki)", "Có (100M+ MAU)", "Có (thiên Web3)", "Không (Agent)", "Không", "Không"),
        ("Sổ cái Version SHA-256 + Diff", "CÓ (On-chain)", "Nội bộ đóng", "Không (nhãn chữ)", "Không trên curve", "Không", "Không"),
        ("Blind A/B Arena + Fit 500 lượt", "CÓ (Độc quyền)", "Chỉ Fit nội bộ", "Không (sao gộp)", "Chỉ DAO hậu kỳ", "Không", "Không (PnL)"),
        ("Launchpad khóa theo Version", "CÓ (M1→M4)", "Không có", "Không ($B3 chung)", "Không (phẳng)", "Không (phẳng)", "Không có"),
        ("Chống Sniper bằng PoP + thoát sớm", "CÓ (24h + 1–12%)", "N/A", "Không", "Thuế theo phút", "Không", "Không"),
        ("Bảo hiểm Ragequit & Doanh thu Kép", "CÓ (100% + Ads/SOL)", "Chỉ Ads USD", "Không", "Ragequit", "Chỉ phí Web3", "Chỉ phí Web3"),
    ]
    y = table(c, M, 392, W - 2 * M, cols, rows,
              col_w=[212, 152, 128, 128, 110, 96, 50], size=7.9, row_h=25, head_h=28,
              cell_colors={(i, 1): GREEN for i in range(6)})

    notes = [
        ("FOMO (fomo.family) → 0% Version", "$33,7M rev/12 tháng, Series B $75M. Chấm PnL trader, rủi ro mua đuổi cá voi. Là kênh phân phối thanh khoản miễn phí cho token Game9K hậu M4.", PURPLE),
        ("Virtuals (fun.virtuals) → 0% Curve Gate", "Curve 42K VIRTUAL mở phẳng ngay từ v0.1, không bắt buộc thắng bản cũ hay Ragequit → 85% agent tốt nghiệp chết.", BLUE),
        ("B3 / BSMNT.fun → Chỉ Nhãn Trang trí", "Nhúng URL ngoài qua JWT (6M+ ví); dòng “Version 0.1.0” chỉ là chữ tĩnh, sao đánh giá cộng gộp cả đời.", ORANGE),
    ]
    cw = (W - 2 * M - 2 * 12) / 3
    for i, (t, b, col) in enumerate(notes):
        x = M + i * (cw + 12)
        card(c, x, 104, cw, 100, accent=col, fill=CARD)   # clears the table (ends 214)
        yy = card_head(c, x + 10, 188, cw - 20, t, color=col, size=7.6)
        para(c, b, x + 10, yy - 4, cw - 20, size=7.7, lead=10.4, color=MUTED, max_lines=5)


def s09_governance(c):
    slide(c, 9, "08 · LUẬN ĐIỂM KINH DOANH & KỶ LUẬT QUẢN TRỊ",
          "Tại sao “Gate-First” Thắng “Infra-First” — Và Hiến pháp Bảo vệ Play-Gate",
          "Bài học triệu đô từ Akerlof (Market for Lemons): xây thêm tầng cho trung tâm thương mại "
          "không cứu được việc cho phép bán hàng giả.")

    left_w = (W - 2 * M) * 0.45
    card(c, M, 74, left_w, 298, accent=RED, fill=CARD)
    card_head(c, M + 14, 354, left_w - 28, "MÔ HÌNH CŨ: INFRA-FIRST", color=RED, size=8.0)
    drawstr(c, M + 14, 316, "85% chết lâm sàng", font=FB, size=24, color=RED)
    facts = [
        ("85% chết", "1.232 AI agent tốt nghiệp tại Base; chỉ 6 dự án giữ thanh khoản >$1M/30 ngày."),
        ("94,4% không có việc", "44.052 agent đăng ký ACP để săn thưởng, chỉ 2.470 từng có khách thật."),
        ("$345.197 → $5,48", "Phí thương mại ACP sụt 99,998% từ 03/2026 xuống 09/2026."),
        ("0,36% tốt nghiệp", "Mở rộng sang Robinhood Chain (25.833 token): 64,5% không có nổi lệnh thứ hai."),
    ]
    bullets(c, facts, M + 14, 294, left_w - 28, size=7.9, lead=10.4, gap=3.0,
            mark_color=RED, prefix_own_line=True)
    drawstr(c, M + 14, 86, "Nguồn: OwnYourMind.ai (10/2026), Chainward.ai (09/2026), DeFiLlama",
            font=F, size=6.8, color=DIM)

    rx = M + left_w + 16
    rw = W - M - rx
    card(c, rx, 74, rw, 298, accent=GREEN, fill=CARD)
    card_head(c, rx + 14, 354, rw - 28, "GAME9K: 6 CƠ CHẾ TỰ KHÓA TAY", color=GREEN, size=8.0)
    mech = [
        ("1. Tách Kinh doanh khỏi Kiểm định:", "đội Growth/BD không có quyền sửa ngưỡng Player Fit, điểm Arena hay danh sách PoP."),
        ("2. Ghi bằng chứng lên Solana:", "mỗi lần mở mốc công khai VPH, retention, thắng Arena & hash báo cáo on-chain."),
        ("3. Similarity Guard:", "chặn tái sinh rác xuyên tựa game — trùng lặp ≥ 92% với dự án đã Stalled thì giao dịch tạo dự án thất bại nguyên tử. (YP §2.2)"),
        ("4. Φ_prog — chống deadlock:", "bản Genesis k=1 được miễn cụm vị từ đấu trường (không có bản cũ để so), nhưng không miễn bất kỳ ngưỡng chất lượng nào. (YP §4.2)"),
        ("5. Tự khóa tay On-Chain (90d):", "nâng cấp cần Squads 4/7 + timelock 48h, khóa terms_hash và đóng băng bất biến sau 90 ngày."),
        ("6. KPI Bắc Đẩu:", "thưởng theo giờ chơi & game sống >90 ngày — không đếm số token tạo ra."),
    ]
    bullets(c, mech, rx + 14, 320, rw - 28, size=7.2, lead=9.3, gap=4.0,
            prefix_own_line=True, mark_color=GREEN)


def s10_business(c):
    slide(c, 10, "09 · MÔ HÌNH KINH DOANH ĐÔI & HÀO KINH TẾ",
          "Hai Động cơ Doanh thu Bổ trợ Xuyên Chu kỳ & Khóa chặt Lợi thế Cạnh tranh",
          "Quảng cáo Web (USD) nuôi sống công ty qua mọi mùa đông crypto; Launchpad & LP trên Solana (SOL) "
          "tạo biên lợi nhuận cao khi thị trường sôi động.")

    cw = (W - 2 * M - 14) / 2
    engines = [
        ("ĐỘNG CƠ 1 · PHÍ GIAO THỨC ON-CHAIN (SOL)", BLUE,
         [("Phí VGBC 0,50%:", "thu trên mọi lệnh Mua/Bán + 10% quỹ phạt xả sớm."),
          ("Phí Tốt nghiệp M4:", "1,50 SOL cố định khi dự án niêm yết thành công."),
          ("Phí Locked DEX LP:", "tích lũy thụ động từ danh mục game sống khỏe."),
          ("Bản chất:", "doanh thu tỷ lệ nghịch với đầu cơ — chúng tôi KHÔNG dự phóng volume lướt sóng.")]),
        ("ĐỘNG CƠ 2 · QUẢNG CÁO WEB & B2B (FIAT USD)", GREEN,
         [("Chia sẻ Ads 50/50:", "chuẩn Poki, từ Rewarded/Commercial Ads trên lưu lượng cổng."),
          ("0% phí traffic tự mang về:", "studio hưởng trọn 100% traffic riêng."),
          ("Tài trợ mùa giải & B2B:", "gói chẩn đoán playtest & tài trợ Arena/Squads."),
          ("Bản chất:", "dòng tiền pháp định KHÔNG phụ thuộc giá token — chiếm 62% doanh thu Năm 1.")]),
    ]
    for i, (title, col, pts) in enumerate(engines):
        x = M + i * (cw + 14)
        card(c, x, 300, cw, 112, accent=col, fill=CARD)
        card_head(c, x + 14, 394, cw - 28, title, color=col, size=8.0)
        bullets(c, pts, x + 14, 362, cw - 28, size=7.9, lead=10.4, gap=2.8, mark_color=col)

    # TOWS
    y2 = 276
    c.setFont(FB, 7.6)
    c.setFillColor(GREEN)
    drawstr(c, M, y2, "MA TRẬN SWOT → HÀNH ĐỘNG CHUYỂN HÓA LỢI THẾ (TOWS EXECUTION)")
    tows = [
        ("S + O · Chiếm lĩnh Nguồn cung",
         "Tiên phong độc quyền × sóng AI Games × lợi thế studio VN/SEA → mở Version Jam hàng tháng nạp 100–200 game M0.", BLUE),
        ("W + O · Giải bài toán Cold-Start",
         "Cần đủ 500 người chơi chấm Fit → chạy SPARK & Squads trước 1 tháng khi mở Launchpad.", GREEN),
        ("S + T · Chống Copy & Click-Farm",
         "Pump.fun kẹt Innovator’s Dilemma (sống nhờ volume rác), không thể copy kho dữ liệu Fit & mạng PoP.", PURPLE),
        ("W + T · An ninh & Tuân thủ Pháp lý",
         "Tuân thủ NQ 05/2025/NQ-CP bằng Tách Cầu/Cung (Web2 dữ liệu · Web3 vốn) + Off-Chain Fallback.", ORANGE),
    ]
    cw2 = (W - 2 * M - 3 * 10) / 4
    for i, (t, b, col) in enumerate(tows):
        x = M + i * (cw2 + 10)
        card(c, x, y2 - 118, cw2, 110, accent=col, fill=CARD_ALT)
        yy = card_head(c, x + 10, y2 - 16, cw2 - 20, t, color=col, size=7.4)
        para(c, b, x + 10, yy - 3, cw2 - 20, size=7.5, lead=10.0, color=MUTED, max_lines=5)

    box(c, M, 52, W - 2 * M, 78,
        "TẠI SAO HAI ĐỘNG CƠ KHÔNG THỂ TÁCH RỜI",
        "Dòng SOL co giãn theo chu kỳ crypto và biến mất khi thị trường nguội; dòng USD (Ads + B2B) "
        "gần như phẳng và tích lũy theo lưu lượng, không phụ thuộc giá token. Tổ hợp này cho phép công ty "
        "vẫn có doanh thu trong mùa đông và bùng nổ khi thanh khoản quay lại — cấu trúc hai động cơ chính là "
        "hào kinh tế: bên copy chỉ sao chép được một nửa.",
        accent=GREEN, title_size=8.6, body_size=8.0)


def s11_roadmap(c):
    slide(c, 11, "10 · KIẾN TRÚC GỌI VỐN ĐA VÒNG",
          "Lộ trình 4 Vòng: Pre-Seed $1M → Seed $3M → Series A $12M → Series B $25M",
          "Game9K thực thi kỷ luật Gate-First với chính nguồn vốn của mình: mỗi vòng chỉ mở khi cột mốc "
          "người chơi & doanh thu thực đã đạt. Chấp nhận lỗ 3 năm để xây Data Moat — xem J-Curve.")

    rounds = [
        ("PRE-SEED · ĐANG MỞ", "$1.0M", "$9M Pre / $10M Post Cap · 10,0%", GREEN,
         [("Công cụ:", "Post-Money SAFE + 1:1 Token Warrant (obligor: pháp nhân phi Hoa Kỳ)."),
          ("Runway & Team:", "15 tháng (0 doanh thu) / 24+ tháng (cơ sở) · 8 FTE."),
          ("Burn gộp:", "~$63,3K/tháng (+ $50K dự phòng)."),
          ("Mở khóa Seed:", "Mainnet + 2 kiểm toán · 400K MAU · 120 game M1+ · 24 game M4 sống >90d.")]),
        ("SEED · M12–M15", "$3.0M", "$22M Pre / $25M Post · 12,0%", BLUE,
         [("Công cụ:", "Priced Seed / SAFE + 1:1 Warrant."),
          ("Runway & Team:", "18–21 tháng · 16 FTE."),
          ("Burn gộp:", "~$158K/tháng (+ $150K dự phòng)."),
          ("Mở khóa Series A:", "2,0M MAU · 450 game M1+ · 95 game M4 · doanh thu Y2 $1,126M.")]),
        ("SERIES A · M24–M27", "$12.0M", "$68M Pre / $80M Post · 15,0%", PURPLE,
         [("Công cụ:", "Preferred Equity (tùy chọn TGE hậu lãi)."),
          ("Runway & Team:", "24+ tháng (vẫn trong J-Curve) · 36 FTE."),
          ("Trọng tâm:", "Direct Brand Ads & Flagship M5+."),
          ("Mở khóa Series B:", "6,5M MAU · 260 game M4 · doanh thu Y3 $5,158M.")]),
        ("SERIES B · M36–M42", "$25.0M", "$225M Pre / $250M Post · 10,0%", ORANGE,
         [("Công cụ:", "Growth Equity (mở rộng toàn cầu)."),
          ("Quy mô Team:", "65 FTE (ngang đúng nhân sự Poki)."),
          ("Trọng tâm:", "M&A cổng/studio & AI Apps Protocol."),
          ("Cột mốc Đích:", "20,0M+ MAU · 620 game M4/năm · doanh thu Y4 $18,46M · EBITDA +$3,96M.")]),
    ]
    cw = (W - 2 * M - 3 * 10) / 4
    CARD_TOP, CARD_BOT = 394, 236
    for i, (label, amt, meta, col, pts) in enumerate(rounds):
        x = M + i * (cw + 10)
        card(c, x, CARD_BOT, cw, CARD_TOP - CARD_BOT, accent=col, fill=CARD)
        drawstr(c, x + 12, CARD_TOP - 18, label, font=FB, size=7.2, color=col)
        drawstr(c, x + 12, CARD_TOP - 44, amt, font=FB, size=21, color=TEXT)
        para(c, meta, x + 12, CARD_TOP - 58, cw - 24, size=7.3, lead=9.6, color=MUTED)
        bullets(c, pts, x + 12, CARD_TOP - 84, cw - 24, size=7.6, lead=10.2, gap=3.4, mark_color=col)

    card(c, M, 52, W - 2 * M, 162, accent=GREEN, fill=CARD_ALT)
    card_head(c, M + 14, 194, W - 2 * M - 28,
              "CAP TABLE & LỢI SUẤT NHÀ ĐẦU TƯ SỚM — tổng vốn 4 vòng $41,0M", color=GREEN, size=8.0)
    para(c, "Sau Series B ($250M): Founders 51,50% · ESOP 9,09% · Pre-Seed 6,73% (= $16,83M, 16,8× MOIC) · "
            "Seed 9,18% (= $22,95M, 7,7× MOIC) · Series A 13,50% (2,8×) · Series B 10,00% — chưa cộng upside "
            "từ Token Warrant.", M + 14, 170, W - 2 * M - 28, size=8.4, lead=12.4, color=MUTED)
    para(c, "J-CURVE INFRASTRUCTURE PLAY: chấp nhận lỗ 3 năm đầu để mua Nguồn cung đã qua cổng và Data Moat "
            "(VPH, retention theo từng phiên bản). Điểm hòa vốn thực tế rơi vào NĂM 4 — không sớm hơn.",
         M + 14, 132, W - 2 * M - 28, font=FB, size=8.6, lead=12.2, color=GREEN)
    para(c, "Đây là kịch bản cơ sở khi cả bốn vòng đóng đúng cột mốc; các vòng sau chỉ mở khi cột mốc của vòng "
            "trước đã đạt — nên đường cong có thể chậm hơn, nhưng không thể bị bơm phồng bằng chi phí đốt trước.",
         M + 14, 92, W - 2 * M - 28, size=7.6, lead=10.6, color=DIM)


def s12_usefunds(c):
    slide(c, 12, "11 · PHÂN BỔ NGUỒN VỐN CHI TIẾT",
          "Kỷ luật Từng Đồng Vốn: Pre-Seed $1,000,000 & Seed $3,000,000",
          "Tối đa hóa ngân sách cho kỹ thuật lõi, kiểm toán bảo mật và tạo thanh khoản cho studio – "
          "game thủ thật; 0% chi phí phô trương.")

    col_w = (W - 2 * M - 14) / 2
    blocks = [
        ("VÒNG PRE-SEED · $1,000,000 (ĐANG MỞ — 8 FTE)", GREEN, [
            ("1. Kỹ thuật Cốt lõi, Edge & AI Anti-Bot", "$400,000", "40%",
             "5 kỹ sư AI-Agile (Web, Sandbox, Arena, Solana Rust, Anti-Bot) + R2/Supabase/Helius RPC."),
            ("2. Thu hút Studio & Version Jams", "$250,000", "25%",
             "6 kỳ Version Jam ($120K) · 20 Genesis Grants ($80K, $4K/studio) · DevRel & SDK ($50K)."),
            ("3. Bảo mật, 2 Kiểm toán & Pháp lý", "$150,000", "15%",
             "2 audits cho 3 Anchor programs ($90K) · Bug Bounty ($25K) · pháp nhân & geo-filter ($35K)."),
            ("4. Cộng đồng Game thủ (Demand)", "$150,000", "15%",
             "Micro-creators TikTok/YT/X ($80K) · Mystery Tile & Squads ($45K) · Solana ($25K)."),
            ("5. Quỹ Dự phòng Vận hành", "$50,000", "5%",
             "Đệm thanh khoản bảo đảm 15 tháng runway 0 doanh thu."),
        ]),
        ("VÒNG SEED · $3,000,000 (M12–M15 — 16 FTE)", BLUE, [
            ("1. Mở rộng Nền tảng, Engine SDK & ML", "$1,050,000", "35%",
             "10 kỹ sư: WebGPU 60fps, plugin Godot/Unity/GDevelop/AI, multiplayer, ML chống click-farm."),
            ("2. Quỹ Đồng Phát triển 100+ Studio", "$900,000", "30%",
             "Tài trợ cột mốc M2→M4, hút studio Poki/CrazyGames/itch.io & Global Championship."),
            ("3. Tăng trưởng Quốc tế & Ad-Tech", "$600,000", "20%",
             "Mở rộng US/EU/KR/BR/SEA, header-bidding Rewarded Ads, tích hợp Phantom/Jupiter."),
            ("4. Kiểm toán v2, SOC2 & Pháp lý", "$300,000", "10%",
             "Kiểm toán nâng cấp + formal verification, SOC2 & tuân thủ đa thị trường."),
            ("5. Quỹ Dự phòng Chiến lược", "$150,000", "5%",
             "Miễn nhiễm mùa đông crypto — duy trì J-Curve mà không phải nới Play-Gate."),
        ]),
    ]
    Y_TOP, Y_BOT = 402, 128          # card band; spacing is distributed, not guessed
    for bi, (title, col, items) in enumerate(blocks):
        x = M + bi * (col_w + 14)
        card(c, x, Y_BOT, col_w, Y_TOP - Y_BOT, accent=col, fill=CARD)
        card_head(c, x + 12, Y_TOP - 16, col_w - 24, title, color=col, size=7.8)
        # measure, then spread the leftover height as extra gap between items
        heights = [13.0 + len(wrap(d, F, 7.2, col_w - 24)) * 9.6 for _, _, _, d in items]
        slack = (Y_TOP - 34) - Y_BOT - 12 - sum(heights)
        gap = max(4.0, slack / max(1, len(items) - 1))
        yy = Y_TOP - 34
        for name, amt, pct, detail in items:
            drawstr(c, x + 12, yy, name, font=FB, size=7.9, color=TEXT)
            drawright(c, x + col_w - 12, yy, amt, font=FB, size=7.9, color=col)
            drawright(c, x + col_w - 12 - sw_mixed(amt, FB, 7.9) - 6, yy, pct,
                      font=F, size=7.4, color=DIM)
            para(c, detail, x + 12, yy - 11, col_w - 24, size=7.2, lead=9.6, color=MUTED)
            yy -= heights[items.index((name, amt, pct, detail))] + gap

    box(c, M, 44, W - 2 * M, 66,
        "HAI VÒNG SAU · CÙNG MỘT NGUYÊN TẮC: KHÔNG ĐỐT TIỀN VÀO TĂNG TRƯỞNG TRẢ TRƯỚC",
        "SERIES A · $12M:  30% Phân phối & Direct Brand Ads · 30% Flagship AA-Indie & LiveOps M5+ · "
        "25% Protocol v3 & AI Playtest Co-Pilot · 10% Pháp lý/An ninh · 5% Dự phòng.\n"
        "SERIES B · $25M:  35% M&A cổng/studio/ad-tech · 30% mở rộng giao thức sang AI Consumer Apps · "
        "20% thương hiệu 20M+ MAU · 10% R&D WebGPU · 5% Dự phòng.",
        accent=PURPLE, title_size=7.8, body_size=7.4)


def s13_pnl(c):
    slide(c, 13, "12 · DỰ PHÓNG TÀI CHÍNH 4 NĂM (BOTTOM-UP)",
          "Từ $0,214M (Năm 1) → $18,46M (Năm 4): J-Curve có kiểm soát, hòa vốn Năm 4",
          "Mọi dòng suy ra từ ba ràng buộc cứng: trần đường cong $11.888 huy động/game · eCPM ĐNA "
          "$11,25 ròng/1.000 VPH · burn Pre-Seed $63.300/tháng.", accent=ORANGE)

    # ---- chart (left) ----
    cx, cy, cw_, ch = M, 120, 290, 246
    card(c, cx, cy, cw_, ch, accent=BLUE, fill=CARD)
    drawstr(c, cx + 12, cy + ch - 22, "DOANH THU RÒNG & EBITDA (Triệu USD)",
            font=FB, size=7.4, color=BLUE)
    rev = [0.214, 1.126, 5.158, 18.46]
    eb = [-0.546, -0.974, -0.642, 3.96]
    labels = ["Năm 1", "Năm 2", "Năm 3", "Năm 4"]
    base = cy + 58
    maxv = 18.46
    bw = 34
    for i, v in enumerate(rev):
        x = cx + 28 + i * 64
        hgt = (v / maxv) * 150
        c.setFillColor(BLUE if i < 3 else GREEN)
        c.rect(x, base, bw, hgt, stroke=0, fill=1)
        drawcentre(c, x + bw / 2, base + hgt + 7, f"${v:g}M", font=FB, size=7.2, color=TEXT)
        drawcentre(c, x + bw / 2, base - 20, f"{eb[i]:+.2f}", font=FB, size=6.8,
                   color=GREEN if eb[i] > 0 else RED)
        drawcentre(c, x + bw / 2, base - 32, labels[i], font=F, size=6.6, color=DIM)
    drawstr(c, cx + 12, cy + 12, "Số dưới chân cột = EBITDA. Hòa vốn rơi vào Năm 4.",
            font=F, size=6.3, color=DIM)

    # ---- table (right): 10 rows must fit above the note boxes ----
    tx = cx + cw_ + 14
    tw = W - M - tx
    cols = ["Chỉ số", "Năm 1", "Năm 2", "Năm 3", "Năm 4"]
    rows = [
        ("MAU cuối kỳ", "400K", "2,0M", "6,5M", "20,0M"),
        ("VPH / năm", "2,93M", "24M", "100M", "320M"),
        ("Game M1 / tốt nghiệp M4", "120 / 24", "450 / 95", "1.200 / 260", "2.800 / 620"),
        ("1. Phí VGBC & Anti-Dump", "$22K", "$122K", "$432K", "$1,34M"),
        ("2. Phí M4 & Locked DEX LP", "$59K", "$244K", "$726K", "$1,92M"),
        ("3. Quảng cáo Web (net 50%)", "$33K", "$360K", "$2,50M", "$11,2M"),
        ("4. B2B, Giải đấu & Grants", "$100K", "$400K", "$1,50M", "$4,0M"),
        ("TỔNG DOANH THU RÒNG", "$214K", "$1,126M", "$5,158M", "$18,46M"),
        ("OpEx & Grants", "$760K", "$2,10M", "$5,80M", "$14,5M"),
        ("EBITDA", "−$546K", "−$974K", "−$642K", "+$3,96M"),
    ]
    yb = table(c, tx, 384, tw, cols, rows,
               col_w=[tw * 0.40, tw * 0.15, tw * 0.15, tw * 0.15, tw * 0.15],
               size=7.5, row_h=22.4, head_h=25,
               aligns=["l", "r", "r", "r", "r"],
               cell_colors={(7, 1): GREEN, (7, 2): GREEN, (7, 3): GREEN, (7, 4): GREEN,
                            (9, 1): RED, (9, 2): RED, (9, 3): RED, (9, 4): GREEN})

    # ---- note boxes under both columns ----
    box(c, M, 46, (W - 2 * M - 14) * 0.55, 60,
        "J-CURVE INFRASTRUCTURE PLAY",
        "Chấp nhận lỗ 3 năm đầu để xây Data Moat (VPH, retention theo từng phiên bản). "
        "Điểm hòa vốn thực tế rơi vào Năm 4 — không sớm hơn, và không phải một mục tiêu ngắn hạn.",
        accent=ORANGE, title_size=8.0, body_size=7.5)

    dx = M + (W - 2 * M - 14) * 0.55 + 14
    dw = W - M - dx
    c.setFillColor(HexColor("#12100C"))
    c.setStrokeColor(DIM)
    c.setLineWidth(0.6)
    c.roundRect(dx, 46, dw, 60, 3, stroke=1, fill=1)
    drawstr(c, dx + 10, 90, "DISCLAIMER — KHOẢNG TRỐNG ĐÃ BIẾT", font=FB, size=6.7, color=DIM)
    para(c, "OpEx và quy mô các vòng gọi vốn là ƯỚC TÍNH CHIẾN LƯỢC, sẽ hiệu chỉnh theo thực tế vận hành — "
            "khai báo là Known Gaps trong YP §12.3. Dòng doanh thu suy ra từ trần kỹ thuật, không phải cam kết thị trường.",
         dx + 10, 78, dw - 20, size=6.6, lead=9.0, color=DIM)


def s14_ask(c):
    slide(c, 14, "13 · LỘ TRÌNH THỰC THI 12 THÁNG & LỜI MỜI ĐẦU TƯ",
          "Kiến trúc Đã Sẵn sàng — Mở Vòng Pre-Seed $1,000,000 Ngay Hôm nay",
          "PRD, 31 bảng DB, API/SDK và 3 hợp đồng Solana Anchor đã hoàn thiện ở mức đặc tả; "
          "toàn bộ số liệu tài chính tái lập được bằng một lệnh.", accent=GREEN)

    # readiness
    lw = (W - 2 * M) * 0.48
    card(c, M, 248, lw, 156, accent=GREEN, fill=CARD)
    card_head(c, M + 14, 388, lw - 28, "HIỆN TẠI · SẴN SÀNG (M0)", color=GREEN, size=7.8)
    bullets(c, [
        ("Master PRD, UX Flows & 31-table Schema", ""),
        ("REST/SSE & Poki-compatible Game SDK", ""),
        ("Yellow Paper v1.0: 12 bất biến, 6 định lý, 10.000 fuzz ops", ""),
        ("Whitepaper v1.5, C4/STRIDE & lộ trình S0–S12", ""),
        ("BÁO CÁO TỰ ĐỘNG TÁI LẬP:", "python3 scripts/verify_protocol_math.py → S1–S9 + 10.000 phép toán ngẫu nhiên: PASS 100%."),
    ], M + 14, 360, lw - 28, size=7.6, lead=10.0, gap=1.8)

    # phases
    px = M + lw + 16
    pw = W - M - px
    phases = [
        ("PHASE 1 · PORTAL & ARENA (M1–M3)", "Ra mắt Cổng Game, Inspector & Fit Funnel · Blind Version Arena + SPARK/Squads · 2 kiểm toán · KPI: 100+ game M0 · 50K+ MAU.", BLUE),
        ("PHASE 2 · GENESIS LAUNCH (M4–M6)", "Mainnet Launchpad: 20 game Genesis · 24h PoP Window, Exit Tax & Ragequit · lứa M4 đầu lên DEX + Ads 50/50.", PURPLE),
        ("PHASE 3 · SCALE → SEED (M7–M12)", "Plugin 1-click Godot/Unity · LiveOps M5+ & mở rộng quốc tế · KPI: 400K MAU · 24 M4 · mở khóa Seed $3,0M @ $25M Post.", ORANGE),
    ]
    yy = 404
    for t, b, col in phases:
        card(c, px, yy - 46, pw, 44, accent=col, fill=CARD_ALT)
        drawstr(c, px + 10, yy - 15, t, font=FB, size=7.3, color=col)
        para(c, b, px + 10, yy - 28, pw - 20, size=6.9, lead=9.0, color=MUTED, max_lines=2)
        yy -= 50

    # the ask
    card(c, M, 60, W - 2 * M, 176, accent=GREEN, fill=CARD)
    drawstr(c, M + 18, 214, "THE ASK · VÒNG PRE-SEED ĐANG MỞ", font=FB, size=8.0, color=GREEN)
    drawstr(c, M + 18, 178, "$1,000,000 USD", font=FB, size=26, color=TEXT)
    drawstr(c, M + 18, 160, "Post-Money Valuation Cap $10,0M  ·  10,0% pha loãng  ·  "
                            "Post-Money SAFE + 1:1 Protocol Token Warrant", font=F, size=9.0, color=MUTED)
    drawstr(c, M + 18, 146, "Data Room & Living Architecture:  github.com/khanhlegood1/GameFun",
            font=F, size=8.0, color=DIM)

    bullets(c, [
        ("Sử dụng vốn kỷ luật:", "40% Eng/Anti-Bot ($400K) · 25% Studio/Jams ($250K) · 15% Audit/Legal ($150K) · 15% UA ($150K) · 5% Dự phòng ($50K)."),
        ("Runway an toàn kép:", "15 tháng ở kịch bản 0 doanh thu; 24+ tháng ở kịch bản cơ sở. Chưa hòa vốn trong năm 1 — J-Curve tới Năm 4."),
        ("Lộ trình nâng hạng:", "Seed $3M ($25M) → Series A $12M ($80M) → Series B $25M ($250M, tương đương 16,8× MOIC cho Pre-Seed)."),
        ("Ai phát hành warrant:", "pháp nhân phi Hoa Kỳ giữ token là obligor; 9K Holdings, Inc. bảo lãnh thực thi qua Token Rights Agreement. Pháp nhân phát hành CHƯA thành lập — phải chốt trước khi ký SAFE."),
    ], M + 18, 132, W - 2 * M - 36, size=7.6, lead=10.0, gap=1.6)


SLIDES = [s01_cover, s02_problem, s03_solution, s04_why_regulatory, s05_dual_curve,
          s06_sol_flows, s07_shield, s08_competition, s09_governance, s10_business,
          s11_roadmap, s12_usefunds, s13_pnl, s14_ask]


def register_fonts_deck():
    """WB.register_fonts() plus a bold DejaVu for exotic glyphs in bold runs."""
    WB.register_fonts()
    src = os.path.join(WB.FONTDIR, "DejaVuSans.ttf")
    bold_src = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    dst = os.path.join(WB.FONTDIR, "DejaVuSans-Bold.ttf")
    if os.path.exists(bold_src) and not os.path.exists(dst):
        import shutil
        shutil.copyfile(bold_src, dst)
    from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
    pdfmetrics.registerFont(RLTTFont(FALLBACK, src))
    pdfmetrics.registerFont(RLTTFont(FALLBACK_B, dst))
    pdfmetrics.registerFontFamily(FALLBACK, normal=FALLBACK, bold=FALLBACK_B,
                                  italic=FALLBACK, boldItalic=FALLBACK_B)


def build(out_path: str, deterministic: bool = True) -> int:
    """deterministic=True pins /CreationDate & /ID so a rebuild is byte-identical
    (CI can then diff the PDF instead of eyeballing it)."""
    register_fonts_deck()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    # invariant=1 pins the timestamp and the /ID array -> byte-identical rebuilds
    c = canvas.Canvas(out_path, pagesize=(W, H), invariant=1 if deterministic else 0)
    c.setTitle("Game9K — Investor Pitch Deck v1.5 (Pre-Seed $1M)")
    c.setAuthor("Game9K")
    c.setSubject("Version-Synced Game Capital Launchpad — Pre-Seed $1,000,000")
    c.setKeywords("Solana, GameFi, Launchpad, Version Gate, Proof of Play")
    for fn in SLIDES:
        fn(c)
        c.showPage()
    c.save()
    return len(SLIDES)


def main(argv: list[str]) -> int:
    out = argv[1] if len(argv) > 1 else "docs/Game9K-Pitch-Deck.pdf"
    n = build(out)
    print(f"built {out} ({os.path.getsize(out):,} bytes, {n} slides)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
