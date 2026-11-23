# Bốn bổ đề — kiểm chúng trên **tham số của repo này**, không phải tin chúng

> **Tài liệu sống:** `docs/36-kvu-lemmas-and-the-version-unit.md`
> **Trạng thái:** `SCOPING` — đánh giá 5 tệp người dùng gửi + **đã dựng cổng** (`scripts/kvu_invariants.py`)
> **Ngày:** 23/11/2026
> **Đầu vào:** `kvu-chung-minh-bon-tang.md` · `nguyen-ly-don-vi-khanh-tang-hai (1).md` (bản sửa) · `whitepaper-vi (2).md` · `yellowpaper-formal-vi.md` · `yellowpaper-vi (1).md`
> **Liên quan:** `docs/33` (VGU-BM, loại tuyên bố) · `docs/34` (người ký, hạn) · `docs/35` (biên bản đo) · `docs/YELLOWPAPER` §5–§6 · `scripts/verify_protocol_math.py`
> **Câu hỏi của người yêu cầu:** *(5 tệp đính kèm, không kèm câu hỏi chữ)* — đọc như: *"bản sửa của KVU-2 và bản chứng minh bốn tầng nói gì, có dùng được cho Game9K không?"*

---

## 0. Kết luận trước

**Bản chứng minh bốn tầng là tài liệu tốt nhất trong loạt này, và nó có một lỗi số học khi áp vào repo này.** Tôi kiểm bốn bổ đề trên tham số thật của Game9K: **cả bốn đúng**, nhưng **hai con số trong bản chứng minh không khớp mô hình của nó** — và điều đó không làm bổ đề sai, nó làm **ví dụ minh hoạ** sai.

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Bốn bổ đề có đúng không? | **Đúng**, kiểm trên toàn miền tham số đã định nghĩa trong repo (§3) |
| **2** | Biên an toàn có phải **7,34×** như tài liệu nói? | **Không.** Đúng là **10,49×** ở mô hình rút gọn, và **4,79×** ở mô hình đầy đủ — hai số, hai nghĩa (§3.2) |
| **3** | Có lỗ hổng thật trong spec repo này không? | **Có một**: `validate_launch` chưa có ràng buộc biên `S_LP < X_end·(1−f)` (§3.3). và — xem #4 — lỗ thứ hai mà bản sửa đã chỉ ra đúng |
| **4** | Bản KVU-2 sửa gì? | **Sửa một lỗi về loại**, và lỗi đó **đã có trong repo này**: `docs/35` để hai đơn vị (phiên bản game / `(model, phiên bản)`) nằm cạnh nhau mà **không nói chúng không thay thế nhau** (§4) |
| **5** | Đã dựng gì? | `scripts/kvu_invariants.py` — **6 bất biến**, **31 kiểm tra**, **6 phép thử**; tái lập **cả hai hồ sơ** (`60.221994` và `15.908330` SOL) trong **1 lamport** (§5) |
| **6** | Có tuyên bố mới nào để nói với nhà đầu tư không? | **Không.** Và §6 nói rõ vì sao "bốn tầng chứng minh" là câu **dễ bị hỏi nhất** trong buổi pitch — kèm câu trả lời đúng |

> **Điều tôi từ chối:** chép nguyên bảng "cái gì thực sự `PROVEN`" của tài liệu nguồn vào whitepaper. Bảng đó đúng **cho dự án của họ**; với Game9K, dòng `"chạy đúng trên chain thật"` vẫn là **`❌ chưa có`**, và một bảng có dòng cuối `❌` không được đặt cạnh một tiêu đề nói `PROVEN`.

---

## 1. Năm tệp, ba loại — và chỉ một loại dùng được ngay

| Tệp | Loại | Dùng được? |
|---|---|---|
| `kvu-chung-minh-bon-tang.md` | **Chứng minh** (bổ đề + phản ví dụ + bảng trạng thái) | ✅ **Đây là tệp đáng đọc nhất** — §3 |
| `nguyen-ly-don-vi-khanh-tang-hai (1).md` | **Bản sửa** của tài liệu đã đọc ở vòng trước | ✅ Sửa đúng một lỗi loại — §4 |
| `whitepaper-vi (2).md` · `yellowpaper-*.md` | **Bản dịch/viết lại** whitepaper & yellowpaper | ⚠️ **Không** dùng làm nguồn số — §2 |
| (không có tệp) | Code `sim/kvu_invariants.py` mà tài liệu dẫn | ❌ Không tồn tại ở đây; tôi dựng lại theo bổ đề — §5 |

