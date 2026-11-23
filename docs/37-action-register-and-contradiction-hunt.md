# Sổ việc có hạn, và bốn cặp câu không thể cùng đúng

> **Tài liệu sống:** `docs/37-action-register-and-contradiction-hunt.md`
> **Trạng thái:** `SCOPING` — đóng các mục mở do `docs/36` tự sinh ra + **đã dựng hai cổng** (`scripts/check_actions.py`, `scripts/find_contradictions.py`)
> **Ngày:** 23/11/2026
> **Đầu vào:** *"làm tiếp"* — không kèm yêu cầu khác
> **Liên quan:** `docs/34` (người ký + hạn) · `docs/36` §3.2/§3.3/§9 (nguồn của P1, P2, P5) · `pm/action-register.json` · `docs/YELLOWPAPER` §4.3, §6.1 · `scripts/verify_protocol_math.py`

---

## 0. Kết luận trước

**Bốn vòng vừa rồi tôi dựng bốn cổng, và cả bốn đều kiểm *sự hiện diện*.** Có nhãn chưa (`docs/33`), có owner chưa (`docs/34`), có biên bản chưa (`docs/35`), có bền chưa (`docs/36`). Không cổng nào kiểm hai thứ khác — và đúng hai thứ đó là chỗ hồ sơ gọi vốn thật sự hỏng: một **việc có hạn mà không ai canh**, và hai **câu trong tài liệu nói ngược nhau**:

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Việc `docs/36` đăng ký bằng văn xuôi có ai canh không? | **Không, cho tới vòng này.** P1 và P2 nằm trong `docs/36` §9 dưới dạng câu văn — không cổng nào đọc được, nên một việc có hạn **không có hạn** theo nghĩa máy kiểm được (§3) |
| **2** | Tài liệu có chỗ nào **tự nói ngược mình** không? | **Có, bốn cặp.** Cả bốn đều đúng ngữ pháp, từng câu đọc riêng thì hợp lý, cộng lại thì sai (§2) |
| **3** | Bốn cặp đó đã vá chưa? | **Đã vá ở dòng chữ, và vá bằng máy từ vòng này.** Nhưng phải nói rõ: vá dòng chữ mà không có cổng thì lần sửa sau làm chúng quay lại — đúng như `0%` đã quay lại **ba lần** (§2.1) |
| **4** | Đã dựng gì? | Hai cổng: `check_actions.py` (**5 bất biến**, 7 phép thử) và `find_contradictions.py` (**4 cặp**, 7 phép thử). Cổng **17** và **18** của CI (§3, §4) |
| **5** | Số nào đổi? | **Không số nào.** Mọi thay đổi là chữ nghĩa hoặc `assert`; `verify_protocol_math.py` vẫn 100%. Deck **trùng md5** với bản commit; whitepaper và yellow paper **buộc phải đổi md5** vì chữ đổi — nên tôi so **text layer từng trang** thay cho md5, và **không token số nào biến mất** (§5) |
| **6** | Có tuyên bố mới nào để nói với nhà đầu tư không? | **Không.** Và §6 nói vì sao câu *"hồ sơ không có chỗ nào tự mâu thuẫn"* là câu **không được** nói — nó đúng với **bốn cặp đã biết**, không đúng với "mọi cặp" |

> **Điều tôi từ chối ở vòng này:** biến `find_contradictions.py` thành một bộ kiểm "văn bản có mâu thuẫn không" bằng LLM. Bốn cặp ở §2 là bốn **câu hỏi hẹp, kiểm được bằng regex + một luật đọc được bằng mắt**; một bộ chấm điểm bằng mô hình ngôn ngữ sẽ cho kết quả khác nhau giữa hai lần chạy, và `docs/30` đã chốt: cổng CI của repo này **không gọi mạng**.

---

## 1. Vì sao "làm tiếp" ở đây nghĩa là đóng nợ của chính vòng trước

`docs/36` kết thúc bằng §9 "Thứ tự làm" — bốn dòng, mỗi dòng là một việc. Đọc lại bằng con mắt của `docs/34`:

| Dòng trong `docs/36` §9 | Có người? | Có ngày? | Có cổng đọc được? |
|---|---|---|---|
| **1.** P1 — ràng buộc biên `S_LP` vào `validate_launch` | **Có** (LXK) | **Có** (2026-12-18) | **Không** |
| **2.** Ghi vào §4.3 rằng gộp root theo giờ là vì rent | **Có** (LXK) | **Có** (2026-12-18) | **Không** |
| **3.** Ai hỏi biên thì trả lời `4,79×` | Không | Không | **Không** |
| **4.** Khi `programs/` chạy được: nâng bảng trạng thái | Không | Không | **Không** |

Ba trên bốn dòng là **văn xuôi**. Và `docs/34` §2 đã định nghĩa đúng lỗi này: *một hạn nằm trong văn xuôi là một hạn không có*. Việc của vòng này là biến nó thành dữ liệu có người đọc được — không phải viết thêm một đoạn văn nữa về việc đó.

> **Đây là chỗ dễ tự lừa nhất.** Cách sai là mở `docs/36` §9, in đậm thêm chữ "HẠN: 2026-12-18", rồi coi như đã xong. Chữ đậm không làm CI đỏ. Một mục trong `pm/action-register.json` thì có.

---

## 2. Bốn cặp câu không thể cùng đúng

Mỗi cặp là hai câu **đều đúng ngữ pháp**, **đều từng được viết ra để giải thích một điều đúng**, và **cộng lại thì sai**. Đây là loại lỗi khó thấy nhất khi đọc lại tài liệu của chính mình, vì không câu nào trông sai.

### 2.1. `0%` chênh lệch giá — và số đo `4.27 × 10⁻¹²`

| Nơi | Câu |
|---|---|
| `docs/WHITEPAPER.md` §1.2 | *"chuyển thanh khoản lên DEX với **`0%` chênh lệch giá**"* |
| `docs/WHITEPAPER.md` §1.3 (nguyên tử 3) và Định lý 6 | *"sai lệch giá đo được **`4.27 × 10⁻¹²`** và **`4.19 × 10⁻¹¹`**"* |

Hai câu này **không thể cùng đúng theo nghĩa chữ**: `0%` là một khẳng định tuyệt đối, `4.27e-12` là một số đo. Câu đúng — và đây là câu đã được dùng để sửa — là *"sai lệch **≤ 1 lamport**, tương đương `0%` chênh lệch giá"*: vế đầu kiểm được, vế sau là **cách nói**, và dấu `tương đương` chính là chỗ nói ra điều đó.

> **Vì sao cặp này là cặp nguy hiểm nhất:** nó đã quay lại **ba lần**. Mỗi lần sửa xong, một vòng sau lại có người viết `0%` ở một chỗ mới vì nghe hay hơn. Không có cổng, "đã sửa" chỉ có nghĩa là "đã sửa lần này".

**Luật máy kiểm:** một dòng có `0%` chênh lệch phải có một cụm nới nghĩa (`sai lệch`, `lamport`, `≈`, `tương đương`, `xấp xỉ`, `MEV`) trong **±1 dòng**. Kiểm ở mức **tệp** (phải có ít nhất một cụm nới nghĩa ở đâu đó) **và** mức **dòng** (cụm đó phải ở cạnh chính câu đó) — vì một tệp 800 dòng có chữ `sai lệch` ở dòng 129 không giúp gì cho câu ở dòng 736.

### 2.2. `LCB₀.₉₅ > 0.50` — và trường on-chain `> 5.000 bps`

| Nơi | Câu |
|---|---|
| `docs/WHITEPAPER.md` §1.3 và §4.1 | điều kiện qua cổng là $\mathrm{LCB}_{0.95} > 0.50$ — **lớn hơn** |
| `docs/YELLOWPAPER.md` §7.1 (offset `152..154`) | `arena_lcb_bps = LCB_0.95 * 10,000 …` — câu này **thiếu mệnh đề vá biên**; bản đã sửa thêm `floor ⇒ >= 5,001 bps` |

