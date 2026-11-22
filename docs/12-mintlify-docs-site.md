# Mintlify cho Game9K — kiểm chứng hai repo và kế hoạch dựng docs site

> **Tài liệu sống:** `docs/12-mintlify-docs-site.md`
> **Trạng thái:** `SCOPING` — kế hoạch, **chưa** dựng site
> **Ngày:** 22/11/2026
> **Đối tượng:** `github.com/lexuankhanh1612/dev-portal` (fork của `chainstack/dev-portal`) và `github.com/lexuankhanh1612/Game9Kmintlify`
> **Câu hỏi:** lấy mô hình công ty + kỹ thuật từ hai repo này cho Game9K thì lấy được gì, và **phải sửa gì**?

---

## 0. Kết luận trước

| Nhận định | Trạng thái sau khi kiểm |
|---|---|
| Chainstack lập trình tài liệu rất tốt | **Đúng** — 2.140 file `.mdx`, `AGENTS.md` 10.768 B + `CLAUDE.md` 25.466 B làm hợp đồng, `docs.json` 234.516 B có redirect map + OpenAPI |
| XWG/Chainstack hỗ trợ **tiếng Việt** | **SAI** — `docs.json` của `chainstack/dev-portal` **không** có khoá `languages`/`i18n`; toàn bộ 2.140 trang là tiếng Anh. Phần "hỗ trợ tiếng Việt" trong câu hỏi **không có bằng chứng trong repo** |
| Founder Chainstack là người Việt | **Đúng là không** — Laurent Dedenis + Eugene Aseev, Singapore. Nhưng có một điểm cần sửa: **CEO hiện tại là Jan-Jaap Jager**, Dedenis là co-founder/Chủ tịch. Đừng viết "CEO" cho Dedenis |
| `Game9Kmintlify` là thứ để copy | **Không** — đó là **starter kit chưa sửa**: `"name": "Mintlify Starter Kit"`, `favicon.svg` mặc định, `index.mdx` vẫn là câu *"Welcome to your project"*, màu `#16A34A` mặc định, `LICENSE` MIT của template |

**Giá trị thật nằm ở repo thứ nhất** (`dev-portal`) — cụ thể là **hợp đồng cho tác nhân AI** (`AGENTS.md` + `CLAUDE.md` + `llms.txt`), chứ không phải giao diện.

**Và có một rào cản kỹ thuật thật:** repo Game9K hiện tại **không render được** trên Mintlify nếu chỉ copy sang — xem §3. Đó là phần tốn công nhất, và cũng là phần dễ bị bỏ qua nhất.

---

## 1. Điểm "mô hình công ty" — cái gì học được, cái gì không

### 1.1. Sửa lại thông tin về Chainstack

| Nội dung | Ghi nhận |
|---|---|
| Thành lập | 2018, Singapore — `CHAINSTACK PTE. LTD.`, UEN `201813548K` (đăng ký 20/04/2018) |
| Đồng sáng lập | **Laurent Dedenis** (co-founder, Chủ tịch) và **Eugene Aseev** (co-founder & CTO) |
| CEO hiện tại | **Jan-Jaap Jager** — không phải Dedenis |
| Đầu tư | ~`$6M` vòng Series A, nhà đầu tư nêu tên: SBI Ven Capital, Ventech, Azimut, Sygnum |
| Trụ sở/hub | Singapore (pháp nhân), hub London, Hong Kong, đội phân tán toàn cầu |
| Sản phẩm | Node/RPC quản lý cho 70+ mạng; tuyên bố SOC 2 Type II + ISO 27001 |
| Có yếu tố Việt Nam? | **Không tìm thấy bằng chứng** về founder người Việt. Việc có nhân sự DevRel/Marketing người Việt là **hợp lý nhưng chưa kiểm chứng** — không nên viết như sự thật |

### 1.2. Mô hình **học được** (và áp được cho Game9K ngay)

