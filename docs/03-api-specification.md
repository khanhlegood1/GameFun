# P03-B — Đặc tả API Contract & Game SDK (OpenAPI 3.1, SSE & PostMessage)

> **Tài liệu sống (Living Documentation):** `docs/03-api-specification.md`  
> **Giai đoạn AI-Agile:** `P03 — API Contract First` (sinh tự động TypeScript client qua `@hey-api/openapi-ts` và mock server qua `Prism`/`MSW` trong `packages/api-contract`)  
> **Base URL:** `https://game9k.com/api/v1` (Staging: `https://staging.game9k.com/api/v1`)  
> **Game Delivery Domains (Cô lập hoàn toàn khỏi cookie portal):**  
> - Preview (chưa phát hành): `https://<version-id>.preview.game9k-cdn.net`  
> - Live / Fit / Arena: `https://<version-id>.play.game9k-cdn.net`

---

## 1. Quy ước Chung (Cross-Cutting API Conventions)

### 1.1. Xác thực & Phân quyền
- **Portal Session:** Supabase Auth SSR cookie (`HttpOnly`, `Secure`, `SameSite=Lax`, gắn chặt domain `game9k.com`, **không bao giờ** chia sẻ sang `game9k-cdn.net`).
- **Developer CLI Token:** `Authorization: Bearer mp_pat_<random>` (SHA-256 hash lưu DB, chỉ có scope `upload:write`, `version:read` trên các game sở hữu).
- **Preview / Play Edge Token:** JWT ký bằng EdDSA (`Ed25519`), thời hạn ngắn (`15 phút` cho preview, `2 giờ` cho play), nhúng `vid` (`version_id`), `ptv` (`preview_token_version` để thu hồi tức thì), `aud` (subdomain đích).
- **Internal Webhook (Solana Indexer / Helius):** HMAC-SHA256 header `X-Game9K-Signature` + allowlist IP/secret.

### 1.2. Định dạng Phản hồi, Idempotency & Correlation ID
- Mọi request ghi nhạy cảm (`upload-complete`, `arena/vote`, `pop-attestation`, `milestone/attestation`) hỗ trợ header `Idempotency-Key: <uuid-v4>`.
- Mọi response trả kèm `X-Correlation-Id: <uuid>` (nối thẳng vào `audit_logs` và `processing_jobs`).
- Chuẩn envelope JSON thống nhất:

```json
// Thành công (200 / 201 / 202)
{
  "data": { "...": "..." },
  "meta": { "correlationId": "01934f2a-7c10-7b11-9a22-4f881e2c9001", "nextCursor": null }
}

// Lỗi (4xx / 5xx — không bao giờ lộ stack trace, đường dẫn file server hay secret)
{
  "error": {
    "code": "ARCHIVE_PATH_TRAVERSAL",
    "message": "Gói ZIP chứa đường dẫn không hợp lệ vượt ra ngoài thư mục gốc.",
    "hint": "Hãy nén trực tiếp nội dung thư mục build sao cho index.html nằm ở cấp gốc.",
    "fieldErrors": {}
  },
  "meta": { "correlationId": "01934f2a-7c10-7b11-9a22-4f881e2c9001" }
}
```

---

## 2. Danh mục Toàn bộ REST & SSE Endpoints theo Module

### 2.1. Health, Auth, Profile & SIWS Wallet (`M01`)

