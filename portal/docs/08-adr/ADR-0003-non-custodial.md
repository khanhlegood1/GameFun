# ADR-0003 · Non-custodial: server không bao giờ giữ khoá, người dùng ký mọi giao dịch

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-11 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

Có nên dùng "session key" cho phép server ký thay để UX tốt hơn?

**Quyết định:** **Không**. Server không giữ private key, không ký giao dịch di chuyển tiền. Session key chỉ dùng để ký **telemetry** (không di chuyển tiền), TTL ≤ 2h.

**Lý do:**
- Custody ⇒ nghĩa vụ pháp lý hoàn toàn khác (money transmitter), yêu cầu giấy phép.
- Một vụ lộ key server = mất toàn bộ tiền người dùng; rủi ro không chấp nhận được với team nhỏ.
- Solana có ví phổ biến (Phantom, Backpack, embedded wallet) ⇒ UX đủ tốt.

**Hệ quả:**
- (+) Rủi ro bảo mật giảm mạnh; lập trường pháp lý rõ ràng.
- (−) Người dùng phải ký mỗi giao dịch ⇒ thêm 1 bước. Đối phó: chỉ yêu cầu ký khi thực sự cần (mua, bán, claim), không ký khi chơi.
- (−) Embedded wallet phức tạp hơn (social recovery, export). Chấp nhận.

Xem [PRD REQ-M9-001/005](../01-requirements/PRD-game9k.md#m9--wallet--payout).


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
