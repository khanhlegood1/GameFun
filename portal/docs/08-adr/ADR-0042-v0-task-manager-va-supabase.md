# ADR-0042 — Áp `v0-task-manager` vào quản lý dự án, và Supabase: **không** áp, **không** dùng

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0012`](ADR-0012-modular-monolith.md) · [`ADR-0015`](ADR-0015-opensource-stack.md) · [`ADR-0016`](ADR-0016-license-compliance.md) · [`docs/10-opensource`](../10-opensource/README.md) · [`dua-vit-tiktok`](../12-decisions/2026-11-22-dua-vit-tiktok-va-phan-loai-game.md) §4.1 · [`portal/`](../../portal/README.md)

> Bạn yêu cầu **hai** việc trong một câu: ① áp source code `v0-task-manager` vào quản lý dự án
> Game9K, ② dùng **Supabase** cho database. Hai việc đó **bị chặn bởi hai lý do khác nhau**, và
> việc thứ hai đã có quyết định từ trước. Tôi kiểm cả hai trước khi nói không.

---

## 0. Trả lời ngắn

| # | Yêu cầu | Kết quả |
|---|---|---|
| 1 | Áp **source code** `v0-task-manager` | 🔴 **Không áp được** — repo đó **không giấy phép**, **không có tầng dữ liệu**, và portal **đã có** chức năng tương đương |
| 1b | Học **thiết kế** của nó | 🟡 **Có, và đã có sẵn** — `portal/public/app.js` đã dùng đúng bố cục Kanban + drawer |
| 2 | Dùng **Supabase** cho database | 🔴 **Không** — đã bị loại ở `ADR-0015` dòng 142, và lặp lại ở 4 tệp khác |
| 3 | *"quản lý dự án cho Game9K"* — có thiếu gì thật không? | ✅ **Có**, nhưng thiếu **ba thứ khác** (§5), không phải giao diện |

---

## 1. Điều đầu tiên phải nói: repo đó **không có giấy phép**

Đo bằng GitHub API ngày 2026-11-18:

```bash
gh api repos/lexuankhanh1612/v0-task-manager --jq '.license'          # ⇒ null
gh api repos/dilums/v0-task-manager --jq '.license'                   # ⇒ null  (repo gốc)
gh api repos/lexuankhanh1612/v0-task-manager/git/trees/main?recursive=1 \
  | jq '.tree[]|select(.path|test("LICENSE|COPYING"))'                # ⇒ 0 kết quả