| Method | Endpoint | Auth | Rate Limit | Mô tả chức năng |
|---|---|---|---|---|
| `GET` | `/api/health` | Public | 120/m | Readiness/liveness nhẹ cho Docker & Coolify (`S0-02`, `S0-08`); không lộ thông tin nội bộ. |
| `GET` | `/api/v1/me` | User | 60/m | Trả về `profile`, `developerProfile`, `primaryWallet`, `popState` (đã tính hồi phục Energy). |
| `PATCH` | `/api/v1/me` | User | 10/m | Cập nhật `displayName`, `avatarKey`, `locale` (không nhận `role`/`status`). |
| `POST` | `/api/v1/developers/apply` | `player` | 3/d | Nộp đơn đăng ký trở thành Developer (`studioName`, `studioSlug`, `portfolioLinks`). |
| `POST` | `/api/v1/wallets/siws/challenge` | User | 10/m | Tạo thông điệp **Sign-In With Solana (SIWS)** kèm `nonce` 5 phút + `domain` chống phishing. |
| `POST` | `/api/v1/wallets/siws/verify` | User | 10/m | Xác minh chữ ký Ed25519 của ví Solana, liên kết vào `user_wallets`, áp cooldown 7 ngày chống xoay vòng ví. |
| `POST` | `/api/v1/auth/oauth/google` | Public | 10/m | Đăng nhập/đăng ký bằng Google qua Supabase OAuth; trả session. **Không** tạo ví on-chain (xem `A1`, `ADR-007`). |
| `POST` | `/api/v1/wallets/passkey/register` | User | 5/m | Đăng ký passkey (WebAuthn, P-256) cho smart wallet PDA của user; lưu `pubkey_p256` vào `wallet_passkeys` với `activates_at = now() + 72h` nếu không phải passkey đầu tiên. |
| `POST` | `/api/v1/wallets/passkey/verify` | User | 20/m | Nhận `credential_id` + signature + `clientDataJSON`, xác minh phong bì WebAuthn, trả về intent đã ký để client ghép giao dịch. |
| `POST` | `/api/v1/wallets/recovery` | User | 3/d | Mở yêu cầu khôi phục (magic link email hoặc passkey còn lại). Luôn tạo `cooling_until = now() + 72h`. |
| `POST` | `/api/v1/wallets/recovery/{id}/cancel` | User | 10/d | Chủ ví chặn một yêu cầu khôi phục khả nghi trong cửa sổ 72h. |
| `POST` | `/api/v1/wallets/sponsor` | User | 30/m | Paymaster: kiểm `instruction` ∈ danh sách cho phép, trần ngày/tháng theo `gas_sponsorships`, `sybil_risk_score < 0.5`; trả chữ ký fee payer cho phong bì **đã có** chữ ký passkey. |

---

### 2.2. Developer Studio, Direct R2 Upload, Validation & Isolated Preview (`M02`, `M03` — `S1-01`..`S1-09`)

| Method | Endpoint | Auth | Rate Limit | Mô tả chức năng |
|---|---|---|---|---|
| `GET` | `/api/v1/developer/games` | `developer` | 60/m | Danh sách game thuộc sở hữu của developer kèm version live, version mới nhất & mốc hiện tại. |
| `POST` | `/api/v1/developer/games` | `developer` | 10/h | Tạo game mới; chuẩn hóa `slug` (nếu trùng trả mã `SLUG_CONFLICT` kèm `suggestedSlug`). |
| `GET` | `/api/v1/developer/games/{gameId}` | Owner | 60/m | Chi tiết game, danh sách phiên bản bất biến, tiến độ Fit/Arena & trạng thái Launchpad. |
| `PATCH` | `/api/v1/developer/games/{gameId}` | Owner | 30/m | Sửa metadata game (không cho sửa `liveVersionId` hay `currentMilestone`). |
| `POST` | `/api/v1/developer/games/{gameId}/archive` | Owner | 5/h | Lưu trữ game (ẩn khỏi portal, giữ nguyên bất biến toàn bộ build cũ). |
| `POST` | `/api/v1/developer/games/{gameId}/upload-sessions` | Owner | 15/h | Khởi tạo phiên upload `.zip` (≤ 50 MB), trả về presigned `PUT` URL 15 phút tới R2 quarantine. |
| `POST` | `/api/v1/developer/upload-sessions/{sessionId}/complete` | Owner | 20/h | Idempotent: `HEAD` kiểm tra object trên R2, cấp `version_number` tuần tự, đẩy job `validate_extract_zip`. |
| `POST` | `/api/v1/developer/upload-sessions/{sessionId}/abort` | Owner | 20/h | Hủy phiên upload dở dang và lên lịch dọn object rác trên R2 quarantine. |
| `GET` | `/api/v1/developer/versions/{versionId}` | Owner/Curator | 60/m | Lấy trạng thái version, SHA-256, `validationReport`, `versionDiff` và trạng thái xử lý job. |
| `GET` | `/api/v1/developer/versions/{versionId}/events` | Owner | 10/m | **SSE Stream** đẩy cập nhật thời gian thực: `uploaded → processing → preview_ready / validation_failed`. |
| `POST` | `/api/v1/developer/versions/{versionId}/preview-token` | Owner/Curator | 30/m | Cấp URL preview ngắn hạn trên `https://<versionId>.preview.game9k-cdn.net` + mã QR cho mobile Inspector. |
| `POST` | `/api/v1/developer/versions/{versionId}/revoke-preview` | Owner/Admin | 20/m | Tăng `preview_token_version + 1` để vô hiệu hóa ngay mọi link preview đang mở. |
| `PATCH` | `/api/v1/developer/versions/{versionId}/inspector-qa` | Owner/Curator | 30/m | Lưu kết quả đánh dấu QA checklist trong Game9K Inspector. |

