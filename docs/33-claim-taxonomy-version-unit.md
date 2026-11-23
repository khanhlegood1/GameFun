# Nguyên lý đơn vị phiên bản, và loại của từng câu tuyên bố

> **Tài liệu sống:** `docs/33-claim-taxonomy-version-unit.md`
> **Trạng thái:** `SCOPING` — đánh giá 2 nguồn + **đã dựng sổ đăng ký tuyên bố** (`pm/claims-registry.json`, `scripts/check_claims.py`)
> **Ngày:** 22/11/2026
> **Đầu vào:** `awesome-ai-sdks` (đã xử lý ở `docs/32`) · `MetaPump/docs/00-framework/nguyen-ly-don-vi-khanh.md` (ADR-0023)
> **Câu hỏi của người yêu cầu:** *"có thêm gì nổi trội hot trend trong thời đại AI và Blockchain để **thuyết phục nhà đầu tư** vào Game9K?"*
> **Liên quan:** `docs/32` · `docs/27` §1.1 (nhãn nguồn) · `docs/31` §2 · `AGENTS.md` · `docs/WHITEPAPER` §9

---

## 0. Kết luận trước — và nó không phải câu người yêu cầu chờ

**Thêm một ý "hot trend" nữa là cách chắc chắn nhất để làm yếu hồ sơ.** Nhà đầu tư không thiếu trend; họ thiếu lý do để tin một con số. Thứ đáng thêm vào Game9K lúc này **không phải một tuyên bố mạnh hơn, mà là một tuyên bố kiểm được hơn**.

Và tài liệu MetaPump đưa ra đúng cơ chế để làm việc đó — nhưng **không** ở chỗ nó khoe thành tựu, mà ở chỗ nó **tự phân loại** từng câu của chính mình.

| # | Câu hỏi | Trả lời |
|---|---|---|
| **1** | Nguyên lý đơn vị Khánh (KVU) nói gì? | *Đơn vị tài sản của giao thức game là **phiên bản**, không phải con game* (§1) |
| **2** | Game9K đã có nó chưa? | **Có, và mạnh hơn** — nhưng **chưa đặt tên**, nên không ai trích dẫn được (§2) |
| **3** | Nên đặt tên không? | **Có, nhưng không đặt theo tên người.** Đặt tên cơ chế: **VGU-BM** (§2.2) |
| **4** | Phần đáng chép nhất là gì? | **Không phải** nguyên lý — mà là **bảng phân loại tuyên bố** (§3) |
| **5** | Nó chỉ ra lỗi gì trong repo này? | **Ba** câu ở `WHITEPAPER`, cả ba **chưa có bằng chứng**: dòng 3 (tiêu đề, cụm `đầu tiên trên Thế giới`), dòng 583 (cụm `Vị thế tiên phong độc quyền`), dòng 736 (cột kiểm thử S8) — chi tiết §3.3 |
| **6** | Đã dựng gì? | `check_claims.py`: **5 bất biến**, sổ đăng ký **3 mục** có owner + hạn xem lại (§4) |
| **7** | Có thêm gì "hot" không? | **Không.** §5 nói rõ vì sao thêm là **trừ điểm**, kèm 3 thứ **nên** nói thay thế |

---

## 1. KVU — phát biểu, và ba tầng bằng chứng của chính nó

### 1.1. Một câu

> *"Đơn vị tài sản của một giao thức game là **phiên bản**, không phải con game."*

Ba hệ quả: **curve riêng** · **escrow riêng** · **điểm riêng** — và điều kiện mở khoá: *chứng minh chất lượng bằng **giờ chơi thật***.

### 1.2. Điều làm tài liệu đó đáng tin — và nó **không** phải nguyên lý

§3 của họ tự chia ba tầng và **không gộp**:

| Tầng | Trạng thái họ ghi |
|---|---|
| Toán + mật mã + code mẫu | ✅ `PROVEN` — 4 bổ đề, 48 kiểm tra tự động |
| Hệ thống chạy thật | ❌ chưa có — `programs/` trống |
| **Giá trị kinh tế** *(người mua có phân biệt được phiên bản?)* | ⚠️ `NEEDS_DATA` — **vẫn là giả thuyết** |

