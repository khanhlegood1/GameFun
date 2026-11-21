# Khảo sát & Lựa chọn Open Source cho Game9K (`khanhlegood1/GameFun`)

> **Tài liệu sống (Living Documentation):** `docs/00-open-source-landscape.md`  
> **Dự án:** **Game9K Funding Portal** (`game9k.com`) — Web Game Portal & Version-Gated Solana Launchpad (kế thừa nền tảng `GAME.FUN v2` tại `khanhlegood1/GameFun`)  
> **Cập nhật:** 2026-11-18  
> **Mục tiêu:** Xác định các mã nguồn mở đã được kiểm chứng để **Dùng trực tiếp (Adopt)**, **Mở rộng/CPI (Integrate)** hoặc **Tham khảo kiến trúc (Reference)** cho từng module, tránh viết lại từ đầu và kiểm soát chặt rủi ro bản quyền (License) cũng như bảo mật.

---

## 1. Chiến lược lựa chọn Open Source (Build vs. Adopt vs. Integrate)

Hiện tại trên thị trường **không tồn tại một repo duy nhất** kết hợp cả 4 mảnh ghép (*Poki Game Portal + Arena Version Evaluation + Pump.fun Bonding Curve + Notcoin Anti-Bot Community Loop*). Tuy nhiên, **80% hạ tầng kỹ thuật** của Game9K có thể lắp ghép từ các dự án mã nguồn mở chất lượng cao, còn **20% giá trị cốt lõi (Core IP)** cần tự xây dựng sạch (clean-room) trong monorepo `khanhlegood1/GameFun`:

| Chiến lược | Áp dụng cho thành phần nào | Lý do kiến trúc |
|---|---|---|
| **Adopt (Dùng trực tiếp qua package/infra)** | Next.js, Supabase, Coolify, `pg-boss`, `yauzl`, `openskill.js`, `rrweb`, `altcha`, `lightweight-charts`, Anchor, SPL Token-2022, `@solana/kit`, `litesvm`, `trident` | Thư viện chuẩn công nghiệp, license sạch (MIT/Apache-2.0/ISC), cộng đồng lớn, dễ audit. |
| **Integrate / CPI (Tích hợp giao thức on-chain & game backend)** | `MeteoraAg/damm-v2` hoặc `raydium-io/raydium-cp-swap` (graduation DEX), `Squads-Protocol/v4` (multisig quản trị), `poki/netlib` / `colyseus` / `nakama` (multiplayer tùy chọn cho dev game) | Tận dụng thanh khoản và bảo mật đã audit trên Solana mainnet; không tự viết lại AMM DEX hay Multisig. |
| **Reference (Tham khảo thiết kế, tự viết clean-room)** | `MeteoraAg/dynamic-bonding-curve`, `itchio/wharf` & `itchio/butler`, `poki/poki-cli`, `lm-sys/FastChat` (Chatbot Arena Bradley-Terry), `TaloDev/backend` | Cần tùy biến sâu cơ chế **Version-Gated Bonding Curve (VGBC)**, **Proof-of-Play Priority Window**, **Game9K SDK & Inspector** và tránh rủi ro license không rõ ràng từ các bản fork Pump.fun trôi nổi. |

> **Cảnh báo bảo mật quan trọng về các repo "pumpfun-smart-contract clone" trên GitHub:** Qua rà soát các repo clone Pump.fun phổ biến (như `m8s-lab/pump-fun-smart-contract`, `justFiveDev/Solana-Pumpfun-Smart-Contract`, `mogons/pumpfun-smart-contract-solana`), đa số **không gắn giấy phép (no-license)**, chưa qua kiểm toán bảo mật độc lập, và đôi khi chứa admin backdoor rút reserve. **Quy tắc bắt buộc của Game9K:** Chỉ dùng làm tài liệu đọc hiểu luồng CPI; toàn bộ Anchor program trong `programs/` phải viết mới trên nền `anchor` + `solana-program/token-2022`, kiểm thử bằng `LiteSVM` + fuzzing bằng `Ackee-Blockchain/trident`, và tham khảo chuẩn từ `MeteoraAg/dynamic-bonding-curve` + `raydium-io/raydium-cp-swap`.

