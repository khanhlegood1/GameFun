# Starter Kit — kiểm chứng đặc tả kỹ thuật

> **Tài liệu sống:** `docs/21-starter-kit-spec-verification.md`
> **Trạng thái:** `SCOPING` — kiểm chứng + hiệu đính
> **Ngày:** 22/11/2026
> **Đầu vào:** `Đặc Tả Game9K Starter Kit.md` (do người sáng lập tải lên, 172 dòng) — đặc tả cho một **game đua xe ô tô mẫu** + khung hạ tầng
> **Phương pháp:** đo lại số gói từ npm registry; đối chiếu từng khẳng định với `docs/01`, `docs/03`, `docs/05`, `docs/11`; kiểm nguồn ngoài
> **Liên quan:** `docs/17` §2.1 (đua tất định), `docs/18` (§2 vị thế cổng, §3 reskin), `docs/20` (§3 R2)

---

## 0. Kết luận trước

**Đặc tả này là tài liệu tốt nhất trong loạt tài liệu bạn gửi. Nó dẫn nguồn sơ cấp cho gần như mọi khẳng định hạ tầng, và ba phát hiện của nó đủ để đổi thiết kế.**

| # | Nội dung | Đánh giá |
|---|---|---|
| **1** | Nêu rõ **khoảng trống dữ liệu**: repo không truy cập được, không có đặc tả Starter Kit, không có mô hình vật lý xe | ✅ **Đúng, và đây là điểm mạnh.** Không bịa |
| **2** | **`Presence` giới hạn `5` lần/30 giây** → không dùng cho cập nhật vị trí | ✅ **Phát hiện quan trọng nhất** — đổi kiến trúc (§3) |
| **3** | Phân tích **`sandbox` + `allow-same-origin`** và `event.origin` = `"null"` | ✅ **Phát hiện thứ hai** — nhưng `docs/03` đã có cách giải tốt hơn (§2) |
| **4** | **`Workers KV` nhất quán cuối cùng tới `60` giây** → kill switch có trễ | ✅ **Phát hiện thứ ba** — cần ghi vào ADR |
| **5** | Số gói **PixiJS `126,1` KB gz** · **Phaser `274,1` KB gz** | ❌ **Sai cả hai.** Đo lại: `255` KB và `319–353` KB (§4) |
| **6** | Đề xuất **Supabase Realtime** cho game đua nhiều người | ❌ **Trái `docs/17` §2.1** và trái luật Presence ở chính §3 |
| **7** | Phân nhóm **NĐ 147** thành bảng G1–G4 cho từng chế độ chơi | ✅ **Rất có ích** — làm rõ `docs/08` câu 2 (§5) |
| **8** | **Google H5 Games Ads β** làm nền tảng quảng cáo | ⚠️ Đúng API, nhưng **β đóng** — rủi ro chưa được nêu (§6) |
| **9** | **Kill switch** qua KV **cộng** RLS | ✅ Đúng, bổ sung đúng chỗ `docs/02` §765 còn thiếu (§7) |

---

## 1. Điều đặc tả này làm đúng nhất: nói rõ cái mình **không** biết

Đặc tả mở đầu bằng việc liệt kê **bốn nhóm tài liệu chưa trích xuất được**, và không tự suy diễn bất kỳ thông số nào của game đua xe: không gia tốc, không ma sát, không số khung hình, không cơ chế chống gian lận.

> Đây đúng là điều `AGENTS.md` yêu cầu: *"Nêu rõ cái KHÔNG biết"*. Và nó **ngược** với bản phân tích ProximaX ở `docs/20` — nơi một khẳng định sai (`GitHub đóng băng`) làm mất uy tín cả tài liệu.

