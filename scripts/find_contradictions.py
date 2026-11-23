#!/usr/bin/env python3
"""find_contradictions.py — tìm chỗ hai tài liệu nói **ngược nhau**, không phải chỗ thiếu.

Vì sao có file này (docs/37):
    Bốn vòng vừa rồi tôi dựng bốn cổng, và cả bốn đều kiểm **sự hiện diện**:
    có nhãn chưa, có owner chưa, có biên bản chưa, có bền chưa. Không cổng nào kiểm
    **mâu thuẫn** — hai câu trong hai tệp, mỗi câu đúng ngữ pháp, cộng lại thì sai.

    Đây không phải phỏng đoán. Khi soát bằng mắt (docs/37 §2) tôi tìm được ba cặp
    mâu thuẫn thật trong repo, và cả ba đều **đã được vá ở dòng chữ nhưng chưa được
    khoá bằng máy** — nghĩa là lần sửa tiếp theo sẽ làm chúng quay lại.

Bốn cặp `(A, B)` — mỗi cặp là **hai khẳng định không thể cùng đúng**:

  1. **"0% chênh lệch giá"** vs **sai lệch đã công bố `4.27 × 10⁻¹²`**
     `0%` là một tuyên bố tuyệt đối; `4.27e-12` là một số đo. Cùng một câu không thể
     vừa "0%" vừa "4.27e-12". Câu đúng: *"sai lệch ≤ 1 lamport"*.
     **Luật:** một tệp có `0%` chênh lệch **phải** có kèm một trong các cụm nới nghĩa
     (`sai lệch`, `lamport`, `≈`, `tương đương`) **trong cùng tệp**.

  2. **`LCB_0.95 > 0.50`** vs **`arena_lcb_bps > 5,000 bps`**
     `5,000/10,000 = 0.50`, và `> 5,000` cộng với làm tròn `floor` cho phép kết quả
     **đúng bằng 0.50** — trong khi điều kiện thắng là **lớn hơn** `0.50`. Hai câu
     lệch nhau đúng ở biên, và biên là nơi mọi thứ quyết định.

  3. **`escrow`** — ba con số khác nhau cho cùng một tên: `60,1998` (trước phí tốt
     nghiệp `F_grad`), `60.221994` (sau `F_grad`), và escrow **rút gọn** của mô hình
     bổ đề. **Luật:** mỗi lần `60,1998` xuất hiện phải kèm `F_grad` hoặc `trước phí`
     trong cùng dòng.

  4. **`programs/` trống** vs bất kỳ khẳng định nào về chương trình đã chạy
     Nếu `programs/` rỗng thì mọi câu "đã triển khai", "đã chạy trên devnet",
     "on-chain đã" đều sai. **Luật:** khi `programs/` rỗng, các cụm đó bị cấm.

Ba chế độ:

    python3 scripts/find_contradictions.py            # 4 cặp
    python3 scripts/find_contradictions.py --audit     # liệt kê từng chỗ khớp
    python3 scripts/find_contradictions.py --selftest  # CI

Chỉ thư viện chuẩn, không mạng.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Tệp được quét: tài liệu công bố + mọi `docs/NN-*.md`.
#
# MIỄN TRỪ THEO CÚ PHÁP, KHÔNG THEO TÊN TỆP: một dòng có `❌` là dòng **bác** câu đó
# (docs/33 §3 quy ước như vậy, và `check_claims.py` dùng đúng dấu hiệu này). Nếu miễn
# theo tên tệp thì `docs/37` — tài liệu phải dẫn lại bốn câu sai để dạy chúng sai ở
# đâu — sẽ được miễn **toàn bộ**, và một câu sai thật viết vào đó sẽ lọt. Miễn theo
# `❌` chỉ miễn **đúng dòng đang bác**, và đọc được bằng mắt.
SOURCES = ["WHITEPAPER.md", "YELLOWPAPER.md", "PRD.md"]
REBUTTED = "❌"

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def lines_of(path: Path):
    """Bỏ khối mã — một công thức trong ``` không phải một lời khẳng định."""
    in_code = False
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        yield i, line


def files() -> list[Path]:
    out = [DOCS / n for n in SOURCES]
    out += sorted(DOCS.glob("[0-9][0-9]-*.md"))
    return [p for p in out if p.exists()]


def asserted(path: Path):
    """Các dòng mang tính KHẲNG ĐỊNH: bỏ khối mã, và bỏ dòng có `❌` (đang bác)."""
    for n, line in lines_of(path):
        if REBUTTED in line:
            continue
        yield n, line


# ------------------------------------------------------------------ cặp 1
ZERO_GAP = re.compile(r"0%\s*chênh\s*lệch|chênh\s*lệch\s*(?:giá\s*)?0%|Zero-MEV|không chênh", re.I)
HEDGE = re.compile(r"sai lệch|lamport|≈|tương đương|gần đúng|xấp xỉ|\bMEV\b", re.I)


def pair_zero_gap() -> None:
    """`0%` chênh lệch phải đi kèm một cụm nới nghĩa trong CÙNG tệp."""
    for path in files():
        rows = list(asserted(path))
        text = "\n".join(l for _, l in rows)
        if not ZERO_GAP.search(text):
            continue
        check(bool(HEDGE.search(text)),
              f"{path.name}: có câu '0% chênh lệch' nhưng KHÔNG có cụm nới nghĩa nào "
              "('sai lệch', 'lamport', '≈') — 0% tuyệt đối không cùng đúng với "
              "sai lệch đã công bố 4.27e-12 (docs/37 §2.1)")
        # Kiểm ở mức CÂU, trong chính dòng đó và 1 dòng lân cận (bảng có thể xuống dòng).
        for n, l in ((n, l) for n, l in rows if ZERO_GAP.search(l)):
            window = "\n".join(x for k, x in rows if abs(k - n) <= 1)
            check(bool(HEDGE.search(window)),
                  f"{path.name}:{n} câu '0% chênh lệch' không có cụm nới nghĩa trong ±1 dòng "
                  "— người đọc chỉ thấy '0%'")


# ------------------------------------------------------------------ cặp 2
# `5,000 bps` = 0.50 đúng biên, mà điều kiện thắng là **lớn hơn** 0.50. Vì vậy mỗi dòng
# nói `> 5,000 bps` phải kèm ngay cạnh nó cái **vá biên**: floor cộng 1 bps, hoặc `5,001`,
# hoặc `>= 0.5001`. Không có vá ⇒ người đọc cài đúng con số 5.000 và mở cổng ở 0.50.
# Chỉ áp lên dòng **khai báo trường** `arena_lcb_bps` — đó là câu spec. Một đoạn văn
# nhắc *tới* con số để giải thích lỗi biên (như §2.2 của docs/37) không phải một khai
# báo miền giá trị, và bắt nó là bắt oan đúng tài liệu đang dạy cách sửa.
LCB_BPS = re.compile(r"arena_lcb_bps[^\n]*>\s*5[,.]?000\s*bps", re.I)
LCB_FIX = re.compile(r"5[.,]001|\bfloor\b|>=\s*5[.,]001|≥\s*5[.,]001|≥\s*0[.,]5001", re.I)


def pair_lcb() -> None:
    """Biên của điều kiện thắng và biên của trường on-chain phải cùng nghĩa."""
    for path in files():
        rows = list(asserted(path))
        for n, line in rows:
            if not LCB_BPS.search(line):
                continue
            window = "\n".join(x for k, x in rows if abs(k - n) <= 2)
            check(bool(LCB_FIX.search(window)),
                  f"{path.name}:{n} nói `> 5,000 bps` (= 0.50 đúng biên) mà không nói cách "
                  "vá biên (floor +1 bps / `5,001`) trong ±2 dòng — trong khi điều kiện thắng "
                  "là `LCB_0.95 > 0.50` **lớn hơn** (docs/37 §2.2)")


# ------------------------------------------------------------------ cặp 3
ESCROW_OLD = re.compile(r"60[,.]1998")
ESCROW_WHY = re.compile(r"F_\{?\\\\?text\{?grad|F_grad|trước phí|sau phí|trước khi thu", re.I)


def pair_escrow() -> None:
    """`60,1998` phải nói rõ nó là escrow TRƯỚC phí tốt nghiệp."""
    for path in files():
        rows = list(asserted(path))
        for n, line in rows:
            if not ESCROW_OLD.search(line):
                continue
            window = "\n".join(x for k, x in rows if abs(k - n) <= 2)
            check(bool(ESCROW_WHY.search(window)),
                  f"{path.name}:{n} `60,1998` không nói trước/sau `F_grad` — cùng tên "
                  "'escrow' với `60.221994 SOL` đã công bố (docs/37 §2.3)")


# ------------------------------------------------------------------ cặp 4
# Chỉ bắt câu khẳng định về CHÍNH Game9K. "hợp đồng đã triển khai" trong một câu
# GIẢ ĐỊNH ("muốn nới thì phải nâng cấp hợp đồng đã triển khai") là mô tả trạng thái
# tương lai, không phải khẳng định hôm nay đã có code chạy.
# Câu ĐIỀU KIỆN thì không phải khẳng định: "muốn nới thì phải nâng cấp hợp đồng đã
# triển khai", "sau khi triển khai trên Solana" đều mô tả một trạng thái giả định.
CONDITIONAL = re.compile(
    r"\b(?:sau khi|trước khi|nếu|khi|muốn|để|sẽ|giả định|giả sử|kế hoạch|một khi|"
    r"cho đến khi|chưa)\b", re.I)

NO_PROGRAMS = re.compile(
    # (a) có chủ thể rõ ràng
    r"(?:hợp đồng|chương trình|program|contract|code)\s+(?:của\s+)?"
    r"(?:Game9K|chúng tôi|dự án)\s+(?:đã|đều đã)\s+(?:triển khai|deploy|chạy)|"
    # (b) chủ thể là chính dự án
    r"\bGame9K\s+đã\s+(?:triển khai|deploy|chạy)|"
    # (c) không chủ thể nhưng có đích cụ thể — đây là câu khẳng định trơn
    r"(?:hợp đồng|chương trình|program|contract)\s+(?:đã|đều đã)\s+"
    r"(?:triển khai|deploy|chạy)\s+(?:lên|trên)\s+(?:mainnet|devnet|Solana)|"
    r"on-chain đã chạy", re.I)


def pair_no_programs() -> None:
    """`programs/` rỗng ⇒ không được nói chương trình đã chạy."""
    programs = ROOT / "programs"
    empty = (not programs.is_dir()) or not any(programs.iterdir())
    if not empty:
        check(True, "")
        return
    for path in files():
        for n, line in asserted(path):
            if CONDITIONAL.search(line):
                continue
            m = NO_PROGRAMS.search(line)
            check(not m,
                  f"{path.name}:{n} nói «{m.group(0) if m else ''}» trong khi `programs/` rỗng "
                  "— chưa có dòng code nào chạy trên chain (docs/37 §2.4)")


PAIRS = (
    ("0% chênh lệch vs sai lệch 4.27e-12", pair_zero_gap),
    ("LCB > 0.50 vs > 5,000 bps", pair_lcb),
    ("escrow 60,1998 vs 60.221994", pair_escrow),
    ("programs/ rỗng vs 'đã triển khai'", pair_no_programs),
)


def audit() -> int:
    print("\nBỐN CẶP MÂU THUẪN — mỗi cặp là hai câu không thể cùng đúng\n")
    for name, fn in PAIRS:
        saved_pass, saved_fail = PASSES, list(FAILS)
        globals()["PASSES"] = 0
        FAILS.clear()
        try:
            fn()
        except Exception as exc:                       # noqa: BLE001
            FAILS.append(str(exc))
        status = "✗ " + FAILS[0] if FAILS else "✓ không mâu thuẫn"
        print(f"  {name}\n    {status}")
        globals()["PASSES"] = saved_pass
        FAILS[:] = saved_fail
    print(f"\n{len(PAIRS)} cặp · {len(files())} tệp được quét")
    return 0


def selftest() -> int:
    """4 phép phá (mỗi cặp) + 1 đối chứng, trên corpus tạm."""
    global DOCS

    saved_docs = DOCS

    def run(text: str, fn) -> list[str]:
        global DOCS
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        (tmp / "docs").mkdir()
        (tmp / "docs" / "WHITEPAPER.md").write_text(text, encoding="utf-8")
        DOCS = tmp / "docs"
        FAILS.clear()
        globals()["PASSES"] = 0
        try:
            fn()
        except Exception as exc:                        # noqa: BLE001
            FAILS.append(str(exc))
        return list(FAILS)

    cases = [
        ("P1 '0% chênh lệch' không nới nghĩa",
         "Thanh khoản chuyển lên DEX với 0% chênh lệch giá.\n", pair_zero_gap,
         "cụm nới nghĩa"),
        ("P2 LCB > 0.50 nhưng trường on-chain > 5,000 bps",
         "Điều kiện thắng: `LCB_0.95 > 0.50`.\n"
         "152..154 ( 2 B) : arena_lcb_bps = LCB_0.95 * 10,000 (> 5,000 bps cho M2+)\n",
         pair_lcb, "vá biên"),
        ("P3 escrow 60,1998 không nói trước/sau phí",
         "| Escrow | 60,1998 SOL |\n", pair_escrow, "F_grad"),
        ("P4 nói 'đã triển khai' khi programs/ rỗng",
         "Hợp đồng đã triển khai lên mainnet.\n", pair_no_programs, "rỗng"),
    ]

    ok = 0
    try:
        for name, text, fn, expect in cases:
            fails = run(text, fn)
            hits = [f for f in fails if expect in f]
            if hits:
                ok += 1
                print(f"  ✓ {name} → đỏ: {hits[0][:110]}")
            else:
                print(f"  ✗ {name} → LỌT (FAILS={fails})")
        # Đối chứng: câu nới nghĩa đầy đủ thì phải SẠCH.
        controls = [
            ("P5 đối chứng: '0%' có nới nghĩa",
             "Thanh khoản chuyển lên DEX, sai lệch ≤ 1 lamport (tương đương 0% "
             "chênh lệch giá).\n", pair_zero_gap),
            # Câu ĐIỀU KIỆN không phải khẳng định "đã có code chạy" — nếu bắt oan thì
            # mọi câu mô tả tương lai trong whitepaper đều đỏ, và cổng sẽ bị tắt.
            ("P6 đối chứng: 'hợp đồng đã triển khai' trong câu giả định",
             "Muốn nới điều kiện thì phải nâng cấp hợp đồng đã triển khai.\n",
             pair_no_programs),
            # `> 5,000 bps` ĐI KÈM vá biên thì hợp lệ — cổng phải chấp nhận cách viết đúng.
            ("P7 đối chứng: '> 5,000 bps' có vá biên",
             "arena_lcb_bps = LCB_0.95 * 10,000 (> 5,000 bps; floor ⇒ >= 5,001)\n",
             pair_lcb),
        ]
        for name, text, fn in controls:
            fails = run(text, fn)
            if not fails:
                ok += 1
                print(f"  ✓ {name} → sạch")
            else:
                print(f"  ✗ {name} → BẮT OAN: {fails[0]}")
    finally:
        DOCS = saved_docs

    total = len(cases) + len(controls)
    if ok != total:
        print(f"CONTRADICTION SELFTEST: FAIL — {ok}/{total} phép thử đúng chiều")
        return 1
    print(f"CONTRADICTION SELFTEST: PASS — {ok}/{total} phép thử đúng chiều "
          f"({len(cases)} phép phá + {len(controls)} đối chứng)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Tìm hai câu không thể cùng đúng.")
    ap.add_argument("--audit", action="store_true", help="liệt kê từng cặp")
    ap.add_argument("--selftest", action="store_true", help="kiểm 4 cặp (CI)")
    args = ap.parse_args()

    if args.audit:
        return audit()
    if args.selftest:
        return selftest()

    for _, fn in PAIRS:
        fn()

    if FAILS:
        print(f"CONTRADICTIONS: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(f"CONTRADICTIONS: PASS — {PASSES} kiểm tra · 4 cặp mâu thuẫn · "
          f"{len(files())} tệp được quét")
    return 0


if __name__ == "__main__":
    sys.exit(main())
