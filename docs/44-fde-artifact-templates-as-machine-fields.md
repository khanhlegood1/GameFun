# 44 — Bốn mẫu bàn giao của FDE, và cái nào chuyển được sang Game9K

> **Tài liệu sống:** `docs/44-fde-artifact-templates-as-machine-fields.md` — bản gốc ở đây.
> **Trạng thái:** `DONE` (vòng 32) · database **đã chạy**: 9 bảng, 12 việc, 4 phụ thuộc
> **Tiền đề:** `docs/37` (sổ việc) · `docs/41` §7 (quyết định R1–R4 **mồ côi**) · `docs/43` (schema `pm`) · `docs/23` §1.2 (giấy phép)
> **Nguồn:** [`xuankhanh1612/Awesome-FDE-Roadmap`](https://github.com/xuankhanh1612/Awesome-FDE-Roadmap) — **MIT**, fork của [`pierpaolo28/Awesome-FDE-Roadmap`](https://github.com/pierpaolo28/Awesome-FDE-Roadmap)

---

## 0. Bốn dòng

Yêu cầu: *áp dụng `Awesome-FDE-Roadmap` vào quản lý dự án Game9K.*

1. **Nguồn này CÓ giấy phép MIT** — khác hoàn toàn `v0-task-manager` của `docs/43` (không có giấy phép). Nên lần này **chép được**. Nhưng nó là **lộ trình học nghề Forward Deployed Engineer**, không phải hệ thống quản lý dự án.
2. **Một nửa nội dung không chuyển được.** VPC Service Controls, GKE Workload Identity, BigQuery partitioning, Terraform, ADK, RAG, triển khai air-gapped — Game9K là cổng game HTML5 Web2-first trên Solana, **không có** thành phần nào tương ứng. Chép vào là tự tạo việc dự án không có.
3. **Phần chuyển được là bốn MẪU BÀN GIAO** ở §"Artifact Templates", và chúng chỉ có giá trị khi biến thành **trường kiểm được bằng máy** — không phải văn xuôi đẹp.
4. **Áp dụng nó lập tức lộ ra một lỗ thật:** `docs/41` §7 có bốn quyết định `R1–R4` giao cho `LXK`, và **cả bốn đều không có mã việc** trong `pm/action-register.json`. Quyết định nằm trong văn xuôi = quyết định không có hạn. Đã đóng bằng P8–P11 và cổng 24.

---

## 1. Nguồn: đọc được gì, kiểm được gì

*(GitHub API + `git clone --depth 1`, 18/11/2026)*

| | |
|---|---|
| Fork của | `pierpaolo28/Awesome-FDE-Roadmap` |
| Giấy phép | **MIT** (`LICENSE` ở gốc) — chép được, phải mang theo thông báo |
| Kích thước | `156` KB · `30` mục trong cây · `README.md` **55 KB** |
| Ngôn ngữ | JavaScript (Vite) — nhưng `web/` chỉ là **trình xem lộ trình** |
| Sao | `0` |

**Cấu trúc thật** (không phải như tên gọi gợi ý): bảng so sánh chân dung SWE vs FDE → ba giai đoạn học (kỹ thuật dữ liệu / GCP / tư vấn) → ADK đa tác nhân → blueprint RAG → triển khai air-gapped → "soft stack" → sổ tay phỏng vấn → **bốn mẫu bàn giao** → danh sách đọc (DDIA, Pyramid Principle, Trusted Advisor) → từ điển thuật ngữ.

Đó là **giáo trình**. Không có bảng, không có trạng thái, không có hạn, không có cột người chịu trách nhiệm. Nói cách khác: nó **không phải** một hệ quản lý dự án, và cũng không có ý định là một.

### 1.1. Vị trí giấy phép

`docs/23` §1.2 đặt luật: *không có giấy phép ⇒ đọc để hiểu, viết lại, ghi nguồn; có giấy phép ⇒ dùng được nhưng thông báo phải đi cùng.* Nguồn này **có** MIT, nên về nguyên tắc chép được.

Đường đã chọn vẫn là **viết lại + ghi nguồn**, vì hai lý do cụ thể:

- Bốn mẫu đó chỉ khoảng **400 từ cấu trúc** — chép nguyên văn tiếng Anh vào một tài liệu tiếng Việt còn tốn công hơn viết lại.
- Chép nguyên văn đòi hỏi phải nhúng toàn bộ khối MIT notice của **cả hai** tác giả vào mọi tệp có nó. Viết lại thì chỉ cần một dòng ghi nguồn — đúng như dòng ở đầu tài liệu này.

**Không có một câu nào trong tài liệu này là bản dịch nguyên văn.** Cấu trúc thì học; chữ thì của Game9K.

### 1.2. Vì sao không dùng `web/` làm giao diện quản lý

`web/src/data/course.js` là **68 KB văn xuôi giáo trình** trong một mảng hằng. Đó không phải mô hình dữ liệu — nó là nội dung. `docs/43` §7 W2 đã hoãn giao diện thật sau một quyết định giấy phép; một trình xem lộ trình không thay đổi quyết định đó, và nó không đọc được `pm/*.json`.

---

## 2. Bốn mẫu — và cái gì chuyển được

### 2.1. Bảng đối chiếu

| Mẫu trong nguồn | Chuyển được? | Ở Game9K thành cái gì |
|---|---|---|
| **Site Survey** — ngày, người dẫn, "bối cảnh dữ liệu", ràng buộc, **"The Delta"** (khoảng cách giữa hiện tại và mong muốn), quick win tuần 2 | **Có** | `docs/44` §3.1 — "The Delta" chính là thứ `docs/37` gọi là **mâu thuẫn**; đã có `find_contradictions.py` |
| **Technical Scoping** — mục tiêu, **Definition of Success = evals** (Hit Rate >90%, độ trễ <5 s, 0% ảo giác), lộ trình MVP→Scale, **Out of Scope** | **Có, một nửa** | `docs/34` (tuyên bố có người + hạn) đã làm "định nghĩa thành công". Phần **Out of Scope** thì chưa ai canh — xem §3.2 |
| **Sơ đồ triển khai Mermaid** | **Không** | Game9K đã có `docs/02` ERD + sơ đồ trong whitepaper; thêm một sơ đồ GCP là bịa hạ tầng |
| **Weekly Executive Summary** — giá trị đã giao (**Metric Move**), rủi ro & chặn, và **"Action Required: Need [Executive Sponsor Name] to approve ticket #12345"**, tầm nhìn "Day 30" | **Có, và đây là mẫu quan trọng nhất** | `pm/action-register.json` **thiếu đúng hai trường**: `blocked_by` (chờ việc nào) và `stakeholder` (chờ **ai**). §3.3 |

### 2.2. Vì sao mẫu thứ tư mới là mẫu đáng giá

Ba mẫu đầu mô tả **công việc**. Mẫu thứ tư mô tả **thứ làm công việc dừng lại**. Và dòng `Action Required: Need [Sponsor] to approve ticket #12345` nói một điều mà sổ việc của Game9K không nói được: **một việc chờ MÁY và một việc chờ NGƯỜI trông giống hệt nhau.**

Đó chính xác là lỗ đã tìm thấy. Xem §3.3.

### 2.3. Cái gì bị từ chối, và vì sao (ghi tường minh)

| Nội dung nguồn | Vì sao không áp dụng |
|---|---|
| Medallion bronze/silver/gold, circuit breakers, Airflow | Game9K không có pipeline dữ liệu; nguồn dữ liệu là `pm/*.json` + `docs/*.md` + SQLite cục bộ |
| Shared VPC, IAP, GKE Workload Identity, **VPC Service Controls**, Terraform | Không có hạ tầng GCP. Cổng CI là GitHub Actions, máy chủ là static hosting |
| BigQuery partitioning, clustering | Không có kho dữ liệu. Sổ dự án là Postgres 17 trên Supabase (`docs/43`) |
| ADK đa tác nhân, blueprint RAG, vector store | `docs/30` đã từ chối LLM trong đường CI vì cổng phải tất định và offline. Thêm RAG là mở lại quyết định đó mà không có lý do |
| Triển khai air-gapped | Sản phẩm là web công khai; "air-gapped" không có nghĩa ở đây |
| Sổ tay phỏng vấn, danh sách đọc, từ điển | Nội dung học tập, không phải quy trình. Không có chỗ trong repo tài liệu kỹ thuật |
| `web/` (Vite viewer) | Xem §1.2 |

---

## 3. Bốn mẫu, thành trường kiểm được

### 3.1. "The Delta" — đã có, gọi tên khác

Mẫu Site Survey hỏi: *hiện tại là gì, mong muốn là gì, khoảng cách nằm ở đâu?* Repo này đã trả lời câu đó bằng `scripts/find_contradictions.py`: **7486** chỗ trong **47** tệp mà hai câu nói hai điều khác nhau. Không cần thêm gì.

Điều đáng giữ từ mẫu là **dòng "Quick win tuần 2"**: một việc nhỏ, xong trong 2 tuần, chứng minh hướng đi. Ở đây nó tương đương khái niệm `block_if_unmet` của `docs/37` — nhưng ngược chiều. Không thêm trường mới; ghi nhận là **đã có tương đương**.

### 3.2. "Out of Scope" — chưa ai canh, và đây là nợ thật

Mẫu Technical Scoping có một mục mà repo này **không có**: danh sách thứ **cố ý không làm**. Repo có 25 bảng "từ chối" (`R*`) rải khắp `docs/13`–`docs/37`, nhưng chúng nằm trong văn xuôi và **không cổng nào đọc**.

Cổng 24 dưới đây làm được một nửa: nó **bắt buộc mọi bảng `R*` phải được khai báo tường minh** là "bảng quyết định" hoặc "bảng từ chối". Nhờ vậy một tài liệu mới có bảng `R*` mà không khai báo sẽ **làm đỏ CI** — thay vì lặng lẽ trôi.

Phần chưa làm: đối chiếu nội dung "từ chối" với việc đang mở (ví dụ: nếu `docs/30` từ chối LLM trong cổng, nhưng `pm/action-register.json` lại có việc "thêm LLM vào cổng" thì phải đỏ). Đó là **W3** ở §6.

### 3.3. Weekly Executive Summary — lỗ thật, và cách đóng

**Phát hiện.** `pm/action-register.json` trước vòng này có 8 việc, mỗi việc có `owner`, `due`, `status`, `evidence`. Nhìn vào thì **mọi việc đều ổn**: ai cũng có người, việc nào cũng có hạn, và không có gì đỏ.

Nhưng sổ đó **không diễn đạt được** câu: *"P1 không thể bắt đầu cho tới khi P8 được quyết."* Và càng không diễn đạt được: *"P8 phải do LXK quyết, không phải agent."* Hệ quả: **một dự án đình trệ và một dự án đang chạy nhìn giống hệt nhau.**

**Cách đóng — hai trường, không phải một:**

| Trường | Nghĩa | Ví dụ |
|---|---|---|
| `blocked_by` | chờ **việc nào** | `P9` chờ `P8` |
| `blocked_by_note` | vì sao chờ | "Không tách được trước khi P8 chọn thứ tự sản phẩm" |
| `stakeholder` | chờ **ai đồng ý** | `P10` do `AGENT` làm, nhưng `stakeholder` là `AGENT`; `P9` do `LXK` |

Hai trường này **khác nhau về bản chất**: `owner` là người *làm*, `stakeholder` là người *phải đồng ý*. P10 là ví dụ rõ nhất — agent viết cổng, nhưng cổng đó chỉ có nghĩa sau khi P9 (do LXK quyết) tách hai sản phẩm.

**Và nó không chỉ là JSON.** Trong database:

```sql
create table pm_action_deps (
  action_id  text not null references pm_actions (id) on delete cascade,
  blocked_by text not null references pm_actions (id) on delete cascade,
  ...
  constraint pm_action_deps_no_self check (action_id <> blocked_by)
);
```

Vì sao là **bảng** chứ không phải `blocked_by text[]` trên `pm_actions`: một mảng tự trỏ vào bảng cha **không có khoá ngoại**, nên Postgres không chặn được `blocked_by = 'P999'`. Bảng nối thì chặn được — và đã chặn thật (§4.2).

### 3.4. "Metric Move" — bằng chứng phải khớp sổ

WES kể *"giá trị đã giao"* kèm một con số đã dịch chuyển. Ở đây hình thức tương đương là `evidence` của một việc `DONE` — nhưng `docs/43` chỉ kiểm rằng **có** evidence, không kiểm rằng nó **đúng**.

Thêm `seed_fingerprint` vào `supabase/VERIFY.json`: md5(title) + `due` + `status` của **từng** dòng `pm_actions`, **đo** bằng `select md5(title)` trên database thật. Cổng 23 đối chiếu nó với `pm/action-register.json`.

Lần chạy đầu tiên, nó **bắt được hai lỗi thật** (P5 và P6: `due` trong DB đã cũ so với sổ). Không phải lỗi giả định — lỗi có thật, sinh ra từ chính vòng này.

---

## 4. Bằng chứng — đo, không tuyên bố

### 4.1. Database sau migration thứ tư

| | |
|---|---|
| Project | `game9k-pm` · ref `illulsggtxlseywsuuyg` · `ap-southeast-1` · PostgreSQL **17.12** |
| Migration | `pm_core_schema_v1`, `pm_rls_readonly_v1`, `pm_seed_from_registers_v1`, **`pm_deps_and_stakeholders_v1`** |
| Bảng | **9** / **9** bật RLS, **0** policy ghi |
| Dòng | `pm_actions` **12** (9 `OPEN`), `pm_action_deps` **4**, `pm_action_stakeholders` **12** |

### 4.2. Bảy phép phá, cả bảy bị chặn

| Phép phá | Bị chặn bởi |
|---|---|
| `DONE` mà `evidence` rỗng | `pm_actions_done_needs_evidence` |
| `done_on` trước `not_before` | `pm_actions_done_after_not_before` |
| **`P1` tự chặn `P1`** | `pm_action_deps_no_self` (**23514**) |
| **`P3` chặn bởi `P999` (không tồn tại)** | `pm_action_deps_blocked_by_fkey` (**23503**) |
| `anon` INSERT `pm_action_deps` | RLS: không có policy ghi |
| `authenticated` UPDATE `pm_actions` | RLS: không có policy ghi |
| `anon` DELETE `pm_audit` | RLS: không có policy ghi |

Hai dòng in đậm là phép thử mới của vòng này. Cả hai trả về mã lỗi Postgres thật; không phải suy luận.

### 4.3. Sổ việc: 12 việc, 9 mở, và bốn chỗ đang chờ

| id | chủ | hạn | chờ việc | chờ ai |
|---|---|---|---|---|
| **P8** | LXK | 2026-12-15 | — | LXK — *launchpad-first hay verification-first?* |
| P9 | LXK | 2026-12-15 | **P8** | tách Trust Stamp khỏi báo cáo bán |
| P10 | AGENT | 2026-12-22 | **P9** | cổng canh "điểm công khai không mua được" |
| P11 | LXK | 2026-12-15 | **P8** | kiểm lại `500 người chơi/tuần` |
| P1 | LXK | 2026-12-18 | **P8** | ràng buộc biên `S_LP` |
| P12 | LXK | 2026-12-20 | — | ngày cho 6 việc `docs/23` §9 |

**Bốn việc trong bảng trên chờ đúng MỘT quyết định của một người.** Trước vòng này, cả bốn trông y như bảy việc còn lại.

---

## 5. Hai cổng mới

### 5.1. Cổng 23 — mở rộng

`scripts/check_pm_supabase.py`: thêm bất biến thứ tư `inv_db_matches_register` (dấu vân tay), đồng thời nâng sàn bảng `7 → 9`, phép thử ràng buộc `5 → 7`, `--selftest` từ **4/4 lên 6/6**.

```
PM SUPABASE: PASS — 114 kiểm tra · 4 bất biến · 9 bảng RLS chỉ-đọc · 7 phép thử ràng buộc bị chặn · seed khớp 12 việc
PM SUPABASE SELFTEST: PASS — 6/6 (1 đối chứng + 5 phép phá)
```

### 5.2. Cổng 24 — quyết định phải có mã việc

`scripts/check_decisions.py` (mới). Ba bất biến:

1. Mọi tài liệu có bảng cột mã `R*` phải khai vào `DECISION_TABLES` (quyết định chờ người) **hoặc** `REJECTION_TABLES` (bảng từ chối). Miễn trừ không được ngầm — phải viết ra kèm lý do.
2. Mỗi quyết định trỏ tới một mã `P*` **có thật**, có `due`, và có `stakeholder`.
3. Cổng không được chết: phải thấy ≥ 4 dòng `R*`, nếu không thì glob hỏng.

```
DECISIONS: PASS — 3 kiểm tra · 3 bất biến · 4 dòng quyết định, 1 đã có người + hạn · 25 bảng từ chối khai tường minh
DECISIONS SELFTEST: PASS — 4/4 (1 đối chứng + 3 phép phá)
```

**Điều đáng nói:** nếu cổng này tồn tại từ trước, `R1–R4` của `docs/41` sẽ **đỏ ngay khi viết**, chứ không phải chờ tới khi có người đọc lại. Đó chính là giá trị của việc biến mẫu văn xuôi thành cổng.

**Vì sao có 25 bảng từ chối:** `docs/13`–`docs/37` dùng cùng một quy ước — mỗi tài liệu có một bảng "cái gì bị từ chối và vì sao". Đó là **điểm mạnh** của repo, không phải lỗi. Cổng 24 không xoá chúng; nó chỉ bắt buộc chúng phải **khai tường minh**, để một bảng `R*` mới không lọt vào mà không ai biết nó là quyết định hay từ chối.

### 5.3. Cổng trong `check_actions.py` — hai bất biến mới

| Bất biến | Nếu vi phạm |
|---|---|
| `blocked_by` trỏ tới id có thật, không tự chặn mình | đỏ, in ra `a → b → a` nếu có vòng |
| `OPEN` chờ một việc `DROPPED` | đỏ — việc đó **không bao giờ** mở được |

Bất biến thứ hai là lý do phải có nó: một chuỗi phụ thuộc dẫn tới việc đã bị bỏ là **đình trệ im lặng**, chứ không phải đình trệ ồn ào.

```
ACTION LOCK: PASS — 195 kiểm tra · 5 bất biến · 12 việc (9 OPEN)
```

---

## 6. Bốn câu hỏi

1. **`stakeholder` của việc `DONE` có nên bỏ trống được không?** Hiện tại: **không**. Cả 12 việc đều có, kể cả 3 việc đã `DONE`. Lý do: một việc đã xong vẫn cần biết ai đã đồng ý đóng nó — nếu không, `evidence` chỉ là lời tự khai của người làm. Nhưng đây là **quyết định của vòng này**, không phải điều hiển nhiên; nếu thấy phiền thì đổi thành miễn trừ **có ghi lý do**, đừng nới lặng lẽ.

2. **`DECISION_TABLES` chỉ có một dòng.** Có đúng vì trong 47 tài liệu chỉ `docs/41` §7 là *quyết định chờ người* thật, hay vì 25 bảng kia bị xếp hết vào "từ chối" cho nhanh? Đã đọc cả 25 — chúng thật sự là bảng từ chối (cột thứ ba là lý do *không làm*). Nhưng nếu một bảng trong đó lẫn một dòng "chờ người", cổng 24 sẽ **không** bắt được. Đó là W1.

3. **`seed_fingerprint` đo `md5(title)` chứ không đo cả `why`/`evidence`.** Đủ chưa? Nếu chỉ `title` đổi thì bắt được; nếu chỉ `why` đổi thì **không**. Đây là đánh đổi có ý thức: đo toàn bộ thì phải dán cả `evidence` (dài) và tệp sẽ phình mỗi lần đóng việc.

4. **Mẫu WES có nên trở thành một tệp sinh tự động (`pm/WES.md`) không?** Hiện chỉ có dữ liệu, chưa có bản in. Cổng thì đã đủ để sinh. Nhưng một báo cáo tuần tự động chỉ có nghĩa nếu có người **đọc** nó — và chưa có ai đọc. Đó là W2.

---

## 7. Chưa làm

| | Nợ | Vì sao để lại |
|---|---|---|
| **W1** | Cổng 24 chỉ khai **bảng nào** là quyết định, chưa đọc **từng dòng** trong bảng | Đọc từng dòng đòi hỏi hiểu ngữ nghĩa cột thứ ba, mà cột đó không có mẫu cố định. Một heuristic sẽ đỏ giả và bị tắt |
| **W2** | Chưa sinh `pm/WES.md` (báo cáo tuần) | Chưa có người đọc; sinh ra chỉ để tồn tại là tự tạo việc |
| **W3** | Chưa đối chiếu "từ chối" với "việc đang mở" (một việc mở trái với bảng từ chối) | Cần một khoá nối giữa `R*` và `P*` — dễ hơn W1 nhưng vẫn cần người gán, không suy được từ chữ |
| **W4** | `web/` của nguồn không dùng được làm giao diện | Vẫn treo sau `docs/43` §7 W2 (quyết định giao diện). Một trình xem giáo trình không giải quyết được câu đó |

---

## 8. Dòng ghi nguồn (bắt buộc, theo `docs/23` §1.2)

Cấu trúc bốn mẫu bàn giao trong tài liệu này học từ **`Awesome-FDE-Roadmap`**, giấy phép MIT, của `pierpaolo28` và những người đóng góp, fork bởi `xuankhanh1612`. Bản gốc: <https://github.com/pierpaolo28/Awesome-FDE-Roadmap>.

Không có câu văn nào được chép nguyên văn. Toàn bộ chữ trong `docs/44`, `scripts/check_decisions.py`, và hai bảng `pm_action_deps` / `pm_action_stakeholders` là của Game9K, viết lại từ cấu trúc.
