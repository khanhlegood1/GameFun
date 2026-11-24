# ADR-0033 — Play SDK + Xsolla sandbox: giống **tên** Poki, không giả vờ là Poki

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`portal/lib/play-sdk.mjs`](../../portal/lib/play-sdk.mjs) · [`portal/lib/xsolla.mjs`](../../portal/lib/xsolla.mjs) · [`portal/public/play.html`](../../portal/public/play.html) · [`portal/server.mjs`](../../portal/server.mjs) · [`vercel.json`](../../vercel.json) · [ADR-0027](ADR-0027-starter-kit-game-mau-dua-khung-long.md) · [ADR-0032](ADR-0032-nhung-game-ngoai-vao-playground.md) · [ADR-0003](ADR-0003-non-custodial.md) · [ADR-0011](ADR-0011-legal-posture.md)

---

## 0. Trả lời ngắn

| | |
|---|---|
| Yêu cầu | "Áp Xsolla SDK vào dự án theo Poki portal SDK" |
| Đo được gì về Xsolla | **Không có SDK JavaScript cho web game.** SDK 3 là native (iOS/Android/Unity/Windows). Đường web duy nhất là **Pay Station**: server tạo token → mở payment UI |
| Làm gì | (1) Play SDK cho game chạy trong portal, tên hàm giống tập con Poki; (2) đường Pay Station **sandbox** đầy đủ: tạo token, webhook có chữ ký, máy trạng thái đơn |
| Có bán gì không | ❌ **Không.** `XSOLLA_ENV=live` bị từ chối ở cả ba tầng. REQ-M5-009 (Must) cấm fiat ở giai đoạn 1 |
| Có phải SDK Poki không | ❌ **Không.** Giống **tên** 5 hàm. Chưa qua Inspector, không có quảng cáo, không có `measure()` |
| Phần thưởng | **Phút chơi đã xác thực** (quyết định của PO) — không token, không tiền |
| Cái giá | Thêm một bảng trạng thái nữa phải giữ đúng; và "phút đã xác thực" hiện **chưa** đủ mạnh để chống bot (xem §6) |

---

## 1. Đo trước khi làm — ba phát hiện đổi hẳn thiết kế

| Đo | Nguồn | Hệ quả |
|---|---|---|
| Xsolla SDK 3 = **native**, không có SDK JS cho web | `developers.xsolla.com/sdk` (2026-11-18) | "Áp SDK" nghĩa là **Pay Station**: 1 lời gọi máy chủ + 1 khung thanh toán |
| Pay Station = `POST /merchants/{id}/token` → `secure.xsolla.com/paystation4/?token=…` | `developers.xsolla.com/api/pay-station` | API key **chỉ** ở máy chủ. Token là bearer của đơn ⇒ không lưu, không log |
| Webhook ký bằng `SHA1(thân thô + project secret)`, header `Authorization: Signature …` | tài liệu Pay Station | Phải đọc **thân thô**; parse rồi stringify lại là hash khác ⇒ mọi webhook hợp lệ bị từ chối |

Và một va chạm **nội bộ** quan trọng hơn cả ba điều trên:

> `REQ-M5-009` (Must): "Không cho phép mua bằng thẻ/fiat trong giai đoạn 1 (tránh tranh chấp
> chargeback + quy định)."

Xsolla Pay Station **chính là** thẻ và fiat. Vậy yêu cầu "áp Xsolla" đụng trực tiếp một yêu cầu
Must đã có. ADR này **không** tự sửa REQ-M5-009 — nó dựng đường nối ở chế độ sandbox và để
quyết định đảo lập trường cho PO (§7).

---

## 2. Quyết định 1 — Play SDK giống *tên*, không giả vờ *tương thích*

### 2.1 Vì sao giống tên

`PRD §M3` (REQ-M3-002) đã chốt: "SDK JS expose **tập con Poki API**". Giống tên giúp studio
port game sang Poki (hoặc ngược lại) không phải viết lại chỗ gọi. Đó là **giảm chi phí port**,
không phải tuyên bố tương thích.

Năm hàm: `gameLoadingFinished`, `gameplayStart`, `gameplayStop`, `commercialBreak`,
`rewardedBreak`.

### 2.2 Vì sao KHÔNG được nói "tương thích Poki"

| Poki Inspector kiểm | Ta có |
|---|---|
| Quảng cáo hiện đúng lúc (không giữa lượt chơi) | ❌ Chưa có ad mediation (REQ-M3-004) |
| Tắt tiếng khi quảng cáo | ❌ Không có quảng cáo nên không có gì để tắt |
| Không cuộn trang, khoá phím khi quảng cáo | ⚠️ Có trong gói ZIP (`poki-sdk.mjs`), **không** trong SDK runtime |
| `measure()` | ❌ Không có |

