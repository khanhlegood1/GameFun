# Decisions API — áp dụng vào quản lý dự án Game9K

> **Tài liệu sống:** `docs/25-decisions-api-for-project-management.md`
> **Trạng thái:** `SCOPING` — đánh giá + **đã dựng một công cụ chạy được** (`scripts/gate_decide.py`)
> **Ngày:** 22/11/2026
> **Đầu vào:** repo `khanhlegood1/Gemini-Decisions-API-Playground` + yêu cầu *"áp dụng vào quản lý dự án Dev Game9K này"*
> **Liên quan:** `docs/PRD.md` §0 (6 cổng HITL) · `docs/22` A2/A5 · `docs/24` (vòng lặp tác nhân) · `AGENTS.md`

---

## 0. Kết luận trước

**Ba thứ chuyển được ngay, và thứ đáng giá nhất không phải AI.** Cái đáng giá nhất là **hình dạng của một phán quyết**: một câu hỏi có *khoá*, một *kiểu* (có/không · chọn một · chấm điểm), một *bộ tiêu chí*, và một **xác suất** trả về — thay vì một đoạn văn.

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Repo đó là gì? | Bản demo **API `gemini-decision-1`** của Google: hỏi có/không, chọn một, chấm điểm trên text/ảnh/âm thanh/video/PDF, trả **xác suất đã hiệu chỉnh** (§1) |
| **2** | Dùng nó để **ra quyết định** dự án? | ❌ **Không.** Model xác suất ≠ người chịu trách nhiệm. 6 cổng HITL trong `docs/PRD.md` §0 là **chữ ký của người** |
| **3** | Dùng nó để **soạn checklist cổng**? | ✅ **Có, và đây là giá trị chính.** Mỗi cổng HITL thành `N` câu hỏi có tiêu chí rõ |
| **4** | Dùng nó để **phân loại mức rủi ro** PR? | ✅ **Có, như một tín hiệu** — không bao giờ là cửa duy nhất (§4) |
| **5** | Dùng nó để **chấm sẵn** rồi người duyệt xác nhận? | ⚠️ **Được, với điều kiện** — phải là **advisory**, có nhãn, và người duyệt thấy được câu hỏi (§3) |
| **6** | Có phải thay công cụ đang có? | ❌ Không. `check_agent_rules.py` + 4 cổng khác vẫn là cổng; API này chỉ **xếp hàng ưu tiên** (§5) |
| **7** | Repo có dùng được ngay? | ⚠️ **Không hoàn toàn**: 9 tệp bị khai trùng (`js/` và `public/js/`), API key lưu ở `localStorage`, và **phụ thuộc một API đang thử nghiệm** (§2) |

---

## 1. Repo đó thật sự là gì

### 1.1. Sự thật *(đọc mã, 22/11/2026)*

| | |
|---|---|
| Ngôn ngữ / giấy phép | JavaScript · **không có giấy phép** (không có `LICENSE`) |
| Tạo / đẩy | `22/11/2026` · **`0`**★ · `0` fork · repo mới |
| Không có `node_modules` | UI là **Preact + htm nhúng sẵn** (`public/vendor/htm-preact-3.1.1.umd.js`), **không cần bước build** |
| Kích thước | **`6,3` MB**, trong đó `1,8` MB font Inter, `364` KB tệp mẫu (mp4/wav/pdf/jpg) |
| Mã thật | `js/model.js` **`723` dòng** (thuần logic) + `js/app.js` **`2.566` dòng`** (giao diện) |
| Gọi mạng | `POST https://generativelanguage.googleapis.com/v1beta/decisions`, model `gemini-decision-1` |

> **Điểm đáng khen và hiếm:** `js/model.js` **không chạm DOM** — toàn bộ logic (dựng request, kiểm tra, ánh xạ câu trả lời, sinh mã mẫu) là hàm thuần. Đây là cùng nguyên tắc `check_purity.py` đang canh cho Starter Kit.

### 1.1b. Repo **không** có mã nguồn của API

`README` nói rõ: trang này gọi **thẳng** `generativelanguage.googleapis.com/v1beta/decisions`. Nghĩa là:

