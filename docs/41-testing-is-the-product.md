# 41 — Bán việc kiểm định, không bán vé đầu tư

> **Tài liệu sống:** `docs/41-testing-is-the-product.md` — bản gốc ở đây, mọi bản khác là bản chép.
> **Trạng thái:** `SCOPING` — đây là **câu hỏi chiến lược**, chưa phải quyết định đã chốt.
> **Tiền đề:** `docs/WHITEPAPER.md` §3 (WHO — 4 nhóm tác nhân) · §5.4 (5 nguồn doanh thu) · `docs/40` §6 (cổng không kiểm được thứ nó không thấy)

---

## 0. Một dòng

Người dùng hỏi đúng chỗ đau: Game9K mạnh ở **kiểm định game**, không mạnh ở **chơi game** — và hai nhóm khách hàng của mô hình hiện tại (game thủ, nhà đầu tư) **không có nhu cầu của nhau**. Câu trả lời ngắn: bán **việc kiểm định** cho **người làm game**, đừng bắt game thủ phải đầu tư và đừng bắt nhà đầu tư phải chơi.

Nhưng có một chỗ mô hình đang **tự mâu thuẫn** mà câu hỏi này làm lộ ra, và nó quan trọng hơn việc chọn benchmark nào. Xem §2.

---

## 1. Vấn đề thật: doanh thu đến từ phía nào?

Whitepaper §8 **đã** ghi nhận vấn đề khởi động ba bên:

> *"Cần đồng thời có game đủ hay, đủ 500 người chơi thật để chấm Fit/Arena nhanh, và nhà giao dịch thanh khoản trong giai đoạn đầu."*

Nhưng §5.4 không có nguồn thu nào **bắt buộc** phải có nhà đầu tư:

| # | Nguồn thu | Ai trả tiền | Cần nhà đầu tư? |
|---|---|---|---|
| 1 | Phí giao dịch đường cong | người mua phiên bản | có |
| 2 | Phí tốt nghiệp `1,50 SOL` | dự án tốt nghiệp | có |
| 3 | Phí LP vĩnh viễn | người giao dịch hậu tốt nghiệp | có |
| 4 | Doanh thu quảng cáo `50/50` | nhãn hàng | **không** |
| 5 | Dịch vụ studio & giải đấu | studio | **không** |

Nghĩa là: **3/5 nguồn thu của Game9K không cần một nhà đầu tư nào tồn tại.** Chúng cần *người chơi* (nguồn 4) và *studio có tiền* (nguồn 5).

> **Điều đáng chú ý:** nguồn 4 và 5 là hai nguồn duy nhất **không phụ thuộc giá token**, tức hai nguồn duy nhất sống được qua mùa đông crypto — chính là hai nguồn **không cần nhà đầu tư**. Whitepaper đã xếp chúng ở vị trí *bổ trợ*; câu hỏi của người dùng gợi ý chúng nên ở vị trí **chính**.

---

## 2. Chỗ mô hình tự mâu thuẫn

Đây là phần quan trọng nhất của tài liệu này.

**Arena đấu mù cần người chấm là game thủ.** §2 của whitepaper nói thẳng: người chấm phải *"đã chơi thật (ví dụ ≥10 phút/24h với điểm PoP/PoPW)"*.

**Nhưng "game thủ không có nhu cầu đầu tư".** Người chơi bình thường mở game để chơi 3 phút, không để chấm điểm hai bản build cho một studio.

Hai câu đó cộng lại thành: **chất lượng dữ liệu kiểm định tỷ lệ nghịch với sự sẵn lòng của người chấm.** Người càng không muốn chấm, dữ liệu càng rác — và `BotShare < 8%` là cổng duy nhất đang canh chuyện đó, trong khi phần thưởng `SPARK` chính là thứ tạo động cơ farm.

**Đây không phải vấn đề marketing. Đây là vấn đề kiến trúc động cơ.** Và nó có tiền lệ rất đắt: **mô hình *issuer-pays* của các tổ chức xếp hạng tín nhiệm**. Moody's và S&P chuyển sang thu tiền từ **bên được xếp hạng** từ thập niên 1970; đến 2005 khoảng **90%** doanh thu của Moody's đến từ phí của tổ chức phát hành [1]. Hệ quả là *ratings inflation* — và SEC đã phải ban hành quy tắc khuyến khích xếp hạng **không được yêu cầu** (*unsolicited ratings*) để chống lại xung đột lợi ích đó [1].

> **Ánh xạ sang Game9K:** nếu studio trả tiền để **được chấm**, thì điểm sẽ bị thổi. Game9K hiện có nguồn thu #5 (*"gói phân tích playtest chuyên sâu cho studio lớn"*) — tức **đã** là issuer-pays, chỉ chưa gọi tên. Điều này không sai về mặt kinh doanh, nhưng **phải có van**: điểm Arena không được là thứ studio mua được.

