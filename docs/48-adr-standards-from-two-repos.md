# 48 — Chuẩn ADR từ hai repo của PO, và một kết luận bị đảo

> **Tài liệu sống:** `docs/48-adr-standards-from-two-repos.md` — bản gốc ở đây.
> **Trạng thái:** `DONE` (vòng 37) · cổng mới: **27**
> **Tiền đề:** `docs/46` (§2: 18 chữ ký không có người) · `docs/47` (§2.2: "ai giữ vai" ≠ "ADR đã ký") · `docs/34` §3 (tên người, không ghi chức danh)

---

## 0. Bốn dòng

Bạn đưa hai repo và nói *"áp dụng vào quản lý dự án và ADR"*.

1. **Kiểm trước khi dùng, theo quy ước repo:** cả hai là **fork**, cả hai có giấy phép **cho phép dùng lại** — `architecture-decisions` Apache-2.0 (gốc `factory-x-contributions`), `hve-core` MIT (gốc `microsoft`, 1.638 sao). Không có repo nào `license: null`.
2. **`adr-standards.instructions.md` của `hve-core` đảo ngược một kết luận của tôi** ở `docs/34` §3. Nó nói ADR nên ghi **vai**, không ghi tên riêng. Điều đó có nghĩa `Principal Architect` **không** sai vì là một vai — và `docs/46` đã kết luận hơi quá tay.
3. **Nhưng nó không cứu 18 ADR nào.** Chúng sai vì *trước đây không ai giữ vai đó và không ai xác nhận*. Nay bạn xác nhận giữ cả bốn vai ⇒ điều kiện nghiệm thu **đổi**, còn số chữ ký còn thiếu **không đổi**: vẫn **18**.
4. **Cổng 27 mới** áp chuẩn của hai repo lên 43 ADR: 307 kiểm tra, 7 bất biến, 8 phép phá.

---

## 1. Đã kiểm hai repo (không giả định)

| | `architecture-decisions` | `hve-core` |
|---|---|---|
| Fork của | `factory-x-contributions/architecture-decisions` | **`microsoft/hve-core`** (1.638 sao) |
| Giấy phép | **Apache-2.0** | **MIT** |
| Dùng được? | có, kèm NOTICE | có, kèm copyright notice |
| Thứ đáng lấy | `scripts/lint-adrs.js` + `.github/workflows/lint-adrs.yaml` | `.github/instructions/project-planning/adr-standards.instructions.md` |
| Có ADR thật? | có (`docs/hercules_network_adr/adr002…`) | **không** — nó là bộ instruction/prompt/skill |
| Sao | 2 | 1.638 |

**Viết đúng bản chất:** `architecture-decisions` cho ta **cách canh** (lint + CI trên mọi PR đụng `docs/**/adr*/**`). `hve-core` cho ta **chuẩn để canh** (MADR v4.0.0 CC0-1.0, GP-16, GP-07, taxonomy 6 trạng thái). Không repo nào cho ta một ADR để chép — và không cần.

---

## 2. Kết luận bị đảo: persona, không phải người

### 2.1. Điều `hve-core` nói

`adr-standards.instructions.md` §**"Personas, Not People"**:

> *"Record stakeholder perspectives by persona or role rather than by named individual so that the record stays accurate as people change teams or leave the organization, and so that personal identifiers are not committed to a repository that may be public."*
>
> *"The single exception is named decider attribution: when the user explicitly requires that a specific individual be credited as a decider for accountability, that name may appear…"*

### 2.2. Điều tôi đã nói, và nó sai ở đâu

`docs/34` §3 (và `docs/46` §2) lập luận: *"`owner: "PO"` là một chức danh; khi quá hạn không ai biết phải tìm ai"* ⇒ phải ghi **họ tên đầy đủ**.

Lập luận đó đúng **cho sổ việc** — một việc quá hạn cần một người để gọi. Nó **không đúng cho ADR**, và tôi đã bê nguyên sang:

| | Sổ việc (`pm/action-register.json`) | ADR |
|---|---|---|
| Câu hỏi | *Ai phải làm việc này?* | *Vai nào đã quyết điều này?* |
| Ghi gì | **tên người** (LXK) | **vai** + người giữ vai |
| Vì sao | quá hạn phải gọi được một người | bản ghi phải còn đúng khi người đổi vai |
| Chuẩn dùng | `docs/34` §3 | GP-16 §Personas, Not People |

**Đây là một lỗi thật của tôi, không phải một khác biệt quan điểm.** Tôi áp một quy tắc đúng cho lĩnh vực A sang lĩnh vực B mà không kiểm.

### 2.3. Và điều nó KHÔNG cứu được

Cám dỗ ngay sau khi đọc §2.1 là: *"vậy `Principal Architect` là đúng chuẩn rồi, 18 ADR không có vấn đề gì."*

