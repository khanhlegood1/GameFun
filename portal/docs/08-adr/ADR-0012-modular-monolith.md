# ADR-0012 · Modular monolith (NestJS) trước, tách service chỉ khi có lý do đo được

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-14 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

**Quyết định:** API là 1 NestJS app với module rõ ràng; chỉ tách riêng ingest (đã tách) và risk worker (đã tách). Payout worker là module trong app, không phải service.

**Lý do:**
- Số domain chưa đủ lớn để microservice; chi phí vận hành (network, tracing, deploy) lớn hơn lợi ích.
- Modular monolith cho phép refactor nhanh ở giai đoạn P03–P04 khi boundary còn thay đổi.
- Ingest tách vì lý do tải (90% traffic) và bảo mật (untrusted input).
- Risk worker tách vì ngôn ngữ (Python) và tài nguyên (bộ nhớ cho graph).

**Ngưỡng tách service:** khi một module cần scale độc lập > 3× phần còn lại, hoặc team > 12 người với ownership rõ ràng.

**Hệ quả:**
- (+) Deploy đơn giản, debug dễ, chi phí thấp.
- (−) Một bug có thể làm sập toàn app ⇒ đối phó: circuit breaker nội bộ + tách ingest.


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
