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


# Ba format header đã gặp thật trong 35 tệp ADR. Không phải "cho chắc" — mỗi
# dòng dưới đây là một tệp thật đã làm generator đọc ra `None`:
#   bảng   `| **Trạng thái** | Accepted (chờ ký) |`      ADR-0001..0018
#   inline `**Trạng thái:** Accepted`                     ADR-0019..0033, 0035, 0036
#   gạch   `- **Trạng thái:** Proposed`                   ADR-0034
FIELD_PATTERNS = {
    "Trạng thái": [
        r"(?m)^\|\s*\*\*Trạng thái\*\*\s*\|[ \t]*([^|\n]+?)[ \t]*\|",
        r"(?m)^\*\*Trạng thái:\*\*[ \t]*([^\n]+?)[ \t]*$",
        r"(?m)^[-*]{0,2}[ \t]*\*\*Trạng thái:\*\*[ \t]*([^\n]+?)[ \t]*$",
    ],
    "Ngày": [
        r"(?m)^\|\s*\*\*Ngày\*\*\s*\|[ \t]*([^|\n]+?)[ \t]*\|",
        r"(?m)^\*\*Ngày:\*\*[ \t]*([^\n]+?)[ \t]*$",
        r"(?m)^[-*]{0,2}[ \t]*\*\*Ngày:\*\*[ \t]*([^\n]+?)[ \t]*$",
    ],
    "Người đề xuất": [
        r"(?m)^\|\s*\*\*Người đề xuất\*\*\s*\|[ \t]*([^|\n]+?)[ \t]*\|",
        r"(?m)^\*\*Người đề xuất:\*\*[ \t]*([^\n]+?)[ \t]*$",
        r"(?m)^[-*]{0,2}[ \t]*\*\*Người đề xuất:\*\*[ \t]*([^\n]+?)[ \t]*$",
    ],
    "Người quyết": [
        # 1. Bảng meta 2 cột (ADR-0001..0018):  | **Người quyết** | Founder *(chờ ký)* |
        r"(?m)^\|\s*\*\*Người quyết\*\*\s*\|[ \t]*([^|\n]+?)[ \t]*\|",
        # 2. Gộp hai vai trên MỘT dòng (ADR-0019..0036):
        #      **Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
        #      - **Người đề xuất:** ... · **Người quyết:** ...
        #    Mẫu này phải đứng TRƯỚC mẫu 3 vì `[-*]` khớp cả `*` (in đậm), nên nếu
        #    đứng sau nó sẽ nuốt mất dòng gộp và trả về chuỗi rỗng.
        r"(?m)^[-*]{0,2}[ \t]*\*\*Người đề xuất:\*\*[^\n]*?·[^\n]*?\*\*Người quyết:\*\*[ \t]*([^\n]+?)[ \t]*$",
        # 3. Một mình một dòng, có hay không gạch đầu dòng.
        r"(?m)^[-*]{0,2}[ \t]*\*\*Người quyết:\*\*[ \t]*([^\n]+?)[ \t]*$",
    ],
    "Ảnh hưởng": [
        r"(?m)^\|\s*\*\*Ảnh hưởng\*\*\s*\|[ \t]*([^|\n]+?)[ \t]*\|",
        r"(?m)^\*\*Ảnh hưởng:\*\*[ \t]*([^\n]+?)[ \t]*$",
        r"(?m)^[-*]{0,2}[ \t]*\*\*Ảnh hưởng:\*\*[ \t]*([^\n]+?)[ \t]*$",
    ],
}


def cell(text: str, label: str) -> str | None:
    """Đọc một trường header, bất kể nó được viết theo format nào trong ba format."""
    for pat in FIELD_PATTERNS.get(label, []):
        m = re.search(pat, text)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return None


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


# Vai → người. Ghi TƯỜNG MINH thay vì suy diễn, để khi vai đổi người thì phải
# sửa đúng một dòng ở đây và cổng sẽ hỏi. `Project Owner` = `Lê Xuân Khánh` là
# điều 25 tệp ADR tự nói ("Project Owner (Lê Xuân Khánh)").
ROLE_TO_PERSON = {
    "Project Owner": "Lê Xuân Khánh",
}
# Vai KHÔNG có người: chức danh trống, không phân biệt được với một chỗ chưa điền.
UNFILLED_ROLES = ("Principal Architect", "Tech Lead", "Founder", "Legal", "Security Lead")