Sai. GP-16 nói ghi **vai**; nó không nói ghi **vai trống**. `Principal Architect *(chờ ký)*` là một vai **không có người giữ và không ai xác nhận** — và chính tệp nói nó đang chờ. Chuẩn ADR không cứu một chữ ký không tồn tại.

Nên `docs/46` §2 cần một chỉnh: **câu đúng không phải "17 ADR do chức danh ký nên vô giá trị", mà là "18 ADR do một vai không có người giữ, và chính tệp nói nó đang chờ ký".** Vấn đề là *không ai chịu trách nhiệm*, không phải *thiếu tên riêng*.

### 2.4. Hệ quả cụ thể: P13 đổi điều kiện nghiệm thu

| | Trước | Sau |
|---|---|---|
| Điều kiện | *"mỗi ADR trong 18 tệp có một **tên người**"* | *"`ROLE_HOLDER` điền đủ 4 vai **có basis**, VÀ mỗi tệp ghi **người giữ vai**"* |
| Số ADR còn thiếu chữ ký | 18 | **18** (không đổi) |

Bạn xác nhận *"Tôi cũng là Founder, PO, TL, PA"* ⇒ `ROLE_HOLDER` nay có 4 vai, mỗi vai có `basis` trỏ về xác nhận ngày 2026-11-24. **Điều đó không ký ADR nào**: 18 tệp vẫn ghi `*(chờ ký)*`, và portal vẫn hiện đúng như thế.

---

## 3. Cổng 27 — và bốn lỗi của chính nó

### 3.1. Cổng kiểm gì (7 bất biến)

| # | Nguồn | Bất biến |
|---|---|---|
| 1 | GP-16 | Tên tệp `ADR-NNNN-kebab-case.md`, slug chỉ `[a-z0-9-]` |
| 2 | GP-16 | Không trùng số; số liên tục 1..max (lỗ hổng = một quyết định im lặng rời lịch sử) |
| 3 | `fx-review-adr` Step 4 | Mọi `ADR-NNNN` được nhắc phải tồn tại |
| 4 | `docs/46` §1 | `Trạng thái` + `Ngày` đọc được; ngày hợp lệ, không ở tương lai |
| 5 | GP-16 taxonomy | Trạng thái thuộc 6 giá trị đóng |
| 6 | — | Không trạng thái nào tự mâu thuẫn |
| 7 | GP-16 §Supersession | Nhắc `supersede` phải nêu số hiệu ADR bị thay thế |

### 3.2. Ba dương tính giả, tìm ra bằng cách chạy trên 43 tệp thật

Lần chạy đầu: **29 vi phạm**. Cả 29 là lỗi của tôi.

**(a) Footer template copy-paste ở MỌI tệp.** Lần nhắc `supersede` duy nhất trong toàn bộ 43 ADR là dòng cuối:

```
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) …
```

Đó là **nhắc tên một giá trị enum**, không phải một khẳng định supersede. 18 vi phạm từ một dòng boilerplate. Sửa: bỏ dòng template + cụm trong ngoặc trước khi quét.

**(b) Tôi đặt cổng thành đỏ vĩnh viễn.** Bất biến "`Accepted` mà người quyết là chức danh ⇒ đỏ" sẽ đỏ cho tới khi ai đó sửa 18 tệp — đúng điều `docs/46` §2.2 và `docs/47` §2.3 nói **không được làm** (sửa bản ghi lịch sử). Một cổng đỏ vĩnh viễn vì một khiếm khuyết đã biết **sẽ bị tắt**, rồi nó không canh được gì. Sửa: cổng chỉ **đếm** (in ra `18 tệp do chức danh ký`), việc canh chữ ký để cổng 25 ở tầng bản chiếu — nơi nó đã canh đúng 18 tệp.

**(c) X7 hết chỗ bám.** Khi bỏ (b), phép phá X7 ("accepted + chức danh") mất phép kiểm ⇒ xanh vì lý do sai. Thay bằng X7 mới: trạng thái chứa **cả** `accepted` lẫn `proposed`.

### 3.3. Hai lỗi trong cổng 25, do chính thay đổi này làm lộ ra

**(d) Bất biến 7 đòi tên riêng — trái GP-16.** Khi `ROLE_HOLDER` được điền, bất biến 7 của cổng 25 báo **23 vi phạm** cho cả `Project Owner` (vai có người giữ, tệp KHÔNG ghi chờ ký). Theo GP-16 §Personas, đó **là** một chữ ký hợp lệ. Sửa: chữ ký quyết định bởi **"tệp có nói nó đang chờ ai không"**, không bởi "có tên riêng không".

**(e) Ba phép phá xanh vì phá sai chỗ.** P5 đặt `state` nhưng cổng đọc `display_state`; P6/P7 đặt `role_holder` nhưng không đặt `signature`. Sửa: mỗi phép phá phải đặt **đúng trường mà cổng đọc**, và phải đặt trường đó thành giá trị vi phạm.

Đếm lại sau khi sửa: **366 kiểm tra · 8 bất biến · selftest 8/8**.

