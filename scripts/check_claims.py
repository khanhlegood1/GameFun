#!/usr/bin/env python3
"""check_claims.py — tuyên bố về THẾ GIỚI phải có loại, và loại phải trung thực.

Vì sao có file này (docs/33):
    `AGENTS.md` cấm **hứa hẹn** ("sẽ sớm", "dẫn đầu thị trường"), nhưng **không** cấm
    **tuyên bố về thế giới** — và đó là lỗ hổng lớn hơn. Câu sai nguy hiểm nhất trong
    một whitepaper gọi vốn không phải "chúng tôi sẽ thành công", mà là
    "**chưa ai làm điều này**": nó kiểm được, nó sai được, và nó làm mất uy tín của
    **mọi** con số khác trong cùng tài liệu.

    Nguồn gốc: `MetaPump/docs/00-framework/nguyen-ly-don-vi-khanh.md` §3–§4 (ADR-0023).
    Họ phân loại **từng câu** và cấm bốn kiểu viết:
      · "X đã chứng minh rằng…"  khi X chỉ là **đề xuất**
      · "người phát minh ra X"    khi PO bác framing "phát minh"
      · "X là mô hình đầu tiên…"  vi phạm chính sách tuyên bố
      · tự so với người nổi tiếng **trước** khi có thành tựu
    Và điều dễ bỏ sót nhất: **ba tầng bằng chứng không được gộp** — toán `PROVEN`
    ≠ hệ thống chạy thật ≠ **giá trị kinh tế** `NEEDS_DATA`.

DẪN LẠI ≠ DÙNG — và đây là chỗ dễ tự lừa mình nhất:
    `docs/33` phải **dẫn lại** câu sai để dạy nó sai ở đâu. Một dòng như
    ``❌ `X` là mô hình đầu tiên…`` là **giáo cụ**, không phải tuyên bố. Nên trước khi
    khớp, chữ nằm trong `` `backtick` `` hoặc `"ngoặc kép"` được **gỡ ra**: đó là chỗ
    người viết đang NHẮC TỚI câu chữ. Ba bất biến dùng bản đã gỡ (`bare`/`nomask`),
    riêng bất biến 2 dùng bản gỡ backtick nhưng **giữ** ngoặc kép — vì
    "X đã chứng minh" trong ngoặc kép vẫn là một câu khẳng định đang được viết ra.
    Thêm nữa, dòng có `❌` hoặc mở đầu bằng `> *"` (khối callout) được miễn bất biến
    3/4: đó là dấu bác tường minh.
    Cả hai ngoại lệ đều **đọc được bằng mắt và hẹp theo cú pháp** — không phải
    whitelist theo tên tệp, và không phải "miễn nếu câu có chữ X".

Năm bất biến:

  1. **Mọi tuyên bố về thế giới phải có nhãn**, trên cùng dòng, hoặc có tên trong
     `pm/claims-registry.json`. Nhãn: `[QUAN SÁT]` · `[TỰ CÔNG BỐ]` · `[ĐỀ XUẤT]`
     · `[CHƯA KIỂM CHỨNG]`.
  2. **Không "đã chứng minh" cho thứ chỉ là đề xuất** (cùng dòng có `đề xuất`/`giả thuyết`).
  3. **Không tự so với người nổi tiếng.** So sánh có giá trị **sau** thành tựu.
  4. **Không gộp ba tầng bằng chứng** trong một dòng mà không nêu tầng.
  5. **Mỗi mục sổ đăng ký phải có owner + lý do + hạn xem lại.** Không có mục "để sau".

Chế độ:

    python3 scripts/check_claims.py            # 5 bất biến
    python3 scripts/check_claims.py --audit     # liệt kê tuyên bố ĐÃ LỌC + nhãn
    python3 scripts/check_claims.py --selftest  # CI

Chỉ thư viện chuẩn, không mạng.

GHI CHÚ VỀ ĐỘ CHÍNH XÁC — đây là phần quan trọng nhất của file này:
    Bản đầu tiên của cổng bắt **46** câu, gần như tất cả là *"vòng lặp đầu tiên"*,
    *"24 giờ đầu tiên"*, *"bản mẫu đầu tiên"* — **không** phải tuyên bố gì về thế giới.
    Một cổng báo sai 45/46 lần sẽ bị tắt trong một tuần, và khi bị tắt thì nó không
    bảo vệ được câu thứ 46. Nên phép khớp ở đây **hẹp có chủ đích**: từ khoá tuyên bố
    chỉ tính khi đứng sau một **chủ thể thị trường** (nền tảng, dự án, mô hình, bệ
    phóng…) — không tính khi đứng sau một **đơn vị thời gian/đếm** (giờ, khối, vòng
    lặp, bản mẫu, lần).
"""

