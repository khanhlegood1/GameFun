# Bản PDF chính thức (dựng tự động từ Markdown)

| Tệp | Nội dung | Số trang |
|---|---|---|
| [`Game9K-Whitepaper-v1.5.pdf`](./Game9K-Whitepaper-v1.5.pdf) | Whitepaper `v1.5` — bản in/chia sẻ cho nhà đầu tư | 35 |
| [`Game9K-Yellow-Paper-v1.0.pdf`](./Game9K-Yellow-Paper-v1.0.pdf) | Yellow Paper `v1.0` — đặc tả hình thức (audit) | 17 |
| [`Game9K-Pitch-Deck.pdf`](./Game9K-Pitch-Deck.pdf) | Pitch deck 14 slides, 16:9, dựng bằng script (không còn nguồn Google Slides) | 14 |

## Dựng lại

```bash
python3 -m venv .venv
.venv/bin/pip install reportlab fonttools pypdf
npm i @fontsource/noto-sans @fontsource/noto-sans-mono \
      dejavu-fonts-ttf@2.37.3   # nguồn font — DejaVu PHẢI ghim phiên bản
# KHÔNG dùng fonts-dejavu-core của OS: 22.04 (2.35) và 24.04 (2.37) khác nhau,
# dựa vào OS là PDF mất tính tất định giữa máy local và CI.

# Whitepaper
.venv/bin/python scripts/build_whitepaper_pdf.py \
    docs/WHITEPAPER.md docs/Game9K-Whitepaper-v1.5.pdf

# Pitch Deck (14 slides, 16:9) — kiểm tra sau khi dựng
.venv/bin/python scripts/build_pitch_deck.py docs/Game9K-Pitch-Deck.pdf
.venv/bin/python scripts/check_pitch_deck.py --with-verifier

# Yellow Paper
.venv/bin/python - <<'PY'
import sys; sys.path.insert(0, "scripts")
import build_whitepaper_pdf as B
B.build("docs/YELLOWPAPER.md", "docs/Game9K-Yellow-Paper-v1.0.pdf",
        "Game9K Yellow Paper v1.0",
        "Formal Specification — Version-Synced Game Capital Formation",
        kicker="YELLOW PAPER", paper_label="Yellow Paper v1.0",
        running_tagline="Formal Specification — Version-Synced Game Capital Formation")
PY
```

Script sẽ tự gộp font (Latin + tiếng Việt + box-drawing) vào cache `~/.cache/game9k-pdf-fonts`
ở lần chạy đầu tiên; trong repo chỉ có tệp PDF thành phẩm.

> **Kiểm chứng deck:** `scripts/check_pitch_deck.py` đối chiếu từng con số trên deck với
> `docs/YELLOWPAPER.md` (phí tốt nghiệp cố định `1,50 SOL`, thang `b_exit`, `−5,95%` cấu hình
> chuẩn) và tự tính lại phép trừ escrow, tổng doanh thu 4 dòng, EBITDA = doanh thu − OpEx.
> Chạy kèm `--with-verifier` để nối tiếp `scripts/verify_protocol_math.py`; mọi con số đã nghỉ
> hưu (`Q4 Năm 1`, `$72,0M`, `$0,75M`, `176/176`…) làm script trả mã lỗi 1.

## Đặc điểm bản PDF

- **Văn bản thật** (chọn/copy/tìm kiếm được), font nhúng đầy đủ dấu tiếng Việt.
- **Mục lục có số trang** + **outline điều hướng** trong trình đọc PDF.
- **Bảng có header lặp lại** khi sang trang; bảng ≥ 7 cột tự chuyển **trang ngang (landscape)**.
- Công thức LaTeX trong Markdown được chuyển sang Unicode (chỉ số dưới/trên giữ dạng `<sub>`/`<super>`).
- Header/footer chạy theo trang: `GAME9K LAUNCHPAD · <tên tài liệu>` — `github.com/khanhlegood1/GameFun` — số trang.
- **Domain separator on-chain là hằng 16 B:** `b"GAME9K_POP_V1\0\0\0"` và `b"GAME9K_MILE_V1\0\0"` (zero-pad), nên mọi offset & kích thước struct trong YP §7.1 không đổi.

> Script kiểm tra hồi quy: sau khi dựng, mọi mục trong mục lục được đối chiếu lại với
> nội dung trang tương ứng; lệch số trang sẽ hiện ngay khi build.
