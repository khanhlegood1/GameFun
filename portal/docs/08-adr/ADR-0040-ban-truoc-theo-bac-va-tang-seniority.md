# ADR-0040 — Bán trước theo bậc (thang giá giảm dần) và tên cho tầng thanh toán: **KMU**

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`Nguyên lý đơn vị Khánh`](../00-framework/nguyen-ly-don-vi-khanh.md) · [`KVU-2 KAU`](../00-framework/nguyen-ly-don-vi-khanh-tang-hai.md) · [`kvu-chung-minh-bon-tang.md`](../00-framework/kvu-chung-minh-bon-tang.md) · [`ADR-0011`](ADR-0011-legal-posture.md) · [`ADR-0023`](ADR-0023-chinh-sach-tuyen-bo-dau-tien.md) · [`yellowpaper-vi.md` §4.4](../11-whitepaper/yellowpaper-vi.md) · [`PRD` REQ-M5](../01-requirements/PRD-game9k.md)

> Viết theo luật thứ tư của [`AGENTS.md`](../../AGENTS.md): **grep trước khi khẳng định**. Mọi phát
> hiện dưới đây đều kèm tệp + mục nơi nó được kiểm, hoặc ghi rõ là suy luận.

---

## 0. Trả lời ngắn

Bạn đề nghị bốn thứ. Bốn thứ đó **không cùng một mức độ đúng**, và gộp chúng lại là chỗ dễ mất
niềm tin nhất vào tài liệu:

| # | Đề nghị | Đánh giá |
|---|---|---|
| 1 | Bán trước theo **bậc giá giảm dần cho tất cả người đang trong nhóm** | ✅ **Đúng về cơ chế** — và có một lợi thế **đo được** so với bonding curve hiện tại |
| 2 | Kênh thu sớm cho studio (bán gói chơi, vật phẩm trước khi escrow giải ngân) | ✅ **Đúng nhu cầu**, nhưng đụng **hai chỗ** đã có luật: play-gate và escrow milestone |
| 3 | "Tách tài sản rủi ro cao thành chuỗi tài sản rủi ro thấp hơn, mỗi cái có kỳ hạn" | ⚠️ **Đã nằm trong repo** — `VGBC-4T` nghĩa là *4 Tranches*, và §6 escrow đã chia 4 mốc. Bạn **không** đề xuất điều mới; bạn đề xuất điều **chưa được hiện thực đúng như tên của nó** |
| 4 | "An toàn hơn trái phiếu quốc gia nhờ định lý KVU + Zero-Knowledge" | ❌ **Không chứng minh được, và repo đã có tài liệu nói ngược lại** |

**Một câu:** đề nghị 1 và 2 **đáng làm**; đề nghị 3 **đã có, nhưng đang hở**; đề nghị 4 **phải
hạ xuống** nếu không muốn cả tài liệu mất trọng lượng.

---

## 1. Đề nghị 1 — bán trước theo bậc: đúng, và có lợi thế đo được

### 1.1. Cơ chế

> *"Giá là một thang bậc, không phải cú giảm giá. Mỗi bậc được lấp đầy sẽ hạ đơn giá cho tất cả
> người đang trong nhóm — kể cả người vào sớm nhất."*

Đây là **giá đồng nhất theo bậc** (uniform-price tiered pricing): giá áp cho **mọi** người trong
nhóm ở cùng một thời điểm, và **giảm** khi nhóm lớn lên. Người vào sớm **không** bị phạt vì vào
sớm — họ hưởng lợi từ những người vào sau.

### 1.2. Vì sao nó tốt hơn bonding curve cho mục tiêu "an toàn cho nhà đầu tư nhỏ"

Bonding curve hiện tại (`R(s) = V·VT/(VT−s) − V`) có một tính chất **đã được ghi trong repo**:

> `docs/11-whitepaper/yellowpaper-vi.md` §5 — `early_exit_fee_bps ≤ 800`, và số đo được là
> **−12,71%** (hồ sơ A, trần 800 bps) và **−8,92%** (hồ sơ B) khi thoát sớm.

Nghĩa là: người vào **sớm** trên curve mua giá thấp, nhưng nếu họ phải thoát sớm, họ mất
8–13%. Và người vào **sau** mua giá cao hơn — curve chỉ tăng, không bao giờ giảm cho người đã vào.