| # | Điều học được | Vì sao đúng với Game9K |
|---|---|---|
| **M1** | **Tài liệu là sản phẩm, không phải phụ lục.** Họ viết tài liệu cho người đọc *và* cho máy đọc | Game9K đã đi đúng hướng (`docs/07`), repo này đã có `llms.txt` + `AGENTS.md`. Chỉ thiếu **site** |
| **M2** | **`AGENTS.md` là hợp đồng, không phải lời chào.** Bản của họ 10.768 B, có mục "component usage", "style", "content boundaries" | `AGENTS.md` của Game9K đã có 3 luật bất khả xâm phạm + thứ bậc nguồn sự thật — **tốt hơn** ở phần số liệu, **yếu hơn** ở phần văn phong |
| **M3** | **Không dùng `languages`/i18n** — chọn một ngôn ngữ, viết cho tốt | Game9K đã chọn tiếng Việt. Giữ nguyên, **đừng** thêm i18n |
| **M4** | **Redirect map** trong `docs.json` (đổi URL cũ → mới, `permanent: true`) | Cần ngay khi tách `${doc}.md` thành nhiều trang: link cũ trong issue/PR không được chết |
| **M5** | **SEO + `contextual.options`** (`copy`, `chatgpt`, `claude`, `mcp`, `cursor`) | Rẻ, và làm tài liệu dùng được ngay trong IDE của dev |
| **M6** | **`<Info>` / `<Warning>` / `<Note>` thay cho câu văn dài** (492 chỗ dùng `<Info>` trong repo họ) | Tài liệu Game9K đang có nhiều đoạn "quan trọng:" dài 5 dòng — nên chuyển thành callout |

### 1.3. Điều **không** học được (và đừng thử)

| # | Nội dung | Vì sao không |
|---|---|---|
| **N1** | Mô hình kinh doanh của họ (SaaS hạ tầng, tính tiền theo request) | Game9K miễn phí cho người chơi; doanh thu từ phí on-chain + quảng cáo. Hai mô hình khác hẳn |
| **N2** | Quy mô tài liệu (2.140 trang) | Game9K có 16 tài liệu. Đừng nhân bản theo trang — **nhân bản theo người đọc** (người chơi / studio / lập trình viên / nhà đầu tư / luật sư) |
| **N3** | Fork `dev-portal` rồi sửa | Đó là tài liệu **của Chainstack** (không có LICENSE file → mặc định "all rights reserved"). Fork công khai để học thì được; **copy nội dung** thì không. Tên, logo, câu chữ đều là của họ |
| **N4** | `Game9Kmintlify` như hiện tại | Starter kit chưa sửa. Dùng làm khung thư mục thì được, nhưng phải thay **toàn bộ** nội dung, favicon, `docs.json`, `LICENSE` |

> **Lưu ý về bản quyền:** repo `chainstack/dev-portal` **không có file LICENSE** (kiểm bằng API: 404). Nghĩa là **không** có giấy phép mở. Ngược lại `Game9Kmintlify` có MIT License của template. Nếu muốn dùng thật, chọn hướng an toàn: **tự viết site mới**, chỉ học *cấu trúc* và *quy ước* — không copy file.

---

## 2. Điểm "kỹ thuật" — học gì từ `dev-portal`

