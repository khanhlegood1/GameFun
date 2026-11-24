# ADR-0017 · Nâng Anchor 0.30.1 → 0.32.x và cập nhật toolchain

| | |
|---|---|
| **Trạng thái** | **Proposed — cần quyết trước S6** |
| **Ngày** | 2026-11-18 |
| **Người đề xuất** | AI (Claude) — soát phiên bản toolchain |
| **Người quyết** | Tech Lead On-chain *(chờ ký)* |
| **Ảnh hưởng** | Toàn bộ 4 Solana program, CI, audit |
| **Liên quan** | [ADR-0002](ADR-0002-four-programs.md), [ADR-0007](ADR-0007-program-upgrade-policy.md) |

---

## Bối cảnh

Toàn bộ tài liệu on-chain đang pin **Anchor 0.30.1 + Rust 1.79**:

- [`README.md`](../../README.md) dòng 66
- [`docs/05-contracts/overview.md`](../05-contracts/overview.md) dòng 8
- [`programs/README.md`](../../programs/README.md)
- [`docs/00-framework/ai-agile-adoption.md`](../00-framework/ai-agile-adoption.md) dòng 45

Kiểm tra ngày 2026-11-18:

| | Phiên bản đang pin | Thực tế | Tuổi |
|---|---|---|---|
| Anchor | 0.30.1 | npm `latest` = **0.32.1**; GitHub release 0.32.3 | 0.30.1 phát hành **2024-06-20** ⇒ **~29 tháng** |
| Rust | 1.79 | 1.79 phát hành 2024-06 ⇒ **~29 tháng** | |

Xác minh: `registry.npmjs.org/@coral-xyz/anchor` trả `dist-tags.latest = 0.32.1`;
GitHub API `releases` của `otter-sec/anchor` (tên mới của `coral-xyz/anchor`) liệt kê
`v0.32.3`, `v0.31.3`, `v0.30.4` đều phát hành 2026-11-03.

## Vấn đề

Pin một toolchain **29 tháng tuổi** trong một dự án **chưa viết dòng code on-chain nào** là quyết định khó hiểu.
Nó không mang lại "ổn định" mà mang lại:

1. **Mất security patch.** Patch `v0.30.4` phát hành 2026-11-03 — tức là có bản vá cho nhánh 0.30 mà ta
   đang không dùng. Không rõ đó là bug gì, nhưng **bỏ qua patch là quyết định, không phải mặc định**.
2. **Lệch ecosystem.** Client TypeScript `@coral-xyz/anchor` mới nhất là 0.32.1. Nếu on-chain program build
   bằng 0.30.1 và client dùng 0.32.x, IDL format có thể lệch (Anchor đã đổi IDL spec ở 0.31).
3. **Khó tuyển.** Rust dev Solana mới học sẽ dùng bản hiện tại; bắt họ dùng toolchain 2 năm cũ là ma sát.
4. **Audit khó hơn.** Auditor sẽ hỏi "vì sao pin bản cũ" — cần trả lời được, hoặc đổi.

## Quyết định

**Nâng lên Anchor 0.32.x + Rust stable hiện hành** trước khi bắt đầu S6.

| Thành phần | Từ | Sang | Ghi chú |
|---|---|---|---|
| `anchor-lang` / `anchor-cli` | 0.30.1 | **0.32.x** | Lấy bản patch mới nhất của nhánh 0.32 |
| Rust | 1.79 | **stable hiện hành tại S6** | Đọc yêu cầu MSRV của Anchor trước khi chốt |
| `@coral-xyz/anchor` (client) | — | **khớp on-chain** | Cùng minor version |
| Trident | — | bản mới nhất | Kiểm tra tương thích Anchor 0.32 |

**Nguyên tắc:** on-chain program và client **phải cùng minor version**. Ghi vào CI: đọc
`Cargo.toml` của program, so với `package.json` của client, fail nếu lệch minor.

## Vì sao không nhảy thẳng lên Anchor 2.x

GitHub tags của `otter-sec/anchor` có `v2.0.0-rc.4`, `v2.0.0-rc.3`… nhưng **đều là release candidate**,
không có bản `2.0.0` stable. Dùng RC cho code giữ tiền là không chấp nhận được.

⇒ Ghim ở **0.32.x stable**, và có ADR riêng khi 2.0 ra bản stable.

## Hệ quả

**(+) Được:**
- Có security patch.
- Client/on-chain cùng version.
- Tài liệu Anchor chính thức khớp với code.
- Dễ tuyển hơn, audit dễ giải thích hơn.

**(−) Phải chấp nhận:**
- Phải đọc changelog 0.30 → 0.32 để biết breaking change (đặc biệt: IDL format ở 0.31, `#[interface]`,
  một số constraint đổi tên). **Đây là việc thật, ước tính 2–3 ngày**, làm ở S6 tuần 1.
- Nếu docs mẫu trên mạng dùng 0.30 API, phải dịch sang 0.32.

**Nếu quyết định GIỮ 0.30.1:** phải ghi lý do cụ thể vào ADR này, và **ít nhất** nâng lên **0.30.4**
(bản patch cuối của nhánh) để có security fix. Pin 0.30.1 nguyên bản là không biện minh được.

## Việc phải làm nếu approve

| # | Việc | Nơi sửa |
|---|---|---|
| 1 | Đổi `Anchor 0.30.1` → `0.32.x` | README, overview.md, programs/README.md, ai-agile-adoption.md |
| 2 | Đổi `Rust 1.79` → stable tại S6 | overview.md |
| 3 | Thêm CI check: Anchor version on-chain == client | `.github/workflows/contracts.yml` |
| 4 | Đọc changelog, ghi lại breaking change ảnh hưởng tới 4 program | issue riêng ở S6 |
| 5 | Ghi phiên bản vào `Anchor.toml` + `rust-toolchain.toml` (pin chính xác, không "latest") | S6 |

---

*Phát hiện này không chặn P01–P05. Nhưng phải quyết **trước** khi viết dòng code on-chain đầu tiên (S6 tuần 1).*
