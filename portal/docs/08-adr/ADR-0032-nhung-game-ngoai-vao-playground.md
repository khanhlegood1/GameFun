# ADR-0032 — Nhúng game **ngoài** vào Playground: học từ xa, không chép một dòng

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`portal/public/app.js`](../../portal/public/app.js) · [`vercel.json`](../../vercel.json) · [`ADR-0027`](ADR-0027-starter-kit-game-mau-dua-khung-long.md) · [`ADR-0031`](ADR-0031-portal-hien-thi-cau-hoi-mo.md) · [`adapter.test.mjs`](../../portal/test/adapter.test.mjs)

---

## 0. Trả lời ngắn

| | |
|---|---|
| Yêu cầu | Gắn `https://game9k-starter-kit-black.vercel.app/` vào Playground cho chơi test được thật |
| Cách làm | Thêm **game thứ 2** cạnh bản nội bộ, nhúng qua `<iframe>` trỏ sang project Vercel kia |
| Có chép mã không | ❌ **Không một dòng.** Chỉ một URL. Bản quyền của họ vẫn của họ |
| Có handshake nonce không | ❌ Không — và **không nên có**. Xem §2.2 |
| Có nối TikTok/YouTube thật không | ❌ Không. Chạy `?demo=1` với người xem **giả**. UI nói thẳng điều đó |
| Cái giá phải trả | Portal giờ phụ thuộc một origin **không do mình kiểm soát** — có thể trắng bất cứ lúc nào |

---

## 1. Đo được gì trước khi làm

| Sự kiện | Bằng chứng |
|---|---|
| Project tồn tại, `READY`/`PROMOTED`, alias đúng | `prj_qfSXx9LjYKUFR31aiC4rlPMBNvUU` · `dpl_FhBQWNukpceexabQSSJF4M5QA9bS` |
| Repo nguồn **khác** MetaPump | `lexuankhanh1612/Game9K-Starter-Kit` (repoId `1467677334`), `private: false` |
| **Không có file LICENSE** | GitHub API: `license: null` |
| Project bật SSO | `ssoProtection: {deploymentType: "all_except_custom_domains"}` |
| Gốc `/` **bị SSO chặn** | fetch trả trang đăng nhập Vercel |
| Nhưng `/games/dino-race/index.html` **công khai** | fetch trả đúng nội dung game |
| Chạy demo được, không cần live | `?demo=1` ⇒ overlay tự sinh người xem + quà |
| Nó dùng `tiktok-live-connector` + `youtube-chat` + socket.io | đọc `README.md` của repo đó |

Hai dòng cuối là điểm cần nói rõ: **bản này không phải bản MetaPump tự viết.** Nó là một
project riêng, đầy đủ hơn ở phần kết nối live — đúng thứ `ADR-0027` cố ý không làm.

---

## 2. Quyết định

### 2.1 Thêm, không thay

Playground giữ **cả hai** dòng:

| Dòng | Là gì | Vì sao giữ |
|---|---|---|
| **Đua khủng long** | `portal/public/games/dino-race.html`, sinh từ `starter-kit/game.html` | **Tất định theo seed** ⇒ kiểm lại được. Có handshake nonce, có cổng test `game-boot.test.mjs` |
| **Dino Race LIVE** | iframe sang project ngoài, `?demo=1` | Cho thấy hướng "kết nối live thật" trông thế nào |

Thay bản nội bộ bằng bản ngoài là đánh đổi tồi: bản nội bộ là bản duy nhất **kiểm chứng
được** (cùng seed ⇒ cùng cuộc đua), và ta sở hữu mã của nó.

### 2.2 Không handshake nonce — và đây không phải thiếu sót

`openGameFrame()` (bản nội bộ) bắt tay nonce vì game nằm **cùng origin** với portal: script
khác trong trang cha đọc được `postMessage` nếu không tách phiên.

Bản ngoài **khác origin**. Trình duyệt đã cô lập nó bằng same-origin policy: nó không đọc
được DOM, cookie, hay `localStorage` của portal. Thêm nonce vào đây sẽ là **bảo mật giả** —
một nghi thức trông giống bảo vệ nhưng không bảo vệ thêm gì. Thà nói rõ là không có.

### 2.3 `sandbox="allow-scripts"` — cố ý **không** có `allow-same-origin`

Có `allow-same-origin` thì iframe được đối xử như cùng origin và **chạm được cookie portal**
(`mp_session` là HttpOnly nên không đọc trực tiếp, nhưng vẫn gửi kèm request). Không có nó,
tài liệu thành origin "opaque" — cô lập kể cả sau này khi project kia đổi cấu hình.

Đánh đổi đã biết: `allow-scripts` **không** kèm `allow-same-origin` cũng chặn luôn
`localStorage` bên trong iframe. Đọc mã của họ: `game.js`, `bridge.js`, `index.html` **không**
dùng `localStorage` hay `sessionStorage` (grep 0 kết quả). Nên ràng buộc này hiện **không**
làm hỏng gì. Nếu họ thêm tính năng cần lưu trữ, khung sẽ hỏng — và đó là lúc phải mở lại
quyết định này, không phải lúc lặng lẽ thêm `allow-same-origin`.

### 2.4 CSP phải khai origin, ở **hai** nơi

