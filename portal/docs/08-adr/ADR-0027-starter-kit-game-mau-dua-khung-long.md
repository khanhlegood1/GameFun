# ADR-0027 — Game mẫu đầu tiên của Starter Kit: đua khủng long **tất định**

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-22
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) · [`dua-vit-tiktok`](../12-decisions/2026-11-22-dua-vit-tiktok-va-phan-loai-game.md) · [`second-screen-race`](../12-decisions/2026-11-22-dua-vit-tiktok-va-phan-loai-game.md) · [`ADR-0016`](ADR-0016-license-compliance.md) · Q59–Q60

---

## 0. Trả lời ngắn — quyết định

| # | Quyết định |
|---|---|
| 1 | Game mẫu đầu tiên là **đua khủng long 4 làn**, nhưng **kết quả tính trước từ seed** — không realtime |
| 2 | Chỉ **học ý tưởng** từ 10 repo tham khảo; **không copy dòng code nào** |
| 3 | Bridge **trung lập**; TikTok và YouTube là hai adapter, game không biết nền tảng nào |
| 4 | Mã nguồn ở `starter-kit/`, tự chứa để `git subtree push` sang `Game9K-Starter-Kit` |

---

## 1. Vì sao "tất định" là quyết định pháp lý, không phải kỹ thuật

PO ban đầu chọn đua khủng long **tất định** sau khi được nêu ba lựa chọn. Ghi lại vì sao đây là
lựa chọn đúng, và nó cứu được gì.

`docs/12-decisions/2026-11-22-dua-vit-tiktok-va-phan-loai-game.md` §2 đã kết luận: dùng Realtime
đồng bộ vị trí đẩy game từ **G2 sang G1** theo NĐ 147/2024 — nhóm cấp phép nặng nhất.

Đua khủng long 4 làn với bứt tốc ngẫu nhiên **trông như** cần realtime. Nhưng nó không cần:

> Nếu kết quả được tính **trước** từ seed, thì mọi máy ra cùng một cuộc đua. Không cần đồng bộ.
> Không cần netcode. Không vào G1. Và người xem **tự kiểm được** bằng cách chạy lại seed.

⇒ Giữ được kịch tính của "lội ngược dòng" mà **không** đánh đổi nhóm cấp phép. Đây là điểm quan
trọng nhất của ADR này.

### 1.1. Nhưng phải nói rõ giới hạn

Tất định **không** làm game miễn nghĩa vụ. Khi nối vào cổng:

- Ghi điểm lên server ⇒ **G2**, không phải G4.
- NĐ 174/2026 bắt xác thực số điện thoại với **cả bốn nhóm**.

Xem cùng tài liệu §2.1–§2.2. Tất định chỉ tránh **G1**, không tránh phần còn lại.

---

## 2. Vì sao KHÔNG copy code — ba loại license, hai loại không dùng được

| Repo | License | Dùng được? |
|---|---|---|
| `jakesgordon/javascript-racer` | MIT | ✅ |
| `qafaraz/Horse-Race` | MIT | ✅ |
| `belumokasl-hub/juego-huevo-ancestral-tiktok-live` | MIT | ✅ |
| `zerodytrash/TikTok-Live-Connector` (và fork `khanhlx6`) | **AGPL-3.0** | ❌ |
| `vamnguyen/tiktok-live-games` | **không có LICENSE** | ❌ |
| `livecade/marble-race-tiktok-live-game` | **không có LICENSE** | ❌ |
| `khanhlx6/TikTok-Chat-Reader` | **không có LICENSE** | ❌ |

`ADR-0016` đã kết luận AGPL lây nhiễm với phần mềm phục vụ qua network. **"Không có LICENSE"
theo luật là giữ toàn bộ quyền** — không phải dùng tự do.

⇒ Một SDK phát hành cho studio bên thứ ba **không thể** chứa hai loại trên. Nên: học ý tưởng
(vòng đời 24/7, phân tầng quà, bứt tốc cuối), viết lại từ đầu.

### 2.1. Điều này làm mất gì, nói thẳng

`vamnguyen/tiktok-live-games` có **79 sao** — repo tốt nhất trong danh sách, và là repo **không
có license**. Ta mất phần đã được cộng đồng kiểm chứng của nó. Đó là cái giá của việc phát hành
được. Không có cách nào vừa dùng code không license vừa phát hành hợp pháp.

---

## 3. Vì sao bridge trung lập

