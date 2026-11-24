# ADR-0007 · Program upgrade policy: multisig 4/7 + timelock 48h, immutable sau 90 ngày

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-13 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

Upgrade authority là rủi ro tập trung lớn nhất trong hệ Solana.

**Quyết định:**
- Authority = Squads v4 multisig **4/7** (không phải single key, không phải 2/3).
- Mọi upgrade có **timelock 48h** công khai trên chain (ai cũng thấy proposal trước khi thực thi).
- Sau **90 ngày** kể từ GA, `game9k_curve` chuyển sang **immutable** (không còn upgrade authority).
- `escrow`/`rewards` được phép upgrade lâu hơn nhưng vẫn qua cùng quy trình.
- Không upgrade khi có launch đang trong refund window.

**Lý do:** người mua bond cần biết rằng luật chơi không thể bị thay đổi sau khi họ đã mua. Immutable là cam kết mạnh nhất có thể đưa ra.

**Hệ quả:**
- (+) Niềm tin cao; giảm rủi ro rug by upgrade.
- (−) Nếu phát hiện bug sau 90 ngày ⇒ **không sửa được**. Đối phó: audit 2 vòng + bug bounty + 90 ngày quan sát trước khi immutable + emergency exit (tạm dừng mua mới bằng feature flag off-chain, không cần upgrade).
- (−) 4/7 chậm hơn 1 người ⇒ không thể phản ứng trong vài phút. Chấp nhận: không có kịch bản nào cần upgrade trong < 48h mà không thể xử lý off-chain.


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
