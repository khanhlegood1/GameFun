# Vòng lặp tác nhân — học từ mã nguồn mở của Arena và các agent OSS

> **Tài liệu sống:** `docs/24-agent-loop-lessons.md`
> **Trạng thái:** `SCOPING` — nghiên cứu + **đã biến một phần thành cổng CI**
> **Ngày:** 22/11/2026
> **Đầu vào:** *"Tham khảo các github open source tạo ra Arena.ai để học cách logic tuần tự mà Agent của Arena trả lời các câu chat"*
> **Liên quan:** `docs/22` (A1: bất biến do test canh · A3: bench sống · A4: trace) · `docs/07` (docs-as-code) · `AGENTS.md`

---

## 0. Kết luận trước

**Có một chỗ hiểu sai cần nói ngay: phần "logic tuần tự" của Agent Mode trên Arena.ai không nằm trong repo công khai nào.** Cái công khai là hạ tầng để **chấm điểm câu trả lời** (FastChat, Arena-Hard), không phải vòng lặp để **tạo ra** câu trả lời. Nhưng vòng lặp đó được mô tả đủ công khai để dựng lại — và nó khớp với bốn dự án agent mở.

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | `lm-sys/FastChat` có phải là Agent của Arena.ai? | ❌ **Không.** Nó là hạ tầng **Battle Mode** (Chatbot Arena). Không có vòng lặp công cụ, không có sandbox |
| **2** | Vòng lặp Agent Mode có mã công khai? | ❌ **Không.** Platform đóng; vote và trace là tài sản riêng |
| **3** | Vậy học được gì? | ✅ **Rất nhiều** — từ **tài liệu công khai của Arena** + **bốn agent OSS**, không từ "repo của Arena" |
| **4** | Bốn dự án đó nói gì? | §2. Điểm chung: **vòng lặp tuyến tính**, **một công cụ mạnh**, **quan sát ngắn**, **bước bị giới hạn** |
| **5** | Áp dụng vào Game9K thế nào? | Đối chiếu **quy trình nội bộ** (§3) + **một cổng CI đã dựng và đã thử làm đỏ** (§4, §6) |
| **6** | Có phải mọi thứ đều đáng bắt chước? | ❌ Không. **Bốn thứ phải từ chối** (§5) — trong đó hai thứ Arena làm tốt nhưng Game9K **không** làm được |

---

## 1. Sự thật về "GitHub open source của Arena.ai"

### 1.1. Cái gì thật sự tồn tại *(quan sát trực tiếp qua GitHub API, 22/11/2026)*

| Repo | Sao | Giấy phép | Đẩy cuối | Nó là gì |
|---|---|---|---|---|
| `lm-sys/FastChat` | **`39.550`** | Apache-2.0 | `01/05/2026` | Serving + **Battle Mode**. README: *"powers Chatbot Arena"* |
| `lm-sys/arena-hard-auto` | `1.087` | Apache-2.0 | `20/11/2026` | **Bộ chấm điểm tự động**: `500` truy vấn + `250` prompt sáng tạo, giám khảo là LLM |
| `lm-sys/RouteLLM` | `5.725` | Apache-2.0 | `10/08/2024` | Định tuyến model theo chi phí. **Không** dùng trong Agent Mode |
| `lm-sys/llm-judge` | — | — | — | ❌ **Không tồn tại** (404) |

> **Ba repo, ba mục đích, không cái nào là Agent Mode.** `FastChat` = *so sánh hai câu trả lời*; `arena-hard-auto` = *chấm điểm*; `RouteLLM` = *định tuyến*. Agent Mode ra mắt **`04/06/2026`** — sau cả ba.

### 1.2. Vòng lặp Agent Mode — mô tả công khai *(tài liệu Arena, không phải mã)*

