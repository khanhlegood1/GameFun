# Flagship template — kiểm chứng bản kế hoạch "9K Labs + Reskin 48 giờ"

> **Tài liệu sống:** `docs/18-flagship-template-review.md`
> **Trạng thái:** `SCOPING` — phản biện, **chưa** phải đặc tả thi công
> **Ngày:** 22/11/2026
> **Đầu vào:** kế hoạch người sáng lập — 3 nguyên tắc: (1) tách tư cách pháp lý qua **9K Labs** + open-source SDK, (2) kiến trúc **Reskin 48 giờ** trên Cloudflare/Supabase, (3) dùng game mẫu làm **bảng minh chứng doanh thu**
> **Tài liệu liên quan:** `docs/17` (§2.1 đua tất định, §2.3 mobile, §3 kinh tế Ads, §5 P2+P1), `docs/08` (4 câu hỏi pháp lý), `WHITEPAPER §288`

---

## 0. Kết luận trước

**Kế hoạch này tốt hơn kế hoạch trước ở ba điểm, và vẫn còn bốn lỗ — trong đó một lỗ có thể làm hỏng cả cổng.**

| # | Nội dung | Đánh giá |
|---|---|---|
| **1** | Công khai **Game9K Starter Kit** dưới dạng mã nguồn mở | ✅ **Đúng, và đây là đóng góp lớn nhất cho studio** |
| **2** | **Tách logic khỏi đồ họa** bằng file cấu hình JSON | ✅ **Ý hay nhất về kỹ thuật** — và là mầm của một cái bẫy (§3) |
| **3** | Nhúng sẵn **telemetry hooks** (vào game, số lần bấm, tỉ lệ hoàn thành, tỉ lệ quay lại) | ✅ Đúng — trừ **tỉ lệ quay lại** (§6) |
| **4** | Không tự mở bán token cho game mẫu | ✅ **Đúng, và đúng vì lý do đúng** — tránh xung đột lợi ích |
| **5** | **"9K Labs"** đứng tên để giữ vị thế trung gian | ❌ **Thương hiệu độc lập không tạo ra độc lập.** Xem §2 |
| **6** | **Reskin 48 giờ** → studio đổi bộ ảnh thành game mới | ⚠️ **Đúng về kỹ thuật, sai về hệ quả.** Xem §3 — 50 bản reskin sẽ làm Arena vô dụng |
| **7** | **Bảng minh chứng doanh thu Ads** công khai | ❌ **Không thể điền được ở Pre-Seed** — và nếu điền thật, con số sẽ **nhỏ hơn** không công bố. Xem §4 |
| **8** | **Chặn IP Việt Nam** để "chưa cần vướng thủ tục cấp phép" | ⚠️ Chặn IP là **giảm rủi ro**, không phải **cơ sở pháp lý**. Xem §5 |
| **9** | Streamer Mode dùng **Supabase Realtime** | ❌ **Trái `docs/17` §2.1**, và **không sửa** nút thắt thật (mobile). Xem §7 |

> **Câu một dòng:** bản kế hoạch này đã **giải đúng** bài toán "con gà – quả trứng" về mặt *kỹ thuật*, nhưng vẫn **giải sai** bài toán *vị thế*: nó dùng một thương hiệu để giả làm bên thứ ba, trong khi cái cần tách là **quyền từ chối**.

---

## 1. Bốn thứ dùng được ngay

### 1.1. Starter Kit mã nguồn mở — ✅ mạnh nhất

Đây chính là **P2** trong `docs/17` §5, và bạn đã tự đi tới đó. Giá trị thật:

| Cho studio | Vì sao quan trọng |
|---|---|
| Mẫu tích hợp SDK chạy được | Studio không phải đoán `input_entropy` thế nào là "đủ" |
| Mẫu vượt qua Inspector | Rút ngắn vòng lặp từ *"nộp → bị trả"* xuống *"chạy local → tự biết đạt"* |
| Mẫu Streamer Mode | Studio không phải tự nghĩ ra cách hiển thị trên livestream |
| Mẫu `simulate` mode | Đúng `docs/15` §2-A1 |

> **Ghi rõ trong giấy phép:** Starter Kit mở **giấy phép tích hợp**, không mở **nội dung**. Studio dùng khung được; **không** được nộp chính khung đó làm game của mình mà không thay đổi (§3).

### 1.2. Tách logic khỏi đồ họa — ✅ ý hay nhất về kỹ thuật

