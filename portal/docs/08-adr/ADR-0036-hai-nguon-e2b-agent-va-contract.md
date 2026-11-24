# ADR-0036 — Hai nguồn e2b: **một chỗ meta bị sai, một chỗ contract thiếu** — không phải chỗ để thêm agent

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-18
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) · [`ADR-0016`](ADR-0016-license-compliance.md) · [`ADR-0034`](ADR-0034-ho-so-sandbox-cho-game-ben-thu-ba.md) · `.github/workflows/license.yml` · `.github/workflows/api.yml` · `scripts/check_gates.py`

> Nguồn đọc:
> [`lexuankhanh1612/awesome-ai-agents`](https://github.com/lexuankhanh1612/awesome-ai-agents) — fork của
> `e2b-dev/awesome-ai-agents`, **CC BY-NC-SA 4.0**.
> [`e2b.dev/resources/the-state-of-ai-agents…`](https://e2b.dev/resources/the-state-of-ai-agents-reliability-sdks-benchmarking-and-market-trends) — bài khảo sát.
> Cả hai đọc để **hiểu**, không chép dòng nào. Xem §7.

---

## 0. Trả lời ngắn

Hai nguồn này **không** dạy MetaPump cách làm agent. Khoản đóng góp thật của chúng hẹp hơn và
cụ thể hơn: **một chỗ meta của repo này đang SAI, một chỗ contract đang THIẾU.**

| Nguồn nói | Áp vào đâu | Giá trị |
|---|---|---|
| Danh sách agent + license **CC BY-NC-SA** | Chính bảng license của repo | 🔴 **Repo đang sai**: bảng xếp CC BY-NC-SA là "không dùng được" nhưng **CI không bảo vệ được điều đó** |
| *"If an agent fails a simple test, it won't pass the more difficult ones"* | `docs/gates/P01…P06` | 🟡 **Contract thiếu**: không có ràng buộc thứ tự |
| Agent Protocol = **OpenAPI v3** làm hợp đồng | `docs/03-api/openapi.yaml` | 🟡 **Contract thiếu**: 3 route production không có trong spec |
| "Agent là **feature ẩn** trong sản phẩm lớn" | Cách viết tài liệu | ✅ Đã đúng — ADR-0026 §4 đã chốt |
| "Đừng khoe công nghệ agent" | `docs/11-whitepaper/` | ✅ Đã đúng, và nay có nguồn để dẫn |

**Không làm:** thêm agent, thêm SDK agent, thêm `benchmark live` vào CI. ADR-0026 đã trả lời
điều đó rồi, và câu trả lời vẫn đúng.

---

## 1. I1 — Bảng license của repo đang SAI, và CI không bảo vệ được

### 1.1. Bằng chứng: gỡ cảnh báo CC BY-NC-SA, `license-audit` vẫn xanh

`license.yml` khai một danh sách "rủi ro" **viết cứng**:

```python
risky = ['minio', 'grafana', 'valkey', 'redis', 'yellowstone', 'squads', 'playgama']
```

Grep `CC BY-NC` trong `license.yml` ⇒ **0 kết quả**. Thử gỡ **toàn bộ** dòng
`theshaneobrien/tickle — CC BY-NC-SA 4.0 — ❌ Không` khỏi `docs/10-opensource/README.md` và chạy
lại phép kiểm: **`✅ license risk register đồng bộ`**.

Nghĩa là: dòng cảnh báo *duy nhất* trong bảng về một license **cấm dùng thương mại** có thể bị
xoá, và CI không nói gì. Với một repo **tài liệu** — nơi bảng license *chính là* sản phẩm — đây
không phải chi tiết nhỏ.

### 1.2. Vì sao chuyện này quan trọng hơn nó trông

`awesome-ai-agents` là **CC BY-NC-SA 4.0**: **NonCommercial** + **ShareAlike**. Đây không phải
license "ghi nguồn là xong". ND/N là hai điều khoản **khác hẳn** MIT/Apache ở chỗ:

- **NC**: dùng cho mục đích thương mại là **không được phép**, kể cả khi đã ghi công.
- **SA**: tác phẩm phái sinh phải chia sẻ dưới **cùng license** ⇒ không thể nhúng vào một giao
  thức độc quyền rồi giữ nguyên các điều khoản khác.
- CC license **không** dành cho phần mềm nói chung — dùng nó cho **danh sách/văn bản** thì hợp,
  nhưng **nội dung** vẫn bị NC ràng buộc.

Những kết luận trong bài e2b (định nghĩa agent, con số 99.9%, các phát biểu của founder) là **ý
tưởng**, không phải mã. Ý tưởng không bị copyright. Nhưng **câu chữ** thì có, và **bảng số liệu**
thì càng có.

### 1.3. Quyết định

| Làm | Không làm |
|---|---|
| Ghi hai nguồn vào `docs/10-opensource/README.md` với license thật + `❌ Không (nội dung NC)` | Không chép bảng, không chép câu chữ vào whitepaper |
| Nếu trích: **diễn đạt lại + ghi nguồn**, hoặc trích ngắn dưới quyền trích dẫn | Không dùng số liệu thị trường của e2b làm số liệu của Game9K |
| Thêm một phép kiểm bắt **họ license NC/SA** thay vì tên repo viết cứng | Không mở rộng `risky` bằng cách thêm tên repo — nó đã chứng minh là không bảo vệ được |

**Đề xuất cụ thể** (chưa làm trong ADR này, chờ PO): đổi phép kiểm từ *"repo X có trong ADR"*
thành *"mọi dòng trong bảng license có nhãn `❌` phải khớp một mẫu license trong danh sách cấm, và
danh sách đó phải được khai một lần"*. Khi bảng đổi, phép kiểm đổi theo. Hiện tại nó chỉ kiểm
bảy cái tên không liên quan gì tới CC.

---

## 2. I2 — Gate không có thứ tự, và điều đó sẽ thành lỗi thật khi bắt đầu ký

e2b dẫn Silen Naihin (AutoGPT):

> *"If an agent fails a simple test, it won't pass the more difficult ones. Part of the challenge
> is hence structuring tests in the correct order."*

Đây là một khẳng định về **thứ tự phụ thuộc**, và nó áp được vào `P01…P06` vì các gate **có**
quan hệ nhân quả thật: P01 (yêu cầu) hỏng thì P06 (vận hành) không thể đúng; P02 (UX) trên một
P01 sai là UX cho một sản phẩm không tồn tại.

**Hiện trạng:** `check_gates.py` kiểm **cấu trúc** (đủ mục, không tự `APPROVED`, mục `REJECTED`
phải có mã lý do). Nó **không** kiểm thứ tự. Grep `order`/`thứ tự`/`phụ thuộc` trong tệp ⇒ **0**.

Hôm nay điều đó chưa gây hại: **cả 6 gate đều chưa ký** (đã kiểm, tất cả `☐ APPROVED  ☐ REJECTED`).
Nhưng nó **sẽ** gây hại đúng vào lúc quan trọng nhất — khi người ta bắt đầu ký, dưới áp lực thời
gian.

**Điều tôi KHÔNG được nói:** rằng thứ tự hiện đang bị vi phạm. Nó không bị. Chưa ai ký gì.

**Đề xuất hẹp:** thêm **một** phép kiểm — *"P0x được APPROVED ⇒ P0(x-1) phải APPROVED, trừ khi
có miễn trừ ghi rõ trong ADR"*. Không đổi luật ký, không đổi SLA, chỉ làm hiện ra một ràng buộc
đang tồn tại ngầm.

---

## 3. I3 — Contract API thiếu đúng những route đang phục vụ production

e2b gọi Agent Protocol là *"OpenAPI specification v3-based protocol… a list of endpoints, which
the agent should expose with predefined response models"*. Mệnh đề cốt lõi: **spec là hợp đồng,
không phải tài liệu mô tả.**

Repo này có `docs/03-api/openapi.yaml` và một cổng thật (`api.yml`: redocly lint 0 error,
operationId duy nhất, traceability screen→API). Nhưng phép kiểm đó so **spec với tài liệu**, không
so **spec với code**.

Đo thực tế:

| Route đang phục vụ production | Có trong `openapi.yaml`? |
|---|---|
| `GET /play/:game` | ❌ **KHÔNG** |
| `GET /api/play/sdk` | ❌ **KHÔNG** |
| `GET /assets/:file` | ❌ **KHÔNG** |

Ba route này là **bề mặt công khai** của sản phẩm — trang chơi game, SDK cho studio, và đường
phục vụ tệp game. Chúng không nằm trong hợp đồng. Một studio đọc `openapi.yaml` sẽ không biết
`/api/play/sdk` tồn tại. Đó là lỗi **hợp đồng**, không phải lỗi tài liệu.

Đây là chỗ nguồn e2b có giá trị thật: nó nói **spec là thứ agent/công cụ đọc**, nên spec thiếu
nghĩa là contract thiếu. Và nó khớp với chính luật repo đã có ở ADR-0034: *control plane quyết
định, và cái gì không khai báo thì không có*.

**Đề xuất:** thêm 3 route vào spec + **một** phép kiểm "mọi route thật trong `portal/server.mjs`
phải có trong `openapi.yaml`". Phép kiểm này chạy offline, tất định.

---

## 4. Ba thứ KHÔNG nên lấy

| Thứ | Vì sao không |
|---|---|
| **Thêm một AI agent tự chủ vào quy trình** | [`ADR-0026`](ADR-0026-agent-sdk-preact-quy-trinh-dev.md) đã trả lời: *"thay cổng kiểm bằng agent tự chủ — ❌ Không"*. Bài e2b §3 còn nói **ngược lại**: các founder nói agent cần **~99,9%** tin cậy để vào doanh nghiệp. Trích nó để **biện hộ** cho agent là trích ngược ý nguồn |
| **Import `awesome-ai-agents` như một nguồn nội dung** | CC BY-NC-SA 4.0. Xem §1.2 |
| **Số liệu thị trường của e2b làm số liệu của Game9K** | Bài đó không nêu số thị trường nào định lượng được — chỉ có phát biểu định tính của founder. Trích "99.9%" như chuẩn của Game9K là biến **một lời nói** thành **một yêu cầu** |

---

## 5. Điều hai nguồn này XÁC NHẬN (không phải thay đổi)

Bài e2b §2 và §6 nói agent đang chuyển từ *sản phẩm độc lập* sang **feature ẩn trong sản phẩm
lớn**, và người dùng quan tâm **kết quả** chứ không quan tâm công nghệ bên dưới
(*"offering users different models is redundant"*).

Đó chính là điều ADR-0026 §4 và ADR-0033/0035 đã chốt theo hướng ngược lại với cơn hào hứng
agent: không khoe công nghệ, không hứa năng lực, không để một beta 3 sao nằm trên đường găng.
Nay có **nguồn độc lập** để dẫn khi bảo vệ lựa chọn đó — và đó là giá trị của bài e2b: nó là
nguồn **bên ngoài** nói cùng điều repo đã tự quyết.

**Nhưng:** dẫn nó như *"e2b đồng ý với chúng tôi"* là sai. e2b không biết MetaPump tồn tại.

---

## 6. Ranh giới trung thực

- **e2b không xem xét, không xác nhận gì về MetaPump.** Dùng bài viết công khai không tạo quan hệ.
- **Không phải nghiên cứu có bình duyệt.** Đây là bài marketing/khảo sát của một nhà cung cấp,
  có phỏng vấn founder. Các con số là **phát biểu trong phỏng vấn**, không phải đo lường.
- **Không chép.** Bảng và câu chữ của `awesome-ai-agents` là CC BY-NC-SA; của bài e2b là của e2b.
- **Không gọi đây là "áp dụng e2b".** Không có mã e2b nào trong repo, không dùng dịch vụ e2b.

---

## 7. Câu hỏi mở

| | |
|---|---|
| **Q-ADR36-a** | ~~Có làm phép kiểm license theo **mẫu NC/SA** thay vì tên repo viết cứng (§1.3) không?~~ **Đã làm** — xem §7.1 |
| **Q-ADR36-b** | Có thêm ràng buộc thứ tự gate P01→P06 (§2) không, hay để người ký tự chịu trách nhiệm? |
| **Q-ADR36-c** | 3 route production (§3) vào `openapi.yaml` ngay, hay chờ chốt hình dạng Play SDK? |

---

### 7.1. Q-ADR36-a — đã trả lời: làm, và đã làm

`license.yml` **đã** được sửa. Phép kiểm danh sách bảy tên repo bị thay bằng
`scripts/check_license_table.py`, kiểm **cặp (license, cách dùng, nhãn)**.

Điều phải nói rõ, vì nó là bài học của chính ADR này: bản đầu của phép kiểm mới
**vẫn xanh khi gỡ cả ba dòng CC BY-NC-SA** — đúng lỗi §1.1 mà nó sinh ra để bắt.
Lý do: ba luật đầu chỉ kiểm những dòng **đang có**, nên xoá dòng thì chúng im lặng.
Đã thêm luật thứ tư: một danh sách **nhóm license đã từng được đọc và đã quyết**;
thiếu cả nhóm ⇒ đỏ. Đo lại: gỡ dòng CC BY-NC-SA ⇒ đỏ đúng thông điệp.

Giới hạn còn lại, ghi để không ai tin nhầm: luật 4 vẫn là kiểm **có mặt**, không
phải kiểm **đúng**. Một license **mới** chưa từng ai đọc vẫn lọt. Không có phép
kiểm tĩnh nào bắt được "tài liệu thiếu một điều chưa ai nghĩ tới".

---

**Trạng thái:** Proposed. `license.yml` **đã sửa** (Q-ADR36-a đã trả lời). Chưa sửa
`check_gates.py` hay `openapi.yaml`. Ba phát hiện ở §1–§3 đều **đã kiểm**, không phải suy đoán.