| Thành phần | Mô tả công khai |
|---|---|
| **Một orchestrator** | *"a dedicated orchestrator model"*, chọn **ngẫu nhiên** mỗi phiên, **không tiết lộ** model nào |
| **Kế hoạch tự lập** | *"autonomously builds a plan and uses its built-in tools"* |
| **Bộ công cụ cố định** | web search · tạo ảnh · **sandbox/bash** · đọc/ghi tệp · hỏi lại người dùng · connectors |
| **Đổi model giữa phiên** | *"if a response is likely to fail and leave the session in a broken state, the system may automatically switch to a different model"* |
| **Connector bật theo lượt** | *"a tool is available to the model only when you have connected its service and enabled it for the current turn. Nothing is loaded in the background"* |
| **Trace dùng để chấm điểm** | *"single-threaded traces, not battles"*; *"causal tracing"* thay cho Bradley-Terry |

> **Câu đáng học nhất:** *"the agent loads only the tool definitions it needs for the task at hand, so adding more connectors does not slow it down or crowd out the rest of your conversation."* Đây là **thiết kế ngữ cảnh**, không phải thiết kế tính năng.

---

## 2. Bốn dự án agent mở — và điều chúng nói giống nhau

Chọn theo **kiến trúc khác nhau**, không theo số sao *(GitHub API, 22/11/2026)*:

| Dự án | Sao | Cách tiếp cận vòng lặp |
|---|---|---|
| `SWE-agent/SWE-agent` | **`20.854`** | **Agent-Computer Interface**: công cụ được *thiết kế cho model*, không phải API thô |
| `SWE-agent/mini-swe-agent` | `9.959` | **~`100` dòng**, **chỉ `bash`**, *"completely linear history — every step just appends"* |
| `huggingface/smolagents` | `30.484` | `CodeAgent`: **hành động viết bằng mã Python**, không phải JSON tool-call |
| `openai/openai-agents-python` | `30.814` | Agents + **handoffs** + **guardrails** + **sessions** + **tracing** |

### 2.1. `mini-swe-agent` — bài học phản trực giác

Đọc README của nó là đọc bản tự phê bình của chính `SWE-agent`:

> *"What if our agent was 100x simpler, and still worked nearly as well?"* · *"Does not have any tools other than bash"* · *"Has a completely linear history — every step of the agent just appends to the messages."*

**Cắt công cụ chuyên dụng, cắt máy trạng thái, chỉ giữ một vòng lặp tuyến tính + một công cụ đủ mạnh** — và hiệu năng *"nearly as well"*.

> **Bài học:** khi một quy trình bắt đầu cần "công cụ thứ mười", câu hỏi đúng là *"bỏ được bảy cái đầu không"*, không phải *"cái thứ mười để ở đâu"*.

### 2.2. `smolagents` — con số đáng nhớ

> *"Writing actions as code snippets … uses **30% fewer steps** (thus 30% fewer LLM calls) and reaches higher performance on difficult benchmarks."*

**`30%` ít bước hơn = `30%` ít lần gọi model hơn.** Đây là con số duy nhất trong bốn README nói thẳng về **chi phí của vòng lặp**, không chỉ về chất lượng.

### 2.3. `openai-agents-python` — điều đáng học là ranh giới

`agents` · `handoffs` · `guardrails` · `sessions` · `tracing`. Điểm đáng học **không phải** tính năng, mà là **tách lớp**: guardrail là **lớp riêng**, không phải `if` nằm trong prompt; trace là **đầu ra bậc một**, không phải log phụ.

> Khớp đúng `docs/22` **A4**. Game9K vẫn chưa có trace — vẫn là nợ.

---

## 3. Đối chiếu với quy trình nội bộ của Game9K

Đây là phần áp dụng thật: **vòng lặp của chính repo này**, không phải của sản phẩm.