Và câu chốt của họ:

> *"Chứng minh cơ chế **không thể vi phạm bất biến** không chứng minh bất biến đó **tạo ra giá trị**."*

> **Đây là thứ đáng chép nhất trong toàn bộ tài liệu.** Không phải KVU — mà là việc họ **tự nói ra** rằng tầng toán đã xong còn tầng kinh tế thì chưa. Một dự án dám viết câu đó trong tài liệu công khai là một dự án **kiểm được**.

---

## 2. Game9K đã có nguyên lý này chưa?

### 2.1. Có — và ở dạng mạnh hơn

`docs/WHITEPAPER` §6 ghi: *"hợp nhất 4 nguyên tử công nghệ – kinh tế xoay quanh **đơn vị duy nhất là Phiên bản (version)**"*. Và `docs/PRD` §0 đặt **mốc M1–M4** làm điều kiện mở khoá — đúng "chứng minh bằng giờ chơi thật".

| KVU | Game9K |
|---|---|
| Curve riêng cho mỗi phiên bản | **VGBC-4T** — bonding curve theo mốc, `docs/WHITEPAPER` §6.1 |
| Escrow riêng | Tranche mở theo milestone `M_k`, `docs/PRD` §2 |
| Điểm riêng, neo merkle | `verified_play` + `pop_score`, `docs/YELLOWPAPER` |
| Mở khoá bằng giờ chơi thật | Play-Gate + Player Fit Test, `docs/PRD` FR-ARN-01 |

> **Nên câu trả lời cho "Game9K có gì nổi trội" không phải "chúng tôi có thêm một nguyên lý" — mà là "chúng tôi đã có nó, đã có **mã kiểm**, và nay có **tên**".**

### 2.2. Đặt tên: **VGU-BM**, không đặt theo tên người

MetaPump đặt tên theo người phát biểu (PO của họ) và §4.3 của họ giải thích vì sao điều đó **không** ngụ ý phát minh. Nhưng với Game9K, đặt tên theo người có ba vấn đề cụ thể:

1. **Người ký là ai?** Repo này chưa có PO đứng tên trong `AGENTS.md`; một nguyên lý mang tên một người chưa được ghi ở đâu là một câu hỏi cho nhà đầu tư, không phải một câu trả lời.
2. **Nó không trích dẫn được giữa câu.** *"Theo VGU-BM…"* dùng được; *"theo nguyên lý đơn vị của anh X…"* thì không, trong một deck tiếng Anh.
3. **Nó tự đặt mình ngang hàng một cái tên.** Đúng điều §2.3 của họ **cấm**: so sánh chỉ có giá trị **sau** thành tựu.

**Đề xuất tên:** **VGU-BM** — *Version-Gated Unit, Bonding-curve Model*.

| Thuộc tính | Giá trị |
|---|---|
| Trích dẫn | *"Under VGU-BM, each version — not the game — is the asset unit."* |
| Nguồn gốc đã có | `docs/WHITEPAPER` §6 (4 nguyên tử), `docs/YELLOWPAPER` (bất biến VGBC-4T) |
| Khác KVU ở đâu | KVU là **phát biểu**; VGU-BM là **phát biểu + bốn bất biến kiểm bằng máy** (`verify_protocol_math.py`, 100%) |
| Tên này có phải tuyên bố "đầu tiên"? | **Không.** Đây là tên **cơ chế của chúng tôi**, không phải tuyên bố về thị trường |

> **Ghi công (nếu dùng):** KVU của MetaPump và VGU-BM nói cùng một điều. Ghi ở **chân trang** một lần: *"Phát biểu tương đương độc lập: KVU (MetaPump, 2026)."* Đó là **dẫn nguồn**, không phải tự so — và `check_claims.py` phân biệt được hai việc đó (§4.2).

---

## 3. Phần thật sự đáng chép: **loại của từng câu**

### 3.1. Bốn kiểu viết bị cấm (§4.2 của họ)