from __future__ import annotations

import argparse
import json
from datetime import date
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "pm" / "claims-registry.json"

LABELS = ["[QUAN SÁT]", "[TỰ CÔNG BỐ]", "[ĐỀ XUẤT]", "[CHƯA KIỂM CHỨNG]"]

# Chủ thể thị trường — đứng TRƯỚC từ khoá thì mới là tuyên bố.
SUBJECTS = (
    r"nền tảng|dự án|giao thức|mô hình|sản phẩm|công ty|hệ thống|launchpad|bệ phóng|"
    r"thị trường|thế giới|ứng dụng|giải pháp|kiến trúc|sáng kiến|ngành|khoảng trống"
)
# Đơn vị thời gian / đếm — đứng trước thì KHÔNG phải tuyên bố.
NON_SUBJECTS = (
    r"giờ|ngày|tuần|tháng|năm|khối|vòng lặp|lượt|bản mẫu|lần|phiên bản|bước|"
    r"người chơi|người dùng|game|tựa|tranche|mốc|dòng|ví|kỳ|quý|"
    r"bài học|kinh nghiệm|mục tiêu|nguyên nhân|lý do|ví dụ"
)
# Cụm tuyên bố thật.
CLAIMS = (
    r"đầu tiên trên thế giới|đầu tiên trên thị trường|duy nhất trên thị trường|"
    r"tiên phong|chưa ai|chưa từng có|không ai làm|đầu tiên"
)

CLAIM_RE = re.compile(
    rf"(?:{SUBJECTS})[^.;|]{{0,40}}?(?:{CLAIMS})",
    re.I,
)
# Chặn oan: nếu giữa chủ thể và từ khoá có một đơn vị thời gian/đếm ⇒ không phải tuyên bố.
# So sánh BẬC NHẤT với thế giới/thị trường thì **luôn** là tuyên bố, bất kể danh từ đứng
# trước — "Game đầu tiên" là đếm, còn "đầu tiên trên Thế giới" là khẳng định về thị trường.
# Chỉ bậc nhất VỚI THẾ GIỚI/THỊ TRƯỜNG mới đứng một mình được. Còn "chưa ai",
# "chưa từng có" thì phải có chủ thể đứng trước — nếu không sẽ bắt oan câu như
# "nhu cầu trở nên cấp bách chưa từng có" (đó là trạng từ nhấn mạnh, không phải tuyên bố).
STRONG = r"đầu tiên trên thế giới|đầu tiên trên thị trường|duy nhất trên thị trường|tiên phong"
STRONG_RE = re.compile(STRONG, re.I)
ANTI_RE = re.compile(rf"(?:{NON_SUBJECTS})\s+(?:{CLAIMS})", re.I)

PROPOSAL = re.compile(r"đề xuất|đề nghị|giả thuyết|phát biểu", re.I)
PROVEN_CLAIM = re.compile(r"đã chứng minh|chứng minh rằng|đã được chứng minh", re.I)
TIERS = ["PROVEN", "NEEDS_DATA", "NEEDS_SYSTEM"]

