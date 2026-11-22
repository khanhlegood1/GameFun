# Coin, TikFinity, StreamToEarn — và vì sao Similarweb không thấy Game9K

> **Tài liệu sống:** `docs/15-livestream-tools-and-token-question.md`
> **Trạng thái:** `SCOPING`
> **Ngày:** 22/11/2026
> **Nguồn:** `streammix.co` (đã khảo sát ở `docs/14`), `tikfinity.com`, `streamtoearn.io`, `similarweb.com`, `vbpo.com.vn`, `ncavn.com`
> **Ba câu hỏi:** (1) vì sao trụ sở Việt Nam mà phát hành coin? (2) TikFinity dạy gì? (3) StreamToEarn dạy gì? (4) Similarweb còn gì nữa?

---

## 0. Kết luận trước

**Tiền đề của câu hỏi đầu tiên sai một nửa — và chỗ sai đó quan trọng hơn câu trả lời.**

StreamMix **không** phát hành coin trên chain. Cái họ bán là **coin trả trước** (`2.000 / 8.000 / 20.000 / 40.000`), tức **số dư dịch vụ mua trước**, không phải tài sản mã hoá. Tôi **không tìm thấy** bằng chứng nào về token, hợp đồng thông minh, hay ví on-chain của StreamMix.

> **Ghi chú về trùng tên:** có một `Streamix (MIXS)` là ERC20 từ 2019–2020, và vài token tên `SMX`. **Không liên quan** — chỉ trùng tên. Đừng gộp.

Nghĩa là: **trụ sở Việt Nam + "coin" không phải là phát hành tài sản mã hoá.** Đó là bán tín dụng trả trước — hoạt động bình thường, không cần giấy phép tài sản số. Nhưng câu hỏi của bạn vẫn đúng ở tầng sâu hơn: **công ty Việt Nam có được phát hành token không?** Câu trả lời ngắn: **được, nhưng không được bán cho người Việt** (§1).

| Site | Bản chất | Đáng lấy nhất |
|---|---|---|
| **TikFinity** | Bộ công cụ TikTok LIVE, free tier dùng được thật | **Chế độ thử không cần lên sóng** (§2-A1) |
| **StreamToEarn** | Nối sự kiện live → hành động trong game | **Trần thu nhập theo bậc** (§3-A2) + **bộ đếm tự đo được** (§3-A4) |
| **Similarweb** | Ước lượng từ panel | **Panel không thấy được traffic của Game9K** — và nhà đầu tư sẽ tra (§4) |

---

## 1. Vì sao trụ sở Việt Nam mà phát hành coin?

### 1.1. Ba cấu trúc thực tế, và cấu trúc nào hợp pháp

| Cấu trúc | Có phải tài sản mã hoá? | Hợp pháp ở VN? |
|---|---|---|
| **A. Bán credit trả trước** ("coin", "diamond", "xu") | **Không** — là số dư dịch vụ | ✅ Có. Đây là mô hình của StreamMix, và của hầu hết công ty VN gọi tên "coin" |
| **B. Phát hành token qua pháp nhân nước ngoài, chặn người Việt** | Có | ✅ Có, nếu cấu trúc đúng và chặn đúng |
| **C. Phát hành token từ công ty VN cho người Việt** | Có | ❌ **Không.** Đây chính là hành vi bị Điều 6 NQ `05/2025/NQ-CP` chặn |

**Vì sao C bị chặn:** NQ `05/2025/NQ-CP` (09/09/2025, thí điểm **5 năm**) quy định tài sản mã hoá trong cơ chế thí điểm **chỉ được chào bán, phát hành cho nhà đầu tư nước ngoài**; tổ chức cung cấp dịch vụ phải do **Bộ Tài chính** cấp phép, vốn điều lệ đã góp tối thiểu **`10.000` tỷ đồng**, sở hữu nước ngoài tối đa **`49%`**; giao dịch và thanh toán **bằng đồng Việt Nam**. *(Nguồn: tự công bố — văn bản Chính phủ; diễn giải qua `vbpo.com.vn`, `ncavn.com` — bên thứ ba.)*

