# 49 — ADR-0044: phê chuẩn 14 ADR, và con số không phải 18

> **Tài liệu sống:** `docs/49-adr-0044-ratification.md` — bản gốc ở đây.
> **Trạng thái:** `DONE` (vòng 38) · ADR mới: `ADR-0044` (**Proposed — chờ PO ký**)
> **Tiền đề:** `docs/46` §2 (18 chữ ký không có người) · `docs/47` §2 (ai giữ vai ≠ ADR đã ký) · `docs/48` §2.3 (GP-16: vai, không phải tên riêng)

---

## 0. Bốn dòng

Bạn chọn đường 2 — **một ADR mới phê chuẩn**, không sửa 18 tệp.

1. **Nhưng con số không phải 18.** Chỉ **14** ADR đang ở trạng thái mâu thuẫn thật: `Accepted` (có hiệu lực) mà chưa ai ký. Bốn ADR còn lại (0011, 0016, 0017, 0018) đang `Proposed` — chúng **chưa có hiệu lực**, nên không có gì để phê chuẩn.
2. **`ADR-0044` phê chuẩn đúng 14 số hiệu**, liệt kê tường minh, có ngày, do PO giữ vai đã quyết.
3. **Không sửa tệp nào.** 14 tệp vẫn ghi `Principal Architect *(chờ ký)*` — đó là sự thật về lúc viết.
4. **Số "chưa ký" trên portal không đổi: 18.** Phê chuẩn không xoá việc tệp chưa có người ký. Thẻ ADR giờ nói **hai câu cùng lúc**, vì cả hai đều đúng.

---

## 1. Vì sao 14, không phải 18 — và tôi đã trình bày sai

Lần trước tôi nói *"18 ADR chờ chữ ký"*. Đúng. Nhưng tôi để bạn hiểu việc cần làm là *"phê chuẩn 18"*. Đo lại:

| Nhóm | Số tệp | Trạng thái thật | Phê chuẩn? |
|---|---|---|---|
| `Accepted` + chức danh + `chờ ký` | **14** (0001–0010, 0012–0015) | **có hiệu lực mà không ai ký** ← mâu thuẫn thật | **có** |
| `Proposed` + chức danh + `chờ ký` | **4** (0011, 0016, 0017, 0018) | chưa có hiệu lực — đang đúng | không |
| `Accepted` + PO có tên | 5 (0019–0022, 0038) | đã có người ký | không |
| | **26** | = 18 chưa ký + 5 đã ký + ADR-0044 | |

**Phê chuẩn một đề xuất là tự nhận nó.** ADR-0044 không làm thế: nó chỉ nói *"14 quyết định đang chạy này đã có người nhận"*. Bốn đề xuất đang mở cần PO quyết **từng cái**, sau khi đọc — và đó là việc khác, có lý do khác.

### 1.1. Vì sao không rút hiệu lực 14 ADR đó

Một lựa chọn khác: để chúng thành `Proposed` cho tới khi có người ký. Tôi không đề nghị. 14 quyết định đó đã được dùng để biện minh cho mã đã merge. Rút hiệu lực **hồi tố** là tuyên bố rằng mã đang chạy chưa từng được phép — có thể đúng về giấy tờ, sai về vận hành, và không giúp ai quyết được việc gì.

Cách đúng: **xác nhận lại từ hôm nay**, có ngày, có người, có số hiệu.

---

## 2. Cơ chế: `signer_alternatives` — câu trả lời thứ hai, không phải chữ ký thứ hai

Sau ADR-0044, mỗi ADR trong 14 tệp có hai nguồn trả lời *"ai chịu trách nhiệm?"*:

| Nguồn | Trả lời | Đọc khi |
|---|---|---|
| chính tệp | `Principal Architect *(chờ ký)*` | tra lịch sử — lúc viết, chưa ai ký |
| `signer_alternatives[]` | `ADR-0044 · 2026-11-24 · Lê Xuân Khánh` | tra hiện tại — nay đã có người nhận |

Generator đọc danh sách **từ chính ADR-0044**, không từ bảng viết tay:

```python
RATIFIER_RE = re.compile(r"^ADR-(\d{4})-phe-chuan.*\.md$")
def read_ratifications() -> dict[str, dict]:
    # đọc khối ``` đầu tiên chứa >= 2 mã ADR trong tệp phê chuẩn