**Một chi tiết cần nói thẳng:** đặc tả ghi *"github.com/khanhlegood1/GameFun không thể truy cập"*. Repo này **công khai** — tôi vừa đọc nó. Nếu công cụ của bạn không truy cập được, đó là **vấn đề công cụ**, không phải vấn đề repo. Nhưng kết luận *"không có đặc tả Starter Kit trong repo"* là **đúng thật**: Starter Kit **chưa tồn tại**, mới chỉ là kế hoạch (`docs/18`).

---

## 2. `sandbox` + `postMessage` — `docs/03` đã có cách giải tốt hơn

### 2.1. Đặc tả nói gì

Đúng: **không được bật đồng thời `allow-scripts` và `allow-same-origin`**. Đúng: nếu origin là `"null"` thì `event.origin` trả `"null"`, nên phải kiểm `event.source === iframe.contentWindow`.

### 2.2. Nhưng `docs/03` §ADR-003 đã tránh được toàn bộ vấn đề đó

`docs/05` §ADR-003 và `docs/03` dòng `239` chốt:

> *"Portal chỉ chấp nhận bản tin khi `event.source === gameIframe.contentWindow` **VÀ** `event.origin === expectedVersionOrigin` (khớp chính xác `https://<versionId>.play.game9k-cdn.net`)."*

**Vì sao quan trọng:** game **không** chạy trên origin `null`. Nó chạy trên **wildcard subdomain riêng theo `version_id`** — tức là một **origin thật, khác nhau cho từng phiên bản**.

| | Nếu origin là `"null"` (đặc tả) | Nếu dùng subdomain theo `version_id` (`docs/05`) |
|---|---|---|
| Kiểm nguồn gửi | ❌ Chỉ `event.source` | ✅ `event.source` **và** `event.origin` chính xác |
| Cô lập giữa hai phiên bản | ❌ Chung `null` | ✅ Mỗi bản một origin |
| Cookie/storage | ❌ Phải tránh `allow-same-origin` | ✅ Cô lập tự nhiên, `allow-same-origin` an toàn **trong subdomain riêng** |
| CSP | Yếu hơn | ✅ CSP riêng theo từng phiên bản |

> **Kết luận:** đặc tả đúng về **nguyên tắc**, nhưng **giải pháp đã tốt hơn có sẵn**. Không đổi gì — chỉ ghi lại để không ai "sửa" `docs/03` thành `origin: null`.

---

## 3. `Presence` 5 lần/30 giây — phát hiện đổi kiến trúc

Đây là phần giá trị nhất của đặc tả, và nó **xác nhận độc lập** kết luận `docs/17` §2.1.

| Cơ chế | Giới hạn thật | Dùng được cho |
|---|---|---|
| **`Presence`** | **`5` lần `track()/untrack()` mỗi `30` giây / client** | Danh sách người trong phòng — **không** cho vị trí |
| **`Postgres Changes`** | p95 `238` ms, payload `1.024` KB, cột > `64` byte bị lược | Bảng xếp hạng sau khi hết chặng |
| **`Broadcast`** | `100` tin/giây (Free) → `2.500` (Pro) | Chỉ khi cần thời gian thực |

**Nếu gửi vị trí xe qua `Presence`:** kết nối **bị đóng ngay** với `ClientPresenceRateLimitReached`. Đặc tả nói đúng — và đây là loại lỗi chỉ phát hiện khi có tải thật.

### 3.1. Nhưng kết luận đúng **không phải** "dùng Broadcast"

Đặc tả kết luận: nếu cần đồng bộ vị trí, *"bắt buộc phải đi qua `Broadcast`"*. Đó là **đúng trong phạm vi Supabase Realtime**, và **sai ở tầng kiến trúc**.

| | Broadcast thời gian thực | Đua tất định (`docs/17` §2.1) |
|---|---|---|
| Tải server | `2.500` tin/giây trần, `10.000` kết nối trần (Pro) | Vài nghìn `INSERT` trong `60` giây |
| Phụ thuộc gói tin | Kết quả phụ thuộc **thứ tự đến** | Kết quả **dựng lại được** từ `seed` + log lệnh |
| Kiểm chứng | ❌ Không | ✅ **Có** — ai có `seed` cũng tính lại được |
| Chi phí | Cao hơn, và tăng theo số người | Thấp, không phụ thuộc số người xem |

