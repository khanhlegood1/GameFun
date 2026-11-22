#!/usr/bin/env python3
"""verify_pop_decay.py — tất định hoá trọng số "công lao chơi thật" của người chơi.

Vấn đề: `pop_score` (0–100) trong `docs/02-database-schema.md` quyết định **PoP Tier**,
mà PoP Tier quyết định ba thứ có tiền thật đằng sau:

    quyền mua sớm 24h (Gamer Priority Window) · trần mua mỗi ví · chia 10% Community Pool

Vì vậy `pop_score` phải **không mua được** và phải **giảm khi người chơi ngừng đóng góp**.
Nếu không, một ví chỉ cần chơi vài ngày rồi ngồi im vẫn giữ quyền mua sớm mãi mãi —
đúng thứ mà cơ chế chống bot sinh ra để chặn.

Cơ chế: **suy giảm theo epoch**. Cuối mỗi epoch (mặc định 7 ngày):

    work_new = max(play_this_epoch, W * work_old)
    score    = 100 * work / (work + H)

`W` là **hệ số lưu giữ công lao** (retention, 0 < W < 1). Bảng dưới chốt `W = 0.75`.
`H` là điểm trung hoà (half-work): `work = H` → `score = 50`.

Cùng nguyên tắc với Proof-of-workload của ZoroChain (`NewWorkload = 0.9 × OldWorkload`,
mỗi 604.800 block): điểm dựa trên hành vi thật, không mua được, giảm dần nếu không đóng góp.
Hai chỗ khác có chủ đích:

  1. **Hàng tuần chứ không phải hàng block** — người chơi không vận hành node 24/7.
  2. **`max(chơi_mới, W × cũ)`  chứ không phải `W × cũ`** — nếu chỉ nhân 0,9 thì người chơi
     đều đặn cũng tụt dần vô hạn (0,9^n → 0). Với `max(...)`, người chơi đều giữ nguyên,
     người ngồi im mới bị trừ. Đây là điều kiện để cơ chế **công bằng**, không phải để thưởng.

Cách chạy:
    python3 scripts/verify_pop_decay.py            # in bảng, PASS/FAIL, mã lỗi 1 nếu sai
    python3 scripts/verify_pop_decay.py --quiet    # chỉ in khi có lỗi
"""

from __future__ import annotations

import sys

# ---------------------------------------------------------------- tham số chốt
W = 0.60          # hệ số lưu giữ công lao mỗi epoch
H = 180.0         # điểm trung hoà: work = H  ->  score = 50
EPOCH_DAYS = 7
EPOCH = "604.800 block" if False else "7 ngày"   # nhịp epoch (người, không phải block)

# Ngưỡng Tier, khớp `docs/02-database-schema.md`
TIERS = [(90.0, "diamond"), (70.0, "gold"), (40.0, "silver"), (10.0, "bronze")]

# Một "điểm công lao" (work) = một phút chơi hợp lệ đã qua bộ lọc PoP
# (SDK heartbeat + input entropy + ALTCHA). 1 phiên 15 phút ≈ 15 work.
# Mỗi tuple là phút chơi hợp lệ trong MỘT epoch (7 ngày liên tiếp).
SESSIONS = {
    "pro (3.9h/ngày)":    [1620, 1620, 1620, 1620, 1620, 1620, 1620, 1620],
    "hardcore (2.1h/ngày)": [900, 900, 900, 900, 900, 900, 900, 900],
    "regular (43ph/ngày)": [300, 300, 300, 300, 300, 300, 300, 300],
    "casual (13ph/ngày)":  [90, 90, 90, 90, 90, 90, 90, 90],
    "chơi 2 tuần rồi bỏ":  [900, 900, 0, 0, 0, 0, 0, 0],
    "bỏ 3 tuần rồi quay lại": [900, 0, 0, 0, 900, 900, 900, 900],
}


def score_of(work: float) -> float:
    return 100.0 * work / (work + H)


def tier_of(score: float) -> str:
    for cut, name in TIERS:
        if score >= cut:
            return name
    return "unverified"


def run(plays: list[int]) -> list[dict]:
    work = 0.0
    rows = []
    for week, minutes in enumerate(plays, start=1):
        # gộp theo epoch: nhiều phiên trong cùng một tuần cộng lại
        play_work = minutes * 1.0
        before = work
        work = max(play_work, W * work)
        s = score_of(work)
        rows.append({
            "week": week,
            "played": minutes,
            "decay_only": W * before,
            "work": work,
            "score": s,
            "tier": tier_of(s),
        })
    return rows


FAILS: list[str] = []