| | Bonding curve (hiện tại) | Bậc giá giảm dần (đề nghị 1) |
|---|---|---|
| Người vào sớm | Giá thấp nhất, **nhưng** thoát sớm mất 8–13% | Vẫn giá thấp nhất, **và** được giảm thêm khi nhóm lớn |
| Người vào sau | Giá **cao hơn** — không có cách nào rẻ hơn | Giá **giảm** theo bậc |
| Động lực mời người mới | Không có (người mới làm giá tăng cho người cũ) | **Có** — mỗi người mới hạ giá cho tất cả |
| Rủi ro "snipe" | Có — REQ-M5-010 đã phải thêm cảnh báo | **Giảm** — vào sớm không còn là đặc quyền duy nhất |

**Đây là lợi thế thật, và nó đo được:** bậc giá giảm dần biến mỗi người tham gia thành người
**làm lợi cho người đã ở trong**. Bonding curve thì ngược lại.

### 1.3. Ba vấn đề kỹ thuật phải giải trước khi cài

**(a) Mâu thuẫn với bonding curve, không phải bổ sung cho nó.**
REQ-M5-003 yêu cầu mua/bán trên curve với slippage guard. Nếu bán trước theo bậc **cùng lúc** với
curve, một người có thể mua ở bậc thấp rồi bán ngay trên curve ở giá cao hơn ⇒ **arbitrage miễn
phí**, và người mua sau trên curve trả giá đó.

⇒ Phải chọn: **hoặc** bán trước theo bậc **đóng trước khi** curve mở, **hoặc** curve không tồn tại
cho phiên bản đã bán trước. Không được cả hai cùng lúc trên cùng một phiên bản.

**(b) "Hạ giá cho tất cả, kể cả người vào sớm nhất" cần một cơ chế hoàn tiền.**
Nếu A mua ở bậc 1 (giá 10) và bậc 2 hạ giá còn 9, A phải được **hoàn 1**. Hoàn bằng gì?

| Cách | Vấn đề |
|---|---|
| Hoàn SOL | Studio đã tiêu tiền đó rồi. Cần **escrow** giữ phần chênh — nhưng escrow đang dành cho milestone (REQ-M5-006) |
| Hoàn bằng token bổ sung | Làm tăng cung ⇒ pha loãng chính người vừa được "thưởng". **Không** miễn phí |
| Ghi công bằng credit nội bộ | Không phải tiền ⇒ phải nói rõ trong hợp đồng, nếu không là hứa hão |

**Đây là chỗ ADR này chưa có câu trả lời, và tôi không tự chọn.** Xem Q-ADR40-a.

**(c) Game thủ Việt Nam quen "mua sớm giá rẻ".**
Bậc giá giảm dần nghĩa là **mua sớm không rẻ hơn** mua muộn — ngược hoàn toàn với kỳ vọng thị
trường. Người mua sớm chịu **rủi ro dự án không thành** mà không có bù đắp giá. Đây là vấn đề
**niềm tin**, không phải vấn đề toán. Xem Q-ADR40-b.

---

## 2. Đề nghị 2 — kênh thu sớm cho studio: đúng nhu cầu, đụng hai luật đã có

### 2.1. Nhu cầu là thật

Escrow giải ngân theo milestone `M0 → M1 → M2 → M3/M4` (REQ-M5-006). Mốc `M2` cần
`N_sess ≥ 500` **và** `N_duel ≥ 50` **và** `LCB₀.₉₅ > 0.50` (`yellowpaper-vi.md` §4.4). Với một
studio nhỏ, đạt `M2` có thể mất **hàng tháng**. Trong khoảng đó studio **không có tiền** để làm
bản tiếp theo, dù người chơi đã trả tiền.

⇒ Bán trước gói chơi / vật phẩm là một kênh thu **không phụ thuộc milestone**. Đó là câu trả lời
đúng cho một khoảng trống có thật.

### 2.2. Nhưng nó đụng luật thứ nhất: play-gate

`REQ-M5-004` và BDD `FUND-04`: 24 giờ đầu, ví có **0 phút chơi verified** **không** được mua, với
lỗi on-chain `PlayGateNotSatisfied`. Lý do đã ghi: chặn bot.

