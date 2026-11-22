# Đua khủng long cho KOL livestream — Starter Kit mẫu đầu tiên

> **Tài liệu sống:** `docs/23-dino-race-starter-kit.md`
> **Trạng thái:** `SCOPING` → đã dựng **khung chạy được** (`assets/game9k-starter-kit.bundle`), **chưa** đẩy được lên `khanhlegood1/Game9K-Starter-Kit`
> **Ngày:** 22/11/2026
> **Đầu vào:** 11 nguồn tham khảo (9 repo + `app.livecade.io`) và yêu cầu: *"làm game9k Starter Kit mẫu đầu tiên là đua khủng long cho KOL TikTok Live, YouTube Live"*
> **Liên quan:** `docs/17` §2.1 (đua tất định) · §2.3 (xếp lệnh trước) · §4 (entropy) · §6 (R6 quà không đổi thứ hạng) · `docs/18` §1.2 (luật chơi có `sha256`, ngân sách `5 MB`) · `docs/21` §3 (`Presence` 5/30 s) · `docs/22` A2/A5 (registry thay nhánh, config bất biến + state một JSON)

---

## 0. Kết luận trước

**Làm được, và 11 nguồn này đủ để không phải đoán. Nhưng bốn trong năm cơ chế đẹp nhất của chúng bị `docs/17` cấm, và hai repo không có giấy phép.**

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Có nên dùng 11 nguồn này làm nền? | ✅ **Đọc để học, không sao chép.** 4/9 repo **không có giấy phép** = giữ toàn bộ bản quyền (§1.2) |
| **2** | Cơ chế nào dùng được ngay? | 5 cơ chế (§2): observer tách rời · lobby `45 s` + trần `80` · **`/juego-test` = `simulate`** · proxy avatar có allowlist · reconnect có backoff |
| **3** | Cơ chế nào **phải** từ chối? | **Quà đổi thứ hạng** — 3/4 repo đọc được đều làm vậy; `docs/17` §6 **R6** cấm (§4) |
| **4** | "Đua khủng long" có an toàn? | ⚠️ Chỉ khi **không** dùng sprite và tên của Chrome Dino (§5) |
| **5** | Làm game này có phá vị thế trung lập? | ❌ **Không** — với điều kiện đóng khung **P2** (§6) |
| **6** | YouTube Live có làm được? | ⚠️ Được về **kiến trúc** (observer thay được), **chưa** kiểm chứng được API đọc chat (§7) |
| **7** | Đã dựng gì? | Khung chạy được: engine tất định + `simulate` + 5 cổng xanh, **0 phụ thuộc bắt buộc** (§8) |
| **8** | Đã đẩy lên `Game9K-Starter-Kit` chưa? | ❌ **Chưa.** Token của phiên này chỉ có quyền trên `khanhlegood1/GameFun` (§8.1) |

---

## 1. Mười một nguồn — cái gì thật sự đọc được

### 1.1. Mức độ kiểm chứng *(quan sát trực tiếp qua GitHub API, 22/11/2026)*