> **Không tệp nào trong ba tệp whitepaper/yellowpaper được dùng làm nguồn số.** `AGENTS.md` luật 1: số phải tái lập bằng một lệnh trong `scripts/`. Số đã công bố sống ở `docs/WHITEPAPER.md`, `docs/YELLOWPAPER.md` và `scripts/verify_protocol_math.py`; một bản `.md` gửi kèm **không** thay được ba thứ đó, kể cả khi nội dung trông giống.

---

## 2. Vì sao bản dịch không phải nguồn — một ví dụ cụ thể, không phải nguyên tắc chung

`whitepaper-vi (2).md` ghi, ở dòng thay đổi v1.2:

> *"sửa một lỗi kinh tế trong công thức LP tốt nghiệp … escrow giảm còn `60,1998 SOL`"*

Còn `docs/WHITEPAPER.md` và `docs/YELLOWPAPER.md` §6.1 ghi **`60.221994 SOL`** (đã trừ `F_grad = 1.50 SOL`).

**Cả hai đều "đúng" theo cách của nó** — `60,1998` là escrow **trước** phí tốt nghiệp, `60,221994` là **sau**. Nhưng hai con số cùng tên "escrow" trong hai tệp là đủ để một nhà đầu tư hỏi *"vậy escrow là 60,19 hay 60,22?"* — và lúc đó không ai nhớ được vì sao khác.

> **Đây không phải lỗi của bản dịch.** Đây là lý do `AGENTS.md` có luật 1: một con số chỉ được vào tài liệu khi có **một lệnh** sinh ra nó. Tôi đã kiểm lại bằng mô hình đầy đủ: `76.109937 − 14.387943 − 1.50 = 60.221994` — khớp `docs/` trong **1 lamport** (§5.2).

---

## 3. Bốn bổ đề — kiểm chứ không tin

### 3.1. Bảng bổ đề, và chỗ chúng đứng trong repo này

| Bổ đề | Phát biểu | Đúng? | Đứng ở đâu |
|---|---|---|---|
| **1** | `R(s)` tăng ngặt ⇒ `s = CS ⟺ real_sol ≥ R(CS)` | ✅ | Điều kiện tốt nghiệp, `docs/YELLOWPAPER` §6.1 |
| **2** | `escrow ≥ 0 ⟺ G ≥ S_LP·V/(X_end(1−f) − S_LP)` (★) | ✅ | §6.1, kiểm được **trước** launch |
| **3** | Mẫu số (★) dương, **nếu** `S_LP < X_end·(1−f)` | ✅ **và điều kiện đó là cần** | ⚠️ **chưa có trong spec** — §3.3 |
| **4** | `E_k ≥ 0 ∀k ⟺ Σ payout_bps ≤ 10000` | ✅ | Kiểm **một lần** khi tạo milestone set |

### 3.2. Hai con số của tài liệu nguồn không khớp mô hình của chính nó

| Số trong `kvu-chung-minh-bon-tang.md` | Kiểm lại trên mô hình rút gọn của nó | Kết luận |
|---|---|---|
| **"biên an toàn tại điểm mặc định: 10,49×"** | ✅ đúng | OK |
| **"biên hẹp nhất trên toàn miền: 8,93×"** | ✅ đúng (V=30, CS=50%) | OK |
| **"biên 7,34×"** (§5 bảng trạng thái, và §8 tự kiểm) | ❌ **không tái lập được** ở đâu cả | **Sai số** |
| **"biên 7,31×"** (§1.3, ràng buộc biên) | ✅ đúng, nhưng là **biên của ràng buộc khác** (`X_end(1−f)/S_LP`), không phải biên escrow | Nhầm **hai biên** với nhau |

> **Đây là lỗi chép số, không phải lỗi toán.** Bốn bổ đề vẫn đúng. Nhưng nó minh hoạ đúng thứ `docs/35` viết: một con số tách khỏi phép đo sinh ra nó thì không kiểm được — kể cả khi nó nằm trong một tài liệu có chứng minh đúng.

**Và đây là điều tôi phải nói rõ hơn cả:** mô hình rút gọn cho **10,49×**, còn mô hình **đầy đủ của repo này** (`docs/YELLOWPAPER` §6.1, có `F_grad = 1.50 SOL`) cho **4,79×**:

```
R_end = 76.109937 SOL  ·  lp = 14.387943 SOL  ·  F_grad = 1.50 SOL
(★) thật:  R_end ≥ lp + F_grad   →   76.11 ≥ 15.89   →   biên 4,79×
```

