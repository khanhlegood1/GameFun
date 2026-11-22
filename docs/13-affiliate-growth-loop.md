# Affiliate — GoStream & StreamAgain dạy gì cho Game9K

> **Tài liệu sống:** `docs/13-affiliate-growth-loop.md`
> **Trạng thái:** `SCOPING` — thiết kế, chưa thi công
> **Ngày:** 22/11/2026
> **Nguồn:** `gostream.co/vi/blog/chuong-trinh-affiliate-marketing.13.html`, `gostream.co/vi/pricing`, `app.streamagain.co/affiliate` (bị chặn sau login), `streamagain.co/*`
> **Câu hỏi:** hai chương trình affiliate này có gì dùng được cho Game9K?

---

## 0. Kết luận trước

**Có, nhưng phần dùng được không phải "trả hoa hồng cho người giới thiệu".** Game9K đã có referral trong `FR-POP-01` (chỉ trả khi người được mời đạt Bronze). Cái **thiếu** là cơ chế *ai được tham gia, trả cho cái gì, và trả bằng gì*.

Ba thứ đáng lấy:

| # | Lấy từ | Nội dung | Vì sao đáng |
|---|---|---|---|
| **A1** | GoStream | **Trả theo doanh thu định kỳ, không trả một lần** | Với Game9K: studio nhận **doanh thu Ads của đúng game đó** khi mang traffic về → chia sẻ doanh thu vĩnh viễn, không phải bounty một cục |
| **A2** | GoStream | **Phễu duyệt người tham gia** (đăng ký → xét duyệt → duyệt mới chạy) | Chặn farm link rác trước khi nó xảy ra; rẻ hơn phát hiện sau |
| **A3** | StreamAgain | **Trang affiliate gated sau login** | Tránh lộ bảng hoa hồng và số liệu cho người chưa xác thực |

Và **ba thứ phải từ chối** — quan trọng hơn phần lấy:

| # | Nội dung | Vì sao từ chối |
|---|---|---|
| **R1** | Mô hình "trả hoa hồng % trên doanh thu **thuê bao**" | Game9K **không có thuê bao**. Người chơi miễn phí; doanh thu là phí on-chain + Ads |
| **R2** | "Thu nhập thụ động lâu dài" như lời hứa marketing | Trong tài liệu tài chính đây là **forward-looking statement**; ở Việt Nam còn có thể bị đọc là hứa hẹn lợi nhuận. `AGENTS.md` đã cấm |
| **R3** | Trả thưởng affiliate bằng **token** | Biến người giới thiệu thành người bán token; vướng câu hỏi chứng khoán mà legal brief đang chờ luật sư trả lời |

---

## 1. Bằng chứng quan sát được

| Mã | Quan sát | Nguồn |
|---|---|---|
| **F1** | GoStream trả hoa hồng khi người được giới thiệu **thanh toán lần đầu hoặc gia hạn**; lý do họ nêu rõ: sản phẩm thuê bao nên người dùng gia hạn hàng tháng → người giới thiệu có "thu nhập thụ động lâu dài" | Trang blog affiliate, truy cập 22/11/2026 |
| **F2** | Điều kiện tham gia: **blogger, nhà xuất bản, người tạo nội dung có cộng đồng** | Như trên |
| **F3** | Quy trình: **đăng ký → "chúng tôi sẽ xem xét đơn và phê duyệt nếu đáp ứng tiêu chí"** | Như trên |
| **F4** | Bảng giá: Free `0K` · Plus `199K` · Premium `599K` /tháng. Thanh toán nhận **thẻ quốc tế, PayPal, Payoo, VNPay, VTCPay** | `gostream.co/vi/pricing` |
| **F5** | Trang affiliate của StreamAgain: `app.streamagain.co/affiliate` **chuyển hướng về trang đăng nhập** (`/login?next=/affiliate`) | Truy cập 22/11/2026 |
| **F6** | StreamAgain và GoStream **cùng một bộ khung sản phẩm** (Nuxt, cùng file ảnh `logo-main`, `menu.053f6c0.png`, `analytics.gif` từ `p.cityadstrack.com`) | So sánh mã nguồn trang |
| **F7** | Điều khoản StreamAgain còn **sót tên thương hiệu khác**: email khiếu nại ghi `contact@streamyard.com`, có câu "read the terms … of StreamYard" | `streamagain.co/terms` |

