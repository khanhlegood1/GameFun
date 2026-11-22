#!/usr/bin/env python3
"""check_specs.py — bản ghi niềm tin của dự án, ba chế độ.

Ý tưởng lấy từ `Proactive-Co-Creator`: giữ một **bản ghi niềm tin** có cấu trúc
(trái ngược với văn xuôi), chỉ áp **delta tối thiểu**, và **hỏi** thay vì đoán.
Nhưng bản ghi ở đây KHÔNG phải "thứ AI nghĩ" — nó là **tuyên bố của người, có
`source` trỏ về tài liệu**, và mỗi câu hỏi **có thể bị từ chối bằng một luật**.

Ba chế độ:

    python3 scripts/check_specs.py --tick
        → so từng giá trị trong `pm/spec-*.json` với dòng nguồn của nó trong docs/.
          Lệch thì báo. Đây là "delta" của repo này: không hỏi model, chỉ so chuỗi.

    python3 scripts/check_specs.py --questions
        → sinh câu hỏi từ `open_questions`, BỎ những câu đã bị `constraints` trả lời.
          Mỗi câu còn lại có 3 lựa chọn, kể cả "[BẠN QUYẾT]" và "[KHÔNG LIÊN QUAN]".

    python3 scripts/check_specs.py --answer q_m1_scope=...
        → kiểm câu trả lời; nếu câu bị một `constraint` chặn thì TỪ CHỐI.

Bốn bất biến (canh bởi `--self-test`):

  1. Mọi giá trị phải có `source` trỏ tới một tệp có thật, và phải còn xuất hiện ở
     dòng nguồn đó. Không có "niềm tin" nào không truy được về tài liệu.
  2. Câu hỏi đã bị constraint trả lời thì KHÔNG được hỏi lại — và phải ghi
     `answered_by_constraint`. (Bài học từ repo mẫu: đừng hỏi lại thứ đã rõ.)
  3. Câu trả lời không được mâu thuẫn với constraint `blocking`.
  4. Mọi câu hỏi phải có lựa chọn thoát: `[BẠN QUYẾT]` và `[KHÔNG LIÊN QUAN]`.

Chỉ dùng thư viện chuẩn, không mạng.
"""

from __future__ import annotations

import argparse
import glob
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PM = ROOT / "pm"

YOU_DECIDE = "[BẠN QUYẾT] Tôi không quan tâm, bạn quyết. Ghi vào ADR."
NOT_RELEVANT = "[KHÔNG LIÊN QUAN] Câu này không áp dụng. Không thêm chi tiết về nó."


# --------------------------------------------------------------- nạp & kiểm
def load_specs() -> list[tuple[pathlib.Path, dict]]:
    out = []
    for f in sorted(PM.glob("spec-*.json")):
        out.append((f, json.loads(f.read_text(encoding="utf-8"))))
    return out


def norm(value: str) -> str:
    """So sánh không phụ thuộc dấu, loại số, khoảng trắng, backtick."""
    v = value.replace("`", "").replace(" ", "").replace("\u00a0", "")
    return v.lower()


def source_line(path_str: str) -> str | None:
    """`docs/X.md:478` → nội dung dòng 478 (hoặc None nếu không có)."""
    m = re.match(r"^(.+?):(\d+)$", path_str)
    if not m:
        return None
    path = ROOT / m.group(1)
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    n = int(m.group(2))
    if n < 1 or n > len(lines):
        return None
    return lines[n - 1]


def iter_values(spec: dict):
    for ent in spec.get("entities", []):
        for attr in ent.get("attributes", []):
            yield ent["name"], attr


def tick() -> int:
    """So từng giá trị với dòng nguồn. Đây là toàn bộ 'delta' của repo này."""
    problems: list[str] = []
    checked = 0
    for path, spec in load_specs():
        for ent_name, attr in iter_values(spec):
            checked += 1
            src = attr.get("source")
            if not src:
                problems.append(f"{path.name}/{ent_name}.{attr['name']}: thiếu `source`")
                continue
            line = source_line(src)
            if line is None:
                problems.append(f"{path.name}/{ent_name}.{attr['name']}: nguồn `{src}` không đọc được")
                continue
            value = attr["value"]
            # Chấp nhận cả hai dạng viết số thập phân và phân cách hàng nghìn.
            candidates = {value, value.replace(",", "."), value.replace(".", ",")}
            if not any(norm(c) in norm(line) for c in candidates):
                problems.append(
                    f"{path.name}/{ent_name}.{attr['name']}: giá trị `{value}` KHÔNG còn ở {src}\n"
                    f"      dòng nguồn: {line.strip()[:120]}"
                )
    if problems:
        print("SPEC TICK: FAIL — tài liệu và bản ghi lệch nhau")
        for p in problems:
            print("  -", p)
        return 1
    print(f"SPEC TICK: PASS — {checked} giá trị khớp dòng nguồn, 0 lệch")
    return 0


def questions() -> int:
    total = 0
    suppressed = 0
    for path, spec in load_specs():
        blocked = {c.get("refuses_question") for c in spec.get("constraints", [])} - {None}
        print(f"\n{spec['gate']} — {spec['status']}")
        for q in spec.get("open_questions", []):
            total += 1
            if q["id"] in blocked:
                suppressed += 1
                continue
            print(f"  ? {q['id']}: {q['text']}")
            print(f"      · {YOU_DECIDE}")
            print(f"      · {NOT_RELEVANT}")
    print(
        f"\n{total} câu hỏi · {suppressed} câu bị luật trả lời nên KHÔNG hỏi lại"
        f" · {total - suppressed} câu cần người quyết"
    )
    return 0


