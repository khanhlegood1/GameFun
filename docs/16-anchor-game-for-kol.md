# Game neo cho KOL — có nên, và nên là game nào

> **Tài liệu sống:** `docs/16-anchor-game-for-kol.md`
> **Trạng thái:** `SCOPING`
> **Ngày:** 22/11/2026
> **Tham chiếu:** video *"StreamMix — Hướng dẫn tạo game tương tác đua vịt trên livestream qua live tiktok studio"* (12/10/2023, 5:00, ~11.5K lượt xem), kênh `@streammixtool`
> **Câu hỏi:** có nên chọn một game kiểu đua vịt để KOL kéo người vào cổng Game9K? Nên là game nào?

---

## 0. Kết luận trước

**Có nên có một game neo — nhưng không phải đua vịt, và Game9K không tự làm nó.**

| Câu hỏi | Trả lời ngắn |
|---|---|
| Có nên có **một** game neo cho KOL? | **Có.** KOL cần thứ *xem hiểu trong 3 giây*. Cổng game 1.200 tựa không cho được điều đó |
| Game đó có nên là **đua vịt / game quà tặng**? | **Không.** Đo được: nó **không tạo ra `work`**, và nó biến quà tặng thành điều kiện thắng (§4) |
| Game9K có nên **tự làm** game đó? | **Không.** Vi phạm nguyên tắc đã ghi: *"Không tự làm game cạnh tranh studio"* (`WHITEPAPER §288`). **Tài trợ một studio** làm, hoặc dùng game có sẵn |
| Vậy nên chọn **game nào**? | **Thể loại "một nút, một biến số", phiên `90–180` giây, có thử thách hằng ngày** (§3, chấm `9/10`) |
| Rủi ro lớn nhất? | **Không phải chọn sai game — mà là ngưỡng Bronze `90` phút đấu với phiên chơi `2` phút** (§4). Đây là lỗi thiết kế đang có, không phải rủi ro của KOL |

---

## 1. Vì sao đua vịt không dùng làm game neo

### 1.1. Video đó thực chất làm gì *(quan sát trực tiếp, bản ghi lời thoại)*

| Bước | Cú pháp / thiết lập |
|---|---|
| Người xem **bình luận** theo cú pháp để tạo nhân vật | `create character` |
| Giới hạn số người chơi một lượt | `maximum character` |
| Thời lượng một lượt đua | `running time` |
| **Điều kiện thắng:** hai chế độ — **ngẫu nhiên**, hoặc **tương tác** (một like / bình luận / **quà tặng** = bao nhiêu điểm) | `set go for winner` |
| Số người hiện trên bảng về đích | `winner number` |
| Biến thể cùng khung | đua xe, đua ngựa |

**Nhận xét:** đây **không phải một game** theo nghĩa người chơi điều khiển. Đây là **một bảng xổ số có hình ảnh đẹp**, chạy trong iframe, lấy like/quà làm biến đầu vào.

### 1.2. Vì sao nó không chuyển được sang Game9K

| Vấn đề | Hệ quả với Game9K |
|---|---|
| **Người xem không điều khiển gì.** Họ bình luận, rồi *xem* một hoạt ảnh chạy | `input_entropy_score` (`docs/02` §382) sẽ **thấp** — đúng dấu hiệu "tab treo / auto-clicker" mà bộ lọc PoP dùng để loại bot. Game9K sẽ **lọc chính người thật của mình** |
| **Like và quà làm tăng tốc** | Ai trả tiền nhiều thì thắng. Đây là **pay-to-win** đặt ở đúng chỗ Game9K tuyên bố không đứng: *"Không kiếm tiền từ việc người chơi thua lỗ"* (`§288`) |
| **Một lượt `30–60` giây** | Không tạo ra `work` theo đơn vị phút hợp lệ. Người chơi ở lại 5 phút được `5` phút `work`, nhưng phần lớn thời gian là **chờ** |
| **Chế độ "ngẫu nhiên"** | Người thắng do RNG, không do chơi. Trùng khớp với thứ `FR-POP-01` cấm: điểm **không mua được và phải do chơi mà có** |
| **Tặng quà trong livestream có thưởng** | Về mặt pháp lý, đây là **khuyến mại có thưởng**. Cần luật sư xác nhận nghĩa vụ đăng ký/thông báo với cơ quan quản lý thương mại — **chưa kiểm chứng**, thêm vào danh sách câu hỏi pháp lý đang chờ |

