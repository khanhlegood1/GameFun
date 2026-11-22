# StreamMix & Similarweb — công cụ tăng trưởng và kỷ luật đo lường

> **Tài liệu sống:** `docs/14-growth-tools-and-measurement.md`
> **Trạng thái:** `SCOPING` — thiết kế, chưa thi công
> **Ngày:** 22/11/2026
> **Nguồn:** `streammix.co` (trang chủ, `/price`, `/banggia`), `similarweb.com`, và ba bài đánh giá độc lập về Similarweb (§2.2)
> **Câu hỏi:** hai site này có gì dùng được cho Game9K?

---

## 0. Kết luận trước

Hai site này **không cùng loại**, và giá trị của chúng nằm ở hai phía đối lập:

| | StreamMix | Similarweb |
|---|---|---|
| Bản chất | **Sản phẩm** — plugin livestream, bán theo giờ | **Dịch vụ dữ liệu** — ước lượng traffic của site người khác |
| Dùng được cho Game9K? | **Có, một phần** — cách đóng gói và cách làm plugin | **Không mua**, nhưng **học kỷ luật** thì rất đáng |
| Thứ đáng lấy nhất | **Bán theo đơn vị đo được, công khai** (A1) + **làm plugin trong công cụ người ta đã dùng** (A2) | **Mọi con số phải có nguồn, ngày, và chiều sai lệch đã biết** (A4) |

Điều đáng nói nhất: **Similarweb là ví dụ về một công ty bán *ước lượng* — và tự ghi rõ giới hạn của ước lượng đó.** Game9K đang có thứ tốt hơn thứ họ bán: **telemetry nhất quán (first-party) từ SDK trong game**. Nhưng trong whitepaper, các con số thị trường hiện **không gắn ngày, không gắn loại nguồn** — đúng cái Similarweb không bao giờ cho phép mình làm.

---

# PHẦN A — StreamMix

## A1. Bằng chứng quan sát được

| Mã | Quan sát | Nguồn |
|---|---|---|
| **S1** | Là **plugin**, không phải nền tảng thay thế: chạy trong **OBS / VMix / Wirecast**, tải bình luận từ TikTok, Facebook, YouTube, Twitch, Twitter | `streammix.co`, trang chủ |
| **S2** | Tính năng tương tác: **ghim bình luận, lọc bình luận theo từ khoá, rút thăm may mắn, thông báo người thắng, quà tặng ảo** | Như trên |
| **S3** | Bán theo **giờ của từng dịch vụ**: `10 / 50 / 100 / 200` giờ cho *Load Comment*, *Forward Stream*, *RTMP Server* | `/price` |
| **S4** | Giá: `$10` (Trial) · `$25` (50 giờ) · `$45` (100 giờ) · `$65` (200 giờ) / 30 ngày. Bản tiếng Việt: `499.000` · `899.000` · `1.299.000` đồng | `/price`, `/banggia` |
| **S5** | Ngoài gói giờ còn **nạp coin**: `2.000` · `8.000` · `20.000` · `40.000` coin | `/price` |
| **S6** | Cùng địa chỉ trụ sở với GoStream: *Khu liền kề 03 Tecco, phường Thành Vinh, Nghệ An*; email hỗ trợ `@gostream.vn` | `streammix.co` + Facebook Page |
| **S7** | **Nhãn gói bị trùng trên trang tiếng Anh:** cả gói `$25` (50 giờ) **và** gói `$65` (200 giờ) đều mang nhãn **"Professional"** | `/price`, truy cập 22/11/2026 |
| **S8** | **Chân trang trang giá tiếng Anh ghi `© 2023 GoStream, Inc.`** trong khi đầu trang ghi `StreamMix` | `/price` |
| **S9** | FAQ còn sai tên sản phẩm: *"**Streamix** is designed to cater to businesses…"* | `/price` |

> **S6–S9 không phải bằng chứng pháp lý** về quan hệ giữa StreamMix và GoStream, và tài liệu này **không** kết luận gì về điều đó. Chúng có nghĩa hẹp hơn: *đây là một công ty vận hành nhiều thương hiệu trên cùng một bộ khung, và các thương hiệu đó đã trôi khỏi nhau.*