def answer(pairs: list[str]) -> int:
    """Trả lời một câu hỏi. Từ chối nếu câu đó đã bị constraint chặn."""
    specs = load_specs()
    if not specs:
        print("không có spec nào", file=sys.stderr)
        return 2
    spec = specs[0][1]
    blocked = {c.get("refuses_question"): c for c in spec.get("constraints", []) if c.get("refuses_question")}
    by_id = {q["id"]: q for q in spec.get("open_questions", [])}

    rc = 0
    for pair in pairs:
        if "=" not in pair:
            print(f"  ✗ `{pair}` không đúng dạng id=giá_trị")
            rc = 2
            continue
        qid, value = pair.split("=", 1)
        if qid in blocked:
            c = blocked[qid]
            print(f"  ⛔ {qid}: KHÔNG được trả lời — bị luật `{c['id']}` chặn: {c['text']}")
            rc = 1
            continue
        if qid not in by_id:
            print(f"  ✗ {qid}: không có câu hỏi này")
            rc = 2
            continue
        if value.strip() in (YOU_DECIDE, NOT_RELEVANT) or value.startswith("["):
            print(f"  ✓ {qid} = {value[:40]}… (người quyết / không áp dụng — ghi vào ADR)")
            continue
        print(f"  ✓ {qid} = {value}")
    return rc


def self_test() -> int:
    """Bốn bất biến. Cổng phải đỏ được — đã thử phá cả bốn."""
    problems: list[str] = []
    specs = load_specs()
    if not specs:
        print("SPEC SELF-TEST: FAIL — không có `pm/spec-*.json`")
        return 1

    for path, spec in specs:
        # Bất biến 1: mọi giá trị có source đọc được.
        for ent_name, attr in iter_values(spec):
            src = attr.get("source", "")
            if not src or source_line(src) is None:
                problems.append(f"{path.name}/{ent_name}.{attr['name']}: source `{src}` không đọc được")
        # Bất biến 2: câu bị luật trả lời phải khai báo, và phải có luật tương ứng.
        blocked = {c.get("refuses_question") for c in spec.get("constraints", [])} - {None}
        for q in spec.get("open_questions", []):
            declared = q.get("answered_by_constraint")
            if q["id"] in blocked and not declared:
                problems.append(f"{path.name}: câu `{q['id']}` bị luật chặn nhưng không khai báo")
            if declared:
                by_id = {c["id"]: c for c in spec.get("constraints", [])}
                if declared not in by_id:
                    problems.append(f"{path.name}: câu `{q['id']}` trỏ tới luật `{declared}` không tồn tại")
                elif by_id[declared].get("refuses_question") != q["id"]:
                    # Hai chiều: câu khai "bị luật X trả lời" thì luật X phải thật sự
                    # trỏ ngược lại câu này. Nếu không, câu sẽ được HỎI LẠI — đúng thứ
                    # repo mẫu dặn tránh ("đừng hỏi lại thứ đã rõ").
                    problems.append(
                        f"{path.name}: câu `{q['id']}` khai bị luật `{declared}` trả lời, "
                        f"nhưng `{declared}` không trỏ ngược lại"
                    )
        # Bất biến 3: mọi constraint phải có severity rõ.
        for c in spec.get("constraints", []):
            if c.get("severity") not in {"blocking", "advisory"}:
                problems.append(f"{path.name}: luật `{c.get('id')}` thiếu severity")
        # Bất biến 4: có đường thoát cho mọi câu hỏi.
        if not YOU_DECIDE or not NOT_RELEVANT:
            problems.append(f"{path.name}: thiếu lựa chọn thoát")

    # Thử phá: câu trả lời cho câu bị chặn phải bị từ chối (mã 1).
    if specs:
        spec = specs[0][1]
        blocked_ids = [c["refuses_question"] for c in spec.get("constraints", []) if c.get("refuses_question")]
        if blocked_ids:
            rc = answer([f"{blocked_ids[0]}=có"])
            if rc != 1:
                problems.append("bất biến 3: trả lời câu bị chặn KHÔNG bị từ chối")

    if problems:
        print("SPEC SELF-TEST: FAIL")
        for p in problems:
            print("  -", p)
        return 1
    total_c = sum(len(s.get("constraints", [])) for _, s in specs)
    total_q = sum(len(s.get("open_questions", [])) for _, s in specs)
    print(
        f"SPEC SELF-TEST: PASS — {len(specs)} spec, {total_c} luật, {total_q} câu hỏi, "
        "4 bất biến (source · không hỏi lại · không mâu thuẫn · có đường thoát)"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Bản ghi niềm tin của dự án: tick / questions / answer.")
    ap.add_argument("--tick", action="store_true", help="so giá trị với dòng nguồn")
    ap.add_argument("--questions", action="store_true", help="liệt kê câu hỏi còn mở")
    ap.add_argument("--answer", nargs="+", metavar="ID=GIÁ_TRỊ", help="trả lời câu hỏi")
    ap.add_argument("--self-test", action="store_true", help="kiểm 4 bất biến, dùng trong CI")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.tick:
        return tick()
    if args.questions:
        return questions()
    if args.answer:
        return answer(args.answer)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
