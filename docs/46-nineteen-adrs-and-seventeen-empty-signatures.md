# 46 — Mười chín ADR thật, và mười bảy chữ ký không có người

> **Tài liệu sống:** `docs/46-nineteen-adrs-and-seventeen-empty-signatures.md` — bản gốc ở đây.
> **Trạng thái:** `DONE` (vòng 34) · portal đã cập nhật: `gamefun9k.vercel.app`
> **Tiền đề:** `docs/45` (portal `/task`) · `docs/44` §3.3 · `pm/action-register.json` (P8)

---

## 0. Năm dòng

Yêu cầu: thả **19 tệp ADR** (0018–0036) vào portal — phần lớn khoảng trống mà `docs/45` §3 đã hiện 20 dòng đỏ.

1. **Đã nhận đủ 19 tệp.** Portal từ **16 → 35 ADR có tệp**, 20 → 8 dòng thiếu.
2. **Nhưng chúng dùng ba format header khác nhau**, và generator của tôi chỉ đọc được một. Nếu thả vào mà không sửa, **11 tệp** sẽ lấy trạng thái từ `README` thay vì từ chính tệp — đúng khi may mắn, và **không cổng nào đỏ**.
3. **Phát hiện lớn hơn cả 19 tệp:** bộ ADR này có **17/35 tệp do một chức danh ký**, không phải người có tên. 14 tệp ghi `Principal Architect *(chờ ký)*` — một vai, không phải ai.
4. **`README.md` của thư mục ADR tự nói điều cấm đó:** *"Mỗi ADR phải có người quyết có tên"*, và đồng thời ở cột trạng thái ghi `Accepted (chờ ký)`. Hai câu trong cùng một tệp.
5. **Portal không sửa lịch sử.** Tệp vẫn ghi `Accepted`; portal hiện **"Chờ ký"** và một nhãn riêng: *chỉ có chức danh — chưa ai ký*.

---

## 1. Ba format header trong 35 tệp

Đây là lý do thật khiến việc "thả tệp vào" không đơn giản.

| Format | Ví dụ | Tệp |
|---|---|---|
| Bảng meta 2 cột | `\| **Trạng thái** \| Accepted (chờ ký) \|` | ADR-0001…0018 (**18**) |
| In đậm một dòng | `**Trạng thái:** Accepted` | ADR-0019…0033, 0035, 0036 (**16**) |
| Gạch đầu dòng | `- **Trạng thái:** Proposed` | ADR-0034 (**1**) |

`scripts/gen_portal_data.py` cũ chỉ có mẫu bảng. Đo được trước khi sửa: **11 tệp đọc ra `state: unknown`** và `status_raw: ""`. Cổng 25 vẫn PASS vì nó không biết phải đỏ ở đâu — dữ liệu trông "hợp lệ", chỉ là rỗng.

**Cách sửa:** bảng mẫu theo từng trường, mỗi trường ba mẫu, và mẫu **gộp hai vai trên một dòng** (`**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)`) phải đứng **trước** mẫu một-dòng.

### 1.1. Hai lỗi regex đáng ghi lại

**Lỗi 1 — `[-*]` khớp cả `*` in đậm.** Mẫu gạch đầu dòng `^[-*][ \t]*\*\*Người quyết:` nuốt luôn dòng `**Người quyết:** …` không có gạch, vì `*` nằm trong character class. Sửa thành `[-*]{0,2}`.

**Lỗi 2 — thứ tự mẫu.** Với ADR-0034, mẫu `^[-*]{0,2}[ \t]*\*\*Người quyết:\*\*[ \t]*([^\n]+?)[ \t]*$` không khớp dòng nào (dòng đó bắt đầu bằng `**Người đề xuất:**`), nên `decider` rỗng — nhưng **trước đó** một mẫu khác lại khớp và trả về chuỗi rỗng. Thứ tự mẫu là ngữ nghĩa, không phải trang trí.

Sau khi sửa: **35/35 tệp đọc được đủ `trạng thái` + `ngày`**, 0 tệp rỗng.

---

## 2. Phát hiện: 17 chữ ký không có người

Kiểm từng tệp, đếm bằng máy:

| Người quyết ghi trong tệp | Số tệp |
|---|---|
| `Principal Architect *(chờ ký)*` | **14** |
| `Principal Architect + Legal *(chờ ký)*` | 1 |
| `Tech Lead On-chain *(chờ ký)*` | 1 |
| `Founder *(chờ ký)*` | 1 |
| `Project Owner (Lê Xuân Khánh)` | 18 |
| **Tổng không có tên người** | **17 / 35** |

`README.md` của thư mục ADR viết, ngay dòng 3:

> *"Mỗi ADR phải có người quyết có tên. ADR chưa ký = `Proposed` và **không** được dùng để justify code đã merge."*

Và cùng tệp đó, cột trạng thái (trích nguyên văn, bỏ link):

```
| 0001 | Vòng lặp phase theo module | **Accepted (chờ ký)** | Quy trình |
```

Hai câu trong **cùng một tệp**, và chúng không thể cùng đúng. `Accepted` nghĩa là đã nhận; `(chờ ký)` nghĩa là chưa ai ký. Nếu chưa ai ký thì nó **không** được dùng để biện minh cho mã đã merge — và 12 ADR trong nhóm này đã được dùng đúng như thế.

### 2.1. Vì sao `role_only` là trường hợp nặng hơn `unsigned`

Ba cách "chưa ký" cần ba câu trả lời khác nhau, nên portal lưu **ba giá trị**, không phải một boolean:

| `signature` | Nghĩa | Cần làm gì |
|---|---|---|
| `named` | có tên người trong tệp | xong |
| `role_only` | có **chức danh**, không có tên | **hỏi ai thật sự giữ vai đó** |
| `unsigned` | không có gì | **ký** |

`role_only` nặng hơn vì nó **trông như đã ký**. Một dòng trống thì ai cũng thấy trống; `Principal Architect` trông như một người đã đồng ý. Đó là lý do phải tách.

### 2.2. Portal không sửa lịch sử

Tôi **không** sửa 17 tệp ADR. Chúng là bản ghi lịch sử, và sửa chúng thành `Proposed` sẽ là viết lại quá khứ để hôm nay trông gọn hơn.

Thay vào đó dữ liệu có **hai trường**:

| Trường | Đọc từ đâu | Dùng để |
|---|---|---|
| `state` | nguyên văn trong tệp (`Accepted`) | truy vết — tệp nói gì |
| `display_state` | suy ra: nếu `signature ∈ {role_only, unsigned}` thì `proposed` | **hiển thị** |

Portal hiện `display_state`. Với 12 ADR `accepted` + `role_only`, portal hiện **"Chờ ký"** kèm nhãn *chỉ có chức danh — chưa ai ký*. Tệp vẫn nói `Accepted`. Cả hai đều đúng, ở hai tầng khác nhau.

**Con số hiện trên portal:** 18 ADR có tên người ký · 17 chỉ có chức danh · 0 hoàn toàn chưa ký · 8 thiếu tệp.

---

## 3. Cổng đã bắt gì trong vòng này

Cổng 25 thêm **bất biến thứ 6** (`inv_signature_is_a_person`) và selftest lên **6/6**:

```
PORTAL: PASS — 209 kiểm tra · 6 bất biến · 12 việc · 43 ADR (35 có tệp, 19 chờ ký, 8 thiếu tệp)
PORTAL SELFTEST: PASS — 6/6 (1 đối chứng + 5 phép phá)
```

### 3.1. Bốn lỗi của chính cổng, theo thứ tự phát hiện

| # | Lỗi | Vì sao nguy hiểm |
|---|---|---|
| 1 | Bắt oan ADR-0019…0022 vì chúng ghi `Project Owner`, không kèm tên | Cổng đỏ vì câu chữ, không vì sự thật ⇒ người ta sẽ tắt nó |
| 2 | Bắt oan ADR-0034 vì extractor trả `decider` rỗng | Cùng lý do |
| 3 | Kiểm `state` thay vì `display_state` ⇒ báo 20 vi phạm trong khi chỉ 12 | Báo động giả làm loãng báo động thật |
| 4 | **Kiểm dữ liệu thay vì kiểm màn hình** | Nghiêm trọng nhất — xem §3.2 |

### 3.2. Lỗi thứ tư: cổng đọc biến, không đọc màn hình

Tôi viết bất biến mới trong `check_portal_render.mjs` như thế này:

```js
for (const item of roleOnly) ok(item.display_state !== "accepted", …);
```

