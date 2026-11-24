#!/usr/bin/env python3
"""check_decisions.py — quyết định nằm trong văn xuôi là quyết định không có hạn.

Học từ `Awesome-FDE-Roadmap` (MIT, docs/44) §2.2 mẫu "Site Survey": *"Người chịu
trách nhiệm là NGƯỜI, hạn là NGÀY, và mỗi quyết định có một `stakeholder` đã đồng
ý."* Repo này đã có `docs/34` (người + hạn cho TUYÊN BỐ) và `docs/37` (người +
hạn cho VIỆC). Thiếu đúng một loại: **QUYẾT ĐỊNH** — thứ nằm ở cột `R1..R4` trong
bảng §7 của nhiều tài liệu, có người, có lý do, nhưng **không có hạn** và **không
mã**.

Ba bất biến:
    1. Mọi tài liệu có mục "Chưa làm" với cột mã `R*` phải khai bảng đó vào
       `DECISION_TABLES` — miễn trừ phải viết ra, không ngầm.
    2. Mỗi quyết định cần NGƯỜI quyết có trong `DECISION_TABLES[doc]` và một mã
       việc `P*` **đang có hạn** trong `pm/action-register.json`.
    3. Cổng không được chết: phải thấy ≥ 4 quyết định, nếu không thì glob hỏng.

Chạy: python3 scripts/check_decisions.py [--audit|--selftest]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REG = ROOT / "pm" / "action-register.json"
FAILS: list[str] = []
PASSES = 0

# Bảng quyết định → việc đã đăng ký. Mỗi dòng là một QUYẾT ĐỊNH của con người,
# không phải suy đoán. Thêm dòng ở đây là một hành động có ý thức.
DECISION_TABLES = {
    # docs/41 §7 R1 — chọn thứ tự sản phẩm (LXK)
    "docs/41-testing-is-the-product.md": "P8",
}
# Tài liệu có cột `R*` nhưng đó là bảng TỪ CHỐI (Reject), không phải quyết định
# chờ người. Khai tường minh + lý do, để không ai phải đoán.
REJECTION_TABLES = {
    "docs/13-affiliate-growth-loop.md": "bảng từ chối mô hình affiliate",
    "docs/14-growth-tools-and-measurement.md": "bảng từ chối công cụ",
    "docs/15-livestream-tools-and-token-question.md": "bảng từ chối mô hình livestream",
    "docs/16-anchor-game-for-kol.md": "bảng từ chối game neo",
    "docs/17-second-screen-race.md": "bảng từ chối cơ chế đua",
    "docs/18-flagship-template-review.md": "bảng từ chối mẫu flagship",
    "docs/19-gitcoin-patterns.md": "bảng từ chối mẫu Gitcoin",
    "docs/20-proximax-teardown-storage.md": "bảng từ chối storage",
    "docs/21-starter-kit-spec-verification.md": "bảng từ chối lựa chọn kỹ thuật",
    "docs/22-agent-sdk-workflow-patterns.md": "bảng từ chối mẫu SDK",
    "docs/23-dino-race-starter-kit.md": "bảng từ chối cơ chế đua khủng long",
    "docs/24-agent-loop-lessons.md": "bảng từ chối vòng lặp agent",
    "docs/25-decisions-api-for-project-management.md": "bảng từ chối Decisions API",
    "docs/26-belief-record-project-memory.md": "bảng từ chối ghi chép dự án",
    "docs/27-sdk-contract-poki-vs-xsolla.md": "bảng từ chối hợp đồng SDK",
    "docs/28-sdk-contract-lock-and-what-not-to-copy.md": "bảng từ chối sao chép",
    "docs/29-sandbox-errors-and-sdk-boundary.md": "bảng từ chối ranh giới sandbox",
    "docs/30-openrouter-deterministic-egress.md": "bảng từ chối LLM trong cổng",
    "docs/31-gate-ladder-and-agent-honesty.md": "bảng từ chối thang cổng",
    "docs/32-sdk-manifest-and-release-evidence.md": "bảng từ chối hồ sơ SDK",
    "docs/33-claim-taxonomy-version-unit.md": "bảng từ chối cách đặt tên",
    "docs/34-accountable-owner-and-claims-register.md": "bảng từ chối cách ghi tên",
    "docs/35-measurement-receipt-model-version-lock.md": "bảng từ chối đo lường",
    # docs/36–37 đánh số R liên tục 13→20 (không reset về R1), nên dò `R*` bắt được;
    # nội dung vẫn là bảng TỪ CHỐI, không phải quyết định chờ người.
    "docs/36-kvu-lemmas-and-the-version-unit.md": "bảng từ chối cách trích số KVU (R13–R16)",
    "docs/37-action-register-and-contradiction-hunt.md": "bảng từ chối cách làm cổng mâu thuẫn (R17–R20)",
}

# Một dòng quyết định: `| **R1** | ... |` (cột mã in đậm).
ROW_RE = re.compile(r"(?m)^\|\s*\*\*(R\d+)\*\*\s*\|")


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def has_r_rows(path: pathlib.Path) -> int:
    return len(ROW_RE.findall(path.read_text(encoding="utf-8")))


def registered() -> dict[str, dict]:
    return {a["id"]: a for a in json.loads(REG.read_text(encoding="utf-8"))["actions"]}


def violations() -> int:
    acts = registered()
    seen = 0
    for path in sorted(DOCS.glob("*.md")):
        n = has_r_rows(path)
        if not n:
            continue
        rel = f"docs/{path.name}"
        if rel in REJECTION_TABLES:
            continue
        seen += n
        target = DECISION_TABLES.get(rel)
        if not target:
            FAILS.append(
                f"{rel}: có {n} dòng `R*` mà KHÔNG khai vào DECISION_TABLES lẫn "
                "REJECTION_TABLES — quyết định đang nằm trong văn xuôi"
            )
            continue
        a = acts.get(target)
        if not a:
            FAILS.append(f"{rel}: trỏ tới việc `{target}` không có trong pm/action-register.json")
            continue
        check(bool(a.get("due")), f"{rel}: việc `{target}` không có `due` — quyết định không có hạn")
        check(bool(a.get("stakeholder")),
              f"{rel}: việc `{target}` không có `stakeholder` — không biết ai đồng ý")
    check(seen >= 4, f"chỉ thấy {seen} dòng quyết định — cổng có thể đã ngừng kiểm")
    return seen


def audit() -> int:
    acts = registered()
    print("\nBẢNG QUYẾT ĐỊNH — quyết định nào đã có hạn?\n")
    print(f"{'Tài liệu':52}{'Việc':7}{'Chủ':8}{'Hạn':13}Trạng thái")
    print("─" * 96)
    for rel, pid in sorted(DECISION_TABLES.items()):
        a = acts.get(pid) or {}
        print(f"{rel:52}{pid:7}{a.get('owner','?'):8}{str(a.get('due','—')):13}{a.get('status','KHÔNG CÓ')}")
    print(f"\n{len(DECISION_TABLES)} bảng quyết định đã đăng ký · "
          f"{len(REJECTION_TABLES)} bảng từ chối (không phải quyết định chờ người)")
    return 0


def selftest() -> int:
    """Ba phép phá trên bảng quyết định TỔNG HỢP — không sửa tệp thật."""
    global DECISION_TABLES, REJECTION_TABLES, REG, FAILS, PASSES
    import tempfile

    real_dt, real_rt, real_reg = dict(DECISION_TABLES), dict(REJECTION_TABLES), REG
    cases: list[tuple[str, bool]] = []

    def run(mut: dict, rt: dict, reg: dict, label: str, must_red: bool) -> None:
        global DECISION_TABLES, REJECTION_TABLES, REG, FAILS, PASSES
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "reg.json"
            p.write_text(json.dumps(reg), encoding="utf-8")
            DECISION_TABLES, REJECTION_TABLES, REG = mut, rt, p
            FAILS, PASSES = [], 0
            violations()
            red = bool(FAILS)
        DECISION_TABLES, REJECTION_TABLES, REG = real_dt, real_rt, real_reg
        FAILS, PASSES = [], 0
        cases.append((label, red == must_red))

    reg = json.loads(real_reg.read_text(encoding="utf-8"))

    # P1: bỏ một tài liệu khỏi cả hai bảng ⇒ quyết định mồ côi ⇒ ĐỎ.
    mut = dict(real_dt)
    mut.pop("docs/41-testing-is-the-product.md")
    run(mut, real_rt, reg, "P1 quyết định mồ côi (không khai bảng) → đỏ", True)

    # P2: trỏ tới việc không tồn tại ⇒ ĐỎ.
    mut = dict(real_dt)
    mut["docs/41-testing-is-the-product.md"] = "P999"
    run(mut, real_rt, reg, "P2 trỏ tới P-id không có thật → đỏ", True)

    # P3: việc không có hạn ⇒ ĐỎ.
    broken = json.loads(real_reg.read_text(encoding="utf-8"))
    for a in broken["actions"]:
        if a["id"] == "P8":
            a.pop("due", None)
    run(dict(real_dt), real_rt, broken, "P3 quyết định không có hạn → đỏ", True)

    # P0: đối chứng.
    run(dict(real_dt), real_rt, reg, "P0 đối chứng: bảng gốc → xanh", False)

    ok = sum(1 for _, o in cases if o)
    for label, o in cases:
        print(f"  {'✓' if o else '✗'} {label}")
    if ok != len(cases):
        print(f"DECISIONS SELFTEST: FAIL — {ok}/{len(cases)}")
        return 1
    print(f"DECISIONS SELFTEST: PASS — {len(cases)}/{len(cases)} (1 đối chứng + 3 phép phá)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mỗi quyết định phải có người, hạn, và mã việc.")
    ap.add_argument("--audit", action="store_true", help="in bảng quyết định + hạn")
    ap.add_argument("--selftest", action="store_true", help="3 phép phá (CI)")
    args = ap.parse_args(argv)

    if args.audit:
        return audit()
    if args.selftest:
        return selftest()

    seen = violations()
    if FAILS:
        print(f"DECISIONS: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(
        f"DECISIONS: PASS — {PASSES} kiểm tra · 3 bất biến · {seen} dòng quyết định, "
        f"{len(DECISION_TABLES)} đã có người + hạn · {len(REJECTION_TABLES)} bảng từ chối khai tường minh"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
