# ADR-0006 · Token-2022 extensions: TransferHook + PermanentDelegate (chỉ escrow), không NonTransferable

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-12 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

Token-2022 mở ra nhiều extension mạnh nhưng cũng nhiều rủi ro.

**Quyết định:**
- **Dùng** `TransferHook`: chặn chuyển creator allocation trước vest (defense-in-depth, ngoài việc vault giữ token).
- **Dùng** `PermanentDelegate` với delegate = **escrow PDA** (không phải team) — chỉ để burn token khi refund.
- **Dùng** `MetadataPointer` + `TokenMetadata` (tên bond hiển thị trong ví).
- **Không dùng** `NonTransferable` (bond phải bán được), `MintCloseAuthority` (cần mint tồn tại cho vesting), `ConfidentialTransfer` (không cần, phức tạp).

**Lý do:** `PermanentDelegate` là quyền mạnh nhất trong Token-2022; nếu giao cho team hoặc multisig, người mua có lý do để nghi ngờ. Giao cho `escrow` PDA (logic bất biến, chỉ dùng trong `request_refund`) làm cho quyền này **có thể chứng minh bằng code**.

**Hệ quả:**
- (+) Refund không cần approve từ holder (họ vẫn ký để nhận SOL, nhưng token bị burn để không double-refund).
- (−) Phải test rất kỹ escrow program: nếu có bug cho phép burn ngoài refund ⇒ thảm hoạ. Test bắt buộc + audit.
- (−) Một số ví/AMM chưa hỗ trợ Token-2022 đầy đủ ⇒ phải kiểm tra tương thích với CPMM đã chọn (Q-03).


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
