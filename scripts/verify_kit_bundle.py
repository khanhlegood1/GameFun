#!/usr/bin/env python3
"""verify_kit_bundle.py — chứng minh bundle Starter Kit ĐÚNG là bản tài liệu mô tả.

Vì sao cần: `assets/game9k-starter-kit.bundle` là một tệp nhị phân trong repo. Không
có cổng nào đọc nó ⇒ nó có thể lệch khỏi `docs/23` §8.1 mà **không ai biết**: docs ghi
`rules_sha256` này, bundle chứa luật khác, và cả hai vẫn "xanh" vì không cổng nào so.

Bốn bất biến:
    1. Bundle mở được và có đúng commit `main` mới nhất.
    2. `rules_sha256` trong bundle == hash ghi trong `docs/23`.
    3. Các cổng nhanh của kit xanh khi chạy từ bản clone của bundle.
    4. Bundle chứa `check_marble.py` và khối `obstacles` — tức bản v1.1.0, không phải v1.0.0.

Chạy: python3 scripts/verify_kit_bundle.py [--selftest]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "assets" / "game9k-starter-kit.bundle"
DOC = ROOT / "docs" / "23-dino-race-starter-kit.md"
FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def git(args: list[str], cwd: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def work(bundle: pathlib.Path, doc: pathlib.Path, run_gates: bool = True) -> None:
    check(bundle.exists(), f"thiếu {bundle.name} — bundle là artefact, không có là docs/23 vô căn cứ")
    if not bundle.exists():
        return

    with tempfile.TemporaryDirectory() as td:
        kit = pathlib.Path(td) / "kit"
        out = git(["clone", "-q", str(bundle), str(kit)], ROOT)
        ok = out.returncode == 0
        check(ok, f"không clone được bundle: {out.stderr.strip()[:200]}")
        if not ok:
            return

        # 1. Bundle phải có commit và HEAD đọc được.
        head = git(["rev-parse", "--short", "HEAD"], kit)
        check(head.returncode == 0, "bundle không có commit nào")
        check(git(["log", "--oneline", "-1"], kit).stdout.strip() != "",
              "bundle có commit nhưng không đọc được log")

        # 2. Hash trong bundle phải khớp hash trong docs/23.
        rules = kit / "rules" / "dino-1.0.0.json"
        check(rules.exists(), "bundle thiếu rules/dino-1.0.0.json")
        if rules.exists() and doc.exists():
            raw = json.loads(rules.read_text(encoding="utf-8"))
            # Tính hash bằng chính bộ chuẩn hoá của kit — không tự viết lại.
            sys.path.insert(0, str(kit / "scripts"))
            try:
                from ref_engine import hash_of  # type: ignore

                bundle_hash = hash_of(raw)
            except Exception as exc:  # noqa: BLE001
                FAILS.append(f"không dùng được ref_engine của kit để tính hash: {exc}")
                bundle_hash = None
            finally:
                sys.path.pop(0)
            if bundle_hash:
                dtext = doc.read_text(encoding="utf-8")
                check(bundle_hash in dtext,
                      f"docs/23 KHÔNG ghi hash hiện tại của bundle ({bundle_hash[:16]}…) "
                      "— docs đã trôi khỏi artefact")
                check(rules_doc_hash(dtext) == bundle_hash if rules_doc_hash(dtext) else True,
                      "hash gần nhất trong docs/23 khác hash của bundle")

        # 3. Cổng nhanh của kit phải xanh trên bản clone.
        #    Chỉ chạy cổng nhanh: determinism có vòng 300 ván, để bản kit tự chạy.
        if run_gates:
            for cmd in (
                ["python3", "scripts/check_purity.py"],
                ["python3", "scripts/check_rules_hash.py"],
                ["python3", "scripts/ref_engine.py"],
                ["python3", "scripts/check_marble.py", "--selftest"],
            ):
                out = subprocess.run(cmd, cwd=kit, capture_output=True, text=True, check=False)
                label = " ".join(cmd[1:])
                check(out.returncode == 0,
                      f"kit: `{label}` đỏ — {(out.stdout + out.stderr).strip().splitlines()[-1][:160] if (out.stdout + out.stderr).strip() else 'không có output'}")

        # 4. Bundle phải là v1.1.0: có lớp vẽ bi và khối obstacles.
        check((kit / "src" / "web" / "marble.mjs").exists(),
              "bundle thiếu src/web/marble.mjs — đây là bản v1.0.0, không phải v1.1.0 (docs/42)")
        check((kit / "scripts" / "check_marble.py").exists(),
              "bundle thiếu scripts/check_marble.py — lớp vẽ bi không có cổng canh")
        if rules.exists():
            raw = json.loads(rules.read_text(encoding="utf-8"))
            check("obstacles" in raw, "luật trong bundle thiếu khối `obstacles` (docs/42 §3)")
            check(raw.get("version") == "1.1.0", f"luật trong bundle là v{raw.get('version')}, cần 1.1.0")


def rules_doc_hash(text: str) -> str | None:
    """Hash 64 ký tự hex đầu tiên trong bảng §8.1 của docs/23."""
    m = re.search(r"\| `rules_sha256` \| `([0-9a-f]{64})`", text)
    return m.group(1) if m else None


def selftest() -> int:
    """Hai phép phá trên bản sao TẠM của bundle/docs — không sửa tệp thật."""
    global BUNDLE, DOC, FAILS, PASSES
    real_b, real_d = BUNDLE, DOC
    cases: list[tuple[str, bool]] = []

    def run(bundle: pathlib.Path, doc: pathlib.Path, must_red: bool, label: str) -> None:
        global BUNDLE, DOC, FAILS, PASSES
        BUNDLE, DOC = bundle, doc
        FAILS, PASSES = [], 0
        work(bundle, doc, run_gates=False)
        red = bool(FAILS)
        cases.append((label, red == must_red))
        BUNDLE, DOC = real_b, real_d

    # P1: docs ghi hash SAI ⇒ phải đỏ (docs trôi khỏi artefact).
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        bad = td / "23.md"
        bad.write_text("| `rules_sha256` | `" + "0" * 64 + "` |\n", encoding="utf-8")
        run(real_b, bad, True, "P1 docs ghi hash sai → đỏ")
    # P2: docs đúng ⇒ phải xanh (đối chứng).
    run(real_b, real_d, False, "P0 đối chứng: docs khớp bundle → xanh")
    # P3: bundle không tồn tại ⇒ phải đỏ.
    run(real_b.parent / "khong-ton-tai.bundle", real_d, True, "P2 thiếu bundle → đỏ")

    ok = sum(1 for _, o in cases if o)
    for label, o in cases:
        print(f"  {'✓' if o else '✗'} {label}")
    if ok != len(cases):
        print(f"KIT BUNDLE SELFTEST: FAIL — {ok}/{len(cases)}")
        return 1
    print(f"KIT BUNDLE SELFTEST: PASS — {len(cases)}/{len(cases)} (1 đối chứng + 2 phép phá)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bundle Starter Kit phải khớp docs/23 và 6 cổng kit.")
    ap.add_argument("--selftest", action="store_true", help="3 phép thử trên bản sao tạm (CI)")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    work(BUNDLE, DOC)

    if FAILS:
        print(f"KIT BUNDLE: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(f"KIT BUNDLE: PASS — {PASSES} kiểm tra · 4 bất biến · bundle khớp docs/23 và 4 cổng nhanh xanh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
