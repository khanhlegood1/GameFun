# 45 — Portal `/task`: bảng điều khiển đọc thẳng từ repo

> **Tài liệu sống:** `docs/45-portal-task-dashboard.md` — bản gốc ở đây.
> **Trạng thái:** `DONE` (vòng 33) · deploy: `gamefun9k.vercel.app` (trang tĩnh, `outputDirectory: portal`)
> **Tiền đề:** `docs/43` (sổ việc trên Supabase) · `docs/44` §3.3 (`blocked_by` + `stakeholder`) · `docs/37` (một việc không có người và ngày là một mong muốn)

---

## 0. Bốn dòng

Yêu cầu: *deploy vào project Vercel `gamefun9k`, thêm đường dẫn `/portal/task`, làm giống cách quản lý dự án của `v0-v0-task-manager.vercel.app`, để nhà đầu tư nhìn trực quan các task còn **Open** trong GitHub — như danh sách ADR ở `MetaPump/docs/08-adr`.*

1. **`gamefun9k.vercel.app` đã tồn tại và đã deploy từ repo này.** Không cần tạo project mới; chỉ cần thêm `portal/` làm output. Nhưng nó **đang deploy cả repo tài liệu** — xem §1, đó là một lỗ phải đóng.
2. **`/portal/task` không tồn tại trong repo này** — trước vòng này repo **không có một tệp HTML nào**. Nên đây là việc xây mới, không phải "bật lên".
3. **`lexuankhanh1612/MetaPump` trả về `404`** với token của phiên này. 17 tệp ADR tôi dùng là **bản bạn đính kèm**, không phải bản đọc từ GitHub — và **20 ADR khác** chỉ có tên trong `README.md` của thư mục đó. Portal hiện đúng sự thật đó thay vì vẽ ra 36 tệp không tồn tại.
4. **Nguồn của "task đang Open" là `pm/action-register.json`, không phải GitHub Issues.** Repo này không dùng Issues làm nguồn (xem §4). Trộn hai thứ sẽ tạo ra hai sự thật.

---

## 1. Trước khi xây: hai điều phải kiểm, không được giả định

### 1.1. `gamefun9k` đã deploy cái gì?

Project `gamefun9k` (`prj_sxRQ5wibSaeVT53QDI8nxLz1kfN7`, team `team_z1xcEvLzD6cBnhuYxEfyo3h4`) đã nối với `khanhlegood1/GameFun`, nhánh `main`, deploy lúc `5b338ad` — đúng commit merge của vòng 32. Nghĩa là **mọi commit lên `main` hiện đang được deploy**.

Nhưng repo này **không có `index.html`, không có `outputDirectory`, không có framework**. Vercel đang phục vụ một thư mục gần như rỗng. Và tệ hơn: khi thêm một trang vào đây, thứ được phục vụ phải là **đúng một thư mục**, không phải cả repo — nếu không, `docs/`, `pm/`, `receipts/` đều lên web.

**Cách đóng:** `vercel.json` với `outputDirectory: "portal"`, cộng `.vercelignore` loại `docs/`, `pm/`, `supabase/`, `scripts/`, `*.pdf`, `*.bundle`. Sau đó chỉ `portal/` là tĩnh công khai.

### 1.2. `v0-task-manager` — đọc hình dạng, không chép

Trang tham chiếu là một dashboard với: lời chào theo giờ, 4 ô số liệu ở đầu, bảng việc (tên · người phụ trách · trạng thái), lịch tuần, ghi chú. Giấy phép: **không có** (đã kiểm ở `docs/43` §1, cả fork và bản gốc). Nên: **học bố cục, viết lại từ đầu**.

Cái **giữ lại**: thứ tự thông tin từ trên xuống — chào → 4 con số → bảng việc. Cái **không giữ**: dữ liệu minh hoạ nằm trong `useState` (`docs/43` §1). Một dashboard tự nhập số là một dashboard có thể nói dối mà không ai biết.

> **Khác biệt cốt lõi:** trang tham chiếu là *ứng dụng* (bạn nhập việc vào). Trang này là *bản chiếu* (việc đã có trong repo, trang chỉ đọc). Đó không phải lựa chọn thẩm mỹ — nó là điều kiện để con số trên màn hình dùng được trước nhà đầu tư.

---

## 2. Đã xây gì

