# Sandbox không thuộc về SDK — nhưng **cách đặt tên lỗi** thì thuộc

> **Tài liệu sống:** `docs/29-sandbox-errors-and-sdk-boundary.md`
> **Trạng thái:** `SCOPING` — đánh giá 4 repo + **đã nâng SDK lên `0.2.0`** với lỗi có tên (`scripts/check_sdk_errors.py`)
> **Ngày:** 22/11/2026
> **Đầu vào:** `e2b-dev/code-interpreter` · `lexuankhanh1612/fragments` · `e2b-dev/open-computer-use` · `e2b-dev/runtime` (`docs/ARCHITECTURE.md`) · yêu cầu *"áp dụng vào sdk cho dự án này theo poki portal sdk"*
> **Liên quan:** `docs/27` (hợp đồng Poki) · `docs/28` (khoá hợp đồng) · `docs/03` §3+§4 · `docs/11`

---

## 0. Kết luận trước

**Ba trong bốn repo là hạ tầng chạy mã không tin cậy. Game9K cần đúng thứ ngược lại: chạy mã của người khác mà *không* cấp cho nó một máy.** Nhưng `e2b-dev/E2B` có một thứ đáng chép nguyên xi: **bảng lỗi phân biệt được**, và một thứ đáng chép *ngược*: **kiến trúc control-plane / data-plane tách rời của `runtime`**.

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Bốn repo làm gì? | `runtime` = control plane Firecracker + `envd`; `code-interpreter` = CLI/SDK cho sandbox; `open-computer-use` = agent điều khiển desktop; `fragments` = app sinh code (§1) |
| **2** | Dùng được không cho SDK cổng game? | ❌ **Không.** `game-sdk` chạy **trong** iframe đã bị sandbox; thêm một sandbox nữa là cấp thêm quyền, không bớt (§2) |
| **3** | Lấy gì? | **Bảng lỗi có tên**: `SandboxNotRunning` ≠ `SandboxUnreachable` — và họ **tự ghi giới hạn** của phép phân biệt đó (§2.3) |
| **4** | SDK Game9K đang hỏng gì? | `send()` trả `resolve(null)` khi hết giờ ⇒ **mọi kiểu hỏng thành "không biết"**, game không xử lý được (§3) |
| **5** | Đã sửa gì? | `0.1.0 → 0.2.0`: **4 hằng lỗi + 3 mã ở chỗ gọi**, `Promise.reject` thay `resolve(null)`, `cloudSave` kiểm `128 KB` **trước khi gửi** (§3.2) |
| **6** | Kiểm được gì? | `check_sdk_errors.py`: **4 bất biến**, **22** kiểm tra, **7** mã khai trong `CONTRACT.json` (§4) |

---

## 1. Nguồn — bốn repo, bốn mức liên quan

| Repo | Giấy phép | Sao | Kích thước | Nó là gì |
|---|---|---|---|---|
| `e2b-dev/runtime` | **Apache-2.0** | **`1.870`** | `105.115` KB · **`3.427`** tệp | Control plane + data plane: API, orchestrator Firecracker, `envd`, client-proxy |
| `e2b-dev/code-interpreter` | **Apache-2.0** | **`2.430`** | `2.591` KB · `123` tệp | **Template + tài liệu** cho sandbox "code interpreter"; SDK thật nằm ở `e2b-dev/E2B` |
| `e2b-dev/open-computer-use` | **Apache-2.0** | **`2.414`** | `1.560` KB · **`24`** tệp | Agent LLM điều khiển desktop sandbox (`sandbox_agent.py`, `grounding.py`) |
| `lexuankhanh1612/fragments` | **Apache-2.0** | **`0`** | `5.426` KB · `127` tệp | **Fork** của `e2b-dev/fragments` (Next.js app sinh code), `304` commit, commit cuối **`13/10/2026`** |

### 1.1. Repo thứ hai là **fork**, và bản gốc còn sống