Bán gói chơi cho **người chưa chơi** là **đi ngược** luật đó. Nếu bán được, bot mua hết gói trước
khi có người chơi thật nào.

⇒ Phải chọn **một**:
- bán trước **chỉ cho ví đã có `verified_minutes`** (giữ play-gate, nhưng thu hẹp thị trường);
- hoặc bán trước **mở**, nhưng **tách hẳn** khỏi launch — không token, chỉ vật phẩm tiêu dùng
  trong game, và **không** cấp quyền gì trên launch.

Đây là câu Q-ADR40-c.

### 2.3. Và nó đụng luật thứ hai: escrow

Nếu studio bán gói chơi **trước khi** phiên bản tồn tại, người mua đã trả tiền cho một thứ **chưa
có**. Repo đã có `Refund path nếu fail M0 trong 14 ngày` (REQ-M5-007) — nhưng đó là cho **launch**,
không phải cho **pre-order vật phẩm**.

⇒ Pre-order cần **cùng một cơ chế hoàn tiền**, và nó **chưa có**. Ghi vào Q-ADR40-d.

### 2.5. Đính chính — có luật thứ ba, và tôi đã bỏ sót khi viết mục này

`docs/05-contracts/tokenomics.md` §8 **"Những gì KHÔNG làm"** ghi:

> | **Presale trước khi có curve** | Chính là chỗ bot & VC xả lên retail; xoá bỏ ưu thế của
> người chơi thật |

Đây là **luật đã ban hành**, không phải chỗ trống. Nên mục 2 ở trên **không** được đọc là "presale
được phép". Phân biệt quyết định:

| | Presale **bị cấm** (§8) | Bán trước **có thể** được |
|---|---|---|
| Bán gì | **Token / quyền kinh tế** của launch | **Vật phẩm tiêu dùng** trong game (skin, gói chơi, mùa) |
| Người mua nhận | Quyền trên dòng tiền / thặng dư của version | Thứ **tiêu thụ được**, không sinh lời |
| Thị trường thứ cấp | Có ⇒ bot xả được | Không ⇒ không xả được |

⇒ Mục 2 chỉ nói về **cột phải**. Cột trái đã bị cấm và **vẫn bị cấm**. Xem
[`2026-11-18-don-vi-tang-truong-va-mo-hinh-hoc.md`](../12-decisions/2026-11-18-don-vi-tang-truong-va-mo-hinh-hoc.md) §1.

### 2.4. "Lợi nhuận kép / quyền lợi kép"

Cụm này **không được vào tài liệu cho nhà đầu tư** ở dạng hiện tại. Lý do: nó mô tả một kết quả
**chưa đo được** bằng ngôn ngữ của kết quả đã chắc chắn. Theo ADR-0023, đây là loại 3
(`NEEDS_DATA`).

Dạng viết được: *"Studio có thêm một kênh thu **trước** khi milestone giải ngân; người chơi nhận
vật phẩm sớm hơn. Lợi ích cho nhà đầu tư **chưa được đo** — không có dữ liệu."*

---

## 3. Đề nghị 3 — "tách thành chuỗi tài sản": đã có trong repo, và đang hở

### 3.1. Bạn không đề xuất điều mới — và đó là tin tốt

`docs/11-whitepaper/yellowpaper-vi.md` §4.4:

> **`VGBC-4T`** = **V**ersion-**G**ated **B**onding **C**urve · **4 T**ranches
> (*"Chuẩn VGBC 4 Chặng"* — bốn chặng `150→330→530→700M`, curve `70%`, `Y₀ = 30 SOL`).
> **`VBOND-LV`** = **V**ersion **B**ond · **L**ow **V**olatility (*"Version Bond Đầm giá"* —
> một chặng `600M`, curve `60%`, `Y₀ = 60 SOL`).

Và §4.4 `GATE_TABLE` đã chia giải ngân escrow thành **bốn mốc** có vị từ nghiệm thu riêng:
`M0` 30% · `M1` 40% · `M2` 30% · `M3` 0% (mặc định).

