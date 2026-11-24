# ADR-0037 — `awesome-ai-sdks`: **danh sách đó không có LICENSE**, và đó mới là điều đáng ghi

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0036`](ADR-0036-hai-nguon-e2b-agent-va-contract.md) · [`ADR-0016`](ADR-0016-license-compliance.md) · [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) · [`docs/10-opensource/README.md`](../10-opensource/README.md) · `.github/workflows/license.yml`

> Nguồn đọc: [`lexuankhanh1612/awesome-ai-sdks`](https://github.com/lexuankhanh1612/awesome-ai-sdks) —
> fork của `e2b-dev/awesome-ai-sdks`. Đọc để hiểu, **không chép**. Xem §6.

---

## 0. Trả lời ngắn

Câu hỏi tưởng là *"danh sách SDK này dạy được gì"*. Nhưng thứ đáng ghi nhất lại là
**trạng thái license của chính nó** — và trạng thái đó **khác** với repo anh em mà ADR-0036 vừa ghi.

| | `awesome-ai-agents` | `awesome-ai-sdks` |
|---|---|---|
| GitHub API `license` | `NOASSERTION` | **`null` — KHÔNG CÓ LICENSE** |
| Có tệp `LICENSE` | ✅ có (CC BY-NC-SA 4.0) | ❌ **không có** |
| Hệ quả pháp lý | NC + SA: hạn chế nhưng **đã nêu** | **All rights reserved** mặc định |
| Trong bảng license của repo | ✅ có (thêm ở ADR-0036) | ❌ **thiếu** |

Và điều quan trọng hơn: **`license.yml` không phát hiện được cả hai trường hợp.**
Xem §1.

**Về nội dung:** danh sách này là **danh mục sản phẩm**, không có kiến trúc, không có mã,
không có benchmark. Giá trị kỹ thuật trực tiếp: **gần bằng 0**. Không có gì để áp dụng vào
`portal/`, `scripts/`, hay `starter-kit/`. Xem §3.

---

## 1. 🔴 Lỗ hổng: CI không phân biệt được "có license" và "không có license"

`license.yml` kiểm ba thứ:

| Phép kiểm | Kiểm gì |
|---|---|
| `license-checker` | dependency npm có GPL/AGPL/SSPL/RSAL không |
| `cargo deny` | crate on-chain |
| `risky = [...]` | **bảy tên repo viết cứng** có xuất hiện trong cả `docs/10-opensource/README.md` **và** ADR-0016 không |

Cả ba đều không đọc **cột license trong bảng**. Nghĩa là:

- Thêm một repo **CC BY-NC-SA** vào bảng với nhãn `✅ Dùng` → **không bị chặn**.
- Thêm một repo **không có LICENSE** vào bảng với nhãn `✅ Dùng` → **không bị chặn**.
- Xoá cảnh báo của một repo NC/SA → **không bị chặn** (đã chứng minh ở ADR-0036 §1.1).

Đây **không** phải lỗi mới của ADR này — nó là cùng một lỗ hổng ADR-0036 đã nêu, chỉ lộ ra
lần nữa vì `awesome-ai-sdks` là ca **khó hơn**: không có `LICENSE` thì **không có gì để grep**.

### 1.1. Vì sao "không có LICENSE" nguy hiểm hơn "CC BY-NC-SA"

Trực giác thường nói ngược: *"CC BY-NC-SA có điều kiện, chắc rủi ro hơn"*. Với một repo **tài
liệu** thì không.

| | CC BY-NC-SA | Không có LICENSE |
|---|---|---|
| Được dùng phi thương mại | ✅ **được**, có điều kiện rõ | ❌ không được phép mặc định |
| Được trích dẫn ngắn | ✅ fair use / quyền trích dẫn | ✅ fair use / quyền trích dẫn |
| Đọc để học | ✅ | ✅ |
| Chép vào repo khác | ❌ trừ khi cùng license | ❌ **không có cơ sở nào để xin** |
| Người đọc biết mình đang ở đâu | ✅ **biết** | ❌ **không biết** |

Điểm cuối là điểm chính: một license **hạn chế nhưng rõ** thì người ta tuân được một license
**không tồn tại** thì không có gì để tuân. Với repo công bố cho nhà đầu tư, sự **không rõ** đó
là rủi ro, không phải sự nhẹ nhõm.

Repo này đã có luật đúng cho ca này từ trước — `docs/10-opensource/README.md` ghi
`arathianevasion/watson-games | Không có LICENSE | ❌ Không | Mặc định "all rights reserved"`.
Luật đã đúng; **CI không cưỡng chế nó**.

### 1.2. Quyết định

| Làm | Không làm |
|---|---|
| Thêm `awesome-ai-sdks` vào bảng license: `không có LICENSE` · `❌ Không (nội dung)` · chỉ đọc | Không coi "không có LICENSE" là "dùng tự do" |
| Ghi rõ nó **khác** `awesome-ai-agents` về license, để lần sau không ai gộp hai repo làm một | Không chép danh mục sản phẩm của nó vào tài liệu này |
| Đề xuất (chờ PO): phép kiểm đọc **cột license**, không đọc tên repo | Không mở rộng `risky` thêm tên — nó đã chứng minh không bảo vệ được |

---

## 2. Điều danh sách này XÁC NHẬN (không phải điều mới)

Đọc 2 chunk của `README.md` (toàn bộ danh sách): phần lớn mục là **sản phẩm thương mại đóng**
(AgentOps, Fixie) hoặc dự án tự khai **alpha** (*"currently in alpha, and is not yet ready for
production use"* — Chidori).

Đó đúng là điều [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) §2.4 đã kết luận khi
cân nhắc `nccasia/agent-sdk`: **API beta không nên nằm trên đường găng của quy trình**. Danh sách
này là **thêm một nguồn nói cùng điều đó** — không phải nguồn nói điều ngược lại.

Không có mục nào trong danh sách là thứ repo này **cần**: repo không chạy agent, không cần
observability cho agent, không cần framework orchestration. Xem ADR-0026 §4 (ba thứ không lấy).

---

## 3. Vì sao không áp dụng được gì về kỹ thuật

| Repo cần | Danh sách này có |
|---|---|
| Một thứ chạy trong CI, tất định, offline | ❌ phần lớn là SaaS đóng |
| Một thư viện để `import` | ❌ danh sách chỉ có link, không có mã |
| Một chuẩn để so artifact với code | ⚠️ có nhắc **Agent Protocol** (OpenAPI v3) — nhưng đó là ý tưởng, và ADR-0036 §3 đã bàn |

Điều duy nhất còn giá trị **đã được khai thác**: Agent Protocol = OpenAPI làm hợp đồng, và nó
dẫn thẳng tới phát hiện ba route production ngoài `openapi.yaml` ở ADR-0036 §3. Không lặp lại ở đây.

---

## 4. Ranh giới trung thực

- **e2b không xem xét, không xác nhận gì về MetaPump.** Danh sách công khai, không tạo quan hệ.
- **`awesome-ai-sdks` không có LICENSE** ⇒ mặc định all-rights-reserved. Không chép danh mục,
  không chép mô tả sản phẩm.
- **Không gọi repo này là "nguồn về AI SDK"** trong tài liệu công bố. Nó là danh mục sản phẩm
  do một nhà cung cấp (e2b) lập, có UTM tracking để đo referral — đó là mục đích của nó.
- **Không suy ra "AI SDK là xu hướng"** từ một danh sách do bên bán SDK lập. Xem [`nguyen-ly-don-vi-khanh-tang-hai.md`](../00-framework/nguyen-ly-don-vi-khanh-tang-hai.md) §5.

---

## 5. Câu hỏi mở

| | |
|---|---|
| **Q-ADR37-a** | ~~Có thay `risky` bằng phép kiểm **đọc cột license** (bắt NC/SA **và** "không có LICENSE") không?~~ **Đã làm** — xem §5.1 |
| **Q-ADR37-b** | ~~Repo có nên có luật: *mọi repo trong bảng license phải có `LICENSE` xác định được, hoặc ghi rõ "không có"*?~~ **Đã trả lời một phần** — đo 25 repo, thêm luật 5; phần còn mở xem §5.2 |

---

### 5.1. Q-ADR37-a — đã trả lời: làm, và đã làm

`risky` (bảy tên repo) **đã bị thay** bằng `scripts/check_license_table.py`. Phép
kiểm mới đọc **cột license**, nên ca của ADR này — `NOASSERTION` và "không có
LICENSE" — bị bắt theo **mẫu**, không theo tên. Thêm một repo không có LICENSE với
nhãn ✅ Dùng trong tương lai sẽ đỏ mà không ai phải nhớ thêm tên vào danh sách.

Đo lại bằng đột biến: đổi dòng `⚠️ KHÔNG CÓ LICENSE` thành `✅ Dùng` ⇒ đỏ. Gỡ cả
dòng đó khỏi bảng ⇒ đỏ hai lần (luật 4 và luật "phải còn một dòng nói rõ không có
LICENSE"). Ca §1 của ADR này giờ không tái diễn được trong im lặng.

### 5.2. Q-ADR37-b — đã trả lời một phần, bằng cách ĐO

Câu hỏi: *"mọi repo trong bảng phải có `LICENSE` xác định được, hoặc ghi rõ 'không có'"*.

Đã đối chiếu **25 repo** với `GET /repos/{owner}/{repo}` → `license.spdx_id` (2026-11-23):

| Kết quả | Số |
|---|---|
| Khớp | 21 |
| Không có LICENSE / `NOASSERTION` — API cũng `null` | 3 |
| **Lệch** | **1** |
| Đã kiểm tay từ trước | 1 |

**Chỗ lệch: `theshaneobrien/tickle`.** Bảng ghi `CC BY-NC-SA 4.0`; API trả `null`,
`/license` 404, **không có file `LICENSE`** — nhưng `README.md` dòng 185–187 ghi
`[CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/)`.

⇒ **"không có LICENSE" ≠ "không có license"**. README, badge, `package.json` đều có
thể là nơi tác giả khai báo. Điều này làm **yếu** chứ không phá kết luận §1: repo
`e2b-dev/awesome-ai-sdks` không có LICENSE **và** README cũng không nói gì — đã kiểm.

**Điểm đáng lo hơn con số 1/25:** chỗ lệch duy nhất rơi vào đúng một dòng mà **nhãn
vẫn tình cờ đúng** (❌ Không, vì NC). Nếu nhãn đã sai thay vì tình cờ đúng, **không
phép kiểm nào trong repo bắt được** — `check_license_table.py` kiểm *nhãn có hợp với
license đã ghi*, không kiểm *license đã ghi có đúng*.

Đã thêm vào `check_license_table.py`: luật 5, bắt buộc dấu `⚠️ *API: null*` trên
những dòng đã **đo** được là license không nằm trong file `LICENSE`. Danh sách là
tường minh, cùng lý do `REQUIRED_FAMILIES` ở luật 4 — bản đầu của luật 5 chỉ kiểm
dòng đang có, nên gỡ dấu là nó im lặng. Đây là lần **thứ ba** trong cùng tệp mắc
đúng lỗi đó.

**Phần CÒN MỞ:** luật 5 chỉ phủ những repo đã đo. Bảng vẫn cho phép thêm một repo
mới với license chép tay mà không ai đối chiếu API. Không có phép kiểm tĩnh nào bắt
được điều đó — nó cần **rà soát định kỳ có người ký**, không phải cổng CI (gọi API
từ CI cần token, dễ rate limit, và license **thay đổi được**).

---

**Trạng thái:** Proposed. `license.yml` **đã sửa** (Q-ADR37-a đã trả lời). Q-ADR37-b trả
lời được một phần bằng phép đo 25 repo (§5.2); phần còn mở là **rà soát định kỳ**, không
phải mã. Phát hiện §1 đã kiểm bằng GitHub API (`license: null`) và bằng cách đọc cây tệp.
