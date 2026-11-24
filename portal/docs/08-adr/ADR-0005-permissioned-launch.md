# ADR-0005 · Permissioned launch giai đoạn 1: chỉ studio tier Silver+ được mở bond

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-12 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

Pump.fun cho mọi người launch ngay ⇒ 98% token chết và rất nhiều nội dung rác. Có nên mở ngay?

**Quyết định:** giai đoạn 1 (GA Phase 1) chỉ studio Silver+ được launch bond. Mở dần ở Phase 2.

**Điều kiện Silver:** ≥ 1 game live ≥ 30 ngày, ≥ 5,000 VPH trong 30 ngày, ≥ 200 rating có trọng số, KYC verified, 0 vi phạm.

**Lý do:**
- Bảo vệ người mua: bond gắn với studio có track record.
- Bảo vệ thương hiệu: một launch rác lớn làm mất niềm tin toàn nền tảng.
- Tạo động lực: studio muốn launch phải chứng minh chất lượng trước (growth theo version — đúng mục tiêu).

**Hệ quả:**
- (+) Chất lượng cao hơn, ít rug hơn, dễ vận hành ở giai đoạn đầu.
- (−) Tăng trưởng chậm hơn; một số studio tốt nhưng mới sẽ bị chặn. Đối phó: đường lên Silver rõ ràng + thời gian chờ ngắn (30 ngày).
- (−) Rủi ro "curation bias" ⇒ công bố tiêu chí công khai.


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
