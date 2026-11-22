# Gitcoin — bốn mẫu dùng được, một mẫu phải từ chối

> **Tài liệu sống:** `docs/19-gitcoin-patterns.md`
> **Trạng thái:** `SCOPING`
> **Ngày:** 22/11/2026
> **Nguồn:** `gitcoin.co` — trang chủ, mục *Case Studies / Mechanisms / Research / Campaigns / Apps* (truy cập 22/11/2026)
> **Liên quan:** `docs/18` (flagship template), `docs/13` (affiliate), `docs/16` (game neo), `WHITEPAPER §54` (bonding curve theo mốc)

---

## 0. Kết luận trước

**Gitcoin hiện không còn là một quỹ tài trợ — nó là một thư viện.** Trang chủ 2026 tự mô tả: *"directory and reference library for funding mechanisms"*, với `120+` mục ở **mỗi** trong năm loại: case study, cơ chế, nghiên cứu, chiến dịch, ứng dụng.

Đó là **một quyết định sản phẩm**, và nó là bài học đầu tiên cho Game9K:

| | Gitcoin (2026) | Game9K nên làm theo? |
|---|---|---|
| Bán gì | **Tri thức về cơ chế tài trợ**, miễn phí, cộng đồng đóng góp | ✅ **Có** — nhưng ở đúng chỗ: **tài liệu kỹ thuật cho studio**, không phải nội dung thay sản phẩm |
| Từng làm gì | Chạy quỹ tài trợ công (quadratic funding) | ⚠️ Mô hình QF **không** dùng được cho Game9K — xem §4 |

**Bốn mẫu dùng được, một phải từ chối:**

| # | Mẫu | Dùng cho Game9K |
|---|---|---|
| **G1** | **Bắt buộc đăng nhập/quy trình mới xem chi tiết** — đổi lại, ai cũng được xem trang tổng | ✅ Cách viết tài liệu studio |
| **G2** | **Hồ sơ quyên góp theo từng chiến dịch**, mỗi chiến dịch công bố *quỹ ghép · số dự án · thời gian* | ✅ **Khớp gần như 1:1 với bonding curve theo mốc** |
| **G3** | **Chiến dịch "đang diễn ra"** được làm nổi, không phải danh sách chết | ✅ Trang studio cần cùng cấu trúc |
| **G4** | **Tiêu chuẩn chất lượng cao, có người duyệt, nói rõ là có duyệt** | ✅ Studio phải biết mình **đang được đánh giá** |
| **G5** | **Quadratic funding / quỹ ghép từ quỹ chung** | ❌ **Không.** Xem §4 — phá đúng cơ chế bảo vệ của Game9K |

---

## 1. G1 — Hồ sơ công khai, chi tiết có điều kiện

Gitcoin cho xem **trang tổng** của mọi chiến dịch; chỉ vào sâu mới cần bước tiếp theo. Đó là cách vừa **tạo niềm tin** (ai cũng kiểm được), vừa **giữ chân người dùng thật**.

**Áp dụng cho Game9K — trang studio:**

| Công khai, không cần gì | Cần đăng nhập mới xem |
|---|---|
| Tên studio, game, mốc đang ở (`M1…M4`) | Số liệu chi tiết từng ngày |
| Tổng SOL đã mở, tổng token đã mở khoá | Danh sách nhà đầu tư riêng lẻ |
| Trạng thái kiểm định (`base_sha256`, ngày qua Inspector) | Dữ liệu thô của `verified_play` |
| Lý do **bị trả lại** (nếu có) | Hợp đồng, điều khoản riêng |

> **Điểm quan trọng:** dòng *"lý do bị trả lại"* phải nằm ở cột **công khai**. Đây đúng là điều kiện thứ ba ở `docs/18` §2.2 (đã từng từ chối, công bố kèm lý do), và Gitcoin cho thấy nó làm được mà không lộ dữ liệu riêng.

---

## 2. G2 — Hồ sơ theo chiến dịch: mẫu khớp nhất

Gitcoin hiển thị mỗi chiến dịch bằng một **bộ ba con số + một khoảng thời gian**:

```
Protocol Guild     Quỹ ghép $100M+   ·  ~190 dự án   ·  05/2022 – đến nay
TheDAO Security    Quỹ ghép $220M+   ·  chưa có      ·  01/2026 – đến nay
```

