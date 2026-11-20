# Bản PDF chính thức (dựng tự động từ Markdown)

| Tệp | Nội dung | Số trang |
|---|---|---|
| [`MetaPump-Whitepaper-v1.5.pdf`](./MetaPump-Whitepaper-v1.5.pdf) | Whitepaper `v1.5` — bản in/chia sẻ cho nhà đầu tư | 35 |
| [`MetaPump-Yellow-Paper-v1.0.pdf`](./MetaPump-Yellow-Paper-v1.0.pdf) | Yellow Paper `v1.0` — đặc tả hình thức (audit) | 17 |
| [`MetaPump-Pitch-Deck.pdf`](./MetaPump-Pitch-Deck.pdf) | Pitch deck 14 slides (nguồn: Google Slides) | 14 |

## Dựng lại

```bash
python3 -m venv .venv
.venv/bin/pip install reportlab fonttools pypdf
npm i @fontsource/noto-sans @fontsource/noto-sans-mono   # nguồn font (Noto Sans + Noto Sans Mono)
sudo apt install fonts-dejavu-core                       # phương án dự phòng ký tự đặc biệt

# Whitepaper
.venv/bin/python scripts/build_whitepaper_pdf.py \
    docs/WHITEPAPER.md docs/MetaPump-Whitepaper-v1.5.pdf

# Yellow Paper
.venv/bin/python - <<'PY'
import sys; sys.path.insert(0, "scripts")
import build_whitepaper_pdf as B
B.build("docs/YELLOWPAPER.md", "docs/MetaPump-Yellow-Paper-v1.0.pdf",
        "MetaPump Yellow Paper v1.0",
        "Formal Specification — Version-Synced Game Capital Formation",
        kicker="YELLOW PAPER", paper_label="Yellow Paper v1.0",
        running_tagline="Formal Specification — Version-Synced Game Capital Formation")
PY
```

Script sẽ tự gộp font (Latin + tiếng Việt + box-drawing) vào cache `~/.cache/metapump-pdf-fonts`
ở lần chạy đầu tiên; trong repo chỉ có tệp PDF thành phẩm.

## Đặc điểm bản PDF

- **Văn bản thật** (chọn/copy/tìm kiếm được), font nhúng đầy đủ dấu tiếng Việt.
- **Mục lục có số trang** + **outline điều hướng** trong trình đọc PDF.
- **Bảng có header lặp lại** khi sang trang; bảng ≥ 7 cột tự chuyển **trang ngang (landscape)**.
- Công thức LaTeX trong Markdown được chuyển sang Unicode (chỉ số dưới/trên giữ dạng `<sub>`/`<super>`).
- Header/footer chạy theo trang: `METAPUMP · <tên tài liệu>` — `github.com/khanhlegood1/GameFun` — số trang.

> Script kiểm tra hồi quy: sau khi dựng, mọi mục trong mục lục được đối chiếu lại với
> nội dung trang tương ứng; lệch số trang sẽ hiện ngay khi build.