| Nguồn | Ngôn ngữ | Sao | Giấy phép | Tôi đọc được gì |
|---|---|---|---|---|
| `livecade/marble-race-tiktok-live-game` | — | `1` | ❌ **không có** | **Chỉ `README`** — repo **không có mã**, chỉ 3 ảnh + README |
| `khanhlx6/khanh-dragon-egg-tiktok-live` | HTML | `0` | ✅ MIT | **Mã đầy đủ**: `serverhuevo.js` `131` dòng + 1 file HTML 3D |
| `khanhlx6/TikTok-Chat-Reader` | JS | `0` | ❌ **không có** | **Mã đầy đủ**: `connectionWrapper.js`, `limiter.js`, `server.js` |
| `khanhlx6/TikTok-Live-Connector` | — | `0` | ⚠️ **AGPL-3.0** | Chỉ metadata — **bản sao** thư viện `tiktok-live-connector` trên npm |
| `vamnguyen/tiktok-live-games` | JS | `79` | ❌ **không có** | Chỉ metadata (`7.603` KB) |
| `qafaraz/Horse-Race` | HTML | `3` | ✅ MIT | **Mã đầy đủ**: `js/app.js` `71` dòng |
| `khanhlx6/javascript-racer` | — | `0` | ✅ MIT | Chỉ metadata (`16.380` KB — chủ yếu asset) |
| `lexuankhanh1612/chainplot` | — | `0` | ✅ MIT | Chỉ metadata — **công cụ dashboard onchain, không phải game** |
| `lexuankhanh1612/watchtower` | — | `0` | ❌ **không có** | Chỉ metadata — **theo dõi thay đổi website, không phải game** |
| `app.livecade.io` | — | — | — | ❌ **Không đọc được** — ứng dụng sau đăng nhập; chỉ có trang marketing |

> **Nói thẳng:** 3 trong 11 nguồn **không liên quan tới game livestream** (`chainplot`, `watchtower`, `javascript-racer` là hướng dẫn làm game đua pseudo-3D). `marble-race` — repo được kỳ vọng nhất — **không có một dòng mã**, chỉ có README mô tả sản phẩm. Giá trị thật của nó là **thông số thiết kế** (§2.1), không phải mã.

### 1.2. Giấy phép — đây là phát hiện chặn đường

| Giấy phép | Repo | Được làm gì |
|---|---|---|
| **MIT** | dragon-egg, Horse-Race, javascript-racer, chainplot | Sao chép, sửa, dùng thương mại — **phải giữ thông báo bản quyền** |
| **AGPL-3.0** | TikTok-Live-Connector | Dùng như **phụ thuộc không sửa** ⇒ an toàn cho repo mở. **Sửa** nó rồi phục vụ qua mạng ⇒ phải công bố toàn bộ mã phục vụ mạng *(cần luật sư xác nhận — chưa kết luận)* |
| **Không có** | marble-race, TikTok-Chat-Reader, tiktok-live-games, watchtower | ❌ **Không được sao chép bất kỳ dòng nào.** Không có giấy phép = giữ toàn bộ quyền |

> **Hệ quả thi công:** hai repo **hay nhất để copy** (`TikTok-Chat-Reader` cho hạ tầng, `marble-race` cho thiết kế) đều **không có giấy phép**. Nên luật của Starter Kit là: **đọc để hiểu, viết lại từ đầu, ghi nguồn ý tưởng**. Không vendor, không dán.

**Một chi tiết nữa:** `khanhlx6/TikTok-Live-Connector` khai `fork=false` nhưng là **bản sao** của gói npm `tiktok-live-connector`. Dùng **npm có ghim phiên bản**, không dùng bản sao — để nhận bản vá bảo mật.

---

## 2. Năm cơ chế dùng được ngay

### 2.1. Thông số thiết kế của một sản phẩm đang chạy *(tự công bố trong README)*

`marble-race` công bố đủ thông số để một người làm lại:

| Thông số | Giá trị họ dùng | Ghi chú |
|---|---|---|
| Lobby mở | **`45` giây**, mở sớm khi **đầy** | Đúng bằng `docs/17` §2.3 cần: người chơi vào **trước** giờ đua |
| Trần người một ván | **`80`** | Con số này quan trọng: nó là **trần hiển thị**, không phải trần kỹ thuật |
| Thời lượng ván | `40` – `90` giây | |
| Hiệu lực boost | **`2,5` giây** | Đủ để thấy, đủ ngắn để không phá cân bằng |
| Hình thức | **một browser source** trong OBS/TikTok LIVE Studio, *"không có gì để người xem cài"* | Đây là mô hình đúng — người xem **không** cài gì |
| Thao tác | *"Every action below is **rebindable**"* | ⭐ **Mọi hành động là một dòng cấu hình, không phải một nhánh code** — đúng `docs/22` **A2** |
| Quà gửi giữa hai ván | **được lưu**, kích hoạt ngay sau ván kế tiếp | Chi tiết nhỏ, tránh cảm giác "gửi mà không thấy gì" |

