# Bản ghi niềm tin của dự án — học từ `Proactive-Co-Creator`

> **Tài liệu sống:** `docs/26-belief-record-project-memory.md`
> **Trạng thái:** `SCOPING` — đánh giá + **đã dựng một bản ghi thật** (`pm/spec-p01-gia-thuyet.json`) và một cổng (`scripts/check_specs.py`)
> **Ngày:** 22/11/2026
> **Đầu vào:** repo `khanhlegood1/Proactive-Co-Creator` + yêu cầu *"áp dụng vào quản lý dự án GameK9 này"*
> **Liên quan:** `docs/25` (câu hỏi có khoá, xác suất) · `docs/24` (vòng lặp tác nhân) · `docs/22` A2/A5 · `docs/PRD.md` §0 (6 cổng HITL)

---

## 0. Kết luận trước

**Repo đó là một trình soạn prompt. Nhưng bốn cơ chế bên trong nó áp thẳng được vào việc quản lý dự án — và cái quan trọng nhất là: nó dặn *đừng* hỏi lại thứ đã rõ.**

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Repo đó làm gì? | Sửa prompt bằng **đồ thị niềm tin** (thực thể + thuộc tính + quan hệ), **hỏi 3 câu**, rồi áp **delta tối thiểu** (§1) |
| **2** | Áp vào quản lý dự án thế nào? | Mỗi **cổng HITL** = một bản ghi có cấu trúc: *thực thể · thuộc tính · luật · câu hỏi mở* (§3) |
| **3** | Cơ chế nào đáng lấy nhất? | **Câu hỏi đã bị luật trả lời thì không hỏi lại.** Kèm: delta tối thiểu · đường thoát · "không chắc thì hỏi" (§2) |
| **4** | Đã dựng gì? | `pm/spec-p01-gia-thuyet.json` + `scripts/check_specs.py` — **tick** so tài liệu, **questions** sinh câu hỏi, **answer** từ chối câu bị chặn (§4) |
| **5** | Nó bắt được lỗi gì? | **16** giá trị trong bản ghi phải còn khớp **dòng nguồn** trong `docs/`; lệch là đỏ (§4.1) |
| **6** | Có phải "AI ghi nhớ dự án" không? | ❌ **Không.** Bản ghi là **tuyên bố của người, có `source`**. Không có mô hình nào viết vào đây (§6) |

---

## 1. Repo đó thật sự là gì

| | |
|---|---|
| Ngôn ngữ / giấy phép | TypeScript · **không có tệp `LICENSE`** ở gốc repo, nhưng **cả `17/17` tệp `.ts`/`.tsx`** đều có header `SPDX-License-Identifier: Apache-2.0` |
| Tạo / đẩy | `22/11/2026` · **`0`**★ · tạo và đẩy cách nhau **`20` giây** |
| Kích thước mã | **`5.903`** dòng trong 5 tệp chính: `components/BeliefGraph.tsx` **`1.586`** · `services/geminiService.ts` **`1.487`** · `server.ts` **`1.322`** · `App.tsx` **`1.062`** · `components/ClarificationCard.tsx` **`446`** |
| Kiến trúc | React + Vite + **Express `server.ts`**; gọi Gemini **phía máy chủ** qua `genaiProxy` (một lớp proxy riêng, không gọi thẳng từ trình duyệt) |
| Có phụ thuộc build | ✅ `npm install` + `vite build` — **khác** repo Decisions API (nhúng sẵn, không build) |
| Khai báo năng lực | `metadata.json`: `MAJOR_CAPABILITY_SERVER_SIDE_GEMINI_API` — quyền gọi API **nằm ở máy chủ** |

> **Điểm đáng khen, và hiếm:** header SPDX trên **từng tệp**, và bản quyền khai rõ **Apache-2.0** dù gốc repo không có `LICENSE`. Về mặt giấy phép, đây là **rõ ràng hơn** nhiều repo cùng loại — nhưng `LICENSE` ở gốc vẫn nên có.

### 1.1. Bốn kiểu dữ liệu — và vì sao chúng là "bản ghi niềm tin"

`types.ts` định nghĩa đúng bốn thứ, không hơn:

