# ADR-NNNN — [Tên quyết định, một dòng, nêu ĐIỀU ĐƯỢC QUYẾT, không nêu chủ đề]

**Trạng thái:** `Proposed` → `Accepted` / `Rejected` / `Superseded by ADR-NNNN`
**Ngày:** YYYY-MM-DD
**Người đề xuất:** AI agent *hoặc* tên người · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** `ADR-00NN` · `docs/NN-…/…md` · `Q-NN`   <!-- viết dạng mã, không dạng link: đích chưa tồn tại -->

> **Mẫu này bắt buộc bốn thứ** — `scripts/check_adr_structure.py` đỏ nếu thiếu:
>
> | # | Mục | Vì sao bắt buộc |
> |---|---|---|
> | 1 | `## 0. Trả lời ngắn` | Người đọc quyết trong 30 giây; không phải đọc hết |
> | 2 | `## N. Điều ADR này KHÔNG bao gồm` | **Bắt buộc từ 2026-11-18** — chống scope creep ([`ADR-0043`](ADR-0043-hoc-tu-fde-roadmap.md) §3.3) |
> | 3 | `## N. Ranh giới trung thực` | Mục nêu cái gì **chưa** kiểm, **chưa** chạy, **chưa** đo |
> | 4 | `**Trạng thái:**` + `**Ngày:**` + `**Người quyết:**` | Không có ba dòng này thì ADR không phân biệt được với ghi chú |
>
> Mục 2 có vì lý do đo được: repo đã có nhiều ADR **tự nguyện** ghi mục này (`ADR-0023` §3,
> `ADR-0040` §8, `ADR-0042` §6) nhưng **không bắt buộc** — nên có lúc thiếu, và một yêu cầu không
> ghi "ngoài phạm vi" thì mặc định được hiểu là **sẽ làm**.

---

## 0. Trả lời ngắn

> Một câu: quyết định là gì. Nếu có nhiều yêu cầu trong một câu hỏi, tách bảng:

| # | Yêu cầu | Kết quả |
|---|---|---|
| 1 | … | ✅ / 🟡 / 🔴 |
| 2 | … | … |

---

## 1. Bối cảnh & vấn đề

Câu hỏi gốc, **nguyên văn** nếu là yêu cầu của PO. Không diễn giải lại thành câu hỏi mình muốn trả lời.

---

## 2. Các phương án đã cân nhắc

| Phương án | Ưu | Nhược | Chọn? |
|---|---|---|---|
| A | | | |
| B | | | |

> Mục "bằng nhau thì tính là gì" (nếu so sánh bằng số): ghi **giá trị của thế hoà**
> ([`gates/README.md`](../gates/README.md) §"Bằng nhau thì tính là gì?").

---

## 3. Quyết định

Điều được chọn, và **điều kiện để nó sai** (cơ chế tự bác bỏ — [`ADR-0023`](ADR-0023-chinh-sach-tuyen-bo-dau-tien.md) §3 điều 3).

---

## 4. Hệ quả

| Loại | Nội dung |
|---|---|
| Được | |
| Mất | |
| Cần làm tiếp | |

---

## 5. Điều ADR này **KHÔNG** bao gồm

> **Mục bắt buộc.** Liệt kê những gì **liên quan nhưng nằm ngoài quyết định này**, và **vì sao**
> chúng ngoài phạm vi. Nếu để trống, điều đó có nghĩa **mọi thứ liên quan đều nằm trong phạm vi** —
> và đó là cách scope creep bắt đầu.

| Không bao gồm | Vì sao ngoài phạm vi | Ai/cái gì sẽ quyết |
|---|---|---|
| | | |

---

## 6. Câu hỏi cần PO quyết

| Mã | Câu hỏi |
|---|---|
| **Q-ADR<N>-a** | |

---

## 7. Ranh giới trung thực

- **Đã kiểm:** (kèm lệnh + phạm vi, không chỉ kết luận — [`AGENTS.md`](../../AGENTS.md) luật thứ tư)
- **Chưa kiểm:** …
- **Chưa chạy:** …
- **Không** khẳng định "đầu tiên" / "duy nhất" / "chưa ai làm" — dạng đúng là *"chúng tôi chưa tìm
  thấy"*, kèm phạm vi đã tìm ([`ADR-0023`](ADR-0023-chinh-sach-tuyen-bo-dau-tien.md) loại 2).