> **Ghi chú:** F6 và F7 **không** phải bằng chứng pháp lý về quan hệ giữa hai công ty, và tài liệu này **không** kết luận gì về điều đó. Chúng chỉ có nghĩa: *đừng dùng hai site này làm hai mẫu độc lập* — chúng là một mẫu, nhìn từ hai góc.

### 1.1. Điều **không** kiểm chứng được

- **Tỷ lệ hoa hồng** của cả hai: trang GoStream hiển thị hình ảnh (`affilate_image_01`) chứa nội dung, không trích được thành chữ; trang StreamAgain bị login chặn. **Không đưa con số nào vào tài liệu này.**
- **Thời hạn cookie, thời gian giữ, ngưỡng chi trả tối thiểu, điều khoản chống gian lận**: không công khai.

---

## 2. Áp dụng cho Game9K: hai loại "affiliate", đừng lẫn

Đây là điểm dễ sai nhất. Game9K có **hai** đối tượng giới thiệu khác hẳn nhau, và trả thưởng khác hẳn nhau:

| | **Người chơi giới thiệu người chơi** | **Studio / nhà sáng nội dung giới thiệu game** |
|---|---|---|
| Đã có trong đặc tả? | **Có** — referral trong `FR-POP-01` | **Chưa** — chỉ có chia Ads 100/0 và 50/50 |
| Trả bằng gì | `SPARK` (không chuyển nhượng) + quyền ưu tiên | **USD từ doanh thu Ads của chính game đó** |
| Điều kiện trả | Người được mời đạt **Bronze** (`referral_verified`) | Traffic **đã kiểm chứng** qua SDK (session thật, không bot) |
| Chống lạm dụng | PoP Tier + `sybil_risk_score` | Cùng bộ lọc PoP + trần theo game |

**Điều đáng lấy từ GoStream là cột phải** — nhưng đổi "thuê bao" thành "doanh thu Ads của game". Đó là biến thể tự nhiên của mô hình 50/50 đã có: người mang traffic về **giữ phần của họ lâu dài**, không phải nhận một cục.

---

## 3. Thiết kế đề xuất

### 3.1. Chương trình A — Người chơi giới thiệu người chơi (đã có, chỉ cần chốt luật)

| Hạng mục | Chốt |
|---|---|
| Thưởng | `SPARK`, **không** quy đổi trực tiếp ra token ngay |
| Điều kiện | Người được mời đạt **Bronze** và có **≥ 120 phút chơi hợp lệ** (`verified_play`) |
| Trần | `≤ 20` referral được tính /người /tháng — chặn "trại link" |
| Không thưởng khi | Người được mời và người mời **cùng cụm Sybil** (`sybil_cluster_id`), cùng thiết bị, hoặc cùng `/24` IP hash |
| Hết hạn | Link có hạn 90 ngày; sau đó không tính |

### 3.2. Chương trình B — Studio / creator giới thiệu game (mới)

Đây là phần **học trực tiếp** từ GoStream, đổi đối tượng:

| Hạng mục | Chốt |
|---|---|
| Đối tượng | Studio sở hữu game, **hoặc** creator được studio uỷ quyền bằng mã mời |
| Trả bằng | **USD từ doanh thu Ads của chính game đó** — không phải token, không phải SOL |
| Tỷ lệ | Creator nhận **phần chia của studio** trong doanh thu Ads, do studio tự quyết; **Game9K không đổi mức 50/50 hiện hành** |
| Điều kiện | Chỉ tính phiên **đã qua bộ lọc PoP** (SDK heartbeat + input entropy), không tính bot |
| Thu hồi | Phiên bị phát hiện gian lận sau đó → **trừ vào kỳ chi trả kế tiếp**, có ghi `audit_logs` |
| Duyệt | **Có phễu duyệt** (A2): đăng ký → xét → duyệt mới có link. Duyệt tay ở giai đoạn đầu, vì số lượng nhỏ |

