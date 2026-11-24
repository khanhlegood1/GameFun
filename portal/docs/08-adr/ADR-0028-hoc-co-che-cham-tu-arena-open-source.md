# ADR-0028 — Học cơ chế chấm từ mã nguồn mở của Arena: **hai việc làm ngay, hai việc phải hỏi PO**

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`hoc-tu-arena-open-source.md`](../00-framework/hoc-tu-arena-open-source.md) · [`ADR-0016`](ADR-0016-license-compliance.md) · [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) · [`ai-agile-adoption.md`](../00-framework/ai-agile-adoption.md) · **Q61**

> ⚠️ Tài liệu này **không** thêm dependency nào. Không `pip install`, không vendored code.
> Cả ba repo được đọc đều Apache-2.0; repo này **chưa có** `NOTICE`, nên chép code là tạo
> nghĩa vụ chưa đáp ứng được. Xem §4.

---

## 0. Trả lời ngắn

| Việc | Làm ngay hay hỏi PO? |
|---|---|
| Trace của gate có **bảng lý do loại** (4 khoá) | ✅ **Làm ngay** — chỉ thêm trường, không đổi quyền |
| Template signoff **nói rõ tie tính là gì** | ✅ **Làm ngay** — sửa một câu |
| `check_gates.py` cảnh báo khi **một người ký > 2 gate** | 🔴 **Hỏi PO** — đổi ai được quyết |
| Trình bày phương án **ẩn danh + hoán vị** ở gate | 🔴 **Hỏi PO** — đổi cách làm việc |
| Học **trình tự agent sinh câu trả lời** từ repo Arena | ❌ **Không thể** — mã đó đóng. Xem §3 |

---

## 1. Bối cảnh

PO yêu cầu *"tham khảo các repo open-source tạo ra Arena.ai để học cách áp dụng logic tuần tự
mà Agent trả lời các câu chat"*.

Tôi đã kiểm (§1 của [ghi chú](../00-framework/hoc-tu-arena-open-source.md)): phần **mở** của
Arena là `lm-sys/FastChat` (arena gốc), `Arena-OSS/arena-rank` (phương pháp xếp hạng hiện
hành), `Arena-OSS/arena-hard-auto` (benchmark tự động). Cả ba **Apache-2.0**. Phần **đang chạy**
trên `arena.ai` thì **đóng**.

Nghĩa là: câu hỏi có **hai nửa**, và chỉ một nửa trả lời được bằng mã.

---

## 2. Quyết định

### 2.1. ✅ Nhận: bảng lý do loại trong trace của gate

`FastChat` loại vote theo **8 lý do có tên**, mỗi lý do có bộ đếm riêng
(`clean_battle_data.py:156`). Tỉ lệ loại vì từng lý do là **số đo được**, không phải chuyện kể.

Repo này đang thiếu đúng thứ đó: `P0x-signoff.md` chỉ có ✅/❌, nên `check_gates.py` kiểm được
**cấu trúc** mà không kiểm được **chất lượng**.

**Nhận 4 khoá, không nhận 8** — quy mô repo này nhỏ hơn nhiều:

| Khoá | Nghĩa |
|---|---|
| `thieu_nguon` | Khẳng định không dẫn được về tệp/dòng trong repo |
| `so_lieu_khong_kiem_duoc` | Có số nhưng không có lệnh đo lại được |
| `mau_thuan` | Hai tài liệu nói khác nhau |
| `vuot_pham_vi` | Thuộc nhóm phải hỏi PO (kinh tế/pháp lý) mà AI tự quyết |

### 2.2. ✅ Nhận: khai báo tie là bao nhiêu

`arena-rank` khai báo `tie = 0.5`, `both_bad = 0.5` **một cách tường minh**
(`preprocessing/common.py:6`). `both_bad = 0.5` là quyết định có chủ ý: "cả hai đều dở" là
**hoà**, không phải "cả hai đều thua".

**Nhận:** template signoff thêm một dòng *"Bằng nhau thì tính là gì?"* cho mọi mục so sánh.

### 2.3. 🔴 Không tự quyết: giới hạn số gate một người được ký

`arena-rank` tính **cỡ mẫu hiệu dụng** (`datasets.py:94`) để một người vote 100 lần không
được tính như 100 người. Tương ứng ở đây: **một PO ký 6/6 gate** không phải là "6/6 gate đồng
thuận", mà là **một** người đồng ý 6 lần.

Nhưng — và đây là chỗ tôi phải dừng — **một PO duy nhất có thể là thiết kế đúng** của dự án
này. `docs/gates/P01-signoff.md` ghi `Owner (người ký) | Product Owner` cho **mọi** gate. Đó
có thể là chủ ý, không phải lỗi.

⇒ **Q61a:** có giới hạn số gate một người được ký trong cùng một ngày không?

### 2.4. 🔴 Không tự quyết: ẩn danh + hoán vị khi trình PO

