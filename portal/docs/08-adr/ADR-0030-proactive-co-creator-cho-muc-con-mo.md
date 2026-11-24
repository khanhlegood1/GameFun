# ADR-0030 — Học `Proactive-Co-Creator`: biến mục còn mở thành **câu hỏi đóng**

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`belief.mjs`](../../scripts/lib/belief.mjs) · [`open_questions.mjs`](../../scripts/open_questions.mjs) · [`PRD-game9k.md` §11](../01-requirements/PRD-game9k.md) · [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) · [`ADR-0029`](ADR-0029-gemini-decisions-api-cho-gate.md) · **Q63**

> Nguồn học: [`khanhlegood1/Proactive-Co-Creator`](https://github.com/khanhlegood1/Proactive-Co-Creator)
> — **0 star**, tạo 2026-11-22, **không có README**, **không có file LICENSE** (API trả
> `license: null`), tác giả khác tài khoản repo này. Đọc để **học cơ chế**, không chép dòng nào. §6.

---

## 0. Trả lời ngắn

| | |
|---|---|
| Học được gì | **`presence_in_prompt: false`** = thứ *được giả định*, không phải *được nói ra*. Và câu hỏi làm rõ **luôn có `options`** |
| Áp vào đâu | `PRD-game9k.md` §11 — **11 mục chưa đóng**, 2 trong đó `BLOCKING` |
| Làm gì | `scripts/open_questions.mjs`: đọc §11, in mục còn mở, **sinh 3 câu hỏi đóng** cho mỗi mục |
| Có gọi model không | ❌ **Không.** Sinh câu hỏi từ dữ liệu của chính mục ⇒ tất định, offline, test được |
| Có chặn merge không | ❌ Không. `--check` tồn tại và **đỏ được**, nhưng chưa wire vào CI — xem §4 |
| Có sửa PRD không | ❌ **Không.** Read-only. Không câu trả lời nào được ghi hộ |

---

## 1. Vấn đề thật, đo được

`PRD-game9k.md` §11 có 11 mục. Cột `Trạng thái` là **văn xuôi tự do**, và có **6 chuỗi khác
nhau** cho cùng một ý "chưa ai quyết":

| Chuỗi trong PRD | Số mục |
|---|---|
| `Giả định, kiểm ở Alpha` | 2 |
| `Cần xác nhận` | 1 |
| `Cần legal review — **rủi ro cao**` | 1 |
| `**BLOCKING**` | 1 |
| `**BLOCKING cho GA**` | 1 |
| `Mở` | 5 |

Hệ quả: `check_req_mapping.py` thấy 11 dòng **có mặt** ⇒ xanh. Nhưng §11 nói rõ:
*"bất kỳ mục `BLOCKING` chưa đóng ⇒ gate P01 không được ký"* — và **không máy nào kiểm điều đó**.
Hôm nay `Q-01` và `Q-06` đều `BLOCKING`, và gate P01 **vẫn đang mở**.

---

## 2. Quyết định

### 2.1. ✅ Nhận: chuẩn hoá 11 mục về **5 trạng thái đóng**

`parseState()` ánh xạ 6 chuỗi trên vào `mo` / `can_xac_nhan` / `gia_dinh` / `blocking` / `dong`.
Chuỗi lạ ⇒ `khong_ro`.

**Không đoán gần đúng.** `"gần đóng"` không được thành `dong`. Lý do: đoán sai theo hướng
"đã đóng" biến một mục chưa xong thành đã xong, và không ai phát hiện.

### 2.2. 🔴 `khong_ro` **không** chặn cứng — đây là chỗ tôi tự sửa giữa đường

Bản đầu tôi cho `blocksGate("khong_ro") === true`. Chạy trên PRD thật thì `A-03` (chuỗi
`"Cần legal review — **rủi ro cao**"`) rơi vào `khong_ro` ⇒ **bị chặn**.

Sai ở đâu: PRD §11 chỉ cấm ký khi **`BLOCKING`**. Một ô chữ khó đọc là **lỗi của parser**,
không phải quyết định của PO. Biến lỗi parser thành án chặn gate là **tự cho máy quyền mà
PRD không trao**.

Đã tách hai hàm:

| Hàm | `blocking` | `khong_ro` |
|---|---|---|
| `blocksGate()` | ✅ chặn | ❌ không |
| `needsHumanRead()` | ❌ | ✅ cần người xem |

Cả hai vẫn nằm trong `unconfirmed` — không mục nào bị coi là đã đóng.

Và đã thêm từ đồng nghĩa **thật** của `A-03` để nó đọc đúng là `can_xac_nhan`.

### 2.3. ✅ Nhận: câu hỏi làm rõ **phải có lựa chọn**

Từ `Clarification {question, options[]}` của repo nguồn. Một câu hỏi mở (*"bạn muốn gì?"*)
đắt hơn nhiều so với câu đóng có 2–4 lựa chọn, vì người trả lời phải **tự nghĩ ra khung**.

`clarificationsFor()` sinh đúng **3** câu:
`owner` (ai quyết) · `deadline` (mốc nào) · `fallback` (không kịp thì sao).
Mỗi câu có 2–4 lựa chọn lấy từ chính PRD (cột `Owner`, gate P01/P03, module M1..M9).

Hai luật, có test khoá:
- **Không hỏi lại** câu đã hỏi.
- **Không bịa thêm câu** để đủ 3 khi pool đã cạn. Pool có 4 câu ⇒ lần 2 trả **1** câu, lần 3 trả **0**.
  Một câu hỏi lặp còn tệ hơn một câu hỏi thiếu.

### 2.4. ✅ Nhận: bản ghi giả định — thứ `ADR-0026` §3 gọi là `trace`

`assumptionsRecord()` trả `{counts, unconfirmed, blocking, canXem}`. Đây là câu trả lời cho vấn
đề `ADR-0026` §3 nêu: *"một gate được ký trên artifact do AI sinh, không có trace, thì chữ ký
đó chỉ xác nhận 'tôi đọc output và thấy ổn'"*.

`generated` **cố ý** là `null` — hàm không đọc đồng hồ. Người gọi truyền ngày vào. Lý do:
một hàm đọc `new Date()` thì không test tất định được (bài học từ Q59).

---

## 3. Hiện trạng đo được (2026-11-18)

```
node scripts/open_questions.mjs
```

| | |
|---|---|
| Tổng mục §11 | **11** |
| Đã đóng | **0** |
| 🔴 `BLOCKING` chặn cứng | **Q-01** (ai là PO) · **Q-06** (giấy phép game tại VN) |
| 🟠 cần xác nhận | A-02 · A-03 |
| 🟡 giả định | A-01 · A-04 |
| ⚪ mở | Q-02 · Q-03 · Q-04 · Q-05 · Q-07 |

`node scripts/open_questions.mjs --check` ⇒ **exit 1**, in ra `Q-01, Q-06`.

---

## 4. Vì sao **chưa** wire `--check` vào CI

`--check` đã tồn tại và **đỏ được** (đã reverse-test cả hai chiều). Nhưng chưa thêm vào
`.github/workflows/docs.yml`, và đây là chủ ý:

Wire nó vào ⇒ **mọi PR đều đỏ** cho tới khi `Q-01` và `Q-06` được đóng. Hai mục đó phụ thuộc
**pháp lý và nhân sự**, không phụ thuộc mã. Một cổng đỏ vĩnh viễn không phải cổng — nó là
tiếng ồn, và người ta sẽ học cách bỏ qua nó.

**Đề nghị** (Q63): wire vào CI ở chế độ `continue-on-error: true` + comment cảnh báo, hoặc
đợi tới khi `Q-01` đóng rồi mới wire cứng. PO quyết.

---

## 5. Đã làm

| | |
|---|---|
| `scripts/lib/belief.mjs` | 5 export, **0 import**, không I/O |
| `scripts/lib/belief.test.mjs` | **26 test**, gồm 4 test chạy trên **PRD thật** |
| `scripts/open_questions.mjs` | CLI read-only: `--ask` · `--json` · `--only` · `--check` |
| Reverse-test | 4 phép tiêm ⇒ **4 lần đỏ** (§7.3) |
| Thêm dependency | **Không** |

---

## 6. License — repo nguồn **không có LICENSE**

| Kiểm | Kết quả (2026-11-18) |
|---|---|
| `license` qua GitHub API | **`null`** |
| File `LICENSE` | **không có** trong danh sách contents |
| `README` | **không có** |
| `package.json` khai báo license | **không** |
| `types.ts` / `index.ts` | chỉ có header `SPDX-License-Identifier: Apache-2.0` — **hai** tệp |
| ★ / fork / tuổi | 0 sao · không phải fork · tạo và push cùng ngày 2026-11-22 |

⇒ Theo [`ADR-0016`](ADR-0016-license-compliance.md) và [`docs/10-opensource`](../10-opensource/README.md) §1:
nhóm **❌ không dùng** — cùng nhóm với `arathianevasion/watson-games` và
`xuankhanh1612/Gemini-Decisions-API-Playground` (ADR-0029 §7).

**Chỉ đọc để học hai ý** (§0). Viết lại bằng lời. Không chép dòng nào.

---

## 7. Tự phê bình

1. **🔴 Tôi tự sửa thiết kế giữa đường, và nếu không chạy trên PRD thật thì đã không thấy.**
   `blocksGate("khong_ro") === true` trông hợp lý khi viết. Nó chỉ sai khi chạy trên `A-03`.
   Đây là lý do test `B-40`/`B-42` đọc **file thật** thay vì dữ liệu bịa: dữ liệu bịa do tôi
   viết sẽ không có chuỗi `"Cần legal review — **rủi ro cao**"`.

2. **Test `B-23` của tôi cũng sai lần đầu.** Tôi viết nó kỳ vọng lần hỏi thứ hai trả **rỗng**.
   Thật ra pool có 4 câu, lấy 3, nên lần hai còn **1**. Test đỏ. Nhưng khi sửa, tôi không chỉ
   sửa kỳ vọng — tôi kiểm lại **hành vi nào mới là đúng** và giữ nguyên luật "không bịa thêm".
   Sửa test cho vừa code là cách tự lừa.

3. **Sinh câu hỏi không dùng model.** Đây là **thiếu sót** so với repo nguồn (nó dùng Gemini để
   sinh câu hỏi theo ngữ cảnh). Nhưng dùng model ở đây có hai cái giá: (a) tất định mất,
   (b) test phải gọi mạng. Tôi chọn template tất định và **ghi rõ nó kém hơn**: câu hỏi của tôi
   là *câu hỏi quy trình chung*, không phải *câu hỏi riêng cho Q-06 về luật VN*.

4. **`--check` chưa vào CI.** Xem §4. Đây là quyết định, không phải bỏ sót — nhưng nếu PO muốn
   nó chặn merge thì thêm một dòng.

5. **Chưa nối vào `check_gates.py`.** Hai cổng đang kiểm hai thứ khác nhau: `check_gates.py`
   kiểm **cấu trúc tệp signoff**, script này kiểm **nội dung bảng §11 của PRD**. Chưa có lý do
   để gộp, nhưng cũng chưa chứng minh là **không nên** gộp.

6. **Q63 chưa trả lời.** Tôi dựng công cụ, không tự đưa nó vào đường chặn merge.