**Vì sao trả bằng USD chứ không token:** doanh thu Ads vốn đã là USD (`docs/WHITEPAPER.md` dòng 550). Trả bằng đúng đơn vị đã thu được thì không tạo thêm nghĩa vụ tài chính mới, không tạo áp lực bán token, và không kéo câu hỏi "token là chứng khoán" vào thêm một nhóm người nhận.

### 3.3. Điều kiện chống lạm dụng — dùng lại hạ tầng đã có, không xây mới

| Rủi ro | Chốt sẵn có |
|---|---|
| Bot tạo tài khoản để tự giới thiệu | ALTCHA PoW + `sybil_risk_score` |
| Farm link trên nhiều tài khoản | `sybil_cluster_id` (đã có trong `user_wallets`) |
| Traffic ảo để ăn chia Ads | Bộ lọc PoP: `input_entropy`, heartbeat tiền cảnh, trần phiên `2 giờ` |
| Rửa nhiều tài khoản luân phiên | `cooldown_until` 7 ngày khi đổi ví |

**Không cần bảng mới cho chương trình A.** Chương trình B cần một bảng nhỏ (`creator_codes`) — chỉ thêm khi thực sự mở chương trình, không thêm trước.

---

## 4. Ba điều từ chối, ghi rõ lý do

| Mã | Nội dung bị từ chối | Lý do |
|---|---|---|
| **R1** | Sao chép nguyên mô hình "hoa hồng % trên thuê bao" | Game9K **không có thuê bao**. Copy nguyên sẽ tạo ra một chương trình trả tiền cho doanh thu không tồn tại |
| **R2** | Dùng câu "thu nhập thụ động lâu dài" trong tài liệu Game9K | Đây là **hứa hẹn lợi nhuận** bằng ngôn ngữ marketing. Trong whitepaper gọi vốn, nó là forward-looking statement phải có disclaimer; ở Việt Nam còn có thể bị đọc là cam kết lợi nhuận. `AGENTS.md` cấm loại câu này |
| **R3** | Trả thưởng affiliate bằng token | Người nhận thành người bán token; thêm một nhóm chịu câu hỏi chứng khoán mà legal brief đang chờ luật sư |

---

## 5. Việc **không** làm trong tài liệu này

- Không đổi tỷ lệ 50/50 trong `docs/WHITEPAPER.md` dòng 550. Đó là số liệu kinh tế đã kiểm chứng bằng script; đổi nó cần sửa whitepaper + deck + PDF, không phải việc của một tài liệu nghiên cứu.
- Không thêm bảng vào schema. Chương trình B chưa mở thì chưa cần bảng.
- Không đưa tỷ lệ hoa hồng của GoStream/StreamAgain — không kiểm chứng được (§1.1).

## 6. Nếu muốn thi công, thứ tự đúng

1. Chốt 5 tham số của Chương trình A (ngưỡng `120` phút, trần `20`/tháng, hạn link `90` ngày) — **sửa `FR-POP-01`**, không cần bảng mới.
2. Đo: có bao nhiêu referral thật trong 30 ngày đầu? Nếu `< 50` thì **dừng** — chương trình B không đáng mở.
3. Chỉ khi (2) đạt: thêm `creator_codes`, phễu duyệt, và trang `/creators` gated sau login.
4. Viết điều khoản chống gian lận **trước** khi mở, không phải sau.

> **Nguyên tắc:** affiliate là kênh **khuếch đại**, không phải kênh **tạo cầu**. Nếu cổng chưa có người chơi thật quay lại, trả tiền cho người mang traffic sẽ chỉ mua được traffic rác — và trả tiền cho traffic rác là cách nhanh nhất để hỏng số liệu Ads.
