# Khoá hợp đồng SDK — và một mẫu POS cho thấy vì sao phải khoá

> **Tài liệu sống:** `docs/28-sdk-contract-lock-and-what-not-to-copy.md`
> **Trạng thái:** `SCOPING` — đánh giá 2 repo + **đã dựng khoá hợp đồng** (`sdk/game-sdk/CONTRACT.json`, `scripts/check_sdk_drift.py`)
> **Ngày:** 22/11/2026
> **Đầu vào:** `github.com/Darhlilove/splice` (MIT) · `github.com/khanhlegood1/Restaurant-POS-Kitchen` (không giấy phép) · yêu cầu *"áp dụng vào SDK cho dự án này theo poki portal SDK"*
> **Liên quan:** `docs/27` (hợp đồng Poki vs Xsolla) · `docs/03` §3 · `docs/20` teardown · `docs/25`, `docs/26`
> **Nối tiếp:** `docs/27` trả lời *"SDK gồm những gì"*. Tài liệu này trả lời *"khi nào được đổi, và ai biết"*.

---

## 0. Kết luận trước

**`splice` là công cụ sinh SDK — bề mặt của nó là *OpenAPI*, còn bề mặt của Game9K là *Poki*. Vì thế không dùng `splice` để sinh SDK Game9K. Nhưng nó chỉ ra đúng một lỗ hổng của `docs/27`: hợp đồng **chưa bị khoá**.**

**Repo POS thì không có gì để lấy cho SDK — và đó mới là điều đáng viết ra: nó là ví dụ sạch nhất của một ranh giới mà SDK Game9K phải giữ.**

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | `splice` là gì? | Bộ sinh SDK TypeScript từ OpenAPI (Next.js 15 + Prism + OpenAPI Generator), **MIT**, `0`★, `3.988 KB` (§1) |
| **2** | Dùng được không? | ❌ **Không phải** vì giấy phép — **MIT thì dùng được**. Mà vì **sai bề mặt**: `splice` sinh client REST có API key; SDK Game9K **cấm** gọi mạng, **cấm** giữ khoá (§2) |
| **3** | Lấy gì? | **Ba** bài học phản diện: commit `dist/` (nó đã lệch khỏi `src/`), mã `.env` trong SDK sinh ra, và `specVersion` chỉ để **log lỗi** chứ không để **khoá hợp đồng** (§2.1) |
| **4** | Repo POS là gì? | Template POS nhà hàng React + Vite, **`22.897` dòng**, **không có `LICENSE`**, tạo và đẩy cách nhau **`70` giây** (§3) |
| **5** | Lấy gì từ POS? | **Không gì cho SDK.** Nhưng nó chứng minh ranh giới: `card_demo` + `ManagerPinDialog` là chỗ *tiền và quyền* bị giả lập — đúng thứ `game-sdk` phải **từ chối** (§3.2) |
| **6** | Đã dựng gì? | `CONTRACT.json` + `check_sdk_drift.py`: **5 bất biến**, **11** kiểm tra, hash bề mặt `sha256:fa218660251cfabe` (§4) |

---

## 1. `splice` — nguồn, và nó thật sự làm gì

| | |
|---|---|
| Mục đích | *"Spec to SDK generator"* — OpenAPI → SDK TypeScript có kiểu |
| Giấy phép | **MIT** (`LICENSE`, "Copyright (c) 2025 Splice") — **dùng được**, khác hẳn 2 repo trước |
| Sao / ngày | **`0`**★ · tạo `12/11/2025` · đẩy lần cuối `08/02/2026` |
| Kích thước | **`368`** tệp · `3.988 KB` · `dist/` đã commit **`50`** tệp |
| Ngăn xếp | Next.js 15 (App Router), React 19, HeroUI, **Prism** (mock), **OpenAPI Generator** (sinh mã) |
| Kiểm thử | **`37`** tệp `*.test.ts`/`*.spec.ts` — nhiều hơn hẳn hai repo trước |
| Việc bỏ ngỏ | **`0`** dấu `TODO` trong `packages/openapi/src` — dấu hiệu repo được dọn kỹ |

