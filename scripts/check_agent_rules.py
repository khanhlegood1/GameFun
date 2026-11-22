#!/usr/bin/env python3
"""check_agent_rules.py — biến quy ước văn xuôi trong `AGENTS.md` thành cổng.

Vì sao có file này (docs/22 **A1**):
    "A change that violates one [invariant] is a regression, not a trade-off."

`AGENTS.md` có 7 quy ước và 3 luật cứng, nhưng cho tới bản này **không quy ước nào
được máy canh**. Một quy ước không ai kiểm là một quy ước sẽ bị vi phạm trong lúc
vội — và ở repo này, vi phạm làm hỏng một vòng gọi vốn, không làm hỏng build.

Nguyên tắc thiết kế: **chỉ kiểm thứ kiểm được bằng máy.** Bốn quy ước còn lại của
`AGENTS.md` (một ý một câu, kết luận trước, callout thay đoạn văn, tiếng Việt) là
phán đoán — nhét vào đây sẽ sinh báo sai, và báo sai làm người ta tắt cổng.

Chạy: python3 scripts/check_agent_rules.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


# ---------------------------------------------------------------- 1. tài liệu sống
def check_living_docs() -> None:
    """Mỗi `docs/NN-*.md` phải tự khai đường dẫn của chính nó.

    Lý do thật: tài liệu này được chép sang nơi khác (Notion, PDF, PR) và mất
    ngữ cảnh. Dòng `> **Tài liệu sống:**` là thứ duy nhất nói "bản gốc ở đây".
    """
    numbered = sorted(p for p in DOCS.glob("[0-9][0-9]-*.md"))
    check(len(numbered) >= 20, f"chỉ thấy {len(numbered)} tài liệu đánh số — glob sai?")
    for path in numbered:
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:14])
        check(
            "Tài liệu sống" in head,
            f"{path.name}: 8 dòng đầu thiếu `> **Tài liệu sống:**` (AGENTS.md — khai báo nguồn)",
        )


# ---------------------------------------------------------------- 2. số bảng schema
def check_schema_count() -> None:
    """`CREATE TABLE` phải đúng 34 trên `docs/*.md`, và 02 phải đúng 34.

    Con số 34 xuất hiện trong README, whitepaper, deck, `docs/00`, `docs/05`.
    Nếu ai thêm bảng mà không cập nhật, mọi câu "34 bảng" thành sai cùng lúc.
    """
    # Đếm NGHIÊM: `CREATE TABLE` ở đầu dòng, sau khi bỏ khối mã và bảng Markdown.
    # Tài liệu quy trình (22, 24) nhắc *tới* chuỗi này khi mô tả quy ước, không
    # phải khi định nghĩa bảng — nên chúng nằm ngoài phép đếm. Khai báo tường minh,
    # không nới ngưỡng lên 37: nới ngưỡng là tự vô hiệu hoá cổng.
    PROCESS_DOCS = {"22-agent-sdk-workflow-patterns.md", "24-agent-loop-lessons.md"}
    per_file: dict[str, int] = {}
    for path in sorted(DOCS.glob("*.md")):
        if path.name in PROCESS_DOCS:
            continue
        # Chỉ bỏ BẢNG Markdown (dòng bắt đầu bằng `|`): đó là nơi quy ước được
        # nhắc tới. KHÔNG bỏ khối mã — `CREATE TABLE` thật nằm trong khối ```sql.
        body = "\n".join(
            l for l in path.read_text(encoding="utf-8").splitlines()
            if not l.lstrip().startswith("|")
        )
        n = len(re.findall(r"(?m)^\s*CREATE TABLE", body))
        if n:
            per_file[path.name] = n
    total = sum(per_file.values())
    check(total == 34, f"tổng `CREATE TABLE` = {total}, cần 34 — {per_file}")
    check(
        per_file.get("02-database-schema.md", 0) == 34,
        f"docs/02 có {per_file.get('02-database-schema.md', 0)} `CREATE TABLE`, cần 34",
    )
    # Lưới an toàn: chuỗi này phải còn xuất hiện ở 02, nếu không phép đếm bị vô hiệu.
    check(
        "CREATE TABLE".lower() in (DOCS / "02-database-schema.md").read_text(encoding="utf-8").lower(),
        "docs/02: không còn `CREATE TABLE` nào — phép đếm vô nghĩa",
    )


# ---------------------------------------------------------------- 3. từ cấm
BANNED = [
    "sẽ sớm",
    "gần như chắc chắn",
    "dẫn đầu thị trường",
    "chắc chắn thành công",
    "đảm bảo lợi nhuận",
]

# Tài liệu ĐƯỢC PHÉP nhắc tới từ cấm khi đang *dạy* về từ cấm.
BANNED_EXEMPT = {
    "22-agent-sdk-workflow-patterns.md",  # A1 liệt kê danh sách từ cấm
    "24-agent-loop-lessons.md",           # tài liệu này mô tả chính cổng này
}


def check_banned_phrases() -> None:
    for path in sorted(DOCS.glob("*.md")):
        if path.name in BANNED_EXEMPT:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in BANNED:
            if phrase in text:
                line = next(
                    (i + 1 for i, l in enumerate(text.splitlines()) if phrase in l), 0
                )
                FAILS.append(f"{path.name}:{line} có từ cấm `{phrase}` (AGENTS.md — không hứa hẹn)")


# ---------------------------------------------------------------- 4. thứ bậc nguồn
def check_source_hierarchy() -> None:
    """Hai file nguồn số phải tồn tại và phải được khai là nguồn trong AGENTS.md.

    Không kiểm nội dung số (đã có `verify_protocol_math.py`). Kiểm **vai trò**:
    nếu ai xoá đoạn "Thứ bậc nguồn sự thật" khỏi `AGENTS.md`, cổng báo.
    """
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    check("Thứ bậc nguồn sự thật" in agents, "AGENTS.md: mất mục `Thứ bậc nguồn sự thật`")
    check("docs/WHITEPAPER.md" in agents, "AGENTS.md: không còn trỏ tới whitepaper là nguồn số")
    check("docs/YELLOWPAPER.md" in agents, "AGENTS.md: không còn trỏ tới yellow paper là nguồn spec")
    for name in ("WHITEPAPER.md", "YELLOWPAPER.md"):
        check((DOCS / name).exists(), f"docs/{name} biến mất — nguồn số/spec không còn")
    # Deck phải được khai là bản tóm tắt, không phải nguồn.
    check(
        "Deck là bản tóm tắt, không phải nguồn" in agents,
        "AGENTS.md: mất câu chốt vai trò của deck",
    )


# ---------------------------------------------------------------- 5. chỉ mục
def check_index_covers_docs() -> None:
    """Mọi tài liệu đánh số phải có mặt trong `README.md` **và** `llms.txt`.

    Đây là bất biến *nội dung ↔ chỉ mục*: một tài liệu không có trong chỉ mục
    thì coi như không tồn tại với người đọc mới.
    """
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in sorted(DOCS.glob("[0-9][0-9]-*.md")):
        check(path.name in readme, f"{path.name}: không có trong README.md")
        check(path.name in llms, f"{path.name}: không có trong llms.txt")


# ---------------------------------------------------------------- 6. ngôn ngữ tài liệu
def check_no_stale_meta() -> None:
    """Không được để lại dấu vết của quy trình soạn thảo trong tài liệu sống."""
    patterns = [
        (r"\bTODO\b", "TODO còn sót"),
        (r"\bTBD\b", "TBD còn sót"),
        (r"\[cần điền\]", "chỗ trống chưa điền"),
        (r"\bXXX\b", "đánh dấu XXX còn sót"),
    ]
    for path in sorted(DOCS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        # Bỏ mã inline: nhắc tới `TODO` trong dấu backtick là đang nói *về* nó,
        # không phải để lại nó. Cùng nguyên tắc với phép đếm `CREATE TABLE`.
        text = re.sub(r"`[^`\n]*`", "", text)
        for pattern, why in patterns:
            for m in re.finditer(pattern, text):
                line = text[: m.start()].count("\n") + 1
                FAILS.append(f"{path.name}:{line} — {why}")


def main() -> int:
    check_living_docs()
    check_schema_count()
    check_banned_phrases()
    check_source_hierarchy()
    check_index_covers_docs()
    check_no_stale_meta()

    if FAILS:
        print(f"AGENT RULES: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1
    print(f"AGENT RULES: PASS — {PASSES} kiểm tra, 6 nhóm quy ước AGENTS.md được máy canh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
