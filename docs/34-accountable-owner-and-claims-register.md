# Người ký, hạn thật — và tờ A4 đưa cho nhà đầu tư

> **Tài liệu sống:** `docs/34-accountable-owner-and-claims-register.md`
> **Trạng thái:** `DECIDED` — chủ dự án đã chốt tên **VGU-BM** và chỉ định **người chịu trách nhiệm có tên**
> **Ngày:** 23/11/2026
> **Đầu vào:** xác nhận trực tiếp của chủ dự án, 23/11/2026 · `docs/33` (phân loại tuyên bố) · `pm/claims-registry.json`
> **Câu hỏi của người yêu cầu:** *"Đồng ý tên **VGU-BM**. Chúng tôi có 3 tuyên bố chưa chứng minh, đây là tên người chịu trách nhiệm: **Lê Xuân Khánh** và hạn xem lại."*
> **Liên quan:** `docs/33` §4 · `AGENTS.md` luật 1 & 3 · `docs/08` (mẫu tờ 1 trang cho luật sư)

---

## 0. Kết luận trước

**Đồng ý cả ba.** Tên **VGU-BM** được chốt. **Lê Xuân Khánh** là người chịu trách nhiệm. Hạn là **2026-12-18** (30 ngày).

Nhưng câu *"đây là tên người chịu trách nhiệm"* có một hệ quả mà bản nháp `docs/33` chưa xử lý, và nó **không** nằm ở chỗ ai ký — nó nằm ở chỗ **tờ giấy đó đi tới đâu**:

| # | Điều đã chốt | Điều tôi **điều chỉnh** | Vì sao |
|---|---|---|---|
| **1** | Tên **VGU-BM** | Không đổi | Đã đúng từ `docs/33` §2.2 |
| **2** | Người chịu trách nhiệm: **Lê Xuân Khánh** | Ghi **họ tên đầy đủ**, không ghi chức danh "PO" | `owner: "PO"` là chỗ lảng tránh: khi quá hạn, không ai biết phải tìm ai (§3) |
| **3** | Có hạn xem lại | Hạn phải là **một NGÀY**, không phải một cụm mô tả | "trước buổi pitch" **không bao giờ quá hạn** ⇒ hạn trang trí (§2) |
| **4** | Sổ đăng ký trong repo | In thành **một tờ A4** đưa kèm whitepaper | Sổ chỉ có giá trị khi **được đưa ra**; và tờ giấy **từ chối in** nếu đã quá hạn (§5) |

> **Điều tôi từ chối làm, dù nó là cách hiểu trực tiếp nhất:** đưa tên cá nhân vào `WHITEPAPER` hoặc vào PDF gọi vốn. Lý do ở §6 R5 — không phải vì thiếu tin, mà vì **tên người không phải bằng chứng**, và đặt nó cạnh một tuyên bố chưa kiểm trong tài liệu chào bán là đổi *rủi ro biên tập* thành *rủi ro cá nhân* mà không đổi được gì cho nhà đầu tư.

---

## 1. VGU-BM — tên đã chốt, và ba điều cấm khi dùng

**VGU-BM** = *Version-Gated Unit, Bonding-curve Model*.

Một câu định nghĩa, dùng nguyên văn khi cần:

> **VGU-BM:** đơn vị tài sản của giao thức là **phiên bản**, không phải con game; mỗi phiên bản mở khoá vốn theo **bonding curve riêng**, và chỉ mở khi phiên bản trước đã qua **cổng bằng giờ chơi thật**.

| Được | Không được |
|---|---|
| Dùng ở lần xuất hiện đầu trong `WHITEPAPER` §6, kèm chân trang ghi công **một lần** | Dùng như **bằng chứng**: "VGU-BM chứng minh mô hình đúng" là câu sai loại |
| Dùng giữa câu tiếng Anh: *"the VGU-BM model"* | Dùng như **thành tựu**: nó là tên **cơ chế**, không phải kết quả |
| Ghi công: *"Phát biểu tương đương độc lập: KVU (MetaPump, 2026)."* | Đặt tên người vào nguyên lý, hoặc so với một tên tuổi khác (§2.3 của KVU) |