> **Không** phải đua vịt là sản phẩm dở. Nó rất hợp với GoStream/StreamMix: họ bán **giờ livestream tương tác**, và tương tác cao = khách hàng ở lại. Game9K bán **phiên chơi đã kiểm chứng** — hai đơn vị khác nhau, hai thước đo khác nhau.

---

## 2. Nếu vẫn muốn dùng đúng *định dạng* đó

Tách ba lớp, giữ hai, bỏ một:

| Lớp | Giữ? | Phiên bản cho Game9K |
|---|---|---|
| **Vào bằng bình luận** | ✅ Giữ ý tưởng | Đổi sang **vào bằng một cú bấm** (passkey / ví đã có ở ADR-007). Không bắt bình luận — Game9K không đọc được comment TikTok |
| **Bảng về đích công khai** | ✅ Giữ | Có, nhưng hạng tính bằng **`work` hợp lệ**, không bằng quà |
| **Like / quà để tăng tốc** | ❌ **Bỏ** | Đổi thành **"chơi càng đúng càng nhanh"** — tăng tốc bằng kỹ năng, không bằng tiền. Nếu vẫn muốn có quà: quà **không** ảnh hưởng thứ hạng, chỉ đổi vật phẩm trang trí |

> **Một câu để nhớ:** đua vịt biến **sự chú ý** thành **tương tác**. Game9K phải biến **tương tác** thành **phiên chơi kiểm chứng được**. Đó là toàn bộ khác biệt.

---

## 3. Vậy nên là game nào

### 3.1. Năm tiêu chí, chấm `0–2` điểm mỗi tiêu chí

| # | Tiêu chí | Vì sao | `0` | `2` |
|---|---|---|---|---|
| **C1** | **Hiểu trong 3 giây** | KOL chỉ có 3 giây để người xem quyết định bấm vào | Phải giải thích luật | Nhìn là hiểu |
| **C2** | **Phiên `90–180` giây** | Khớp ngưỡng `active_gameplay_sec ≥ 90` đã có trong `PRD §199` | `< 60` giây hoặc `> 10` phút | `90–180` giây |
| **C3** | **Mật độ thao tác cao** | `input_entropy_score` cao = PoP đo sạch, **không lọc oan người thật** | Ngồi xem, thỉnh thoảng bấm | Bấm liên tục có nhịp |
| **C4** | **Chi phí nội dung gần `0`** | Không phải chi phí code — chi phí **duy trì nội dung** | Cần viết mới mỗi ngày | Sinh ngẫu nhiên được |
| **C5** | **Lý do quay lại hằng ngày** | KOL đưa người vào **một lần**; D1/D7 do game giữ | Không có | Có thử thách ngày |

### 3.2. Chấm năm ứng viên

| Ứng viên | C1 | C2 | C3 | C4 | C5 | **Tổng** | Ghi chú |
|---|---|---|---|---|---|---|---|
| **Một nút, một biến số** *(endless runner / stacker / helix)* | 2 | 2 | 2 | 2 | 1 | **`9/10`** | ✅ **Chọn cái này** |
| Quiz / thử thách chữ hằng ngày | 2 | 1 | 1 | **0** | 2 | `6/10` | C4 = `0`: mỗi ngày cần câu hỏi mới → chi phí nội dung **vĩnh viễn** |
| Game `.io` nhiều người cùng lúc | 2 | 2 | 2 | 1 | 1 | `8/10` | Điểm cao, nhưng cần **netcode + server** — vượt xa "game neo" |
| Idle / clicker | 2 | 1 | **0** | 2 | 2 | `7/10` | C3 = `0` là **trọng yếu**: PoP sẽ lọc oan chính người chơi thật |
| **Đua vịt trên livestream** | 2 | **0** | **0** | 2 | 0 | `4/10` | ❌ C2 và C3 cùng `0` |

> **C3 = `0` là điểm chí tử, không phải điểm trừ nhỏ.** Nó không làm game kém vui — nó làm **hệ thống thưởng của Game9K từ chối người chơi thật.** Đây là loại lỗi không sửa được bằng marketing.