⇒ **Cấu trúc "tách thành chuỗi, mỗi mốc một kỳ hạn" đã tồn tại trong thiết kế.** Nó tên là
`4 Tranches`, và nó đã có luật nghiệm thu từng mốc.

### 3.2. Chỗ hở thật — và đây là phát hiện của ADR này

**"Tranche" trong repo hiện là tranche của *escrow* (phía studio), không phải tranche của *quyền
kinh tế* (phía nhà đầu tư).**

Kiểm bằng grep (đã chạy):

| Tìm | Kết quả |
|---|---|
| `senior` / `subordinat` / `tranch` trong `docs/11-whitepaper/*.md` | **không có cơ chế ưu tiên thanh toán** — chỉ có tên `4 Tranches` và `unlock_tranche` trong automaton |
| Cơ chế nào quy định **thứ tự** ai được trả trước khi tiền không đủ | **không có** |

Nghĩa là: hiện tại **mọi nhà đầu tư của một phiên bản xếp cùng một hàng**. Nếu escrow không đủ để
trả hết, không có luật nào nói ai được trả trước.

**Đây mới là "tách tài sản rủi ro cao thành chuỗi rủi ro thấp hơn" mà bạn muốn** — và nó
**chưa tồn tại**. Đó là một cơ chế **thứ tự ưu tiên** (seniority), không phải thêm một tranche
nữa của escrow.

### 3.3. Vì sao tôi không tự cài nó, và cảnh báo pháp lý

Một cơ chế ưu tiên thanh toán biến quyền kinh tế thành **hai hạng khác nhau**. Đó đúng là định
nghĩa vận hành của **trái phiếu ưu tiên / trái phiếu thứ cấp** — tức là **chứng khoán** trong
nghĩa của pháp luật Việt Nam.

Và `ADR-0011` đã ghi:

> *"Bond có bị coi là 'chứng khoán' theo Nghị định 155/2020 không?"* — **Trạng thái: Proposed,
> cần legal opinion. Blocking cho GA.**

⇒ Thêm seniority **làm nặng** câu hỏi đang chặn GA, không nhẹ đi. Không thể cài trước khi có ý
kiến luật sư. Xem Q-ADR40-e.

---

## 4. Đề nghị 4 — "an toàn hơn trái phiếu quốc gia": phải hạ xuống

Đây là phần tôi phải nói thẳng, vì nếu để nguyên nó sẽ làm mất trọng lượng của **mọi** tuyên bố
khác trong repo.

### 4.1. Repo đã tự bác bỏ ba trong bốn mệnh đề

| Mệnh đề | Repo nói gì |
|---|---|
| "nhờ **định lý** của KVU" | `nguyen-ly-don-vi-khanh.md` §4.2: *"❌ *'Nguyên lý Khánh đã chứng minh rằng…'* — nguyên lý **không chứng minh gì cả**; nó **đề xuất**."* Cái **có** định lý là `kvu-chung-minh-bon-tang.md`, và nó chỉ chứng minh **H1/H2/H3** — ba hệ quả về curve/escrow/điểm. **Không** chứng minh "an toàn hơn trái phiếu quốc gia" |
| "hơn cả độ an toàn của trái phiếu quốc gia" | `kvu-chung-minh-bon-tang.md` §7: H1–H3 `PROVEN` **chỉ ở tầng toán + mật mã + code mẫu**; *"**Chưa** `PROVEN` ở tầng hệ thống chạy thật — `programs/` vẫn trống (S6)"*. Trái phiếu quốc gia được bảo đảm bằng **ngân sách có thẩm quyền thuế**. Repo **không có** gì tương đương, và không tuyên bố có |
| "không con người nào can thiệp, kể cả bot" | `yellowpaper-vi.md` §4.4 `GATE_TABLE`: `M3` cần `HITL_curator`, `M4` cần `HITL_release`. **Có** người trong đường đi, có chủ ý |
| "kiểm chứng bằng Zero-Knowledge" | grep `zero-knowledge` / `zk-SNARK` trong `docs/01-requirements/` và `docs/02-nfr/`: **không có kết quả**. Cơ chế kiểm chứng hiện tại là **merkle root + chữ ký** (§7 yellowpaper), không phải ZK |

