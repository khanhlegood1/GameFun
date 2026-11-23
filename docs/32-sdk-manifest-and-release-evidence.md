# Hồ sơ chứng cứ — danh sách văn xuôi thiếu cột nào, và Game9K cũng thiếu

> **Tài liệu sống:** `docs/32-sdk-manifest-and-release-evidence.md`
> **Trạng thái:** `SCOPING` — đánh giá + **đã dựng hồ sơ chứng cứ** (`sdk/game-sdk/MANIFEST.json`, `scripts/check_sdk_manifest.py`)
> **Ngày:** 22/11/2026
> **Đầu vào:** `github.com/lexuankhanh1612/awesome-ai-sdks`
> **Liên quan:** `docs/27` · `docs/28` (khoá hợp đồng) · `docs/29` (lỗi có tên) · `docs/31` (fork + `NOASSERTION`)

---

## 0. Kết luận trước

**Danh sách đó không có gì để chép — nó là `223` dòng văn xuôi, `11` mục, `4` tệp, không giấy phép, không phiên bản, không ngày.** Nhưng chính **cái nó thiếu** chỉ ra một lỗ hổng trong repo này, và cổng mới đã **bắt được một lỗi thật tôi vừa tạo ra ở vòng trước**.

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Repo đó là gì? | **Fork** của `e2b-dev/awesome-ai-sdks`; **`4` tệp**, `3,5` MB, **không có `LICENSE`**, `0`★ (§1) |
| **2** | Lấy gì? | **Không gì cho mã.** Lấy **hình dạng của thứ còn thiếu**: một dòng có *giấy phép · phiên bản · ngày · bề mặt* (§2) |
| **3** | Game9K thiếu gì tương tự? | `docs/28` ghi hash, `docs/29` ghi phiên bản, `CONTRACT.json` ghi luật — **ba nơi, không nơi nào kiểm nơi nào** (§2.2) |
| **4** | Đã dựng gì? | `MANIFEST.json` + `check_sdk_manifest.py`: **5 bất biến**, **13** kiểm tra (§3) |
| **5** | Nó bắt được gì? | **`docs/28` còn ghi hash cũ** trong khi SDK đã lên `0.2.0` — tôi đã quên cập nhật ở vòng `docs/29`. Đã sửa (§4) |
| **6** | Nới ngưỡng không? | **Không.** Sửa tài liệu cho đúng, và mở **một** ngoại lệ hẹp có ghi chép (§4.2) |

---

## 1. Repo — nhỏ, là fork, và **không có giấy phép**

| | |
|---|---|
| Quan hệ | `fork = true`; `parent` và `source` đều là **`e2b-dev/awesome-ai-sdks`** (**`1.241`**★, đẩy lần cuối `09/07/2026`, **`license = none`** ở cả hai) |
| Bản fork | **`0`**★ · tạo `23/11/2026` **`07:21:33Z`** · `pushed_at` `09/07/2026` (**trước** ngày tạo ⇒ metadata của lần fork) |
| Kích thước | **`4`** tệp: `README.md` · `CODEOWNERS` · `assets/…` · `3,5` MB (**chủ yếu là ảnh**) |
| Nội dung | **`223`** dòng, **`11`** mục. Mỗi mục = một heading cấp hai có dạng `Tên` kèm URL + một câu mô tả + khối `<details>` chứa link mạng xã hội |
| Cột dữ liệu | **`0`** — không một bảng Markdown nào (`grep -c '^|'` = `0`) |

> **Ba lần liên tiếp** ba repo `awesome-*` của cùng một tài khoản đều là **fork**: `fragments` (`docs/29` §1.1), `awesome-ai-agents` (`docs/31` §1), và repo này. Đó không phải trùng hợp — đó là **cùng một cách chọn nguồn**. Ghi ra để lần sau khỏi mất thời gian: **kiểm `fork` trước, đọc sau**.

### 1.1. Vì sao "không có cột" mới là điều đáng nói

Một danh sách văn xuôi trả lời được: *"có những SDK nào?"*. Nó **không** trả lời được: *"bản tôi đang `import` là bản nào, giấy phép gì, bề mặt ra sao, ai chịu trách nhiệm?"* — và đó là câu một studio hỏi **trước khi** thêm một dòng `import` vào game của họ.

Đó không phải lỗi của danh sách. Nó là **giới hạn của định dạng**: văn xuôi không có ô để trống.

---

## 2. Game9K thiếu đúng thứ đó — ở ba nơi khác nhau

### 2.1. Hiện trạng trước tài liệu này