#### Mẫu Payload tiêu biểu: Khởi tạo & Hoàn tất Upload ZIP

```json
// POST /api/v1/developer/games/8f12.../upload-sessions — Request
{
  "filename": "sky-drift-v0.2.0.zip",
  "byteSize": 18452910,
  "contentType": "application/zip",
  "semanticLabel": "v0.2.0",
  "changelog": "Thêm màn Boss 3, tối ưu texture WebP giảm 38% thời gian tải đầu, tích hợp gameplayStart/Stop."
}

// 201 Created — Response (presignedUrl KHÔNG BAO GIỜ ghi vào log server/audit_logs)
{
  "data": {
    "uploadSessionId": "c390a1d4-22b0-4b9f-9f71-81a9e7710023",
    "expiresAt": "2026-11-18T11:15:00Z",
    "maxBytes": 52428800,
    "upload": {
      "method": "PUT",
      "url": "https://<account>.r2.cloudflarestorage.com/game9k-quarantine/q/9f8a...c12?X-Amz-Expires=900&...",
      "requiredHeaders": {
        "Content-Type": "application/zip",
        "Content-Length": "18452910"
      }
    }
  }
}
```

---

### 2.3. Play Portal, Sessions, Cloud Save & Poki 3-Stage Fit Pipeline (`M04`, `M05`)

| Method | Endpoint | Auth | Rate Limit | Mô tả chức năng |
|---|---|---|---|---|
| `GET` | `/api/v1/games` | Public | 120/m | Lưới game trang chủ/category/search (cursor pagination, lọc `category`, `orientation`, `hasLaunchpad`, `sort=trending\|top_arena\|new`). |
| `GET` | `/api/v1/games/{slug}` | Public | 120/m | Chi tiết game công khai, live version, điểm Arena, tóm tắt mốc token (nếu có) & danh sách version công khai. |
| `POST` | `/api/v1/play-sessions` | Public/User | 30/m | Khởi tạo phiên chơi, phân loại `trafficSource` (`direct_dev` vs `portal_*`), trả về `playUrl` + `playToken` + `heartbeatNonce`. |
| `POST` | `/api/v1/play-sessions/{sessionId}/heartbeat` | Public/User | 6/m | Nhận nhịp 15s (`activeDeltaSec`, `inputCount`, `entropyBucket`, `sdkEvents`, `nextNonce`), kiểm tra PoP, trừ Energy & cộng `SPARK`. |
| `POST` | `/api/v1/play-sessions/{sessionId}/end` | Public/User | 30/m | Đóng phiên chơi, chốt thời lượng thực cho thống kê Fit Test & C2P. |
| `GET` / `PUT` | `/api/v1/games/{gameId}/cloud-save/{slot}` | User | 30/m | Đọc/ghi Cloud Save (AUDS ≤ 128 KB) cho game thủ đang đăng nhập. |
| `GET` | `/api/v1/mystery-tile` | User | 30/m | Lấy 1 game đang chạy `playtest_10` khớp sở thích thể loại & thiết bị của người chơi. |
| `POST` | `/api/v1/playtest/{fitTestId}/recordings` | User | 5/h | Khởi tạo presigned upload cho video canvas + input/console log sau khi người chơi ký consent. |
| `POST` | `/api/v1/developer/versions/{versionId}/fit-tests` | Owner | 5/d | Gửi bản build vào `playtest_10`, `player_fit_500` (tối đa 2/ngày, cần xem đủ 10 bản ghi playtest) hoặc `web_fit`. |
| `GET` | `/api/v1/developer/games/{gameId}/fit-tests/compare` | Owner/Curator | 60/m | So sánh song song histogram playtime & chỉ số CTR/Time/C2P giữa 2 phiên bản (`?vA=...&vB=...`). |
| `POST` | `/api/v1/developer/recordings/{recordingId}/watched` | Owner | 60/m | Đánh dấu developer đã xem hết bản ghi playtest để mở khóa vòng Player Fit Test. |

