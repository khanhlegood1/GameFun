#!/usr/bin/env python3
"""gate_decide.py — biến tiêu chí 6 cổng HITL thành câu hỏi CÓ/KHÔNG kiểm được.

Vấn đề: `docs/PRD.md` §0 có 6 cổng, mỗi cổng vài tiêu chí viết bằng văn xuôi. Văn
xuôi thì mỗi người đọc một kiểu, và không ai kiểm được "đã đủ chưa". Repo mẫu
`Gemini-Decisions-API-Playground` cho thấy một hình dạng tốt hơn: mỗi câu hỏi có
**khoá**, **kiểu** (có/không · chọn một · chấm điểm) và **bộ tiêu chí**.

File này KHÔNG gọi API. Nó làm hai việc, cả hai đều offline:

    python3 scripts/gate_decide.py --gate P03
        → in bộ câu hỏi suy ra từ tiêu chí trong `docs/PRD.md`, kèm payload JSON
          đúng hình dạng `gemini-decision-1` để dán vào playground nếu muốn.

    python3 scripts/gate_decide.py --gate P03 --verdict verdict.json
        → chấm một phán quyết (của người HOẶC của API) và trả mã lỗi nếu chưa đạt.

BA BẤT BIẾN (được canh bởi `--self-test`):

  1. Câu hỏi lấy NGUYÊN VĂN từ `docs/PRD.md`. Script không được viết lại tiêu chí,
     vì làm vậy là tạo ra một cổng thứ hai không ai duyệt.
  2. Phán quyết KHÔNG BAO GIỜ là chữ ký: output luôn có `advisory: true` và
     `signer: null`. Cổng HITL là chữ ký của người (`docs/PRD.md` §0).
  3. Xác suất `true` dưới ngưỡng ⇒ câu đó KHÔNG đạt, kể cả khi model trả "true".
     Một câu trả lời không chắc chắn không được làm cổng xanh.

Chỉ dùng thư viện chuẩn. Không phụ thuộc mạng.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRD = ROOT / "docs" / "PRD.md"

# Ngưỡng mặc định cho một câu CÓ/KHÔNG. 0,70 là mức "khá chắc" — không phải 0,50,
# vì 0,50 nghĩa là model chỉ hơn tung đồng xu một chút, mà cổng thì cần chắc hơn.
DEFAULT_THRESHOLD = 0.70


def read_exit_criteria() -> dict[str, str]:
    """Đọc cột 'Tiêu chí vượt cổng' của bảng 6 cổng trong `docs/PRD.md`.

    Không hardcode: nếu ai sửa tiêu chí trong PRD, script tự thấy. Đây là bất biến 1.
    """
    text = PRD.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("| **P0"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        gate = cells[0].replace("*", "").strip()
        out[gate] = cells[-1]
    return out


def split_criteria(criteria: str) -> list[str]:
    """Tách một ô tiêu chí thành từng mệnh đề. Dấu phẩy trong ngoặc không tách."""
    parts: list[str] = []
    depth = 0
    buf = ""
    for ch in criteria:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return [p.strip(" .;") for p in parts if p.strip(" .;")]


def strip_diacritics(text: str) -> str:
    """`toán học` → `toan hoc`, `đ` → `d`. Cần cho tiếng Việt.

    `toKey` của repo mẫu chỉ xử lý `a–z`; áp nguyên vào tiếng Việt sẽ ra
    `to_n_h_c_...` — khoá không đọc được, và người duyệt không nhận ra câu nào.
    """
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )


def to_key(text: str, used: set[str] | None = None) -> str:
    """Chữ thường, `_`, tối đa 48 ký tự, không trùng trong cùng một cổng."""
    base = re.sub(r"[^a-z0-9]+", "_", strip_diacritics(text).lower()).strip("_")
    if len(base) > 48:
        # Cắt ở ranh giới từ, không cắt giữa âm tiết: khoá phải đọc được.
        base = base[:48].rsplit("_", 1)[0] or base[:48]
    base = base or "cau_hoi"
    if used is None:
        return base
    key, n = base, 2
    while key in used:
        suffix = f"_{n}"
        key = base[: 48 - len(suffix)] + suffix
        n += 1
    used.add(key)
    return key


def as_question(statement: str, used: set[str]) -> dict:
    """Một mệnh đề tiêu chí → một câu hỏi CÓ/KHÔNG, giữ nguyên văn mệnh đề."""
    return {
        "key": to_key(statement, used),
        "type": "noul",
        "instructions": f"Đã đạt chưa: {statement}?",
        "criteria": {
            "true_description": f"Có bằng chứng trong repo cho: {statement}",
            "false_description": "Không tìm thấy bằng chứng, hoặc chỉ có lời tuyên bố",
        },
        # Trường nội bộ, KHÔNG gửi lên API: giữ nguyên văn để đối chiếu ngược PRD.
        "_source": statement,
    }


def build_gate(gate: str, criteria: str) -> dict:
    used: set[str] = set()
    questions = [as_question(s, used) for s in split_criteria(criteria)]
    return {
        "gate": gate,
        "source": "docs/PRD.md §0 — cột 'Tiêu chí vượt cổng'",
        "advisory": True,
        "signer": None,
        "threshold": DEFAULT_THRESHOLD,
        "note": (
            "Đây là câu hỏi, không phải phán quyết. Cổng chỉ đóng khi NGƯỜI ký "
            "(docs/PRD.md §0 — Người ký duyệt)."
        ),
        "questions": questions,
    }


def to_api_payload(gate_doc: dict, model: str = "gemini-decision-1") -> dict:
    """Hình dạng `gemini-decision-1`: `{model, input, questions{key: {...}}}`."""
    questions = {}
    for q in gate_doc["questions"]:
        questions[q["key"]] = {
            "type": q["type"],
            "instructions": q["instructions"],
            "criteria": q["criteria"],
        }
    return {
        "model": model,
        "input": f"Cổng {gate_doc['gate']} của dự án Game9K. Đánh giá từng câu hỏi dưới đây "
        "dựa trên tài liệu trong repo khanhlegood1/GameFun.",
        "questions": questions,
    }


def grade(gate_doc: dict, verdict: dict) -> tuple[int, list[str]]:
    """Chấm một phán quyết. Bất biến 2 và 3 sống ở đây."""
    threshold = float(verdict.get("threshold", gate_doc["threshold"]))
    answers = verdict.get("answers") or {}
    lines: list[str] = []
    failed = 0
    for q in gate_doc["questions"]:
        key = q["key"]
        a = answers.get(key)
        if a is None:
            lines.append(f"  ?  {key:38s} thiếu câu trả lời")
            failed += 1
            continue
        p_true = a.get("probabilities", {}).get("true", a.get("noul"))
        if p_true is None:
            lines.append(f"  ?  {key:38s} không có xác suất — không chấm được")
            failed += 1
            continue
        ok = p_true >= threshold
        lines.append(
            f"  {'✓' if ok else '✗'}  {key:38s} p(true)={p_true:.3f} "
            f"{'≥' if ok else '<'} {threshold:.2f}"
        )
        if not ok:
            failed += 1
    return failed, lines


def self_test() -> int:
    """Kiểm ba bất biến + khả năng bắt lỗi. Cổng phải ĐỎ ĐƯỢC."""
    gates = read_exit_criteria()
    problems: list[str] = []

    if len(gates) != 6:
        problems.append(f"đọc được {len(gates)} cổng, cần 6 (P01–P06)")

    for gate, criteria in gates.items():
        doc = build_gate(gate, criteria)
        if not doc["advisory"] or doc["signer"] is not None:
            problems.append(f"{gate}: vi phạm bất biến 2 (advisory/signer)")
        if not doc["questions"]:
            problems.append(f"{gate}: không sinh được câu hỏi nào")
        for q in doc["questions"]:
            # Bất biến 1: câu hỏi phải chứa nguyên văn mệnh đề tiêu chí.
            if q["_source"] not in q["instructions"]:
                problems.append(f"{gate}/{q['key']}: câu hỏi không giữ nguyên văn tiêu chí")
            if "PASS" in q["instructions"] or "đạt cổng" in q["instructions"].lower():
                problems.append(f"{gate}/{q['key']}: câu hỏi tự tuyên bố đạt")
            # Khoá phải đọc được: không quá 3 ký tự đơn lẻ liên tiếp (dấu vết của
            # việc bỏ dấu sai, kiểu `to_n_h_c`).
            if re.search(r"(?:^|_)(?:[a-z]_){3,}", q["key"]):
                problems.append(f"{gate}: khoá `{q['key']}` không đọc được — bỏ dấu sai")
        keys = [q["key"] for q in doc["questions"]]
        if len(set(keys)) != len(keys):
            problems.append(f"{gate}: khoá bị trùng")

    # Bất biến 3: xác suất thấp phải bị chặn, kể cả khi verdict ghi `true`.
    doc = build_gate("P99", "Tiêu chí thử")
    bad = {"answers": {doc["questions"][0]["key"]: {"boolean": True, "noul": 0.55}}}
    failed, _ = grade(doc, bad)
    if failed != 1:
        problems.append("bất biến 3: p(true)=0.55 vẫn được chấm đạt")
    good = {"answers": {doc["questions"][0]["key"]: {"noul": 0.95}}}
    failed, _ = grade(doc, good)
    if failed != 0:
        problems.append("bất biến 3: p(true)=0.95 bị chấm trượt")
    missing = {"answers": {}}
    failed, _ = grade(doc, missing)
    if failed != 1:
        problems.append("thiếu câu trả lời phải bị chấm trượt")

    if problems:
        print("GATE DECIDE: FAIL")
        for p in problems:
            print("  -", p)
        return 1
    total = sum(len(build_gate(g, c)["questions"]) for g, c in gates.items())
    print(
        f"GATE DECIDE: PASS — 6 cổng, {total} câu hỏi có/không, "
        "3 bất biến giữ nguyên (nguyên văn PRD · advisory · ngưỡng chặn)"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh & chấm câu hỏi cổng HITL.")
    ap.add_argument("--gate", help="P01..P06")
    ap.add_argument("--verdict", help="tệp JSON phán quyết cần chấm")
    ap.add_argument("--json", action="store_true", help="in JSON thay vì bảng")
    ap.add_argument("--self-test", action="store_true", help="kiểm 3 bất biến, dùng trong CI")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    gates = read_exit_criteria()
    if not args.gate:
        print("Các cổng đọc được từ docs/PRD.md §0:", ", ".join(sorted(gates)) or "(không có)")
        return 0 if gates else 1

    gate = args.gate.upper()
    if gate not in gates:
        print(f"Không có cổng {gate}. Có: {', '.join(sorted(gates))}", file=sys.stderr)
        return 2

    doc = build_gate(gate, gates[gate])
    if args.verdict:
        verdict = json.loads(pathlib.Path(args.verdict).read_text(encoding="utf-8"))
        failed, lines = grade(doc, verdict)
        print(f"CỔNG {gate} — {len(doc['questions']) - failed}/{len(doc['questions'])} câu đạt")
        print("\n".join(lines))
        print(
            f"\nADVISORY — không phải phán quyết. Người ký cổng {gate} theo docs/PRD.md §0 "
            "phải xem từng câu và ký riêng."
        )
        return 0 if failed == 0 else 1

    if args.json:
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        print(json.dumps(to_api_payload(doc), ensure_ascii=False, indent=2))
        return 0

    print(f"CỔNG {gate} — {len(doc['questions'])} câu hỏi có/không, ngưỡng {doc['threshold']:.2f}")
    print(f"Nguồn: {doc['source']}")
    for q in doc["questions"]:
        print(f"  · {q['key']:38s} ← {q['_source']}")
    print("\nADVISORY — câu hỏi, không phải phán quyết.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
