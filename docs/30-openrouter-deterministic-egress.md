# OpenRouter: thứ đáng lấy không phải mô hình, mà là **cách nó từ chối**

> **Tài liệu sống:** `docs/30-openrouter-deterministic-egress.md`
> **Trạng thái:** `SCOPING` — đánh giá + **đã dựng khoá xuất mạng** (`scripts/check_egress_lock.py`)
> **Ngày:** 22/11/2026
> **Đầu vào:** `https://openrouter.ai/` + 2 trang tài liệu (`provider-routing`, `byok`)
> **Liên quan:** `docs/25` (cổng quyết định) · `docs/26` · `docs/24` · `AGENTS.md` · `docs/PM` §0 6 cổng HITL

---

## 0. Kết luận trước

**OpenRouter là một nhà định tuyến, không phải một mô hình. Với repo này, giá trị nằm ở chỗ nó làm rõ một câu hỏi mà `AGENTS.md` mới chỉ khẳng định: *cái gì chứng minh cổng là tất định?***

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | OpenRouter là gì? | Một endpoint, 600+ mô hình, tự chọn nhà cung cấp theo **giá/throughput/độ trễ/độ tin cậy** (§1) |
| **2** | Dùng được cho Game9K không? | ❌ **Không cho CI, không cho Arena, không cho SDK.** Ba lý do khác nhau, không phải "sợ" (§2) |
| **3** | Có chỗ nào cần không? | ✅ **Một**: trợ lý **soạn thảo tài liệu**, chạy **ngoài repo**, kết quả vào PR dưới dạng `> Gợi ý chưa kiểm chứng` (§3) |
| **4** | Lấy gì về kỹ thuật? | **Bốn tham số** từ chối định tuyến: `only` · `data_collection: deny` · `zdr` · `max_price` — mỗi cái là một câu trả lời cho một câu hỏi khác nhau (§4) |
| **5** | Đã dựng gì? | `check_egress_lock.py`: **4 bất biến**, **8** kiểm tra — *"chưa có gì gọi mạng"* thành *"được chứng minh là không gọi được"* (§5) |
| **6** | Vì sao quan trọng? | Vì `AGENTS.md` viết **"tất định byte-for-byte"**, và tới hôm nay thứ chứng minh điều đó là **hai CI run xanh**, không phải một tính chất của mã (§5.1) |

---

## 1. Nó là gì — ba con số và một cơ chế

Trang chủ tự công bố: **`800T+`** token/tháng · **`10M+`** người dùng · **`600+`** mô hình *(đều là **tự công bố**, không kiểm được — cùng nhãn với §1.1 của `docs/27`)*.

Cơ chế đáng chú ý nhất là **định tuyến mặc định**. Với mỗi mô hình, OpenRouter chọn nhà cung cấp bằng cách so **cái giá thật** của một câu trả lời tốt ở từng bên, không phải giá niêm yết:

- **Effective price** — giá thật, tính cả tỉ lệ cache hit và tỉ lệ input/output thực tế
- **Throughput** (token/giây) · **TTFT** (thời gian tới token đầu) · **tỉ lệ 429** · **độ tin cậy** · **chất lượng tool call**

> Cùng một `model` + cùng một prompt có thể được **hai nhà cung cấp khác nhau** phục vụ ở hai lần gọi. Đó là **tính năng** với một ứng dụng chat. Với **một cổng** thì đó là **định nghĩa của không tất định**.

---

## 2. Ba chỗ **không** dùng — và ba lý do khác nhau

| Chỗ | Có dùng? | Lý do kỹ thuật |
|---|---|---|
| **CI `docs.yml`** (10 cổng) | ❌ | Cổng phải cho **cùng kết quả với cùng input**. Một judge LLM cho `0.66` hôm nay và `0.71` mai là một cổng **không đo được gì**. §5 biến điều này thành luật máy kiểm. |
| **Arena Blind Duel** (`docs/PRD` FR-ARN-01) | ❌ | Arena chấm bằng **người chơi thật** + `openskill`/Bradley-Terry (`docs/00` §2.3). Thay người bằng LLM là **phá luận điểm của sản phẩm**, không phải tiết kiệm chi phí. |
| **`game-sdk`** (iframe) | ❌ | `docs/27` §6 R1 + `docs/29` §3: SDK chỉ `postMessage`, **cấm** `fetch`. Thêm một client HTTP vào iframe là mở lại đúng lỗ đã bịt. |
| **Trợ lý soạn thảo, ngoài repo** | ✅ | §3 |