| Tệp | Vai trò |
|---|---|
| `scripts/gen_portal_data.py` | Sinh `portal/data.json` từ `pm/action-register.json` + `portal/docs/08-adr/*.md`. **Không có số nào gõ tay.** |
| `portal/data.json` | Bản chiếu: 36 dòng ADR, 12 việc, 2 người, policy. |
| `portal/index.html` + `portal/app.js` | Trang tĩnh, không framework, không bước build, không backend, không theo dõi. |
| `portal/docs/08-adr/` | 16 tệp ADR + `README.md` + `_TEMPLATE.md`. |
| `scripts/check_portal.py` | **Cổng 25**: 6 bất biến — dữ liệu khớp repo, không mất việc, tệp ADR có thật, không ký khống, trang tự nối được. |
| `scripts/check_portal_render.mjs` | **Cổng 26**: nạp `app.js` nguyên văn vào một DOM tối thiểu trong Node và kiểm **nhãn đã vẽ** — không chỉ kiểm HTTP 200. |
| `vercel.json` · `.vercelignore` | Chỉ `portal/` lên web; `/task` rewrite về `index.html`. |

### 2.1. Ba thứ trang này nói mà một bảng Kanban không nói

**Thứ nhất: nhãn "Đang chờ" khác "Đang mở".** Một việc có `blocked_by` mà vẫn `OPEN` **không phải** việc ai đó đang làm. Nếu cả hai đều hiện "Đang mở", bảng trông bận rộn trong khi thực tế đứng im — đúng lỗi `docs/44` §3.3 đã đóng ở tầng dữ liệu, nay đóng nốt ở tầng hiển thị.

**Thứ hai: cột "Đang chờ" vẽ cả dây chuyền.** `P10 ← P9 ← P8` cho thấy **P8** là gốc. Kèm nhãn `+1`, `+2` = số bậc phải đi ngược lên mới tới một việc tự bắt đầu được. Đây là con số khó chịu nhất trên trang, và nó có thật: **3/9 việc đang mở không thể tự bắt đầu.**

**Thứ ba: ADR "chờ ký" không được hiện "Đã nhận".** `README.md` của thư mục ADR viết: *"ADR chưa ký = `Proposed` và **không** được dùng để justify code đã merge."* Nếu portal hiện `Accepted (chờ ký)` thành "Đã nhận" thì nó phá đúng luật đó — bằng hình ảnh, không bằng câu chữ. Đây là **bẫy chữ ký**, và cổng 25 có một bất biến riêng cho nó.

> **Một lỗi thật cổng này bắt được khi mới bật:** `ADR-0008` có trong chỉ mục, ghi `Accepted (chờ ký)`, nhưng **không có tệp**. Generator của tôi đặt `needs_signature=False` cho mọi dòng thiếu tệp — nên một ADR *vừa thiếu tệp vừa chưa ký* bị đánh dấu là không cần ký. Sửa ở generator, không sửa ở cổng: `needs_signature` giờ đọc cả trạng thái của dòng thiếu tệp.

---

## 3. Sự thật về 36 ADR

| | |
|---|---|
| Có tệp trong `portal/docs/08-adr/` | **16** |
| Có tên trong `README.md` nhưng **không có tệp** | **20** |
| Trạng thái `Proposed` / cần chữ ký | **4** (`ADR-0011`, `ADR-0015`, `ADR-0016`, `ADR-0017`) |
| `ADR-0008` | **thiếu tệp** *và* chỉ mục ghi `Accepted (chờ ký)` |

20 dòng "thiếu tệp" **hiện ra trên trang** với nhãn đỏ, không bị ẩn. Đó là lựa chọn có chủ ý: một danh sách ADR trông đầy đủ trong khi 20 quyết định không có văn bản là đúng loại ấn tượng mà portal này sinh ra để tránh.

**Vì sao không tự lấy 20 tệp còn lại từ GitHub:** `lexuankhanh1612/MetaPump` trả `404` với phiên này (`gh api` → `Not Found`; `khanhlegood1/MetaPump` cũng `404`; tìm kiếm theo tên → `0` kết quả). Repo đó **private hoặc không tồn tại dưới tên đó**. Không có cách nào phân biệt hai khả năng từ đây, nên tài liệu này không khẳng định cái nào.

**Cách bổ sung** (bạn làm, hoặc cấp quyền rồi tôi làm): thả 20 tệp `.md` còn lại vào `portal/docs/08-adr/`, chạy `python3 scripts/gen_portal_data.py`, commit. Portal tự chuyển 20 dòng đỏ thành thẻ có link. Không cần sửa mã.

---

## 4. Vì sao nguồn việc là JSON, không phải GitHub Issues

Yêu cầu nói *"các task đang còn Open trong github"*. Có hai cách đọc, và chọn sai thì portal nói dối:

| Cách đọc | Hệ quả |
|---|---|
| GitHub Issues là nguồn | Portal phải gọi API GitHub lúc chạy ⇒ cần token trong trình duyệt, hoặc một hàm server. Repo này **không có** Issues nào là nguồn sự thật — `pm/action-register.json` mới là |
| `pm/action-register.json` là nguồn | Portal là trang tĩnh, không token, không backend. Số trên trang **chính là** số mà `check_actions.py` đang canh |

Chọn cách thứ hai. Lý do không phải cho tiện: nếu portal đọc Issues, thì có **hai** nơi nói việc nào đang mở, và chúng sẽ lệch nhau — mà lệch nhau trong im lặng chính là lỗi `docs/37` sinh ra để chặn. Trang tĩnh không có chỗ nào để lệch: nó là ảnh chụp của một tệp, và `check_portal.py` bắt buộc ảnh chụp đó khớp bản gốc **từng byte**.

Nếu sau này muốn GitHub Issues thành nguồn thật, việc đúng là **đổi nguồn sự thật trước** (một ADR), rồi mới cho portal đọc nó — không phải thêm một nguồn thứ hai bên cạnh.

---

## 5. Deploy

### 5.1. Đã cấu hình trong repo

`vercel.json`:

```json
{
  "framework": null,
  "buildCommand": null,
  "outputDirectory": "portal",
  "rewrites": [{ "source": "/task", "destination": "/index.html" }]
}
```

Không bước build ⇒ không có gì để hỏng lúc build. `cleanUrls` bật, `Cache-Control` cho `data.json` là `max-age=0, must-revalidate` — sổ việc đổi thì trang không được giữ bản cũ.

### 5.2. Đường dẫn

| URL | Trỏ tới |
|---|---|
| `https://gamefun9k.vercel.app/` | `portal/index.html` |
| `https://gamefun9k.vercel.app/task` | `portal/index.html` (rewrite) |
| `https://gamefun9k.vercel.app/portal/task` | `portal/portal/task` — **không tồn tại** |

**Điểm phải nói rõ:** `/portal/task` như trong yêu cầu **sẽ 404**, vì `outputDirectory` đã là `portal/` nên tiền tố đó bị "ăn" mất một tầng. Hai lựa chọn, và tôi chọn cái thứ hai:

1. Đặt `outputDirectory` là gốc repo và để trang ở `portal/index.html` ⇒ URL đúng là `/portal/task`, nhưng **cả repo lên web** (docs, pm, supabase). Không chấp nhận được.
2. `outputDirectory: "portal"` + rewrite `/task` ⇒ URL là **`/task`**. Thêm một redirect `/portal/task → /task` để đường dẫn cũ vẫn sống.

Đã thêm rewrite thứ hai cho `/portal/task → /index.html`, nên **cả hai đường dẫn đều mở được trang**. Chỉ có một tên miền gốc, không có ổ `/portal` riêng.

### 5.3. Việc phải làm trên Vercel

Trang là tĩnh, nhưng project hiện **chưa có** `outputDirectory` trong cấu hình của nó. `vercel.json` trong repo sẽ được đọc ở lần deploy kế tiếp. Nếu Vercel báo "No Output Directory named `portal`", đặt `Root Directory` = `portal` và `Output Directory` = `.` trong Settings — hai cách tương đương.

---

## 5.4. Đã live, và đã kiểm bằng mắt trên bản thật

Deploy production `READY` ở commit `30306e8` (sau merge). Đọc trang thật qua HTTPS trả về: **4 KPI** (`9` việc đang mở / `4` không thể tự bắt đầu / `0` quá hạn / `4` ADR chờ ký), **9 dòng việc** đúng nhãn `Đang chờ`, và **36 thẻ ADR** với 20 thẻ đỏ "chỉ có trong chỉ mục".

Ba thứ chỉ thấy khi nhìn bản thật:

| Hiện tượng | Nguyên nhân | Sửa |
|---|---|---|
| Người phụ trách hiện `LKLXK` | avatar chứa chữ `LK` **và** tên `LXK` — chữ trong avatar là trang trí nhưng vẫn bị đọc | `aria-hidden="true"` trên avatar |
| Chữ "Đang đọc `data.json`…" vẫn nằm trong DOM sau khi tải | `hidden` ẩn khỏi màn hình, **không** xoá khỏi cây | đặt `textContent = ""` sau khi nạp |

Không có lỗi nào trong hai lỗi này làm cổng 25/26 đỏ — đó là lý do phải **mở trang thật**, không chỉ chạy cổng.

