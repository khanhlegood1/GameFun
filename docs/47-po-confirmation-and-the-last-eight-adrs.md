# 47 — Đủ 43 ADR, và một câu "tôi là PO" không ký được 18 tệp

> **Tài liệu sống:** `docs/47-po-confirmation-and-the-last-eight-adrs.md` — bản gốc ở đây.
> **Trạng thái:** `DONE` (vòng 36)
> **Tiền đề:** `docs/46` (§2 phát hiện 17 chữ ký không có người) · `docs/34` §3 (tên người, không ghi chức danh) · `docs/37` (việc không người là mong muốn)

---

## 0. Bốn dòng

Bạn nói *"Tôi Lê Xuân Khánh là PO"* và thả **8 tệp ADR** còn thiếu (0008, 0037–0043).

1. **Đủ 43/43 ADR có tệp.** Con số "8 thiếu tệp" trên portal về **0**. Không còn dòng đỏ nào.
2. **`ADR-0037` … `0043` ghi `Project Owner (Lê Xuân Khánh)`** — khớp với điều bạn vừa xác nhận.
3. **Nhưng `ADR-0008` ghi `Principal Architect *(chờ ký)*`.** Nó được `Accepted` từ 13/11, và vẫn chưa có người ký. Vậy tổng là **18 ADR chờ chữ ký**, không phải 17.
4. **Câu "tôi là PO" không ký được 18 tệp đó.** Nó trả lời *ai giữ vai `Project Owner`*. Nó không trả lời *ADR-0017 do `Tech Lead On-chain` ký đã được ký chưa*. Tôi đã dựng một cổng để chính tôi không được lẫn hai câu này.

---

## 1. Đã nhận 8 tệp, và không có gì bất ngờ về format

Lần trước (vòng 35) ba format header làm hỏng extractor. Lần này đo trước:

| Tệp | Format | `Người quyết` |
|---|---|---|
| 0008 | bảng meta 2 cột | `Principal Architect *(chờ ký)*` |
| 0037–0043 | `**Trạng thái:**` một dòng | `Project Owner (Lê Xuân Khánh)` |

Extractor đọc đúng **8/8** ngay lần đầu, 0 tệp `unknown`, 0 tệp thiếu ngày. Bài học vòng 35 đã trả tiền: *đo trước khi sửa*.

**43/43 ADR · 0 thiếu tệp.** Đây là lần đầu tiên con số đó bằng 0.

Tôi cũng phát hiện `README.md` của thư mục ADR **thiếu 7 dòng** (0026–0032 có tệp nhưng không có trong chỉ mục) — đã chèn, giờ chỉ mục đủ **43 dòng**.

---

## 2. Câu hỏi quan trọng: "tôi là PO" ký được những gì?

### 2.1. Hai câu hỏi, không phải một

Khi bạn nói *"Tôi Lê Xuân Khánh là PO"*, thông tin đó là:

> **Ai giữ vai `Project Owner`?** → Lê Xuân Khánh.

Đó là một khẳng định về **con người**. Nó khác với:

> **ADR-0017 đã được ký chưa?** → Chưa. Tệp ghi `Tech Lead On-chain *(chờ ký)*`.

Đó là một khẳng định về **một quyết định cụ thể**.

Biết câu trả lời thứ nhất **không** suy ra câu trả lời thứ hai. Người giữ vai hoàn toàn có thể chưa ký một ADR cụ thể — và trong bộ tài liệu này, đúng là như vậy: 18 tệp ghi `chờ ký` ngay trong dòng `Người quyết`.

### 2.2. Vì sao đây là chỗ dễ sai nhất trong cả dự án

Mã của tôi có một bảng `ROLE_TO_PERSON`. Trước vòng này nó chạy như sau:

```python
for role, who in ROLE_TO_PERSON.items():
    if role in d:
        return who            # → "Project Owner (Lê Xuân Khánh)" ⇒ có người
```

Nếu tôi chỉ **thêm một dòng**:

```python
"Principal Architect": "Lê Xuân Khánh",   # ← một dòng
```

thì 18 ADR `role_only` biến thành `named`, portal hiện **"Đã nhận · có tên người ký"** cho cả 18, và **cổng 25 sẽ xanh**. Không tệp ADR nào đổi một byte.

Đó là một chữ ký được tạo ra bằng cách sửa bảng tra cứu. Nó trông y hệt một chữ ký thật trên màn hình, và chỉ khác ở chỗ **không ai đã ký**.