Điều S7–S9 nói lên, và nó là bài học đắt: **trang giá là nơi dễ sai nhất trong toàn bộ site** — vì nó là HTML viết tay, nhân bản cho từng ngôn ngữ, không có nguồn duy nhất.

## A2. Lấy gì

### A1 — Bán theo **đơn vị đo được**, và cho người dùng thấy đồng hồ

StreamMix không bán "gói tính năng", họ bán **giờ**. Một đơn vị, ba dịch vụ, ngưỡng rõ ràng. Người mua biết mình còn bao nhiêu.

**Áp dụng vào Game9K:** Game9K đã có đơn vị đo đúng — **`work` = phút chơi hợp lệ** trong `FR-POP-01`. Thiếu đúng một thứ: **người chơi không nhìn thấy đồng hồ**.

| Làm | Không làm |
|---|---|
| Hồ sơ hiển thị: *"hôm nay `184 / 300` phút hợp lệ"*, và còn bao nhiêu để lên hạng kế | Thanh tiến trình trang trí không gắn với `work` thật |
| Cùng một đơn vị cho mọi chỗ: PoP, streak, quest, trần chống bot | Ba đơn vị khác nhau (điểm, giờ, lượt) như StreamMix có "giờ" **và** "coin" |

> **Vì sao quan trọng:** khi người chơi thấy đồng hồ, họ tự điều chỉnh hành vi. Khi không thấy, họ nghi ngờ hệ thống và ngừng chơi. Đây là lý do UX, không phải lý do kinh tế.

### A2 — Làm **plugin trong công cụ người ta đã dùng**, không bắt họ đổi công cụ

StreamMix chạy **bên trong** OBS/VMix/Wirecast. Nó không đòi streamer bỏ công cụ đang dùng.

**Áp dụng vào Game9K:** đây chính là lý do SDK tồn tại, và là lập luận nên **đẩy mạnh hơn** trong tài liệu dành cho studio:

| Đã có | Nên nói rõ hơn |
|---|---|
| SDK nhúng cho Godot / Unity WebGL / Phaser / Three.js | **"Không phải port lại game"** — đó là câu studio cần nghe trước tiên |
| Đo `VPH`, D1/D7, `crash_rate` tự động | **"Không phải tự làm dashboard"** |
| Inspector kiểm `base_sha256` | **"Không phải viết lại build pipeline"** |

### A3 — Ba nguyên thuỷ tương tác, nhưng chỉ lấy một

StreamMix có *ghim bình luận*, *rút thăm*, *quà tặng ảo*. Game9K lấy **một**, ở dạng kiểm chứng được:

| Nguyên thuỷ | Áp dụng cho Game9K | Vì sao |
|---|---|---|
| **Rút thăm may mắn** | ✅ **Có** — rút thưởng **chỉ trong tập ví đã qua PoP ≥ Bronze**, dùng random seed công khai (commit-reveal) | Rẻ, tăng tương tác, và biến chống bot thành **lợi ích nhìn thấy được**: bot không được tham gia |
| **Ghim bình luận** | ✅ **Có, dạng nhẹ** — "ghim" một **game/quest của tuần** trên trang chủ | Cùng cơ chế, cùng chi phí gần bằng 0 |
| **Quà tặng ảo** | ❌ **Không** | Trùng chức năng với tip/doanh thu Ads, và tạo thêm một đơn vị tiền (§B-R1) |

## A3. Từ chối gì

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | **Nạp coin** (S5) làm đơn vị tiền thứ hai | Game9K đã có `SPARK`. Thêm "coin" nạp trước là **đơn vị lưu trữ giá trị**, kéo theo câu hỏi về ví điện tử/thanh toán mà legal brief đang chờ luật sư — để đổi lấy một tính năng không ai xin |
| **R2** | **Bảng giá viết tay theo từng ngôn ngữ** | S7 chứng minh cái giá: cùng một công ty, hai trang, nhãn gói lệch nhau. Giá và nhãn phải sinh từ **một nguồn** |
| **R3** | **Thương hiệu / pháp nhân / năm bản quyền viết rải rác** | S8, S9: chân trang ghi tên công ty khác, FAQ gọi sai tên sản phẩm. Với Game9K đây là **ci phải chặn**, không phải lỗi cần nhớ |

