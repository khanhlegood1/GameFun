# Mười hai bất biến, tám cái có mã — và ba hệ đánh số trùng tên

> **Tài liệu sống:** `docs/38-invariant-ledger-and-the-three-numbering-systems.md`
> **Trạng thái:** `SCOPING` — đã dựng cổng (`scripts/check_invariants_coverage.py`) + sửa nguồn 3 chỗ
> **Ngày:** 23/11/2026
> **Đầu vào:** *"làm tiếp"* — không kèm yêu cầu khác
> **Liên quan:** `docs/YELLOWPAPER` §8.1, §12.1 · `docs/WHITEPAPER` §1.3 · `docs/04` §5 · `docs/37` (sổ việc) · `scripts/verify_protocol_math.py`

---

## 0. Kết luận trước

**Yellow Paper khai 12 bất biến; mã kiểm 4. Câu in trong §12.1 nói *"0 vi phạm"* trên **toàn dải `INV-01` đến `INV-08`** — một câu không thể đúng cũng không thể sai, vì nó nói về tám bất biến mà mô hình không có.** Và trong lúc kiểm, tôi tìm ra thứ tệ hơn: repo có **ba hệ đánh số `INV-nn` khác nhau**, dùng cùng những mã số cho những bất biến khác nhau.

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Có bao nhiêu bất biến được khai? | **12** (`YELLOWPAPER` §8.1, `INV-01..INV-12`) |
| **2** | Bao nhiêu cái thực sự có phép kiểm trong `scripts/`? | **Trước vòng này: 4.** Sau vòng này: **8** — tôi thêm `INV-06`, `INV-08`, `INV-09`, `INV-10` vào chỗ chúng thực sự thuộc về (§2) |
| **3** | Vậy câu *"0 vi phạm toàn dải 01–08"* ở §12.1 đúng hay sai? | **Không đánh giá được** — đó chính là lỗi. Nay câu đã được viết lại để nêu **đúng 8 mã có mã kiểm** (§4) |
| **4** | Ba hệ đánh số là gì? | `docs/YELLOWPAPER` §8.1 (12 bất biến **của giao thức**), `docs/WHITEPAPER` §1.3 (cùng mã, khác nghĩa), `docs/04` §5 (8 bất biến **của chương trình Anchor**) (§1) |
| **5** | Đã sửa gì? | 3 chỗ chữ trong nguồn + **gắn thẻ `INV-nn` cho từng dòng `assert`** để cổng đọc được. Không đổi con số nào (§4) |
| **6** | Có tuyên bố mới nào để nói với nhà đầu tư? | **Không.** Và §6 có câu trả lời cho câu *"12 bất biến của anh đã kiểm hết chưa?"* — câu mà trước vòng này tài liệu **không có cách nào** trả lời đúng |

> **Điều tôi từ chối:** thêm 4 `assert` giả để bảng đủ 12 dòng xanh. `INV-05`, `INV-07`, `INV-11`, `INV-12` cần **đối tượng dữ liệu** mà mô hình đường cong không có (bản ghi phiên bản, custody token, dấu `BotShare`, trạng thái governance). Viết `assert True` cho đủ số là đúng loại gian lận mà cả loạt `docs/33`–`docs/37` tồn tại để chặn.

---

## 1. Ba hệ đánh số, cùng những con số

| Hệ | Nơi khai | Phạm vi | `INV-01` nghĩa là gì |
|---|---|---|---|
| **A — giao thức** | `docs/YELLOWPAPER.md` §8.1 | 12 bất biến của máy trạng thái + đường cong | *Bảo toàn Cung & `0%` Nền tảng* |
| **B — whitepaper** | `docs/WHITEPAPER.md` §1.3 (cột "Bất biến / Định lý bảo vệ") | **cùng mã số, gắn cho nguyên tử** | nguyên tử 3 dùng `INV-01`–`INV-04` (trùng hệ A, đúng) nhưng nguyên tử 4 dùng `INV-07`, `INV-08` — **không** phải nghĩa của hệ A |
| **C — chương trình** | `docs/04-solana-smart-contracts.md` §5 | 8 bất biến của Anchor program | *Solvency tuyệt đối* (khác hẳn hệ A) |

Hệ **C** là hệ nguy hiểm nhất, vì nó **trông giống hệt** hệ A: cùng dải `INV-01..INV-08`, cùng từ "bất biến", cùng nói về tiền. Một kiểm toán viên đọc `docs/04` §5 rồi đọc `YELLOWPAPER` §8.1 sẽ thấy `INV-05` là *"Bảo toàn Token Custody"* ở một chỗ và *"Phả hệ Phiên bản Đơn điệu"* ở chỗ kia — và không có gì trong repo nói rằng hai thứ đó khác nhau.