| Kiểu | Nội dung | Điểm mạnh |
|---|---|---|
| **`Entity`** | `name` · `presence_in_prompt` · `description` · `alternatives` · `attributes` | Phân biệt **có trong prompt** với **suy ra** |
| **`Attribute`** | `name` · `presence_in_prompt` · `value: Candidate[]` | Giá trị là **danh sách ứng viên**, không phải một chuỗi |
| **`Relationship`** | `source` · `target` · `label` · `alternatives` | Quan hệ cũng có **phương án khác** |
| **`Clarification`** | `question` · `options[]` | Câu hỏi **kèm lựa chọn**, không phải câu hỏi mở |

---

## 2. Bốn cơ chế đáng lấy — và một câu dặn rất cụ thể

### 2.1. "Câu đã rõ thì đừng hỏi lại" — cơ chế đáng giá nhất

Khi có ảnh tham chiếu, repo đổi hẳn chỉ dẫn (`geminiService.ts:956`):

> *"DO NOT ask about visual details that are clearly visible and unambiguous in the images. DO ask questions that clarify the INTENT behind the text prompt's modifications."*

Và khi hỏi vòng sau (`geminiService.ts:999`): *"**Avoid Repetition**: DO NOT ask any of: …"* — kèm **danh sách câu đã hỏi**.

> **Áp vào dự án:** rất nhiều cuộc họp lặp lại vì hỏi lại thứ đã có trong tài liệu. Nếu câu hỏi đã bị một **luật** hoặc một **dòng trong `docs/`** trả lời, nó phải **không được hỏi lại** — và phải **ghi rõ đã bị trả lời bởi cái gì**.

### 2.2. Delta tối thiểu

`geminiService.ts:641`:

> *"MINIMAL DELTA: ONLY output the entities and relationships that have changed. DO NOT output the entire graph. If an entity or relationship has not changed, DO NOT include it in the output."*

Và khi một thực thể **bị bỏ** (`geminiService.ts:637`), phải **xoá hẳn** chứ không đánh dấu `existence=false`:

> *"REMOVE ABSENT ENTITIES … Do NOT keep it in the graph with existence=false."*

> **Áp vào dự án:** trong `docs/`, một quyết định bị bỏ thường được để lại dưới dạng *"trước đây chúng tôi định…"* — và ba tháng sau không ai biết nó còn hiệu lực hay không. **Xoá hẳn, hoặc ghi rõ trạng thái.**

### 2.3. Ba mức "chủ động" — một tham số, không phải ba chế độ

`Proactiveness = 'low' | 'medium' | 'high'`, và mỗi mức đổi **một câu chỉ dẫn**:

| Mức | Nguyên văn (`geminiService.ts:964–967`) |
|---|---|
| `low` | *"STRICT MODE: Only ask about the attributes of existing entities explicitly mentioned in the prompt… Do NOT invent story elements or suggest creative additions."* |
| `medium` | *"BALANCED MODE: Ask about missing technical details and offer a few creative suggestions that stay close to the original prompt's intent."* |
| `high` | *"CREATIVE MODE: Be highly proactive. Invent interesting, specific, and creative attributes…"* (`:446`) |

Cùng một tham số này còn đổi cả **khâu trích xuất** (`:428–446`), không chỉ khâu hỏi — tức là "chủ động" ảnh hưởng **cái gì được ghi vào bản ghi**, không chỉ cái gì được hỏi.

> **Áp vào dự án:** "mức can thiệp" là **một tham số của quy trình**, không phải thói quen của người viết. Ở giai đoạn `SCOPING` thì được `high`; khi chốt số thì phải `low`.

### 2.4. Hai đường thoát cho mọi câu hỏi

`components/ClarificationCard.tsx:12–13` — hai hằng số, không phải một dropdown:

```
[NOT RELEVANT] This question is not relevant to my prompt. Do not include details about it.
[YOU DECIDE]   I don't care, you decide. Take creative liberty here.
```

> **Áp vào dự án:** câu hỏi **không có đường thoát** sẽ bị trả lời bừa hoặc bị bỏ qua. Cả hai đều tệ hơn "không hỏi".

### 2.5. Một chỗ **không** đáng bắt chước

`withRetry(fn, retries = 3, initialDelay = 1000)` bọc **mọi** lệnh gọi model, chỉ thử lại khi `isRetryableError(error)` đúng (`geminiService.ts:113–130`). Khi hỏi lại thất bại hẳn thì:

> `:1060` *"Clarifications unavailable; returning empty list"* · `:1163` *"Prompt refinement unavailable; keeping original prompt"*

Đây là **fail-soft** đúng cho một công cụ sáng tạo. Nhưng nếu áp vào cổng dự án thì **sai**: một cổng "không lấy được ý kiến" phải **đỏ**, không được **im lặng đi tiếp**. Đây là cùng lý do `docs/25` §5 tách *tín hiệu* khỏi *cổng*.

---

## 3. Áp dụng: mỗi cổng HITL thành **một bản ghi** (thay vì một đoạn văn)

`docs/25` đã biến tiêu chí cổng thành **câu hỏi có/không**. Nhưng câu hỏi vẫn chỉ là câu hỏi — nó không nói **cái gì đang được hỏi về**. Repo này bổ sung đúng phần thiếu: **thực thể và thuộc tính**.

| Khái niệm của repo | Tương ứng trong quản lý dự án Game9K |
|---|---|
| `Entity` | Một **hạng mục đã chốt**: token · `pop_score` decay · chia doanh thu · MOIC |
| `Attribute` + `value[]` | Một **con số kèm nguồn**, ví dụ `supply = 1,000,000,000` ← `WHITEPAPER:478` |
| `presence_in_prompt` | **`presence_in_spec`** — hạng mục này có trong bản ghi hay chỉ là giả thuyết |
| `Relationship` | Quan hệ giữa hai hạng mục (ví dụ: `MOIC` **phụ thuộc** `eCPM`) |
| `Clarification` → `open_questions` | Câu hỏi mở, **có đường thoát** |
| **Luật chống hỏi lại** (mới) | **`constraints`**: câu hỏi nào đã bị luật trả lời |

**Khác biệt cốt lõi so với repo gốc:** trong repo, model **điền** đồ thị. Ở đây, **người** điền, và mỗi giá trị phải trỏ về **một dòng có thật** trong `docs/`. Đó là điều làm nó dùng được cho quản lý dự án: nó không thể bịa.

---

## 4. Đã dựng: `pm/spec-p01-gia-thuyet.json` + `scripts/check_specs.py`

```bash
python3 scripts/check_specs.py --tick        # so 16 giá trị với dòng nguồn trong docs/
python3 scripts/check_specs.py --questions   # câu hỏi còn mở, bỏ câu đã bị luật trả lời
python3 scripts/check_specs.py --answer q_pii=có   # ⛔ từ chối, mã lỗi 1
python3 scripts/check_specs.py --self-test   # 4 bất biến, chạy trong CI
```

### 4.1. `--tick` là gì, và vì sao nó mạnh hơn một lần đọc

Mỗi giá trị trong bản ghi có `source` dạng `docs/WHITEPAPER.md:478`. `--tick` đọc **đúng dòng đó** và kiểm giá trị còn nằm trong dòng ấy.

```
SPEC TICK: PASS — 16 giá trị khớp dòng nguồn, 0 lệch
```

Đây là **cùng tinh thần** với `verify_pop_decay.py` và `check_pitch_deck.py`: một con số không còn ở nguồn của nó là **một con số đã chết**. Cổng này bắt được cả hai chiều:

- ai sửa **bản ghi** mà không sửa tài liệu → đỏ;
- ai sửa **tài liệu** ở dòng nguồn mà bản ghi còn giữ số cũ → đỏ.

Luật trung thực **không kiểm được bằng máy** vẫn tồn tại: một giá trị **đúng nhưng vô nghĩa** vẫn qua cổng. §6 ghi rõ.

### 4.2. `--questions`: câu đã bị luật trả lời thì **không hỏi lại**

```
P01 — HYPOTHESIS — chưa ai duyệt
  ? q_m1_scope: M1 (15% cung) gồm những cột mốc kỹ thuật nào?
      · [BẠN QUYẾT] …
      · [KHÔNG LIÊN QUAN] …
5 câu hỏi · 2 câu bị luật trả lời nên KHÔNG hỏi lại · 3 câu cần người quyết
```

Hai câu bị chặn: `q_pii` (bị luật **C5** — không thêm PII khi chưa có luật sư) và `q_youtube` (bị **C6** — chưa hứa YouTube). Đây là **đúng những điều người sáng lập đã quyết trong các vòng trước** — giờ chúng là **luật máy đọc được**, không còn là trí nhớ của một phiên chat.