> **Quy tắc rút ra cho Game9K, kiểm tra được bằng máy:** tên thương hiệu, tên pháp nhân, năm bản quyền, và bảng giá **chỉ được xuất hiện từ một nguồn duy nhất** trong repo. Hiện đã có tiền lệ tốt: số `34` bảng trong `docs/02` và tỷ lệ `50/50` trong whitepaper đều là số sinh từ script và được CI kiểm.

---

# PHẦN B — Similarweb

## B1. Similarweb bán gì

| Mã | Quan sát | Loại nguồn |
|---|---|---|
| **W1** | Ước lượng traffic/engagement cho site **mình không sở hữu**, từ **panel clickstream** + đối tác ISP + site tự chia sẻ số liệu + crawler công khai | Tự công bố |
| **W2** | Tự nêu giới hạn: panel **không thấy** lưu lượng API, giá trị hợp đồng doanh nghiệp, và traffic đi qua nền tảng cloud | Tự công bố |
| **W3** | Tự nêu: "**không có một nguồn sự thật duy nhất**"; "tự tin hơn" với site trên **`100.000` lượt/tháng**; hai công cụ đo trực tiếp có thể lệch **tới `30%`** trên cùng một site | Tự công bố |
| **W4** | Không công bố **khoảng tin cậy** cho từng con số | Tự công bố (thiếu) |
| **W5** | Nghiên cứu PLOS ONE 5/2022 (Jansen, Jung, Salminen), **86 site / 26 nước**: so với Google Analytics, Similarweb thấp hơn **`19,4%`** về lượt truy cập, **`38,7%`** về người dùng duy nhất; bounce cao hơn **`25,2%`**, thời lượng phiên cao hơn **`56,2%`**. Sai lệch **có hệ thống**, nhưng **thứ hạng giữa các site tương quan mạnh** | Bên thứ ba, có bình duyệt |
| **W6** | Ngưỡng thực dụng được các bài đánh giá nêu: dưới **`5.000`–`50.000` lượt/tháng** thì số liệu chỉ dùng để **so thứ hạng**, không dùng làm số tuyệt đối; dữ liệu cập nhật **theo tháng** | Bên thứ ba, ý kiến nghề |

## B2. Lấy gì

### A4 — Một con số phải có **ba thứ**: nguồn, ngày, chiều sai lệch đã biết

Đây là bài học đáng giá nhất, và nó **miễn phí** — không cần mua gói nào.

**Vấn đề hiện tại của Game9K:** `docs/WHITEPAPER.md` dòng 310 nêu `Poki 100M+ MAU`, `CrazyGames 60M+ MAU, ~3 tỷ lượt chơi/năm`, và thị trường `8–10 tỷ USD/năm`. **Không có ngày, không có loại nguồn, không có chiều sai lệch.** Đó đúng là kiểu trích dẫn mà chính Similarweb không cho phép trong sản phẩm của họ.

**Đề xuất — sổ số liệu thị trường.** Một bảng duy nhất, mỗi dòng là một con số dùng ở deck/whitepaper:

| Cột | Nội dung |
|---|---|
| Con số | `100M+ MAU` |
| Nơi dùng | `WHITEPAPER §… dòng 310`, slide nào của deck |
| Nguồn | tên tổ chức + đường dẫn |
| Ngày | ngày công bố, **và** ngày truy cập |
| Loại | *quan sát trực tiếp* / *tự công bố* / *bên thứ ba* / *tự đo lại* |
| Sai lệch đã biết | ví dụ: *"panel thường thấp hơn GA `19,4%`"* |
| Được dùng để làm gì | *"nêu quy mô thị trường"* — **không** dùng để suy ra SOM |

> ⚠️ **Quy tắc cứng đề xuất:** số liệu **không** có đủ 6 cột trên thì **không được** vào deck gọi vốn. Hiện có **3** con số ở dòng 310 chưa đạt; tài liệu này **không** sửa whitepaper (sửa = dựng lại PDF + deck), chỉ ghi nhận khoản nợ.

### A5 — First-party telemetry là tài sản, và phải nói ra như một lợi thế