> **Tên không phải bằng chứng.** VGU-BM làm cơ chế **trích dẫn được** — nó không làm cơ chế **đúng hơn**. Cổng `check_claims.py` không kiểm được tên hay, chỉ kiểm được câu có nhãn. Nên mọi câu chứa VGU-BM vẫn phải theo `docs/33` §3 như mọi câu khác.

---

## 2. Hai loại "hạn" — và lý do phải tách

"30 ngày" nghe như một hạn, nhưng nó là **hai** hạn khác nhau, và gộp chúng là cách để không hạn nào được thực hiện:

| Loại | Câu hỏi nó trả lời | Hết hạn thì sao | Ai làm |
|---|---|---|---|
| **Hạn quyết định** (`review_by`) | *Đến ngày này, câu này còn nằm nguyên trong whitepaper không?* | **Có**, nhưng phải đổi: dùng câu viết lại, hoặc gỡ | Người chịu trách nhiệm |
| **Điều kiện chấp nhận** (`blocked_on`) | *Cần gì để câu này được coi là đã kiểm?* | Không có hạn — nó là **điều kiện**, không phải lịch | Khảo sát / `programs/` |

Chốt cho ba mục:

| Mục | Hạn quyết định | Điều kiện để `ACCEPTED` |
|---|---|---|
| **C1** tiêu đề | **2026-12-18** | khảo sát launchpad ≥ 10 nền tảng, ghi `docs/00` hoặc ADR, có ngày |
| **C2** "tiên phong độc quyền" | **2026-12-18** | khảo sát 4 nhóm sản phẩm, ghi `docs/00` §2 |
| **C3** cột kiểm thử S8 | **2026-12-18** | `programs/` hiện thực + một lần chạy devnet |

**Vì sao cùng một ngày:** ba câu này sẽ được sửa trong **cùng một lần rebuild PDF** — tách ngày chỉ làm tăng số lần rebuild. Nhưng chúng **không** cùng điều kiện: C3 có thể đóng bằng code, C1/C2 chỉ đóng bằng khảo sát. Gộp ngày, tách điều kiện.

> **Hết hạn 2026-12-18 mà chưa có khảo sát** ⇒ mặc định **dùng câu viết lại** (`block_if_unmet: rewrite`), không phải "gia hạn". Gia hạn mà không đổi lý do là cách một hạn biến thành nghi thức.

---

## 3. Người chịu trách nhiệm — có tên, có căn cứ, có ranh giới

```json
"accountable": {
  "id": "LXK",
  "name": "Lê Xuân Khánh",
  "role": "người sáng lập kiêm PO (product owner)",
  "basis": "Xác nhận trực tiếp của chủ dự án trong phiên làm việc 2026-11-23.",
  "scope": "Nội dung ba tuyên bố và việc đóng chúng đúng hạn."
}
```

### 3.1. Ba ranh giới — ghi trước, vì sau thì không ai ghi

| Ranh giới | Nghĩa cụ thể |
|---|---|
| **Không phải chữ ký pháp lý** | Đây là trách nhiệm **biên tập**: ai sửa câu này, khi nào. Không phải cam kết về kết quả, không phải đại diện phát ngôn |
| **Không phải xác nhận câu viết lại sẽ đúng** | Câu viết lại cũng là một **đề xuất**; nó không được miễn khỏi `docs/33` §3 |
| **Không phải danh sách đầy đủ rủi ro** | Nó chứa đúng ba câu mà cổng tự động tìm được. Rủi ro thị trường/pháp lý/kỹ thuật ở tài liệu khác |

### 3.2. Điều xảy ra nếu người này rời dự án

Đây là lỗ hổng thật của mọi sổ "có owner", và nó phải được trả lời **trước** khi xảy ra:

- `owner` trỏ tới `id` trong khối `accountable`, **không** trỏ tới chức danh. Nếu `id` biến mất khỏi `accountable`, cổng **ĐỎ** (`P8`) — sổ không thể mồ côi trong im lặng.
- Chuyển giao = sửa `accountable` + ghi `basis` mới. **Không** được giữ nguyên tên người đã rời đi, vì khi đó tên là **vật trang trí**, đúng thứ §3.1 cấm.
- Nếu chưa có người nhận: `status` chuyển `REWRITTEN` hoặc gỡ câu. Không có trạng thái "chờ người ký".

