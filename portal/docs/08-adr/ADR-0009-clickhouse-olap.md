# ADR-0009 · ClickHouse cho raw event; Postgres là nguồn sự thật cho tiền

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-13 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

**Quyết định:** raw telemetry & product event ở ClickHouse; entity + tiền + audit ở Postgres.

**Lý do:**
- Funnel/cohort/retention query trên Postgres sẽ chậm và ảnh hưởng OLTP.
- ClickHouse nén tốt (10–20×), query aggregate nhanh, chi phí lưu thấp.
- Nhưng ClickHouse không có transaction ⇒ **không bao giờ** là nguồn sự thật cho số dư.

**Ranh giới cứng:**
- Mọi con số hiển thị cho người dùng về tiền ⇒ từ Postgres (đã đối soát với chain).
- Mọi phân tích hành vi ⇒ từ ClickHouse.
- Nếu hai bên lệch về VPH ⇒ Postgres `version_daily_stats` là bản dùng cho payout (vì đã qua kiểm tra), ClickHouse chỉ để phân tích.

**Hệ quả:**
- (+) Hiệu năng & chi phí tốt.
- (−) Hai nguồn số liệu ⇒ phải có job đối soát hàng ngày (đã có trong test strategy §3.6).


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