Similarweb bán **ước lượng từ mẫu**. Game9K có **đo trực tiếp từ SDK** trong chính game: `VPH`, D1/D7, `crash_rate`, heartbeat tiền cảnh. Đây là loại dữ liệu mà không panel nào mua được, và không đối thủ nào chép được.

**Áp dụng:** trong phần cạnh tranh của whitepaper, nói thẳng:

> "Chúng tôi không ước lượng bằng panel. Chúng tôi đo bằng SDK trong game, trên từng studio, từng bản build, có `base_sha256`."

Điều này **không** thay đổi con số nào; nó đổi **cách định vị**. Và nó là câu trả lời trực tiếp cho câu hỏi nhà đầu tư luôn hỏi: *"số liệu của bạn lấy từ đâu và ai kiểm chứng được?"*

### A6 — Chỉ dùng số panel để **so thứ hạng**, không để **định giá**

Từ W5: sai lệch **có hệ thống** nhưng **thứ hạng tương quan mạnh**. Nghĩa là:

| Được | Không được |
|---|---|
| "Poki lớn hơn CrazyGames" | "Poki có đúng 100M MAU" |
| "Nhóm cổng game xếp theo độ lớn là A > B > C" | Nhân số panel với eCPM để ra doanh thu dự kiến |

Game9K đã làm đúng một lần ở whitepaper: mô hình Ads dùng **`eCPM $1–$3`** (biên bảo thủ cho traffic ĐNÁ) kèm bảng độ nhạy 5 bậc, chứ không lấy eCPM cao nhất. **Giữ nguyên tinh thần đó** cho mọi số panel.

## B3. Từ chối gì

| Mã | Nội dung | Lý do |
|---|---|---|
| **R4** | **Mua Similarweb bây giờ** | Game9K chưa có traffic để benchmark. Với site `0` người dùng, panel không có gì để đo — mua bây giờ là trả tiền cho số liệu về **người khác**, trong khi thứ cần đo là **của mình** |
| **R5** | Dùng số Similarweb để **suy ra SOM `$25–45M`** | SOM trong whitepaper đã dựng từ số game/MAU mục tiêu của chính Game9K, không từ panel. Trộn panel vào sẽ làm hỏng chuỗi kiểm chứng |
| **R6** | Trích số traffic mà **không gắn tháng** | Dữ liệu cập nhật theo tháng (W6) và trôi nhanh; một con số không ngày là con số không kiểm chứng được — đúng điều `AGENTS.md` cấm |

---

## C. Việc **không** làm trong tài liệu này

- Không sửa `docs/WHITEPAPER.md`, không dựng lại PDF, không đụng deck. Ba con số ở dòng 310 được **ghi nhận là khoản nợ** (§A4), không được sửa vội vì sửa là phải dựng lại toàn bộ artefact in.
- Không đổi schema, không thêm bảng.
- Không đổi bất kỳ số liệu kinh tế nào — `50/50`, `eCPM $1–$3`, MOIC `16.8×` giữ nguyên.
- Không mua, không đăng ký dịch vụ nào.

## D. Thứ tự thi công nếu muốn làm

1. **Rẻ nhất, làm ngay được:** dựng `docs/15-market-numbers.md` — sổ 6 cột ở §A4, điền 3 con số dòng 310 + các số thị trường khác đang dùng trong deck. Không đụng PDF.
2. **Sửa nội dung, không sửa số:** thêm vào whitepaper đoạn định vị first-party telemetry (§A5) — chờ đợt dựng PDF tiếp theo, gộp một lần.
3. **Sản phẩm:** hiện đồng hồ `work` trong hồ sơ người chơi (§A1) và rút thăm chỉ trong tập PoP ≥ Bronze (§A3).
4. **Quy tắc CI:** chặn tên thương hiệu / pháp nhân / năm bản quyền / bảng giá nằm ngoài nguồn duy nhất (§R3).

> **Điểm chung của cả hai site:** cả hai đều **bán sự rõ ràng** — StreamMix bán "bạn còn `50` giờ", Similarweb bán "con số này đến từ đâu và sai bao nhiêu". Game9K mạnh hơn cả hai ở chỗ có dữ liệu thật, và yếu hơn cả hai ở chỗ **chưa ghi nguồn cho những con số mình đã công bố**. Sửa cái thứ hai rẻ hơn nhiều so với tưởng.