---

## 4. Cổng: từ 16 lên 31 kiểm tra, và **bất biến thứ sáu**

`scripts/check_claims.py` nay kiểm cả **hình dạng của lời hứa**, không chỉ hình dạng của câu:

| # | Bất biến | Bắt được gì |
|---|---|---|
| 1–4 | (giữ nguyên `docs/33` §4.1) | tuyên bố không nhãn · đề xuất viết như thành tựu · tự so với tên người · gộp ba tầng |
| **5** | `owner` trỏ **người có tên** trong `accountable`, có `basis`; `review_by` là **ngày**; có `block_if_unmet` | `owner: "PO"` · `review_by: "trước buổi pitch"` · quá hạn mà không biết làm gì |
| **6** | **Quá hạn mà vẫn `OPEN` ⇒ ĐỎ** | Hạn không có hậu quả |

```
CLAIMS: PASS — 31 kiểm tra · 5 bất biến · 3 tuyên bố về thế giới, 3 mục trong sổ đăng ký
CLAIMS SELFTEST: PASS — 10/10 phép thử đúng chiều (9 phép phá + 1 đối chứng)
```

### 4.1. Ba lỗi schema có thật, phát hiện khi siết cổng

Cả ba đều nằm trong bản `pm/claims-registry.json` **tôi vừa viết ở vòng trước**:

| Lỗi | Vì sao nguy hiểm | Nay |
|---|---|---|
| `owner: "PO"` | Một **chức danh**. Khi quá hạn, "PO" không phải người để tìm | `owner: "LXK"` trỏ `accountable` có họ tên |
| `review_by: "trước buổi pitch với nhà đầu tư kế tiếp"` | Một **cụm mô tả**. Không có ngày nào nó quá hạn ⇒ không bao giờ phải làm | `2026-12-18` |
| Không có `block_if_unmet` | Quá hạn ⇒ trạng thái mơ hồ ⇒ mục "để sau" trá hình | `rewrite` + `suggested_rewrite` bắt buộc |

> Bài học giống hệt `docs/33` §4: **cổng cũ báo xanh vì nó chỉ kiểm sự tồn tại của một trường, không kiểm nội dung của trường đó.** `owner` khác rỗng, `review_by` khác rỗng — cả hai đều "đạt".

### 4.2. Ba phép phá mới

| # | Phá | Kết quả |
|---|---|---|
| 8 | `owner: "PO"` (chức danh) | ❌ `không có trong accountable — phải trỏ tới một NGƯỜI có tên` |
| 9 | `review_by: "trước buổi pitch"` | ❌ `không phải ngày YYYY-MM-DD` |
| 10 | `review_by: "2020-01-01"` + `OPEN` | ❌ `QUÁ HẠN 2020-01-01 (hôm nay …) mà vẫn OPEN` |

Ngày hôm nay được **ghim qua biến môi trường** `GAME9K_TODAY` trong phép thử, để phép phá 10 không phụ thuộc đồng hồ máy — một phép thử đỏ vào năm 2030 là phép thử hỏng.

---

## 5. Tờ A4 — `docs/Game9K-Claims-Register.pdf`

```bash
python3 scripts/build_claims_register.py docs/Game9K-Claims-Register.pdf
# built … (44379 bytes, 1 pages, md5 d1f0f3b54adea3b49d0b237c234bd5d1)
```

Đây là **lựa chọn thứ ba** trong ba lựa chọn về chỗ đặt tên, và nó là lựa chọn duy nhất vừa mạnh vừa không tạo rủi ro mới:

| Chỗ đặt tên | Mạnh với nhà đầu tư | Rủi ro |
|---|---|---|
| Chỉ trong `pm/claims-registry.json` | ❌ không ai đọc | ✅ không |
| Trong `WHITEPAPER` + 4 PDF | ✅✅ | ⚠️ tên cá nhân đứng cạnh tuyên bố chưa kiểm **trong tài liệu chào bán** |
| **Tờ A4 riêng, data room** *(chọn)* | ✅✅ | ✅ chỉ đưa cho người đã ký NDA; không nằm trong tài liệu công khai |

