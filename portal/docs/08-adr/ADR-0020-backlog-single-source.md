# ADR-0020 — `backlog.md` là nguồn duy nhất; GitHub Issues và portal là bản chiếu

**Trạng thái:** Accepted  
**Ngày:** 2026-11-21  
**Người quyết:** Project Owner  
**Liên quan:** [ADR-0019](ADR-0019-portal-khong-fork.md), [ai-agile-adoption §1 Nguyên tắc 04](../00-framework/ai-agile-adoption.md), [backlog.md](../01-requirements/backlog.md), [roadmap.md](../07-delivery/roadmap.md)

---

## 1. Bối cảnh

[ai-agile-adoption §1 Nguyên tắc 04](../00-framework/ai-agile-adoption.md) đã chốt: **"Backlog = GitHub Issues (mirror từ `backlog.md`)"**. Thực tế repo làm ngược lại nguyên tắc này ở cả hai đầu:

| Nơi lưu | Nội dung | Trạng thái đo được (2026-11-21) |
|---|---|---|
| `docs/01-requirements/backlog.md` | 80 story · 10 epic · 290 điểm, 8 cột bắt buộc | **Đầy đủ**, có CI kiểm (`check_req_mapping`, `check_sprint_allocation`) |
| GitHub Issues | 0 issue (repo có bật Issues) | **Trống** — không ai mở, không ai dùng |
| `portal/lib/seed.mjs` | 10 issue chép tay vào SQLite | **Sai**: 7/10 ID (`MP-1008`, `MP-1009`, `MP-1101`…`MP-1105`) **không tồn tại trong backlog** |

Ba bản sao của cùng một tập story, và **hai bản sai**. Đây không phải vấn đề công cụ — thiếu Jira/Linear không gây ra lỗi này, thêm vào sẽ thành bản sao thứ tư.

### Vì sao không dùng công cụ PM ngoài

Cùng lý do [ADR-0019](ADR-0019-portal-khong-fork.md) đã loại fork Plane/OpenProject: thứ Game9K cần là **cổng Owner ánh xạ 1-1 từ tài liệu quy trình** và **luật "AI không bao giờ merge"** — không công cụ nào có sẵn. `OpenTimelineIO` (khảo sát 2026-11-20: C++, Apache-2.0, topics `film-editing`/`nle`/`vfx`) là định dạng trao đổi timeline dựng phim, **không liên quan** quản trị mã nguồn.

## 2. Quyết định

**`docs/01-requirements/backlog.md` là nguồn duy nhất. Mọi nơi khác là bản chiếu một chiều, CI kiểm tính khớp.**

```
backlog.md  ──(sinh)──►  portal/lib/backlog.generated.mjs  ──(import)──►  portal
     │
     └──(sync)──►  GitHub Issues
```

| Thành phần | Vai trò | Chiều |
|---|---|---|
| `scripts/backlog_source.mjs` | Bộ đọc duy nhất của `backlog.md` + `roadmap.md` | đọc |
| `scripts/build_backlog_manifest.mjs` | Sinh `portal/lib/backlog.generated.mjs` | `backlog.md` → portal |
| `scripts/sync_backlog_issues.mjs` | Tạo/cập nhật issue, khoá theo `[MP-xxxx]` trong tiêu đề | `backlog.md` → GitHub |
| `scripts/check_backlog_sync.py` | CI đỏ khi ba nơi lệch nhau | kiểm |

## 3. Vì sao đúng những lựa chọn này

**a. Không lưu state để tìm lại issue.** Tiêu đề issue mang `[MP-101]`. Chạy lại bao nhiêu lần cũng tìm được issue cũ mà không cần bảng ánh xạ — bảng ánh xạ là bản sao thứ tư và sẽ lệch.

**b. Không tự đóng issue.** Story bị xoá khỏi backlog ⇒ sync chỉ **cảnh báo**, người quyết định đóng. Tự đóng là hành động phá huỷ không thể hoàn tác bằng cách chạy lại.

**c. Không để seed đọc `backlog.md` lúc chạy.** `vercel.json` khai `includeFiles: "{portal/**,demo/docsend/**,package.json}"` — `docs/**` **không được đóng gói vào function**. `fs.readFileSync('docs/.../backlog.md')` trong seed sẽ chạy đúng ở local rồi crash trên production. Đây là loại lỗi tệ nhất: hỏng sau deploy, không hỏng trong test. Nên dùng bước sinh lúc build + commit kết quả, CI so byte.