| ❌ Cấm | Vì sao |
|---|---|
| *"X đã chứng minh rằng…"* khi X chỉ là một lời `đề xuất` | Đề xuất không chứng minh gì; nó **đề nghị** |
| *"Người phát minh ra X"* | Framing "phát minh" bị chính PO bác — dùng **khám phá** / **phát biểu** |
| `X` là `mô hình đầu tiên`… | Vi phạm chính sách tuyên bố; không có phản ví dụ nào bác được một **đề xuất**, nhưng có phản ví dụ cho câu *"chưa ai làm"* |
| Tự so với người nổi tiếng **trước** thành tựu | So sánh có giá trị **sau**; đặt trước thì nó là **tuyên bố**, không phải **quan sát** |

### 3.2. Và điều dễ bỏ sót nhất: **ba tầng không gộp**

Một câu như *"cơ chế đã chứng minh và giá trị kinh tế đã rõ"* trộn hai tầng có trạng thái **ngược nhau**. `check_claims.py` bất biến 4 bắt đúng việc đó.

### 3.3. Áp vào Game9K — hai câu đang có vấn đề

Cổng quét **toàn bộ** `docs/` + `README.md` và tìm được **đúng ba** tuyên bố về thế giới — cả ba ở `WHITEPAPER`:

| Dòng | Câu | Nhãn đề xuất |
|---|---|---|
| **3** (tiêu đề) | *"Bệ phóng Vốn đồng bộ theo phiên bản Game **đầu tiên trên Thế giới**"* | `[CHƯA KIỂM CHỨNG]` |
| **583** | *"**Vị thế tiên phong độc quyền (Category Creator):** Nền tảng **đầu tiên** kết hợp…"* | `[CHƯA KIỂM CHỨNG]` |
| 736 | *"Dự án đầu tiên tốt nghiệp tự động 0% chênh lệch giá"* (cột **kiểm thử** của S8) | `[ĐỀ XUẤT]` |

> **Ba câu này không được sửa trong vòng này.** Lý do: chúng nằm trong **nguồn số** (`WHITEPAPER.md`), và sửa chúng là **rebuild 4 PDF** — việc `AGENTS.md` cấm làm tuỳ tiện. Thay vào đó chúng được **đăng ký** trong `pm/claims-registry.json` với `status: OPEN`, kèm **câu viết lại đề xuất** và **điều kiện gỡ** (`blocked_on`).
>
> Một tuyên bố `OPEN` là một **món nợ có tên người và hạn** — khác hẳn một tuyên bố không ai để ý.

---

## 4. Đã dựng: `check_claims.py` + sổ đăng ký

```bash
python3 scripts/check_claims.py            # 5 bất biến
python3 scripts/check_claims.py --audit     # liệt kê tuyên bố đã lọc + nhãn/sổ
python3 scripts/check_claims.py --selftest  # 7 phép thử, chạy trong CI
```

```
CLAIMS: PASS — 16 kiểm tra · 5 bất biến · 3 tuyên bố về thế giới, 3 mục trong sổ đăng ký
CLAIMS SELFTEST: PASS — 7/7 phép thử đúng chiều (6 phép phá + 1 đối chứng)
```

`--audit` in ra **đúng ba** dòng, cả ba đã có chủ:

```
  R WHITEPAPER.md:3   «đầu tiên trên Thế giới» → sổ: [CHƯA KIỂM CHỨNG] (OPEN)
  R WHITEPAPER.md:583 «tiên phong»             → sổ: [CHƯA KIỂM CHỨNG] (OPEN)
  R WHITEPAPER.md:736 «Dự án đầu tiên»         → sổ: [ĐỀ XUẤT] (OPEN)
3 tuyên bố · 3 đã xử lý · 0 chưa
```

### 4.1. Năm bất biến

| # | Bất biến | Bắt được gì |
|---|---|---|
| **1** | Mọi tuyên bố có **nhãn trên cùng dòng** hoặc **tên trong sổ** | Câu "chưa ai làm" không ai ký |
| **2** | Không `đề xuất` + `đã chứng minh` cùng dòng | Đề xuất được viết như thành tựu |
| **3** | Không tự so với **tên người** | Trích *"giống như **tên người nổi tiếng**"* trước khi có thành tựu |
| **4** | Không trộn `PROVEN`/`NEEDS_DATA`/`NEEDS_SYSTEM` mà không nêu tầng | Gộp ba tầng bằng chứng |
| **5** | Mỗi mục sổ có `owner` + `reason` + `review_by` | Mục "để sau" = mục không bao giờ |

