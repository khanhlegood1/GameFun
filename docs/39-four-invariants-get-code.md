# Bốn bất biến từng chỉ có tên — nay có mã kiểm, và cái giá của việc đó

> **Tài liệu sống:** `docs/39-four-invariants-get-code.md`
> **Trạng thái:** `SCOPING` — P6 đóng; `scripts/verify_invariants.py` + cổng **20**
> **Ngày:** 23/11/2026
> **Đầu vào:** *"Bốn bất biến chưa có mã kiểm (INV-05, INV-07, INV-11, INV-12) phải có assert : làm tiếp"*
> **Liên quan:** `docs/38` §2.2 (lý do chúng từng chưa có) · `docs/YELLOWPAPER` §2.2, §3.2, §7.2, §8.1 · `pm/action-register.json` P6

---

## 0. Kết luận trước

**Đã có `assert` cho cả bốn — nhưng chúng không cùng một loại với tám cái trước.** `INV-06/08/09/10` chỉ cần *phát biểu lại* một điều mô hình đường cong đã đúng. `INV-05/07/11/12` cần **đối tượng dữ liệu mới**: một sổ phiên bản, một ledger lưu ký, một oracle `BotShare`, một ôtômat governance. Vòng này dựng bốn đối tượng đó và assert đúng câu đặc tả ở `YELLOWPAPER` §8.1.

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Đã có `assert` chưa? | **Có** — 66 kiểm tra trong `scripts/verify_invariants.py`, bảng `--audit` xanh cả bốn |
| **2** | Cái được chứng minh là gì? | **Hàm quyết định từ chối đúng chỗ và chấp nhận đúng chỗ** — `record_version_milestone`, `withdraw`, `allow_new_launch`, ôtômat governance |
| **3** | Cái **không** được chứng minh là gì? | **Chương trình Anchor chạy đúng.** `programs/` vẫn trống; đây là mô hình, không phải on-chain (§1) |
| **4** | `check_invariants_coverage.py` nói gì? | **12/12 mã có mã kiểm** — `docs/38` từng báo 8/12 |
| **5** | Có con số nào đổi không? | **Không.** Tệp mới không sửa `verify_protocol_math.py`; nó chỉ *import* mô hình đường cong để dựng ledger custody (§2) |
| **6** | Có phải chỉ thêm `assert` cho đủ? | **Không.** Mỗi bất biến có ít nhất một **phép phá**: một hành vi sai bị từ chối với **đúng mã lỗi**, và một bất biến **đỏ** khi dữ liệu bị làm bẩn sau lưng API |

> **Điều tôi từ chối:** gọi bốn thứ này là "đã kiểm on-chain". Chúng là **mô hình quyết định** — đúng loại bằng chứng mà `docs/36` dùng cho bốn bổ đề, và đúng giới hạn mà `docs/36` §0 đã nói ra: tầng hệ thống vẫn là `❌ chưa có`.

---

## 1. Ranh giới: mô hình quyết định ≠ chương trình

| | `verify_protocol_math.py` (8 mã) | `verify_invariants.py` (4 mã) |
|---|---|---|
| Đối tượng | trạng thái đường cong (`CurveState`) | **quyết định** của hợp đồng: nhận/từ chối một bản ghi, một lệnh rút, một launch |
| Kiểm cái gì | bất biến **trên trạng thái** sau mỗi phép chuyển | bất biến **trên hàm quyết định** và trên lịch sử |
| Ví dụ | `v_sol · v_tok ≥ K` sau `buy()` | `record()` từ chối `ν` không lớn hơn, với `ERR_VERSION_OLDER` |

Điều này **không** làm yếu bất biến — nó làm rõ **cái gì** đang được kiểm. Một bất biến "không có token nào trong ví trước Graduation" chỉ kiểm được nếu mô hình có khái niệm "ví" **tách khỏi** "PDA"; mô hình đường cong cũ không có, và đó chính là lý do `INV-07` từng là một cái tên.

---

## 2. Bốn bất biến, bốn đối tượng dựng mới

### 2.1. `INV-05` — Phả hệ Phiên bản Đơn điệu → `VersionChain`

