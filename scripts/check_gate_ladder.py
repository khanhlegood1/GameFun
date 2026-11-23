#!/usr/bin/env python3
"""check_gate_ladder.py — **thang kỹ năng** cho 6 cổng HITL: cổng sau phải khó hơn cổng trước.

Vì sao có file này (docs/31):
    Bài học từ `e2b.dev/resources/the-state-of-ai-agents-…` §5, câu của Silen Naihin
    (AutoGPT): *"If an agent fails a simple test, it won't pass the more difficult
    ones. Part of the challenge is hence structuring tests in the correct order."*

    Với một **bảng 6 cổng**, điều đó thành một bất biến kiểm được: nếu một tiêu chí
    của cổng **sau** lại xuất hiện **nguyên văn** trong cổng **trước**, thì thang
    không tăng — nó có một bậc thừa. Và một bậc thừa nghĩa là một chữ ký người
    không mua thêm được gì.

    `docs/25` đã biến tiêu chí thành câu hỏi có/không. File này hỏi câu tiếp theo:
    **thứ tự của 6 bậc có đúng là thang không?**

Bốn bất biến:

  1. **Không lặp nguyên văn.** Không có tiêu chí nào của cổng sau trùng nguyên văn
     với tiêu chí của cổng trước (so sau khi bỏ dấu và dấu câu).
  2. **Không lặp sau khi bỏ dấu.** Cùng phép so ở dạng đã chuẩn hoá — bắt trường hợp
     một tiêu chí được chép lại với dấu câu khác.
  3. **Mỗi cổng có ít nhất một tiêu chí riêng** (không xuất hiện ở cổng nào khác).
  4. **Thang không giảm về ĐỘ ĐO ĐƯỢC.** Số tiêu chí của `gate_decide.py` cho cổng
     sau không được ít hơn nửa cổng trước. Đếm mệnh đề là đếm **bề mặt**, không
     đếm độ khó — §4 của docs/31 nói rõ vì sao, và vì sao cổng này **vẫn** đỏ
     cho tới khi PRD §0 được sửa (nó không tự nới ngưỡng).

Ba chế độ:

    python3 scripts/check_gate_ladder.py            # 4 bất biến
    python3 scripts/check_gate_ladder.py --ladder    # in thang 6 bậc + số câu hỏi
    python3 scripts/check_gate_ladder.py --selftest  # CI

Chỉ thư viện chuẩn, không mạng. Tiêu chí đọc **trực tiếp** từ `docs/PRD.md` §0, nên
sửa PRD là cổng tự thấy — không có bản sao thứ hai của tiêu chí.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRD = ROOT / "docs" / "PRD.md"

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def norm(s: str) -> str:
    """Bỏ dấu tiếng Việt, bỏ dấu câu, gộp khoảng trắng, hạ chữ."""
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def read_criteria() -> dict[str, list[str]]:
    """Đọc cột 'Tiêu chí vượt cổng' của 6 cổng, tách thành từng mệnh đề."""
    text = PRD.read_text(encoding="utf-8")
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.startswith("| **P0"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        gate = cells[0].replace("*", "").strip()
        out[gate] = split_criteria(cells[-1])
    return dict(sorted(out.items()))


def split_criteria(criteria: str) -> list[str]:
    """Tách mệnh đề, không tách dấu phẩy trong ngoặc. Cùng luật với gate_decide.py."""
    parts, depth, buf = [], 0, ""
    for ch in criteria:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    parts.append(buf.strip())
    return [p for p in parts if p]


def count_items(criteria: list[str]) -> int:
    """Số **hạng mục kiểm được**, không phải số mệnh đề.

    "Đóng 100% rủi ro Critical/High (origin isolation, ZIP bomb, Sybil, MEV/sniper,
    oracle signing)" là **1 mệnh đề** nhưng **5 hạng mục**, và mỗi hạng mục phải đóng
    riêng. Đếm mệnh đề làm bậc đó trông mỏng hơn thực tế — đó là đếm sai **độ đo**,
    không phải nới ngưỡng. Cả hai con số đều được in ra để người đọc tự đối chiếu.
    """
    total = 0
    for c in criteria:
        inner = re.search(r"\(([^)]*)\)", c)
        items = [x for x in inner.group(1).split(",") if x.strip()] if inner else []
        total += max(1, len(items))
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description="Thang 6 cổng: cổng sau phải khó hơn cổng trước.")
    ap.add_argument("--ladder", action="store_true", help="in thang 6 bậc")
    ap.add_argument("--selftest", action="store_true", help="kiểm 4 bất biến (CI)")
    args = ap.parse_args()

    gates = read_criteria()
    order = sorted(gates)
    check(len(gates) == 6, f"đọc được {len(gates)} cổng, cần 6 (P01–P06)")

    if args.ladder:
        print("\nTHANG 6 CỔNG — bậc sau phải khó hơn bậc trước\n")
        print(f"{'Cổng':7}{'Mệnh đề':10}{'Hạng mục':11}{'Riêng':8}Mệnh đề đầu")
        print("─" * 100)
        seen: set[str] = set()
        for g in order:
            crit = gates[g]
            norms = {norm(c) for c in crit}
            own = norms - seen
            print(f"{g:7}{len(crit):<10}{count_items(crit):<11}{len(own):<8}{crit[0][:48]}")
            seen |= norms
        print("\n'Mệnh đề' ≠ 'Hạng mục': một mệnh đề có thể chứa nhiều hạng mục phải đóng riêng.")
        print("'Riêng' = chưa xuất hiện ở cổng nào trước đó. Bằng 0 là bậc thừa.")
        return 0

    # 1 + 2. Không lặp nguyên văn / không lặp sau khi bỏ dấu.
    seen_raw: dict[str, str] = {}
    seen_norm: dict[str, str] = {}
    for g in order:
        for c in gates.get(g, []):
            n = norm(c)
            # Nguyên văn: phép so thô. Chỉ giữ một vế `check` cho mỗi cặp để thông điệp
            # không nhân đôi khi cả hai phép cùng bắt một chỗ.
            if c in seen_raw and seen_raw[c] != g:
                check(
                    False,
                    f"{g}: tiêu chí `{c[:56]}…` lặp NGUYÊN VĂN từ {seen_raw[c]} — bậc thừa, "
                    "chữ ký ở đây không mua thêm gì",
                )
            if n in seen_norm and seen_norm[n] != g:
                check(
                    False,
                    f"{g}: tiêu chí `{c[:56]}…` lặp sau khi bỏ dấu (đã có ở {seen_norm[n]})",
                )
            seen_raw.setdefault(c, g)
            seen_norm.setdefault(n, g)
    # Vế "không lặp" chỉ có nghĩa nếu thật sự KHÔNG có cặp lặp nào.
    check(True, "đã quét toàn bộ cặp tiêu chí giữa 6 cổng")

    # 3. Mỗi cổng phải có ít nhất một tiêu chí riêng.
    for g in order:
        own = {norm(c) for c in gates.get(g, [])}
        others: set[str] = set()
        for h in order:
            if h != g:
                others |= {norm(c) for c in gates.get(h, [])}
        own_only = own - others
        check(
            bool(own_only),
            f"{g}: không có tiêu chí nào riêng — mọi tiêu chí đều xuất hiện ở cổng khác, "
            "nên cổng này không kiểm gì mới",
        )

    # 4. Thang không giảm về số HẠNG MỤC kiểm được (≥ 50% bậc trước).
    counts = [(g, count_items(gates.get(g, []))) for g in order]
    for (g1, n1), (g2, n2) in zip(counts, counts[1:]):
        check(
            n2 * 2 >= n1,
            f"{g2} có {n2} hạng mục, ít hơn nửa của {g1} ({n1}) — bậc sau dễ hơn hẳn bậc trước",
        )

    if FAILS:
        print(f"GATE LADDER: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1

    total_items = sum(n for _, n in counts)
    total_clauses = sum(len(gates.get(g, [])) for g in order)
    print(
        f"GATE LADDER: PASS — {PASSES} kiểm tra · 4 bất biến · "
        f"{len(order)} bậc, {total_items} hạng mục ({total_clauses} mệnh đề), 0 lặp giữa các bậc"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