---

## 3. Chỗ **duy nhất** dùng được — và ba điều kiện

Nếu cần một mô hình để **đọc lại** một PR tài liệu (không phải để chấm cổng): chạy **ngoài repo**, **không có quyền ghi**, kết quả dán vào PR dưới dạng bình luận có nhãn.

| Điều kiện | Vì sao |
|---|---|
| **1. Kết quả không bao giờ là cổng** | Cùng nguyên tắc `docs/25` §5: máy = cổng tất định; người = chữ ký. LLM không thuộc cả hai. |
| **2. Mọi câu nó nói phải trỏ về câu `source`** | Nếu không trích được dòng, đó là **gợi ý**, không phải **phát hiện** — và phải ghi đúng như vậy. |
| **3. Không có khoá trong repo, không có khoá ở máy dev** | `AGENTS.md`: *"Thông tin định danh cá nhân, khoá API… không bao giờ commit"*. Khoá ở **máy người chạy**, không ở CI. |

> **Điều kiện thứ tư, ít ai nghĩ tới:** tài liệu Game9K chứa **số liệu tài chính chưa công bố**. Gửi nguyên một PR lên một nhà định tuyến nghĩa là nó có thể dừng ở **nhà cung cấp nào cũng được**. Nếu ai đó làm việc này, họ phải đặt `provider.data_collection: "deny"` và `zdr: true` — xem §4.

---

## 4. Bốn tham số đáng chép — vì mỗi cái là một câu trả lời khác nhau

Tài liệu `provider-routing` liệt kê 14 trường. Bốn trường dưới đây **không** phải về hiệu năng; chúng là **bốn câu hỏi quản trị**, và Game9K nên viết câu trả lời của mình ra thay vì để mặc định.

| Tham số | Mặc định | Câu hỏi nó trả lời | Câu trả lời cho Game9K |
|---|---|---|---|
| `only: [...]` | — | *Ai **được phép** phục vụ?* | Repo không có allowlist này ⇒ **im lặng cho phép tất cả**. Ghi rõ: `only` phải liệt kê tường minh. |
| `data_collection` | **`"allow"`** | *Nhà cung cấp có được **lưu dữ liệu** không?* | Mặc định là **cho phép**. Với tài liệu tài chính: **`"deny"`**. |
| `zdr: true` | — | *Chỉ dùng endpoint **không lưu**?* | Bật, nếu có dùng thật. |
| `max_price` | — | *Trần chi phí cho **một** request?* | Cần trần, không cần dự báo. |

> **Bài học chung:** ba trong bốn thứ trên có **mặc định nguy hiểm** (`allow`, không allowlist, không trần). Đây là cùng loại bẫy với `docs/27` §2.2 (`Promise<void>` không nói được gì) — **một mặc định không nói ra là một quyết định không ai ký**.

### 4.1. BYOK — con số để **ghi**, không để **dùng**

Tài liệu `byok` ghi: dùng khoá nhà cung cấp riêng tốn **`5%`** so với giá thường trên OpenRouter, trừ vào credit; hạn mức miễn phí **`$25.000`**/tháng với gói trả theo mức dùng.

> **Không đưa `5%` hay `$25.000` vào mô hình tài chính.** Đây là phí của **một nhà cung cấp cho một luồng không tồn tại** trong Game9K. Cùng nguyên tắc `docs/27` §1.1 (phí `5%` của Xsolla) và `docs/28` §6 R3.

---

## 5. Đã dựng: khoá xuất mạng

```bash
python3 scripts/check_egress_lock.py            # 4 bất biến
python3 scripts/check_egress_lock.py --audit    # liệt kê mọi điểm có thể ra mạng
```

```
EGRESS LOCK: PASS — 8 kiểm tra · 4 bất biến · 14 tệp Python không có HTTP client · 1 workflow không gọi dịch vụ AI
```

### 5.1. Vì sao cần cổng này — câu `AGENTS.md` chưa được chứng minh

`AGENTS.md` viết cổng là **"tất định byte-for-byte"** và hướng dẫn kiểm bằng cách dựng vào **hai font cache** rồi so `md5`. Đó là kiểm **kết quả**. Nhưng không có gì kiểm **cơ chế**: một dòng `fetch(...)` thêm vào `build_pitch_deck.py` vẫn cho hai `md5` giống nhau trên máy này, và **khác** trên máy có mạng chậm. Từ hôm nay, dòng đó làm cổng **đỏ**.