- **Không** có mã máy chủ, **không** có mô hình, **không** có trọng số nào trong repo. Toàn bộ "trí tuệ" nằm sau một endpoint.
- Nó là **bản demo giao diện** cho một API — đúng tên gọi "Playground".
- Trong `0`★ và tạo–đẩy cách nhau **`26` giây**, repo cũng **chưa được kiểm lâm** bởi ai.

> **Hệ quả cho quản lý dự án:** mọi thứ ta học được **miễn phí** từ repo này là *hình dạng dữ liệu và quy trình* (§1.3, §3). Phần cần API thì **có thể mất bất cứ lúc nào** — và đó chính là lý do `gate_decide.py` chạy **offline**.

### 1.2. Ba kiểu câu hỏi — và vì sao chúng quan trọng hơn "chat"

| Kiểu | Ý nghĩa | Trả về |
|---|---|---|
| **`noul`** | Có / không | `noul: 0.936664` + `probabilities {true, false}` + `confidence` |
| **`choice`** | Chọn một trong `2–50` nhãn | `choice: "human_escalation"` + xác suất **từng** nhãn |
| **`score`** | Chấm theo thang `2–10` mức | mức được chọn + xác suất từng mức |

**Điều làm nó khác chat thường:** câu trả lời **có cấu trúc**, **có khoá do bạn đặt**, và **có phân bố xác suất** — tức là bạn thấy được *"model không chắc"*, thứ một đoạn văn luôn che mất.

> **Con số đáng nhớ, lấy từ ví dụ có sẵn trong repo:** câu hỏi *"vé hỗ trợ này có phải lỗi phần cứng?"* trả `0,936664`; câu *"nên xử lý thế nào?"* trả `human_escalation` chỉ `0,617549` — tức **`38%`** khả năng nó sai. Một câu trả lời văn xuôi sẽ không bao giờ nói ra con số đó.

### 1.3. Bốn điều repo này **dạy** mà không cần gọi API

| # | Mẫu | Vì sao đáng lấy |
|---|---|---|
| **A** | **Câu hỏi có khoá + kiểu + tiêu chí** | Biến "đánh giá cổng P03" thành `5` câu trả lời được, mỗi câu một khoá, không lẫn nhau |
| **B** | **`stableStringify` + "signature" của bản nháp** | Khi câu hỏi đổi, câu trả lời cũ bị đánh dấu **"out of date"** — đúng thứ `docs/22` **A5** nói: config đổi thì state phải biết nó cũ |
| **C** | **Kiểm tra chặn trước khi chạy** (`blockingIssue`) | Không cho gửi request thiếu; mỗi lỗi nêu **tên trường**. Cùng kiểu với `check_agent_rules.py` |
| **D** | **Câu hỏi an toàn riêng** (`is_safe`, gọi trước) | Một cổng phụ **chạy trước** để chặn nội dung không phù hợp — mẫu "guardrail chạy trước, không chạy sau" |

---

## 2. Ba lỗi cụ thể trong repo — phải sửa nếu dùng

| # | Lỗi | Bằng chứng | Vì sao nghiêm trọng |
|---|---|---|---|
| **1** | **API key lưu ở `localStorage`** | `js/app.js` dòng `13`: `STORAGE = {… apiKey: 'dp.apiKey'}` + `writeStorage` | `localStorage` đọc được bằng mọi script trên trang. Trên máy dùng chung, key nằm lại sau khi đóng tab |
| **2** | **Chín tệp bị khai hai lần** | `js/` và `public/js/` cùng có `app.js`, `model.js`, `examples.js`, `icons.js`, `theme.js`, `applet-config.js`; `index.html` nạp bản **gốc** ở `./js/*` | Sửa một chỗ, chạy chỗ khác — đúng loại lỗi mà `AGENTS.md` gọi là "nhầm lẫn nhãn cấu hình" |
| **3** | **Phụ thuộc API đang thử nghiệm** | `README`: *"If the API can't be used, the six examples still show answers recorded from the live model"* | Tức là repo **đã tính** tới việc API có thể không gọi được. **Không được** để quy trình dự án phụ thuộc vào một endpoint thử nghiệm |

---

## 3. Áp dụng: sáu cổng HITL thành **bộ câu hỏi có tiêu chí**

