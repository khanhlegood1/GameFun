#!/usr/bin/env python3
"""verify_invariants.py — bốn bất biến **chưa từng có mã** (docs/39).

Vì sao có file này:
    `docs/38` §2 lập bảng 12 bất biến của `YELLOWPAPER.md` §8.1 và phát hiện
    **tám** cái có phép kiểm, **bốn** cái chỉ có tên: `INV-05`, `INV-07`,
    `INV-11`, `INV-12`. Bốn cái đó không thiếu người viết — chúng thiếu
    **đối tượng dữ liệu**: mô hình `verify_protocol_math.py` chỉ có đường cong
    (SOL ↔ token), nên không có sổ phiên bản, không có ledger custody, không có
    oracle `BotShare`, không có trạng thái governance.

    Vòng này dựng bốn đối tượng đó **ở mức mô hình**, đủ để assert đúng câu
    đặc tả trong §8.1 — không phải để giả vờ rằng `programs/` đã tồn tại.

Ranh giới phải nói rõ (docs/39 §1):
    Đây là **mô hình quyết định**, không phải chương trình on-chain. Cái được
    chứng minh là *"hàm quyết định từ chối đúng chỗ và chấp nhận đúng chỗ"* —
    không phải *"chương trình Anchor cư xử đúng"*. `programs/` vẫn trống, và
    `docs/37` §2.4 vẫn là bất biến đang canh điều đó.

Bốn bất biến:

  1. **`INV-05` Phả hệ Phiên bản Đơn điệu** — `ν_k >_lex ν_{k-1}`, `h_base,k = h_{k-1}`,
     `h_k ≠ h_{k-1}`, `δ_k ≥ θ_diff = 0.08`. Sai ⇒ từ chối với đúng mã lỗi.
  2. **`INV-07` Cô lập Lưu ký Tiền Tốt nghiệp** — trước `Graduated`, không token nào
     nằm trong ví cá nhân; token chỉ rời PDA vault sau `Graduated`.
  3. **`INV-11` Giới hạn Gian lận Hệ thống** — `BotShare > 0.08 ⇒ allow_new_launch = false`,
     và chỉ mở lại **sau hai chu kỳ liên tiếp** sạch (§3.2 — *Stop-the-Line R2*).
  4. **`INV-12` Tính Bất biến Điều khoản & Quản trị** — `terms_hash` không đổi suốt
     vòng đời; `upgrade_authority = None` với mọi `t ≥ t₀ + 7,776,000 s`.

Ba chế độ:

    python3 scripts/verify_invariants.py            # 4 bất biến
    python3 scripts/verify_invariants.py --audit     # in từng bước quyết định
    python3 scripts/verify_invariants.py --selftest  # CI

Chỉ thư viện chuẩn, không mạng.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_protocol_math import (          # noqa: E402
    PROFILE_VBOND_LV,
    CurveState,
    LAMPORTS_PER_SOL,
)

THETA_DIFF = Fraction(8, 100)      # YP §2.2 — ngưỡng BuildDiff 8%
T_IMM = 7_776_000                  # YP §7.2 — 90 ngày tới bất biến
TIMELOCK = 172_800                 # YP §7.2 — 48h
BETA_MAX = Fraction(8, 100)        # YP §3.2 — cầu dao BotShare 8%

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def expect_red(fn) -> list[str]:
    """Chạy một **phép phá** và trả về các vi phạm nó sinh ra, KHÔNG làm bẩn `FAILS`.

    Vì sao cần: phép phá ở đây là "cố tình làm sai rồi xem bất biến có đỏ không".
    Nếu nó ghi thẳng vào `FAILS` thì lần chạy đầy đủ sẽ báo đỏ **vì chính phép
    phá của mình** — và người đọc sẽ tưởng bất biến bị vi phạm. Đây đúng là lỗi
    tôi gặp ở lần chạy đầu của tệp này (4 vi phạm, cả 4 là phép phá).
    """
    global PASSES
    saved_fails, saved_passes = list(FAILS), PASSES
    FAILS.clear()
    globals()["PASSES"] = 0
    try:
        fn()
        produced = list(FAILS)
    finally:
        FAILS[:] = saved_fails
        globals()["PASSES"] = saved_passes
    return produced


# ==================================================================== INV-05
ZERO32 = "00" * 32


@dataclass
class Version:
    k: int
    nu: tuple[int, int, int]
    h: str
    h_base: str
    delta: Fraction


@dataclass
class VersionChain:
    """Sổ phiên bản — đủ để chạy `record_version_milestone` ở mức quyết định."""

    versions: list[Version] = field(default_factory=list)

    def record(self, nu: tuple[int, int, int], h: str, h_base: str,
               delta: Fraction) -> tuple[bool, str | None]:
        """Trả `(True, None)` nếu ghi được, ngược lại `(False, mã_lỗi)`.

        Thứ tự kiểm khớp thứ tự trong YP §2.2: phả hệ → định danh → thay đổi thực chất.
        """
        k = len(self.versions) + 1
        if k == 1:
            # YP §2.2 — Lớp 2: "Với k = 1, yêu cầu h_base,1 = 0^32"
            if h_base != ZERO32:
                return False, "ERR_ORPHAN_BASE"
        else:
            prev = self.versions[-1]
            # Lớp 1 — thứ tự từ điển nghiêm ngặt
            if nu == prev.nu:
                return False, "ERR_VERSION_SAME"
            if not (nu > prev.nu):
                return False, "ERR_VERSION_OLDER"
            # Lớp 2 — Ancestry Guard
            if h_base != prev.h:
                return False, "ERR_ORPHAN_BASE"
            if h == prev.h:
                return False, "ERR_IDENTICAL_BUILD"
        # Lớp 2 — HOTFIX không bao giờ được gọi record_version_milestone
        if delta < THETA_DIFF:
            return False, "ERR_HOTFIX_NOT_MILESTONE"
        self.versions.append(Version(k=k, nu=nu, h=h, h_base=h_base, delta=delta))
        return True, None

    def check_invariant(self) -> None:
        """`INV-05` đọc trên chính sổ — không tin kết quả của `record`."""
        for i, v in enumerate(self.versions):
            check(v.k == i + 1, f"INV-05: k không liên tục tại vị trí {i}: {v.k}")
            if i == 0:
                check(v.h_base == ZERO32, "INV-05: v_1 có h_base khác 0^32")
            else:
                prev = self.versions[i - 1]
                check(v.nu > prev.nu, f"INV-05: ν_{v.k} không lớn hơn từ điển ν_{v.k-1}")
                check(v.h_base == prev.h, f"INV-05: h_base,{v.k} != h_{v.k-1}")
                check(v.h != prev.h, f"INV-05: h_{v.k} == h_{v.k-1}")
            check(v.delta >= THETA_DIFF,
                  f"INV-05: δ_{v.k} = {float(v.delta):.3f} < θ_diff — HOTFIX không được vào sổ")


def inv05() -> None:
    def h(tag: str) -> str:
        return (tag.encode().hex() * 32)[:64]

    chain = VersionChain()
    # Chuỗi hợp lệ: 4 phiên bản, ν tăng dần, phả hệ nối đúng.
    ok, err = chain.record((0, 1, 0), h("a"), ZERO32, Fraction(30, 100))
    check(ok and err is None, f"INV-05: v_1 hợp lệ bị từ chối ({err})")
    prev = chain.versions[-1]
    for i, nu in enumerate([(1, 0, 0), (1, 1, 0), (2, 0, 0)], start=2):
        ok, err = chain.record(nu, h(f"v{i}"), prev.h, Fraction(20 + i, 100))
        check(ok, f"INV-05: v_{i} hợp lệ bị từ chối ({err})")
        prev = chain.versions[-1]
    chain.check_invariant()

    # Bốn phép phá: mỗi phép phải bị TỪ CHỐI với đúng mã lỗi.
    cases = [
        ("ν bằng ν trước", (2, 0, 0), h("x"), prev.h, Fraction(50, 100), "ERR_VERSION_SAME"),
        ("ν nhỏ hơn", (1, 0, 0), h("y"), prev.h, Fraction(50, 100), "ERR_VERSION_OLDER"),
        ("h_base sai cha", (3, 0, 0), h("z"), h("khong-phai-cha"), Fraction(50, 100),
         "ERR_ORPHAN_BASE"),
        ("h trùng cha", (3, 0, 0), prev.h, prev.h, Fraction(50, 100), "ERR_IDENTICAL_BUILD"),
        ("δ dưới ngưỡng (đổi màu 1 nút)", (3, 0, 0), h("w"), prev.h, Fraction(7, 100),
         "ERR_HOTFIX_NOT_MILESTONE"),
    ]
    for name, nu, hh, hb, dl, want in cases:
        ok, err = chain.record(nu, hh, hb, dl)
        check((not ok) and err == want,
              f"INV-05: phép phá «{name}» không bị từ chối bằng {want} (nhận {ok}, {err})")
    # Sổ không được thay đổi sau các phép phá.
    check(len(chain.versions) == 4, f"INV-05: sổ bị ghi bẩn ({len(chain.versions)} bản ghi)")
    # k=1 với h_base != 0^32 bị từ chối.
    ok, err = VersionChain().record((0, 1, 0), h("a"), h("b"), Fraction(50, 100))
    check(not ok and err == "ERR_ORPHAN_BASE", "INV-05: v_1 có h_base khác 0^32 mà vẫn nhận")


# ==================================================================== INV-07
class CustodyViolation(Exception):
    """Token rời PDA vault khi chưa `Graduated` — đúng thứ `INV-07` cấm."""


class CustodyLedger:
    """Sổ lưu ký: token đã bán nằm trong `BuyerPosition` PDA, KHÔNG nằm trong ví.

    Mô hình `CurveState` chỉ biết `positions[u].tokens` — nó không phân biệt
    "token trong PDA" và "token trong ví". `INV-07` nói về đúng khác biệt đó,
    nên nó cần một ledger riêng (docs/39 §2).
    """

    def __init__(self, state: CurveState) -> None:
        self.state = state
        self.wallets: dict[str, int] = {}

    def buy(self, user: str, lamports: int, now_ts: int = 0) -> int:
        tokens, _ = self.state.buy(user, lamports, now_ts=now_ts, enforce_caps=False)
        return tokens

    def withdraw(self, user: str, units: int) -> int:
        """Rút token từ PDA ra ví. Chỉ sau `Graduated` — nếu không, `INV-07` bị vi phạm."""
        if self.state.status != "Graduated":
            raise CustodyViolation(
                f"INV-07: rút {units} token khi status = {self.state.status}"
            )
        held = self.state.positions[user].tokens
        if units > held:
            raise CustodyViolation(f"rút {units} > nắm giữ {held}")
        self.state.positions[user].tokens -= units
        self.wallets[user] = self.wallets.get(user, 0) + units
        return units

    def check_invariant(self) -> None:
        """`INV-07`: trước Graduated, tổng token trong ví cá nhân == 0."""
        in_wallets = sum(self.wallets.values())
        if self.state.status != "Graduated":
            check(in_wallets == 0,
                  f"INV-07: {in_wallets} token nằm trong ví cá nhân khi status = "
                  f"{self.state.status}")
        # Bảo toàn: token trong PDA + trong ví == token đã bán
        in_pda = sum(p.tokens for p in self.state.positions.values())
        check(in_pda + in_wallets == self.state.net_sold,
              f"INV-07: bảo toàn custody sai: PDA {in_pda} + ví {in_wallets} "
              f"!= net_sold {self.state.net_sold}")


def inv07() -> None:
    ledger = CustodyLedger(CurveState(PROFILE_VBOND_LV))
    ledger.buy("alice", 3 * LAMPORTS_PER_SOL)
    ledger.buy("bob", 5 * LAMPORTS_PER_SOL)
    ledger.check_invariant()
    check(sum(ledger.wallets.values()) == 0, "INV-07: ví có token ngay sau khi mua")

    # Phép phá 1: rút trước Graduation phải bị chặn.
    try:
        ledger.withdraw("alice", 1)
        check(False, "INV-07: rút token khi chưa Graduated mà KHÔNG bị chặn")
    except CustodyViolation:
        check(True, "")

    # Phép phá 2: ghi thẳng vào ví (bỏ qua API) — bất biến phải đỏ.
    ledger.wallets["mallory"] = 1_000
    produced = expect_red(ledger.check_invariant)
    ledger.wallets.pop("mallory")
    check(any("INV-07" in m for m in produced),
          "INV-07: token lọt vào ví cá nhân mà bất biến KHÔNG đỏ")

    # Đường hợp lệ: tốt nghiệp rồi mới rút được.
    state = ledger.state
    state.buy("carol", 200 * LAMPORTS_PER_SOL, now_ts=700_000, enforce_caps=False)
    while state.active_milestone < len(state.profile.tranche_caps):
        state.unlock_next_milestone()
    state.buy("carol", 200 * LAMPORTS_PER_SOL, now_ts=800_000, enforce_caps=False)
    if state.net_sold < state.profile.curve_supply:
        state.buy("carol", 400 * LAMPORTS_PER_SOL, now_ts=900_000, enforce_caps=False)
    check(state.status == "Active", "INV-07: trạng thái lệch trước khi tốt nghiệp")
    state.graduate()
    got = ledger.withdraw("alice", 1)
    check(got == 1 and ledger.wallets["alice"] == 1,
          "INV-07: rút sau Graduated không thực hiện được")
    ledger.check_invariant()


# ==================================================================== INV-11
@dataclass
class Session:
    d_act: int          # thời lượng hoạt động (giây) — trọng số
    p_bot: Fraction     # điểm mô hình
    audited: bool = False
    y: int = 0          # nhãn người thật: 0 = người, 1 = bot
    pi: Fraction = Fraction(1, 200)   # π_audit = 0.5%


def botshare(sessions: list[Session]) -> Fraction:
    """Ước lượng difference/HT của YP §3.2 — phân số chính xác, không float."""
    total_d = sum(s.d_act for s in sessions)
    if total_d == 0:
        raise ValueError("BotShare: mẫu rỗng")
    acc = sum(s.d_act * s.p_bot for s in sessions)
    for s in sessions:
        if s.audited:
            acc += Fraction(s.d_act, 1) / s.pi * (s.y - s.p_bot)
    return acc / total_d


@dataclass
class LaunchBreaker:
    """`Stop-the-Line R2`: ngắt ngay, mở lại chỉ sau HAI chu kỳ liên tiếp sạch."""

    history: list[Fraction] = field(default_factory=list)
    allowed: bool = True
    _clean_streak: int = 0

    def observe(self, estimate: Fraction) -> bool:
        self.history.append(estimate)
        if estimate > BETA_MAX:
            self.allowed = False
            self._clean_streak = 0
        else:
            self._clean_streak += 1
            if self._clean_streak >= 2:
                self.allowed = True
        return self.allowed

    def check_invariant(self) -> None:
        """`INV-11` đọc trên lịch sử — không tin cờ `allowed` do chính nó đặt."""
        for i, est in enumerate(self.history):
            if est > BETA_MAX:
                # Sau một chu kỳ bẩn, cổng phải đóng cho tới khi có 2 chu kỳ sạch liền.
                streak = 0
                for later in self.history[i + 1:]:
                    if later > BETA_MAX:
                        streak = 0
                    else:
                        streak += 1
                        if streak >= 2:
                            break
                else:
                    check(not self.allowed,
                          f"INV-11: chu kỳ {i+1} có BotShare "
                          f"{float(est)*100:.2f}% > 8% nhưng vẫn cho launch mới")


def inv11() -> None:
    # 1. Công thức: kiểm bằng một ví dụ tính tay được.
    sessions = [
        Session(600, Fraction(1, 10), audited=True, y=1),     # audit nói là bot
        Session(900, Fraction(1, 10), audited=True, y=0),     # audit nói là người
        Session(1_500, Fraction(1, 10)),
    ]
    est = botshare(sessions)
    # Σ d·p = 300·0.1 = 30 ; audit: 600/π·(1−0.1) + 900/π·(0−0.1), π = 1/200
    #        = 120000·0.9 − 180000·0.1 = 108000 − 18000 = 90000
    # => (30 + 90000) / 3000 = 30.01
    check(abs(est - Fraction(30_030, 1_000)) < 1,
          f"INV-11: ước lượng sai ({est} — kỳ vọng ≈ 30,03)")
    # Mẫu không audit: ước lượng = trung bình có trọng số của p_bot.
    plain = [Session(1_000, Fraction(2, 10)), Session(3_000, Fraction(6, 100))]
    check(botshare(plain) == Fraction(200 + 180, 4_000),
          f"INV-11: mẫu không audit tính sai ({botshare(plain)})")

    # 2. Cầu dao: ngắt đúng biên, mở lại đúng sau HAI chu kỳ.
    br = LaunchBreaker()
    check(br.observe(Fraction(5, 100)) is True, "INV-11: 5% không được ngắt")
    check(br.observe(Fraction(8, 100)) is True,
          "INV-11: đúng 8% không được ngắt — biên là > 8%, không phải >= 8%")
    check(br.observe(Fraction(81, 1000)) is False, "INV-11: 8.1% KHÔNG ngắt cổng")
    check(br.observe(Fraction(1, 100)) is False, "INV-11: mở lại sau MỘT chu kỳ sạch")
    check(br.observe(Fraction(1, 100)) is True, "INV-11: không mở lại sau HAI chu kỳ sạch")
    br.check_invariant()

    # Phép phá: một cổng bị ép mở sau chu kỳ bẩn duy nhất phải làm bất biến đỏ.
    br2 = LaunchBreaker()
    br2.observe(Fraction(9, 100))
    br2.allowed = True                     # ai đó "sửa cờ" thay vì sửa dữ liệu
    produced = expect_red(br2.check_invariant)
    check(any("INV-11" in m for m in produced),
          "INV-11: ép cờ allowed = True mà bất biến KHÔNG đỏ")


# ==================================================================== INV-12
@dataclass
class Governance:
    """Ôtômat 3 trạng thái của YP §7.2 — `G0/G1` có multisig, `G2` bất biến."""

    t0: int
    terms_hash: str
    authority: str | None = "squads_4of7"
    queued_at: int | None = None

    def propose(self, signers: int, sim_tests_pass: bool, now: int) -> str | None:
        if self.authority is None:
            return "ERR_PROGRAM_IMMUTABLE"
        if signers < 4 or not sim_tests_pass:
            return "ERR_UPGRADE_NOT_APPROVED"
        self.queued_at = now
        return None

    def execute(self, now: int) -> str | None:
        if self.authority is None:
            return "ERR_PROGRAM_IMMUTABLE"
        if self.queued_at is None:
            return "ERR_UPGRADE_NOT_QUEUED"
        if now < self.queued_at + TIMELOCK:
            return "ERR_TIMELOCK_NOT_ELAPSED"
        self.queued_at = None
        return None

    def set_final(self, now: int) -> str | None:
        if self.authority is None:
            return "ERR_PROGRAM_IMMUTABLE"
        if now < self.t0 + T_IMM:
            return "ERR_IMMUTABILITY_NOT_REACHED"
        self.authority = None
        return None

    def muah_terms(self, new_hash: str) -> str | None:
        """Đổi `terms_hash` — `INV-12` cấm tuyệt đối, kể cả trước `G2`."""
        if new_hash != self.terms_hash:
            return "ERR_TERMS_HASH_IMMUTABLE"
        return None

    def check_invariant(self, now: int) -> None:
        """`INV-12`: terms_hash không đổi, và authority = None với mọi t ≥ t0 + T_imm."""
        check(self.terms_hash == INITIAL_TERMS_HASH,
              "INV-12: terms_hash đã bị đổi trong vòng đời")
        if now >= self.t0 + T_IMM:
            check(self.authority is None,
                  f"INV-12: t = {now} ≥ t0 + T_imm nhưng upgrade_authority = "
                  f"{self.authority!r}")


INITIAL_TERMS_HASH = "9f3c" + "ab" * 30


def inv12() -> None:
    tg = Governance(t0=0, terms_hash=INITIAL_TERMS_HASH)
    # Trước G2: 3/7 chữ ký phải bị từ chối.
    check(tg.propose(3, True, now=1_000) == "ERR_UPGRADE_NOT_APPROVED",
          "INV-12: 3/7 chữ ký mà vẫn cho queue")
    # 4/7 nhưng sim_test fail ⇒ từ chối.
    check(tg.propose(4, False, now=1_000) == "ERR_UPGRADE_NOT_APPROVED",
          "INV-12: sim_tests = False mà vẫn cho queue")
    # Đủ điều kiện ⇒ queue, nhưng chưa hết 48h thì không execute được.
    check(tg.propose(5, True, now=2_000) is None, "INV-12: 5/7 + test PASS bị từ chối")
    check(tg.execute(now=2_000 + TIMELOCK - 1) == "ERR_TIMELOCK_NOT_ELAPSED",
          "INV-12: execute trước 48h")
    check(tg.execute(now=2_000 + TIMELOCK) is None, "INV-12: execute đúng hạn bị từ chối")
    # terms_hash bất khả xâm phạm, cả trước G2.
    check(tg.muah_terms("deadbeef") == "ERR_TERMS_HASH_IMMUTABLE",
          "INV-12: đổi được terms_hash trước G2")
    tg.check_invariant(now=1_000)

    # Phép phá: đặt bất biến SỚM hơn 90 ngày phải bị từ chối.
    check(tg.set_final(now=T_IMM - 1) == "ERR_IMMUTABILITY_NOT_REACHED",
          "INV-12: bất biến hoá trước 90 ngày")
    check(tg.set_final(now=T_IMM) is None, "INV-12: set_final đúng hạn bị từ chối")
    check(tg.authority is None, "INV-12: sau set_final authority vẫn khác None")
    # Sau G2: mọi lệnh nâng cấp bị từ chối vĩnh viễn.
    check(tg.propose(7, True, now=T_IMM + 10) == "ERR_PROGRAM_IMMUTABLE",
          "INV-12: propose sau bất biến không bị từ chối")
    check(tg.execute(now=T_IMM + 10) == "ERR_PROGRAM_IMMUTABLE",
          "INV-12: execute sau bất biến không bị từ chối")
    # Quét toàn đường thời gian: từ T_imm trở đi, authority luôn None.
    for now in (T_IMM, T_IMM + 1, T_IMM + 86_400, 10 * T_IMM):
        tg.check_invariant(now=now)

    # Phép phá cuối: hạ bất biến (đặt lại authority) phải làm bất biến đỏ.
    tg.authority = "squads_4of7"
    produced = expect_red(lambda: tg.check_invariant(now=T_IMM + 1))
    check(any("INV-12" in m for m in produced),
          "INV-12: authority được đặt lại mà bất biến KHÔNG đỏ")


# ==================================================================== runner
INVARIANTS = (
    ("INV-05", inv05, "Phả hệ Phiên bản Đơn điệu"),
    ("INV-07", inv07, "Cô lập Lưu ký Tiền Tốt nghiệp"),
    ("INV-11", inv11, "Giới hạn Gian lận Hệ thống"),
    ("INV-12", inv12, "Tính Bất biến Điều khoản & Quản trị"),
)


def audit() -> int:
    print("\nBỐN BẤT BIẾN TỪNG CHỈ CÓ TÊN — nay có phép kiểm\n")
    for code, fn, name in INVARIANTS:
        global PASSES
        saved = list(FAILS)
        globals()["PASSES"] = 0
        FAILS.clear()
        try:
            fn()
            status = f"✓ {PASSES} kiểm tra"
        except Exception as exc:                        # noqa: BLE001
            FAILS.append(str(exc))
            status = f"✗ {FAILS[0][:70]}"
        print(f"  {code}  {name:42}{status}")
        FAILS[:] = saved
    print("\n4 bất biến · mô hình quyết định, KHÔNG phải chương trình on-chain "
          "(programs/ vẫn trống — docs/39 §1)")
    return 0


def selftest() -> int:
    """4 đối chứng (mỗi bất biến một cái) + 2 phép phá ở mức cổng.

    Ở đây phép phá không nằm trong hàm kiểm — nó nằm ở **chính các `check`** của
    mỗi bất biến (rút trước Graduated, ép cờ allowed, hạ bất biến…). Đối chứng
    của tệp này là: mỗi bất biến, khi chạy trên dữ liệu ĐÚNG, phải xanh — nếu
    không thì cổng đang đỏ vì lý do khác với điều nó định bảo vệ.
    """
    ok = 0
    for code, fn, name in INVARIANTS:
        saved = list(FAILS)
        globals()["PASSES"] = 0
        FAILS.clear()
        try:
            fn()
            good = not FAILS
            detail = FAILS[0][:80] if FAILS else "sạch"
        except Exception as exc:                        # noqa: BLE001
            good, detail = False, str(exc)[:80]
        FAILS[:] = saved
        if good:
            ok += 1
            print(f"  ✓ {code} trên dữ liệu đúng → sạch")
        else:
            print(f"  ✗ {code} → BẮT OAN: {detail}")

    # Phép phá 1: nếu THETA_DIFF bị hạ về 0, "đổi màu 1 nút" phải lọt ⇒ cổng vô dụng.
    global THETA_DIFF
    saved_theta = THETA_DIFF
    THETA_DIFF = Fraction(0)
    _, err = VersionChain().record((0, 1, 0), "aa" * 32, ZERO32, Fraction(0))
    THETA_DIFF = saved_theta
    if err is None:
        ok += 1
        print("  ✓ P5 phép phá: θ_diff = 0 làm δ = 0 lọt vào sổ → chứng minh ngưỡng CÓ tác dụng")
    else:
        print(f"  ✗ P5 phép phá: θ_diff = 0 mà vẫn bị chặn ({err})")

    # Phép phá 2: ngưỡng cầu dao đổi thành 0.5 thì 8.1% KHÔNG được ngắt nữa.
    global BETA_MAX
    saved_beta = BETA_MAX
    BETA_MAX = Fraction(1, 2)
    br = LaunchBreaker()
    allowed = br.observe(Fraction(81, 1000))
    BETA_MAX = saved_beta
    if allowed:
        ok += 1
        print("  ✓ P6 phép phá: β_max = 0.5 làm 8.1% lọt → chứng minh ngưỡng CÓ tác dụng")
    else:
        print("  ✗ P6 phép phá: β_max = 0.5 mà 8.1% vẫn bị ngắt")

    total = len(INVARIANTS) + 2
    if ok != total:
        print(f"INVARIANTS SELFTEST: FAIL — {ok}/{total} phép thử đúng chiều")
        return 1
    print(f"INVARIANTS SELFTEST: PASS — {ok}/{total} phép thử đúng chiều "
          f"(4 đối chứng + 2 phép phá ngưỡng)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Bốn bất biến từng chỉ có tên.")
    ap.add_argument("--audit", action="store_true", help="in từng bất biến")
    ap.add_argument("--selftest", action="store_true", help="kiểm (CI)")
    args = ap.parse_args()

    if args.audit:
        return audit()
    if args.selftest:
        return selftest()

    for code, fn, _name in INVARIANTS:
        try:
            fn()
        except Exception as exc:                        # noqa: BLE001
            FAILS.append(f"{code} — {exc}")
    if FAILS:
        print(f"INVARIANTS: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(f"INVARIANTS: PASS — {PASSES} kiểm tra · 4 bất biến (INV-05, 07, 11, 12) · "
          f"mô hình quyết định")
    return 0


if __name__ == "__main__":
    sys.exit(main())