---

### 2.4. Game9K Version Arena (`M06` — Arena.io Style)

| Method | Endpoint | Auth | Rate Limit | Mô tả chức năng |
|---|---|---|---|---|
| `POST` | `/api/v1/arena/matches` | User | 15/h | Tạo trận Blind A/B (`mode: "version_duel" \| "category_duel"`, tùy chọn `gameSlug` hoặc `category`, kèm `altchaPayload`). Trả `slotA` & `slotB` **không lộ `versionNumber`**. |
| `POST` | `/api/v1/arena/matches/{matchId}/vote` | Voter | 20/h | Gửi phiếu bầu (`outcome`, `subscores`, `feedbackNote`). Yêu cầu `slot_a_play_sec >= 90` & `slot_b_play_sec >= 90`. Trả về thông tin **Reveal** + `sparkEarned`. |
| `GET` | `/api/v1/arena/leaderboard` | Public | 120/m | Bảng xếp hạng Bradley-Terry Elo kèm 95% CI & 4 chiều điểm phụ theo category. |
| `GET` | `/api/v1/arena/games/{slug}/versions` | Public | 120/m | Đường cong tiến hóa điểm Arena qua từng phiên bản `v0.1 → v0.2 → v0.5 → v1.0` của một game. |
| `POST` | `/api/v1/developer/versions/{versionId}/arena-campaigns` | Owner | 3/d | Mở chiến dịch đối kháng mù `v(n)` vs `v(n-1)` để chứng minh đạt mốc M2/M3/M4/M5+. |

#### Mẫu Payload: Bỏ phiếu & Reveal trên Version Arena

```json
// POST /api/v1/arena/matches/77a1.../vote — Request
{
  "outcome": "slot_a",
  "subscores": { "fun": "slot_a", "controls": "slot_a", "visuals": "tie", "performance": "slot_a" },
  "feedbackNote": "Bản A điều khiển nhảy nhạy hơn hẳn, boss màn 3 rất cuốn."
}

// 200 OK — Response (chỉ tiết lộ danh tính sau khi phiếu đã khóa bất biến)
{
  "data": {
    "matchId": "77a1...",
    "reveal": {
      "slotA": { "versionNumber": 4, "semanticLabel": "v0.4.0", "btElo": 1342, "eloDelta": 9 },
      "slotB": { "versionNumber": 2, "semanticLabel": "v0.2.1", "btElo": 1248, "eloDelta": -9 }
    },
    "reward": { "sparkEarned": 45, "energySpent": 10, "consensusBonusPending": true }
  }
}
```

---

### 2.5. Notcoin Community Loop, PoP Score & Anti-Bot (`M07`)

| Method | Endpoint | Auth | Rate Limit | Mô tả chức năng |
|---|---|---|---|---|
| `GET` | `/api/v1/altcha/challenge` | Public | 60/m | Cấp bài toán Proof-of-Work SHA-256 tự host (`altcha`) bảo vệ tạo phiên chơi, Arena & claim. |
| `GET` | `/api/v1/pop/status` | User | 60/m | Điểm `popScore`, `tier`, hạn mức mua Priority Window tương ứng, `energyCurrent`, `streakDays`, lịch sử `spark_ledger`. |
| `GET` | `/api/v1/quests` | User | 60/m | Danh sách nhiệm vụ khám phá version mới (Explore-to-Earn kiểu Notcoin) & trạng thái hoàn thành. |
| `POST` | `/api/v1/quests/{questId}/claim` | User | 20/m | Kiểm tra điều kiện server-side và cộng `SPARK` vào sổ cái. |
| `GET` / `POST` | `/api/v1/squads` | Public/User | 60/m / 2/d | Xem bảng xếp hạng Squad tuần hoặc tạo Squad mới. |
| `POST` | `/api/v1/squads/{slug}/join` | User | 5/d | Tham gia/chuyển Squad (cooldown 24h chống nhảy bang hội farm giải). |

---

### 2.6. Solana Version Launchpad, Attestations & Transparency Feed (`M08`)

