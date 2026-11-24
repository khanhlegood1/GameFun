# ADR-0010 · Indexer viết bằng Rust (Yellowstone gRPC), không dùng Python/Node

| | |
|---|---|
| **Trạng thái** | Accepted |
| **Ngày** | 2026-11-14 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

**Quyết định:** indexer là Rust binary, đọc Yellowstone geyser qua gRPC.

**Lý do:**
- Cần xử lý 1k+ tx/s, parse account, decode instruction; Python GIL và Node event loop không phù hợp ở tải cao.
- Rust có `solana-sdk` chính thức, type-safe account decode ⇒ ít bug decode hơn.
- Memory thấp ⇒ chạy 2 node nhỏ.

**Hệ quả:**
- (+) Throughput + độ tin cậy decode.
- (−) Khó tuyển người hơn, build chậm hơn. Đối phó: code đơn giản (chỉ decode 4 program), test bằng fixture từ mainnet.
- (−) Team Rust nhỏ ⇒ indexer phải có runbook chi tiết (đã có).


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
