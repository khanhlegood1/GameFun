# ADR-0013 · Single-region primary ở giai đoạn 1; chấp nhận RTO 30 phút

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-14 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

**Quyết định:** một region chính (ap-southeast-1), multi-AZ. Không multi-region active-active.

**Lý do:**
- Chi phí multi-region (DB, replication, traffic) ~$3,000+/tháng — chưa xứng với 120k VPH/tuần.
- RTO 30 phút chấp nhận được cho portal game (không phải hệ thống thanh toán realtime).
- On-chain vẫn hoạt động khi off-chain down (người dùng có thể bán qua ví/aggregator).

**Ngưỡng xem lại:** > 200k VPH/tuần hoặc có yêu cầu SLO 99.99% từ đối tác.

**Hệ quả:**
- (+) Tiết kiệm ~40% hạ tầng.
- (−) Mất region = downtime 30 phút. Đối phó: DR runbook đã diễn tập, read-only mode có sẵn.


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