`5.000 / 10.000 = 0.50` **đúng biên**. Một implementation đọc dòng thứ hai rồi viết `lcb_bps > 5000` sẽ **mở cổng ở đúng 0.50** — tức mở ở giá trị mà dòng thứ nhất nói là **chưa đủ**. Đây là lỗi lệch một đơn vị ở biên, loại lỗi mà không ai tìm ra bằng cách đọc, chỉ tìm ra bằng cách so hai câu.

**Luật máy kiểm:** mỗi dòng nói `> 5.000 bps` phải nói **cách vá biên** trong ±2 dòng: `5.001`, `floor`, hoặc `≥ 0.5001`. Câu đã sửa trong `docs/YELLOWPAPER.md` §7.1 là: *"(…; floor ⇒ >= 5,001 bps, tức > 0.50)"*. **Con số không đổi** — nó là số đã công bố; cái thêm vào là **một mệnh đề** nói rằng `floor` cộng một bps, nên trường on-chain không bao giờ bằng đúng `0.50`.

### 2.3. Escrow `60,1998` — và `60.221994`

Hai số cùng tên "escrow", cách nhau đúng **phí tốt nghiệp** $F_{\text{grad}} = 1.50$ SOL:

| Nơi | Câu | Trước hay sau `F_grad` |
|---|---|---|
| Bản dịch whitepaper (đã dẫn ở `docs/36` §2) | *"escrow giảm còn `60,1998 SOL`"* | **trước** `F_grad` |
| `docs/YELLOWPAPER.md` §6.1 | `60.221994 SOL` | **sau** `F_grad` |

Cả hai đúng: số thứ nhất là escrow **trước** phí tốt nghiệp, số thứ hai là **sau**. Nhưng hai con số cùng tên "escrow" là đủ để một nhà đầu tư hỏi *"vậy escrow là 60,19 hay 60,22?"* — và lúc đó không ai nhớ được vì sao khác. `docs/36` **R14** đã từ chối dùng lẫn; vòng này khoá điều đó lại.

**Luật máy kiểm:** mỗi lần `60,1998` xuất hiện, trong **±2 dòng** phải có `F_grad`, `trước phí`, `sau phí`, hoặc `trước khi thu`. Không có ⇒ đỏ.

### 2.4. `programs/` rỗng — và "đã triển khai"

| Nơi | Câu |
|---|---|
| `docs/00-open-source-landscape.md` | *"gọi on-chain program **đã deploy**"* (mô tả **Squads**, một repo khác) |
| thực tế repo | `programs/` **không tồn tại** |

Đây là cặp mà `docs/36` §0 đã chạm: dòng *"chạy đúng trên chain thật"* vẫn là **`❌ chưa có`**. Nhưng câu "đã deploy" vẫn sống khoẻ trong repo — và nó **đúng** ở chỗ nó đứng (Squads đã deploy thật), nên nó không phải câu cần xoá. Nó là câu cần **không bị đọc nhầm chủ thể**.

**Luật máy kiểm:** khi `programs/` rỗng, câu khẳng định **trơn** về chính Game9K ở thì đã-hoàn-thành bị cấm — nhưng chỉ khi (a) chủ thể là Game9K/chúng tôi/dự án, hoặc (b) không có chủ thể mà có đích cụ thể (`lên mainnet`, `trên devnet`). Câu **điều kiện** (`sau khi triển khai`, `nếu`, `muốn… thì phải`) được miễn.

> **Cặp 2 cũng phải thu hẹp một lần.** Bản đầu khớp *mọi* dòng có `> 5,000 bps`, nên nó bắt luôn chính đoạn văn đang giải thích lỗi biên (và sẽ bắt mọi câu trả lời cho nhà đầu tư). Bản đúng chỉ áp lên dòng **khai báo trường** `arena_lcb_bps` — đó là câu spec; câu văn nhắc lại con số để giải thích **không** phải một khai báo miền giá trị. Ba lần thu hẹp trong một vòng, cùng một nguyên nhân: **phép khớp rộng bắt oan chính tài liệu đang dạy cách sửa**.