Đúng, và nên làm **triệt để hơn** kế hoạch: không chỉ ảnh/nhân vật/âm thanh, mà **cả luật chơi** (số chặng, cửa sổ bấm, hệ số tốc độ) nằm trong file cấu hình có **phiên bản và `sha256`**.

Lý do: khi luật chơi nằm trong code, mỗi studio sửa một kiểu → `VPH` không so sánh được. Khi luật chơi nằm trong file có hash, **cùng một hash = cùng một luật**, và Arena so sánh được công bằng. Đây là điều kiện để `docs/17` §2.1 (đua tất định) hoạt động.

### 1.3. Telemetry hooks — ✅ nhưng phải nói rõ nó **không** thay Inspector

Kế hoạch viết telemetry là *"bộ chuẩn để hệ thống tự động quét mã băm bất biến"*. Hai việc khác nhau, đừng gộp:

| Việc | Ai làm | Không thể thay bằng |
|---|---|---|
| Quét `base_sha256`, kiểm build | **Inspector** (offline, trước khi lên cổng) | Telemetry runtime |
| Đo hành vi thật (`input_entropy`, D1/D7) | **Telemetry** (online, sau khi lên cổng) | Hash |

Studio cần hiểu: **hash chứng minh "đây là bản tôi nộp"**, không chứng minh "bản này hay".

### 1.4. Không tự mở bán token cho game mẫu — ✅ và lý do còn mạnh hơn kế hoạch viết

Bạn viết *"tránh xung đột lợi ích giữa người cầm cân nảy mực và người gọi vốn"*. Đúng — và có một lớp nữa: nếu game của chính cổng mở bán token thành công, **mọi studio sẽ nghi ngờ mọi thứ còn lại** — bảng xếp hạng, `VPH`, thứ tự hiển thị. Không có cách nào lấy lại niềm tin đó bằng tài liệu.

---

## 2. "9K Labs" — thương hiệu độc lập **không** tạo ra độc lập

Đây là lỗ nghiêm trọng nhất về mặt *vị thế*, và nó **không sửa được bằng cách đặt tên**.

### 2.1. Phép thử duy nhất

> **Game9K có thể từ chối game của 9K Labs không?**

Nếu câu trả lời là *"không"* (vì cùng đội, cùng lương, cùng nhà đầu tư) → **9K Labs không phải bên thứ ba**, chỉ là **nhãn dán**. Và lúc đó `game9k.com` đã **là** một studio phát hành game, đúng như điều kế hoạch muốn tránh.

Việc đổi thương hiệu còn **tệ hơn** để nguyên: nó **giả** làm bên thứ ba. Nhà đầu tư và studio đều tra được. Một nhãn bị phát hiện là giả sẽ **làm mất giá mọi tuyên bố trung lập khác** — kể cả những cái đúng.

### 2.2. Ba điều kiện để thật sự độc lập

| # | Điều kiện | Kiểm chứng được bằng |
|---|---|---|
| **1** | **Quyền sở hữu tách biệt**: bản dựng do pháp nhân khác sở hữu (hoặc studio đối tác thật), không phải `9K Holdings` | Hợp đồng chuyển nhượng + giấy phép thương hiệu, **công khai bản tóm tắt** |
| **2** | **Kho mã riêng**, không nằm trong tổ chức GitHub của Game9K | Đường dẫn repo khác nhau |
| **3** | **Quy tắc từ chối viết trước và công khai**: game của 9K Labs bị trả lại nếu không đạt ngưỡng nào, và **đã từng** bị trả lại ít nhất một lần | `audit_logs`, công bố kèm lý do |

> Điều kiện **3** là điều kiện duy nhất thực sự tạo niềm tin. Không có lần từ chối nào được công bố thì không ai tin quy tắc tồn tại.

### 2.3. Cách làm đúng — và nó không chậm hơn

| | Cách | Ai làm game | Vị thế cổng |
|---|---|---|---|
| **Q1** | **Studio đối tác thật** nhận tài trợ theo mốc, dùng Starter Kit | Bên thứ ba thật | ✅ Trung lập |
| **Q2** | Game9K làm **Starter Kit + demo kỹ thuật**, gắn nhãn rõ *"demo, không lên trang chủ, không nhận vốn"* | Game9K | ✅ Trung lập, miễn là **không lên cổng** |
| **Q3** | 9K Labs đứng tên nhưng cùng đội, cùng vốn | Nhãn dán | ❌ Không trung lập |

