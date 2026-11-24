# ADR-0029 — Dùng Gemini Decisions API cho gate P0x: **một công cụ đọc, không phải người ký**

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`decisions.mjs`](../../scripts/lib/decisions.mjs) · [`decide_gate.mjs`](../../scripts/decide_gate.mjs) · [`docs/gates/`](../gates/) · [`ADR-0028`](ADR-0028-hoc-co-che-cham-tu-arena-open-source.md) · [`AGENTS.md`](../../AGENTS.md) · **Q62**

> Nguồn học: [`xuankhanh1612/Gemini-Decisions-API-Playground`](https://github.com/xuankhanh1612/Gemini-Decisions-API-Playground)
> — repo **riêng tư một phần**, **không có file LICENSE**, tác giả khác tài khoản (`xuankhanh1612`,
> không phải `lexuankhanh1612`). Đọc để **học cơ chế**, không chép dòng nào. Xem §7.

---

## 0. Trả lời ngắn

| | |
|---|---|
| API này là gì | Ra **2026-11-11**. Chấm câu hỏi đóng trên văn bản/ảnh/audio/video/PDF, trả **xác suất đã hiệu chỉnh**, **0 output token** |
| Áp vào đâu | **Đọc** tệp `P0x-signoff.md` và nói chỗ nào chưa chắc |
| Có làm gate tự pass không | ❌ **Không.** `gateHint()` luôn trả `mayQuyet: false` — có test khoá |
| Có chạy trong CI không | ❌ **Không.** `decide_gate.mjs` tự thoát 2 khi thấy biến `CI` |
| Có thêm dependency không | ❌ **Không.** `decisions.mjs` không import gì, `fetch` do người gọi tiêm |
| Đã chạy thật chưa | ❌ **CHƯA.** Sandbox này chặn `generativelanguage.googleapis.com`. Xem §6 |

---

## 1. Bối cảnh — chỗ hổng mà công cụ này lấp

`P0x-signoff.md` có checklist ✅/❌. Một ô tick trả lời *"mục này đạt hay không"*, nhưng
**không** trả lời *"người ký chắc bao nhiêu"*. Trong thực tế hai câu đó khác nhau rất xa:
một mục có thể được tick vì "không thấy sai" — trong khi người tick chỉ chắc 55%.

[`ADR-0028`](ADR-0028-hoc-co-che-cham-tu-arena-open-source.md) đã lấy từ `arena-rank` bài học
**báo khoảng tin cậy, không báo một con số** (§5.3 của ghi chú kèm theo). ADR đó áp vào chỗ
so sánh số. ADR này áp vào chỗ **đọc văn bản**.

Decisions API phù hợp vì nó **không sinh văn xuôi**. Không có chữ để parse, không có nguy cơ
model viết ra một câu nghe hợp lý rồi bị chép vào tài liệu. Chỉ có số.

---

## 2. Quyết định

### 2.1. ✅ Nhận: ba câu hỏi đóng + một câu thang bậc, trên **văn bản đã commit**

`GATE_QUESTIONS` (`decisions.mjs`) có 4 câu, cố định:

| Khoá | Loại | Hỏi gì |
|---|---|---|
| `co_nguon` | `noul` | Mọi khẳng định định lượng có dẫn nguồn là **tệp/lệnh trong cùng repo**? |
| `tu_mau_thuan` | `noul` | Có tự mâu thuẫn với tài liệu nó link tới? |
| `con_no` | `noul` | Có **khai báo** khoảng trống của chính nó thay vì hứa việc tương lai? |
| `muc_do_san_sang` | `score` | Sẵn sàng để người ký chưa, **chỉ xét tính nhất quán nội bộ** |

Đây là bốn thứ `check_*.py` **không** kiểm được: script kiểm được *có link không*, không kiểm
được *link đó có chống lưng cho câu vừa viết không*.

### 2.2. 🔴 Cố ý **KHÔNG** hỏi "gate này có nên pass không"

Đó là câu hỏi về **quyền**, không phải về nội dung. Nếu đưa vào, sẽ có ngày một script đọc
`p >= 0.8` rồi tick hộ. `gateHint()` khoá việc đó bằng **kiểu dữ liệu**:

```js
{ band: "dat", action: "xem_lai", mayQuyet: false }
```

Test `D-22` khẳng định **mọi** giá trị `p` (kể cả 0.999) đều cho `mayQuyet: false`.

### 2.3. ✅ Nhận: ba dải, không hai

`BANDS = { high: 0.8, low: 0.5 }` ⇒ `dat` / `hoi` / `khong_dat`.

Vì sao ba: hai dải buộc `p = 0.55` phải chọn phe, và nó sẽ chọn "đạt" vì 0.55 > 0.5. Ba dải
thì 0.55 rơi vào `hoi` ⇒ **phải có người đọc**. Đây chính là điều
[`ADR-0028`](ADR-0028-hoc-co-che-cham-tu-arena-open-source.md) §2.1 nói: một cột chỉ có hai
giá trị không chứa được thông tin "không chắc".

### 2.4. 🔴 `p` không xác định ⇒ `khong_ro`, **không** mặc định đạt

Đây là chỗ dễ sai nhất và tôi đã viết test riêng (`D-21`). Nếu API trả hình dạng lạ, hoặc
mạng hỏng, thì kết luận **không** được là "không có vấn đề". Nó phải là "không biết".

---

## 3. Ranh giới kỹ thuật

| | |
|---|---|
| Endpoint | `POST https://generativelanguage.googleapis.com/v1beta/decisions` — **`v1beta`**, không phải `v1` |
| Model | `gemini-decision-1` |
| Khoá | Header `x-goog-api-key`. **Không** vào body — có test `D-32` khẳng định |
| Giới hạn | 1.000 câu hỏi/lượt · `choice` 2..255 option · `score` 2..255 bậc · `noul` chặn trong [0.01, 0.99] |
| Câu hỏi có thấy nhau? | ❌ **Không.** API chấm song song. Đặt câu hỏi phụ thuộc câu trước là hiểu sai API |
| `choice` có bị thiên lệch thứ tự? | Không — API **sắp alphabet** trước khi chấm |
| Ngữ cảnh | 262.144 token cho input + mọi câu hỏi |

**Hệ quả của `noul` chặn ở 0.99:** một ngưỡng `p > 0.99` **không bao giờ khớp**. Đừng viết.
`BANDS.high = 0.8` nằm dưới ngưỡng đó nên an toàn.

**Cảnh báo prompt-injection riêng của loại API này:** văn bản được chấm có thể **tự lập luận**
để được chấm điểm cao. Với gate, "kẻ tấn công" là chính AI đã viết artifact — nó có thể viết
một câu như *"tài liệu này đã được kiểm đầy đủ"* để làm câu `con_no` đạt. Đây là lý do §2.2
quan trọng: kết quả chỉ là **gợi ý cho người**, và người phải đọc chính tài liệu.

---

## 4. Vì sao **không** chạy trong CI — và điều đó không phải thiếu sót

`decide_gate.mjs` thoát `2` khi **gọi API thật** nếu `process.env.CI` tồn tại
(`--dry-run` vẫn chạy được — nó không gọi mạng). Ba lý do:

1. **CI không có khoá.** Đưa khoá vào Actions secret nghĩa là mọi PR from fork đều có đường
   tới một API trả tiền.
2. **Gate phải kiểm được offline.** Nếu `check_gates.py` phụ thuộc Decisions API, thì mất mạng
   ⇒ **không biết** gate có hợp lệ hay không. Đó là biến một phép kiểm thành phép thử may rủi.
3. **`v1beta`.** API chưa GA. Đặt nó vào đường bắt buộc của CI là đặt một beta vào chỗ chặn merge.

Nguyên tắc: **cổng chặn merge phải tất định và offline.** Công cụ này là **trợ giúp đọc**, chạy tay.

---

## 5. Đã làm

| | |
|---|---|
| `scripts/lib/decisions.mjs` | 4 hàm thuần + 1 hàm mạng có tiêm `fetch`. **0 import** |
| `scripts/lib/decisions.test.mjs` | **28 test**, chạy offline: `node --test scripts/lib/decisions.test.mjs` |
| `scripts/decide_gate.mjs` | CLI: `--dry-run` (không gọi mạng) · `--json` · chặn CI · từ chối tệp không phải signoff |
| Reverse-test | 4 phép tiêm ⇒ **4 lần đỏ** (xem §6.2) |
| Thêm dependency | **Không** |

---

## 6. Tự phê bình

1. **🔴 Tôi CHƯA gọi được API thật.** Sandbox này chặn `generativelanguage.googleapis.com`
   (đã thử: `ECONNRESET`). Vậy nên:
   - Hình dạng request ở §3 là **đọc từ tài liệu + repo playground**, chưa đối chiếu phản hồi thật.
   - `readAnswer()` xử lý **ba** hình dạng (`noul`, `choice`, `probabilities.true`) vì tôi không
     kiểm được hình dạng nào là hiện hành. Đó là phòng thủ, không phải hiểu biết.
   - **Không** có số đo về chất lượng: tôi không biết `co_nguon` có thật sự bắt được khẳng định
     thiếu nguồn hay không.

   ⇒ **Q62a:** ai có khoá AI Studio để chạy thử trên 6 tệp signoff và ghi lại kết quả?

2. **Lỗi thật do test bắt được, không phải do tôi đọc ra.** `fetchImpl: null` ban đầu **không**
   tắt được mạng (vì `fetchImpl || globalThis.fetch`), khiến test lẽ ra phải im lặng lại gọi
   Google thật. Và lỗi mạng ném stack trace thay vì trả `ok:false`. Cả hai đã vá. Ghi lại vì
   nếu tôi không viết test "tắt mạng", cả hai sẽ nằm im.

3. **`score` không được phân dải.** API trả xác suất cho **từng bậc**, nên quy về một số rồi
   phân dải là làm mất thông tin. Hiện `hintFor()` trả `xem_lai_ky` cho mọi `score` — tức là
   **không dùng được** thông tin đó. Đây là thiếu sót chưa sửa, không phải thiết kế.

4. **Repo nguồn không có LICENSE.** Xem §7.

5. **Q62 chưa trả lời.** Tôi dựng công cụ nhưng không tự quyết đưa nó vào quy trình gate.

6. **🔴 Tôi đã viết một cổng CI đỏ, và nó đỏ vì lỗi thiết kế của chính tôi.** Bản đầu đặt
   khối chặn `CI` **trước** nhánh `--dry-run`, nên `--dry-run` cũng bị chặn ⇒ bước CI
   `node … --dry-run` chết với exit 2.

   Tôi đã chạy thử bước này ở máy và nó **xanh** — vì tôi chạy nó với `CI` chưa set ở đúng
   thứ tự, và ở lần thử thứ hai tôi đặt `CI=true` **sau** `bash -c`, nên biến không tới được
   tiến trình con. Cả hai lần đều cho tín hiệu sai.

   Bài học, ghi lại vì nó thuộc đúng nhóm lỗi mà `AGENTS.md` cảnh báo: **chạy thử một cổng ở
   máy không chứng minh cổng đó chạy trong CI.** Chỉ log của lần chạy thật mới chứng minh.
   Đã sửa: khối chặn `CI` chuyển xuống **sau** `--dry-run`, và bước CI kiểm **cả hai** chiều
   (`--dry-run` phải exit 0, gọi thật phải exit 2).

---

## 7. License — đọc kỹ trước khi ai đó muốn chép

| Kiểm | Kết quả (2026-11-18) |
|---|---|
| `license` qua GitHub API | **`null`** — không có file LICENSE |
| Owner | `xuankhanh1612` (2014, 107 repo) — **khác** `lexuankhanh1612` |
| Có phải fork | Không |
| License trong `metadata.json` / `package.json` | Không khai báo |
| `index.ts` | Chỉ có header `SPDX-License-Identifier: Apache-2.0` — **một** tệp 58 byte |

⇒ **Không có license rõ ràng** ⇒ theo [`ADR-0016`](ADR-0016-license-compliance.md) và
[`docs/10-opensource`](../10-opensource/README.md) §1, đây là nhóm **❌ không dùng** — cùng nhóm
với `arathianevasion/watson-games` ("mặc định all rights reserved").

**Quyết định:** chỉ đọc để học **hành vi API**, viết lại từ đầu. Không chép một dòng nào.
Các trích dẫn trong ADR này là **dẫn chứng**, không phải mã dùng lại.

Nếu PO là chủ repo đó và muốn dùng chung mã: **Q62b** — thêm file `LICENSE` cho repo playground
trước, rồi mới bàn chuyện tái dùng.