PO chọn **cả TikTok và YouTube**. Hai nền tảng khác nhau ở mức không thể trộn:

| | TikTok | YouTube |
|---|---|---|
| API | **không chính thức** | **chính thức** |
| Rủi ro | đổi/hỏng bất kỳ lúc nào | ổn định, nhưng quota |
| Xác thực | không cần | OAuth 2.0 |
| Quota | — | 10.000 unit/ngày; `liveChatMessages.list` = 5 unit |

Nếu game đọc trực tiếp sự kiện nền tảng: TikTok đổi ⇒ sửa game. Thêm nền tảng thứ ba ⇒ sửa game.

⇒ Game chỉ đọc `NormalizedEvent`. Adapter chịu trách nhiệm dịch. Đây là điều cho phép thêm
nền tảng **không sửa game**.

---

## 4. Về yêu cầu "TikTok Live + YouTube Live" — phần chưa làm được

PO yêu cầu cả hai. Trạng thái thật:

| | Trạng thái |
|---|---|
| Adapter TikTok | ✅ viết, có test |
| Adapter YouTube | ✅ viết, có test |
| Nối TikTok **thật** | ❌ **chưa** — cần connector của host (license ở §2) |
| Nối YouTube **thật** | ❌ **chưa** — cần OAuth + quota |
| Chạy 24/7 trên YouTube | ⚠️ **polling 5 giây vượt quota 8×** — phải xin tăng hoặc dùng `streamList` |

> Bản mẫu **không** kết nối nền tảng nào. Nó có **cầu nối** đúng, và đó là thứ đáng có trước.
> Một bản mẫu tự nhận "đã nối TikTok" khi chưa nối là đúng loại lỗi mà `check_doc_refs.py` và
> `AGENTS.md` được viết để chặn.

---

## 5. Đánh giá bản HTML mà PO gửi kèm — đo lại, không tin mô tả

PO gửi `jurassic_sanctuary_sprint_..._game9k_edition.html` (78.197 B). Tài liệu đi kèm mô tả nó.
Đối chiếu:

| Tài liệu nói | Đo thật | |
|---|---|---|
| *"`< 55 KB`"* | **78.197 B** thô · **20.493 B gzip** | ⚠️ sai đơn vị — nhưng gzip **tốt hơn** con số nêu |
| *"`Game9KBridge`"* | **không tồn tại** — chỉ có `window.TikTokBridge` | ❌ |
| *"TikTok **và** YouTube Live"* | **0** chỗ nhắc YouTube | ❌ |
| *"nhận luồng sự kiện TikTok Live từ bên ngoài"* | **0** WebSocket — chỉ giả lập trên UI | ⚠️ đúng về `postMessage`, sai về "thu luồng" |

Phần **đáng giữ**: né `<video>` cho TikTok in-app browser (đúng), và **20,5 KB gzip** là con số
rất tốt cho một game như vậy.

---

## 6. Đã làm

| | |
|---|---|
| Lõi mô phỏng tất định | `starter-kit/src/engine/` — 14 bất biến |
| Ranh giới tin cậy | `starter-kit/src/bridge/` — 13 bất biến |
| Game chạy được | `starter-kit/game.html` — **31.603 B thô · 11.865 B gzip** (đo 2026-11-18) |
| Sinh tự động | `starter-kit/build.py` nhúng `rng.mjs` + `race.mjs` + `nonce.mjs`; `--check` trong CI |
| Test | **47/47 pass** — 14 lõi · 13 bridge · 13 nonce · 7 parity |
| Reverse-test | ✅ `Date.now()`/`Math.random()` ⇒ 4 đỏ · nonce ⇒ 6 + 1 đỏ · `surgeMultiplier` ⇒ 2 đỏ |
| Smoke test trong DOM | ✅ jsdom: tất định, ingest, `ads.break()` không treo, rank đủ |

---

## 7. Hai câu hỏi đã tự giải, và phần còn cần PO

### Q59 — đã đóng (2026-11-18)

Câu hỏi cũ: *sinh `game.html` bằng script, hay chấp nhận nợ "hai bản có thể trôi"?*

Trả lời: **sinh bằng script**, và **chứng minh bằng hai cổng độc lập**:

| Cổng | Kiểm gì | Reverse-test |
|---|---|---|
| `python3 starter-kit/build.py --check` | văn bản, byte-for-byte | tiêm `2.2 → 2.3` ⇒ exit 1 |
| `test/build-parity.test.mjs` (7 test) | **hành vi** — `simulate()` của bản nhúng vs `src/`, 20 seed + boost | cùng phép tiêm ⇒ 2 test đỏ |

