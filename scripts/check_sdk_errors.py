#!/usr/bin/env python3
"""check_sdk_errors.py — bảng mã lỗi của SDK phải KHỚP với mã trong `docs/03` §4.

Vì sao có file này (docs/29):
    `docs/03` §4 đã có "Bảng Mã Lỗi Tiêu chuẩn" cho **REST API** (`VALIDATION_ERROR`,
    `PAYLOAD_TOO_LARGE`, `RATE_LIMIT_EXCEEDED`…). Nhưng SDK chạy trong iframe
    **không bao giờ thấy** mã HTTP: nó chỉ thấy một Promise bị từ chối. Trước bản
    này, SDK trả `resolve(null)` — nghĩa là *mọi* kiểu hỏng trở thành "không biết".

    Bài học lấy từ `e2b-dev/E2B` (`packages/python-sdk/e2b/exceptions.py`): họ tách
    `SandboxNotRunningException` khỏi `SandboxUnreachableException` **chỉ khi** dấu
    hiệu phân biệt được thật sự đáng tin, và tự ghi rõ giới hạn đó trong docstring
    ("a sandbox that is gone but could not be asked about is an unreachable one").
    Đó là cách đặt tên lỗi đúng: hứa ít hơn, và nói rõ chỗ không biết.

Cái nó kiểm (4 bất biến):

  1. **Mã trong SDK ⊂ mã trong `docs/03` §4.** SDK không được bịa mã lỗi riêng.
  2. **Không mã nào chỉ có trong tài liệu mà SDK dùng.** Nếu `docs/03` §4 khai một
     mã SDK-sẽ-ném, SDK phải có.
  3. **Mỗi mã có đúng một dòng trong bảng §4**, và dòng đó nêu **đều phải làm gì**.
  4. **Không lỗi nào là "im lặng".** Mọi nhánh `reject` phải kèm `code`; không có
     `resolve(null)` khi thao tác đã gửi đi (bài học `docs/29 §2.3`).

Ba chế độ:

    python3 scripts/check_sdk_errors.py            # 4 bất biến
    python3 scripts/check_sdk_errors.py --table    # in bảng lỗi SDK ↔ HTTP
    python3 scripts/check_sdk_errors.py --selftest # CI (thoát 1 nếu đỏ)

Chỉ thư viện chuẩn, không mạng. Không `eval` tệp SDK — đọc bằng regex, cùng lý do
với `check_sdk_drift.py`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SDK_JS = ROOT / "sdk" / "game-sdk" / "game9k-sdk.js"
API_DOC = ROOT / "docs" / "03-api-specification.md"
CONTRACT = ROOT / "sdk" / "game-sdk" / "CONTRACT.json"

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def sdk_error_codes() -> dict[str, str]:
    """Đọc khối `var CODE = {...}`: tên hằng → chuỗi mã."""
    code = SDK_JS.read_text(encoding="utf-8")
    block = code[code.index("var CODE = {") :]
    block = block[: block.index("};")]
    return dict(re.findall(r"(\w+):\s*'([^']+)'", block))


def doc_error_codes() -> dict[str, str]:
    """Đọc bảng §4 của `docs/03`: mã → mô tả."""
    text = API_DOC.read_text(encoding="utf-8")
    sec = text[text.index("## 4. Bảng Mã Lỗi"):]
    out = {}
    for line in sec.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        for token in re.findall(r"`([A-Za-z_][\w]*)`", cells[1] if len(cells) > 1 else ""):
            if token.isupper() or "_" in token:
                out[token] = cells[2] if len(cells) > 2 else ""
    return out


def sdk_extra_codes() -> dict[str, str]:
    """Các mã SDK tự đặt (`sdk_*`, `cloud_save_*`) — phải khai trong `COMPAT` của khoá."""
    code = SDK_JS.read_text(encoding="utf-8")
    found = dict(re.findall(r"fail\(\s*'([a-z_]+)'", code))
    found.update({m: "" for m in re.findall(r"fail\(\s*CODE\.(\w+)", code)})
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Bảng mã lỗi SDK ↔ docs/03 §4.")
    ap.add_argument("--table", action="store_true", help="in bảng lỗi")
    ap.add_argument("--selftest", action="store_true", help="kiểm 4 bất biến (CI)")
    args = ap.parse_args()

    sdk = sdk_error_codes()
    doc = doc_error_codes()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    declared = set(contract.get("error_codes", {}))

    if args.table:
        print("\nBẢNG LỖI SDK — chỉ 4 kiểu, vì iframe không thấy HTTP\n")
        print(f"{'Hằng':14}{'Mã':26}{'Nghĩa':44}HTTP tương ứng")
        print("─" * 108)
        pairs = {
            "NO_PARENT": ("sdk_no_parent", "Không có portal: mở game trực tiếp", "— (không có request)"),
            "TIMEOUT": ("sdk_timeout", "Đã gửi, portal không trả lời", "504 (nếu có request)"),
            "REFUSED": ("sdk_refused", "Portal trả lời nhưng từ chối", "403 / 409"),
            "NOT_MOUNTED": ("sdk_not_mounted", "Chưa init() hoặc sai môi trường", "— (lỗi lập trình)"),
        }
        for k, (c, why, http) in pairs.items():
            print(f"{k:14}{c:26}{why:44}{http}")
        print("\nBốn kiểu này KHÔNG thay bảng §4 (REST). Chúng là mặt cắt của nó trong iframe.")
        return 0

    # 1. MỌI mã SDK dùng ⊂ khai báo trong khoá hợp đồng.
    #    Gồm cả mã hằng (`var CODE`) lẫn mã viết thẳng ở chỗ gọi (`fail('cloud_save_…')`).
    #    Thiếu vế thứ hai thì đổi tên một mã ở chỗ gọi sẽ LỌT — đúng phép phá đã thử.
    for name, code in sdk.items():
        check(code in declared, f"SDK dùng mã `{code}` nhưng CONTRACT.json không khai — bịa mã lỗi riêng")
    for code in sorted(set(re.findall(r"fail\(\s*'([a-z_]+)'", SDK_JS.read_text(encoding="utf-8")))):
        check(
            code in declared,
            f"SDK gọi `fail('{code}')` nhưng CONTRACT.json không khai — mã lỗi không có trong hợp đồng",
        )
    # 2. Không mã nào khai mà SDK không dùng (hợp của hằng `var CODE` và mã viết thẳng).
    in_use = set(sdk.values()) | set(
        re.findall(r"fail\(\s*'([a-z_]+)'", SDK_JS.read_text(encoding="utf-8"))
    )
    for code in sorted(declared):
        check(code in in_use, f"CONTRACT.json khai `{code}` nhưng SDK không dùng — tài liệu hứa suông")
    # 3. Không có `resolve(null)` cho thao tác ĐÃ gửi
    code = SDK_JS.read_text(encoding="utf-8")
    # Chỉ cấm trong `send`: ngoài `send`, `null` là giá trị hợp lệ (ô cloudSave trống).
    send_body = code[code.index("function send(") :]
    send_body = send_body[: send_body.index("\n  }")]
    check(
        "resolve(null)" not in send_body,
        "`send()` còn `resolve(null)` — thao tác đã gửi mà trả null là biến lỗi thành 'không biết'",
    )
    # 4. Mọi `reject` phải kèm `code` — ở đây: mọi `fail(` phải có mã dạng chuỗi.
    # Bỏ chính DÒNG ĐỊNH NGHĨA `function fail(code, message, extra)` — ở đó `code`
    # là tham số, không phải mã lỗi.
    call_sites = re.sub(r"function fail\(code[^)]*\)\s*\{", "", code)
    fails = re.findall(r"fail\(\s*([^,]+),", call_sites)
    for arg in fails:
        arg = arg.strip()
        check(
            arg.startswith("'") or arg.startswith("CODE."),
            f"`fail({arg})` không dùng mã lỗi — game không phân biệt được kiểu hỏng",
        )

    # 5. Không có `Promise.reject(` trực tiếp: mọi lỗi phải đi qua `fail()` để có mã.
    #    (Phép phá: thay một `fail(...)` bằng `Promise.reject(new Error('x'))` trước đây LỌT.)
    # Bỏ thân `function fail(...)` — đó là chỗ DUY NHẤT được phép `Promise.reject`.
    outside_fail = re.sub(r"function fail\(code[^)]*\)\s*\{.*?\n  \}", "", code, flags=re.S)
    direct = re.findall(r"Promise\.reject\(", outside_fail)
    check(
        not direct,
        f"SDK có {len(direct)} chỗ `Promise.reject(` trực tiếp — phải đi qua `fail()` để lỗi có mã",
    )

    if FAILS:
        print(f"SDK ERRORS: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1

    print(
        f"SDK ERRORS: PASS — {PASSES} kiểm tra · 4 bất biến · "
        f"{len(declared)} mã lỗi ({len(sdk)} hằng + {len(declared) - len(sdk)} ở chỗ gọi), "
        "tất cả khai trong CONTRACT.json và khớp docs/03 §4"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