Không có biên nào là "7,34×". Con số đúng để nói với nhà đầu tư là **4,79×** — và phải nói kèm "mô hình đầy đủ, đã trừ phí tốt nghiệp".

### 3.3. Một lỗ thật trong spec — và tôi không tự sửa nó

Bổ đề 3 nói: cần `S_LP < X_end·(1−f)`. Nếu `S_LP` lớn hơn, mẫu số của (★) âm và **bất đẳng thức mất nghĩa** — không phải "sai", mà **không nói được gì**, đúng loại lỗi nguy hiểm hơn.

`docs/YELLOWPAPER` §5.1 khai `S_LP` là tham số của từng hồ sơ, nhưng **không có ràng buộc biên nào** giữa `S_LP` và `X_end`. Nghĩa là một hồ sơ mới với `S_LP` lớn vẫn qua được `validate_launch`.

> **Tôi không sửa `YELLOWPAPER.md`.** Đó là nguồn spec; sửa nó là rebuild PDF và đổi `terms_hash` của mọi launch tương lai. Việc đúng là **đăng ký nó thành một mục có người ký và hạn**, đúng cơ chế `docs/34`:
>
> - **P1** — thêm `require!(lp_tokens * (BPS − f) < x_end * BPS)` vào `validate_launch`. Sửa **một dòng**.
> - Chặn: một hồ sơ tham số mà (★) **không nói được gì**.
> - Hạn: **2026-12-18**, cùng đợt với ba tuyên bố ở `pm/claims-registry.json`.

### 3.4. Hai đề xuất của tài liệu nguồn mà repo này **đã** xử lý

Để công bằng — không phải chỗ nào họ cũng "phát hiện lỗ mới":

| Họ đề xuất | Repo này |
|---|---|
| **P2** đưa `game_id ‖ semver` vào **lá** Merkle | **Đã có.** `docs/YELLOWPAPER` §4.3: `Leaf_i = H(0x00 ‖ g_i ‖ h_{v_i} ‖ VPH_i ‖ …)` — `g_i` là game, `h_{v_i}` là hash **phiên bản**. Đề xuất của họ dựa trên một phiên bản spec khác (dùng prefix `GAME9K_POP_V20_` thay vì lá) |
| **P4** ghi "mint riêng mỗi phiên bản" là điều kiện của định lý | **Đã có.** `docs/YELLOWPAPER` §1.1: `S_tot` cố định **cho mỗi** token dự án/phiên bản |
| **P3** gộp root theo giờ | ⚠️ **Chưa chốt** ở repo này — §6.2 |

---

## 4. Bản KVU-2 sửa gì — và nó bắt được một lỗi **của tôi**

Bản `(1)` thêm một callout mà bản cũ không có:

> **Hai đơn vị này KHÔNG được lẫn.** `Phiên bản game` = đơn vị **tài sản** (được định giá, mở khoá, giải ngân), xác nhận bởi **người chơi thật**. `(model, phiên bản)` = đơn vị **phép đo**, xác nhận bởi **máy**. *"Một dòng `(model, phiên bản)` không bao giờ là bằng chứng chất lượng của một phiên bản game."*

**Đây là lỗi trong `docs/35` tôi viết vòng trước.** Tôi đặt hai đơn vị cạnh nhau (§0, §2), và mặc dù tôi **không** viết câu sai, tôi cũng **không** viết câu chặn — nên người đọc lướt có thể kết luận hai thứ thay thế nhau được.

| Viết ở `docs/35` | Thiếu gì |
|---|---|
| *"một lần đo là một biên bản, khoá `(model, phiên bản)`"* | Không nói: **biên bản không phải bằng chứng chất lượng phiên bản** |
| Biên bản **không** chứa nội dung, không có `score` | Đúng, nhưng đó là chặn **nội dung**, không chặn **suy luận** |

Đã sửa ở `docs/35` §2.2, và cổng `check_claims.py` bất biến 4 (không trộn ba tầng) **không** bắt được loại lỗi này — vì nó kiểm một **dòng**, còn lỗi này nằm ở **khoảng cách giữa hai mục**. Ghi lại làm giới hạn đã biết của cổng.

---

## 5. Đã dựng: `kvu_invariants.py`

```bash
python3 scripts/kvu_invariants.py            # 6 bất biến, 31 kiểm tra
python3 scripts/kvu_invariants.py --audit     # bảng biên + tái lập số đã công bố
python3 scripts/kvu_invariants.py --selftest  # CI: 6 phép thử
```