> **Dùng nguyên bộ thông số này**, ghi rõ nguồn là *tự công bố*. Không cần đoán, và không cần thử.

### 2.2. `/juego-test` — đúng thứ `simulate` cần

`khanh-dragon-egg` có một endpoint bơm sự kiện giả vào game (`like`, `gift`, `follow` theo nhịp `150 ms`). Đó chính là `simulate` mode mà `docs/15` §2-A1 đã đòi, **làm bằng 8 dòng**.

**Bài học lớn hơn endpoint đó:** game chạy được **khi live chưa mở**. Nếu bản mẫu chỉ chạy khi có live thật thì không ai kiểm thử được nó, và không ai dám sửa nó.

### 2.3. Observer tách khỏi game — nguồn sự kiện là thứ thay được

`serverhuevo.js` đọc TikTok bằng thư viện, rồi **đẩy vào game qua SSE** trên một endpoint riêng. Game **không biết** TikTok tồn tại.

Đúng kiến trúc cần: **`observer` → `event bus` → `engine`**. Đổi TikTok sang YouTube chỉ là **viết một observer khác**, không chạm engine. Đây là điều kiện để câu "TikTok Live **và** YouTube Live" không phải hai bản mã.

### 2.4. Proxy avatar có allowlist — chống SSRF, đáng học nguyên văn

```js
const u = new URL(String(req.query.u || ''));
if (u.protocol !== 'https:' || !/(tiktokcdn|ibyteimg|byteimg|muscdn)/.test(u.hostname)) return 400;
```

Ba lớp đúng trong 3 dòng: **chỉ `https`** · **allowlist hostname** · **timeout `5 s`**. Ảnh đại diện là **dữ liệu người thật** — nếu proxy không có allowlist thì server của KOL thành proxy mở cho bất kỳ ai.

### 2.5. Reconnect có backoff, và biết **khi nào bỏ**

`connectionWrapper.js` (TikTok-Chat-Reader): `1000 ms × 2`, tối đa **`5` lần**, và `streamEnd` ⇒ **dừng hẳn** thay vì thử lại.

Cộng thêm `limiter.js`: `10` kết nối và `5` yêu cầu/phút **mỗi IP**.

> **Vì sao quan trọng với tiền:** live TikTok **rớt kết nối là chuyện thường**. Nếu observer thử lại vô hạn, một live đã kết thúc sẽ giữ tiến trình chạy mãi. Nếu observer **không** thử lại, khán giả mất lượt giữa ván. Đúng ranh giới này phải nằm trong config, không nằm trong đầu người viết.

---

## 3. Ba repo không dùng được cho việc này

| Repo | Vì sao không |
|---|---|
| `lexuankhanh1612/chainplot` | Dashboard onchain, SQL trên sự kiện — **không có yếu tố game**. Có thể hữu ích cho **Inspector** sau này, không cho Starter Kit |
| `lexuankhanh1612/watchtower` | Dịch vụ theo dõi thay đổi website — **không liên quan** |
| `khanhlx6/javascript-racer` | Hướng dẫn game đua pseudo-3D, `16` MB chủ yếu asset. Chỉ dùng nếu sau này làm **đua xe nhìn từ sau**; đua khủng long nhìn ngang thì không cần |

---

## 4. Cơ chế phải từ chối — và cách giữ được mục tiêu

### 4.1. Quà đổi thứ hạng: ba phần tư nguồn đều làm, `docs/17` cấm

| Nguồn | Quà làm gì |
|---|---|
| `marble-race` | *"a Rose boosts the sender's own marble"* · *"a banana lands in front of the **leader**"* · *"a shell knocks the leader back"* |
| `khanh-dragon-egg` | *"cuantas más monedas, más rara será la cría"* — **quà quyết định độ hiếm** |
| `Horse-Race` | không có quà (game một máy) |

