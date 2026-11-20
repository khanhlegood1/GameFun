# MetaPump (`GameFun`)

**MetaPump** là nền tảng **Instant-Play HTML5 Game Portal** kết hợp **Version-Gated Solana Launchpad**, được thiết kế và phát triển theo **AI-Agile Product Development Framework v1.0** (AI-native · HITL-governed · Contract-first · Living Documentation).

### Bốn trụ cột sản phẩm cốt lõi
1. **Phân phối & Kiểm định Game chuẩn [Poki](https://developers.poki.com/guide/working-with-poki):** Chơi tức thì trên trình duyệt (desktop & mobile, không cần ví), SDK tương thích 1:1 sự kiện Poki, công cụ **MetaPump Inspector**, phễu kiểm định 3 chặng (*Mystery Tile Playtest → Player Fit Test 500 lượt → Web Fit Test CTR/Time/C2P*) và chia sẻ doanh thu công bằng (100% direct traffic / 50-50 portal traffic).
2. **Đánh giá Đối kháng theo Phiên bản chuẩn Arena:** Chế độ **Blind Version Duel** (`v(n)` vs `v(n-1)`) và **Category Duel** xếp hạng bằng thuật toán **OpenSkill / Bradley-Terry (95% CI)** chỉ tính phiếu từ phiên chơi thật đã xác minh.
3. **Launchpad Minh bạch Khóa theo Cột mốc Phiên bản (Pump.fun nâng cấp):** Token SPL Token-2022 (`1,000,000,000` cung, `0%` token nền tảng) mở dần theo tỷ lệ lũy kế trên tổng cung (`M1: 15% → M2: 33% → M3: 53% → M4: 70%` — tức hoàn tất `100%` phần đường cong; `30%` tổng cung còn lại khóa cố định cho `15%` thanh khoản DEX, `10%` thưởng game thủ, `5%` nhà phát triển và `0%` nền tảng) gắn chặt với `SHA-256` bản build và kết quả kiểm định; tự động Graduate sang **Meteora DAMM v2 / Raydium CPMM** với `0%` chênh lệch giá và khóa vĩnh viễn LP; hỗ trợ **Ragequit hoàn SOL** nếu dự án ngừng phát triển.
4. **Vòng lặp Cộng đồng & Chống Bot Đầu cơ Xả sớm chuẩn Notcoin:** Hệ thống **Energy**, điểm không chuyển nhượng **`SPARK`**, **Squads**, **Proof-of-Play (PoP) Tier** cấp quyền mua sớm **24h Gamer Priority Window** (có trần mỗi ví chặn sniper bot block-0), **Early-Exit Anti-Dump Fee (12% → 6% → 3% → 1%)** chuyển ngược 50% về quỹ thưởng game thủ + 40% nâng giá sàn, và trả thưởng **streaming 21 ngày**.

---

## Bộ Tài liệu Sống (AI-Agile Living Documentation)

| # | Tài liệu | Pha AI-Agile | Mô tả |
|---|---|---|---|
| ★ | [**`docs/WHITEPAPER.md`**](./docs/WHITEPAPER.md) | **Strategy / Fundraising** | **Whitepaper Gọi vốn v1.4:** Nghịch lý ngành & từ điển dữ liệu có mẫu đo, **ánh xạ 4 nguyên tử công nghệ – kinh tế ↔ đặc tả hình thức Yellow Paper (§1.3)**, 5W1H + Kill Criteria, chuẩn Phiên bản 3 Lớp, *Gate-First* & Tự khóa tay on-chain, NQ `05/2025/NQ-CP`, kinh tế đơn vị `VPH` + độ nhạy eCPM, `0%` token nền tảng, điều KHÔNG hứa & gọi vốn 4 vòng (`$1M → $3M → $12M → $25M`) |
| ◆ | [**`docs/YELLOWPAPER.md`**](./docs/YELLOWPAPER.md) | **Formal Spec / Audit** | **Yellow Paper v1.0:** Đặc tả hình thức giao thức — hệ tiên đề, DAG phiên bản & hàm `BuildDiff`, toán học `PoPW`/`BotShare`/Bradley-Terry `95% LCB`, số học `u128` (`VGBC-4T` & `VBOND-LV`), 12 bất biến & chứng minh 6 định lý, bố cục byte `Ed25519`, ngân sách `CU/Rent` & kiểm chứng `S1–S9` + `10,000` fuzz ops ([`scripts/verify_protocol_math.py`](./scripts/verify_protocol_math.py)) |
| ✦ | [**`docs/MetaPump-Pitch-Deck.pdf`**](./docs/MetaPump-Pitch-Deck.pdf) | **Investor Deck** | **Pitch Deck Gọi vốn v1.4 (14 slides, 16:9):** Đồng bộ Whitepaper `v1.4` & Yellow Paper `v1.0` (*"Không Tốt hơn — Không Cho Mở Thanh khoản Mới"*, kèm bản chỉnh sửa trực tiếp trên Google Slides) |
| 0 | [`docs/00-open-source-landscape.md`](./docs/00-open-source-landscape.md) | P01 / P04 | Danh mục mã nguồn mở đã xác minh cho từng module, ma trận Build/Adopt/CPI, kiểm soát License & cấu trúc Monorepo |
| 1 | [**`docs/PRD.md`**](./docs/PRD.md) | **P01 → P06** | **PRD Tổng thể:** Tầm nhìn, OKRs, Personas, Cơ chế Version-Gated Growth & 6 lớp chống bot, FRs, User Stories, BDD, MoSCoW, HITL Gates, NFR & DORA |
| 2 | [`docs/01-user-flows-and-ux.md`](./docs/01-user-flows-and-ux.md) | P02 | Sitemap, danh mục màn hình (Screen Specs) & 8 sơ đồ Luồng người dùng End-to-End |
| 3 | [`docs/02-database-schema.md`](./docs/02-database-schema.md) | P03-A | Sơ đồ ERD, thiết kế chi tiết 31 bảng PostgreSQL/Supabase, State Machine, Indexes & ma trận RLS |
| 4 | [`docs/03-api-specification.md`](./docs/03-api-specification.md) | P03-B | Đặc tả REST API `/api/v1`, SSE streams, `@metapump/game-sdk` (`postMessage`), Rate Limit & Error Catalog |
| 5 | [`docs/04-solana-smart-contracts.md`](./docs/04-solana-smart-contracts.md) | P03-C | Thiết kế 3 Anchor Programs (`metapump_registry`, `metapump_curve`, `metapump_rewards`), PDA Map, toán học `u128` VGBC, Ed25519 PoP Attestation, Ragequit, DEX CPI & 8 Bất biến Fuzzing |
| 6 | [`docs/05-c4-architecture-and-nfr.md`](./docs/05-c4-architecture-and-nfr.md) | P05 / P06 | Kiến trúc C4 (Level 1–4 + Deployment), 6 ADRs, Mô hình đe dọa STRIDE & Well-Architected Review |
| 7 | [`docs/06-implementation-roadmap.md`](./docs/06-implementation-roadmap.md) | P04 / P06 | Kế hoạch triển khai 9 Module (`M01`–`M09`) & Lộ trình Sprint 0 → Sprint 7 (nối tiếp 17 GitHub Issues `[S0-01]..[S1-09]`) |

---

## Trạng thái Triển khai

- **Phase hiện tại:** `P01–P03 Living Docs Ready` — chờ duyệt **HITL Gate G1** để bắt đầu triển khai `M01` (`[S0-01] Bootstrap the pnpm monorepo`) và song song dựng prototype UI (`P02`) / Anchor workspace (`M08`).
