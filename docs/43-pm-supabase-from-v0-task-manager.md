# 43 — Sổ dự án Game9K trên Supabase, và vì sao không chép `v0-task-manager`

> **Tài liệu sống:** `docs/43-pm-supabase-from-v0-task-manager.md` — bản gốc ở đây.
> **Trạng thái:** `DONE` (vòng 44) · database **đã chạy**: project `game9k-pm`
> **Tiền đề:** `docs/02` §4 (RLS: *cấm client ghi trực tiếp*) · `docs/23` §1.2 (giấy phép) · `docs/37` (sổ việc)

---

## 0. Bốn dòng

Yêu cầu: *áp dụng source code từ `lexuankhanh1612/v0-task-manager` vào quản lý dự án Game9K, dùng Supabase cho database.*

Ba phát hiện, theo thứ tự quan trọng:

1. **Repo đó là fork và KHÔNG CÓ GIẤY PHÉP.** Theo luật đã áp dụng ở `docs/23` §1.2: *đọc để hiểu, viết lại từ đầu, ghi nguồn ý tưởng* — **không** chép một dòng.
2. **Repo đó không có backend.** 89 tệp, **0** tệp SQL/migration/supabase. Toàn bộ dữ liệu là **mảng hằng trong `lib/*.ts`**. Nên "dùng Supabase" là việc phải **làm mới**, không phải "nối vào có sẵn".
3. **`docs/02` §4 đã tuyên bố `supabase/migrations/*.sql` là nguồn schema — nhưng thư mục đó không tồn tại.** Câu đó đã sai trong repo này từ trước vòng này.

Đã làm: schema `pm` (7 bảng), RLS chỉ-đọc, seed sinh từ `pm/*.json`, **project Supabase thật đã chạy**, cộng cổng 23 để ba nguồn không lệch nhau.

---

## 1. `v0-task-manager` — đọc được gì, không được dùng gì

*(đọc trực tiếp qua GitHub API + `git clone`, 24/11/2026)*

| | |
|---|---|
| Fork của | `dilums/v0-task-manager` |
| Giấy phép | **Không có** (cả repo gốc cũng không) |
| Ngôn ngữ | TypeScript / Next.js App Router |
| Kích thước | `631` KB, `89` tệp (phần lớn là `components/ui/*` — shadcn) |
| Backend | **Không có.** Không SQL, không migration, không supabase, không API route |

**Ba ý tưởng dùng được** (học, rồi viết lại):

| Ý tưởng | Ở repo đó | Ở đây |
|---|---|---|
| Người có **múi giờ + giờ làm việc** như một khoảng | `Person.workingHours {start, end, timezone}` | `pm_people.tz`, `work_start`, `work_end` + ràng buộc *"phải là một khoảng"* |
| Tài liệu có `tags[]` + `isStarred` + `folder` | `Document` interface | `pm_documents.tags text[]` (GIN index), `is_starred`, `folder` |
| `projects` là **thực thể riêng**, không phải nhãn | `app/projects` | `pm_projects` + bảng nối `pm_action_projects` |

**Ba thứ từ chối:**

| | Vì sao |
|---|---|
| `app/dashboard`, `app/receipts` | **Trang rỗng** — `ReceiptsPage` chỉ in một câu giới thiệu. Không có logic để học |
| Dữ liệu mẫu (`Lily Grace`, avatar Cloudinary, `@company.com`) | Dữ liệu giả của người khác; đưa vào repo là vừa sai giấy phép vừa sai sự thật |
| Chép `components/ui/*` | shadcn/ui có giấy phép riêng — nhưng repo này **không** ghi giấy phép, nên đường hợp pháp là `npx shadcn init`, không phải copy từ đây |

> **Đây không phải khắt khe hình thức.** Một repo không có giấy phép nghĩa là **giữ toàn bộ quyền** — kể cả quyền kiện. `docs/23` §1.2 đã ghi đúng luật này cho `marble-race`; áp dụng cùng luật cho repo này là nhất quán, không phải đổi ý.

---

## 2. Schema `pm` — 7 bảng, và vì sao tách khỏi `docs/02`

`docs/02` mô tả **34 bảng** cho sản phẩm (game, phiên chơi, arena, token). Sổ dự án là **thứ khác**: nó quản lý *việc phải làm*, không quản lý *người chơi*.