### 5.1. Ba tính chất, mỗi tính chất là một cổng cứng

1. **Sinh từ JSON, không viết tay** — không có đường nào để tờ giấy nói khác sổ. CI so md5 để bắt đúng việc đó.
2. **Đúng một tờ A4** — tràn trang ⇒ `exit 1`. Nội dung dài thêm thì phải cắt; người đọc data room chỉ đọc tờ đầu.
3. **Từ chối in bản đã quá hạn** — nếu một mục `OPEN` có `review_by` < `as_of`, builder **không dựng**. Một tờ giấy nói "hạn 18/12" mà in ngày 20/12 là tờ giấy tự bác mình.

### 5.2. Tờ này **không** phải gì — in ngay trên tờ giấy

- **Không phải chữ ký pháp lý** — trách nhiệm biên tập nội bộ.
- **Không phải xác nhận câu viết lại sẽ đúng** — câu viết lại cũng là đề xuất.
- **Không phải danh sách đầy đủ rủi ro** — chỉ là ba câu mà cổng tìm được.

> Ghi ba điều này **lên chính tờ giấy**, không chỉ trong tài liệu nội bộ: người đọc tờ giấy sẽ không đọc `docs/34`.

---

## 6. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R5** | Đưa tên cá nhân vào `WHITEPAPER`/PDF gọi vốn | Tên người **không phải bằng chứng**; và đặt nó cạnh tuyên bố chưa kiểm trong **tài liệu chào bán** đổi rủi ro biên tập thành rủi ro cá nhân mà không thêm gì cho nhà đầu tư. Tờ A4 data room làm được việc đó mà không có tác dụng phụ |
| **R6** | Dùng tên người để **tăng độ tin** | "Có người ký" chỉ nói rằng câu đó **sẽ được xử lý**; nó không nói câu đó đúng. Viết khác đi là dùng chữ ký làm bằng chứng |
| **R7** | Đặt hạn bằng cụm mô tả | "trước buổi pitch" không bao giờ quá hạn ⇒ hạn trang trí (`P9`) |
| **R8** | **Gia hạn** một mục quá hạn mà không đổi lý do | Gia hạn là nghi thức; hoặc có khảo sát mới (đổi `blocked_on`), hoặc dùng câu viết lại |

---

## 7. Việc **không** làm trong tài liệu này

- **Không sửa `WHITEPAPER.md`**, **không rebuild 4 PDF cũ** — ba câu vẫn `OPEN` cho tới 2026-12-18.
- Không đổi số đã kiểm (`12 KB`, `3,5 s`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không thêm tên người vào deck, whitepaper, hay `docs/08` (tờ cho luật sư — phạm vi của nó là câu hỏi pháp lý).
- Không gọi mạng, không thêm phụ thuộc Python (chỉ `reportlab`/`pypdf` đã ghim).

---

## 8. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | Trước **2026-12-18**: quyết từng mục — dùng câu viết lại (C1, C2), hay chờ `programs/` (C3) | Sau ngày đó, `check_claims.py` **ĐỎ** và tờ A4 **từ chối dựng** |
| **2** | Nếu sửa `WHITEPAPER` → rebuild **năm** PDF trong cùng PR (`docs/README-PDF.md`) | `AGENTS.md` luật 2: sửa nguồn, không sửa bản dựng |
| **3** | Dùng **VGU-BM** ở lần xuất hiện đầu trong `WHITEPAPER` §6, ghi công KVU **một lần** ở chân trang | §1 — dẫn nguồn ≠ tự so |
| **4** | Đưa `check_claims.py` vào `AGENTS.md` như luật thứ tư (cấm tuyên bố không nhãn) | `AGENTS.md` cấm **hứa hẹn**, chưa cấm **tuyên bố về thế giới** — lỗ hổng lớn hơn |
| **5** | Khi có người nhận bàn giao: sửa `accountable` + `basis` mới, không giữ tên người đã rời | §3.2 — sổ không được mồ côi trong im lặng |