### 3.3. Đề xuất cụ thể

**Game neo nên là: một tựa "một nút" có sẵn, chạy trong iframe, phiên `90–180` giây, kèm một thử thách sinh ngẫu nhiên mỗi ngày.**

Ba ràng buộc khi chọn:

1. **Ưu tiên game đã có trên cổng** hoặc **mã nguồn mở dùng được** (Phaser/Godot) — không đặt hàng studio làm mới ở giai đoạn này.
2. **Phải chạy được với `simulate` mode của SDK** (`docs/15` §2-A1) trước khi KOL chạm vào — KOL không thể là người test đầu tiên.
3. **Nếu không tìm được tựa nào đạt `≥ 8/10`** → **không làm game neo**, dùng cách khác (§5.3).

---

## 4. Lỗi thiết kế mà câu hỏi này làm lộ ra

Đây là phần quan trọng nhất của tài liệu, và nó **không** phải về KOL.

`FR-POP-01` quy định referral **chỉ trả khi người được mời đạt Bronze**. Với `W = 0.60`, `H = 180`, Bronze cần **`work ≈ 89,9` phút** *(tính lại từ công thức đã kiểm chứng, `scripts/verify_pop_decay.py`)*.

| Nếu một phiên chơi dài | Số phiên để tới Bronze |
|---|---|
| `2` phút *(đua vịt, game giải trí nhanh)* | **`45` phiên** |
| `5` phút | **`18` phiên** |
| `15` phút | **`6` phiên** |

> ⚠️ **Hệ quả:** nếu KOL kéo về một làn sóng người chơi phiên ngắn, người mời **không bao giờ** nhận được thưởng referral — vì phần lớn sẽ bỏ trước phiên thứ `45`. Chương trình KOL sẽ **trông như thất bại** dù nó hoạt động đúng như đã viết.

**Cách sửa, ba lựa chọn — không cái nào cần đổi `W`/`H`:**

| | Cách | Đánh giá |
|---|---|---|
| **S1** | Trả referral theo **tổng `work` tích luỹ `≥ 120` phút**, không theo Tier. Tier vẫn là **huy hiệu**, không phải điều kiện trả tiền | ✅ **Đề xuất.** Tách "trạng thái" khỏi "điều kiện thanh toán" — hai thứ đang bị buộc vào nhau |
| **S2** | Hạ ngưỡng referral riêng xuống `≥ 30` phút tích luỹ | Đơn giản hơn, nhưng mở đường farm nhanh hơn `30` phút |
| **S3** | Thưởng làn sóng KOL bằng **`SPARK`** (không chuyển nhượng) ngay, referral tiền mặt vẫn chờ Bronze | An toàn nhất về gian lận, nhưng người mời không thấy tiền → ít động lực |

**Khuyến nghị: S1 + S3.** `SPARK` ngay lập tức cho người chơi mới (phần thưởng *của chính họ*), tiền referral chỉ mở khi **`work` tích luỹ `≥ 120` phút** (không phải Tier).

---

## 5. Về KOL

### 5.1. Khi nào nên

| Điều kiện | Ngưỡng |
|---|---|
| Cổng đã có **người chơi thật quay lại** | `≥ 500` người chơi thật/tuần — **đúng điều kiện dừng đã ghi** ở `WHITEPAPER §288` |
| Game neo đã qua `simulate` mode + đo được D1/D7 thật | Có số, không phải cảm nhận |
| Đã sửa xong ngưỡng referral (§4) | Nếu không, tiền KOL mua về một chương trình không bao giờ trả thưởng |
| Có cách đo **D1/D7 của riêng làn sóng KOL** | SDK đã có; cần **tag nguồn** trên link/wallet |

### 5.2. Khi nào **không** nên

- Khi cổng chưa giữ được người chơi. **KOL khuếch đại thứ đã có, không tạo ra thứ chưa có.** Cùng logic với `docs/13` §6: trả tiền cho traffic khi cổng chưa giữ người = mua traffic rác.
- Khi game neo chưa qua `simulate`. KOL sẽ là người phát hiện lỗi telemetry — trước mặt `100.000` người.
- Khi chưa có **tag nguồn**. Nếu không, không biết làn sóng nào mang lại người chơi thật, và lần sau vẫn phải đoán.

