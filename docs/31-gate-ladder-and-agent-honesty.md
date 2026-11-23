# Thang cổng, và một bài học về sự thật của chính tài liệu

> **Tài liệu sống:** `docs/31-gate-ladder-and-agent-honesty.md`
> **Trạng thái:** `SCOPING` — đánh giá 2 nguồn + **đã dựng thang cổng** (`scripts/check_gate_ladder.py`)
> **Ngày:** 22/11/2026
> **Đầu vào:** `github.com/lexuankhanh1612/awesome-ai-agents` · `e2b.dev/resources/the-state-of-ai-agents-reliability-sdks-benchmarking-and-market-trends`
> **Liên quan:** `docs/25` (câu hỏi cổng) · `docs/26` (bản ghi niềm tin) · `docs/29` · `docs/30` · `docs/PRD.md` §0

---

## 0. Kết luận trước

**Danh sách agent không dùng được cho sản phẩm nào cả. Nhưng bài báo của E2B có một câu — của người làm AutoGPT, không phải của E2B — biến `docs/25` thành một phép kiểm mới: *"nếu agent trượt bài dễ thì nó không qua bài khó; nên thứ tự bài kiểm là một phần của bài kiểm."***

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | `awesome-ai-agents` là gì? | **Fork** của `e2b-dev/awesome-ai-agents` (**`31.033`**★), **không có `LICENSE` chuẩn** (`NOASSERTION`, "Other"), `117.929` KB, `0`★ ở bản fork (§1) |
| **2** | Lấy gì từ nó? | **Không gì cho mã.** Chỉ một điều: **phân loại theo use-case** là cách trình bày dễ kiểm hơn phân loại theo tên (§1.1) |
| **3** | Bài báo nói gì? | 6 mục: thiếu định nghĩa · agent thành *tính năng ẩn* · **độ tin cậy `~99,9%`** · thiếu SDK · **thang benchmark** · đi theo chiều dọc (§2) |
| **4** | Áp vào đâu? | **Bảng 6 cổng HITL** (`docs/PRD.md` §0). `docs/25` đã hỏi *"câu hỏi có kiểm được không"*; nay hỏi tiếp *"thứ tự 6 bậc có đúng là thang không"* (§3) |
| **5** | Đã dựng gì? | `check_gate_ladder.py`: **4 bất biến**, **13** kiểm tra, **20 hạng mục / 16 mệnh đề** trên 6 bậc (§4) |
| **6** | Nó bắt được lỗi gì? | Một phép đếm sai **của chính tôi** — và tôi đã sửa **phép đếm**, không sửa ngưỡng (§4.2) |

---

## 1. `awesome-ai-agents` — fork, và không có giấy phép chuẩn

| | |
|---|---|
| Quan hệ | `fork = true`; `parent` và `source` đều là **`e2b-dev/awesome-ai-agents`** |
| Bản gốc | **`31.033`**★ · `117.929` KB · đẩy lần cuối `21/08/2026` |
| Bản fork | **`0`**★ · tạo `23/11/2026` **`07:01:26Z`** · `pushed_at` `21/08/2026` (**trước** ngày tạo ⇒ trường này chỉ là metadata của lần fork, không phải hoạt động) |
| Giấy phép | **`NOASSERTION`** — tệp `LICENSE` ghi "**Other**", **không phải** một giấy phép SPDX nhận diện được |
| Nội dung | **Chỉ Markdown**: danh sách agent kèm mô tả. Không mã chạy được. |

> **Đừng trích bản fork.** Nếu cần đọc, đọc `e2b-dev/awesome-ai-agents`: cùng nội dung, có `31.033`★ nghĩa là có người sửa lỗi.
>
> **Và đừng coi "Other" là "được dùng thoải mái".** Một giấy phép không nhận diện được là **chưa có quyền rõ ràng** — cùng cách xử lý như `docs/27` §1 với repo không có `LICENSE`: đọc để biết, không chép.

### 1.1. Thứ duy nhất đáng lấy: **phân loại theo việc làm, không theo tên**

Danh sách này nhóm agent theo **use-case** (coding · personal tasks · research). Bài báo xác nhận đó là hướng đi thật: *"agent use cases are being narrowed down to achieve perfection in one specific role"*.

Áp vào repo này: `docs/00-open-source-landscape.md` đã nhóm theo **vai trò** (Adopt / Integrate / Reference) — đúng hướng. Không cần đổi gì, chỉ cần **không** thêm một bảng "danh sách công cụ hay" thứ hai.

---

## 2. Bài báo — sáu mục, ba mục dùng được

Nhãn nguồn: đây là **bài blog của một nhà cung cấp** (E2B bán sandbox). Mọi con số trong đó là **tự công bố** hoặc **ý kiến được phỏng vấn**, không phải đo lường độc lập.