> **Đề xuất: Q2 + Q1.** Làm Starter Kit + demo (đúng ý "làm chuẩn mẫu", và **được đưa lên GitHub**), rồi **một studio thật** dùng nó để làm game đầu tiên lên cổng. Được cả hai thứ bạn muốn: có mẫu chạy thật **và** giữ được vị thế.

---

## 3. "Reskin 48 giờ" — kỹ thuật đúng, hệ quả sai

### 3.1. Chỗ đúng

Đúng: đổi bộ ảnh + JSON → thành đua xe/đua ngựa/đua phi thuyền. Rẻ, và là **điểm bán thật** cho studio.

### 3.2. Chỗ sai — và nó đụng vào lõi của Game9K

> **Nếu 50 studio cùng reskin một khung, cổng sẽ có 50 game giống nhau. Và Arena — thứ dùng để phân biệt game hay với game dở — sẽ xếp chúng bằng nhau.**

Đó không phải rủi ro lý thuyết. `WHITEPAPER §288` cam kết *"Không tự làm game cạnh tranh studio"* để studio tin cổng; nhưng nếu cổng **phát một khung** rồi khuyến khích 50 bản sao, cổng đang tự tạo ra **hàng rào cạnh tranh giả** — nhiều tựa, một game.

| Thứ mất đi | Vì sao |
|---|---|
| **Giá trị của Arena** | Đấu mù giữa `v0.1` và `v0.2` là vô nghĩa nếu cả hai là cùng một khung đổi ảnh |
| **Ý nghĩa của `VPH`** | `VPH` so sánh giữa các game; 50 bản reskin cho cùng một `VPH` thì không nói lên gì |
| **Lý do người chơi quay lại** | Người chơi không quay lại vì "đua ngựa thay vì đua vịt" |

### 3.3. Cách chặn — rẻ, và nên đặt **trước** khi phát Starter Kit

| Quy tắc | Cách kiểm |
|---|---|
| **Reskin không phải game mới** | Nếu `sha256` của file cấu hình **luật chơi** trùng bản đã có → xếp cùng nhóm, không tính là tựa mới |
| **Ngưỡng thay đổi tối thiểu** | Phải đổi ít nhất **một** trong: luật chơi, số chặng, cơ chế thắng. Đổi ảnh + tên **không** đủ |
| **Nhãn công khai** | Trang game ghi *"dựa trên Game9K Starter Kit"* + link khung gốc. Minh bạch, không phạt |
| **Trần ban đầu** | Trong `S1–S2`, tối đa **`5`** tựa dùng chung một khung luật chơi |

> **Nhãn công khai quan trọng hơn nó có vẻ.** Studio trung thực sẽ **thích** nhãn này — vì nó cho thấy họ bắt đầu từ một nền đã kiểm chứng, chứ không phải copy lậu.

---

## 4. "Bảng minh chứng doanh thu" — không điền được, và điền thật thì **tệ hơn**

Đây là chỗ kế hoạch tự bắn vào chân. Tôi tính từ chính số đã có trong repo.

### 4.1. Số đầu vào *(đều đã có, không bịa thêm)*

| Đầu vào | Giá trị | Nguồn |
|---|---|---|
| `eCPM` biên bảo thủ (ĐNÁ) | `$1–$3` | `WHITEPAPER §192` |
| `eCPM` Mỹ/CA | `$15–$28` | `WHITEPAPER §192` |
| Điều kiện mở cổng | `500` người chơi thật/tuần | `WHITEPAPER §288` |

### 4.2. Ở đúng điều kiện mở cổng

Giả định `20` lượt chơi/người/ngày (ván `45` giây + nghỉ) và `1` lượt hiển thị/ván:

```
500 người/tuần  →  DAU ≈ 100  →  ~2.000 lượt chơi/ngày
                                 ~60.000 lượt chơi/tháng
```

| Traffic | `eCPM` ĐNÁ `$1–$3` | `eCPM` Mỹ/CA `$15–$28` |
|---|---|---|
| `60.000` lượt/tháng | **`$60 – $180` / tháng** | `$900 – $1.680` / tháng |
| `1.000.000` lượt/tháng | `$1.000 – $3.000` | `$15.000 – $28.000` |

> ⚠️ **`$60–180` một tháng không nuôi được ai.** Đây chính là con số mà "bảng minh chứng doanh thu" sẽ hiển thị ở giai đoạn Pre-Seed.

### 4.3. Hai kết luận