Thêm một lớp chế tài: theo `Nghị định 284/2026/NĐ-CP` (hiệu lực **01/09/2026**), nhà đầu tư trong nước giao dịch **ngoài** tổ chức được cấp phép có thể bị phạt **`30–50` triệu đồng**. *(Bên thứ ba — hãng luật. **Chưa** đối chiếu văn bản gốc; cần luật sư xác nhận trước khi đưa vào tài liệu pháp lý.)*

> **Đây là điều đáng chú ý nhất:** người bị chế tài ở cấu trúc C không chỉ là công ty phát hành — mà là **người mua**. Một công ty VN phát hành token cho người Việt đang đẩy **khách hàng của mình** vào chỗ bị phạt.

### 1.2. Game9K đã chọn đúng, và tài liệu này không đổi gì

Whitepaper (`§290`, `§465`) đã tách hai mặt trận: **cầu — huy động vốn (Web3)** phục vụ nhà đầu tư nước ngoài, **chặn IP và KYC với Việt Nam**; **cung — người chơi (Web2)** phục vụ Việt Nam, không có token. Đó chính là **cấu trúc B**.

Tôi **không** đề xuất đổi. Điều đáng nói thêm chỉ là một câu, ở §1.1: **lý do không phải "để tránh rủi ro pháp lý" mà là "để người chơi Việt Nam không bị phạt".** Đó là cách diễn đạt mạnh hơn, và đúng hơn.

### 1.3. Lấy gì từ StreamMix ở đúng chỗ này

**Không lấy.** Credit trả trước (`2.000` coin) là thứ `docs/14` §A3 đã từ chối (R1) — Game9K đã có `SPARK` là điểm không chuyển nhượng, và thêm số dư trả trước là mở lại đúng câu hỏi ở §1.1.

---

## 2. TikFinity

### 2.1. Quan sát *(truy cập 22/11/2026, `tikfinity.com`)*

| Mã | Quan sát |
|---|---|
| **K1** | Free tier **dùng được thật**: alerts, game, chat command, TTS, hệ điểm — có giới hạn nhưng không bị khoá chức năng cốt lõi. Pro nâng **hạn mức**, thêm overlay/giọng cao cấp |
| **K2** | Chạy **trong trình duyệt** (không cài đặt), chỉ cần `@handle` TikTok. Có bản Windows và bản mobile riêng |
| **K3** | **Không bao giờ hỏi mật khẩu TikTok**, và nói rõ: *"nếu site nào hỏi, hãy đóng site đó"* |
| **K4** | Mô hình **"bạn đặt luật, chat bấm cò"**: `Rose → hiện alert`, `!tts → đọc`, `Like → đổi scene OBS`, `Gift → quay vòng may mắn` |
| **K5** | Có **Event Simulator** — thử một hành động **không cần đang phát trực tiếp** |
| **K6** | Overlay chạy trong **bất kỳ công cụ nào nhận browser source** (TikTok LIVE Studio, Streamlabs), không bắt buộc OBS |
| **K7** | ⚠️ **Bản mobile là gói thuê bao riêng**; cấu hình desktop **không** chuyển sang mobile |
| **K8** | Có **Event API** cho bên thứ ba |

### 2.2. Lấy gì

**A1 — Chế độ thử không cần lên sóng (K5). Đây là thứ đáng lấy nhất.**

Game9K đòi studio nhúng SDK rồi mới biết telemetry có chạy không. TikFinity cho bấm một nút là thấy kết quả. **Áp dụng:** SDK phải có **`simulate` mode** — phát một luồng sự kiện giả (`session_start`, `heartbeat`, `input_entropy`, `crash`) và hiện đúng những gì Inspector sẽ thấy, **trước** khi studio phải sửa một dòng code nào.

