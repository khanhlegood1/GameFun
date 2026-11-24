# ADR-0024 — Sản phẩm lợi suất là dòng riêng, tách hẳn khỏi launchpad

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-22
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [Nguyên lý đơn vị Khánh](../00-framework/nguyen-ly-don-vi-khanh.md), [ADR-0023](ADR-0023-chinh-sach-tuyen-bo-dau-tien.md), [`changelog/README.md` §6](../../changelog/README.md)

---

## 1. Bối cảnh

PO quyết định: **muốn có một sản phẩm lợi suất**, nhưng nó phải **tách hẳn** khỏi
launchpad — dòng sản phẩm riêng, **không chia sẻ escrow, không chia sẻ điểm**.

Bối cảnh kỹ thuật: Renzo Basis và các mô hình Basis/Yield (Kava, funding-rate
strategies) kiếm lợi suất từ **funding rate** — chênh lệch spot/perp, trả bởi
người dùng đòn bẩy. Game9K kiếm giá trị từ **giờ chơi thật**.

Hai nguồn lợi suất này **khác bản chất**, không chỉ khác cơ chế:

| | Basis / Yield | Game9K launchpad |
|---|---|---|
| Nguồn lợi suất | Funding rate | Giờ chơi thật |
| Ai tạo ra | Người dùng đòn bẩy | Người chơi |
| Đo được khi nào | Realtime | Sau 24h + merkle anchor |
| Điều kiện thắng | Vị thế lớn hơn | Milestone đạt |
| Rủi ro chính | Funding âm, thanh lý | Chất lượng game |

### Vì sao "tách hẳn" là **yêu cầu kiến trúc**, không phải sở thích

[Nguyên lý đơn vị Khánh](../00-framework/nguyen-ly-don-vi-khanh.md) đứng trên một
tuyên bố duy nhất: **điểm không mua được bằng tiền**. Nếu vốn basis chảy vào cùng
một escrow hoặc cùng một hệ điểm, thì:

```
vốn lớn  →  vị thế lớn  →  điểm lớn  →  phá vỡ KVU
```

Người có vốn nhiều nhất luôn thắng, đúng thứ KVU được thiết kế để chống. Vì vậy
tách biệt không phải "cho gọn" — nó là **điều kiện để KVU còn đúng**.

---

## 2. Quyết định

### 2.1 Sản phẩm lợi suất là một dòng riêng

| Thuộc tính | Launchpad | Sản phẩm lợi suất |
|---|---|---|
| Mã định danh | `game9k-*` | `g9k-yield-*` |
| Program ID | `game9k_curve`, `game9k_escrow`, `game9k_rewards`, `game9k_registry` | chưa đặt — **không** dùng program ID của launchpad |
| Kho tiền | `curve_vault`, `escrow` | ví riêng, **không** là `curve_vault` hay `escrow` |
| Điểm | `GameScore` theo version | **không có điểm** — sản phẩm này không tạo điểm |
| Mint token | mint riêng mỗi phiên bản | **không** mint token của launchpad |
| Đơn vị kế toán | phiên bản game | tài sản cơ sở (SOL/USDC/BTC…) |

### 2.2 Ba quy tắc tách biệt — phải kiểm được

Một lời hứa "tách hẳn" không kiểm được thì không có giá trị. Ba quy tắc dưới đây
được cài vào CI (xem §4):

**R1 — Không chung kho tiền.**
Không địa chỉ nào vừa là `curve_vault`/`escrow` của launchpad vừa là kho của sản
phẩm lợi suất. Hệ quả: một lỗ hổng ở sản phẩm lợi suất **không** chạm được escrow
của studio.

**R2 — Không chung đường dẫn điểm.**
Sản phẩm lợi suất không được ghi vào `GameScore`, `RatingRootAccount`, hay bất kỳ
account nào thuộc luồng điểm. Hệ quả: lợi suất **không** quy đổi được thành điểm.

**R3 — Không chung quyền quản trị.**
Khoá quản trị của sản phẩm lợi suất (Squads multisig) **không** trùng khoá quản trị
launchpad. Hệ quả: một quyết định về sản phẩm lợi suất không mở được cổng nào của
launchpad, và ngược lại.

> **Vì sao R3 quan trọng nhất.** R1 và R2 chặn rò rỉ **kỹ thuật**. R3 chặn rò rỉ
> **quản trị** — và rò rỉ quản trị khó thấy hơn nhiều: hai sản phẩm "tách" về code
> nhưng chung 2/3 chữ ký thì thực chất là một.

### 2.3 Điều sản phẩm lợi suất **được** phép

Tách biệt **không** có nghĩa là cấm mọi liên hệ. Ba thứ được phép, và nên có:

| Được phép | Vì sao |
|---|---|
| Dùng chung thương hiệu Game9K | Cùng công ty, khác sản phẩm — như Google Docs và Google Ads |
| Chia sẻ hạ tầng **không mang trạng thái** (RPC, indexer, oracle giá) | Không tạo đường rò rỉ tài sản |
| Công bố lợi suất trong cùng nhật ký `changelog/` | Minh bạch; nhưng phải **ghi rõ là dòng khác**, và tuân quy tắc số liệu hiện có |