`docs/17` §6 **R6** đã chốt: *"Quà TikTok ảnh hưởng thứ hạng — pay-to-win, và bị đọc là cá cược."*

**Nếu chỉ nói "không được dùng quà" thì mất luôn lý do KOL bật game.** Cách giữ cả hai:

| Vế | Cơ chế |
|---|---|
| **Thứ hạng** chỉ phụ thuộc hành động **miễn phí** | Boost bằng **comment đúng nhịp** (`±150 ms`) — mọi người đều làm được, và nó **sinh entropy** đúng `docs/17` §4 |
| Quà vẫn có giá trị | **Trang trí**: skin khủng long, vệt chạy, hiệu ứng nổ. Hiện **thẻ cảm ơn** có tên người gửi — thứ KOL thật sự muốn |
| Ghi rõ trên màn hình | Một dòng: *"Quà chỉ đổi trang trí, không đổi thứ hạng"* |

> **Đây là chỗ khác biệt duy nhất về sản phẩm so với cả 3 đối thủ đọc được.** Nó không làm yếu game; nó làm game **bán được cho trường học và nhãn hàng** — nhóm khách không thể chạm vào bản pay-to-win.

### 4.2. Bốn thứ khác phải từ chối

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Kết quả tính bằng `Math.random()` lúc chạy (như `Horse-Race`) | Không phát lại được ⇒ không kiểm chứng được ⇒ vô hiệu `docs/17` §2.1 |
| **R2** | Khung 3D (dragon-egg) cho bản mẫu đầu tiên | Ngân sách `5 MB` (`docs/18` §1.2) là **tổng gói**; khung 3D ăn gần hết vào asset, và không cần cho một cuộc đua nhìn ngang |
| **R3** | Dùng `Socket.IO` + `setInterval` giữ kết nối cho từng khán giả | Cần nuôi `N` kết nối; `docs/17` §2.1 đã bỏ WebSocket. Chỉ **một** kết nối: từ observer tới TikTok |
| **R4** | Sao chép mã từ repo không giấy phép | §1.2 |

---

## 5. "Đua khủng long" — dùng được, nhưng phải vẽ con khủng long của mình

**Rủi ro thật, không phải hình thức:**

| Rủi ro | Cách tránh |
|---|---|
| Sprite `T-Rex` của Chrome Dino là **tác phẩm có bản quyền của Google** | Vẽ sprite riêng, phong cách pixel, **ghi rõ trong repo** là thiết kế gốc |
| Tên "Chrome Dino", "T-Rex Runner", "No Internet Game" | ❌ Không dùng trong tên game, tên gói, tên thư mục. Dùng **"Game9K Dino Race"** |
| Bắt chước y hệt bố cục màn hình Chrome | Đổi bố cục: **5 làn dọc**, không phải 1 đường chạy ngang — cũng để `80` người cùng thấy được |
| Hình ảnh "đua" + "về đích" + quà ⇒ bị đọc là cá cược | §6 của `docs/17`: **không** chữ "cược/đặt/ăn tiền/x2"; tiêu đề là **"Bảng thành tích"** |

> **Quyết định:** nhân vật là **khủng long pixel tự vẽ** (CC0, kèm file nguồn trong repo). Nếu studio muốn nhân vật khác, họ thay **một sprite sheet**, không sửa engine — đúng `docs/18` §1.2.

---

## 6. Vị thế trung lập — đóng khung P2, không phải P3

`docs/17` §5 và `WHITEPAPER §288` cấm Game9K tự làm game **cạnh tranh studio**. Nhưng `docs/17` §5 **P2** cho phép đúng việc này:

> *"Game9K làm **bộ khung mã nguồn mở** (SDK + mẫu Streamer Mode), **không** làm game."*