```

Thêm một ADR vào phạm vi phê chuẩn = **sửa tệp ADR**, không sửa mã. Hai nguồn là hai chỗ để lệch; ở đây chỉ có một.

### 2.1. Ba quy tắc cứng, đã thành bất biến

| Quy tắc | Vì sao |
|---|---|
| `signature` **không đổi** khi có phê chuẩn | Phê chuẩn ≠ chữ ký. Tệp ghi `chờ ký` ⇒ vẫn `role_only` |
| `needs_signature` **vẫn true** | Phê chuẩn không xoá việc tệp chưa có người ký |
| Phải có `by` + `date` + `person` | Một phê chuẩn không có ngày là một phê chuẩn **không kiểm được** |

`display_state` thì **được** chuyển `accepted` — vì nay có một quyết định có ngày, có người, có số hiệu nói nó có hiệu lực.

---

## 3. Đường vòng thứ ba — và bất biến 9

Cám dỗ ngay sau đó: có phê chuẩn ⇒ để `signature = "named"` ⇒ `needs_signature` về 0 ⇒ portal hết báo "chưa ký" cho 14 tệp ⇒ **không tệp nào đổi một byte**.

Đây là **cùng một mánh** với hai lần trước:

| Vòng | Đường vòng | Bị chặn bởi |
|---|---|---|
| 36 | điền `ROLE_TO_PERSON` một dòng ⇒ 18 ADR thành "đã ký" | `docs/47` §2.3, phép phá P6 |
| 37 | điền `ROLE_HOLDER` cho 4 vai ⇒ 18 ADR thành "đã ký" | bất biến 7, phép phá P6/P7 |
| **38** | **có `signer_alternatives` ⇒ 14 ADR thành "đã ký"** | **bất biến 9, phép phá P8/P9** |

Ba đường vòng, một cái đích sai: **làm con số trên màn hình đẹp lên mà không ai ký gì.** Nay cổng 25 có **9 bất biến · 401 kiểm tra · 10 phép phá**.

---

## 4. Cổng 26 phải được hoà giải, không phải tắt

Sau khi thêm `adr-rat`, cổng 26 **đỏ 15 vi phạm**:

```
ADR-0001 do chức danh "Principal Architect *(chờ ký)*" ký nhưng THẺ VẼ RA "Đã nhận" — phải là "Chờ ký"
```

Đây **không** phải lỗi của cổng. Nó bắt đúng một điều: thẻ vừa hiện "Đã nhận" trong khi tệp ghi "chờ ký". Câu hỏi là: *điều đó có đúng không?*

Trả lời: **đúng, nhưng phải hiện đủ hai vế.** Nên tôi không tắt invariant — tôi thêm luật:

> `Đã nhận` hợp lệ trong đúng **hai** trường hợp: tệp ghi `Accepted`, **hoặc** có ADR phê chuẩn.
> Nhưng ở trường hợp thứ hai, thẻ **phải** hiện cả *"có hiệu lực theo ADR-0044"* **và** *"tệp vẫn ghi chờ ký"*.

Thử phá trên `app.js` thật:

| Phá | Kết quả |
|---|---|
| bỏ vế `"chờ ký"` khỏi nhãn người giữ vai | **FAIL 32** |
| thay nhãn "có hiệu lực theo …" bằng chữ "Đã nhận" trần | **FAIL 14** |

---

## 5. Một dương tính giả nữa của cổng 27

Cổng 27 đỏ vì ADR-0044 *"nhắc `supersede` mà không nêu ADR nào"*. Kiểm: đúng, nhưng hai chỗ:

1. Dòng **trích GP-16 nguyên văn** (`> "… supersede the prior decision …"`) — đang nói *về* chuẩn.
2. Câu của tôi: *"thêm một ADR mới supersede 0044"* — dùng `supersede` để nhắc một ADR **chưa tồn tại**.

(1) là dương tính giả thứ ba của cùng một dòng chữ ⇒ cổng nay bỏ qua khối trích dẫn `>`.
(2) là **cổng đúng** ⇒ tôi sửa câu, không sửa cổng.

---

## 6. Bằng chứng

```
PORTAL: PASS — 501 kiểm tra · 9 bất biến · 13 việc · 44 ADR (44 có tệp, 26 chờ ký, 0 thiếu tệp)
PORTAL SELFTEST: PASS — 10/10 (1 đối chứng + 9 phép phá)
PORTAL RENDER: PASS — app.js chạy trong DOM tối thiểu · 44 ADR · nhãn khớp dữ liệu
ADR STANDARDS: PASS — 314 kiểm tra · 7 bất biến · 44 ADR · đánh số 1..44 liên tục
```

Hai phép phá mới:

```
✓ P8 phê chuẩn bị dùng làm chữ ký (needs_signature về 0) → đỏ
✓ P9 phê chuẩn không có ngày → đỏ
```

---

## 7. Còn mở

| | Nợ | Vì sao |
|---|---|---|
| **W1** | **ADR-0044 đang `Proposed`** — chính PO phải ký | Một ADR tự phê chuẩn chính nó là vòng tròn. P13 canh, hạn 2026-12-15 |
| **W2** | 4 ADR `Proposed` (0011, 0016–0018) chưa ai quyết | Mỗi cái cần PO đọc và quyết riêng — không gộp |
| **W3** | 14 tệp vẫn ghi `*(chờ ký)*` | Đúng như thiết kế: bản ghi lịch sử không sửa. Có thể thêm `superseded-by: ADR-0044` nếu PO muốn liên kết hai phía đầy đủ theo GP-16 |
| **W4** | Cổng 25 chưa kiểm ADR phê chuẩn đã `Accepted` chưa | Hiện ADR-0044 `Proposed` mà vẫn phê chuẩn được — chấp nhận có ý thức, vì nếu bắt buộc thì P13 phải đóng trước khi ADR-0044 có hiệu lực, tức vòng tròn. Ghi nhận, không áp |