# Tự so với người nổi tiếng. Hẹp: chỉ khi ngay sau "giống như"/"như" là một tên riêng
# và câu không nói rõ đang dẫn nguồn ("theo", "Crockford" là ví dụ về phương pháp).
# Chỉ bắt TÊN NGƯỜI (≥ 2 từ viết hoa). So sánh với một SẢN PHẨM (Poki, Pump.fun,
# StreamMix) là việc phải làm trong tài liệu cạnh tranh — không phải tự đề cao.
NAME_DROP = re.compile(r"(?:giống như|như)\s+([A-Z][a-zà-ỹ]{2,}\s+[A-Z][a-zà-ỹ]{2,})")
# Miễn trừ CHỈ khi tên được dẫn như NGUỒN ("theo Crockford", "như Crockford đã nói").
# KHÔNG miễn chỉ vì câu có "chúng tôi" — ngược lại, có "chúng tôi" thì càng rõ là tự so.
# (Phép phá: "Chúng tôi làm việc này giống như Steve Jobs" từng LỌT vì lý do đó.)
NAME_DROP_OK = re.compile(r"\btheo\s+|đã (?:nói|viết|chỉ ra)", re.I)

# Ngày hôm nay được GHIM qua biến môi trường để phép thử hạn chạy được mà không
# phụ thuộc đồng hồ máy. Trong CI: không đặt ⇒ dùng ngày thật.
TODAY = date.fromisoformat(os.environ.get("GAME9K_TODAY") or date.today().isoformat())

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def norm(s: str) -> str:
    """Chuẩn hoá để so cụm: bỏ dấu, bỏ dấu câu, **giữ** `**` vì `match` trong sổ
    thường trích nguyên cụm có in đậm."""
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s.lower()).strip()