**Game9K đã có đúng cấu trúc đó, chỉ chưa hiển thị theo dạng này.** `WHITEPAPER §54`:

```
M1: 15%  →  M2: 33%  →  M3: 53%  →  M4: 70%   (tổng cung mở dần)
```

Ghép lại thành một dòng trên trang studio:

```
<bonding curve>  Đã mở 33,0% cung  ·  4 mốc  ·  M2/4  ·  giải ngân theo cột mốc
```

| Việc cần làm | Vì sao |
|---|---|
| Đưa **mốc hiện tại** lên đầu trang studio, dạng `M2/4` | Người xem hiểu ngay tiến độ mà không đọc bảng |
| Mỗi mốc có **ngày dự kiến** và **điều kiện mở** viết bằng một câu | Mốc không có điều kiện là mốc không kiểm được |
| Mốc **đã qua** hiện `sha256` + ngày Inspector | Đây là bằng chứng; mốc chưa qua thì để trống rõ ràng |

> **Không đổi số nào.** Đây là **cách hiển thị** của số đã có, không phải số mới.

---

## 3. G3 — "Đang diễn ra" thay vì danh sách chết

Trang chủ Gitcoin có mục **Featured Campaigns** — hai chiến dịch đang chạy, làm nổi. Không phải bảng `120+` dòng.

**Áp dụng:** trang chủ Game9K không nên mở bằng "1.200 tựa game". Nên mở bằng **`3` thứ đang diễn ra**:

1. Một studio **đang ở giữa** một mốc (có tiến độ, có ngày).
2. Một cuộc **đấu mù Arena** đang mở bình chọn.
3. Một **thử thách cộng đồng** đang chạy (nếu có).

| Vì sao | |
|---|---|
| Người mới hiểu cổng **đang làm gì** trong `3` giây | Con số `1.200` không nói lên điều đó |
| Tạo lý do **quay lại** hằng ngày | Danh sách tĩnh thì xem một lần là hết |
| Khớp với `docs/16` §5.3 (KOL giới thiệu **câu chuyện**, không chỉ game) | Cùng một logic |

---

## 4. G5 — Quadratic funding: **từ chối**, và lý do không phải "khó"

Đây là phần quan trọng nhất của tài liệu.

### 4.1. Vì sao QF hấp dẫn

Quadratic funding ghép quỹ theo **số người ủng hộ**, không theo số tiền. Nó thưởng cho dự án có **nhiều người tin**, kể cả người góp rất ít. Nghe rất hợp với một cổng game cộng đồng.

### 4.2. Vì sao nó phá đúng thứ Game9K đang xây

> **QF trả tiền theo *số người*. Game9K trả tiền theo *phiên chơi đã kiểm chứng*. Hai đơn vị khác nhau, và QF biến mọi nỗ lực chống bot thành vô nghĩa.**

| | Nếu dùng QF | Nếu giữ cơ chế hiện tại |
|---|---|---|
| Đo cái gì | Số **người ủng hộ** | Số **phút chơi hợp lệ** (`work`) |
| Đơn vị tấn công | **Một người, nhiều ví** | **Một phiên, nhiều thao tác thật** |
| Cách ăn gian | Tạo nhiều danh tính ủng hộ | Phải chơi thật, liên tục, qua nhiều epoch |
| Chi phí phòng thủ | Chống Sybil trên **tài khoản** | Chống bot trên **hành vi** |
| Thứ đang có sẵn | ❌ Không có gì | ✅ `sybil_cluster_id`, `input_entropy_score`, ALTCHA, PoP decay |

**Và QF thưởng chính xác thứ mà kế hoạch flagship đang cố tránh** (`docs/18` §3): một khung game, nhiều bản reskin. Với QF, `50` bản reskin của cùng một khung **không** phải vấn đề — mỗi bản tự kéo người ủng hộ, và quỹ ghép trả cho cả `50`. Nó **khuyến khích** đúng thứ làm Arena vô dụng.

### 4.3. Nhưng có **một** phần của QF dùng được

Không phải cơ chế tài trợ — mà là **cách công bố**. QF nổi tiếng vì **ai cũng tính lại được** kết quả từ dữ liệu công khai. Đó là tinh thần đúng, và Game9K đã có sẵn công cụ: `scripts/verify_pop_decay.py`, `base_sha256`, Inspector.

