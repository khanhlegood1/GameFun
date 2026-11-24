# ADR-0039 — Hermes Agent + `hermes-plugin-e2b` cho quy trình dev: **sandbox cho tác nhân**, không phải quy trình tự động

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) · [`ADR-0036`](ADR-0036-hai-nguon-e2b-agent-va-contract.md) · [`ADR-0034`](ADR-0034-ho-so-sandbox-cho-game-ben-thu-ba.md) · [`sandbox-profile.mjs`](../../portal/lib/sandbox-profile.mjs) · [`AGENTS.md`](../../AGENTS.md) · **Q62a**

> Nguồn: [`e2b-dev/hermes-plugin-e2b`](https://github.com/e2b-dev/hermes-plugin-e2b) ·
> [`NousResearch/hermes-agent`](https://github.com/NousResearch/hermes-agent).
> Đọc README + metadata qua GitHub API ngày 2026-11-23. **Chưa cài, chưa chạy, chưa gọi mạng.**

---

## 0. Trả lời ngắn

Câu hỏi: *"Tôi muốn áp dụng AI Agent Hermes tự động hoá vào quy trình dev của dự án này."*

**Hai nửa câu, và chúng khác nhau về bản chất:**

| Nửa | Đánh giá |
|---|---|
| **Sandbox cho tác nhân** (Hermes + plugin e2b: mọi lệnh shell chạy trong máy ảo dùng một lần) | ✅ **Đáng làm** — và repo này đã có **cùng một luật** ở chỗ khác |
| **"Tự động hoá quy trình dev"** (agent tự làm PR, tự sửa tài liệu, tự ký gate) | ❌ **Không** — `AGENTS.md`, `README` và `check_gates.py` đã cấm, bằng mã |

**Một câu:** plugin này làm cho **tác nhân an toàn hơn khi nó sửa repo**. Nó **không** làm cho tác
nhân **được phép sửa nhiều hơn**.

Đây không phải sự thận trọng của tôi — đó là cấu trúc của repo đã có từ trước:

> *"AI sinh artifact, con người ký gate."* — `README.md` dòng 56
> *"AI **không bao giờ** tự chuyển gate sang 🟢."* — `README.md` dòng 82

---

## 1. Plugin này thực sự làm gì

`hermes-plugin-e2b` là một **backend terminal** cho Hermes Agent. Nó **không** phải một agent, không
phải một quy trình, không phải một bộ prompt.

| Nó làm | Nó không làm |
|---|---|
| Đẩy mọi lệnh shell, đọc/ghi tệp, `execute_code` của agent vào một sandbox E2B | Không quyết định agent được làm gì |
| Giữ `E2B_API_KEY` ở máy chủ, không đưa vào sandbox | Không cấp quyền git, không tạo PR |
| Cách ly mạng (`allow_internet_access: false` ⇒ chặn toàn bộ egress) | Không kiểm nội dung agent sinh ra |
| Giữ trạng thái agent (`skills/`, `memories/`) qua các phiên | Không thay `check_*.py` |

Trạng thái thật của hai dự án (đo 2026-11-23):

| | `NousResearch/hermes-agent` | `e2b-dev/hermes-plugin-e2b` |
|---|---|---|
| License | MIT | **MIT** |
| Sao | 265,566 | **2** |
| Push gần nhất | 2026-11-23 (hôm nay) | 2026-10-23 |
| Commit | — | **13** |

Plugin là **MIT** — khác hẳn `awesome-ai-sdks` (`license: null`) và `awesome-ai-agents`
(CC BY-NC-SA) ở ADR-0037. Không có vấn đề license ở đây.

---

## 2. Điểm khớp thật: repo này đã có luật "không cấp cái chưa xin"

`portal/lib/sandbox-profile.mjs` ra đời cho **game của studio**, và lập luận ở đầu tệp đó áp dụng
nguyên vẹn cho **agent sửa repo**:

> *"Một sandbox là một hồ sơ khai báo trước (template), và mọi thứ không khai báo thì **không có**.
> Không phải 'chặn cái xấu', mà là 'không cấp cái chưa xin'."*

Plugin e2b làm đúng điều đó ở tầng hạ tầng:

- `allow_internet_access: false` ⇒ egress **deny-all**, không phải danh sách chặn.
- `secure: true` ⇒ giữ bảo vệ envd token của E2B.
- `E2B_API_KEY` **không** vào sandbox, và bị **strip** khỏi môi trường tiến trình con.
- Sandbox identity **bao gồm** thế bảo mật: siết `allow_internet_access` ⇒ **sandbox mới**, không
  lặng lẽ dùng lại sandbox đang chạy dưới chính sách cũ.

Điểm cuối là thứ repo này nên **học**, không chỉ dùng: nó là cùng một bài học với KVU-2 §1.4 —
một phép đo mà **cấu hình của nó thay đổi được** thì phải **khoá cấu hình vào danh tính**.

---

## 3. 🔴 Ba điều phải nói rõ trước khi PO quyết

### 3.1. "Tự động hoá" ở đây nghĩa là "agent chạy lệnh trong máy ảo", không phải "agent tự quyết"

Plugin chạy lệnh. Việc agent **có được phép chạy lệnh gì** là cấu hình của Hermes, không phải của
plugin. Và trong repo này, chữ ký gate, việc merge, và việc chuyển trạng thái gate là **việc của
người** — `check_gates.py` từ chối một gate tự khai `APPROVED`.

⇒ Áp dụng plugin **không** thay đổi luật nào. Nếu PO muốn nó thay đổi luật, đó là **ADR riêng**
và nó sẽ phải supersede ADR-0026 §4 + `AGENTS.md`. Tôi không đề nghị điều đó, và ADR này không làm
điều đó.

### 3.2. Plugin yêu cầu **Python 3.11+** — repo này chạy 3.11, nên **khớp** (khác ADR-0026)

ADR-0026 §2.2 ghi một chặn thật: `agent-sdk` cần Python **3.12+**, CI của repo chạy **3.11**.
Plugin e2b cần **3.11+** — tức **không** có chặn đó.

Nhưng plugin còn cần:

| Yêu cầu | Trạng thái trong repo này |
|---|---|
| `e2b>=2.46,<3` (Python SDK) | ❌ chưa có |
| `hermes-agent` bản có `register_terminal_environment_provider` | ❌ chưa có |
| `E2B_API_KEY` | ❌ chưa có |

⇒ Đây là **ba dependency mới của môi trường dev**, không phải của CI. Xem §5.

### 3.3. 🔴 Hermes gọi mạng từ máy dev — và **Q62a chưa được trả lời**

Đây là chặn **thật nhất**, và nó đã tồn tại từ trước ADR này.

**Q62a** (từ ADR-0029, nhắc lại ở ADR-0035 và ADR-0038): *"Có cho phép gọi mạng từ máy dev
không?"* — đến giờ **chưa ai trả lời**.

Hermes ở chế độ bình thường gọi mô hình qua mạng. Nếu Q62a trả lời **không**, toàn bộ §1 của ADR
này **không dùng được** — trừ khi chạy mô hình cục bộ, điều ADR này **không** giả định.

⇒ **ADR-0039 bị chặn bởi Q62a.** Tôi ghi điều đó ra thay vì viết một kế hoạch triển khai mà tôi
biết là không chạy được.

---

## 4. ✅ Việc nên làm, theo thứ tự, và việc KHÔNG nên làm

### 4.1. Nên làm — theo thứ tự tăng dần rủi ro

| Bước | Việc | Điều kiện | Rủi ro |
|---|---|---|---|
| **1** | Ghi lại **chính sách sandbox cho tác nhân dev** vào `AGENTS.md` — học từ `sandbox-profile.mjs` và từ `allow_internet_access: false`. Không cài gì. | Không | **Không** |
| **2** | Chạy Hermes + plugin **trên máy dev**, `container_persistent: false`, `allow_internet_access: false` khi tác vụ không cần mạng | Q62a = có | Thấp |
| **3** | Chỉ khi bước 2 cho thấy giá trị: cân nhắc `container_persistent: true` để giữ `skills/`/`memories/` | Bước 2 | Trung bình |

**Bước 1 làm được ngay và không cần Q62a** — nó chỉ là văn bản, và nó có giá trị kể cả khi không
bao giờ cài Hermes.

### 4.2. KHÔNG nên làm

| Thứ | Vì sao |
|---|---|
| Đưa Hermes vào **CI** | Cổng chặn merge phải offline và tất định. ADR-0026 §2 và ADR-0035 luật 2 đã ghi. Hermes gọi mô hình ⇒ không tất định, và tốn tiền mỗi lần chạy |
| Cho agent **quyền ghi vào `docs/`** rồi commit tự động | ADR-0026 §4: *"Agent có quyền ghi vào `docs/` là bỏ HITL gate."* Vẫn đúng |
| Cho agent **tự chuyển trạng thái gate** | `check_gates.py` đã từ chối; `README` dòng 82 đã cấm |
| Dùng `container_persistent: true` trên **máy thứ hai** cùng một tài khoản E2B | README plugin nói rõ: hai máy cùng một profile home **không** được hỗ trợ, và trên Windows/không có `flock` cũng vậy. Đây là giới hạn đã biết, không phải rủi ro lý thuyết |
| Coi "plugin MIT, 2 sao" là bằng chứng chất lượng | Nó MIT — tốt cho license. 2 sao, 13 commit, 1 tháng không push — **không** phải bằng chứng độ bền. Cùng lập luận ADR-0026 §5.1, áp cho plugin này |

---

## 5. Rủi ro cụ thể

### 5.1. Dependency chỉ dành cho máy dev, và nó không được rò vào CI

`e2b` (Python), `hermes-agent` (Python), `E2B_API_KEY` — **không** cái nào thuộc CI. Nếu chúng vào
CI, mọi PR sẽ cần một khoá bí mật và một mạng — đúng thứ hai luật của ADR-0029/0035 cấm.

**Giảm thiểu:** không thêm gì vào `.github/workflows/`. Không thêm `requirements.txt` ở gốc repo.
Nếu cần, để trong một thư mục dev riêng và ghi rõ nó **không** được CI đọc.

### 5.2. Sandbox không phải biên giới bảo mật tuyệt đối

Plugin tự nói rõ ba giới hạn:

- **Admission không atomic với launch.** Một command đã chạy thì vẫn chạy tiếp qua lần đồng bộ sau.
- **Cửa sổ không đóng được:** một tiến trình trong sandbox ghi vào `~/.hermes` **sau** ảnh chụp của
  recovery và **trước** lần push — ghi vào đường dẫn máy chủ **cũng có** sẽ bị ghi đè.
- **Approval prompt vẫn hiện** cho lệnh nguy hiểm (contract gap 2 của plugin), dù sandbox dùng một lần.

⇒ Sandbox giảm **bán kính thiệt hại**, không xoá nó. Không được viết tài liệu nói nó "an toàn".

### 5.3. Repo này cam kết **zero-dependency** ở hai chỗ, và cần nói rõ chỗ nào

`README.md` dòng 69 và 71 mô tả `demo/docsend/` và `portal/` là **zero-dependency**. Điều đó
vẫn đúng: `package.json` gốc chỉ có `pg`, và portal không import gì ngoài Node chuẩn.

Hermes là **công cụ của người dev**, không phải dependency của sản phẩm. Nhưng nếu ai đó đọc
"zero-dependency" rồi thấy `e2b` trong repo, câu cam kết đó mất nghĩa.

**Giảm thiểu:** nếu PO chấp thuận bước 2, phải ghi rõ trong `README` rằng Hermes là **công cụ dev**,
không phải dependency sản phẩm — và **không** commit `requirements-dev.txt` chứa nó vào đường mà
`npm test` hay CI đọc.

---

## 6. Bảy điều cần PO quyết

| Mã | Câu hỏi |
|---|---|
| **Q-ADR39-a** | Có làm **bước 1** (chính sách sandbox cho tác nhân dev vào `AGENTS.md`) không? — không cần Q62a, không cần cài gì |
| **Q-ADR39-b** | **Q62a**: có cho phép gọi mạng từ máy dev không? Nếu **không**, §4.1 bước 2 và 3 vô hiệu |
| **Q-ADR39-c** | Hermes là **công cụ dev**, không phải dependency sản phẩm — PO đồng ý ghi điều đó vào `README`? |
| **Q-ADR39-d** | Có chấp nhận `container_persistent: false` (sandbox mới mỗi phiên, mất `skills/`/`memories/` giữa các phiên) cho lần dùng đầu không? |
| **Q-ADR39-e** | Ai giữ `E2B_API_KEY`, và nó được đặt ở đâu? (Không được vào repo, không được vào CI) |
| **Q-ADR39-f** | Có cấm rõ ràng việc đưa Hermes vào `.github/workflows/` không? Tôi đề nghị **cấm**, bằng một dòng trong `AGENTS.md` |
| **Q-ADR39-g** | Plugin 2 sao / 13 commit / 1 tháng không push — PO có muốn một điều kiện "thử lại sau N tháng" trước khi phụ thuộc không? |

---

## 7. Ranh giới trung thực

- **Chưa cài, chưa chạy, chưa gọi mạng.** Toàn bộ hiểu biết về plugin đến từ README của nó và
  metadata GitHub API. Không có dòng nào trong ADR này là kết quả của một lần chạy.
- **E2B không xem xét hay xác nhận gì về Game9K.** API công khai, không quan hệ.
- **Không nói "AI tự động hoá quy trình dev"** trong bất kỳ tài liệu nào cho studio hay nhà đầu tư.
  Nói đúng: *"agent chạy lệnh trong sandbox dùng một lần, người vẫn ký gate."*
- **Không chép mã** từ plugin. ADR này không thêm dòng mã nào vào repo.
- **Bước 1 là phần duy nhất tôi đề nghị làm ngay**, và nó không phụ thuộc dự án nào bên ngoài.
