# Teardown X World Games (`xwg.games`) — áp dụng gì vào Game9K

> **Tài liệu sống:** `docs/09-xwg-portal-teardown.md`
> **Đối tượng khảo sát:** [`xwg.games/games`](https://xwg.games/games) — cổng game Web3 của X World Games (XWG)
> **Ngày quan sát:** 22/11/2026 · **Người khảo sát:** đội dự án Game9K
> **Câu hỏi:** XWG làm cổng game Web3 theo cách nào, và **phần nào dùng được** cho Game9K?

---

## 0. Kết luận trước, chi tiết sau

XWG **không phải** đối thủ trực tiếp của Game9K, và cũng **không phải** hình mẫu kinh doanh. Họ là **trang giới thiệu + dẫn link** cho game Web3: bấm "Get started" là **rời khỏi** `xwg.games` sang web của studio (ví dụ `nyanheroes.com`), tải game PC về chơi. Game9K thì ngược lại — chơi **ngay trong khung iframe** trên `game9k.com`, không cài đặt.

Vì vậy giá trị của XWG với Game9K nằm ở **hình thức trình bày catalog**, không nằm ở mô hình doanh thu:

| Dùng được | Không dùng được |
|---|---|
| Cách gắn nhãn **trạng thái + thể loại + nền tảng** ngay trên thẻ game | Một token duy nhất cho cả nền tảng |
| Bố cục **"bảng thông số"** ở trang chi tiết game | Đẩy người chơi ra khỏi cổng để chơi |
| Khối **tài sản/bộ sưu tập gắn với từng game** | Bắt buộc ví crypto mới chơi được |
| Xác nhận mô hình `llms.txt` + `.md` (đã chọn ở `docs/07`) | Thuê ngoài swap/quest; game PC gắn nhãn "Web" |

**3 việc áp dụng ngay** (đã sửa vào `docs/01-user-flows-and-ux.md`): chip mốc `M0–M4` trên thẻ game, facet thiết bị/thể loại phụ ở trang danh mục, và "bảng thông số kiểm chứng" ở trang chi tiết game. **7 việc từ chối** kèm lý do — ghi lại để lần sau không ai đề xuất lại.

---

## 1. Bằng chứng quan sát được

Mỗi dòng dưới đây là thứ **nhìn thấy trực tiếp** trên site ngày 22/11/2026, kèm nguồn. Những gì không tự kiểm chứng được thì ghi rõ là dữ liệu bên thứ ba.

| Mã | Quan sát | Nguồn |
|---|---|---|
| **F1** | Trang `/games` ghi **"Games203"**, phân trang 5 trang; mỗi thẻ game có 3 nhóm nhãn: **Stage**, **Genres**, **Platforms** | `https://xwg.games/games` |
| **F2** | Giá trị `Stage` dùng không nhất quán: `Launched`, `Released`, `Beta`, `Alpha`, `Developing`, `Closed Beta`, `Open Beta`, `Early Access` — "Launched" và "Released" cùng tồn tại, không có định nghĩa | `https://xwg.games/games` |
| **F3** | `Platforms` gồm: `Web`, `Win`, `Mac`, `Android`, `iOS` | `https://xwg.games/games` |
| **F4** | Trang chi tiết game = gallery ảnh + mô tả dài + nút **"Get started" trỏ RA NGOÀI** (`nyanheroes.com`, hoặc link Epic Games Store) + khối thông số **Network / Developer / Stage / Community / Platforms / Genres** + mục **"On-Chain Assets"** + "Latest News" + đăng ký newsletter | `https://xwg.games/games/TVRNMQ==/Nyan-Heroes` |
| **F5** | Catalog trộn game **bên thứ ba AAA** (Nyan Heroes, Parallel, Off The Grid, Big Time, Star Atlas, Guild of Guardians, Otherside…) với game tự phát triển (Dream Card / Hero Card) | `https://xwg.games/` |
| **F6** | **Một token duy nhất** `XWG` cho toàn nền tảng; tiện ích = thưởng chơi (P2E2S), staking/farming, bỏ phiếu quản trị (X DAO + Snapshot), mua NFT/vật phẩm | `https://docs.xwg.games/getting-started/xwg-token/token-utility.md` |
| **F7** | FAQ nói **cần ví crypto để chơi**; nếu chưa có ví thì đăng ký bằng **số điện thoại hoặc email** và dữ liệu lưu **cục bộ trên máy (off-chain)**; muốn thao tác on-chain vẫn phải gắn ví | `https://docs.xwg.games/service/faq/do-i-need-a-crypto-wallet-to-play-games.md` |
| **F8** | `/collections` (10/2023) phân loại NFT theo PFP / Skins / Cards / Consumables / Characters / Mystery Boxes / Loots / Lands / Passes; **mỗi bộ sưu tập link ngược về trang game tương ứng** | Medium XWG, 22/10/2023 |
| **F9** | Hạ tầng then chốt **thuê ngoài**: nút "Swap" → `app.uniswap.org`; "DAO" → `community.xwg.games`; sự kiện chạy trên `quest3.xyz` | `https://xwg.games/` |
| **F10** | Catalog công khai còn **entry rác**: `zzgame`, `zzgame`, `zzgame3` nằm ngay trang 1, cạnh game thật | `https://xwg.games/games` |
| **F11** | `docs.xwg.games` có **`llms.txt`** + hậu tố `.md` cho từng trang (GitBook) — cùng mô hình docs-as-code Game9K đã chọn | `https://docs.xwg.games/llms.txt` |
| **F12** | *(Bên thứ ba, **không** tự kiểm chứng)* `XWG` đa chuỗi (BNB Chain / Ethereum / Arbitrum); một trang theo dõi thị trường ghi giá ~`$0.001269`; ngày niêm yết 22/11/2022 | gamefi.org, coinranking.com |

> **Giới hạn của lần khảo sát này:** không đăng nhập, không kết nối ví, **không bấm chơi thử** game nào. Không có số liệu lưu lượng, doanh thu hay tỷ lệ giữ chân của XWG — và bản tóm tắt này **không** đưa ra con số nào như vậy.

---

## 2. Đọc đúng bản chất: XWG là "danh bạ", Game9K là "sân chơi"

| Tiêu chí | XWG | Game9K |
|---|---|---|
| Người chơi ở lại cổng? | **Không** — bấm "Get started" là rời site, hoặc tải game PC (F4, F3) | **Có** — iframe cô lập `<version-id>.play.<game-domain>` (`SCR-02`) |
| Cần cài đặt? | Có, với phần lớn game (`Win`/`Mac`/`Android`/`iOS`) | Không — HTML5 instant-play |
| Cần ví để chơi? | **Có** (F7) | **Không** — `A1` trong `PRD.md` đã cố định nguyên tắc này |
| Kiểm định chất lượng game? | Không thấy công bố tiêu chí nào | Phễu 4 chặng Poki + Version Arena (`FR-TST-01`, `FR-ARN-01`) |
| Token | Một token nền tảng (F6) | Token **theo từng game**, mở theo từng chặng sau khi phiên bản mới đạt kiểm định |
| Chống "bơm rồi bỏ hoang" | Không có cơ chế | Version-Gated Bonding Curve — mỗi tranche cần một phiên bản tốt hơn |

Điểm này quan trọng vì nó quyết định **cách đọc** phần còn lại: mọi thứ XWG làm tốt đều thuộc lớp **trình bày catalog**; mọi thứ họ thiếu đều thuộc lớp **cơ chế** — đúng lớp Game9K đang xây.

---

## 3. Bảng quyết định: dùng / biến thể / từ chối

| Mã | Nội dung | Trạng thái | Áp dụng vào đâu |
|---|---|---|---|
| **D1** | Chip **trạng thái + mốc** trên mỗi thẻ game (F1, F2) | **ADOPT** (chuẩn hoá lại giá trị) | `SCR-01` — dùng cột có sẵn `lifecycle_status` + `current_milestone`, **không đổi schema** |
| **D2** | Facet **nền tảng / thiết bị** + thể loại phụ ở trang danh mục (F3) | **ADOPT** | `SCR-01` + `/c/[category]` — dùng `mobile_supported`, `orientation`, `secondary_categories` |
| **D3** | Bố cục **"bảng thông số"** ở trang chi tiết game (F4) | **ADAPT** — giữ bố cục, **đổi ruột**: điền dữ liệu kiểm chứng thay vì marketing | `SCR-02` — khối "Hồ sơ kiểm chứng" (hash build, mốc, báo cáo kiểm định, ngày) |
| **D4** | Khối **tài sản gắn với game**, link ngược hai chiều (F8) | **ADOPT** | `SCR-02` — khối tài sản/token có nhãn loại, trỏ `/launch/[slug]` |
| **D5** | Nút "Get started" **đẩy người chơi ra ngoài** (F4) | **REJECT** | Phá vỡ lợi thế instant-play và làm hỏng phễu Fit Test (500 lượt phải đo trong cổng) |
| **D6** | **Một token toàn nền tảng** cho mọi game (F6) | **REJECT** | Xung đột trực tiếp với token theo từng game + version-gating; đây đúng là mô hình "một token, nhiều game" mà Game9K sinh ra để tránh |
| **D7** | **Thuê ngoài** swap / quest / DAO (F9) | **REJECT** (hoãn) | Curve và LP phải nằm trong `programs/` để giữ bất biến minh bạch on-chain; quest/Squad đã có thiết kế riêng ở `SCR-04` |
| **D8** | Game **PC/download** gắn nhãn "Web" (F3, F4) | **REJECT** | Không phải instant-play; sẽ làm sai lệch benchmark CTR/Time-on-Page của `category_benchmarks` |
| **D9** | **Entry rác hiển thị công khai** (F10) | **REJECT** + đặt quy tắc | Catalog công khai chỉ hiển thị `lifecycle_status = 'published' AND visibility = 'public'` (đã có index `idx_games_portal_listing`); trước mỗi đợt mở catalog chạy checklist dữ liệu thật |
| **D10** | **Bắt buộc ví** mới chơi, lưu tiến trình cục bộ (F7) | **REJECT** | `A1` của Game9K đã cố định "không cần ví"; Cloud Save qua Supabase tốt hơn lưu cục bộ (mất máy là mất tiến trình) |
| **D11** | Docs-as-code: `llms.txt` + hậu tố `.md` (F11) | **ADOPT — đã có** | Xác nhận lựa chọn ở `docs/07-docs-as-code-model.md`; không cần làm gì thêm |

### Vì sao D2 và D3 đáng làm dù nhỏ

Cả hai đều **không cần migration**. `games` đã có `mobile_supported`, `orientation`, `secondary_categories`, `current_milestone`, `lifecycle_status`; `game_versions` đã có hash build và validation report. Việc XWG làm đúng và Game9K đang **có dữ liệu nhưng không hiển thị** — nghĩa là chi phí gần bằng 0 mà lại tăng độ tin cậy, thứ mà một cổng game kiểm định cần nhất.

### Vì sao D1 phải chuẩn hoá lại, không copy nguyên

XWG dùng lẫn lộn `Launched` / `Released` / `Open Beta` mà không định nghĩa (F2) — người xem không biết "Released" khác "Launched" ở đâu. Game9K đã có enum đóng trong `docs/02-database-schema.md`:

```
'draft', 'in_testing', 'soft_launch', 'published', 'archived', 'suspended'
```

Chip trên thẻ game vì vậy lấy **đúng 6 giá trị này** + mốc `M0–M4`, không thêm nhãn tự do. Đây là điểm khác biệt có chủ đích: nhãn phải tra được về schema, không phải chữ trang trí.

---

## 4. Điều đáng học nhất — và nó không nằm ở code

XWG có 203 game trong catalog nhưng **không có tiêu chí công khai nào** để biết một game đã "Released" nghĩa là gì (F1, F2). Người chơi không có cách nào phân biệt game thật với `zzgame` (F10). Đó chính là khoảng trống mà `FR-TST-01` (phễu 4 chặng) và `SCR-07` (Inspector) của Game9K lấp vào.

Bài học rút ra, viết thành quy tắc cho chính mình:

1. **Nhãn phải tra được về schema.** Không có nhãn tự do trên UI; mọi chip ánh xạ 1-1 với enum hoặc cột đã khai báo.
2. **Dữ liệu kiểm chứng phải đứng cùng chỗ với lời giới thiệu.** Không để mô tả marketing ở trên và báo cáo kiểm định ở một trang khác.
3. **Catalog công khai là mặt tiền, không phải bãi nháp.** Một entry rác công khai làm mất niềm tin vào toàn bộ 202 entry còn lại.

---

## 5. Việc đã làm trong cùng thay đổi này

- `docs/01-user-flows-and-ux.md` — `SCR-01` thêm chip mốc/trạng thái + facet thiết bị; `SCR-02` thêm khối "Hồ sơ kiểm chứng" và khối tài sản gắn game.
- `docs/PRD.md` — bảng đối chiếu mô hình tham chiếu ghi nhận XWG là **tham chiếu catalog**, không phải tham chiếu mô hình kinh tế.
- `README.md`, `llms.txt` — thêm chỉ mục cho tài liệu này.

## 6. Việc **không** làm

- Không đổi schema, không đổi số liệu, không đổi mô hình doanh thu. Toàn bộ thay đổi ở mục 5 là **mô tả UI trên dữ liệu đã có**.
- Không đưa con số lưu lượng/doanh thu của XWG vào bất kỳ tài liệu nào — không kiểm chứng được (xem giới hạn ở §1).
- Không đưa `$0.001269` (F12) vào deck hay whitepaper: đó là dữ liệu bên thứ ba, có thể sai, và không phải bằng chứng cho bất kỳ luận điểm nào của Game9K.