**d. Bug và việc hạ tầng portal không mang khoá `MP-*`.** Seed cũ dùng `MP-1008`… cho bug và `MP-1101`… cho việc tự xây portal. Cả hai **không phải story sản phẩm**: bug nên là bug, và theo ADR-0019 portal tự xây nên không nằm trong backlog khách hàng. Nay chúng dùng khoá `WK-001`…`WK-007`.

**e. Sprint lấy từ `roadmap.md` §3b, không phải `backlog.md` §3.** Mục §3 của backlog là bảng **tóm tắt** dùng ký hiệu khoảng (`MP-101…108`) và bỏ sót 16 story; đọc nó sẽ báo sai "story không có sprint". §3b trong roadmap được `check_sprint_allocation.py` kiểm từng dòng và đối chiếu tổng điểm.

## 4. Hệ quả

**Được**
- Một story sửa ở một chỗ. Sửa `backlog.md` rồi chạy 2 lệnh là GitHub và portal khớp.
- Lệch trở thành lỗi CI, không phải phát hiện tình cờ. Đã bắt được ngay: dòng `Tổng` của roadmap ghi **81** trong khi các dòng cộng lại là **80**.
- Tìm được 7 ID ma trong seed mà trước đó portal vẫn hiển thị như thật.

**Mất / chấp nhận**
- Thêm một bước sinh (`node scripts/build_backlog_manifest.mjs`) mỗi khi sửa backlog. Quên ⇒ CI đỏ, không im lặng.
- `sync_backlog_issues.mjs` cần `gh` đã đăng nhập — không chạy được trong CI không có token. `check_backlog_sync.py --offline` bỏ qua tầng GitHub chứ không giả vờ đã kiểm.

**Giới hạn đã biết**
- Trạng thái thật của công việc (đang làm, đã xong) **không** nằm trong `backlog.md` — nó ở GitHub (issue state, PR). Sync chỉ đẩy *định nghĩa* story, không đẩy *trạng thái*. Một chiều là cố ý: nếu sync ghi ngược trạng thái vào `backlog.md` thì `backlog.md` hết là nguồn chuẩn.
- `check_backlog_sync.py` kiểm issue có tồn tại và tiêu đề khớp, **không** kiểm nội dung body khớp từng byte (body do sync sinh nên khớp theo cách xây dựng).

## 5. Phương án đã cân nhắc và loại

| Phương án | Vì sao loại |
|---|---|
| Thêm Linear/Jira | Bản sao thứ tư. Vấn đề là *ba bản sao*, không phải thiếu công cụ. |
| Chỉ dùng GitHub Issues, xoá `backlog.md` | Mất 6 trường DoR (persona, MoSCoW, BDD, screen, API) và toàn bộ CI hiện có; `backlog.md` còn là nguồn của `check_req_mapping`. |
| GitHub Issues là nguồn, sinh ngược ra `backlog.md` | Issue không giữ được bảng MoSCoW 8 cột, và `backlog.md` phải nằm trong git để review qua PR. |
| `OpenTimelineIO` | Định dạng timeline dựng phim (C++, Apache-2.0). Không có khái niệm branch/PR/issue/sprint. |
| Đồng bộ hai chiều | Vòng lặp xung đột không có trọng tài. Một chiều + CI kiểm là đủ và kiểm chứng được. |

## 6. Tự kiểm

| Câu hỏi | Trả lời | Bằng chứng |
|---|---|---|
| Có bản sao dữ liệu nào không được kiểm? | Không | `check_backlog_sync.py` 13/13: cấu trúc, manifest, seed, issue |
| Số công bố có kiểm chứng được? | Có | 80 story · 290 điểm, khớp `check_sprint_allocation.py` và roadmap §3b |
| Sync có thể phá dữ liệu? | Không | Chỉ tạo/sửa issue có marker `[MP-*]`; không xoá, không đóng |
| Portal còn hiển thị dữ liệu ma? | Không | Seed dẫn xuất từ manifest; khoá lạ ⇒ ném lỗi ngay lúc seed |
| Vi phạm Nguyên tắc 04? | Không | Đây là bản hiện thực của chính Nguyên tắc 04 |
