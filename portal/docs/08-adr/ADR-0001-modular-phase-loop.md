# ADR-0001 · Modular phase loop: P01–P03 lặp lại theo module, không chạy một lần cho toàn sản phẩm

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-10 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

Trong AI-Agile Framework, P01→P06 được mô tả như một pipeline tuyến tính cho một sản phẩm. Game9K có 11 module với mức phức tạp rất khác nhau (từ i18n tới bonding curve), và tham số kinh tế on-chain là **yêu cầu sản phẩm**, không phải chi tiết kỹ thuật.

**Quyết định:** chạy P01/P02/P03 một lần cho *platform core* (identity, discovery, play runtime, rating), và **lặp lại** cho từng module nặng (launchpad, rewards, payouts). Mỗi vòng lặp có gate riêng và artifact riêng.

**Lý do:**
- Chạy P01 cho toàn sản phẩm một lần sẽ tạo PRD 200 trang mà không ai đọc hết; review chất lượng thấp.
- On-chain code không thể sửa sau deploy ⇒ cần gate P03 *rất cụ thể* cho launchpad, không thể gộp.
- Frontend-first có nghĩa là mỗi module phải có màn hình được duyệt trước khi viết API cho module đó.

**Hệ quả:**
- (+) Gate sớm hơn, feedback sớm hơn, rủi ro on-chain được kiểm soát riêng.
- (−) Nhiều PR gate hơn ⇒ cần kỷ luật. Đối phó: template gate + CI check.
- (−) Có thể lệch phiên bản giữa các module ⇒ đối phó: dùng chung `openapi.yaml` và `schema.sql` làm nguồn sự thật duy nhất.

**Đã cân nhắc:**
1. Pipeline tuyến tính 1 lần — loại vì rủi ro on-chain quá lớn để gộp.
2. Waterfall cho on-chain + Agile cho off-chain — loại vì tạo 2 văn hoá, 2 lịch.
3. **Được chọn:** modular loop.

## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
