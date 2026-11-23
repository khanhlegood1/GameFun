#!/usr/bin/env python3
"""check_sdk_manifest.py — mỗi bản phát hành SDK có một **hồ sơ chứng cứ** đầy đủ.

Vì sao có file này (docs/32):
    `awesome-ai-sdks` là một **danh sách dạng văn xuôi**: `223` dòng, mỗi mục là một
    heading `## [Tên](link)` + một câu mô tả + khối `<details>` chứa link. **Không
    có cột giấy phép, không có cột phiên bản, không có cột ngày.**

    Đó không phải lỗi của một danh sách — nó là **giới hạn của định dạng văn xuôi**.
    Và Game9K đang có đúng giới hạn đó: `docs/28` ghi hash bề mặt `sha256:af63…`,
    `docs/29` ghi phiên bản `0.2.0`, `CONTRACT.json` ghi luật tương thích — **ba nơi,
    không nơi nào kiểm nơi nào.** Sửa `CONTRACT.json` lên `0.3` là hai tài liệu kia
    thành sai mà **không cổng nào đỏ**.

    File này biến `sdk/game-sdk/MANIFEST.json` thành **một dòng** của bảng đó, có cột:
    `name · version · surface_hash · license · built_from · compat · evidence`.
    Và mỗi cột phải khớp với thứ đã có, không phải chép lại lần hai.

Năm bất biến:

  1. **Hash bề mặt trong MANIFEST = hash tính từ `CONTRACT.json`.**
     Không chép tay: hash được tính lại mỗi lần chạy.
  2. **Version trong MANIFEST = `SDK_VERSION` trong mã = `MAJOR.MINOR` của khoá.**
  3. **Mọi tài liệu nhắc hash/phiên bản phải khớp MANIFEST.** Quét `docs/*.md`:
     nếu một tài liệu chứa `sha256:<12 hex>` hoặc `MAJOR.MINOR.x`, nó phải là giá trị
     hiện tại — nếu không, tài liệu đã lạc hậu so với SDK.
     Ngoại lệ **duy nhất**: một dòng có chữ `lịch sử` được coi là **ghi chép quá khứ**
     và được phép nêu giá trị cũ. Đây là ngoại lệ hẹp, có chủ đích: tài liệu sống phải
     kể được lịch sử bump, nhưng không được **trình bày giá trị cũ như giá trị hiện tại**.
  4. **Giấy phép phải khai và phải cụ thể.** `license` không được rỗng và không được
     là `NOASSERTION`/`Other` — đúng lỗi của hai repo `awesome-*` (docs/31 §1, docs/32 §1).
  5. **Có `evidence` trỏ tới cổng đã kiểm.** Mỗi trường của MANIFEST phải nêu **lệnh**
     tái lập được nó. Một trường không có lệnh là một trường không ai kiểm.

Bốn chế độ:

    python3 scripts/check_sdk_manifest.py            # 5 bất biến
    python3 scripts/check_sdk_manifest.py --row      # in MANIFEST như MỘT DÒNG bảng
    python3 scripts/check_sdk_manifest.py --compare  # so định dạng Game9K ↔ awesome-ai-sdks
    python3 scripts/check_sdk_manifest.py --selftest # CI

Chỉ thư viện chuẩn, không mạng.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SDK = ROOT / "sdk" / "game-sdk"
CONTRACT = SDK / "CONTRACT.json"
MANIFEST = SDK / "MANIFEST.json"
SDK_JS = SDK / "game9k-sdk.js"
DOCS = ROOT / "docs"

BAD_LICENSES = {"", "none", "noassertion", "other", "unknown", "see license"}

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def surface_hash(contract: dict) -> str:
    canon = json.dumps(
        {"major": contract["major"], "minor": contract["minor"], "functions": contract["functions"]},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def sdk_version() -> str | None:
    m = re.search(r"var SDK_VERSION = '([^']+)'", SDK_JS.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Hồ sơ chứng cứ cho bản phát hành SDK.")
    ap.add_argument("--row", action="store_true", help="in MANIFEST thành một dòng bảng")
    ap.add_argument("--compare", action="store_true", help="so định dạng với awesome-ai-sdks")
    ap.add_argument("--selftest", action="store_true", help="kiểm 5 bất biến (CI)")
    args = ap.parse_args()

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    want_hash = surface_hash(contract)
    want_version = f"{contract['major']}.{contract['minor']}.0"

    if args.compare:
        print("\nHAI ĐỊNH DẠNG — cùng nội dung, khác khả năng kiểm\n")
        rows = [
            ("Đơn vị", "một heading `## [Tên]`", "một dòng `MANIFEST.json`"),
            ("Số mục", "11 mục trong `223` dòng", "1 gói: `@game9k/game-sdk`"),
            ("Giấy phép", "**không có cột**", "`license` bắt buộc, `NOASSERTION` bị từ chối"),
            ("Phiên bản", "**không có cột**", "`version` = `SDK_VERSION` = khoá"),
            ("Ngày", "**không có cột**", "`built_from` = commit"),
            ("Bề mặt", "**không mô tả**", "`surface_hash` tính lại mỗi lần chạy"),
            ("Cách kiểm", "đọc bằng mắt", "`check_sdk_manifest.py` (5 bất biến)"),
        ]
        w = (14, 34, 56)
        print(f"{rows[0][0]:{w[0]}}{rows[0][1]:{w[1]}}{rows[0][2]}")
        print("─" * sum(w))
        for r in rows[1:]:
            print(f"{r[0]:{w[0]}}{r[1]:{w[1]}}{r[2]}")
        print(
            "\nDanh sách văn xuôi KHÔNG sai — nó đúng cho mục đích của nó (khám phá).\n"
            "Nhưng nó không trả lời được 'bản tôi đang dùng là bản nào', và đó là câu\n"
            "mà một studio hỏi trước khi `import`."
        )
        return 0

    if not MANIFEST.exists():
        print(f"SDK MANIFEST: FAIL — thiếu {MANIFEST.relative_to(ROOT)}")
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if args.row:
        print("\nMỘT DÒNG CỦA BẢNG — cùng dữ liệu, kiểm được\n")
        print(f"name           {manifest['name']}")
        print(f"version        {manifest['version']}")
        print(f"surface_hash   sha256:{manifest['surface_hash']}")
        print(f"license        {manifest['license']}")
        print(f"built_from     {manifest['built_from']}")
        print(f"compat         {manifest['compat_removal']} (MAJOR {manifest['major']})")
        print(f"evidence       {len(manifest['evidence'])} lệnh tái lập")
        for k, v in manifest["evidence"].items():
            print(f"               · {k}: `{v}`")
        return 0

    # 1. Hash bề mặt — TÍNH LẠI, không tin giá trị trong tệp.
    check(
        manifest.get("surface_hash") == want_hash,
        f"MANIFEST.surface_hash `{manifest.get('surface_hash')}` ≠ hash tính từ CONTRACT.json "
        f"`{want_hash}` — hồ sơ đã lạc hậu",
    )

    # 2. Version ba nơi phải trùng.
    v = sdk_version()
    check(v == want_version, f"SDK_VERSION `{v}` ≠ `{want_version}` (từ khoá)")
    check(
        manifest.get("version") == want_version,
        f"MANIFEST.version `{manifest.get('version')}` ≠ `{want_version}`",
    )

    # 3. Tài liệu nhắc hash/phiên bản phải khớp.
    hash_hits, version_hits = 0, 0
    seen: set[tuple[str, str]] = set()          # báo một lần cho mỗi (tệp, giá trị)
    for path in sorted(DOCS.glob("*.md")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "lịch sử" in line.lower():
                continue                          # ghi chép quá khứ, được phép
            for h in re.findall(r"sha256:([0-9a-f]{8,64})", line):
                hash_hits += 1
                if (path.name, h) in seen:
                    continue
                seen.add((path.name, h))
                check(
                    h == want_hash,
                    f"{path.name}:{lineno} ghi `sha256:{h}` nhưng hash hiện tại là `{want_hash}` "
                    "— tài liệu lạc hậu so với SDK",
                )
            for mm in re.findall(r"(?<![\d.])(\d+\.\d+)\.x(?![\d.])", line):
                version_hits += 1
                key = (path.name, mm + ".x")
                if key in seen:
                    continue
                seen.add(key)
                check(
                    mm == f"{contract['major']}.{contract['minor']}",
                    f"{path.name}:{lineno} ghi khoá `{mm}.x` nhưng khoá hiện tại là "
                    f"`{contract['major']}.{contract['minor']}.x`",
                )
    check(
        hash_hits >= 1 and version_hits >= 1,
        "không tìm thấy hash/phiên bản nào trong docs/ — phép quét vô nghĩa",
    )

    # 4. Giấy phép cụ thể.
    lic = str(manifest.get("license", ""))
    check(
        lic.strip().lower() not in BAD_LICENSES,
        f"MANIFEST.license `{lic}` không cụ thể — `NOASSERTION`/`Other` là CHƯA có quyền rõ ràng "
        "(docs/31 §1, docs/32 §1)",
    )

    # 5. Mỗi trường then chốt có một lệnh tái lập.
    ev = manifest.get("evidence", {})
    for field in ("version", "surface_hash", "surface", "budget", "errors"):
        check(field in ev, f"MANIFEST.evidence thiếu `{field}` — trường đó không ai kiểm")

    if FAILS:
        print(f"SDK MANIFEST: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1

    print(
        f"SDK MANIFEST: PASS — {PASSES} kiểm tra · 5 bất biến · "
        f"{manifest['name']} {manifest['version']} · sha256:{want_hash} · "
        f"{hash_hits} chỗ ghi hash + {version_hits} chỗ ghi phiên bản trong docs/ đều khớp"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
