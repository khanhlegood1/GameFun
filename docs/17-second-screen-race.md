# Đua tương tác kiểu second-screen — kiểm chứng kế hoạch

> **Tài liệu sống:** `docs/17-second-screen-race.md`
> **Trạng thái:** `SCOPING` — phản biện kế hoạch, **chưa** phải đặc tả thi công
> **Ngày:** 22/11/2026
> **Đầu vào:** kế hoạch do người sáng lập viết tay — "second-screen", 3 bẫy, funnel 4 bước, và ý định **đội ngũ Game9K tự dựng bản mẫu đầu tiên**
> **Tài liệu liên quan:** `docs/16` (chọn game neo), `docs/15` (§2-A1 `simulate`, §3-A2 trần chi trả), `docs/08` (4 câu hỏi pháp lý đang chờ)

---

## 0. Kết luận trước

**Hướng "second-screen" đúng. Ba cơ chế trong kế hoạch dùng được ngay. Nhưng bốn chỗ phải sửa trước khi viết dòng code đầu tiên.**

| # | Nội dung trong kế hoạch | Đánh giá |
|---|---|---|
| **1** | Buộc mở `game9k.com` để nhân vật xuất hiện / bấm Nitro | ✅ **Đúng, và là ý hay nhất của cả kế hoạch** |
| **2** | Tách 2 lớp: cổng = đua đơn / Ghost Race; livestream = Streamer Mode đọc DB | ✅ **Đúng, và rẻ hơn kế hoạch nghĩ** — xem §2 |
| **3** | Không bắt tạo tài khoản ở ván đầu, chỉ hỏi khi muốn giữ vật phẩm | ✅ **Đúng** |
| **4** | "Cách này giữ game nằm gọn trong nhóm **G4**" | ❌ **Không kiểm chứng được — và đang gánh quá nhiều.** Xem §1 |
| **5** | "Mỗi ván 30–60 giây tạo khoảng nghỉ tự nhiên để hiện quảng cáo" | ⚠️ **Sai cả về chính sách lẫn kinh tế.** Xem §3 |
| **6** | **Đội ngũ Game9K tự dựng bản mẫu đầu tiên** | ❌ **Trái nguyên tắc đã ghi.** Xem §5 — và có cách giữ được cả hai |
| **7** | Người xem vừa xem live vừa bấm Nitro trên web | ❌ **Không làm được trên điện thoại.** Xem §2.3 — đây là chỗ kế hoạch sẽ vỡ khi chạy thật |

---

## 1. Nhóm G4 — giả định đang gánh quá nhiều

Kế hoạch dùng "nằm gọn trong G4" như một **kết luận**. Trong `docs/08` §Câu 2, nó là **một câu hỏi đang chờ luật sư**:

> *"Những game này có thể xếp **G4** và **miễn** Giấy xác nhận thông báo phát hành không? Nếu vẫn phải có giấy, xin cho biết **căn cứ điều khoản** — vì chúng tôi đọc Điều 37 và chưa thấy tiêu chí loại trừ rõ ràng."*

Nghĩa là: **chính tài liệu pháp lý của Game9K đã ghi rằng chưa tìm thấy căn cứ.** Không thể lấy một câu hỏi mở làm nền cho kiến trúc.

Và kế hoạch **vô tình làm khó câu hỏi đó hơn**, không dễ hơn:

| Thành phần trong kế hoạch | Tác động tới lập luận "chỉ là G4" |
|---|---|
| Nhân vật của khán giả **xuất hiện trong cuộc đua của người khác** | Có **tương tác giữa người chơi** — đúng thứ `docs/08` §Câu 2 dùng để biện minh "không gọi máy chủ, không tương tác" |
| Bảng xếp hạng lưu trên Supabase | Có **lưu dữ liệu người chơi** — `docs/08` §Câu 1 đã nêu đây là yếu tố khiến cổng có thể bị xếp vào nhóm **cung cấp dịch vụ**, không chỉ phân phối |
| Streamer Mode hiển thị tên người thật | Có **hiển thị dữ liệu người chơi cho bên thứ ba** — cần sự đồng ý, và có thể là dữ liệu cá nhân |