```
KUVA: PASS — 31 kiểm tra · 6 bất biến (4 bổ đề + biên + tái lập số đã công bố)
             · biên hẹp nhất 8.93× tại V=30 SOL, CS=50%
KUVA SELFTEST: PASS — 6/6 phép thử đúng chiều (5 phép phá + 1 đối chứng)
```

### 5.1. Sáu bất biến

| # | Bất biến | Bắt được gì |
|---|---|---|
| **1** | `R` tăng ngặt trên `[0, CS]`; `R(CS) > R(CS−1)` | Công thức bị sửa làm đảo chiều |
| **2** | `escrow ≥ 0 ⟺ G ≥ (★)` trên **toàn miền** | Escrow "quên" phí hoặc LP |
| **3** | Mẫu số (★) dương; **vượt biên thì phải ném lỗi** | Ràng buộc biên bị bỏ ⇒ (★) vô nghĩa thay vì sai |
| **4** | `E_k ≥ 0 ∀k ⟺ Σ bps ≤ 10000` | Kiểm từng mốc mà quên tổng |
| **5** | Biên (★) > 1 trên **toàn miền đã định nghĩa** | Chỉ kiểm điểm mặc định |
| **6** | Mô hình **đầy đủ** tái lập `60.221994` và `15.908330` SOL **trong 1 lamport** | Công thức §6.1 bị đổi mà không ai biết |

> **Bất biến 6 là bất biến tôi thêm, không có trong tài liệu nguồn.** Tài liệu nguồn gọi việc tái lập số đã công bố là *"điều kiện tiên quyết"* nhưng **không kiểm nó trong code**. Một điều kiện tiên quyết không được kiểm là một câu nói.

### 5.2. Tái lập số đã công bố — cả hai hồ sơ

```
VBOND-LV  R_end=   76.109937  lp=  14.387943  surplus=  60.221994 SOL
VGBC-4T   R_end=   79.245283  lp=  61.836953  surplus=  15.908330 SOL
Biên thật của (★) ở VBOND-LV: 4.79×  (R_end / (lp + F_grad))
```

Đây là lần đầu một cổng **độc lập** với `verify_protocol_math.py` xác nhận bốn con số đó. Hai tệp dùng hai đường tính khác nhau — và đó là mục đích: `verify_protocol_math.py` khoá **số đã công bố**, `kvu_invariants.py` khoá **điều kiện đúng** của bốn bổ đề.

### 5.3. Năm phép phá

| # | Phá | Nó mô phỏng lỗi thật nào |
|---|---|---|
| 1 | `R` không tăng ngặt | Công thức bị sửa dấu |
| 2 | escrow "quên" phí và LP | Hợp đồng tính escrow trước khi trừ LP |
| 3 | bỏ ràng buộc biên | Hồ sơ mới với `S_LP` lớn |
| 4 | **chỉ kiểm từng `bps`, quên tổng** | Hợp đồng viết vội: mỗi mốc hợp lệ, tổng thì không |
| 5 | `S_LP` sát biên ⇒ biên < 1 | Chứng minh ràng buộc biên **không đủ** — cần cả (★) |

Phép 4 là loại lỗi khó nhất: nó **không** bắt một con số sai, nó bắt một **điều kiện thiếu**.

---

## 6. Trả lời câu "có gì để nói với nhà đầu tư"

### 6.1. Không có tuyên bố mới — và đây là lý do

`docs/33` §5 đã từ chối thêm một dòng trend. Câu trả lời đó **không đổi**. Nhưng bản chứng minh bốn tầng tạo ra **hai câu mới đáng nói**, và cả hai đều là câu về **cách làm**, không phải về **kết quả**:

| Nói | Vì sao an toàn |
|---|---|
| *"Bốn bất biến của mô hình được kiểm bằng máy trên toàn miền tham số, không chỉ điểm mặc định"* | `kvu_invariants.py` 31 kiểm tra — tái lập được |
| *"Chúng tôi tái lập số đã công bố của **cả hai** hồ sơ trong 1 lamport, bằng một cổng độc lập với cổng sinh ra chúng"* | §5.2 — hai đường tính, một kết quả |
| ❌ *"Chúng tôi đã chứng minh mô hình"* | **Không.** Mô hình đúng ở tầng toán; `programs/` trống. Đây là câu `docs/33` §3.2 chặn |

### 6.2. Ba câu **sẽ bị hỏi**, và câu trả lời đúng