> **Vì sao phép miễn đó không phải nới lỏng để cổng xanh:** bản đầu tiên của cổng này bắt **4 câu**, cả 4 là câu **giả định** hoặc câu về **repo khác**. Một cổng báo sai 4/4 lần sẽ bị tắt — và khi bị tắt thì nó không bảo vệ được câu thật. `check_claims.py` đã học đúng bài này ở bản đầu (46 câu bắt, 45 sai) và ghi lại trong docstring của nó; ở đây tôi áp lại cùng kết luận: **thu hẹp có chủ đích, và ghi lý do vào mã**.

---

## 3. `check_actions.py` — việc đã hứa phải có NGƯỜI, NGÀY, HẬU QUẢ, BẰNG CHỨNG

`pm/action-register.json` giữ **việc** (xong/chưa), khác `pm/claims-registry.json` giữ **tuyên bố** (đúng/sai). Hai sổ chết theo cùng một kiểu — không ai nhớ — nhưng chúng hỏng khác nhau, nên bất biến cũng khác.

| # | Bất biến | Nó chặn đúng cái gì |
|---|---|---|
| **1** | `owner` ∈ `people`, `due` là `YYYY-MM-DD` | "để sau", "trước khi launch", "PO" (chức danh, không phải người) |
| **2** | Quá hạn ⇒ **ĐỎ**, trừ khi `DONE` kèm bằng chứng | Mục ngủ đông: vẫn `OPEN` sau ngày hạn, không ai thấy |
| **3** | `DONE` mà không có `evidence` ⇒ **ĐỎ**, và `evidence` phải trỏ tệp **có thật** | "Đã xong" là một tuyên bố; nó cần cùng loại bằng chứng như mọi tuyên bố khác |
| **4** | `DONE` trước `not_before` ⇒ **ĐỎ** | Cổng bị làm cho xanh: đóng một việc trước ngày nó *có thể* làm được |
| **5** | `source_doc` phải tồn tại; mục phải có `why` + `block_if_unmet` | Mục trôi khỏi lý do sinh ra nó, và mục không có hậu quả |

Năm việc đang mở:

| id | người | hạn | `block_if_unmet` | trạng thái | việc |
|---|---|---|---|---|---|
| **P1** | LXK | 2026-12-18 | `revert` | `OPEN` | Ràng buộc biên `S_LP < X_end·(1−f)` vào `validate_launch` |
| **P2** | LXK | 2026-12-18 | `revert` | `OPEN` | Ghi vào §4.3: gộp root Merkle theo giờ là **bắt buộc vì rent** |
| **P3** | AGENT | 2026-12-20 | `remove` | `OPEN` | `requirements.txt` + `docs/README-PDF.md` trỏ tới nó (nếu không: gỡ dòng "md5 khớp") |
| **P4** | AGENT | 2026-11-24 | `remove` | **`DONE`** | Chính `check_actions.py` là cổng 17 — việc "dựng cổng" phải tự kiểm được |
| **P5** | AGENT | 2026-11-24 | `remove` | **`DONE`** | Biên `1,25×`/`4,79×` phải là `assert` trong `verify_protocol_math.py`, không phải số in ra |

`python3 scripts/check_actions.py --audit`:

```text
P1    2026-12-18       25  LXK    OPEN       Thêm ràng buộc biên S_LP < X_end·(1−f) vào validate_launch
P2    2026-12-18       25  LXK    OPEN       Ghi vào YELLOWPAPER §4.3 rằng gộp root Merkle theo giờ là …
P3    2026-12-20       27  AGENT  OPEN       Requirements lock: ghim phiên bản Python cho mọi cổng chạy…
P4    2026-11-24        1  AGENT  DONE       Cổng thứ 17: mọi việc có hạn đều phải kiểm được (check_act…
P5    2026-11-24        1  AGENT  DONE       Biên (★) trên mô hình ĐẦY ĐỦ của cả hai hồ sơ là một bất…
```