| Làm | Không làm |
|---|---|
| `gamefun-sdk simulate` in ra bảng sự kiện + cảnh báo "sẽ bị PoP lọc vì X" | Bắt studio deploy lên production rồi mới phát hiện sai |
| Trang `/studio/sandbox` chạy luồng giả, không ghi vào `verified_play` | Trộn dữ liệu thử vào dữ liệu thật |

**A2 — Free tier phải dùng được thật (K1).** Ngưỡng của Game9K đã có ở whitepaper: **`500` người chơi thật/tuần** mới mở Launchpad. Cùng tinh thần: bậc miễn phí của studio **không** được chặn thứ họ cần để **quyết định** có dùng hay không (đo VPH, xem dashboard, kiểm tra SDK). Chặn ở khâu **phát hành quy mô**, không chặn ở khâu **đánh giá**.

**A3 — Không bao giờ hỏi mật khẩu nền tảng (K3).** Game9K đã theo hướng này qua ADR-007 (passkey + SIWS, không giữ khoá người dùng). Cách diễn đạt của TikFinity đáng chép vì nó **dạy người dùng cách tự bảo vệ**: *"nếu site nào hỏi mật khẩu, hãy đóng site đó"*. Đưa câu tương đương vào trang kết nối ví.

**A4 — Overlay sống trong công cụ sẵn có (K6).** Đã ghi ở `docs/14` §A2 (plugin, không bắt đổi công cụ). TikFinity xác nhận lại: điều kiện thành công là **không đòi thay đổi thói quen**.

### 2.3. Từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | **Bản mobile là thuê bao riêng, cấu hình không chuyển (K7)** | Người dùng trả hai lần cho cùng một tài khoản và mất cấu hình. Game9K có một danh tính (`FR-FND-01`) — **quyền lợi phải theo danh tính, không theo thiết bị** |
| **R2** | Mở **Event API** cho bên thứ ba ngay | Bề mặt tấn công + bề mặt chịu trách nhiệm, khi chưa có ai xin. Để P2 |
| **R3** | Đếm "5 sound alert / 75 TTS mỗi ngày" kiểu hạn mức theo ngày | Với Game9K, hạn mức đúng là **`work` theo epoch 7 ngày**, đã có. Đừng thêm đơn vị thời gian thứ hai |

---

## 3. StreamToEarn

### 3.1. Quan sát *(truy cập 22/11/2026, `streamtoearn.io`)*

| Mã | Quan sát |
|---|---|
| **E1** | **Ba lớp giữa quà và game:** *Preset* (luật `if gift → action`), *Alert/Interrupt* (người xem **ngắt** được, có ưu tiên và cooldown), *Overlay* (giải thích mọi món quà làm gì) |
| **E2** | **Trần thu nhập theo bậc**: Free `$25` · Creator `$140` · Pro `$500` · Expert `$1.000` · Elite `$2.500` · Prime không trần — *"mức USD/tháng streamer có thể kiếm qua hành động do preset kích hoạt trước khi trigger tạm dừng"* |
| **E3** | Chỉ đọc **API sự kiện công khai**; không sửa luồng phát, không sửa tài khoản người xem |
| **E4** | **Thư viện preset cộng đồng**, fork được — nội dung do người dùng tạo, chi phí biên bằng 0 |
| **E5** | Trang chủ hiện **bộ đếm sống**: `85` game hỗ trợ · `339` đang phát trực tiếp |
| **E6** | Công khai **ba cách kết nối** kèm nhược điểm thật: *Server* (mặc định, nhanh, nhưng **ghế dùng chung nên có thể đầy**), *Browser* (phải **mở cửa sổ suốt buổi**), *Socket* (WebSocket trực tiếp, dùng khi Server nghẽn) |
| **E7** | Quy đổi công khai: `200` coin = `$1`; Kick trả `$1.00` / `100` coin |

### 3.2. Lấy gì