# ─────────────────────────────────────────────────────────────────────────────
# HAI câu hỏi khác nhau, và tôi từng trả lời gộp chúng thành một (docs/47 §2):
#
#   (A) "Ai giữ vai này?"        → ROLE_HOLDER        (một khẳng định về con người)
#   (B) "ADR này đã được ký chưa?" → signature       (một khẳng định về quyết định)
#
# Biết (A) KHÔNG suy ra (B). Người giữ vai vẫn có thể chưa ký một ADR cụ thể.
# Gộp hai câu này lại là cách một dòng `Principal Architect *(chờ ký)*` biến thành
# một chữ ký không tồn tại — đúng lỗi docs/46 §2 đi bắt.
#
# ⚠ `ROLE_HOLDER` CHỈ được điền khi PO xác nhận TƯỜNG MINH, và mỗi mục phải có
# căn cứ. Thêm một dòng ở đây KHÔNG làm ADR nào được ký: `signature` chỉ đổi khi
# chính tệp ADR đổi. Đây là chốt chặn để không ai (kể cả tôi) "sửa" 18 chữ ký
# bằng cách sửa bảng tra cứu.
# ─────────────────────────────────────────────────────────────────────────────
ROLE_HOLDER: dict[str, dict] = {
    # PO xác nhận đích danh ngày 2026-11-24: "Tôi cũng là Founder, PO, TL, PA."
    # Đây là SỰ THẬT ĐƯỢC XÁC NHẬN, không phải suy đoán từ một câu nói về vai khác.
    # Và — quan trọng — nó KHÔNG ký ADR nào. Xem docs/48 §2.2.
    "Founder": {"person": "Lê Xuân Khánh",
                "basis": "PO xác nhận 2026-11-24 (4 vai: Founder · PO · TL · PA)"},
    "Project Owner": {"person": "Lê Xuân Khánh",
                      "basis": "PO xác nhận 2026-11-24 · trùng với 25 tệp ADR ghi 'Project Owner (Lê Xuân Khánh)'"},
    "Tech Lead": {"person": "Lê Xuân Khánh",
                  "basis": "PO xác nhận 2026-11-24 (4 vai: Founder · PO · TL · PA)"},
    "Principal Architect": {"person": "Lê Xuân Khánh",
                            "basis": "PO xác nhận 2026-11-24 (4 vai: Founder · PO · TL · PA)"},
}


def person_for(decider: str) -> str:
    """Người thật đứng sau `Người quyết`, hoặc rỗng nếu đó chỉ là một chức danh.

    Tra theo thứ tự: tên ghi ngay trong tệp → `ROLE_HOLDER` (chỉ khi PO đã xác
    nhận). Không đoán bừa: "Founder" không phải một cái tên.
    """
    d = (decider or "").strip()
    if not d:
        return ""
    for role, who in ROLE_TO_PERSON.items():
        if role in d:
            return who
    for role, info in ROLE_HOLDER.items():
        if role in d:
            return info["person"]
    return ""


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
            "decider_person": person_for(decider),
            # Vai này có người giữ (do PO xác nhận), và căn cứ là gì. Tách khỏi
            # `signature`: biết ai giữ vai không có nghĩa ADR này đã được ký.
            "role_holder": next(
                ({**info, "role": r} for r, info in ROLE_HOLDER.items() if r in decider),
                None,
            ),
            "impact": cell(text, "Ảnh hưởng") or index.get(num, {}).get("impact", "—"),
            # "chờ ký" là dấu vết của một chữ ký CHƯA có. Nó phải hiện ra.
            "needs_signature": "chờ ký" in decider or "chờ ký" in status,
            # AI THỰC SỰ KÝ — ba giá trị, không phải boolean, vì có hai cách khác
            # nhau để chưa ký và chúng cần hai câu trả lời khác nhau:
            #   named      có tên người trong tệp                     → xong
            #   role_only  có chức danh ("Principal Architect")      → phải hỏi AI
            #   unsigned   có chữ "chờ ký" nhưng không có gì khác    → phải ký
            # CHỮ KÝ = "tệp có nói nó ĐANG CHỜ ai ký hay không", không phải
            # "có tên riêng hay không". Sửa hướng này là kết quả của việc đọc
            # `hve-core` adr-standards §"Personas, Not People" (docs/48 §2.2):
            # ghi NGƯỜI GIỮ VAI là cách ĐƯỢC ƯU TIÊN, nên `Project Owner` có người
            # giữ ĐÃ XÁC NHẬN là một chữ ký hợp lệ — dù tệp không ghi tên riêng.
            #   · `Project Owner`              (có người giữ)  → named
            #   · `Principal Architect *(chờ ký)*` (có người giữ) → VẪN chưa ký,
            #     vì chính tệp nói nó đang chờ. Biết ai giữ vai không xoá chữ "chờ ký".
            "signature": (
                "unsigned" if not decider
                else ("role_only" if ("chờ ký" in decider.lower()) or not person_for(decider)
                      else "named")
            ),
            # `display_state`: thứ được PHÉP hiện trên portal. Không bao giờ nói
            # "đã nhận" cho một ADR chưa có người ký — dù tệp ghi `Accepted`.
            # Tách khỏi `state` (đọc nguyên văn từ tệp) để không sửa lịch sử:
            # tệp vẫn nói `Accepted`, portal nói "chờ người ký".
            "display_state": None,   # điền bên dưới
            "sections": [l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("## ")],
            "bytes": len(text.encode()),
        })
    for i in items:
        if i["signature"] in ("role_only", "unsigned"):
            i["display_state"] = "proposed"
            i["needs_signature"] = True
        else:
            i["display_state"] = i["state"]
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
            "state": "missing", "date": "", "proposer": "", "decider": "", "decider_person": "",
            "impact": row["impact"],
            # Thiếu tệp MÀ chỉ mục còn ghi "chờ ký" là hai thiếu sót chồng lên
            # nhau. Vẫn phải bật cờ — nếu không, cổng 25 bắt được nhưng vì lý do
            # sai (nó tưởng dòng này đã ký).
            "needs_signature": "chờ ký" in row["status_listed"],
            "signature": "no_file",
            "display_state": "missing",
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
                "signed_by_named_person": sum(1 for i in items if i["signature"] == "named"),
                "held_by_role_only": sum(1 for i in items if i["signature"] == "role_only"),
                "unsigned": sum(1 for i in items if i["signature"] == "unsigned"),
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