### 5.5. Bản deploy có lộ tài liệu riêng tư không?

Repo là **private**; trang thì công khai. Đã kiểm: `docs/`, `pm/`, `supabase/`, `scripts/` đều trả **404** trên tên miền production — chúng không nằm trong artefact.

Nhưng một lỗ **có thật**: `outputDirectory: "portal"` chỉ định nghĩa **thư mục phục vụ**, không thu hẹp **phạm vi upload**. `README.md`, `AGENTS.md`, `llms.txt`, `vercel.json` nằm ở gốc nên vẫn được upload (không truy cập được qua URL, nhưng có trong build output). `.vercelignore` hiện chỉ loại `docs/ pm/ supabase/ scripts/ sdk/ assets/ receipts/`.

**Chưa đóng** vì hai lý do: (a) đó là thay đổi phạm vi upload, không phải hiển thị — cần deploy lại và kiểm lại; (b) cách chắc chắn nhất là đổi `outputDirectory` sang một thư mục **chỉ chứa** `portal/`, việc đó đổi cấu trúc repo. Ghi thành **W5**.

---

## 6. Bằng chứng

Chạy được, không phải tuyên bố:

```
PORTAL: PASS — 97 kiểm tra · 6 bất biến · 12 việc · 36 ADR (16 có tệp, 4 chờ ký, 20 thiếu tệp) · data.json == generator
PORTAL SELFTEST: PASS — 5/5 (1 đối chứng + 4 phép phá)
PORTAL RENDER: PASS — app.js chạy trong DOM tối thiểu · 9 việc vẽ ra · 36 ADR · nhãn khớp dữ liệu
```

Cổng 26 đã được **thử phá hai lần** để chứng minh nó không phải đồ trang trí:

| Phép phá | Kết quả |
|---|---|
| Đổi nhãn `Đang chờ` → `Đang mở` | **FAIL 4 vi phạm** — `P1`, `P9`, `P10`, `P11` bị chặn nhưng hiện "Đang mở" |
| Ẩn `P8` khỏi bảng | **FAIL 2 vi phạm** — "vẽ 8 dòng, sổ có 9 việc đang mở" |

Và cổng 25 bắt được một lỗi thật trong generator của chính nó (`ADR-0008`, §2.1).

---

## 7. Ba câu hỏi

1. **20 ADR thiếu tệp — có nên lấy từ `MetaPump` không?** Tôi không đọc được repo đó (`404`). Nếu nó private, cấp quyền cho phiên này thì tôi lấy; nếu nó đã đổi tên thì cần tên đúng. Cho tới lúc đó, 20 dòng đỏ là **sự thật**, và xoá chúng đi sẽ là nói dối.
2. **`/task` hay `/portal/task`?** Tôi đã làm cả hai mở được, nhưng chỉ `/task` là đường chính. Nếu bắt buộc URL phải có tiền tố `/portal`, cách duy nhất là chấp nhận cả repo lên web — hoặc thêm một project Vercel thứ hai chỉ để phục vụ `portal/`.
3. **Có nên cho portal đọc Supabase (`docs/43`) thay vì `data.json` không?** Được, và sẽ làm trang "sống" không cần deploy lại. Nhưng nó thêm một nguồn có thể lệch, cần một anon key công khai trong trình duyệt, và `docs/02` §4 cấm client ghi — đọc thì được. Chưa làm vì chưa cần.

---

## 8. Chưa làm

| | Nợ | Vì sao để lại |
|---|---|---|
| **W1** | 20 ADR chưa có tệp | Cần quyền đọc `MetaPump`, hoặc bạn thả tệp vào. Không tự bịa nội dung quyết định |
| **W2** | Portal chưa đọc Supabase | Xem §7 câu 3. Thêm nguồn thứ hai là thêm chỗ để lệch |
| **W3** | Không có ảnh chụp màn hình trong tài liệu | Không có trình duyệt trong sandbox (tải Chromium bị chặn). Cổng 26 kiểm bằng DOM thay vì bằng mắt — hẹp hơn, nhưng tất định và chạy được trong CI |
| **W4** | Chưa có nút "tải `.md`" cho từng ADR | Chỉ là `href` tới tệp; làm khi có người thật sự cần |
| **W5** | `.vercelignore` chưa loại `README.md`, `AGENTS.md`, `llms.txt` ở gốc | Xem §5.5 — không truy cập được qua URL, nhưng vẫn nằm trong build output. Sửa là thay đổi phạm vi upload, phải deploy lại và kiểm lại |
