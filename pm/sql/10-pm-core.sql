-- ---------------------------------------------------------------------------
-- pm/sql/10-pm-core.sql — lõi quản lý dự án Game9K trên Supabase (PostgreSQL 16)
--
-- Đây là NGUỒN CHUẨN. `supabase/migrations/*.sql` được sinh từ đây bằng
-- `scripts/gen_supabase_migrations.py`, và `scripts/check_pm_supabase.py` canh
-- ba thứ: (1) migration khớp nguồn, (2) RLS bật trên MỌI bảng, (3) không có
-- bảng nào cho phép client ghi (`docs/02` §4 — quyền ghi chỉ qua server/RPC).
--
-- Vì sao KHÔNG dùng schema của `v0-task-manager`:
--   repo đó là **fork, không có giấy phép** (`docs/43` §1). Luật của repo này
--   (docs/23 §1.2, docs/42) là: đọc để hiểu, viết lại từ đầu, ghi nguồn ý tưởng.
--   Ở đây học **ba ý tưởng**: người có múi giờ làm việc, tài liệu có `tags` +
--   `isStarred`, và `projects` như một thực thể riêng. Phần còn lại viết mới.
-- ---------------------------------------------------------------------------

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------- 1. người
-- Một dòng = một người hoặc một tác nhân (agent). `kind` tách NGƯỜI khỏi MÁY,
-- vì `pm/action-register.json` đã phân biệt `LXK` và `AGENT` (`owner_protocol`).
create table if not exists pm_people (
  id            uuid primary key default gen_random_uuid(),
  code          text not null unique,      -- 'LXK', 'AGENT' — khớp pm/*.json
  name          text not null,
  kind          text not null default 'human' check (kind in ('human', 'agent')),
  role          text not null default '',
  tz            text not null default 'Asia/Ho_Chi_Minh',
  work_start    time,
  work_end      time,
  created_at    timestamptz not null default now(),
  -- Giờ làm việc phải là một KHOẢNG, không phải hai giá trị rời.
  constraint pm_people_hours_pair check (
    (work_start is null and work_end is null) or (work_start is not null and work_end is not null)
  )
);
comment on table pm_people is
  'Người/tác nhân trong sổ quản lý. `code` khớp khoá trong pm/action-register.json và pm/claims-registry.json.';

-- ---------------------------------------------------------------- 2. việc
-- Sao từ `pm/action-register.json`. Cột nào có ở đó thì có ở đây.
create table if not exists pm_actions (
  id              text primary key,        -- 'P1'..'P8' — giữ nguyên mã, không tự sinh
  title           text not null,
  source_doc      text not null,
  why             text not null default '',
  owner_code      text not null references pm_people (code) on update cascade,
  agent_allowed   boolean not null default false,
  owner_reason    text not null default '',
  not_before      date,
  due             date not null,
  block_if_unmet  text not null check (block_if_unmet in ('revert', 'remove', 'accept')),
  block_note      text not null default '',
  evidence_req    text not null default '',
  status          text not null check (status in ('OPEN', 'DONE')),
  done_on         date,
  evidence        text,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  -- docs/37: DONE mà không có bằng chứng là một việc chưa xong.
  constraint pm_actions_done_needs_evidence check (
    status <> 'DONE' or (evidence is not null and btrim(evidence) <> '' and done_on is not null)
  ),
  -- docs/37 §3: không đóng sớm trước `not_before`.
  constraint pm_actions_done_after_not_before check (
    status <> 'DONE' or not_before is null or done_on >= not_before
  ),
  -- Hạn không được trước ngày bắt đầu.
  constraint pm_actions_due_after_not_before check (
    not_before is null or due >= not_before
  )
);
create index if not exists pm_actions_due_idx on pm_actions (status, due);
comment on table pm_actions is
  'Bản sao có ràng buộc của pm/action-register.json. pm/*.json vẫn là nguồn; bảng này là bản CHẶN được (docs/43 §4).';

-- ---------------------------------------------------------------- 3. dự án
-- Ý tưởng học từ `v0-task-manager/lib/people.ts` (team) và `app/projects`:
-- một thực thể riêng, không phải một nhãn trên việc.
create table if not exists pm_projects (
  id          uuid primary key default gen_random_uuid(),
  code        text not null unique,        -- 'S6', 'P6', 'docs-42'…
  name        text not null,
  track       text not null default 'product'
              check (track in ('product', 'docs', 'ci', 'growth', 'legal')),
  status      text not null default 'active'
              check (status in ('active', 'paused', 'done', 'dropped')),
  started_on  date,
  target_on   date,
  created_at  timestamptz not null default now()
);

create table if not exists pm_action_projects (
  action_id   text not null references pm_actions (id) on delete cascade,
  project_id  uuid not null references pm_projects (id) on delete cascade,
  primary key (action_id, project_id)
);

-- ---------------------------------------------------------------- 4. tài liệu
-- Học từ `v0-task-manager/lib/documents.ts`: `tags[]`, `isStarred`, `folder`.
-- Khác biệt quan trọng: `path` phải TRỎ TỚI một tệp thật trong repo — xem
-- `scripts/check_pm_supabase.py` (docs/43 §4.3).
create table if not exists pm_documents (
  id          uuid primary key default gen_random_uuid(),
  path        text not null unique,        -- 'docs/42-…md'
  title       text not null,
  folder      text not null default 'docs',
  tags        text[] not null default '{}',
  is_starred  boolean not null default false,
  status      text not null default 'living'
              check (status in ('living', 'frozen', 'superseded')),
  bytes       integer check (bytes is null or bytes >= 0),
  created_at  timestamptz not null default now()
);
create index if not exists pm_documents_tags_idx on pm_documents using gin (tags);

-- ---------------------------------------------------------------- 5. ghi chú
create table if not exists pm_notes (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid references pm_projects (id) on delete set null,
  action_id   text references pm_actions (id) on delete set null,
  author_code text not null references pm_people (code) on update cascade,
  body        text not null check (btrim(body) <> ''),
  created_at  timestamptz not null default now()
);
create index if not exists pm_notes_action_idx on pm_notes (action_id, created_at desc);

-- ---------------------------------------------------------------- 6. audit
-- `docs/02` §4: nhật ký chỉ được APPEND. Không UPDATE, không DELETE — kể cả
-- với `service_role`. Đây là bảng duy nhất trong repo cấm cả service_role sửa.
create table if not exists pm_audit (
  id          bigserial primary key,
  at          timestamptz not null default now(),
  actor_code  text not null default 'AGENT',
  table_name  text not null,
  row_pk      text not null,
  op          text not null check (op in ('insert', 'update', 'delete')),
  diff        jsonb not null default '{}'::jsonb
);
create index if not exists pm_audit_at_idx on pm_audit (at desc);

-- ---------------------------------------------------------------- 7. phụ thuộc
-- Học từ mẫu "WES" của FDE (docs/44 §2.2): *"Action Required: Need [Executive
-- Sponsor] to approve"*. Không có bảng này, một việc chờ NGƯỜI trông giống một
-- việc chờ MÁY — và `docs/37` không phân biệt được hai thứ đó.
--
-- Vì sao là BẢNG chứ không phải `blocked_by text[]`: một mảng tự trỏ vào bảng
-- cha **không có khoá ngoại**, nên database không chặn được `blocked_by` trỏ tới
-- một P-id không tồn tại. Bảng nối thì chặn được.
create table if not exists pm_action_deps (
  action_id   text not null references pm_actions (id) on delete cascade,
  blocked_by  text not null references pm_actions (id) on delete cascade,
  note        text not null default '',
  primary key (action_id, blocked_by),
  -- Tự chặn mình là vòng lặp độ dài 1.
  constraint pm_action_deps_no_self check (action_id <> blocked_by)
);

-- Ai phải HÀNH ĐỘNG, khác với ai SỞ HỮU. Một việc có thể chờ quyết định của LXK
-- trong khi owner là AGENT — chính xác là P9/P10/P11.
create table if not exists pm_action_stakeholders (
  action_id   text not null references pm_actions (id) on delete cascade,
  person_code text not null references pm_people (code) on update cascade,
  primary key (action_id, person_code)
);