---

## 4. Cổng 27 và cổng 25 khác nhau ở đâu

Câu hỏi công bằng: nếu `docs/46` đã có cổng 25 canh ADR, cổng 27 có thừa?

| | Cổng 25 | Cổng 27 |
|---|---|---|
| Kiểm | `portal/data.json` == bản sinh từ repo; chữ ký | Cấu trúc tệp ADR |
| Thấy lỗi `docs/46` §1 (11 tệp `state=unknown`) | **không** — generator đọc được thì nó xanh | **có** (bất biến 4) |
| Thấy tên tệp sai GP-16 | không | **có** |
| Thấy tham chiếu `ADR-9999` chết | không | **có** |
| Thấy `Ngày` ở tương lai | không | **có** |
| Thấy `supersede` mơ hồ | không | **có** |
| Canh chữ ký | **có** | không (chỉ đếm) |

Hai cổng không thay nhau được. Cổng 25 hỏi *"bản chiếu có nói dối không"*; cổng 27 hỏi *"tệp nguồn có đúng chuẩn không"*.

---

## 5. Bằng chứng

```
ADR STANDARDS: PASS — 307 kiểm tra · 7 bất biến · 43 ADR · đánh số 1..43 liên tục
                · 0 tham chiếu chết · 18 tệp do chức danh ký (cổng 25 canh chữ ký)
ADR STANDARDS SELFTEST: PASS — 9/9 (1 đối chứng + 8 phép phá)

PORTAL: PASS — 366 kiểm tra · 8 bất biến · 13 việc · 43 ADR (43 có tệp, 25 chờ ký, 0 thiếu tệp)
PORTAL SELFTEST: PASS — 8/8 (1 đối chứng + 7 phép phá)
PORTAL RENDER: PASS — 43 ADR · nhãn khớp dữ liệu

GATE WIRING: PASS — 47 kiểm tra · 27 cổng trong sổ
TẤT CẢ XANH — 25 cổng (mã thoát, không đọc chữ)
```

Tám phép phá của cổng 27, cả tám đều đỏ đúng chỗ:

```
✓ X1 slug có chữ hoa + khoảng trắng     ✓ X5 `Ngày` ở tương lai
✓ X2 hai ADR trùng số                   ✓ X6 trạng thái ngoài taxonomy
✓ X3 nhắc ADR-9999 không tồn tại        ✓ X7 accepted + proposed cùng lúc
✓ X4 ADR mất `Trạng thái`               ✓ X8 accepted mà chỉ nói "sẽ supersede"
```

Thử phá trên **app.js thật** (bản sao): bỏ vế `"chờ ký"` khỏi nhãn người giữ vai ⇒
**FAIL 18 vi phạm** — *`ADR-0001: vai "Principal Architect" nay có người giữ (Lê Xuân Khánh) nhưng tệp vẫn chờ ký — thẻ phải nói rõ`*.

---

## 6. Đã KHÔNG lấy gì, và vì sao

| Không lấy | Vì sao |
|---|---|
| `lint-adrs.js` (mã) | Apache-2.0 cho phép, nhưng nó phụ thuộc `gray-matter` + cấu trúc `adrNNN-*/README.md` — không khớp repo này. **Chép hành vi**, viết lại bằng Python, ghi nguồn. |
| MADR v4 template | CC0-1.0, chép được — nhưng 43 ADR đã có format riêng (bảng meta tiếng Việt). Thay đổi format header lần nữa là lặp lại `docs/46` §1. Dùng **taxonomy trạng thái** của nó, không dùng template. |
| `adr-author` skill / agent | Thiết kế cho Copilot + `.copilot-tracking/`; repo này dùng cổng Python. Lấy **chuẩn**, không lấy quy trình. |
| Y-Statement | Hay, nhưng là *định dạng thứ hai* — thêm một format nữa cho 43 tệp đang có 3 format là tự tạo lỗi. Ghi nhận ở §7. |

---

## 7. Còn mở

| | Nợ | Vì sao để lại |
|---|---|---|
| **W1** | 18 ADR vẫn ghi `*(chờ ký)*` | Cần quyết định của PO: sửa 18 tệp, hay tạo một ADR mới phê chuẩn 0001–0018 (GP-16 §Supersession cấm sửa ADR đã `Accepted`). P13 canh, hạn 2026-12-15 |
| **W2** | Chưa dùng Y-Statement cho quyết định nhỏ | Thêm định dạng thứ tư lúc này là tăng rủi ro; làm khi bộ tệp đã ổn định |
| **W3** | Cổng 27 chưa kiểm `asrTriggers` (GP-07) | 43 ADR không có trường này; áp bây giờ là bắt 43 tệp viết lại. Ghi nhận, không áp |
| **W4** | `README.md` của ADR vẫn `Accepted (chờ ký)` | Mâu thuẫn gốc ở tệp nguồn của PO. Cổng 27 nay **đếm** được nó (§3.2b) |
