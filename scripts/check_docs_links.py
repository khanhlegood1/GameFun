#!/usr/bin/env python3
"""check_docs_links.py — kiểm tra toàn bộ liên kết nội bộ và tính nhất quán chỉ mục.

Lấy ý tưởng từ `mint broken-links` của Chainstack dev-portal: tài liệu chỉ đáng tin khi
liên kết bên trong nó không chết. Repo này không dùng Mintlify, nên phần kiểm tra được
viết lại bằng Python thuần — không phụ thuộc gì thêm, chạy được trong CI.

Kiểm tra 4 nhóm:

  1. Liên kết tương đối trong *.md (README, docs/*.md, AGENTS.md) trỏ tới file có thật.
  2. Mọi mục trong llms.txt trỏ tới file có thật.
  3. Mọi file .md trong docs/ đều được README.md nhắc tới (không có tài liệu mồ côi).
  4. Không file .md nào nằm ngoài quy ước đặt tên (README, AGENTS, hoặc NN-*.md, hoặc tên
     viết hoa đã biết).

Dùng:
    python3 scripts/check_docs_links.py            # in báo cáo, mã lỗi 1 nếu có lỗi
    python3 scripts/check_docs_links.py --quiet    # chỉ in khi có lỗi
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Tên file .md hợp lệ trong docs/ ngoài quy ước NN-*.md
KNOWN_UPPER = {"PRD.md", "WHITEPAPER.md", "YELLOWPAPER.md", "README-PDF.md"}

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
LLMS_ENTRY = re.compile(r"^\s*-\s*\[[^\]]*\]\(([^)]+)\)")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checks = 0

    def check(self, ok: bool, message: str, detail: str = "") -> bool:
        self.checks += 1
        if not ok:
            self.errors.append(f"{message}{(' — ' + detail) if detail else ''}")
        return ok


def md_files() -> list[Path]:
    files = [ROOT / "README.md", ROOT / "AGENTS.md"]
    files += sorted((ROOT / "docs").glob("*.md"))
    return [f for f in files if f.exists()]


def internal_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    out = []
    for m in LINK.finditer(text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        out.append(target.split("#", 1)[0])
    return out


def check_links(r: Report) -> None:
    for f in md_files():
        rel = f.relative_to(ROOT)
        for target in internal_links(f):
            if not target:
                continue          # pure anchor such as "(#section)"
            resolved = (f.parent / target).resolve()
            r.check(resolved.exists(), f"liên kết chết trong {rel}", target)


def check_llms(r: Report) -> None:
    llms = ROOT / "llms.txt"
    if not r.check(llms.exists(), "thiếu llms.txt"):
        return
    entries = 0
    for line in llms.read_text(encoding="utf-8").splitlines():
        m = LLMS_ENTRY.match(line)
        if not m:
            continue
        entries += 1
        target = m.group(1)
        r.check((ROOT / target).exists(), "llms.txt trỏ tới file không tồn tại", target)
    r.check(entries >= 10, "llms.txt quá ngắn để làm chỉ mục", f"{entries} mục")


def check_indexed(r: Report) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for f in sorted((ROOT / "docs").glob("*.md")):
        if f.name == "README-PDF.md":
            continue
        r.check(f"docs/{f.name}" in readme,
                "tài liệu không được README.md nhắc tới", f"docs/{f.name}")


def check_naming(r: Report) -> None:
    for f in sorted((ROOT / "docs").glob("*.md")):
        name = f.name
        if name in KNOWN_UPPER or re.fullmatch(r"\d\d-[a-z0-9-]+\.md", name):
            continue
        r.check(False, "tên file docs/ ngoài quy ước", name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    r = Report()
    check_links(r)
    check_llms(r)
    check_indexed(r)
    check_naming(r)

    if r.errors:
        for e in r.errors:
            print(f"  FAIL  {e}")
    if not args.quiet or r.errors:
        passed = r.checks - len(r.errors)
        print(f"\nDOCS LINK CHECKS: {passed}/{r.checks} passed "
              f"({100.0 * passed / max(r.checks, 1):.1f}%)")
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main())