> **Đây không phải lỗi chính tả.** Nó là lỗi **loại**: hai tài liệu dùng cùng một ký hiệu cho hai vị từ khác nhau. Nếu `programs/` đã tồn tại thì đây là lỗi chặn kiểm toán; vì `programs/` còn trống nên nó mới chỉ là lỗi chặn **đọc hiểu** — và đó là lý do nó sống sót lâu như vậy.

**Cách sửa đã chọn:** không đổi số của hệ nào (đổi số là phá mọi trích dẫn cũ). Thay vào đó **khai báo tường minh** hệ C là hệ riêng tại chỗ nó được định nghĩa, và trỏ hệ B về danh mục chuẩn. Cổng kiểm **sự có mặt của câu khai báo**, không kiểm nội dung tám bất biến của hệ C (vì `programs/` trống, nội dung đó chưa kiểm được — xem `docs/37` §2.4).

---

## 2. Bảng 12 dòng — cái nào thực sự có mã

`python3 scripts/check_invariants_coverage.py --audit`:

```text
mã      trạng thái    số dòng  ý nghĩa
INV-01  ✓ asserted    4        check_invariants: tổng cung + 0% nền tảng
INV-02  ✓ asserted    2        check_invariants: v_sol * v_tok >= K
INV-03  ✓ asserted    4        check_invariants: real_sol == v_sol - Y0 >= 0, penalty_floor >= 0
INV-04  ✓ asserted    5        check_invariants: net_sold == VT - v_tok, trần chặng, tổng position
INV-05  · unasserted  0        cần đối tượng VersionRecord (h_k, h_base, nu_k)
INV-06  ✓ asserted    2        check_invariants + unlock_next_milestone: m_act tăng đúng +1
INV-07  · unasserted  0        cần custody token trước Graduation
INV-08  ✓ asserted    3        buy(enforce_caps=True): trần ví + trần epoch
INV-09  ✓ asserted    1        check_invariants(Stalled): creator_fee == 0 và creator_vest_frozen
INV-10  ✓ asserted    1        graduate(): rel_gap < 1/S_LP
INV-11  · unasserted  0        cần đóng dấu BotShare của Oracle
INV-12  · unasserted  0        cần trạng thái governance (upgrade_authority, terms_hash)

8/12 mã có phép kiểm trong `scripts/` · 4 mã còn là TÊN
```

### 2.1. Bốn bất biến tôi **thêm** trong vòng này — và vì sao chúng thuộc về đây

Không phải bất biến nào cũng cần một đối tượng mới. Bốn cái này **đã đúng trong mô hình**, chỉ chưa được **phát biểu**:

| Mã | Trước vòng này | Sau |
|---|---|---|
| **`INV-06`** (thứ tự cột mốc) | chỉ có `active_milestone += 1` — không ai kiểm nó tăng đúng `+1` | `assert self.active_milestone == before + 1` trong `unlock_next_milestone`, và `1 <= m_act <= len(tranche_caps)` trong `check_invariants` |
| **`INV-08`** (trần ví/epoch) | trần được **áp** trong `buy()` nhưng không **assert** — một regression làm trần sai sẽ không đỏ | `assert pos.tokens <= wallet_cap` và `epoch_bought <= epoch_cap` ở nhánh `enforce_caps=True` |
| **`INV-09`** (đóng băng khi `Stall`) | `trigger_stall()` gán hai cờ, không ai assert | nhánh `Stalled` của `check_invariants`: `creator_fee == 0 and creator_vest_frozen` |
| **`INV-10`** (liên tục giá DEX) | `rel_gap` được **tính và in**, chỉ `S3` so với `< 1.0/lp` ở một chỗ | `assert rel_gap < 1.0 / lp_sol` ngay trong `graduate()` — mọi lần gọi đều kiểm |

> **`INV-08` là ca tinh vi nhất.** Trần ví/epoch **có** được cưỡng chế trong mã, nên ai đọc cũng thấy "đã kiểm". Nhưng nó được áp như **giới hạn đầu vào**, không như **bất biến đầu ra** — nghĩa là nếu một thay đổi làm `max_allowed` tính sai, không có gì đỏ. Bất biến khác giới hạn ở chỗ: giới hạn là *tính năng*, bất biến là *lời hứa về trạng thái sau mỗi phép chuyển*.

### 2.2. Bốn bất biến **không** có mã — và tôi không giả vờ

| Mã | Vì sao chưa có mã | Điều kiện để có |
|---|---|---|
| `INV-05` | cần `VersionRecord(h_k, h_base, ν_k)` — mô hình hiện chỉ có đường cong, không có sổ phiên bản | cùng lúc với `programs/game9k_registry` |
| `INV-07` | cần custody token (token nằm trong PDA) — mô hình chỉ giữ SOL | cùng lúc với `programs/game9k_curve` |
| `INV-11` | cần dấu `BotShare` do Oracle ký — mô hình không có oracle | cần một oracle giả trong test; đăng ký **P6** |
| `INV-12` | cần trạng thái governance (`upgrade_authority`, `terms_hash`) | ngoài phạm vi mô hình đường cong |