> **Chốt:** đặc tả đã **chứng minh rất tốt** rằng Realtime là đường sai. Bước tiếp theo đúng là **bỏ Realtime**, không phải chuyển sang `Broadcast`.

---

## 4. Số gói engine — đo lại, cả hai số đều sai

Đặc tả đưa `PixiJS 126,1 KB gzip` và `Phaser 274,1 KB gzip`, dẫn Bundlephobia và một blog so sánh.

### 4.1. Đo lại *(tự đo lại — `npm pack` + `gzip -9`, 22/11/2026)*

| Gói | Phiên bản | Minified | **Gzip `-9`** | Đặc tả ghi |
|---|---|---|---|---|
| `pixi.js` | **`8.23.0`** | `912.519` B | **`255.257` B** | `126,1 KB` ❌ |
| `phaser` | **`4.2.1`** | `1.375.976` B | **`352.227` B** | `274,1` KB ❌ |
| `phaser` (arcade physics) | `4.2.1` | `1.266.396` B | `319.663` B | — |
| `phaser` (ESM) | `4.2.1` | `1.377.611` B | `353.180` B | — |

### 4.2. Vì sao lệch — và vì sao điều đó **không** phá kết luận

Hai nguyên nhân, cả hai đều đúng:

1. **Phiên bản khác nhau.** Đặc tả đo `pixi.js@6.4.2`; bản mới nhất là `8.23.0`, lớn hơn đáng kể.
2. **Bundlephobia đo *nhánh nhập*, không đo *bundle thật*.** Nó ước lượng phần cây được kéo vào từ `import`, đã tree-shake. Một game thật thường nhập nhiều hơn.

> ⚠️ **Nhưng kết luận của đặc tả vẫn đúng:** **PixiJS nhỏ hơn Phaser rõ rệt** — đo lại cho **`255` so với `352` KB** (tỉ lệ `1 : 1,38`), tương đương tỉ lệ đặc tả nêu (`126` so với `274`, `1 : 2,17`). Hướng đúng, độ lớn sai.

### 4.3. Việc cần làm thay vì sửa số

| Bỏ | Làm |
|---|---|
| Tranh luận `126` hay `255` KB | **Đo bundle của chính mình** trong CI, ghi vào `docs/18` §1.2 như một con số có ngưỡng |
| Chọn engine theo blog so sánh | Chọn theo **bundle đo được** + `simulate` mode chạy được (`docs/15` §2-A1) |

> **Quan trọng hơn cả hai:** ngưỡng `5 MB` trong `docs/18` là **tổng gói**, không phải engine. Engine chỉ chiếm `5–7%` ngân sách đó. Con số đáng lo là **asset**, không phải framework.

---

## 5. Phân nhóm NĐ 147 theo **chế độ chơi** — đóng góp thật cho `docs/08`

Đặc tả làm được điều `docs/08` chưa làm: gắn **từng chế độ chơi** với **từng nhóm G**. Đó chính là câu trả lời cho câu hỏi 2 của `docs/08` — nhưng nêu ở dạng **giả thuyết cần luật sư xác nhận**, không phải kết luận.

| Chế độ | Nhóm (đặc tả) | Hệ quả |
|---|---|---|
| Đua nhiều người qua Realtime / server cổng | **G1** | Giấy phép G1 + quyết định phát hành từng game |
| Đua đơn có cloud save / bảng xếp hạng | **G2** | Giấy chứng nhận G2–G4 + thông báo phát hành |
| Nhiều người qua LAN/P2P, không qua server | **G3** | Cùng phạm vi G2–G4 |
| Chạy hoàn toàn cục bộ, không gọi API | **G4** | Vẫn thuộc phạm vi điều chỉnh; miễn theo Điều 37 **đang chờ tư vấn** |

