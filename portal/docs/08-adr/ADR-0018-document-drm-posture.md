# ADR-0018 · Mức bảo vệ tài liệu: overlay watermark trước, pixel-burn sau

| | |
|---|---|
| **Trạng thái** | Proposed — **chờ chủ dự án quyết** |
| **Ngày** | 2026-11-18 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 cho module M11 |
| **Người quyết** | Founder *(chờ ký)* |
| **Ảnh hưởng** | M11 Project Dossier, chi phí hạ tầng, UX đọc tài liệu |
| **Liên quan** | [PRD M11](../01-requirements/PRD-game9k.md#m11--project-dossier-hồ-sơ-dự-án) · [REQ-M11-007](../01-requirements/PRD-game9k.md#m11--project-dossier-hồ-sơ-dự-án) · [REQ-M11-013](../01-requirements/PRD-game9k.md#m11--project-dossier-hồ-sơ-dự-án) · [MP-W7](../01-requirements/backlog.md) · [threat-model](../06-nfr/threat-model.md) · [demo](../../demo/docsend/README.md) |

## Bối cảnh & vấn đề

Yêu cầu gốc: *"chia sẻ white paper như DocSend để bảo vệ khó bị copy hơn"*.

Cần một quyết định dứt khoát, vì hai lựa chọn khác nhau về **bản chất** — không phải hai mức của cùng một thứ:

| | A · Nhúng PDF gốc + overlay | B · Render trang thành ảnh, đốt watermark vào pixel |
|---|---|---|
| Trình duyệt nhận | **file PDF gốc** | ảnh từng trang |
| Watermark có trong file? | **không** — là lớp DOM phủ bên trên | **có** — nằm trong ảnh |
| Tải lậu (DevTools → Network) | dính **không** watermark | dính watermark |
| Screenshot | dính watermark | dính watermark |
| Copy chữ | được (text layer còn) | **không** |
| Screen reader / SEO | tốt | kém |
| Chi phí storage | 1× | ~8–15× (PNG/WebP mỗi trang, nhiều độ phân giải) |
| Chi phí CPU | 0 | render mỗi khi upload + mỗi độ phân giải |
| Độ trễ mở tài liệu | ~0 | 200–600ms trang đầu |

## Quyết định

**Giai đoạn 1 dùng A** (nhúng PDF gốc + overlay watermark), vì:

1. **Mục tiêu thật là truy vết, không phải chặn.** Chặn tuyệt đối không tồn tại trên web — DocSend cũng không chặn. Giá trị nằm ở: mỗi lượt xem có mã riêng, in lên mọi trang, và tra ngược được ra người mở. A làm được điều này với chi phí gần bằng 0.
2. **Đối tượng đọc là nhà đầu tư, không phải người lạ.** Rủi ro thật là "gửi cho quỹ X rồi deck xuất hiện ở quỹ Y", không phải "một người tải PDF rồi đọc một mình". A giải quyết đúng rủi ro đó.
3. **Copy chữ được là tính năng, không phải lỗ hổng.** Nhà đầu tư trích dẫn white paper là điều tốt. B phá vỡ việc này.
4. **Chi phí.** B tăng storage 8–15× cho một module chỉ có hàng chục tài liệu mỗi studio. Chưa đáng ở giai đoạn chưa có doanh thu.

**Chuyển sang B khi có một trong ba dấu hiệu** (ghi thành ngưỡng, không phải "khi cần"):

- ≥ 5 vụ rò rỉ đã xác định được nguồn, **và** bên nhận nói watermark đã bị cắt/xoá
- ≥ 1 nhà đầu tư từ chối ký NDA vì "tài liệu có thể tải về"
- Tài liệu có giá trị thương mại trực tiếp (bản thiết kế kỹ thuật cốt lõi, không phải white paper marketing)

## Hệ quả

**(+) với A**
- Không thêm hạ tầng, không thêm job render, không thêm chi phí đáng kể.
- Tài liệu vẫn tìm kiếm/trích dẫn/đọc bằng screen reader được.
- Watermark đổi được theo từng phiên mà không phải render lại.

**(−) với A — phải nói rõ với người dùng, không giấu**
- File PDF gốc vẫn tới trình duyệt. Người hiểu kỹ lấy được bản **không watermark**.
- Nói "chống copy" là nói sai. UI phải ghi đúng: *"mọi ảnh chụp đều truy được nguồn"*, không phải *"không thể copy"*.
- Nếu cần bằng chứng pháp lý "bản rò này từ ai", A chỉ chứng minh được khi bản rò là **ảnh chụp**, không phải khi là file gốc.

**(−) với B — lý do chưa chọn**
- Mất text layer ⇒ mất khả năng trích dẫn, giảm giá trị với nhà đầu tư đang làm due diligence.
- Render là pipeline mới phải vận hành: worker, storage lifecycle, cache, nhiều độ phân giải, retry. Đây là một module con, không phải một cấu hình.
- Ảnh vẫn bị OCR. B không chặn copy — chỉ làm copy **dính mã**. Về mặt mục tiêu, B không mạnh hơn A nhiều; khác biệt là ở **bản tải lậu có mã hay không**.

## Phương án bị loại

| Phương án | Lý do loại |
|---|---|
| **DRM kiểu Adobe (khoá file, cần client)** | Cần plugin/extension; không chạy trên mobile web; UX đọc tài liệu gọi vốn mà bắt cài plugin là tự sát |
| **Chặn chuột phải / chặn Ctrl+P / chặn F12** | Vô nghĩa về bảo mật (DevTools vẫn mở được), nhưng **làm hỏng UX thật**. Đã loại có chủ ý — đây là thứ nhiều sản phẩm Việt Nam làm và nó chỉ gây khó chịu |
| **Chỉ cho xem trong app, không cho web** | Trái định hướng web-first ([ADR-0004](ADR-0004-guest-first.md)) |
| **Mã hoá PDF bằng mật khẩu gửi qua kênh khác** | Thêm ma sát cho mọi người để chống một rủi ro hiếm; passcode của link đã đủ |

## Rủi ro còn lại

| Rủi ro | Mức | Theo dõi ở đâu |
|---|---|---|
| Người dùng hiểu sai "bảo vệ" thành "không copy được" | **Cao** | Câu chữ trong UI là một phần của REQ-M11-007, có test DOM kiểm |
| Bản rò là file gốc ⇒ watermark vô dụng | Trung bình | Chấp nhận; đổi sang B khi đạt ngưỡng ở trên |
| Email người xem bị lộ qua watermark khi ảnh lan ra ngoài | Trung bình | Đây là **mục đích**, nhưng phải nêu trong chính sách riêng tư: người xem cần biết email mình sẽ in lên tài liệu. Ghi ở [NFR-L](../06-nfr/nfr-spec.md) |
| Studio lạm dụng watermark để "đánh dấu" người xem ngoài mục đích | Thấp | Watermark chỉ chứa email + giờ + mã phiên, không cho tuỳ biến nội dung |

## Tài liệu tham chiếu

- [PRD M11](../01-requirements/PRD-game9k.md#m11--project-dossier-hồ-sơ-dự-án) — 13 yêu cầu
- [Demo chạy thật](../../demo/docsend/README.md) — 51 test, hiện thực phương án A
- [Screen specs SCR-33…37](../02-ux/screen-specs.md)
- [Threat model](../06-nfr/threat-model.md) — mục "Dossier"

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