Đặt nó vào `docs/02` sẽ làm sai mọi câu "34 bảng" trong README, whitepaper, deck — và cổng `check_agent_rules.py` đếm `CREATE TABLE` = `34` sẽ đỏ. Nên schema `pm` nằm ở **`pm/sql/`**, là nguồn riêng, có cổng riêng.

| Bảng | Vai trò | Ràng buộc đáng chú ý |
|---|---|---|
| `pm_people` | người **và** tác nhân (`kind ∈ human, agent`) | `work_start`/`work_end` phải cùng null hoặc cùng có |
| `pm_actions` | bản sao có ràng buộc của `pm/action-register.json` | **DONE ⇒ phải có `evidence` + `done_on`** |
| `pm_projects` | dự án (track, status) | `track ∈ product, docs, ci, growth, legal` |
| `pm_action_projects` | nối việc ↔ dự án | khoá chính ghép |
| `pm_documents` | tài liệu trong repo | `path` **unique**; `tags` có GIN index |
| `pm_notes` | ghi chú gắn việc/dự án | `body` không được rỗng |
| `pm_audit` | nhật ký append-only | **`revoke update, delete`** — kể cả `service_role` |

### 2.1. Ràng buộc quan trọng nhất: `DONE` phải có bằng chứng

`docs/37` nói: *"Không mục nào được chuyển sang DONE mà không có `evidence`"*. Trước vòng này, câu đó chỉ được `check_actions.py` canh **trong tệp JSON**. Nay nó là ràng buộc **trong database**:

```sql
constraint pm_actions_done_needs_evidence check (
  status <> 'DONE' or (evidence is not null and btrim(evidence) <> '' and done_on is not null)
)
```

Và nó **đã được thử phá trên database thật** (§4.2). Đây là khác biệt giữa *"chúng tôi có quy ước"* và *"database từ chối"*.

---

## 3. Đã chạy trên Supabase thật

| | |
|---|---|
| Project | `game9k-pm` |
| Ref | `illulsggtxlseywsuuyg` |
| Region | `ap-southeast-1` |
| Plan | `free` |
| Server | **PostgreSQL 17.12** |
| Migration đã chạy | `pm_core_schema_v1` · `pm_rls_readonly_v1` · `pm_seed_from_registers_v1` |

**Dữ liệu đã nạp:** `2` người (`LXK`, `AGENT`) · **`8` việc** (`5` OPEN, `3` DONE) — khớp `pm/action-register.json`.

> **Mật khẩu database đã được đặt trong phiên tạo project và KHÔNG ghi vào repo.** Repo này không chứa `.env`, không `service_role` key, không connection string — và `check_egress_lock.py` canh điều đó. Nếu cần lấy lại mật khẩu: Supabase Dashboard → Project Settings → Database → Reset.

---

## 4. Bằng chứng — đo, không tuyên bố

### 4.1. RLS: 7/7 bảng chỉ-đọc

Đo bằng `pg_class` + `has_table_privilege` trên project thật:

| Bảng | RLS | `anon` đọc | `anon` ghi | `auth` UPDATE | `auth` DELETE | policy ghi |
|---|---|---|---|---|---|---|
| `pm_people` | ✓ | ✓ | **✗** | **✗** | **✗** | **0** |
| `pm_actions` | ✓ | ✓ | **✗** | **✗** | **✗** | **0** |
| `pm_projects` | ✓ | ✓ | **✗** | **✗** | **✗** | **0** |
| `pm_action_projects` | ✓ | ✓ | **✗** | **✗** | **✗** | **0** |
| `pm_documents` | ✓ | ✓ | **✗** | **✗** | **✗** | **0** |
| `pm_notes` | ✓ | ✓ | **✗** | **✗** | **✗** | **0** |
| `pm_audit` | ✓ | ✓ | **✗** | **✗** | **✗** | **0** |

Đây là `docs/02` §4 (*"CẤM client ghi trực tiếp"*) áp cho schema `pm` — không phải mặc định an toàn tình cờ.

### 4.2. Năm phép phá, cả năm bị chặn

| Phép phá | Bị chặn bởi |
|---|---|
| `update … status='DONE', evidence=null` | `pm_actions_done_needs_evidence` |
| `update … status='DONE', done_on='2026-11-01'` (trước `not_before`) | `pm_actions_done_after_not_before` |
| `set role anon; insert into pm_actions` | privilege |
| `set role authenticated; update pm_actions` | privilege |
| `set role anon; delete from pm_audit` | privilege |

