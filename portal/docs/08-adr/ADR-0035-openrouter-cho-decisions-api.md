# ADR-0035 — OpenRouter cho lớp ra quyết định: **nhà cung cấp thứ hai, không phải quan toà**

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`decisions-openrouter.mjs`](../../scripts/lib/decisions-openrouter.mjs) · [`gate_decide.mjs`](../../scripts/gate_decide.mjs) · [`decisions.mjs`](../../scripts/lib/decisions.mjs) · [`ADR-0029`](ADR-0029-gemini-decisions-api-cho-gate.md) · **Q62**

> Nguồn đọc: [`openrouter.ai/docs/guides/community/jev`](https://openrouter.ai/docs/guides/community/jev) ·
> [`jev-tutorial`](https://openrouter.ai/docs/guides/community/jev-tutorial) ·
> [`multimodal-decisions`](https://openrouter.ai/docs/guides/community/multimodal-decisions)
> — tài liệu công khai, đọc để **hiểu hình dạng dữ liệu**. **Không chép mã**, không suy ra
> rằng OpenRouter đã xem xét hay xác nhận gì về MetaPump. Xem §7.

---

## 0. Trả lời ngắn

| | |
|---|---|
| OpenRouter có gì dùng được | `POST /api/alpha/decisions` — cùng bộ primitive `noul`/`choice`/`score` mà `decisions.mjs` đã dùng cho Gemini |
| Áp vào đâu | **Lớp thứ hai** cho cùng một việc: đọc `P0x-signoff.md`, trả **phân bố**, không trả văn xuôi |
| Có thay Gemini không | ❌ **Không.** Đây là *seam* thứ hai, không phải bản thay thế. Cả hai cùng tồn tại |
| Có làm gate tự pass không | ❌ **Không.** `mayQuyet: false` ở **mọi** nhánh, kể cả `0.999` |
| Có chạy trong CI không | ❌ **Không.** CLI xử lý `--dry-run` **trước** khối `CI`; gọi thật trong CI ⇒ thoát 2 (§6.6 kế thừa ADR-0029) |
| Có thêm dependency không | ❌ **Không.** 0 import. `fetch` do người gọi tiêm |
| Đã chạy thật chưa | ❌ **CHƯA.** Sandbox không có `OPENROUTER_API_KEY`. §6 nói rõ điều này |
| Có phải "AI chấm điểm" không | ❌ **Không.** Jev **không phải LLM**; đây là bộ phân loại có xác suất, không sinh chữ |

---

## 1. Bối cảnh — vì sao cần seam thứ hai

[`ADR-0029`](ADR-0029-gemini-decisions-api-cho-gate.md) đã chốt: dùng Decisions API để **đọc**
tệp signoff và nói chỗ nào chưa chắc, với ba ràng buộc — không sinh văn xuôi, không tự tick,
không chạy trong CI. Cả ba vẫn giữ nguyên.

Vấn đề của một nhà cung cấp duy nhất là **vận hành**, không phải kỹ thuật: nếu
`generativelanguage.googleapis.com` đổi hình dạng, hết quota, hoặc khoá bị thu hồi, thì toàn
bộ tính năng đọc-gate tắt — và tệ hơn, người dùng có thể bị dụ sang một đường khác mà không
biết. Khi cả hai khoá cùng tồn tại, chọn ngầm một nhà cung cấp là **một quyết định không ai
bấm nút**. Đã chứng minh bằng thực nghiệm (§6.1): bản đầu tiên trả `gemini` mà không nói gì.

OpenRouter hấp dẫn vì nó phục vụ **đúng bộ primitive** đó — `noul` (có/không), `choice` (chọn
một trong danh sách), `score` (thang bậc có thứ tự) — nên phần lớn mã đọc kết quả dùng lại
được, và ngữ nghĩa "trả phân bố, không trả chữ" giữ nguyên.

---

## 2. Quyết định

**Nhận OpenRouter làm seam thứ hai cho lớp ra quyết định, sau một cờ chọn tường minh, với
ba bất biến:**

1. **Không bao giờ chọn ngầm.** Có hai khoá mà không truyền `--provider` ⇒ `ProviderError`
   với `code: 'ambiguous_provider'`, CLI thoát **2**. Không "đoán cho tiện".
2. **Không fallback im lặng.** Chọn `--provider openrouter` mà thiếu khoá ⇒ `no_key`, thoát
   **2**. Không lặng lẽ quay về Gemini.
3. **Không tự tick.** `hintFor()` trả `mayQuyet: false` ở mọi nhánh. Không có ngưỡng nào biến
   một con số thành chữ ký.

Ngoài ra, khoá API **chỉ đi trong header**, không bao giờ vào thân request — có test quét
chuỗi đã serialize để tìm `apiKey`/`Bearer`/`x-goog`.

---

## 3. Khác biệt wire-format so với Gemini (đã mã hoá, không phải giả định)

| | Gemini (`decisions.mjs`) | OpenRouter (`decisions-openrouter.mjs`) |
|---|---|---|
| Endpoint | `generativelanguage.googleapis.com/...` | `https://openrouter.ai/api/alpha/decisions` |
| Xác thực | `x-goog-api-key: <key>` | `Authorization: Bearer <key>` |
| Trường văn bản | `input` | `state.artifact` |
| Câu `score` | `levels: [...]` | `criteria: [...]` (**mảng** cùng nghĩa) |
| Model mặc định | (theo ADR-0029) | `typesafe/jev-1.14` |
| Chi phí | không có trong phản hồi | `usage.cost` — **con số tiền duy nhất** trong tính năng, và nó do nhà cung cấp trả |

`OR_BANDS` được **assert bằng nhau** với `BANDS` của `decisions.mjs`: hai nhà cung cấp không
được phân dải khác nhau, nếu không thì "đạt" ở đường này lại là "hỏi" ở đường kia.

---

## 4. Phân dải `score` — điều tôi **đã đo** và điều tôi **không biết**

`bandForScore()` đọc **phân bố** (`probabilities`), không đọc trường `score` đã trộn.

| Nhánh | Luật |
|---|---|
| `dat` | khối lượng ở bậc **cao nhất** ≥ `high` (0.8) |
| `khong_dat` | khối lượng dồn ở **nửa dưới** thang ≥ `high` (0.8) |
| còn lại | `hoi` |
| không có phân bố | `khong_ro` — không đoán từ `score` |

**Điều đã đo (và nó không như tôi tưởng):** so với cách phân dải theo vị trí trộn chuẩn hoá
`Σ pᵢ·i/(n-1)` cùng ngưỡng, trên **200.000** phân bố ngẫu nhiên (thang 3..6 bậc), hai cách
**lệch 82.755 ca (41,4%)**.

**Điều tôi không biết:** cách nào đúng hơn. Không có nhãn của người để đo; không có gì nói
cách này khớp phán đoán của người ký hơn. Lý do giữ bản phân bố là **kỹ thuật**: nó không
phụ thuộc việc trường `score` được model tính khớp với `probabilities`, và nó không phải viết
lại nếu PO đổi ngưỡng. **Không phải** vì "chính xác hơn".

Xem §6.2 — kết luận đầu tiên của tôi ở đây là **sai**, và nó được rút ra từ một tệp đã bị
đột biến.

---

## 5. Hệ quả

**Được:**
- Có đường thứ hai khi một nhà cung cấp hỏng, sau một cờ tường minh.
- `bandForScore` sửa một điểm yếu thật của ADR-0029 §6.3 (dùng con số trộn thay vì phân bố).
- Phần lớn hình dạng trả về (`{band, hint, mayQuyet, provider}`) dùng chung ⇒ chỗ gọi không
  phải rẽ nhánh.

**Mất / phải chịu:**
- **Alpha.** `/api/alpha/decisions` có thể đổi hình dạng. `readOrAnswer`/`readAnswer` phải
  chịu được thiếu trường, và không được ném lỗi vì một khoá lạ.
- Hai bộ kiểm thử, hai bộ khoá, hai cách hỏng.
- Không có lời hứa nào rằng hai nhà cung cấp cho cùng một dải trên cùng một tệp. Nếu lệch
  nhau, **đó là thông tin**, không phải lỗi cần che — và không nhà cung cấp nào được tự tick.

**Không làm (giữ nguyên ranh giới):**
- Không dùng `/api/v1/chat/completions` hay `/api/v1/responses` cho gate — hai đường đó
  **sinh văn xuôi**.
- Không route gate qua `cloudflare/clef*` — đọc ~2.000 token đầu của `state` rồi **bỏ phần
  còn lại mà không báo lỗi**. Một tệp signoff dài sẽ bị chấm trên phần đầu.
- Không dùng primitive `box` cho gate.
- Không tuyên bố "xác suất đã hiệu chỉnh" cho tới khi có phép đo hiệu chỉnh.

---

## 6. Bằng chứng, và hai lỗi đã mắc

### 6.1 Chọn ngầm nhà cung cấp — cái bẫy, đã chứng minh

Mô phỏng thứ tự ưu tiên ban đầu với **cả hai** khoá trong môi trường và **không** truyền
`--provider`: kết quả là `gemini`, không cảnh báo. Người dùng tưởng mình đang gọi đường này,
thực tế hoá đơn đi đường khác. Đây là lý do tồn tại của `ambiguous_provider` (§2.1) và của
test khoá nó.

### 6.2 Kết luận sai vì đo trên tệp đã bị đột biến — **lỗi thật, đã sửa**

Tôi viết bản nháp §4 với khẳng định "phân bố phân biệt được ca mà `score` trộn làm mất thông
tin". Để kiểm, tôi đo — và nhận **0 ca lệch trong 200.000**, rồi suýt viết vào ADR rằng hai
cách tương đương.

Sự thật: phép đo đó chạy trên **bản đã bị đột biến RT-O2** (thay `lowerHalf` bằng cách vị trí
trộn). Tệp đã bị phá ở vòng đột biến trước, và bản "khôi phục" từ `/tmp/or.bak` **cũng là bản
đột biến** — vì bản sao lưu được tạo sau khi đã phá. Đo lại trên bản đúng: **82.755/200.000
lệch (41,4%)**.

Hai bài học, cả hai đã thành quy tắc:
- **Sao lưu/khôi phục cũng phải được kiểm.** "Đã khôi phục" không phải bằng chứng; `md5sum`
  hai đầu mới là. Vòng đột biến sau đã làm đúng: md5 khớp trước và sau.
- **Một test xanh trên code sai không nói gì.** Bài kiểm tra cũ của tôi khẳng định
  "phân bố quyết định" nhưng lại chọn ca mà cả hai cách cho cùng kết quả — nó không cô lập
  được gì. Phải vét cạn/ngẫu nhiên để biết hai hàm có thật sự khác nhau.

### 6.3 Lỗi dấu phẩy động — **lỗi thật trong code, đã sửa**

Test `[0.7, 0.1, 0.2]` (80% khối lượng ở nửa dưới, đáng lẽ `khong_dat`) trả `hoi`, vì
`0.7 + 0.1 === 0.7999999999999999 < 0.8`. Ngưỡng 0.8 không bao giờ đạt được bằng tổng các
phần lẻ. Đã sửa bằng làm tròn 6 chữ số trước khi so ngưỡng — sai số IEEE-754 ở đây cỡ `1e-16`,
nên `1e-6` dư rộng và không che khác biệt thật. Có test khoá ca này.

Đây là loại lỗi chỉ lộ ra khi test **đi ngược kỳ vọng ban đầu**; nếu tôi chỉ viết test cho ca
mình nghĩ là đúng, nó sẽ nằm im.

### 6.4 Đột biến — cái nào chết, cái nào sống

| Mã | Đột biến | Kết quả |
|---|---|---|
| RT-O1 | có hai khoá thì chọn ngầm một nhà cung cấp | ✅ 1 test đỏ |
| RT-O2 | `lowerHalf` lấy từ vị trí trộn thay vì phân bố | ✅ **2 test đỏ** (sau khi sửa §6.2) |
| RT-O3 | `--dry-run` bị chặn khi có `CI` | ✅ 2 test đỏ |
| RT-O4 | gửi `levels` thay vì `criteria` | ✅ 3 test đỏ |

### 6.5 Chưa chạy thật

Sandbox **không có** `OPENROUTER_API_KEY`. Mọi kết quả trên là **offline**, với `fetch` giả.
Hình dạng phản hồi trong §3 lấy từ **tài liệu**, chưa lấy từ một lời gọi thật.

Để không ai lỡ tin: `decisions-openrouter.test.mjs` có một test **tự vô hiệu** — nó khẳng định
môi trường **không** có khoá. Ai có khoá và chạy bộ test sẽ thấy **đỏ ngay**, buộc phải cập
nhật §6.5 này bằng kết quả thật trước khi tin bất cứ điều gì ở trên.

### 6.6 CI — kế thừa ADR-0029 §6.6

`gate_decide.mjs --dry-run` chạy **trước** khối kiểm `CI`, nên dry-run thành công trong CI
(exit 0) trong khi gọi thật bị chặn (exit 2). Thứ tự này quan trọng: đặt `CI` lên trước sẽ
làm hỏng chính bước kiểm tra mà CI cần chạy.

---

## 7. Ranh giới trung thực

- **OpenRouter không xem xét, không xác nhận, không bảo trợ MetaPump.** Đây là API công khai;
  dùng nó không tạo quan hệ nào.
- **Không phải LLM.** Jev là bộ phân loại có xác suất. Không được mô tả tính năng này là
  "AI viết nhận xét" hay "AI chấm điểm".
- **Không tuyên bố hiệu chỉnh.** Tài liệu nói `confidence` là độ tập trung của phân bố, **không
  phải** độ an toàn của một quy trình. Không có phép đo hiệu chỉnh nào được chạy ở đây.
- **Không chép mã.** Tài liệu OpenRouter là nguồn mô tả hình dạng dữ liệu; mã trong
  `decisions-openrouter.mjs` viết cho repo này.
- **Không gọi đây là "tích hợp OpenRouter"** trong tài liệu người dùng. Nó là *một đường đọc
  gate có thể chọn*, mặc định tắt (không có khoá thì không chạy).

---

## 8. Câu hỏi mở

| | |
|---|---|
| **Q-ADR35-a** | PO có muốn bật seam này không, hay để mã tồn tại nhưng không dùng? |
| **Q-ADR35-b** | Ngưỡng 0.8/0.5 có đúng cho `score` 4 bậc (`muc_do_san_sang`) không? §4 cho thấy đổi ngưỡng làm hai cách lệch nhau nhiều hơn |
| **Q-ADR35-c** | Có cần đo hiệu chỉnh trên tệp signoff thật (có nhãn người) trước khi tin bất kỳ dải nào không? |
| **Q62a** | (từ ADR-0029) Có cho phép gọi mạng từ máy dev không? Đến giờ vẫn chưa trả lời |

---

**Trạng thái:** Proposed. Chưa có lời gọi mạng thật nào. Chưa có tuyên bố nào về độ chính xác.
