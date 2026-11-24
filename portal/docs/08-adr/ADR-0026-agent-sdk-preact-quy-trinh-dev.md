# ADR-0026 — `nccasia/agent-sdk` (PreAct) áp dụng vào quy trình Dev: **một phần, có điều kiện**

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-22
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ai-agile-adoption.md`](../00-framework/ai-agile-adoption.md) · [`docs/gates/`](../gates/) · [`ADR-0001`](ADR-0001-modular-phase-loop.md) · Q56–Q58

> ⚠️ Tài liệu này **đề xuất**, không phải hướng dẫn cài đặt. Phần §2 là điều **phải kiểm
> trước**, và nó chưa được kiểm xong.

---

## 0. Trả lời ngắn

**Áp dụng được — nhưng không phải "cài SDK rồi dùng".**

| Điều | Khả thi? |
|---|---|
| Thay cổng kiểm hiện tại bằng agent tự chủ | ❌ **Không** |
| Dùng mô hình `lobe → stage → flow` để cấu trúc lại prompt của từng cổng P01–P06 | ✅ **Có**, giá trị cao nhất |
| Dùng `trace` (`path`, `prompts`, `activations`, `cost`) làm bằng chứng kiểm toán cho tài liệu do AI sinh | ✅ **Có**, và repo đang **thiếu** đúng thứ này |
| Dùng `pinned lobes` để ép cổng `filter`/`cite` không bị bỏ qua | ✅ **Có**, tương ứng trực tiếp HITL gate |
| Chạy trong CI | ❌ **Không** (xem §2) |
| Dùng `PluginWorkspace` để agent sửa repo thật | ⚠️ **Rủi ro cao** — xem §5 |

---

## 1. Vì sao nó khớp với quy trình hiện có

Repo này đã có đúng cấu trúc mà PreAct hình thức hoá, nhưng dưới dạng **văn xuôi**:

| PreAct | Repo đã có | Đánh giá |
|---|---|---|
| `intent` → chọn `flow` | P01…P06, mỗi cổng một loại artifact | **khớp 1:1** |
| `stages` (pipeline có thứ tự) | [`ai-agile-adoption.md` §2](../00-framework/ai-agile-adoption.md) mapping 6 pha → module | **khớp** — mỗi pha là một stage |
| `pinned lobes` (không được bỏ qua) | HITL gate: **không auto-approve**, `check_gates.py` từ chối gate tự `APPROVED` | **cùng ý tưởng, đã có kiểm tự động** |
| `cite` / `filter` (output contract) | `check_doc_refs.py`, `check_claims.py`, ADR-0023 | **repo mạnh hơn** — đã có, không phải plugin |
| `metacognition: monitor → regulate` | `docs/gates/P0x-signoff.md` + `check_gate_deadlines.py` | **khớp** — nhưng repo dùng SLA người, không phải vòng lặp máy |
| `trace` (bằng chứng kiểm toán) | **KHÔNG CÓ** | 🔴 **lỗ hổng thật** |

> Điểm khớp mạnh nhất: **PreAct coi `filter`/`cite` là *pinned* — không stage nào được bỏ qua.**
> Repo này cũng vậy, nhưng bằng `check_*.py` chạy trong CI. Đây là hai cách diễn đạt cùng một
> luật, và cách của repo **mạnh hơn** vì nó chạy trên artifact đã commit, không chỉ trên một lượt.

---

## 2. 🔴 Bốn điều phải kiểm trước khi áp dụng — và chưa kiểm được

### 2.1. `pip install agent-sdk` **không hoạt động** — package không có trên PyPI

README hướng dẫn:

```bash
pip install agent-sdk
pip install "agent-sdk[openai,redis]"
```

Kiểm thực tế:

| Tên package | PyPI |
|---|---|
| `agent-sdk` | **HTTP 404** |
| `agent_sdk` | 404 |
| `preact-agent` | 404 |
| `nccasia-agent-sdk` | 404 |

⇒ **Chỉ cài được từ source**: `git clone … && uv sync`. Không phải vấn đề lớn, nhưng nghĩa là
mọi tài liệu của repo này **không thể** dẫn `pip install agent-sdk` như một bước — nó sẽ hỏng
với người đọc sau.

### 2.2. 🔴 Yêu cầu **Python 3.12+**, CI của repo này chạy **3.11**

| | Phiên bản |
|---|---|
| `agent-sdk` (`pyproject.toml`, badge README) | **≥ 3.12** |
| `setup-python` trong **toàn bộ** workflow của repo này | **3.11** |

⇒ **Không thể** đưa vào CI hiện tại mà không nâng version cho mọi workflow. Đó là một thay đổi
hạ tầng riêng, không phải một dòng `pip install`.

### 2.3. `agent-sdk:docs/building-a-harness.md` **không khớp** package công khai

> Quy ước: tiền tố `agent-sdk:` nghĩa là đường dẫn **trong repo `nccasia/agent-sdk`**, không
> phải trong repo này. `check_doc_refs.py` sẽ báo đỏ nếu tôi trích chúng như đường dẫn nội bộ —
> và nó đã báo, đúng lúc viết tài liệu này.

Trang đó hướng dẫn `from agent_core.sdk import Lobe, Flow, LlmCall` — tức module nội bộ
`agent_core`, **không phải** `agent_sdk` mà README quảng bá. Nó cũng dẫn
`../../../docs/architecture.md` — đường dẫn **ra ngoài** repo công khai.

⇒ Tài liệu mô hình (PreAct) đọc được, nhưng **API để dùng thật** thì phải đọc `agent-sdk:docs/api.md` và
`agent-sdk:examples/coding-agent/`. Đừng trích `building-a-harness.md` làm hướng dẫn triển khai.

### 2.4. Trạng thái thật của dự án

| Chỉ số | Giá trị |
|---|---|
| Trạng thái tự khai | **Beta**, *"API may still shift before 1.0"* |
| Sao / fork | **3 / 1** |
| Commit | 64 |
| Push gần nhất | 2026-09-24 (≈ 2 tháng) |
| License | Apache-2.0 |

Không phải lý do để từ chối — nhưng là lý do để **không đặt nó vào đường găng của quy trình**.
Một API beta ở 3 sao không nên là thứ quyết định việc một gate có ký được hay không.

---

## 3. ✅ Giá trị thật: `trace` — thứ repo đang thiếu

Đây là lý do **duy nhất** đủ mạnh để áp dụng, và nó đáng áp dụng.

**Hiện trạng repo:** mỗi cổng `P0x-signoff.md` ghi *"AI-COMPLETE — chờ ký"* và người ký tick
checklist. Nhưng **không có bản ghi nào** về:

- AI đã đọc tài liệu nào để sinh artifact đó;
- nó đã cân nhắc và **bỏ** phương án nào;
- chỗ nào nó **không chắc** và đã nêu giả định ở đâu.

Repo có [`ADR-0023`](ADR-0023-chinh-sach-tuyen-bo-dau-tien.md) về chính sách tuyên bố, nhưng đó
là **luật về output**, không phải **bản ghi về quá trình**.

> Một gate được ký bởi người, trên artifact do AI sinh, **không có trace** — thì chữ ký đó chỉ
> xác nhận *"tôi đọc output và thấy ổn"*. Nó không xác nhận *"tôi biết output này từ đâu ra"*.

**PreAct cung cấp đúng cấu trúc đó:** mỗi lượt phát ra `path`, `prompts`, `activations`, `tools`,
`cost` — dạng máy đọc được, có viewer HTML.

**Đề xuất hẹp và cụ thể:**

| Làm | Không làm |
|---|---|
| Lưu trace của **lượt sinh artifact** cho mỗi gate, cạnh `P0x-signoff.md` | Không dùng trace để **thay** chữ ký |
| Ghi trace vào `docs/gates/P0x-trace/` | Không đưa trace vào repo nếu nó chứa prompt nhạy cảm (xem §5.2) |
| Một script kiểm: gate đã ký ⇒ **phải có** trace | Không bắt trace cho gate **chưa** ký |

Đây là phần **tôi đề nghị làm trước**, và nó **không cần** đưa SDK vào CI.

---

## 4. Ba thứ KHÔNG nên lấy

| Thứ | Vì sao không |
|---|---|
| **PluginWorkspace / `fs.*` tools** cho agent sửa repo | Agent có quyền ghi vào `docs/` là **bỏ HITL gate**. Repo này đã có luật: AI sinh artifact, người ký gate. Cấp quyền ghi = bỏ luật đó |
| **`safety ≠ rag` và `filter` của PreAct** như lớp bảo vệ **duy nhất** | `check_*.py` (22 cổng) đã mạnh hơn và chạy trên artifact thật. Thêm `filter` của SDK là **lớp thứ hai yếu hơn**, không phải lớp thay thế |
| **Benchmarks live-only** làm bằng chứng chất lượng | Nó cần credential provider → **không chạy được trong CI** của repo này. Và repo đã có luật: *"xanh vì chưa có gì để kiểm" không phải bảo vệ* |

---

## 5. Rủi ro cụ thể

### 5.1. Đường găng phụ thuộc dự án beta 3 sao

Nếu `agent-sdk` đổi API, mọi prompt của P01–P06 phải sửa. Đó là **rủi ro quy trình**, không phải
rủi ro kỹ thuật.

**Giảm thiểu:** dùng nó **offline**, sinh prompt/trace, **commit kết quả** — không phải gọi nó ở
CI. Như vậy API đổi chỉ ảnh hưởng lần sinh sau, không làm đỏ build.

### 5.2. Trace có thể chứa nội dung không được commit

`trace` ghi lại **prompt đầy đủ**. Repo này có luật cứng: không commit PII, khoá API, địa chỉ ví
thật ([`AGENTS.md` §Phạm vi ngoài repo](../../AGENTS.md)). Một trace chứa lệnh `grep` trên dữ
liệu thật có thể mang theo dữ liệu thật.

**Giảm thiểu:** trace phải qua `check_doc_refs.py` + một bộ lọc PII **trước** khi commit. Nếu
không làm được, **không commit trace** — chỉ commit **bản tóm tắt** (đường đi + chi phí + tệp đã
đọc).

### 5.3. Ngôn ngữ: SDK là tiếng Anh, quy trình là tiếng Việt

`stages`, `flows`, `lobes` là **cấu trúc trong code**; checklist gate là **văn bản tiếng Việt có
người ký**. Không nên dịch tên kỹ thuật (đúng [`AGENTS.md` §Văn phong](../../AGENTS.md)), nhưng
phải giữ **một** bản checklist — không sinh bản thứ hai từ prompt.

---

## 6. Đề xuất thứ tự thực hiện

| Bước | Việc | Điều kiện tiên quyết |
|---|---|---|
| **1** | Viết `docs/00-framework/prompts/` cho P02–P06, **theo cấu trúc** lobe/stage/flow của PreAct — **không cần cài SDK** | PO đồng ý cấu trúc |
| **2** | Thử trace trên **một** gate (P05, vì nó đã có checklist đầy đủ nhất), offline, commit bản tóm tắt | Bước 1 |
| **3** | Quyết định có nâng Python 3.12 cho CI hay không | Chỉ khi bước 2 cho thấy giá trị |

**Bước 1 làm được ngay và không có rủi ro** — nó chỉ là cách viết prompt. Đó là phần tôi đề
nghị trước.

---

## 7. Quyết định cần PO

| Mã | Câu hỏi |
|---|---|
| **Q56** | Áp dụng **cấu trúc** PreAct (lobe/stage/flow) cho prompt P02–P06 — không cài SDK? |
| **Q57** | Có commit `trace` của lượt sinh artifact vào `docs/gates/P0x-trace/` không? (nếu có, cần bộ lọc PII trước) |
| **Q58** | Có nâng Python 3.12 cho toàn bộ CI để dùng SDK được không? (chỉ cần nếu muốn chạy tự động) |

---

## 8. Tự phê bình

1. **Tôi chưa chạy `agent-sdk` lần nào.** Toàn bộ đánh giá dựa trên README, `agent-sdk:docs/building-a-harness.md`,
   và metadata GitHub. `demo/` thực tế có thể khác tài liệu.
2. **`pip install agent-sdk` → 404 là kiểm được và rõ ràng**, nhưng có thể package phát hành dưới
   tên khác mà README không nêu. Tôi thử 4 tên phổ biến, không thử hết.
3. **Tôi không đọc `agent-sdk:docs/api.md`, `agent-sdk:docs/preact.md`, `agent-sdk:docs/concepts/*`** — chỉ đọc README và
   `building-a-harness.md`. Kết luận về mô hình dựa trên mô tả, không dựa trên đặc tả đầy đủ.
4. **§3 là phán đoán của tôi**, rằng `trace` là giá trị lớn nhất. Có thể PO thấy giá trị ở
   `metacognition` (tự kiểm) hoặc `intent` routing thay vì trace. Tôi không có dữ liệu để so.
5. **Tôi không đề xuất đánh số ADR-0026 ở §0** vì đây **là** ADR-0026 — nhưng nếu PO ký thì phải
   thêm vào `docs/08-adr/llms.txt` và một tài liệu phải dẫn nó (nếu không `check_doc_refs.py`
   sẽ báo ADR mồ côi ở lượt `check_adr_refs.py` kế tiếp).
6. **Đây là ADR thứ hai tôi đề xuất trong hai lượt** (sau ADR-0025 của phiên trước). Cần tự hỏi:
   quy trình có đang sinh ADR nhanh hơn khả năng ký không? Sáu gate P01–P06 **chưa cái nào được
   ký**. Thêm một ADR `Proposed` vào hàng đợi có thể là **nghịch lý**: dùng công cụ của quy trình
   để tạo thêm việc cho quy trình.