| § | Nội dung | Dùng được? |
|---|---|---|
| 1 | *"The space lacks consensus on the definition of an AI agent"* — 3 năng lực: **reasoning + acting**, **bộ nhớ ngắn & dài hạn**, **dùng công cụ** | ❌ Không áp dụng: Game9K **không** xây agent
| 2 | Agent chuyển từ sản phẩm độc lập thành **tính năng ẩn** trong sản phẩm lớn | ✅ **Đúng, và đã đúng**: 6 cổng HITL là "AI sinh, người duyệt" (`docs/PRD` §0 nguyên lý 2)
| 3 | Độ tin cậy: *"for enterprise customers, we are talking at least ~`99,9%` reliability"* (David Zhang, Aomni) — và *"around `200` milliseconds is already considered slow… LLM calls taking more than `30` seconds"* (Sully Omar, Cognosys) | ⚠️ **Chỉ để so**: KR1.1 hứa `p75 < 3,5 s` cho **lượt tải game**, không phải cho một lời gọi LLM. Hai đơn vị khác nhau, **không** đặt cạnh nhau trong deck
| 4 | Thiếu SDK/framework; agent **rất khó debug** — *"identifying at what step their agent broke and why"* | ✅ **Đúng cho cổng**: khi cổng đỏ, phải biết **bậc nào** đỏ và **vì sao** (§3)
| 5 | **Benchmark**: *"If an agent fails a simple test, it won't pass the more difficult ones. Part of the challenge is hence structuring tests in the correct order"* (Silen Naihin, AutoGPT) | ✅ **Đây là thứ đáng nhất** (§3)
| 5b | **Agent Protocol** — OpenAPI v3 chuẩn hoá giao diện agent | ❌ Game9K không có agent để chuẩn hoá; `docs/03` đã là OpenAPI cho **API**, không phải cho agent
| 6 | Đi theo chiều dọc; giao tiếp với người dùng bằng **kết quả cụ thể**, không giải thích công nghệ | ✅ **Đúng cho thông điệp**: `docs/18` đã chốt "reskin 48h làm Arena vô dụng" — bán *kết quả đo được*, không bán *cơ chế*

---

## 3. Áp vào: **thang 6 cổng**

`docs/25` biến tiêu chí cổng thành **câu hỏi có/không** và canh 3 bất biến. Nhưng nó **không** kiểm được câu hỏi mà §5 của bài báo đặt ra:

> Nếu cổng P01 dễ hơn P02, và P05 lại dễ hơn P04, thì **thang không tăng** — và một chữ ký ở bậc thừa **không mua thêm gì**.

Bốn bất biến của `check_gate_ladder.py`:

| # | Bất biến | Nó bắt được gì |
|---|---|---|
| **1** | Không tiêu chí nào của cổng sau **trùng nguyên văn** cổng trước | Chép tiêu chí để "cho đủ cột" |
| **2** | Không trùng **sau khi bỏ dấu và dấu câu** | Chép lại với dấu câu khác — cùng một phép kiểm, hai chữ ký |
| **3** | Mỗi cổng có **ít nhất một tiêu chí riêng** | Một bậc không kiểm gì mới |
| **4** | Số **hạng mục** của cổng sau ≥ 50% cổng trước | Bậc sau mỏng hẳn bậc trước |

---

## 4. Đã dựng: `check_gate_ladder.py`

```bash
python3 scripts/check_gate_ladder.py           # 4 bất biến
python3 scripts/check_gate_ladder.py --ladder   # in thang 6 bậc
```

```
GATE LADDER: PASS — 13 kiểm tra · 4 bất biến · 6 bậc, 20 hạng mục (16 mệnh đề), 0 lặp giữa các bậc
```

```
Cổng   Mệnh đề   Hạng mục   Riêng   Mệnh đề đầu
P01    3         3          3       Chốt tham số tokenomics
P02    2         2          2       Duyệt toàn bộ màn hình desktop/mobile
P03    3         3          3       OpenAPI 3.1 lint pass
P04    4         4          4       CI xanh 100%
P05    1         5          1       Đóng 100% rủi ro Critical/High (origin isolation…
P06    3         3          3       Staging E2E + Devnet dry-run hoàn tất
```

### 4.1. Vì sao tiêu chí được đọc **trực tiếp** từ `docs/PRD.md`

Không có bản sao tiêu chí trong script. Sửa `docs/PRD.md` §0 là cổng tự thấy — cùng bất biến 1 của `docs/25` ("câu hỏi lấy nguyên văn từ PRD"). Một bản sao thứ hai của tiêu chí là **một cổng thứ hai không ai duyệt**.