| Nơi | Ghi gì | Ai kiểm? |
|---|---|---|
| `sdk/game-sdk/CONTRACT.json` | `major: 0`, `minor: 2`, 8 hàm, luật `compat` | `check_sdk_drift.py` (11 kiểm tra) |
| `sdk/game-sdk/game9k-sdk.js` | `var SDK_VERSION = '0.2.0'` | `check_sdk_drift.py` (so với khoá) |
| `docs/28` | hash bề mặt + khoá | **không ai** |
| `docs/29` | phiên bản `0.2.0` + mô tả thay đổi | **không ai** |
| `docs/03` §3 | 8 hàm (nguồn hợp đồng công khai) | `check_sdk.py` |

> **Khoảng trống:** `docs/28` và `docs/29` **không thuộc cổng nào**. Nếu ai bump khoá lên `0.3`, hai tài liệu đó thành sai và **không cổng nào đỏ**. Đây đúng là loại hỏng mà `docs/28` được viết ra để chống — và nó **tự mắc** ở tầng tài liệu.

### 2.2. Đã dựng: một dòng có cột

`sdk/game-sdk/MANIFEST.json` — `12` trường, mỗi trường **then chốt** có một lệnh tái lập:

```
name           @game9k/game-sdk
version        0.2.0
surface_hash   sha256:af63b9121f9c0c5a
license        Apache-2.0
built_from     sdk/game-sdk/game9k-sdk.js (bản tham chiếu trong repo, chưa phát hành npm)
compat         next_major (MAJOR 0)
evidence       5 lệnh tái lập
```

Và một khối `not_claimed` — **những điều hồ sơ này KHÔNG nói**: chưa phát hành npm, không có người dùng thật, `0.x` không kèm bảo đảm tương thích, số `gzip` đo trên bản trong repo chứ không phải trên CDN.

> **`not_claimed` là phần quan trọng nhất.** Một hồ sơ chỉ nói điều nó chứng minh được thì dùng được; một hồ sơ ngụ ý nhiều hơn thế là một quảng cáo.

---

## 3. Năm bất biến

```bash
python3 scripts/check_sdk_manifest.py            # 5 bất biến
python3 scripts/check_sdk_manifest.py --row       # in MANIFEST như MỘT DÒNG
python3 scripts/check_sdk_manifest.py --compare   # so định dạng với awesome-ai-sdks
```

```
SDK MANIFEST: PASS — 13 kiểm tra · 5 bất biến · @game9k/game-sdk 0.2.0
  · sha256:af63b9121f9c0c5a · 2 chỗ ghi hash + 1 chỗ ghi phiên bản trong docs/ đều khớp
```

| # | Bất biến | Nó bắt được gì |
|---|---|---|
| **1** | `surface_hash` trong MANIFEST = hash **tính lại** từ `CONTRACT.json` | Hash chép tay rồi quên cập nhật |
| **2** | `version` = `SDK_VERSION` = `MAJOR.MINOR` của khoá | Ba nơi lệch nhau |
| **3** | Mọi `sha256:<8+ hex>` và `MAJOR.MINOR.x` trong `docs/*.md` phải khớp hiện tại | Tài liệu lạc hậu — **đây là bất biến bắt được lỗi thật** |
| **4** | `license` cụ thể; `NOASSERTION`/`Other` bị **từ chối** | Đúng lỗi của cả ba repo `awesome-*` |
| **5** | Mỗi trường then chốt có một lệnh trong `evidence` | Một trường không có lệnh là một trường không ai kiểm |

---

## 4. Cổng bắt được lỗi thật — của tôi, ở vòng trước

### 4.1. Chuyện đã xảy ra

Lần chạy đầu tiên:

```
SDK MANIFEST: FAIL — 5 vi phạm
  - 28-…md: ghi `sha256:fa218660251cfabe` (hash cũ, lịch sử) nhưng hash hiện tại là `af63b9121f9c0c5a`
  - 28-…md: ghi khoá `0.1.x` (lịch sử) nhưng khoá hiện tại là `0.2.x`
```

Ở vòng `docs/29` tôi bump SDK `0.1.0 → 0.2.0` và **quên cập nhật `docs/28`** — tài liệu mô tả chính cơ chế khoá hợp đồng lại đang ghi **khoá cũ**. `check_sdk_drift.py` không thấy, vì nó chỉ đọc `CONTRACT.json` và mã, **không đọc tài liệu**.

> **Đây là lỗi thật, không phải lỗi giả định.** Nếu một studio đọc `docs/28` hôm nay, họ sẽ thấy một hash không tồn tại ở bất kỳ bản nào đang có.

