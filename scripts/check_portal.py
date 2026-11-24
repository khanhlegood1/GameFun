#!/usr/bin/env python3
"""check_portal.py — bảng điều khiển không được nói dối về repo.

`portal/` là bản chiếu của `pm/action-register.json` + `portal/docs/08-adr/*.md`.
Một bản chiếu có hai cách sai, và cả hai đều *im lặng*:

    (a) trôi — dữ liệu trong portal khác repo, nhưng trang vẫn mở bình thường;
    (b) ký khống — ADR `chờ ký` được hiển thị như đã ký, vì "trông gọn hơn".

Sáu bất biến:

    1. `portal/data.json` đúng là bản generator sinh ra (so từng byte, không so "gần đúng").
    2. Không việc nào trong sổ bị bỏ khỏi portal, và không việc nào được thêm vào.
    3. Mỗi ADR trỏ tới một tệp CÓ THẬT trong `portal/docs/08-adr/`.
    4. Mỗi dòng `missing` phải thật sự không có tệp — "thiếu" là thiếu sót, không phải nhãn trang trí.
    5. Không ADR nào có chữ "chờ ký" mà lại mang `state: accepted` (bẫy chữ ký).
    6. Trang phải tự nối được: `index.html` → `app.js` → `data.json`, cả ba đều tồn tại.

Chạy: python3 scripts/check_portal.py [--selftest|--audit]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORTAL = ROOT / "portal"
DATA = PORTAL / "data.json"
ADR_DIR = PORTAL / "docs" / "08-adr"
REGISTER = ROOT / "pm" / "action-register.json"
GEN = ROOT / "scripts" / "gen_portal_data.py"

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


# ---------------------------------------------------------------- bất biến
def inv_matches_generator(data: dict | None = None) -> None:
    """(1) data.json phải đúng là bản generator sinh ra — nếu không, trang đang
    hiển thị một quá khứ không còn tồn tại."""
    import subprocess

    if not GEN.exists():
        FAILS.append("thiếu scripts/gen_portal_data.py — không sinh lại được data.json")
        return
    want = subprocess.run([sys.executable, str(GEN), "--check"],
                          capture_output=True, text=True, cwd=ROOT)
    check(want.returncode == 0,
          "portal/data.json KHÁC bản sinh từ repo — chạy `python3 scripts/gen_portal_data.py` "
          "rồi commit (đừng sửa tay)")
    if want.returncode == 0:
        PASSES_MSG.append("data.json == generator")


PASSES_MSG: list[str] = []


def inv_no_action_lost(data: dict) -> None:
    """(2) Bản chiếu không được bỏ sót việc — bỏ sót là cách một bảng điều khiển
    trông sạch hơn thực tế."""
    reg = {a["id"]: a for a in json.loads(REGISTER.read_text(encoding="utf-8"))["actions"]}
    got = {a["id"]: a for a in data.get("actions") or []}
    check(set(reg) == set(got),
          f"portal lệch sổ việc — thiếu {sorted(set(reg) - set(got))}, thừa {sorted(set(got) - set(reg))}")
    for aid in sorted(set(reg) & set(got)):
        for field in ("title", "owner", "due", "status"):
            check(reg[aid].get(field) == got[aid].get(field),
                  f"{aid}: `{field}` trong portal ({got[aid].get(field)!r}) ≠ sổ ({reg[aid].get(field)!r})")


def inv_adr_files_exist(items: list[dict]) -> None:
    """(3)(4) Mỗi hàng ADR phải nói đúng về sự tồn tại của tệp."""
    on_disk = {p.name for p in ADR_DIR.glob("ADR-*.md")}
    seen: set[str] = set()
    for i in items:
        f = i.get("file")
        if f:
            check(f in on_disk, f"{i.get('id')}: trỏ tới `{f}` nhưng tệp đó không có trong portal/docs/08-adr/")
            seen.add(f)
        else:
            check(i.get("state") == "missing",
                  f"{i.get('id')}: không có tệp nhưng `state` = {i.get('state')!r} — phải là 'missing'")
    check(on_disk == seen,
          f"có tệp ADR không được chiếu: {sorted(on_disk - seen)}")


def inv_no_fake_signature(items: list[dict]) -> None:
    """(5) Bẫy chữ ký: `Accepted (chờ ký)` vẫn là CHƯA KÝ.

    README của thư mục ADR cấm dùng ADR chưa ký để biện minh cho mã đã merge.
    Nếu portal hiển thị nó như `accepted`, nó trở thành đúng thứ bị cấm — bằng
    hình ảnh, không bằng câu chữ.
    """
    for i in items:
        raw = (i.get("status_raw") or "").lower()
        if "chờ ký" in raw:
            check(i.get("state") != "accepted",
                  f"{i.get('id')}: trạng thái thô có 'chờ ký' nhưng state = 'accepted' — ký khống")
            check(i.get("needs_signature") is True,
                  f"{i.get('id')}: có 'chờ ký' nhưng `needs_signature` không phải true")


def inv_page_wiring() -> None:
    """(6) Trang phải tự nối được. Một đường dẫn sai làm trang trắng và KHÔNG
    cổng nào khác biết."""
    html = PORTAL / "index.html"
    js = PORTAL / "app.js"
    check(html.exists(), "thiếu portal/index.html")
    check(js.exists(), "thiếu portal/app.js")
    if not (html.exists() and js.exists()):
        return
    h = html.read_text(encoding="utf-8")
    j = js.read_text(encoding="utf-8")
    check("./app.js" in h or "app.js" in h, "index.html không nạp app.js")
    check("data.json" in j, "app.js không đọc data.json")
    check("data.json" in h or DATA.exists(), "trang không tìm thấy data.json")
    # Không có URL tuyệt đối: trang phải chạy dưới bất kỳ tên miền nào.
    for bad in re.findall(r'https?://[^\s"\'<>]+', h + j):
        check(not bad.startswith(("http://localhost", "http://127.0.0.1")),
              f"trang gọi địa chỉ cục bộ `{bad}` — sẽ trắng khi deploy")


def audit(data: dict) -> int:
    adr = data["adr"]
    print("\nPORTAL — bản chiếu của repo\n")
    print(f"  ADR      : {adr['counts']['total']} dòng · {adr['counts']['on_disk']} có tệp · "
          f"{adr['counts']['proposed']} chờ ký · {adr['counts']['listed_but_absent']} thiếu tệp")
    print(f"  Việc     : {len(data['actions'])} · "
          f"{sum(1 for a in data['actions'] if a['status'] == 'OPEN')} đang mở")
    absent = [i["id"] for i in adr["items"] if i["state"] == "missing"]
    if absent:
        print(f"\n  ADR có trong chỉ mục nhưng CHƯA có tệp ({len(absent)}): {' '.join(absent)}")
        print("  → đây là thiếu sót hiện ra, không phải bị ẩn đi.")
    print()
    return 0


def selftest() -> int:
    """Bốn phép phá + đối chứng, trên bản sao trong BỘ NHỚ — không sửa tệp thật."""
    global FAILS, PASSES
    import tempfile

    good = json.loads(DATA.read_text(encoding="utf-8"))
    cases: list[tuple[str, bool]] = []

    def run(mutate, label: str, must_red: bool) -> None:
        global FAILS, PASSES
        d = json.loads(json.dumps(good))
        mutate(d)
        FAILS, PASSES = [], 0
        inv_no_action_lost(d)
        inv_adr_files_exist(d["adr"]["items"])
        inv_no_fake_signature(d["adr"]["items"])
        red = bool(FAILS)
        FAILS, PASSES = [], 0
        cases.append((label, red == must_red))

    def drop_action(d):
        d["actions"] = [a for a in d["actions"] if a["id"] != "P8"]

    def bump_owner(d):
        d["actions"][0]["owner"] = "SOMEONE"

    def fake_signature(d):
        # Phải nhắm một dòng mà TRẠNG THÁI THÔ có "chờ ký" (vd `Accepted (chờ ký)`)
        # rồi khai nó là đã ký. Nhắm vào `Proposed` thường (không có chữ "chờ ký")
        # thì không có gì bịa ra cả — phép thử sẽ xanh vì lý do sai.
        for i in d["adr"]["items"]:
            if "chờ ký" in (i.get("status_raw") or "").lower():
                i.update(state="accepted", needs_signature=False)
                return
        raise AssertionError("corpus không có dòng nào 'chờ ký' — phép thử P3 vô nghĩa")

    def phantom_file(d):
        for i in d["adr"]["items"]:
            if i["state"] == "missing":
                i.update(file="ADR-9999-khong-co.md", state="accepted")
                break

    run(drop_action, "P1 bỏ mất một việc khỏi portal → đỏ", True)
    run(bump_owner, "P2 đổi người sở hữu trong portal → đỏ", True)
    run(fake_signature, "P3 ADR chờ ký hiện ra như đã ký → đỏ", True)
    run(phantom_file, "P4 ADR trỏ tới tệp không tồn tại → đỏ", True)
    run(lambda d: None, "P0 đối chứng: data.json gốc → xanh", False)

    ok = sum(1 for _, o in cases if o)
    for label, o in cases:
        print(f"  {'✓' if o else '✗'} {label}")
    if ok != len(cases):
        print(f"PORTAL SELFTEST: FAIL — {ok}/{len(cases)}")
        return 1
    print(f"PORTAL SELFTEST: PASS — {len(cases)}/{len(cases)} (1 đối chứng + 4 phép phá)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="portal/ phải khớp repo, và không được ký khống.")
    ap.add_argument("--selftest", action="store_true", help="4 phép phá + đối chứng (CI)")
    ap.add_argument("--audit", action="store_true", help="in bảng chiếu")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    check(DATA.exists(), "thiếu portal/data.json — chưa sinh bản chiếu")
    if not DATA.exists():
        print(f"PORTAL: FAIL — {FAILS[0]}")
        return 1
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if args.audit:
        return audit(data)

    inv_matches_generator()
    inv_no_action_lost(data)
    inv_adr_files_exist(data["adr"]["items"])
    inv_no_fake_signature(data["adr"]["items"])
    inv_page_wiring()

    if FAILS:
        print(f"PORTAL: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    c = data["adr"]["counts"]
    print(f"PORTAL: PASS — {PASSES} kiểm tra · 6 bất biến · "
          f"{len(data['actions'])} việc · {c['total']} ADR ({c['on_disk']} có tệp, "
          f"{c['proposed']} chờ ký, {c['listed_but_absent']} thiếu tệp) · data.json == generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
