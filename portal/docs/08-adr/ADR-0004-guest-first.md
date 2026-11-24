# ADR-0004 · Guest-first: chơi được không cần ví, nâng cấp không mất tiến trình

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-11 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

Yêu cầu persona Trang (không biết crypto) đối lập với yêu cầu chống bot (cần định danh).

**Quyết định:** cho phép chơi hoàn toàn không cần ví. Ví chỉ cần khi: nhận thưởng, mua bond, giữ tiến trình trên nhiều thiết bị.

**Lý do:**
- Cửa vào là yếu tố quyết định tăng trưởng (bài học Notcoin: 35M người dùng nhờ zero-friction).
- Ép ví ở bước đầu làm mất 60–80% người chơi casual.
- Bot không thể lợi dụng guest vì guest **không** nhận được token và **không** mua được bond (cần play proof gắn ví).

**Hệ quả:**
- (+) Conversion cao; portal giống sản phẩm tiêu dùng.
- (−) Phải xử lý merge tiến trình guest → ví (đã có trong AUTH flow).
- (−) Telemetry của guest không có identity ⇒ risk engine phải chấm theo device + session, không chỉ wallet.


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
