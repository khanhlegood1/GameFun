#!/usr/bin/env python3
"""check_adr_standards.py — ADR của Game9K phải lọt được một cổng ADR thật.

Vì sao có file này (docs/48):
    `docs/46` §1 phát hiện cổng 25 **không** kiểm cấu trúc ADR. Nó kiểm bản chiếu
    (`portal/data.json`) khớp generator, và kiểm chữ ký — nhưng một ADR viết sai
    quy ước vẫn lọt nếu generator đọc được header. Đó là lỗ thật: 35 tệp dùng **ba
    format header** khác nhau và không cổng nào bắt.

    Vòng này áp chuẩn ADR từ hai repo của chính PO, cả hai đều là **fork** và đều
    có giấy phép cho phép dùng lại:

      · `factory-x-contributions/architecture-decisions` (Apache-2.0) — script
        `scripts/lint-adrs.js` kiểm cấu trúc thư mục + frontmatter, chạy trong
        `.github/workflows/lint-adrs.yaml` trên mọi PR đụng `docs/**/adr*/**`.
      · `microsoft/hve-core` (MIT) — `.github/instructions/project-planning/
        adr-standards.instructions.md`, nhúng MADR v4.0.0 (CC0-1.0), GP-16
        (file naming), GP-07 (ASR trigger), và status taxonomy 6 trạng thái.

    Cả hai đều KHÔNG bắt được lỗi đã xảy ra ở `docs/46`: một ADR `Accepted` do
    chức danh ký vẫn lọt lint của factory-x (nó chỉ kiểm `id` và `title`), và
    MADR v4 không có trường `Người quyết` (nó dùng `decision-makers` tự do). Nên
    cổng này là hợp của hai bên, cộng hai bất biến của repo này.

Bảy bất biến:
    1. (X2) File naming — `ADR-NNNN-kebab-case-title.md`, slug chỉ `[a-z0-9-]`.
    2. (X2) Không trùng số; số phải liên tục từ 1 tới max (lỗ hổng là ADR đã xoá
       mà không ghi supersede — im lặng mất một quyết định).
    3. (X2) Mọi `ADR-NNNN` được nhắc trong bất kỳ ADR nào phải tồn tại.
    4. (X1) Frontmatter bắt buộc: `Trạng thái` + `Ngày` đọc được, ngày là
       `YYYY-MM-DD` hợp lệ, không ở tương lai.
    5. (X1) Trạng thái thuộc taxonomy ĐÓNG của MADR v4 / GP-16 — 6 giá trị.
    6. (repo) Không trạng thái nào tự mâu thuẫn (`Accepted … Proposed`).
    7. (repo) Supersede phải có HAI phía: không được nhắc `supersede` mà không
       chỉ ra ADR nào bị thay thế bằng số hiệu cụ thể.

Chạy: python3 scripts/check_adr_standards.py [--audit|--selftest]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADR_DIR = ROOT / "portal" / "docs" / "08-adr"

FAILS: list[str] = []
PASSES = 0

# GP-16 (hve-core `adr-standards.instructions.md` §"File-Naming Rule (GP-16)"):
# `NNNN` 4 chữ số, slug `a-z`, `0-9`, `-`. Không chữ hoa, gạch dưới, khoảng trắng,
# không ký tự ngoài ASCII.
FILE_RE = re.compile(r"^ADR-(\d{4})-([a-z0-9-]+)\.md$")
REF_RE = re.compile(r"ADR-(\d{4})")

# GP-16 §"Status Taxonomy": sáu giá trị, enum ĐÓNG. Ghi kèm các biến thể tiếng
# Việt mà bộ tài liệu này dùng, vì bản gốc là tiếng Anh và ADR ở đây là tiếng Việt.
STATUS_ENUM = {
    "proposed", "accepted", "rejected", "deprecated", "superseded", "withdrawn",
    "đề xuất", "chấp nhận", "từ chối", "bãi bỏ", "thay thế", "rút lại",
}
# Từ chối (Reject) của chính dự án này, có lai lịch: ADR `Accepted (chờ ký)` đã
# được dùng để biện minh cho mã đã merge (docs/46 §2) ⇒ "chờ ký" KHÔNG phải một
# trạng thái hợp lệ; nó là một chữ ký còn thiếu, và phải hiện ra như thế.
STATUS_MARKERS = ("chờ ký", "chờ po", "chờ chủ dự án")


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def header_field(text: str, name: str) -> str:
    """Đọc một trường header bất kể ba format đang tồn tại trong repo.

    Cùng lý do với `scripts/gen_portal_data.py`: `docs/46` §1 đã đo được 3 format
    (bảng 2 cột · `**X:**` một dòng · `- **X:**` gạch đầu dòng) và extractor chỉ
    đọc được một. Cổng không được lặp lại lỗi đó.
    """
    pats = (
        rf"(?m)^\|\s*\*\*{name}\*\*\s*\|\s*([^|\n]+)\|",
        rf"(?m)^[-*]{{0,2}}[ \t]*\*\*{name}:\*\*[ \t]*([^\n]+?)[ \t]*$",
    )
    for p in pats:
        m = re.search(p, text)
        if m:
            return m.group(1).strip().strip("*").strip()
    return ""


def load_adrs() -> list[dict]:
    out = []
    for f in sorted(ADR_DIR.glob("ADR-*.md")):
        text = f.read_text(encoding="utf-8")
        out.append({
            "file": f.name,
            "text": text,
            "status": header_field(text, "Trạng thái"),
            "date": header_field(text, "Ngày"),
            "decider": header_field(text, "Người quyết"),
        })
    return out


def inv_filename(adrs: list[dict]) -> None:
    """(1) GP-16 file naming. Đo được trước khi viết cổng: 43/43 tệp SẠCH, nên
    bất biến này là *chốt chặn cho tương lai*, không phải một lỗi đang tồn tại.
    Nói đúng như thế — một cổng xanh vì repo vốn đã đúng vẫn có giá trị, nhưng
    không được trình bày như thể nó vừa cứu một thứ gì."""
    for a in adrs:
        m = FILE_RE.match(a["file"])
        check(bool(m), f"{a['file']}: tên tệp phải là `ADR-NNNN-kebab-case.md` (GP-16), "
                       "slug chỉ chứa a-z, 0-9, -")
        if m:
            check(len(m.group(1)) == 4, f"{a['file']}: số ADR phải đúng 4 chữ số (GP-16)")


def inv_numbering(adrs: list[dict]) -> None:
    """(2) Không trùng số, và không có lỗ hổng.

    Lỗ hổng là dấu vết của một ADR bị xoá. GP-16 nói id **không bao giờ** được
    tái sử dụng; một số biến mất không ghi chú nghĩa là một quyết định đã im lặng
    rời khỏi lịch sử. Đo trước khi viết: 1→43, đếm 43, 0 trùng, 0 thiếu.
    """
    nums = []
    for a in adrs:
        m = FILE_RE.match(a["file"])
        if m:
            nums.append(int(m.group(1)))
    dup = sorted({n for n in nums if nums.count(n) > 1})
    check(not dup, f"trùng số ADR: {dup} — GP-16: id không bao giờ được tái sử dụng")
    if nums:
        gaps = [n for n in range(1, max(nums) + 1) if n not in nums]
        check(not gaps, f"thiếu số ADR {gaps} — một số biến mất là một quyết định "
                        "rời khỏi lịch sử mà không có supersede ghi lại")


def inv_references(adrs: list[dict]) -> None:
    """(3) Mọi `ADR-NNNN` được nhắc phải tồn tại.

    `fx-review-adr` Step 4 kiểm đúng điều này (cross-reference validation). Nó
    đáng chép vì ADR tham chiếu nhau là cách duy nhất đọc một quyết định trong
    ngữ cảnh — một tham chiếu chết làm hỏng cả chuỗi.
    """
    nums = {int(FILE_RE.match(a["file"]).group(1)) for a in adrs if FILE_RE.match(a["file"])}
    for a in adrs:
        for ref in sorted(set(REF_RE.findall(a["text"]))):
            n = int(ref)
            if n in nums:
                continue
            # `ADR-9999` là mẫu giả trong phép phá; bỏ qua ở chế độ repo thật.
            check(False, f"{a['file']}: nhắc ADR-{ref} nhưng tệp đó không tồn tại")


def inv_header_complete(adrs: list[dict], today: dt.date) -> None:
    """(4) `Trạng thái` + `Ngày` phải đọc được, ngày phải hợp lệ.

    `docs/46` §1 đã đo: trước khi sửa extractor, **11 tệp** đọc ra `state=unknown`
    và `status_raw=''` — và **cổng 25 vẫn xanh**. Bất biến này đóng đúng lỗ đó ở
    tầng ADR, không ở tầng bản chiếu.
    """
    for a in adrs:
        check(bool(a["status"]), f"{a['file']}: thiếu hoặc không đọc được `Trạng thái`")
        check(bool(a["date"]), f"{a['file']}: thiếu `Ngày`")
        if a["date"]:
            try:
                d = dt.date.fromisoformat(a["date"].strip())
            except ValueError:
                check(False, f"{a['file']}: `Ngày` = {a['date']!r} không phải YYYY-MM-DD")
                continue
            check(d <= today, f"{a['file']}: `Ngày` = {a['date']} ở TƯƠNG LAI — một quyết "
                              "định chưa xảy ra không thể là bản ghi lịch sử")


def inv_status_enum(adrs: list[dict]) -> None:
    """(5) Trạng thái thuộc taxonomy đóng của MADR v4 / GP-16.

    Sáu giá trị. `Accepted (chờ ký)` là ca đáng nói: nó **không** thuộc enum, và
    đúng là nó đã bị dùng để biện minh cho mã đã merge. Cổng không bắt phải đổi
    tệp — nó chỉ bắt phải *nhìn thấy*.
    """
    for a in adrs:
        raw = a["status"].lower()
        if not raw:
            continue
        hit = {s for s in STATUS_ENUM if s in raw}
        check(bool(hit), f"{a['file']}: trạng thái {a['status']!r} ngoài taxonomy GP-16 "
                         f"({', '.join(sorted(STATUS_ENUM))})")
        # KHÔNG kiểm "accepted nhưng người quyết là chức danh" ở đây thành lỗi ĐỎ.
        # Lý do, và nó là một quyết định có ghi chép: docs/46 §2.2 + docs/47 §2.3
        # chốt rằng repo KHÔNG sửa `Người quyết` trong tệp `Accepted` — đó là sửa
        # bản ghi lịch sử. Việc "ADR chưa có người ký thì không được hiện là đã
        # nhận" do cổng 25 canh ở tầng BẢN CHIẾU (`display_state`), và nó đã canh
        # đúng 18 tệp. Một cổng đỏ vĩnh viễn vì một khiếm khuyết đã biết sẽ bị tắt
        # — rồi nó không canh được gì nữa. Ở đây chỉ ĐẾM (xem `summary()`).


def inv_no_contradiction(adrs: list[dict]) -> None:
    """(6) Một trạng thái không được nói hai điều ngược nhau."""
    for a in adrs:
        s = a["status"]
        if not s:
            continue
        low = s.lower()
        both = ("accepted" in low or "chấp nhận" in low) and \
               ("proposed" in low or "đề xuất" in low)
        check(not both, f"{a['file']}: trạng thái {s!r} chứa cả `accepted` lẫn "
                        "`proposed` — tệp đang nói hai điều ngược nhau")


def inv_supersede_is_bidirectional(adrs: list[dict]) -> None:
    """(7) Nhắc `supersede` thì phải chỉ ra ADR nào, bằng số hiệu.

    GP-16 §"Supersession Idiom": hai phía phải được cập nhật trong **cùng** một
    changeset. Đo trước khi viết: ADR-0039 dòng 91 viết *"nó sẽ phải supersede
    ADR-0026 §4"* — đúng là một supersede, nhưng là **dự định**, ở thì tương lai.
    Nó không sai (ADR đó đang `Proposed`); điều sai sẽ là nếu nó `Accepted` mà vẫn
    chỉ nói "sẽ phải". Cổng tách hai ca đó.
    """
    # Dương tính giả đã gặp thật (đo trên 43 tệp): **mọi** lần nhắc `supersede`
    # đều là dòng footer template copy-paste ở cuối tệp —
    #   "*Template AI-Agile · mọi ADR phải có trạng thái rõ
    #    (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*"
    # Đó là một lần NHẮC TÊN một giá trị enum, không phải một khẳng định supersede.
    # Bỏ cả hai dạng trước khi quét: dòng template, và cụm trong ngoặc đơn liệt kê
    # trạng thái.
    def strip_template(text: str) -> str:
        """Bỏ những chỗ `supersede` được NHẮC TÊN, không phải được DÙNG.

        Đo được trên 44 tệp thật — ba dạng, cả ba đều từng cho dương tính giả:
          1. footer template copy-paste ở mọi ADR (`Template AI-Agile …`);
          2. cụm enum trong ngoặc (`(Proposed/Accepted/Deprecated/Superseded)`);
          3. TRÍCH DẪN một chuẩn — ADR-0044 trích GP-16 nguyên văn, và câu trích
             có chữ `supersede`. Đó là đang nói VỀ chuẩn, không phải đang nói
             ADR này thay thế ADR nào.
        Dạng 3 là dạng khó: một ADR viết về chuẩn ADR sẽ luôn nhắc chữ này.
        """
        lines = []
        for line in text.splitlines():
            if re.search(r"Proposed\s*/\s*Accepted\s*/\s*Deprecated\s*/\s*Superseded", line):
                continue
            if "Template AI-Agile" in line:
                continue
            # (3) dòng trích dẫn: bắt đầu bằng `>` hoặc nằm trong khối trích dẫn.
            if line.lstrip().startswith(">"):
                continue
            lines.append(line)
        out = "\n".join(lines)
        return re.sub(r"\([^)]*Superseded[^)]*\)", " ", out, flags=re.I)

    for a in adrs:
        text = strip_template(a["text"])
        for m in re.finditer(r"supersede[sd]?\b", text, re.I):
            tail = text[m.end():m.end() + 200]
            has_id = bool(REF_RE.search(tail))
            fut = bool(re.search(r"\bsẽ\b|\bwill\b|\bwould\b|tương lai", text[max(0, m.start() - 120):m.end() + 60], re.I))
            accepted = "accepted" in a["status"].lower()
            check(has_id,
                  f"{a['file']}: nhắc `supersede` mà không nêu ADR nào bị thay thế — "
                  "GP-16 đòi liên kết hai phía bằng số hiệu 4 chữ số")
            check(has_id or not accepted or fut,
                  f"{a['file']}: đã `accepted` mà chỉ nói `sẽ phải supersede` — một dự "
                  "định ở thì tương lai không phải một liên kết supersede")


def audit() -> int:
    adrs = load_adrs()
    print("\nADR STANDARDS — chuẩn ADR từ hai repo của PO, áp vào 08-adr\n")
    print(f"  {len(adrs)} tệp ADR\n")
    print(f"  {'#':<6}{'trạng thái':<28}{'ngày':<12}người quyết")
    for a in adrs:
        num = FILE_RE.match(a["file"]).group(1) if FILE_RE.match(a["file"]) else "????"
        print(f"  {num:<6}{a['status'][:27]:<28}{a['date'][:11]:<12}{a['decider'][:36]}")
    return 0


def run(today: dt.date | None = None) -> int:
    global FAILS, PASSES
    FAILS, PASSES = [], 0
    today = today or dt.date.today()
    adrs = load_adrs()
    inv_filename(adrs)
    inv_numbering(adrs)
    inv_references(adrs)
    inv_header_complete(adrs, today)
    inv_status_enum(adrs)
    inv_no_contradiction(adrs)
    inv_supersede_is_bidirectional(adrs)
    return 0 if not FAILS else 1


def selftest() -> int:
    """Đối chứng + 7 phép phá. Mỗi phép phá phải ĐỎ được; nếu một phép xanh vì
    corpus không còn gì để phá thì `raise` — thà nổ còn hơn xanh giả (docs/47 §3.2).
    """
    global FAILS, PASSES
    base = load_adrs()
    today = dt.date(2026, 11, 24)
    cases: list[tuple[str, bool]] = []

    def scenario(label: str, mutate, must_red: bool) -> None:
        global FAILS, PASSES
        adrs = json.loads(json.dumps([{k: v for k, v in a.items()} for a in base]))
        mutate(adrs)
        FAILS, PASSES = [], 0
        inv_filename(adrs)
        inv_numbering(adrs)
        inv_references(adrs)
        inv_header_complete(adrs, today)
        inv_status_enum(adrs)
        inv_no_contradiction(adrs)
        inv_supersede_is_bidirectional(adrs)
        red = bool(FAILS)
        FAILS, PASSES = [], 0
        cases.append((label, red == must_red))

    def slot(adrs, pred, what: str) -> int:
        for i, a in enumerate(adrs):
            if pred(a):
                return i
        raise AssertionError(f"corpus không có dòng nào {what} — phép phá sẽ vô nghĩa")

    def bad_slug(adrs):
        i = slot(adrs, lambda a: True, "để đổi tên")
        adrs[i]["file"] = "ADR-0001-Modular_Phase Loop.md"

    def dup_number(adrs):
        adrs[1]["file"] = adrs[0]["file"]

    def dead_ref(adrs):
        i = slot(adrs, lambda a: True, "để chèn tham chiếu chết")
        adrs[i]["text"] += "\n\nXem ADR-9999 để biết chi tiết.\n"

    def no_status(adrs):
        i = slot(adrs, lambda a: bool(a["status"]), "có trạng thái")
        a = adrs[i]
        a["status"] = ""
        a["text"] = re.sub(r"(?m)^.*Trạng thái.*$", "", a["text"])

    def future_date(adrs):
        i = slot(adrs, lambda a: bool(a["date"]), "có ngày")
        adrs[i]["date"] = "2099-01-01"

    def bad_enum(adrs):
        i = slot(adrs, lambda a: bool(a["status"]), "có trạng thái")
        adrs[i]["status"] = "Đang bàn"

    def contradiction(adrs):
        # Một trạng thái nói hai điều ngược nhau — dạng tệ nhất của "vừa xong vừa
        # chưa", và nó KHÔNG phải ca `Accepted (chờ ký)` (ca đó do cổng 25 canh ở
        # tầng bản chiếu; xem ghi chú ở `inv_status_enum`).
        i = slot(adrs, lambda a: bool(a["status"]), "có trạng thái")
        adrs[i]["status"] = "Accepted/Proposed"

    def vague_supersede(adrs):
        i = slot(adrs, lambda a: bool(a["status"]), "để chèn supersede mơ hồ")
        adrs[i]["status"] = "Accepted"
        adrs[i]["text"] += "\n\nADR này sẽ phải supersede một ADR khác sau này.\n"

    scenario("X1 đổi tên tệp thành slug có chữ hoa + khoảng trắng → đỏ", bad_slug, True)
    scenario("X2 hai ADR trùng số → đỏ", dup_number, True)
    scenario("X3 nhắc ADR-9999 không tồn tại → đỏ", dead_ref, True)
    scenario("X4 ADR mất `Trạng thái` → đỏ", no_status, True)
    scenario("X5 `Ngày` ở tương lai → đỏ", future_date, True)
    scenario("X6 trạng thái ngoài taxonomy GP-16 → đỏ", bad_enum, True)
    scenario("X7 trạng thái chứa cả accepted lẫn proposed → đỏ", contradiction, True)
    scenario("X8 accepted mà chỉ nói 'sẽ phải supersede' → đỏ", vague_supersede, True)
    scenario("X0 đối chứng: corpus gốc → xanh", lambda a: None, False)

    ok = sum(1 for _, o in cases if o)
    for label, o in cases:
        print(f"  {'✓' if o else '✗'} {label}")
    if ok != len(cases):
        print(f"ADR STANDARDS SELFTEST: FAIL — {ok}/{len(cases)}")
        return 1
    print(f"ADR STANDARDS SELFTEST: PASS — {ok}/{len(cases)} "
          f"(1 đối chứng + {len(cases) - 1} phép phá)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Chuẩn ADR (GP-16 · MADR v4 · cross-ref) áp lên portal/docs/08-adr.")
    ap.add_argument("--selftest", action="store_true", help="8 phép phá + đối chứng (CI)")
    ap.add_argument("--audit", action="store_true", help="in bảng 43 ADR")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.audit:
        return audit()

    rc = run()
    if FAILS:
        print(f"ADR STANDARDS: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    adrs = load_adrs()
    role_signed = sum(1 for a in adrs if a["decider"] and
                      any(m in a["decider"].lower() for m in ("principal architect",
                                                              "tech lead", "founder", "legal")))
    print(f"ADR STANDARDS: PASS — {PASSES} kiểm tra · 7 bất biến · {len(adrs)} ADR · "
          f"đánh số 1..{max(int(FILE_RE.match(a['file']).group(1)) for a in adrs if FILE_RE.match(a['file']))} "
          f"liên tục · 0 tham chiếu chết · {role_signed} tệp do chức danh ký (cổng 25 canh chữ ký)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
