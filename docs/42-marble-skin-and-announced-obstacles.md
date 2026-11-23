# 42 — Skin bi, chướng ngại, và ba đề xuất phải từ chối

> **Tài liệu sống:** `docs/42-marble-skin-and-announced-obstacles.md` — bản gốc ở đây.
> **Trạng thái:** `DONE` (vòng 43) · mã ở `assets/game9k-starter-kit.bundle` (v1.1.0)
> **Tiền đề:** `docs/17` §6 **R6** (quà không đổi thứ hạng) · `docs/18` §3.3 (reskin ≠ game mới) · `docs/23` §1.2 (giấy phép)

---

## 0. Ba dòng

Yêu cầu có hai phần: **thêm game Marble Race**, và **chuẩn hoá hai game khủng long** theo ba cơ chế (skin bi, bẫy ngẫu nhiên, PK giữa hai streamer).

Phần **skin bi** làm được, và đã làm — nhưng là **lớp vẽ**, không phải engine mới. Phần **bẫy ngẫu nhiên** hoá ra engine **đã có** từ v1.0.0, chỉ là nó **không xuất ra kết quả** nên overlay không vẽ được. Phần **PK giữa hai streamer** phải từ chối, và lý do không phải khẩu vị — nó phá đúng thứ làm nên sản phẩm.

Ba con số dưới đây là toàn bộ lập luận:

| | Đo được | Ý nghĩa |
|---|---|---|
| Bán kính bi `11 px` | **36 bi/làn × 5 = 180** không đè (lý thuyết) | nhưng trần engine là **80 người** |
| Chướng ngại `0‰` → `30‰` | lật kèo **2% → 39%** | chướng ngại **có** tạo kịch tính |
| Chướng ngại `30‰` → `120‰` | về đích **8,9 → 0,0** trên 80 | kịch tính **ăn mất** cuộc đua |

---

## 1. "Thêm game Marble Race" — đây là reskin, và điều đó tốt

`docs/18` §3.3 đã viết quy tắc trước khi có yêu cầu này:

> *reskin ≠ game mới* — nếu `sha256` của file luật **trùng**, đó là cùng một game, chỉ khác ảnh.

Yêu cầu "thay sprite khủng long bằng viên bi dán avatar" **đúng là** trường hợp đó. Và điều đó **tốt**, vì:

- Luật không đổi ⇒ **cân bằng không đổi** ⇒ mọi số đã công bố vẫn đúng (xem §5).
- Không có engine thứ hai ⇒ không có fixture vàng thứ hai ⇒ không có hai nguồn sự thật.
- Người xem **không** phải học lại luật.

> **Nếu gọi nó là "game mới"** thì mỗi skin là một game, và quy tắc `reskin ≠ game mới` trở thành vô nghĩa — đúng lúc nó cần có hiệu lực nhất.

---

## 2. Skin bi — làm gì, và giới hạn ở đâu

**Đã dựng: `src/web/marble.mjs`** — hàm thuần, 3 việc: `layoutMarbles()`, `maxPerLane()`, và hằng số hình học.

| Bất biến | Cách canh |
|---|---|
| Không import, không DOM, không `Date`, không `Math.random` | `check_marble.py` bất biến 1 |
| Avatar **không** đổi `x`, `y`, `r` | bất biến 2 — chạy cùng input với/không avatar, so từng toạ độ |
| Engine **không đọc** khoá `marble` | bất biến 3 — grep `race.mjs` |
| Đổi `finish_units` ⇒ toạ độ đổi | bất biến 4 — nếu không, lớp vẽ tự đặt luật riêng |

**Vì sao avatar không được đổi bán kính:** quà mua skin. Nếu skin to hơn ⇒ dễ nhìn hơn ⇒ đó là **lợi thế mua được**, đúng thứ `docs/17` §6 **R6** cấm. Phép phá **P2** của `check_marble.py` chèn đúng lỗi đó và cổng phải đỏ.

