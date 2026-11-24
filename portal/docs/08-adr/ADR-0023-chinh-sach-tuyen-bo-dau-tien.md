# ADR-0023 — Chính sách tuyên bố "đầu tiên": phân loại, điều kiện, và cưỡng chế bằng CI

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-21
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [ADR-0021](ADR-0021-builddiff-toan-cuc.md) §4 (bài học "không tìm thấy ≠ không tồn tại"), [ADR-0022](ADR-0022-the-loai-cong-bang.md), [`whitepaper-vi.md` §5.2](../11-whitepaper/whitepaper-vi.md), [`changelog/`](../../changelog/)

---

## 1. Bối cảnh — và vì sao cần ADR này

Trong whitepaper hiện có **bốn** tuyên bố "lần đầu tiên":

| # | Vị trí | Câu |
|---|---|---|
| A | §1 "Một câu" | *"Game9K là Bệ phóng Vốn đồng bộ theo phiên bản Game **đầu tiên trên Thế giới**"* |
| B | §5.2 Mới #1 | *"**Lần đầu tiên**, một đợt tài trợ cộng đồng gắn với một bản cập nhật cụ thể"* |
| C | §5.2 Mới #2 | *"**Lần đầu tiên**, quyền tham gia một đợt tài trợ bị ràng buộc bởi hành vi sử dụng thật"* |
| D | §5.2 Mới #3 | *"**Lần đầu tiên**, điểm của một bản game là có thể kiểm chứng công khai"* |

Cùng lúc, §① của chính whitepaper ghi: *"không hứa, chỉ nêu điều khác biệt"*. Và README của
whitepaper đặt quy tắc số 1: *"Không có số liệu không kiểm được."*

**Đây là tự mâu thuẫn có sẵn.** Một tuyên bố "đầu tiên" về bản chất là tuyên bố **phủ định
toàn cầu** ("chưa ai từng làm") — không thể kiểm chứng bằng bất kỳ artifact nào. Nó vi phạm
quy tắc số 1 của chính tài liệu.

### Bài học từ ADR-0021 §4

Ở ADR-0021, cùng một lỗi đã xảy ra và được ghi lại: phép đo trên 4 game **không chứng minh**
được `θ_diff = 800 bps` là đúng; nó chỉ cho thấy công thức sai. Kết luận đúng đã ghi là
*"đo được"* chứ không phải *"đã đúng"*.

Áp dụng cùng chuẩn đó cho tuyên bố "đầu tiên": **không tìm thấy phản ví dụ ≠ không tồn tại
phản ví dụ.** Việc tìm kiếm của chúng tôi là hữu hạn; không gian launchpad là vô hạn và
thay đổi hàng tuần.

### Vì sao đây là rủi ro thật, không phải chuyện câu chữ

| Rủi ro | Hậu quả |
|---|---|
| Nhà đầu tư Mỹ đã nghe hàng trăm "world's first" | Bị đọc là dấu hiệu dự án thiếu tự nhận thức → giảm uy tín |
| Một phản ví dụ được nêu công khai | Toàn bộ tài liệu mất trọng lượng, kể cả phần đúng |
| Tuyên bố phủ định toàn cầu trong tài liệu gọi vốn | Có thể bị coi là tuyên bố gây nhầm lẫn — cần luật sư xem |

---

## 2. Quyết định — ba loại tuyên bố, ba mức bằng chứng

Mọi tuyên bố về tính mới trong tài liệu Game9K **phải** được phân loại vào một trong ba loại
dưới đây, và **phải xuất hiện trong bảng §4** của ADR này.

### Loại 1 — `PROVEN` (chứng minh được)

Tuyên bố **khẳng định** một tính chất mà repo hoặc chain chứng minh được.

| Đặc điểm | Giá trị |
|---|---|
| Dạng câu | "Game9K **làm X**" (không phải "chưa ai làm X") |
| Bằng chứng | Artifact chạy lại được: script, test, chữ ký on-chain, hoặc tệp trong repo |
| CI kiểm | Có đường dẫn artifact trong cùng mục |
| Ví dụ | *"Ngưỡng chất lượng nằm trong `check_governance.py`: hạ ngưỡng làm CI đỏ"* |