> **P4 và P5 hết hạn trong một ngày — và đã đóng trong ngày đó.** Đó không phải sự cố: hai việc đó là việc của **vòng này**, và nếu vòng này không làm xong thì `block_if_unmet` nói rõ phải gỡ cái gì. Một sổ mà mọi hạn đều ở xa là một sổ không có hạn nào.

### 3.1. Phép thử của cổng — 7 phép, 6 phá + 1 đối chứng

```text
✓ P1 thiếu người → đỏ
✓ P2 hạn là cụm mô tả → đỏ
✓ P3 quá hạn vẫn OPEN → đỏ
✓ P4 DONE không bằng chứng → đỏ
✓ P5 DONE trước not_before → đỏ
✓ P6 đối chứng: DONE có bằng chứng thật → sạch
✓ P7 source_doc không tồn tại → đỏ
```

Đối chứng **P6** là phép thử quan trọng nhất trong bảy phép: nó chứng minh cổng **không** đỏ với mọi thứ. Một cổng chỉ có phép phá thì không phân biệt được "bắt đúng" với "bắt tất".

---

## 4. `find_contradictions.py` — bốn cặp, và vì sao chỉ bốn

Cổng quét **41 tệp** (`WHITEPAPER.md`, `YELLOWPAPER.md`, `PRD.md` + mọi `docs/NN-*.md`), bỏ khối mã, và chạy bốn phép kiểm ở §2. Kết quả hiện tại:

```text
CONTRADICTIONS: PASS — 6670 kiểm tra · 4 cặp mâu thuẫn · 41 tệp được quét
CONTRADICTION SELFTEST: PASS — 7/7 phép thử đúng chiều (4 phép phá + 3 đối chứng)
```

Ba đối chứng — và mỗi cái ứng với **một lần cổng bắt oan** trong lúc dựng:

| Đối chứng | Bắt oan cái gì | Vì sao phải miễn |
|---|---|---|
| `0%` có nới nghĩa | câu viết đúng | Không miễn ⇒ mọi cách viết đúng đều đỏ ⇒ người ta xoá chữ "sai lệch ≤ 1 lamport" và giữ `0%` |
| `hợp đồng đã triển khai` trong câu **giả định** | câu mô tả **tương lai** | *"muốn nới điều kiện thì phải nâng cấp hợp đồng đã triển khai"* là câu đúng, và là câu **mạnh nhất** trong whitepaper §2 (bảng 5W1H) |
| `> 5.000 bps` **có** vá biên | câu đã sửa đúng | Không miễn ⇒ cách sửa duy nhất còn lại là **đổi số** — việc `AGENTS.md` cấm |

**Vì sao chỉ bốn cặp, không phải "mọi cặp":** một bộ kiểm mâu thuẫn tổng quát cần hiểu nghĩa, và cổng này **không** hiểu nghĩa. Bốn cặp ở đây là bốn **mẫu câu hẹp** gắn với bốn con số cụ thể của repo. Nói cách khác: cổng này chứng minh *"bốn cặp đã biết không quay lại"*, **không** chứng minh *"tài liệu không mâu thuẫn"*. §6 giữ đúng ranh giới đó.

> **Miễn trừ theo cú pháp, không theo tên tệp.** Dòng có `❌` là dòng **bác** câu đó (quy ước của `docs/33` §3, `check_claims.py` dùng đúng dấu hiệu này). `docs/37` — tài liệu phải dẫn lại bốn câu sai để dạy chúng sai ở đâu — **không** được miễn theo tên tệp: nếu miễn cả tệp thì một câu sai thật viết vào đây sẽ lọt. Miễn theo `❌` chỉ miễn **đúng dòng đang bác**, và đọc được bằng mắt.

---

## 5. Đã sửa gì, và cái gì **không** được sửa

Toàn bộ thay đổi trong vòng này là **chữ nghĩa** hoặc **`assert`**. Kiểm chứng theo thứ tự:

| Kiểm | Kết quả |
|---|---|
| `verify_protocol_math.py` | **100% PASS** — mọi con số đã công bố không đổi |
| `check_specs.py --tick` | **16/16** giá trị khớp đúng dòng nguồn |
| `check_pitch_deck.py --with-verifier` | **48/48**, verifier 100% |
| Dựng lại PDF trong **2 cache font độc lập** | md5 **giống nhau** ở cả hai ⇒ builder tất định (cổng `reproducible-pdf` canh đúng điều này) |
| **So text layer PDF cũ ↔ mới, từng trang** | **không token số nào đổi.** Whitepaper: 4 chỗ chữ + ngắt trang dịch lại; Yellow Paper: 4 chỗ chữ; **deck: md5 y hệt bản commit** (`7c07a9fb…`) — deck vốn không chứa các câu đó |
| Số trang | `35 → 35` (whitepaper) · `17 → 17` (yellow paper) · `14 → 14` (deck) |

Phép so text layer là phép kiểm **quan trọng nhất** ở đây, và nó thay cho một phép kiểm không tồn tại: `md5` **phải** đổi khi chữ đổi, nên "md5 khớp" không dùng được để chứng minh "không đổi số". Cách đúng là so **tập token số** của hai bản (hiệu hai `Counter`):

```text
whitepaper   bản CŨ chỉ có: {100: 1, 9: 3, 11: 1}     bản MỚI chỉ có: {4.27: 1, 10: 2, 12: 1, 1: 3}
yellow paper bản CŨ chỉ có: {}                        bản MỚI chỉ có: {0.50: 1, 5,001: 1}
pitch deck   bản CŨ chỉ có: {}                        bản MỚI chỉ có: {}
```

Đọc từng dòng:

| Token | Nghĩa | Có phải "số mới" không |
|---|---|---|
| `100` (mất **1**) | trang 22 cũ in *"đúng **100%** giá cuối trên đường cong"* — câu đó **sai** và đã bị sửa thành *"đúng giá cuối"* + số đo. Đây là **con số duy nhất bị gỡ**, và nó bị gỡ vì nó **không đo được** | **Không** — gỡ bỏ, không thêm |
| `4.27` (thêm **1**) | §7.3 đã có `4.27 × 10⁻¹²` từ trước; bản in **thêm một lần** ở trang 22 khi câu `100%` biến thành số đo | **Không** — số đã công bố, in thêm một chỗ |
| `0.50`, `5,001` (thêm) | hai vế của bất đẳng thức đã có (`LCB > 0.50`, `floor ⇒ 5,001`), nay hiện trong Yellow Paper §7.1 | **Không** — cùng một bất đẳng thức, nay nói ra cách vá biên |
| `9 / 11` → `10 / 12`, `1` ×3 | **số trang trong mục lục** dịch do ngắt trang đổi (chữ dài ra ở §1.3 và §1.4) | **Không** — điều hướng, không phải dữ liệu |

> **Ba số mới xuất hiện, và không số nào là số mới *phát minh*.** `4.27 × 10⁻¹²` là con số đã công bố ở §7.3 bản Markdown; nó chỉ **chưa từng được in ở trang 22** vì trang đó nói `100%`. `0.50` và `5,001` là hai vế của cùng bất đẳng thức đã có (`LCB > 0.50`, `floor`). Không số nào trong ba số đó cần một lệnh mới để sinh ra.

Chữ đã sửa — **8 chỗ**, mỗi chỗ khẳng định `count == 1` trước khi thay (một phép thay không đếm được là một phép thay có thể sửa nhầm chỗ):

