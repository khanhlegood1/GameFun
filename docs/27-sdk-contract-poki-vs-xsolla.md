# Hợp đồng SDK: Poki là hiến pháp, Xsolla là bưu điện

> **Tài liệu sống:** `docs/27-sdk-contract-poki-vs-xsolla.md`
> **Trạng thái:** `SCOPING` — đánh giá + **đã dựng hợp đồng kiểm được** (`scripts/check_sdk.py`, `sdk/game-sdk/game9k-sdk.js`)
> **Ngày:** 22/11/2026
> **Đầu vào:** `https://xsolla.com/sdk` · `https://developers.xsolla.com/sdk/demo/` · yêu cầu *"áp dụng vào SDK cho dự án này theo poki portal SDK"*
> **Liên quan:** `docs/03` §3 (hợp đồng SDK) · `docs/PRD.md` FR-SDK-01 · `docs/11` (auth/passkey) · `docs/25` · `docs/26`

---

## 0. Kết luận trước

**Xsolla không phải SDK của một cổng game. Nó là bưu điện thanh toán. Chép nó vào SDK của Game9K là chép nhầm — nhưng có đúng hai thứ đáng lấy, và một thứ đáng bắt chước về hình thức.**

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Xsolla SDK làm gì? | 4 bước: **Authenticate → Load catalog → Purchase → Finalize**; không backend, không thuế, phí **`5%`/giao dịch** (§1) |
| **2** | Có dùng được cho cổng web game không? | ❌ **Không.** Trang chính thức **không liệt kê** nền web/WebGL là nền tảng hỗ trợ; SDK chạy trong **ứng dụng native**, còn game Game9K chạy trong **iframe trên trình duyệt** (§1.2) |
| **3** | Vậy lấy gì? | **Hai** thứ: **Web Shop** (bán ngoài store, không phí nền tảng) và **trạng thái giao dịch tường minh** thay vì `Promise<void>` (§2) |
| **4** | Bắt chước gì về hình thức? | **SDK Explorer** — đi hết luồng bằng **lệnh gọi thật** nhưng **không cần tài khoản**, và nhãn **"Live API calls, not simulated"** (§3) |
| **5** | SDK của Game9K khác gì? | **Hai loài**: `game-sdk` trong iframe **không chạm tiền**; portal ngoài iframe giữ phiên + passkey (§4) |
| **6** | Đã kiểm được gì? | `check_sdk.py`: **5 bất biến**, **18** kiểm tra, SDK tham chiếu **`2.633` B gzip / `12.000` B** = **`21,9%`** ngân sách (§5) |

---

## 1. Xsolla SDK thật sự là gì

| | |
|---|---|
| Phiên bản | **`SDK v3.1`** — "Xsolla SDK 3" |
| Mô hình | 4 bước: **Authenticate · Load catalog · Purchase · Finalize** |
| Phí | **`5%` mỗi giao dịch**, "no monthly fees, no minimum volume" *(tự công bố)* |
| Nền tảng | **iOS · Android · Unity · Windows/Epic** — trang chính thức **không nêu Web/WebGL** |
| Backend | Không cần cho luồng chuẩn; thuế VAT/sales tax "calculated, collected, and filed automatically" *(tự công bố)* |
| Mã nguồn | `github.com/xsolla` — `xsolla-sdk-unity` · `xsolla-sdk-android` · `xsolla-sdk-ios` (**Apache-2.0**, `0`★); **không có** repo SDK web/HTML5 |

### 1.1. Nhãn nguồn — ba loại, đừng trộn

| Loại | Ví dụ | Dùng được để làm gì |
|---|---|---|
| **Quan sát trực tiếp** | Trang SDK ghi "Code complexity reduced to four API calls"; SDK Explorer chạy được và hiện `User ID: AA1DXE` | Trích dẫn như mô tả sản phẩm |
| **Tự công bố** | `200+` quốc gia · `1.000+` phương thức · `130+` tiền tệ · `25+` ngôn ngữ · `5%` phí · "up to 95% revenue" | Chỉ ghi kèm nhãn; **không** đưa vào mô hình tài chính |
| **Không kiểm được** | "Trusted by the studios behind _Crossout_, _Modern Warship_…" | Bỏ. Không có bằng chứng công khai |

