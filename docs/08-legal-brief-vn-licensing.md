# Game9K — Bản tóm tắt 1 trang cho tư vấn pháp lý

**Ngày soạn:** 22/11/2026 · **Người soạn:** đội dự án Game9K · **Mục đích:** xin ý kiến tư vấn, **không** phải yêu cầu soạn hồ sơ

| Thông tin tài liệu | Chi tiết |
|---|---|
| **Dự án** | Game9K — cổng game HTML5 instant-play, kết hợp cơ chế gọi vốn cho studio game bằng token trên Solana |
| **Tên miền** | `game9k.com` · **Mã nguồn:** `github.com/khanhlegood1/GameFun` (repo công khai, đầy đủ đặc tả) |
| **Giai đoạn** | Pre-Seed, chưa có sản phẩm vận hành, chưa có người dùng thật. Toàn bộ số liệu trong tài liệu là **dự phóng** |
| **Trụ sở dự kiến** | `9K Holdings, Inc.` (Delaware, Hoa Kỳ) — **chưa thành lập** |
| **Hoạt động tại VN** | Đội ngũ sáng lập tại TP.HCM. **Chưa có pháp nhân Việt Nam nào** |

---

## 1. Mô hình hoạt động (chỉ 4 ý)

1. **Cổng game:** người chơi vào `game9k.com` chơi game HTML5 ngay trên trình duyệt, không cần cài đặt, **không cần ví**. Game do **studio bên thứ ba** phát triển và tải lên — chúng tôi **không sản xuất game**.
2. **Kiểm định:** mỗi bản game được kiểm tra tự động (mã băm bất biến, quét mã độc) và đo lường bằng dữ liệu người chơi thật trước khi được đẩy lên trang chủ.
3. **Gọi vốn:** studio có thể mở một **token riêng** cho game của mình; token chỉ mở bán theo từng chặng, và mỗi chặng chỉ mở khi phiên bản game mới đã vượt qua kiểm định.
4. **Doanh thu:** (a) **phí giao dịch on-chain bằng SOL**; (b) **chia sẻ doanh thu quảng cáo bằng USD** từ lưu lượng cổng.

**Hạ tầng kỹ thuật (quan trọng cho câu hỏi dữ liệu):** Cloudflare Edge + R2 (CDN/lưu trữ) · Supabase (PostgreSQL) · Solana. **Không có máy chủ đặt tại Việt Nam.**

---

## 2. Bốn câu hỏi

### Câu 1 — Phân loại dịch vụ (NĐ 147/2024/NĐ-CP)

Chúng tôi chỉ làm **cổng tổng hợp**, không sản xuất, không sở hữu game. Nhưng cổng có tài khoản người chơi, lưu tiến trình chơi (cloud save), bảng xếp hạng và đo lường hành vi chơi.

> **Hỏi:** Cổng dạng này thuộc **"cung cấp dịch vụ trò chơi điện tử trên mạng"** theo Điều 3 khoản 34, hay chỉ là **"phân phối"**? Nếu thuộc nhóm **G2/G3/G4**, xin xác nhận: **Giấy chứng nhận** cấp cho cổng, còn **Giấy xác nhận thông báo phát hành** là do **studio** (chủ game) hay do **chúng tôi** đứng tên nộp?

### Câu 2 — Game không gọi máy chủ của chúng tôi

Một phần game trên cổng chạy **hoàn toàn phía trình duyệt**: không gọi API của chúng tôi, không lưu dữ liệu, không tương tác giữa người chơi.

> **Hỏi:** Những game này có thể xếp **G4** và **miễn** Giấy xác nhận thông báo phát hành không? Nếu vẫn phải có giấy, xin cho biết **căn cứ điều khoản** — vì chúng tôi đọc Điều 37 và chưa thấy tiêu chí loại trừ rõ ràng.

### Câu 3 — Trách nhiệm khi studio đứng tên hồ sơ

Nếu studio tự nộp hồ sơ phát hành cho game của họ, còn chúng tôi chỉ hiển thị game trên cổng:

> **Hỏi:** (a) Chúng tôi có bị coi là **"doanh nghiệp phát hành"** không? (b) Nếu phải chịu trách nhiệm, trách nhiệm đó dừng ở đâu — kiểm duyệt nội dung, hay cả nội dung game? (c) Cơ chế thực tế để **gỡ một game mất giấy phép** khỏi cổng mà không vi phạm hợp đồng với studio là gì?

### Câu 4 — Cấu trúc sở hữu và dữ liệu người chơi

**Phần này quan trọng nhất với chúng tôi.** Dự kiến:

```
9K Holdings, Inc. (Delaware, Mỹ)  ── sở hữu IP cổng game, cấp phép lại
        │
        └── hợp đồng dịch vụ / BCC với đối tác Việt Nam đã có giấy phép
            (chúng tôi KHÔNG thành lập công ty VN, KHÔNG góp vốn vào ngành game tại VN)
```

> **Hỏi:**
> **(a)** Cấu trúc "pháp nhân Mỹ giữ IP + đối tác Việt Nam đã có giấy phép đứng tên cung cấp dịch vụ" có bị coi là **đầu tư nước ngoài vào ngành game** (kéo theo trần 49% theo cam kết WTO CPC 964\*\*) không, hay được coi là **thương mại dịch vụ xuyên biên giới**?
> **(b)** **Dữ liệu người chơi** (tên, ngày sinh, **số điện thoại Việt Nam** để xác thực theo NĐ 174/2026) đang nằm trên Supabase/Cloudflare ngoài Việt Nam. Theo **Luật BVDLCN 91/2025/QH15 + NĐ 356/2025/NĐ-CP** (hiệu lực 01/01/2026), đây có phải là **chuyển dữ liệu cá nhân xuyên biên giới** phải lập hồ sơ đánh giá tác động? **Ai** là bên kiểm soát dữ liệu — chúng tôi hay đối tác VN?
> **(c)** Có yêu cầu **lưu trữ dữ liệu tại Việt Nam** cho dữ liệu người chơi game không?

---

## 3. Phương án dự phòng nếu câu 1–3 kết luận là "phải có giấy phép"

Chúng tôi **chưa** loại trừ phương án **không phục vụ người chơi tại Việt Nam** ở giai đoạn Pre-Seed (chặn theo địa lý), và chỉ mở thị trường VN sau khi có đối tác đã được cấp phép.

> **Hỏi:** Nếu chặn người chơi VN, chúng tôi cần làm gì để việc chặn được coi là **đầy đủ** — chỉ cần chặn IP, hay phải có thêm điều khoản hợp đồng với studio, và có nghĩa vụ nào khác (ví dụ: không niêm yết giá VND, không quảng cáo tại VN)?

---

## 4. Điều chúng tôi **không** hỏi trong bản này

Để giữ phạm vi hẹp, bản tóm tắt này **không** đề cập: cấu trúc thuế, xử lý token theo pháp luật chứng khoán VN, hay việc thành lập pháp nhân. Những nội dung đó chúng tôi sẽ hỏi riêng khi đã có kết luận cho câu 1–4.

---

## 5. Tài liệu tham chiếu (nếu cần đọc sâu)

| Nội dung | Đường dẫn |
|---|---|
| Mô hình kinh tế đầy đủ | `docs/WHITEPAPER.md` §6.1b, §9 |
| Đặc tả kỹ thuật & luồng người dùng | `docs/PRD.md`, `docs/01-user-flows-and-ux.md` |
| Kiến trúc hạ tầng (nơi dữ liệu được lưu) | `docs/05-c4-architecture-and-nfr.md` |
| Bản in cho nhà đầu tư | `docs/Game9K-Whitepaper-v1.5.pdf` |

> **Lưu ý:** repo công khai, nhưng **không** chứa dữ liệu cá nhân, khóa API hay thông tin pháp nhân nào. Mọi số liệu tài chính trong đó là dự phóng và không liên quan đến câu hỏi pháp lý ở đây.