### 4.3. Bốn bất biến, và bốn phép phá đã chạy thật

| # | Bất biến | Phép phá | Kết quả |
|---|---|---|---|
| **1** | Mọi giá trị có `source` đọc được và còn khớp | đổi `supply` thành `999,999,999` | ❌ `giá trị không còn ở docs/WHITEPAPER.md:478` |
| **2** | Câu bị luật trả lời phải khai **hai chiều** | bỏ `refuses_question` của `C5` | ❌ `q_pii khai bị C5 trả lời, nhưng C5 không trỏ ngược lại` |
| **3** | Trả lời câu bị chặn phải **bị từ chối** | `--answer q_pii=có` | ⛔ mã lỗi **`1`** |
| **4** | Mọi câu hỏi có đường thoát | — | ✅ `[BẠN QUYẾT]` + `[KHÔNG LIÊN QUAN]` |

> **Phép phá 2 là phát hiện thật trong lúc làm:** ban đầu `--self-test` chỉ kiểm một chiều, nên bỏ `refuses_question` thì câu hỏi **lặng lẽ xuất hiện lại** — đúng thứ repo mẫu dặn tránh. Đã sửa thành kiểm hai chiều.

---

## 5. Ba tệp, ba vai trò — đừng để lẫn

| Tệp | Là gì | Ai ghi | Vào CI? |
|---|---|---|---|
| `pm/spec-*.json` | **Bản ghi niềm tin**: con số + nguồn + luật + câu hỏi | **Người** | ✅ `--tick` + `--self-test` |
| `docs/*.md` | **Nguồn số** (whitepaper, PRD, teardown) | Người, qua PR | ✅ 5 cổng hiện có |
| `docs/25` `gate_decide.py` | **Câu hỏi** cho cổng, suy từ tiêu chí | Máy sinh từ PRD | ✅ `--self-test` |

> **Không tệp nào là "bộ nhớ của AI".** Bản ghi là **tuyên bố của người**; cổng là **phép kiểm**; tài liệu là **nguồn**. Ba thứ này lệch nhau là chuyện bình thường — `--tick` tồn tại để **phát hiện** lúc lệch.

---

## 6. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Cho model **điền** bản ghi dự án | Repo gốc làm vậy cho *prompt sáng tạo*. Với số liệu tài chính thì **một giá trị bịa là một vòng gọi vốn sai** |
| **R2** | `withRetry` + fail-soft cho cổng | §2.5 — cổng "không lấy được ý kiến" phải **đỏ**, không im lặng |
| **R3** | Tin `--tick` là bằng chứng **đúng** | Nó chỉ chứng minh **khớp nguồn**. Một giá trị đúng-nguồn nhưng vô nghĩa vẫn qua |
| **R4** | Tự động sinh câu hỏi từ tài liệu rồi coi là "đã hỏi" | Câu hỏi chỉ có giá trị khi **người** đọc và trả lời; §2.1 chỉ nói **đừng hỏi lại**, không nói **tự trả lời** |

---

## 7. Việc **không** làm trong tài liệu này

- Không gọi API nào. `check_specs.py` chỉ đọc tệp.
- Không đổi `W = 0,60` / `H = 180`, whitepaper, deck, 4 PDF, schema (**34** bảng).
- Không thêm phụ thuộc; chỉ thư viện chuẩn.
- Không đưa `pm/` vào bản in — đây là công cụ, không phải tài liệu công bố.

## 8. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | `--questions` và **trả lời ba câu còn mở** (`q_m1_scope`, `q_kyc`, `q_legal_entity`) | Ba câu này chặn cả P01 lẫn P06 |
| **2** | Thêm `pm/spec-p03-hop-dong.json` khi `docs/03` chốt | P03 đang có 3 câu hỏi từ `docs/25` |
| **3** | Gắn `--tick` vào job `verify` (đã làm) và **đọc báo cáo mỗi lần đỏ** | Cổng chỉ có giá trị khi người ta đọc lý do |
| **4** | Quy tắc "xoá hẳn, đừng để `existence=false`" vào `AGENTS.md` | §2.2 — chống quyết định treo lơ lửng |
