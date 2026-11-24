# ADR-0043 — Học từ `Awesome-FDE-Roadmap`: bốn thứ áp được, ba thứ không

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0038`](ADR-0038-openrouter-cho-game9k.md) (§5.2 — không đo chất lượng game bằng AI) · [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) · [`test-strategy`](../07-delivery/test-strategy.md) · [`ADR-0011`](ADR-0011-legal-posture.md) · [`tokenomics`](../05-contracts/tokenomics.md) §8 · [`ADR-0023`](ADR-0023-chinh-sach-tuyen-bo-dau-tien.md)

> **Repo bạn đưa là MIT và dùng được** — khác hẳn lần trước (`v0-task-manager` không license).
> Nhưng nó là **giáo trình**, không phải mã hạ tầng: 22 tệp, phần lớn là `README.md` 55 KB +
> một web app Vite để *hiển thị* nội dung đó. Nên câu hỏi không phải "chép gì" mà "**học gì**".

---

## 0. Trả lời ngắn

| # | Nội dung repo | Áp được? | Vì sao |
|---|---|---|---|
| 1 | **Hai vòng eval** (inner/outer loop) cho hệ thống LLM | ✅ **Áp được — và đang thiếu thật** | `docs/07-delivery/test-strategy.md` §5 đo coverage, mutation, flaky — **không có** một dòng nào về eval AI |
| 2 | **MVA** (*Minimum Viable Architecture*, chứng minh giá trị < 30 ngày) | ✅ Áp được | Khớp `ADR-0012` (modular monolith) — nhưng repo **chưa có** ngưỡng "30 ngày" thành luật |
| 3 | **Discovery Checklist** (4 mục: chính trị · dữ liệu · hạ tầng · red flag) | ✅ Áp được **một phần** | Ba mục đầu đã có tương đương; mục **"The Champion / The Blocker"** thì **chưa có ở đâu** |
| 4 | **SOW** (*Statement of Work*) chống scope creep | 🟡 Áp được, có điều kiện | Repo đã có `gates/` + `backlog.md`, nhưng **không có** khái niệm "công việc này NGOÀI phạm vi" |
| 5 | Stack GCP: BigQuery · GKE · VPC SC · ADK · Vertex · LlamaParse | ❌ **Không áp** | Game9K chạy **Postgres + ClickHouse + Solana + Valkey**, không phải GCP. Đây là **khoá nhà cung cấp**, không phải kỹ thuật |
| 6 | "Model-as-a-Judge" / Pairwise / autorater | 🔴 **Bị cấm ở đúng chỗ dễ áp nhất** | `ADR-0038` §5.2: *"Không nhét một phép đo AI vào chuỗi đó"* — chất lượng phiên bản đo bằng **giờ chơi người thật** |
| 7 | `web/` (Vite + React hiển thị roadmap) | ❌ Không áp | Portal là `node:http` thuần + `app.js`; thêm Vite/React là framework thứ ba, và `vercel.json` chỉ ship `{portal/**,demo/docsend/**,package.json}` |

---

## 1. Điều thứ nhất — repo này **MIT**, khác bốn repo vừa xét

Ghi lại vì **tiền lệ quan trọng** — bốn repo liên tiếp trước đó không dùng được:

| Repo | License | Kết quả |
|---|---|---|
| `non4me/marble-race` · `non4me/marbles2d` · `livecade/marble-race-tiktok-live-game` | **`null`** | ❌ |
| `mwood77/YouTubePlays-vs-TwitchPlays` | **GPL-3.0** | ❌ |
| `v0-task-manager` (fork + gốc) | **`null`** | ❌ |
| **`Awesome-FDE-Roadmap`** | **MIT** ✅ | ✅ **Đọc và học được** |

Nhưng "MIT ⇒ dùng được" **không** có nghĩa "chép vào repo này". `ADR-0016` đã ghi quy tắc: đọc mã,
**viết lại cơ chế bằng lời của mình** thì được; chép nguyên hàm thì phải kèm `NOTICE` — và repo này
**chưa có `NOTICE`**. Nên: **học, không chép**.

> Và repo này là **giáo trình** — nội dung chính là văn xuôi hướng dẫn. Chép giáo trình của người
> khác vào tài liệu gọi vốn của mình là việc **sai về bản chất**, không chỉ sai về license.

---

## 2. Chỗ trống thật: repo **không có** eval nào cho hệ thống AI

Đây là phát hiện chính, và nó độc lập với repo bạn đưa.

### 2.1. Bằng chứng

`docs/07-delivery/test-strategy.md` §5 **Đo chất lượng** có 9 chỉ số:

```
Line coverage ≥ 80% · Money-module ≥ 90% · Branch ≥ 70% · Mutation (money) ≥ 60%
BDD scenario có test 100% · Error code có test 100% · Flaky < 2%
CI (PR) < 12 phút · Fuzz 1k/PR, 10k/nightly
```

**Không có** chỉ số nào cho một hệ thống có thành phần AI. Và `ADR-0038` §6 tự ghi:

> *"Phân loại thể loại có đúng không — ❌ **CHƯA ĐO.** Không có nhãn người để đối chiếu."*

⇒ Repo **đang có** một bộ phân loại AI trong đường đi (`portal/lib/`, `ADR-0038`), **đang chạy**,
và **không có phép đo nào** cho nó. Đó là chỗ trống thật, không phải chỗ trống lý thuyết.

### 2.2. Học đúng phần nào — và **không** học phần nào

Repo FDE mô tả hai vòng:

| Vòng | Nội dung repo | Áp vào Game9K? |
|---|---|---|
| **Inner loop** (dev) | Golden Dataset + `tool_trajectory_avg_score` + `response_match_score` + rubric | ✅ **Áp được**: golden set cho bộ phân loại thể loại |
| **Outer loop** (production) | Pipeline eval + **Pairwise (Model-as-a-Judge)** + RAG Triad + drift monitoring | 🔴 **Pairwise bị cấm** ở đúng chỗ này — xem §4 |

**Cụ thể áp được, hẹp và kiểm được:**

| Việc | Chi tiết | Vì sao hẹp |
|---|---|---|
| **Golden set** cho `genre_id` | ≥ 200 game có nhãn người, mỗi nhóm ≥ 30 | Chính là điều `ADR-0038` §6 ghi là **thiếu** (*"không có nhãn người để đối chiếu"*) |
| **Đo bằng ma trận nhầm lẫn**, không bằng "điểm" | precision/recall **theo từng nhóm** trong 6 `genre_id` | `percentile_C` tính **trong cùng genre** (§4.4a) ⇒ một nhóm sai làm hỏng phân vị của cả nhóm |
| **Ngưỡng chặn**, ghi trong config | Nếu precision của bất kỳ nhóm nào < 0,8 ⇒ **tắt** tính năng phân loại, quay về `source: assumed` | Đúng luật `ADR-0023` loại 3: chưa có dữ liệu thì **không được ở dạng khẳng định** |
| **CI kiểm** | `check_genre_eval.py` đỏ nếu golden set < 200 hoặc precision < ngưỡng | Một cổng phải **đỏ được** — `ADR-0027` §7 |

> **Điểm quan trọng:** đây **không** phải "đo chất lượng game bằng AI". Đây là **đo bộ phân loại
> bằng nhãn người**. Khác nhau hoàn toàn: cái thứ nhất bị `ADR-0038` §5.2 cấm; cái thứ hai là cách
> duy nhất biết bộ phân loại có dùng được hay không.

---

## 3. Ba thứ áp được nữa, và cái giá của mỗi thứ

### 3.1. **MVA** — "chứng minh giá trị trong < 30 ngày" (áp được, cần thành luật)

Repo FDE: *"Don't over-engineer. Design the simplest version that proves the value in < 30 days."*

Game9K **đã có** tinh thần này ở `ADR-0012` (modular monolith trước, tách service sau), nhưng
**chưa có ngưỡng thời gian**. Đề nghị thêm vào `test-strategy` hoặc `roadmap.md`:

> Mỗi module mới phải chứng minh được giá trị trong **một sprint (10 ngày)**, hoặc bị cắt.

**Cái giá:** "30 ngày" nghe hay nhưng **không đo được** nếu không nói "chứng minh bằng gì". Nên
phải kèm: *chứng minh bằng một drill hoặc một test end-to-end chạy được*, không phải bằng demo.
Xem Q-ADR43-b.

### 3.2. **Discovery Checklist** — mục "The Champion / The Blocker" (**thật sự thiếu**)

Đây là mục duy nhất trong checklist của repo mà Game9K **không có tương đương**:

| Mục FDE | Game9K đã có? |
|---|---|
| Success Metric | ✅ `gates/` + `check_gates.py` |
| Data Classification (PII/PHI) | ✅ `AGENTS.md` (không commit PII) + `ADR-0026` §5.2 |
| Ingestion / Compliance | ✅ `ADR-0011` + NFR |
| **The "Champion"** — ai trong nội bộ đang đấu cho dự án này? | 🔴 **KHÔNG CÓ Ở ĐÂU** |
| **The "Blocker"** — bộ phận nào dễ dừng dự án nhất? | 🔴 **KHÔNG CÓ Ở ĐÂU** |

Với Game9K, "Champion" và "Blocker" **đã có tên thật**:

| Vai | Là ai | Bằng chứng |
|---|---|---|
| **Champion** | PO (Lê Xuân Khánh) — người ký mọi ADR | `ADR-0023` §4.3: tên gắn với người **phát biểu** |
| **Blocker** | **luật sư** — vì `ADR-0011` **đang chặn GA** | `ADR-0011` trạng thái `Proposed`, *"blocking cho GA"* |

⇒ Đề nghị thêm một dòng vào `docs/gates/README.md`: mỗi cổng phải ghi **ai là người ký** (đã có)
và **ai có thể chặn** (chưa có). Đây là việc **văn bản**, không phải mã.

### 3.3. **SOW** — "công việc này NGOÀI phạm vi" (**áp được, có điều kiện**)

Game9K có `backlog.md` (80 story · 290 điểm) và `gates/` (P01–P06), nhưng **không có** khái niệm
"yêu cầu này nằm ngoài phạm vi". Mọi yêu cầu hiện được xử lý bằng cách **thêm ADR** — kể cả những
yêu cầu nên bị **từ chối kèm lý do** (như `ADR-0040` §4, `ADR-0042`, ADR này §4).

Đề nghị: mỗi ADR có **bắt buộc** một mục *"Điều ADR này KHÔNG bao gồm"*. Đã có ở nhiều ADR
(`ADR-0023` §3, `ADR-0040` §8) nhưng **không bắt buộc** — nên có lúc thiếu.

---

## 4. Ba thứ **không** áp — và hai trong số đó bị cấm bởi luật đã có

### 4.1. 🔴 Pairwise / Model-as-a-Judge để đo chất lượng game

Repo FDE nói *"Pairwise Evaluation… uses a superior model as an autorater to compare two model
responses"*. Nghe rất hợp với một dự án đã có **Blind Version Duel** (`ADR-0027`, `yellowpaper` §4).

> **Nhưng đó chính là chỗ `ADR-0038` §5.2 đã cấm:**
>
> *"Chất lượng một phiên bản đo bằng **giờ chơi người thật** (`play_sessions`, `verified_minutes`),
> … Một lần gọi API không phải một con người, và **không phải một lượt chơi**. Điểm chất lượng neo
> merkle theo phiên bản. **Không** nhét một phép đo AI vào chuỗi đó."*

Và `KVU-2` §1.4 là lý do gốc: **đơn vị kiểm toán của một phép đo AI là `(model, phiên bản)`** — nó
đo *model*, không đo *game*. Thay đấu mù người thật bằng judge AI là **đổi thứ đang đo**.

⇒ **Bị cấm.** Còn đấu mù người thật thì **giữ nguyên**.

### 4.2. ❌ Stack GCP

| Repo FDE | Game9K thật | Kết luận |
|---|---|---|
| BigQuery | **ClickHouse 24** (`ADR-0009`) | Đã chọn, có lý do |
| GKE | Vercel + `node:http` | Khác mô hình |
| VPC Service Controls | Không có (không phải enterprise VPC) | Không áp dụng được |
| Google ADK / Vertex / LlamaParse | **Không có** — `package.json` chỉ `pg` + `pglite` + `jsdom` | Thêm = khoá nhà cung cấp |
| Air-gap / tactical edge | Không có nhu cầu | Không áp dụng |

Đây là **nội dung giáo trình cho một vai trò khác** (FDE bán vào doanh nghiệp lớn), không phải
hạ tầng của một portal game.

### 4.3. ❌ `web/` (Vite + React)

`web/` là **website hiển thị giáo trình** (34 KB `App.jsx` + 68 KB `course.js`). Portal là
`node:http` thuần, và `vercel.json` chỉ ship `{portal/**,demo/docsend/**,package.json}` —
`bundle.test.mjs` B-01 đã chứng minh rủi ro bundling ở đây là **thật** (một tệp `portal/` import
`../scripts/lib/…` từng 500 ở production). Thêm Vite = framework thứ ba cho một trang tĩnh.

---

## 5. Một điều repo FDE nói mà Game9K nên **đối chiếu ngược** — và nó không dễ chịu

Repo FDE có mục **🚩 Red Flags**, ba dấu hiệu phải escalate ngay:

| # | Red flag (nguyên văn) | Game9K có dấu hiệu này không? |
|---|---|---|
| 1 | *"Data will be ready in 2 weeks" (It never is)* | ⚠️ **Có, ở dạng khác**: `θ_D7,C` cho 2 thể loại **không có nguồn công khai** (`yp-1.8` ghi `source: assumed`); `percentile_C` cần **≥ 200 game/genre** mà hôm nay là **0** |
| 2 | *"We don't need a project manager on our side"* | ✅ **Không** — repo có `gates/` P01–P06 + 6 cổng chưa ký |
| 3 | *"Can we just run this on-prem for now?"* | ✅ **Không áp dụng** (không có on-prem) |

⇒ Red flag #1 **đúng một phần**, và nó không phải chuyện để nói nhẹ: ba tham số đang ở trạng thái
"chờ dữ liệu" nằm trong **đường đi của cổng M2** — cổng chặn việc mở bán token cho studio.

Đây là **giá trị thật** của việc đọc repo này: nó cho một **danh sách kiểm tra từ bên ngoài** để đối
chiếu, và repo đã tự ghi những điểm yếu đó ở nơi khác.

---

## 6. Việc nên làm, theo thứ tự

| Bước | Việc | Chặn bởi | Tính chất |
|---|---|---|---|
| **1** | Thêm **mục eval AI** vào `test-strategy.md` §5 — golden set `genre_id`, ma trận nhầm lẫn, ngưỡng precision 0,8 | Không | 🟡 Văn bản; nhưng cần **200 nhãn người** mới chạy được |
| **2** | Thêm **"ai có thể chặn cổng này"** vào `docs/gates/README.md` | Không | 🟢 Thuần văn bản, làm ngay |
| **3** | Bắt buộc mục *"ADR này KHÔNG bao gồm"* trong mẫu ADR | Không | 🟢 Thuần văn bản |
| **4** | Luật **MVA**: module mới phải chứng minh giá trị trong 1 sprint, bằng **drill hoặc e2e test** | Q-ADR43-b | 🟡 Cần định nghĩa "chứng minh" |
| **5** | Golden set thật cho `genre_id` | **Cần 200 nhãn người** | 🔴 Việc của con người |

**Bước 2 và 3 không phụ thuộc gì** — làm ngay được.

---

## 7. Năm câu cần PO quyết

| Mã | Câu hỏi |
|---|---|
| **Q-ADR43-a** | Có thêm **mục eval AI** vào `test-strategy.md` §5 không? Tôi đề nghị **có**, nhưng ghi rõ là **chưa chạy được** cho tới khi có 200 nhãn người |
| **Q-ADR43-b** | "MVA trong 1 sprint" — **chứng minh bằng gì**? Drill? e2e test? Một người dùng thật? Không định nghĩa thì luật này thành khẩu hiệu |
| **Q-ADR43-c** | Có thêm dòng **"ai có thể chặn cổng"** vào `gates/README.md` không? Đây là việc 10 phút |
| **Q-ADR43-d** | Có bắt buộc mục *"ADR này KHÔNG bao gồm"* trong mẫu ADR không? |
| **Q-ADR43-e** | Ba tham số `source: assumed` (`θ_D7,C` cho `idle-incremental` và `multiplayer-arena`, + `percentile_C` cần 200 game) — ai sẽ lấy dữ liệu, và khi nào? Đây là red flag #1 của chính repo FDE |

---

## 8. Ranh giới trung thực

- **Không** nói repo FDE "chứng minh" cách làm của Game9K đúng. Nó là **giáo trình cho một vai trò
  khác** (FDE bán vào doanh nghiệp). Giá trị nằm ở **danh sách kiểm tra**, không ở kết luận.
- **Không** chép nội dung. MIT cho phép **dùng**, nhưng repo chưa có `NOTICE`, và chép giáo trình
  của người khác vào tài liệu gọi vốn là sai về bản chất.
- **Không** khẳng định "Game9K thiếu eval" mà không dẫn chỗ: `test-strategy.md` §5 có 9 chỉ số,
  **0** chỉ số về AI; `ADR-0038` §6 tự ghi *"CHƯA ĐO"*.
- **Không** áp Pairwise/AI-judge cho chất lượng game. `ADR-0038` §5.2 cấm, và lý do là
  `KVU-2` §1.4 — nó đo **model**, không đo **game**.
- **Không** có dòng mã nào trong ADR này. Bước 2 và 3 là **văn bản**, làm được ngay; bước 1 và 5 cần
  **nhãn người**, không phải mã.
