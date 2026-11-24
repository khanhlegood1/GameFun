# ADR-0038 — OpenRouter cho **Game9K** (không phải cho gate): đọc bản nộp, không duyệt bản nộp

**Trạng thái:** **Accepted** cho §3 (PO quyết 2026-11-23, Q-ADR38-b) — đã hiện thực
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0035`](ADR-0035-openrouter-cho-decisions-api.md) · [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) · [`game-handoff.mjs`](../../portal/lib/game-handoff.mjs) · [`nguyen-ly-don-vi-khanh-tang-hai.md`](../00-framework/nguyen-ly-don-vi-khanh-tang-hai.md) · **Q62a**

> Nguồn: [`openrouter.ai`](https://openrouter.ai/) · [`jev`](https://openrouter.ai/docs/guides/community/jev) ·
> [`multimodal-decisions`](https://openrouter.ai/docs/guides/community/multimodal-decisions) ·
> [`typescript decisions SDK`](https://openrouter.ai/docs/client-sdks/typescript/sdks/decisions/README.md).
> Không chép mã. OpenRouter không xem xét hay xác nhận gì về Game9K. Xem §7.

---

## 0. Trả lời ngắn

Câu hỏi: *"OpenRouter có giúp áp dụng cho Game9K?"* — **Game9K là sản phẩm**, không phải quy trình gate.

| Việc trong Game9K | OpenRouter làm được? | Vì sao |
|---|---|---|
| Đọc **bản nộp** của studio (`manifest.json`, changelog) và chỉ chỗ mâu thuẫn | ✅ **CÓ** — đây là giá trị thật | Cùng bộ primitive `noul`/`choice`/`score` đã dùng ở ADR-0035 |
| Phân loại thể loại game từ mô tả | ✅ **CÓ**, nhưng **PO phải xác nhận** | `choice` + `probabilities`, không phải nhãn cứng |
| Đọc ảnh chụp màn hình game | ⚠️ **CÓ với `google/gemini-decision-1`** | Chỉ adapter đó đọc `image_url` (bảng adapter là contract) |
| **Duyệt** bản nộp | ❌ **KHÔNG, và không bao giờ** | `game-handoff.mjs:287` — `ai_cannot_approve` |
| Tính **giờ chơi** / xác thực phút | ❌ **KHÔNG** | `play_sessions` từ người thật (KVU-2 §1.4) |
| Chấm điểm chất lượng game | ❌ **KHÔNG** | Cùng lý do — người chơi thật |
| Đo độ "hot trend" của AI/blockchain | ❌ **KHÔNG** | Không có dữ liệu; xem ADR-0037 §5 |

**Một câu:** OpenRouter giúp Game9K ở chỗ **đọc và mô tả**, không ở chỗ **quyết định và đo**.

---

## 1. Vì sao câu hỏi này KHÁC ADR-0035

ADR-0035 áp OpenRouter vào **quy trình của chính đội** — đọc `P0x-signoff.md` để PO biết chỗ nào chưa
chắc. Đó là công cụ nội bộ, không ai ngoài thấy.

Câu này áp vào **sản phẩm**: bản nộp của studio đi qua portal. Khác biệt về bản chất:

| | ADR-0035 (gate) | ADR-0038 (Game9K) |
|---|---|---|
| Ai bị ảnh hưởng khi AI sai | PO đọc một gợi ý sai | **studio bị từ chối oan**, hoặc **game xấu được duyệt** |
| Có tiền không | không | **có** — escrow, doanh thu, điểm |
| Có luật cứng đã tồn tại | `mayQuyet: false` | `ai_cannot_approve` — **mạnh hơn** |

Vì vậy ADR này **hẹp hơn** ADR-0035, không rộng hơn. Cùng một API, mức độ được phép thấp hơn.

---

## 2. Luật cứng đã có — và nó không cần sửa

`portal/lib/game-handoff.mjs` đã chặn AI ở tầng quyền, **trước** khi xét vai trò:

```js
if (actor.kind === 'ai') {
  return { ok: false, reason: 'ai_cannot_approve',
           message: 'AI không được duyệt bản nộp. Đây là nguyên tắc HITL.' };
}
```

Dòng chú thích ngay trên nó giải thích thứ tự — và thứ tự đó đúng:

> *"AI bị chặn TRƯỚC khi xét vai trò — cùng thứ tự với `policy.mjs`, và cùng lý do: nếu báo 'thiếu
> vai trò', người sửa sẽ đi cấp thêm quyền rồi vẫn hỏng."*

Đây là bài học tôi đã viết ở ADR-0035 §6.1 (chọn ngầm nhà cung cấp), nhưng repo này đã làm đúng
**trước** tôi. **ADR này không sửa dòng nào trong `game-handoff.mjs`.** Nếu một đề xuất OpenRouter
nào cần sửa hàm đó, đề xuất đó sai.

---

## 3. ✅ Việc áp dụng được: **đọc bản nộp** — và nó lấp một chỗ trống thật

### 3.1. Chỗ trống

Khi studio nộp bản 2.0, `validateSubmission` kiểm **máy kiểm được**:

| Kiểm | Có |
|---|---|
| `manifest.json` là JSON hợp lệ | ✅ |
| có `game` / `version` / `base_sha256` | ✅ |
| `base_sha256` khớp gói portal đã bàn giao | ✅ |
| version mới **lớn hơn** bản đang có | ✅ |
| gói **không giống hệt** gói gốc | ✅ |

Tất cả đều là **so khớp và bất biến**. Không có gì kiểm **nội dung có mâu thuẫn không**: changelog
nói "sửa lỗi âm thanh" nhưng diff không chạm tệp âm thanh; mô tả nói "thêm 3 màn" nhưng không có tệp
màn mới; version nhảy 1.0 → 9.0 mà gói gần như y hệt.

PO đọc thủ công. Với 6 thể loại và nhiều studio, đó là chỗ **trôi**.

### 3.2. Đề xuất hẹp

| Làm | Không làm |
|---|---|
| Chạy Decisions API trên `manifest.json` + changelog + danh sách tệp đã đổi | Không đọc **toàn bộ mã nguồn** game (xem §3.3) |
| Hỏi 3 câu `noul`: *có mâu thuẫn giữa mô tả và tệp đã đổi*, *version có nhảy bất thường*, *có dấu hiệu đổi tên để né `base_sha256`* | Không hỏi *"game này có tốt không"* — câu đó không có câu trả lời bằng văn bản |
| Trả về **gợi ý cho người duyệt**, cùng hình dạng `{band, action, mayQuyet:false}` | Không tạo trạng thái `approved`. Không tạo trạng thái mới nào |
| Ghi `(model, phiên bản)` vào biên bản (KVU-2 §6) | Không ghi vào `submissions` như một trường quyết định |

**Đầu ra chỉ có một chỗ để đi:** hộp thoại của người duyệt. Nếu không ai đọc, nó vô hại.

### 3.3. Vì sao KHÔNG đọc toàn bộ mã nguồn — và đây là chỗ dễ sai nhất

Hai lý do, cả hai **kỹ thuật**, không phải thận trọng:

1. **Trần ngầm của Clef.** Tài liệu OpenRouter ghi `clef`/`clef-flash` chỉ đọc **~2.000 token đầu**
   của `state` và **bỏ phần còn lại mà không báo lỗi**. Một gói game vượt 2.000 token rất nhanh.
   Đường này **không được** dùng cho gate — và cũng **không được** dùng ở đây.
2. **Nội dung game là tài sản của studio.** Gửi toàn bộ mã nguồn sang bên thứ ba là một quyết định
   pháp lý, không phải quyết định kỹ thuật. Changelog + manifest + **danh sách đường dẫn** là đủ cho
   ba câu hỏi ở §3.2, và **không** gửi mã.

> Nếu PO muốn gửi cả mã nguồn, đó là **ADR riêng** — có điều khoản studio, có chỗ trong hợp đồng,
> không phải một dòng thêm vào đây.

---

## 4. ⚠️ Việc áp dụng được nhưng phải cẩn thận: phân loại thể loại

Game9K có 6 thể loại và `choice` của Decisions API trả `{choice, probabilities, confidence}`, đúng
hình dạng cần. Nhưng:

| | |
|---|---|
| Trường hợp dùng | gợi ý thể loại khi studio nộp, và gợi ý **lại** khi PO thấy game lệch |
| Ai quyết | **PO**, luôn. Gợi ý không ghi vào DB như một trường quyết định |
| Rủi ro thật | Phân loại sai ⇒ game vào sai bảng ⇒ studio mất hiển thị ⇒ **mất tiền** |
| Vì sao `confidence` không cứu được | Tài liệu nói `confidence` là **độ tập trung của phân bố**, không phải độ đúng. Không có phép đo hiệu chỉnh nào ở đây |

Đây là chỗ dễ trượt sang "AI tự gắn nhãn". **Không** làm vậy. Xem §5.

---

## 5. Ba thứ OpenRouter KHÔNG được làm trong Game9K

### 5.1. Không duyệt, không từ chối, không đổi trạng thái

`SUBMISSION_STATUS` có đúng ba giá trị và `in_review` là **mặc định**. Chú thích trong tệp:
*"không có đường nào tạo ra `approved` trực tiếp từ lúc nộp. Đó là điểm mấu chốt: duyệt là hành
động riêng."* Một tính năng đọc **không** được mở đường thứ hai.

**Đã kiểm bất biến này (không sửa gì):** grep toàn `portal/` — chỉ có **hai** chỗ ghi `'approved'`:

| Chỗ | Ghi khi nào | Có phải "duyệt bản nộp"? |
|---|---|---|
| `decideHandoff()` — `store.mjs:423` | sau khi route đã kiểm quyền | ✅ **đúng chỗ duy nhất** |
| `recordHandoff()` — `store.mjs:354` | lúc **phát hành** gói (`kind='issued'`) | ❌ không — đó là gói bàn giao, luôn dùng được |

`createSubmission()` viết cứng `'in_review'` và **không có tham số `status`**, kèm chú thích:
*"Nếu hàm này nhận `status`, sẽ có ngày ai đó truyền 'approved' từ route và toàn bộ cơ chế duyệt
thành hình thức."* Bất biến **đang giữ đúng** — nên ADR này không đụng vào nó.

**Đã làm (Q-ADR38-c):** `portal/test/game-handoff-invariant.test.mjs` khoá điều trên.

Test này kiểm **ở mức nguồn**, có chủ ý: đường vòng không phải một hành vi để gọi
vào, nó là một **cấu trúc** để không được xuất hiện. Năm điều được khoá:

1. `UPDATE game_handoffs` xuất hiện **đúng một lần** trong `store.mjs`, và nằm trong `decideHandoff`.
2. `createSubmission` **không có** tham số `status` và viết cứng `'in_review'`.
3. Route `/api/submissions/:id/decide` gọi `canApproveSubmission` **trước** `decideHandoff`, và dùng kết quả để chặn.
4. `game-handoff.mjs` không chứa `UPDATE`/`INSERT` — nó là hàm thuần.
5. Nhánh `actor.kind === 'ai'` đứng **trước** `can(...)`.

Đã phá thử từng điều: thêm `approveNow()` ghi `'approved'` trực tiếp · cho
`createSubmission` nhận `status` · đảo thứ tự trong route · cho `game-handoff.mjs`
tự ghi DB · đảo thứ tự AI-vs-vai trò. **Cả năm đều đỏ**, mỗi lần đỏ đúng lý do của nó.

Giới hạn, ghi trong chính tệp test: nó **không** bắt SQL dựng bằng chuỗi nối, không
bắt một route **mới** gọi `decideHandoff`, và không chứng minh hệ thống an toàn. Nó
là hàng rào cho năm đường vòng đã biết — không phải một chứng minh.

### 5.2. Không đo chất lượng game

Đây là bài học từ chính lần sửa trước ([KVU-2 §1.4](../00-framework/nguyen-ly-don-vi-khanh-tang-hai.md)):
chất lượng một phiên bản đo bằng **giờ chơi người thật** (`play_sessions`, `verified_minutes`), và
luật trong `store.mjs` nói rõ một con số **chỉ có giá trị khi ràng buộc được với một con người**.
Một lần gọi API không phải một con người, và **không phải một lượt chơi**.

Điểm chất lượng neo merkle theo phiên bản (KVU §1.2). **Không** nhét một phép đo AI vào chuỗi đó.

### 5.3. Không gửi nội dung người chơi

Bản nộp có thể chứa dữ liệu mẫu, tên người chơi trong ảnh chụp, hoặc nội dung do người dùng sinh.
Repo đã có luật không commit PII (`AGENTS.md`, ADR-0026 §5.2). Gửi sang bên thứ ba là **cùng một
luật, mức nặng hơn** — không có cách gỡ lại.

---

## 6. Điều tôi đã kiểm, và điều tôi chưa

| | |
|---|---|
| Bảng adapter `noul`/`choice`/`score` là contract, sinh từ registry | ✅ đọc tài liệu |
| `box` chỉ có ở adapter first-party, không dùng được | ✅ đọc tài liệu |
| Clef cắt ~2.000 token **không báo lỗi** | ✅ đọc tài liệu — **lý do §3.3 tồn tại** |
| `ai_cannot_approve` chặn **trước** khi xét vai trò | ✅ **đọc mã**, `game-handoff.mjs:287` |
| `validateSubmission` chỉ kiểm so khớp/bất biến | ✅ **đọc mã** |
| Có lời gọi OpenRouter thật nào chưa | ❌ **CHƯA.** Sandbox không có `OPENROUTER_API_KEY` |
| Phân loại thể loại có đúng không | ❌ **CHƯA ĐO.** Không có nhãn người để đối chiếu |
| PO có muốn gửi tài liệu studio sang bên thứ ba | ✅ **PO trả lời CÓ**, 2026-11-23 |
| Route `/api/submissions/:id/review` có ghi trạng thái không | ✅ **KHÔNG** — 8 test HTTP, đã phá thử 3 cách ghi |
| Gói đọc có mang nội dung tệp đi không | ✅ **KHÔNG** — test truyền `content` cố tình, gói vẫn không mang |
| Có lời gọi OpenRouter thật nào chưa | ❌ **CHƯA.** Sandbox không có `OPENROUTER_API_KEY` |

**Đã có mã, chưa có lời gọi thật.** §9 mô tả phần đã hiện thực và kiểm offline. Toàn bộ hiểu biết
về *hình dạng* API vẫn đến từ tài liệu, không từ một response thật nào.

---

## 7. Ranh giới trung thực

- **OpenRouter không xem xét, không xác nhận, không bảo trợ Game9K.** API công khai, không quan hệ.
- **Không phải LLM.** Jev là bộ phân loại có xác suất; không sinh văn xuôi. Không mô tả tính năng
  này là "AI viết nhận xét cho studio".
- **Không tuyên bố hiệu chỉnh.** `confidence` là độ tập trung phân bố, không phải độ an toàn.
- **Không nói "AI hỗ trợ kiểm duyệt"** trong tài liệu cho studio. Nói đúng: *"người duyệt có thêm
  một bản đọc gợi ý"*.
- **Không chép mã** từ tài liệu OpenRouter.

---

## 9. Đã hiện thực (2026-11-23) — sau khi PO trả lời Q-ADR38-b

### 9.1. Hai tệp, ba tầng giữ ranh giới

| Tệp | Vai trò |
|---|---|
| `portal/lib/review-packet.mjs` | dựng gói đọc + đọc kết quả. **Hàm thuần** cho phần dựng, transport riêng |
| `portal/test/review-packet.test.mjs` | 34 test cho hàm thuần + transport |
| `portal/test/review-route.test.mjs` | 8 test HTTP cho route — **mỗi test đọc lại DB** |

Route: `GET /api/submissions/:id/review`, cần quyền `release.publish`.

**Ba tầng giữ cho "chỉ đọc" là thật, không phải lời hứa:**

1. **Schema.** `game_handoffs` chỉ có `manifest` (chữ), `file_count`, `bytes`. Nó **không có cột nào
   chứa nội dung tệp**. Nghĩa là route này *không thể* gửi mã nguồn dù muốn — ranh giới của §3.3 do
   DB thi hành. Có test đọc thẳng bảng và khẳng định điều đó.
2. **Hàm dựng.** `buildReviewPacket` chỉ đọc `path` và `bytes`; một `content` lọt vào mảng đầu vào bị
   bỏ ở đúng dòng map. Test truyền cố tình một API key giả trong `content` và khẳng định nó không có
   mặt trong `state`.
3. **Đầu ra.** Không có trường `ok`, `status`, `decision`, `verdict`. `mayQuyet` là hằng số, **không
   phải tham số** — truyền vào cũng không đổi được.

### 9.2. Phạm vi gửi đi — PO đã chấp thuận

| Gửi | KHÔNG gửi |
|---|---|
| `manifest.json` (game, version, sha256) | nội dung tệp game |
| changelog studio tự viết | mã nguồn |
| đường dẫn tệp + kích thước | ảnh, âm thanh, asset |

Đây đúng là ba loại PO chấp thuận ở Q-ADR38-b, **không hơn**. Việc "chỉ đường dẫn" được thi hành ở
tầng 1 và 2 phía trên.

### 9.3. Ba câu hỏi `noul` — và điều chúng KHÔNG hỏi

| Câu | Ý nghĩa câu trả lời "có" |
|---|---|
| `mo_ta_khop_tep` | Có mâu thuẫn giữa changelog và tệp đã đổi |
| `version_nhay_bat_thuong` | Số phiên bản nhảy không khớp mức thay đổi |
| `co_dau_hieu_ne_base` | Có dấu hiệu đổi tên/dời chỗ để né so khớp `base_sha256` |

Câu trả lời "có" nghĩa là **"nên đọc lại chỗ đó"**, không phải "từ chối". Có test khẳng định không
câu nào hỏi chất lượng game hay "có nên duyệt".

### 9.4. Bốn chỗ dễ hỏng, và cách chúng bị chặn

| Chỗ hỏng | Bị chặn bởi |
|---|---|
| Gửi `input` thay vì `state` ⇒ 400 không rõ lý do | test `buildReviewRequest` |
| Dùng `clef-flash` ⇒ đọc 1/6 đầu gói, trả lời trông chắc chắn | `isForbiddenModel` chặn **trước** khi gọi mạng |
| Câu trả lời thiếu ⇒ bị coi là "không có vấn đề" | vào `unanswered`, không vào `findings` |
| Route vô tình ghi trạng thái | 3 test đọc lại DB sau khi gọi; đã phá thử 3 kiểu ghi |

### 9.5. Một lỗi thật do test cũ bắt được

Bản nháp đầu import `../scripts/lib/decisions-openrouter.mjs`. `portal/test/bundle.test.mjs` **B-01
đỏ ngay**: `vercel.json` chỉ ship `{portal/**,…}`, nên import đó chạy được trên máy nhưng **500 trên
production**. Đã chuyển transport vào `portal/lib/review-packet.mjs` và thêm một test khoá hằng số
(endpoint, model mặc định) không trôi khỏi bản CLI.

Đây là lần thứ hai trong loạt việc này một cổng cũ bắt được lỗi tôi vừa tạo. Cổng đó đáng giữ.

### 9.6. Chưa làm — và không giả vờ là đã làm

- **Chưa có lời gọi OpenRouter thật nào.** Không có `OPENROUTER_API_KEY` trong sandbox. Toàn bộ
  hình dạng request/response vẫn là **đọc tài liệu**, chưa phải **đo**.
- **Ngưỡng 0.5 chưa hiệu chỉnh.** Đó là "quá nửa", không phải một ngưỡng đã đo. Tinh chỉnh cần nhãn
  người — chưa có.
- **Chưa nối vào giao diện.** Route trả JSON; chưa có chỗ hiển thị trong portal. Người duyệt gọi
  bằng API, hoặc chưa dùng gì cả.

---

## 8. Câu hỏi mở

| | |
|---|---|
| **Q-ADR38-a** | ~~Có làm phần §3 (đọc bản nộp) không?~~ **Đã làm** — xem §9 |
| **Q-ADR38-b** | ~~Gửi `manifest` + changelog + danh sách đường dẫn sang bên thứ ba có chấp nhận được không?~~ **PO trả lời: CÓ** (2026-11-23). Ba loại dữ liệu đó là **toàn bộ** phạm vi được gửi; xem §9.2 |
| **Q-ADR38-c** | ~~Có thêm test *"chỉ `game-handoff.mjs` được gán `approved`"* (§5.1) không?~~ **Đã làm** — `portal/test/game-handoff-invariant.test.mjs`, 5 test, đã phá thử cả 5 |
| **Q62a** | Có cho phép gọi mạng từ máy dev không? Đến giờ vẫn chưa trả lời (từ ADR-0029) |

---

**Trạng thái:** Proposed. Không sửa **hành vi** nào trong `portal/` — chỉ **thêm** một tệp
test (Q-ADR38-c đã trả lời). Chưa có lời gọi OpenRouter thật nào.
