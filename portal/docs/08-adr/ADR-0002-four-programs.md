# ADR-0002 · Bốn program Solana tách theo vòng đời tiền, không phải một program lớn

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-11 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

Cần quyết định: 1 program duy nhất (đơn giản) hay nhiều program (linh hoạt)?

**Quyết định:** 4 program — `game9k_registry`, `game9k_curve`, `game9k_escrow`, `game9k_rewards`.

**Lý do:**
- `curve` chứa logic kinh tế bất biến; muốn "đóng băng" nó (immutable) sau 90 ngày mà vẫn tiến hoá được các phần khác.
- `escrow` và `rewards` cần thêm loại milestone/claim mechanism trong tương lai; nếu gộp vào `curve`, mỗi lần thêm phải upgrade program giữ tiền của curve.
- Bề mặt rủi ro khác nhau ⇒ audit có thể tập trung (audit `curve` kỹ hơn `registry`).
- Giới hạn 10KB account & compute budget: tách giúp mỗi program nhỏ, dễ test.

**Hệ quả:**
- (+) Có thể immutable `curve`, vẫn upgrade `escrow`.
- (+) Audit rẻ hơn (audit 1 program nhỏ kỹ hơn audit 1 program khổng lồ).
- (−) Cần CPI giữa program ⇒ thêm CU + thêm test.
- (−) Nhiều program ID ⇒ nhiều authority ⇒ phải quản lý multisig cho cả 4.

**Đã cân nhắc:** 1 program (loại: không thể immutable từng phần), 10 program theo instruction (loại: quá nhiều CPI, over-engineering).


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