**Cấm rõ ràng:** dùng lợi suất để **thưởng** cho người chơi, hoặc dùng giờ chơi để
**tăng** lợi suất. Hai chiều đều bị cấm — đó chính là chỗ hai dòng sản phẩm sẽ dính
vào nhau nếu ai đó muốn "tăng trưởng".

---

## 3. Vì sao không tích hợp vào launchpad (phương án đã loại)

| Phương án | Vì sao loại |
|---|---|
| **A. Lợi suất trên escrow chưa giải ngân** | Nghe hấp dẫn: tiền nhàn rỗi sinh lãi. Nhưng nếu lợi suất **âm**, escrow giảm và milestone không trả đủ. Người tài trợ chịu rủi ro funding mà họ không chọn. **Phá bất biến §1.4** (E_k ≥ 0) của [chứng minh](../00-framework/kvu-chung-minh-bon-tang.md) |
| **B. Lợi suất làm phần thưởng mùa** | Lợi suất thành điểm ⇒ người có vốn lớn có nhiều điểm ⇒ phá KVU. Vi phạm R2 |
| **C. Cùng một program, hai chế độ** | Không kiểm được R1 ở tầng địa chỉ. Một lỗi chế độ này chạm chế độ kia. Vi phạm R1 |
| **D. Dòng riêng, tách hoàn toàn** | ✅ **Đã chọn** |

**Phương án A đáng cân nhắc nhất và bị loại vì lý do cụ thể:** nó biến escrow — nơi
phải **không bao giờ** giảm ngoài nghĩa vụ milestone — thành nơi chịu rủi ro thị
trường. Một bất biến đã chứng minh được sẽ mất hiệu lực.

---

## 4. Cưỡng chế

### 4.1 Trong CI (`scripts/check_yield_isolation.py`)

| Kiểm | Cách | Chặn điều gì |
|---|---|---|
| R1 | Grep đường dẫn chứa cả `g9k-yield` và `curve_vault`/`escrow` trong cùng một dòng cấu hình | Dùng chung kho tiền |
| R2 | Không tệp `g9k-yield-*` nào import module điểm | Rò rỉ điểm |
| R3 | Khoá quản trị khai báo trong `params.toml` phải **khác** nhau | Rò rỉ quản trị |

### 4.2 Ở tầng vận hành

- **Nhật ký phải ghi dòng sản phẩm** cho mọi mục số liệu liên quan lợi suất.
- **Không** cộng lợi suất vào số liệu launchpad khi báo cáo. Nếu báo tổng, phải
  tách hai dòng.

---

## 5. Hệ quả

**Chấp nhận:**
- Phải xây một dòng sản phẩm nữa — chi phí thật, không nhỏ.
- Không tận dụng được escrow nhàn rỗi (phương án A bị loại).
- Phải duy trì hai bộ khoá quản trị và hai quy trình audit.

**Bắt buộc:**
- Chưa được viết code sản phẩm lợi suất trước khi có: (a) ADR này được ký, (b) thiết
  kế kho tiền riêng, (c) ý kiến pháp lý về việc chào bán sản phẩm lợi suất.
- Sản phẩm lợi suất **không** được xuất hiện trong whitepaper launchpad cho tới khi
  tách biệt được kiểm chứng bằng code chạy thật.

## 6. Điều ADR này KHÔNG nói

- **Không** nói sản phẩm lợi suất sẽ dùng chiến lược nào. Basis? Funding farming?
  Staking? Chưa quyết — và **phải** là ADR riêng.
- **Không** nói sản phẩm lợi suất có token riêng hay không.
- **Không** nói thực thể nào vận hành sản phẩm lợi suất — câu đó ở
  [ADR-0025](ADR-0025-game9k-foundation-san-pham-loi-suat.md), nơi giải thích vì sao
  một "Foundation" **không thể** vận hành sản phẩm lợi suất thương mại.
- **Không** thay thế ý kiến pháp lý. Một sản phẩm lợi suất **có thể** bị xem là chào
  bán chứng khoán ở Mỹ, khác hoàn toàn với launchpad. Đây là câu hỏi mới, không nằm
  trong ba câu ở [`changelog/README.md` §6](../../changelog/README.md).

---

## 7. Tự kiểm — ADR này sai ở đâu?

1. **R1 và R2 kiểm được bằng grep, nhưng grep không chứng minh runtime tách biệt.**
   Chúng chặn *cấu hình sai*, không chặn *lỗi logic*. Bằng chứng thật phải là test
   trên chain.
2. **R3 phụ thuộc việc khoá quản trị được khai báo trong repo.** Nếu khoá thật được
   tạo ngoài repo, CI không biết. Cần thêm bước xác nhận thủ công có chữ ký.
3. **Có một rủi ro chưa xử lý:** nếu sản phẩm lợi suất thất bại, uy tín Game9K bị
   ảnh hưởng **dù tách biệt về kỹ thuật**. Tách biệt kỹ thuật không tách biệt thương
   hiệu. Đây là đánh đổi PO đã chấp nhận, nhưng phải ghi lại.
