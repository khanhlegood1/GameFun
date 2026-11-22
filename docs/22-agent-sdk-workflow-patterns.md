# `nccasia/agent-sdk` — mẫu quy trình dùng được, và chỗ không nên dùng

> **Tài liệu sống:** `docs/22-agent-sdk-workflow-patterns.md`
> **Trạng thái:** `SCOPING`
> **Ngày:** 22/11/2026
> **Nguồn:** `github.com/nccasia/agent-sdk` — `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `docs/concepts/10-plugins.md`, `13-task-execution-mode.md`, `16-stateless-serving.md` (truy cập 22/11/2026)
> **Câu hỏi:** SDK này áp dụng được gì vào **quản lý quy trình** của Game9K?
> **Liên quan:** `docs/18` §1.2 (cấu hình có `sha256`), `docs/17` §2.1 (đua tất định), `docs/19` §4.3 (số liệu tính lại được), `docs/21` §7 (kill switch)

---

## 0. Kết luận trước

**Đây là một repo kỹ thuật nghiêm túc, và nó có ích cho Game9K — nhưng ở tầng *quy trình*, không phải tầng *sản phẩm*.**

### 0.1. Sự thật về repo *(quan sát trực tiếp, GitHub API)*

| | |
|---|---|
| Ngôn ngữ / giấy phép | Python **`3.12+`** · **Apache-2.0** (có `NOTICE`) |
| Tạo / đẩy cuối | **13/06/2026** / **24/09/2026** |
| Sao / fork | **`3`** / **`1`** |
| Trạng thái tự khai | **"Beta"**, `270+` test |
| Quy mô nội bộ | kernel `agent_sdk/engine.py` **~`72` KB**; mạng mặc định **`18` lobe, `8` path** |

> ⚠️ **`3` sao và trạng thái beta** là dữ kiện, không phải đánh giá. Nhưng nó nói rõ: **không phải nơi đặt hệ thống quyết định tiền.**

### 0.2. Phán quyết

| | Nội dung |
|---|---|
| ❌ **Không** | Dùng SDK này làm engine quyết định `verified_play`, `work`, hay giải ngân. Lý do ở §2 |
| ✅ **Có** | Năm **mẫu quy trình** trong §1 áp dụng được **ngay**, không cần cài một dòng Python nào |
| ✅ **Đáng chú ý nhất** | Chính repo này **đã kiểm chứng độc lập** hai quyết định của Game9K: **cấu hình bất biến** và **tính tất định** |

---

## 1. Năm mẫu quy trình áp dụng được

### A1 — Bất biến phải do **test** canh, và *"vi phạm = hồi quy, không phải đánh đổi"*

Đây là câu mạnh nhất trong cả repo:

> *"These are load-bearing properties of the SDK. A change that violates one is a **regression, not a trade-off**."*

Và mỗi bất biến có **một test file canh nó**: leaf isolation → `tests/test_sdk_isolation.py`; default-network parity → `tests/test_lobe_network.py`.

**Game9K đang thiếu đúng chỗ này.** `AGENTS.md` có 7 quy ước văn phong + luật số liệu, nhưng **toàn bộ là văn xuôi**. Không có test nào canh.

| Luật trong `AGENTS.md` | Canh được bằng máy? |
|---|---|
| Con số phải gọi tên nguồn | ✅ **Có** — quét `docs/*.md` tìm `$`/`%` không kèm `§` hoặc link |
| Không dùng "sẽ sớm", "gần như chắc chắn", "dẫn đầu thị trường" | ✅ **Có** — danh sách từ cấm |
| Số bảng `CREATE TABLE` phải là `34` | ✅ **Có** — `grep -c` (đã kiểm bằng tay nhiều lần) |
| Liên kết không chết | ✅ **Đã có** — `check_docs_links.py` |
| Một ý một câu (`> 35` từ thì tách) | ⚠️ Được, nhưng dễ báo sai — để mức **cảnh báo** |
| Kết luận trước | ❌ Không máy nào canh được |
| Trích dẫn phải có **loại** | ⚠️ Một phần — đếm được số dòng bảng nguồn có cột "loại" |

> **Việc cần làm:** `scripts/check_agent_rules.py`, thêm làm bước thứ 5 trong `.github/workflows/docs.yml`. Rẻ, và biến `AGENTS.md` từ **lời khuyên** thành **cổng**.

### A2 — "Năng lực mới là **một dòng registry**, không phải một nhánh interpreter"

> *"New capability is a registry row, not an interpreter branch."*

Đây là nguyên tắc chống **phình kernel**. Game9K có phiên bản tương đương trong tài liệu, nhưng chưa nói thành luật:

| Chỗ | Trạng thái |
|---|---|
| Thêm tài liệu mới | ✅ Đã là "một dòng" — bảng `README.md` + `llms.txt` (`docs/12`–`docs/22` đều làm vậy) |
| Thêm một cổng CI | ⚠️ Hiện là **sửa `docs.yml`** — tức là sửa file trung tâm mỗi lần |
| Thêm một hằng số kinh tế | ❌ **Không** có registry — `W`, `H`, `50/50` nằm rải trong Markdown + script |

> **Đề xuất vừa phải:** một tệp `docs/params.yml` cho các tham số số học (`W=0.60`, `H=180`, epoch `7`, `eCPM $1–$3`, `50/50`, `34` bảng), **sinh** bảng trong tài liệu từ nó, và CI so `params.yml` với script. Đây là **điều kiện** để làm được `docs/18` §1.2 (cấu hình có `sha256`) mà không phải sửa tay nhiều nơi.

> ⚠️ **Không làm ngay.** Đây là refactor lớn (chạm `WHITEPAPER`, `PRD`, 4 script, 4 PDF). Ghi nhận, để sau `S1`.

### A3 — Bench phải **sống**, không được stub

> *"Benches are **live-only** (no LLM stubs — a stubbed bench is an integration test)"*

Phân biệt này rất đúng và Game9K nên chép nguyên:

| Loại | Là gì | Game9K đang có |
|---|---|---|
| **Test** (stub) | Kiểm một hàm cho đúng | ✅ `verify_pop_decay`, `verify_protocol_math`, `check_pitch_deck` |
| **Bench** (sống) | Đo **hành vi thật** với **đầu ra kiểm chứng được** | ❌ **Chưa có** |

**Điều này nói thẳng ra một khoảng trống:** toàn bộ `143/143` link, `11/11` bất biến, `100%` toán học đều là **test**, không phải **bench**. Chúng chứng minh tài liệu **tự nhất quán**, **không** chứng minh mô hình **đúng ngoài thực tế**.

> **Bench đầu tiên cần có** — và nó **không** cần SDK: **một làn sóng người chơi thật, đo D1/D7 và tỉ lệ phiên bị lọc oan.** Đúng thứ `docs/16` §5.1 đã đòi trước khi nói tới KOL.

### A4 — Mỗi lượt phải để lại **trace có cấu trúc**, đọc được

agent-sdk: mỗi lượt phát ra trace (*path, prompts, activations, tools, cost*) và có **viewer HTML**.

Game9K cần đúng thứ đó, nhưng cho **tiền**:

| Hiện tại | Cần |
|---|---|
| `verified_play` quyết định `work` | ❌ Không ai xem được **vì sao** một phiên bị loại |
| `audit_logs`, `sybil_risk_score` có | ⚠️ Có dữ liệu, **không** có bản trình bày |
| Người chơi thấy "bị lọc" | ❌ Không thấy lý do (`docs/15` §3-A3 đã nêu) |

> **Việc cần làm:** một **trace quyết định** cho mỗi epoch/người chơi: phiên nào được tính, phiên nào bị loại, **lý do**, và **tổng `work`** — dạng JSON + một trang đọc được. Đây là cùng một đối tượng phục vụ **ba** nhu cầu: khiếu nại của người chơi, kiểm toán của nhà đầu tư, và `docs/19` §4.3 (số liệu tính lại được).

### A5 — **Config bất biến · State một JSON** — mẫu khớp nhất

agent-sdk tách một agent đang chạy thành hai nửa:

```
CONFIG (bất biến, dùng chung)     STATE (mỗi phiên, MỘT JSON)
  mạng lobe/stage/flow              history, summary, facts, context
  trọng số, ngân sách, plugin       skills_in_use, meta_flow_bias, memory
  client LLM                        → SessionState.to_json()
  → dựng một lần, dùng lại          → load là dựng lại được; save là offload
```

Và hệ quả họ nêu: **"worker chỉ là một hàng đợi: load → turn → offload"**. Bất kỳ worker nào phục vụ bất kỳ phiên nào; khởi động lại không mất gì.

**Game9K có thể dùng y hệt, không cần SDK:**

| | Nội dung |
|---|---|
| **Config** | `W`, `H`, epoch `7`, trần paymaster, danh sách rule chống bot — **bất biến trong một epoch**, có **`sha256`** (đúng `docs/18` §1.2), công bố trước |
| **State** | **một JSON mỗi phiên chơi**: seed, danh sách lệnh, `input_entropy`, kết quả. Chính là ván đua tất định ở `docs/17` §2.1 |
| **Hệ quả** | Server không giữ kết nối; Worker/Edge đọc-ghi một dòng; **kill switch dừng được giữa lượt** (`docs/21` §7) |

> **Đây là chỗ hai tài liệu độc lập gặp nhau.** agent-sdk viết cho agent LLM; `docs/17` viết cho game đua. Cùng một cấu trúc. Đó là dấu hiệu cấu trúc đó **đúng**.

---

## 2. Ba mẫu phải từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | Dùng SDK làm **engine quyết định** `verified_play` / giải ngân | `3` sao, **beta**, `270+` test nhưng API *"may still shift before 1.0"*. Hệ thống quyết định tiền không đặt trên API còn đổi |
| **R2** | Dùng **LLM classifier** cho phân loại ảnh hưởng tới tiền | Chính repo này đặt **bất biến #4**: *"Determinism in the core — never an LLM judging the pipeline."* Với Game9K, mọi thứ chạm `work`/Tier phải **tất định** |
| **R3** | Port repo sang `uv` + `ruff` + Python `3.12` | Script hiện tại chạy `python3` stdlib trên CI `3.12` **đã ổn**. Đổi toolchain là **rủi ro byte-identical PDF** — thứ đang là điểm mạnh nhất của repo. Không đáng |
| **R4** | Vendor mã nguồn vào repo | Apache-2.0 **cho phép**, nhưng `3532` KB mã Python để lấy 5 mẫu quy trình là đánh đổi sai. Đọc, ghi lại mẫu; không chép |

---

## 3. Đối chiếu: Game9K mạnh hơn ở đâu, yếu hơn ở đâu

| Khía cạnh | agent-sdk | Game9K | |
|---|---|---|---|
| Bất biến do test canh | ✅ 5/5 | ⚠️ 4/7 luật canh được, **0** đang được canh | **Yếu** |
| Tất định | ✅ tuyên bố, có test parity | ✅ **mạnh hơn** — PDF trùng byte | **Mạnh** |
| Bench sống | ✅ có, sống-only | ❌ chưa có | **Yếu** |
| Trace đọc được | ✅ trace + viewer HTML | ❌ chưa có | **Yếu** |
| Cấu hình có `sha256` | ✅ `spec()` serialize được | ⚠️ có `base_sha256` cho **bản dựng**, **chưa** cho **tham số PoP** | Trung bình |
| Cổng CI | ✅ pytest + ruff | ✅ 5 bước + byte-identical | **Ngang** |
| Quy mô / độ chín | ❌ beta, `3` sao | — | Không so được |
| Tài liệu cho tác nhân AI | ✅ `CLAUDE.md` 12.756 B | ✅ `AGENTS.md` + `llms.txt` | **Ngang** |

---

## 4. Việc **không** làm trong tài liệu này

- Không cài, không chạy, không nhập SDK. Không thêm phụ thuộc Python nào.
- Không đổi `.github/workflows/docs.yml`, `AGENTS.md`, `docs/02` (**34** bảng), whitepaper, deck, 4 PDF.
- Không refactor `params.yml` — ghi nhận ở §A2, để sau `S1`.
- Không đánh giá repo này như một khoản đầu tư hay một đối thủ.

## 5. Thứ tự thi công

| # | Việc | Vì sao trước | Công sức |
|---|---|---|---|
| **1** | **`scripts/check_agent_rules.py`** — canh 3 luật máy kiểm được của `AGENTS.md`, thêm bước 5 vào CI | §A1 — biến lời khuyên thành cổng | Nhỏ |
| **2** | **Trace quyết định** cho `verified_play` (JSON + trang đọc) | §A4 — phục vụ 3 nhu cầu cùng lúc | Vừa |
| **3** | **Bench sống đầu tiên**: một làn sóng thật, đo D1/D7 + tỉ lệ lọc oan | §A3 — thứ duy nhất chứng minh mô hình đúng | Trung bình |
| **4** | Chốt **config bất biến + state một JSON** thành đặc tả | §A5 — điều kiện cho `docs/17` §2.1 và `docs/21` §7 | Trung bình |
| **5** | `params.yml` sinh bảng tham số | §A2 — chỉ sau khi 1–4 ổn định | Lớn |