`frame-src 'self'` từ chối mọi origin khác. Đã thêm
`https://game9k-starter-kit-black.vercel.app` vào **cả**:

- `vercel.json` — header Vercel gắn ở production;
- `portal/server.mjs` — header server tự set ở local/test.

Sửa một nơi mà quên nơi kia là lỗi **chỉ lộ sau khi deploy** — đúng loại lỗi `bundle.test.mjs`
(ADR-0031) sinh ra để bắt. Ở đây `adapter.test.mjs` kiểm cả hai, và có reverse-test:
bỏ origin ở `vercel.json` ⇒ đỏ; bỏ ở `server.mjs` ⇒ đỏ; **thay** `'self'` thay vì **thêm**
⇒ cũng đỏ (vì làm vậy khung xem PDF hỏng theo).

---

## 3. Điều portal **không** kiểm được, và nói thẳng

Trang cha **không đọc được** nội dung iframe khác origin — đó chính là lý do nó an toàn.
Hệ quả: sự kiện `load` **vẫn bắn** khi bên trong là trang 404 hay trang đăng nhập Vercel.

Vì vậy trạng thái trong drawer nói đúng thứ biết được:

> *"đã nạp iframe từ `<origin>` — trình duyệt không cho portal đọc bên trong"*

chứ **không** nói "chạy thành công". Kèm link **mở tab mới** để người dùng tự kiểm.

---

## 4. Hệ quả

**Được:** người xem thấy được hướng "kết nối live thật" ngay trong portal, mà không phải
vendor `tiktok-live-connector` hay chép mã không licence.

**Mất / phải chịu:**

- Portal phụ thuộc một origin **không do mình kiểm soát**. Project kia bật SSO cho
  `/games/**`, xoá project, hoặc hết hạn deployment ⇒ khung trắng. Portal **không** hỏng,
  nhưng một dòng trong Playground sẽ vô dụng cho tới khi có người sửa URL.
- Repo nguồn **không có LICENSE**. Ta chỉ nhúng URL nên luật *"chỉ học ý tưởng, viết lại
  từ đầu"* không bị đụng — nhưng nếu sau này ai muốn **chép** mã từ đó vào MetaPump thì
  câu trả lời là **không**, cho tới khi có giấy phép rõ ràng.
- Thêm một origin vào CSP là nới bề mặt tấn công: nếu origin đó bị chiếm, nó vẫn bị
  `sandbox` chặn, nhưng nó **hiện được nội dung tuỳ ý** trong portal. Đây là lý do danh
  sách cho phép phải ngắn và có người ký.

**Chưa làm, và biết là chưa làm:**

- Chưa nối TikTok Live / YouTube Live thật — bản ngoài chạy `?demo=1`.
- Chưa kiểm trong **trình duyệt thật**. jsdom không có mạng ra origin ngoài, nên cổng test
  chỉ kiểm được `src`, `sandbox`, và phần công bố — **không** kiểm iframe có vẽ ra game không.
  Việc này phải làm bằng mắt trên production.
- Chưa có cơ chế phát hiện "origin ngoài đã chết". Hiện chỉ có nút *Nạp lại* và link ngoài.

---

## 5. Việc PO phải quyết

| | Câu hỏi |
|---|---|
| **Q-ADR32-a** | Có chấp nhận để portal phụ thuộc một origin **bên ngoài** repo này không? Nếu không, phương án thay thế là **bỏ dòng game ngoài** và chỉ giữ link văn bản. |
| **Q-ADR32-b** | Repo `Game9K-Starter-Kit` **không có LICENSE**. Có cần thêm giấy phép cho nó trước khi quảng bá nó trong sản phẩm không? (Nhúng URL thì không vi phạm, nhưng đây là chuyện chính sách, không phải kỹ thuật.) |
| **Q-ADR32-c** | Khi nào nối **live thật** (TikTok/YouTube)? Việc đó cần gateway chạy thường trực, không làm được trên Vercel serverless — tức là cần hạ tầng riêng. |

---

## Ranh giới trung thực

- **Đã kiểm:** CSP `frame-src` cho đúng origin `game9k-starter-kit-black.vercel.app`; `adapter.test.mjs`
  kiểm khớp giữa `server.mjs` và `vercel.json`.
- **Chưa kiểm:** game ngoài có **thật sự** chạy trong iframe đó không. Sandbox không mở ra được
  origin bên ngoài, nên đây là suy luận từ CSP, không phải quan sát.
- **Chưa có:** cơ chế nonce cho game ngoài. `ADR-0027` §7 Q60 đóng nonce **chỉ** cho game cùng
  origin; game khác origin **không** có handshake.
- **Không** khẳng định "nhúng được" là "nhúng an toàn". Khác origin nghĩa là **không kiểm soát được**
  mã bên trong.

## Điều ADR này **KHÔNG** bao gồm

| Không bao gồm | Vì sao | Ai quyết |
|---|---|---|
| Nonce/handshake cho game khác origin | iframe khác origin không chia sẻ `postMessage` tin cậy | — |
| Ký duyệt nội dung game ngoài | Đó là `M8 Moderation`, không phải Playground | — |
| Tự lưu trữ (mirror) game ngoài | Bản quyền của studio; xem `ADR-0016` | Q-ADR32-b |
