# ADR-0019 — Portal đóng góp mở: tự viết, không fork

**Trạng thái:** Accepted  
**Ngày:** 2026-11-19  
**Người quyết:** Project Owner  
**Liên quan:** [ADR-0015](ADR-0015-opensource-stack.md), [ADR-0016](ADR-0016-license-compliance.md), [docs/10-opensource/README.md](../10-opensource/README.md), [docs/portal/README.md](../portal/README.md)

---

## 1. Bối cảnh

Game9K cần một cửa cho người đóng góp bên ngoài (dev, AI agent, đối tác) nộp việc và nhận việc, gắn với quy trình AI-Agile đã chốt ở [docs/00-framework/ai-agile-adoption.md](../00-framework/ai-agile-adoption.md). Có hai cách làm:

1. **Fork một portal mã nguồn mở** (Plane, Huly, OpenProject, Taiga…) rồi tuỳ biến.
2. **Tự viết phần lõi**, chỉ dùng thư viện chuẩn của Node.

Đội đã khảo sát 9 dự án mã nguồn mở. Kết quả license là yếu tố quyết định, không phải số sao.

## 2. Dữ liệu license — kiểm bằng GitHub API, không theo lời giới thiệu

Số liệu lấy trực tiếp từ `api.github.com/repos/{owner}/{repo}` ngày **2026-11-19**. Script `scripts/audit-opensource.sh` chạy lại được bất cứ lúc nào.

| Dự án | License (SPDX) | ★ | Dùng được? |
|---|---|---:|---|
| `makeplane/plane` | **AGPL-3.0** | 62.748 | ❌ |
| `nocodb/nocodb` | **NOASSERTION** | 65.573 | ❌ |
| `hcengineering/platform` (Huly) | EPL-2.0 | 28.144 | ⚠️ |
| `opf/openproject` | **GPL-3.0** | 17.533 | ❌ |
| `apitable/apitable` | **AGPL-3.0** | 15.672 | ❌ |
| `kanboard/kanboard` | MIT | 9.968 | ✅ |
| `usekaneo/kaneo` | MIT | 9.839 | ✅ |
| `RedPlanetHQ/tegon` | **AGPL-3.0** · *archived* | 1.908 | ❌ |
| `taigaio/taiga-back` | MPL-2.0 | 858 | ⚠️ |

## 3. Quyết định

**Tự viết `portal/`, zero dependency, không sao chép mã từ bất kỳ dự án nào ở trên.**

Lý do, theo thứ tự quan trọng:

1. **AGPL/GPL không hợp với mô hình vận hành.** Game9K chạy portal như một dịch vụ mạng. Dùng AGPL-3.0 nghĩa là nghĩa vụ mở toàn bộ mã nguồn cho người dùng dịch vụ — kể cả phần không liên quan. Đây đúng là lý do ADR-0016 đã loại Redis, MinIO, Grafana. Không thể áp dụng luật đó cho hạ tầng rồi phá luật đó cho portal.
2. **Điều cần nhất lại là phần dự án khác không có.** Thứ Game9K cần không phải bảng Kanban — Kanban nào cũng có. Cần **cổng chặn của Project Owner ánh xạ 1-1 từ một tài liệu quy trình cụ thể** (§4 của framework), và **luật "AI không bao giờ merge"** kiểm ở tầng hàm. Không portal nào có sẵn hai thứ đó; fork về rồi vẫn phải viết lại toàn bộ tầng quyết định.
3. **Bề mặt tấn công.** Portal này cấp quyền tạo nhánh và PR trên repo thật. Một hệ 200 nghìn dòng với hàng trăm dependency là bề mặt không kiểm soát nổi cho một đội nhỏ. `portal/` hiện tại: **0 dependency ngoài thư viện chuẩn Node**, toàn bộ tầng quyết định quyền là hàm thuần, test được từng nhánh.
4. **Không phải nguồn sự thật thứ hai.** Nguyên tắc 04 của framework: GitHub là nguồn duy nhất. Portal là lớp đọc và điều phối, không lưu bản sao lâu dài. Fork một portal đầy đủ sẽ khuyến khích làm ngược lại.