> **Không** đưa `5%` của Xsolla vào bảng doanh thu `docs/WHITEPAPER.md` §7. Đó là phí của **một nhà cung cấp thanh toán** cho **một luồng khác** (bán vật phẩm trong app native), không phải nguồn thu của Game9K.

### 1.2. Vì sao nó **không** lắp vào cổng game web

1. **Không có nền web.** Trang SDK liệt kê iOS, Android, Unity, Windows/PC. Unity SDK có "Web: WebGL monetization support" — nhưng đó là **Unity WebGL build**, không phải **HTML5 game bất kỳ** chạy iframe.
2. **SDK của họ sống trong tiến trình của ứng dụng.** SDK của Game9K sống trong **iframe `sandbox` không `allow-same-origin`** (`docs/03` §3, `docs/05`). Hai mô hình đe doạ khác nhau hoàn toàn.
3. **Họ giải bài toán *bán vật phẩm*; Game9K giải bài toán *phân phối game*.** Hai bài toán khác nhau. Trộn vào là SDK vừa phải mở cổng thanh toán vừa phải chạy game — đúng thứ §4 tách ra.

---

## 2. Lấy đúng **hai** thứ

### 2.1. Web Shop — bán ngoài store, không phí nền tảng

Luồng *Buy Button* của Xsolla: mở Web Shop trong trình duyệt, **không cần cài SDK**. Áp vào Game9K: khi studio muốn bán vật phẩm/vé giải đấu **trực tiếp cho người chơi của mình**, Game9K cung cấp **trang bán** do studio cấu hình, chứ không bắt studio nhét giá vào game.

> Đây là điều **đúng** với mô hình doanh thu đã chốt: `docs/WHITEPAPER` §7 nguồn 4 ghi **`0%`** phí trên lưu lượng studio tự kéo. Một trang bán do studio sở hữu là **cách thi hành** con số `0%` đó, không phải con số mới.

### 2.2. Trạng thái giao dịch tường minh, không `Promise<void>`

Hợp đồng hiện tại của Game9K (`docs/03` §3) có:

```ts
commercialBreak(onStart?: () => void): Promise<void>;
```

`Promise<void>` **không nói được** điều gì đã xảy ra: quảng cáo có phát không, có bị chặn không, có lỗi không. Xsolla làm ngược lại — mỗi bước trả **trạng thái**. Đổi thành:

```ts
type BreakResult = 'shown' | 'skipped' | 'no_fill' | 'blocked_by_env';
commercialBreak(opts?: { onStart?: () => void }): Promise<BreakResult>;
```

> **Đây là thay đổi hợp đồng, không phải thay đổi số liệu.** Nó làm hỏng game đang gọi `.then(() => {})`? Không — thêm giá trị trả về là tương thích ngược ở JavaScript. Nhưng nó làm **Inspector** đếm được `no_fill` thay vì im lặng, và làm `arena` chứng minh được **đã chặn**.

> **Chưa sửa `docs/03` trong vòng này.** Chữ ký hiện tại vẫn đúng với Poki và `check_sdk.py` đang canh nó. Đề xuất đổi `Promise<void>` → `Promise<BreakResult>` cần một ADR riêng vì nó chạm hợp đồng công khai. Ghi vào §8.

---

## 3. Bắt chước **SDK Explorer** — dạng kiểm chứng, không phải dạng API

| Vì sao nó hay | Áp vào Game9K |
|---|---|
| **"No account required"** | `python3 scripts/check_sdk.py --matrix` — in ma trận hành vi mà không cần chạy gì |
| **"Live API calls, not simulated"** | Nhãn nguồn ở §1.1: mỗi con số ghi rõ *quan sát* / *tự công bố* / *không kiểm được* |
| **Bốn bước có tên** | Inspector của Game9K phải hiện **đúng 5 sự kiện Poki** thành 5 dòng có tên, không phải một log thô |
| **Đổi được môi trường (iOS/Android/Unity)** | `--matrix` in **5 môi trường** × 8 hàng; cùng một SDK, hành vi khác nhau có chủ đích |

