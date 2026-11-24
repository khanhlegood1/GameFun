# ADR-0034 — Hồ sơ sandbox cho game bên thứ ba

- **Trạng thái:** Proposed
- **Ngày:** 2026-11-23
- **Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
- **Liên quan:** ADR-0032 (nhúng game ngoài), ADR-0033 (Play SDK)
- **Nguồn tham khảo:** e2b `runtime` (ARCHITECTURE.md), `code-interpreter`,
  `open-computer-use`, `fragments` — tất cả Apache-2.0

## 0. Trả lời ngắn

> Thay **một thuộc tính cứng** `sandbox="allow-scripts"` bằng **hồ sơ khai báo được** cho từng game,
> để studio xin đúng quyền mình cần thay vì tất cả nhận cùng một mức. Hồ sơ là **dữ liệu**, không
> phải mã: mỗi game có một danh sách quyền, và `permissionsPolicy()` sinh header từ danh sách đó.

## 1. Vấn đề

`/play/:game` đang nhúng game bằng **một thuộc tính cứng**:

```html
<iframe sandbox="allow-scripts" allow="autoplay">
```

Và máy chủ **không gửi `Permissions-Policy`**. Hệ quả:

1. Mọi game — kể cả game của studio chưa ai đọc mã — nhận **cùng một bộ quyền**.
2. Những gì game *không* được cấp thì **không có chỗ nào trong mã nguồn nói ra**.
   Nó là mặc định của trình duyệt, mà mặc định thì khác nhau giữa các trình duyệt
   và đã từng nới ra theo thời gian.
3. Thêm một game mới không cần ai review quyền, vì không có gì để review.

Với một cổng game nhận bài từ studio bên ngoài, đây là chỗ hẹp nhất của hệ thống.

## 2. Nguyên tắc lấy từ e2b

Bốn repo được nêu đều nói về **một** ý, và ý đó áp dụng được:

> Một sandbox là một **hồ sơ khai báo trước**. Mọi thứ không khai báo thì **không
> có** — không phải "chặn cái xấu", mà là "không cấp cái chưa xin".

Trong `runtime`, điều này hiện ra ở chỗ: sandbox được tạo **từ một template**, và
template quyết định sandbox có gì. Không có đường "tạo sandbox rồi tự cấp quyền
sau". Trong `code-interpreter`/`open-computer-use`, nó hiện ra ở chỗ mọi thứ
chạy được đều phải đi qua một API có kiểu và có giới hạn.

Điều **không** lấy được, và phải nói rõ: e2b chạy code trong **microVM trên máy
chủ**; ở đây code chạy trong **trình duyệt người chơi**. Không thể thay iframe
bằng VM mà không đổi toàn bộ kiến trúc — và bắt mỗi người chơi trả tiền cho một
VM mỗi phiên là điều không làm được với một cổng game.

Vậy nên: **lấy nguyên tắc, không lấy mã.** Không có dòng nào của e2b trong repo
này, không thêm dependency nào.

## 3. Quyết định

`portal/lib/sandbox-profile.mjs`:

- `CAPABILITIES` là **danh sách ĐÓNG**: `scripts`, `autoplay`, `fullscreen`,
  `pointer_lock`, `storage`. Không có mục "khác".
- Không khai báo ⇒ hồ sơ **tối thiểu** (`scripts`). Đúng, vì game cũ không phải sửa.
- Khai báo tên lạ ⇒ **ném `ProfileError`**, route trả 500 kèm lý do. Không lặng lẽ
  hạ xuống "không có quyền": game sẽ chạy thiếu thứ nó cần, và người ta đi tìm lỗi
  ở chỗ khác.
- `sandboxAttr()`, `allowAttr()`, `permissionsPolicy()` sinh từ **cùng một** hồ sơ
  ⇒ thuộc tính iframe và header không thể lệch nhau.
- `NEVER_GRANTED`: camera, micro, vị trí, clipboard, `payment`, usb, serial,
  bluetooth, midi, hid, display-capture, screen-wake-lock, idle-detection —
  **liệt kê tường minh trong header** thành `feature=()`. Vắng mặt thì giữ mặc
  định trình duyệt; liệt kê thì "không cấp" là một lời khẳng định.
- `play.html` giữ chỗ `{{SANDBOX}}`/`{{ALLOW}}`; máy chủ bơm từ hồ sơ của **từng
  game**. `renderTemplate` **ném** nếu còn chỗ giữ chỗ nào chưa bơm — vì
  `sandbox="{{SANDBOX}}"` bị hiểu là token rác, tức chặn tất cả, và game trắng
  mà không ai biết vì sao.

### Ba điều cố ý KHÔNG làm