### 4.2. Ba lần cổng báo sai — và tôi sửa **phép khớp**, không hạ chuẩn

Đây là phần đáng ghi nhất, vì nó là lỗi của chính tôi:

| Bản | Kết quả | Vấn đề |
|---|---|---|
| **1** | **46** vi phạm | Bắt *"vòng lặp đầu tiên"*, *"24 giờ đầu tiên"*, *"bản mẫu đầu tiên"* — **không** phải tuyên bố gì |
| **2** | **6** vi phạm | Thu hẹp còn "chủ thể thị trường + từ khoá", nhưng vẫn bắt *"tự so với Poki"* — so sánh **sản phẩm** là việc phải làm, không phải tự đề cao |
| **3** | **2** vi phạm | Còn đúng hai câu thật: `WHITEPAPER:583` và `736` — **nhưng bỏ sót tiêu đề dòng 3** |

> Một cổng báo sai **45/46** lần sẽ bị tắt trong một tuần — và khi bị tắt thì nó **không bảo vệ được câu thứ 46**. Nên phép khớp ở đây **hẹp có chủ đích**: từ khoá tương đối (`đầu tiên`, `chưa ai`) chỉ tính khi đứng sau một **chủ thể thị trường** (nền tảng, dự án, mô hình, bệ phóng…), không tính khi đứng sau một **đơn vị thời gian/đếm** (giờ, khối, vòng lặp, bản mẫu). Cụm **bậc nhất với thế giới** (`đầu tiên trên thế giới`, `tiên phong`) thì tính **kể cả khi đứng một mình** — và đó chính là chỗ bản 3 sai (§4.4).
>
> Đây **không** phải hạ chuẩn: danh sách "chủ thể thị trường" là **cố định và đọc được**, không phải một whitelist theo tên tệp. Câu thật vẫn đỏ (phép phá 1).

Một chỗ nữa: `norm()` ban đầu bỏ **toàn bộ** ký tự không phải chữ/số, nên `**Vị thế…**` không khớp `match` trong sổ. Nay `*` được giữ — vì cụm trong sổ thường trích nguyên đoạn có in đậm.

### 4.3. Sáu phép phá — và **một phép đã lọt**

| # | Phá | Kết quả |
|---|---|---|
| 1 | thêm *"nền tảng đầu tiên trên thế giới"* vào một tài liệu mới | ❌ bắt đúng dòng |
| 2 | xoá `review_by` của một mục sổ | ❌ `thiếu review_by — không có mục 'để sau'` |
| 3 | `đề xuất` + `đã chứng minh` cùng dòng | ❌ |
| 4 | Một câu tự sánh mình với **Steve Jobs** | **✅ LỌT** — rồi bị bịt |
| 5 | trộn `PROVEN` + `NEEDS_DATA` | ❌ |
| 6 | **đối chứng** — dòng dạy học trong backtick | ✅ phải **sạch**, và đã sạch |
| 7 | đơn vị **đếm** + so sánh bậc nhất với thế giới (*"game đầu tiên trên Thế giới"*) | ❌ |

**Phép phá 4 lọt vì** điều kiện miễn trừ cũ có chữ `chúng tôi` — tức là câu **càng rõ tự so** thì lại **càng được miễn**. Đã sửa: chỉ miễn khi tên được dẫn như **nguồn** (`theo X`, `X đã nói`). Chạy lại: đỏ đúng chỗ.

**Phép 7 ra đời vì một lỗi thật:** bản 3 lọc theo *"đơn vị thời gian/đếm đứng trước từ khoá thì không phải tuyên bố"*. Luật đó đúng với *"vòng lặp đầu tiên"*, nhưng **sai** với *"Game đầu tiên trên Thế giới"* — vì `game` là đơn vị đếm mà `đầu tiên trên Thế giới` là so sánh bậc nhất với **thị trường**. Hậu quả: bản 3 **bỏ sót chính tiêu đề `WHITEPAPER` dòng 3**, thứ rõ ràng nhất trong cả repo.