---

## 2. Danh mục Open Source đã xác minh theo từng Module

### 2.1. Nhóm 1 — Core Portal, Database, Auth & Self-Hosted PaaS (Sprint 0–1)

| Dự án Open Source | GitHub URL | Ngôn ngữ / License | Vai trò trong Game9K | Mức độ sử dụng |
|---|---|---|---|---|
| **Supabase** | `https://github.com/supabase/supabase` | TypeScript, SQL / `Apache-2.0` | PostgreSQL chính, Auth (Email/OAuth + Sign-In With Solana), Row Level Security (RLS), Realtime cập nhật trạng thái xử lý build & Arena, `pgTAP` test phân quyền. | **Adopt (Core)** |
| **Coolify** | `https://github.com/coollabsio/coolify` | PHP, Docker / `Apache-2.0` | Triển khai container `apps/web`, `apps/worker`, `apps/indexer` cho môi trường staging/production (khớp issue `S0-08`). | **Adopt (Infra)** |
| **shadcn/ui** | `https://github.com/shadcn-ui/ui` | TypeScript / `MIT` | Bộ UI component truy cập tốt (WCAG/keyboard), xây nhanh Game Portal, Developer Studio, Game9K Inspector, Arena Battle UI và bảng giao dịch Launchpad. | **Adopt (UI)** |
| **Cloudflare workerd** | `https://github.com/cloudflare/workerd` | C++, JS / `Apache-2.0` | Runtime cho `workers/game-delivery` phục vụ game HTML5/WebGL cô lập theo từng version (`<version-id>.preview.<game-domain>` và `<version-id>.play.<game-domain>`) gắn trực tiếp R2 binding (khớp `S1-08`). | **Adopt (Edge)** |
| **Zod** | `https://github.com/colinhacks/zod` | TypeScript / `MIT` | Schema validation dùng chung trong `packages/shared` cho env vars, metadata game, validation report JSON, postMessage SDK và API payloads. | **Adopt (Core)** |

---

### 2.2. Nhóm 2 — Game Upload, Secure ZIP Pipeline, CLI & Distribution (Mô hình Poki)

| Dự án Open Source | GitHub URL | Ngôn ngữ / License | Vai trò trong Game9K | Mức độ sử dụng |
|---|---|---|---|---|
| **pg-boss** *(hoặc Graphile Worker)* | `https://github.com/timgit/pg-boss` / `https://github.com/graphile/worker` | TypeScript / `MIT` | Hàng đợi job bền vững trên PostgreSQL sử dụng `FOR UPDATE SKIP LOCKED`, retry/backoff, dead-letter queue, singleton key chống xử lý trùng version (khớp `S1-04`, không cần vận hành Redis riêng ở giai đoạn đầu). | **Adopt (Worker)** |
| **yauzl** | `https://github.com/thejoshwolfe/yauzl` | JavaScript / `MIT` | Đọc ZIP theo cơ chế lazy entry-by-entry (`lazyEntries: true`), cho phép kiểm tra magic bytes, chặn path traversal (`..`, absolute path, drive prefix), chặn symlink, chặn ZIP mã hóa, kiểm soát tỷ lệ nén chống ZIP bomb **trước khi** giải nén từng file (khớp `S1-05`). | **Adopt (Security)** |
| **poki/poki-cli** | `https://github.com/poki/poki-cli` | TypeScript / `ISC` | Tham khảo thiết kế CLI (`packages/game9k-cli`) để studio game upload bản build ZIP + changelog trực tiếp từ CI/CD (GitHub Actions, Godot, Unity WebGL, GDevelop). | **Reference** |
| **itchio/butler** & **itchio/wharf** | `https://github.com/itchio/butler` / `https://github.com/itchio/wharf` | Go / `MIT` | Tham khảo giao thức manifest, chữ ký chunk và diff giữa hai bản build `v(n-1)` → `v(n)` (phục vụ tính toán **Code/Asset Delta Score** chống dev upload lại bản cũ đổi số version để mở khóa token!). | **Reference (Core)** |
| **poki/netlib** | `https://github.com/poki/netlib` | Go / `ISC` | Thư viện WebRTC peer-to-peer networking gọn nhẹ của chính Poki cho web game multiplayer; có thể cung cấp/tích hợp cho developer trên Game9K. | **Integrate (Phase 2)** |
| **TaloDev/backend** | `https://github.com/TaloDev/backend` | TypeScript / `MIT` | Game backend tự host (player stats, leaderboards, save data/cloud storage tương đương Poki AUDS, events). Tham khảo schema cho dịch vụ **Game9K Cloud Save (AUDS)** & Leaderboards. | **Reference** |
| **Heroic Labs Nakama** / **Colyseus** | `https://github.com/heroiclabs/nakama` (`Apache-2.0`) / `https://github.com/colyseus/colyseus` (`MIT`) | Go / TypeScript | Giải pháp multiplayer/matchmaking nâng cao cho các game realtime ở M4/M5+ (lưu ý user đã fork sẵn `nakama` và `GDevelop` trên tài khoản GitHub). | **Optional Add-on** |
| **GDevelop** | `https://github.com/4ian/GDevelop` | JS/TS / `MIT` (Core) | Engine làm HTML5 game phổ biến; viết plugin xuất bản 1-click tích hợp sẵn `@game9k/game-sdk` (tương tự `poki/phaser-plugin` cho Phaser/Godot/Unity). | **Ecosystem Integration** |