### 2.1. Con số "hàng trăm viewer" — đúng về hình học, sai về hệ thống

`maxPerLane({radius_px: 11})` = **36 bi/làn**; 5 làn ⇒ **180** bi không đè nhau.

Nhưng `rules.players.max` = **80**. Vẽ bi **không nâng trần đó**: trần do `seedFor(seed, index)` và kích thước `ranking` quyết định, không do hình dạng nhân vật.

| Bán kính | Bi/làn | Tổng lý thuyết | Trần thật |
|---|---|---|---|
| `8 px` | 47 | 235 | **80** |
| `11 px` | 36 | 180 | **80** |
| `16 px` | 26 | 130 | **80** |

> **Đổi sang bi KHÔNG làm game chứa được nhiều người hơn.** Nó làm **80 người hiện tại** dễ nhìn hơn. Muốn 180 người thật thì phải sửa `players.max` **và** đo lại toàn bộ cân bằng — việc đó **chưa làm**, và không nên làm nhân danh một thay đổi đồ hoạ.

---

## 3. Chướng ngại — engine đã có, nhưng nó vô hình

Đây là phát hiện đáng chú ý nhất của vòng này.

Từ **v1.0.0**, `race.mjs` đã có:

```js
const hit = p.state % 1000 < obstaclePermille ? obstaclePenalty : 0;
```

Tức chướng ngại **đã tồn tại và đã ảnh hưởng kết quả**. Nhưng `result` **không có** mục nào mô tả chúng ⇒ overlay **không biết** chúng xảy ra ⇒ người xem chỉ thấy những con số nhảy bất thường.

> **Đề xuất "thêm bẫy ngẫu nhiên để tăng kịch tính" thực chất là: làm cho một cơ chế đã có trở nên NHÌN THẤY ĐƯỢC.** Không phải thêm cơ chế mới.

### 3.1. Đã sửa (v1.1.0)

- Khối `obstacles` tách khỏi `speed`: `rate_permille`, `penalty`, `announce_ticks`, `target`.
- Mỗi va chạm vào `result.obstacles` với **hai** mốc: `announce_tick` (overlay bắt đầu báo) và `impact_tick` (thật sự bị chậm).
- `announce_ticks = 8` ⇒ **0,8 giây** báo trước. Người xem thấy trước khi nó xảy ra.

`announce_tick` **tất định** (một hằng số trừ đi), nên phát lại vẫn khớp `sha256` — không phải "hiệu ứng phía client".

### 3.2. Mọi chướng ngại đều ảnh hưởng người bị nó — không ai nhắm vào ai

`obstacles.target = "self_only"`, và `check_rules_hash.py` **đỏ** nếu khác. Không có "thả banana trước mặt người dẫn đầu" (đúng thứ `marble-race` README mô tả, và `docs/23` §4.1 đã từ chối).

Lý do không phải khẩu vị: **một cuộc đua mà người dẫn đầu bị bắn hạ bởi người không dẫn đầu là một cuộc đua không đo kỹ năng.** Nó đo *ai trả tiền nhiều hơn* — và trên livestream, đó là hình ảnh của cá cược.

---

## 4. Đo: chướng ngại có tạo "lật kèo giây cuối" không?

Thước đo: **người dẫn ở 80% thời gian (tick 360/450) có thắng không?** Nếu luôn thắng ⇒ không có kịch tính. Chạy **120 ván × 80 người**, 40 người bấm hoàn hảo.

| `rate_permille` | Lật kèo (leader@80% ≠ winner) | Về đích TB | Cách biệt ≤ `0,2 s` |
|---|---|---|---|
| **`0‰`** | **`2%`** | `71,5/80` | `37/120` |
| **`30‰`** (hiện tại) | **`39%`** | `8,9/80` | `19/120` |
| `60‰` | `44%` | `0,1/80` | `0/120` |
| `120‰` | `49%` | `0,0/80` | `0/120` |

