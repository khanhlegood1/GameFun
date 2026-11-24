# ADR-0031 — Portal hiển thị câu hỏi mở: **sinh dữ liệu lúc build, chỉ đọc lúc chạy**

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`gen_portal_data.mjs`](../../scripts/gen_portal_data.mjs) · [`open-questions.generated.mjs`](../../portal/lib/open-questions.generated.mjs) · [`portal/server.mjs`](../../portal/server.mjs) · [`ADR-0030`](ADR-0030-proactive-co-creator-cho-muc-con-mo.md) · [`ADR-0027`](ADR-0027-starter-kit-game-mau-dua-khung-long.md)

---

## 0. Trả lời ngắn

| | |
|---|---|
| Vấn đề | `https://game9k.vercel.app/portal` chạy đúng commit mới nhất nhưng **không có gì mới để thấy** — Request Z chỉ thêm script CLI và tài liệu |
| Cách làm | Thêm tab **"Câu hỏi mở"** đọc `PRD §11`, và nhúng **game đua khủng long** vào Playground |
| Điểm kỹ thuật quyết định | Portal **không đọc được `docs/` lúc chạy** trên Vercel ⇒ phải **sinh dữ liệu lúc build** |
| Có ghi vào PRD không | ❌ **Không.** Chỉ đọc. Đóng một mục vẫn là việc của Owner ghi trong PRD |
| Có gọi model không | ❌ Không |
| Phát hiện kèm theo | `game.html` **crash ngay khi nạp** (`f.pos` vs `f.positions`) — đã sửa và thêm cổng `game-boot.test.mjs` |

---

## 1. Vấn đề thật, đo được

Ngày 2026-11-18, production đã ở `157b752` — commit merge của PR #151. Nhưng mở `/portal`
thì **không thấy gì mới**: PR #151 thêm `scripts/open_questions.mjs` (chạy bằng dòng lệnh)
và hai ADR (đọc trên GitHub). Portal phục vụ 8 tab tĩnh, không tab nào chạm tới §11.

Nói cách khác: *"deploy tính năng mới"* không phải bài toán deploy — **bản deploy đã đúng**.
Đó là bài toán **thiếu bề mặt**: capability có trong repo nhưng không có đường vào từ sản phẩm.

Đo được, không suy đoán:

| Sự kiện | Bằng chứng |
|---|---|
| Production ở `157b752` | `dpl_9BvaqF9kWiJ6PRconMmiJj8jPqQJ` `READY`/`PROMOTED`, alias `game9k.vercel.app` |
| Portal không có mục §11 | grep `portal/server.mjs` + `portal/public/index.html`: 0 kết quả |
| Portal không có game mẫu | `portal/public/games/` chỉ có `neon-drift*` |
| `docs/` không lên production | `.vercelignore` chỉ upload `prototype/`; `portal/` đến qua `includeFiles` |

---

## 2. Quyết định

### 2.1 Sinh dữ liệu lúc build, không đọc tài liệu lúc chạy

`scripts/gen_portal_data.mjs` đọc nguồn **trong repo** và ghi ra hai artifact đã commit:

| Nguồn | Đích | Vì sao |
|---|---|---|
| `docs/01-requirements/PRD-game9k.md` §11 (qua `parseOpenQuestions`) | `portal/lib/open-questions.generated.mjs` | `.vercelignore` không ship `docs/`; đọc lúc chạy ⇒ 503 |
| `starter-kit/game.html` | `portal/public/games/dino-race.html` | Portal phục vụ file tĩnh; chép tay sẽ trôi (đúng nợ Q59) |

Cả hai có `--check`: **exit 1 khi lệch nguồn**, exit 2 khi thiếu nguồn. Artifact được
**commit** để bản deploy không phụ thuộc vào việc chạy script trước `git push`.

**Vì sao sinh CẢ câu hỏi gợi ý, không để server tự sinh:** `vercel.json` khai
`includeFiles: "{portal/**,demo/docsend/**,package.json}"` — **`scripts/` không được ship**.
Lần đầu tôi viết `import { clarificationsFor } from '../scripts/lib/belief.mjs'` trong
`portal/server.mjs`: local xanh, 364 test xanh. Trên Vercel thì `ERR_MODULE_NOT_FOUND` ở
**cấp module**, nên **cả function chết** — mọi route 500, không riêng route mới. Câu hỏi
được "nướng" vào module sinh thay vì tính lúc chạy.

Cổng chặn: `portal/test/bundle.test.mjs` dựng một thư mục chỉ chứa đúng những gì
`includeFiles` ship (đọc từ chính `vercel.json`, không chép tay), rồi `import()` entry
point từ đó. Reverse-test: trả lại import chéo ⇒ `B-01`/`B-02` **đỏ** trong khi
`server.test.mjs` vẫn **50/50 xanh** — đúng lý do lỗi này lọt qua mọi test cũ.

**Vì sao không nới `.vercelignore` cho `docs/`:** làm vậy là publish toàn bộ cây tài liệu
nội bộ (gồm cả ghi chú pháp lý và số liệu chưa công bố) lên Internet. Cái giá đó lớn hơn
nhiều so với việc sinh một module 3 KB.

### 2.2 Route chỉ đọc

`GET /api/open-questions` trả `{source, items, counts, blocking, canXem, disclaimer}`.
Mỗi item mang thêm `clarifications` — **câu hỏi có lựa chọn**, không phải câu trả lời.

**Không có `POST`/`PUT`/`PATCH`/`DELETE`.** Đây là ràng buộc cứng, không phải "chưa làm":
đóng một mục §11 là hành động của Owner trong PRD, có người chịu trách nhiệm. Một nút
"trả lời" trên portal sẽ tạo ra *vẻ ngoài* của quyết định mà không có ai ký.