Bốn mã này vẫn **được trích** trong whitepaper và yellow paper. Đó là điều đúng — chúng là **đặc tả**, không phải kết quả đo. Nhưng từ hôm nay, bảng ở §2 là chỗ duy nhất nói rõ cái nào là đặc tả và cái nào là kết quả đo, và cổng giữ cho bảng đó không lạc hậu.

---

## 3. `check_invariants_coverage.py` — năm bất biến

| # | Bất biến | Nó chặn đúng cái gì |
|---|---|---|
| **1** | Mọi thẻ `INV-nn` trong `scripts/` phải có trong danh mục YP §8.1 | thẻ lạ, mã bịa, hoặc mã đã bị gỡ khỏi đặc tả mà còn trong mã |
| **2** | Câu **khẳng định đã kiểm** nêu dải `INV-xx..INV-yy` phải khớp số mã thực sự có mã | đúng lỗi của §12.1: `INV-01..INV-08` khi mã chỉ có bốn |
| **3** | Ba hệ đánh số phải được **khai báo tường minh** (`docs/04` nói nó là hệ riêng; Whitepaper trỏ về §8.1) | hai tài liệu nói chuyện lệch nhau mà không ai biết |
| **4** | Mỗi `INV-01..INV-12` có đúng một dòng trạng thái | mã "không ai nhớ" |
| **5** | `asserted` phải có ít nhất một dòng `assert` mang thẻ; `unasserted` phải có `why` | khai "đã kiểm" mà không có mã — và ngược lại, có mã mà bảng nói chưa |

Bảy phép thử, **bốn phá + ba đối chứng**:

```text
✓ P1 thẻ INV-99 không có trong danh mục → đỏ
✓ P2 câu 'INV-01..INV-08' khi mã chỉ có INV-01..INV-04 → đỏ
✓ P3 khai `asserted` mà không có dòng assert → đỏ
✓ P4 thẻ nằm trên dòng CHÚ THÍCH, không phải phép kiểm → đỏ
✓ P5 đối chứng: assert đủ các mã đã khai → sạch
✓ P6 đối chứng: câu 'vi phạm' chỉ nói về mã ĐÃ có → sạch
✓ P7 đối chứng: TIÊU ĐỀ nêu dải mà không khẳng định đã kiểm → sạch
INVARIANT COVERAGE SELFTEST: PASS — 7/7 phép thử đúng chiều
```

**P4 là phép thử quan trọng nhất.** Nó chứng minh cổng chỉ đếm **dòng kiểm**, không đếm chú thích. Nếu cổng đếm chú thích thì cách rẻ nhất để làm nó xanh là viết `# INV-05: sẽ làm sau` — và đó chính là kiểu "đã kiểm" mà `docs/37` §1 gọi là *in đậm thêm chữ HẠN*.

**P7 là đối chứng tôi phải thêm sau khi cổng bắt oan chính tài liệu này.** Bản đầu khớp mọi dải `INV-xx..INV-yy`, nên nó đỏ ở **tiêu đề** §8 ("Hệ 12 Bất biến, dải 01 đến 12") và ở **dòng mục lục** — hai chỗ chỉ **đặt tên** khái niệm, không khẳng định đã kiểm. Đây là **lần thu hẹp thứ tư** trong loạt `docs/35`–`docs/38`, cùng một nguyên nhân: khớp rộng bắt oan chính tài liệu đang định nghĩa khái niệm. Nguyên tắc nay viết thẳng trong mã: **chỉ câu có động từ khẳng định (`vi phạm`, `PASS`, `vượt qua`) mới bị kiểm.**

---

## 4. Đã sửa gì trong nguồn

Ba chỗ, tất cả là **chữ**:

| Tệp | Trước | Sau |
|---|---|---|
| `YELLOWPAPER.md` §12.1 (dòng `FUZZ`) | *"0 vi phạm"* trên **toàn dải 01–08** | `` **`0` vi phạm** trên các bất biến mô hình có mã kiểm (`INV-01..INV-04`, `INV-06`, `INV-08..INV-10` — 8/12 mã, xem `docs/38` §3) `` |
| `WHITEPAPER.md` §1.3 (sau bảng 4 nguyên tử) | *(không có)* | một callout trỏ thẻ `INV-nn` về danh mục chuẩn `YELLOWPAPER.md` §8.1 + lệnh `--audit` |
| `docs/04` §5 | *"8 bất biến toán học"* | *"8 bất biến toán học — **hệ đánh số riêng của tầng chương trình**, KHÔNG phải 12 bất biến `INV-01..INV-12` của `YELLOWPAPER.md` §8.1"* |