**Điều này nói thẳng ra một chuyện quan trọng:** nếu dùng **Realtime** cho game neo, nó rơi vào **G1** — nhóm nặng nhất. Đó là **lý do thứ hai** để chọn đua tất định (`docs/17` §2.1), bên cạnh lý do kỹ thuật.

> **Ghi nhận, không sửa `docs/08`.** Đây là **giả thuyết** để luật sư xác nhận, không phải kết luận. Không được đưa bảng này vào deck như sự thật.

### 5.1. Ba điều kiện kỹ thuật — dùng được ngay

Đặc tả nêu đúng ba yêu cầu **kỹ thuật** (không phải pháp lý) mà cổng phải xây **nếu** mở Việt Nam:

| # | Yêu cầu | Ghi chú triển khai |
|---|---|---|
| **1** | Lưu **họ tên · ngày sinh · số điện thoại VN**, giữ **`6` tháng** sau khi ngừng chơi | ⚠️ **Xung đột với `docs/02`** — schema hiện **không** có ba trường này. Không thêm bây giờ (chưa mở VN), nhưng phải ghi là **khoản nợ** |
| **2** | Giới hạn **`60` phút/ngày/game** và **`180` phút/ngày** cho người dưới `18` | ✅ Đặc tả đúng: bộ đếm phải ở **lớp vỏ ngoài `<iframe>`**, không trong game. Nếu để studio tự làm, mỗi studio làm một kiểu |
| **3** | Phương án dự phòng + sao lưu | Đã có ở `docs/05` §NFR |

**Về điều 1 — một cảnh báo cụ thể:** *"số điện thoại di động tại Việt Nam"* + *"Supabase Auth mặc định `30` SMS/giờ"* là **hai con số không đi cùng nhau**. `30` SMS/giờ = `720`/ngày. Với `1.000` người đăng ký/ngày, hàng đợi sẽ dài **hơn một ngày**. Cần nhà cung cấp SMS riêng **trước** khi mở VN — không phải sau.

---

## 6. Google H5 Games Ads — đúng API, nhưng rủi ro chưa nêu

| Thực tế | Hệ quả |
|---|---|
| `H5 Games Ads` vẫn ở trạng thái **beta**, phải **nộp đơn và được duyệt** | Không thể coi là nguồn thu **chắc chắn** trong mô hình tài chính |
| Phải **được duyệt riêng cho `game9k.com`**; tài khoản AdSense thường trả `breakStatus=other` | Ngay cả khi có AdSense, vẫn phải chờ duyệt |
| Google cấm chèn quảng cáo **toàn màn hình trong lúc đang chơi** | ⚠️ **Trực tiếp bác bỏ** ý "quảng cáo xen kẽ mỗi ván" ở `docs/17` §3 — xác nhận thêm |

**Ba việc phải làm:**

1. **Không** đưa doanh thu H5 Ads vào mô hình cơ sở như doanh thu chắc chắn — chỉ là **kịch bản**, kèm nhánh "nếu không được duyệt".
2. Thiết kế **`adBreak` ở điểm dừng tự nhiên** (menu, kết thúc ván) — không bao giờ giữa đường đua.
3. **Luôn** gọi `adBreakDone()` trong nhánh lỗi, nếu không game treo ở màn chờ.

> Và nhắc lại kết luận `docs/17` §3: với `eCPM $1–$3`, quảng cáo **không** nuôi được đội ngũ. Việc H5 Ads là **beta có duyệt** chỉ làm kết luận đó mạnh hơn.

---

## 7. Kill switch — `docs/02` còn thiếu cơ chế, đặc tả bổ sung đúng

| Cơ chế | Độ trễ | Ai kiểm |
|---|---|---|
| **RLS / `published` flag trong Supabase** | Tức thì | Server — **nhưng** game đã tải trong trình duyệt vẫn chạy |
| **`Workers KV` kill switch** | **Tới `60` giây** | Edge — chặn **yêu cầu mới**, không dừng phiên đang chạy |
| **`Cache-Control` / purge CDN** | Giây | Edge |