### 4.2. Cổng này đã bắt lỗi **của chính tôi** — và tôi sửa phép đếm, không sửa ngưỡng

Lần chạy đầu tiên:

```
GATE LADDER: FAIL — 1 vi phạm
  - P05 có 1 tiêu chí, ít hơn nửa của P04 (4) — bậc sau dễ hơn hẳn bậc trước
```

Nhưng P05 **không** mỏng. Tiêu chí của nó là một mệnh đề chứa **năm** hạng mục:

> *Đóng 100% rủi ro Critical/High (`origin isolation`, `ZIP bomb`, `Sybil`, `MEV/sniper`, `oracle signing`)*

Mỗi hạng mục phải đóng **riêng**. Đếm mệnh đề là đếm **dấu phẩy**, không đếm **việc phải làm**.

> **Đã sửa phép đếm: 1 mệnh đề có `n` hạng mục trong ngoặc = `n`.** Không nới ngưỡng, không thêm ngoại lệ cho P05, và **vẫn in cả hai con số** để người đọc tự đối chiếu.
>
> Đây đúng là điều `AGENTS.md` cấm: *"Không nâng ngưỡng cho khớp số đếm quan sát được."* Sửa **độ đo** thì khác sửa **ngưỡng** — nhưng chỉ khác khi nói rõ ra, như ở đây.

### 4.3. Bốn phép phá đã chạy thật

| # | Phá | Kết quả |
|---|---|---|
| 1 | thêm `coverage ≥ 80%` (nguyên văn của P04) vào P05 | ❌ **2** lỗi: lặp nguyên văn + lặp sau bỏ dấu |
| 2 | chép lại thành `CI XANH 100%!` | ❌ `lặp sau khi bỏ dấu (đã có ở P04)` |
| 3 | thay toàn bộ P06 bằng 3 tiêu chí của P03/P04 | ❌ **4** lỗi: 3 lặp + P06 không còn hạng mục riêng |
| 4 | rút P06 còn `Chạy thử xong` | ❌ `P06 có 1 hạng mục, ít hơn nửa của P05 (5)` |

### 4.4. Một chi tiết của phép phá 1 đáng ghi

Lần đầu, phép phá 1 chỉ in **một** dòng — dòng "lặp sau khi bỏ dấu" — vì dòng "lặp nguyên văn" bị một điều kiện `g != "P01"` chặn. Không sai kết quả, nhưng **thông điệp thiếu vế mạnh hơn**. Đã sửa để in cả hai; giờ phép phá 1 cho đúng **2** dòng, đúng như bảng trên.

---

## 5. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Trích `awesome-ai-agents` như nguồn có giấy phép rõ | §1 — `NOASSERTION`/"Other"; và bản được nêu là **fork** của một repo `31.033`★ |
| **R2** | Đưa `~99,9%` hay `30` giây vào deck cạnh `p75 < 3,5 s` | §2 — hai **đơn vị** khác nhau (độ tin cậy của agent vs thời gian tải trang). Đặt cạnh nhau là gây hiểu sai có chủ ý |
| **R3** | Áp "Agent Protocol" vào `docs/03` | §2 — nó chuẩn hoá **giao diện agent**; Game9K không có agent để chuẩn hoá |
| **R4** | Nới bất biến 4 bằng ngoại lệ cho P05 | §4.2 — sửa độ đo thì được, thêm ngoại lệ thì không |

---

## 6. Việc **không** làm trong tài liệu này

- Không thêm mục "danh sách agent hay" vào `docs/00`; không chép nội dung từ repo không có giấy phép rõ.
- Không sửa `docs/PRD.md` §0 (bảng 6 cổng là nguồn sự thật; cổng đọc từ đó).
- Không đổi số đã kiểm (`12 KB`, `3,5 s`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không dựng lại 4 PDF; không gọi mạng.

## 7. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | Gắn **tên bậc** vào mỗi dòng đỏ của mọi cổng khác, như `check_gate_ladder.py` làm | §2 mục 4 — *"không biết agent hỏng ở bước nào"* là vấn đề số một của agent; với cổng cũng vậy |
| **2** | Khi thêm cổng P07 (nếu có), chạy `--ladder` **trước** khi viết tiêu chí | §3 — thứ tự là một phần của bài kiểm |
| **3** | Ghi vào `AGENTS.md`: **sửa độ đo ≠ sửa ngưỡng**, và mọi lần sửa độ đo phải nêu trong PR | §4.2 — chỗ dễ tự lừa nhất |
| **4** | Không thêm `awesome-*` list thứ hai vào repo | §1.1 — `docs/00` đã nhóm theo vai trò; hai danh sách là hai nguồn sự thật |