Vì vậy mọi chỗ nói về SDK này đều kèm câu "**không phải SDK Poki, chưa qua Inspector**" —
`/api/play/sdk` trả mảng `not_claimed`, và UI in ra. Một SDK tự nhận tương thích mà trượt
Inspector là lời khai sai với studio, và họ sẽ phát hiện ở vòng nộp đầu tiên.

### 2.3 Trang chơi riêng, không nhúng vào tab Playground

PO chọn `/play/:game` (mô hình cổng game thật). Ba lý do kỹ thuật, không phải thẩm mỹ:

1. **Cô lập lỗi.** SDK chết không kéo theo bảng issue, cổng chất lượng, tài liệu.
2. **Vòng đời rõ.** Trang này có đúng ba việc: dựng iframe, bắt tay nonce, đếm phút.
3. **CSP nới đúng một chỗ.** `frame-src` có thêm `secure.xsolla.com`; portal không cần.

---

## 3. Quyết định 2 — phút chơi do **máy chủ** đếm

### 3.1 Nhận DELTA, không nhận tổng

Client gửi `deltaMs` của 5 giây vừa qua. Nếu nhận **tổng**, client tự khai "tôi đã chơi 10
tiếng" và máy chủ không có cách nào biết. Ba hàng rào, mỗi cái chặn một kịch bản khác:

| Hàng rào | Chặn gì | Nơi |
|---|---|---|
| `deltaMs` ≤ 600 000 | một request tự cấp 10 năm phút | `store.mjs` |
| delta âm ⇒ 0 | tự trừ ngược để "làm lại" | `store.mjs` |
| trần phút/ngày 240 | tab mở 24 giờ | `store.mjs` + `play-sdk.mjs` |

### 3.2 Không tính khi tab ẩn hoặc không tương tác

`document.hidden` ⇒ `stop()` ngay (REQ-M3-006). Và `dt > 60000` bị **bỏ**: máy bị sleep rồi
thức dậy cho `dt` hàng giờ, và tin nó là một lần gập máy được cộng hàng trăm phút.

### 3.3 Fail-open: máy chủ chết thì game vẫn chơi

Không có `await` nào chặn khung hình đầu. Mọi lời gọi đều `.catch`, và thời gian chưa gửi được
**giữ lại** (tối đa 2 phút) — mất mạng không được biến thành mất phút. Khi lỗi ≥ 3 lần, UI
hiện badge "mất kết nối — phút chơi đang chờ". Im lặng ở đây là lừa người chơi.

---

## 4. Quyết định 3 — Xsolla: sandbox, và **không** đường nào bật live

### 4.1 Ba tầng từ chối

```
XSOLLA_ENV=live            → xsollaConfig() trả live_not_allowed (tầng lõi)
                           → route trả 403 fiat_blocked      (tầng HTTP)
                           → test khẳng định cả hai           (tầng CI)
```

Không có biến môi trường nào một mình bật được fiat. Đảo lập trường REQ-M5-009 phải là
**một ADR**, không phải một lần đặt nhầm env.

### 4.2 Thiếu cấu hình vẫn đi hết đường UI — nhưng nói thật

Không có merchant id: route tạo đơn ở trạng thái `created`, trả `simulated: true`,
`pay_url: null`, và câu "Đơn này **KHÔNG** được gửi sang Xsolla; không có giao dịch nào".
Làm vậy để test chạy được trong CI không cần bí mật — nhưng **không** trả một `pay_url` giả,
vì người dùng sẽ bấm vào trang lỗi của Xsolla và tưởng portal hỏng.

### 4.3 Webhook là **nguồn duy nhất** đổi trạng thái đơn

```
không có XSOLLA_PROJECT_SECRET  → 501  (không phải 200: không kiểm được thì không nhận)
chữ ký sai                       → 401  (và trạng thái đơn KHÔNG đổi)
chữ ký đúng, đơn lạ              → 404
chữ ký đúng, trạng thái lạ       → 200 + changed:false + reason
chữ ký đúng, paid lần đầu        → 200 + granted:true     ← cấp vật phẩm
chữ ký đúng, paid lần hai        → 200 + changed:false    ← KHÔNG cấp lại
```

Dòng cuối là dòng quan trọng nhất: **Xsolla có gửi lại webhook**. Không có cờ idempotent thì
người chơi nhận vật phẩm mỗi lần họ gửi lại.

---

## 5. Những gì đã kiểm, và kiểm ngược