Sau cả năm, `P1` vẫn `OPEN` và `P3` vẫn `OPEN` — tức không phép phá nào **âm thầm thành công**.

---

## 5. Ba nguồn, một cổng — `check_pm_supabase.py`

Khi sổ nằm ở hai nơi (JSON trong repo và bảng trên Supabase), có ba cách lệch:

| Cách lệch | Ai phát hiện |
|---|---|
| Seed SQL lệch `pm/*.json` | bất biến 2 (so **tập `id`**, không so văn bản) |
| Migration bị sửa tay | bất biến 1 (so `sha256` với bản sinh lại) |
| Một policy ghi được thêm | bất biến 3 (`write_policies` phải `= 0`) |
| Ràng buộc `DONE ⇒ evidence` bị gỡ | bất biến 4 (phải có trong migration **và** có phép thử chứng minh chặn) |

Migration **sinh** từ `pm/*.json` bằng `gen_supabase_migrations.py`, không viết tay — vì seed viết tay sẽ lệch im lặng. Cùng lý do `supabase/migrations/SHA256` tồn tại.

> **Cổng chạy offline.** CI không gọi Supabase: không có key, không có mạng ra ngoài (`docs/30`). Nó so **ba tệp trong repo** đối chiếu nhau, và `supabase/VERIFY.json` ghi `ref` + `measured_at` để biết bằng chứng đo **ở đâu, ngày nào**.

---

## 6. Bốn câu hỏi

**"Sao không dùng thẳng repo đó rồi đổi sang Supabase?"** Vì repo đó **không có** lớp dữ liệu nào để đổi. Mọi thứ là mảng hằng trong `lib/*.ts`. Công việc thật là *thiết kế schema*, và thiết kế schema thì không chép được từ một repo không có schema.

**"Không có giấy phép thì có thật sự không dùng được?"** Dùng **ý tưởng** thì được — ý tưởng không có bản quyền. Dùng **mã** thì không. Ở đây tôi học ba ý tưởng ở §1 và viết lại toàn bộ SQL; không dòng TypeScript nào được chép.

**"Đưa sổ dự án lên cloud có làm nó công khai không?"** Policy đọc là `using (true)` cho `anon` — **có**, ai có `anon` key đều đọc được. Đó là **lựa chọn**, không phải sơ suất: sổ này không chứa PII, không chứa ví, không chứa điểm số; nó chứa *việc phải làm và hạn*. Nếu sau này có PII, phải thêm điều kiện **và ghi lý do** — không lặng lẽ đổi `true`.

**"Sao không cho client ghi để có giao diện kéo-thả?"** Vì `docs/02` §4 cấm, và vì ghi từ client nghĩa là mọi ràng buộc ở §2 phải tin vào client. Giao diện (nếu làm) gọi RPC/`service_role` qua server — đó là **W2**.

---

## 7. Chưa làm

| | Việc | Vì sao chưa |
|---|---|---|
| **W1** | Đồng bộ **hai chiều** `pm/*.json` ↔ Supabase | Hiện một chiều (JSON → SQL). Hai chiều cần quyết định *nguồn nào thắng khi lệch* — quyết định của người |
| **W2** | Giao diện (Next.js) — phần duy nhất repo kia thật sự có | Cần ghi giấy phép trước khi chép `components/ui/*`; hợp pháp là `shadcn init`, không copy |
| **W3** | Đưa `pm/claims-registry.json` (3 tuyên bố) vào bảng | Cần bảng `pm_claims` + ràng buộc `review_by` quá hạn ⇒ đỏ (docs/34 §4). Cùng khuôn, làm sau |
| **W4** | Xoay mật khẩu database + bật branching | Free plan không có branching; xoay mật khẩu là việc của người giữ project |

> **Điều đáng nhớ:** yêu cầu là "áp dụng source code", và phát hiện chặn đường là **repo đó không có mã để áp dụng** — không có backend, không có giấy phép. Nhưng phần *giá trị* của yêu cầu vẫn làm được: sổ dự án nay có schema thật, chạy trên PostgreSQL thật, và **database từ chối** việc đóng một mục mà không có bằng chứng.
