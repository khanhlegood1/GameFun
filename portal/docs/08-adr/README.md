# Architecture Decision Records

> AI-Agile: *"Every decision is an ADR."* Quyết định nằm ngoài repo (Slack, họp) **không tồn tại**.
> Mỗi ADR phải có người quyết có tên. ADR chưa ký = `Proposed` và **không** được dùng để justify code đã merge.

| # | Quyết định | Trạng thái | Ảnh hưởng |
|---|---|---|---|
| [0001](ADR-0001-modular-phase-loop.md) | Vòng lặp phase theo module, không tuyến tính | Accepted (chờ ký) | Quy trình |
| [0002](ADR-0002-four-programs.md) | 4 program Solana tách theo vòng đời tiền | Accepted (chờ ký) | On-chain |
| [0003](ADR-0003-non-custodial.md) | Non-custodial, server không giữ khoá | Accepted (chờ ký) | Bảo mật, pháp lý |
| [0004](ADR-0004-guest-first.md) | Guest-first, ví là opt-in | Accepted (chờ ký) | UX, tăng trưởng |
| [0005](ADR-0005-permissioned-launch.md) | Chỉ Silver+ được launch ở GA1 | Accepted (chờ ký) | Go-to-market |
| [0006](ADR-0006-token2022-extensions.md) | Token-2022: hook + permanent delegate (escrow) | Accepted (chờ ký) | On-chain |
| [0007](ADR-0007-program-upgrade-policy.md) | Multisig 4/7, timelock 48h, immutable 90 ngày | Accepted (chờ ký) | Bảo mật on-chain |
| [0008](ADR-0008-redis-streams.md) | Redis Streams thay Kafka | Accepted (chờ ký) | Hạ tầng |
| [0009](ADR-0009-clickhouse-olap.md) | ClickHouse cho raw event, PG cho tiền | Accepted (chờ ký) | Data |
| [0010](ADR-0010-rust-indexer.md) | Indexer bằng Rust | Accepted (chờ ký) | Hạ tầng |
| [0011](ADR-0011-legal-posture.md) | Lập trường pháp lý cho bond | **Proposed — blocking GA** | Pháp lý |
| [0012](ADR-0012-modular-monolith.md) | Modular monolith trước microservice | Accepted (chờ ký) | Kiến trúc |
| [0013](ADR-0013-single-region.md) | Single-region, RTO 30' | Accepted (chờ ký) | Vận hành |
| [0014](ADR-0014-chaos-testing.md) | Chaos thủ công trước GA | Accepted (chờ ký) | Vận hành |
| [0015](ADR-0015-opensource-stack.md) | Không fork portal open-source, tự viết core | Accepted (chờ ký) | Delivery, pháp lý |
| [0016](ADR-0016-license-compliance.md) | **Thay Redis→Valkey, MinIO→R2** | **Proposed — blocking S2** | Hạ tầng, pháp lý |
| [0017](ADR-0017-anchor-version.md) | **Nâng Anchor 0.30.1 → 0.32.x** | **Proposed — quyết trước S6** | On-chain |
| [0018](ADR-0018-document-drm-posture.md) | **Bảo vệ tài liệu: overlay watermark trước, pixel-burn sau** | **Proposed — chờ chủ dự án** | M11, chi phí, pháp lý |
| [0019](ADR-0019-portal-khong-fork.md) | Portal đóng góp mở: tự viết, không fork (loại Plane/OpenProject vì AGPL/GPL) | Accepted | Delivery, pháp lý |
| [0020](ADR-0020-backlog-single-source.md) | `backlog.md` là nguồn duy nhất; GitHub Issues + portal là bản chiếu một chiều, CI kiểm | Accepted | Quy trình, công cụ PM |
| [0021](ADR-0021-builddiff-toan-cuc.md) | `BuildDiff` dùng Jaccard toàn cục + vế `content_files_added`; **còn nghịch lý kích thước** | Accepted | On-chain, kinh tế |
| [0022](ADR-0022-the-loai-cong-bang.md) | Thể loại cổng bằng (genre matching) cho `GATE_TABLE` | Accepted | On-chain, kinh tế |
| [0023](ADR-0023-chinh-sach-tuyen-bo-dau-tien.md) | **Chính sách tuyên bố "đầu tiên":** ba loại `PROVEN`/`NO_COUNTEREXAMPLE`/`NEEDS_DATA`; CI chặn khẳng định thiếu bằng chứng | Proposed — chờ PO ký | Nội dung, pháp lý |
| [0024](ADR-0024-san-pham-loi-suat-tach-roi.md) | **Sản phẩm lợi suất là dòng riêng, tách hẳn launchpad** (R1 không chung kho tiền · R2 không chung điểm · R3 không chung quyền quản trị) | Proposed — chờ PO ký | Kiến trúc, pháp lý, KVU |
| [0025](ADR-0025-game9k-foundation-san-pham-loi-suat.md) | **Không dùng tên "Foundation" cho thực thể thương mại**; đề xuất phương án A (phân phối, không tự vận hành) | Proposed — chờ PO ký | Pháp lý, cấu trúc công ty |
| [0026](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) | ADR-0026 — `nccasia/agent-sdk` (PreAct) áp dụng vào quy trình Dev: **một phần, có điều kiện** | Proposed — chờ PO ký | — |
| [0027](ADR-0027-starter-kit-game-mau-dua-khung-long.md) | ADR-0027 — Game mẫu đầu tiên của Starter Kit: đua khủng long **tất định** | Proposed — chờ PO ký | — |
| [0028](ADR-0028-hoc-co-che-cham-tu-arena-open-source.md) | ADR-0028 — Học cơ chế chấm từ mã nguồn mở của Arena: **hai việc làm ngay, hai việc phải hỏi PO** | Proposed — chờ PO ký | — |
| [0029](ADR-0029-gemini-decisions-api-cho-gate.md) | ADR-0029 — Dùng Gemini Decisions API cho gate P0x: **một công cụ đọc, không phải người ký** | Proposed — chờ PO ký | — |
| [0030](ADR-0030-proactive-co-creator-cho-muc-con-mo.md) | ADR-0030 — Học `Proactive-Co-Creator`: biến mục còn mở thành **câu hỏi đóng** | Proposed — chờ PO ký | — |
| [0031](ADR-0031-portal-hien-thi-cau-hoi-mo.md) | ADR-0031 — Portal hiển thị câu hỏi mở: **sinh dữ liệu lúc build, chỉ đọc lúc chạy** | Proposed — chờ PO ký | — |
| [0032](ADR-0032-nhung-game-ngoai-vao-playground.md) | ADR-0032 — Nhúng game **ngoài** vào Playground: học từ xa, không chép một dòng | Proposed — chờ PO ký | — |
| [0033](ADR-0033-play-sdk-va-xsolla-sandbox.md) | **Play SDK giống TÊN Poki nhưng không giả vờ tương thích**; Xsolla Pay Station chỉ ở sandbox, cấm live theo REQ-M5-009 | Proposed — chờ PO ký | Kiến trúc, pháp lý |
| [0034](ADR-0034-ho-so-sandbox-cho-game-ben-thu-ba.md) | **Hồ sơ sandbox khai báo trước** cho game bên thứ ba: danh sách đóng, mặc định từ chối, `Permissions-Policy` tường minh (lấy nguyên tắc của e2b, không lấy mã) | Proposed — chờ PO ký | Kiến trúc, bảo mật |
| [0035](ADR-0035-openrouter-cho-decisions-api.md) | **OpenRouter là seam thứ hai, không phải quan toà:** cùng bộ primitive `noul`/`choice`/`score`, không chọn ngầm nhà cung cấp, không tự tick; `bandForScore` đọc phân bố (lệch 41,4% so cách vị trí trộn — **chưa biết cách nào đúng**) | Proposed — chờ PO ký | Kiến trúc |
| [0036](ADR-0036-hai-nguon-e2b-agent-va-contract.md) | **Hai nguồn e2b:** một chỗ meta SAI (bảng license CC BY-NC-SA không được CI bảo vệ), một chỗ contract THIẾU (3 route production ngoài `openapi.yaml`); không thêm agent | Proposed — chờ PO ký | Kiến trúc, nội dung |
| [0037](ADR-0037-awesome-ai-sdks-khong-co-license.md) | **`awesome-ai-sdks` KHÔNG CÓ LICENSE** (`license: null`) — ca khó hơn CC BY-NC-SA: không có gì để grep. Cùng lỗ hổng `license.yml` mà ADR-0036 §1 nêu | Proposed — chờ PO ký | Kiến trúc, nội dung |
| [0038](ADR-0038-openrouter-cho-game9k.md) | **OpenRouter cho Game9K (sản phẩm, không phải gate):** đọc bản nộp studio và gợi ý — **không duyệt, không đo chất lượng, không gửi mã nguồn**; `ai_cannot_approve` đã chặn sẵn và ADR này không sửa nó | Proposed — chờ PO ký | Kiến trúc, pháp lý |
| [0039](ADR-0039-hermes-agent-e2b-cho-quy-trinh-dev.md) | **Hermes Agent + `hermes-plugin-e2b` cho quy trình dev:** sandbox dùng một lần cho tác nhân sửa repo — **không** tự động hoá việc ký gate, **không** vào CI; plugin MIT nhưng 2 sao và bị chặn bởi **Q62a** | Proposed — chờ PO ký | Quy trình, bảo mật |
| [0040](ADR-0040-ban-truoc-theo-bac-va-tang-seniority.md) | **Bán trước theo bậc giá giảm dần** (đúng cơ chế, hở cách hoàn chênh lệch) + **tầng seniority** (chưa tồn tại — "4 Tranches" hiện là tranche escrow, không phải tranche quyền kinh tế); **hạ bốn mệnh đề "an toàn hơn trái phiếu quốc gia"** xuống `NO_COUNTEREXAMPLE`/`NEEDS_DATA` | Proposed — chờ PO ký | Kinh tế, pháp lý |
| [0041](ADR-0041-marble-race-va-ba-gioi-han-cua-no.md) | **Đua bi N người cho live** — đã cài lõi `marble.mjs` (2..256 viên, tất định, 25 test + 2 reverse-test); chướng ngại **chỉ làm chậm** (giữ INV-04); **từ chối** PK realtime (mất tất định ⇒ G1) | Proposed — phần lớn đã cài | Starter Kit, pháp lý |
| [0042](ADR-0042-v0-task-manager-va-supabase.md) | **Không áp** `v0-task-manager` (license `null` ở cả fork và gốc · **0 dữ liệu** — task là hằng số trong `useState` · **0 test**) và **không dùng Supabase** (đã loại ở ADR-0015 + 4 tệp). `portal/` **đã có** board Kanban + drawer + `issues`/`issue_events`/`branches` trong Postgres | Proposed — chờ PO ký | Kiến trúc, license |
| [0043](ADR-0043-hoc-tu-fde-roadmap.md) | **Học từ `Awesome-FDE-Roadmap`** (MIT — lần đầu dùng được): áp **eval nội bộ cho bộ phân loại** (chỗ trống thật — `test-strategy` §5 có 9 chỉ số, **0** về AI), **MVA 1 sprint**, **ai có thể chặn cổng**, **ADR này KHÔNG bao gồm**. Từ chối **Pairwise/AI-judge** (`ADR-0038` §5.2 cấm) và **stack GCP** | Proposed — chờ PO ký | Quy trình, eval |

## Cách thêm ADR

1. Copy [`_TEMPLATE.md`](_TEMPLATE.md) — **không** copy một ADR cũ. Mẫu bắt buộc bốn mục:
   `## 0. Trả lời ngắn`, mục **Điều ADR này KHÔNG bao gồm**, mục **Ranh giới trung thực**,
   và dòng `**Người quyết:**`. `scripts/check_adr_structure.py` đỏ nếu thiếu một trong bốn.
   (26 ADR viết trước 2026-11-18 được miễn — chúng ra đời trước khi có mẫu.)
2. Số tiếp theo, không tái sử dụng số đã xoá.
3. Trạng thái: `Proposed` → (review) → `Accepted` / `Rejected` → `Superseded by ADR-xxxx`.
4. Không sửa ADR đã `Accepted`; tạo ADR mới và supersede.
5. CI check: mỗi ADR phải được link từ ≥ 1 tài liệu khác (NFR-T-04).
