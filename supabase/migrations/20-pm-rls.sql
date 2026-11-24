-- ---------------------------------------------------------------------------
-- pm/sql/20-pm-rls.sql — RLS + quyền ghi, áp dụng `docs/02` §4 cho schema `pm`
--
-- Nguyên tắc lấy NGUYÊN VĂN từ docs/02 §4:
--   "CẤM client ghi trực tiếp" — quyền ghi chỉ qua server/RPC.
--
-- Hệ quả ở đây: `anon` và `authenticated` chỉ ĐỌC. Không bảng `pm_*` nào cho
-- client ghi. Đây không phải mặc định an toàn tình cờ — nó là **lựa chọn**, và
-- `scripts/check_pm_supabase.py` đỏ nếu ai thêm một policy `INSERT`/`UPDATE`/
-- `DELETE` cho `anon`/`authenticated`.
--
-- VÌ SAO KHÔNG dùng `auth.uid()` ở đây: sổ dự án này là **nội bộ**, một người
-- (LXK) + một tác nhân (AGENT). Nó không phải bảng người chơi. Mô hình đúng là
-- "đọc công khai trong tổ chức, ghi qua service_role", không phải "mỗi người
-- thấy dòng của mình" — dán mô hình của docs/02 §4 (dữ liệu người chơi) vào đây
-- sẽ tạo cảm giác an toàn giả.
-- ---------------------------------------------------------------------------

alter table pm_people           enable row level security;
alter table pm_actions          enable row level security;
alter table pm_projects         enable row level security;
alter table pm_action_projects  enable row level security;
alter table pm_documents        enable row level security;
alter table pm_notes            enable row level security;
alter table pm_audit            enable row level security;

-- Chỉ đọc. `using (true)` ở đây là chấp nhận được vì dữ liệu này KHÔNG phải dữ
-- liệu người chơi: không PII, không ví, không điểm số. Nếu một ngày có PII, phải
-- thêm điều kiện và ghi lại lý do — không im lặng đổi `true` thành thứ khác.
create policy pm_people_read on pm_people
  for select to anon, authenticated using (true);
create policy pm_actions_read on pm_actions
  for select to anon, authenticated using (true);
create policy pm_projects_read on pm_projects
  for select to anon, authenticated using (true);
create policy pm_action_projects_read on pm_action_projects
  for select to anon, authenticated using (true);
create policy pm_documents_read on pm_documents
  for select to anon, authenticated using (true);
create policy pm_notes_read on pm_notes
  for select to anon, authenticated using (true);
create policy pm_audit_read on pm_audit
  for select to anon, authenticated using (true);

-- Nhật ký là APPEND-ONLY: không ai được sửa hay xoá, kể cả service_role.
revoke update, delete on pm_audit from public;

-- `service_role` cần ghi để chạy migration/kéo dữ liệu từ pm/*.json.
grant usage on schema public to service_role;
grant select, insert, update, delete on
  pm_people, pm_actions, pm_projects, pm_action_projects, pm_documents, pm_notes
  to service_role;
grant select, insert on pm_audit to service_role;
grant usage, select on sequence pm_audit_id_seq to service_role;

-- Chốt chặn cuối: kể cả khi ai cấp quyền rộng, client vẫn không ghi được.
revoke insert, update, delete, truncate on
  pm_people, pm_actions, pm_projects, pm_action_projects, pm_documents, pm_notes, pm_audit
  from anon, authenticated;