**Áp dụng:** mọi con số công bố trên trang studio phải **tính lại được** bằng script công khai. Không phải "QF", mà là **kỷ luật công bố của QF**.

> Đây là cùng nguyên tắc đã ghi ở `docs/14` §A4 (sổ số liệu 6 cột) và `docs/15` §3-A4 (bộ đếm tự đo được). QF chỉ là **ví dụ nổi tiếng nhất** của việc đó.

---

## 5. G4 — Duyệt có tiêu chuẩn, và **nói rõ là có duyệt**

Gitcoin ghi trên trang chủ: *"Only well-researched, original submissions that meet our high standards are accepted."* Đây là câu quan trọng hơn nó trông.

**Vì sao:** một thư viện **không** nói rõ có duyệt sẽ bị đọc là *"ai đăng cũng được"* → mất giá. Một thư viện nói rõ có duyệt → **mỗi mục có giá trị**.

**Áp dụng cho Game9K:** trang studio và trang game phải nói rõ:

| Câu cần có trên UI | Vì sao |
|---|---|
| *"Đã qua Inspector ngày `dd/mm/yyyy`"* | Có mốc thời gian, kiểm được |
| *"Kiểm định tự động, không phải xác nhận chất lượng sáng tạo"* | Phân biệt **đạt ngưỡng** với **hay** — chính là điều `docs/18` §1.3 lo |
| *"Game này dựa trên Game9K Starter Kit"* | Nhãn minh bạch của `docs/18` §3.3 |
| *"Đã bị trả lại `n` lần"* + lý do | Điều kiện tạo niềm tin ở `docs/18` §2.2 |

> Điểm thứ hai là điểm dễ bị bỏ nhất và **dễ mất uy tín nhất**. Nếu cổng để người đọc hiểu "đã kiểm định = đã hay", mọi tranh chấp sau đó sẽ đổ lên cổng.

---

## 6. Từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | **Quadratic funding** / quỹ ghép từ ngân sách nền tảng | §4.2 — trả tiền theo *số người*, thưởng cho Sybil, và thưởng cho reskin |
| **R2** | Mô hình "cổng biến thành thư viện" | Gitcoin làm được vì họ **đã** phân phối xong `$100M+`. Game9K chưa có gì để phân phối — làm thư viện lúc này là **tránh việc khó** |
| **R3** | Bỏ bảng xếp hạng để thay bằng "danh mục cơ chế" | Cùng lý do R2. Không có người chơi thật thì không có gì để xếp hạng |
| **R4** | Công bố số liệu **không tính lại được** bằng script | §4.3 — trái kỷ luật đã có ở `docs/14` và `docs/15` |
| **R5** | Ghi "đã kiểm định" mà không nói rõ **kiểm cái gì** | §5 — biến "đạt ngưỡng" thành "chất lượng cao", tạo tranh chấp về sau |

---

## 7. Việc **không** làm trong tài liệu này

- Không đổi bonding curve, `15/33/53/70%`, hay bất kỳ số nào ở `WHITEPAPER §54`.
- Không đổi `W = 0.60`, `H = 180`, `eCPM`, schema (**34** bảng), deck, 4 PDF.
- Không đề xuất nộp đơn xin tài trợ Gitcoin hay quỹ nào — không có thông tin về điều kiện, và đó không phải việc của tài liệu kỹ thuật.

## 8. Thứ tự thi công

| # | Việc | Vì sao |
|---|---|---|
| **1** | Trang studio dạng **G2**: `M2/4` + ngày + điều kiện mỗi mốc | Chỉ là cách hiển thị số đã có — rẻ nhất |
| **2** | Đưa **"lý do bị trả lại"** vào cột công khai (G1) | Điều kiện tạo niềm tin, `docs/18` §2.2 |
| **3** | Trang chủ mở bằng **3 thứ đang diễn ra** (G3) | Thay `1.200 tựa` bằng thứ có nghĩa |
| **4** | Viết câu **"kiểm định tự động ≠ xác nhận chất lượng"** (G4) | Tránh tranh chấp về sau |
| **5** | Viết script công bố để **mọi con số trên trang studio tính lại được** | Kỷ luật của QF, không phải QF |