| | Cách đóng khung | Đánh giá |
|---|---|---|
| **P2** | Starter Kit = **khung tích hợp + một game mẫu nhỏ** để chứng minh khung chạy. Studio thay luật + sprite | ✅ **Đây là việc đang làm** |
| **P3** | Đưa game mẫu lên Arena như một tựa game | ❌ Không. Game mẫu **không** vào Arena, **không** nhận `VPH`, có nhãn công khai `SAMPLE` |

**Ba luật cứng để giữ vị thế trung lập** — phải nằm trong `README` của Starter Kit:

1. Game mẫu **không** được xếp hạng trên Arena, **không** nhận vốn.
2. Luật chơi ở **file JSON có `sha256`** — nếu studio chỉ đổi ảnh, `sha256` luật trùng ⇒ **cùng một game**, đúng `docs/18` §3.3.
3. Starter Kit **không** chứa gì riêng của `game9k.com`: không gọi API riêng, không phụ thuộc Supabase của Game9K.

---

## 7. YouTube Live — kiến trúc đúng, API chưa kiểm chứng

**Đọc chat YouTube không có thư viện tương đương `tiktok-live-connector` ở mức trưởng thành.** Có ba đường, và cả ba đều chưa kiểm chứng trong phiên này:

| Đường | Trạng thái |
|---|---|
| YouTube Data API v3 · `liveChatMessages.list` | API chính thức, **có quota**; chưa kiểm chứng hạn mức thực tế |
| `yt-dlp`/`pytchat` đọc luồng chat | Không chính thức, dễ vỡ khi YouTube đổi |
| Không đọc chat, chỉ dùng **link + màn hình chung** | Rẻ nhất, nhưng mất mô hình "comment để tham gia" |

**Quyết định:** viết **interface observer** (`open()`, `on(event)`, `close()`) và chỉ cài `observer-tiktok` trong bản mẫu. `observer-youtube` để trống có chủ đích, ghi rõ **chưa kiểm chứng**. Không hứa "hỗ trợ YouTube" khi chưa có một dòng chạy được.

---

## 8. Đã dựng gì trong Starter Kit

```
Game9K-Starter-Kit/
├── rules/dino-1.0.0.json       # luật chơi + sha256 — hợp đồng, không phải code
├── src/engine/race.mjs         # hàm kết quả TẤT ĐỊNH, không DOM, không mạng
├── src/engine/canonical.mjs    # JSON chuẩn hoá + sha256
├── src/server/index.mjs        # node:http, 0 phụ thuộc
├── src/server/observer-*.mjs    # file | sim | tiktok(tùy chọn)
├── src/web/                    # Canvas2D, ~1 file, không engine
├── scripts/check_*.py          # 5 cổng, chạy được khi chưa cài gì
└── fixtures/golden/            # ván vàng: Node và Python phải ra cùng hash
```

**Năm quyết định kỹ thuật, và lý do:**

| Quyết định | Lý do |
|---|---|
| **Không dùng engine** (Canvas2D thuần) | Không phải vì PixiJS/Phaser tệ (§4.1 `docs/21`: `255` / `352` KB) mà vì đua nhìn ngang chỉ cần vẽ `5` làn. Ngân sách `5 MB` để dành cho **asset của studio** |
| **Số nguyên, không dấu phẩy động** | Kết quả phải giống **từng bit** giữa V8 và CPython. Vị trí tính bằng **mili-giây × đơn vị**, không bằng `float` |
| **Cùng một `seed` ⇒ cùng một kết quả, ở hai ngôn ngữ** | Fixture vàng trong `fixtures/golden/`: Node ghi, Python phải khớp `result_sha256`. Đây là **cổng mạnh nhất** của repo |
| **`CONFIG` bất biến + `STATE` một JSON mỗi ván** | `docs/22` **A5**. Ván đua là **state**, luật là **config có `sha256`** |
| **Observer TikTok là phụ thuộc *tùy chọn*** | AGPL-3.0 (§1.2): lõi giữ Apache-2.0, chỉ nạp observer khi `OBSERVER=tiktok` |