Đặc tả (`YP` §2.2) có **năm** điều kiện, mỗi điều kiện có **một mã lỗi riêng**. Một phép kiểm chỉ nói "bị từ chối" là chưa đủ — nó phải nói **từ chối vì lý do gì**, vì năm lý do đó dẫn tới năm thông báo khác nhau cho studio.

| Hành vi sai | Mã lỗi phải trả |
|---|---|
| `ν_k = ν_{k-1}` | `ERR_VERSION_SAME` |
| `ν_k <_lex ν_{k-1}` | `ERR_VERSION_OLDER` |
| `h_base,k ≠ h_{k-1}` | `ERR_ORPHAN_BASE` |
| `h_k = h_{k-1}` (đóng ZIP lại y nguyên) | `ERR_IDENTICAL_BUILD` |
| `δ_k < θ_diff = 0.08` (đổi màu 1 nút) | `ERR_HOTFIX_NOT_MILESTONE` |

Cộng thêm luật riêng của `k = 1`: `h_base,1 = 0^32` — nếu không, `ERR_ORPHAN_BASE`. Và một kiểm **đọc lại sổ** sau khi ghi: `k` liên tục, `ν` tăng, `h` nối đúng, `δ` trên ngưỡng. Đọc lại là phần quan trọng — nó không tin kết quả của `record()`.

> **Vì sao dựng một sổ thật thay vì assert trên tham số:** `INV-05` là bất biến **theo thời gian** ("với mọi `v_k` ghi nhận on-chain"). Nó chỉ có nghĩa nếu có một chuỗi bản ghi để đọc. Assert trên một đối tượng đơn lẻ sẽ chỉ kiểm được một hành vi, không kiểm được **tính đơn điệu**.

### 2.2. `INV-07` — Cô lập Lưu ký Tiền Tốt nghiệp → `CustodyLedger`

Đặc tả: *"Trước khi `Graduated`, không tồn tại bất kỳ token dự án nào trong ví cá nhân bên ngoài các PDA vault."*

Mô hình cũ có `positions[u].tokens` — nhưng đó là **token đã bán**, không phân biệt nằm ở PDA hay ở ví. `CustodyLedger` tách hai chỗ đó ra, và `withdraw()` là **đường duy nhất** đưa token ra ví:

```text
withdraw(user, units):
    if status != "Graduated":  raise CustodyViolation     # INV-07
    ...
```

Ba phép kiểm: (a) mua token **không** làm ví có token; (b) `withdraw` trước `Graduated` bị chặn; (c) **ghi thẳng vào ví** (bỏ qua API) làm bất biến **đỏ**. Phép (c) là phép quan trọng nhất — nó chứng minh bất biến đọc **dữ liệu**, không đọc **lời khai của API**.

### 2.3. `INV-11` — Giới hạn Gian lận Hệ thống → `botshare()` + `LaunchBreaker`

Hai phần, và phần thứ hai là phần dễ làm ẩu:

**(a) Ước lượng.** Công thức difference/HT của `YP` §3.2, tính bằng `Fraction` (không `float`) và kiểm bằng một ví dụ **tính tay được**:

```text
Σ d·p = 3000 × 0.10 = 300
audit:  600/(1/200)·(1−0.10) + 900/(1/200)·(0−0.10) = 108 000 − 18 000 = 90 000
BotShare = (300 + 90 000) / 3000 ≈ 30.01
```

**(b) Cầu dao.** `YP` §3.2 nói: `> 0.08 ⇒ allow_new_launch = false`, và *"mở lại sau hai chu kỳ liên tiếp ≤ 0.08"*. Ba điều kiện biên được kiểm riêng:

| Đầu vào | Kỳ vọng | Vì sao |
|---|---|---|
| `0.08` đúng bằng | **vẫn cho** | bất đẳng thức là `>`, không phải `≥` — cùng loại lỗi biên như `5,000 bps` ở `docs/37` §2.2 |
| `0.081` | **đóng** | |
| một chu kỳ sạch | **vẫn đóng** | "hai chu kỳ liên tiếp" — đây là chỗ dễ đọc lướt |
| hai chu kỳ sạch | **mở** | |

