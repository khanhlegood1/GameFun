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


def inv_role_holder_is_not_a_signature(items: list[dict], people: dict) -> None:
    """(7) Biết AI GIỮ MỘT VAI không có nghĩa ADR đó đã được ký.

    PO xác nhận "tôi là Lê Xuân Khánh, PO" — điều đó trả lời câu hỏi *ai giữ vai
    `Project Owner`*. Nó KHÔNG trả lời *ADR-0017 (`Tech Lead On-chain`) đã được ký
    chưa*. Hai câu hỏi khác nhau, và gộp chúng là cách một dòng
    `Principal Architect *(chờ ký)*` biến thành một chữ ký không tồn tại.

    Rủi ro cụ thể mà bất biến này chặn: ai đó (kể cả agent) điền `ROLE_HOLDER`
    cho `Principal Architect` rồi tưởng đã sửa xong 18 ADR. Bảng tra cứu đó chỉ
    nói ai giữ vai; chữ ký chỉ đổi khi **chính tệp ADR** đổi.
    """
    for i in items:
        if i.get("state") == "missing":
            continue
        holder = i.get("role_holder") or {}
        if not holder:
            continue
        signed = i.get("signature") == "named"
        # Tên đó có THẬT trong tệp không? Phải so với `decider` — nguyên văn đọc từ
        # tệp — chứ không phải với `decider_person`, vì chính trường đó là thứ có
        # thể bị điền từ ROLE_HOLDER. (Lần đầu tôi so với `decider_person` nên phép
        # phá P6 vẫn xanh: kẻ phá đặt cả hai trường.)
        name_in_file = bool(holder.get("person")) and holder["person"] in (i.get("decider") or "")
        check(not signed or name_in_file,
              f"{i.get('id')}: khai đã ký nhưng tên người ký KHÔNG có trong tệp — `Người quyết` "
              f"là {i.get('decider')!r}. Biết ai giữ vai {holder.get('role')!r} "
              f"({holder.get('person')}) không làm ADR này được ký")
        # Chính điều nguy hiểm: `role_holder` có mặt ⇒ phải có căn cứ.
        check(bool((holder.get("basis") or "").strip()),
              f"{i.get('id')}: `role_holder` cho vai {holder.get('role')!r} thiếu `basis` — "
              "một khẳng định về con người phải có nguồn")


def inv_signature_is_a_person(items: list[dict], people: dict) -> None:
    """(6) Người quyết phải là NGƯỜI CÓ TÊN, không phải một chức danh.

    `README.md` của thư mục ADR tuyên bố: *"Mỗi ADR phải có người quyết có tên.
    ADR chưa ký = `Proposed` và **không** được dùng để justify code đã merge."*

    Nhưng 17/35 tệp ghi `Người quyết: Principal Architect *(chờ ký)*` — một **vai**,
    không phải một con người, và nó không phân biệt được với một chỗ trống. Kiểm
    35 dòng bằng mắt là việc không ai làm; kiểm bằng máy thì rẻ.

    Bất biến này KHÔNG bắt phải ký. Nó chỉ bắt **không được coi là đã ký** khi
    người ký không có tên — nếu không, `Accepted (chờ ký)` biến thành `accepted`
    và portal tuyên bố một chữ ký chưa tồn tại.
    """
    for i in items:
        if i.get("state") == "missing":
            continue
        decider = (i.get("decider") or "").strip()
        # `decider_person` do generator suy ra từ chính tệp ADR (bảng vai → người
        # khai tường minh trong gen_portal_data.py). Rỗng = chưa có ai.
        has_person = bool((i.get("decider_person") or "").strip())
        # Cái được kiểm là `display_state` — thứ THẬT SỰ hiện trên portal — chứ
        # không phải `state` (nguyên văn trong tệp). Tệp lịch sử ghi `Accepted`
        # thì để nguyên; portal không được lặp lại lời đó khi chưa có người ký.
        check(i.get("display_state") != "accepted" or has_person,
              f"{i.get('id')}: `Người quyết` = {decider!r} — không có tên người, "
              "nhưng portal hiển thị 'accepted' (README: ADR chưa ký không được dùng để biện minh)")
        check(bool(i.get("display_state")),
              f"{i.get('id')}: thiếu `display_state` — portal không có trạng thái nào để hiện")
        check(i.get("needs_signature") is True or has_person,
              f"{i.get('id')}: `Người quyết` = {decider!r} không có tên người nhưng `needs_signature` = False")