### Loại 2 — `NO_COUNTEREXAMPLE` (chưa tìm thấy phản ví dụ)

Tuyên bố về **điều khác biệt**, kèm minh bạch rằng việc tìm kiếm là hữu hạn.

| Đặc điểm | Giá trị |
|---|---|
| Dạng câu **bắt buộc** | "Chúng tôi **chưa tìm thấy** … nếu bạn biết, xin cho biết" |
| **Cấm** | "đầu tiên", "duy nhất", "chưa ai từng", "world's first", "first ever" |
| Bằng chứng | Ghi lại **đã tìm ở đâu** (nguồn + ngày) để người khác kiểm lại được |
| CI kiểm | Câu chứa "đầu tiên"/"duy nhất" ⇒ đỏ |
| Ví dụ | *"Chúng tôi chưa tìm thấy launchpad nào lấy phiên bản làm đơn vị tài sản"* |

### Loại 3 — `NEEDS_DATA` (cần dữ liệu)

Tuyên bố cần số liệu chưa có. **Không được ở dạng khẳng định.**

| Đặc điểm | Giá trị |
|---|---|
| Dạng câu **bắt buộc** | "chưa có dữ liệu" hoặc "giả thuyết, chưa kiểm chứng" |
| Điều kiện chuyển sang `PROVEN` | Ghi rõ: cần bao nhiêu mẫu / điều kiện gì |
| CI kiểm | Câu khẳng định về số liệu mà không có nguồn ⇒ đỏ |
| Ví dụ | *"`θ_D7,C` của `idle-incremental` là giả thuyết, chưa có nguồn"* |

---

## 3. Điều kiện để giữ câu "đầu tiên" (nếu PO muốn giữ)

PO **có thể** giữ câu "đầu tiên", nhưng chỉ khi thoả **cả bốn** điều kiện:

| # | Điều kiện | Kiểm được? |
|---|---|---|
| 1 | Ghi rõ **phạm vi** ("đầu tiên" trong ngành nào, trên chain nào, tính đến ngày nào) | Có — dạng câu |
| 2 | Ghi rõ **đã tìm ở đâu** (nguồn + ngày tra cứu) | Có — mục bắt buộc |
| 3 | Có **cơ chế tự bác bỏ**: nêu điều gì sẽ khiến tuyên bố sai | Có — dạng câu |
| 4 | Có **ngày hết hạn**: tuyên bố "đầu tiên" cũ đi theo thời gian | Có — trường ngày |

Tuyên bố không thoả cả bốn ⇒ **hạ xuống loại 2** (`NO_COUNTEREXAMPLE`), tức đổi thành
*"chúng tôi chưa tìm thấy"*.

> **Đề xuất của AI:** hạ **cả bốn** tuyên bố hiện có xuống loại 2. Không phải vì chúng sai,
> mà vì loại 2 **mạnh hơn** trong pitch: nó mời phản biện, và nhà đầu tư giỏi đọc đó là dấu
> hiệu người làm thật. "Đầu tiên" chỉ thuyết phục người không kiểm tra.

---

## 4. Bảng phân loại tuyên bố hiện có

