# ADR-0044 — Phê chuẩn 14 ADR đã `Accepted` nhưng chưa ai ký, bằng một quyết định mới

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-24
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0001`](ADR-0001-modular-phase-loop.md) → [`ADR-0015`](ADR-0015-opensource-stack.md) · [`docs/46`](../../../46-nineteen-adrs-and-seventeen-empty-signatures.md) §2 · [`docs/47`](../../../47-po-confirmation-and-the-last-eight-adrs.md) §2 · [`docs/48`](../48-adr-standards-from-two-repos.md) §2.3

---

## 0. Trả lời ngắn

**Mười bốn ADR đang ghi `Accepted` nhưng người quyết chỉ là một chức danh, và chính tệp nói nó đang chờ ký.** ADR này phê chuẩn chúng bằng một quyết định mới, thay vì sửa 14 bản ghi lịch sử.

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Có bao nhiêu ADR như vậy? | **14**, không phải 18 — xem §1. Con số 18 trên portal là *"chưa ký"*, không phải *"Accepted mà chưa ký"* |
| 2 | Phê chuẩn nghĩa là gì? | PO xác nhận các quyết định đó **đang có hiệu lực**, do PO giữ vai đã quyết |
| 3 | Có sửa 14 tệp không? | **Không.** GP-16 §Supersession: ADR đã `Accepted` không được sửa nghĩa; thay đổi đi bằng ADR mới |
| 4 | Portal có đổi số không? | **Không.** Vẫn 14 tệp `chưa ký`; thêm `signer_alternatives` (§4) |
| 5 | Cái gì thật sự đổi? | `display_state` của 14 tệp chuyển **`proposed` → `accepted`**, có `decided_by: ADR-0044` làm căn cứ |

**Điều quan trọng nhất:** ADR này **không** làm 14 tệp kia trông như đã ký. Nó nói: *một người, vào một ngày, đã xác nhận các quyết định đó có hiệu lực* — và mọi con số "chưa ký" vẫn giữ nguyên, vì chúng vẫn đúng.

---

## 1. Vì sao 14, không phải 18

Đây là chỗ dễ sai nhất, và tôi đã sai khi trình bày với PO lần trước. Đo lại:

| Nhóm | Số tệp | Cần ADR-0044? |
|---|---|---|
| `Accepted` + người quyết là **chức danh** + tệp ghi **chờ ký** | **14** (0001–0010, 0012–0015) | **có** — đang có hiệu lực mà không ai ký |
| `Proposed` + chức danh + chờ ký | **4** (0011, 0016, 0017, 0018) | không — chúng **chưa** có hiệu lực, nên chưa có gì để phê chuẩn |
| `Accepted` + **PO (có tên)** | 5 (0019–0022, 0038) | không — đã có người ký |

Tổng "chưa ký" = 14 + 4 = **18**. Nhưng chỉ **14** đang ở trạng thái mâu thuẫn thật: *có hiệu lực mà không ai ký*.

Bốn tệp `Proposed` **không** cần phê chuẩn — chúng đang đúng. Phê chuẩn một đề xuất là tự nhận nó, và đó là việc của một bước khác (PO quyết, sau khi đọc).

**Nói cách khác:** ADR-0044 đóng lỗ hổng *"14 quyết định đang chạy mà không ai chịu trách nhiệm"*. Nó không đóng 4 đề xuất đang mở — đó là quyết định riêng, từng cái một.

### 1.1. Tại sao không phải `Rejected`

Một lựa chọn khác là để 14 ADR đó thành `Proposed` (rút lại hiệu lực) cho tới khi có người ký. Tôi **không** đề nghị: 14 quyết định đó đã được dùng để biện minh cho mã đã merge (`docs/46` §2). Rút hiệu lực *hồi tố* là tuyên bố rằng mã đang chạy chưa từng được phép — điều đó có thể đúng về mặt giấy tờ nhưng sai về mặt vận hành, và nó không giúp ai. Cách đúng là **xác nhận lại từ hôm nay**, có ngày, có người.

---

## 2. Quyết định

**PO phê chuẩn 14 ADR sau là quyết định có hiệu lực, do chính PO giữ vai `Principal Architect` đã quyết:**

```
ADR-0001  ADR-0002  ADR-0003  ADR-0004  ADR-0005  ADR-0006  ADR-0007
ADR-0008  ADR-0009  ADR-0010  ADR-0012  ADR-0013  ADR-0014  ADR-0015
```

Căn cứ ba tầng, cả ba đều phải đúng:

1. **Ai giữ vai** — PO xác nhận 2026-11-24 giữ cả bốn vai Founder · PO · TL · PA
   (`ROLE_HOLDER` trong `scripts/gen_portal_data.py`, mỗi vai có `basis`).
2. **Quyết định nào** — 14 số hiệu ở trên, liệt kê **tường minh**, không dùng
   khoảng `0001–0015` (khoảng đó sẽ nuốt ADR-0011 `Proposed` và mọi ADR thêm sau).
3. **Ngày** — 2026-11-24. Một phê chuẩn không có ngày là một phê chuẩn không kiểm được.

### 2.1. Điều ADR này KHÔNG làm

- **Không** sửa trường `Người quyết` của 14 tệp. Bản ghi lịch sử giữ nguyên
  `Principal Architect *(chờ ký)*` — đó là sự thật về **lúc viết**.
- **Không** đổi số "ADR chưa có người ký" trên portal. Vẫn **18**.
- **Không** phê chuẩn 0011, 0016, 0017, 0018 (đang `Proposed`).
- **Không** phê chuẩn 0019–0022, 0038 (đã có PO ký).
- **Không** tuyên bố mã đã merge là đúng. Phê chuẩn một *quyết định* không xác nhận
  *cách hiện thực* nó.

---

## 3. Vì sao đây là đường đúng, không chỉ là đường dễ

GP-16 §Supersession (từ `microsoft/hve-core`, MIT, `adr-standards.instructions.md`):

> *"Treat each ADR as version-controlled; do not edit accepted decisions to change their meaning. When circumstances change, supersede the prior decision with a new ADR that links back to the original."*

Hai đường, chỉ một đường đúng:

| | Sửa 14 tệp | ADR-0044 (đường này) |
|---|---|---|
| Bản ghi lịch sử | bị viết lại — mất bằng chứng "lúc đó chưa ai ký" | giữ nguyên |
| Kiểm được không? | không: ai sửa gì, khi nào, không còn dấu | có: số hiệu + ngày + danh sách |
| Nếu PO đổi ý sau đó | phải sửa lại 14 tệp nữa | thêm một ADR mới thay thế `ADR-0044` (liên kết hai phía) |
| Trung thực với `docs/46` §2 | phủ nhận phát hiện đó | xác nhận nó, rồi xử lý |

Đường thứ nhất làm cổng 25 xanh **bằng cách xoá bằng chứng**. Đó đúng là điều
`docs/46` §2.2 đã từ chối làm, và `docs/48` §2.3 đã xác nhận lại.

---

## 4. Cơ chế: `signer_alternatives` — một trường mới, không phải một ngoại lệ

Sau ADR này, mỗi ADR trong 14 tệp có **hai** cách trả lời câu *"ai chịu trách nhiệm?"*:

| Nguồn | Trả lời | Dùng khi |
|---|---|---|
| chính tệp ADR | `Principal Architect *(chờ ký)*` | đọc lịch sử — lúc viết, chưa ai ký |
| `signer_alternatives[]` | `ADR-0044 · 2026-11-24 · Lê Xuân Khánh (PO đã xác nhận)` | đọc hiện tại — nay đã có người nhận |

`gen_portal_data.py` sinh trường này **từ chính ADR-0044**, không từ một bảng
viết tay: ADR-0044 liệt kê 14 số hiệu, generator đọc danh sách đó. Thêm một ADR
vào phạm vi phê chuẩn = sửa ADR-0044, không sửa mã.

Quy tắc cứng, đã thành bất biến của cổng 25:

- **`signature` KHÔNG đổi** khi có `signer_alternatives`. Tệp vẫn ghi `chờ ký` ⇒
  vẫn `role_only`. Nếu ai đó làm `signature` thành `named` nhờ trường này, đó là
  **ký khống qua đường vòng** — và đó là điều bất biến mới canh.
- **`display_state` được phép** chuyển `accepted`, vì nay có một quyết định có
  ngày, có người, có số hiệu nói nó có hiệu lực.
- **`decided_by`** ghi số hiệu ADR phê chuẩn, để portal hiện được *"có hiệu lực
  theo ADR-0044, 2026-11-24"* thay vì một chữ `Accepted` trần.

---

## 5. Ranh giới trung thực

- **Tôi không biết 14 quyết định đó có đúng về kỹ thuật hay không.** ADR này
  không đánh giá nội dung; nó chỉ xử lý câu hỏi *ai chịu trách nhiệm*.
- **"PO xác nhận 4 vai" là lời PO nói, không phải bằng chứng độc lập.** Nó được
  ghi kèm `basis` đúng như quy ước, nhưng không có tài liệu thứ ba nào xác nhận
  ngoài chính lời đó. Nếu điều đó quan trọng với nhà đầu tư, cần một văn bản riêng.
- **`signer_alternatives` là cơ chế của repo này, không phải của MADR v4.** MADR
  có `decision-makers` tự do; tôi không mượn tên trường đó vì nó mang nghĩa khác
  (người tham gia quyết), và ghi đè nghĩa một trường chuẩn là cách tốt nhất để
  sau này không ai đọc đúng.
- **Chưa có cổng nào kiểm `signer_alternatives` trỏ tới một ADR tồn tại và
  `Accepted`.** Cổng 25 kiểm số hiệu trong danh sách là số hiệu ADR thật; nó
  **chưa** kiểm ADR đó đã `Accepted`. Ghi ở đây, làm sau.

---

## 6. Hệ quả

| Đối tượng | Trước | Sau |
|---|---|---|
| 14 tệp ADR | `display_state = proposed` | `display_state = accepted`, `decided_by = ADR-0044` |
| Số "chưa có người ký" | 18 | **18 (không đổi)** |
| Số "có hiệu lực" | 18 | 18 (không đổi tổng; 14 tệp nay có căn cứ thay vì mâu thuẫn) |
| P13 | "gán tên cho 18 ADR" | còn **4 ADR `Proposed`** (0011, 0016–0018) + việc ký ADR-0044 |
| Portal | thẻ ghi *"chỉ có chức danh — chưa ai ký"* | thêm *"có hiệu lực theo ADR-0044"* — **cả hai** hiện cùng lúc |

Điểm cuối là điểm chính: thẻ ADR sẽ nói **hai câu cùng lúc**, vì cả hai đều đúng.
Một chữ `Accepted` duy nhất không nói được điều đó.

---

## 7. Điều ADR này KHÔNG bao gồm

- **Không** phê chuẩn nội dung kỹ thuật của 14 quyết định (xem §5).
- **Không** phê chuẩn ADR-0011, 0016, 0017, 0018 — bốn đề xuất đang mở.
- **Không** cấp cho PO quyền ký thay bất kỳ vai nào khác trong tương lai: mỗi lần
  cần một ADR mới như ADR này, không phải một uỷ quyền thường trực.
- **Không** sửa `README.md` của `08-adr` (vẫn ghi `Accepted (chờ ký)` — mâu thuẫn
  gốc ở tệp nguồn, đã ghi ở `docs/48` §7 W4).
- **Không** áp cho ADR-0044 chính nó: ADR này `Proposed`, và **chính PO phải ký nó**
  thì hiệu lực mới bắt đầu. Một ADR tự phê chuẩn chính nó là vòng tròn.