Điểm **không** bắt chước: demo của họ gọi API **thật** với **tài khoản thật**. Cổng của Game9K là CI tất định, **không gọi mạng** (`AGENTS.md`; `docs/25`, `docs/26` cùng nguyên tắc).

---

## 4. Hình dạng SDK của Game9K: **hai loài**, không phải một

Đây là kết luận thiết kế quan trọng nhất của tài liệu này.

| | **Loài A — `game-sdk`** (trong iframe game) | **Loài B — portal** (ngoài iframe) |
|---|---|---|
| Ai ký mã | Game9K ký, phát hành; studio `import` | Game9K; **không** studio nào chạy mã ở đây |
| Ai gọi | Mã game gọi; **người chơi không bao giờ gọi trực tiếp** | Trình duyệt người chơi, qua `/g/[slug]` |
| **Chạm tiền?** | **Không.** Không hàm nào trong 8 hàm tạo/ký/gửi giao dịch | **Có** — nhưng chỉ *hiển thị* số dư; chữ ký nằm ở passkey (`docs/11`) |
| **Chạm danh tính?** | Chỉ `cloudSave`, và nó đi qua portal — SDK **không thấy token** | **Có** — phiên Supabase `HttpOnly`, **không bao giờ** xuống iframe |
| Quyền tối thiểu | `postMessage` ra `window.parent`; đọc `performance` / `rAF` | CSP `frame-ancestors 'self'`; iframe `sandbox` **không** `allow-same-origin` |
| Nếu bị sửa | Game hỏng, **không mất tiền** — trong iframe không có gì để mất | **Mất tiền/mất danh tính** — bề mặt cần review tay |

> **Gộp hai loài là lỗi thiết kế.** Nếu `game-sdk` giữ được token thanh toán, một game bị xâm nhập là một ví bị xâm nhập. Xsolla gộp vì họ chạy trong app **của chính chủ game**; Game9K không có quyền đó — mã trong iframe là mã **của người khác**.

---

## 5. Đã dựng: `scripts/check_sdk.py` + SDK tham chiếu

```bash
python3 scripts/check_sdk.py            # 5 bất biến + đo ngân sách gzip
python3 scripts/check_sdk.py --species  # in đặc tả 2 loài
python3 scripts/check_sdk.py --matrix   # 5 sự kiện Poki × 5 môi trường
```

```
SDK CONTRACT: PASS — 18 kiểm tra · 5 bất biến · chế độ: thi hành
  gzip đo được: 2633 B / 12000 B ngân sách (21.9%) trên 1 tệp
```

### 5.1. Năm bất biến

| # | Bất biến | Vì sao nó phải đỏ được |
|---|---|---|
| **1** | Đủ **5 hàm Poki** đúng tên, đúng chữ ký, cộng **3 tiện ích** Game9K | Lời hứa "port trong 10 phút" chỉ đúng nếu hợp đồng không thiếu hàm |
| **2** | **Ngân sách `12 KB` gzip** — đo **byte**, cộng dồn **từng tệp** | `docs/PRD.md` FR-SDK-01 hứa con số này; không ai đếm thì nó là lời hứa |
| **3** | Không `fetch` / `XHR` / `eval` / `new Function` / `import` / `require` | SDK tự gọi mạng là SDK tự rò dữ liệu |
| **4** | Không `localStorage` / `cookie` / **hàm thanh toán** / **hàm ký giao dịch** | `docs/03` §3.2 cấm đọc storage; §4 cấm chạm tiền |
| **5** | `commercialBreak`/`rewardedBreak` phải **hỏi môi trường** | `arena` cấm quảng cáo (lộ thời điểm → phá Blind Duel); `direct` cấm vì lưu lượng studio chịu `0%` phí |

### 5.2. Ma trận hành vi — vì sao phải hỏi môi trường