## 4. Cái gì học từ đâu (ý tưởng, không phải mã)

Ghi rõ để sau này không ai nghi ngờ đạo văn:

| Ý tưởng | Học từ | Cách hiện thực |
|---|---|---|
| Bảng Kanban theo trạng thái, thẻ có nhãn | Kaneo (MIT), Kanboard (MIT) | Tự viết HTML/CSS, không copy |
| Nhãn `good first issue` cho người mới | Quy ước GitHub chung | Trường `labels` + bộ lọc |
| Checklist có nguồn, có bằng chứng | Không của dự án nào — lấy từ chính §4 framework | `portal/lib/gates.mjs` |
| Cổng duyệt bắt buộc trước khi merge | GitHub branch protection | `can()` trong `portal/lib/policy.mjs` |
| Mô hình quyền theo vai trò | RBAC nói chung | 5 vai trò + ràng buộc `kind`, không superuser |

## 5. Hệ quả

**Được:**
- Không nghĩa vụ license nào. Portal dùng nội bộ và có thể mở một phần tuỳ ý.
- Tầng quyền test được 100% bằng hàm thuần — hiện có 54 test cho riêng phần này.
- Cài đặt = `node portal/server.mjs`. Không build, không `npm install`, không Docker.

**Mất:**
- Không có tính năng "miễn phí" như sprint burndown, time tracking, Gantt. Nếu cần, đó là việc mới có ID riêng.
- Phải tự làm mọi thứ về sau: thông báo email, tìm kiếm toàn văn, đính kèm tệp.
- Không có cộng đồng upstream vá lỗi giúp.

**Giới hạn đã biết (không giấu):**
- Đăng nhập hiện là chọn thành viên (demo). Production phải là GitHub OAuth + kiểm tra thành viên tổ chức. Đã ghi ở `portal/server.mjs`.
- Portal **không merge PR** và **không nhận token GitHub từ trình duyệt**. Token chỉ nằm trong biến môi trường server, và việc ghi ra GitHub thật phải bật rõ ràng bằng `PORTAL_GITHUB=live`.

## 6. Phương án đã cân nhắc và loại

| Phương án | Vì sao loại |
|---|---|
| Fork Plane | AGPL-3.0. Xung đột trực tiếp ADR-0016. |
| Fork OpenProject | GPL-3.0 + Ruby/Rails, không khớp stack Node. |
| Fork Kanboard | MIT nên hợp pháp, nhưng PHP; và vẫn phải viết lại toàn bộ tầng cổng/Owner. |
| Fork Huly | EPL-2.0 (yếu hơn AGPL nhưng vẫn có nghĩa vụ), 28k★, nặng. |
| Dùng GitHub Projects + Actions | Không có cổng Owner có cấu trúc, không có checklist đọc từ tài liệu, không phù hợp người xem không đọc code. |
| Không làm portal, chỉ dùng GitHub Issues | Đúng tinh thần "GitHub là nguồn duy nhất", nhưng nhà đầu tư/business user không đọc được tiến độ. **Đây vẫn là fallback hợp lệ** nếu portal hỏng. |

---

## 7. Tự kiểm

| Câu hỏi | Trả lời | Bằng chứng |
|---|---|---|
| Có dòng mã nào copy từ dự án AGPL/GPL? | Không | Toàn bộ `portal/` viết mới; không có dependency ngoài stdlib |
| License portal là gì? | Theo repo (xem `LICENSE` gốc) | — |
| Ai chịu trách nhiệm nếu sau này có người copy mã AGPL vào? | Maintainer, qua review | `check_portal_gates.py` + review PR bắt buộc |
| Portal có phá Nguyên tắc 04 (GitHub là nguồn duy nhất)? | Không — DB là cache, mọi artifact thật nằm ở GitHub | `portal/lib/github.mjs` tạo nhánh/PR thật khi bật live |
