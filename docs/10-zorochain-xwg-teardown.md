# Teardown ZoroChain + XWG — bài học cơ chế cho Game9K

> **Tài liệu sống:** `docs/10-zorochain-xwg-teardown.md`
> **Nguồn:** `ZoroChain_WhitePaper_EN.pdf` (35 trang) và `X World Games White Paper {v2.0.0}.pdf` (56 trang)
> **Ngày đọc:** 22/11/2026 · **Người đọc:** đội dự án Game9K
> **Câu hỏi:** hai mô hình này **dạy được gì** cho Game9K, và **cái gì không nên bắt chước**?

---

## 0. Kết luận trước, chi tiết sau

Hai whitepaper này **không phải đối thủ** của Game9K — ZoroChain là hạ tầng tính toán phi tập trung (L2 + engine game `BlaCat`), XWG là hệ sinh thái game Web3 đa chuỗi. Nhưng ZoroChain có **một cơ chế đáng học** và nó chạm đúng chỗ yếu nhất của Game9K.

**Điểm đáng học (ZoroChain, tr. 6):** *Proof-of-workload* — điểm tích luỹ từ lịch sử xác nhận giao dịch/khối, điều chỉnh mỗi **604.800 block (~1 tuần)** theo `NewWorkload = 0.9 × OldWorkload`. Điểm này **dựa trên hành vi thật, không mua được, và giảm dần nếu không tiếp tục đóng góp**.

**Chỗ Game9K yếu hơn họ:** `pop_score` (0–100) của Game9K quyết định **PoP Tier**, mà Tier quyết định **quyền mua sớm 24h + trần mua mỗi ví + chia 10% Community Pool** — ba thứ có tiền thật đằng sau. Nhưng cho tới trước tài liệu này, `pop_score` **chưa có luật suy giảm**: một ví chơi vài ngày rồi ngồi im vẫn giữ nguyên Tier mãi mãi.

**Đã vá trong cùng thay đổi này:** đưa suy giảm theo epoch vào schema + đặc tả, và chốt tham số bằng một script kiểm chứng được (`scripts/verify_pop_decay.py`, 11 bất biến).

> **Cảnh báo về mức độ kiểm chứng:** cả hai PDF là **whitepaper tự công bố**, không có mã nguồn, không có kiểm toán độc lập, không có số liệu vận hành. Vì vậy tài liệu này **chỉ trích dẫn cơ chế được mô tả**, **không** dùng bất kỳ con số hiệu năng, lưu lượng hay giá token nào của họ.

---

## 1. ZoroChain — Proof-of-workload, nguyên văn và đọc kỹ

### 1.1. Nguyên văn (tr. 6, mục STC / VRF-BFT)

> "Proof-of-workload: The historical participated transaction confirmation and consensus block will be converted into points and accumulated to the node. […] **Work score is adjusted once every 604,800 blocks (about a week). The adjustment algorithm is: NewWorkload = 0.9\*OldWorkload.** By adjusting the algorithm, nearest integral weight can be kept higher than historical one. Each period integral decreases with time."

Điểm này là một trong **hai** tham số quyết định "reliability" của node trong STC, cái còn lại là **node mortgage** (số token stake). Danh sách node được sắp theo `Fx(mortgage, proof-of-workload)`, lấy **top 100** làm ứng viên VRF-BFT.

### 1.2. Ba điều đúng — và đúng với cả Game9K

| # | Điều đúng | Vì sao quan trọng |
|---|---|---|
| **Z1** | **Điểm đến từ hành vi đã xảy ra**, không mua được, không tự khai | Nếu mua được thì nó là một loại cổ phần trả trước; uy tín biến thành thứ mua được bằng tiền |
| **Z2** | **Suy giảm theo thời gian** — "each period integral decreases with time" | Uy tín là **trạng thái hiện tại**, không phải **huy hiệu vĩnh viễn**. Không suy giảm thì người bỏ đi vẫn giữ quyền |
| **Z3** | **Gắn với một nhịp cố định** (604.800 block) | Nhịp công khai, tính trước được, không phụ thuộc "lúc nào admin thấy cần" |

### 1.3. Điều **không** bê nguyên được

**Vấn đề số học:** `NewWorkload = 0.9 × OldWorkload` áp cho **mọi** node. Nghĩa là một node hoạt động **hoàn hảo, liên tục** cũng bị nhân 0,9 mỗi tuần: `0,9^n → 0`. Sau 22 tuần còn ~10%, sau 44 tuần còn ~1%.

Điều này chỉ chấp nhận được **nếu** điểm được cộng lại đủ nhanh trong kỳ — whitepaper không nói tốc độ cộng. Với một mạng node chạy 24/7 thì giả định đó có thể đúng. Với **người chơi** thì không: người chơi không chạy 24/7, và một cơ chế khiến người chơi đều đặn vẫn tụt điểm là cơ chế **sai về mặt thiết kế**, không phải "chặt".