| # | Kỹ thuật của họ | Áp cho Game9K | Ghi chú |
|---|---|---|---|
| **T1** | `docs.json` làm **một** nguồn cấu hình: theme, màu, logo, navbar, **navigation**, redirects, SEO | **ADOPT** | Bắt buộc nếu dùng Mintlify |
| **T2** | Frontmatter `title` + `description` **bắt buộc** trên mọi trang | **ADOPT** | Hiện tài liệu Game9K chỉ có `# H1`, không có `description` → phải sinh |
| **T3** | `AGENTS.md` + `CLAUDE.md` song song (cùng quy ước, hai định dạng cho hai công cụ) | **ADOPT (một phần)** | Game9K giữ `AGENTS.md` là nguồn duy nhất; thêm `CLAUDE.md` chỉ là symlink nội dung, tránh hai bản lệch nhau |
| **T4** | `llms.txt` ở root + **`llms.txt` lồng theo từng mục** + `llms-full.txt` | **ADOPT (một phần)** | Game9K đã có root `llms.txt`; thêm bản lồng khi site có ≥3 mục |
| **T5** | `<Info>`, `<Warning>`, `<Steps>`, `<Tabs>`, `<Card>`, `<Frame>` | **ADOPT** | Xem bảng chuyển đổi §3.3 |
| **T6** | OpenAPI spec nhúng (`openapi.json` 163 KB) để sinh trang API tương tác | **ADOPT — nhưng chưa có** | Game9K hiện chỉ có **bảng Markdown** cho `/api/v1` (`docs/03`), **không có** file OpenAPI. Đây là việc riêng, đáng làm, nhưng **không** chặn việc dựng site |
| **T7** | Trang `changelog.mdx` (40 KB) | **ADOPT (nhẹ)** | Game9K: changelog đã có trong git log; một trang tóm tắt theo mốc là đủ |
| **T8** | `mint broken-links` trong CI | **ADOPT** | Game9K đã có `check_docs_links.py` — giữ, và **thêm** bước chạy `mint broken-links` sau khi có site |
| **T9** | `npx mint@latest instructions` trước mọi việc Mintlify | **ADOPT** | Vì CLI đổi nhanh; đừng viết CI dựa trên ký ức |

---

## 3. Rào cản thật: tài liệu Game9K **không** render được trên Mintlify nếu copy nguyên

Đây là phần quan trọng nhất của tài liệu này. Đo trên 16 file `.md` hiện có:

| Đặc điểm | Số lượng | Mintlify (MDX) xử lý thế nào | Việc phải làm |
|---|---|---|---|
| **Mermaid** | **20 khối** (`flowchart LR/TB/TD`, `sequenceDiagram`, `stateDiagram`) | Hỗ trợ ```` ```mermaid ```` — nhưng **nhãn có `<br/>`** (dùng nhiều trong WHITEPAPER) là HTML trong Mermaid, vẫn chạy | Giữ; kiểm tra nhãn dài |
| **Toán `$$...$$`** | **48 khối** (44 trong YELLOWPAPER + 4 trong `04`) | Hỗ trợ KaTeX — nhưng **`{`, `}` trong công thức bị MDX hiểu là biểu thức JS** | **Bắt buộc** bọc `$$ ... $$` trong `{``}` hoặc chuyển sang component math; **1.168 cặp ngoặc** trong YP là bề mặt lỗi |
| **Toán inline `$...$`** | **782 chỗ** (598 YP, 165 WP, 18 `04`) | Như trên — rủi ro tương tự ở mức độ lớn hơn | Cần script kiểm + bọc |
| **Bảng Markdown** | **857 dòng** bắt đầu bằng `\|` | OK | — |
| **HTML thô** | `<br/>`, `<sup>`, `<b>` trong bảng và mermaid | MDX **chấp nhận** HTML thô, nhưng `<` không đóng thẻ sẽ làm **build fail** | Rà các chỗ `<` trong văn xuôi (ví dụ "nhỏ hơn 100ms") |
| **Không có frontmatter** | 16/16 file | Mintlify **không** tự lấy `# H1`; trang thiếu `title` sẽ hiện tên file | Sinh frontmatter từ H1 + một câu mô tả |
| **Ký tự `{` `}` ngoài toán** | nhiều trong code fence | Chỉ an toàn **trong** code fence; ngoài fence phải escape | Kiểm bằng build thật |

**Hệ quả:** việc "bê sang Mintlify" **không** phải copy-paste. Cần một bước **chuyển đổi có kiểm chứng** — và bước đó chỉ đáng làm khi có người thật sự đọc site.

### 3.1. Ước lượng công sức (không phải cam kết)

| Việc | Khối lượng |
|---|---|
| Sinh frontmatter cho 16 tài liệu | nhỏ — script một lần |
| Bọc 48 khối `$$` + 782 inline math an toàn cho MDX | **trung bình–lớn** — cần test render từng công thức |
| Chuyển 20 sơ đồ Mermaid | nhỏ |
| Tách 4 tài liệu dài thành nhiều trang (WP 231 bảng, YP 87 bảng) | **lớn** — và có rủi ro **phá vỡ liên kết chéo** đang được `check_docs_links.py` bảo vệ |
| Dựng `docs.json` navigation + redirect map | trung bình |
| CI: `mint broken-links` + build | nhỏ |