Và nó là thứ *bạn vừa tạo điều kiện cho tôi làm* — một cách vô tình. "Tôi là PO" là một câu đúng, và nó rất gần với "vậy thì điền tên tôi vào". Tôi không làm thế.

### 2.3. Đã dựng chốt chặn

`gen_portal_data.py` giờ có **hai** bảng, không phải một:

| Bảng | Trả lời | Điền khi nào |
|---|---|---|
| `ROLE_TO_PERSON` | Vai này có người, ghi **ngay trong tệp** | Tệp đã ghi tên |
| `ROLE_HOLDER` | Vai này có người, **theo xác nhận của PO** | Chỉ khi PO nói rõ, **và phải có `basis`** |

`ROLE_HOLDER` hiện **rỗng**. Điền nó vào **không** làm ADR nào được ký — vì `signature` chỉ đổi khi chính tệp ADR đổi. Bảng đó chỉ để portal *hiện* được "vai này do ai giữ", tách khỏi "ai đã ký".

Cổng 25 thêm **bất biến thứ 7** (`inv_role_holder_is_not_a_signature`) và **hai phép phá mới**:

| Phép phá | Câu hỏi nó đặt ra | Kết quả |
|---|---|---|
| **P6** | Điền `ROLE_HOLDER` cho `Principal Architect` rồi khai 18 ADR đã ký → có đỏ không? | ✓ đỏ |
| **P7** | Khai "vai này có người" mà không có căn cứ → có đỏ không? | ✓ đỏ |

P6 kiểm bằng cách so tên người ký với **`decider` — nguyên văn trong tệp**, không phải với `decider_person` (trường có thể bị điền từ bảng tra cứu). Xem §3.1: lần đầu tôi viết đúng sai chỗ này và P6 **vẫn xanh**.

---

## 3. Ba lỗi của chính cổng trong vòng này

### 3.1. P6 xanh vì tôi so với chính trường bị làm giả

Bất biến mới ban đầu:

```python
in_file = bool((i.get("decider_person") or "").strip())   # ← SAI
check(not (holder and not in_file) or not signed, ...)
```

`decider_person` là trường mà kẻ phá **đặt** trong P6. Nên `in_file` thành `True`, và phép kiểm không bao giờ đỏ. **Lần thứ hai trong hai vòng** tôi viết một cổng đọc phải chính thứ nó đang canh.

Sửa: so với **`decider`** — chuỗi nguyên văn đọc từ tệp:

```python
name_in_file = bool(holder.get("person")) and holder["person"] in (i.get("decider") or "")
```

### 3.2. P4 đang xanh vì không còn gì để phá

Phép phá P4 tìm một dòng `state == "missing"` rồi gán cho nó một tệp không tồn tại. Nhưng vòng này **43/43 tệp đã đủ** ⇒ không còn dòng `missing` nào ⇒ vòng lặp không chạy ⇒ không có gì đỏ ⇒ P4 "xanh".

Đây **đúng lỗi `docs/40`**: một cổng chỉ xanh vì nó không làm gì. Sửa: nhắm dòng **đang có tệp** và đổi tên tệp thành tên không tồn tại; nếu corpus không có dòng nào như vậy thì `raise` — thà nổ còn hơn xanh giả.

### 3.3. "6 bất biến" là số gõ tay

Tôi thêm bất biến thứ 7 nhưng dòng tổng kết vẫn in `6 bất biến`, vì nó là **hằng số viết trong f-string**. Sửa bằng cách đếm bằng cách **chạy**:

```python
INVARIANTS = [inv_matches_generator, lambda: inv_no_action_lost(data), …]
for inv in INVARIANTS: inv()
print(f"… {PASSES} kiểm tra · {len(INVARIANTS)} bất biến · …")
```

Một con số tự khai thì không kiểm được gì. Cùng họ với `docs/46` §3.3 (vòng quét đọc chữ thay vì đọc mã thoát): **con số mô tả cổng phải do cổng tự tính.**

### 3.4. Tiêu đề P13 ghi "17" trong khi thực tế là 18

Sau khi merge PR #80, đọc lại trang thật thì thấy dòng việc **P13** vẫn ghi:

> Gán tên người thật cho **17** ADR đang do chức danh ký ('Principal Architect' **×14**, …)

Con số đó **đúng lúc viết** (vòng 35, 17 tệp) và **sai ngay khi ADR-0008 vào repo**. Không cổng nào đọc tiêu đề, nên nó đã đi qua: commit → PR → 4 check → merge → trang thật.