`lexuankhanh1612/fragments` có `fork = true`, và README **vẫn là README của E2B** ("Fragments by E2B", "Make sure to give us a star!"), `CODEOWNERS` và `LICENSE` cũng nguyên của E2B. `api.github.com` ghi repo này `pushed_at = 18/11/2026` — **trước** commit cuối thật (`13/10/2026`), tức chỉ là metadata của lần fork.

> **Đừng trích nó như một dự án độc lập.** Nếu cần đọc `fragments`, đọc `e2b-dev/fragments` — cùng giấy phép, cùng nội dung, và **có người bảo trì**.

### 1.2. Một chỗ dễ sai: `code-interpreter` **không phải** SDK Python

Tôi tải `e2b-dev/code-interpreter` với kỳ vọng thấy SDK. Bên trong là **template** (`template/server/api/...`), ảnh Docker, và tài liệu; SDK Python/JS thật nằm ở **`e2b-dev/E2B`** (`packages/python-sdk/e2b/exceptions.py` — nơi tôi lấy §2.3). Ghi ra vì đây là loại nhầm sẽ khiến người sau đọc sai nguồn.

---

## 2. `runtime`: kiến trúc đáng học, nhưng **không** để chạy game

`docs/ARCHITECTURE.md` (**`118.397`** B) mô tả 6 service. Hai ý dẫn dắt thiết kế của họ:

> 1. *"A sandbox is a resumed snapshot."* — tạo sandbox = **khôi phục snapshot**, nên khởi động nhanh; trang bộ nhớ nạp lười qua `userfaultfd`, rootfs là overlay copy-on-write.
> 2. *"Control plane and data plane are separate."* — API quyết định sandbox chạy **ở đâu**; orchestrator trên mỗi node quyết định chạy **thế nào**.

### 2.1. Ý thứ hai **đúng** cho Game9K, và đã đúng sẵn

| `runtime` | Game9K (đã có) |
|---|---|
| API (control plane) + orchestrator (data plane) | `apps/worker` (control) + `workers/game-delivery` (data, Cloudflare R2) |
| "Sandbox traffic never passes through the API" | Byte của game **không đi qua** API; đi thẳng Edge Worker (`docs/05`, `docs/06` M03) |
| `envd` gRPC trong VM | `postMessage` giữa iframe và portal (`docs/03` §3) |
| Template = snapshot đã boot sẵn | `<vid>.play.<domain>` = bản build đã đóng gói sẵn, **không** khởi động máy |

> Game9K **đã** tách hai mặt phẳng. `runtime` chỉ xác nhận; **không** cần đổi thiết kế.

### 2.2. Ý thứ nhất **sai** cho một cổng game — và đây là ranh giới

Một sandbox Firecracker tồn tại để chạy **mã không tin cậy mà không phá máy chủ**. Game9K không chạy mã của studio trên máy chủ nào cả: nó **phục vụ tệp tĩnh** trong một origin riêng, và trình duyệt của người chơi là nơi mã chạy.

Ba lý do cụ thể, không phải "không cần":

1. **Không có gì để bảo vệ.** Mã game HTML5 chạy trong iframe **đã** bị cô lập bởi `sandbox` không `allow-same-origin` + origin riêng (`docs/03` §3). Thêm VM là **thêm** một lớp mà **không** bớt quyền nào của mã game.
2. **Nó phá lời hứa `3,5` giây.** `docs/PRD.md` KR1.1 hứa `p75 < 3,5 s` desktop. Khôi phục snapshot nhanh **với hạ tầng của họ**; tự dựng Firecracker + object storage + `userfaultfd` để phục vụ **tệp tĩnh** là trả giá khởi động cho một việc không cần khởi động.
3. **Nó thêm chỗ giữ bí mật.** `ARCHITECTURE.md` mô tả API key `e2b_`, JWT OIDC, JWKS admin, mTLS cho telemetry. Mỗi thứ là một bí mật phải quản. `AGENTS.md` đã chốt: **không** commit khoá; thêm một hệ thống khoá là thêm rủi ro, không thêm tính năng.

### 2.3. Thứ **đáng chép nguyên xi**: đặt tên lỗi, và nói rõ chỗ **không biết**