| Tệp | Từ | Thành |
|---|---|---|
| `WHITEPAPER.md` §1.2 | *"với `0%` chênh lệch giá"* | *"với **sai lệch ≤ 1 lamport** (tương đương `0%` chênh lệch giá)"* |
| `WHITEPAPER.md` §6.1 (bảng Locked LP) | *"**100% giá cuối** trên đường cong"* | *"**đúng giá cuối trên đường cong** — sai lệch đo được **`4.27 × 10⁻¹²`** (≤ 1 lamport, …)"* |
| `WHITEPAPER.md` §9.4 (dòng S8) | *"**`0%`** chênh lệch giá"* | *"sai lệch **≤ 1 lamport** (tương đương `0%` chênh lệch giá)"* |
| `WHITEPAPER.md` §2 (bảng 5W1H) | *"hợp đồng đã triển khai"* | *"hợp đồng **sau khi** nó được triển khai"* |
| `YELLOWPAPER.md` §6 (mục lục + tiêu đề) | *"Zero-Gap"* | *"sai lệch ≤ 1 lamport & Cơ chế `Stall / Ragequit`"* |
| `YELLOWPAPER.md` §7.2 | *"hợp đồng đã triển khai"* | *"hợp đồng **sau khi** triển khai"* |
| `YELLOWPAPER.md` §7.1 | `(> 5,000 bps cho M2+)` | `(> 5,000 bps cho M2+; floor ⇒ >= 5,001 bps, tức > 0.50)` |
| `PRD.md` | *"`0%` chênh lệch giá"* | *"(sai lệch ≤ 1 lamport, tương đương `0%` chênh lệch giá)"* |

Hai chỗ **cố ý không sửa**:

- **`docs/33` dòng 115** dẫn lại câu S8 của whitepaper. Đó là **giáo cụ**, không phải tuyên bố — sửa câu đang được trích là làm hỏng ví dụ. Nhưng nó **vẫn phải qua cổng**: `docs/33` nằm trong 41 tệp được quét, và phép kiểm ở §2.1 bắt đúng dòng này cho tới khi chỗ trích **nói ra** rằng câu gốc đã được nới nghĩa. Cách sửa đã dùng: cắt câu trích bằng `…` và thêm *"(câu đã được nới nghĩa ở `docs/37` §2.1)"* — **không** đổi câu gốc trong whitepaper, và **không** miễn tệp.
- **`4.27 × 10⁻¹²` vs `4.19 × 10⁻¹¹`** — hai đại lượng **khác nhau** (delta vốn hoá thị trường vs delta giá), không phải mâu thuẫn. `docs/36` đã ghi; vòng này không "sửa" cái không sai.

---

## 6. Ba câu **sẽ bị hỏi**, và câu trả lời đúng

| Câu hỏi | Trả lời đúng | Trả lời **sai** |
|---|---|---|
| *"Tài liệu của anh có chỗ nào tự mâu thuẫn không?"* | *"Bốn cặp đã biết, đã vá, và có cổng chặn chúng quay lại. Cổng không chứng minh hết — nó kiểm bốn mẫu câu gắn với bốn con số."* | *"Không có chỗ nào mâu thuẫn"* — câu này nói về **mọi cặp**, mà cổng chỉ kiểm **bốn** |
| *"P1 đã sửa chưa?"* | *"Chưa. Sổ việc ghi rõ: LXK, hạn 18/12, quá hạn thì phải rút lại câu 'escrow ≥ 0 được bảo đảm trước launch'."* | *"Đang xử lý"* — không người, không ngày, không hậu quả |
| *"Làm sao tôi biết sổ việc không phải hình thức?"* | *"`check_actions.py` là cổng 17. Quá hạn ⇒ CI đỏ. Đóng sớm hơn `not_before` ⇒ đỏ. `DONE` không bằng chứng trỏ tệp thật ⇒ đỏ."* | *"Có sổ đầy đủ"* — không có cổng đọc nó thì sổ là trang trí |

---

