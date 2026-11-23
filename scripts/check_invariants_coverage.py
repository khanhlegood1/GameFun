#!/usr/bin/env python3
"""check_invariants_coverage.py — bất biến nào **thực sự có mã**, và bất biến nào chỉ có tên.

Vì sao có file này (docs/38):
    `docs/YELLOWPAPER.md` §8.1 khai **12** bất biến `INV-01..INV-12`.
    `docs/YELLOWPAPER.md` §12.1 dòng `FUZZ` in: *"`0` vi phạm bất biến `INV-01..INV-08`"*.
    `docs/WHITEPAPER.md` §1.3 và `docs/04-solana-smart-contracts.md` §5 dùng **cùng
    những mã số đó cho những bất biến khác nhau**.

    Đó là ba hệ đánh số, và cho tới vòng này **không cổng nào** đối chiếu chúng.
    Hệ quả đọc được: câu "0 vi phạm `INV-01..INV-08`" trong Yellow Paper **không thể
    đúng cũng không thể sai** — nó nói về tám bất biến mà mô hình mô phỏng không có.
    Trước vòng này mã chỉ assert bốn (`INV-01..INV-04`).

Nguyên tắc: **thẻ trong mã là nguồn, câu trong tài liệu là bản in.**
    Mỗi `assert` mang thẻ `INV-nn`; cổng đọc chính các dòng đó. Không ai khai
    "đã kiểm 12 bất biến" bằng văn xuôi mà qua được cổng này.

Năm bất biến của cổng:

  1. **Mọi `INV-nn` được assert trong `scripts/` phải là mã CÓ THẬT trong danh mục
     `docs/YELLOWPAPER.md` §8.1** (đúng 12 mã). Thẻ lạ ⇒ đỏ.
  2. **Mọi câu "N vi phạm bất biến `INV-xx..INV-yy`" phải khớp số mã thực sự được
     assert trong dải đó.** Đây là bất biến bắt đúng lỗi đã có: câu `INV-01..INV-08`
     khi mã chỉ có bốn.
  3. **Ba hệ đánh số phải được khai báo tường minh.** `docs/04` §5 cũng dùng
     `INV-01..INV-08` cho tám bất biến của **program** — nếu `docs/04` không nói ra
     rằng nó là hệ khác, người đọc Whitepaper và người đọc `docs/04` sẽ nói chuyện
     lệch nhau mà không ai biết.
  4. **Bảng ánh xạ đầy đủ:** mỗi `INV-01..INV-12` phải có đúng một dòng trạng thái —
     `asserted` (có mã) hoặc `unasserted` (chưa có mã, và nói rõ vì sao).
  5. **Không được khai "đã kiểm" khi chưa có mã.** Mọi dòng `asserted` phải có ít
     nhất một `assert` mang thẻ đó; mọi dòng `unasserted` phải có `why`.

Ba chế độ:

    python3 scripts/check_invariants_coverage.py            # 5 bất biến
    python3 scripts/check_invariants_coverage.py --audit     # bảng 12 dòng
    python3 scripts/check_invariants_coverage.py --selftest  # CI

Chỉ thư viện chuẩn, không mạng.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DOCS = ROOT / "docs"
YP = DOCS / "YELLOWPAPER.md"
CONTRACTS = DOCS / "04-solana-smart-contracts.md"

CATALOG_TOTAL = 12

# Trạng thái khai báo cho từng mã — `docs/38` §3 giải thích từng dòng.
DECLARED = {
    "INV-01": ("asserted", "check_invariants: tổng cung + 0% nền tảng"),
    "INV-02": ("asserted", "check_invariants: v_sol * v_tok >= K"),
    "INV-03": ("asserted", "check_invariants: real_sol == v_sol - Y0 >= 0, penalty_floor >= 0"),
    "INV-04": ("asserted", "check_invariants: net_sold == VT - v_tok, trần chặng, tổng position"),
    "INV-05": ("unasserted", "cần đối tượng VersionRecord (h_k, h_base, nu_k) — mô hình đường cong không có; assert cùng programs/"),
    "INV-06": ("asserted", "check_invariants + unlock_next_milestone: m_act tăng đúng +1"),
    "INV-07": ("unasserted", "cần custody token trước Graduation — mô hình chỉ giữ SOL, không giữ token"),
    "INV-08": ("asserted", "buy(enforce_caps=True): trần ví + trần epoch"),
    "INV-09": ("asserted", "check_invariants(Stalled): creator_fee == 0 và creator_vest_frozen"),
    "INV-10": ("asserted", "graduate(): rel_gap < 1/S_LP"),
    "INV-11": ("unasserted", "cần đóng dấu BotShare của Oracle — đăng ký P6, cùng lúc với programs/"),
    "INV-12": ("unasserted", "cần trạng thái governance (upgrade_authority, terms_hash) — ngoài mô hình đường cong; đăng ký P6"),
}

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


def asserted_in_code(scripts_dir: Path | None = None) -> dict[str, list[str]]:
    """{mã: [tệp:dòng]} cho mọi thẻ nằm trên dòng KIỂM (`assert` / `check(`).

    Một thẻ trong chú thích không phải một phép kiểm — đây chính là chỗ dễ tự
    lừa nhất, nên nó là một phép phá ở `--selftest`.
    """
    base = scripts_dir or SCRIPTS
    found: dict[str, list[str]] = {}
    for path in sorted(base.glob("*.py")):
        # Tự miễn: tệp này chứa các chuỗi thẻ dùng làm phép thử ("INV-99"), nên
        # quét chính nó sẽ báo thẻ lạ. Miễn theo ĐÚNG một tệp, không theo thư mục.
        if path.name == "check_invariants_coverage.py":
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not re.search(r"\bassert\b|\bcheck\(", line):
                continue
            for code in re.findall(r"INV-\d\d", line):
                found.setdefault(code, []).append(f"{path.name}:{n}")
    return found


def catalog() -> list[str]:
    """Đọc 12 mã từ Yellow Paper §8.1 — không chép tay danh sách."""
    codes = []
    for _, line in lines_of(YP):
        m = re.match(r"^- \*\*`(INV-\d\d)` \(", line)
        if m:
            codes.append(m.group(1))
    return codes


# ------------------------------------------------------------------ 1. mã có thật
def inv1_catalog() -> None:
    codes = catalog()
    check(len(codes) == CATALOG_TOTAL,
          f"Yellow Paper §8.1 khai {len(codes)} mã, cần {CATALOG_TOTAL}: {codes}")
    check(sorted(codes) == [f"INV-{i:02d}" for i in range(1, CATALOG_TOTAL + 1)],
          f"Yellow Paper §8.1 đánh số không liên tục: {codes}")
    found = asserted_in_code()
    for code in sorted(found):
        check(code in codes,
              f"`scripts/` assert {code} nhưng mã này KHÔNG có trong danh mục YP §8.1 "
              f"({found[code]}) — thẻ lạ")
    check(bool(found), "`scripts/` không assert bất biến nào — cổng này vô nghĩa")


# ------------------------------------------------------------------ 2. câu "N vi phạm"
# Cụm khẳng định ĐÃ KIỂM. Chỉ khi một dòng vừa nêu dải vừa khẳng định đã kiểm thì
# mới có chuyện "nói về bất biến không tồn tại". Một TIÊU ĐỀ như "Hệ 12 Bất biến
# (`INV-01..INV-12`)" hay một dòng mục lục chỉ **đặt tên** — không khẳng định gì.
# (Đây là lần thu hẹp thứ tư trong loạt này, cùng một nguyên nhân: khớp rộng bắt oan
# chính tài liệu đang định nghĩa khái niệm.)
RANGE_CLAIM = re.compile(r"`?(INV-\d\d)`?\s*(?:\.\.|–|—|-)\s*`?(INV-\d\d)`?")
VERIFY_CLAIM = re.compile(r"vi phạm|\bPASS\b|\bpass\b|vượt qua|tất định .{0,12}100%", re.I)


def range_hits(line: str, codes: list[str], found: dict[str, list[str]],
               where: str) -> list[str]:
    """Trả về các vi phạm của MỘT dòng (hàm thuần — để đối chứng không phụ thuộc repo)."""
    out: list[str] = []
    if not VERIFY_CLAIM.search(line):
        return out
    for a, b in RANGE_CLAIM.findall(line):
        if a not in codes or b not in codes:
            out.append(f"{where} dải `{a}..{b}` nằm ngoài danh mục 12 mã")
            continue
        rng = [c for c in codes if a <= c <= b]
        missing = [c for c in rng if c not in found]
        if missing:
            out.append(f"{where} nói về `{a}..{b}` ({len(rng)} mã) nhưng {len(missing)} "
                       f"mã chưa có mã kiểm: {missing} (docs/38 §2)")
    return out

# Tệp mô tả hệ đánh số RIÊNG của chương trình Anchor (`docs/04` §5, `docs/06` M08).
# Dải `INV-xx` ở đó nói về code chưa tồn tại (`programs/` trống), nên chúng không thể
# được đối chiếu với mô hình đường cong — bất biến 3 kiểm việc KHAI BÁO hệ đó, không
# kiểm nội dung của nó.
PROGRAM_SYSTEM_DOCS = {"04-solana-smart-contracts.md", "06-implementation-roadmap.md"}


def inv2_range_claims() -> None:
    """Câu "0 vi phạm bất biến `INV-xx..INV-yy`" phải khớp số mã THỰC SỰ assert."""
    codes = catalog()
    found = asserted_in_code()
    docs = [YP] + sorted(p for p in DOCS.glob("[0-9][0-9]-*.md")
                         if p.name not in PROGRAM_SYSTEM_DOCS)
    for path in docs:
        for n, line in lines_of(path):
            for msg in range_hits(line, codes, found, f"{path.name}:{n}"):
                check(False, msg)


# ------------------------------------------------------------------ 3. ba hệ đánh số
def inv3_three_systems() -> None:
    """`docs/04` dùng cùng dải `INV-01..INV-08` cho hệ khác ⇒ phải khai báo tường minh."""
    text = CONTRACTS.read_text(encoding="utf-8")
    check("hệ đánh số riêng" in text,
          "docs/04 §5 dùng `INV-01..INV-08` cho bất biến của program nhưng không khai "
          "đó là HỆ ĐÁNH SỐ RIÊNG — người đọc Whitepaper sẽ hiểu lệch (docs/38 §1)")
    wp = (DOCS / "WHITEPAPER.md").read_text(encoding="utf-8")
    check("YELLOWPAPER" in wp and "§8.1" in wp,
          "Whitepaper gắn thẻ `INV-nn` nhưng không trỏ về danh mục chuẩn YP §8.1")


# ------------------------------------------------------------------ 4. bảng ánh xạ
def inv4_mapping() -> None:
    codes = catalog()
    for code in codes:
        check(code in DECLARED, f"{code} không có dòng trạng thái trong bảng ánh xạ")
    for code in DECLARED:
        check(code in codes, f"bảng ánh xạ có {code} nhưng YP §8.1 không có")


# ------------------------------------------------------------------ 5. trạng thái khớp mã
def inv5_status_matches_code() -> None:
    found = asserted_in_code()
    for code, (state, why) in DECLARED.items():
        if state == "asserted":
            check(code in found,
                  f"{code} khai `asserted` nhưng không có dòng assert nào mang thẻ này "
                  "trong `scripts/` — lời khai không có mã")
        else:
            check(state == "unasserted", f"{code}: trạng thái phải là asserted/unasserted")
            check(bool(why and why.strip()), f"{code} khai `unasserted` mà không nói vì sao")
    for code in sorted(found):
        state = DECLARED.get(code, ("?", ""))[0]
        check(state == "asserted",
              f"{code} CÓ mã kiểm ({found[code]}) nhưng bảng khai `{state}` — bảng lạc hậu")


# ------------------------------------------------------------------ báo cáo
def audit() -> int:
    found = asserted_in_code()
    print("\nMƯỜI HAI BẤT BIẾN — cái nào thực sự có mã?\n")
    print(f"{'mã':8}{'trạng thái':14}{'số dòng':9}ý nghĩa")
    print("─" * 100)
    n_ok = 0
    for code in catalog():
        state, why = DECLARED.get(code, ("?", ""))
        n = len(found.get(code, []))
        n_ok += 1 if state == "asserted" else 0
        mark = "✓" if state == "asserted" else "·"
        print(f"{code:8}{mark + ' ' + state:14}{n:<9}{why[:66]}")
    print(f"\n{n_ok}/12 mã có phép kiểm trong `scripts/` · {12 - n_ok} mã còn là TÊN")
    print("Câu '0 vi phạm INV-01..INV-08' chỉ được nói khi cả 8 mã đều ở cột ✓.")
    return 0


def selftest() -> int:
    global SCRIPTS, FAILS, PASSES

    def run(body: str, fn) -> list[str]:
        global SCRIPTS
        tmp = Path(tempfile.mkdtemp())
        (tmp / "scripts").mkdir()
        (tmp / "scripts" / "probe.py").write_text(body, encoding="utf-8")
        saved = SCRIPTS
        SCRIPTS = tmp / "scripts"
        FAILS.clear()
        globals()["PASSES"] = 0
        try:
            fn()
        except Exception as exc:                        # noqa: BLE001
            FAILS.append(str(exc))
        finally:
            SCRIPTS = saved
        return list(FAILS)

    cases = [
        ("P1 thẻ INV-99 không có trong danh mục",
         "assert x, 'INV-99 violated'\n", inv1_catalog, "thẻ lạ"),
        ("P2 câu 'INV-01..INV-08' khi mã chỉ có INV-01..INV-04",
         "assert a, 'INV-01'\nassert b, 'INV-02'\nassert c, 'INV-03'\nassert d, 'INV-04'\n",
         inv2_range_claims, "chưa có mã kiểm"),
        ("P3 khai `asserted` mà không có dòng assert",
         "", inv5_status_matches_code, "lời khai không có mã"),
        ("P4 thẻ nằm trên dòng CHÚ THÍCH, không phải phép kiểm",
         "# INV-05 se lam sau\nx = 1\n", inv5_status_matches_code, "lời khai không có mã"),
    ]

    ok = 0
    for name, body, fn, expect in cases:
        fails = run(body, fn)
        hits = [f for f in fails if expect in f]
        if hits:
            ok += 1
            print(f"  ✓ {name} → đỏ: {hits[0][:100]}")
        else:
            print(f"  ✗ {name} → LỌT (FAILS={fails[:2]})")

    full = "\n".join(f"assert x, '{c}'" for c, (s, _) in DECLARED.items() if s == "asserted") + "\n"
    fails = run(full, inv5_status_matches_code)
    if not fails:
        ok += 1
        print("  ✓ P5 đối chứng: assert đủ các mã đã khai → sạch")
    else:
        print(f"  ✗ P5 đối chứng → BẮT OAN: {fails[0]}")

    # Hai đối chứng cho bất biến 2, cả hai đều chạy trên ĐÚNG MỘT dòng tổng hợp —
    # không phụ thuộc trạng thái repo (đối chứng phụ thuộc repo sẽ đỏ khi repo sai,
    # và như vậy nó không còn là đối chứng).
    codes = catalog()
    found_ok = {c: ["x:1"] for c, (s, _) in DECLARED.items() if s == "asserted"}
    if not range_hits("**`0` vi phạm bất biến `INV-01..INV-04`**", codes, found_ok, "x"):
        ok += 1
        print("  ✓ P6 đối chứng: câu 'vi phạm' chỉ nói về mã ĐÃ có → sạch")
    else:
        print("  ✗ P6 đối chứng → BẮT OAN")
    if not range_hits("8. [Hệ 12 Bất biến Hình thức (`INV-01..INV-12`) & Chứng minh](...)",
                      codes, found_ok, "x"):
        ok += 1
        print("  ✓ P7 đối chứng: TIÊU ĐỀ nêu dải mà không khẳng định đã kiểm → sạch")
    else:
        print("  ✗ P7 đối chứng → BẮT OAN mục lục/tiêu đề")

    total = len(cases) + 3
    if ok != total:
        print(f"INVARIANT COVERAGE SELFTEST: FAIL — {ok}/{total} phép thử đúng chiều")
        return 1
    print(f"INVARIANT COVERAGE SELFTEST: PASS — {ok}/{total} phép thử đúng chiều "
          f"({len(cases)} phép phá + 3 đối chứng)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Bất biến nào thực sự có mã?")
    ap.add_argument("--audit", action="store_true", help="bảng 12 dòng")
    ap.add_argument("--selftest", action="store_true", help="kiểm 5 bất biến (CI)")
    args = ap.parse_args()

    if args.audit:
        return audit()
    if args.selftest:
        return selftest()

    inv1_catalog()
    inv2_range_claims()
    inv3_three_systems()
    inv4_mapping()
    inv5_status_matches_code()

    found = asserted_in_code()
    n = sum(1 for _c, (s, _w) in DECLARED.items() if s == "asserted")
    if FAILS:
        print(f"INVARIANT COVERAGE: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(f"INVARIANT COVERAGE: PASS — {PASSES} kiểm tra · 5 bất biến · "
          f"{n}/12 mã có mã kiểm · {sum(len(v) for v in found.values())} dòng assert mang thẻ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