### 4.2. Vì sao "hơn trái phiếu quốc gia" là câu **sai về loại**, không chỉ sai về số

Trái phiếu quốc gia có ba thứ mà repo này **không có và không tuyên bố có**:

| Trái phiếu quốc gia | Game9K hôm nay |
|---|---|
| Nghĩa vụ trả nợ bằng **quyền đánh thuế** | Không có nghĩa vụ trả nợ. Đây là **quyền kinh tế có điều kiện** (ADR-0011) |
| Thị trường thứ cấp có thanh khoản | Chưa có. `programs/` trống |
| Được luật định nghĩa và bảo vệ | `ADR-0011` **đang chờ legal opinion**, blocking GA |

Một thứ **chưa chạy được** không thể "an toàn hơn" một thứ đã chạy được hàng thế kỷ. So sánh đó
không phải tự tin — nó là **nhầm loại**.

### 4.3. Dạng viết được, và nó vẫn mạnh

> *"KVU được chứng minh ở **tầng mô hình** cho ba hệ quả H1–H3, có script tái lập được. Chúng tôi
> **chưa tìm thấy** launchpad nào lấy phiên bản làm đơn vị tài sản. Chúng tôi **chưa** chứng minh
> được ở tầng hệ thống vì `programs/` chưa có mã. Chúng tôi **không** so sánh với trái phiếu quốc
> gia — khác loại."*

Theo ADR-0023, đây là loại **`NO_COUNTEREXAMPLE`** + **`NEEDS_DATA`**, và nó **mạnh hơn** trong
pitch: nó mời phản biện. ADR-0023 §3 đã nói đúng điều này: *"'Đầu tiên' chỉ thuyết phục người
không kiểm tra."*

---

## 5. Tên cho tầng mới — và vì sao tôi **không** đặt tên ngay

### 5.1. Tiền lệ đã có, và nó chỉ ra cách đặt tên đúng

| Tên | Là gì | Tầng |
|---|---|---|
| **KVU** | Đơn vị tài sản là **phiên bản**, không phải game | tài sản |
| **KAU** | Đơn vị kiểm toán của một lần đo là `(model, phiên bản)` | biên bản |

Cả hai đều đặt tên cho **một đơn vị**, không phải cho một tính năng. Đó là quy ước cần theo.

### 5.2. Tầng còn thiếu, đúng theo phát hiện ở §3.2

Nếu PO chấp thuận seniority, tầng đó là: **thứ tự ưu tiên thanh toán của một phiên bản**.

Đề xuất tên, kèm lý do — nhưng **chưa đặt**:

| Ứng viên | Nghĩa | Vấn đề |
|---|---|---|
| **KSU** — *Khanh's Seniority Unit* | đơn vị thứ tự ưu tiên | Dễ đọc nhầm thành "KSU" của trường đại học; chữ "seniority" gợi chứng khoán — đúng về pháp lý nhưng **xấu** về marketing |
| **KTU** — *Khanh's Tranche Unit* | đơn vị chặng | "Tranche" đã dùng cho escrow ⇒ **trùng nghĩa**, đúng thứ lỗi §3.2 |
| **KPU** — *Khanh's Priority Unit* | đơn vị ưu tiên | Trung tính hơn "seniority"; không gợi chứng khoán |

**Tôi không chọn hộ.** Ba lý do:

1. Đặt tên là **quyết định của PO** — ADR-0023 §4.3 nói rõ tên gắn với người **phát biểu**.
2. Tên gọi gợi **chứng khoán** là một quyết định **pháp lý**, không phải quyết định viết. `KSU`
   (seniority) và `KPU` (priority) có cùng cơ chế nhưng **khác** rủi ro pháp lý khi đọc lên.
3. Tầng đó **chưa tồn tại**. Đặt tên trước khi có cơ chế là đúng thứ `AGENTS.md` luật 3 cấm:
   *"Khai báo khoảng trống, đừng lấp bằng lời hứa."*

⇒ Q-ADR40-f.

### 5.3. Tên cho cơ chế bán trước theo bậc (§1) — cũng chưa đặt

Cơ chế này **không** phải một đơn vị tài sản mới, nên nó **không** cần tên kiểu KVU/KAU. Nó là một
**cách định giá**. Nếu cần tên, nó nên nằm trong `yellowpaper-vi.md` như một hồ sơ thứ ba cạnh
`VGBC-4T` / `VBOND-LV`.

