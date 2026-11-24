# ADR-0021 — `BuildDiff` dùng Jaccard toàn cục + vế `content_files_added`

**Trạng thái:** Accepted (PO chốt Q1–Q6; Q1+Q2 → `yp-1.6`/`yp-1.7`, Q4–Q6 → `yp-1.8`)  
**Ngày:** 2026-11-21  
**Người quyết:** Project Owner  
**Liên quan:** [ADR-0020](ADR-0020-backlog-single-source.md), [ADR-0022](ADR-0022-the-loai-cong-bang.md) (Q4–Q6 — cổng chất lượng), [`yellowpaper-vi.md` §2.3](../11-whitepaper/yellowpaper-vi.md#23-build-diff--đo-thay-đổi-không-đo-cải-thiện), [`yellowpaper-formal-vi.md` §2.2](../11-whitepaper/yellowpaper-formal-vi.md), [PR #114](https://github.com/lexuankhanh1612/MetaPump/pull/114)

---

## 1. Bối cảnh

YP `1.5` định nghĩa `δ_k = 0,50·δ_code + 0,30·δ_asset + 0,20·δ_data`, mỗi `δ_c` là Jaccard **trong lớp tệp** `c`. Cổng `CANDIDATE` chỉ kiểm `δ_k ≥ 0,08`.

Đo trên gói game thật (chi tiết: [PR #114](https://github.com/lexuankhanh1612/MetaPump/pull/114)) cho thấy hai lỗi **độc lập**:

| Lỗi | Bằng chứng |
|---|---|
| **Lớp rỗng tặng điểm miễn phí** | Gói không có asset ⇒ `δ_asset = 1` khi thêm bất kỳ tệp nào. Thêm `.png` **rỗng 300 B** ⇒ `3.000 bps` |
| **Ngưỡng đo byte, không đo loại thay đổi** | `pacman` 70 KB: sửa **1 dòng** ⇒ `1.532 bps` (qua), thêm **tính năng 2 KB** ⇒ `210 bps` (trượt) |

Lỗi thứ hai **không sửa được bằng cách tinh chỉnh `θ_diff`**: `2 KB` là `2 KB` ở mọi ngưỡng.

## 2. Quyết định

**Q1 — Bỏ trọng số lớp, dùng Jaccard toàn cục:**

```
δ_k = 1 − (Σ_{x ∈ S_k ∩ S_{k−1}} size(x)) / (Σ_{x ∈ S_k ∪ S_{k−1}} size(x))
```

**Q2 — Thêm vế thứ hai vào vị từ `CANDIDATE`:**

```
CANDIDATE ⟺ δ_k ≥ θ_diff ∧ content_files_added(k) ≥ 1
content_files_added(k) = |{ p ∈ F_k : ext(p) ∈ {asset, data} ∧ p ∉ F_{k−1} }|
```

`θ_diff` **giữ nguyên `800 bps`**. Chỉ cách tính và vị từ đổi.

## 3. Vì sao đúng hai thay đổi này

**a. Trọng số lớp là lỗi cấu trúc, không phải tham số.** Trọng số cố định `0,30` cho lớp asset có nghĩa: *"nếu gói cũ không có asset, thêm asset là 30% thay đổi, bất kể tổng gói lớn bao nhiêu"*. Không có giá trị nào của `0,30` sửa được điều đó — phải bỏ cơ chế.

**b. Vế thứ hai phải độc lập kích thước.** Đo `content_files_added` trên 4 game thật (70 KB – 4,8 MB):

| Studio làm gì | tệp nội dung mới |
|---|---:|
| sửa 1 dòng lỗi | **0** |
| thêm tính năng (1 tệp `.js`) | **0** |
| thêm bộ sprite | **1** |
| thêm màn chơi | **1** |

Phân biệt **sạch ở mọi kích thước gói**, trong khi `δ` thì không.

**c. Hai vế là hội, không phải tuyển.** Đo lại `--sweep` sau khi sửa: sửa `1.000 byte` trong mã nguồn cho `δ = 9.314 bps` (qua vế 1) nhưng `0` tệp nội dung mới ⇒ `HOTFIX`. Trước `1.6` nó là `CANDIDATE`. Đây chính là lỗ "một commit, một cột mốc" mà cổng sinh ra để chặn.

## 4. ⚠️ Hạn chế còn lại — phải đọc trước khi tin cổng này

**Vế 1 (`δ`) vẫn phạt gói lớn.** Đo trên cùng corpus với công thức mới:

| Game | gói | thêm sprite 50 KB | thêm màn 100 KB |
|---|---:|---:|---:|
| pacman | 70 KB | **1.257 ✓** | **1.306 ✓** |
| asteroids | 247 KB | 389 · | 406 · |
| devil | 257 KB | 376 · | 392 · |
| slither | 4,8 MB | 116 · | 121 · |

**Thêm 50 KB đồ hoạ mới vào một game 247 KB bị xếp `HOTFIX`.** Đây là nghịch lý cùng loại với lỗi đã sửa, chỉ ở chiều ngược lại: `δ` là **tỷ lệ**, nên nó luôn phạt gói lớn.

Hệ quả thực tế: game HTML5 thương mại thường 1–10 MB. Với `θ_diff = 800 bps`, một game 5 MB cần thay đổi **> 400 KB** mới qua vế 1 — tức gần như không bao giờ, trừ khi thay toàn bộ nội dung.

**Vì vậy ADR này CHƯA đóng vấn đề.** Nó chỉ sửa được lỗi cấu trúc và lỗi "sửa 1 dòng". Nghịch lý kích thước cần một quyết định riêng.

## 5. Phương án cho nghịch lý kích thước — **ĐÃ CHỌN: A**

| Phương án | Ý tưởng | Ưu | Nhược |
|---|---|---|---|
| **A. Đổi `δ` sang byte tuyệt đối** | `δ_bytes ≥ θ_abs` với `θ_abs` tính theo bội số khối (VD `2× 4 KiB`) | Độc lập kích thước hoàn toàn | Cần chọn `θ_abs`; phải đo phân bố thật |
| **B. `δ` theo phân vị trong thể loại** | `δ ≥ median(δ của thể loại C)` | Tự thích nghi | Cần corpus đủ lớn theo thể loại |
| **C. Bỏ vế 1, chỉ dùng `content_files_added`** | Cổng chỉ kiểm "có nội dung mới" | Đơn giản, độc lập kích thước | Một tệp `.json` rác vẫn qua |
| **D. Giữ nguyên, ghi nhận là hạn chế** | Không làm gì | Không rủi ro | Game lớn không bao giờ qua cổng ⇒ chặn oan |

**Quyết định: PO chọn A** (2026-11-21, trên cơ sở đề xuất của AI). A đo cùng đại lượng bằng một đơn vị độc lập kích thước, và đã có sẵn khung đo (`cdc_chunk_bytes = 4096`).

### 5.1 Thi hành — `yp-1.7`

Đại lượng quyết định không còn là tỷ lệ mà là **số khối đối xứng hiệu**:

```
Δ_k = |S_k Δ S_{k−1}|        θ_abs = 8 khối (32 KiB)
CANDIDATE ⟺ Δ_k ≥ θ_abs ∧ content_files_added ≥ 1
```

`θ_abs` được **đo, không đoán** — chạy `node scripts/build_diff_granularity.mjs` (tất định, tái lập được):

| Thay đổi | pacman 70 KB | asteroids 247 KB | devil 257 KB | slither 4,8 MB |
|---|---:|---:|---:|---:|
| sửa `1 byte` | 2 | 2 | 2 | 2 |
| thêm feature `2 KB` | 1 | 1 | 1 | 1 |
| thêm sprite `50 KB` | **8** | **8** | **8** | **8** |
| thêm `300 KB` | 46 | 46 | 46 | 46 |

Hai tính chất quyết định:
1. **Độc lập kích thước.** `50 KB` cho đúng `8` khối ở cả bốn gói, chênh nhau `70×` về kích thước. Đây là thứ tỷ lệ `δ` không có: cùng sprite đó cho `1.257 bps` ở gói 70 KB (qua) và `116 bps` ở gói 4,8 MB (trượt).
2. **Sàn tự nhiên `2`.** Mọi sửa cục bộ đều cho `2` khối (một khối cũ mất, một khối mới sinh). `θ_abs = 8` cách sàn `4×`, nên ba kiểu sửa vặt đo được đều bị chặn.

**Đánh đổi đã biết:** thêm feature `2 KB` (1 khối) bị chặn. Đây là chủ ý — bản chỉ sửa `.js` đúng là `HOTFIX` theo định nghĩa. Hạ `θ_abs` xuống `4` sẽ mở loại này nhưng cho lọt sửa `30 byte` rải rác (`12–60` khối tuỳ mật độ).

**Sửa đổi kèm theo:** `MilestoneAttestation` `150..151` = `build_diff_chunks` (1 B, `uint8`) thay `build_diff_bps` (2 B); `151..152` thành `reserved = 0`; tổng vẫn `162 B`. `check_governance.py` 88 → **98** kiểm tra, trong đó có guard chống tỷ lệ quay lại (kiểm trực tiếp dòng vị từ `CANDIDATE`, đã test đảo chiều).

## 6. Hệ quả

**Được**
- Thêm tệp rỗng không còn mở được cột mốc.
- Sửa một dòng không còn mở được cột mốc (đo được: `HOTFIX` ở cả 4 game).
- `check_governance.py` từ 82 → **88** kiểm tra; có phép kiểm **đảo chiều** chặn công thức trọng số lớp quay lại.

**Mất / chấp nhận**
- `MilestoneAttestation` đổi layout: `expiry_ts` rút `8 B → 6 B` (`u48`, đủ tới năm 10889) để nhường `160..162` cho `content_files_added`. Tổng vẫn `162 B`.
- Oracle phải ghi thêm một trường; chương trình **tự băm lại** `h_k`/`h_{k−1}` để kiểm, nên oracle không khai khống được.
- Chưa giải quyết nghịch lý kích thước (§4).

## 7. Tự kiểm

| Câu hỏi | Trả lời | Bằng chứng |
|---|---|---|
| Số đo có tái lập được? | Có | `node scripts/build_diff_reference.mjs --sweep <gói>` · `build_diff_corpus_measure.mjs` |
| Guard có chặn công thức cũ quay lại? | Có — đã thử phá | `check_governance.py` 88/88, thử chèn lại `0.50·δ_code` ⇒ đỏ |
| Có bịa `θ_abs` cho phương án A? | Không — ghi rõ "cần đo trước" | §5 |
| Đã tuyên bố hết lỗi chưa? | Chưa — §4 ghi rõ nghịch lý kích thước còn nguyên | §4 |