---

### 2.3. Nhóm 3 — Playtesting, Inspector & Version Arena (Mô hình Poki Playtest + Arena)

| Dự án Open Source | GitHub URL | Ngôn ngữ / License | Vai trò trong Game9K | Mức độ sử dụng |
|---|---|---|---|---|
| **openskill.js** | `https://github.com/philihp/openskill.js` | TypeScript / `MIT` | Thuật toán xếp hạng Plackett-Luce / Bradley-Terry / Thurstone-Mosteller (thay thế mã mở cho TrueSkill, hỗ trợ độ không chắc chắn `sigma`, `mu` và trọng số người chấm). Dùng tính điểm xếp hạng **giữa các version `v(n)` vs `v(n-1)`** và **giữa các game cùng category** trên Game9K Arena. | **Adopt (Core Arena)** |
| **lm-sys/FastChat** & **Arena-OSS/arena-hard-auto** | `https://github.com/lm-sys/FastChat` / `https://github.com/Arena-OSS/arena-hard-auto` | Python / `Apache-2.0` | Tham khảo phương pháp **Blind A/B Pairwise Battle**, bootstrap confidence interval (95% CI) cho bảng xếp hạng Bradley-Terry, lọc phiếu nhiễu (anomalous voter detection) và cơ chế ghép cặp ưu tiên các cặp có độ bất định cao. | **Reference (Math)** |
| **rrweb** | `https://github.com/rrweb-io/rrweb` | TypeScript / `MIT` | Kết hợp cùng MediaRecorder API (Canvas `captureStream` cho WebGL) + SDK input/console telemetry để xây tính năng **Mystery Tile Playtesting** giống Poki (ghi 10 phiên chơi đầu kèm log phím bấm & lỗi console khi người chơi đồng ý consent). | **Adopt (Playtest)** |
| **PostHog** | `https://github.com/PostHog/posthog` | Python, TS / `MIT` (FOSS parts) | Tham khảo/tích hợp funnel phân tích **CTR → Conversion-to-Play (C2P) → Time-on-Page Histogram (0–1m, 1–2m, 3–5m, 5m+)** cho Poki-style Player Fit Test (500 lượt chơi) & Web Fit Test. | **Optional / Reference** |

---

### 2.4. Nhóm 4 — Anti-Bot, Proof-of-Play & Community Loop (Mô hình Notcoin)

