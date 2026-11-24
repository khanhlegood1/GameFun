#!/usr/bin/env python3
"""gen_supabase_migrations.py — dựng migration Supabase TỪ `pm/*.json`.

Vì sao sinh thay vì viết tay: `pm/action-register.json` và
`pm/claims-registry.json` là **nguồn**. Nếu seed SQL viết tay, sổ JSON và bảng
Supabase sẽ lệch nhau — và sẽ lệch im lặng, vì không ai diff hai định dạng khác
nhau. Sinh ở đây + so hash ở `check_pm_supabase.py` là cách duy nhất để độ lệch
thành **đỏ**.

Chạy:
    python3 scripts/gen_supabase_migrations.py --write   # ghi đè supabase/
    python3 scripts/gen_supabase_migrations.py           # chỉ in ra, không ghi
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PM = ROOT / "pm"
SQL = PM / "sql"
OUT = ROOT / "supabase" / "migrations"

# Thứ tự file quyết định thứ tự chạy. `10` = cấu trúc, `20` = RLS, `30` = dữ liệu.
ORDER = ["10-pm-core.sql", "20-pm-rls.sql", "30-pm-seed.sql"]


def q(text: str | None) -> str:
    """Chuỗi SQL an toàn. Dùng dollar-quote để không phải lo dấu nháy đơn."""
    if text is None:
        return "null"
    if "'" not in text and "\\" not in text:
        return "'" + text + "'"
    tag = "$q$"
    while tag in text:
        tag = "$q" + "q" + "$"
    return tag + text + tag


def seed_sql() -> str:
    """Sinh phần seed từ pm/*.json. Tất định: cùng JSON ⇒ cùng bytes."""
    reg = json.loads((PM / "action-register.json").read_text(encoding="utf-8"))
    claims = json.loads((PM / "claims-registry.json").read_text(encoding="utf-8"))

    out: list[str] = []
    out.append("-- Nguồn: pm/action-register.json · pm/claims-registry.json")
    out.append(f"-- as_of: {reg.get('as_of', '?')}")
    out.append("")
    out.append("begin;")
    out.append("")

    # --- người: `people` của action register + `accountable` của claims registry
    people: dict[str, dict] = dict(reg.get("people") or {})
    acc = claims.get("accountable") or {}
    if acc.get("id") and acc["id"] not in people:
        people[acc["id"]] = {"name": acc.get("name", ""), "role": acc.get("role", "")}
    # AGENT là tác nhân, không phải người — `owner_protocol` nói rõ điều này.
    people.setdefault("AGENT", {"name": "Tác nhân tự động", "role": "agent"})

    out.append("insert into pm_people (code, name, kind, role, tz) values")
    rows = []
    for code, info in sorted(people.items()):
        kind = "agent" if code == "AGENT" else "human"
        rows.append(
            f"  ({q(code)}, {q(info.get('name', code))}, {q(kind)}, "
            f"{q(info.get('role', ''))}, 'Asia/Ho_Chi_Minh')"
        )
    out.append(",\n".join(rows))
    out.append("on conflict (code) do update set name = excluded.name, role = excluded.role;")
    out.append("")

    # --- việc
    out.append("insert into pm_actions (id, title, source_doc, why, owner_code, agent_allowed,")
    out.append("  owner_reason, not_before, due, block_if_unmet, block_note, evidence_req,")
    out.append("  status, done_on, evidence) values")
    rows = []
    for a in reg["actions"]:
        owner = a.get("owner", "AGENT")
        if owner not in people:
            raise SystemExit(f"{a['id']}: owner {owner!r} không có trong `people` — sổ JSON hỏng")
        note = a.get("block_if_unmet_note") or ""
        rows.append(
            "  (" + ", ".join([
                q(a["id"]),
                q(a["title"]),
                q(a.get("source_doc") or a.get("source", "")),
                q(a.get("why", "")),
                q(owner),
                "true" if a.get("agent_allowed") else "false",
                q(a.get("owner_reason", "")),
                q(a.get("not_before")) if a.get("not_before") else "null",
                q(a.get("due")),
                q(a.get("block_if_unmet", "accept")),
                q(note),
                q(a.get("evidence_required", "")),
                q(a.get("status", "OPEN")),
                q(a.get("done_on")) if a.get("done_on") else "null",
                q(a.get("evidence")) if a.get("evidence") else "null",
            ]) + ")"
        )
    out.append(",\n".join(rows))
    # Không `do update` mọi cột: `evidence` là bằng chứng, ghi đè nó là xoá dấu.
    out.append(
        "on conflict (id) do update set title = excluded.title, due = excluded.due, "
        "status = excluded.status, done_on = excluded.done_on, evidence = excluded.evidence;"
    )
    out.append("")

    # --- phụ thuộc + người phải hành động (docs/44 §2.2)
    deps = [(a["id"], d, a.get("blocked_by_note", "")) for a in reg["actions"] for d in a.get("blocked_by") or []]
    if deps:
        out.append("insert into pm_action_deps (action_id, blocked_by, note) values")
        out.append(",\n".join(f"  ({q(a)}, {q(b)}, {q(n)})" for a, b, n in deps))
        out.append("on conflict (action_id, blocked_by) do update set note = excluded.note;")
    else:
        out.append("-- không có phụ thuộc nào")
    out.append("")

    stakes = [(a["id"], who) for a in reg["actions"] for who in a.get("stakeholder") or []]
    if stakes:
        out.append("insert into pm_action_stakeholders (action_id, person_code) values")
        out.append(",\n".join(f"  ({q(a)}, {q(w)})" for a, w in stakes))
        out.append("on conflict do nothing;")
    out.append("")
    out.append("commit;")
    out.append("")
    return "\n".join(out)


def build() -> dict[pathlib.Path, str]:
    files: dict[pathlib.Path, str] = {}
    for name in ORDER[:2]:
        files[OUT / name] = (SQL / name).read_text(encoding="utf-8")
    header = (
        "-- SINH TỰ ĐỘNG bởi scripts/gen_supabase_migrations.py — ĐỪNG SỬA TAY.\n"
        "-- Nguồn: pm/sql/*.sql và pm/*.json. Sửa nguồn rồi chạy lại.\n"
    )
    files[OUT / "30-pm-seed.sql"] = header + "\n" + seed_sql()
    return files


def digest(files: dict[pathlib.Path, str]) -> str:
    h = hashlib.sha256()
    for p in sorted(files, key=lambda x: x.name):
        h.update(p.name.encode())
        h.update(b"\0")
        h.update(files[p].encode("utf-8"))
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh migration Supabase từ pm/*.json.")
    ap.add_argument("--write", action="store_true", help="ghi vào supabase/migrations/")
    ap.add_argument("--print-digest", action="store_true", help="chỉ in sha256 của bộ tệp")
    args = ap.parse_args()

    files = build()
    if args.print_digest:
        print(digest(files))
        return 0
    if not args.write:
        for p, text in files.items():
            print(f"===== {p.relative_to(ROOT)} =====")
            print(text)
        print(f"===== sha256: {digest(files)} =====")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    for p, text in files.items():
        p.write_text(text, encoding="utf-8")
    (OUT / "SHA256").write_text(digest(files) + "\n", encoding="utf-8")
    print(f"đã ghi {len(files)} migration · sha256 {digest(files)[:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