**Kết luận 1 — bảng đó không chứng minh được gì cho studio.** Để trả cho **một** lập trình viên (`$2.000`/tháng) ở `eCPM` ĐNÁ, cần **~`1.000.000` lượt chơi/tháng** — gấp **`17`** lần traffic ở điều kiện mở cổng. Ở `eCPM` Mỹ/CA thì cần **~`100.000`** lượt/tháng, khả thi hơn — nhưng chỉ khi KOL là **quốc tế**, đúng như §5.

**Kết luận 2 — công bố con số thật sẽ làm yếu lập luận, không mạnh lên.** Studio thấy `$60–180`/tháng sẽ kết luận *"mô hình không kiếm ra tiền"*. Trong khi sự thật là *"mô hình chưa có traffic"* — hai chuyện khác nhau, nhưng bảng số không phân biệt được.

### 4.4. Thay bằng **bảng minh chứng chi phí**, không phải doanh thu

| Công bố cái này | Không công bố cái này |
|---|---|
| **Chi phí để có một phiên hợp lệ** = giá KOL ÷ số người chơi có `active_gameplay_sec ≥ 90` | Doanh thu Ads/1.000 lượt |
| **Tỉ lệ chuyển đổi** từ người xem → người có tài khoản → người quay lại | Con số tuyệt đối USD |
| **`VPH`, D1, D7** của chính game mẫu | "Đủ nuôi đội ngũ" |

> Lý do: chi phí thu hút là thứ **kiểm soát được** ở Pre-Seed. Doanh thu Ads thì **không** — nó phụ thuộc traffic mà Pre-Seed chưa có. Công bố thứ mình kiểm soát được.

---

## 5. Chặn IP Việt Nam — giảm rủi ro, **không** phải cơ sở pháp lý

Kế hoạch viết: chặn IP để *"thoải mái thử nghiệm luồng người dùng mà chưa cần vướng thủ tục cấp phép nội địa"*. Vế sau **không đúng**, và cách viết đó sẽ tạo cảm giác an toàn giả.

| Chặn IP **có** làm được | Chặn IP **không** làm được |
|---|---|
| Giảm nguy cơ bị coi là **phân phối game tại Việt Nam** cho người dùng trong nước | Trả lời `docs/08` **Câu 1** — cổng có phải *"cung cấp dịch vụ trò chơi điện tử trên mạng"* hay không. Câu này **không** phụ thuộc người dùng ở đâu |
| Giữ đúng cam kết ở `WHITEPAPER §465` (chặn IP **và** KYC với Việt Nam) | Trả lời `docs/08` **Câu 4** — cấu trúc sở hữu `9K Holdings` và dữ liệu người chơi |
| Là **biện pháp giảm thiểu**, ghi được trong hồ sơ | Thay cho **Giấy chứng nhận** nếu cổng thuộc nhóm phải có |

> ⚠️ **Cách viết an toàn:** *"Chặn IP để giảm rủi ro trong giai đoạn thử nghiệm; phân loại dịch vụ vẫn là câu hỏi 1 và 4 đang chờ luật sư."* **Không** viết *"chưa cần vướng thủ tục cấp phép"*.

**Thêm hai điểm kỹ thuật, đừng bỏ qua:**

1. **Chặn IP không chặn được người Việt dùng VPN.** Vì vậy nó là **giảm rủi ro**, không phải **kiểm soát**. Đừng đặt lên nó trọng lượng pháp lý.
2. **Nếu KOL là quốc tế** (đúng như kế hoạch đề xuất) thì nội dung live cũng phải **không nhắc** tới thị trường Việt Nam như thị trường đang phục vụ — nếu không, tuyên bố "chưa phân phối tại VN" sẽ mâu thuẫn với nội dung.

---

## 6. Tỉ lệ quay lại (D1) — không đo được nếu chưa có danh tính

Kế hoạch liệt kê *"tỷ lệ quay lại ngày hôm sau"* trong bộ telemetry, **đồng thời** hoãn tạo tài khoản tới bước 4 của funnel (`docs/17` §7). Hai điều này **không cùng tồn tại được**.

| Đo được gì khi chưa có tài khoản | Không đo được |
|---|---|
| Số phiên, thời lượng, `input_entropy`, số lần bấm | **D1, D7** — cần một danh tính ổn định qua ngày |

Ba cách, chọn **một**:

| | Cách | Đánh giá |
|---|---|---|
| **M1** | Gắn **ví ẩn danh** ngay từ ván đầu (không hỏi gì) — danh tính **máy**, không phải người | ✅ **Đề xuất.** Đủ để đo D1, không cần đăng ký, và khớp ADR-007 (passkey tạo im lặng) |
| **M2** | Cookie/localStorage | ⚠️ Dễ mất, tỉ lệ D1 sẽ **thấp giả tạo** |
| **M3** | Chỉ đo D1 **sau** khi người chơi tạo tài khoản | ❌ Mẫu bị chọn lệch — chỉ đo người đã ở lại |