```

| Thuộc tính | Giá trị |
|---|---|
| Fork của | `dilums/v0-task-manager` |
| LICENSE (cả bản fork **và** bản gốc) | **`null`** — không có tệp LICENSE |
| Sao | 0 |
| Push cuối | 2026-02-20 (bản gốc cũng vậy) |
| Nguồn | Sinh tự động từ **v0.dev**, README tự ghi *"Automatically synced with your v0.dev deployments"* |

Theo luật bản quyền mặc định, **không có LICENSE = giữ toàn bộ quyền**. Đây **không** phải chuyện
thận trọng — `ADR-0016` và `docs/10-opensource/README.md` đã loại nhiều repo vì đúng lý do này
(`theshaneobrien/tickle`, `vamnguyen/tiktok-live-games`, `livecade/marble-race-*`,
`khanhlx6/TikTok-Chat-Reader`, `lm-sys/lm-sys.github.io`).

⇒ **Không chép một dòng nào.** Đây là cùng ranh giới `ADR-0027` §2 đã áp cho Starter Kit.

---

## 2. Điều thứ hai: repo đó **không có tầng dữ liệu** — nên câu "dùng Supabase cho database" không có gì để nối vào

Tôi tải toàn bộ tarball (`89 blob · 631 KB`) và grep:

| Tìm | Kết quả |
|---|---|
| `supabase` (không phân biệt hoa thường) | **0 tệp** |
| `fetch(`, `localStorage`, `axios`, `useSWR`, `@tanstack` | **0 kết quả** |
| thư mục `app/api/**` (API route của Next) | **0 tệp** |
| `@supabase/supabase-js` trong `package.json` | **không có** |
| Dữ liệu task nằm ở đâu | **Hằng số trong `useState`** — `const [tasks, setTasks] = useState<Task[]>({ "This Week": [...] })` |

Nghĩa là: **không có database để chuyển sang Supabase**. Toàn bộ task, people, documents là dữ liệu
mẫu viết cứng trong mã. Nếu áp repo này, việc "dùng Supabase" sẽ phải **xây mới từ đầu** — không
phải "áp dụng source code".

> **Nói thẳng:** hai nửa yêu cầu của bạn **không nối được với nhau**. Nửa ① là giao diện không có
> dữ liệu; nửa ② là database không có gì ghi vào.

---

## 3. Điều thứ ba: MetaPump **đã có** một trình quản lý công việc, và nó đang chạy

Đây là chỗ dễ bỏ qua nhất, và nó quyết định toàn bộ câu trả lời.

| Chức năng | `v0-task-manager` | `portal/` **đã có** |
|---|---|---|
| Kanban 4 cột | ✅ `This Week / In Progress / Done` | ✅ `Chờ làm · Đang làm · Chờ duyệt · Xong` (`app.js:335`) |
| Thẻ task + người phụ trách + badge | ✅ | ✅ `issueCard()` — badge AI/human, bug, gate, PR, có nhánh |
| Drawer chi tiết | ✅ | ✅ `openIssue()` + `#drawer` — có **acceptance**, prompt_ref, người duyệt |
| Bình luận / like | ✅ (đếm, không có nội dung) | ✅ **`issue_events`** — nhật ký thật, append-only |
| Gắn người | ✅ `people.ts` (hằng số) | ✅ `members` + `author_id` |
| Tài liệu | ✅ `documents/page.tsx` | ✅ `dossier` — **có watermark, share link, passkey** |
| **Gắn với mã nguồn** | ❌ | ✅ `POST /api/issues/:key/branch` · `/pr` · `/merge` — tạo nhánh và PR từ thẻ |
| **Gắn với cổng chất lượng** | ❌ | ✅ cột `gate` + `GET /api/issues/:key/handoff` |
| **Phân quyền** | ❌ | ✅ `portal/lib/policy.mjs` — `can(actor, action)` |
| **Lưu trong Postgres** | ❌ (hằng số) | ✅ `portal/lib/store.mjs` — `issues`, `issue_events`, `branches`, `gate_items`, `signoffs`, `sessions` |
| **Nhật ký kiểm toán** | ❌ | ✅ `issue_events` (append-only) + `audit_log` |
| Test | ❌ **0 tệp test** | ✅ `portal/test/` — **514 test, 514 pass** |

Nguồn: `portal/lib/store.mjs` dòng 5 ghi rõ *"members · issues · issue_events · branches · gates ·
gate_items · signoffs · sessions"*, và `portal/public/index.html` có 7 tab gồm `board`
(*"Việc & Bug"*), `gates`, `questions`, `dossier`, `play`, `access`.

⇒ Áp `v0-task-manager` nghĩa là **thay một thứ đang chạy, có test, có phân quyền, có lưu trữ** bằng
**một thứ không chạy dữ liệu, không test, không license**. Đó không phải nâng cấp.

### 3.1. Nhưng thiết kế của nó **đã được dùng** — và đây là phần ghi nhận

Bố cục Kanban + drawer chi tiết bên phải **đã là** bố cục của `portal/public/app.js` từ trước. Nếu
bạn thấy nó giống `v0-task-manager`, đó là vì **cùng một mẫu thiết kế phổ biến**, không phải vì
portal chép. Ghi ra để không ai đi tìm "đã chép ở đâu".

---

## 4. Supabase: **không** dùng — và câu này đã có từ trước, không phải tôi mới nghĩ

### 4.1. Đã bị loại ở **năm** chỗ, cùng một lý do

| Tệp | Câu |
|---|---|
| [`ADR-0015`](ADR-0015-opensource-stack.md) dòng 142 | *"Supabase — Dùng được nhưng **không cần**: đã có Postgres + NestJS + Prisma. Thêm = thêm một hệ auth song song"* |
| [`docs/10-opensource`](../10-opensource/README.md) dòng 39 | `supabase/supabase` 115.142 sao, Apache-2.0, **❌ Không cần** |
| Cùng tệp, dòng 273 | *"Thêm Supabase = 2 hệ auth, 2 nguồn user ID ⇒ **không bao giờ đối soát được**"* |
| [`dua-vit-tiktok`](../12-decisions/2026-11-22-dua-vit-tiktok-va-phan-loai-game.md) §4.1 | Kế hoạch trước dùng Supabase cho leaderboard ⇒ bị bác |
| [`doc-lai-bay-luat-va-danh-tinh`](../12-decisions/2026-11-22-doc-lai-bay-luat-va-danh-tinh.md) §5 | *"Supabase Realtime: tôi nhận ý, nhưng **không** nhận lý do"* |

### 4.2. Lý do kỹ thuật cụ thể, không phải "đã chốt rồi"

| Vấn đề | Chi tiết |
|---|---|
| **Hệ auth thứ hai** | Supabase phát JWT của chính nó. Portal đã có `auth_sessions` + `members` + `policy.mjs`. Hai nguồn `user_id` ⇒ mọi bảng có `author_id`/`actor_id` sẽ có hai loại giá trị, và **không có khoá ngoại nào ràng buộc được cả hai** |
| **Supabase là Postgres** | Nó **không thay** Postgres — nó bọc Postgres. `ADR-0012` và `c4-model.md` đã chốt **PostgreSQL 16** là nguồn sự thật về tiền, với luật bất biến: *"Postgres là sự thật về tiền; Solana là sự thật về token."* Dùng Supabase nghĩa là thêm một nhà cung cấp nằm **giữa** ứng dụng và sự thật đó |
| **RLS thay cho `policy.mjs`** | Supabase khuyến nghị Row Level Security. Portal có **`policy.mjs` với `can(actor, action)` đã được test**. Chuyển sang RLS = viết lại toàn bộ phân quyền bằng SQL, và **mất 514 test hiện có** |
| **Vercel** | `server.mjs` mở Postgres qua `DATABASE_URL` (dòng 165, 1964). Đổi sang Supabase = đổi chuỗi kết nối **và** thêm lớp auth — không phải "chỉ đổi DB" |
| **Chi phí** | Supabase free tier giới hạn 500 MB + pause sau 7 ngày không hoạt động. `schema.sql` có **45 bảng**; `play_events` trên ClickHouse là hàng triệu dòng. Không phù hợp |

### 4.3. Nếu điều bạn thật sự muốn là "**có database thật, không phải in-memory**"

Đây mới là nhu cầu có thể đúng, và nó **đã được giải**:

```bash
DATABASE_URL=postgres://… npm start        # portal dùng Postgres thật
PORTAL_FRESH=1 npm run start:pg            # in-memory PGlite cho dev
```

`portal/lib/store.mjs` dùng **cùng một dialect Postgres**, nên chạy PGlite (dev) và Postgres
(production) là **cùng một bộ SQL**. Không có gì cần Supabase để "có database".

⇒ **Q-ADR42-b**: nếu bạn đang gặp lỗi cụ thể khi nối Postgres (thiếu `DATABASE_URL`, Vercel không
giữ kết nối…), hãy nói triệu chứng. Đó là việc sửa được, và nó **không** cần Supabase.

---

## 5. "Quản lý dự án cho Game9K" — ba thứ **thật sự** thiếu, và không cái nào là giao diện

Đây là phần tôi đề nghị làm thay cho yêu cầu ban đầu, vì nó giải đúng vấn đề mà yêu cầu đó có lẽ
đang cố giải.

Tôi đã đọc **đủ** `CREATE TABLE issues` (`portal/lib/store.mjs:104`) để không đoán:

```
issue_key · type · title · body · acceptance · status · module · gate · area · labels
author_id · author_kind · assignee_id · points · ai_confidence · prompt_ref
branch · pr_url · pr_number · checks_green · reviewed_by · created_at · updated_at
```

⇒ **`assignee_id` và `points` ĐÃ CÓ.** Nên hai thứ tôi định báo thiếu thì **không** thiếu ở tầng dữ
liệu — chúng thiếu ở **tầng hiển thị**. Đây là phát hiện làm thay đổi cả ba mục dưới:

| # | Thiếu gì | Bằng chứng | Việc cần làm |
|---|---|---|---|
| **1** | **Có `assignee_id` nhưng board không lọc theo nó** | `app.js:329` filter chỉ có `kind/type/gate/q` | Thêm filter `assignee` — **thuần `app.js`, không cần đổi schema** |
| **2** | **Có `points` nhưng không hiển thị tiến độ theo điểm** | `issues.points` tồn tại; `build_backlog_manifest.mjs` sinh *"80 story · 290 điểm"*; tab `overview` không có tổng điểm | Thêm vào `overview` — đọc từ `BACKLOG` đã có sẵn ở `portal/lib/backlog.generated.mjs` |
| **3** | **Không có view theo sprint** | `issues` không có cột `sprint`; sprint nằm ở `docs/07-delivery/roadmap.md` | Nối `sprint` vào manifest rồi hiển thị — **thêm cột**, cần migration |

> Ba việc này **đều làm được trong `portal/`** hiện có, bằng `app.js` + route mới, **không cần**
> Next.js, không cần repo ngoài, không cần Supabase.

---

## 6. Điều tôi **không** làm, và vì sao

| Việc | Vì sao không |
|---|---|
| Chép mã từ `v0-task-manager` | **Không license** (§1). Kể cả nếu có, nó là Next.js 14 + 89 tệp + 38 thư viện Radix — trong khi portal là `node:http` thuần, `vercel.json` chỉ ship `{portal/**,demo/docsend/**,package.json}` |
| Thêm Next.js vào portal | `ADR-0012` chốt **modular monolith NestJS** cho API và `node:http` cho portal. Thêm Next = framework thứ ba, và `bundle.test.mjs` B-01 đã cho thấy rủi ro bundling của Vercel ở đây là **thật** |
| Đổi sang Supabase | §4 |
| Dựng một "app quản lý dự án" thứ hai | §3 — sẽ có **hai** nguồn sự thật về task, đúng loại lỗi `docs/10-opensource` dòng 273 cảnh báo (*"2 nguồn user ID ⇒ không bao giờ đối soát được"*) |

---

## 7. Năm câu cần PO quyết

| Mã | Câu hỏi |
|---|---|
| **Q-ADR42-a** | Bạn muốn **giao diện đẹp hơn** cho board hiện có, hay **một app quản lý dự án riêng**? Hai việc khác nhau hoàn toàn. Tôi đề nghị việc thứ nhất |
| **Q-ADR42-b** | Có lỗi cụ thể nào khi nối **Postgres** (`DATABASE_URL`) không? Nếu có, đó là việc sửa được và **không** cần Supabase |
| **Q-ADR42-c** | Có cần **sprint view + tiến độ theo điểm** (§5) không? Đây là ba thứ thật sự thiếu |
| **Q-ADR42-d** | Có cần **lọc theo người phụ trách** (`assignee_id`)? Cột **đã có** trong bảng, chỉ thiếu nút lọc ở board — việc nhỏ, thuần `app.js` |
| **Q-ADR42-e** | Nếu vẫn muốn dùng `v0-task-manager`: bạn có **quyền tác giả** với repo đó không (bạn tạo nó từ v0.dev)? Nếu **có** và **bạn** là chủ, thì có thể cấp license cho chính repo này rồi ta bàn tiếp — nhưng repo gốc `dilums/v0-task-manager` vẫn `null` |

### 7.1. Về Q-ADR42-e — đây là câu duy nhất có thể mở đường

Repo là **fork** của `dilums/v0-task-manager` (license `null`). Nhưng nếu bạn **tự** tạo nội dung đó
trong v0.dev (README ghi *"started with this design from dribbble"* + *"Built with v0.dev"*), thì:

- **Thiết kế** (bố cục, màu) **không** được bảo hộ như mã nguồn — dùng làm **tham khảo** thì được.
- **Mã** vẫn thuộc về người đã viết nó trong phiên v0.dev, trừ khi bạn là người tạo phiên đó.
- Trong **mọi** trường hợp: tôi **không** chép mã. Tôi có thể **viết lại từ đầu** một giao diện
  board tốt hơn, dựa trên mô tả — như `ADR-0027` §2 đã chọn cho Starter Kit.

---

## 8. Ranh giới trung thực

- **Không** nói "repo đó dở". Nó là một **bản demo giao diện** tốt cho mục đích của nó (v0.dev
  showcase). Nó **không** được thiết kế để làm quản lý dự án thật — không dữ liệu, không test.
- **Đính chính trong chính ADR này:** bản nháp đầu của §5 ghi *"`issues` không có `estimate`"* và
  *"cần đọc đủ cột để xác nhận"*. Đã đọc: **`assignee_id` và `points` đều có**. Tôi suýt báo thiếu
  một thứ đang tồn tại — đúng loại lỗi `AGENTS.md` luật thứ tư cấm. Đã sửa §5 thay vì để nguyên.
- **Không** nói Supabase "không an toàn". Nó an toàn. Nó chỉ **không cần ở đây**, và lý do là
  kiến trúc (`ADR-0015`), không phải chất lượng.
- **Không** dùng chữ "tốt nhất" / "duy nhất" cho bất kỳ lựa chọn nào. `ADR-0023` loại 2.
- **Không có dòng mã nào trong ADR này.** Nó là một câu trả lời, không phải một tính năng.