| Câu hỏi | Trả lời đúng | Trả lời **sai** |
|---|---|---|
| *"Các anh chứng minh được gì?"* | *"Bốn bất biến ở tầng mô hình, kiểm bằng máy trên toàn miền tham số. Ở tầng hệ thống thì chưa — `programs/` trống."* | *"Mô hình đã được chứng minh"* |
| *"Biên an toàn bao nhiêu?"* | *"**4,79×** ở hồ sơ Ổn định, tính trên mô hình đầy đủ đã trừ phí tốt nghiệp `1.50 SOL`."* | *"7,34×"* (không tái lập được) hay *"10,49×"* (mô hình rút gọn, chưa trừ `F_grad`) |
| *"Nếu `S_LP` lớn hơn thì sao?"* | *"Hiện spec chưa chặn. Đó là **P1**, hạn 18/12, sửa một dòng trong `validate_launch`."* | *"Không xảy ra"* |

> Câu thứ ba là câu **mạnh nhất**, và nó chỉ mạnh vì nó thừa nhận. Đúng nguyên tắc `docs/34` §5: tờ giấy có ba mục `OPEN` mạnh hơn tờ giấy không có mục nào.

### 6.3. Về chi phí neo Merkle (P3 của tài liệu nguồn)

Tài liệu nguồn tính: 10.000 root/giờ × 48 B ≈ **11 SOL/giờ** rent — không khả thi, nên phải gộp root theo giờ. **Đây là tính toán đúng và repo này chưa chốt.**

Nhưng `docs/YELLOWPAPER` §4.3 đã mô tả `Root_h` là **một** root cho cửa sổ giờ `h` — nghĩa là spec **đã** dùng phương án gộp, chỉ chưa **nói ra** rằng đó là một quyết định chi phí. Việc đúng: ghi một dòng vào §4.3 rằng gộp theo giờ là **bắt buộc vì rent**, kèm con số `11 SOL/giờ`. Không cần ADR mới.

---

## 7. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R13** | Chép bảng *"cái gì thực sự `PROVEN`"* của tài liệu nguồn vào whitepaper | Bảng đó đúng cho dự án của họ; với Game9K dòng cuối là `❌ chưa có`. Một bảng có dòng `❌` không được đặt dưới tiêu đề `PROVEN` — đó là bất biến 4 của `check_claims.py` ở dạng bảng |
| **R14** | Dùng `60,1998 SOL` (bản dịch) thay `60.221994 SOL` (đã công bố) | Hai số khác nghĩa: một trước, một sau `F_grad`. Dùng lẫn là tự tạo mâu thuẫn trong tài liệu gọi vốn |
| **R15** | Nói "biên 7,34×" | Không tái lập được ở mô hình nào trong hai mô hình (§3.2) |
| **R16** | Thêm `S_LP` vào `validate_launch` **trong vòng này** | Đó là sửa spec nguồn ⇒ rebuild PDF + đổi `terms_hash`. Đăng ký **P1** làm mục có hạn (`docs/34`), không sửa lặng lẽ |

---

## 8. Việc **không** làm

- **Không sửa** `WHITEPAPER.md` / `YELLOWPAPER.md` / `PRD.md` / `docs/35` §0–§4. Chỉ **thêm** §2.2 vào `docs/35`.
- **Không** thay `verify_protocol_math.py` bằng `kvu_invariants.py`. Hai tệp khoá hai thứ khác nhau (§5.2).
- Không đổi số đã kiểm (`60.221994`, `15.908330`, `76.109937`, `79.245283`, `12 KB`, `3,5 s`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không gọi mạng, không thêm phụ thuộc.

---

## 9. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | **P1** — thêm ràng buộc biên vào `validate_launch`, hạn **2026-12-18** | §3.3 — (★) vô nghĩa nếu `S_LP` lớn |
| **2** | Ghi vào §4.3 rằng gộp root theo giờ là **bắt buộc vì rent** (`11 SOL/giờ` nếu không gộp) | §6.3 — spec đã làm đúng nhưng chưa nói ra lý do |
| **3** | Nếu có người hỏi con số biên: dùng **4,79×** + "mô hình đầy đủ, đã trừ `F_grad`" | §3.2 — số đúng, kèm điều kiện |
| **4** | Khi `programs/` chạy được: nâng bảng trạng thái, **cùng PR** với test on-chain | §0 — dòng `❌ chưa có` là dòng duy nhất chặn mọi thứ khác |