> ⚠️ **Kết luận thay thế:** đừng thiết kế để "vừa G4". Thiết kế để **nếu bị xếp nhóm cao hơn, sản phẩm vẫn chạy được** — tức là tách phần *đua* khỏi phần *có tài khoản + xếp hạng*, và ghi rõ phần nào bật/tắt được. Đây là cùng cách whitepaper đã xử lý NQ `05/2025` (có `Off-Chain Fallback`).

**Việc cần làm:** thêm **câu hỏi 5** vào `docs/08`: *"Nếu cổng có bảng xếp hạng và hiển thị tên người chơi trên livestream của bên thứ ba, phân loại thay đổi thế nào, và cần consent dạng nào?"* — chờ luật sư, **không** chặn việc dựng bản mẫu.

---

## 2. Kiến trúc — chỗ này kế hoạch đúng hướng nhưng rẻ hơn nhiều

### 2.1. Bỏ hẳn "real-time" theo nghĩa netcode

Kế hoạch lo "máy chủ WebSocket tốn kém". Đúng — nhưng **không cần** WebSocket, và cũng **không cần** Supabase Realtime.

**Cách đúng: đua tất định, phát lại (deterministic replay).**

```
Kết quả ván đua  =  f( seed ,  danh sách người vào ,  lệnh boost kèm timestamp ,  tham số nhân vật )
```

- `seed` do server sinh **một lần** cho mỗi ván, công bố trước giờ đua.
- Mọi lệnh `boost` chỉ là **một dòng có timestamp** ghi vào DB.
- Không ai "chạy đua" ở thời gian thực. Tất cả tính cùng một hàm, ra cùng một kết quả.
- Server **không** phải giữ kết nối nào trong lúc đua. Chỉ cần: một dòng `INSERT` khi vào, một dòng khi bấm boost, một lượt tính kết quả khi hết giờ.

> **Vì sao quan trọng:** nó chuyển bài toán từ *"nuôi 5.000 kết nối đồng thời"* thành *"đọc ghi vài nghìn dòng trong 60 giây"* — Cloudflare + Supabase làm được. Và nó làm ván đua **kiểm chứng lại được**: bất kỳ ai có `seed` + danh sách lệnh đều dựng lại đúng kết quả. Cùng tinh thần với `base_sha256` + Inspector.

**Hệ quả phụ rất đáng giá:** ván đua trở thành **bằng chứng**, không phải lời tuyên bố. Đây là thứ Game9K có mà đối thủ không có.

### 2.2. Streamer Mode chỉ cần đọc, không cần đẩy

Kế hoạch đã đúng. Bổ sung: Streamer Mode **poll mỗi `2` giây** một view đã tổng hợp sẵn (materialized), **không** subscribe từng dòng. Với `300` người vào một ván, đẩy từng dòng sẽ tốn hơn nhiều so với một lần đọc.

### 2.3. Chỗ kế hoạch sẽ vỡ: hai màn hình, một điện thoại

Đây là lỗi thực thi nghiêm trọng nhất, và nó **không** hiện ra khi thử trên máy tính.

> **Trên điện thoại, mở trình duyệt từ link trong TikTok sẽ làm phiên live bị dừng hoặc mất tiếng.** Khán giả **không thể** vừa xem live vừa bấm Nitro cùng lúc. Mà phần lớn khán giả là mobile.

Kế hoạch §4 bước 2 viết *"chọn nhân vật và bấm nút tương tác ngay"* — với mobile, người dùng phải **rời live để bấm**, rồi **quay lại live**, và lúc quay lại thì ván đã xong.

**Cách sửa — đổi từ "bấm đồng thời" sang "xếp lệnh trước":**

| Trước | Sau |
|---|---|
| Vào phòng → bấm Nitro **trong lúc** đua | Vào phòng **trước** giờ đua → **xếp sẵn `3` lệnh** (boost, chướng ngại) → đóng tab → quay lại xem live |
| Người dùng phải ở hai nơi cùng lúc | Người dùng chỉ cần **`5–8` giây** trên web, rồi về lại TikTok |
| Kết quả hiện trên web, người dùng không thấy | Kết quả hiện **trên live**; web chỉ cần một **màn tổng kết** cho lần quay lại sau |