**Điều đặc tả nêu đúng và cần ghi thành luật:** *kill switch KV có thể trễ tới `60` giây*, nên nó **không thể** là cơ chế duy nhất để gỡ game vi phạm.

**Ba lớp phải cùng tồn tại:**

1. **RLS** — chặn dữ liệu (tức thì với yêu cầu mới).
2. **KV kill switch** — chặn tải bản dựng mới (trễ ≤ `60` giây).
3. **`postMessage` từ chối** — Portal gửi lệnh `mp:terminate` tới iframe đang mở; SDK **phải** xử lý. Đây là lớp **duy nhất** dừng được phiên đang chạy.

> ⚠️ Lớp 3 **chưa có** trong `docs/03`. Cần thêm một thông điệp `mp:terminate` vào hợp đồng SDK — rẻ, và là lớp duy nhất thật sự "gỡ ngay".

---

## 8. Từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | Dùng **Supabase Realtime / Broadcast** cho game đua nhiều người | §3 — trái `docs/17` §2.1; mất tính dựng lại được; và đẩy game vào nhóm **G1** |
| **R2** | Dùng **`Presence`** cho bất kỳ dữ liệu nào cập nhật liên tục | §3 — trần `5`/`30` giây, đóng kết nối ngay |
| **R3** | Số gói `126,1` và `274,1` KB | §4 — đo lại cho `255` và `352` KB. Sai kiểm được |
| **R4** | Coi **H5 Games Ads β** là nguồn thu chắc chắn | §6 — phải được duyệt, và đang beta |
| **R5** | Quảng cáo toàn màn hình trong lúc đang chơi | §6 — Google cấm; xác nhận lại `docs/17` §3 |
| **R6** | Đưa bảng G1–G4 vào deck như kết luận | §5 — là **giả thuyết** chờ luật sư |
| **R7** | Thêm ba trường `họ tên/ngày sinh/SĐT` vào schema **bây giờ** | §5.1 — chưa mở VN; thêm là nợ dữ liệu không cần thiết |
| **R8** | Dựa vào **kill switch KV** làm cơ chế gỡ game duy nhất | §7 — trễ tới `60` giây |

---

## 9. Việc **không** làm trong tài liệu này

- Không tạo Starter Kit, không viết game đua xe, không chọn engine. Đó là `docs/18` §10 (Q2).
- Không đổi `docs/02` (**34** bảng), `docs/03`, `docs/05`, `docs/08`, `docs/17`.
- Không đổi `W = 0.60`, `H = 180`, `eCPM`, whitepaper, deck, 4 PDF.
- Không đưa bất kỳ con số nào của **game đua xe** (vật lý, fps) — chưa có gì để đo.

## 10. Thứ tự thi công

| # | Việc | Vì sao trước |
|---|---|---|
| **1** | Thêm **`mp:terminate`** vào hợp đồng SDK (`docs/03` §3) | §7 — lớp duy nhất dừng được phiên đang chạy |
| **2** | Ghi **`60` giây KV** + ba lớp kill switch vào `docs/05` §NFR | §7 — rủi ro vận hành thật |
| **3** | Chốt **đua tất định**, đóng hẳn nhánh Realtime | §3 + §5 — tránh G1 và giữ tính kiểm chứng |
| **4** | Thêm bước **đo bundle trong CI** với ngưỡng | §4.3 — thay cho tranh luận số |
| **5** | Ghi **ba khoản nợ pháp lý** (họ tên/ngày sinh/SĐT, `6` tháng, giới hạn tuổi) vào `docs/08` | §5.1 — để không quên, và không xây sớm |
| **6** | Thiết kế `adBreak` + nhánh "nếu H5 Ads **không** được duyệt" | §6 |