Cổng mới: `portal/test/play-sdk.test.mjs` (35), `portal/test/play-routes.test.mjs` (32),
`scripts/check_play_ui.mjs` (18). Mỗi phép kiểm ngược **phải** làm cổng đỏ; phép nào không
làm đỏ nghĩa là assertion đang đo sai thứ.

| Phá gì | Kết quả |
|---|---|
| Cho `live` vào `ALLOWED_ENVS` | 2 đỏ (lõi) |
| Webhook bỏ kiểm chữ ký | 1 đỏ |
| Webhook luôn `grant` | 1 đỏ |
| Bỏ cắt `deltaMs` | 1 đỏ (route) |
| `/play` nhận cả game khung | 1 đỏ |
| Bỏ `secure.xsolla.com` khỏi CSP runtime | 1 đỏ — **thêm sau khi phát hiện cổng mù** |
| Bỏ origin Xsolla khỏi `vercel.json` | 1 đỏ |
| Bỏ rewrite `/play` | 1 đỏ |
| SDK xoá `pendingMs` khi mất mạng | 1 đỏ — **sau khi sửa một assertion đo sai** |
| Bỏ kiểm `ev.source` | 1 đỏ — **sau khi sửa một assertion đo sai** |

### 5.0 Lỗi CHỈ xảy ra trên production — và đã lọt qua mọi cổng local

Bản đầu đặt ba tệp của trang chơi ở **gốc**: `/play.js`, `/play.css`,
`/play-sdk.js`, kèm route `GET /play.js` trong `server.mjs`.

- Local: 18/18 phép kiểm DOM xanh, 32 test route xanh, máy chủ trả 200 cho cả ba.
- Production: `vercel.json` **chỉ** rewrite `/assets/:path*` vào function. Ba tệp
  ở gốc không khớp rewrite nào ⇒ **404**. Trang vẫn 200, chỉ là **không có JS** —
  trắng câm, và không log nào nói tại sao.

Đây là loại lỗi tệ nhất trong cả loạt: mọi cổng local đều xanh, vì local và
production phục vụ tệp tĩnh bằng **hai cơ chế khác nhau**.

Nay: mọi tệp ở `/assets/`, và có ba cổng giữ đúng —
(1) mọi `src`/`href` trong `play.html` phải khớp một rewrite của `vercel.json`,
(2) mọi `import` trong `play.js` cũng vậy, (3) không tệp trang chơi nào được
thêm vào danh sách phục vụ ở gốc.

Viết cổng này cũng sai hai lần, cùng một chỗ: escape regex ăn luôn dấu `*` của
`:path*`. Vì vậy có thêm một phép kiểm **chính bộ khớp** bằng ví dụ biết trước —
nếu bộ khớp hỏng, hai phép kiểm kia sẽ xanh/đỏ vì lý do sai.

### 5.0b Lỗi THỨ HAI, cùng một nguyên nhân gốc: `cleanUrls`

Sửa xong `/assets/` thì production vẫn hỏng — lần này khung game hiện
**"Không tìm thấy"** ở giữa, còn khung ngoài vẫn chạy.

`vercel.json` bật `cleanUrls: true`, nghĩa là Vercel **308-redirect mọi đường
`.html`** sang bản không đuôi. Iframe trỏ `/assets/games/dino-race.html` ⇒
Vercel đổi thành `/assets/games/dino-race` ⇒ rơi vào bộ định tuyến ⇒ 404.

Vì sao tìm ra: `play.js`, `play.css`, `play-sdk.js`, `dossier.css` — tất cả
200. Chỉ **hai tệp `.html`** hỏng. Đúng mẫu đó chỉ có một lời giải thích.

**Bài học chung của §5.0 và §5.0b:** cả hai đều là *local và production phục vụ
tệp tĩnh bằng hai cơ chế khác nhau*, nên cổng local **không thể** nhìn thấy.
Cách duy nhất kiểm được là **kiểm cấu hình** (`vercel.json`) thay vì kiểm hành
vi, và **kiểm trên production thật** thay vì chỉ CI.

Đã sửa: bỏ `cleanUrls`; route `/assets/games/:file` phục vụ cả tên có đuôi lẫn
không đuôi (để đường dẫn cũ không chết nếu ai bật lại); thêm 3 phép kiểm đọc
`vercel.json` và đỏ khi `cleanUrls`/`trailingSlash` bị bật lại.

### 5.1 Hai assertion đầu tiên của tôi là test rỗng

Ghi lại vì đây là loại lỗi tệ nhất trong bộ test:

1. **Đo `pendingMs` sau `stop()`.** `stop()` gọi `tick()` nên luôn để lại vài ms ⇒
   `pendingMs > 0` đúng **kể cả khi SDK đã xoá sạch**. Phép kiểm ngược phát hiện; nay đo ngay
   sau `flush()`, trước `stop()`, và đòi ≥ 60 000 ms.