### 5.2. Bốn bất biến — đọc từ mã, không tin lời khai

| # | Bất biến | Nó bắt được gì |
|---|---|---|
| **1** | Không thư viện HTTP trong `scripts/*.py` | `requests`, `httpx`, `urllib.request`, `socket`, `openai`, `anthropic`, `genai`… |
| **2** | Không workflow nào nhắc dịch vụ AI | `openrouter`, `api.openai.com`, `OPENROUTER_API_KEY`… |
| **3** | Chỉ 5 action ngoài `actions/*`… thực ra: **allowlist 5 tên**, gồm `softprops/action-gh-release` | Mỗi action chạy bằng **token của repo**; thêm một action là thêm một chương trình không ai review |
| **4** | Mọi bước trong workflow có `run:` hoặc `uses:` | Không có "hộp đen" — bước không đọc được nó làm gì |

`urllib.parse` **được phép** (xử lý chuỗi, không mở socket). Đây là chỗ dễ viết luật quá rộng rồi tự chặn mình.

### 5.3. Bốn phép phá đã chạy thật

| # | Phá | Kết quả |
|---|---|---|
| 1 | thêm `import requests` vào `check_specs.py` | ❌ `import requests — thư viện HTTP` |
| 2 | workflow có `OPENROUTER_API_KEY` | ❌ **2** lỗi: `openrouter` + tên biến |
| 3 | thêm `some-org/ai-reviewer@v2` | ❌ `action ngoài allowlist` |
| 4 | bỏ `run:` của một bước | ❌ `17 bước nhưng chỉ 16 run: + 0 uses:` |

Phép phá 4 là loại khó nhất: nó không bắt một chuỗi xấu, nó bắt **một bước không đọc được**.

### 5.4. `--audit` — nói thẳng chỗ chưa kiểm

`scripts/` có **4** tệp import thư viện ngoài chuẩn: `reportlab`, `fontTools`, `pypdf`, `pypdfium2`. Chúng là thư viện **dựng PDF**, không mở socket — nhưng cổng này **không chứng minh** điều đó, nó chỉ chứng minh *không có HTTP client*. `--audit` in ra đúng bốn dòng đó để người đọc tự xác nhận.

> **Đây là giới hạn thật của cổng, và phải nói ra** — cùng chuẩn với `docs/29` §2.3 (E2B tự ghi giới hạn của phép phân biệt lỗi) và `docs/28` §4 (hash bề mặt không chứng minh hành vi).

---

## 6. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Dùng LLM làm **một trong 10 cổng** | §2 — cổng phải cùng input → cùng output; §5 khoá điều này bằng máy |
| **R2** | Dùng LLM chấm **Arena** | `docs/PRD` FR-ARN-01 chấm bằng người thật + `openskill`; thay bằng LLM là phá luận điểm sản phẩm |
| **R3** | Thêm client HTTP vào `game-sdk` | `docs/27` §6 R1, `docs/29` §3 — SDK chỉ `postMessage` |
| **R4** | Đưa `5%` BYOK / `$25.000` vào `WHITEPAPER` §7 | §4.1 — phí của một luồng không tồn tại trong Game9K |

---

## 7. Việc **không** làm trong tài liệu này

- Không thêm phụ thuộc; không có khoá nào trong repo; không gọi mạng trong CI.
- Không sửa `docs/03`, không sửa `docs/PRD` §0, không đổi 6 cổng HITL.
- Không đổi số đã kiểm (`12 KB`, `3,5 s`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không dựng lại 4 PDF.

## 8. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | Nếu dùng trợ lý soạn thảo: viết **allowlist `only`** và `data_collection: "deny"` vào SOP nội bộ, không vào repo | §4 — ba mặc định nguy hiểm phải được trả lời tường minh |
| **2** | Ghi **giới hạn của `check_egress_lock.py`** vào `AGENTS.md`: nó chứng minh *không có HTTP client*, không chứng minh *không có socket trong thư viện dựng PDF* | §5.4 — một cổng không nói giới hạn của mình là một cổng bị tin quá mức |
| **3** | Nếu sau này có `apps/web` gọi mô hình cho **tính năng người dùng**, đặt `data_collection: "deny"` + `zdr` + `max_price` và đưa vào `docs/03` §2 như một endpoint có rate limit | §4 — trần chi phí phải ở tầng API, không ở tầng client |
| **4** | Không mở BYOK cho studio | Không có ai trong Game9K cần khoá nhà cung cấp riêng; thêm là thêm chỗ giữ bí mật |