`packages/python-sdk/e2b/exceptions.py` (qua `e2b-dev/E2B`) tách hai trường hợp mà đa số SDK gộp làm một:

| Lớp | Nghĩa | Có thử lại được không |
|---|---|---|
| `SandboxNotRunningException` | Sandbox **đã chết** (bị kill / hết hạn) | **Không** — phải tạo lại |
| `SandboxUnreachableException` | Sandbox **có thể còn sống**, nhưng không tới được (mạng, `envd` chưa lên) | **Có thể** — phụ thuộc |

Và điều làm nó đáng tin — họ **tự ghi giới hạn** ngay trong docstring:

> *"The split … is only as good as the proxy's answer and the health probe: a sandbox that is gone but could not be asked about is a `SandboxUnreachableException`."*

> Đây là chuẩn `AGENTS.md` đòi: **"nêu rõ cái KHÔNG biết"**. Một SDK dám nói *"tôi không biết"* dùng được hơn một SDK luôn trả `null`.

### 2.4. `open-computer-use` và `fragments`: đọc để biết, không áp dụng

- **`open-computer-use`** (`24` tệp, `main.py` + `os_computer_use/*.py`) điều khiển **desktop** bằng ảnh chụp màn hình + mô hình grounding. Với một cổng game HTML5 thì **không áp dụng**: game9k không điều khiển UI của ai.
- **`fragments`** là app *sinh code rồi chạy trong sandbox*. Nó là **nguồn của một rủi ro** mà `docs/27` §6 R2 đã từ chối: nếu Game9K từng "sinh game bằng AI rồi phát hành", thì bước chạy thử bắt buộc phải là sandbox — **và đó là một sản phẩm khác**, không phải SDK.

---

## 3. Vậy SDK Game9K hỏng gì? — và đã sửa

### 3.1. Lỗi thật, tìm được khi đọc §2.3

`send()` (bản `0.1.0`) có đúng một nhánh thất bại:

```js
var timer = W.setTimeout(function () {
  if (!done) { done = true; delete pending[id]; resolve(null); }
}, 4000);
```

`resolve(null)` là **im lặng**: game không biết portal từ chối, portal treo, hay game đang mở ngoài iframe. Với `rewardedBreak`, điều đó nguy hiểm nhất — **game có thể đã phát quảng cáo** và câu trả lời bị mất, nên game hoặc cộng thưởng mù, hoặc không cộng dù người chơi đã xem xong.

### 3.2. Đã sửa trong `0.2.0`

| Trước (`0.1.0`) | Sau (`0.2.0`) |
|---|---|
| hết giờ → `resolve(null)` | hết giờ → **từ chối** với `sdk_timeout` |
| `window.parent === window` → treo 4 giây rồi `null` | → từ chối ngay với `sdk_no_parent` |
| portal trả `{__error}` → không có đường | → từ chối với `sdk_refused` + `reason` |
| `cloudSave.set` gửi rồi mới bị từ chối | kiểm **`128 KB` trước khi gửi**, mã `cloud_save_too_large` |
| `reportProgress` không chống trùng | gửi kèm `idem` để portal phát lại không cộng hai lần |

Bề mặt **8 hàm không đổi** — đây là `MINOR`, không phải `MAJOR`. `CONTRACT.json` lên `0.2`, hash bề mặt `sha256:af63b9121f9c0c5a`.

> **Bốn mã này không thay bảng §4 của `docs/03`.** §4 là bảng **lỗi REST** (`VALIDATION_ERROR`, `PAYLOAD_TOO_LARGE`…). SDK trong iframe **không bao giờ thấy mã HTTP**, nên nó cần một **mặt cắt** của bảng đó — không phải một bảng thứ hai độc lập.

---

## 4. Đã dựng: `check_sdk_errors.py`

```bash
python3 scripts/check_sdk_errors.py            # 4 bất biến
python3 scripts/check_sdk_errors.py --table    # bảng lỗi SDK ↔ HTTP
```