| Dự án Open Source | GitHub URL | Ngôn ngữ / License | Vai trò trong Game9K | Mức độ sử dụng |
|---|---|---|---|---|
| **ALTCHA** | `https://github.com/altcha-org/altcha` | TypeScript / `MIT` | CAPTCHA tự host dựa trên **Proof-of-Work (SHA-256)** không theo dõi người dùng, tuân thủ GDPR/WCAG 2.2 AA, không phụ thuộc bên thứ ba. Chặn bot tạo session hàng loạt, spam vote Arena và farm nhiệm vụ `SPARK`. | **Adopt (Anti-Bot)** |
| **FingerprintJS** | `https://github.com/fingerprintjs/fingerprintjs` | TypeScript / `MIT` (BSL lưu ý bản v4+; dùng bản MIT hoặc tự viết tín hiệu WebGL/Audio/Canvas hợp pháp có consent) | Tham khảo tín hiệu phát hiện đa tài khoản trên cùng thiết bị; kết hợp IP ASN reputation, input timing entropy (Shannon entropy + inter-keystroke variance) và phân tích cụm ví on-chain (funding tree Sybil detection). | **Reference (Lưu ý license)** |

---

### 2.5. Nhóm 5 — Solana Smart Contracts, Launchpad, DEX Graduation & Trading UI (Mô hình Pump.fun nâng cấp)

| Dự án Open Source | GitHub URL | Ngôn ngữ / License | Vai trò trong Game9K | Mức độ sử dụng |
|---|---|---|---|---|
| **Anchor Framework** | `https://github.com/solana-foundation/anchor` | Rust, TS / `Apache-2.0` | Framework phát triển Solana smart contracts chính cho toàn bộ bộ program của Game9K + sinh IDL TypeScript tự động. | **Adopt (Core On-Chain)** |
| **SPL Token-2022** | `https://github.com/solana-program/token-2022` | Rust / `Apache-2.0` | Chuẩn token cho Game Tokens (hỗ trợ Metadata Pointer tích hợp ngay trong Mint account tiết kiệm rent, tương thích Raydium CPMM & Meteora DAMM v2). | **Adopt (Core On-Chain)** |
| **Metaplex Token Metadata** | `https://github.com/metaplex-foundation/mpl-token-metadata` | Rust / `Metaplex License` | Tùy chọn gắn metadata chuẩn hiển thị ngay trên Phantom, Backpack, Solscan, DexScreener, Jupiter. | **Integrate (CPI)** |
| **Meteora Dynamic Bonding Curve (DBC) & SDK** | `https://github.com/MeteoraAg/dynamic-bonding-curve` / `https://github.com/MeteoraAg/dynamic-bonding-curve-sdk` (`MIT`) | Rust, TS | Tham khảo kiến trúc curve động, anti-sniper fee scheduler và cơ chế migrate thanh khoản sang DAMM v2 với LP khóa vĩnh viễn nhưng vẫn thu phí giao dịch chia cho creator/cộng đồng. | **Reference / CPI** |
| **Meteora DAMM v2** & **CPI Examples** | `https://github.com/MeteoraAg/damm-v2` / `https://github.com/MeteoraAg/cpi-examples` | Rust, TS / `MIT` (SDK) | Đích **DEX Graduation số 1** khi game đạt mốc M4 (Global Release) và bán hết 700M token trên curve; hỗ trợ lock LP vĩnh viễn + claim phí LP nuôi Player Pool & Dev. | **Integrate (CPI)** |
| **Raydium CP-Swap (CPMM)** | `https://github.com/raydium-io/raydium-cp-swap` | Rust / `Apache-2.0` | Đích **DEX Graduation thay thế/song song** — AMM constant-product không cần OpenBook market ID (tiết kiệm chi phí khởi tạo pool), hỗ trợ đầy đủ Token-2022, mã nguồn Apache-2.0 sạch. | **Integrate (CPI)** |
| **Squads Protocol v4** | `https://github.com/Squads-Protocol/v4` | Rust, TS / `AGPL-3.0` (gọi on-chain program đã deploy, không nhúng mã nguồn) | Multisig quản trị `upgrade_authority` của các program Game9K, `protocol_treasury`, và quyền cập nhật `GlobalConfig` / danh sách `OracleSigner`. | **Integrate (On-Chain)** |
| **Anza `@solana/kit` & Wallet Adapter** | `https://github.com/anza-xyz/kit` (`MIT`) / `https://github.com/anza-xyz/wallet-adapter` (`Apache-2.0`) | TypeScript | Kết nối ví Phantom, Backpack, Solflare, ký giao dịch, Sign-In With Solana (SIWS), đọc PDA state và subscribe logs trên frontend/indexer. | **Adopt (Core Web3)** |
| **Helius SDK** / **Yellowstone gRPC** | `https://github.com/helius-labs/helius-sdk` (`MIT`) / `https://github.com/rpcpool/yellowstone-grpc` (`AGPL-3.0` client lưu ý) | TypeScript / Rust | Lắng nghe sự kiện giao dịch, cập nhật nến OHLCV, sổ lệnh/trade feed real-time, danh sách top holders và phát hiện cụm ví sniper/dev bán lén. | **Adopt (`helius-sdk`)** |
| **TradingView Lightweight Charts** | `https://github.com/tradingview/lightweight-charts` | TypeScript / `Apache-2.0` | Biểu đồ nến giá/marketcap real-time kiểu Pump.fun, có gắn **Version Milestone Markers (`v0.2 M1`, `v0.5 M2`, `v0.8 M3`, `v1.0 M4`)** trực tiếp trên trục thời gian! | **Adopt (UI)** |
| **LiteSVM** | `https://github.com/LiteSVM/litesvm` | Rust, TS / `Apache-2.0` | Chạy unit/integration test cho Solana programs cực nhanh trong bộ nhớ (time-travel `Clock` test vesting, priority window 24h, early-exit fee decay, ragequit timeout). | **Adopt (Test)** |
| **Ackee Trident** | `https://github.com/Ackee-Blockchain/trident` | Rust / `MIT` | Property-based fuzzing cho Anchor programs — kiểm chứng bất biến `x * y = k`, không tràn số, không rút lố reserve, không bypass version cap. | **Adopt (Security)** |
| **Solana Program Examples** & **0xMacro Awesome Solana Security** | `https://github.com/solana-foundation/program-examples` (`MIT`) / `https://github.com/0xMacro/awesome-solana-security` | Rust | Mẫu chuẩn CPI Token-2022, Ed25519 signature introspection và checklist kiểm toán bảo mật Solana trước mainnet. | **Reference** |