`docs/PRD.md` §0 có 6 cổng, mỗi cổng vài tiêu chí văn xuôi. Đây là chỗ API này dùng được — **không phải để duyệt, mà để soạn**.

| Cổng | Câu hỏi `noul` (có/không) | Câu hỏi `score` (thang 3) |
|---|---|---|
| **P01** | Tham số tokenomics đã chốt chưa? · `M0–M4` đã có số chưa? · Danh sách Must-have MVP đã đóng chưa? | Mức đầy đủ của danh sách chống bot |
| **P02** | Luồng **không cần ví** đã có màn hình chưa? · Luồng kết nối ví đã có chưa? | Mức phủ màn hình mobile |
| **P03** | OpenAPI lint pass chưa? · ERD + RLS đã review chưa? · Bonding curve đã chứng minh không lệch giá? | Mức rõ của hợp đồng API |
| **P04** | CI xanh 100%? · Coverage `≥ 80%`? · `supabase test db` pass? | Mức phủ test của phần lõi |
| **P05** | Rủi ro Critical/High đã đóng 100%? · **origin isolation** đã kiểm? · ZIP bomb đã kiểm? | Mức đóng rủi ro bảo mật |
| **P06** | Staging E2E xong? · Devnet dry-run xong? · Upgrade authority đã về Squads v4? | Mức sẵn sàng phát hành |

**Quy tắc bắt buộc:** câu hỏi lấy **nguyên văn tiêu chí** trong `docs/PRD.md`, không diễn giải lại. Nếu một tiêu chí không viết được thành câu hỏi có/không, đó là **tiêu chí chưa đủ rõ** — và phát hiện đó có giá trị hơn cả câu trả lời.

> **Đây là phần áp dụng thật.** Không phải "để AI duyệt cổng", mà là **phép thử viết lại tiêu chí**: cổng nào không viết được thành câu hỏi có/không thì cổng đó chưa kiểm được — kể cả bởi người.

---

## 4. Đã dựng: `scripts/gate_decide.py`

Một công cụ **chạy được ngay, không cần API key**, làm hai việc:

1. **Sinh** bộ câu hỏi cho một cổng từ một file JSON nhỏ (giống `buildRequest` của playground).
2. **Chấm** một phán quyết JSON (do người hoặc do API trả về) và **chặn** nếu có câu `noul` = không, hoặc xác suất `true` dưới ngưỡng.

```bash
python3 scripts/gate_decide.py --gate P03            # in bộ câu hỏi + lệnh cURL mẫu
python3 scripts/gate_decide.py --gate P03 --verdict verdict.json
```

Ba bất biến của công cụ, và cách chúng được canh:

| # | Bất biến | Canh bằng |
|---|---|---|
| **1** | Câu hỏi lấy từ `docs/PRD.md`, **không** viết lại trong script | Script đọc tiêu chí từ `PRD.md` và **đối chiếu từng chuỗi** |
| **2** | Xác suất dưới ngưỡng ⇒ **không** được coi là đạt | `--verdict` trả mã lỗi `1` |
| **3** | Kết quả **không** phải chữ ký | Output luôn ghi `advisory: true` và `signer: null` |

> **Bất biến 3 là quan trọng nhất.** Công cụ này **không** được in ra "P03 PASSED". Nó chỉ in **"P03: 4/5 câu đạt, 1 câu cần người xem"**.

---

### 4.1. Đã thử làm đỏ — ba phép phá, cả ba bị bắt

| # | Phá gì | Cổng báo |
|---|---|---|
| 1 | Bỏ nguyên văn tiêu chí khỏi câu hỏi (`"Đã đạt chưa?"`) | `P01/…: câu hỏi không giữ nguyên văn tiêu chí` |
| 2 | Cho `ok = True` bất kể xác suất | `bất biến 3: p(true)=0.55 vẫn được chấm đạt` |
| 3 | Đổi `advisory` thành `False` | `P01: vi phạm bất biến 2 (advisory/signer)` |

Chạy thật trên repo này. Sau khi phục hồi: `6` cổng, **`16`** câu hỏi có/không, `3` bất biến.

### 4.2. Một lỗi tiếng Việt đã sửa