**A2 — Trần thu nhập theo bậc, không phải trần số lượt (E2). Đây là thứ đáng lấy nhất, và nó khớp trực tiếp với bài toán chống bot của Game9K.**

Game9K đang chống lạm dụng bằng **đếm phiên** (`2 giờ`, `120` phút, `20` referral/tháng). Đếm phiên thì bot chỉ cần tạo nhiều phiên ngắn. **Trần theo tiền** thì bot phải tạo ra **doanh thu thật** để vượt — và doanh thu thật thì phải có người thật.

| Áp dụng | Cụ thể |
|---|---|
| Trần **theo USD/tháng** cho mỗi studio/creator, không theo số phiên | Vượt trần → **tạm dừng chi trả**, không cấm tài khoản |
| Bậc trần **gắn với mốc `M1…M4`** đã có | Ví dụ `M1` → trần thấp, `M4` → trần cao; mốc đã được kiểm bằng `sha256` + Inspector |
| Tạm dừng **không** xoá dữ liệu | Phiên hợp lệ vẫn ghi; chỉ dòng tiền dừng |

> **Vì sao đúng:** trần theo số phiên tạo **động cơ làm giả phiên**. Trần theo USD tạo **động cơ làm thật** — vì muốn nhiều tiền hơn thì phải có nhiều người chơi thật hơn, mà đó đúng là thứ Game9K muốn đo.

**A3 — Ba lớp tách bạch: luật / ngắt / giải thích (E1).** Rất gần với Game9K, chỉ cần đặt tên:

| StreamToEarn | Game9K tương ứng | Đã có? |
|---|---|---|
| **Preset** — luật | Điều kiện quest / mốc milestone | ✅ |
| **Alert/Interrupt** — ngắt có ưu tiên + cooldown | Thông báo milestone, có chống dội | Một phần |
| **Overlay** — giải thích mọi thứ đang xảy ra | **Chưa có.** Đây là chỗ Game9K yếu: người chơi không thấy vì sao `work` của mình bị lọc | ❌ |

**Việc cần làm:** một "overlay" cho PoP — mỗi lần `work` bị loại, hiện **một dòng lý do** (`phiên < 60s`, `không có input`, `trùng thiết bị`). Đây là cùng một ý với `docs/14` §A1 (cho người chơi thấy đồng hồ), nhưng ở phía **giải thích**, không phải phía **đếm**.

**A4 — Bộ đếm tự đo được trên trang chủ (E5).** `339` đang phát trực tiếp là con số **họ tự sinh lại được mỗi giây**. Đây là câu trả lời đúng cho vấn đề `docs/14` §A4 nêu ra: khi buộc phải công bố số, hãy công bố **số mình tự đo được theo thời gian thực**, không phải số của bên thứ ba. Với Game9K: *"`N` người chơi đang trong phiên hợp lệ"* — sinh từ cùng nguồn `verified_play`, kiểm chứng được.

**A5 — Công khai ba cách kết nối kèm nhược điểm (E6).** Game9K có `docs/03` liệt kê endpoint nhưng **chưa có** `openapi.json`. Bài học: khi viết tài liệu API, **ghi cả nhược điểm** (`rate limit`, `best-effort`, `deprecated`) chứ không chỉ ghi tính năng. Người tích hợp cần biết chỗ nào sẽ vỡ.

### 3.3. Từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R4** | **Trả tiền cho người chỉ *xem*** (mô hình `Stream2Earn`/`STREAMN` kiểu "xem càng lâu càng nhiều") | Đây đúng là thứ `FR-POP-01` cấm: điểm **không mua được**, và Game9K **không** kiếm tiền từ việc người chơi thua lỗ. Trả tiền cho thời gian xem = mở lại đường farm |
| **R5** | Câu "free vĩnh viễn, không trần" của đối thủ | Không giữ được về mặt kinh tế; `AGENTS.md` cấm lời hứa không kèm số |
| **R6** | `200 coin = $1` như một tỷ giá công khai | Đó là **nghĩa vụ quy đổi**. Game9K trả USD từ doanh thu Ads, không phát hành đơn vị có tỷ giá cố định |
| **R7** | Xây lõi trên **luồng sự kiện của một nền tảng thứ ba** | StreamToEarn phụ thuộc TikTok (và thêm Kick). Game9K chạy trên web — **đừng** đổi lấy sự phụ thuộc tương tự. Đo bằng SDK của mình |

