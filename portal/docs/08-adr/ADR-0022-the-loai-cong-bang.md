# ADR-0022 — Danh mục thể loại đóng, ngưỡng `θ_D7,C` neo top-25%, và chính sách công bố

**Trạng thái:** Accepted (PO chốt Q4–Q6, 2026-11-21)
**Ngày:** 2026-11-21
**Người quyết:** Project Owner
**Liên quan:** [ADR-0007](ADR-0007-program-upgrade-policy.md), [ADR-0021](ADR-0021-builddiff-toan-cuc.md), [`yellowpaper-vi.md` §4.4a–c](../11-whitepaper/yellowpaper-vi.md), [PR #117](https://github.com/lexuankhanh1612/MetaPump/pull/117)

---

## 1. Bối cảnh

`percentile_C(v_k) ≥ 0,60` (`M3`) và `D_7 ≥ θ_D7,C` (`M4`) đã có trong `GATE_TABLE` từ
`yp-1.6`, nhưng **không chạy được**: thiếu danh mục thể loại `C` và thiếu giá trị
`θ_D7,C`. Đây là Q4–Q6 của [tài liệu quyết định](../12-decisions/2026-11-21-builddiff-corpus-va-nguong.md).

Ba câu hỏi này **không** thuộc Build Diff — Build Diff đã xong ở ADR-0021. Chúng thuộc
**cổng chất lượng**, nơi việc so với thể loại là đúng chỗ (so **kết quả**, không so
**lượng thay đổi**).

## 2. Quyết định

### Q4 — Danh mục `C`: 6 nhóm, **đóng**

`hyper-casual` · `puzzle` · `arcade-action` · `idle-incremental` · `multiplayer-arena` · `simulation-strategy`

Chọn theo **cách người chơi tiêu thời gian**, vì `d̄_act ≥ 180 s` và `D_7` là thứ cổng đo.
Phân loại của app store không dùng được: nó tối ưu cho khám phá, không cho so sánh giữ chân.

### Q5 — `θ_D7,C`: neo **top 25%** của thể loại

Không neo vào trung vị: trung vị nghĩa là **một nửa số game trượt**, tức `M4` đóng với
một nửa thị trường — vô nghĩa với một cổng "phát hành toàn cầu".

| `genre_id` | `θ_D7,C` | Nguồn | Độ tin |
|---|---:|---|---|
| `hyper-casual` | `0.080` | Mistplay 2023: `5,90%` | suy ra (nới lên top-25% band) |
| `puzzle` | `0.140` | Mistplay 2023: `12,18%` | suy ra (làm tròn) |
| `arcade-action` | `0.090` | action `7,64%` / shooting `6,45%` | suy ra |
| `idle-incremental` | `0.120` | — | **`assumed`** |
| `multiplayer-arena` | `0.100` | — | **`assumed`** |
| `simulation-strategy` | `0.100` | simulation `8,71%` / strategy `8,06%` | suy ra |

### Q6 — Công bố: ba bảng tách biệt

| Bảng | Nội dung | Công bố |
|---|---|---|
| B1 | Benchmark ngành (đã công khai) | ngay |
| B2 | Phân bố `Δ_k` của bản nộp | `n ≥ 50`, ≥ 5 game/ô, theo quý |
| B3 | `D_7` từng studio | **không bao giờ** |

## 3. Phương án đã cân nhắc

| Phương án | Vì sao không chọn |
|---|---|
| **Danh mục mở** (studio tự nhập) | Mỗi game một thể loại ⇒ `percentile_C` không có mẫu nào đủ lớn |
| **Danh mục theo app store** (~30 nhóm) | Mẫu mỗi nhóm quá mỏng; `θ_D7,C` thành 30 tham số phải biện luận |
| **`θ_D7,C` = trung vị thể loại** | Một nửa thị trường bị chặn ở `M4` |
| **`θ_D7,C` = một số chung, không theo thể loại** | Phạt oan `hyper-casual` (sàn tự nhiên `5,9%`) và ưu ái `puzzle` (`12,18%`) |
| **Công bố `D_7` từng studio** | Là dữ liệu kinh doanh của studio; công bố là phản bội niềm tin |

## 4. Hệ quả

**Chấp nhận:**
- Hai giá trị `θ_D7,C` là **giả thuyết chưa có nguồn** (`idle-incremental`, `multiplayer-arena`). Đánh dấu `source: assumed` trong config để thay được mà không sửa luật.
- `percentile_C` trên `n < 200` game/thể loại là nhiễu ⇒ suy giảm về toàn cục với cờ `percentile_basis = global`.
- Danh mục đóng có thể thiếu thể loại thật (vd. rhythm, sports). Thêm nhóm **sau** khi có dữ liệu, không phải trước.

**Bắt buộc:**
- `genre` `not null` khi tạo game; đổi sau `M2` cần `HITL_curator` (chống genre shopping).
- `θ_D7,C` là **config**, sửa bằng `4/7` multisig + timelock `48h` ([ADR-0007](ADR-0007-program-upgrade-policy.md)) — cùng luật `θ_abs`.
- CI: `check_governance.py` khoá danh mục 6 nhóm (kể cả chặn thể loại thứ 7 lọt vào bảng) và bất biến `θ_D7,C ≥ trung vị` — đã test đảo chiều.

## 5. Điều ADR này KHÔNG nói

- **Không** đặt `θ_abs` — `θ_abs = 8` khối đã chốt ở ADR-0021 và **không phụ thuộc thể loại**.
- **Không** có số liệu phân bố `D_7` riêng của nền tảng — chưa có studio nào. Mọi số ở đây đều là benchmark ngành **đã công khai**, có dẫn nguồn.
- **Không** cam kết `θ_D7,C` là đúng. Nó là **neo khởi đầu** để `M4` chạy được; số thật thay khi có ≥ 50 bản nộp.