### 1.1. Vì sao **không** dùng nó để sinh `@game9k/game-sdk`

Bề mặt đầu vào của `splice` là một **OpenAPI spec**; đầu ra là một **client REST**. Hai điều đó va thẳng vào hợp đồng đã chốt ở `docs/27`:

| `splice` sinh ra | Hợp đồng Game9K |
|---|---|
| `new Configuration({ apiKey })` | `check_sdk.py` **cấm** khoá trong mã chạy từ studio |
| `httpClient.ts` có retry + interceptor | SDK **chỉ** `postMessage`; `fetch`/`XHR` bị cấm |
| `.env.example` | SDK không có biến môi trường — nó chạy trong iframe |
| `logger.ts` gửi log đi | SDK không gửi gì ngoài 5 sự kiện + PoP tổng hợp |

> Nếu mai này Game9K cần **client REST cho backend** (`docs/03` §2), `splice` là ứng viên **tốt** — MIT, có test, có Prism. Nhưng đó là **`@game9k/api-client` cho portal/CLI**, **không phải** `game-sdk` chạy trong iframe. Hai gói, hai bề mặt, hai mức đặc quyền.

### 1.2. Ba bài học **phản diện** — cái đáng giá nhất của repo này

**(a) `dist/` trong git đã lệch khỏi `src/` — đây là bằng chứng, không phải suy đoán.**

| Thư mục | Tệp template |
|---|---|
| `packages/openapi/src/sdk-templates/` | `README` · `config` · `credentialProvider` · `env.example` · `httpClient` (**phẳng**) |
| `packages/openapi/dist/sdk-templates/` | y hệt 5 tệp trên (**cũng phẳng**, nhưng đây là bản **dựng**) |
| `apps/web/public/sdk-templates/` | **10** tệp, có thư mục `auth/`, `http/`, `utils/`, thêm `client.ts`, `interceptors.ts` |

Câu hỏi thật: **template nào đang chạy?** `sdk-enhancer.ts` chọn `public/` nếu tồn tại, ngược lại `__dirname` (tức `dist/`). Nghĩa là **hai bộ template cùng tồn tại, khác nội dung, và bộ nào được dùng phụ thuộc vào thư mục làm việc lúc chạy**.

> Đây là lý do `check_sdk_drift.py` có **bất biến 5**: `sdk/` không được chứa `dist/`, `node_modules/`, `*.min.js`, `*.map`. Không phải vì "cho sạch" — vì **hai bản của cùng một thứ thì không bản nào là nguồn sự thật**.

**(b) `specVersion` chỉ xuất hiện trong log lỗi.** `sdk-generator.ts:409` ghi `specVersion: spec.info?.version` khi sinh **thất bại**. Không có hash bề mặt, không có tệp khoá, không có phép so bề mặt cũ ↔ mới. Với một công cụ demo thì đủ. Với một SDK mà **hàng trăm bản build của studio đang gọi** thì **không**: đổi tên hàm là im lặng phá tất cả.

**(c) Sinh `.env` + credential provider cho SDK.** Tiện cho client máy chủ; **nguy hiểm** cho SDK chạy trong iframe của người khác. `docs/27` §6 R1 đã từ chối đúng điều này.

---

## 2. Lấy đúng **một** thứ từ `splice`

**Ý tưởng "spec là nguồn, SDK là đầu ra" — nhưng đảo chiều.** `splice` sinh mã từ spec. Game9K **khoá** bề mặt trong một spec nhỏ (`CONTRACT.json`) và **so cả ba chiều**: khoá ↔ mã ↔ `docs/03` §3.

Không chép mã, không chép template. Sự khác biệt không phải kỹ thuật mà là **mục đích**: `splice` giúp *tạo ra* SDK mới; Game9K cần *không cho* SDK đã phát hành đổi lặng lẽ.