| # | Tuyên bố | Loại hiện tại (ngầm) | Loại đề xuất | Bằng chứng / lý do |
|---|---|---|---|---|
| A | "Bệ phóng Vốn đồng bộ theo phiên bản Game đầu tiên trên Thế giới" | khẳng định "đầu tiên" | **`NO_COUNTEREXAMPLE`** | Phủ định toàn cầu, không kiểm được |
| B | "Lần đầu tiên, tài trợ gắn với một bản cập nhật cụ thể" | khẳng định "đầu tiên" | **`NO_COUNTEREXAMPLE`** | IGO gắn với *game*; gắn với *version* thì chưa thấy |
| C | "Lần đầu tiên, quyền tham gia tài trợ bị ràng buộc bởi giờ chơi" | khẳng định "đầu tiên" | **`NO_COUNTEREXAMPLE`** | Play-gate có ở nhiều nơi; play-gate **áp lên tài trợ** thì chưa thấy |
| D | "Lần đầu tiên, điểm version kiểm chứng công khai" | khẳng định "đầu tiên" | **`NO_COUNTEREXAMPLE`** | Merkle anchor đã phổ biến; neo **điểm version** thì chưa thấy |
| E | "Ngưỡng chất lượng khoá bằng CI" (Mới #5) | — | **`PROVEN`** | [`check_governance.py`](../../scripts/check_governance.py) — hạ ngưỡng là CI đỏ |
| F | "`θ_D7,C` của `idle-incremental` / `multiplayer-arena`" | — | **`NEEDS_DATA`** | Đã đánh dấu `source: assumed` trong `params.toml` |

### Đã tìm ở đâu (cho các mục loại 2)

Tra cứu ngày **2026-11-21**, cho tuyên bố A–D:

| Nguồn | Đã xem | Kết quả |
|---|---|---|
| Solana Compass — launchpad category | Meteora, Portals, arc, vvaifu, Collaterize, dev.fun | Không cái nào lấy **phiên bản** làm đơn vị tài sản |
| CoinPaprika — crypto launchpads 2026 | pump.fun, Raydium LaunchLab, four.meme, Clanker, Virtuals | Tất cả ở cấp **token**, không cấp phiên bản |
| IGO / GameFi launchpad (Seedify, Gamestarter, Enjinstarter, TrustPad) | Mô hình IGO | Gắn với **game**, không với **phiên bản** |
| Season/phase token (khảo sát chung) | Nhiều dự án | Gần giống nhưng là đợt phát hành, không phải đơn vị tài sản |

**Kết luận trung thực:** không tìm thấy phản ví dụ trực tiếp. Nhưng mô hình **season/phase
token** là **tương tự gần nhất** và phải được nêu ra — nếu không nêu, tuyên bố sẽ bị bắt bẻ
đúng ở điểm đó.

---

## 5. Cưỡng chế bằng CI

`scripts/check_claims.py` kiểm ba thứ:

| Kiểm | Cách | Chặn điều gì |
|---|---|---|
| 1. Không có từ cấm ở loại 2 | Regex trên các tệp tuyên bố: `đầu tiên\|duy nhất\|chưa ai từng\|world's first\|first ever` | Tuyên bố "đầu tiên" tự quay lại |
| 2. Mục loại `NO_COUNTEREXAMPLE` có mục "đã tìm ở đâu" | Tệp ADR này phải có §4 với bảng nguồn | Tuyên bố không có cơ sở tra cứu |
| 3. Mục loại `NEEDS_DATA` có dấu hiệu | Câu phải chứa `chưa có dữ liệu` / `giả thuyết` / `assumed` / `chưa có nguồn` | Số chưa có bị viết như số thật |

**Ngoại lệ có kiểm soát:** ADR này và `changelog/` được phép chứa từ cấm khi **đang thảo luận**
về chúng (như §1 ở trên). Script chỉ quét tệp tuyên bố, và có danh sách ngoại lệ tường minh.

---

## 6. Hệ quả

**Chấp nhận:**
- Bốn câu "đầu tiên" phải đổi thành "chúng tôi chưa tìm thấy". Mất một chút độ mạnh bề mặt, được nhiều hơn về độ tin.
- Phải nêu **season/phase token** là tương tự gần nhất — tự nêu điểm yếu trước khi người khác nêu.
- Mỗi tuyên bố loại 2 cần một mục "đã tìm ở đâu" và phải cập nhật khi tra cứu lại.

**Bắt buộc:**
- Mọi tuyên bố mới về tính mới **phải** vào bảng §4 trước khi vào whitepaper.
- Tuyên bố loại 2 phải có câu mời phản biện — đó là điều kiện để loại 2 mạnh hơn loại "đầu tiên".

## 7. Điều ADR này KHÔNG nói

- **Không** nói Game9K không phải đầu tiên. Không ai biết. Nó nói: **chưa đủ cơ sở để khẳng định**.
- **Không** cấm dùng "đầu tiên" trong hội thoại, slide nội bộ, hay email. Chỉ cấm trong **tài liệu công bố**.
- **Không** thay thế ý kiến pháp lý. Tuyên bố gây nhầm lẫn trong tài liệu gọi vốn vẫn cần luật sư xem.