### 4.2. Cách sửa — và một ngoại lệ hẹp, có ghi chép

Sửa `docs/28` về giá trị hiện tại. Nhưng tài liệu sống **phải kể được lịch sử bump** — nếu cấm mọi giá trị cũ thì `docs/28` không còn viết được câu *"`0.1.x` từng là `fa218…`"*.

Ngoại lệ: **một dòng có chữ `lịch sử`** được phép nêu giá trị cũ. Hẹp, có chủ đích, và **được ghi trong docstring của cổng**.

> Nhưng khi áp dụng, ngoại lệ đó lại **che** một dòng: *"Bản thân tài liệu này từng ghi hash `0.1.x` sau khi SDK đã lên `0.2.0`"* — câu đó có chữ "lịch sử" nên được bỏ qua, dù nó đang nêu giá trị cũ **không** kèm nhãn. Tôi đã **viết lại câu đó để không nêu giá trị**, thay vì mở thêm ngoại lệ thứ hai. Một ngoại lệ đủ dùng; hai ngoại lệ là bắt đầu nới.

### 4.3. Năm phép phá đã chạy thật

| # | Phá | Kết quả |
|---|---|---|
| 1 | `surface_hash = 'deadbeefdeadbeef'` | ❌ `≠ hash tính từ CONTRACT.json` |
| 2 | `license = 'NOASSERTION'` | ❌ `không cụ thể — CHƯA có quyền rõ ràng` |
| 3 | xoá `evidence.budget` | ❌ `trường đó không ai kiểm` |
| 4 | bump khoá `0.2 → 0.3`, không sửa tài liệu | ❌ **5** lỗi (hash + version + 3 tài liệu) |
| 5 | thêm một dòng ghi hash cũ vào `docs/30` | ❌ chỉ đúng dòng đó, đúng số dòng |

Phép phá 4 là **tái hiện lỗi thật ở §4.1** — và giờ nó đỏ thay vì im lặng.

### 4.4. Nói rõ giới hạn

Cổng này **không** kiểm nội dung kỹ thuật của tài liệu. Nó kiểm **ba giá trị có thể so**: hash, phiên bản, giấy phép. Một tài liệu có thể ghi hash đúng mà mô tả sai hoàn toàn — cổng sẽ xanh. Cùng giới hạn đã nêu ở `docs/30` §5.4 và `docs/28` §4: **cổng chỉ chứng minh điều nó đo**.

---

## 5. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Chép mục nào từ `awesome-ai-sdks` vào `docs/00` | §1 — fork, **không `LICENSE`**; và `docs/00` đã nhóm theo **vai trò**, đúng hơn nhóm theo **tên** |
| **R2** | Thêm `MANIFEST.json` cho **mọi** thứ trong repo (docs, PRD, deck) | Mỗi hồ sơ là một bản sao phải giữ đồng bộ. Chỉ **bản phát hành** mới cần — hiện có **một** |
| **R3** | Cho `not_claimed` thành tuỳ chọn | §2.2 — một hồ sơ không nói giới hạn của mình là một quảng cáo |
| **R4** | Dùng `license` của repo được đọc làm `license` của gói | §2.1 — `splice` MIT, ba repo `awesome-*` là `none`/`NOASSERTION`; gói của Game9K là **Apache-2.0** và đó là một **quyết định**, không phải hệ quả |

---

## 6. Việc **không** làm trong tài liệu này

- Không thêm phụ thuộc; không gọi mạng; không chép nội dung từ repo không giấy phép.
- Không sửa `docs/03` §3, `docs/PRD` §0, không đổi hợp đồng SDK (vẫn `0.2.0`, 8 hàm).
- Không đổi số đã kiểm (`12 KB`, `3,5 s`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không dựng lại 4 PDF.

## 7. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | `CHANGELOG.md` cho `sdk/game-sdk` — mỗi bump một dòng: `version · surface_hash · lý do` | §4.2 — thay vì rải lịch sử trong tài liệu, giữ **một** nơi; khi đó ngoại lệ "lịch sử" có thể bỏ hẳn |
| **2** | Khi `packages/game-sdk` thành thật (`M03`): thêm trường `npm_integrity` (hash của tarball) | §2.2 — `surface_hash` đo **hợp đồng**; tarball cần hash **riêng** |
| **3** | Nếu có gói thứ hai (`@game9k/api-client`), mỗi gói **một** MANIFEST — không gộp | §5 R2 |
| **4** | Không thêm ngoại lệ thứ hai vào bất biến 3 | §4.2 — ngoại lệ thứ hai là bắt đầu nới |
