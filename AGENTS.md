# AGENTS.md — Quy ước làm việc trong repo Game9K

Tài liệu này là **hợp đồng cho mọi tác nhân** (người hoặc AI) sửa nội dung trong repo này.
Nó tồn tại vì một lý do cụ thể: phần lớn nội dung ở đây là **số liệu tài chính và đặc tả
giao thức**, nơi một con số sai không làm hỏng build mà làm hỏng một vòng gọi vốn.

> **Đọc hết file này trước khi sửa bất kỳ con số nào.** Nếu bạn chỉ có 30 giây, đọc mục
> [Ba luật không được vi phạm](#ba-luật-không-được-vi-phạm).

---

## Ba luật không được vi phạm

1. **Không có số liệu không kiểm chứng được.** Mọi con số tài chính trong `docs/WHITEPAPER.md`,
   `docs/YELLOWPAPER.md` và deck phải tái lập được bằng một lệnh trong `scripts/`. Nếu bạn
   không chỉ ra được lệnh đó, con số chưa được phép vào tài liệu.
2. **Sửa nguồn, không sửa bản dựng.** Ba file PDF **không bao giờ** được sửa tay. Chúng được
   sinh từ `scripts/build_pitch_deck.py` và `scripts/build_whitepaper_pdf.py`. Sửa PDF trực
   tiếp sẽ bị ghi đè ở lần dựng sau và làm mất khả năng tái lập.
3. **Khai báo khoảng trống, đừng lấp bằng lời hứa.** Khi một điều kiện chưa tồn tại (ví dụ:
   pháp nhân phát hành token chưa được thành lập), ghi thẳng vào mục **Known Gap**. Không
   dùng ngôn ngữ mô tả nó như đã có.

---

## Văn phong tài liệu

Mượn từ hợp đồng tác nhân của `chainstack/dev-portal` (xem `docs/12-mintlify-docs-site.md`).
Phần số liệu ở trên là luật cứng; phần này là luật mềm nhưng vẫn phải theo.

| Quy ước | Cụ thể | Không làm |
|---|---|---|
| **Một ý một câu** | Câu dài hơn 35 từ thì tách | Câu ba mệnh đề nối bằng dấu phẩy |
| **Nói thẳng kết luận trước** | Mỗi mục mở bằng câu trả lời, rồi mới giải thích | Mở bài bằng bối cảnh dài rồi mới vào ý |
| **Gọi tên con số có nguồn** | "`79,245283 SOL` (`§6.1b`)" | "khoảng 79 SOL" |
| **Nêu rõ cái KHÔNG biết** | "chưa kiểm chứng", "bên thứ ba", "không tìm thấy bằng chứng" | Viết như sự thật đã xác nhận |
| **Trích dẫn phải có loại** | Bảng nguồn ghi rõ: *quan sát trực tiếp* / *tự công bố* / *bên thứ ba* / *tự đo lại* | Trộn lẫn bốn loại trên trong một câu |
| **Callout thay đoạn văn** | Dùng `>` cho cảnh báo ngắn thay vì đoạn "quan trọng:" 5 dòng | Chôn cảnh báo giữa đoạn văn |
| **Tiếng Việt, một ngôn ngữ** | Không thêm i18n; thuật ngữ kỹ thuật giữ tiếng Anh khi chuẩn là tiếng Anh (`commit`, `hash`, `nonce`) | Dịch nửa vời (`băm xâu` cho `hash`) |

> **Không** dùng từ mang tính hứa hẹn: "sẽ sớm", "gần như chắc chắn", "dẫn đầu thị trường" —
> trừ khi có số liệu tái lập được ngay bên cạnh.

## Cấu trúc repo

```
GameFun/
├── AGENTS.md                    # file này — quy ước cho tác nhân
├── README.md                    # điểm vào + bảng chỉ mục tài liệu
├── docs/
│   ├── PRD.md                   # yêu cầu sản phẩm
│   ├── 00…06-*.md               # khảo sát OSS, UX, DB, API, contract, C4/NFR, roadmap
│   ├── WHITEPAPER.md            # SSOT cho số liệu kinh tế & lộ trình gọi vốn
│   ├── YELLOWPAPER.md           # SSOT cho đặc tả hình thức (bất biến, định lý, byte layout)
│   ├── README-PDF.md            # cách dựng & kiểm chứng bản PDF
│   └── *.pdf                    # SINH TỰ ĐỘNG — không sửa tay
├── pm/
│   ├── claims-registry.json   # TUYÊN BỐ về thế giới (đúng/sai) — người + hạn
│   └── action-register.json   # VIỆC phải làm (xong/chưa) — người + hạn + hậu quả
└── scripts/
    ├── build_pitch_deck.py      # deck 14 slide (ReportLab, 16:9)
    ├── build_whitepaper_pdf.py  # markdown → A4 (whitepaper + yellow paper)
    ├── check_pitch_deck.py      # 48 kiểm tra chéo deck ↔ yellow paper
    ├── check_actions.py         # sổ việc: quá hạn / DONE không bằng chứng ⇒ ĐỎ (docs/37)
    ├── find_contradictions.py   # bốn cặp câu không thể cùng đúng (docs/37)
    ├── check_invariants_coverage.py  # 12 bất biến: cái nào có mã, cái nào chỉ có tên (docs/38)
    ├── verify_invariants.py     # 4 bất biến từng chỉ có tên: INV-05/07/11/12 (docs/39)
    ├── check_gate_wiring.py     # mỗi cổng phải được CI gọi cả chế độ kiểm repo (docs/40)
    ├── verify_kit_bundle.py     # bundle Starter Kit: 6 cổng xanh, hash khớp docs/23 (docs/42)
    ├── check_pm_supabase.py     # sổ dự án Supabase: RLS chỉ-đọc, seed khớp pm/*.json (docs/43)
    ├── check_decisions.py       # quyết định R* phải có mã việc P* kèm hạn + stakeholder (docs/44)
    ├── check_portal.py          # portal/ khớp repo, cấm ký khống ADR chờ ký (docs/45)
    ├── check_portal_render.mjs  # app.js phải VẼ được trong DOM tối thiểu (docs/45, node)
    ├── gen_portal_data.py       # sinh portal/data.json từ pm/*.json + portal/docs/08-adr (docs/45)
    └── gen_supabase_migrations.py # sinh supabase/migrations/ từ pm/sql + pm/*.json (docs/43)
    └── verify_protocol_math.py  # S1–S9 + fuzz, in dòng PASS 100%
```

### Thứ bậc nguồn sự thật (source of truth)

| Câu hỏi | Đọc ở đâu | Không đọc ở đâu |
|---|---|---|
| Con số kinh tế, phí, lộ trình vốn | `docs/WHITEPAPER.md` | deck |
| Đặc tả hình thức, bất biến, byte layout | `docs/YELLOWPAPER.md` | whitepaper |
| Trạng thái kỹ thuật, lộ trình thi công | `docs/06-implementation-roadmap.md` | deck |
| Cách dựng & kiểm chứng PDF | `docs/README-PDF.md` | — |

**Deck là bản tóm tắt, không phải nguồn.** Nếu deck và whitepaper lệch nhau, whitepaper đúng
và deck phải sửa.

---

## Quy trình sửa một con số

```bash
# 1. Sửa nguồn (WHITEPAPER.md hoặc YELLOWPAPER.md)
# 2. Nếu con số xuất hiện trên deck, sửa cả scripts/build_pitch_deck.py
# 3. Nếu con số được kiểm tra tự động, cập nhật scripts/check_pitch_deck.py
# 4. Dựng lại cả bốn PDF (xem docs/README-PDF.md)
# 5. Chạy kiểm chứng
python scripts/check_pitch_deck.py --with-verifier
```

Kỳ vọng đầu ra:

```
PITCH DECK CHECKS: 48/48 passed (100.0%)
ALL WHITEPAPER v1.5 & YELLOW PAPER v1.0 FORMAL CHECKS PASSED (100%)
```

Nếu một trong hai dòng không xuất hiện, **chưa xong**.

### Khi thêm một kiểm tra mới

Thêm vào `scripts/check_pitch_deck.py` trong `FORBIDDEN` (chuỗi đã nghỉ hưu, ví dụ
`"Q4 Năm 1"`) hoặc `REQUIRED` (chuỗi bắt buộc phải có), hoặc viết một `r.check(...)` có
thông điệp nêu rõ kỳ vọng. Một kiểm tra mới phải **thất bại được** — nếu nó luôn đúng thì
nó không kiểm tra gì.

---

## Quy ước dựng PDF

Ba PDF phải **tất định byte-for-byte**. Cơ chế:

- `build_pitch_deck.py` dùng `Canvas(..., invariant=1)` để ghim `/CreationDate` và `/ID`.
- `build_whitepaper_pdf.py` ghim metadata font qua `pin_font_metadata()` +
  `save_font()`. Không có bước này, `fontTools` ghi thời điểm build vào `head.modified`
  và mỗi máy sinh ra một file khác.

**Kiểm chứng tất định đúng cách** — dựng vào hai font cache độc lập, không so với file đã
commit:

```bash
GAME9K_FONT_REBUILD=1 XDG_CACHE_HOME=/tmp/fa python scripts/build_pitch_deck.py /tmp/fa/deck.pdf
GAME9K_FONT_REBUILD=1 XDG_CACHE_HOME=/tmp/fb python scripts/build_pitch_deck.py /tmp/fb/deck.pdf
md5sum /tmp/fa/deck.pdf /tmp/fb/deck.pdf      # bắt buộc trùng
```

Nếu bạn chỉ dựng lại trong cùng một cache rồi so với file đã commit, bạn **chưa** kiểm chứng
được gì — kết quả đó đúng ngay cả khi builder không tất định.

Phụ thuộc: `reportlab`, `fonttools`, `pypdf`, `pypdfium2` và font `@fontsource/noto-sans*`.
Xem `docs/README-PDF.md`.

---

## Quy ước ngôn ngữ & định dạng

- **Tiếng Việt** cho nội dung giải thích; **tiếng Anh** cho định danh kỹ thuật (`VGBC-4T`,
  `INV-01`, `build_sha256`).
- Số thập phân dùng **dấu phẩy** (`60,221994 SOL`), phân cách hàng nghìn dùng **dấu chấm**
  (`$1.000.000`) — theo quy ước tiếng Việt. Ngoại lệ: giá trị trong code và trong khối mã.
- Mọi con số SOL phải ghi đủ **6 chữ số thập phân** khi là kết quả tất toán.
- Trích dẫn điều khoản pháp lý phải kèm **số hiệu văn bản và điều khoản** (`NĐ 147/2024/NĐ-CP,
  Điều 3 khoản 34`), không trích chung chung.

---

## Bẫy đã từng gặp — đừng lặp lại

| Bẫy | Triệu chứng | Cách tránh |
|---|---|---|
| **Nhầm lẫn nhãn cấu hình** | Thay `"hồ sơ A"` bằng chuỗi khác làm hỏng `"hồ sơ ADR"` → `"hồ sơ Tăng trưởngDR"` | Sau mỗi lần thay chuỗi hàng loạt, `grep` lại **cả chữ hoa và chữ thường**, và đọc lướt các dòng bị đổi |
| **Chỉ grep chữ hoa** | `grep "Hồ sơ A"` bỏ sót `"hồ sơ A"` trong câu văn | Dùng `grep -i`, hoặc grep cả hai biến thể |
| **Cây làm việc tụt về commit cũ** | Sửa xong, commit xong, lần sau mở ra thấy file biến mất | `git status -sb` + `git fetch` **trước khi** kết luận bất cứ điều gì về trạng thái repo |
| **PDF "tái lập được" giả** | Dựng lại cùng máy → trùng; máy khác → khác | Dựng vào **hai cache khác nhau** rồi so md5 |
| **Sửa PDF bằng tay** | Lần dựng sau ghi đè, mất công sức | Luôn sửa script, không sửa PDF |
| **Ký tự LaTeX lọt ra bản in** | `\texttt{Stalled}`, `\leftarrow` hiện nguyên văn trong PDF | Sau khi dựng, quét text layer: `pypdf` tìm `texttt`, `leftarrow`, `begin{cases`, `mathrm` |

---

## Phạm vi ngoài repo này

Những việc **không** thuộc repo và không nên đưa vào:

- **Thành lập pháp nhân** (`9K Holdings, Inc.`, foundation phát hành token) — đây là hồ sơ
  pháp lý, không phải tài liệu kỹ thuật. Repo chỉ ghi *trạng thái* (Known Gap) và *yêu cầu*.
- **Giấy phép kinh doanh game tại Việt Nam** — phụ thuộc tư vấn luật sư. Không tự suy diễn
  điều kiện cấp phép vào tài liệu.
- **Thông tin định danh cá nhân, khóa API, địa chỉ ví thật** — không bao giờ commit.
- **Số liệu người dùng thật** — chưa có sản phẩm chạy, nên mọi số MAU/doanh thu trong tài
  liệu là **dự phóng**, và phải được gọi đúng như vậy.

---

## Khi bạn không chắc

Mặc định đúng là **hỏi lại**, không phải tự quyết. Cụ thể:

- Con số kinh tế → hỏi trước khi đổi, vì nó lan sang nhiều tài liệu.
- Nhãn/định danh kỹ thuật (`VGBC-4T`, tên module, route) → hỏi, vì đổi nó phá vỡ tham chiếu.
- Câu chữ tiếp thị → có thể đề xuất, nhưng không tự đổi thông điệp định vị.
- Bất cứ điều gì liên quan đến **pháp lý, thuế, chứng khoán** → không tự kết luận.