---

## 4. Similarweb — phần chưa nói ở `docs/14`

`docs/14` §B đã nói: không mua, và lấy kỷ luật *nguồn · ngày · chiều sai lệch*. Còn **một** điểm chưa nói, và nó quan trọng hơn:

> **Panel không nhìn thấy traffic của Game9K — về mặt cấu trúc, không phải vì Game9K còn nhỏ.**

Game9K chạy game **trong iframe trên tên miền của studio**, sau lớp chia sẻ SDK, phần lớn phiên đến từ link trực tiếp và chia sẻ trong app nhắn tin. Panel clickstream dựa trên **tên miền** và **tiện ích mở rộng trình duyệt** — nó đếm `cổng game`, **không** đếm `game chạy trong iframe`, và bỏ sót phần lớn traffic đi qua app nhắn tin. Ba nguồn mù này đã được ghi nhận với chính Similarweb: *API, hợp đồng doanh nghiệp, và traffic qua nền tảng cloud* (`docs/14` §W2), cộng thêm app/direct/messaging.

**Hệ quả thực tế, phải chuẩn bị trước:**

| Tình huống | Cách xử lý |
|---|---|
| Nhà đầu tư tra tên miền Game9K trên Similarweb, thấy số thấp | **Chủ động nêu trước**: đây là số panel, và nó **cấu trúc** không thấy traffic trong iframe + messaging. Đưa số first-party kèm **cách tự kiểm chứng** |
| Bị hỏi "số của bạn có kiểm chứng được không?" | Câu trả lời đã có: `base_sha256` + Inspector + telemetry SDK. Đây là thứ panel **không** làm được |
| Bị so sánh với đối thủ có traffic web cao | So **số phiên hợp lệ/người chơi thật**, không so lượt truy cập tên miền |

> ⚠️ **Đừng** dùng lập luận này để bác bỏ mọi con số panel. Nó chỉ đúng với **traffic của chính Game9K**. Với site của người khác (`Poki`, `CrazyGames`), panel vẫn là nguồn duy nhất có — và ở đó luật `docs/14` §A6 vẫn áp: **so thứ hạng, không định giá**.

---

## 5. Việc **không** làm trong tài liệu này

- Không đổi whitepaper, deck, hay 4 PDF. Câu ở §1.2 là gợi ý diễn đạt, chờ đợt dựng PDF tiếp theo.
- Không đổi schema (**34** bảng), không đổi `50/50`, `eCPM $1–$3`, MOIC `16.8×`.
- Không khẳng định StreamMix có token — **không tìm thấy bằng chứng**, và tài liệu nói rõ như vậy.
- Không đưa `Nghị định 284/2026/NĐ-CP` vào tài liệu pháp lý chính thức khi chưa đối chiếu văn bản gốc.

## 6. Thứ tự thi công

1. **`simulate` mode cho SDK** (§2-A1) — rẻ, và gỡ đúng rào cản lớn nhất của studio.
2. **Dòng lý do khi `work` bị lọc** (§3-A3) — sửa ở tầng hiển thị, không đổi công thức PoP.
3. **Trần chi trả theo USD/tháng gắn mốc `M1…M4`** (§3-A2) — thiết kế trước, mở cùng chương trình creator ở `docs/13` §3.2.
4. **Bộ đếm tự đo trên trang chủ** (§3-A4) — chỉ khi đã có người chơi thật; đừng hiện `0`.
5. **Ghi nhược điểm vào `docs/03`** khi làm `openapi.json` (§3-A5).