2. **Kiểm nguồn bằng `race:ready` thiếu nonce.** Bị từ chối vì **nonce**, không phải vì nguồn
   ⇒ bỏ hẳn kiểm `ev.source` mà test vẫn xanh. Nay dùng `game9k:run-start` (không có nonce),
   và thêm phép kiểm **ngược lại**: từ nguồn đúng thì phải bật.

---

## 6. Điều ADR này **KHÔNG** làm được — nói trước

| Giới hạn | Vì sao | Cần gì để hết |
|---|---|---|
| "Phút đã xác thực" **chưa** chống bot | Client gửi delta; hàng rào hiện chỉ là trần và đồng hồ | Risk Engine REQ-M3-005 (`impossible_input`, `headless`, `background_tab`) + chữ ký session key |
| Telemetry 30 s có chữ ký **chưa có** | REQ-M3-003 chưa làm | `/api/play/sdk` khai `telemetry.status = 'partial'` để không ai tưởng đã có |
| Không có quảng cáo nào | REQ-M3-004 chưa làm | Ad mediation + floor price theo region |
| Không kiểm được iframe Xsolla hiển thị đúng | jsdom không tải nổi iframe khác origin | Chỉ trình duyệt thật mới trả lời được |
| Chưa test với Xsolla thật | Sandbox credentials chưa có trong CI | Chạy một giao dịch sandbox thật, ghi lại mã đơn |

---

## 7. Câu hỏi cho PO (không tự trả lời)

- **Q-ADR33-a:** REQ-M5-009 cấm fiat ở giai đoạn 1. Có mở cho **vật phẩm cosmetic giá trị nhỏ**
  (không phải tài sản, không quy đổi) không? Nếu có, cần một ADR sửa REQ-M5-009 + ý kiến pháp lý
  về hoàn tiền/thuế.
- **Q-ADR33-b:** Trần **240 phút/ngày** và **60 phút/lượt** có đúng ý không? Con số này sẽ thành
  tham số trong `params.toml` nếu được chốt, để CI kiểm thay vì để trong mã.
- **Q-ADR33-c:** "Phút đã xác thực" có được dùng làm **play gate** cho mua bond (REQ-M5-004,
  10 phút trong 24h đầu) không? Nếu có, ngưỡng chống bot ở §6 phải xong **trước**.
- **Q-ADR33-d:** Khung 1–5 theo XP là trang trí hay có giá trị? Nếu có giá trị, nó cần một
  nguồn phát hành (season) chứ không phải một hàm trong `play-sdk.mjs`.

---

## 8. Liên quan

- [ADR-0027](ADR-0027-starter-kit-game-mau-dua-khung-long.md) — game mẫu, handshake nonce
- [ADR-0032](ADR-0032-nhung-game-ngoai-vao-playground.md) — nhúng game ngoài (khác origin ⇒ không nonce)
- [ADR-0003](ADR-0003-non-custodial.md) — server không giữ khoá; ở đây: server không nhận tiền
- [ADR-0011](ADR-0011-legal-posture.md) — lập trường pháp lý mà REQ-M5-009 bảo vệ
- `docs/01-requirements/PRD-game9k.md` §M3 (SDK, telemetry) · §M5 REQ-M5-009 (cấm fiat)

---

## Ranh giới trung thực

- **Đã kiểm:** `adapter.test.mjs` kiểm CSP `frame-src` có đúng **một** origin Xsolla
  (`https://secure.xsolla.com`), và `PAYSTATION_ORIGIN` trong `lib/xsolla.mjs` khớp hằng số đó.
- **Chưa kiểm:** **chưa có giao dịch Xsolla thật nào chạy.** Sandbox không có khoá sandbox của
  Xsolla, nên toàn bộ hiểu biết về luồng thanh toán đến từ **tài liệu**, không từ một response thật.
- **Chưa chạy:** luồng hoàn tiền / chargeback. `REQ-M5-009` cấm fiat giai đoạn 1, nên đây là
  **sandbox để học**, chưa phải đường thu tiền.
- **Không** mô tả tính năng này là "đã thanh toán được". Nó là **khung nhúng đúng chỗ**, chưa nối.

## Điều ADR này **KHÔNG** bao gồm

| Không bao gồm | Vì sao | Ai quyết |
|---|---|---|
| Bật thanh toán thật ở giai đoạn 1 | `REQ-M5-009` cấm thẻ/fiat (chargeback + quy định) | PO |
| Webhook xác nhận thanh toán | Chưa có endpoint; cần chữ ký Xsolla | — |
| Đối soát (reconciliation) | Thuộc `docs/04-data`, không phải SDK | — |