**Cách Game9K dùng:** giữ nguyên tắc Z1–Z3, đổi công thức thành

```
work_new = max(play_this_epoch, W × work_old)      W = 0.60, epoch = 7 ngày
score    = 100 × work / (work + 180)
```

- `max(...)` chứ không phải `×`: **người chơi đều giữ nguyên**, chỉ người **ngồi im** mới bị trừ.
- `W = 0,60`: mạnh hơn 0,9 của ZoroChain, vì mỗi epoch của Game9K là 7 ngày **của người**, không phải 604.800 block **của máy**.
- `100 × work/(work+180)`: bão hoà, nên **không ai chạm 100** và **không mua được** — chỉ có phút chơi hợp lệ mới đẩy được điểm lên.

---

## 2. ZoroChain còn lại: đường ống, không phải thị trường

Nhận định này **đúng** và đáng ghi lại vì nó chính là khoảng trống Game9K nhắm vào.

| Thành phần | ZoroChain có gì | Game9K có gì |
|---|---|---|
| **Escrow / ký quỹ theo mốc** | Không. `BlaCat` có "Presale / crowdfunding … with agreed return mechanisms" (tr. 34) — **một dòng mô tả, không có cơ chế** | 4 tranche gắn `M1..M4`, mỗi tranche chỉ mở khi phiên bản mới vượt kiểm định |
| **Cổng chất lượng** | **Không có tiêu chí nào**. "Game rating system based on the community" (tr. 30) — do cộng đồng chấm, không có ngưỡng, không có mẫu số | Phễu Poki 4 chặng (10 phiên → 500 lượt → Web Fit → Curated) + Version Arena + 95% CI |
| **Chống bơm-rồi-bỏ** | Không. Không có gì ràng buộc dev phải ship bản mới | Version-Gated: mỗi tranche cần **một phiên bản tốt hơn** |
| **Ai bán token** | Node (thợ đào) nhận thưởng khối | Studio, và chỉ theo chặng đã kiểm định |
| **Nhãn dữ liệu game** | "Data disclosure" — registered users, active users, paid users **do dev tự khai** (tr. 32) | Số đo **do cổng tự đếm** qua SDK (heartbeat + input entropy), dev không tự khai được |

Hai chỗ ZoroChain mô tả **giống ý Game9K** nhưng dừng ở mức khẩu hiệu:

1. **"Game version progress announcement"** (tr. 32) — hiển thị lịch sử phát triển, bản hiện tại, kế hoạch tương lai "under supervision of community users". Game9K làm **cơ học**: không có bằng chứng phiên bản mới ⇒ không mở tranche.
2. **Weihting hoá người chấm** (tr. 32) — "user weighting algorithm … prevent robots and bots from brushing comments". Game9K có `pop_score` + `sybil_risk_score`, và bây giờ có thêm **suy giảm**.

> **Bài học cốt lõi:** ZoroChain mô tả đúng **vấn đề** (uy tín phải đến từ hành vi và phải suy giảm), nhưng giải ở **tầng hạ tầng**. Game9K phải giải ở **tầng thị trường** — nơi tiền thật đổi chủ.

### 2.1. Điểm kỹ thuật khác đáng ghi (không áp dụng bây giờ)

| Nội dung | Trang | Đánh giá |
|---|---|---|
| Ba tầng thưởng khối `50/40/10` (đề xuất / đồng thuận / pool) | 21 | Cơ chế phân phối rõ ràng — nhưng là cho node, Game9K không có node |
| Pool chia `30%` cho top-10 workload + `10%` random trong danh sách | 22 | **Ý hay**: thưởng theo công lao **và** một phần ngẫu nhiên để chống độc quyền. Game9K đã có tương đương: PoP Tier + ưu tiên theo mốc |
| Node application cần ký quỹ `10.000 ZORO` | 24 | Rủi ro tập trung vốn; Game9K không có tầng node |
| `MappingChain` / `RootChain` / application chain song song | 9–15 | Vấn đề Game9K **không có** (chỉ một chương trình trên Solana) |

---

## 3. XWG whitepaper v2.0.0 — đối chiếu với những gì quan sát được trên site

`docs/09-xwg-portal-teardown.md` đã kết luận từ **quan sát site**. Đọc whitepaper xác nhận thêm, và **sửa một điểm**:

| Điểm | Whitepaper nói | Trạng thái |
|---|---|---|
| **Doanh thu** | 4 dòng: NFT sales · Player subscriptions & services · Transaction fees · Advertising & partnerships (tr. 36) | Xác nhận: không có dòng nào là "phí mở khoá theo mốc chất lượng" |
| **Bonding curve** | X Swap dùng bonding curve **cho NFT collection**, tham số do người tạo pool đặt (linear/exponential + delta) (tr. 19) | Xác nhận: curve ở đây là **công cụ định giá NFT**, không phải cơ chế mở khoá vốn theo tiến độ |
| **Bắt buộc ví** | Whitepaper cam kết "accessibility improvements for Web2 users" (tr. 37) — nhưng FAQ hiện hành vẫn nói **cần ví** | **Mâu thuẫn giữa whitepaper và tài liệu vận hành** → dùng FAQ (thực tế) làm bằng chứng, không dùng whitepaper |
| **Tự khai là "protocol"** | "XWG is a leading gaming protocol on blockchain" (tr. 5) | Không kiểm chứng được; không trích |
| **Disclaimer** | Rất đầy đủ (tr. 8–9): không phải lời khuyên đầu tư, không phải chào bán chứng khoán, có forward-looking statements | **Đáng học về hình thức** — xem §4 |

### 3.1. Bài học hình thức đáng copy (rẻ, và giảm rủi ro)

Whitepaper XWG có mục **Disclosures** đứng **trước** phần nội dung (tr. 8), nêu rõ: tài liệu không tạo quan hệ hợp đồng, không phải chào bán chứng khoán, token chưa được cơ quan quản lý nào phê duyệt, và có **forward-looking statements**.

Game9K đã có tương đương một phần (`Phạm vi` trong `llms.txt`, ghi chú "số liệu là dự phóng"). **Không cần thêm gì trong PR này** — nhưng nếu về sau mở rộng whitepaper cho nhà đầu tư nước ngoài, đây là bố cục nên tham chiếu.

---

## 4. Bảng quyết định

| Mã | Nội dung | Trạng thái | Nơi áp dụng |
|---|---|---|---|
| **P1** | Điểm uy tín từ **hành vi đã kiểm chứng**, không mua được | **ADOPT — đã có** | `pop_score` / `SPARK` |
| **P2** | Điểm **suy giảm theo epoch** nếu không đóng góp | **ADOPT — vá trong PR này** | `scripts/verify_pop_decay.py`, `docs/02-database-schema.md`, `docs/PRD.md` |
| **P3** | `NewWorkload = 0.9 × OldWorkload` **nguyên bản** | **REJECT** | Phạt cả người chơi đều (0,9ⁿ → 0). Thay bằng `max(play, 0,60 × cũ)` |
| **P4** | Nhịp epoch **công khai, cố định** (~1 tuần) | **ADOPT** | Epoch = 7 ngày, không phải "khi admin thấy cần" |
| **P5** | Trọng số người chấm để chống bot | **ADOPT — đã có** | `arena_votes_valid`, `arena_consensus_rate`, `sybil_risk_score` |
| **P6** | "Community rating system" **không ngưỡng** | **REJECT** | Game9K dùng ngưỡng số học + CI, không dùng "cộng đồng thấy tốt" |
| **P7** | Presale một dòng mô tả, không escrow | **REJECT** | Game9K: 4 tranche gắn mốc kiểm định |
| **P8** | Dữ liệu game do **dev tự khai** | **REJECT** | Cổng tự đo qua SDK; dev không tự khai số |
| **P9** | Mục **Disclosures** đặt trước nội dung | **THAM KHẢO** | Chưa cần; ghi lại cho lần mở rộng whitepaper |

---

## 5. Đã thay đổi gì trong cùng PR này

| Tệp | Thay đổi |
|---|---|
| `scripts/verify_pop_decay.py` | **Mới.** Chốt `W=0,60`, `H=180`, epoch 7 ngày; in bảng 8 tuần cho 6 kiểu người chơi; 11 bất biến; mã lỗi 1 nếu sai |
| `docs/02-database-schema.md` | Thêm `pop_work`, `pop_work_updated_at` vào `player_pop_states` + ghi chú "không ghi thẳng `pop_score`" |
| `docs/PRD.md` | `FR-POP-01` ghi rõ công thức suy giảm và script kiểm chứng |
| `.github/workflows/docs.yml` | Job `verify` chạy thêm `verify_pop_decay.py` |

**Không** đổi: mô hình doanh thu, số liệu kinh tế, deck, whitepaper, yellow paper, 4 tệp PDF. PR này chỉ **thêm luật suy giảm** cho một cột đã có.

## 6. Không làm

- Không đưa bất kỳ số liệu hiệu năng/lưu lượng/giá token nào của ZoroChain hay XWG vào tài liệu Game9K.
- Không bê tầng node/consensus của ZoroChain — Game9K chạy trên Solana, không vận hành chuỗi riêng.
- Không đổi `W` mà không chạy lại `verify_pop_decay.py`: mọi ngưỡng Tier trong bảng đều là hệ quả của `W`, `H`.