Cộng thêm **14 dòng `assert`** trong `verify_protocol_math.py` được gắn thẻ `INV-nn` và bốn `assert` mới (§2.1). `verify_protocol_math.py` vẫn **100% PASS**, và mọi con số đã công bố không đổi.

### 4.1. Một cổng thứ hai cũng phải sửa — và nó là bài học, không phải sự cố

Thêm một callout vào `WHITEPAPER.md` §1.3 làm `check_specs.py --tick` **đỏ 11/16**: nó ghim `source` theo **số dòng tuyệt đối** (`docs/WHITEPAPER.md:259`), nên mọi ghim nằm **sau** dòng chèn đều lệch — dù **không con số nào đổi**.

Đây là loại cổng sẽ bị tắt: nó đỏ vì lý do không liên quan tới điều nó định bảo vệ. Cách sửa **không** phải cập nhật 11 con số dòng (lần chèn sau lại làm lệch tiếp) mà là đổi **loại** của phép kiểm:

| | Trước | Sau |
|---|---|---|
| `source` là gì | **vị trí tuyệt đối** của con số | **điểm neo**: đúng tệp, đúng vùng |
| `tick` kiểm gì | con số nằm **đúng dòng 259** | con số **còn tồn tại** trong ±40 dòng quanh neo |
| Đổi số | đỏ | **vẫn đỏ** |
| Chèn/xoá một đoạn văn | **đỏ (sai)** | xanh |

> **Ranh giới phải nói rõ:** ±40 dòng là một **nới ngưỡng**, và nới ngưỡng là cách người ta tự vô hiệu hoá cổng. Nó chấp nhận được ở đây vì đối tượng của phép kiểm là **giá trị**, không phải vị trí — và vẫn đỏ khi giá trị biến mất khỏi vùng. Nếu một ngày ai cần kiểm **vị trí**, đó là một cổng khác, không phải cổng này bị nới thêm.

> **Vì sao phải gắn thẻ vào mã, không chỉ viết bảng trong tài liệu:** một bảng trong `.md` là **lời khai về mã**, và nó lạc hậu ngay lần sửa tiếp theo. Thẻ nằm **trên chính dòng `assert`** thì cổng đọc được, và khi ai xoá một `assert` thì bảng đỏ ngay — không cần ai nhớ cập nhật.

---

## 5. Việc **không** làm

- **Không** đổi số của hệ đánh số nào (đổi số = phá mọi trích dẫn trong tài liệu đã gửi nhà đầu tư).
- **Không** thêm `assert True` cho `INV-05/07/11/12` để bảng đủ 12 dòng xanh.
- **Không** đổi con số nào: `60.221994`, `15.908330`, `4.27 × 10⁻¹²`, `4.79×`, `1.252×`, `5,000 bps`.
- **Không** kiểm nội dung 8 bất biến của `docs/04` §5 — `programs/` trống, nên nội dung đó **chưa kiểm được** (`docs/37` §2.4).

---

## 6. Ba câu **sẽ bị hỏi**

| Câu hỏi | Trả lời đúng | Trả lời **sai** |
|---|---|---|
| *"12 bất biến của anh đã kiểm hết chưa?"* | *"Tám cái có mã kiểm trong mô hình, bốn cái là đặc tả chờ `programs/` — bảng ở `docs/38` §2, máy canh."* | *"Đã kiểm 12"* — sai; hoặc *"đã kiểm hết"* — không có nghĩa |
| *"Sao `INV-05` chỗ này khác chỗ kia?"* | *"Hai hệ đánh số: 12 bất biến giao thức (`YELLOWPAPER` §8.1) và 8 bất biến chương trình (`docs/04` §5). Nay cả hai chỗ đều khai điều đó."* | *"Chắc là cùng nghĩa"* |
| *"Làm sao biết bảng đó không lạc hậu?"* | *"Bảng không phải nguồn — thẻ `INV-nn` trên dòng `assert` là nguồn. Cổng đọc mã, nên xoá một `assert` là đỏ."* | *"Bảng được cập nhật thường xuyên"* |

---

## 7. Thứ tự làm

| # | Việc | Hạn | Nếu quá hạn |
|---|---|---|---|
| **1** | Đưa `check_invariants_coverage.py` thành cổng **19** của CI | trong PR này | cổng không tồn tại ⇒ bảng §2 lại thành văn xuôi |
| **2** | **P6** — bốn mã chưa có mã kiểm: hoặc có `assert`, hoặc bị gỡ khỏi §8.1 | 2026-12-05 | gỡ 4 mã và đổi mọi câu "12 bất biến" thành "8 bất biến có mã kiểm" |

`P6` nằm trong `pm/action-register.json` — cùng cơ chế `docs/37`: có người, có hạn, có hậu quả, và quá hạn là **ĐỎ**.