| Method | Endpoint | Auth | Rate Limit | Mô tả chức năng |
|---|---|---|---|---|
| `GET` | `/api/v1/launchpad` | Public | 120/m | Danh sách các dự án đang trên Version-Gated Bonding Curve (`filter=priority_live\|m1\|m2\|m3\|near_grad\|graduated\|stalled`). |
| `GET` | `/api/v1/launchpad/{slug}` | Public | 120/m | Trạng thái curve, tiến độ tranche hiện tại, danh sách `version_milestones` (kèm `build_sha256` & `evidence_bundle_sha256`), đồng hồ Priority Window & Stall Deadline. |
| `GET` | `/api/v1/launchpad/{slug}/candles` | Public | 120/m | Dữ liệu OHLCV (`1m`, `5m`, `15m`, `1h`, `1d`) + mảng cờ mốc version `milestoneMarkers` cho `lightweight-charts`. |
| `GET` | `/api/v1/launchpad/{slug}/trades` | Public | 120/m | Lịch sử giao dịch công khai real-time (phân biệt rõ `buy_priority`, `buy_public`, `sell`, `ragequit` & phí phạt đã thu). |
| `GET` | `/api/v1/launchpad/{slug}/stream` | Public | 20/m | **SSE Stream** đẩy giao dịch mới, giá khớp và sự kiện mở khóa mốc version theo thời gian thực. |
| `GET` | `/api/v1/launchpad/{slug}/holders` | Public | 120/m | Top Holders kèm nhãn minh bạch (`Bonding Curve`, `Community Vault`, `Dev Vesting`, `Creator`, `Verified Gamer`, `Cluster Warning`). |
| `GET` | `/api/v1/launchpad/{slug}/sell-quote` | Public | 60/m | Ước tính minh bạch số SOL nhận về, `weightedHoldAge`, tỷ lệ `earlyExitFeeBps` (12%/6%/3%/1%) và phân bổ phí trước khi ký ví. |
| `POST` | `/api/v1/launchpad/{slug}/pop-attestation` | User (SIWS) | 10/m | Kiểm tra PoP Tier + thời lượng chơi game ≥ 5 phút + `sybil_risk_score < 0.5`, trả về chữ ký Ed25519 ngắn hạn (`120s`) để ví người chơi gọi `buy_priority` trên Solana. |
| `POST` | `/api/v1/developer/games/{gameId}/milestones/{level}/attestation` | Owner | 5/h | Kiểm tra toàn bộ điều kiện mốc `M1..M5+` (Fit Test + Arena + Build Diff + Curator HITL), đóng gói bằng chứng lên R2/Arweave, trả chữ ký Ed25519 của Oracle để mở khóa tranche on-chain. |
| `GET` | `/api/v1/rewards/claims` | User (SIWS) | 60/m | Lấy danh sách phân bổ token (stream 21 ngày) & SOL từ phí phạt Early-Exit kèm `merkleProof` để người chơi claim trực tiếp từ `game9k-rewards`. |
| `POST` | `/api/v1/internal/solana/webhook` | HMAC | 1000/m | Nhận sự kiện giao dịch từ Helius/Indexer để cập nhật read-projection theo slot. |

---

### 2.7. Curator & Admin Operations (`M09`)

| Method | Endpoint | Auth | Rate Limit | Mô tả chức năng |
|---|---|---|---|---|
| `POST` | `/api/v1/admin/developers/{userId}/decision` | `admin` | 30/m | Duyệt/từ chối hồ sơ Developer + ghi `audit_logs`. |
| `POST` | `/api/v1/admin/versions/{versionId}/review` | `curator`/`admin` | 30/m | Ký duyệt HITL cho Final QA / nâng mốc M1, M3, M4 hoặc từ chối kèm lý do + ghi `audit_logs`. |
| `POST` | `/api/v1/admin/versions/{versionId}/suspend` | `admin` | 30/m | Khóa khẩn cấp bản build vi phạm, thu hồi preview/play tại Edge Worker + ghi `audit_logs`. |
| `GET` | `/api/v1/admin/audit-logs` | `admin` | 60/m | Truy vấn nhật ký kiểm toán theo `actor`, `resource`, `action`, `correlationId`. |
| `GET` / `POST` | `/api/v1/admin/jobs/{jobId}/retry` | `admin` | 30/m | Giám sát và chạy lại các `processing_jobs` bị rơi vào `dead_letter`. |

---

## 3. Hợp đồng `@game9k/game-sdk` (Tương thích 1:1 với Poki SDK)

