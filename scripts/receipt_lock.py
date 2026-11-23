#!/usr/bin/env python3
"""receipt_lock.py — một con số không kèm **biên bản** thì không kiểm toán được.

Vì sao có file này (docs/35):
    `scripts/gate_decide.py` sinh câu hỏi cho một dịch vụ chấm điểm, rồi **không để lại
    dấu vết nào**: không model, không phiên bản, không ngày, không hash đầu vào. Nghĩa
    là nếu mai ai đó chạy lại với một model khác và nhận kết quả khác, **không có cách
    nào biết hai lần chạy khác nhau ở đâu**.

    Nguồn gốc ý tưởng: tài liệu KVU-2 (`nguyen-ly-don-vi-khanh-tang-hai.md`). Họ dẫn
    một lỗi thật của chính họ: một phép đo chạy trên **tệp đã bị đột biến**, cho
    **0 ca lệch trên 200.000**, suýt được ghi vào ADR — số đúng là **41,4%**.
    Đó không phải lỗi của họ; đó là lỗi của mọi phép đo không ghi lại đầu vào.

    Nên: biên bản ở đây là một TỆP JSON có hình dạng cố định, và bất biến 5 kiểm nó
    **khớp với tệp thật**. Một biên bản trỏ tới đầu vào đã đổi là biên bản vô giá trị.

Sáu bất biến (đọc từ tệp, không tin lời khai):

  1. **Đủ 8 trường**: receipt_id · date · model_requested · model_served · provider ·
     input_sha256 · output_sha256 · artifact_bytes. Thiếu một trường ⇒ không kiểm được.
  2. **`model_served` ≠ `model_requested` ⇒ phải có `drift_note`.** Model trôi là
     chuyện bình thường; trôi mà **không ai biết** mới là lỗi.
  3. **Không cộng dồn khác khoá**: một tệp tổng hợp không được trộn hai `model_served`
     khác nhau như cùng một phép đo.
  4. **Không có nội dung tài liệu** trong biên bản — chỉ hash. Tài liệu Game9K chứa số
     tài chính chưa công bố.
  5. **Hash phải khớp tệp thật** nếu tệp còn tồn tại. Đây là bất biến quan trọng nhất:
     nó là bản sao của lỗi 41,4%.
  6. **Biên bản không phải điểm số**: không `score` / `confidence` / `grade` /
     `pass` / `verdict`. Một lần đo là dữ liệu, không phải phán quyết.

Chế độ:

    python3 scripts/receipt_lock.py                  # 6 bất biến
    python3 scripts/receipt_lock.py --audit           # liệt kê biên bản + khoá
    python3 scripts/receipt_lock.py --selftest        # CI
    python3 scripts/receipt_lock.py --new ...         # sinh biên bản rỗng đúng schema

Chỉ thư viện chuẩn, không mạng.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECEIPTS = ROOT / "receipts"

# Tám trường bắt buộc. Đây là **toàn bộ** hợp đồng của một biên bản.
REQUIRED = (
    "receipt_id", "date", "model_requested", "model_served", "provider",
    "input_sha256", "output_sha256", "artifact_bytes",
)
# Trường biến biên bản thành phán quyết. Cấm tuyệt đối.
FORBIDDEN = ("score", "confidence", "grade", "pass", "verdict", "rating", "rank")
# Trường chứa NỘI DUNG. Biên bản ghi hash, không ghi nội dung.
CONTENT_KEYS = ("text", "content", "body", "prompt", "response", "excerpt")

HASH_RE = re.compile(r"^[0-9a-f]{16,64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def receipt_files() -> list[Path]:
    if not RECEIPTS.is_dir():
        return []
    return sorted(p for p in RECEIPTS.glob("*.json"))


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        FAILS.append(f"{path.name}: JSON hỏng — {exc}")
        return {}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_source(ref: str) -> Path | None:
    """`input_source` là đường dẫn tương đối repo; `none:` = không có đầu vào tệp."""
    if not ref or ref.startswith("none:"):
        return None
    p = (ROOT / ref).resolve()
    return p if p.exists() else None


def audit_one(path: Path, r: dict) -> None:
    rid = r.get("receipt_id", path.stem)
    req, served = r.get("model_requested"), r.get("model_served")
    drift = "" if req == served else "  ⚠ TRÔI"
    print(f"  {rid:26s} {(served or '?'):30s} {r.get('provider', '?'):12s}"
          f" {r.get('date', '?')}{drift}")


def audit() -> int:
    print("\nBIÊN BẢN ĐO — khoá là (model đã phục vụ), không phải (model đã yêu cầu)\n")
    files = receipt_files()
    if not files:
        print("  (chưa có biên bản nào)")
        print("\n  Đây là trạng thái ĐÚNG của repo hôm nay: chưa có lần đo AI nào chạy thật,")
        print("  và `check_egress_lock.py` bảo đảm điều đó. `receipts/` để trống, không lấp.")
        return 0
    for p in files:
        audit_one(p, load(p))
    print(f"\n{len(files)} biên bản")
    return 0


def check_receipt(path: Path) -> None:
    r = load(path)
    if not r:
        return
    tag = r.get("receipt_id", path.stem)

    # 1. Đủ trường.
    missing = [k for k in REQUIRED if k not in r or r[k] in ("", None)]
    check(not missing, f"{path.name} [{tag}]: thiếu trường {missing} — không kiểm được")

    # 1b. Hình dạng của hash và ngày.
    for k in ("input_sha256", "output_sha256"):
        v = str(r.get(k, ""))
        check(bool(HASH_RE.match(v)), f"{path.name} [{tag}]: `{k}` không phải hex ≥16 ký tự")
    check(bool(DATE_RE.match(str(r.get("date", "")))),
          f"{path.name} [{tag}]: `date` phải là YYYY-MM-DD")

    # 2. Trôi model phải được ghi ra.
    req, served = r.get("model_requested"), r.get("model_served")
    if req and served and req != served:
        check(bool(r.get("drift_note")),
              f"{path.name} [{tag}]: model_requested={req!r} ≠ model_served={served!r} "
              "nhưng không có `drift_note` — trôi mà không ai biết là lỗi")

    # 4. Không nội dung tài liệu, chỉ hash.
    leaked = [k for k in r if k in CONTENT_KEYS]
    check(not leaked,
          f"{path.name} [{tag}]: chứa trường nội dung {leaked} — biên bản chỉ ghi hash "
          "(tài liệu có số tài chính chưa công bố)")

    # 6. Biên bản không phải điểm số.
    scored = [k for k in r if k in FORBIDDEN]
    check(not scored,
          f"{path.name} [{tag}]: chứa trường phán quyết {scored} — một lần đo là dữ liệu, "
          "không phải phán quyết")

    # 5. Hash phải khớp tệp thật — bản sao của lỗi 41,4%.
    src_ref = r.get("input_source", "")
    src = resolve_source(src_ref)
    if src is not None:
        actual = sha256_of(src)
        check(actual == r.get("input_sha256"),
              f"{path.name} [{tag}]: `input_sha256` KHÔNG khớp {src_ref} "
              f"(biên bản {str(r.get('input_sha256'))[:12]}…, thật {actual[:12]}…) — "
              "đúng lỗi đo trên tệp đã bị đột biến (docs/35 §2)")
    elif src_ref and not src_ref.startswith("none:"):
        check(False, f"{path.name} [{tag}]: `input_source` = {src_ref!r} không tồn tại "
                     "— biên bản trỏ tới một đầu vào không kiểm được")


def check_digest_file(path: Path) -> None:
    """Tệp tổng hợp: không trộn hai `model_served` khác nhau (bất biến 3)."""
    d = load(path)
    rows = d.get("receipts")
    if not isinstance(rows, list):
        return
    keys = {r.get("model_served") for r in rows if isinstance(r, dict)}
    keys.discard(None)
    check(len(keys) <= 1,
          f"{path.name}: trộn {len(keys)} khoá {sorted(keys)} trong một tệp tổng hợp — "
          "không cộng dồn kết quả của các khoá khác nhau")


def violations() -> int:
    for p in receipt_files():
        if "receipts" in p.read_text(encoding="utf-8")[:400] and p.stem.startswith("digest"):
            check_digest_file(p)
        else:
            check_receipt(p)
    return len(receipt_files())


def selftest() -> int:
    """5 phép phá + 1 đối chứng — mỗi phép phải làm cổng ĐỎ trên corpus tạm."""
    global RECEIPTS, FAILS, PASSES

    def rec(**over) -> dict:
        base = {
            "receipt_id": "R-TEST", "date": "2026-11-23",
            "model_requested": "m-latest", "model_served": "m-latest",
            "provider": "p", "input_sha256": "a" * 32, "output_sha256": "b" * 32,
            "artifact_bytes": 1234, "input_source": "none:no-file",
        }
        base.update(over)
        return base

    cases = [
        ("P1 thiếu `model_served`", [rec(model_served="")], "thiếu trường"),
        ("P2 trôi model không `drift_note`",
         [rec(model_served="m-2026-11-01")], "không có `drift_note`"),
        ("P3 biên bản có trường `score`", [rec(score=0.9)], "trường phán quyết"),
        ("P4 biên bản có nội dung tài liệu", [rec(excerpt="doanh thu 1,2 triệu")],
         "trường nội dung"),
        ("P5 hash không khớp tệp thật", [rec(input_source="CHANGED")], ""),
        ("P6 đối chứng: biên bản sạch KHÔNG bị bắt", [rec()], None),
    ]

    saved = RECEIPTS
    ok = 0
    try:
        for name, receipts, expect in cases:
            tmp = Path(tempfile.mkdtemp())
            rdir = tmp / "receipts"
            rdir.mkdir()
            if name.startswith("P5"):
                # Tạo một tệp thật, ghi hash SAI vào biên bản — đúng lỗi 41,4%.
                src = tmp / "changed.txt"
                src.write_text("nội dung đã bị đột biến\n", encoding="utf-8")
                receipts = [rec(input_source=str(src))]
            elif name.startswith("P6"):
                receipts = [rec()]
            (rdir / "R-TEST.json").write_text(
                json.dumps(receipts[0], ensure_ascii=False), encoding="utf-8")
            if name.startswith("P5"):
                # input_source là đường dẫn tuyệt đối ⇒ resolve_source tìm thấy.
                pass

            RECEIPTS, FAILS, PASSES = rdir, [], 0
            violations()

            if expect is None:
                if not FAILS:
                    ok += 1
                    print(f"  ✓ {name} → sạch (đúng)")
                else:
                    print(f"  ✗ {name} → BẮT OAN: {FAILS[0]}")
                continue
            hits = [f for f in FAILS if expect in f]
            if hits:
                ok += 1
                print(f"  ✓ {name} → đỏ: {hits[0]}")
            else:
                print(f"  ✗ {name} → LỌT (FAILS={FAILS})")
    finally:
        RECEIPTS, FAILS, PASSES = saved, [], 0

    # Bất biến 3 cần corpus riêng (tệp tổng hợp).
    tmp = Path(tempfile.mkdtemp())
    rdir = tmp / "receipts"
    rdir.mkdir()
    (rdir / "digest-2026-11.json").write_text(json.dumps({
        "receipts": [rec(), rec(model_served="m-2026-10-01", drift_note="x")],
    }, ensure_ascii=False), encoding="utf-8")
    saved = RECEIPTS
    RECEIPTS, FAILS, PASSES = rdir, [], 0
    try:
        violations()
        if any("trộn" in f for f in FAILS):
            ok += 1
            print(f"  ✓ P7 tệp tổng hợp trộn hai khoá → đỏ: {FAILS[0]}")
        else:
            print(f"  ✗ P7 tệp tổng hợp trộn hai khoá → LỌT (FAILS={FAILS})")
    finally:
        RECEIPTS, FAILS, PASSES = saved, [], 0

    total = len(cases) + 1
    if ok != total:
        print(f"RECEIPT LOCK SELFTEST: FAIL — {ok}/{total} phép thử đúng chiều")
        return 1
    print(f"RECEIPT LOCK SELFTEST: PASS — {ok}/{total} phép thử đúng chiều "
          f"({total - 1} phép phá + 1 đối chứng)")
    return 0


def new_receipt(args) -> int:
    """Sinh biên bản rỗng ĐÚNG schema — để không ai tự đoán hình dạng."""
    out = RECEIPTS / f"R-{args.date}-{args.model_served[:24].replace('/', '_')}.json"
    RECEIPTS.mkdir(exist_ok=True)
    src = args.input
    doc = {
        "receipt_id": out.stem,
        "date": args.date,
        "model_requested": args.model_requested,
        "model_served": args.model_served,
        "provider": args.provider,
        "input_source": src or "none:không có đầu vào tệp",
        "input_sha256": sha256_of((ROOT / src).resolve()) if src else "0" * 64,
        "output_sha256": "0" * 64,
        "artifact_bytes": 0,
        "note": ("Sinh bằng `receipt_lock.py --new`. `output_sha256`/`artifact_bytes` "
                 "phải được điền sau khi chạy thật — chưa điền thì biên bản không "
                 "chứng minh gì (docs/35 §4)."),
    }
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created {out.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Biên bản đo: khoá (model, phiên bản), không điểm số.")
    ap.add_argument("--audit", action="store_true", help="liệt kê biên bản + khoá")
    ap.add_argument("--selftest", action="store_true", help="kiểm 6 bất biến (CI)")
    ap.add_argument("--new", action="store_true", help="sinh biên bản rỗng đúng schema")
    ap.add_argument("--date", default="2026-11-23")
    ap.add_argument("--model-requested", dest="model_requested", default="")
    ap.add_argument("--model-served", dest="model_served", default="")
    ap.add_argument("--provider", default="")
    ap.add_argument("--input", default="")
    args = ap.parse_args()

    if args.audit:
        return audit()
    if args.selftest:
        return selftest()
    if args.new:
        if not (args.model_requested and args.model_served):
            print("--new cần --model-requested và --model-served", file=sys.stderr)
            return 2
        return new_receipt(args)

    n = violations()
    if FAILS:
        print(f"RECEIPT LOCK: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(f"RECEIPT LOCK: PASS — {PASSES} kiểm tra · 6 bất biến · {n} biên bản trong receipts/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