def sources() -> list[Path]:
    files = sorted((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]
    return [p for p in files if p.exists()]


def lines_of(path: Path):
    in_code = False
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        yield i, line


# Dòng dạy học = dẫn lại câu sai để bác nó. Ba dấu hiệu, đều đọc được bằng mắt:
#   ❌       — dấu bác tường minh
#   > *"…"   — trích dẫn trong khối callout
#   `từ khoá` — từ khoá nằm trong backtick, tức đang được NHẮC TỚI, không phải dùng
TEACHING = re.compile(r"❌|^\s*>\s*\*?\"")


def is_teaching(line: str) -> bool:
    return bool(TEACHING.search(line))


def is_world_claim(line: str) -> str | None:
    if is_teaching(line):
        return None
    # Bậc nhất với thế giới/thị trường: đứng một mình cũng là tuyên bố.
    strong = STRONG_RE.search(line)
    if strong:
        return strong.group(0)
    m = CLAIM_RE.search(line)
    if not m:
        return None
    if ANTI_RE.search(line):
        return None
    return m.group(0)


def load_registry() -> dict:
    if not REGISTRY.exists():
        return {"claims": []}
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def registered(registry: dict, path: Path, line: str) -> dict | None:
    """Khớp theo (tệp, đoạn văn bản) đã chuẩn hoá — không theo số dòng, vì dòng trôi."""
    n = norm(line)
    for entry in registry.get("claims", []):
        if entry.get("path") != path.relative_to(ROOT).as_posix():
            continue
        frag = norm(entry.get("match", ""))
        if frag and frag in n:
            return entry
    return None


def audit() -> int:
    registry = load_registry()
    print("\nTUYÊN BỐ VỀ THẾ GIỚI — sau khi lọc theo chủ thể thị trường\n")
    total = handled = 0
    for path in sources():
        for n, line in lines_of(path):
            claim = is_world_claim(re.sub(r'"[^"]*"', "", re.sub(r"`[^`]*`", "", line)))
            if not claim:
                continue
            total += 1
            has = next((l for l in LABELS if l in line), None)
            reg = registered(registry, path, line)
            if has or reg:
                handled += 1
            mark = "✓" if has else ("R" if reg else "✗")
            label = has or (f"sổ: {reg.get('label')} ({reg.get('status')})" if reg else "KHÔNG NHÃN")
            print(f"  {mark} {path.name}:{n} «{claim}» → {label}")
    print(f"\n{total} tuyên bố · {handled} đã xử lý · {total - handled} chưa")
    return 0


def violations(registry: dict) -> int:
    """Quét 4 bất biến văn bản. Trả về số tuyên bố đã thấy (để bắt cổng chết)."""
    claims = 0
    for path in sources():
        for n, line in lines_of(path):
            # Gỡ backtick VÀ nội dung trong ngoặc kép: cả hai đều đang NHẮC TỚI câu chữ,
            # không phải dùng nó. Bất biến 1 vẫn chạy trên `line` đầy đủ.
            nomask = re.sub(r"`[^`]*`", "", line)
            bare = re.sub(r'"[^"]*"', "", nomask)
            claim = is_world_claim(bare)
            if claim:
                claims += 1
                if not any(l in line for l in LABELS) and not registered(registry, path, line):
                    FAILS.append(
                        f"{path.name}:{n} «{claim}» không có nhãn và không có trong pm/claims-registry.json"
                    )
            if PROPOSAL.search(line) and PROVEN_CLAIM.search(bare):
                FAILS.append(
                    f"{path.name}:{n} vừa `đề xuất/giả thuyết` vừa `đã chứng minh` — "
                    "đề xuất không chứng minh gì (docs/33 §2)"
                )
            m = NAME_DROP.search(nomask)
            if m and not NAME_DROP_OK.search(bare) and not is_teaching(line):
                FAILS.append(
                    f"{path.name}:{n} tự so với «{m.group(1)}» — so sánh chỉ có giá trị "
                    "SAU thành tựu (docs/33 §2.3)"
                )
            tiers = [t for t in TIERS if t in nomask]
            if len(tiers) >= 2 and "tầng" not in line.lower() and not is_teaching(line):
                FAILS.append(
                    f"{path.name}:{n} trộn {tiers} mà không nêu tầng — toán đúng ≠ hệ thống "
                    "chạy ≠ giá trị kinh tế (docs/33 §3.2)"
                )

    # 5. Mỗi mục sổ phải có owner + lý do + hạn xem lại.
    people = registry.get("accountable", {}) if isinstance(registry.get("accountable"), dict) else {}
    people = {people["id"]: people} if people.get("id") else {}
    for i, entry in enumerate(registry.get("claims", [])):
        tag = entry.get("match", f"#{i}")[:40]
        check(bool(entry.get("label")) and entry["label"] in LABELS,
              f"sổ claims [{tag}]: `label` phải là một trong {LABELS}")
        # 5a. `owner` phải trỏ tới một NGƯỜI có tên, không phải một chức danh.
        #     "PO", "team", "TBD" là chỗ để lảng tránh — docs/34 §3.
        owner = entry.get("owner")
        check(bool(owner), f"sổ claims [{tag}]: thiếu `owner`")
        if owner:
            check(owner in people,
                  f"sổ claims [{tag}]: `owner` = {owner!r} không có trong `accountable` "
                  "— phải trỏ tới một NGƯỜI có tên, không phải chức danh (docs/34 §3)")
            if owner in people:
                check(bool(people[owner].get("name")),
                      f"sổ accountable [{owner}]: thiếu `name` — chức danh không phải người")
                check(bool(people[owner].get("basis")),
                      f"sổ accountable [{owner}]: thiếu `basis` — căn cứ nào chỉ định người này?")
        check(bool(entry.get("reason")), f"sổ claims [{tag}]: thiếu `reason`")
        # 5b. Hạn phải là MỘT NGÀY kiểm được, không phải một cụm mô tả.
        #     "trước buổi pitch" không kiểm được — không ai biết hôm nào quá hạn.
        due = entry.get("review_by")
        check(bool(due), f"sổ claims [{tag}]: thiếu `review_by` — không có mục 'để sau'")
        if due:
            try:
                date.fromisoformat(str(due))
            except ValueError:
                FAILS.append(
                    f"sổ claims [{tag}]: `review_by` = {due!r} không phải ngày YYYY-MM-DD "
                    "— hạn mô tả thì không bao giờ quá hạn (docs/34 §3)"
                )
        # 5c. Quá hạn mà vẫn OPEN ⇒ ĐỎ. Đây là bất biến thứ sáu: một hạn không có
        #     hậu quả là một hạn trang trí.
        if due and entry.get("status") == "OPEN":
            try:
                if date.fromisoformat(str(due)) < TODAY:
                    FAILS.append(
                        f"sổ claims [{tag}]: QUÁ HẠN {due} (hôm nay {TODAY}) mà vẫn OPEN — "
                        "dùng `suggested_rewrite`, hoặc đổi status (docs/34 §4)"
                    )
            except ValueError:
                pass
        # 5d. Khi quá hạn thì phải biết làm gì — không có "sẽ tính sau".
        check(entry.get("status") in {"OPEN", "REWRITTEN", "ACCEPTED"},
              f"sổ claims [{tag}]: `status` phải là OPEN / REWRITTEN / ACCEPTED")
        if entry.get("status") == "OPEN":
            check(entry.get("block_if_unmet") in {"rewrite", "remove", "accept"},
                  f"sổ claims [{tag}]: `block_if_unmet` phải là rewrite / remove / accept "
                  "— quá hạn mà không biết làm gì là mục 'để sau' trá hình")
            check(bool(entry.get("suggested_rewrite")) or entry.get("block_if_unmet") != "rewrite",
                  f"sổ claims [{tag}]: `block_if_unmet: rewrite` nhưng thiếu `suggested_rewrite`")

    return claims


def selftest() -> int:
    """5 phép phá — mỗi phép phải làm cổng ĐỎ, trên một corpus tổng hợp trong tmp.

    Không sửa tệp thật: `ROOT` và `REGISTRY` được trỏ tạm sang thư mục tạm.
    Phép P4 ghi lại một lỗi THẬT đã xảy ra: câu tự so với người nổi tiếng từng LỌT
    vì luật miễn trừ khớp chữ "chúng tôi".
    """
    global ROOT, REGISTRY, FAILS, PASSES
    import tempfile

    cases = [
        (
            "P1 tuyên bố không nhãn",
            "| Nền tảng đầu tiên làm việc này trên thị trường |\n",
            [],
            "không có nhãn",
        ),
        (
            "P2 mục sổ thiếu hạn xem lại",
            "Câu sạch.\n",
            [{"path": "docs/scratch.md", "match": "Câu sạch", "label": "[ĐỀ XUẤT]",
              "owner": "T1", "reason": "thử", "status": "OPEN", "suggested_rewrite": "x",
              "block_if_unmet": "rewrite"}],
            "review_by",
        ),
        (
            "P3 đề xuất + đã chứng minh",
            "Mô hình này là đề xuất và đã chứng minh là đúng.\n",
            [],
            "đề xuất/giả thuyết",
        ),
        (
            "P4 tự so với người nổi tiếng (lỗi thật đã lọt)",
            "Chúng tôi làm việc này giống như Steve Jobs từng làm.\n",
            [],
            "tự so với",
        ),
        (
            "P5 trộn PROVEN với NEEDS_DATA",
            "Kết quả là PROVEN và NEEDS_DATA cùng lúc.\n",
            [],
            "trộn",
        ),
        (
            # BẪY NGƯỢC LẠI với ANTI_RE: "game" là đơn vị ĐẾM, nhưng "đầu tiên trên Thế giới"
            # là so sánh bậc nhất với thị trường — vẫn phải là tuyên bố.
            "P7 đơn vị đếm + so sánh bậc nhất với thế giới",
            "Đây là game đầu tiên trên Thế giới làm được việc này.\n",
            [],
            "không có nhãn",
        ),
        (
            # docs/34 §3: chức danh không phải người. "PO" từng nằm trong sổ thật.
            "P8 owner là CHỨC DANH, không phải người",
            "Câu sạch.\n",
            [{"path": "docs/scratch.md", "match": "Câu sạch", "label": "[ĐỀ XUẤT]",
              "owner": "PO", "reason": "thử", "status": "OPEN", "review_by": "2999-01-01",
              "suggested_rewrite": "x", "block_if_unmet": "rewrite"}],
            "không có trong `accountable`",
        ),
        (
            # docs/34 §3: "trước buổi pitch" không bao giờ quá hạn.
            "P9 hạn là cụm mô tả, không phải ngày",
            "Câu sạch.\n",
            [{"path": "docs/scratch.md", "match": "Câu sạch", "label": "[ĐỀ XUẤT]",
              "owner": "T1", "reason": "thử", "status": "OPEN",
              "review_by": "trước buổi pitch", "suggested_rewrite": "x",
              "block_if_unmet": "rewrite"}],
            "không phải ngày YYYY-MM-DD",
        ),
        (
            # BẤT BIẾN 6: quá hạn mà vẫn OPEN thì cổng phải ĐỎ.
            "P10 quá hạn vẫn OPEN",
            "Câu sạch.\n",
            [{"path": "docs/scratch.md", "match": "Câu sạch", "label": "[ĐỀ XUẤT]",
              "owner": "T1", "reason": "thử", "status": "OPEN", "review_by": "2020-01-01",
              "suggested_rewrite": "x", "block_if_unmet": "rewrite"}],
            "QUÁ HẠN",
        ),
        (
            # ĐỐI CHỨNG: nếu miễn trừ quá rộng thì cổng vô dụng; nếu quá hẹp thì không
            # viết được tài liệu dạy về tuyên bố. Dòng dưới là giáo cụ ⇒ phải SẠCH.
            "P6 dòng dạy học trong backtick KHÔNG bị bắt",
            "Luật: `Nền tảng đầu tiên` trên thị trường thì phải có nhãn.\n",
            [],
            None,
        ),
    ]

    # Người có tên — dùng cho các phép thử về owner/hạn (docs/34 §3).
    person = {"id": "T1", "name": "Người thử có tên", "basis": "phép thử"}

    saved_root, saved_reg = ROOT, REGISTRY
    ok = 0
    try:
        for name, body, claims, expect in cases:
            tmp = Path(tempfile.mkdtemp())
            (tmp / "docs").mkdir()
            (tmp / "docs" / "scratch.md").write_text(body, encoding="utf-8")
            reg = tmp / "pm-registry.json"
            reg.write_text(
                json.dumps({"accountable": person, "claims": claims, "not_claims": []},
                           ensure_ascii=False),
                encoding="utf-8",
            )
            ROOT, REGISTRY, FAILS, PASSES = tmp, reg, [], 0
            violations(load_registry())
            if expect is None:
                if not FAILS:
                    ok += 1
                    print(f"  ✓ {name} → sạch (đúng)")
                else:
                    print(f"  ✗ {name} → BẮT OAN: {FAILS[0]}")
                continue
            hit = [f for f in FAILS if expect in f]
            if hit:
                ok += 1
                print(f"  ✓ {name} → đỏ: {hit[0]}")
            else:
                print(f"  ✗ {name} → LỌT (không thấy «{expect}» trong {FAILS})")
    finally:
        ROOT, REGISTRY, FAILS, PASSES = saved_root, saved_reg, [], 0

    if ok != len(cases):
        print(f"CLAIMS SELFTEST: FAIL — {ok}/{len(cases)} phép thử đúng chiều")
        return 1
    print(
        f"CLAIMS SELFTEST: PASS — {ok}/{len(cases)} phép thử đúng chiều "
        f"({len(cases) - 1} phép phá làm cổng đỏ + 1 đối chứng dòng dạy học phải sạch)"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Tuyên bố về thế giới: có nhãn, và nhãn trung thực.")
    ap.add_argument("--audit", action="store_true", help="liệt kê tuyên bố đã lọc")
    ap.add_argument("--selftest", action="store_true", help="kiểm 5 bất biến (CI)")
    args = ap.parse_args()

    if args.audit:
        return audit()

    if args.selftest:
        return selftest()

    registry = load_registry()
    claims = violations(registry)

    check(claims >= 1, f"quét ra {claims} tuyên bố — cổng vô nghĩa, kiểm lại mẫu khớp")

    if FAILS:
        print(f"CLAIMS: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1

    print(
        f"CLAIMS: PASS — {PASSES} kiểm tra · 5 bất biến · {claims} tuyên bố về thế giới, "
        f"{len(registry.get('claims', []))} mục trong sổ đăng ký"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