### 5.3. Nếu không có game neo đạt `≥ 8/10`

Ba lựa chọn thay thế, **không cần game mới**:

1. **"90 giây làm quen PoP"** — một màn tương tác *không phải game*: người xem thấy đồng hồ `work` chạy, thấy một dòng bị lọc kèm lý do, rồi vào cổng. Rẻ, và dạy đúng thứ cần dạy.
2. **KOL chơi game của studio đang xin vốn** — vừa kéo người, vừa là kênh phân phối cho studio. Không vi phạm "không tự làm game".
3. **Chỉ dùng KOL cho nội dung**, không cho chuyển đổi: KOL giới thiệu *câu chuyện* (studio Việt được tài trợ theo cột mốc), không giới thiệu *một game*. Đo bằng lượt xem, không bằng đăng ký.

### 5.4. Về chi phí — số **không** được bịa

Không có giá KOL trong repo, nên tài liệu này **không đưa con số CAC nào**. Công thức cần điền:

```
Hòa vốn khi:   (doanh thu Ads/người chơi × D30)  ≥  (giá KOL ÷ số người chơi thật giữ được)
```

Với `eCPM $1–$3` (biên bảo thủ, `WHITEPAPER §192`), vế trái rất nhỏ. **Kết luận có thể rút ngay không cần số:** KOL phải trả bằng **thương hiệu + phân phối cho studio**, không phải bằng doanh thu Ads của người chơi mới. Nếu bán KOL như một kênh hoàn vốn bằng Ads, phép tính sẽ không đóng.

---

## 6. Từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | Dùng **đua vịt / game quà tặng** làm game neo | §1.2 — không tạo `work`, PoP lọc oan người thật, và là pay-to-win |
| **R2** | Giữ cơ chế **like/quà để tăng tốc** trong bất kỳ game neo nào | Tiền phải **không** đổi được thứ hạng |
| **R3** | **Game9K tự làm** game neo | Vi phạm `WHITEPAPER §288`. Tài trợ studio, hoặc dùng game có sẵn |
| **R4** | Chạy KOL **trước** khi có `500` người chơi thật/tuần | Đảo ngược điều kiện dừng đã ghi trước |
| **R5** | Chọn **idle/clicker** vì "dễ giữ người" | C3 = `0`: `input_entropy` thấp → hệ thống thưởng từ chối người thật |
| **R6** | Chọn **quiz hằng ngày** vì "rẻ" | C4 = `0`: rẻ lúc làm, **đắt vĩnh viễn** vì phải sinh nội dung mỗi ngày |
| **R7** | Đưa một con số CAC/ROI KOL khi chưa có giá KOL | Đúng loại trích dẫn `AGENTS.md` cấm |

---

## 7. Việc **không** làm trong tài liệu này

- Không đổi `W = 0.60` / `H = 180`. §4 chỉ **tách điều kiện thanh toán khỏi Tier**, không đụng công thức.
- Không đổi whitepaper, deck, 4 PDF, schema (**34** bảng).
- Không chọn một **tựa game cụ thể** — không có dữ liệu D1/D7 của bất kỳ tựa nào trong repo, nên chọn tên sẽ là phỏng đoán. Chọn **thể loại + tiêu chí chấm**.
- Không đưa giá KOL, CAC, hay ROI.

## 8. Thứ tự thi công

1. **Sửa `FR-POP-01`**: referral trả theo **`work` tích luỹ `≥ 120` phút`**, Tier là huy hiệu (§4-S1). Đây là việc **cấp bách nhất**, làm trước cả khi nói tới KOL.
2. Chấm `3–5` tựa đang có trên cổng theo bảng §3.1. Ghi điểm **vào tài liệu**, không ghi trong đầu.
3. Chạy `simulate` mode trên tựa thắng. Nếu telemetry sai → loại, chấm tựa khác.
4. Đo D1/D7 của tựa đó **với người chơi hiện có** (không cần KOL). Đạt ngưỡng → mới nói tới KOL.
5. Thêm **tag nguồn** trên link/wallet trước làn sóng KOL đầu tiên.
6. Đưa câu hỏi khuyến mại có thưởng (§1.2, dòng cuối) vào danh sách chờ luật sư — cùng chỗ với 4 câu đang chờ.
