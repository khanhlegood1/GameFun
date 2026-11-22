#!/usr/bin/env python3
"""check_sdk_drift.py — hợp đồng SDK đã **đóng băng** chưa, và có ai đang lệch không.

Vì sao có file này (docs/28):
    `docs/27` kiểm hợp đồng *hiện tại* đúng Poki và đúng ngân sách 12 KB. Nhưng nó
    **không** phát hiện được kiểu hỏng nguy hiểm nhất với một SDK đã phát hành:
    hợp đồng **đổi lặng lẽ** trong khi hàng trăm bản build của studio vẫn đang gọi
    theo hợp đồng cũ.

    Repo `Darhlilove/splice` sinh SDK từ OpenAPI: nó có `specVersion` trong log lỗi
    nhưng **không** có tệp khoá hợp đồng, không có phép so bề mặt, và **commit cả
    `dist/`** (50 tệp) — tức là một bản dựng nằm trong git. Ba điều đó đúng cho một
    công cụ demo, sai cho một SDK mà người khác `import`.

Cái nó kiểm (5 bất biến):

  1. **Khoá hợp đồng khớp mã.** `sdk/game-sdk/CONTRACT.json` phải bằng đúng bề mặt
     đọc được từ `game9k-sdk.js`. Thêm/bớt/đổi tên hàm mà không bump khoá là đỏ.
  2. **Khoá khớp `docs/03` §3.** Bề mặt trong tài liệu phải trùng bề mặt trong khoá:
     không có hàm "chỉ có trong mã" (studio không biết) hay "chỉ có trong tài liệu"
     (studio gọi và hỏng).
  3. **`MINOR` trong khoá bằng `version` trong mã.** `Game9KSDK.version` phải là
     `0.MINOR.PATCH` khớp `CONTRACT.json`. Một SDK tự khai sai phiên bản là SDK
     không kiểm được.
  4. **Không có `MAJOR` mồ côi.** Mọi `MAJOR` đã phát hành phải có luật tương thích
     ghi trong `COMPAT`, trừ `MAJOR` hiện tại. Đổi `MAJOR` mà không nói game cũ
     phải làm gì là bỏ rơi người dùng.
  5. **Không có bản dựng trong git.** Không `dist/`, `node_modules/`, `*.min.js`,
     `*.map` dưới `sdk/`. Đây là bài học từ `splice`: `dist/` 50 tệp đã commit,
     và `dist/sdk-templates/` đã **lệch** khỏi `src/sdk-templates/` (thiếu
     `client.ts`, `interceptors.ts`, có thư mục phẳng khác) — tức là thứ được dùng
     lúc chạy không phải thứ đang được review.

Ba chế độ:

    python3 scripts/check_sdk_drift.py              # kiểm 5 bất biến
    python3 scripts/check_sdk_drift.py --surface     # in bề mặt + hash hợp đồng
    python3 scripts/check_sdk_drift.py --bump minor  # in việc phải làm, KHÔNG sửa tệp

Chỉ thư viện chuẩn, không mạng. `--bump` cố ý **không** ghi tệp: bump hợp đồng là
một hành động của người, qua PR, có ADR (docs/25 — cổng là chữ ký người).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SDK_DIR = ROOT / "sdk" / "game-sdk"
CONTRACT = SDK_DIR / "CONTRACT.json"
SDK_JS = SDK_DIR / "game9k-sdk.js"
API_DOC = ROOT / "docs" / "03-api-specification.md"

# Thứ tự này là một phần của hợp đồng: Inspector in 5 sự kiện Poki theo đúng thứ tự
# developers.poki.com/guide/sdk-overview liệt kê.
POKI_EVENTS = ["gameLoadingFinished", "gameplayStart", "gameplayStop", "commercialBreak", "rewardedBreak"]
# `init` là của Game9K nhưng đứng đầu hợp đồng vì game cần nó trước mọi thứ.
GAME9K_EXTRA = ["init", "cloudSave", "reportProgress"]

# Tệp không được có trong git dưới `sdk/`.
BUILD_ARTIFACT_PATTERNS = [
    (r"(^|/)dist/", "bản dựng trong git — sẽ lệch khỏi nguồn (bài học `splice`)"),
    (r"(^|/)node_modules/", "phụ thuộc trong git"),
    (r"\.min\.js$", "bản nén trong git — không review được, không đếm được"),
    (r"\.map$", "source map của bản dựng trong git"),
]

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


# ------------------------------------------------------------------ đọc bề mặt
def surface_from_js() -> list[str]:
    """Đọc tên hàm công khai từ `var SDK = { ... }` trong SDK tham chiếu.

    Cố ý đọc bằng regex thay vì chạy mã: cổng CI không được `eval` một tệp có thể
    bị sửa bởi PR. Đây cũng là lý do `check_sdk.py` cấm `eval`/`new Function`.
    """
    code = SDK_JS.read_text(encoding="utf-8")
    start = code.index("var SDK = {")
    # Cân ngoặc từ `{` đầu tiên sau `var SDK = `.
    i = code.index("{", start)
    depth = 0
    for j in range(i, len(code)):
        if code[j] == "{":
            depth += 1
        elif code[j] == "}":
            depth -= 1
            if depth == 0:
                block = code[i : j + 1]
                break
    else:
        raise ValueError("không cân được ngoặc của `var SDK`")
    # Chỉ lấy khoá ở mức ngoài cùng (depth 1).
    names, depth = [], 0
    for line in block.splitlines():
        if depth == 1:
            # Chỉ nhận KHOÁ LÀ HÀM. `version: '0.1.0'` là thuộc tính, không phải
            # hàm — đếm nó vào bề mặt là làm khoá hợp đồng sai ngay từ đầu.
            m = re.match(r"\s{4}([A-Za-z_$][\w$]*)\s*:\s*(function\b|\{)", line)
            if m:
                names.append(m.group(1))
        depth += line.count("{") - line.count("}")
    return names


def surface_from_doc() -> list[str]:
    text = API_DOC.read_text(encoding="utf-8")
    sec = text[text.index("## 3. Hợp đồng") :]
    sec = sec[: sec.find("\n---", 10)]
    names = re.findall(r"(?m)^\s{2}([A-Za-z_$][\w$]*)\s*[:(]", sec)
    return list(dict.fromkeys(names))


def contract_hash(data: dict) -> str:
    """Hash của *bề mặt*, không phải của tệp — comment đổi không được đổi hash."""
    canon = json.dumps(
        {"major": data["major"], "minor": data["minor"], "functions": data["functions"]},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------ 5 bất biến
def check_contract_matches_js(contract: dict) -> None:
    js = surface_from_js()
    want = contract["functions"]
    check(
        js == want,
        f"CONTRACT.json ≠ mã: thừa {sorted(set(js) - set(want))}, thiếu {sorted(set(want) - set(js))}, "
        f"hoặc sai thứ tự. Bề mặt đọc từ mã: {js}",
    )
    # Thứ tự cũng là hợp đồng: `init` đầu, rồi ĐÚNG thứ tự 5 sự kiện Poki,
    # rồi tiện ích riêng. Đổi thứ tự là đổi thứ tự Inspector in ra.
    check(
        want[:6] == ["init"] + POKI_EVENTS,
        f"CONTRACT.json: 6 hàm đầu phải là `init` + thứ tự Poki {POKI_EVENTS}, đang là {want[:6]}",
    )
    check(
        want[6:] == ["cloudSave", "reportProgress"],
        f"CONTRACT.json: tiện ích riêng sau cùng phải là cloudSave, reportProgress — đang là {want[6:]}",
    )


def check_contract_matches_doc(contract: dict) -> None:
    doc = surface_from_doc()
    want = contract["functions"]
    only_doc = [n for n in doc if n not in want and n not in {"cloudSave"}]
    only_code = [n for n in want if n not in doc]
    check(not only_doc, f"docs/03 §3 có hàm KHÔNG có trong khoá: {only_doc} — studio sẽ gọi và hỏng")
    check(not only_code, f"khoá có hàm KHÔNG có trong docs/03 §3: {only_code} — studio không biết là có")


def check_version_sync(contract: dict) -> None:
    code = SDK_JS.read_text(encoding="utf-8")
    m = re.search(r"var SDK_VERSION = '([^']+)'", code)
    check(m is not None, "SDK: không tìm thấy `var SDK_VERSION`")
    if m:
        parts = m.group(1).split(".")
        check(len(parts) == 3, f"SDK_VERSION `{m.group(1)}` không theo dạng MAJOR.MINOR.PATCH")
        if len(parts) == 3:
            check(
                int(parts[0]) == contract["major"] and int(parts[1]) == contract["minor"],
                f"SDK_VERSION `{m.group(1)}` ≠ CONTRACT {contract['major']}.{contract['minor']}.x "
                "— SDK tự khai sai phiên bản là SDK không kiểm được",
            )


def check_compat_rules(contract: dict) -> None:
    compat = contract.get("compat", {})
    for major in contract.get("released_majors", []):
        check(
            str(major) in compat,
            f"MAJOR `{major}` đã phát hành nhưng thiếu luật tương thích trong `compat` "
            "— game cũ không biết phải làm gì",
        )
    for major, rule in compat.items():
        check(
            bool(rule.get("rule")) and len(rule["rule"]) > 20,
            f"compat[{major}]: luật quá ngắn để làm theo (`{rule.get('rule')}`)",
        )
        check(
            rule.get("removal") in {"never", "after_major_plus_1", "next_major"},
            f"compat[{major}]: `removal` phải là never / after_major_plus_1 / next_major",
        )


def check_no_artifacts() -> None:
    if not SDK_DIR.exists():
        return
    for path in sorted(SDK_DIR.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(ROOT).as_posix()
        for pattern, why in BUILD_ARTIFACT_PATTERNS:
            if re.search(pattern, rel):
                FAILS.append(f"{rel}: {why}")
                break


# ------------------------------------------------------------------ in
def print_surface() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    print(f"\nBỀ MẶT HỢP ĐỒNG — {contract['package']} {contract['major']}.{contract['minor']}.x\n")
    for i, name in enumerate(contract["functions"]):
        kind = "Poki" if 1 <= i <= 5 else "Game9K"
        print(f"  {i + 1}. {name:<22} [{kind}]  {contract['signatures'][name]}")
    print(f"\n  ADAPTER      {contract['adapter']}")
    print(f"  khoá bề mặt  sha256:{contract_hash(contract)}")
    print(f"  luật gỡ bỏ  {contract['compat'][str(contract['major'])]['removal']}")
    return 0


def print_bump(kind: str) -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    major, minor = contract["major"], contract["minor"]
    if kind == "minor":
        print(
            f"\nBUMP MINOR: {major}.{minor}.x → {major}.{minor + 1}.0\n"
            "  Thêm hàm = MINOR. Việc phải làm, theo thứ tự:\n"
            "  1. thêm hàm vào `docs/03` §3 (hợp đồng công khai) — cùng PR\n"
            "  2. cập nhật `sdk/game-sdk/CONTRACT.json` (functions + signatures + minor)\n"
            "  3. cập nhật `var SDK_VERSION` trong `game9k-sdk.js`\n"
            "  4. thêm một dòng vào `compat` nếu luật gỡ bỏ đổi\n"
            "  5. `python3 scripts/check_sdk.py && python3 scripts/check_sdk_drift.py`\n"
            "\n  Tệp KHÔNG bị sửa bởi lệnh này: bump hợp đồng là hành động của người, qua PR."
        )
    elif kind == "major":
        print(
            f"\nBUMP MAJOR: {major} → {major + 1}.0.0\n"
            "  Đổi MAJOR = game đang chạy phải sửa. Trước khi bump, viết vào `compat`:\n"
            f"  · luật cho MAJOR `{major}`: giữ hàm bao lâu, cảnh báo ở đâu, gỡ khi nào\n"
            "  · một trong ba giá trị `removal`: never / after_major_plus_1 / next_major\n"
            f"  · ghi ADR nêu rõ: ai đang gọi hàm bị đổi, và họ biết bằng cách nào.\n"
            "\n  Không có luật tương thích thì không được bump (check_sdk_drift.py sẽ đỏ)."
        )
    else:
        print("--bump nhận `minor` hoặc `major`", file=sys.stderr)
        return 2
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Khoá hợp đồng SDK: chống đổi lặng lẽ.")
    ap.add_argument("--surface", action="store_true", help="in bề mặt + hash hợp đồng")
    ap.add_argument("--bump", metavar="MINOR|MAJOR", help="in việc phải làm (không sửa tệp)")
    args = ap.parse_args()

    if args.surface:
        return print_surface()
    if args.bump:
        return print_bump(args.bump.lower())

    if not CONTRACT.exists():
        print(f"SDK DRIFT: FAIL — thiếu {CONTRACT.relative_to(ROOT)}")
        return 1
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    check_contract_matches_js(contract)
    check_contract_matches_doc(contract)
    check_version_sync(contract)
    check_compat_rules(contract)
    check_no_artifacts()

    if FAILS:
        print(f"SDK DRIFT: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1

    print(
        f"SDK DRIFT: PASS — {PASSES} kiểm tra · 5 bất biến · "
        f"khoá {contract['package']} {contract['major']}.{contract['minor']}.x "
        f"sha256:{contract_hash(contract)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
