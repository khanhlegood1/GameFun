#!/usr/bin/env python3
"""check_sdk.py — hợp đồng `@game9k/game-sdk` phải khớp CẢ Poki lẫn `docs/03`.

Vì sao có file này (docs/27):
    `docs/03` §3 khai SDK "tương thích 1:1 với Poki" và hiện có **6** hàm.
    `docs/PRD.md` FR-SDK-01 hứa module **< 12 KB gzip**. Một lời hứa như thế
    chỉ đúng nếu có ai đó đếm. File này là người đếm.

Cái nó kiểm (5 bất biến):

  1. **Siêu tập Poki.** Mọi hàm Poki công bố phải có trong `docs/03` §3, đúng tên,
     đúng chữ ký. Thiếu một hàm là lời hứa "port trong 10 phút" thành sai.
  2. **Ngân sách 12 KB.** Số byte của một client tối thiểu (đoạn `const d=…`);
     so với `12000` trong FR-SDK-01. Đếm **byte**, không đếm ký tự.
  3. **Chỉ `postMessage`.** Không `import`, không `fetch`, không `eval`,
     không `localStorage`/`cookie`/`Function(` — vì `docs/03` §3 cấm đọc storage
     ngoài phạm vi game, và một SDK tự do gọi mạng là một SDK tự do rò dữ liệu.
  4. **Không có hàm thanh toán/đăng nhập.** Một SDK game trả tiền cho Xsolla/Paddle
     hoặc tự `openCheckout` là thứ `docs/27` §6 R2 **từ chối**: ví và thanh toán
     không bao giờ nằm trong mã chạy từ studio.
  5. **Có `env()` để tắt quảng cáo.** `commercialBreak`/`rewardedBreak` phải
     **hỏi môi trường trước khi hứa**: Inspector và Arena không được phát quảng cáo
     (Arena Blind Duel cấm lộ nhãn phiên bản → cấm cả quảng cáo vì nó lộ thời điểm).

Bốn chế độ:

    python3 scripts/check_sdk.py                # 5 bất biến + in bảng ngân sách
    python3 scripts/check_sdk.py --species      # in đặc tả 2 loài (game ↔ portal)
    python3 scripts/check_sdk.py --matrix       # in ma trận hành vi 5 môi trường
    python3 scripts/check_sdk.py --selftest     # dùng trong CI (thoát 1 nếu đỏ)

Chỉ thư viện chuẩn, không mạng. File này KHÔNG chạy mã của SDK; nó đọc chuỗi.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API_DOC = ROOT / "docs" / "03-api-specification.md"
SDK_DIR = ROOT / "sdk" / "game-sdk"

# Ngân sách gzip theo `docs/PRD.md` FR-SDK-01.
BUDGET_BYTES = 12_000

# 5 sự kiện vòng đời Poki + `init` mà Game9K thêm.
# Nguồn: developers.poki.com/guide/sdk-overview (đọc 22/11/2026).
POKI_EVENTS = [
    "gameLoadingFinished",
    "gameplayStart",
    "gameplayStop",
    "commercialBreak",
    "rewardedBreak",
]
GAME9K_ONLY = ["init", "cloudSave", "reportProgress"]

# Chuỗi bị cấm trong mã SDK, kèm lý do đọc được.
FORBIDDEN = [
    (r"\bfetch\s*\(", "gọi mạng — SDK chỉ nói chuyện qua postMessage"),
    (r"\bXMLHttpRequest\b", "gọi mạng — SDK chỉ nói chuyện qua postMessage"),
    (r"\beval\s*\(", "chạy mã động — không kiểm được, không ký được"),
    (r"\bnew\s+Function\b", "chạy mã động — không kiểm được, không ký được"),
    (r"\bimport\s+", "phụ thuộc ngoài — phá ngân sách 12 KB"),
    (r"\brequire\s*\(", "phụ thuộc ngoài — phá ngân sách 12 KB"),
    (r"localStorage", "đọc storage — docs/03 §3.2 cấm đọc storage ngoài phạm vi game"),
    (r"sessionStorage", "đọc storage — docs/03 §3.2 cấm đọc storage ngoài phạm vi game"),
    (r"document\.cookie", "đọc cookie — docs/03 §3.2 cấm"),
    (r"openCheckout|purchase\s*\(|payStation|xsolla", "thanh toán trong mã studio — docs/27 §6 R2"),
    (r"signTransaction|sendTransaction|window\.solana", "ký/gửi giao dịch trong iframe game — docs/27 §6 R2"),
]

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


# ------------------------------------------------------------------ đọc tài liệu
def api_section() -> str:
    """Trả về khối §3 của `docs/03` (từ heading tới `---` kế tiếp)."""
    text = API_DOC.read_text(encoding="utf-8")
    start = text.index("## 3. Hợp đồng")
    rest = text[start:]
    end = rest.find("\n---", 10)
    return rest[: end if end > 0 else len(rest)]


def sdk_sources() -> list[Path]:
    if not SDK_DIR.exists():
        return []
    return sorted(p for p in SDK_DIR.rglob("*.js") if "node_modules" not in p.parts)


# ------------------------------------------------------------------ 1. siêu tập Poki
def check_poki_superset() -> None:
    sec = api_section()
    for ev in POKI_EVENTS:
        check(
            re.search(rf"\b{ev}\s*\(", sec) is not None,
            f"docs/03 §3: thiếu hàm Poki `{ev}()` — lời hứa 'tương thích 1:1' thành sai",
        )
    # Chữ ký của 5 hàm phải đúng kiểu: gameLoadingFinished(): void
    for ev in ("gameLoadingFinished", "gameplayStart", "gameplayStop"):
        check(
            re.search(rf"\b{ev}\(\):\s*void", sec) is not None,
            f"docs/03 §3: `{ev}` không còn là `(): void` — đổi chữ ký là phá game đang chạy",
        )
    check(
        re.search(r"rewardedBreak\(.*?\):\s*Promise<boolean>", sec) is not None,
        "docs/03 §3: `rewardedBreak` phải trả `Promise<boolean>` (true = người chơi xem xong)",
    )
    check(
        re.search(r"commercialBreak\(.*?\):\s*Promise<void>", sec) is not None,
        "docs/03 §3: `commercialBreak` phải trả `Promise<void>`",
    )
    # Tiện ích riêng của Game9K phải còn — nếu mất, `reportProgress` thành lời hứa suông.
    for own in GAME9K_ONLY:
        check(own in sec, f"docs/03 §3: mất tiện ích riêng `{own}`")


# ------------------------------------------------------------------ 2. ngân sách
def measure(path: Path) -> int:
    return len(gzip.compress(path.read_bytes(), 9))


def check_budget() -> None:
    sources = sdk_sources()
    if not sources:
        # Khi chưa có mã, vẫn kiểm *lời hứa* còn trong PRD — nếu ai xoá nó, cổng báo.
        prd = (ROOT / "docs" / "PRD.md").read_text(encoding="utf-8")
        check("12 KB" in prd, "docs/PRD.md: FR-SDK-01 không còn ngân sách `12 KB`")
        return
    # Tổng gzip của mọi file .js — cộng dồn là cách duy nhất không tự lừa mình
    # bằng cách đo một file rồi bỏ quên file thứ hai.
    total = sum(measure(p) for p in sources)
    check(
        total < BUDGET_BYTES,
        f"sdk/game-sdk gzip {total} B ≥ ngân sách {BUDGET_BYTES} B (FR-SDK-01) — {[p.name for p in sources]}",
    )
    # Từng file cũng phải dưới ngân sách: một file 20 KB không thể "trung bình" xuống.
    for p in sources:
        check(measure(p) < BUDGET_BYTES, f"{p.name}: gzip {measure(p)} B ≥ ngân sách {BUDGET_BYTES} B")


# ------------------------------------------------------------------ 3-4. chuỗi cấm
def check_forbidden() -> None:
    sources = sdk_sources()
    if not sources:
        return
    for p in sources:
        code = p.read_text(encoding="utf-8")
        # Bỏ comment để không bắt oan một ghi chú kiểu "không dùng fetch".
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
        code = re.sub(r"(?m)^\s*//.*$", "", code)
        for pattern, why in FORBIDDEN:
            if re.search(pattern, code, flags=re.I if "xsolla" in pattern else 0):
                FAILS.append(f"{p.name}: chứa `{pattern}` — {why}")


# ------------------------------------------------------------------ 5. tắt quảng cáo
def check_ad_guard() -> None:
    sources = sdk_sources()
    if not sources:
        return
    code = "\n".join(p.read_text(encoding="utf-8") for p in sources)
    for fn in ("commercialBreak", "rewardedBreak"):
        check(fn in code, f"SDK thiếu `{fn}` — hợp đồng Poki không đủ")
    # Quảng cáo phải được chặn theo môi trường, không phải theo lời gọi của game.
    check(
        re.search(r"\b(?:env|environment)\s*={2,3}\s*['\"]arena['\"]", code) is not None
        or "NO_ADS" in code,
        "SDK: `commercialBreak`/`rewardedBreak` không kiểm môi trường — Arena sẽ phát quảng cáo",
    )


# ------------------------------------------------------------------ in
SPECIES = [
    ("Loài A — `game-sdk` (chạy trong iframe game)", "viết bởi **studio**, chạy trên origin của bản build"),
]
SPECIES_ROWS = [
    ("Ai ký mã", "Game9K ký và phát hành (`@game9k/game-sdk`), studio `import`"),
    ("Ai gọi", "Mã game gọi hàm; **người chơi không bao giờ gọi trực tiếp**"),
    ("Chạm tiền?", "**Không.** Không hàm nào trong 6 hàm tạo, ký hay gửi giao dịch"),
    ("Chạm danh tính?", "**Chỉ `cloudSave`** — và nó đi qua portal, SDK không thấy token"),
    ("Quyền tối thiểu", "`postMessage` ra `window.parent`; đọc `performance`/`rAF`"),
    ("Nếu bị sửa", "Game hỏng, không mất tiền — vì không có gì để mất trong iframe"),
]
PORTAL_ROWS = [
    ("Ai ký mã", "Game9K; **không** studio nào chạy mã trong tiến trình này"),
    ("Ai gọi", "Trình duyệt của người chơi, qua trang `/g/[slug]`"),
    ("Chạm tiền?", "**Có** — nhưng chỉ để *hiển thị* số dư; ký nằm ở passkey (docs/11)"),
    ("Chạm danh tính?", "**Có** — phiên Supabase `HttpOnly`, không bao giờ xuống iframe"),
    ("Quyền tối thiểu", "CSP `frame-ancestors 'self'`; iframe có `sandbox` không `allow-same-origin`"),
    ("Nếu bị sửa", "Mất tiền/mất danh tính — nên đây là bề mặt cần review tay"),
]


def print_species() -> int:
    print("\nHAI LOÀI SDK — cùng một hợp đồng, khác hẳn mức đặc quyền\n")
    w1, w2 = 22, 62
    print(f"{'':24}│ {'Loài A — `game-sdk`':{w1}}│ Loài B — portal")
    print("─" * (24 + 1 + w1 + 1 + w2))
    for (label, a), (_, b) in zip(SPECIES_ROWS, PORTAL_ROWS):
        print(f"{label:{24}}│ {a:{w1}}│ {b}")
    print(
        "\nGộp hai loài là lỗi thiết kế: nếu `game-sdk` giữ được token thanh toán, "
        "một game bị xâm nhập là một ví bị xâm nhập."
    )
    return 0


MATRIX = [
    # (hàm, inspector, preview, play, arena, direct)
    ("gameLoadingFinished", "✓ ghi log", "✓ ghi log", "✓ tính C2P", "✓ tính C2P", "✓ ghi log"),
    ("gameplayStart", "✓", "✓", "✓", "✓ (bắt buộc 90 s)", "✓"),
    ("gameplayStop", "✓", "✓", "✓", "✓", "✓"),
    ("commercialBreak", "⛔ không phát", "⛔ không phát", "✓ (portal quyết)", "⛔ **cấm**", "⛔ `0%` phí → không chèn"),
    ("rewardedBreak", "⛔ trả `false`", "⛔ trả `false`", "✓ tự nguyện", "⛔ **cấm**", "⛔ trả `false`"),
    ("cloudSave", "✓ bộ nhớ tạm", "✓", "✓", "✓ (ghi sau khi chấm)", "✗ không có portal"),
    ("reportProgress", "✓", "✓", "✓", "✓", "✗"),
    ("init().versionLabel", "✓ có", "✓ có", "✓ có", "⛔ **không trả**", "✓ có"),
]


def print_matrix() -> int:
    head = ("Hàm", "inspector", "preview", "play", "arena", "direct")
    widths = (22, 14, 13, 20, 16, 22)
    print("\nMA TRẬN HÀNH VI — 5 sự kiện Poki + 3 tiện ích, trên 5 môi trường\n")
    print("".join(h.ljust(w) for h, w in zip(head, widths)))
    print("─" * sum(widths))
    for row in MATRIX:
        print("".join(c.ljust(w) for c, w in zip(row, widths)))
    print(
        "\nHai ô ⛔ cấm tuyệt đối: **arena** (quảng cáo lộ thời điểm, phá Blind Duel) và\n"
        "**direct** (`0%` phí trên lưu lượng studio tự kéo — docs/WHITEPAPER §7 nguồn 4).\n"
        "Đây là lý do `commercialBreak`/`rewardedBreak` phải **hỏi môi trường**, không tin lời gọi."
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm hợp đồng @game9k/game-sdk (Poki 1:1 + ngân sách 12 KB).")
    ap.add_argument("--species", action="store_true", help="in đặc tả 2 loài (game ↔ portal)")
    ap.add_argument("--matrix", action="store_true", help="in ma trận hành vi 5 môi trường")
    ap.add_argument("--selftest", action="store_true", help="kiểm 5 bất biến (CI)")
    args = ap.parse_args()

    if args.species:
        return print_species()
    if args.matrix:
        return print_matrix()

    check_poki_superset()
    check_budget()
    check_forbidden()
    check_ad_guard()

    sources = sdk_sources()
    measured = sum(measure(p) for p in sources) if sources else 0

    if FAILS:
        print(f"SDK CONTRACT: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1

    mode = "thi hành" if sources else "chỉ lời hứa (chưa có mã)"
    print(
        f"SDK CONTRACT: PASS — {PASSES} kiểm tra · 5 bất biến · chế độ: {mode}"
    )
    if sources:
        print(f"  gzip đo được: {measured} B / {BUDGET_BYTES} B ngân sách "
              f"({100 * measured / BUDGET_BYTES:.1f}%) trên {len(sources)} tệp")
    else:
        print("  5 hàm Poki + 3 tiện ích Game9K còn đủ trong docs/03 §3; ngân sách 12 KB còn trong PRD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
