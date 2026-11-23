# Game9K Launchpad (`GameFun`)

**Game9K Launchpad** (`game9k.com`) là nền tảng **Instant-Play HTML5 Game Portal** kết hợp **bệ phóng vốn Solana khóa theo cột mốc phiên bản (Version-Gated)**, được thiết kế và phát triển theo **AI-Agile Product Development Framework v1.0** (AI-native · HITL-governed · Contract-first · Living Documentation).

### Bốn trụ cột sản phẩm cốt lõi
1. **Phân phối & Kiểm định Game chuẩn [Poki](https://developers.poki.com/guide/working-with-poki):** Chơi tức thì trên trình duyệt (desktop & mobile, không cần ví), SDK tương thích 1:1 sự kiện Poki, công cụ **Game9K Inspector**, phễu kiểm định 3 chặng (*Mystery Tile Playtest → Player Fit Test 500 lượt → Web Fit Test CTR/Time/C2P*) và chia sẻ doanh thu công bằng (100% direct traffic / 50-50 portal traffic).
2. **Đánh giá Đối kháng theo Phiên bản chuẩn Arena:** Chế độ **Blind Version Duel** (`v(n)` vs `v(n-1)`) và **Category Duel** xếp hạng bằng thuật toán **OpenSkill / Bradley-Terry (95% CI)** chỉ tính phiếu từ phiên chơi thật đã xác minh.
3. **Bệ phóng Vốn Khóa theo Cột mốc Phiên bản (Pump.fun nâng cấp):** Token SPL Token-2022 (`1,000,000,000` cung, `0%` token nền tảng) mở dần theo tỷ lệ lũy kế trên tổng cung (`M1: 15% → M2: 33% → M3: 53% → M4: 70%` — tức hoàn tất `100%` phần đường cong; `30%` tổng cung còn lại khóa cố định cho `15%` thanh khoản DEX, `10%` thưởng game thủ, `5%` nhà phát triển và `0%` nền tảng) gắn chặt với `SHA-256` bản build và kết quả kiểm định; tự động Graduate sang **Meteora DAMM v2 / Raydium CPMM** với `0%` chênh lệch giá và khóa vĩnh viễn LP; hỗ trợ **Ragequit hoàn SOL** nếu dự án ngừng phát triển.
4. **Vòng lặp Cộng đồng & Chống Bot Đầu cơ Xả sớm chuẩn Notcoin:** Hệ thống **Energy**, điểm không chuyển nhượng **`SPARK`**, **Squads**, **Proof-of-Play (PoP) Tier** cấp quyền mua sớm **24h Gamer Priority Window** (có trần mỗi ví chặn sniper bot block-0), **Early-Exit Anti-Dump Fee** — phụ phí bán sớm giảm dần theo thời gian nắm giữ, cộng với phí cơ bản `1%` (xem thang đầy đủ ở Whitepaper §6.1): **chế độ mặc định `VBOND-LV`** `1% → 5% → 1%` (bot lướt sóng lỗ ròng **`−5,95%`**); **cấu hình đầu-cuối `VGBC-4T`** `1% → 12% → 6% → 3% → 1%` (lỗ ròng tới **`−12,88%`** ở cửa sổ `< 1 giờ`). Phụ phí thu được chuyển ngược 50% về quỹ thưởng game thủ + 40% nâng giá sàn, và trả thưởng **streaming 21 ngày**.

---

## Starter Kit — bản mẫu đã dựng

Bản mẫu **đua khủng long cho KOL livestream** (TikTok LIVE / YouTube Live) đã dựng và commit:
engine tất định, luật chơi có `sha256`, `simulate` mode, 5 cổng CI xanh. Mã nguồn nằm trong
[`assets/game9k-starter-kit.bundle`](./assets/game9k-starter-kit.bundle) — một **git bundle**
thật, vì token của phiên làm việc không có quyền ghi lên repo `Game9K-Starter-Kit`.

```bash
git clone assets/game9k-starter-kit.bundle Game9K-Starter-Kit
cd Game9K-Starter-Kit && bash scripts/run_gates.sh   # 5 cổng, không cần npm install
```

Lý do thiết kế, nguồn tham khảo, và các thứ **từ chối** (quà đổi thứ hạng, netcode thời gian
thực, sprite Chrome Dino): [`docs/23-dino-race-starter-kit.md`](./docs/23-dino-race-starter-kit.md).

---

## Bộ Tài liệu Sống (AI-Agile Living Documentation)

| # | Tài liệu | Pha AI-Agile | Mô tả |
|---|---|---|---|
| ★ | [**`docs/WHITEPAPER.md`**](./docs/WHITEPAPER.md) | **Strategy / Fundraising** | **Whitepaper Gọi vốn v1.5:** Nghịch lý ngành & từ điển dữ liệu có mẫu đo, **ánh xạ 4 nguyên tử công nghệ – kinh tế ↔ đặc tả hình thức Yellow Paper (§1.3)**, **giải phẫu "phiên bản là đơn vị tài sản" thành 4 thành phần riêng biệt (§1.5) + đối chiếu 4 hệ thống đánh số và lỗ hổng ngành game (§1.5b) + 3 cơ chế hào kinh tế ↔ 3 lớp cưỡng chế (§1.6–1.7)**, 5W1H + Kill Criteria, chuẩn Phiên bản 3 Lớp, *Gate-First* & Tự khóa tay on-chain, NQ `05/2025/NQ-CP`, kinh tế đơn vị `VPH` + độ nhạy eCPM, `0%` token nền tảng, điều KHÔNG hứa & gọi vốn 4 vòng (`$1M → $3M → $12M → $25M`) |
| ◆ | [**`docs/YELLOWPAPER.md`**](./docs/YELLOWPAPER.md) | **Formal Spec / Audit** | **Yellow Paper v1.0:** Đặc tả hình thức giao thức — hệ tiên đề, DAG phiên bản & hàm `BuildDiff`, toán học `PoPW`/`BotShare`/Bradley-Terry `95% LCB`, số học `u128` (`VGBC-4T` & `VBOND-LV`), 12 bất biến & chứng minh 6 định lý, bố cục byte `Ed25519`, ngân sách `CU/Rent` & kiểm chứng `S1–S9` + `10,000` fuzz ops ([`scripts/verify_protocol_math.py`](./scripts/verify_protocol_math.py)) |
| ✦ | [**`docs/Game9K-Pitch-Deck.pdf`**](./docs/Game9K-Pitch-Deck.pdf) | **Investor Deck** | **Pitch Deck Gọi vốn (14 slides, 16:9):** Đồng bộ Whitepaper `v1.5` & Yellow Paper `v1.0` — *"Không Tốt hơn — Không Cho Mở Thanh khoản Mới"*; J-Curve với hòa vốn **Năm 4**, khung **Tách Cầu/Cung** (NQ `05/2025/NQ-CP`), phép trừ escrow `60,221994 SOL` và bảng P&L bottom-up — dựng lại bằng [`scripts/build_pitch_deck.py`](./scripts/build_pitch_deck.py) và kiểm chứng bằng [`scripts/check_pitch_deck.py`](./scripts/check_pitch_deck.py) |
| ✧ | [**`docs/Game9K-Whitepaper-v1.5.pdf`**](./docs/Game9K-Whitepaper-v1.5.pdf) | **Print / Share** | **Whitepaper `v1.5` bản PDF (35 trang, A4):** bìa + mục lục có số trang + outline điều hướng, bảng rộng tự chuyển trang ngang, font Việt nhúng đầy đủ — dựng lại bằng [`scripts/build_whitepaper_pdf.py`](./scripts/build_whitepaper_pdf.py) |
| ✧ | [**`docs/Game9K-Yellow-Paper-v1.0.pdf`**](./docs/Game9K-Yellow-Paper-v1.0.pdf) | **Print / Audit** | **Yellow Paper `v1.0` bản PDF (17 trang, A4):** đặc tả hình thức, số học `u128`, mật mã `Ed25519` / Merkle RFC 6962 — cùng pipeline dựng PDF |
| 0 | [`docs/00-open-source-landscape.md`](./docs/00-open-source-landscape.md) | P01 / P04 | Danh mục mã nguồn mở đã xác minh cho từng module, ma trận Build/Adopt/CPI, kiểm soát License & cấu trúc Monorepo |
| 1 | [**`docs/PRD.md`**](./docs/PRD.md) | **P01 → P06** | **PRD Tổng thể:** Tầm nhìn, OKRs, Personas, Cơ chế Version-Gated Growth & 6 lớp chống bot, FRs, User Stories, BDD, MoSCoW, HITL Gates, NFR & DORA |
| 2 | [`docs/01-user-flows-and-ux.md`](./docs/01-user-flows-and-ux.md) | P02 | Sitemap, danh mục màn hình (Screen Specs) & 8 sơ đồ Luồng người dùng End-to-End |
| 3 | [`docs/02-database-schema.md`](./docs/02-database-schema.md) | P03-A | Sơ đồ ERD, thiết kế chi tiết 34 bảng PostgreSQL/Supabase, State Machine, Indexes & ma trận RLS |
| 4 | [`docs/03-api-specification.md`](./docs/03-api-specification.md) | P03-B | Đặc tả REST API `/api/v1`, SSE streams, `@game9k/game-sdk` (`postMessage`), Rate Limit & Error Catalog |
| 5 | [`docs/04-solana-smart-contracts.md`](./docs/04-solana-smart-contracts.md) | P03-C | Thiết kế 3 Anchor Programs (`game9k_registry`, `game9k_curve`, `game9k_rewards`), PDA Map, toán học `u128` VGBC, Ed25519 PoP Attestation, Ragequit, DEX CPI & 8 Bất biến Fuzzing |
| 6 | [`docs/05-c4-architecture-and-nfr.md`](./docs/05-c4-architecture-and-nfr.md) | P05 / P06 | Kiến trúc C4 (Level 1–4 + Deployment), 6 ADRs, Mô hình đe dọa STRIDE & Well-Architected Review |
| 7 | [`docs/06-implementation-roadmap.md`](./docs/06-implementation-roadmap.md) | P04 / P06 | Kế hoạch triển khai 9 Module (`M01`–`M09`) & Lộ trình Sprint 0 → Sprint 7 (nối tiếp 17 GitHub Issues `[S0-01]..[S1-09]`) |
| 8 | [`docs/README-PDF.md`](./docs/README-PDF.md) | Docs | Quy trình dựng lại & kiểm chứng bốn bản PDF in (3 bản dài + legal brief 1 tờ A4) |
| 9 | [`docs/07-docs-as-code-model.md`](./docs/07-docs-as-code-model.md) | Docs | Mô hình tài liệu & kiểm chứng lấy từ Chainstack dev-portal: AGENTS.md, llms.txt, link check, CI cổng tái lập PDF |
| 10 | [`docs/08-legal-brief-vn-licensing.md`](./docs/08-legal-brief-vn-licensing.md) · [`PDF`](./docs/Game9K-Legal-Brief-VN.pdf) | Legal | Bản tóm tắt 1 trang gửi luật sư: mô hình Game9K + 4 câu hỏi về cấp phép game và dữ liệu cá nhân tại Việt Nam (`Game9K-Legal-Brief-VN.pdf`, **đúng 1 tờ A4** in một mặt) |
| 11 | [`docs/09-xwg-portal-teardown.md`](./docs/09-xwg-portal-teardown.md) | Research | Teardown cổng `xwg.games`: cái gì dùng được cho catalog Game9K (chip mốc/trạng thái, facet thiết bị, bảng thông số kiểm chứng) và 6 thứ từ chối — kèm bằng chứng quan sát có mã F1–F12 |
| 12 | [`docs/10-zorochain-xwg-teardown.md`](./docs/10-zorochain-xwg-teardown.md) | Research | Teardown ZoroChain + XWG whitepaper: Proof-of-workload và luật **suy giảm PoP score** (`W=0,60`, epoch 7 ngày) đã vá vào schema — chốt bằng `scripts/verify_pop_decay.py` |
| 13 | [`docs/11-auth-wallet-ux.md`](./docs/11-auth-wallet-ux.md) | ADR-007 | Đăng nhập email/Google + **ví Web3 ẩn dưới nền** bằng passkey smart wallet (SIMD-0075): so sánh 3 phương án (MPC vendor / passkey PDA / server giữ khoá), paymaster có trần, khôi phục 72h |
| 14 | [`docs/12-mintlify-docs-site.md`](./docs/12-mintlify-docs-site.md) | Docs | Kiểm chứng `chainstack/dev-portal` + `Game9Kmintlify` và kế hoạch dựng docs site: hai chỗ **sửa lại** nhận định ban đầu, và rào cản MDX (48 khối `$$`, 782 inline math, 1.168 cặp ngoặc) |
| 15 | [`docs/13-affiliate-growth-loop.md`](./docs/13-affiliate-growth-loop.md) | Growth | GoStream + StreamAgain: lấy **trả theo doanh thu định kỳ** và **phễu duyệt**; từ chối mô hình thuê bao, câu "thu nhập thụ động", và trả thưởng bằng token |
| 16 | [`docs/14-growth-tools-and-measurement.md`](./docs/14-growth-tools-and-measurement.md) | Growth | StreamMix + Similarweb: bán theo **đơn vị đo được**, làm **plugin trong công cụ sẵn có**, và **sổ số liệu 6 cột** (nguồn · ngày · loại · sai lệch) |
| 17 | [`docs/15-livestream-tools-and-token-question.md`](./docs/15-livestream-tools-and-token-question.md) | Growth | "Coin" của StreamMix là **credit trả trước**, không phải token; TikFinity (simulate mode) + StreamToEarn (**trần theo USD**) + Similarweb (**panel không thấy iframe**) |
| 18 | [`docs/16-anchor-game-for-kol.md`](./docs/16-anchor-game-for-kol.md) | Growth | Game neo cho KOL: **không** dùng đua vịt (không tạo `work`, PoP lọc oan người thật); chấm 5 ứng viên, chọn **"một nút, một biến số"** `9/10`; lộ ra lỗi ngưỡng Bronze `90` phút |
| 19 | [`docs/17-second-screen-race.md`](./docs/17-second-screen-race.md) | Growth | Đua second-screen: 3 cơ chế dùng được; **xếp lệnh trước** thay vì bấm đồng thời (mobile không làm được); **đua tất định** thay netcode; G4 **chưa** có căn cứ; đừng để Game9K vừa làm game vừa xếp hạng |
| 20 | [`docs/18-flagship-template-review.md`](./docs/18-flagship-template-review.md) | Growth | Flagship template: Starter Kit + JSON tách logic ✅; **"9K Labs"** không tạo ra độc lập (phép thử: *cổng có từ chối được game của mình?*); **reskin 48h** làm Arena vô dụng; bảng doanh thu Ads ở Pre-Seed = `$60–180`/tháng |
| 21 | [`docs/19-gitcoin-patterns.md`](./docs/19-gitcoin-patterns.md) | Growth | Gitcoin 2026 = **thư viện**, không phải quỹ. Lấy: hồ sơ theo chiến dịch (`M2/4`), "đang diễn ra", duyệt có tiêu chuẩn, số liệu tính lại được. **Từ chối quadratic funding** — trả theo *số người* phá mọi lớp chống bot |
| 22 | [`docs/20-proximax-teardown-storage.md`](./docs/20-proximax-teardown-storage.md) | Tech | ProximaX: **kết luận đúng, ba lý do sai** — GitHub `cpp-xpx-chain` có commit `18/03/2026` (chỉ **ví** mới đóng băng); "buộc token native" loại luôn Solana; **Greenfield cho state game làm hỏng `verified_play`** |
| 23 | [`docs/21-starter-kit-spec-verification.md`](./docs/21-starter-kit-spec-verification.md) | Tech | Kiểm chứng đặc tả Starter Kit: **`Presence` 5/30s** + **KV trễ `60` giây** là hai phát hiện đổi thiết kế; số gói engine **đo lại sai** (`255`/`352` KB gz, không phải `126`/`274`); Realtime đẩy game vào nhóm **G1** |
| 24 | [`docs/22-agent-sdk-workflow-patterns.md`](./docs/22-agent-sdk-workflow-patterns.md) | Process | `nccasia/agent-sdk` (Apache-2.0, **beta**, `3` sao): lấy **5 mẫu quy trình** — bất biến do test canh, registry thay nhánh, bench sống ≠ test, trace đọc được, **config bất biến + state một JSON**; **không** dùng làm engine quyết định |
| 25 | [`docs/23-dino-race-starter-kit.md`](./docs/23-dino-race-starter-kit.md) | Growth | Đua khủng long cho KOL livestream — 11 nguồn: **4/9 repo không có giấy phép**, `marble-race` **không có mã**; giữ 5 cơ chế; **quà không đổi thứ hạng** (`docs/17` **R6**); khung chạy được ở `Game9K-Starter-Kit` |
| 26 | [`docs/24-agent-loop-lessons.md`](./docs/24-agent-loop-lessons.md) | Process | Vòng lặp tác nhân: `FastChat` là hạ tầng **Battle Mode**, không phải Agent Mode; học từ 4 agent mở; **cổng `check_agent_rules.py`** biến 6 nhóm quy ước `AGENTS.md` thành kiểm tự động |
| 27 | [`docs/25-decisions-api-for-project-management.md`](./docs/25-decisions-api-for-project-management.md) | Process | Decisions API (`gemini-decision-1`): lấy **hình dạng phán quyết** (câu hỏi có khoá + kiểu + xác suất) để soạn 6 cổng HITL; **không** dùng để ký cổng; công cụ offline `gate_decide.py` |
| 28 | [`docs/26-belief-record-project-memory.md`](./docs/26-belief-record-project-memory.md) | Process | Bản ghi niềm tin dự án (học `Proactive-Co-Creator`): mỗi giá trị có `source` trỏ **đúng dòng** trong `docs/`, câu hỏi **đã bị luật trả lời thì không hỏi lại**; cổng `check_specs.py` (`--tick` / `--questions` / `--answer`) |
| 29 | [`docs/27-sdk-contract-poki-vs-xsolla.md`](./docs/27-sdk-contract-poki-vs-xsolla.md) | Tech | Xsolla SDK là **bưu điện thanh toán**, không phải SDK cổng game (không có nền web/WebGL); lấy **Web Shop `0%`** + **trạng thái `BreakResult`**; SDK Game9K là **hai loài**; cổng `check_sdk.py` (5 bất biến, ngân sách `12 KB`) |
| 30 | [`docs/28-sdk-contract-lock-and-what-not-to-copy.md`](./docs/28-sdk-contract-lock-and-what-not-to-copy.md) | Tech | Khoá hợp đồng SDK: `splice` (MIT) sinh client **REST** nên **không** dùng cho SDK iframe — nhưng `dist/` đã commit của nó **lệch khỏi `src/`**; POS Kit **không có giấy phép**, `card_demo` là *kiểu dữ liệu*; cổng `check_sdk_drift.py` (5 bất biến, hash bề mặt `sha256:fa218660…`) |
| 31 | [`docs/29-sandbox-errors-and-sdk-boundary.md`](./docs/29-sandbox-errors-and-sdk-boundary.md) | Tech | 4 repo `e2b-dev`: `runtime` tách control/data plane ✅ (Game9K đã tách), nhưng **không** chạy game trong VM; lấy **cách đặt tên lỗi** (`NotRunning` ≠ `Unreachable`, kèm tự ghi giới hạn); SDK lên `0.2.0`: **bỏ `resolve(null)`**, 7 mã lỗi, cổng `check_sdk_errors.py`; `fragments` là **fork** |
| 32 | [`docs/30-openrouter-deterministic-egress.md`](./docs/30-openrouter-deterministic-egress.md) | Process | OpenRouter = **nhà định tuyến**, không phải mô hình: cùng prompt có thể đi **hai nhà cung cấp khác nhau** ⇒ định nghĩa của *không tất định*. **Không** dùng cho CI/Arena/SDK; lấy **4 tham số từ chối định tuyến**; cổng `check_egress_lock.py` biến *"chưa gọi mạng"* thành *"không gọi được"* |
| 33 | [`docs/31-gate-ladder-and-agent-honesty.md`](./docs/31-gate-ladder-and-agent-honesty.md) | Process | **Thang cổng**: *"trượt bài dễ thì không qua bài khó"* ⇒ 6 cổng HITL phải là **thang tăng**, không có bậc thừa. `awesome-ai-agents` là **fork**, giấy phép `NOASSERTION`; cổng `check_gate_ladder.py` (4 bất biến · **20 hạng mục** trên 6 bậc) — và nó bắt lỗi **đếm mệnh đề thay vì hạng mục** của chính tôi |

**Tài liệu cho tác nhân & chỉ mục máy đọc:** [`AGENTS.md`](./AGENTS.md) là quy ước bắt buộc cho mọi người/AI sửa repo (ba luật, thứ bậc nguồn sự thật, cách kiểm chứng tất định). [`llms.txt`](./llms.txt) là chỉ mục máy đọc của toàn bộ tài liệu — để tác nhân AI đọc đúng file thay vì đoán.

---

## Trạng thái Triển khai

- **Phase hiện tại:** `P01–P03 Living Docs Ready` — chờ duyệt **HITL Gate G1** để bắt đầu triển khai `M01` (`[S0-01] Bootstrap the pnpm monorepo`) và song song dựng prototype UI (`P02`) / Anchor workspace (`M08`).