---

### 2.6. Nhóm 6 — AI-Agile Contract-First & Observability Toolchain (P03–P06)

| Dự án Open Source | GitHub URL | Ngôn ngữ / License | Vai trò trong Game9K | Mức độ sử dụng |
|---|---|---|---|---|
| **Hey API (`openapi-ts`)** | `https://github.com/hey-api/hey-api` | TypeScript / `MIT` | Sinh TypeScript client, Zod validators và TanStack Query hooks tự động từ OpenAPI 3.1 (đúng nguyên lý P03 AI-Agile Framework). | **Adopt (DX)** |
| **Stoplight Prism** & **MSW** | `https://github.com/stoplightio/prism` (`Apache-2.0`) / `https://github.com/mswjs/msw` (`MIT`) | TypeScript | Chạy Mock API ngay từ ngày 1 để Frontend và Backend/Smart Contract làm việc song song không chờ nhau (P03). | **Adopt (DX)** |
| **OpenTelemetry JS** | `https://github.com/open-telemetry/opentelemetry-js` | TypeScript / `Apache-2.0` | Distributed tracing xuyên suốt `web` → `worker` → `indexer` với `correlation_id` thống nhất (P06). | **Adopt (Ops)** |

---

## 3. Kiểm soát tương thích Giấy phép (License Compliance Matrix)

Vì `khanhlegood1/GameFun` là sản phẩm thương mại (private repo), mọi phụ thuộc nhúng trực tiếp vào mã nguồn phải tránh copyleft lây nhiễm:

| Nhóm License | Các thư viện tiêu biểu | Chính sách trong Game9K |
|---|---|---|
| **An toàn tuyệt đối (`MIT`, `Apache-2.0`, `ISC`, `BSD`)** | Next.js, Supabase, Anchor, Token-2022, Raydium CPMM, Meteora DBC/DAMM v2 SDK, `pg-boss`, `yauzl`, `openskill.js`, `rrweb`, `altcha`, `lightweight-charts`, `litesvm`, `trident`, `poki/netlib` | Được phép cài đặt trực tiếp vào `apps/*`, `packages/*`, `workers/*`, `programs/*`. |
| **Hạn chế / Copyleft (`GPL-3.0`, `AGPL-3.0`, `BSL`)** | `raydium-sdk-V2` (GPL-3.0), `streamflow-finance/js-sdk` (GPL-3.0), `Squads-Protocol/v4` (AGPL-3.0), `fingerprintjs` v4+ (BSL) | **KHÔNG copy/vendor code vào proprietary bundle.** Với Raydium CPMM gọi trực tiếp qua Anchor CPI (`raydium-cp-swap` là `Apache-2.0`); với Vesting tự viết module gọn trong `game9k_launchpad` (~250 dòng Rust); với Squads chỉ tương tác qua địa chỉ program on-chain; với device signal tự xây module privacy-safe. |
| **Không giấy phép (`no-license`)** | Các bản clone Pump.fun cộng đồng | **CẤM copy mã nguồn** (theo luật bản quyền, `no-license` = All Rights Reserved + rủi ro backdoor). |

---

## 4. Bản đồ ánh xạ vào cấu trúc Monorepo `khanhlegood1/GameFun`

Cấu trúc này kế thừa 100% thiết kế ở issue `[S0-01]` và mở rộng sạch sẽ cho toàn bộ hệ sinh thái **Game9K**:

```text
GameFun/                              # Monorepo pnpm workspace (Game9K)
├── apps/
│   ├── web/                          # Next.js App Router + TS (Portal, Dev Studio, Inspector, Arena, Launchpad UI)
│   ├── worker/                       # Node.js isolated container (pg-boss + yauzl + build diff + static scanner)
│   └── indexer/                      # Solana event indexer + OHLCV aggregator + Sybil/Cluster detector
├── workers/
│   └── game-delivery/                # Cloudflare Worker (R2 binding, isolated origin per version, CSP/Sandbox headers)
├── programs/                         # Anchor Workspace (Rust — Solana Smart Contracts)
│   ├── game9k-registry/            # Program 1: On-chain Game & Immutable Version Milestone Registry
│   ├── game9k-curve/               # Program 2: Version-Gated Bonding Curve, Anti-Bot/Anti-Dump, Ragequit & DEX CPI
│   └── game9k-rewards/             # Program 3: Proof-of-Play Community Vault (SPARK epochs) & Dev Milestone Vesting
├── packages/
│   ├── shared/                       # Zod schemas, domain types, version state machine, curve math (TS mirror)
│   ├── api-contract/                 # OpenAPI 3.1 specs + generated client + MSW handlers (AI-Agile P03)
│   ├── game-sdk/                     # @game9k/game-sdk (Poki-compatible HTML5 SDK: loading, gameplay, breaks, PoP heartbeat)
│   ├── solana-sdk/                   # Anchor IDL + generated @solana/kit instructions & PDA helpers
│   ├── arena-engine/                 # OpenSkill/Bradley-Terry pairwise ranking + confidence interval + vote weighting
│   └── game9k-cli/                 # CLI upload build ZIP từ CI/CD của game dev (tham khảo poki-cli / butler)
├── supabase/
│   ├── config.toml                   # Supabase CLI config
│   ├── migrations/                   # Committed SQL migrations + RLS policies + grants
│   └── tests/                        # pgTAP database authorization & immutability tests
├── infra/
│   ├── docker/                       # Production Dockerfiles (web, worker, indexer) + local docker-compose
│   └── coolify/                      # Staging/Production deployment manifests & runbooks
└── docs/                             # AI-Agile Living Documentation (PRD, OSS, Flows, DB, API, Solana, C4, Roadmap)
```
