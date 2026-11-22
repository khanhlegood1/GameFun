# 07 — Mô hình Tài liệu & Kiểm chứng lấy từ Chainstack Dev-Portal

> **Tài liệu sống (Living Documentation):** `docs/07-docs-as-code-model.md`
> **Nguồn tham khảo:** [`chainstack/dev-portal`](https://github.com/chainstack/dev-portal) — repo công khai của tài liệu Chainstack (Mintlify), ~1.500 commit
> **Áp dụng cho:** Game9K Launchpad (`game9k.com`)
> **Ngày lập:** 2026-11-22

---

## 1. Vì sao lấy Chainstack làm mẫu, và vì sao không copy nguyên

Chainstack dev-portal là một trong số ít repo tài liệu công khai giải quyết đúng bài toán
Game9K đang có: **tài liệu vừa là bản in cho người, vừa là đầu vào cho máy, vừa là hợp đồng
với cộng tác viên.** Họ làm được ba việc mà repo này trước đây chưa có:

| Việc | Chainstack làm | Game9K trước đây |
|---|---|---|
| Quy ước cho tác nhân | `CLAUDE.md` + `AGENTS.md` ở gốc repo, có style guide | **không có** |
| Chỉ mục máy đọc | `llms.txt` + `llms-full.txt`, mọi trang có `.md` | **không có** |
| Kiểm tra liên kết | `mint broken-links` trước mỗi PR | **không có** |

Nhưng **không thể copy nguyên** — ba khác biệt căn bản:

| | Chainstack | Game9K |
|---|---|---|
| Bản chất | Tài liệu API, độ chính xác nằm ở **mô tả endpoint** | Tài liệu tài chính, độ chính xác nằm ở **con số** |
| Nguồn sự thật | OpenAPI spec tự sinh reference | `WHITEPAPER.md` + `YELLOWPAPER.md` viết tay, có script đối chiếu |
| Nền tảng | Mintlify (MDX + `docs.json`) | Markdown thuần + ReportLab sinh PDF |

Vì vậy Game9K **học cách tổ chức**, không học công cụ. Cụ thể là bốn điểm dưới đây.

---

## 2. Bốn điểm áp dụng

### 2.1. `AGENTS.md` — quy ước thành văn bản, không phải truyền miệng

Chainstack đặt `CLAUDE.md` + `AGENTS.md` ở gốc, ghi rõ: repo công khai, không bao giờ commit
secret, dùng MDX + frontmatter, thêm trang phải sửa `docs.json`, kèm style guide.

Game9K trước đây **không có file nào như vậy**. Kiến thức về "phải sửa script rồi dựng lại
PDF, không sửa PDF", hay "số liệu phải tái lập được bằng một lệnh" chỉ tồn tại trong cách
làm, không tồn tại trong repo. Đó là lý do các lỗi sau từng xảy ra và có thể lặp lại:

- PDF bị coi là "tái lập được" khi thực tế font cache không tất định.
- Thay chuỗi hàng loạt làm hỏng `"hồ sơ ADR"` thành `"hồ sơ Tăng trưởngDR"`.
- Grep chỉ chữ hoa nên bỏ sót `"hồ sơ A"` viết thường trong câu văn.

→ **Đã tạo [`AGENTS.md`](../AGENTS.md)** với ba luật không được vi phạm, thứ bậc nguồn sự
thật, quy trình sửa một con số, và bảng **bẫy đã từng gặp**.

### 2.2. `llms.txt` — chỉ mục cho tác nhân, không phải cho SEO

Chainstack duy trì `llms.txt` (chỉ mục có mô tả) và `llms-full.txt` (toàn văn) theo chuẩn
[llmstxt.org](https://llmstxt.org/), cộng thêm khả năng lấy `.md` của từng trang và một MCP
server để tìm kiếm tài liệu.

Game9K không cần MCP server, nhưng **cần `llms.txt`** vì lý do khác: bộ tài liệu có 12 file
với tên dễ nhầm (`WHITEPAPER` vs `YELLOWPAPER`, `PRD` vs `00`–`06`), và một tác nhân AI đọc
sai file sẽ trích dẫn sai con số. Chỉ mục này nói rõ **file nào là nguồn cho câu hỏi nào**.

→ **Đã tạo [`llms.txt`](../llms.txt)**: 20 mục chia 5 nhóm (bắt đầu / nguồn sự thật / sản
phẩm & kỹ thuật / bản in / kiểm chứng), kèm một mục **Phạm vi** nói thẳng đây là thiết kế
chứ không phải sản phẩm đang chạy.

### 2.3. `mint broken-links` → `scripts/check_docs_links.py`

Chainstack chạy `mint broken-links` trước khi mở PR. Game9K không dùng Mintlify nên không có
lệnh đó, nhưng **vấn đề thì giống hệt**: link tương đối trong Markdown chết âm thầm khi file
đổi tên.

→ **Đã tạo [`scripts/check_docs_links.py`](../scripts/check_docs_links.py)**, kiểm tra 4 nhóm:

1. Liên kết tương đối trong `*.md` trỏ tới file có thật.
2. Mọi mục trong `llms.txt` trỏ tới file có thật.
3. Không tài liệu mồ côi — mọi file trong `docs/` phải được `README.md` nhắc tới.
4. Tên file trong `docs/` đúng quy ước (`NN-*.md` hoặc tên viết hoa đã biết).

Kết quả hiện tại: **87/87 PASS**. Và quan trọng hơn — script **thất bại được**: cài thử một
link hỏng vào `README.md` thì nó báo `FAIL` và trả mã lỗi 1.

### 2.4. CI như một cổng, không phải một báo cáo

Chainstack dùng workflow đồng bộ `llms.txt` và gán người nhận để PR không bị bỏ quên — một
chi tiết vận hành đáng học: **tự động hoá mà không có người nhận thì tự động hoá bị bỏ qua.**

Game9K trước đây **không có CI nào**. Mọi kiểm chứng đều chạy bằng tay, nghĩa là chúng chỉ
được chạy khi có người nhớ.

→ **Đã tạo [`.github/workflows/docs.yml`](../.github/workflows/docs.yml)** với hai job:

| Job | Cổng |
|---|---|
| `verify` | link nội bộ + `verify_protocol_math.py` + `check_pitch_deck.py --with-verifier` |
| `reproducible-pdf` | dựng lại bốn PDF (3 bản dài + legal brief 1 tờ) → **md5 phải trùng bản đã commit**; quét macro LaTeX thô trong text layer |

Cổng thứ hai là cổng quan trọng nhất và là cổng duy nhất repo này từng **tưởng** là đã có.
Nó biến câu "PDF tái lập được" từ một lời khẳng định thành một điều kiện merge.

---

## 3. Điều **không** áp dụng — và lý do

Ghi rõ để lần sau không ai thêm vào rồi phải gỡ:

| Chainstack có | Game9K không dùng | Lý do |
|---|---|---|
| Mintlify + `docs.json` + MDX + frontmatter | Giữ Markdown thuần | Đầu ra chính là **PDF in** cho nhà đầu tư, không phải website docs. Mintlify không sinh được PDF này. |
| `llms-full.txt` (toàn văn một file) | Chỉ `llms.txt` | Toàn văn ~3.800 dòng; tác nhân đọc `llms.txt` rồi mở đúng file sẽ tốt hơn là nạp hết. |
| MCP server để tìm kiếm tài liệu | Không | Chưa có nhu cầu tra cứu động; thêm hạ tầng khi chưa cần là nợ kỹ thuật. |
| Sản phẩm Cloud / Self-Hosted switcher | Không | Game9K là một sản phẩm, không phải hai. |
| Release notes theo từng tháng | Không | Chưa có bản phát hành nào để ghi. |
| Repo công khai có demo endpoint công khai | **Tuyệt đối không** | Xem mục 4. |

---

## 4. Một cảnh báo ngược chiều từ chính repo mẫu

Chainstack có một mục trong `CLAUDE.md` giải thích rằng các **endpoint demo công khai** trong
tài liệu trông giống credential nhưng là cố ý công bố, nên đừng báo cáo chúng là secret bị lộ.

Điều đáng học không phải ngoại lệ đó, mà là **lý do nó phải tồn tại**: khi một repo công khai
chứa chuỗi trông giống bí mật, bạn phải viết ra vì sao nó không phải bí mật — nếu không, mỗi
người đọc sẽ tự quyết định theo cách riêng.

Game9K không có ngoại lệ nào như vậy, và nên giữ nguyên trạng thái đó. Quy ước trong
[`AGENTS.md`](../AGENTS.md) vì thế ghi thẳng: **không bao giờ commit khóa API, địa chỉ ví
thật, hay dữ liệu người dùng** — không kèm ngoại lệ nào.

---

## 5. Việc còn lại (chưa làm trong tài liệu này)

| # | Việc | Vì sao chưa làm |
|---|---|---|
| 1 | Sinh `.md` cho từng trang PDF để tác nhân đọc bản song song | Chưa có nhu cầu; `llms.txt` đã đủ chỉ đường |
| 2 | Kiểm tra **ngữ nghĩa** số liệu giữa deck và whitepaper (hiện chỉ kiểm tra deck ↔ yellow paper) | `check_pitch_deck.py` kiểm tra deck ↔ YP; cầu nối deck ↔ WP còn thiếu |
| 3 | Kiểm tra chính tả tiếng Việt tự động | Chưa có công cụ đủ tốt cho thuật ngữ tài chính Việt |
| 4 | Đo độ tươi của số liệu (con số nào chưa được xác nhận lại trong N ngày) | Cần thêm metadata ngày vào từng bảng — thay đổi lớn |

---

## 6. Kiểm chứng

```bash
python3 scripts/check_docs_links.py
# DOCS LINK CHECKS: 87/87 passed (100.0%)

python3 scripts/check_pitch_deck.py --with-verifier
# PITCH DECK CHECKS: 48/48 passed (100.0%)
# ALL WHITEPAPER v1.5 & YELLOW PAPER v1.0 FORMAL CHECKS PASSED (100%)
```

Cả hai lệnh đều chạy trong CI ([`.github/workflows/docs.yml`](../.github/workflows/docs.yml)),
nên chúng không phụ thuộc vào việc có ai nhớ chạy hay không.