> **Đây là thay đổi quan trọng nhất trong tài liệu này.** Nó biến "second-screen" từ một hành vi **không khả thi trên mobile** thành một hành vi **khả thi**: một lần chạm, rồi rời đi.

**Thêm:** cho phép **xếp lệnh cho ván kế tiếp** ngay trên màn tổng kết — người chơi chuẩn bị trước, không phải quay lại giữa ván.

---

## 3. "30–60 giây = khoảng nghỉ tự nhiên cho quảng cáo" — sai hai lần

**Sai về chính sách.** Quảng cáo xen kẽ (interstitial) gắn với mỗi ván `30–60` giây là **tần suất cao**, và các mạng quảng cáo lớn giới hạn tần suất interstitial + cấm đặt quảng cáo để "khuyến khích bấm". Cần **rewarded ad do người dùng chủ động chọn** — đúng thứ whitepaper đã mô hình hoá (`rewardedBreak`), **không** phải interstitial tự bật. *(Chính sách cụ thể của từng mạng: **chưa** đối chiếu điều khoản gốc — cần kiểm trước khi thiết kế màn hình.)*

**Sai về kinh tế — và đây là phần đáng nói hơn.** Với `eCPM $1–$3` (biên bảo thủ, `WHITEPAPER §192`):

```
1.000 phiên × 2 lượt hiển thị = 2.000 impression
2.000 ÷ 1.000 × $1–$3        = $2 – $6 mỗi 1.000 phiên
```

| Phiên/tháng | Doanh thu Ads ước tính |
|---|---|
| `10.000` | `$20 – $60` |
| `100.000` | `$200 – $600` |
| `1.000.000` | `$2.000 – $6.000` |

> **Kết luận:** game đua **không phải nguồn doanh thu.** Nó là **chi phí thu hút người dùng (CAC)**, và phải được đo bằng *"bao nhiêu người ở lại cổng"*, không bằng *"bao nhiêu USD quảng cáo"*. Đừng để kế hoạch dựa vào vế thứ hai.

Điều này **không** phá kế hoạch — nó **đổi thước đo**. Bỏ câu "tối ưu doanh thu quảng cáo" khỏi phần lý do, thay bằng "chi phí để một người xem TikTok trở thành một người chơi có phiên hợp lệ".

---

## 4. C3 — lỗi mà `docs/16` đã cảnh báo, và cách sửa tại chỗ

`docs/16` §3.2 chấm thể loại đua vịt `4/10` vì **C3 = `0`**: người xem **không điều khiển gì** → `input_entropy_score` thấp → PoP **lọc oan người thật**.

Kế hoạch mới **sửa được một nửa**: người chơi phải **bấm nút** trên web. Nhưng nếu chỉ bấm `3` lần trong `60` giây thì entropy vẫn thấp.

**Cách sửa đúng — để chính cơ chế đua sinh ra entropy:**

| Làm | Không làm |
|---|---|
| Nút Nitro là **nhịp đều**, cần bấm đúng cửa sổ thời gian (`±150 ms`) → tạo mẫu thời gian thật | Nút bấm một lần rồi chờ |
| Màn "xếp lệnh" là **kéo thả / chọn ô** — cần vài thao tác có hướng | Chỉ có một nút "Tham gia" |
| Sau ván, `1` ván luyện tập `90` giây trên cổng (đúng C2 của `docs/16`) | Đẩy người chơi thẳng về TikTok |

> **Nguyên tắc:** cổng **không** được nhận một phiên mà nó biết là không đo được. Nếu người chơi chỉ xem, họ vẫn được chơi — nhưng **không** được tính `work`, và phải **nói rõ** (xem `docs/15` §3-A3: hiện một dòng lý do).

---

## 5. "Game9K tự dựng bản mẫu" — trái nguyên tắc, và có cách giữ được cả hai

`WHITEPAPER §288` ghi rõ trong **3 điều chủ đích KHÔNG làm**: *"Không tự làm game cạnh tranh studio"*. Lý do không phải giáo điều — đó là **lý do studio tin cổng**.

Nếu Game9K tự làm game neo, ba thứ xấu đi cùng lúc:

| Xấu đi | Vì sao |
|---|---|
| **Vị thế trung lập của Arena** | Studio sẽ hỏi: game của chính cổng có được xếp hạng ưu tiên trên Arena không? |
| **Tính khách quan của `VPH` / Player Fit** | Bên đo và bên được đo là một |
| **Điều kiện dừng** (`≥ 500` người chơi thật/tuần) | Game của chính mình luôn có lợi thế hiển thị → con số `500` mất nghĩa |

**Nhưng ý định "làm chuẩn cho studio khác học" là đúng và đáng giữ.** Bốn cách làm mà không phá nguyên tắc:

| | Cách | Đánh giá |
|---|---|---|
| **P1** | **Tài trợ một studio** dựng game neo; Game9K viết **spec + hợp đồng mốc**, không viết code | ✅ **Đề xuất.** Đúng tiền lệ: cổng tài trợ nội dung, không sản xuất nội dung |
| **P2** | Game9K làm **bộ khung mã nguồn mở** (SDK + mẫu Streamer Mode), **không** làm game | ✅ Tốt. Đây là "làm chuẩn" đúng nghĩa: chuẩn *tích hợp*, không chuẩn *nội dung* |
| **P3** | Game9K làm game nhưng **không đưa lên Arena, không nhận vốn, gắn nhãn "demo kỹ thuật"** | ⚠️ Chấp nhận được, nhưng phải **công khai** nhãn đó |
| **P4** | Game9K làm và đưa lên cổng như game thường | ❌ **Không.** Đây là thứ `§288` cấm |

> **Đề xuất: P2 + P1.** Game9K công bố **mẫu tích hợp** (SDK `simulate`, mẫu Streamer Mode, định dạng file kịch bản ván đua) dưới dạng mở; **một studio** làm game đầu tiên và nhận tài trợ theo mốc. Đạt đúng mục tiêu "làm chuẩn cho studio khác học" mà không đặt cổng vào vị thế vừa trọng tài vừa thí sinh.

---

## 6. Ba bẫy còn lại — đánh giá

### Bẫy 1 (chỉ xem chay) — ✅ Sửa đúng

Cơ chế second-screen là câu trả lời đúng. Bổ sung §2.3 (xếp lệnh trước) và §4 (entropy).

### Bẫy 2 (G1 + quá tải) — ✅ Hướng đúng, ⚠️ lý do sai

Tách 2 lớp là đúng. Nhưng **lý do** không phải "để vừa G4" (§1), mà là **để không phải nuôi kết nối thời gian thực** (§2.1). Nhóm G4 là **kết quả có thể có**, không phải mục tiêu thiết kế.

### Bẫy 3 (TikTok quét cá cược) — ✅ Đúng, và quan trọng hơn kế hoạch nghĩ

Đồng ý hoàn toàn. Ba bổ sung cụ thể:

| Rủi ro | Cách tránh |
|---|---|
| Hình ảnh đua ngựa/đua vịt + "về đích" + "đặt cược" | **Tránh chữ "cược", "đặt", "ăn tiền", "x2", "x5"** trong tên vật phẩm và overlay |
| Tên người thắng hiện như bảng kết quả cá độ | Hiện **"Bảng thành tích"**, không hiện "Kết quả" |
| Nhắc `game9k.com` bằng lời nhiều lần trong live | Đặt ở **bio + bình luận ghim**, không đọc lặp lại. Nói tên miền lặp lại dễ bị hạn chế hiển thị |
| Nhắc "token", "Solana", "đổi thưởng" | **Tuyệt đối không.** Kế hoạch đã đúng — tài liệu này chỉ xác nhận lại thành luật cứng |

> **Bổ sung quan trọng:** quà tặng trên TikTok **không được** ảnh hưởng thứ hạng đua. Đó là pay-to-win và là đúng thứ sẽ bị đọc thành cá cược. Quà chỉ đổi vật phẩm trang trí, và phải ghi rõ trên màn hình.

---

## 7. Funnel — sửa 4 chỗ