---

### 8.1. Chưa đẩy được lên GitHub — và cách đẩy trong một lệnh

Token của phiên làm việc này là **GitHub App** chỉ cài trên `khanhlegood1/GameFun`:

```
remote: Permission to khanhlegood1/Game9K-Starter-Kit.git denied to khanhlegood1. (403)
POST /repos/.../contents/...  →  "Resource not accessible by integration"
```

Đọc `Game9K-Starter-Kit` thì được (repo công khai), **ghi thì không**. Nên toàn bộ mã nằm
trong `assets/game9k-starter-kit.bundle` — một **git bundle** thật, đã có commit sẵn:

```bash
git clone assets/game9k-starter-kit.bundle Game9K-Starter-Kit
cd Game9K-Starter-Kit
git remote set-url origin https://github.com/khanhlegood1/Game9K-Starter-Kit.git
git push -u origin main
```

Hoặc cài lại GitHub App cho repo đó trong Arena, rồi phiên sau đẩy trực tiếp.

**Số đo của bản đã commit:**

| | |
|---|---|
| `rules_sha256` | `f910cb5234806382d2ffa35d3210f2777691cb9691d8394220f7f2e04cc2fbd9` |
| Fixture vàng | **3** (`empty`, `wave-8`, `full-80`), Node và Python ra cùng `result_sha256` |
| Cổng | **5/5 xanh** — purity · rules hash · ref engine · determinism · server end-to-end |
| Về đích | **`10,8%`** người-chơi trong một ván 80 người (60 seed) |
| Người không bấm thắng | **`0/60`** ván khi 40 người khác bấm hoàn hảo |
| Một người bấm hoàn hảo | hạng trung vị **`7/80`** (p10 `1`, p90 `35`) |
| Bấm bừa `~1,4 s/lần` | chỉ **`11,1%`** lệnh được nhận (bấm đúng nhịp: `100%`) |

---

## 9. Sáu việc phải làm trước làn sóng KOL đầu tiên

Không việc nào nằm trong Starter Kit, và cả sáu đều đã có trong `docs/17`:

| # | Việc | Vì sao chặn |
|---|---|---|
| **1** | Sửa `FR-POP-01`: referral theo **`work` tích luỹ `≥ 120` phút** | Phiên đua `40` giây **không bao giờ** tới ngưỡng Bronze `≈ 89,9` phút ⇒ chương trình KOL luôn trông thất bại |
| **2** | Ghi **"không cần đăng nhập"** ở bước 1 của funnel | Câu giảm bỏ ngang mạnh nhất |
| **3** | Người chỉ-xem **không** được tính `work`, và **phải thấy lý do** | `docs/15` §3-A3 · `docs/17` §4 |
| **4** | Đo **CAC**: bao nhiêu người xem → bao nhiêu phiên hợp lệ `≥ 90` giây | Game đua **không phải doanh thu** (`$2–6`/`1.000` phiên) — nó là chi phí |
| **5** | Câu hỏi 5 cho luật sư: bảng xếp hạng + hiện tên người chơi trên live bên thứ ba | `docs/17` §1 |
| **6** | Quy tắc **"reskin ≠ game mới"** công bố **trước** khi phát Starter Kit | `docs/18` §3.3 — sau khi phát thì không rút lại được |

---

## 10. Việc **không** làm trong tài liệu này

- Không sửa `W = 0.60` / `H = 180`, whitepaper, deck, 4 PDF, schema (**34** bảng).
- Không đưa giá KOL, eCPM hay doanh thu mới — dùng đúng `$1–$3` đã có ở `WHITEPAPER §192`.
- Không khẳng định YouTube Live chạy được (§7).
- Không sao chép mã từ 4 repo không giấy phép.
- Không đưa game mẫu lên Arena, không gán `VPH` cho nó.