---

## 6. Việc nên làm, theo thứ tự

| Bước | Việc | Chặn bởi | Rủi ro |
|---|---|---|---|
| **1** | Sửa **§4** — hạ bốn mệnh đề "an toàn hơn trái phiếu quốc gia" xuống `NO_COUNTEREXAMPLE` / `NEEDS_DATA` trong mọi tài liệu | Không | **Không** — đây là sửa câu chữ, làm ngay được |
| **2** | Đặc tả cơ chế bán trước theo bậc, **chưa cài** — gồm cách hoàn chênh lệch (§1.3b) và quan hệ với curve (§1.3a) | Q-ADR40-a | Không |
| **3** | Quyết quan hệ pre-order với play-gate (§2.2) | Q-ADR40-c | Không |
| **4** | Đặc tả seniority (tầng §3.2) | Q-ADR40-e (legal) + Q-ADR40-f (tên) | Cao |

**Bước 1 là phần duy nhất tôi đề nghị làm ngay**, và nó không phụ thuộc gì.

---

## 7. Tám câu cần PO quyết

| Mã | Câu hỏi |
|---|---|
| **Q-ADR40-a** | Hoàn chênh lệch khi bậc hạ giá cho người vào sớm: **SOL từ escrow**, **token bổ sung**, hay **credit nội bộ**? Mỗi cách có hệ quả khác nhau; tôi không tự chọn |
| **Q-ADR40-b** | Bậc giá giảm dần nghĩa là **mua sớm không rẻ hơn** — ngược kỳ vọng thị trường Việt Nam. Có chấp nhận đánh đổi này không? |
| **Q-ADR40-c** | Pre-order gói chơi/vật phẩm: **chỉ cho ví có `verified_minutes`** (giữ play-gate), hay **mở** nhưng tách hẳn khỏi launch? |
| **Q-ADR40-d** | Pre-order có dùng chung `Refund path` của REQ-M5-007 không, hay cần cơ chế riêng? |
| **Q-ADR40-e** | Có đặc tả **seniority** (ưu tiên thanh toán) trước khi có legal opinion của ADR-0011 không? Tôi đề nghị **không** |
| **Q-ADR40-f** | Nếu có seniority: tên là **KSU** (seniority), **KPU** (priority), hay tên khác? |
| **Q-ADR40-g** | Có làm **bước 1** (hạ bốn mệnh đề §4) ngay không? |
| **Q-ADR40-h** | Có gộp cơ chế bán trước theo bậc thành hồ sơ thứ ba trong `yellowpaper-vi.md` (cạnh `VGBC-4T`/`VBOND-LV`) không? |
| **Q70** | *(chuyển sang quyết định 2026-11-18)* Tách "bán trước vật phẩm tiêu dùng" khỏi "presale quyền kinh tế" — xem [`2026-11-18-don-vi-tang-truong-va-mo-hinh-hoc.md`](../12-decisions/2026-11-18-don-vi-tang-truong-va-mo-hinh-hoc.md) §1 |

---

## 8. Ranh giới trung thực

- **Không có dòng mã nào trong ADR này.** Nó là đặc tả và danh sách câu hỏi.
- **Không tuyên bố mô hình "đúng nhu cầu kinh tế".** Đó là `NEEDS_DATA`: chưa có người dùng thật,
  chưa có doanh thu, chưa có phép đo nào. So sánh với PumpFun/Poki là **định vị**, không phải bằng
  chứng.
- **Không khẳng định "chưa ai làm"** về seniority trong launchpad game. Theo ADR-0023 loại 2, dạng
  đúng là *"chúng tôi chưa tìm thấy"*, kèm phạm vi đã tìm. **Tôi chưa tìm** — nên câu đó **chưa
  được viết**.
- **Không dùng chữ "định lý"** cho KVU. `kvu-chung-minh-bon-tang.md` có định lý cho H1–H3; KVU
  nguyên lý **đề xuất**, không chứng minh.
- **Không nói "an toàn hơn trái phiếu quốc gia"** ở bất kỳ đâu. Xem §4.
