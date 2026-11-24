#!/usr/bin/env python3
"""check_pm_supabase.py — sổ dự án trên Supabase phải nói ĐÚNG điều tài liệu nói.

Vì sao cần: `docs/37` (action register) và `docs/02` §4 (RLS: *cấm client ghi trực
tiếp*) đều là **văn xuôi**. Khi sổ được nạp vào Supabase, ba thứ có thể lệch mà
không ai thấy:

    · seed SQL lệch khỏi `pm/*.json`  → sổ JSON nói 8 việc, bảng có 7
    · migration bị sửa tay          → hash lệch, không ai biết
    · một policy write được thêm    → client ghi được, docs/02 §4 thành sai

Cổng này chạy **offline** (CI không gọi Supabase). Nó kiểm ba nguồn đối chiếu nhau:
`pm/*.json` ↔ `supabase/migrations/` ↔ `supabase/VERIFY.json` (bằng chứng đo trên
database thật, ghi ngày + ref).

Bốn bất biến:
    1. Migration khớp nguồn: `gen_supabase_migrations.py --print-digest` == `SHA256`.
    2. Seed chứa ĐỦ mọi `id` trong pm/action-register.json — không thiếu, không thừa.
    3. `VERIFY.json`: mọi bảng pm_* đều `rls=true`, `write_policies=0`, không quyền ghi.
    4. Ràng buộc `DONE ⇒ có evidence` tồn tại trong migration VÀ được chứng minh chặn.

Chạy: python3 scripts/check_pm_supabase.py [--selftest]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIG = ROOT / "supabase" / "migrations"
VERIFY = ROOT / "supabase" / "VERIFY.json"
REG = ROOT / "pm" / "action-register.json"
FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def inv_migrations_match_source() -> None:
    """Migration phải đúng là bản sinh từ nguồn — không sửa tay."""
    want = (MIG / "SHA256")
    check(want.exists(), "thiếu supabase/migrations/SHA256 — không có cách phát hiện sửa tay")
    if not want.exists():
        return
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gen_supabase_migrations.py"), "--print-digest"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        FAILS.append(f"không chạy được generator: {out.stderr.strip()[:200]}")
        return
    check(out.stdout.strip() == want.read_text(encoding="utf-8").strip(),
          "migration KHÔNG khớp bản sinh từ pm/*.json — ai đó sửa tay supabase/ (chạy lại --write)")


def inv_seed_covers_register() -> None:
    """Seed phải chứa đúng tập `id` của sổ JSON — không thiếu, không thừa."""
    seed = MIG / "30-pm-seed.sql"
    check(seed.exists(), "thiếu supabase/migrations/30-pm-seed.sql")
    if not seed.exists() or not REG.exists():
        return
    text = seed.read_text(encoding="utf-8")
    want = {a["id"] for a in json.loads(REG.read_text(encoding="utf-8"))["actions"]}
    # Chỉ khối `insert into pm_actions` mới đếm — `pm_people` cũng có mã dạng chữ.
    start = text.find("insert into pm_actions")
    if start < 0:
        FAILS.append("seed không có `insert into pm_actions`")
        return
    block = text[start:]
    got = set(re.findall(r"^  \('([A-Z]\d+)',", block, re.M))
    check(got == want,
          f"seed lệch sổ JSON — thiếu {sorted(want - got)}, thừa {sorted(got - want)}")


def inv_read_only(table: str, meta: dict) -> None:
    """Mỗi bảng phải bật RLS và KHÔNG cho client ghi (docs/02 §4)."""
    check(bool(meta.get("rls")), f"{table}: RLS tắt — bảng mở toang")
    for field in ("anon_write", "auth_update", "auth_delete"):
        check(meta.get(field) is False, f"{table}: `{field}` = {meta.get(field)!r}, phải `false` (docs/02 §4)")
    check(meta.get("write_policies") == 0,
          f"{table}: có {meta.get('write_policies')} policy ghi — client ghi được, docs/02 §4 thành sai")
    check(meta.get("anon_read") is True, f"{table}: `anon_read` phải `true` — sổ này không có PII")


def inv_verify_evidence(vf: dict) -> None:
    tables = vf.get("tables") or {}
    check(len(tables) >= 7, f"VERIFY.json chỉ có {len(tables)} bảng, cần ≥ 7")
    for table, meta in sorted(tables.items()):
        inv_read_only(table, meta)

    # Ràng buộc DONE ⇒ evidence: phải có trong migration VÀ được chứng minh chặn.
    core = (MIG / "10-pm-core.sql").read_text(encoding="utf-8") if (MIG / "10-pm-core.sql").exists() else ""
    check("pm_actions_done_needs_evidence" in core,
          "migration thiếu ràng buộc `pm_actions_done_needs_evidence` — docs/37 không được DB canh")
    probes = {p.get("name"): p for p in vf.get("constraint_probes") or []}
    for name, needle in (
        ("DONE mà không có evidence", "evidence"),
        ("đóng sớm trước not_before", "not_before"),
    ):
        p = probes.get(name)
        check(p is not None, f"VERIFY.json thiếu phép thử `{name}`")
        if p:
            check(p.get("blocked") is True,
                  f"phép thử `{name}` KHÔNG bị chặn (blocked={p.get('blocked')!r}) — ràng buộc không hoạt động")
            check(bool(p.get("by")), f"phép thử `{name}` không ghi được nó bị chặn bởi ràng buộc nào")

    # Bằng chứng phải có ngày và ref — nếu không, nó là lời tuyên bố không kiểm được.
    proj = vf.get("project") or {}
    check(bool(proj.get("ref")), "VERIFY.json thiếu `project.ref` — không biết đo trên project nào")
    check(bool(re.match(r"\d{4}-\d{2}-\d{2}$", str(proj.get("measured_at", "")))),
          "VERIFY.json thiếu `measured_at` dạng YYYY-MM-DD")
    check(len(vf.get("migrations_applied") or []) >= 3,
          "VERIFY.json ghi ít hơn 3 migration đã chạy")


def selftest() -> int:
    """Bốn phép phá trên bản sao TẠM — không sửa tệp thật."""
    global VERIFY, FAILS, PASSES
    import tempfile

    real = VERIFY
    good = json.loads(real.read_text(encoding="utf-8"))
    cases: list[tuple[str, bool]] = []

    def run(mutate, label: str, must_red: bool) -> None:
        global VERIFY, FAILS, PASSES
        data = json.loads(json.dumps(good))
        mutate(data)
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "VERIFY.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            VERIFY = p
            FAILS, PASSES = [], 0
            inv_verify_evidence(json.loads(p.read_text(encoding="utf-8")))
            red = bool(FAILS)
        VERIFY = real
        FAILS, PASSES = [], 0
        cases.append((label, red == must_red))

    run(lambda d: d["tables"]["pm_actions"].update(rls=False),
        "P1 tắt RLS một bảng → đỏ", True)
    run(lambda d: d["tables"]["pm_notes"].update(write_policies=1),
        "P2 thêm policy ghi → đỏ", True)
    run(lambda d: d["constraint_probes"].__setitem__(
            0, {**d["constraint_probes"][0], "blocked": False}),
        "P3 ràng buộc DONE không chặn → đỏ", True)
    run(lambda d: None, "P0 đối chứng: VERIFY.json gốc → xanh", False)

    ok = sum(1 for _, o in cases if o)
    for label, o in cases:
        print(f"  {'✓' if o else '✗'} {label}")
    if ok != len(cases):
        print(f"PM SUPABASE SELFTEST: FAIL — {ok}/{len(cases)}")
        return 1
    print(f"PM SUPABASE SELFTEST: PASS — {len(cases)}/{len(cases)} (1 đối chứng + 3 phép phá)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sổ dự án trên Supabase khớp docs + pm/*.json.")
    ap.add_argument("--selftest", action="store_true", help="4 phép thử (CI)")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    check(VERIFY.exists(), "thiếu supabase/VERIFY.json — không có bằng chứng đo trên DB")
    if VERIFY.exists():
        vf = json.loads(VERIFY.read_text(encoding="utf-8"))
        inv_verify_evidence(vf)
        inv_migrations_match_source()
        inv_seed_covers_register()

    if FAILS:
        print(f"PM SUPABASE: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    vf = json.loads(VERIFY.read_text(encoding="utf-8"))
    print(
        f"PM SUPABASE: PASS — {PASSES} kiểm tra · 4 bất biến · "
        f"7 bảng RLS chỉ-đọc · {len(vf['constraint_probes'])} phép thử ràng buộc bị chặn · "
        f"seed khớp {len(json.loads(REG.read_text(encoding='utf-8'))['actions'])} việc"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