`FastChat` làm **hai** việc tách biệt — ẩn tên (`gradio_block_arena_anony.py:56`) và hoán vị
ngẫu nhiên hai bên (cùng tệp, dòng `262`). Chúng chống **hai** thiên lệch khác nhau: thương
hiệu và vị trí. Thiếu một trong hai là vẫn lệch.

Áp vào đây sẽ đổi **cách PO làm việc** ở mọi gate. Không phải việc AI tự quyết.

⇒ **Q61b:** có thử ẩn danh + hoán vị ở **một** gate (đề nghị P05, vì checklist đầy đủ nhất)
trước khi áp cho cả 6?

---

## 3. ❌ Không nhận: "logic tuần tự agent" — vì không có mã để đọc

Đây là phần trung tâm của yêu cầu, và tôi phải nói thẳng **không làm được**:

| Thứ câu hỏi muốn | Có trong repo mở của Arena? |
|---|---|
| Agent lập kế hoạch trả lời thế nào | ❌ Không |
| Gọi công cụ gì, theo thứ tự nào | ❌ Không |
| Tự kiểm rồi sửa ra sao | ❌ Không |
| Quyết định dừng khi nào | ❌ Không |

`FastChat` có `bot_response_multi()` (`gradio_block_arena_anony.py:358`) — nhưng đó là **gọi
hai model song song và stream chữ về hai khung**, không phải vòng lặp suy luận. `get_battle_pair()`
là **lấy mẫu**, không phải ra quyết định.

> Nếu tôi viết *"Agent của Arena làm theo 5 bước sau…"* thì đó là **bịa**. ADR-0023 cấm tuyên
> bố không kiểm được, và điều này cũng vậy.

**Thay vào đó:** ghi chú §7 mô tả trình tự **quan sát được** ở chính agent này
(`đọc → đo → viết → tự kiểm → tiêm lỗi → hoàn nguyên → ghi cái đã sai`), có nhãn rõ là **quan
sát**, không phải đọc mã. Nó khớp với `metacognition: monitor → regulate` mà ADR-0026 §1 đã map.

---

## 4. Vì sao không chép code, dù cả ba đều Apache-2.0

| | |
|---|---|
| Repo này có `NOTICE`? | **Không** (đã kiểm: `ls NOTICE` → không có) |
| Apache-2.0 §4 yêu cầu gì khi phân phối lại? | Giữ license + **kèm NOTICE** nếu bản gốc có |
| Vậy chép code vào đây nghĩa là | Tạo nghĩa vụ chưa đáp ứng được |

Tiền lệ: [`ADR-0016`](ADR-0016-license-compliance.md) loại AGPL và "không có license". Ở đây
license **tốt**, nhưng **nghĩa vụ ghi công** chưa được chuẩn bị. Chọn cách **viết lại cơ chế**,
không chép dòng nào.

`lm-sys/lm-sys.github.io` (trang web + blog) có license **NOASSERTION** ⇒ **không đụng**, cùng
nhóm với `theshaneobrien/tickle` trong [`docs/10-opensource`](../10-opensource/README.md) §1.

---

## 5. Hệ quả nếu nhận

| | |
|---|---|
| Tệp phải sửa | `docs/gates/README.md` (template), 6 tệp `P0x-signoff.md` |
| Script phải sửa | `check_gates.py` (kiểm trường mới), có thể `check_gate_deadlines.py` |
| Dependency mới | **Không có** |
| Gate đang mở có bị ảnh hưởng? | Không — thêm trường, không đổi trạng thái |
| Ai phải ký lại? | Không ai. 6 gate vẫn **chưa ký** |

---

## 6. Tự phê bình

1. **Tôi không đọc được mã đang chạy trên arena.ai.** §3 nói "không có trong 5 repo đã kiểm",
   **không** nói "không tồn tại". Phạm vi: 5 repo, đo 2026-11-18.
2. **`FastChat` cũ hơn nền tảng đang chạy hơn 2 năm** (bản phát hành mới nhất `v0.2.36`,
   2024-02-11). Cơ chế có thể đã đổi. Tôi dẫn **số dòng cụ thể** để kiểm lại được — và đã
   tự kiểm lại: **5 trong 8** số dòng tôi viết lần đầu là **sai**, đã sửa bằng `grep -n`.
   Đây đúng là lỗi mà `AGENTS.md` cảnh báo.
3. **§2.3 là ánh xạ của tôi**, không phải điều `arena-rank` nói. Nó nói về *judge*, tôi đổi
   thành *reviewer*. Ánh xạ có thể sai.
4. **Không có số liệu về hiệu quả.** Tôi không biết bảng lý do loại sẽ cải thiện chất lượng
   gate bao nhiêu — không có dữ liệu trước/sau. Đây là **đề xuất hợp lý**, không phải
   **cải tiến đã đo**.
5. **Q61 chưa trả lời.** §2.3 và §2.4 chờ PO. Tôi không tự quyết vì cả hai đổi **ai được quyết**.
