#!/usr/bin/env python3
"""gen_portal_data.py — sinh `portal/data.json` từ repo, không từ tay người.

Trang `portal/` là bản chiếu MỘT CHIỀU của hai nguồn sự thật đã có:

    pm/action-register.json   → việc (mã P*, người, hạn, phụ thuộc)
    portal/docs/08-adr/*.md   → quyết định kiến trúc (mã ADR-*)

Vì sao phải sinh bằng máy thay vì viết JSON tay: một bảng điều khiển tự nhập số
là một bảng điều khiển có thể nói dối mà không ai biết. `scripts/check_portal.py`
chạy lại generator rồi so từng byte — sửa tay `portal/data.json` là cổng ĐỎ.

Điều KHÔNG làm: không tự thêm ADR nào không có trong `docs/08-adr/`, không tự
đoán trạng thái ký. Chỉ mục README có thể nhắc tới ADR chưa có tệp — những dòng
đó được đánh dấu `state: "missing"` và hiện ra như một thiếu sót, không bị ẩn.

Chạy: python3 scripts/gen_portal_data.py [--check]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ADR_DIR = ROOT / "portal" / "docs" / "08-adr"
REGISTER = ROOT / "pm" / "action-register.json"
OUT = ROOT / "portal" / "data.json"

NUM_RE = re.compile(r"ADR-(\d{4})")
INDEX_ROW_RE = re.compile(r"^\| \[(\d{4})\]\(([^)]+)\) \| (.+?) \| (.+?) \| (.+?) \|")


def cell(text: str, label: str) -> str | None:
    """Đọc một ô trong bảng meta 2 cột ở đầu ADR: `| **Nhãn** | giá trị |`."""
    m = re.search(r"\| \*\*" + re.escape(label) + r"\*\* \| ([^|\n]+?)\s*\|", text)
    return m.group(1).strip() if m else None


def classify(status: str) -> str:
    """Trạng thái ADR, suy từ chữ người viết — không suy từ số thứ tự.

    `Accepted (chờ ký)` KHÔNG phải `accepted`: quyết định đã nhận về nội dung
    nhưng người có tên chưa ký. Trộn hai thứ đó là cách một ADR chưa ký được
    dùng để biện minh cho mã đã merge (README của thư mục này cấm đúng điều đó).
    """
    low = status.lower()
    if "superseded" in low:
        return "superseded"
    if low.startswith("rejected"):
        return "rejected"
    if "chờ ký" in low or "proposed" in low:
        return "proposed"
    if "accepted" in low:
        return "accepted"
    return "unknown"


def read_adrs() -> tuple[list[dict], dict[str, dict]]:
    index: dict[str, dict] = {}
    readme = ADR_DIR / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            m = INDEX_ROW_RE.match(line)
            if m:
                index[m.group(1)] = {
                    "title": m.group(3), "status_listed": m.group(4),
                    "impact": m.group(5), "file": m.group(2),
                }

    items: list[dict] = []
    for path in sorted(ADR_DIR.glob("ADR-*.md")):
        m = NUM_RE.search(path.name)
        if not m:
            continue
        num = m.group(1)
        text = path.read_text(encoding="utf-8")
        head = text.splitlines()[0].lstrip("# ").strip()
        title = head.split("·", 1)[1].strip() if "·" in head else head
        status = cell(text, "Trạng thái") or index.get(num, {}).get("status_listed", "")
        decider = cell(text, "Người quyết") or ""
        items.append({
            "id": f"ADR-{num}",
            "num": num,
            "file": path.name,
            "title": title,
            "status_raw": status,
            "state": classify(status),
            "date": cell(text, "Ngày") or "",
            "proposer": cell(text, "Người đề xuất") or "",
            "decider": decider,
            "impact": cell(text, "Ảnh hưởng") or index.get(num, {}).get("impact", "—"),
            # "chờ ký" là dấu vết của một chữ ký CHƯA có. Nó phải hiện ra.
            "needs_signature": "chờ ký" in decider or "chờ ký" in status,
            "sections": [l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("## ")],
            "bytes": len(text.encode()),
        })
    return items, index


def missing_rows(items: list[dict], index: dict[str, dict]) -> list[dict]:
    """ADR có trong chỉ mục nhưng KHÔNG có tệp. Đây là thiếu sót, không phải bị bỏ."""
    have = {i["num"] for i in items}
    out = []
    for num in sorted(set(index) - have):
        row = index[num]
        out.append({
            "id": f"ADR-{num}", "num": num, "file": None,
            "title": row["title"].strip("*"),
            "status_raw": row["status_listed"].strip("*"),
            "state": "missing", "date": "", "proposer": "", "decider": "",
            "impact": row["impact"],
            # Thiếu tệp MÀ chỉ mục còn ghi "chờ ký" là hai thiếu sót chồng lên
            # nhau. Vẫn phải bật cờ — nếu không, cổng 25 bắt được nhưng vì lý do
            # sai (nó tưởng dòng này đã ký).
            "needs_signature": "chờ ký" in row["status_listed"],
            "sections": [], "bytes": 0,
        })
    return out


def build() -> dict:
    assert ADR_DIR.exists(), f"thiếu thư mục {ADR_DIR}"
    assert REGISTER.exists(), f"thiếu {REGISTER}"
    items, index = read_adrs()
    absent = missing_rows(items, index)
    reg = json.loads(REGISTER.read_text(encoding="utf-8"))
    return {
        "$comment": (
            "Sinh tự động bởi scripts/gen_portal_data.py từ portal/docs/08-adr/*.md "
            "và pm/action-register.json. ĐỪNG SỬA TAY: scripts/check_portal.py so lại từng byte."
        ),
        "$schema_version": 1,
        "generated_from": {"adr_dir": "portal/docs/08-adr", "register": "pm/action-register.json"},
        "as_of": reg["as_of"],
        "adr": {
            "items": items + absent,
            "counts": {
                "total": len(items) + len(absent),
                "on_disk": len(items),
                "listed_but_absent": len(absent),
                "proposed": sum(1 for i in items if i["state"] == "proposed"),
                "accepted": sum(1 for i in items if i["state"] == "accepted"),
                "needs_signature": sum(1 for i in items if i["needs_signature"]),
            },
        },
        "actions": reg["actions"],
        "people": reg["people"],
        "policy": reg["policy"],
    }


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sinh portal/data.json từ repo.")
    ap.add_argument("--check", action="store_true", help="không ghi, chỉ so với bản đã commit")
    args = ap.parse_args(argv)

    text = render(build())
    if args.check:
        if not OUT.exists():
            print(f"PORTAL DATA: FAIL — thiếu {OUT.relative_to(ROOT)}")
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print("PORTAL DATA: FAIL — portal/data.json KHÁC bản sinh từ repo "
                  "(sửa tay, hoặc quên chạy lại generator)")
            return 1
        print("PORTAL DATA: PASS — data.json khớp bản sinh từ repo")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    d = json.loads(text)
    c = d["adr"]["counts"]
    print(f"đã ghi {OUT.relative_to(ROOT)} — "
          f"{c['total']} ADR ({c['on_disk']} có tệp, {c['listed_but_absent']} thiếu tệp, "
          f"{c['proposed']} chờ ký) · {len(d['actions'])} việc")
    return 0


if __name__ == "__main__":
    sys.exit(main())