**Đọc bảng này:**

- Đề xuất **đúng một nửa**: chướng ngại tạo lật kèo thật, `2% → 39%`. Đó là mức thay đổi lớn nhất trong mọi tham số đã thử.
- Nhưng nó **sai về liều**: từ `30‰` lên `120‰` chỉ thêm `10` điểm lật kèo, mà **xoá sạch** tỷ lệ về đích (`8,9 → 0,0`).
- Nghịch lý cần nói rõ: **nhiều "kịch tính" hơn nghĩa là ít người về đích hơn.** Một cuộc đua mà gần như không ai về đích không phải kịch tính — nó là hỏng.

> **Kết luận:** `30‰` là **điểm cân**, không phải tham số trang trí. Và câu "tăng cảm giác lật kèo ở giây cuối" **không** đạt được bằng cách tăng số bẫy — nó đạt được bằng cách **cho người xem thấy bẫy trước** (`announce_ticks`), thứ vừa làm mà không đổi một đơn vị cân bằng nào.

---

## 5. Cân bằng không đổi — bằng chứng

Đây là điều quan trọng nhất để biết thay đổi này **an toàn**:

```
v1.0.0 (trước)                       v1.1.0 (sau)
về đích  10,8%                       về đích  10,8%
0/60 ván người-không-bấm thắng       0/60
trung vị 7/80, p10 1, p90 35         trung vị 7/80, p10 1, p90 35
```

**Y hệt.** Vì sao? Vì chướng ngại **không đổi hành vi engine** — nó chỉ **xuất ra** thứ engine đã làm. Đây là phép thử đúng cho một thay đổi "chỉ để nhìn thấy được".

Cái **đổi** thì phải đổi, và đã đổi có kiểm soát:

| | Trước | Sau |
|---|---|---|
| `rules` version | `1.0.0` | **`1.1.0`** |
| `rules_sha256` | `f910cb52…` | **`7c0f470a…`** |
| Fixture vàng | 3 | 3 (**sinh lại**, diff đã đọc) |
| Cổng | 5/5 | **6/6** |

Python (`ref_engine.py`) khớp Node trên cả 3 fixture ⇒ luật mới vẫn kiểm chứng chéo hai ngôn ngữ.

---

## 6. Đề xuất 3 — PK giữa hai streamer: từ chối

> *"Điểm Gift của khán giả bên nào to hơn sẽ thả chướng ngại vật sang đường đua của bên đối thủ."*

Đây là **hai** cơ chế ghép lại, và cả hai đều vi phạm luật đã công bố:

| Thành phần | Vi phạm | Tham chiếu |
|---|---|---|
| Quà quyết định ai được thả bẫy | quà đổi thứ hạng ⇒ pay-to-win | `docs/17` §6 **R6** |
| Người A đặt bẫy lên đường người B | `obstacles.target` phải `self_only` | `docs/42` §3.2 |
| "Bên nào nhiều gift hơn thắng" | thứ hạng phụ thuộc số tiền | `docs/23` §4.1 |

**Nhưng mục tiêu của đề xuất thì đạt được, theo cách khác.** Cái làm nên "trận đấu" không phải quyền hại đối thủ — nó là **hai bảng xếp hạng cạnh nhau trên cùng một màn hình**:

| Giữ | Bỏ |
|---|---|
| Hai phòng đua, hai `seed` **công bố riêng**, hai `result_sha256` | quà đặt bẫy sang đường đối thủ |
| Điểm đội = **tổng** thành tích thành viên, không phải tổng gift | bất kỳ cơ chế nào để người ngoài can thiệp vào đường đua |
| Bảng đối đầu hiện **số người về đích**, **hạng trung vị**, **số lệnh đúng nhịp** | "gift to hơn thì thắng" |
| Quà vẫn có giá trị: skin, vệt chạy, thẻ cảm ơn có tên | — |

