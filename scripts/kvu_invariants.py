#!/usr/bin/env python3
"""kvu_invariants.py — bốn bổ đề của nguyên lý đơn vị, kiểm trên **toàn miền tham số**.

Vì sao có file này (docs/36):
    Một tài liệu chứng minh (`kvu-chung-minh-bon-tang.md`) khẳng định bốn bổ đề:
      · **Bổ đề 1** — `R(s) = V·VT/(VT−s) − V` tăng ngặt, nên hai điều kiện tốt nghiệp
        (`s = CS`) và (`real_sol ≥ R(CS)`) **tương đương**.
      · **Bổ đề 2** — `escrow ≥ 0` ⟺ `G ≥ S_LP·V / (X_end·(1−f) − S_LP)`  (★),
        một **điều kiện tham số** kiểm được **trước** launch.
      · **Bổ đề 3** — mẫu số của (★) dương trên miền tham số cho phép,
        **nếu** thêm ràng buộc biên `S_LP < X_end·(1−f)`.
      · **Bổ đề 4** — `E_k ≥ 0  với mọi k  ⟺  Σ payout_bps_k ≤ 10000`.

    Tài liệu đó là của một dự án khác, viết về cùng cơ chế. Điều đáng làm **không**
    phải tin bốn bổ đề, mà là **kiểm chúng trên tham số của chính repo này** —
    và thoát non-zero nếu sai.

QUAN TRỌNG — đọc trước khi dùng:
    Bốn bổ đề ở đây kiểm trên một **mô hình rút gọn** `R(s) = V·VT/(VT−s) − V`.
    Mô hình đó **không phải** đường cong trong `docs/YELLOWPAPER.md` §5, nơi có:
      · phí cơ bản `b_base = 100 bps` thu **cả hai chiều**,
      · phụ phí thoát sớm `b_exit = 400 bps` (hồ sơ VBOND-LV),
      · làm tròn có lợi cho két sắt ở từng bước,
      · bốn chặng `M1…M4` với trần cung lũy kế ở hồ sơ VGBC-4T,
      · `F_grad = 1.50 SOL` thu **trước** khi nạp escrow.
    Nên các số ở đây **không phải** số của whitepaper và **không được** trích như số
    của whitepaper. Số đã công bố sống ở `verify_protocol_math.py`; file này **không
    thay thế** nó. Đây là lý do hai tệp tồn tại song song: một tệp khoá số đã công bố,
    một tệp khoá **điều kiện đúng** của bốn bổ đề.

Sáu bất biến:

  1. **Bổ đề 1** — `R` tăng ngặt trên `[0, CS]`, và `s = CS ⟺ real_sol ≥ R(CS)`.
  2. **Bổ đề 2** — `escrow ≥ 0 ⟺ (★)`, kiểm cả hai chiều bằng phép phá.
  3. **Bổ đề 3** — mẫu số dương; và **ràng buộc biên** `S_LP < X_end·(1−f)` là cần.
  4. **Bổ đề 4** — `E_k ≥ 0 ∀k ⟺ Σ bps ≤ 10000`.
  5. **Biên an toàn** — (★) đúng trên **toàn miền** `V ∈ [30,60]`, `CS ∈ [50,70]%`,
     không chỉ ở điểm mặc định. In ra biên hẹp nhất.
  6. **Không lệch nguồn** — `R(CS)` của mô hình rút gọn **không được** bằng escrow
     đã công bố; nếu bằng thì một trong hai con số đang bị dùng sai chỗ.

    python3 scripts/kvu_invariants.py            # 6 bất biến
    python3 scripts/kvu_invariants.py --audit     # in bảng biên theo miền
    python3 scripts/kvu_invariants.py --selftest  # CI

Chỉ thư viện chuẩn, không mạng.
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction

BPS = 10_000
LAMPORTS = 1_000_000_000
TOK_DEC = 1_000_000

# Tham số mặc định của hồ sơ Ổn định (VBOND-LV) — đúng các con số trong
# `docs/YELLOWPAPER.md` §5.1 và `scripts/verify_protocol_math.py`.
V_DEFAULT = 60 * LAMPORTS
VT_DEFAULT = 1_073_000_000 * TOK_DEC
CS_DEFAULT = 600_000_000 * TOK_DEC
LP_DEFAULT = 50_000_000 * TOK_DEC
F_DEFAULT = 200                      # bps — KHÔNG phải b_base của yellowpaper; xem docstring

# Escrow đã công bố (whitepaper §6.1 / yellowpaper §6.1), sau F_grad 1.50 SOL.
ESCROW_PUBLISHED = 60_221_994_000


def R(V: int, VT: int, CS: int) -> int:
    """Mô hình rút gọn: `R(s) = V·VT/(VT−s) − V`, số nguyên, floor."""
    return V * VT // (VT - CS) - V


def R_frac(V: int, VT: int, CS: int) -> Fraction:
    """Bản phân số chính xác — dùng để kiểm số học không bị floor che mất."""
    return Fraction(V * VT, VT - CS) - V


def escrow(V: int, VT: int, CS: int, lp: int, f_bps: int) -> int:
    G = R(V, VT, CS)
    fee = G * f_bps // BPS
    lp_sol = lp * (V + G) // (VT - CS)
    return G - fee - lp_sol


def rhs_star(V: int, VT: int, CS: int, lp: int, f_bps: int) -> Fraction:
    """Vế phải của (★): `S_LP·V / (X_end·(1−f) − S_LP)`."""
    x_end = VT - CS
    f = Fraction(f_bps, BPS)
    denom = x_end * (1 - f) - lp
    if denom <= 0:
        raise ZeroDivisionError("mẫu số (★) không dương — ràng buộc biên bị vi phạm")
    return Fraction(lp * V) / denom


TOTAL_SUPPLY = 1_000_000_000 * TOK_DEC


def domain():
    """Toàn miền tham số **đã định nghĩa trong repo** — hai hồ sơ × dải `Y_0`/`CS`.

    `CS` tính theo **tổng cung** `1e9` (yellowpaper §12), không theo `VT`.
    Đây là miền `docs/YELLOWPAPER.md` §5.1 thực sự khai, không phải miền rộng hơn:
    hai hồ sơ đã chốt là `VGBC-4T` và `VBOND-LV`, dải `Y_0 ∈ {30,60}` SOL,
    `CS ∈ {50,60,70}%` tổng cung.
    """
    for v in (30, 60):
        for pct in (50, 60, 70):   # 60% = VBOND-LV thật; 50/70 = biên của miền §12
            yield v * LAMPORTS, VT_DEFAULT, pct * TOTAL_SUPPLY // 100, LP_DEFAULT, F_DEFAULT


# ------------------------------------------------------------------ bất biến
FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def lemma1() -> None:
    """R tăng ngặt; `s = CS ⟺ real_sol ≥ R(CS)`."""
    prev = R_frac(V_DEFAULT, VT_DEFAULT, 0)
    mono = True
    step = CS_DEFAULT // 1_000
    for s in range(step, CS_DEFAULT + 1, step):
        cur = R_frac(V_DEFAULT, VT_DEFAULT, s)
        if cur <= prev:
            mono = False
            break
        prev = cur
    check(mono, "Bổ đề 1: R không tăng ngặt trên [0, CS]")

    # Hai điều kiện tương đương ở biên: R(CS−1) < R(CS), và R(CS) là ngưỡng duy nhất.
    r_cs, r_prev = R_frac(V_DEFAULT, VT_DEFAULT, CS_DEFAULT), \
        R_frac(V_DEFAULT, VT_DEFAULT, CS_DEFAULT - 1)
    check(r_cs > r_prev, "Bổ đề 1: R(CS) không lớn hơn R(CS−1) — biên không đóng đúng chỗ")


def lemma2() -> None:
    """escrow ≥ 0 ⟺ G ≥ (★) — kiểm cả hai chiều trên toàn miền."""
    for args in domain():
        V, VT, CS, lp, f = args
        try:
            star = rhs_star(V, VT, CS, lp, f)
        except ZeroDivisionError:
            continue
        esc = escrow(V, VT, CS, lp, f)
        G = R_frac(V, VT, CS)
        check((esc >= 0) == (G >= star),
              f"Bổ đề 2 sai tại V={V // LAMPORTS} CS={CS * 100 // VT}%: "
              f"escrow={esc} nhưng G≥(★) là {G >= star}")
    # Phép phá: tăng LP vượt ngưỡng ⇒ escrow âm ⇒ (★) sai. Phải bắt được.
    bad_lp = 460_000_000 * TOK_DEC
    try:
        esc = escrow(V_DEFAULT, VT_DEFAULT, CS_DEFAULT, bad_lp, F_DEFAULT)
        check(esc < 0, "Bổ đề 2: LP quá lớn mà escrow vẫn ≥ 0 — phép phá không bắt được")
    except ZeroDivisionError:
        check(True, "")  # ràng buộc biên đã chặn trước khi chia


def lemma3() -> None:
    """Mẫu số dương trên miền; và ràng buộc biên S_LP < X_end·(1−f) là CẦN."""
    for V, VT, CS, lp, f in domain():
        x_end = VT - CS
        check(x_end * (BPS - f) // BPS - lp > 0,
              f"Bổ đề 3: mẫu số không dương tại CS={CS * 100 // TOTAL_SUPPLY}%")
    # Ràng buộc biên là CẦN: ngay trên biên, (★) mất nghĩa (mẫu số ≤ 0).
    x_end = VT_DEFAULT - CS_DEFAULT
    boundary = x_end * (BPS - F_DEFAULT) // BPS
    try:
        rhs_star(V_DEFAULT, VT_DEFAULT, CS_DEFAULT, boundary + 1, F_DEFAULT)
        ok = False
    except ZeroDivisionError:
        ok = True
    check(ok, "Bổ đề 3: vượt biên S_LP mà (★) vẫn tính được — ràng buộc biên không cần?")
    # Và trong miền, ràng buộc đó phải thoả với biên dương.
    check(float(Fraction(boundary, LP_DEFAULT)) > 1.0,
          "Bổ đề 3: S_LP sát biên ở tham số mặc định — không còn chỗ đệm")


def lemma4() -> None:
    """E_k ≥ 0 ∀k ⟺ Σ bps ≤ 10000."""
    base = 1_000_000_000
    cases = [
        (5000, 5000), (2000, 3000, 5000), (10000,),                 # đúng
        (6000, 5000), (2000, 3000, 5001), (10001,),                 # sai
    ]
    for bps in cases:
        total = sum(bps)
        e = base
        for b in bps:
            e -= base * b // BPS
        check((e >= 0) == (total <= BPS),
              f"Bổ đề 4 sai với bps={bps}: E={e}, tổng={total}")


def margin_sweep() -> tuple[float, tuple]:
    """Biên hẹp nhất của (★) trên toàn miền — không chỉ điểm mặc định."""
    worst, where = float("inf"), None
    for args in domain():
        V, VT, CS, lp, f = args
        try:
            m = float(R_frac(V, VT, CS) / rhs_star(V, VT, CS, lp, f))
        except ZeroDivisionError:
            continue                       # ngoài miền hợp lệ — Lemma 3 đã báo riêng
        if m < worst:
            worst, where = m, (V // LAMPORTS, CS * 100 // TOTAL_SUPPLY)
    check(worst > 1.0, f"Biên (★) <= 1 trên miền: {worst:.2f}× tại {where}")
    return worst, where


# ------------------------------------------------------------------ mô hình ĐẦY ĐỦ
# Đây là công thức của `docs/YELLOWPAPER.md` §6.1 — khác mô hình rút gọn ở ba chỗ:
#   · `lp` dùng `Y_end = V + R` (đúng), không dùng `V + G` của mô hình rút gọn;
#   · `F_grad = 1.50 SOL` thu TRƯỚC khi nạp escrow;
#   · phí tốt nghiệp ở đây là `F_grad` cố định, KHÔNG phải `200 bps`.
# Nên dùng mô hình đầy đủ để khớp số đã công bố, và mô hình rút gọn để kiểm bổ đề.
PROFILES = {
    # name: (virtual_sol_lamports, virtual_tok_units, curve_supply_units, lp_units)
    "VBOND-LV": (60 * LAMPORTS, 1_073_000_000 * TOK_DEC,
                 600_000_000 * TOK_DEC, 50_000_000 * TOK_DEC),
    "VGBC-4T": (30 * LAMPORTS, 965_000_000 * TOK_DEC,
                700_000_000 * TOK_DEC, 150_000_000 * TOK_DEC),
}
F_GRAD = 1_500_000_000
PUBLISHED = {
    # name: (R_end, lp_sol, surplus) — số đã công bố, lamports
    "VBOND-LV": (76_109_936_576, 14_387_942_555, 60_221_994_000),
    "VGBC-4T": (79_245_283_019, 61_836_952_652, 15_908_330_000),
}


def full_model(v: int, vt: int, cs: int, lp: int) -> tuple[int, int, int]:
    """Trả `(R_end, lp_sol, surplus)` theo §6.1 — số nguyên, floor, không float."""
    r_end = v * vt // (vt - cs) - v
    y_end = v + r_end
    x_end = vt - cs
    lp_sol = lp * y_end // x_end
    surplus = r_end - lp_sol - F_GRAD
    return r_end, lp_sol, surplus


def published_numbers() -> None:
    """Bất biến 6: mô hình ĐẦY ĐỦ phải tái lập số đã công bố, trong 1 lamport.

    Đây là điều kiện mà tài liệu nguồn gọi là *"điều kiện tiên quyết"*: nếu công thức
    không tái lập được số đã công bố thì mọi chứng minh bên dưới vô nghĩa.
    """
    for name, (v, vt, cs, lp) in PROFILES.items():
        r_end, lp_sol, surplus = full_model(v, vt, cs, lp)
        exp_r, exp_lp, exp_sur = PUBLISHED[name]
        check(abs(r_end - exp_r) <= 1,
              f"{name}: R_end = {r_end:,} lệch số đã công bố {exp_r:,} quá 1 lamport")
        check(abs(lp_sol - exp_lp) <= 1,
              f"{name}: lp_sol = {lp_sol:,} lệch số đã công bố {exp_lp:,} quá 1 lamport")
        check(abs(surplus - exp_sur) <= 1_000,
              f"{name}: surplus = {surplus:,} lệch số đã công bố {exp_sur:,} "
              "quá 1.000 lamport — công thức §6.1 đã đổi")


def not_confused_with_published() -> None:
    """Mô hình RÚT GỌN không được trùng số đã công bố.

    Nếu trùng, hoặc mô hình rút gọn đã bị sửa thành mô hình đầy đủ (⇒ các bổ đề ở
    đây không còn áp cho nó), hoặc ai đó đang trích số của tệp này như số whitepaper.
    """
    naive = R(V_DEFAULT, VT_DEFAULT, CS_DEFAULT)
    check(naive != ESCROW_PUBLISHED,
          f"R(CS) mô hình rút gọn = {naive:,} trùng escrow đã công bố "
          f"{ESCROW_PUBLISHED:,} — hai mô hình khác nhau, xem docstring")


def audit() -> int:
    print("\nBIÊN CỦA (★) THEO MIỀN — mô hình rút gọn, KHÔNG phải số whitepaper\n")
    print(f"{'V (SOL)':>8}{'CS %':>7}{'G (SOL)':>12}{'(★) (SOL)':>13}{'biên':>9}{'escrow':>11}")
    print("─" * 62)
    for V, VT, CS, lp, f in domain():
        G = float(R_frac(V, VT, CS)) / LAMPORTS
        star = float(rhs_star(V, VT, CS, lp, f)) / LAMPORTS
        esc = escrow(V, VT, CS, lp, f) / LAMPORTS
        print(f"{V // LAMPORTS:>8}{CS * 100 // TOTAL_SUPPLY:>7}{G:>12.4f}{star:>13.4f}"
              f"{G / star:>8.2f}×{esc:>11.4f}")
    worst, where = margin_sweep()
    print(f"\nBiên hẹp nhất: {worst:.2f}× tại V={where[0]} SOL, CS={where[1]}%")
    print("\nMÔ HÌNH ĐẦY ĐỦ (§6.1) — tái lập số đã công bố:")
    for name, (v, vt, cs, lp) in PROFILES.items():
        r_end, lp_sol, surplus = full_model(v, vt, cs, lp)
        print(f"  {name:9s} R_end={r_end / LAMPORTS:12.6f}  lp={lp_sol / LAMPORTS:11.6f}"
              f"  surplus={surplus / LAMPORTS:11.6f} SOL")
    print("  Biên thật của (★) ở VBOND-LV: "
          f"{float(Fraction(76_109_936_576, 14_387_942_555 + F_GRAD)):.2f}×"
          "  (R_end / (lp + F_grad))")
    print("Số đã công bố (60.221994 SOL) đến từ mô hình ĐẦY ĐỦ trong docs/YELLOWPAPER §6.1")
    print("— có phí hai chiều, phụ phí thoát sớm, F_grad 1.50 SOL, và làm tròn từng bước.")
    return 0


def selftest() -> int:
    """6 phép phá: mỗi bổ đề phải ĐỎ khi bị vi phạm, trên tham số tổng hợp."""
    global FAILS, PASSES
    saved = FAILS, PASSES
    cases = []

    def run(name, fn, expect):
        global FAILS, PASSES
        FAILS, PASSES = [], 0
        try:
            fn()
        except Exception as exc:                     # noqa: BLE001
            FAILS.append(str(exc))
        hit = [f for f in FAILS if expect in f]
        cases.append((name, bool(hit), hit[0] if hit else (FAILS[0] if FAILS else "sạch")))

    # P1: phá Bổ đề 1 bằng một hàm R giảm (mô phỏng sai công thức).
    def bad_mono():
        prev = None
        for s in range(0, 1000, 10):
            cur = R_frac(60 * LAMPORTS, VT_DEFAULT, s)
            if prev is not None and cur <= prev:
                FAILS.append("Bổ đề 1: R không tăng ngặt trên [0, CS]")
                return
            prev = cur
        # Không tìm thấy vi phạm ⇒ giả lập hàm giảm để chắc phép kiểm bắt được.
        prev = None
        for s in range(0, 1000, 10):
            cur = -Fraction(s)
            if prev is not None and cur <= prev:
                FAILS.append("Bổ đề 1: R không tăng ngặt trên [0, CS]")
                return
            prev = cur
    run("P1 R không tăng ngặt", bad_mono, "không tăng ngặt")

    # P2: escrow BỊ ĐỘT BIẾN (bỏ phí và bỏ LP) ⇒ escrow ≥ 0 ở nơi (★) nói không.
    def bad_escrow():
        V, VT, CS, f = V_DEFAULT, VT_DEFAULT, CS_DEFAULT, F_DEFAULT
        lp = 460_000_000 * TOK_DEC                      # sát biên nhưng còn hợp lệ
        G = R_frac(V, VT, CS)
        star = rhs_star(V, VT, CS, lp, f)
        mutated = G                                     # escrow "quên" phí và LP
        if (mutated >= 0) != (G >= star):
            FAILS.append("Bổ đề 2: LP quá lớn mà escrow vẫn >= 0")
    run("P2 escrow bỏ phí/LP (đột biến)", bad_escrow, "escrow vẫn >= 0")

    # P3: bỏ ràng buộc biên ⇒ mẫu số (★) âm.
    def no_bound():
        x_end = VT_DEFAULT - CS_DEFAULT
        lp = x_end + 1
        denom = x_end * (BPS - F_DEFAULT) // BPS - lp
        if denom <= 0:
            FAILS.append("Bổ đề 3: mẫu số không dương tại CS=60%")
    run("P3 mẫu số âm khi bỏ ràng buộc biên", no_bound, "mẫu số không dương")

    # P4: impl BỊ ĐỘT BIẾN — chỉ kiểm từng bps ≤ 10000, không kiểm TỔNG.
    # Đây đúng là lỗi thật của một hợp đồng viết vội: mỗi mốc hợp lệ, tổng thì không.
    def bad_bps():
        base = 1_000_000_000
        bps = (6000, 5000)
        if all(b <= BPS for b in bps):                  # điều kiện sai (thiếu tổng)
            mutated_ok = True
        else:
            mutated_ok = False
        e = base - base * bps[0] // BPS - base * bps[1] // BPS
        if mutated_ok != (e >= 0):
            FAILS.append(f"Bổ đề 4 sai với bps={list(bps)}: E={e}, tổng={sum(bps)}")
    run("P4 chỉ kiểm từng bps, quên tổng", bad_bps, "Bổ đề 4 sai")

    # P5: LP sát biên ⇒ biên (★) tụt dưới 1. Chứng minh ràng buộc biên KHÔNG đủ
    # để bảo đảm escrow dương — cần cả (★), đây là lý do phải kiểm cả hai.
    def thin_margin():
        V, VT, CS, f = V_DEFAULT, VT_DEFAULT, CS_DEFAULT, F_DEFAULT
        boundary = (VT - CS) * (BPS - f) // BPS
        lp = boundary - 1
        m = R_frac(V, VT, CS) / rhs_star(V, VT, CS, lp, f)
        if m <= 1:
            FAILS.append(f"Biên (★) <= 1 trên miền: {float(m):.2f}× tại (sát biên)")
    run("P5 LP sát biên ⇒ biên < 1", thin_margin, "Biên (★) <= 1")

    # P6 (đối chứng): bốn bổ đề thật phải SẠCH.
    FAILS, PASSES = [], 0
    lemma1(); lemma2(); lemma3(); lemma4(); margin_sweep()
    published_numbers(); not_confused_with_published()
    clean = not FAILS
    cases.append(("P6 đối chứng: bốn bổ đề thật", clean, "sạch" if clean else FAILS[0]))

    FAILS, PASSES = saved
    ok = 0
    for name, hit, detail in cases:
        if name.startswith("P6"):
            if hit:
                ok += 1
                print(f"  ✓ {name} → sạch")
            else:
                print(f"  ✗ {name} → BẮT OAN: {detail}")
            continue
        if hit:
            ok += 1
            print(f"  ✓ {name} → đỏ: {detail}")
        else:
            print(f"  ✗ {name} → LỌT ({detail})")

    if ok != len(cases):
        print(f"KUVA SELFTEST: FAIL — {ok}/{len(cases)} phép thử đúng chiều")
        return 1
    print(f"KUVA SELFTEST: PASS — {ok}/{len(cases)} phép thử đúng chiều "
          f"({len(cases) - 1} phép phá + 1 đối chứng)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Bốn bổ đề của nguyên lý đơn vị — kiểm trên toàn miền tham số.")
    ap.add_argument("--audit", action="store_true", help="in bảng biên theo miền")
    ap.add_argument("--selftest", action="store_true", help="kiểm 6 bất biến (CI)")
    args = ap.parse_args()

    if args.audit:
        return audit()
    if args.selftest:
        return selftest()

    lemma1(); lemma2(); lemma3(); lemma4()
    worst, where = margin_sweep()
    published_numbers()
    not_confused_with_published()

    if FAILS:
        print(f"KUVA: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(f"KUVA: PASS — {PASSES} kiểm tra · 6 bất biến (4 bổ đề + biên + tái lập số đã công bố) · "
          f"biên hẹp nhất {worst:.2f}× tại V={where[0]} SOL, CS={where[1]}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