Cổng chứng minh điều này: `portal/test/server.test.mjs` gọi cả bốn phương thức ghi và
khẳng định chúng **không** lọt qua (đã reverse-test: thêm một route `POST` giả ⇒ 49/50, đỏ đúng chỗ).

### 2.3 Game mẫu vào Playground qua iframe cùng origin

`portal/public/games/dino-race.html` là **bản sao sinh tự động** của `starter-kit/game.html`
(có banner đầu file). Portal mở nó bằng `<iframe sandbox="allow-scripts">` và **bắt tay
nonce** trước khi nhận lệnh.

Giới hạn phải nói rõ: iframe **cùng origin** với portal, nên nonce chỉ tách *phiên*, không
tách *nguồn*. Script cùng trang cha vẫn đọc được nonce. Đó không phải lỗ mới — ADR-0027 §7
đã ghi; ở đây chỉ tái sử dụng đúng cơ chế đó.

---

## 3. Lỗi tìm ra trong lúc làm, và cổng chặn tái phát

Khi nhúng game, script **crash ngay khi nạp**:

```
TypeError: Cannot read properties of undefined (reading '0')
    at drawFrame (game.html:410)  ← const pos = f.pos[i]
    at setSeed  (game.html:464)
```

`simulate()` sinh frame `{tick, positions, surging}`, còn `drawFrame` đọc `f.pos` / `f.surge`.
Vì TypeError ném ở `setSeed(...)` — dòng áp chót của script — nên `wireBridge()` **chưa kịp chạy**:
game hiển thị được khung nhưng **handshake nonce im lặng không tồn tại**.

Vì sao 47 test cũ vẫn xanh: `build-parity.test.mjs` chỉ chạy phần **lõi** trong sandbox,
không chạy phần **vẽ**. Không test nào chạm `drawFrame`.

Đã sửa hai dòng ở **nguồn** `starter-kit/game.html` (rồi sinh lại bản portal), và thêm
`starter-kit/test/game-boot.test.mjs` — chạy **toàn bộ** script trong jsdom với canvas giả:

| | Khẳng định |
|---|---|
| `GB-01` | nạp xong không ném lỗi; frame có `positions`/`surging` và **không** có `pos` |
| `GB-02` | hello hợp lệ ⇒ khoá phiên, phát ra đúng một `race:ready` mang nonce |
| `GB-03` | lệnh không nonce, nonce sai, hello thứ hai — cả ba bị từ chối **và** để lại cảnh báo |

Reverse-test, cả ba đều đỏ được rồi phục hồi:

| Phá gì | Kết quả |
|---|---|
| Trả lại `f.pos`/`f.surge` | 3/3 đỏ |
| Bỏ `if (locked) return false` | 1 đỏ |
| `check()` luôn `return true` | 1 đỏ |

---

## 4. Hệ quả

**Được:** §11 lần đầu *nhìn thấy được* từ sản phẩm, không chỉ từ dòng lệnh. Game mẫu
chạy được trong portal. Hai artifact sinh tự động có `--check` nên không trôi.

**Mất / phải chịu:** thêm 1 route đọc và ~3 KB module vào bundle function; mỗi lần §11 đổi
phải chạy `node scripts/gen_portal_data.mjs` rồi commit artifact — nếu quên, `--check` đỏ
(đây là *ý định*, không phải phiền toái).

**Chưa làm, và biết là chưa làm:**

- `--check` **chưa** wire vào CI. Lý do giống Q63: có người phải quyết việc một artifact
  sinh tự động trở thành điều kiện merge. ADR này **không** tự quyết thay PO.
- Chưa có nút "đóng mục" nào, và sẽ không có cho tới khi PO quyết ai được ký.
- Tab mới **không** phân quyền: ai mở portal cũng thấy §11. Nội dung §11 là câu hỏi,
  không phải câu trả lời — nhưng đây vẫn là quyết định công bố, PO nên xác nhận.

---

## 5. Việc PO phải quyết

| | Câu hỏi |
|---|---|
| **Q-ADR31-a** | §11 (11 mục, gồm 2 `BLOCKING`) có được **công khai** trên portal không, hay chỉ hiện sau khi đăng nhập? |
| **Q-ADR31-b** | `gen_portal_data.mjs --check` có thành điều kiện merge (CI) không? |
| **Q-ADR31-c** | Có mở đường cho Owner đóng mục **từ portal** (có ghi vào PRD, có audit) không — hay giữ nguyên "chỉ sửa PRD bằng PR"? |

---

## 6. Điều ADR này **KHÔNG** bao gồm

| Không bao gồm | Vì sao ngoài phạm vi | Ai quyết |
|---|---|---|
| Đóng mục **từ portal** (ghi ngược vào PRD) | Portal là máy đọc; ghi ngược tạo hai nguồn sự thật cho §11 | Q-ADR31-c |
| Nội dung **đầy đủ** của PRD | Portal chỉ hiển thị §11 (11 mục). §1–§10 và §12 ở lại repo | — |
| Phân quyền xem từng mục | Hiện toàn bộ §11 hiện hoặc ẩn cùng nhau | Q-ADR31-a |

## 7. Ranh giới trung thực

- **Đã kiểm:** `gen_portal_data.mjs --check` khớp nguồn (13.047 B, đo 2026-11-18) — nhưng đó là
  **so khớp byte**, không chứng minh nội dung §11 đúng.
- **Chưa kiểm:** có người thật nào đọc tab "Câu hỏi mở" chưa. Không có phép đo lượt xem.
- **Chưa chạy:** `--check` **chưa** là điều kiện merge (Q-ADR31-b). Hiện nó chạy tay.
- **Không** khẳng định portal giúp PO đóng câu hỏi nhanh hơn — không có dữ liệu trước/sau.