Để mọi developer từng làm game cho Poki (Godot, Unity WebGL, Phaser, Construct, GDevelop, Three.js) có thể port game sang Game9K trong **dưới 10 phút**, SDK giữ nguyên tên hàm chuẩn của Poki và giao tiếp an toàn từ iframe cô lập lên Portal qua `window.parent.postMessage`:

```ts
// Interface công khai trong iframe game: window.Game9KSDK (có sẵn adapter tương thích PokiSDK)
export interface Game9KSDK {
  init(): Promise<{ environment: 'inspector' | 'preview' | 'play' | 'arena'; versionLabel?: string }>;

  // 5 sự kiện vòng đời chuẩn Poki (developers.poki.com/guide/sdk-overview)
  gameLoadingFinished(): void;
  gameplayStart(): void;
  gameplayStop(): void;
  commercialBreak(onStart?: () => void): Promise<void>;
  rewardedBreak(options?: { size?: 'small' | 'medium' | 'large'; onStart?: () => void }): Promise<boolean>;

  // Tiện ích mở rộng cho Game9K (Cloud Save AUDS & Version Quest milestones)
  cloudSave: {
    get<T = unknown>(slot?: string): Promise<T | null>;
    set<T = unknown>(value: T, slot?: string): Promise<void>;
  };
  reportProgress(milestoneKey: string, numericValue?: number): void; // Phục vụ nhiệm vụ version (không tự cấp token!)
}
```

**Quy tắc bảo mật `postMessage` bắt buộc:**
1. Portal chỉ chấp nhận bản tin khi `event.source === gameIframe.contentWindow` **VÀ** `event.origin === expectedVersionOrigin` (khớp chính xác `https://<versionId>.play.game9k-cdn.net`).
2. SDK bên trong iframe tự động đo tổng hợp *chỉ số thống kê ẩn danh* (`input_event_count`, khoảng cách thời gian giữa các lần nhấn để tính Shannon entropy, `requestAnimationFrame` FPS, `window.onerror`) — **tuyệt đối không đọc hay gửi nội dung phím gõ văn bản, clipboard, cookie hay storage ngoài phạm vi game**.
3. Trong chế độ **Arena Blind Duel**, hàm `init()` **không trả về `versionLabel`** để game không thể tự tiết lộ mình là bản cũ hay bản mới nhằm thao túng người chấm.

---

## 4. Bảng Mã Lỗi Tiêu chuẩn (Standard Error Catalog)

| HTTP | Error Code | Ý nghĩa & Xử lý ở Client |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Dữ liệu đầu vào sai schema Zod; hiển thị theo `fieldErrors`. |
| `401` | `UNAUTHENTICATED` | Chưa đăng nhập hoặc phiên hết hạn. |
| `403` | `FORBIDDEN_ROLE` / `NOT_RESOURCE_OWNER` | Không đủ vai trò (`developer`/`curator`/`admin`) hoặc truy cập tài nguyên người khác. |
| `403` | `ALTCHA_VERIFICATION_FAILED` | Thiếu hoặc sai lời giải Proof-of-Work chống bot. |
| `403` | `POP_REQUIREMENT_NOT_MET` | Chưa đủ PoP Tier, chưa chơi đủ 5 phút hoặc `sybil_risk_score` vượt ngưỡng cho Priority Window. |
| `409` | `SLUG_CONFLICT` | Trùng slug game/studio; kèm gợi ý `suggestedSlug`. |
| `409` | `INVALID_STATE_TRANSITION` | Chuyển trạng thái version/upload/milestone trái với state machine. |
| `409` | `INSUFFICIENT_BUILD_DELTA` | Bản build mới quá giống bản trước, không đủ điều kiện xin mở khóa mốc token. |
| `409` | `INSUFFICIENT_VERIFIED_GAMEPLAY` | Chưa chơi đủ 90 giây mỗi bản trong Arena Blind Duel. |
| `410` | `UPLOAD_SESSION_EXPIRED` / `PREVIEW_REVOKED` | Hết hạn 15 phút upload hoặc preview token đã bị thu hồi; yêu cầu tạo mới. |
| `413` | `PAYLOAD_TOO_LARGE` | Vượt 50 MB file ZIP hoặc 128 KB Cloud Save. |
| `429` | `RATE_LIMIT_EXCEEDED` / `ENERGY_DEPLETED` | Vượt giới hạn gọi API hoặc hết Energy tích `SPARK`; kèm `Retry-After`. |