Đây là cùng một họ lỗi với §3.3 và `docs/46` §3.3: **một con số gõ tay thì không tự đúng lại**. Và nó đắt hơn hai lỗi kia ở một điểm: tiêu đề P13 là thứ **PO đọc để biết phải làm gì**. Sai một đơn vị nghĩa là PO không biết còn bao nhiêu chữ ký phải xin.

**Đã sửa:** tiêu đề sinh từ dữ liệu, `17 → 18`, `×14 → ×15`. Và thêm **bất biến thứ 8** (`inv_task_numbers_match_data`): đọc số trong tiêu đề P13 rồi so với số dòng `role_only` thật, kể cả số của từng vai. Cổng bắt được ngay lần chạy đầu (`P13 nói 17 … nhưng dữ liệu có 18`).

---

## 4. Bằng chứng

```
TẤT CẢ XANH — 24 cổng (mã thoát, không đọc chữ)        ./scripts/run_all_gates.sh
PORTAL: PASS — 237 kiểm tra · 8 bất biến · 13 việc · 43 ADR (43 có tệp, 25 chờ ký, 0 thiếu tệp)
PORTAL SELFTEST: PASS — 8/8 (1 đối chứng + 7 phép phá)
PORTAL RENDER: PASS — app.js chạy trong DOM tối thiểu · 10 việc vẽ ra · 43 ADR
```

Bốn phép phá chạy thật trên bản sao trong bộ nhớ:

```
✓ P3 ADR chờ ký hiện ra như đã ký → đỏ
✓ P5 ADR do chức danh ký nhưng khai là đã nhận → đỏ
✓ P6 điền ROLE_HOLDER rồi coi 18 ADR là đã ký → đỏ
✓ P7 khai 'vai này có người' mà không có căn cứ → đỏ
✓ P0 đối chứng: data.json gốc → xanh
```

---

## 5. Con số trên portal, trước và sau vòng này

| | Vòng 35 | **Vòng 36** |
|---|---|---|
| ADR có tệp | 35 / 43 | **43 / 43** |
| Thiếu tệp | 8 | **0** |
| Có tên người ký | 18 | **25** |
| Chỉ có chức danh | 17 | **18** ← thêm ADR-0008 |
| Chờ chữ ký | 17 | **18** |

Con số "chờ ký" **tăng** một dòng. Đó không phải bước lùi: `ADR-0008` đã ở đó từ 13/11, chỉ là chưa ai thấy nó vì tệp chưa có trong repo. **Nhìn thấy một vấn đề cũ không làm nó tệ hơn.**

---

## 6. Ba câu hỏi

1. **`Principal Architect` — bạn có phải người đó không?** Bạn xác nhận là PO. PO và Principal Architect có thể là cùng một người, nhưng tôi không suy ra điều đó từ một câu nói về vai khác. Nếu đúng, hãy nói rõ *"Principal Architect cũng là tôi"* — và việc sửa vẫn là sửa 18 tệp, không phải sửa một dòng trong mã.
2. **`Tech Lead On-chain` và `Founder` là ai?** ADR-0017 và ADR-0018. Hai vai này chưa có ai xác nhận. Nếu chính bạn giữ cả ba vai, nói một câu là đủ để tôi ghi vào `ROLE_HOLDER` — nhưng ADR vẫn phải được sửa tệp mới tính là ký.
3. **Sửa 18 tệp ADR bây giờ, hay để nguyên?** Đây là lựa chọn của bạn, và tôi không nên tự chọn: sửa `Người quyết` trong một tệp `Accepted` là **sửa bản ghi lịch sử**. Cách sạch hơn là tạo một ADR mới ghi *"các ADR 0001–0018 được PO phê chuẩn ngày …"* — nhưng đó là quyết định của PO, không phải của agent.

---

## 7. Chưa làm

| | Nợ | Vì sao để lại |
|---|---|---|
| **W1** | `ROLE_HOLDER` rỗng cho cả 5 vai | Chỉ điền khi bạn xác nhận **từng vai**, không suy ra từ "tôi là PO" (§2.1) |
| **W2** | 18 ADR vẫn chưa ký | Cần quyết định của bạn ở §5 câu 3. **P13** đang canh việc này, hạn 2026-12-15 — tiêu đề P13 nay tự khớp dữ liệu (bất biến 8, §3.4) |
| **W3** | `README.md` của ADR vẫn ghi `Accepted (chờ ký)` | Mâu thuẫn gốc vẫn ở tệp nguồn của bạn; portal đã hiện đúng bất kể README nói gì |
| ~~W4~~ | ~~8 ADR thiếu tệp~~ | **Đóng:** 43/43 |