**Khuyến nghị:** làm **Phase 1 hẹp** — chỉ đưa 6 tài liệu "đọc để hiểu" lên site (PRD, 00, 01, 05, 06, 09); **để nguyên** WP/YP/`04` trên GitHub vì chúng là **bản in** (PDF đã có, đã tất định). Như vậy tránh đúng chỗ rủi ro cao nhất (1.168 cặp ngoặc toán) mà vẫn có site dùng được.

---

## 4. Kế hoạch 3 phase

| Phase | Nội dung | Điều kiện xong |
|---|---|---|
| **P0 — Hợp đồng** (rẻ nhất, làm ngay) | Thêm `description` vào frontmatter kế hoạch; chuẩn hoá callout `<Info>/<Warning>` trong 6 tài liệu Phase 1; thêm mục **"văn phong"** vào `AGENTS.md` (giọng, độ dài câu, cách viết số) | `check_docs_links.py` xanh; không đổi một con số nào |
| **P1 — Site hẹp** | Dựng site Mintlify với **6 tài liệu**, không toán nặng; `docs.json` + redirect map; bật `contextual.options`; CI `mint broken-links` | Build xanh; mọi link nội bộ cũ → mới có redirect; **không** trang nào lệch nội dung so với repo |
| **P2 — Mở rộng (tuỳ)** | Thêm OpenAPI thật cho `/api/v1` (hiện chỉ có bảng), rồi mới đưa trang API lên site; sau đó cân nhắc WP/YP | OpenAPI validate được; trang API sinh từ spec, không viết tay |

**Không làm ở bất kỳ phase nào:** copy nội dung từ `chainstack/dev-portal`; dùng `Game9Kmintlify` nguyên trạng; tách WP/YP thành trang web khi PDF đã là bản in chính thức.

---

## 5. Một điều đáng nói về "thị trường Việt Nam"

Tiền đề của câu hỏi — *"Chainstack đầu tư mạnh vào Việt Nam"* — **không kiểm chứng được từ repo**. Trong `dev-portal` không có i18n, không có trang tiếng Việt, không có nội dung riêng cho VN.

Điều này **không** làm luận điểm của bạn sai: Việt Nam đúng là thị trường Web3 lớn, và việc một công ty hạ tầng viết tài liệu tốt để hút dev toàn cầu là mô hình đúng. Nhưng nếu đưa nhận định này vào tài liệu gọi vốn hay bài nói, nó sẽ là **một khẳng định không có nguồn** — đúng loại thứ `AGENTS.md` cấm.

**Cách nói an toàn:** *"Chainstack là ví dụ về một công ty hạ tầng không phải gốc Việt nhưng đặt ưu tiên rất cao vào chất lượng tài liệu cho lập trình viên — thứ Game9K cũng phải làm."* Không cần khẳng định về VN.

---

## 6. Nguồn

| Nội dung | Nguồn | Loại |
|---|---|---|
| `dev-portal`: 2.140 `.mdx`, `AGENTS.md` 10.768 B, `CLAUDE.md` 25.466 B, `docs.json` 234.516 B, **không có** `languages`, **không có** LICENSE | GitHub API, 22/11/2026 | **Quan sát trực tiếp** |
| `Game9Kmintlify`: `"Mintlify Starter Kit"`, MIT, 8 file | GitHub API, 22/11/2026 | **Quan sát trực tiếp** |
| Chainstack: 2018, Singapore, UEN `201813548K`, founder Dedenis + Aseev, CEO Jan-Jaap Jager | Tracxn; nownodes.io; freehire.me | Bên thứ ba — **không** dùng làm số liệu tài chính |
| 20 mermaid / 48 `$$` / 782 inline math / 857 dòng bảng / 1.168 cặp ngoặc trong YP | Đếm bằng script trên repo này | **Tự đo lại được** |

> Không dùng số liệu doanh thu, định giá hay số khách hàng của Chainstack ở bất kỳ đâu trong tài liệu Game9K.