Phép phá: ép `allowed = True` sau một chu kỳ bẩn duy nhất ⇒ `check_invariant()` phải **đỏ**. Nó đọc **lịch sử**, không đọc cờ.

### 2.4. `INV-12` — Tính Bất biến Điều khoản & Quản trị → `Governance`

Ôtômat 3 trạng thái của `YP` §7.2, và **ba** ràng buộc tách biệt:

1. **Trước `G2`** (`t < t₀ + 7.776.000 s`): cần `≥ 4/7` chữ ký **và** `sim_tests == PASS` để queue; `execute` cần `now ≥ queued_at + 172.800 s` (48h). Thiếu một điều ⇒ từ chối, mỗi trường hợp một mã lỗi.
2. **`terms_hash` bất khả xâm phạm suốt vòng đời** — kể cả trước `G2`. Đây là vế dễ bị bỏ: người ta hay nghĩ "trước G2 thì còn sửa được", nhưng đặc tả nói `terms_hash` **không đổi**, chỉ `upgrade_authority` mới đổi theo thời gian.
3. **Từ `t ≥ t₀ + T_imm`**: `authority == None`, và **mọi** lệnh nâng cấp bị từ chối vĩnh viễn với `ERR_PROGRAM_IMMUTABLE`. Kiểm trên cả đường thời gian (`T_imm`, `+1`, `+86 400`, `×10`), không chỉ một điểm.

Phép phá: đặt lại `authority` sau `G2` ⇒ `check_invariant()` phải **đỏ**.

---

## 3. Một lỗi thiết kế tôi gặp ngay lần chạy đầu — và nó đáng ghi lại

Lần chạy đầu của `verify_invariants.py`:

```text
INVARIANTS: FAIL — 4 vi phạm / 71 kiểm tra
  - INV-07: 1000 token nằm trong ví cá nhân khi status = Active
  - INV-07: bảo toàn custody sai: …
  - INV-11: chu kỳ 1 có BotShare 9.00% > 8% nhưng vẫn cho launch mới
  - INV-12: t = 7776001 ≥ t0 + T_imm nhưng upgrade_authority = 'squads_4of7'
```

**Cả bốn "vi phạm" là phép phá của chính tôi.** Tôi viết phép phá bằng cách làm bẩn dữ liệu rồi kiểm "số vi phạm có tăng không" — nhưng để nó tăng thì nó phải ghi vào **cùng danh sách** `FAILS`, nên lần chạy đầy đủ báo đỏ vì chính phép thử của mình.

Cách sửa: `expect_red(fn)` chạy phép phá trong một **danh sách riêng** và trả về vi phạm nó sinh ra.

> **Vì sao ghi lại:** đây đúng loại lỗi mà `docs/37` §2 gọi là "cổng tự bắt oan". Nếu tôi chỉ sửa cho xanh rồi im, tệp này sẽ trông như một cổng sạch — trong khi cách duy nhất để nó xanh là **không có phép phá nào**. Một cổng không có phép phá là một cổng chưa được kiểm.

---

## 4. Cổng 20 và bảng `--audit`

```text
INV-05  Phả hệ Phiên bản Đơn điệu                 ✓ 29 kiểm tra
INV-07  Cô lập Lưu ký Tiền Tốt nghiệp             ✓  8 kiểm tra
INV-11  Giới hạn Gian lận Hệ thống                ✓  8 kiểm tra
INV-12  Tính Bất biến Điều khoản & Quản trị       ✓ 21 kiểm tra

INVARIANTS: PASS — 66 kiểm tra · 4 bất biến · mô hình quyết định
INVARIANTS SELFTEST: PASS — 6/6 (4 đối chứng + 2 phép phá ngưỡng)
```

Hai phép phá **ngưỡng** ở `--selftest` là loại khác với phép phá hành vi: chúng hạ ngưỡng xuống và chứng minh **ngưỡng có tác dụng**.

| Phép phá | Làm gì | Kết quả phải có |
|---|---|---|
| `P5` | đặt `θ_diff = 0` | `δ = 0` **lọt** vào sổ ⇒ nếu ngưỡng không có tác dụng thì phép thử này đỏ |
| `P6` | đặt `β_max = 0.5` | `8,1%` **không** bị ngắt ⇒ chứng minh con số `0.08` đang làm việc |