Nó kiểm `item` — **dữ liệu**. Rồi tôi thử phá: đổi `chip(i.display_state)` thành `chip(i.state)` trong `app.js`, tức là **vẽ sai**, và cổng vẫn **PASS**. Vì dữ liệu vẫn đúng; chỉ màn hình sai.

Sửa thành đọc **thẻ đã vẽ**:

```js
const drawn = stateChip ? stateChip.textContent.trim() : "(không có nhãn)";
ok(!drawn.includes("Đã nhận"), `${item.id} … THẺ VẼ RA "${drawn}"`);
```

Thử phá lại: **FAIL 12 vi phạm** — `ADR-0001 … THẺ VẼ RA "Đã nhận" — phải là "Chờ ký"`.

Đây đúng là lỗi `docs/45` §5.4 ghi lần trước, lặp lại ở một cổng khác: **một cổng kiểm dữ liệu sẽ không bao giờ bắt được một lỗi vẽ.** Cùng một sai lầm, hai vòng liên tiếp — nên lần này ghi thành quy tắc: *nếu điều đang bảo vệ là thứ người ta **nhìn thấy**, cổng phải đọc thứ đã vẽ ra.*

---

## 4. Bằng chứng

```
PORTAL: PASS — 209 kiểm tra · 6 bất biến · 12 việc · 43 ADR (35 có tệp, 19 chờ ký, 8 thiếu tệp) · data.json == generator
PORTAL SELFTEST: PASS — 6/6 (1 đối chứng + 5 phép phá)
PORTAL RENDER: PASS — app.js chạy trong DOM tối thiểu · 9 việc vẽ ra · 43 ADR · nhãn khớp dữ liệu
GATE WIRING: PASS — 45 kiểm tra · 26 cổng trong sổ
DOCS LINK CHECKS: 218/218 passed
CONTRADICTIONS: PASS — 7849 kiểm tra · 4 cặp · 49 tệp
```

Bốn phép phá đã chạy thật trên bản sao, cả bốn đều đỏ đúng chỗ:

| Phép phá | Kết quả |
|---|---|
| Đổi `display_state` → vẽ `state` | **FAIL 12** — `THẺ VẼ RA "Đã nhận"` |
| Bỏ nhãn chữ ký trên thẻ | **FAIL 12** — `thẻ hiện "Đã nhận"` |
| Trả lại công thức viết tắt cũ | **FAIL** — `avatar hiện "XK"` |
| Ẩn một việc khỏi bảng | **FAIL** — `vẽ 8 dòng, sổ có 9` |

---

## 5. Ba câu hỏi

1. **17 ADR do chức danh ký — `Principal Architect` là ai?** Nếu là bạn, sửa 17 dòng `Người quyết` thành tên bạn và cổng tự xanh. Nếu là một vai sẽ do người khác giữ, cần biết ai — vì hiện tại **không ai** chịu trách nhiệm cho 14 quyết định đã `Accepted`. Đây là câu hỏi cho **P8** và nên thành một việc riêng.
2. **Sửa 17 tệp ADR, hay để `display_state` làm việc đó?** Tôi chọn cách thứ hai vì sửa lịch sử là việc của người, không phải của tôi. Nhưng nếu bạn muốn tệp tự đúng, đó là 17 dòng và một lần chạy.
3. **8 ADR còn thiếu (0008, 0037–0043) có tệp không?** `README` liệt kê chúng; thư mục không có. Nếu bạn có, thả vào là xong — không cần sửa mã.

---

## 6. Chưa làm

| | Nợ | Vì sao để lại |
|---|---|---|
| **W1** | Chưa có `P*` cho "gán tên người cho 17 ADR do chức danh ký" | Cần biết `Principal Architect` là ai trước. Đã nêu ở §5 câu 1 |
| **W2** | 8 ADR thiếu tệp | Cần tệp, không cần mã |
| **W3** | `README.md` của thư mục ADR vẫn ghi `Accepted (chờ ký)` — mâu thuẫn gốc | Sửa nó là sửa tài liệu nguồn của bạn. Portal đã hiện đúng bất kể README nói gì |
| **W4** | Cổng 25 chưa đọc được format header thứ tư, nếu có | Ba format đã gặp đều xử lý; nếu gặp format mới, cổng 25 sẽ đỏ ở `display_state` rỗng chứ không im lặng |
