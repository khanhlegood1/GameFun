#!/usr/bin/env python3
"""Fail-fast verifier for docs/Game9K-Pitch-Deck.pdf.

"Người phản biện không cần tin — chỉ cần chạy một lệnh":

    python3 scripts/check_pitch_deck.py

Checks, in order:
  1. Page count and page box (14 slides, 960 x 540 pt 16:9).
  2. Every retired claim is gone (Q4 breakeven, $72.0M, 0.75M, test counts).
  3. Every load-bearing claim is present with the exact spec string.
  4. Arithmetic inside the deck closes to the lamport / to the dollar.
  5. Cross-check against the protocol verifier (optional: --with-verifier).

Exit code 0 = the deck may be shipped; 1 = some assertion failed (printed).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs" / "Game9K-Pitch-Deck.pdf"

# --------------------------------------------------------------- ground truth
# Spec SSOT: docs/YELLOWPAPER.md §6.1 (flat graduation fee), §264 (b_exit ladder).
R_END_B = 76.109937          # SOL raised, VBOND-LV
DEX_LP_B = 14.387943         # SOL locked into DEX LP (18.9%)
F_GRAD = 1.500000            # FLAT fee, F_grad = 1_500_000_000 lamports
ESCROW_B = 60.221994
MILESTONES = [5.0, 15.0, 20.0, 20.221994]

R_END_A = 79.245283
DEX_LP_A = 61.836953         # 78.0%
ESCROW_A = 15.908330

REV = [0.214, 1.126, 5.158, 18.46]           # $M, net revenue
OPEX = [0.760, 2.10, 5.80, 14.50]            # $M
EBITDA = [-0.546, -0.974, -0.642, 3.96]      # $M

# Round-trip loss ladder, locked by scripts/verify_protocol_math.py (Theorem 4).
RT_LADDER = {12.88: "<1h A", 6.94: "1-24h A", 3.97: "1-7d A", 5.95: "<7d B", 1.99: ">=7d"}

FORBIDDEN = [
    "Q4 Năm 1",            # retired breakeven claim
    "hòa vốn vận hành",     # retired framing
    "$72,0M", "$72.0M",     # retired Y4 revenue
    "$0,75M", "$0.75M",     # retired Y1 revenue
    "176/176", "83/83", "360/360",   # unverifiable test counts
    "60,199795 SOL chia",   # the 2% fee rule must never be used as the answer
]

REQUIRED = [
    "Mô hình Dual-Curve",
    "60,221994",
    "1,500000",
    "TÁCH CẦU / CUNG",
    "05/2025/NQ-CP",
    "hòa vốn Năm 4",
    "J-Curve",
    "$18,46M",
    "$0,214M",
    "Similarity Guard",
    "verify_protocol_math.py",
    "5,95",       # standard-config bound (-5.95%)
    "12,88",      # theoretical maximum-config bound (-12.88%)
]


class Report:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.passes: list[str] = []

    def check(self, ok: bool, label: str, detail: str = "") -> None:
        (self.passes if ok else self.fails).append(f"{label}{(' — ' + detail) if detail else ''}")


def money(x: float) -> str:
    return f"{x:,.2f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default=str(DECK))
    ap.add_argument("--with-verifier", action="store_true",
                    help="also run scripts/verify_protocol_math.py and require 100%% PASS")
    args = ap.parse_args()

    r = Report()
    pdf = Path(args.pdf)

    # ---------------------------------------------------------- 1. file + box
    r.check(pdf.exists(), "deck exists", str(pdf))
    if not pdf.exists():
        return _finish(r)

    try:
        from pypdf import PdfReader
    except ImportError:
        print("! pypdf is required: pip install pypdf", file=sys.stderr)
        return 1

    reader = PdfReader(str(pdf))
    pages = reader.pages
    r.check(len(pages) == 14, "14 slides", f"got {len(pages)}")
    w, h = float(pages[0].mediabox.width), float(pages[0].mediabox.height)
    r.check(abs(w - 960) < 1 and abs(h - 540) < 1, "960x540 pt (16:9)", f"got {w:g}x{h:g}")

    text = "\n".join(p.extract_text() or "" for p in pages)
    flat = re.sub(r"\s+", " ", text)

    # ------------------------------------------------------- 2. retired claims
    for bad in FORBIDDEN:
        r.check(bad not in flat, f"retired claim absent: {bad!r}")

    # ------------------------------------------------------- 3. required claims
    for good in REQUIRED:
        r.check(good in flat, f"claim present: {good!r}")

    # --------------------------------------------- 4. arithmetic must close
    esc_b = R_END_B - DEX_LP_B - F_GRAD
    r.check(abs(esc_b - ESCROW_B) < 5e-7, "VBOND-LV escrow closes",
            f"{money(R_END_B)} - {money(DEX_LP_B)} - {money(F_GRAD)} = {esc_b:.6f}")
    esc_a = R_END_A - DEX_LP_A - F_GRAD
    r.check(abs(esc_a - ESCROW_A) < 5e-7, "VGBC-4T escrow closes", f"{esc_a:.6f}")
    r.check(abs(sum(MILESTONES) - ESCROW_B) < 5e-7, "milestones sum to escrow",
            f"{sum(MILESTONES):.6f} vs {ESCROW_B:.6f}")
    # the rejected 2% rule, shown only as a foil: 2% * 76.109937 = 1.522199
    r.check(abs(0.02 * R_END_B - 1.522199) < 5e-7, "2% foil reproduced", "1,522199 SOL")
    foil_escrow = R_END_B - DEX_LP_B - 1.522199
    r.check(abs(foil_escrow - 60.199795) < 5e-7, "2% foil escrow reproduced",
            f"{foil_escrow:.6f} SOL (không dùng làm đáp án)")

    # DEX LP shares, matching the deck's 78.0% / 18.9%
    r.check(abs(DEX_LP_A / R_END_A * 100 - 78.0) < 0.05, "VGBC-4T DEX share 78.0%")
    r.check(abs(DEX_LP_B / R_END_B * 100 - 18.9) < 0.05, "VBOND-LV DEX share 18.9%")

    # revenue = sum of the four lines; EBITDA = revenue - OpEx
    lines = [[0.022, 0.059, 0.033, 0.100],
             [0.122, 0.244, 0.360, 0.400],
             [0.432, 0.726, 2.500, 1.500],
             [1.340, 1.920, 11.200, 4.000]]
    for i, row in enumerate(lines):
        r.check(abs(sum(row) - REV[i]) < 5e-3, f"revenue Y{i+1} = sum of 4 lines",
                f"{sum(row):.3f} vs {REV[i]:.3f} ($M)")
    for i in range(4):
        calc = REV[i] - OPEX[i]
        r.check(abs(calc - EBITDA[i]) < 5e-3, f"EBITDA Y{i+1} = rev - OpEx",
                f"{calc:+.3f} vs {EBITDA[i]:+.3f} ($M)")
    r.check(EBITDA[0] < 0 and EBITDA[1] < 0 and EBITDA[2] < 0 and EBITDA[3] > 0,
            "J-Curve shape: 3 loss years then positive", "breakeven lands in Y4")

    # round-trip ladder is the one locked by the verifier
    for bps in RT_LADDER:
        r.check(f"{bps:.2f}".replace(".", ",") in flat, f"round-trip {bps:.2f}% printed")

    # ------------------------------------------------------- 5. protocol maths
    if args.with_verifier:
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_protocol_math.py")],
                              capture_output=True, text=True)
        r.check(proc.returncode == 0 and "PASSED (100%)" in proc.stdout,
                "protocol verifier 100% PASS", proc.stdout.strip().splitlines()[-1]
                if proc.stdout.strip() else proc.stderr[-200:])

    return _finish(r)


def _finish(r: Report) -> int:
    for line in r.passes:
        print(f"  PASS  {line}")
    for line in r.fails:
        print(f"  FAIL  {line}")
    total = len(r.passes) + len(r.fails)
    pct = 100.0 * len(r.passes) / total if total else 0.0
    print(f"\nPITCH DECK CHECKS: {len(r.passes)}/{total} passed ({pct:.1f}%)")
    return 0 if not r.fails else 1


if __name__ == "__main__":
    sys.exit(main())