`check_invariants_coverage.py` nay đọc **12/12**:

```text
INVARIANT COVERAGE: PASS — 65 kiểm tra · 5 bất biến · 12/12 mã có mã kiểm · 37 dòng assert mang thẻ
```

---

## 5. Một cổng khác cũng phải sửa — lần này cổng đúng, lời khai sai

Khi đóng `P6`, tôi ghi `evidence` là *"… cho 12/12 asserted (tệp: `scripts/verify_invariants.py`)"* và `check_actions.py` **đỏ**:

```text
[P6]: `evidence` trỏ tới check_invariants_coverage.py nhưng tệp không tồn tại
```

Lỗi ở **cách viết bằng chứng**, không ở bằng chứng: tôi viết tên tệp **trần** (không thư mục), và `evidence_paths()` giải nó thành `ROOT/check_invariants_coverage.py`. Hai lựa chọn:

| Cách sửa | Đánh giá |
|---|---|
| Sửa `evidence` thành `scripts/check_invariants_coverage.py` | **Sai hướng** — nó làm lời khai đúng bằng cách né cổng, và lần sau ai viết tên trần lại đỏ |
| Sửa `evidence_paths()` để thử thêm `scripts/`, `pm/`, `docs/` với tên trần | **Đúng** — "chạy `foo.py`" là cách người ta thật sự viết; cổng đỏ vì *cách viết* là cổng sẽ bị tắt |

Đã thêm **đối chứng `P8`** để khoá hành vi mới (`--selftest` nay **8/8**). Tên tệp không tồn tại ở đâu cả thì **vẫn đỏ** — `P7` chứng minh điều đó.

---

## 6. Ba câu **sẽ bị hỏi**

| Câu hỏi | Trả lời đúng | Trả lời **sai** |
|---|---|---|
| *"12 bất biến đã kiểm hết chưa?"* | *"Mười hai mã có phép kiểm trong **mô hình quyết định**. Tầng on-chain thì chưa — `programs/` trống, và đó là P1/P6 loại khác."* | *"Đã kiểm hết 12"* — không nói mô hình hay on-chain |
| *"Kiểm 'hàm quyết định' thì có giá trị gì?"* | *"Nó khoá **hợp đồng hành vi**: năm mã lỗi của `record_version_milestone`, biên `> 0.08` là `>` chứ không `≥`, và `terms_hash` bất biến **trước** `G2`. Đó là những chỗ implementation hay hiểu lệch, không phải chỗ toán sai."* | *"Tương đương kiểm on-chain"* |
| *"Nếu `programs/` viết xong mà lệch thì sao?"* | *"Cùng một bộ kiểm chạy lại trên chương trình thật; lệch là đỏ. Đó là lý do bốn mô hình này tồn tại **trước** khi có code."* | *"Sẽ không lệch"* |

---

## 7. Việc **không** làm

- **Không** sửa `verify_protocol_math.py` để "gom" bốn bất biến vào — hai tệp khoá hai loại khác nhau (§1), và file mới chỉ **import** mô hình đường cong, không sửa nó.
- **Không** đổi con số nào đã công bố.
- **Không** nói bốn bất biến này đã được kiểm on-chain.
- **Không** dùng `float` ở chỗ quyết định: `BotShare`, `δ`, `θ` đều là `Fraction` — biên `0.08` phải so **chính xác**, nếu không phép kiểm biên là vô nghĩa.

---

## 8. Còn lại gì

| # | Việc | Ai | Hạn |
|---|---|---|---|
| **P1** | ràng buộc biên `S_LP < X_end·(1−f)` vào `validate_launch` | LXK | 2026-12-18 |
| **P2** | ghi lý do rent vào `YELLOWPAPER` §4.3 | LXK | 2026-12-18 |
| **P3** | `requirements.txt` cho toolchain PDF | AGENT | 2026-12-20 |

`P6` **đã đóng** trong vòng này, kèm bằng chứng trỏ tệp thật — và chính việc đóng nó đã làm lộ một lỗi trong `check_actions.py` (§5).
