# ADR-0041 — Đua bi (Marble Race) cho live: làm được gì, và ba thứ **không** làm được

**Trạng thái:** Proposed — một phần **đã cài** (§6), một phần **bị từ chối có lý do** (§4, §5)
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0027`](ADR-0027-starter-kit-game-mau-dua-khung-long.md) (game mẫu đua khủng long) · [`ADR-0016`](ADR-0016-license-compliance.md) (license) · [`ADR-0011`](ADR-0011-legal-posture.md) · [`dua-vit-tiktok`](../12-decisions/2026-11-22-dua-vit-tiktok-va-phan-loai-game.md) (NĐ 147/2024, G1–G4) · [`tokenomics`](../05-contracts/tokenomics.md) §8 · `starter-kit/src/engine/marble.mjs`

> Bạn yêu cầu **ba** nâng cấp (skin bi, chướng ngại, PK streamer) và **một** việc khác
> (chuẩn hoá hai game khủng long). Kết quả **không** đồng nhất, nên ADR này tách ra:
>
> | # | Yêu cầu | Kết quả |
> |---|---|---|
> | 1 | Skin bi, hàng trăm viewer không đè hình | ✅ **Đã cài** — `marble.html`, 2..256 viên |
> | 2 | Chướng ngại ngẫu nhiên, lật kèo giây cuối | 🟡 **Đã cài một nửa** — chỉ làm chậm, không đẩy lùi (§3) |
> | 3 | PK / Streamer Battle, thả chướng ngại theo quà | 🔴 **Từ chối** — mất tất định ⇒ về G1 (§4) |
> | 4 | "Chuẩn hoá 2 game khủng long theo mô tả mới" | 🔴 **Không có game thứ hai** — xem §5.1 |
> | 5 | "Đã có Gateway Multi-Tenant + TikTok Connector v2 + youtube-chat" | 🔴 **Không đúng** — xem §5.2 |

---

## 0. Trả lời ngắn

> **Một câu:** tôi đã làm được cái làm được — đua bi N người, tất định, có chướng ngại làm chậm,
> 25 test mới. Và tôi **không** làm cái không làm được: **PK streamer theo quà thời gian thực**
> không phải "khó", nó **phá đúng thứ duy nhất** giữ game này ở nhóm cấp phép nhẹ.

---

## 1. Điều đúng trong yêu cầu của bạn: đua bi **là** cải tiến so với đua khủng long

Bạn đúng ở chỗ quan trọng nhất, và nó đáng ghi lại vì sao:

| | Đua khủng long (`race.mjs`) | Đua bi (`marble.mjs`) |
|---|---|---|
| Danh tính | **4 làn cố định** — người xem chọn 1 trong 4 | **mỗi viewer LÀ một viên** — 2..256 |
| Ai được đại diện | 4 nhóm | từng người |
| Hình | chữ nhật bo, rộng 18–26 px | **hình tròn**, bán kính co theo `1/√N` |
| Đè hình ở 200 người | 4 hình, không đè — nhưng chỉ có 4 | 200 hình, bán kính tự co ⇒ **không đè** |
| Màu | 4 màu cố định trong mã | suy từ `id` (360 hue) |

**Cơ chế co bán kính** giải đúng vấn đề bạn nêu, và nó **không cần Three.js**:

```js
const r = Math.sqrt(area / (n * Math.PI * 2.2));   // n = số viên
return Math.max(2.5, Math.min(15, r));
```

Đo được: 4 viên ⇒ r ≈ 15 px (chạm trần) · 64 viên ⇒ r ≈ 8 px · 256 viên ⇒ r ≈ 4 px. Ở r < 7 px
thì chữ cái đầu tự tắt (không đọc được thì đừng vẽ), chỉ còn màu phân biệt.

> **Vì sao Canvas 2D chứ không Three.js/WebGL:** ba lý do cụ thể, không phải "đơn giản hơn".
> ① `game.html` hiện là **31.603 B thô · 11.865 B gzip** và cam kết **0 request ngoài** —
> Three.js thêm ~600 KB. ② OBS Browser Source trên máy streamer yếu chạy 256 sphere
> texture là đúng chỗ giật. ③ `test/dom/` chạy được trong jsdom **vì** canvas 2D giả được —
> WebGL trong jsdom thì không, tức mất toàn bộ cổng "game nạp là chết".

---

## 2. Chướng ngại: đã cài, nhưng **chỉ làm chậm**

### 2.1. Vì sao không "đá rơi làm chậm 50%" đúng như bạn viết

Bạn viết *"lốc xoáy, đá rơi làm chậm 50%"* — cả hai đều **làm chậm**, nên cài được, và đã cài:
`obstacleSlowFactor ∈ [0.45, 0.75]`, tức chậm 25–55%. Lịch chướng ngại được quyết **trước**
từ seed, không quyết giữa cuộc đua.

Nhưng có một thứ **không** cài được dù nghe hợp lý: **"đẩy lùi"**.

### 2.2. Vì sao "đẩy lùi" bị loại — và đây là bất biến, không phải sở thích

`starter-kit/test/race.test.mjs` **INV-04** khẳng định vị trí **đơn điệu không giảm**:

```js
assert.ok(cur.positions[i] >= prev.positions[i] - 1e-9, "lùi lại");
```

Bất biến này tồn tại vì một lý do cụ thể: nó là thứ cho phép người xem **tua lại** và kiểm kết
quả. Nếu một viên có thể bị đẩy lùi, thì "vị trí tại tick t" không còn là hàm của `(seed, roster)`
theo cách tuyến tính — và quan trọng hơn, **không ai kiểm được** ngoài việc chạy lại toàn bộ.

⇒ `marble.mjs` **kẹp cứng** `factor` vào `[0.2, 1]`. Không phải kiểm tra đầu vào — mà là
cưỡng chế tại chỗ dùng, để dù config truyền `factor: -5` thì kết quả vẫn chỉ là chậm đi.
Test **MB-09** chứng minh điều này, và **MB-25** chứng minh nó **đỏ được** (bỏ kẹp ⇒ test đỏ).

> **Cái mất, nói thẳng:** "lật kèo ở giây cuối" bằng cách kéo người dẫn đầu lùi lại **không có**.
> Cái có là: người dẫn đầu bị chậm 55% trong 40 tick (≈0,67 giây xem) — đủ để người sau vượt,
> nhưng không đủ để "lội ngược dòng" từ vị trí cuối. Đây là **giới hạn tự chọn**, và nó đánh đổi
> kịch tính lấy tính kiểm chứng được.

### 2.3. Một phát hiện khi đo: bước ghi frame phải tự co

Ở 256 viên, JSON của `frames` ban đầu là **2.003 KB** — gấp ba lần cần thiết, vì tôi lặp
`surging`/`slowed` vào **từng frame** trong khi chúng suy ra được từ `racers[].surges`/`.obstacles`
(mỗi viên vài khoảng, không phải mỗi frame một mảng).

Sau khi bỏ + cho bước ghi tự co theo N:

| Số viên | Thời gian mô phỏng | Số frame | JSON | gzip |
|---|---|---|---|---|
| 4 | 15,9 ms | 403 | 22 KB | 6 KB |
| 32 | 19,0 ms | 398 | 95 KB | 30 KB |
| 64 | 32,2 ms | 200 | 103 KB | 32 KB |
| 256 | 37,4 ms | 133 | **301 KB** (từ 2.003) | 83 KB |

Công thức: `stride = frameStride × ceil(N / 32)`, chặn trên `6`. Đây là **đánh đổi có khai báo**:
ở 256 viên, renderer nội suy giữa các frame cách nhau 6 tick, nên chuyển động mượt hơn một chút
so với thực tế. Test **MB-21** khoá ngân sách 400 KB; **MB-22** khoá việc frame chỉ có `positions`.

---

## 3. Yêu cầu 3 — PK / Streamer Battle: **từ chối**, và đây là lý do

### 3.1. Cơ chế bạn mô tả

> *"Hai phòng live đua song song. Điểm Gift của khán giả bên nào to hơn sẽ **thả chướng ngại vật
> sang đường đua của bên đối thủ**."*

### 3.2. Vì sao nó phá đúng thứ giữ game ở nhóm nhẹ

| Bước | Hệ quả |
|---|---|
| Quà đến **sau khi** cuộc đua bắt đầu | Nó là **input mới**, không nằm trong `cfg` |
| Kết quả không còn tính trước được | Mất tính tất định |
| Không tất định ⇒ phải đồng bộ trạng thái giữa hai phòng | Cần **realtime** |
| Realtime ⇒ **G2 → G1** | `dua-vit-tiktok` §2.1 và `ADR-0027` §1 đã kết luận: G1 là nhóm cấp phép nặng nhất |

Và tệ hơn: *"thả chướng ngại sang đường đua bên kia"* là **tác động lên kết quả của người khác**.
`dua-vit-tiktok` §3 đã xét đúng cơ chế này ở bối cảnh đua vịt và kết luận:

> *"Ném vật cản vào người khác đặc biệt nhạy: nó là **tác động lên kết quả của người khác**, tức
> là tính cạnh tranh trực tiếp — đúng thứ G1 mô tả, và đúng thứ dễ bị nhìn như **cá cược** khi có
> xếp hạng + phần thưởng."*

⇒ Không phải "khó làm". Là **làm được nhưng mất quyền mở ở Việt Nam**.

### 3.3. Ba phương án thay thế — và cái nào tôi chọn

| Phương án | Giữ tất định? | Đánh giá |
|---|---|---|
| **A.** Quà đặt **trước** khi đua: mỗi phòng có `obstacleBudget` từ quà đã nhận, cả hai phòng chốt budget rồi cùng chạy | ✅ | **Chọn.** Đây là "PK" thật: kết quả phụ thuộc **ai gây quỹ nhiều hơn trước giờ**, không phụ thuộc ai bấm nhanh hơn |
| **B.** Hai phòng chạy **hai seed khác nhau**, quà của phòng A chỉ ảnh hưởng roster phòng A | ✅ | Được, nhưng không phải "PK" — hai cuộc đua độc lập, không ai tác động ai |
| **C.** Thả chướng ngại realtime sang phòng đối thủ | ❌ | **Từ chối** — §3.2 |

Phương án **A** cài được **ngay bây giờ** và không cần thêm dòng mã lõi nào: nó chỉ là
"truyền `obstacleCount` khác nhau cho hai lần gọi `simulateMarble`". Xem Q-ADR41-c.

### 3.4. Và một rủi ro pháp lý riêng, không liên quan G1

"Điểm gift bên nào to hơn thì bên đó…" là **so sánh số tiền** để giành lợi thế trong một cuộc thi
có xếp hạng. Dù chưa có thưởng, cấu trúc này **gần** với mô tả trò chơi có thưởng. `ADR-0011`
chưa có ý kiến luật sư về điểm này, và `tokenomics.md` §8 đã cấm mọi thứ tạo "kỳ vọng lợi nhuận".

⇒ Nếu PO muốn giữ, nó cần **một câu hỏi luật sư riêng** (Q-ADR41-d), không thể quyết bằng ADR này.

---

## 4. Điều tôi **không** làm, và vì sao (phần quan trọng nhất)

### 4.1. "Chuẩn hoá **2 game khủng long** của tôi theo mô tả mới" — repo chỉ có **một**

Bạn viết *"2 game khủng long cũ"* và nhắc *"game #2 **Jurassic Sanctuary Sprint**"*. Kiểm:

```bash
grep -rln "Jurassic\|jurassic" --include="*.md" --include="*.mjs" --include="*.js" .
# ⇒ 0 kết quả
```

`Jurassic Sanctuary Sprint` **không tồn tại trong repo này**. Nó từng được nhắc ở
`ADR-0027` §5 — nhưng ở đó nó là một **tệp HTML bạn gửi kèm** (78.197 B), không phải mã trong
repo. ADR-0027 §5 cũng đã đo và ghi: tệp đó **không có `Game9KBridge`**, **0 chỗ nhắc YouTube**,
và **0 WebSocket**.

Trong repo có **một** game khủng long: `starter-kit/game.html` → sinh ra
`portal/public/games/dino-race.html` bằng `scripts/gen_portal_data.mjs`.

⇒ Không có "game thứ hai" để chuẩn hoá. Tôi **không** bịa ra một game để rồi "chuẩn hoá" nó.
Nếu bạn có tệp `Jurassic Sanctuary Sprint` ở máy, cần đưa vào repo trước (Q-ADR41-e).

### 4.2. "Dự án đã có sẵn Gateway Multi-Tenant + TikTok-Live-Connector v2 + youtube-chat" — **không đúng**

Kiểm từng mục:

| Bạn nói repo đã có | Thực tế (lệnh kiểm) |
|---|---|
| **Architecture Gateway Multi-Tenant** | `grep -rn "Multi-Tenant\|multi-tenant\|gateway" starter-kit/ docs/08-adr/ADR-0027*` ⇒ **0 kết quả** |
| **`TikTok-Live-Connector` v2** trong kit | **Không có, và là quyết định có chủ ý.** `starter-kit/src/bridge/adapters.mjs` dòng 5–24: connector là **AGPL-3.0** ⇒ *"Starter Kit phát hành cho studio bên thứ ba KHÔNG THỂ chứa hoặc phụ thuộc AGPL"*. `package.json` chỉ có `pg`, `@electric-sql/pglite`, `jsdom` |
| **`youtube-chat`** | Không có trong `package.json`. `starter-kit/docs/01-tich-hop.md` chỉ có **ví dụ** host tự nối |

⇒ Adapter **có**, và **có test** (13 test). Connector **không có**, và `ADR-0027` §4 đã ghi rõ:
*"Bản mẫu **không** kết nối nền tảng nào. Nó có **cầu nối** đúng, và đó là thứ đáng có trước."*

Khoảng cách này **không phải thiếu sót** — nó là ranh giới license. Lấp nó bằng cách nhúng AGPL
làm mất quyền phát hành kit.

### 4.3. Bốn repo bạn đề nghị tham khảo: ba không dùng được, một là GPL-3.0

Đo bằng GitHub API ngày 2026-11-18 (`gh api repos/<r>`):

| Repo | License | Sao | Push cuối | Dùng được? |
|---|---|---|---|---|
| `non4me/marble-race` | **`null`** | 1 | 2026-06-13 | ❌ **Không có license** ⇒ giữ toàn bộ quyền |
| `non4me/marbles2d` | **`null`** | 2 | 2026-06-13 | ❌ Cùng lý do |
| `mwood77/YouTubePlays-vs-TwitchPlays` | **GPL-3.0** | 2 | **2024-04-15** | ❌ GPL-3.0 lây nhiễm; và **2,5 năm không cập nhật** ⇒ YouTube Data API v3 đã đổi |
| `livecade/marble-race-tiktok-live-game` | **`null`** | 1 | 2026-11-04 | ❌ Cùng `ADR-0027` §2 — tên này **đã được xét** và loại |

⇒ Cả bốn **không dùng được**, và cả bốn đều **≤ 2 sao**. Điều này không nói chúng dở — nó nói
**không có gì để học về quy mô**. `ADR-0027` §2.1 đã ghi cái giá của việc này một lần rồi
(`vamnguyen/tiktok-live-games` **79 sao**, không license, ta mất phần đã được cộng đồng kiểm chứng).

### 4.4. "Avatar của viewer" — không tải từ CDN, và đây là lý do

Bạn yêu cầu *"dán Avatar của viewer"*. Ba cách, và tôi chọn cách thứ ba:

| Cách | Vấn đề |
|---|---|
| `<img src="…tiktok CDN…">` | ① Phá cam kết **0 request ngoài** của `game.html` (lý do OBS Browser Source khởi động được); ② TikTok chặn hotlink; ③ **không tất định** — cùng seed ra ảnh khác nếu CDN đổi ⇒ người xem không tái lập được |
| Host tải sẵn, đẩy qua `postMessage` | ✅ **Đúng**, và là đường tôi để mở: renderer nhận `avatarUrl` đã cache, game không tự gọi mạng |
| Suy **màu** từ `id` | ✅ **Chọn ở bản mẫu**: 0 request, tất định, phân biệt 256 viên (`hueFor()`) |

Bản mẫu vẽ **chữ cái đầu + màu**. Đây là **thiếu so với yêu cầu**, và tôi ghi ra thay vì gọi nó
là "đã xong".

---

## 5. Đã làm — đo, không kể

| Hạng mục | Số liệu |
|---|---|
| Lõi mới | `starter-kit/src/engine/marble.mjs` — 2..256 viên, tất định |
| Test lõi | **25 test** (`marble.test.mjs`), **25 pass** — gồm **2 reverse-test** (MB-24, MB-25) |
| Test DOM | **5 test** (`test/dom/marble-boot.test.mjs`), **5 pass** |
| Tổng kit | **72 test / 72 pass** (trước: 47) — `game.html` không đổi hành vi |
| Game mới | `starter-kit/marble.html` — **35.293 B thô · 13.439 B gzip**, **0 request ngoài** |
| `game.html` | **31.611 B thô · 11.857 B gzip** — **không đổi** |
| Build | `python3 starter-kit/build.py` sinh **cả hai**; `--check` xanh cho cả hai |
| `npm test` | **514 pass / 0 fail** — không hồi quy |

### 5.1. Một lỗi thật mà test bắt được (ghi lại vì nó đáng ghi)

**MB-02 đỏ ngay lần chạy đầu.** Nguyên nhân: RNG được tiêu theo **thứ tự roster**, nên hai lần
gọi cùng `seed` + cùng **tập** người nhưng khác **thứ tự mảng** cho kết quả **khác nhau** — trong
khi `raceId` (băm trên id **đã sắp**) lại **giống nhau**.

> Nghĩa là: người xem chạy lại `raceId` sẽ thấy kết quả khác, đúng thứ **INV-08** của kit cấm.

Sửa: sắp roster theo `id` **trước khi** tiêu RNG. Kết quả là hàm của **tập** người tham gia, không
phải của thứ tự họ vào phòng. Đây là loại lỗi mà không test nào viết sau sẽ tìm ra.

### 5.2. Và một test **sai** mà tôi suýt tin (ghi lại vì cùng lý do)

MGB-03 đỏ, và bản nháp đầu tôi kết luận "mã sai". Thực ra `postMessage` giao **bất đồng bộ** —
test kiểm tra ngay sau `dispatchEvent` nên luôn thấy rỗng. Đã xác nhận bằng tay (`marble:ready`
có phát, chỉ muộn một microtask) rồi sửa **test**, không sửa mã.

> Nhưng trong lúc sửa tôi **cũng** sửa mã: `post()` bản đầu chỉ phát khi `window.parent !== window`.
> Đúng cho production, nhưng làm cổng test không quan sát được gì ⇒ cổng thành vô dụng. Nay luôn
> phát trong `try/catch`. Ghi cả hai vì đây đúng là cặp "mã sai / test sai" dễ lẫn.

---

## 6. Việc nên làm tiếp, có thứ tự

| Bước | Việc | Chặn bởi | Trạng thái |
|---|---|---|---|
| **1** | Xác nhận `marble.html` chạy trong OBS + TikTok in-app browser **thật** | Không | 🔴 **Chưa làm** — jsdom chỉ chứng minh logic, không chứng minh render |
| **2** | Phương án **A** của PK: quà chốt **trước** giờ đua, hai phòng hai `obstacleCount` | Q-ADR41-c | 🟡 Cài được, cần PO chốt |
| **3** | Avatar thật qua `postMessage` (host cache) | Không | 🟡 Đường đã mở, chưa cài |
| **4** | Đưa `Jurassic Sanctuary Sprint` vào repo (nếu bạn muốn nó được chuẩn hoá) | Q-ADR41-e | 🔴 Không có tệp |
| **5** | PK realtime (§3.3 phương án C) | **Từ chối** | 🔴 Cần legal + chấp nhận G1 |

---

## 7. Sáu câu cần PO quyết

| Mã | Câu hỏi |
|---|---|
| **Q-ADR41-a** | Đua bi thay hay **bổ sung** đua khủng long? Tôi đề nghị **bổ sung** — `game.html` không đổi, kit có hai mẫu |
| **Q-ADR41-b** | Chấp nhận giới hạn "chướng ngại chỉ làm chậm, không đẩy lùi"? Nếu **không**, phải bỏ INV-04 ⇒ mất khả năng người xem tự kiểm |
| **Q-ADR41-c** | PK theo phương án **A** (quà chốt trước giờ đua) — có làm không? Đây là cách duy nhất giữ tất định |
| **Q-ADR41-d** | Nếu giữ PK realtime: có sẵn sàng (i) nhận **G1** và (ii) hỏi luật sư về "so gift để giành lợi thế" không? |
| **Q-ADR41-e** | `Jurassic Sanctuary Sprint` — có tệp để đưa vào repo không? Hiện **0 kết quả** grep |
| **Q-ADR41-f** | Ghi đè `srcDir`/`assetDir` của đua bi trong `game.html` thay vì để mặc định? — xem Q-ADR41-f giải thích ở §8 |

---

## 8. Ranh giới trung thực

- **Không** nói "đã đạt yêu cầu về avatar". Bản mẫu vẽ **chữ cái + màu**, không phải avatar. Đường
  để có avatar thật đã mở (`postMessage`), nhưng **chưa cài**.
- **Không** nói "lật kèo giây cuối" như bạn mô tả. Chướng ngại làm chậm 25–55% trong 18–40 tick;
  đủ để vượt, **không** đủ để lội từ cuối lên đầu.
- **Không** nói "PK đã có". PK **realtime** bị từ chối có lý do; PK **chốt trước** là đề xuất, chưa cài.
- **Không** nói "đã nối TikTok/YouTube". Vẫn **0 dòng** nối nền tảng thật — đúng như `ADR-0027` §4.
- **Không** nói "hai game khủng long". Repo có **một**. `Jurassic Sanctuary Sprint` là **0 kết quả**
  grep, và tôi **không** bịa nó ra.
- **Không** nói "Gateway Multi-Tenant đã có". `grep` ⇒ **0 kết quả**. Đó là mô tả về một hệ thống
  khác, không phải repo này.
- **Không** dùng chữ "first" / "duy nhất" / "chưa ai làm" cho bất kỳ phần nào. Theo `ADR-0023`
  loại 2, dạng đúng là *"chúng tôi chưa tìm thấy"* **kèm phạm vi đã tìm** — và tôi chưa tìm.
