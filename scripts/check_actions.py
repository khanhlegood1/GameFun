#!/usr/bin/env python3
"""check_actions.py — việc đã hứa phải có NGƯỜI, NGÀY, HẬU QUẢ, và BẰNG CHỨNG.

Vì sao có file này (docs/37):
    `docs/33`–`docs/36` đăng ký **tuyên bố** (đúng/sai) trong `pm/claims-registry.json`.
    Nhưng cùng bốn vòng đó còn đăng ký **việc phải làm** — P1 (ràng buộc biên),
    P2 (gộp root vì rent), và nhiều mục §9 khác — bằng **văn xuôi trong tài liệu**.
    Không cổng nào đọc được văn xuôi. Nghĩa là: một việc có hạn nằm trong văn xuôi
    **không có hạn** theo nghĩa máy kiểm được.

    Sổ này khác sổ tuyên bố ở một điểm quan trọng: tuyên bố đúng/sai, việc xong/chưa.
    Cả hai đều chết theo cùng một kiểu — không ai nhớ, và không có gì đỏ lên.

Năm bất biến (mỗi cái ứng với một cách một "todo" trở thành vật trang trí):

  1. **Có người và ngày.** `owner` phải là id có trong `people`; `due` phải là YYYY-MM-DD.
  2. **Quá hạn ⇒ ĐỎ**, trừ khi đã `DONE` kèm bằng chứng. (Giống `check_claims.py` bất biến 6,
     nhưng ở đây hậu quả là `block_if_unmet`, không phải `suggested_rewrite`.)
  3. **`DONE` mà không có `evidence` ⇒ ĐỎ.** Và `evidence` phải trỏ tới một tệp CÓ THẬT
     trong repo. "Đã xong" là một tuyên bố; nó cần cùng loại bằng chứng như mọi tuyên bố khác.
  4. **`not_before`: không được đóng SỚM.** Một việc đóng trước ngày nó *có thể* làm được
     là dấu hiệu mạnh nhất của một cổng bị làm cho xanh. Ví dụ: mục chờ `programs/` mà
     `programs/` chưa tồn tại thì không thể DONE.
  5. **`source_doc` phải tồn tại**, và mục phải có `why` + `block_if_unmet` — để mục đó
     không trôi khỏi lý do sinh ra nó.

Ba chế độ:

    python3 scripts/check_actions.py            # 5 bất biến
    python3 scripts/check_actions.py --audit     # bảng việc + hạn + số ngày còn lại
    python3 scripts/check_actions.py --selftest  # CI

Chỉ thư viện chuẩn, không mạng.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "pm" / "action-register.json"

# Người/đại diện được phép đứng tên. `AGENT` là hợp lệ với điều kiện `agent_allowed`.
PEOPLE_OK = {"LXK", "AGENT"}
STATUS_OK = {"OPEN", "DONE", "DROPPED"}
BLOCK_OK = {"revert", "remove", "accept", "escalate"}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Ngày hôm nay ghim qua biến môi trường để phép thử không phụ thuộc đồng hồ máy.
TODAY = date.fromisoformat(os.environ.get("GAME9K_TODAY") or date.today().isoformat())

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def load() -> dict:
    if not REGISTRY.exists():
        return {"actions": [], "people": {}}
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def evidence_paths(ev: str) -> list[Path]:
    """Rút ra mọi đường dẫn tệp từ chuỗi evidence rồi kiểm chúng có thật.

    Tên tệp TRẦN (`check_invariants_coverage.py`, không có thư mục) được thử thêm
    trong `scripts/` và `pm/` — vì đó là cách người ta thật sự viết bằng chứng
    ("chạy `foo.py`"), và một cổng đỏ vì *cách viết* chứ không vì *bằng chứng sai*
    là một cổng sẽ bị tắt. Nếu tên tệp không tồn tại ở đâu cả thì vẫn đỏ.
    """
    out = []
    for m in re.finditer(r"[\w./-]+\.(?:py|md|json|js|yml|yaml|txt)", ev):
        raw = m.group(0).rstrip(".,;)")
        cand = ROOT / raw
        if not cand.exists() and "/" not in raw:
            for sub in ("scripts", "pm", "docs"):
                alt = ROOT / sub / raw
                if alt.exists():
                    cand = alt
                    break
        out.append(cand)
    return out


def violations(reg: dict) -> int:
    actions = reg.get("actions") or []
    people = reg.get("people") or {}
    for a in actions:
        tag = a.get("id", "?")
        who = a.get("owner")

        # 1. Người + ngày.
        check(bool(who), f"[{tag}]: thiếu `owner`")
        if who:
            check(who in PEOPLE_OK,
                  f"[{tag}]: `owner` = {who!r} không phải người/đại diện hợp lệ {sorted(PEOPLE_OK)}")
            check(who in people or who == "AGENT",
                  f"[{tag}]: `owner` = {who!r} không có trong `people` của sổ")
        if who == "AGENT":
            check(bool(a.get("agent_allowed")),
                  f"[{tag}]: giao cho AGENT nhưng `agent_allowed` không phải true — "
                  "chỉ việc máy kiểm được mới được giao cho máy")

        due = a.get("due")
        check(bool(due), f"[{tag}]: thiếu `due` — không có mục 'để sau'")
        due_d = None
        if due:
            check(bool(DATE_RE.match(str(due))),
                  f"[{tag}]: `due` = {due!r} không phải ngày YYYY-MM-DD")
            if DATE_RE.match(str(due)):
                due_d = date.fromisoformat(str(due))

        nb = a.get("not_before")
        nb_d = None
        if nb:
            check(bool(DATE_RE.match(str(nb))),
                  f"[{tag}]: `not_before` = {nb!r} không phải ngày YYYY-MM-DD")
            if DATE_RE.match(str(nb)):
                nb_d = date.fromisoformat(str(nb))

        status = a.get("status")
        check(status in STATUS_OK,
              f"[{tag}]: `status` phải là OPEN / DONE / DROPPED (đang là {status!r})")

        # 2. Quá hạn.
        if due_d and status == "OPEN" and due_d < TODAY:
            check(False,
                  f"[{tag}]: QUÁ HẠN {due} (hôm nay {TODAY}) mà vẫn OPEN — "
                  f"làm `{a.get('block_if_unmet')}`, hoặc đổi status")

        # 3. DONE cần bằng chứng có thật.
        if status == "DONE":
            ev = a.get("evidence") or ""
            check(bool(ev.strip()), f"[{tag}]: DONE mà không có `evidence` — 'đã xong' là một tuyên bố")
            if ev.strip():
                paths = evidence_paths(ev)
                check(bool(paths),
                      f"[{tag}]: `evidence` không trỏ tới tệp nào — cần một đường dẫn kiểm được")
                for p in paths:
                    check(p.exists(),
                          f"[{tag}]: `evidence` trỏ tới {p.relative_to(ROOT) if p.is_relative_to(ROOT) else p} "
                          "nhưng tệp không tồn tại")

        # 4. Không đóng sớm.
        if status == "DONE" and nb_d and TODAY < nb_d:
            check(False,
                  f"[{tag}]: DONE trước `not_before` {nb} (hôm nay {TODAY}) — "
                  "một việc chỉ có thể làm được sau ngày X thì không thể xong trước X")

        # 5. Nguồn + lý do + hậu quả.
        src = a.get("source_doc")
        check(bool(src), f"[{tag}]: thiếu `source_doc`")
        if src:
            check((ROOT / str(src)).exists(),
                  f"[{tag}]: `source_doc` = {src!r} không tồn tại")
        check(bool(a.get("why")), f"[{tag}]: thiếu `why` — việc không có lý do là việc sẽ bị bỏ")
        check(a.get("block_if_unmet") in BLOCK_OK,
              f"[{tag}]: `block_if_unmet` phải là {sorted(BLOCK_OK)}")

    # 6. Đồ thị `blocked_by` phải là DAG và trỏ tới việc có thật.
    #    Không có bước này, "P1 chờ P8, P8 chờ P1" là một vòng lặp im lặng: cả hai
    #    đều OPEN, cả hai đều có hạn, và không cổng nào đỏ. Một cái chết mềm.
    by_id = {a.get("id"): a for a in actions}
    for a in actions:
        tag = a.get("id", "?")
        deps = a.get("blocked_by") or []
        check(isinstance(deps, list), f"[{tag}]: `blocked_by` phải là mảng")
        for dep in deps:
            check(dep in by_id, f"[{tag}]: `blocked_by` trỏ tới {dep!r} không có trong sổ")
            check(dep != tag, f"[{tag}]: tự chặn chính mình")
        # Người/tác nhân phải hành động — học từ mẫu WES của FDE (docs/44 §2).
        for who in a.get("stakeholder") or []:
            check(who in PEOPLE_OK, f"[{tag}]: `stakeholder` = {who!r} không hợp lệ")
        check(bool(a.get("stakeholder")),
              f"[{tag}]: thiếu `stakeholder` — việc không có ai phải hành động là việc sẽ đứng im")

    # Chu trình trên đồ thị phụ thuộc.
    state: dict[str, int] = {}  # 1 = đang thăm, 2 = xong

    def visit(node: str, path: list[str]) -> None:
        if state.get(node) == 1:
            cyc = " → ".join(path + [node])
            FAILS.append(f"`blocked_by` có CHU TRÌNH: {cyc} — không mục nào trong vòng này có thể bắt đầu")
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        for dep in (by_id.get(node) or {}).get("blocked_by") or []:
            if dep in by_id:
                visit(dep, path + [node])
        state[node] = 2

    for a in actions:
        if a.get("id") in by_id and state.get(a.get("id")) != 2:
            visit(a["id"], [])

    # 7. Việc OPEN mà bị chặn bởi một việc ĐÃ DROPPED là việc không bao giờ mở.
    for a in actions:
        for dep in a.get("blocked_by") or []:
            d = by_id.get(dep) or {}
            if d.get("status") == "DROPPED" and a.get("status") == "OPEN":
                FAILS.append(
                    f"[{a.get('id')}]: OPEN nhưng chờ {dep!r} đã DROPPED — việc này không bao giờ mở được"
                )

    return len(actions)


def audit(reg: dict) -> int:
    print("\nVIỆC PHẢI LÀM — người, ngày, hậu quả\n")
    print(f"{'#':6}{'hạn':13}{'còn':>6}  {'người':7}{'trạng thái':11}việc")
    print("─" * 100)
    for a in reg.get("actions") or []:
        due = a.get("due", "?")
        left = "?"
        try:
            left = str((date.fromisoformat(due) - TODAY).days)
        except ValueError:
            pass
        who = a.get("owner", "?")
        print(f"{a.get('id', '?'):6}{due:13}{left:>6}  {who:7}{a.get('status', '?'):11}"
              f"{a.get('title', '')[:58]}")
    print(f"\n{len(reg.get('actions') or [])} việc · hôm nay {TODAY}")
    print("Quá hạn ⇒ cổng ĐỎ trừ khi DONE kèm bằng chứng trỏ tới tệp có thật.")
    return 0


def selftest() -> int:
    """6 phép phá + 2 đối chứng, trên corpus tạm."""
    global REGISTRY, FAILS, PASSES

    def item(**over) -> dict:
        base = {
            "id": "T1",
            "title": "việc thử",
            "source_doc": "docs/37-action-register-and-contradiction-hunt.md",
            "why": "vì phép thử",
            "owner": "LXK",
            "agent_allowed": False,
            "not_before": "2026-11-01",
            "due": "2999-01-01",
            "block_if_unmet": "revert",
            "evidence_required": "tệp nào đó",
            "status": "OPEN",
        }
        base.update(over)
        return base

    cases = [
        ("P1 thiếu người", [item(owner="")], "thiếu `owner`"),
        ("P2 hạn là cụm mô tả", [item(due="trước khi launch")], "không phải ngày YYYY-MM-DD"),
        ("P3 quá hạn vẫn OPEN", [item(due="2020-01-01")], "QUÁ HẠN"),
        ("P4 DONE không bằng chứng", [item(status="DONE")], "không có `evidence`"),
        ("P5 DONE trước not_before", [
            item(status="DONE", not_before="2999-01-01",
                 evidence="scripts/check_actions.py"),
        ], "DONE trước `not_before`"),
        ("P6 đối chứng: DONE có bằng chứng thật", [
            item(status="DONE", evidence="scripts/check_actions.py xanh trong CI"),
        ], None),
        # Bằng chứng ghi bằng TÊN TỆP TRẦN là cách viết thật của con người
        # ("chạy check_invariants_coverage.py") — cổng phải giải được, không đỏ
        # vì cách viết. Xem `evidence_paths`.
        ("P8 đối chứng: evidence là tên tệp trần", [
            item(status="DONE", evidence="check_invariants_coverage.py --audit cho 12/12"),
        ], None),
    ]

    saved = REGISTRY
    ok = 0
    try:
        for name, actions, expect in cases:
            tmp = Path(tempfile.mkdtemp())
            reg = tmp / "action-register.json"
            reg.write_text(json.dumps(
                {"as_of": "2026-11-23",
                 "people": {"LXK": {"name": "người thử", "role": "PO"}},
                 "actions": actions}, ensure_ascii=False), encoding="utf-8")
            REGISTRY, FAILS, PASSES = reg, [], 0
            violations(load())
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
        REGISTRY, FAILS, PASSES = saved, [], 0

    # Bất biến 5b: source_doc không tồn tại.
    tmp = Path(tempfile.mkdtemp())
    reg = tmp / "action-register.json"
    reg.write_text(json.dumps({"people": {"LXK": {"name": "x"}},
                               "actions": [item(source_doc="docs/khong-ton-tai.md")]},
                              ensure_ascii=False), encoding="utf-8")
    saved = REGISTRY
    REGISTRY, FAILS, PASSES = reg, [], 0
    try:
        violations(load())
        if any("không tồn tại" in f for f in FAILS):
            ok += 1
            print(f"  ✓ P7 source_doc không tồn tại → đỏ: {FAILS[0]}")
        else:
            print(f"  ✗ P7 source_doc không tồn tại → LỌT (FAILS={FAILS})")
    finally:
        REGISTRY, FAILS, PASSES = saved, [], 0

    total = len(cases) + 1
    if ok != total:
        print(f"ACTION LOCK SELFTEST: FAIL — {ok}/{total} phép thử đúng chiều")
        return 1
    print(f"ACTION LOCK SELFTEST: PASS — {ok}/{total} phép thử đúng chiều "
          f"({total - 1} phép phá + 1 đối chứng)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Việc đã hứa: người, ngày, hậu quả, bằng chứng.")
    ap.add_argument("--audit", action="store_true", help="bảng việc + hạn")
    ap.add_argument("--selftest", action="store_true", help="kiểm 5 bất biến (CI)")
    args = ap.parse_args()

    if args.audit:
        return audit(load())
    if args.selftest:
        return selftest()

    reg = load()
    n = violations(reg)
    if FAILS:
        print(f"ACTION LOCK: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    open_n = sum(1 for a in reg.get("actions") or [] if a.get("status") == "OPEN")
    print(f"ACTION LOCK: PASS — {PASSES} kiểm tra · 5 bất biến · {n} việc ({open_n} OPEN)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