## 7. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R17** | Dùng LLM/chấm điểm ngữ nghĩa làm cổng mâu thuẫn | Cổng CI phải tất định và offline (`docs/30`). Một cổng cho hai kết quả khác nhau ở hai lần chạy **không** phải cổng |
| **R18** | Miễn `find_contradictions.py` theo **tên tệp** (`docs/37`, `docs/36`, `docs/33`) | Miễn cả tệp = một câu sai thật viết vào đó sẽ lọt. Miễn theo cú pháp (`❌`, hoặc câu trích đã nới nghĩa tại chỗ) chỉ miễn **đúng dòng đó**, và đọc được bằng mắt |
| **R19** | Sửa câu trích S8 trong `docs/33` | Nó là **giáo cụ**. Sửa câu đang được trích là làm hỏng ví dụ, không phải sửa lỗi |
| **R20** | Đổi `5,000 bps` thành `5,001 bps` cho "gọn" | Đó là **đổi số đã công bố**. Cách đúng là thêm mệnh đề `floor ⇒ >= 5,001` — số giữ nguyên, nghĩa được nói ra |

---

## 8. Việc **không** làm

- **Không** sửa `docs/36` hay bất kỳ tài liệu đã merge nào ngoài các dòng chữ ở §5.
- **Không** đổi con số nào: `60.221994`, `15.908330`, `4.27 × 10⁻¹²`, `4.79×`, `1.252×`, `5,000 bps`, `76.109937`, `79.245283`.
- **Không** thêm phụ thuộc, không gọi mạng — cả hai cổng mới chỉ dùng thư viện chuẩn.
- **Không** đụng `programs/`: chưa có dòng code nào, và đó là lý do cặp §2.4 tồn tại.

---

## 9. Thứ tự làm — lần này bằng dữ liệu, không bằng văn xuôi

`pm/action-register.json` là **nguồn**, bảng dưới là **bản in** của nó (cùng nguyên tắc `docs/34`: tờ giấy sinh từ sổ, không viết tay song song).

| # | Việc | Hạn | Nếu quá hạn |
|---|---|---|---|
| **1** | **P4** · đưa `check_actions.py` thành cổng 17 | 2026-11-24 | xoá sổ, ghi lại rằng P1/P2 chỉ là văn xuôi |
| **2** | **P5** · biên `4,79×` trên mô hình đầy đủ thành `assert` | 2026-11-24 | xoá dòng "biên thật 4,79×" khỏi `docs/36` §5.2 |
| **3** | **P1** · ràng buộc biên vào `validate_launch` | 2026-12-18 | rút câu "escrow ≥ 0 được bảo đảm trước launch" khỏi mọi tài liệu |
| **4** | **P2** · ghi lý do rent vào §4.3 | 2026-12-18 | gỡ con số `11 SOL/giờ` khỏi tài liệu trình bày |
| **5** | **P3** · `requirements.txt` cho toolchain PDF | 2026-12-20 | gỡ dòng "md5 khớp" khỏi `docs/README-PDF.md` |

Hai việc **đã xong trong vòng này**, bằng chứng là lệnh chạy được:

| Việc | Bằng chứng (dán từ đầu ra, không phải lời khai) |
|---|---|
| **P4** | `ACTION LOCK: PASS — 66 kiểm tra · 5 bất biến · 5 việc (3 OPEN)` · `ACTION LOCK SELFTEST: PASS — 7/7 phép thử đúng chiều (6 phép phá + 1 đối chứng)` |
| **P5** | `S3 PASS (Zero-Gap Graduation): … margin (★) = 1.251170x / 4.790421x` |

**P5 đã xong trong vòng này** — và bằng chứng là `verify_protocol_math.py` in ra:

```text
S3 PASS (Zero-Gap Graduation): VGBC-4T LP=61.836953 SOL (gap=4.27e-12) | VBOND-LV LP=14.387943 SOL,
Escrow=60.221994 SOL after F_grad=1.50 SOL (gap=4.19e-11) | margin (★) = 1.251170x / 4.790421x
```

`1.251170` là biên của **VGBC-4T** — hồ sơ **hẹp nhất**, và trước vòng này nó **chưa từng được in ra ở đâu**. Con số `4,79×` mà `docs/36` nói với nhà đầu tư là hồ sơ **rộng hơn**. Cả hai giờ là `assert`, nên đổi tham số làm biên tụt ⇒ CI đỏ.