| Mẫu | Arena / OSS | Game9K hôm nay | Đánh giá |
|---|---|---|---|
| **Kế hoạch trước khi hành động** | *"builds a plan"* | Mỗi việc là chuỗi lệnh có mục tiêu rõ (`commit` → `push` → PR → chờ CI → merge) | ✅ **Đã đúng** |
| **Một công cụ mạnh thay nhiều công cụ** | `mini`: chỉ `bash` | `python3` + `git` + `gh`, không framework riêng | ✅ **Đã đúng** |
| **Quan sát ngắn, không đổ cả log** | *"lean context"* | `tail -1`, `--jq`, `| head` là mặc định | ✅ **Đã đúng** |
| **Cổng chặn thay vì lời dặn** | `guardrails` là lớp riêng | `AGENTS.md` có 7 quy ước — **`0`** được máy canh *(trước PR này)* | ❌ **Sai** → §4 |
| **Trace là đầu ra bậc một** | `tracing` built-in | Không có trace cho "vì sao tài liệu này ra đời" | ❌ **Sai** — vẫn là nợ `docs/22` A4 |
| **Bước bị giới hạn** | rate limit, `max` bước | CI có timeout; phiên làm việc không có ngân sách bước | ⚠️ **Một nửa** |
| **Tách "làm" khỏi "chấm"** | orchestrator ≠ judge | `check_pitch_deck.py` chấm `build_pitch_deck.py` — **hai chương trình khác nhau** | ✅ **Đúng, và hiếm** |

> **Dòng cuối là điểm mạnh đáng giữ:** bên dựng và bên chấm là hai chương trình khác nhau. Rất nhiều dự án để chính builder tự khai "đã kiểm".

---

## 4. Đã biến thành cổng: `scripts/check_agent_rules.py`

`docs/22` **A1**: *"A change that violates one [invariant] is a regression, not a trade-off."* PR này dựng cổng đó — **bước ① của thứ tự thi công trong `docs/22`**.

Sáu nhóm kiểm, tất cả **canh được bằng máy**:

| # | Kiểm | Vì sao canh được |
|---|---|---|
| **1** | Mọi `docs/NN-*.md` có dòng `> **Tài liệu sống:**` | Tự khai đường dẫn của chính nó — sai là sai ngay |
| **2** | `CREATE TABLE` = **`34`** | Con số tuyệt đối, đã chốt nhiều lần |
| **3** | Từ cấm trong `docs/*.md`: "sẽ sớm", "gần như chắc chắn", "dẫn đầu thị trường", … | Danh sách hữu hạn, đúng luật `AGENTS.md` |
| **4** | `AGENTS.md` còn mục **Thứ bậc nguồn sự thật** + câu chốt vai trò của deck | Bảo vệ thứ bậc nguồn số |
| **5** | Mọi `docs/NN-*.md` có mặt trong **`README.md`** và **`llms.txt`** | Chỉ mục không được lệch khỏi nội dung |
| **6** | Không còn dấu vết soạn thảo (`TODO`, `TBD`, chỗ trống chưa điền, `XXX`) trong `docs/*.md` | Bản công bố không được chứa ghi chú nội bộ |

**Nguyên tắc thiết kế:** chỉ kiểm thứ **kiểm được bằng máy**. Bốn quy ước còn lại của `AGENTS.md` (một ý một câu, kết luận trước, callout thay đoạn văn, tiếng Việt) là phán đoán — nhét vào đây sẽ sinh báo sai, và báo sai làm người ta tắt cổng.

Đã thêm vào `docs.yml` làm **bước thứ năm** của job `verify`, chạy **trước** các cổng nặng vì nó rẻ và bắt lỗi biên tập sớm. Bốn cổng cũ giữ nguyên thứ tự và điều kiện chạy.

**Một thay đổi kéo theo, phải khai báo:** `docs/08` được thêm dòng `> **Tài liệu sống:**` ngay sau bảng thông tin đầu trang, để thoả quy ước 1. Dòng đó nằm **sau** khối tiêu đề mà `build_legal_brief.py` đọc nên PDF không đổi — **đã dựng lại trên máy**: md5 vẫn `a15a92b8…b3beb`, **đúng 1 trang**. Nếu md5 đổi thì thay đổi này phải **bị rút lại**, không phải cập nhật PDF.

---