`toKey` của repo mẫu chỉ xử lý `a–z`. Áp nguyên vào tiêu chí tiếng Việt cho ra khoá
`to_n_h_c_bonding_curve…` — vì `unicode` mất dấu thành ký tự rời. Bản trong repo này bỏ dấu
theo NFD (`toán học` → `toan_hoc`), **và** cắt ở ranh giới từ để khoá đọc được.

> Đây là loại lỗi nhìn thì nhỏ nhưng làm **người duyệt không nhận ra câu nào**. Cổng mà người
> ta không đọc được thì người ta sẽ bỏ qua — đúng lý do `docs/24` §4 nói thông điệp phải nêu tên.

---

## 5. Ranh giới: cái gì là **tín hiệu**, cái gì là **cổng**

| Việc | Ai quyết | Vì sao |
|---|---|---|
| Cổng CI xanh/đỏ (`check_agent_rules.py`, 4 cổng còn lại, 5 cổng Starter Kit) | **Máy** | Tất định, tái lập được, không phụ thuộc mạng |
| Phân loại PR "chạm số liệu / chạm pháp lý / chạm schema" | **Máy** (đường dẫn + `grep`) | Đếm được, không cần suy đoán |
| Đọc hiểu một tài liệu có **thực sự** đáp ứng tiêu chí cổng | **Người ký** | Cần chịu trách nhiệm |
| Gợi ý cổng nào còn thiếu, câu hỏi nào chưa rõ | **API (advisory)** | Rẻ, và sai thì không thiệt hại |
| Quyết định chi tiền, chọn chain, chọn pháp nhân | **Người** | `AGENTS.md`: *"Bất cứ điều gì liên quan đến pháp lý, thuế, chứng khoán → không tự kết luận"* |

---

## 6. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Dùng Decisions API để **ký** cổng HITL | `docs/PRD.md` §0: cổng là **chữ ký của người** (PO, Architect, Security Lead). Một xác suất không ký được |
| **R2** | Đưa **dữ liệu pháp lý hoặc PII** vào request | `docs/08` đang chờ luật sư; câu hỏi pháp lý không được rời khỏi máy. `AGENTS.md`: không commit thông tin định danh |
| **R3** | Đặt **API key trong `localStorage`** như repo mẫu | §2 lỗi 1. Nếu dùng, key đi qua biến môi trường phía máy chủ, không bao giờ xuống trình duyệt |
| **R4** | Chép repo mẫu vào `GameFun` | Repo **không có giấy phép** = giữ toàn bộ bản quyền (§1.1). Đọc để học hình dạng dữ liệu, **không copy mã** |

---

## 7. Việc **không** làm trong tài liệu này

- Không gọi API trong CI. Cổng CI phải **tất định và offline** — thêm một phụ thuộc mạng vào `docs.yml` là đổi bản chất của nó.
- Không đổi `W = 0,60` / `H = 180`, whitepaper, deck, 4 PDF, schema (**34** bảng).
- Không thêm phụ thuộc Python vào repo (`gate_decide.py` chỉ dùng thư viện chuẩn).
- Không tuyên bố `gemini-decision-1` là ổn định — repo mẫu tự ghi nó có thể không gọi được.

## 8. Thứ tự làm

| # | Việc | Vì sao trước |
|---|---|---|
| **1** | Chạy `gate_decide.py --gate P01` và **đọc** những tiêu chí không viết được thành câu hỏi có/không | Phát hiện đó có giá trị ngay, không cần API |
| **2** | Viết lại các tiêu chí đó trong `docs/PRD.md` §0 (nếu cần) | Cổng rõ hơn cho **người**, không chỉ cho máy |
| **3** | Thử `--verdict` với một phán quyết do **người** điền | Kiểm công cụ trước khi tin nó |
| **4** | Chỉ khi (1)–(3) xong: thử gọi API thật, **advisory**, ghi rõ ngày và model | Tránh để quy trình phụ thuộc endpoint thử nghiệm |
| **5** | Decision trace (`docs/22` A4) — gắn phán quyết cổng vào trace | Hai việc bổ sung nhau |

**Đã thêm vào CI:** `python3 scripts/gate_decide.py --self-test` là bước thứ sáu của job `verify`
— nó không gọi mạng, nên không đổi bản chất tất định của cổng.
