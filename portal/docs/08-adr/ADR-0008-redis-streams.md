# ADR-0008 · Redis Streams thay Kafka cho event bus (giai đoạn 1)

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-13 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

**Quyết định:** dùng **Valkey Streams** cho telemetry & internal event, không dùng Kafka.

> **Cập nhật 2026-11-18:** đổi từ Redis sang **Valkey** (BSD-3-Clause) vì Redis 8+ chuyển sang
> RSALv2/SSPLv1/AGPLv3. API và hành vi Streams giống hệt, chỉ đổi image. Xem
> [ADR-0016](ADR-0016-license-compliance.md). ADR này vẫn giữ nguyên phần so sánh với Kafka.

**Lý do:**
- Tải dự kiến: 140 msg/s trung bình, 800/s peak. Kafka overkill.
- Valkey đã có mặt cho cache ⇒ không thêm hạ tầng, không thêm vận hành.
- Consumer group + ack + replay đủ cho nhu cầu (replay giới hạn 24h).
- Chi phí: ~$120/tháng (Valkey) vs ~$700/tháng cho MSK tối thiểu.

**Ngưỡng chuyển:** nếu > 5,000 msg/s kéo dài > 1 tuần hoặc cần replay > 7 ngày hoặc cần nhiều consumer độc lập > 5 ⇒ chuyển Kafka.

**Hệ quả:**
- (+) Đơn giản, rẻ, đủ dùng.
- (−) Mất event nếu Valkey mất dữ liệu (không persistence mạnh). Đối phó: AOF everysec + raw event cũng ghi vào ClickHouse trực tiếp (double write cho telemetry).
- (−) Replay dài hạn không có ⇒ nếu risk engine cần tính lại 90 ngày, phải đọc lại từ ClickHouse (đã có).


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