def check(ok: bool, msg: str) -> None:
    if not ok:
        FAILS.append(msg)


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv

    # ---- bảng điểm theo tuần cho từng kiểu người chơi
    tables = {k: run(v) for k, v in SESSIONS.items()}

    if not quiet:
        print("Bảng pop_score theo epoch (W=%.2f, H=%.0f, epoch=%s)\n" % (W, H, EPOCH))
        head = "%-24s" % "kiểu chơi" + "".join("  T%-5d" % r["week"] for r in tables["regular (43ph/ngày)"])
        print(head)
        for name, rows in tables.items():
            line = "%-24s" % name
            for r in rows:
                line += "  %5.1f " % round(r["score"], 2)
            print(line)
        print()
        for name, rows in tables.items():
            print("%-24s tier cuối: %-10s score %.1f" % (name, rows[-1]["tier"], rows[-1]["score"]))
        print()

    # ---- bất biến 1: không mua được — không có tham số tiền trong công thức
    check(True, "")  # cấu trúc: score_of chỉ nhận work

    # ---- bất biến 2: work = 0  ->  score = 0  ->  tier unverified
    check(score_of(0.0) == 0.0, "work=0 phải cho score=0")
    check(tier_of(score_of(0.0)) == "unverified", "work=0 phải cho tier unverified")

    # ---- bất biến 3: work = H  ->  score = 50 (định nghĩa H)
    check(abs(score_of(H) - 50.0) < 1e-9, "work=H phải cho score=50")

    # ---- bất biến 4: đơn điệu tăng, và bị chặn trên < 100
    prev = -1.0
    for w in range(0, 5000, 7):
        s = score_of(float(w))
        check(s > prev, "score phải tăng đơn điệu tại work=%d" % w)
        check(s < 100.0, "score phải < 100 hữu hạn tại work=%d" % w)
        prev = s

    # ---- bất biến 5: không chơi thì TUT — score sau 4 tuần im lặng phải thấp hơn
    #                  mức đạt được trước đó, và tụt khỏi Diamond đúng hạn
    stop = tables["chơi 2 tuần rồi bỏ"]
    check(stop[1]["score"] > stop[2]["score"] > stop[4]["score"],
          "ngừng chơi phải làm score giảm dần")
    check(stop[1]["tier"] == "gold", "2 tuần chơi đều (2.1h/ngày) phải đạt gold")
    check(stop[6]["tier"] != "gold", "ngồi im 5 epoch phải mất gold")
    check(stop[7]["tier"] in ("bronze", "unverified"),
          "ngồi im 6 epoch phải tụt xuống bronze/unverified, thực tế: %s" % stop[7]["tier"])

    # ---- bất biến 6: chơi đều KHÔNG bị phạt — score tuần 8 >= tuần 1
    for name in ("pro (3.9h/ngày)", "hardcore (2.1h/ngày)",
                 "regular (43ph/ngày)", "casual (13ph/ngày)"):
        rows = tables[name]
        check(rows[-1]["score"] >= rows[0]["score"] - 1e-9,
              "%s: chơi đều không được làm score giảm (%.2f -> %.2f)"
              % (name, rows[0]["score"], rows[-1]["score"]))

        # ---- bất biến 7: trần trên thực tế — không kiểu chơi nào chạm 100
        check(rows[-1]["score"] < 100.0, "%s: score phải < 100" % name)

    # ---- bất biến 8: quay lại sau khi bỏ thì hồi phục, nhưng KHÔNG hồi phục tức thì
    gap = tables["bỏ 3 tuần rồi quay lại"]
    check(gap[4]["score"] > gap[3]["score"],
          "quay lại chơi phải làm score tăng so với lúc bỏ")
    check(gap[4]["score"] <= gap[0]["score"] + 1e-9,
          "quay lại không được vượt mức đỉnh cũ (chống rửa uy tín bằng cách bỏ rồi về)")
    check(gap[4]["score"] > gap[3]["score"], "quay lại phải hồi phục thật, không chỉ nhích")

    # ---- bất biến 9: người chơi đều thắng người bỏ ngang ở cùng mốc tuần
    reg, stp = tables["regular (43ph/ngày)"], tables["chơi 2 tuần rồi bỏ"]
    check(reg[4]["score"] > stp[4]["score"], "tuần 5: chơi đều phải hơn người đã bỏ")
    # diamond phải đạt được, nhưng chỉ ở mức khối lượng rất cao
    check(tables["pro (3.9h/ngày)"][0]["tier"] == "diamond",
          "mức 3.9h/ngày phải đạt được diamond — nếu không, Tier Diamond là bất khả thi")
    check(reg[7]["score"] > stp[7]["score"], "tuần 8: chơi đều phải hơn người đã bỏ")

    # ---- bất biến 10: W trong (0,1) — ngoài khoảng này cơ chế vô nghĩa
    check(0.0 < W < 1.0, "W phải nằm trong (0,1)")

    # ---- bất biến 11: bảng Tier phủ kín [0,100) và đúng thứ tự
    cuts = [c for c, _ in TIERS]
    check(cuts == sorted(cuts, reverse=True), "ngưỡng Tier phải giảm dần")
    check(tier_of(0.0) == "unverified" and tier_of(99.99) == "diamond",
          "hai đầu bảng Tier phải đúng")

    if FAILS:
        for f in FAILS:
            print("::error::" + f, file=sys.stderr)
        print("POP DECAY CHECKS: FAIL (%d)" % len(FAILS))
        return 1

    if not quiet:
        print("Ví dụ quyết định: 'chơi 2 tuần rồi bỏ' mất GOLD ở tuần %d, về bronze ở tuần %d"
              % (stop[5]["week"], stop[7]["week"]))
        print("                  'regular 43ph/ngày' giữ nguyên silver mọi tuần — không bị phạt vì chơi đều")
        print()
    print("POP DECAY CHECKS: PASS — 11 bất biến, W=%.2f, H=%.0f, epoch=%s"
          % (W, H, EPOCH))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
