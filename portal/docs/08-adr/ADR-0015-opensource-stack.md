# ADR-0015 · Chọn open-source stack: tự viết core, không fork portal

| | |
|---|---|
| **Trạng thái** | Accepted (chờ ký) |
| **Ngày** | 2026-11-18 |
| **Người đề xuất** | AI (Claude) — nghiên cứu open-source theo yêu cầu |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn bộ delivery, pháp lý license, ngân sách |
| **Supersedes** | không |
| **Liên quan** | [ADR-0012](ADR-0012-modular-monolith.md), [ADR-0008](ADR-0008-redis-streams.md), [ADR-0009](ADR-0009-clickhouse-olap.md), [ADR-0016](ADR-0016-license-compliance.md) |

---

## Bối cảnh

Yêu cầu: *"Tìm open source để làm"* — tức là trả lời câu hỏi **có nên fork một game portal mã nguồn mở thay vì tự xây?**

Đã kiểm tra **16 repository** qua GitHub API ngày 2026-11-18 (số liệu thật, không phải ước lượng).
Kết quả đầy đủ ở [`docs/10-opensource/README.md`](../10-opensource/README.md).

Ba phát hiện quyết định câu trả lời:

1. **Không có repo nào làm được "đánh giá theo version"**. Đây chính là lợi thế cạnh tranh của Game9K.
   Repo gần nhất (`afonsoft/gamehub`) có rating theo *game*, không theo *version* — và chỉ có **1 star**.
2. **License của các repo "gần nhất" đều rủi ro**: `afonsoft/gamehub` **tự mâu thuẫn** (README ghi GPL-3.0,
   file LICENSE ghi MIT, GitHub API nhận MIT). `CloudArcade` là GPL-3.0. Fork GPL vào sản phẩm thương mại
   đóng nghĩa là phải mở toàn bộ source.
3. **Stack hạ tầng đang đề xuất trong NFR có 3 license cần soát lại**: Redis ≥ 8 (RSALv2/SSPLv1/AGPLv3),
   MinIO (AGPL-3.0), Grafana (AGPL-3.0). Xem [ADR-0016](ADR-0016-license-compliance.md).

## Quyết định

**Không fork portal open-source nào.** Dùng open-source ở **tầng hạ tầng và thư viện**, tự viết ở **tầng sản phẩm**.

| Tầng | Quyết định | Repo / thư viện |
|---|---|---|
| Framework web | Dùng | Next.js (MIT), NestJS (MIT), Prisma (Apache-2.0) |
| Auth ví | Dùng | `phantom/sign-in-with-solana` (MIT), `anza-xyz/wallet-adapter` (Apache-2.0) |
| Anti-bot CAPTCHA | Dùng | `altcha-org/altcha` (MIT) |
| SDK tham khảo | **Đọc, không import** | `Playgama/bridge` (LGPL-3.0) — chỉ đọc API surface |
| Analytics tham khảo | **Đọc, không import** | `devoidinity/GamePulse` (MIT, nhưng 7 star, stale 5 tháng) |
| On-chain framework | Dùng | Anchor (Apache-2.0) — **không phải 0.30.1, xem ADR-0017** |
| Multisig | Dùng binary/SDK | Squads v4 (AGPL-3.0 **program**, MIT client) |
| **Version registry** | **Tự viết** | — |
| **Verified Play Rating** | **Tự viết** | — |
| **Version Launchpad** | **Tự viết** | — |
| **Anti-snipe / anti-bundle** | **Tự viết** | — |

## Lý do

### Vì sao không fork `afonsoft/gamehub`

Đây là repo sát nhất về chức năng (portal + iframe player + build management + moderation).
Nhưng:

| Vấn đề | Bằng chứng (2026-11-18) |
|---|---|
| **License mâu thuẫn** | README badge `GPL-3.0`, file `LICENSE` = MIT, GitHub API = MIT. Không thể xác định | 
| **Không có cộng đồng** | **1 star**, 0 fork, 0 subscriber, 13 open issue |
| **Không ai dùng** | Không có deployment công khai, không case study |
| **Stack không khớp** | .NET 10 (C#) + Angular 20 — trong khi đội và toàn bộ P03 đã chốt TypeScript |
| **Không có gì ta cần nhất** | Không rating theo version, không launchpad, không proof-of-play |

Fork repo này nghĩa là **nhận 1.9M dòng C# + 2.9M dòng TypeScript của người khác**, trong đó phần ta cần
(~5% code) vẫn phải viết lại. Tỷ lệ học/hại quá xấu, cộng thêm rủi ro pháp lý license.

### Vì sao không dùng `CloudArcade`

GPL-3.0, CMS cho HTML5 game, 21 star. GPL-3.0 **lây nhiễm**: nếu ta phân phối sản phẩm dẫn xuất,
phải công bố toàn bộ source dưới GPL. Không phù hợp mô hình kinh doanh đóng.

### Vì sao vẫn dùng open-source ở tầng dưới

Ba lý do cụ thể, không phải "open-source là tốt":

1. **Auth ví là bài toán đã được giải đúng.** `phantom/sign-in-with-solana` (MIT) implement đúng chuẩn
   CAIP-122/SIWS. Tự viết lại = tự tạo lỗ hổng replay nonce (đã là threat T-02 trong
   [threat-model](../06-nfr/threat-model.md)). **Dùng, nhưng vẫn phải review code.**
2. **CAPTCHA PoW không phải lợi thế cạnh tranh.** `altcha` (MIT, 2.9k star, GDPR/WCAG compliant) làm tốt hơn
   bất cứ thứ ta viết trong 2 tuần. Xem [ALTCHA ở đâu trong pipeline](#vị-trí-altcha-trong-kiến-trúc).
3. **Anchor là chuẩn de-facto** cho Solana program. Không dùng Anchor = tự viết serialization + account
   validation, tức là tự tạo lỗ hổng.

## Vị trí ALTCHA trong kiến trúc

ALTCHA **không** thay thế chống sybil. Nó chỉ là **một lớp** ở đúng chỗ:

| Chỗ dùng | Chỗ KHÔNG dùng |
|---|---|
| Đăng ký tài khoản (SCR-11) | Chống bot chơi game (dùng proof-of-play) |
| Gửi review lần đầu (SCR-04) | Chống bot mua token (dùng play-gate on-chain) |
| Tạo launch request (SCR-09) | Chống multi-account (dùng sybil graph) |
| Report nội dung (SCR-32) | Chống MEV (dùng commit-reveal/batch) |

Nói cách khác: ALTCHA chặn **request tự động**, không chặn **người thật có 100 ví**.
Đây chính là lỗi phổ biến khi triển khai CAPTCHA — tưởng đã chống bot, thực ra chỉ chống script.

## Hệ quả

**(+) Được:**
- Không rủi ro license ở tầng sản phẩm.
- Không phải maintain code của người khác (repo 1 star không có ai vá bug).
- Toàn bộ code sản phẩm là TypeScript/Rust — một ngôn ngữ, một toolchain, một CI.
- Thời gian tới MVP **ngắn hơn** so với fork + gỡ: ước tính 12 sprint (đã có trong
  [roadmap](../07-delivery/roadmap.md)) vs 16+ sprint nếu phải hiểu và gỡ 4.8M dòng code lạ.

**(−) Mất / phải chấp nhận:**
- Phải tự viết admin UI (Payload CMS giúp phần này — xem dưới).
- Không có "head start" về UI portal. Nhưng UI portal không phải lợi thế cạnh tranh; nó là commodity.
- Phải tự viết moderation queue. Đã có trong backlog MP-801…MP-803.

## Payload CMS — có dùng không?

**Có, nhưng có điều kiện** — chỉ cho **nội dung biên tập**, không cho dữ liệu tiền tệ.

| Dùng Payload cho | KHÔNG dùng Payload cho |
|---|---|
| Game metadata, category, tag, thumbnail | Số dư, ledger, payout |
| Partner profile, public page | Play session, telemetry |
| Editorial collection ("Game Việt nổi bật") | Launch / curve state |
| Admin UI cho moderator | Bất cứ thứ gì on-chain là nguồn sự thật |

Lý do: Payload là CMS, không phải ledger. Nếu để Payload quản lý số dư, ta mất tính append-only
và tính đối soát — vi phạm [NFR-S-04](../06-nfr/nfr-spec.md) và sự thật là **Postgres schema riêng**
đã được thiết kế cho việc này ([`schema.sql`](../04-data/schema.sql), 45 bảng).

**Quan trọng:** nếu dùng Payload, nó phải dùng **cùng Postgres**, ở **schema riêng** (`cms.*`),
và **không** được JOIN trực tiếp vào `app.*`. Giao tiếp qua API hoặc materialized view.
Lý do: một CMS có quyền ghi vào bảng tiền là một lỗ hổng privilege escalation.

## Điều KHÔNG chọn (và vì sao)

| Phương án | Vì sao không |
|---|---|
| Fork `afonsoft/gamehub` | License mâu thuẫn, 1 star, .NET+Angular không khớp, không có feature ta cần |
| Fork `CloudArcade` | GPL-3.0, CMS đơn giản, không có version registry |
| `devoidinity/GamePulse` làm analytics | MIT nhưng 7 star, commit cuối 5 tháng trước, 10 open issue. **Đọc để tham khảo schema**, không deploy |
| `Playgama/bridge` làm SDK | LGPL-3.0. Import vào bundle = phải cho phép relink. **Chỉ đọc API surface** (tên event, thứ tự lifecycle) |
| `Tickle` | CC BY-NC-SA 4.0 — **cấm dùng thương mại** |
| `Watson Games` | Không có file LICENSE ⇒ mặc định "all rights reserved" |
| Supabase | Dùng được nhưng **không cần**: đã có Postgres + NestJS + Prisma. Thêm = thêm một hệ auth song song |
| PocketBase | Tốt nhưng viết bằng Go ⇒ thêm ngôn ngữ thứ 4 vào hệ thống (TS, Rust, Python, Go) |

## Rủi ro còn lại

| Rủi ro | Mức | Đối phó |
|---|---|---|
| Tự viết nhiều hơn dự kiến | Trung bình | Roadmap đã tính 290 điểm; S12 là buffer |
| Không có ai review code open-source đã dùng | **Cao** | Mỗi thư viện phải có 1 người "owner" đọc code trước khi merge (checklist P04) |
| Payload đổi license | Thấp | MIT, 45k star, có thể thay bằng admin tự viết |
| ALTCHA bị bypass | Trung bình | Nó chỉ là 1 lớp; lớp thật là PoPW + play-gate on-chain |

---

*Quyết định này phải được ký trước sprint S2 (khi bắt đầu chọn thư viện cho registry).*