---

## 3. `Restaurant-POS-Kitchen` — có gì, và vì sao **không** có gì cho SDK

| | |
|---|---|
| Nội dung | `Remix Restaurant POS & Kitchen Display Template` — React 19 + Vite, `lucide-react`, `motion` |
| Kích thước | **`22.897`** dòng, **`126`** tệp = **`60`** tệp mã + **`66`** ảnh món ăn |
| Tệp lớn nhất | `src/storage.ts` **`968`** dòng · `src/types.ts` **`392`** · `src/App.tsx` **`673** |
| Giấy phép | **Không có tệp `LICENSE`** — không có quyền sao chép |
| Sao / ngày | **`0`**★ · tạo `22/11/2026 18:08:38Z` · đẩy `18:09:48Z` — cách nhau **`70` giây** |
| Năng lực khai báo | `metadata.json`: `majorCapabilities: []` — **không** gọi API ngoài |

### 3.1. Nó là **mẫu giao diện**, không phải hệ thống thanh toán

Ba dấu hiệu độc lập:

1. **Phương thức thanh toán có tên `card_demo`** (`PaymentDialog.tsx`, `types.ts:190/204`) — chữ `demo` nằm trong **kiểu dữ liệu**, nên không thể vô tình coi là thật.
2. **`ManagerPinDialog`** — quyền quản lý được mô phỏng bằng một PIN trong trình duyệt.
3. **Dữ liệu lưu trong trình duyệt** — `metadata.json` mô tả *"saved in your browser"*; không backend, không webhook, không đối soát.

> **Đừng** trích repo này như bằng chứng "đã có luồng thanh toán". Nó **không** có: không cổng thanh toán, không hoá đơn, không đối soát. Đây là cùng loại bằng chứng với `docs/19` (Gitcoin): *mẫu giao diện ≠ cơ chế*.

### 3.2. Nhưng nó là ranh giới tốt nhất tôi thấy — vì nó **giả lập đúng hai chỗ nguy hiểm**

| Trong POS | Trong `game-sdk` |
|---|---|
| `card_demo` — thu tiền giả, nhãn ghi rõ | **`commercialBreak`/`rewardedBreak` trả trạng thái**, không bao giờ tự quyết tiền |
| `ManagerPinDialog` — quyền quản lý bằng PIN | **`init()` không trả `versionLabel` ở `arena`**, không có hàm "là admin" |
| Dữ liệu chỉ trong trình duyệt | `cloudSave` đi **qua portal**, SDK không thấy token |

Cả ba đều là **"giả lập được, nhưng không cấp quyền"**. Đó chính xác là mức mà một SDK chạy trong iframe của người khác phải giữ.

---

## 4. Đã dựng: khoá hợp đồng

```bash
python3 scripts/check_sdk_drift.py              # 5 bất biến
python3 scripts/check_sdk_drift.py --surface    # in bề mặt + hash
python3 scripts/check_sdk_drift.py --bump minor # in việc phải làm, KHÔNG sửa tệp
```

```
SDK DRIFT: PASS — 11 kiểm tra · 5 bất biến · khoá @game9k/game-sdk 0.1.x sha256:fa218660251cfabe
```

### 4.1. Năm bất biến

| # | Bất biến | Nó bắt được gì |
|---|---|---|
| **1** | `CONTRACT.json` = bề mặt **đọc từ mã** (tên, **và thứ tự**) | Thêm/bớt/đổi tên hàm mà không bump khoá |
| **2** | `CONTRACT.json` = bề mặt **trong `docs/03` §3** | Hàm "chỉ có trong mã" (studio không biết) hoặc "chỉ có trong tài liệu" (studio gọi và hỏng) |
| **3** | `SDK_VERSION` = `MAJOR.MINOR` của khoá | SDK tự khai sai phiên bản |
| **4** | Mọi `MAJOR` đã phát hành có **luật tương thích** | Bump `MAJOR` mà không nói game cũ phải làm gì |
| **5** | `sdk/` không có `dist/`, `node_modules/`, `*.min.js`, `*.map` | Bài học (a) ở §1.2 — hai bản của cùng một thứ |

> **Hash bề mặt `sha256:fa218660251cfabe`** là hash của *bề mặt*, không phải của tệp: sửa comment không đổi hash, đổi một tên hàm thì đổi. Đó là thứ để dán vào `CHANGELOG` và vào PR.

### 4.2. Năm phép phá đã chạy thật

| # | Phá | Kết quả |
|---|---|---|
| 1 | thêm `hiddenTelemetry()` vào mã, không bump khoá | ❌ `thừa ['hiddenTelemetry']` |
| 2 | `SDK_VERSION = '0.2.0'` trong khi khoá `0.1` | ❌ `SDK_VERSION 0.2.0 ≠ CONTRACT 0.1.x` |
| 3 | thêm `leaderboard(): void` vào `docs/03` | ❌ `docs/03 §3 có hàm KHÔNG có trong khoá` |
| 4 | commit `dist/a.js` + `poki.min.js` | ❌ **2** lỗi: bản dựng + bản nén trong git |
| 5 | bump `MAJOR` lên `1` không có `compat[1]` | ❌ **2** lỗi: lệch phiên bản + thiếu luật tương thích |

Phép phá 1 và 3 là cặp quan trọng nhất: chúng bắt **hai chiều** của cùng một lỗi — sửa mã mà quên tài liệu, và sửa tài liệu mà quên mã.

### 4.3. `--bump` **không** sửa tệp — cố ý

Bump hợp đồng là **chữ ký của người**, không phải việc của máy (`docs/25` §5: cổng là chữ ký người). Lệnh này **in ra 5 bước** phải làm, rồi dừng. Một công cụ tự bump hợp đồng là một công cụ có thể tự phá lời hứa với studio.

---

## 5. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Dùng `splice`/OpenAPI Generator để sinh `game-sdk` | §1.1 — bề mặt là REST + API key + `fetch`; cả ba bị cấm trong iframe |
| **R2** | Đưa `.env` / credential provider vào SDK | §1.2(c) — SDK chạy trong iframe **của người khác** |
| **R3** | Dùng `Restaurant-POS-Kitchen` làm bằng chứng "đã có thanh toán" | §3.1 — `card_demo` là **kiểu dữ liệu**, không phải cổng thanh toán |
| **R4** | Giữ `dist/` trong git vì "cho tiện chạy" | §1.2(a) — `splice` đang có hai bộ template lệch nhau; đừng lặp lại |

---

## 6. Việc **không** làm trong tài liệu này

- Không chép mã từ hai repo (một MIT nhưng sai bề mặt; một không có giấy phép).
- Không nói `splice` "hỏng": nó **đúng** cho mục đích của nó. Chỉ **không** dùng cho SDK iframe.
- Không sửa `docs/03` §3, không đổi số đã kiểm (`12 KB`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không dựng lại 4 PDF; không thêm phụ thuộc; không gọi mạng.

## 7. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | ADR `BreakResult` (đang mở từ `docs/27` §8) — đây là lần **bump MINOR đầu tiên**, dùng `--bump minor` làm danh sách việc | Bump đầu tiên phải làm đúng để làm mẫu |
| **2** | Nếu cần client REST cho portal/CLI: đánh giá `splice` cho **`@game9k/api-client`**, không phải `game-sdk` | §1.1 — hai gói, hai bề mặt |
| **3** | Dán `sha256` bề mặt vào `CHANGELOG.md` mỗi lần bump | §4.1 — hash là thứ so được giữa hai bản phát hành |
| **4** | Khi `1.0.0`: đổi `compat[1].removal` từ `next_major` sang `after_major_plus_1` và ghi lý do | `0.x` chưa hứa gì; từ `1.0` mới hứa |