## 5. Bốn thứ **phải từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Gọi `FastChat` là "agent của Arena" | §1.1 — hạ tầng Battle Mode, **không có vòng lặp công cụ**. Gọi sai tên sẽ khiến ta bắt chước nhầm kiến trúc |
| **R2** | Dùng **causal tracing** để chấm điểm tài liệu nội bộ | Arena dùng với *hàng triệu* phiên thật; Game9K có **`0`** phiên. Thống kê nhân quả trên `0` quan sát là trang trí |
| **R3** | Cho agent **tự chọn và tự đổi model giữa phiên** | Arena làm được vì họ **đo** model. Game9K không đo ⇒ đổi model giữa việc là **mất tái lập**, đúng thứ repo này dùng PDF trùng byte để chống |
| **R4** | **Bật connector theo lượt** cho tác nhân có quyền ghi repo | Tốt cho **đọc**. Với quyền **push**, connector bật nhầm một lượt là một commit sai. Giữ nguyên tắc: **một tác nhân, một phạm vi, ghi rõ trong PR** |

> **R2 và R3 là hai chỗ dễ bắt chước nhất và cũng sai nhất.** Cả hai đều là kỹ thuật tốt — trong một hệ **có** dữ liệu và **có** nhu cầu đo model. Game9K không có cái nào.

---

## 6. Kiểm chứng cổng mới

Đã **thử làm đỏ** bằng năm phép phá, chạy thật trên repo này:

| # | Phá gì | Cổng báo (nguyên văn) |
|---|---|---|
| 1 | Xoá dòng `> **Tài liệu sống:**` khỏi `docs/19` | `19-gitcoin-patterns.md: 8 dòng đầu thiếu …` |
| 2 | Thêm `CREATE TABLE` thứ `35` vào `docs/02` | `tổng CREATE TABLE = 35, cần 34` |
| 3 | Chèn "gần như chắc chắn dẫn đầu thị trường" | `19-gitcoin-patterns.md:34 có từ cấm` |
| 4 | Đổi tiêu đề `### Thứ bậc nguồn sự thật` trong `AGENTS.md` | `AGENTS.md: mất mục …` |
| 5 | Thêm `docs/25-tam-thoi.md` mà không vào chỉ mục | `không có trong README.md` + `llms.txt` |

Sau khi phục hồi: **`85` kiểm tra, `0` vi phạm**. Mỗi thông điệp nêu **tên file** — đó là điều kiện để người ta sửa thay vì tắt cổng.

**Một chi tiết đáng ghi lại:** phép đếm `CREATE TABLE` ban đầu ra **`37`** vì nó tính cả hai câu *mô tả* cổng này trong `docs/22` và `docs/24`. Cách sửa **sai** là nâng ngưỡng lên `37` — thế là cổng tự vô hiệu. Cách đúng: đếm **nghiêm** (đầu dòng, bỏ bảng Markdown) và **khai báo tường minh** hai tài liệu quy trình nằm ngoài phép đếm.

> Đúng bài học `docs/22` **A1**: một bất biến bị "nới cho vừa lỗi hiện tại" thì không còn là bất biến. Khi cổng báo sai, sửa **phép đếm**, không sửa **ngưỡng**.

---

## 7. Việc **không** làm trong tài liệu này

- Không đổi thứ tự hay điều kiện chạy của bốn cổng cũ trong `docs.yml` — chỉ **thêm** một bước.
- Không đổi `W = 0,60` / `H = 180`, whitepaper, deck, 4 PDF, schema (**`34`** bảng).
- Không mô tả Agent Mode như thể đã đọc mã nguồn của nó.
- Không đưa số sao/ngày tháng nào không lấy từ GitHub API trong phiên này.

## 8. Thứ tự làm tiếp

| # | Việc | Vì sao |
|---|---|---|
| **1** | **Decision trace** (`docs/22` A4) — JSON + trang đọc được cho mỗi epoch/phiên bị lọc | Nợ lớn nhất; phục vụ khiếu nại, kiểm toán, `docs/19` §4.3 |
| **2** | Thêm cổng 7: `docs/21` §4 đã yêu cầu **đo bundle trong CI** | Chặn tranh luận `255` hay `352` KB bằng một con số |
| **3** | Bench sống đầu tiên cho PoP (D1/D7 + tỉ lệ lọc oan) | `docs/22` A3 — mọi cổng hiện tại là *test*, **`0`** là *bench* |