def inv_task_numbers_match_data(items: list[dict], data: dict) -> None:
    """(8) Con số trong TIÊU ĐỀ một việc phải khớp dữ liệu thật.

    P13 tiêu đề ghi "17 ADR đang do chức danh ký" trong khi thực tế là 18 — con
    số đó đúng vào lúc viết và sai ngay khi ADR-0008 vào repo. Không cổng nào
    đọc tiêu đề, nên nó đã lọt qua PR, CI, và lên trang thật.

    Đây là họ lỗi mà `docs/47` §3.3 vừa ghi: **một con số gõ tay thì không tự
    đúng lại**. Việc P13 là thứ PO đọc để biết phải làm gì; nó sai một đơn vị
    nghĩa là PO không biết còn bao nhiêu chữ ký phải xin.
    """
    import re
    role_only = [i for i in items if i.get("signature") == "role_only"]
    counts = {}
    for i in role_only:
        who = (i.get("decider") or "").strip()
        counts[who] = counts.get(who, 0) + 1
    acts = {a.get("id"): a for a in data.get("actions") or []}
    p13 = acts.get("P13")
    if not p13:
        return
    title = p13.get("title") or ""
    m = re.search(r"(\d+)\s+ADR", title)
    check(bool(m), "P13 tiêu đề không nêu số ADR — không kiểm được con số")
    if m:
        check(int(m.group(1)) == len(role_only),
              f"P13 nói {m.group(1)} ADR do chức danh ký nhưng dữ liệu có {len(role_only)} "
              f"({', '.join(f'{v}×{k}' for k, v in sorted(counts.items(), key=lambda x: -x[1]))})")
    # Từng vai cũng phải khớp: "Principal Architect ×15" là một con số kiểm được.
    for role, n in counts.items():
        base = role.split("(")[0].strip()
        mk = re.search(re.escape(base) + r"\s*×(\d+)", title)
        if base.lower().startswith("principal architect") and mk:
            check(int(mk.group(1)) == n,
                  f"P13 nói '{base} ×{mk.group(1)}' nhưng có {n} tệp ghi đúng vai đó")


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
        inv_signature_is_a_person(d["adr"]["items"], d.get("people") or {})
        inv_role_holder_is_not_a_signature(d["adr"]["items"], d.get("people") or {})
        inv_task_numbers_match_data(d["adr"]["items"], d)
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
        # Nhắm dòng ĐANG CÓ TỆP, không nhắm dòng `missing`: sau khi đủ 43/43 tệp thì
        # không còn dòng `missing` nào, và phép thử cũ sẽ xanh vì không làm gì cả
        # — đúng lỗi "cổng chạy trần" của docs/40.
        for i in d["adr"]["items"]:
            if i.get("file") and i["state"] != "missing":
                i["file"] = "ADR-9999-khong-co.md"
                return
        raise AssertionError("corpus không còn dòng nào có tệp — P4 vô nghĩa")

    run(drop_action, "P1 bỏ mất một việc khỏi portal → đỏ", True)
    run(bump_owner, "P2 đổi người sở hữu trong portal → đỏ", True)
    run(fake_signature, "P3 ADR chờ ký hiện ra như đã ký → đỏ", True)
    def phantom_signature(d):
        # ADR do một CHỨC DANH ký, được khai là đã nhận ⇒ tuyên bố một chữ ký
        # không tồn tại. Đây đúng là trạng thái của ADR-0001..0014.
        for i in d["adr"]["items"]:
            if i["file"]:
                i.update(state="accepted", needs_signature=False,
                         decider="Principal Architect *(chờ ký)*")
                return

    run(phantom_signature, "P5 ADR do chức danh ký nhưng khai là đã nhận → đỏ", True)
    def role_holder_used_as_signature(d):
        # PO xác nhận "tôi là PO". Ai đó điền ROLE_HOLDER cho `Principal Architect`
        # rồi khai 18 ADR đã được ký — chữ ký mà không tệp nào chứa tên.
        for i in d["adr"]["items"]:
            if i["signature"] == "role_only":
                i.update(role_holder={"role": "Principal Architect",
                                      "person": "Lê Xuân Khánh", "basis": "PO xác nhận"},
                         decider_person="Lê Xuân Khánh", signature="named",
                         needs_signature=False)
                return
        raise AssertionError("corpus không còn dòng 'role_only' — P6 vô nghĩa")

    run(role_holder_used_as_signature,
        "P6 điền ROLE_HOLDER rồi coi 18 ADR là đã ký → đỏ", True)

    def role_holder_without_basis(d):
        for i in d["adr"]["items"]:
            if i["signature"] == "role_only":
                i.update(role_holder={"role": "Principal Architect",
                                      "person": "", "basis": ""})
                return

    run(role_holder_without_basis,
        "P7 khai 'vai này có người' mà không có căn cứ → đỏ", True)
    run(phantom_file, "P4 ADR trỏ tới tệp không tồn tại → đỏ", True)
    run(lambda d: None, "P0 đối chứng: data.json gốc → xanh", False)

    ok = sum(1 for _, o in cases if o)
    for label, o in cases:
        print(f"  {'✓' if o else '✗'} {label}")
    if ok != len(cases):
        print(f"PORTAL SELFTEST: FAIL — {ok}/{len(cases)}")
        return 1
    print(f"PORTAL SELFTEST: PASS — {len(cases)}/{len(cases)} (1 đối chứng + 7 phép phá)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="portal/ phải khớp repo, và không được ký khống.")
    ap.add_argument("--selftest", action="store_true", help="7 phép phá + đối chứng (CI)")
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

    # Đếm bất biến bằng cách CHẠY chúng, không đếm bằng số gõ tay: con số "6 bất
    # biến" từng đứng im khi tôi thêm bất biến thứ 7 (docs/47 §3). Một con số tự
    # khai thì không kiểm được gì.
    INVARIANTS = [
        inv_matches_generator,
        lambda: inv_no_action_lost(data),
        lambda: inv_adr_files_exist(data["adr"]["items"]),
        lambda: inv_no_fake_signature(data["adr"]["items"]),
        lambda: inv_signature_is_a_person(data["adr"]["items"], data.get("people") or {}),
        lambda: inv_role_holder_is_not_a_signature(data["adr"]["items"], data.get("people") or {}),
        lambda: inv_task_numbers_match_data(data["adr"]["items"], data),
        inv_page_wiring,
    ]
    for inv in INVARIANTS:
        inv()

    if FAILS:
        print(f"PORTAL: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    c = data["adr"]["counts"]
    print(f"PORTAL: PASS — {PASSES} kiểm tra · {len(INVARIANTS)} bất biến · "
          f"{len(data['actions'])} việc · {c['total']} ADR ({c['on_disk']} có tệp, "
          f"{c['proposed']} chờ ký, {c['listed_but_absent']} thiếu tệp) · data.json == generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