---

## 7. Streamer Mode dùng Supabase Realtime — trái `docs/17` và không sửa nút thắt

`docs/17` §2.1 đã chốt: **đua tất định + Streamer Mode poll `2` giây** một view tổng hợp. Kế hoạch quay lại Realtime.

| Vấn đề | Chi tiết |
|---|---|
| **Realtime tốn hơn** | `300` người/ván × đẩy từng dòng = nhiều kết nối thường trực. Poll một view = **một** truy vấn mỗi `2` giây |
| **Không sửa nút thắt thật** | Nút thắt là **người dùng không thể ở hai app cùng lúc** (`docs/17` §2.3), không phải độ trễ. Realtime chỉ giảm độ trễ — thứ **không** phải vấn đề |
| **Phá tính kiểm chứng** | Đua tất định cho một kết quả **dựng lại được**. Realtime đẩy trạng thái thì kết quả phụ thuộc **thứ tự gói tin đến** — không dựng lại được |

> Giữ **xếp lệnh trước** (`docs/17` §2.3) + **poll view**. Realtime là tối ưu cho một vấn đề bạn không có.

---

## 8. Từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | Dùng **thương hiệu** 9K Labs để tạo vị thế bên thứ ba | §2 — cái cần tách là **quyền từ chối**, không phải cái tên |
| **R2** | Đưa game của chính đội lên trang chủ / cổng | §2 — phá `WHITEPAPER §288` và làm mất nghĩa ngưỡng `500` |
| **R3** | Phát Starter Kit **trước** khi có quy tắc "reskin không phải game mới" | §3 — 50 bản sao làm Arena vô dụng, và **không rút lại được** |
| **R4** | Công bố "bảng minh chứng doanh thu Ads" bằng số thật ở Pre-Seed | §4 — `$60–180`/tháng **làm yếu** lập luận |
| **R5** | Viết "chặn IP nên chưa cần thủ tục cấp phép" | §5 — che mất câu hỏi 1 và 4 đang chờ luật sư |
| **R6** | Đo D1 khi chưa có danh tính ổn định | §6 — hoặc không đo được, hoặc mẫu bị lệch |
| **R7** | Supabase Realtime cho Streamer Mode | §7 — tốn hơn, không sửa nút thắt, phá tính dựng lại được |
| **R8** | Quảng cáo xen kẽ mỗi ván `45` giây | Giữ nguyên kết luận `docs/17` §3: cần **rewarded do người dùng chọn** |

---

## 9. Việc **không** làm trong tài liệu này

- Không viết code, không chọn engine cụ thể, không đặt tên game.
- Không đổi `W = 0.60`, `H = 180`, `eCPM`, whitepaper, deck, 4 PDF, schema (**34** bảng).
- Không đưa giá KOL hay CAC — chưa có dữ liệu, và `AGENTS.md` cấm.
- Không sửa `docs/17`; tài liệu này **bổ sung**, và ghi rõ chỗ kế hoạch mâu thuẫn với nó.

## 10. Thứ tự thi công

| # | Việc | Vì sao trước |
|---|---|---|
| **1** | **Viết quy tắc "reskin ≠ game mới"** + nhãn công khai | §3 — nếu phát Starter Kit trước, không rút lại được |
| **2** | **Sửa `FR-POP-01`** (referral theo `work` tích luỹ) | `docs/16` §4 — mọi làn sóng KOL phụ thuộc việc này |
| **3** | Chốt **danh tính ẩn danh từ ván đầu** (ví, không đăng ký) | §6 — không có nó thì không đo được D1 |
| **4** | Đặc tả **file cấu hình luật chơi có `sha256`** | §1.2 + §3.3 — là hợp đồng, và là khoá chống reskin tràn lan |
| **5** | Dựng **Starter Kit + demo kỹ thuật** (Q2) — **không** lên trang chủ | §2.3 |
| **6** | **Chọn studio đối tác** cho tựa đầu tiên lên cổng (Q1) | §2.3 — giữ vị thế trung lập |
| **7** | Công bố **bảng chi phí/phiên hợp lệ**, không phải bảng doanh thu | §4.4 |
| **8** | Gửi **câu hỏi 5** cho luật sư (`docs/17` §1), gộp cùng câu 1 và 4 | §5 |