### 4.4. Lần thứ tư: cổng **bỏ sót** chính tiêu đề whitepaper

Cách sửa không phải "thêm `game` vào danh sách chủ thể" (sẽ bắt oan *"tựa đầu tiên lên cổng"*), mà là tách **hai mức**:

| Mức | Cụm | Đứng một mình có tính không? |
|---|---|---|
| **Bậc nhất với thế giới** | `đầu tiên trên thế giới` · `đầu tiên trên thị trường` · `duy nhất trên thị trường` · `tiên phong` | **Có** — tự nó đã là khẳng định về thị trường |
| **Tương đối** | `chưa ai` · `chưa từng có` · `không ai làm` · `đầu tiên` | **Không** — phải có chủ thể thị trường đứng trước |

Mức thứ hai phải giữ chặt, vì nếu không sẽ bắt oan *"nhu cầu trở nên cấp bách **chưa từng có**"* — đó là trạng từ nhấn mạnh, không phải tuyên bố. Lần này cổng báo **5 chỗ sai**, gồm cả hai dòng trong chính bảng này. Cách sửa: gỡ `` `backtick` `` **và** `"ngoặc kép"` trước khi khớp — chỗ nào người viết **nhắc tới** câu chữ thì đã đánh dấu bằng cú pháp, chỗ nào **dùng** thì không.

### 4.5. Lần thứ năm: **chính tài liệu này** bị cổng bắt

Viết xong bảng dạy học ở §3.1 thì cổng **đỏ 9 chỗ**, tất cả đều nằm trong `docs/33`: chính bảng dạy *"đừng viết câu đầu tiên"* lại bị đọc là **đang viết** câu đó. Đây là bài học chung cho mọi cổng quét văn xuôi:

| Cách sửa | Vì sao **không** dùng |
|---|---|
| Thêm `docs/33` vào danh sách miễn | Whitelist theo tên tệp = cổng chết ở tệp thứ hai |
| Bỏ bớt từ khoá | Hạ chuẩn, và câu thật `WHITEPAPER:583` sẽ lọt |
| **Gỡ `` `backtick` `` và `"ngoặc kép"` trước khi khớp** | ✅ Chỗ nào người viết **nhắc tới** câu chữ thì đã đánh dấu bằng cú pháp; chỗ nào **dùng** thì không |

Đối chứng bắt buộc: **phép thử P6** — một dòng dạy học trong backtick phải **sạch**. Không có đối chứng này thì lần sau ai đó "sửa" bằng cách nới luật, và cổng mất tác dụng mà vẫn **báo xanh**.

---

## 5. Về "hot trend để thuyết phục nhà đầu tư"

### 5.1. Vì sao **không** thêm

| Thêm gì | Hậu quả thật |
|---|---|
| "AI Agent + Blockchain" như một dòng sản phẩm | Game9K **không** bán agent. `docs/29` §2 và `docs/31` §2 đã chốt: không chạy agent, không dùng LLM chấm điểm. Nói khác đi trong deck là **nói sai về chính mình** |
| Thêm một tuyên bố "đầu tiên" nữa | Mỗi tuyên bố chưa kiểm **chiết khấu** các con số đã kiểm. `eCPM $1–$3`, MOIC `16,8×`, `34` bảng là những thứ **tái lập được** — chúng yếu đi khi đứng cạnh một câu không kiểm được |
| Đổi sang thuật ngữ trend (agentic, autonomous, on-chain AI) | `docs/18` đã chốt: bán **kết quả đo được**, không bán cơ chế. Đổi từ vựng là đổi **đối tượng** khách, không đổi **giá trị** |

### 5.2. Ba thứ **nên** nói, đã có bằng chứng trong repo

Đây là câu trả lời thật cho câu hỏi "có điểm cộng gì xứng đáng":