| Bước trong kế hoạch | Sửa |
|---|---|
| 1. KOL ghim bình luận mời vào link | ✅ Giữ. Thêm: **nêu rõ "không cần đăng nhập"** — đây là câu quan trọng nhất để giảm bỏ ngang |
| 2. Mở web, chọn nhân vật, bấm ngay | ⚠️ Sửa: **chọn + xếp `3` lệnh + đóng tab** trong `≤ 8` giây (§2.3) |
| 3. Hết ván → màn tổng kết + nút "chơi luyện tập" | ✅ Giữ. Thêm: màn tổng kết **mở được khi quay lại** (không cần đúng lúc) |
| 4. Hỏi tạo tài khoản khi muốn giữ vật phẩm | ✅ Giữ — nhưng **không** dùng đăng ký làm điều kiện nhận `SPARK`. Xem §8 |

---

## 8. Chỗ kế hoạch chưa nối vào luật đã có

`docs/16` §4 đã chỉ ra: referral chỉ trả khi người được mời đạt **Bronze ≈ `89,9` phút** `work`. Một làn sóng người chơi từ game đua (phiên `60` giây) **sẽ không bao giờ** tới ngưỡng đó.

**Nếu làm game đua mà không sửa ngưỡng này, chương trình KOL sẽ luôn trông thất bại — dù mọi thứ chạy đúng.**

Ba việc phải làm **trước** làn sóng đầu tiên:

1. Đổi `FR-POP-01`: referral trả theo **`work` tích luỹ `≥ 120` phút**, Tier là huy hiệu (`docs/16` §4-S1).
2. `SPARK` cho người chơi mới **không** phụ thuộc đăng ký — gắn với **ví**, không gắn với tài khoản (§7 bước 4).
3. Người chơi chỉ-xem **không** được tính `work`, và phải thấy lý do (§4, `docs/15` §3-A3).

---

## 9. Từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | Thiết kế dựa trên "chắc chắn là G4" | §1 — `docs/08` ghi rõ **chưa** tìm thấy căn cứ |
| **R2** | Real-time multiplayer có netcode | §2.1 — đua tất định rẻ hơn, và kiểm chứng được |
| **R3** | Bấm Nitro **đồng thời** với lúc xem live | §2.3 — không làm được trên mobile |
| **R4** | Interstitial tự bật mỗi ván | §3 — cần rewarded do người dùng chọn; và doanh thu ở mức `$2–6`/1.000 phiên |
| **R5** | KOL đọc tên miền lặp lại trong live | §6 — rủi ro bị hạn chế hiển thị |
| **R6** | Quà TikTok ảnh hưởng thứ hạng | §6 — pay-to-win, và bị đọc là cá cược |
| **R7** | Game9K vừa làm game vừa xếp hạng nó trên Arena | §5 — phá vị thế trung lập, làm mất nghĩa ngưỡng `500` |
| **R8** | Trả referral theo Tier Bronze cho làn sóng KOL | §8 — người mời không bao giờ nhận được |

## 10. Việc **không** làm trong tài liệu này

- Không chọn tên game, không thiết kế giao diện, không viết code.
- Không sửa `W = 0.60` / `H = 180`; không đổi whitepaper, deck, 4 PDF, schema (**34** bảng).
- Không đưa eCPM hay giá KOL mới — dùng đúng `$1–$3` đã có trong `WHITEPAPER §192`.

## 11. Thứ tự thi công

| # | Việc | Vì sao trước |
|---|---|---|
| **1** | **Sửa `FR-POP-01`** (referral theo `work` tích luỹ) | Không sửa thì mọi làn sóng KOL đều trông thất bại |
| **2** | **Chốt cơ chế "xếp lệnh trước"** trên giấy, thử bằng giấy, không bằng code | Đây là chỗ kế hoạch sẽ vỡ (§2.3); sửa trên giấy rẻ hơn 100 lần |
| **3** | **Đặc tả định dạng ván đua tất định** (`seed`, lệnh, hàm kết quả) + `simulate` mode | Là **hợp đồng tích hợp** — thứ P2 công bố cho studio |
| **4** | **Chọn studio** cho P1, ký theo mốc | Giữ vị thế trung lập (§5) |
| **5** | Dựng **Streamer Mode** (đọc, poll `2` giây) | Rẻ nhất, và dùng lại được cho mọi game khác |
| **6** | Gửi **câu hỏi 5** cho luật sư (§1) | Chạy song song, không chặn |
| **7** | Đo **CAC**: bao nhiêu người xem → bao nhiêu người có phiên hợp lệ `≥ 90` giây | Đây mới là thước đo đúng (§3) |
