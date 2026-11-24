# ADR-0014 · Chaos testing thủ công trước GA, tự động hoá sau GA

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-14 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

**Quyết định:** trước GA, chạy chaos drill **thủ công** 2 lần (S10, S11). Tự động hoá sau GA.

**Lý do:**
- Chaos tự động cần đầu tư (Litmus/Chaos Mesh + kịch bản + phân tích) ~1 sprint.
- Team SRE 1 người; ưu tiên P05 gaps khác (alert, backup, pen-test) trước.
- 2 lần drill thủ công đủ để phát hiện lỗ hổng lớn.

**Kịch bản drill bắt buộc:**
1. Kill 2/3 API pod.
2. RPC primary down.
3. Redis restart (mất stream state).
4. DB failover.
5. ClickHouse down (API vẫn đọc được từ PG).

**Hệ quả:**
- (−) Không có regression test cho resilience ⇒ đối phó: ghi lại kết quả drill, so sánh lần sau.


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