| # | Điều để nói | Bằng chứng **chạy được** |
|---|---|---|
| **1** | **SDK của chúng tôi có hợp đồng bị khoá và ngân sách được đo** | `check_sdk.py` 18 · `check_sdk_drift.py` 11 · `check_sdk_errors.py` 22 · `2.633 → 3.975` B trong ngân sách `12.000` B |
| **2** | **Cổng của chúng tôi chứng minh được là không gọi mạng** | `check_egress_lock.py` 8 — không HTTP client trong `scripts/`, không dịch vụ AI trong workflow |
| **3** | **Chúng tôi tự phân loại tuyên bố của chính mình, và đang nợ ba câu** | `check_claims.py` 16 + `pm/claims-registry.json` **3 mục** `OPEN` có owner và hạn |

> Câu số 3 là câu **mạnh nhất** với một nhà đầu tư kỹ tính: *"chúng tôi có ba tuyên bố chưa chứng minh được, đây là tên người chịu trách nhiệm và hạn xem lại."* Không dự án nào nói câu đó. Nó đổi cuộc đối thoại từ *"tin chúng tôi đi"* sang *"kiểm chúng tôi đi"* — và Game9K là dự án **duy nhất trong phòng** có thể nói câu đó kèm **mười bốn** cổng chạy được.

---

## 6. Bốn thứ **từ chối**

| Mã | Từ chối | Lý do |
|---|---|---|
| **R1** | Đặt tên nguyên lý theo **tên người** | §2.2 — chưa có PO đứng tên trong repo; và nó tự đặt ngang hàng một cái tên, đúng thứ §2.3 của MetaPump cấm |
| **R2** | Viết rằng Game9K là `nền tảng đầu tiên` trong bất kỳ tài liệu nào **chưa** có khảo sát | §3.1 — câu `chưa ai làm` sai được, và có phản ví dụ; season/phase token là tương tự gần nhất |
| **R3** | Gộp *"toán đã chứng minh"* với *"giá trị kinh tế đã rõ"* | §3.2 — `docs/29` §2.3 và `docs/31` §2.3 cùng một nguyên tắc: **nêu rõ cái KHÔNG biết** |
| **R4** | Thêm dòng "AI Agent" vào `WHITEPAPER`/deck để bắt trend | §5.1 — Game9K không bán agent; nói khác là nói sai về chính mình, và làm yếu các con số đã kiểm |

---

## 7. Việc **không** làm trong tài liệu này

- **Không sửa `WHITEPAPER.md`** và **không dựng lại 4 PDF** — ba tuyên bố được **đăng ký** (`OPEN`), không được sửa lặng lẽ.
- Không đổi `docs/PRD` §0, không đổi số đã kiểm (`12 KB`, `3,5 s`, `W=0,60`/`H=180`, `$1–$3`, MOIC, **34** bảng, `50/50`, `0%`).
- Không thêm `PRD`/`WHITEPAPER` vào sổ đăng ký trừ khi có tuyên bố thật — sổ **không** phải danh sách tài liệu.
- Không gọi mạng, không thêm phụ thuộc.

## 8. Thứ tự làm

| # | Việc | Vì sao |
|---|---|---|
| **1** | **PO quyết ba mục `OPEN`** trong `pm/claims-registry.json`: chấp nhận câu viết lại, hay gỡ tuyên bố | Ba câu này là **chữ ký của người**, không phải của máy (`docs/25` §5) |
| **2** | Nếu sửa `WHITEPAPER` dòng 3/583/736 → rebuild 4 PDF **trong cùng PR**, theo `docs/README-PDF.md` | `AGENTS.md` luật 2: sửa nguồn, không sửa bản dựng |
| **3** | Dùng **VGU-BM** ở lần xuất hiện đầu trong whitepaper §6, kèm chân trang ghi công KVU **một lần** | §2.2 — dẫn nguồn ≠ tự so |
| **4** | Đưa `check_claims.py` vào `AGENTS.md` như luật thứ tư (cấm tuyên bố không nhãn) | `AGENTS.md` đang cấm **hứa hẹn**, chưa cấm **tuyên bố về thế giới** — đó là lỗ hổng lớn hơn |