```
Hàm                   inspector     preview      play                arena           direct
commercialBreak       ⛔ không phát  ⛔ không phát ✓ (portal quyết)    ⛔ **cấm**       ⛔ `0%` phí → không chèn
rewardedBreak         ⛔ trả `false` ⛔ trả `false`✓ tự nguyện         ⛔ **cấm**       ⛔ trả `false`
init().versionLabel   ✓ có          ✓ có         ✓ có                ⛔ **không trả** ✓ có
```

Hai ô cấm tuyệt đối, và cả hai đều **đã có nguồn trong repo**, không phải tôi tự nghĩ ra:
- **`arena`** — `docs/03` §3 quy tắc 3: `init()` không trả `versionLabel`. Quảng cáo cũng lộ thời điểm; cấm luôn.
- **`direct`** — `docs/WHITEPAPER` §7 nguồn 4: **`0%`** phí trên lưu lượng studio tự kéo ⇒ **không chèn quảng cáo của Game9K** vào luồng đó.

### 5.3. Năm phép phá đã chạy thật

| # | Phá | Kết quả |
|---|---|---|
| 1 | thêm `fetch("https://evil.example/x")` | ❌ `chứa \bfetch — gọi mạng` |
| 2 | thêm `function openCheckout(){}` | ❌ `chứa openCheckout\|xsolla — thanh toán trong mã studio` |
| 3 | bỏ `gameplayStart(): void` khỏi `docs/03` | ❌ **2** lỗi: thiếu hàm **và** sai chữ ký |
| 4 | thêm một tệp 30 KB vào `sdk/game-sdk` | ❌ `gzip 24512 B ≥ 12000 B` — bắt cả tổng **và** từng tệp |
| 5 | đổi điều kiện môi trường thành `if (false)` | ❌ `không kiểm môi trường — Arena sẽ phát quảng cáo` |

Phép phá 3 và 4 là loại quan trọng nhất: chúng bắt **lời hứa trong tài liệu**, không chỉ bắt mã.

---

## 6. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Nhúng SDK thanh toán của bên thứ ba vào `game-sdk` | §4 — mã trong iframe là mã của người khác; nhúng thanh toán là trao khoá ví cho studio |
| **R2** | Bắt studio cấu hình giá/vật phẩm trong game | Giá nằm ở **portal**; game chỉ báo *"người chơi đã xong màn 3"* |
| **R3** | Dùng `5%` của Xsolla làm giả định doanh thu | §1.1 — phí của một nhà cung cấp cho một luồng khác. Không vào `WHITEPAPER` §7 |
| **R4** | Biến SDK Explorer thành cổng CI gọi mạng | Cổng phải tất định (`AGENTS.md`); demo của họ cần tài khoản thật |

---

## 7. Việc **không** làm trong tài liệu này

- Không sửa `docs/03` §3 — chữ ký Poki giữ nguyên; đề xuất `Promise<BreakResult>` để ở §8.
- Không đổi số đã kiểm: `12 KB`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`.
- Không dựng 4 PDF; không thêm phụ thuộc; không gọi mạng.
- Không khẳng định Xsolla "không hỗ trợ web" như một sự thật tuyệt đối — chỉ ghi **trang SDK 3.1 không liệt kê web/WebGL là nền tảng**, và Unity WebGL là ngoại lệ đã nêu.

## 8. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | ADR: `commercialBreak` → `Promise<BreakResult>` (§2.2) | Đổi hợp đồng công khai phải có ADR, không sửa lặng lẽ |
| **2** | Dựng `sdk/game-sdk/game9k-sdk.js` thành `packages/game-sdk` khi `M03` mở (`docs/06`) | Bản này là **tham chiếu**, chưa phải bản phát hành |
| **3** | Inspector hiện **5 dòng có tên** + cột `BreakResult` | §3 — bắt chước *hình thức* của SDK Explorer, không bắt chước API |
| **4** | Trang bán của studio (Web Shop) theo §2.1 | Đây là cách thi hành `0%` phí, không phải con số mới |