| Không làm | Vì sao |
|---|---|
| Cấp `allow-same-origin` | Cùng `allow-scripts` là cấp luôn quyền đọc cookie/localStorage của portal — bỏ hẳn ranh giới. Khung game vì thế là origin mờ, `event.origin` là `"null"`, bắt tay dùng `ev.source` + nonce (ADR-0033). |
| Thêm `sandbox` cho API máy chủ | iframe là ranh giới giữa *trang* và *game*, **không** phải giữa *game* và *hạ tầng*. Game vẫn `fetch` được API portal như mọi trang. Vì thế phút chơi do **máy chủ** đếm, không do game tự khai. |
| Dùng e2b để chạy game | Đổi toàn bộ kiến trúc; chi phí mỗi phiên; và game phải vẽ 60 fps trong trình duyệt, không trong VM. |

## 4. Hệ quả

- Thêm quyền cho một game = **một dòng trong `GAME_CATALOG`**, và đó là dòng phải
  đọc kỹ trong review. Trước đây không có dòng nào để đọc.
- Header `permissions-policy` áp cho **mọi** response của portal, không chỉ trang
  chơi.
- `/api/play/sdk` công bố luật chung (`sandbox: describeSandbox()`).

## 5. Đã kiểm, và kiểm ngược

`portal/test/sandbox-profile.test.mjs` (19) + 5 test HTTP trong
`portal/test/play-routes.test.mjs`.

| Phá gì | Kỳ vọng | Thực tế |
|---|---|---|
| Bỏ header `permissions-policy` | đỏ | 2 test đỏ |
| Nối thêm `allow-same-origin` vào call site | đỏ | đỏ ở **cả hai** tệp (xem §5.1) |
| `camera=(self)` thay vì `camera=()` | đỏ | 2 test đỏ |
| Viết cứng `sandbox="allow-scripts"` trong `play.html` | đỏ | 1 test đỏ |

### 5.1 Một lỗ thật, do chính phép phá tìm ra

Lần chạy đầu, phép phá "nối thêm `allow-same-origin` vào call site" khiến
`sandbox-profile.test.mjs` vẫn **15/15 xanh**. Vì tệp đó chỉ kiểm **hàm thuần**;
hàm vẫn đúng, chỉ chỗ gọi sai.

Đã bịt bằng một nhóm test đọc **mã nguồn** `server.mjs` và `play.html`: không
`allow-same-origin` ngoài `lib/`, thuộc tính phải là `{{SANDBOX}}`, và giá trị
phải đến từ `profileFor()`. Chạy lại phép phá ⇒ đỏ ở cả hai tệp.

Bài học giống ADR-0033 §5.0: **kiểm hàm không phải kiểm hệ thống.** Chỗ nối mới
là chỗ hay sai.

## 6. Câu hỏi mở

- **Q-ADR34-a.** `pointer_lock` và `fullscreen` hiện chưa game nào xin. Có nên
  xoá khỏi danh sách cho tới khi có game cần (danh sách nhỏ hơn = dễ review hơn)?
- **Q-ADR34-b.** Có cần hồ sơ **theo phiên bản bản build** thay vì theo game
  không? Nếu studio nộp 2.0 xin thêm quyền, hiện tại đó là sửa `GAME_CATALOG`,
  không phải một bước duyệt riêng.
- **Q-ADR34-c.** Có nên chặn `storage` khỏi danh sách công khai, vì nó **không có
  hiệu lực** (chỉ là tên để khai báo ý định)? Một mục khai báo mà không làm gì là
  chỗ dễ hiểu nhầm.

## Ranh giới trung thực

- **Đã kiểm:** `permissionsPolicy()` khoá tường minh những quyền portal **không bao giờ** cấp
  (`NEVER_GRANTED`); trước bản này máy chủ **không gửi** header `permissions-policy` nào.
- **Chưa kiểm:** trình duyệt **thật** có tôn trọng từng quyền trong hồ sơ không. jsdom không thực
  thi `permissions-policy`; đây là suy luận từ đặc tả.
- **Chưa chạy:** một game thật xin `camera` để xem nó có bị chặn đúng không.
- **Không** khẳng định hồ sơ này "an toàn hơn" thuộc tính cứng. Nó **rõ hơn** (khai báo được),
  và đó là khác biệt có thật; "an toàn hơn" là tuyên bố chưa đo.

## Điều ADR này **KHÔNG** bao gồm

| Không bao gồm | Vì sao | Ai quyết |
|---|---|---|
| Hồ sơ theo **phiên bản build** thay vì theo game | Hiện đổi quyền = sửa `GAME_CATALOG`, không có bước duyệt riêng | Q-ADR34-b |
| Thực thi `storage` | Nó chỉ là **tên khai báo ý định**, không có hiệu lực | Q-ADR34-c |
| Sandbox cách ly thật (VM/container) | Xem `ADR-0039` (Hermes/e2b) — khác tầng | — |