> Đây không phải phiên bản yếu hơn. Đây là phiên bản **so sánh được**: hai đội chơi cùng một luật, cùng một seed công bố, và người xem kiểm chứng được cả hai bên. Cơ chế PK bằng gift **không so sánh được** — nó chỉ đo ví tiền, và nó phá luật thứ ba của kit.

---

## 7. Hai game khủng long — "chuẩn hoá" nghĩa là gì

Trong repo này hiện có **một** luật đua (`rules/dino-1.0.0.json`, nay `1.1.0`). Yêu cầu nhắc tới *"Dino Race"* và *"Jurassic Sanctuary Sprint"* như hai game.

**Sự thật:** bản `1.1.0` là **một** luật, chạy được với **hai** lớp vẽ:

| Lớp vẽ | Trạng thái |
|---|---|
| Thanh khủng long (vẽ trong code, không sprite) | có, từ v1.0.0 |
| Viên bi + avatar | **có, từ v1.1.0** (`src/web/marble.mjs`) |

**Không có** file luật thứ hai tên `jurassic-sanctuary`. Nếu muốn nó là **game khác** (luật khác), thì theo `docs/18` §3.3 phải có `rules/*.json` riêng + `version` riêng + fixture riêng + số cân bằng riêng — **chưa làm**, và **không nên làm** chỉ để có hai cái tên. Xem **W1**.

---

## 8. Ba câu hỏi

**"Nếu skin bi chỉ là lớp vẽ, sao phải làm cổng riêng?"** Vì lớp vẽ **có** quyền truy cập vào `ranking`, và dòng code đổi bán kính theo avatar chỉ dài **một dòng**. `check_marble.py` P2 chèn đúng dòng đó; không có cổng thì nó lọt, và quà thành pay-to-win qua đường hình thức.

**"`announce_ticks = 8` có phải tham số làm đẹp?"** Không — nó **không** đổi kết quả (nó chỉ đổi thời điểm *hiện*). Đó là loại tham số duy nhất được thêm vào mà **không** cần đo lại cân bằng. Nếu nó từng đổi `finish_tick`, §5 sẽ khác.

**"TikTok-Live-Connector v2 / Gateway Multi-Tenant đã có trong kit chưa?"** Chưa. Kit có `observer-tiktok.mjs` (phụ thuộc **tuỳ chọn**, AGPL — `docs/23` §1.2) và **không** có gateway đa phòng: `race-store` giữ **một** ván đang mở. Hai phòng song song cho PK là việc của **W2**, sau khi quyết §6.

---

## 9. Chưa làm

| | Việc | Vì sao chưa |
|---|---|---|
| **W1** | Luật riêng cho `Jurassic Sanctuary Sprint` (nếu thật sự là game khác) | Phải có số cân bằng riêng + fixture riêng; làm hai cái tên trên một luật là tự lừa |
| **W2** | Chế độ 2 phòng song song (bản **hợp luật** của đề xuất PK, §6) | `race-store` đang giữ một ván; cần thiết kế khoá theo `room_id`. Chỉ nên làm sau khi §6 được chấp nhận |
| **W3** | Nâng `players.max` lên trên 80 | Đổi trần ⇒ đổi toàn bộ số cân bằng (10,8% · 7/80). Cần người quyết, không phải một thay đổi đồ hoạ |
| **W4** | `observer-youtube` | `AGENTS.md` của kit cấm hứa "hỗ trợ YouTube" khi chưa có; `docs/23` §7 ghi rõ chưa kiểm chứng |

> **Điều đáng nhớ:** ba đề xuất, và **cả ba** đều đã có câu trả lời trong repo từ trước — `docs/18` §3.3 (reskin), `docs/23` §4.1 (quà và người dẫn đầu), `docs/17` §6 R6 (quà và thứ hạng). Việc của vòng này không phải nghĩ ra luật mới, mà là **làm cho luật cũ kiểm được bằng máy** — và đó là lý do có `check_marble.py` thay vì một đoạn văn.
