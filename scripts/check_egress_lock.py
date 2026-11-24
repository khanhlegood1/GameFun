#!/usr/bin/env python3
"""check_egress_lock.py — tất định **không phải** một tính từ của quy trình; nó là một tính chất của mã.

Vì sao có file này (docs/30):
    `AGENTS.md` gọi cổng là "**tất định byte-for-byte**". Nhưng cái *chứng minh* điều đó
    cho tới hôm nay là **hai CI run xanh**, không phải một tính chất đọc được từ mã.
    Với một repo mà toàn bộ giá trị là "số liệu tái lập được", sự khác biệt giữa
    *"chưa có gì gọi mạng"* và *"được chứng minh là không thể gọi mạng"* là sự khác biệt
    giữa hy vọng và bảo đảm.

    Nguồn gốc ý tưởng: OpenRouter là một *nhà định tuyến*. Thứ nguy hiểm của nó không
    phải API key — mà là **định tuyến không tường minh**: `sort: "price"` chọn theo *giá
    của lần chạy trước*, nên hai lần chạy cho hai nhà cung cấp khác nhau, cho hai kết quả
    khác nhau. Đó chính xác là thứ một cổng tất định phải **từ chối**.

PHẠM VI — và đây là chỗ bản trước đã sai (docs/35 §3.1):
    Bản trước chỉ quét `scripts/*.py`. Nhưng `pm/*.json`, `sdk/**/*.json`, `sdk/**/*.js`,
    `package.json` và `.github/*.yml` đều có thể chứa một URL — tức một **điểm ra mạng** —
    và không tệp nào trong số đó từng được quét. Đúng loại lỗi mà chính cổng này sinh ra
    để bắt: *"được chứng minh là không gọi được"* chỉ đúng cho **một thư mục**.
    Nay phạm vi là **toàn repo**, trừ `docs/*.md` (tài liệu **dẫn nguồn** — trích URL ở đó
    là việc phải làm, không phải lỗi) và `node_modules/`.

Cái nó kiểm (6 bất biến, đọc từ mã chứ không tin lời khai):

  1. **Không có thư viện HTTP** trong `scripts/*.py` — không `requests`, `httpx`,
     `urllib.request`, `http.client`, `socket`, `aiohttp`, `openai`, `anthropic`.
     (`urllib.parse` thì được: xử lý chuỗi, không gọi mạng.)
  2. **Không có `.github/workflows/*.yml` nào gọi dịch vụ AI** — không `openrouter`,
     không `anthropic`, không `generativelanguage`, không `api.openai.com`.
  3. **Chỉ một action ngoài `actions/*`** được phép (`softprops/action-gh-release`).
     Mỗi action là một chương trình chạy với token của repo; càng ít càng tốt.
  4. **Mọi bước trong workflow đều có `run:`** — không có bước "dùng một action viết sẵn
     để làm việc X" mà không ai đọc được nó làm gì.
  5. **Không URL trong tệp THỰC THI hoặc tệp DỮ LIỆU** (`pm/`, `sdk/`, `.github/`,
     `package.json`, `scripts/`) — vì đó là điểm ra mạng, không phải tài liệu.
  6. **Không `fetch(`/`XMLHttpRequest`/`curl `/`wget `** trong tệp dữ liệu hoặc mã SDK.

Ba chế độ:

    python3 scripts/check_egress_lock.py            # 6 bất biến
    python3 scripts/check_egress_lock.py --audit     # liệt kê mọi điểm có thể ra mạng
    python3 scripts/check_egress_lock.py --selftest  # CI

Chỉ thư viện chuẩn, không mạng — tất nhiên.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
WORKFLOWS = ROOT / ".github" / "workflows"

# Thư viện/khoá mà việc xuất hiện trong `scripts/` nghĩa là "có thể gọi mạng".
FORBIDDEN_IMPORTS = [
    ("requests", "thư viện HTTP"),
    ("httpx", "thư viện HTTP"),
    ("aiohttp", "thư viện HTTP"),
    ("urllib.request", "HTTP client"),
    ("urllib3", "HTTP client"),
    ("http.client", "HTTP client"),
    ("socket", "socket thô"),
    ("openai", "SDK nhà cung cấp AI"),
    ("anthropic", "SDK nhà cung cấp AI"),
    ("google.generativeai", "SDK nhà cung cấp AI"),
    ("genai", "SDK nhà cung cấp AI"),
    ("openrouter", "SDK định tuyến"),
]

# Chuỗi trong workflow nghĩa là "CI gọi một dịch vụ AI".
FORBIDDEN_WORKFLOW_TOKENS = [
    "openrouter",
    "anthropic.com",
    "api.openai.com",
    "generativelanguage.googleapis",
    "OPENROUTER_API_KEY",
]

# Action ngoài `actions/*` được phép, kèm lý do. Danh sách này **chỉ được ngắn đi**.
ALLOWED_ACTIONS = {
    "actions/checkout",
    "actions/setup-python",
    "actions/upload-artifact",
    "actions/download-artifact",
    "softprops/action-gh-release",
}

# Tệp THỰC THI / DỮ LIỆU — nơi một URL nghĩa là một điểm ra mạng.
# `docs/*.md` KHÔNG nằm ở đây: trích URL trong tài liệu là dẫn nguồn, không phải gọi mạng.
# `node_modules/` không nằm ở đây: đó là mã của bên thứ ba, không phải của repo.
DATA_GLOBS = (
    "scripts/*.py",
    "pm/*.json",
    "sdk/**/*.json",
    "sdk/**/*.js",
    "package.json",
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    ".github/*.yml",
    "receipts/*.json",
    # docs/43: bằng chứng đo trên Supabase. Không chứa URL, nhưng phải được
    # canh — một tệp "bằng chứng" không ai quét là một chỗ để lén thêm endpoint.
    "supabase/*.json",
    "pm/sql/*.sql",
)
URL_RE = re.compile(r"https?://[^\s'\"<>)\]]+", re.I)
CALL_RE = re.compile(r"\b(?:fetch\s*\(|XMLHttpRequest|new\s+WebSocket|curl\s|wget\s)", re.I)
# Được phép: tự tham chiếu repo, và chuỗi tài liệu trong danh sách "cấm" của CONTRACT.json.
URL_ALLOW = (
    "github.com/khanhlegood1/gamefun",
    "game9k.com",
    "localhost",
    "127.0.0.1",
)

FAILS: list[str] = []
PASSES = 0


def check(ok: bool, message: str) -> None:
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(message)


def python_files() -> list[Path]:
    return sorted(SCRIPTS.glob("*.py"))


def workflow_files() -> list[Path]:
    return sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))


def scan_text(path: Path) -> str:
    """Văn bản để quét — bỏ docstring và comment của tệp Python.

    Cần thiết vì tệp này và các cổng khác **nhắc tới** `fetch(`/`XMLHttpRequest` khi
    giải thích luật. Nhắc tới không phải dùng — cùng nguyên tắc với `check_claims.py`
    (gỡ backtick trước khi khớp). Ở đây gỡ theo cú pháp: chuỗi ba nháy và `#`.
    """
    text = path.read_text(encoding="utf-8")
    if path.suffix != ".py":
        return text

    def blank(m):
        return "\n" * m.group(0).count("\n")

    text = re.sub(r'"""[\s\S]*?"""', blank, text)
    text = re.sub(r"'''[\s\S]*?'''", blank, text)
    return "\n".join(re.sub(r"\s#.*$", "", ln) for ln in text.splitlines())


def data_files() -> list[Path]:
    """Mọi tệp thực thi/dữ liệu — nơi URL là điểm ra mạng. Bỏ node_modules."""
    out: set[Path] = set()
    for pattern in DATA_GLOBS:
        out.update(p for p in ROOT.glob(pattern) if p.is_file())
    return sorted(p for p in out if "node_modules" not in p.parts)


def imports_in(path: Path) -> list[str]:
    """Liệt kê mọi dòng `import`/`from … import`, đã bỏ comment."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        m = re.match(r"(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", s)
        if m:
            out.append(m.group(1) or m.group(2))
    return out


def audit() -> int:
    print("\nĐIỂM CÓ THỂ RA MẠNG — kiểm bằng mắt, không bằng lời khai\n")
    print(f"{'Tệp':32}{'Thư viện ngoài chuẩn':44}Đánh giá")
    print("─" * 104)
    stdlib_prefixes = {
        "argparse", "glob", "json", "pathlib", "re", "sys", "os", "hashlib", "math",
        "random", "itertools", "datetime", "textwrap", "subprocess", "shutil",
        "collections", "typing", "zlib", "gzip", "struct", "tempfile", "functools",
        "decimal", "dataclasses", "unicodedata", "html", "csv", "io", "time",
    }
    external = 0
    for path in python_files():
        ext = sorted({i.split(".")[0] for i in imports_in(path)} - stdlib_prefixes - {"__future__"})
        if ext:
            external += 1
            print(f"{path.name:32}{', '.join(ext):44}{'cần xem'}")
    if not external:
        print(f"{'(không tệp nào)':32}{'':44}")
    print(f"\n{len(python_files())} tệp Python trong scripts/ · {external} tệp import thư viện ngoài chuẩn")
    print("\nGhi chú: reportlab/fonttools/pypdf là thư viện DỰNG PDF — chúng không mở socket.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Khoá xuất mạng: chứng minh cổng không gọi ra ngoài.")
    ap.add_argument("--audit", action="store_true", help="liệt kê điểm có thể ra mạng")
    ap.add_argument("--selftest", action="store_true", help="kiểm 6 bất biến (CI)")
    args = ap.parse_args()

    if args.audit:
        return audit()

    # 1. Thư viện HTTP trong scripts/
    for path in python_files():
        mods = imports_in(path)
        for mod in mods:
            for bad, why in FORBIDDEN_IMPORTS:
                if mod == bad or mod.startswith(bad + "."):
                    FAILS.append(f"{path.name}: import `{mod}` — {why}")
                    break

    # 2. Workflow không gọi dịch vụ AI
    for path in workflow_files():
        text = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_WORKFLOW_TOKENS:
            check(
                token.lower() not in text,
                f"{path.name}: có `{token}` — CI gọi dịch vụ AI; cổng phải tất định",
            )

    # 3. Allowlist action
    for path in workflow_files():
        text = path.read_text(encoding="utf-8")
        used = set(re.findall(r"uses:\s*([\w.-]+/[\w.-]+)", text))
        for action in sorted(used):
            check(
                action in ALLOWED_ACTIONS,
                f"{path.name}: dùng action `{action}` ngoài allowlist — mỗi action chạy bằng token của repo",
            )

    # 4. Mọi bước có `run:` (không có "hộp đen")
    for path in workflow_files():
        text = path.read_text(encoding="utf-8")
        steps = re.findall(r"(?m)^\s{6}- name:.*$", text)
        runs = re.findall(r"(?m)^\s{8}run:", text)
        # Mỗi bước phải có `run:` hoặc là `uses:` (đã kiểm ở bất biến 3).
        uses = re.findall(r"(?m)^\s{8}uses:", text)
        check(
            len(runs) + len(uses) >= len(steps),
            f"{path.name}: {len(steps)} bước nhưng chỉ {len(runs)} `run:` + {len(uses)} `uses:` "
            "— có bước không đọc được nó làm gì",
        )

    # 5. Không URL trong tệp thực thi/dữ liệu.
    files = data_files()
    # Cổng chết: nếu phạm vi co lại (đổi glob, đổi cấu trúc thư mục) thì số tệp tụt và
    # cổng vẫn báo xanh trong khi không kiểm gì. Đây là bất biến chống chính nó.
    check(len(files) >= 20,
          f"chỉ quét {len(files)} tệp dữ liệu/mã — phạm vi hẹp bất thường, cổng có thể "
          "đã ngừng kiểm (cần ≥ 20)")
    for path in files:
        try:
            text = scan_text(path)
        except UnicodeDecodeError:
            continue
        for m in URL_RE.finditer(text):
            url = m.group(0).lower()
            if any(a in url for a in URL_ALLOW):
                continue
            line = text[: m.start()].count("\n") + 1
            FAILS.append(
                f"{path.relative_to(ROOT)}:{line}: URL `{m.group(0)}` trong tệp dữ liệu/mã "
                "— đó là một điểm ra mạng (docs/35 §3.1)"
            )

    # 6. Không lời gọi mạng trong tệp dữ liệu hoặc mã SDK.
    for path in files:
        try:
            text = scan_text(path)
        except UnicodeDecodeError:
            continue
        for m in CALL_RE.finditer(text):
            # CONTRACT.json liệt kê "fetch / XMLHttpRequest" như thứ SDK CẤM — chuỗi đó
            # nằm trong danh sách `forbidden`, không phải một lời gọi.
            line = text[: m.start()].count("\n") + 1
            ctx = text[max(0, m.start() - 160): m.start()]
            if "forbidden" in ctx or "cấm" in ctx.lower():
                continue
            # Dòng ĐỊNH NGHĨA bộ dò (`re.compile(...)`) không phải lời gọi mạng.
            if "re.compile(" in text.splitlines()[line - 1]:
                continue
            FAILS.append(
                f"{path.relative_to(ROOT)}:{line}: `{m.group(0).strip()}` — lời gọi mạng "
                "trong tệp dữ liệu/mã; SDK chỉ dùng postMessage (docs/27 §6 R1)"
            )

    if FAILS:
        print(f"EGRESS LOCK: FAIL — {len(FAILS)} vi phạm / {PASSES + len(FAILS)} kiểm tra")
        for f in FAILS:
            print("  -", f)
        return 1

    print(
        f"EGRESS LOCK: PASS — {PASSES} kiểm tra · 6 bất biến · "
        f"{len(python_files())} tệp Python không có HTTP client · "
        f"{len(files)} tệp dữ liệu/mã không chứa URL · "
        f"{len(workflow_files())} workflow không gọi dịch vụ AI"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