```
SDK ERRORS: PASS — 22 kiểm tra · 4 bất biến · 7 mã lỗi (4 hằng + 3 ở chỗ gọi)
```

| # | Bất biến | Nó bắt được gì |
|---|---|---|
| **1** | Mọi mã SDK dùng phải khai trong `CONTRACT.json` | Bịa mã lỗi riêng ngoài hợp đồng |
| **2** | Mọi mã khai phải **thật sự được dùng** | Tài liệu hứa một lỗi không tồn tại |
| **3** | `send()` không còn `resolve(null)` | Biến lỗi thành "không biết" |
| **4** | Không `Promise.reject(` ngoài `fail()` | Lỗi không có mã, game không phân biệt được |

### 4.1. Ba phép phá, và **một phép phá đã lọt** — rồi bị bịt

| # | Phá | Kết quả |
|---|---|---|
| 1 | đổi `fail('cloud_save_too_large')` → `'cloud_save_way_too_big'` | ❌ `gọi fail(...) nhưng CONTRACT.json không khai` |
| 2 | xoá `sdk_timeout` khỏi hợp đồng | ❌ `SDK dùng mã sdk_timeout nhưng không khai` |
| 3 | thay `fail(CODE.NO_PARENT…)` bằng `Promise.reject(new Error('x'))` | **✅ PASS — LỌT** |
| 4 | `resolve(null)` trong `send` | ❌ `send() còn resolve(null)` |

> **Phép phá 3 là phát hiện thật.** Bản đầu chỉ đọc mã trong `var CODE = {…}`, nên đổi một mã **ở chỗ gọi** lọt; và `Promise.reject` trực tiếp cũng lọt. Đã bịt **cả hai**: thêm vế "mã viết thẳng ở chỗ gọi", thêm bất biến 4, và **loại trừ chính thân `function fail()`** — chỗ duy nhất được phép `Promise.reject`. Chạy lại: 22 kiểm tra, cả 4 phép phá đều đỏ.

---

## 5. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Chạy `game-sdk` trong sandbox/VM | §2.2 — iframe **đã** là sandbox; thêm VM là thêm quyền, thêm chỗ giữ khoá, phá hứa `3,5 s` |
| **R2** | Thêm API key / JWT / mTLS vào SDK | `docs/27` §6 R2; `AGENTS.md` — không khoá trong repo, và SDK chạy trong iframe **của người khác** |
| **R3** | Trích `lexuankhanh1612/fragments` như dự án độc lập | §1.1 — là **fork**, README/CODEOWNERS/LICENSE vẫn của E2B |
| **R4** | Dùng `open-computer-use` để "test game tự động" | Nó điều khiển desktop bằng ảnh; Playwright + Inspector (`docs/01` SCR-07) đã đủ và **tất định** |

---

## 6. Việc **không** làm trong tài liệu này

- Không chép mã từ repo nào; `runtime` là Go + Firecracker, không liên quan ngăn xếp Cloudflare của Game9K.
- Không sửa `docs/03` §4 (bảng lỗi REST) — SDK dùng **mặt cắt**, không thay bảng.
- Không đổi số đã kiểm (`12 KB`, `3,5 s`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không dựng lại 4 PDF; không thêm phụ thuộc; không gọi mạng trong CI.

## 7. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | Portal phải **trả lời** `{__error, reason}` đúng hợp đồng — hiện chỉ SDK phía nhận đã sẵn | §3.2 — nửa còn lại của hợp đồng |
| **2** | Inspector hiện **4 mã lỗi** thành 4 dòng có tên (cùng nguyên tắc `docs/27` §3) | Lỗi không hiện ra thì không ai sửa |
| **3** | ADR `BreakResult` (mở từ `docs/27` §8) — nay có thêm lý do: `Promise<void>` **không chở được** mã lỗi | Ba tài liệu cùng chỉ về một ADR |
| **4** | Khi có `packages/game-sdk` thật (`M03`): port nguyên 4 mã + `idem` sang TypeScript | Bản này là tham chiếu, chưa phát hành |