**Van đó là gì (đề xuất, chưa chốt):** tách **hai sản phẩm** —
- **Chứng chỉ công khai** (`Trust Stamp`, điểm Arena, `VPH`) → **miễn phí, không bán, không ai mua được**. Đây là thứ tạo uy tín.
- **Dữ liệu chẩn đoán riêng** (điểm rơi người chơi phút đầu, video playtest, so sánh theo thể loại) → **bán cho studio**. Đây là thứ tạo doanh thu.

Một bên là *phán quyết công khai*, một bên là *tư vấn riêng*. Trộn hai bên là mô hình 2008.

---

## 3. Ba mô hình đã chứng minh — và Game9K nên học gì ở từng cái

Nguyên tắc chọn: chỉ học mô hình mà **doanh thu không phụ thuộc việc người chơi phải đầu tư**, vì đó chính là ràng buộc người dùng nêu.

### 3.1. Voodoo — *greenlight bằng dữ liệu, giết rất nhanh*

**Bằng chứng:** Voodoo thử khoảng **1.500 nguyên mẫu mỗi năm** và chỉ đưa ra thị trường khoảng **4 game/năm** sau khi tái cấu trúc sang hybridcasual (2023) [2][3]. Cách diễn đạt cũ hơn từ chính Voodoo: *"với mỗi game phát hành, chúng tôi thử 100 nguyên mẫu"* [4].

**Học gì:** tỷ lệ chấp nhận ~0,3% **không phải dấu hiệu bộ máy hỏng** — đó là *sản phẩm*. Voodoo bán **năng lực loại bỏ**, không bán game.

**Khác biệt sống còn:** Voodoo **sở hữu** nguyên mẫu nên giết được. Game9K **không sở hữu** game của studio — nó chỉ nói "bản này chưa đạt". Đây là lý do Game9K phải bán *bằng chứng* chứ không bán *phán quyết*: studio không đạt sẽ đi nơi khác, còn nếu có báo cáo chẩn đoán thì họ quay lại.

**Không học được:** Voodoo giết nguyên mẫu **trước khi** có người chơi thật. Game9K cần người chơi thật để đo — nên Game9K không thể giết rẻ như Voodoo.

### 3.2. Poki — *cổng có biên tập, kiếm tiền từ sự chú ý*

**Bằng chứng:** Poki tự công bố **100M+ MAU** và **1 tỷ lượt chơi/tháng** (06/2025), giữ khoảng **1.500 game** đã vượt bài kiểm tra thời gian chơi, và bổ sung **227 game mới** với khoảng **65 nhân sự** [5]. Whitepaper §4 đã dùng đúng luận điểm này: *"Poki không cần 10 triệu tựa game"*.

**Học gì:** **biên tập là hào kinh tế.** 1.500 game đã chọn lọc đáng giá hơn 10 triệu tựa rác — và người chơi hưởng lợi trực tiếp, không cần biết gì về vốn.

**Đây là mô hình gần nhất với "mạnh ở kiểm định".** Poki không bán vé đầu tư; Poki bán **sự chú ý đã được lọc**.

**Không học được:** Poki có 100M MAU trước khi có sức mạnh biên tập. Game9K đi ngược thứ tự — phải *dùng* kiểm định để *giành* người chơi. Đó là lý do nguồn thu 4 (quảng cáo) không thể là "giai đoạn 2".

### 3.3. PlaytestCloud — *bán báo cáo kiểm định, người chơi được trả tiền*

**Bằng chứng:** dịch vụ playtest từ xa có giá **từ $69/người tham gia** (đã gồm video), có gói subscription cho studio chạy thường xuyên và gói rẻ hơn cho indie [6]. Phía người chơi: một buổi 15 phút có khảo sát thường được trả **$5–$9** [7].

**Học gì:** đây là bằng chứng **có thị trường trả tiền cho đúng thứ Game9K giỏi nhất**. Và nó trả lời trực tiếp câu "game thủ không có nhu cầu đầu tư": **người chơi không cần đầu tư — họ cần được trả tiền cho 15 phút.** `SPARK` hiện là tiền ảo có giá trị đầu cơ; một khoản **$5–$9 tiền thật** là động cơ sạch hơn nhiều và **không tạo ra người chơi giả** (vì chỉ trả khi bài test được chấp nhận).

**Không học được:** PlaytestCloud bán *một buổi test*, không bán *một tài sản*. Game9K muốn cả hai — nên phải tách như §2.

---

## 4. Trả lời trực tiếp: nên học cái nào, theo thứ tự nào

Xếp theo **mức độ phụ thuộc vào nhà đầu tư** (thấp → cao), vì đó là ràng buộc người dùng đặt ra:

| Thứ tự | Học từ | Bán cho ai | Vì sao đúng lúc này |
|---|---|---|---|
| **1** | **PlaytestCloud** | studio | Chứng minh **có người trả tiền** cho kiểm định. Không cần token, không cần MAU, không cần nhà đầu tư. Có thể bắt đầu **trước** khi launchpad tồn tại |
| **2** | **Poki** | người chơi (gián tiếp: qua nhãn hàng) | Biên tập = hào kinh tế. Đã có sẵn trong whitepaper §4; chỉ cần **đặt lên trước** thay vì "giai đoạn 2" |
| **3** | **Voodoo** | — | Học **kỷ luật giết nhanh** và ngưỡng 0,3%, nhưng **không** học cách sở hữu nguyên mẫu — Game9K không sở hữu |
| **4** | **Arena đấu mù** | người chơi | Giữ, nhưng **hạ vai trò**: từ *cơ chế tạo doanh thu* xuống *cơ chế lấy dữ liệu*. Xem §5 |

**Một câu:** bán **Trust Stamp** cho người chơi (miễn phí, để họ tin), bán **báo cáo chẩn đoán** cho studio (để lấy tiền), và để **launchpad** là *tùy chọn* cho ai muốn đầu tư.

---

## 5. Hệ quả khó nghe: arena nên là *chi phí*, không phải *doanh thu*

Nếu arena đấu mù phục vụ **lấy dữ liệu** chứ không phục vụ **tạo doanh thu**, thì:

- Nó phải được **đo bằng độ sạch dữ liệu**, không bằng số người tham gia. `BotShare` và tỷ lệ đồng thuận hậu kiểm là KPI; số lượt chấm *không phải* KPI.
- Nó **không cần** 500 người chơi/tháng để có ý nghĩa — 30 người chấm đã đủ cho một phán quyết thống kê, miễn là **đúng người**. Điều này hạ mức Cold-Start xuống rất nhiều so với "500 người chơi thật/tuần".
- Nó là **dòng chi phí**, và chi phí phải trả bằng **doanh thu quảng cáo + báo cáo studio**, không bằng phí token.

> **Điều này va vào một con số trong whitepaper** (`500 người chơi thật/tuần` như điều kiện mở launchpad). Không phải con số sai — nó đúng **nếu** launchpad là sản phẩm đầu. Nó sai **nếu** sản phẩm đầu là dịch vụ kiểm định. Đây chính là thứ cần người quyết, xem §7.

---

## 6. Ba câu hỏi

**"Vậy bỏ launchpad à?"** Không. Launchpad là **nguồn thu #1–3** và là lý do tồn tại của token. Nhưng nó nên là **tầng trên** của một sản phẩm đã có người dùng thật, không phải **cửa vào**. Đây đúng là luận điểm *Gate-First* mà whitepaper đã viết ở §4 — chỉ khác chỗ **áp dụng cho chính Game9K**.

**"Nếu bán báo cáo cho studio thì lại issuer-pays như §2?"** Đúng, và đó là lý do van ở §2 phải có **trước** khi bán: chứng chỉ công khai miễn phí + không mua được; báo cáo riêng thì bán. Nếu một studio trả tiền mà điểm công khai đổi, mô hình đã chết về mặt uy tín — và cổng phải làm nó **đỏ**, không chỉ ghi trong văn xuôi.

**"Số liệu Voodoo/Poki/PlaytestCloud có tin được không?"** Voodoo và Poki là **tự công bố** qua báo chí ngành, không phải số kiểm toán — dùng để **định hình**, không dùng để tính doanh thu. PlaytestCloud có **giá niêm yết** nên kiểm được hơn. Không con số nào ở đây được đưa vào mô hình tài chính của whitepaper.

---

## 7. Chưa làm — và cần người quyết

| | Việc | Ai quyết | Vì sao chưa |
|---|---|---|---|
| **R1** | Chọn: **launchpad-first** hay **dịch vụ-kiểm-định-first** | **LXK** | Đổi thứ tự sản phẩm ⇒ đổi §3 WHO, §5.4 doanh thu, điều kiện mở launchpad, và **rebuild whitepaper + deck**. Không phải việc agent tự quyết |
| **R2** | Tách `Trust Stamp` (miễn phí) khỏi báo cáo chẩn đoán (bán) thành **hai** mục riêng trong §5.4 | LXK | Hệ quả trực tiếp của R1; nếu chưa chọn R1 thì tách sẽ sai |
| **R3** | Cổng canh **"điểm công khai không phải thứ mua được"** | AGENT | Kiểm được bằng máy *nếu* R2 đã tách. Hiện chưa có mục riêng để canh ⇒ chưa viết cổng (viết trước là canh một thứ không tồn tại) |
| **R4** | Kiểm lại `500 người chơi thật/tuần` theo kết luận §5 | LXK | Con số này là **điều kiện dừng đã công bố**; đổi nó cần người, không cần agent |

> **Giới hạn của tài liệu này:** tôi **không** sửa whitepaper, không đổi bất kỳ con số nào, không thêm cổng nào. Một câu hỏi chiến lược mở ra bốn quyết định thuộc về người — và viết cổng trước khi có quyết định là cách tạo ra một cổng canh hư không.