Hai cổng không thay thế nhau: cổng văn bản bắt được sửa tay; cổng hành vi bắt được
trôi phát sinh do build sai thứ tự hoặc do `src/` đổi mà bản nhúng không đổi.

Một lần **suýt** cho kết quả giả: phép tiêm đầu tiên dùng chuỗi `const surge = cfg.surge ?? 0.9`
— chuỗi đó **không tồn tại** trong mã, nên phép tiêm là no-op và cả hai cổng xanh. Đã sửa
bằng cách thêm `assert s != before` vào chính script tiêm. Ghi lại vì đây đúng là cái bẫy
"script xanh ≠ bằng chứng".

### Q60 — đã đóng (2026-11-18)

Câu hỏi cũ: *`REQ-M3-001` yêu cầu postMessage có nonce. Thêm trước khi phát hành?*

Trả lời: **đã thêm, và đã nối vào `game.html`** (không chỉ nằm trong module rời):

- Cha sinh nonce (≥ 16, ≤ 128) → `bridge:hello` → game khoá phiên, echo trong `race:ready`.
- `hello` chỉ nhận **một lần** ⇒ chống chiếm phiên.
- Mọi lệnh sau **phải** kèm nonce đúng; sai thì `console.warn` và bỏ qua.
- **Breaking change** so với #147 — đã ghi ở `starter-kit/docs/01-tich-hop.md` §3.1.

Giới hạn còn lại, **không sửa được ở phía game**: nonce tách *phiên*, không tách *script*.
Một script khác cùng origin trong trang cha vẫn đọc được nonce. Chặn việc đó là bổn phận
của cổng (origin allowlist), không phải của iframe.

### Còn cần PO

| Mã | Câu hỏi |
|---|---|
| **Q51/Q52** | Giữ nguyên — xem `docs/12-decisions/` |
| **Q46** | Ngân sách gzip tổng của gói game? Hiện **11.865 B**, nhưng đó là game **rỗng** — chưa asset, chưa SDK |

---

## 8. Tự phê bình

1. **Tôi chưa push sang `Game9K-Starter-Kit`.** Đã kiểm: có quyền `admin: true`. Nhưng session này
   gắn với `MetaPump`, nên tôi dựng ở `starter-kit/` và để PO quyết cách chuyển.
2. **Chưa nối TikTok thật, chưa nối YouTube thật.** Cả hai đều là kế hoạch trong
   `starter-kit/docs/01-tich-hop.md`. Không có dòng nào đã chạy.
3. **Smoke test dùng jsdom, không phải trình duyệt thật.** jsdom có canvas giả nên chỉ chứng minh
   **logic** chạy, không chứng minh **render** đúng. Chưa test trong TikTok in-app browser, chưa
   test trong OBS.
4. **§5 là đánh giá của tôi về file của PO** — có thể tôi đọc sai ý định của tài liệu đi kèm.
   Tôi chỉ khẳng định những gì **grep/đo được**; phần "đáng giữ" là phán đoán.
5. **Lõi chưa mô hình hoá quà tặng** — chỉ `game.html` có. Đây là nợ đã ghi trong
   `starter-kit/docs/00-kien-truc.md` §3, không phải tính năng đã xong.
6. ~~**`game.html` không import từ `src/`** — hai bản có thể trôi.~~ **Đã đóng cùng Q59:** có
   `build.py` + 7 test parity, cả hai đã reverse-test. Nhưng xem mục 7 — phép reverse-test
   đầu tiên của tôi là **giả**, và nếu tôi không kiểm lại thì đã báo xong sai.
7. **Kích thước tăng 18.775 → 31.603 B thô (+68%).** Không phải vì tôi thêm tính năng, mà vì
   bản #147 **thiếu** `nonce.mjs` và chép tay phần còn lại. Con số cũ nhỏ hơn vì nó thiếu code.
   Tôi ghi ra thay vì để người đọc so sánh hai bản và tưởng bản mới phình ra.
8. **Nonce chưa được test qua iframe thật.** Test kiểm `createNonceGuard()` và kiểm game có gắn
   nó, nhưng chưa có test nào dựng hai document thật rồi `postMessage` qua lại. jsdom không
   chạy `postMessage` cross-frame đủ tin cậy. Đó là khoảng trống **thật**.
