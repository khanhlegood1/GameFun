#!/usr/bin/env python3
"""check_gate_wiring.py — mỗi cổng phải có HAI đường: tự kiểm VÀ kiểm repo.

Vì sao có file này (docs/40):
    docs/37 §2 nói "một việc có hạn nằm trong văn xuôi là một việc không có hạn".
    Cùng lỗi đó, ở tầng cổng: một cổng mà CI chỉ gọi `--selftest` là một cổng chỉ
    tự kiểm **chính nó**, không bao giờ kiểm repo. Bản này tìm ra **3** cổng như vậy
    (check_claims, receipt_lock, kvu_invariants — cả ba `return` ngay sau selftest),
    và một trong ba đang **ĐỎ trên `main`** trong khi CI vẫn xanh mỗi tuần.

Bốn bất biến:
    1. Cổng nhận `--selftest` mà không đọc cờ ⇒ phải khai lý do trong `EMPTY_FLAG_OK`.
    2. Cổng có chế độ nội dung ⇒ workflow phải gọi **cả** chế độ nội dung.
    3. Mọi cổng được CI gọi ⇒ phải có mặt trong sổ `CONTENT_MODE` (không lọt sổ).
    4. Mọi tệp sổ nhắc ⇒ phải tồn tại (sổ không được trôi).

Chạy: python3 scripts/check_gate_wiring.py [--audit|--selftest]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "docs.yml"
FAILS: list[str] = []
PASSES = 0

SELFTEST_FLAGS = {"--selftest", "--self-test"}

# Sổ đăng ký: cổng → cờ của chế độ tự kiểm (None = cổng không có chế độ tự kiểm
# riêng; chế độ mặc định của nó ĐÃ LÀ phép kiểm thật trên repo).
# Mỗi dòng là một quyết định đã kiểm bằng tay ở docs/40 §3 — không phải suy đoán.
CONTENT_MODE = {
    "check_docs_links.py": None,
    "verify_protocol_math.py": None,
    "verify_pop_decay.py": None,
    "check_agent_rules.py": None,
    "check_pitch_deck.py": None,
    "check_sdk_drift.py": None,
    "gate_decide.py": "--self-test",
    "check_specs.py": "--self-test",
    "check_gate_ladder.py": "--selftest",
    "check_egress_lock.py": "--selftest",
    "check_sdk.py": "--selftest",
    "check_sdk_errors.py": "--selftest",
    "check_sdk_manifest.py": "--selftest",
    "check_claims.py": "--selftest",
    "receipt_lock.py": "--selftest",
    "kvu_invariants.py": "--selftest",
    "check_actions.py": "--selftest",
    "find_contradictions.py": "--selftest",
    "check_invariants_coverage.py": "--selftest",
    "verify_invariants.py": "--selftest",
    "check_gate_wiring.py": "--selftest",
    "verify_kit_bundle.py": "--selftest",
}

# Cổng được PHÉP nhận cờ `--selftest` mà không đọc cờ, vì chế độ mặc định của nó đã
# là phép kiểm thật trên repo và không có "corpus tổng hợp" nào để phá. Ghi lý do
# TÊN TỪNG CỔNG — miễn trừ ngầm là cách một cổng chết (docs/33 §2).
EMPTY_FLAG_OK = {
    "check_gate_ladder.py": "mặc định kiểm thang thật; phép phá đòi 6 cổng tổng hợp",
    "check_egress_lock.py": "mặc định kiểm toàn repo; phép phá đã thử tay ở docs/27 §6",
    "check_sdk.py": "mặc định đo ngân sách thật; phép phá đòi SDK tổng hợp",
    "check_sdk_errors.py": "mặc định đối chiếu SDK ↔ docs/03",
    "check_sdk_manifest.py": "mặc định đối chiếu 4 chỗ ghi hash trong docs/",
}


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def run_lines(text: str) -> list[str]:
    """Mọi lệnh `scripts/…` trong workflow: dòng `run:` một dòng (tách `&&`) và khối `run: |`."""
    out: list[str] = []
    for m in re.finditer(r"(?m)^\s{8}run:[ \t]*(?!\|)(.+)$", text):
        out.extend(p.strip() for p in m.group(1).split("&&"))
    for block in re.findall(r"(?ms)^\s{8}run:[ \t]*\|\n(.*?)(?=^\s{6}- |\Z)", text):
        out.extend(re.findall(r"(?m)^\s*python3\s+scripts/\S+.*$", block))
    return [re.sub(r"\s+", " ", s).strip() for s in out if "scripts/" in s]


def gate_scripts() -> list[str]:
    return [p.name for p in sorted((ROOT / "scripts").glob("*.py")) if not p.name.startswith("build_")]


def calls_by_script(cmds: list[str]) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for c in cmds:
        m = re.search(r"scripts/([\w.-]+\.py)", c)
        if m:
            seen.setdefault(m.group(1), []).append(c)
    return seen


def calls_selftest(cmd: str) -> bool:
    return any(f in cmd for f in SELFTEST_FLAGS)


def audit() -> int:
    seen = calls_by_script(run_lines(workflow_text()))
    print("\nCỔNG ĐÃ NỐI VÀO CI — chế độ nào THỰC SỰ chạy\n")
    print(f"{'Tệp':34}{'tự kiểm?':12}{'kiểm repo?':13}lần gọi")
    print("─" * 80)
    missing = 0
    for s in gate_scripts():
        calls = seen.get(s)
        if not calls:
            missing += 1
            print(f"{s:34}{'—':12}{'—':13}0   ← không nối vào CI")
            continue
        st = any(calls_selftest(c) for c in calls)
        # Kiểm repo chạy ⇔ có một lần gọi KHÔNG kèm cờ tự kiểm.
        ct = any(not calls_selftest(c) for c in calls)
        print(f"{s:34}{'CÓ' if st else '—':12}{'CÓ' if ct else 'KHÔNG':13}{len(calls)}")
    print(f"\n{len(seen)} tệp scripts/ được gọi · {missing} tệp không nối")
    return 0


def violations() -> None:
    global PASSES
    seen = calls_by_script(run_lines(workflow_text()))

    # 1. Cờ tự kiểm phải thực sự chạy phép phá, hoặc có lý do ghi TÊN.
    for s in gate_scripts():
        src = (ROOT / "scripts" / s).read_text(encoding="utf-8")
        if not any(f'"{f}"' in src for f in SELFTEST_FLAGS):
            continue
        reads_flag = bool(re.search(r"args\.sel(?:f)?test|args\.self_test", src))
        if reads_flag or s in EMPTY_FLAG_OK:
            PASSES += 1
        else:
            FAILS.append(
                f"{s}: nhận `--selftest` nhưng KHÔNG đọc cờ — CI chạy cờ rỗng rồi "
                "tưởng đã có phép phá (docs/40 §3). Nối cờ, hoặc khai vào EMPTY_FLAG_OK"
            )

    # 2. Cổng có chế độ nội dung ⇒ workflow phải gọi cả chế độ nội dung.
    for s, self_flag in CONTENT_MODE.items():
        calls = seen.get(s)
        if not calls:
            FAILS.append(f"{s}: có trong sổ nhưng KHÔNG được workflow gọi — cổng chết")
            continue
        if self_flag and all(calls_selftest(c) for c in calls):
            FAILS.append(
                f"{s}: CI chỉ gọi `{calls[0]}` — chế độ tự kiểm rồi THOÁT, phần kiểm "
                f"repo không bao giờ chạy. Thêm `&& python3 scripts/{s}` (docs/40 §2)"
            )
        else:
            PASSES += 1

    # 3. Mọi cổng được CI gọi phải có mặt trong sổ.
    for s in seen:
        if s not in CONTENT_MODE:
            FAILS.append(f"{s}: được CI gọi nhưng không có trong CONTENT_MODE — thêm quyết định vào sổ")

    # 4. Sổ không được trôi khỏi đĩa.
    for s in CONTENT_MODE:
        if not (ROOT / "scripts" / s).exists():
            FAILS.append(f"sổ nhắc `{s}` nhưng tệp không tồn tại — sổ đã trôi")


def selftest() -> int:
    """Bốn phép phá trên workflow TỔNG HỢP — không sửa tệp thật, không đụng repo."""
    global WORKFLOW, FAILS, PASSES
    import tempfile

    real = WORKFLOW
    saved = (list(FAILS), PASSES)
    cases: list[tuple[str, bool, list[str]]] = []

    def run_on(body: str, label: str, must_red: bool) -> None:
        global WORKFLOW, FAILS, PASSES
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "docs.yml"
            p.write_text(body, encoding="utf-8")
            WORKFLOW = p
            FAILS, PASSES = [], 0
            violations()
            red, first = bool(FAILS), FAILS[:1]
        cases.append((label, red == must_red, first))

    REG_ONE = "      - name: x\n        run: python3 scripts/check_docs_links.py\n"
    all_ok = "".join(
        "      - name: x\n        run: python3 scripts/%s\n" % s for s in CONTENT_MODE
    )
    # Dựng workflow TỔNG HỢP gọi đủ mọi cổng ở chế độ nội dung (không cờ) ⇒ phải XANH.
    run_on(all_ok, "P0 đối chứng: gọi đủ cổng, không cờ → xanh", False)
    # Bỏ một cổng khỏi workflow ⇒ phải ĐỎ (bắt đúng cổng bị bỏ).
    run_on(
        all_ok.replace("python3 scripts/kvu_invariants.py\n", "\n"),
        "P1 bỏ một cổng khỏi CI → đỏ",
        True,
    )
    # Cổng có chế độ nội dung mà chỉ gọi --selftest ⇒ phải ĐỎ.
    run_on(
        all_ok.replace(
            "python3 scripts/receipt_lock.py\n",
            "python3 scripts/receipt_lock.py --selftest\n",
        ),
        "P2 cổng chỉ gọi --selftest (thoát sớm) → đỏ",
        True,
    )
    # Gọi một cổng lạ không có trong sổ ⇒ phải ĐỎ.
    run_on(all_ok + "      - name: y\n        run: python3 scripts/khong_co_that.py\n",
           "P3 cổng lạ ngoài sổ → đỏ", True)

    ok = sum(1 for _, o, _ in cases if o)
    for label, o, detail in cases:
        print(f"  {'✓' if o else '✗'} {label}" + ("" if o else f" → {detail}"))

    WORKFLOW = real
    FAILS, PASSES = saved
    if ok != len(cases):
        print(f"GATE WIRING SELFTEST: FAIL — {ok}/{len(cases)}")
        return 1
    print(
        f"GATE WIRING SELFTEST: PASS — {len(cases)}/{len(cases)} "
        "(1 đối chứng + 3 phép phá)"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Mỗi cổng phải được CI gọi cả chế độ kiểm repo.")
    ap.add_argument("--audit", action="store_true", help="in bảng cổng đã nối + chế độ")
    ap.add_argument("--selftest", action="store_true", help="phép phá trên workflow tổng hợp")
    args = ap.parse_args()

    if args.audit:
        return audit()
    if args.selftest:
        return selftest()

    violations()

    if FAILS:
        print(f"GATE WIRING: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(
        f"GATE WIRING: PASS — {PASSES} kiểm tra · {len(CONTENT_MODE)} cổng trong sổ · "
        "mỗi cổng có cả đường tự kiểm và đường kiểm repo"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
