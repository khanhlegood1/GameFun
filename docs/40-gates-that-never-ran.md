# 40 — Bảy cổng CI chưa bao giờ kiểm repo

> **Tài liệu sống:** `docs/40-gates-that-never-ran.md` — bản gốc ở đây, mọi bản khác là bản chép.
> **Trạng thái:** `DONE` (vòng 28) · cổng: `scripts/check_gate_wiring.py` (cổng thứ 21)
> **Tiền đề:** `docs/37` §2 (*một việc có hạn nằm trong văn xuôi là một việc không có hạn*) · `docs/33` §2 (miễn trừ ngầm là cách một cổng chết)

---

## 0. Một dòng

`main` xanh **2/2** suốt nhiều vòng, nhưng **7 cổng** trong `.github/workflows/docs.yml` chỉ được gọi ở chế độ `--selftest` — và với 3 trong số đó, `--selftest` **`return` ngay**, nên phần kiểm repo chưa từng chạy. Một trong ba cổng đó đang **ĐỎ** trên `main` khi tôi bắt đầu vòng này.

Đây không phải lỗi của một cổng. Đây là lỗi của **cách nối cổng**: một cổng có hai chế độ, và CI chỉ gọi chế độ tự kiểm.

---

## 1. Ranh giới: cổng tự kiểm ≠ cổng kiểm repo

Mỗi cổng trong repo này có hai chế độ, và chúng trả lời **hai câu khác nhau**:

| Chế độ | Câu hỏi | Chạy trên |
|---|---|---|
| `--selftest` | *Bộ dò của tôi còn bắt được lỗi không?* | corpus **tổng hợp** trong `tmp/` |
| *(không cờ)* | *Repo này có vi phạm không?* | `docs/`, `sdk/`, `pm/`, `.github/` |

Một cổng xanh ở chế độ thứ nhất **không nói gì** về chế độ thứ hai. Đó chính là định nghĩa của một cổng chưa bao giờ kiểm repo.

> **Vì sao điều này khó thấy:** `--selftest` in ra dòng `PASS — 10/10 phép thử`, và dòng đó nằm trong log CI màu xanh. Không ai đọc lại để hỏi *"thế còn repo thì sao?"*. Cổng càng có nhiều phép phá thì càng **trông** như đang canh repo.

---

## 2. Bảy cổng, ba kiểu hỏng

`--audit` của cổng mới in ra bảng này. Cột phải là thứ đáng đọc.

| Cổng | Kiểu hỏng | Hậu quả thật |
|---|---|---|
| `check_claims.py` | `--selftest` **`return`** trước phần kiểm | **ĐỎ trên `main`**: `WHITEPAPER.md:738` có cụm `Dự án đầu tiên` mà không nhãn |
| `receipt_lock.py` | `--selftest` **`return`** | không có biên bản nào trong `receipts/` ⇒ chưa lộ, nhưng cổng chưa từng chạy |
| `kvu_invariants.py` | `--selftest` **`return`** | 31 kiểm tra nội dung chưa từng chạy trong CI |
| `gate_decide.py` | chỉ gọi `--self-test` | 8 quyết định chưa từng được kiểm bởi CI |
| `check_gate_ladder.py` | chỉ gọi `--selftest` | thang 6 cổng chưa từng được kiểm |
| `check_sdk.py` + `check_sdk_errors.py` + `check_sdk_manifest.py` | chỉ gọi `--selftest` | ngân sách 12 KB, 7 mã lỗi, 4 chỗ ghi hash — chưa từng kiểm |

**Kiểu 1 (nguy hiểm nhất) — `return` ngay sau selftest.** Ba cổng này *có* code kiểm repo, đầy đủ, đã chạy đúng khi tôi gọi tay. Nhưng trong CI chúng dừng ở dòng thứ ba của `main()`.

**Kiểu 2 — cờ `--selftest` là cờ RỖNG.** `check_egress_lock.py`, `check_gate_ladder.py`, `check_sdk.py`, `check_sdk_errors.py`, `check_sdk_manifest.py` **nhận** cờ rồi không làm gì với nó; chúng chạy kiểm repo luôn. Nghĩa là chúng an toàn **do may mắn**, không do thiết kế: ai thêm `if args.selftest: return selftest()` vào sau này sẽ biến chúng thành kiểu 1 mà không có gì báo.

**Kiểu 3 — tên cờ không nhất quán.** `gate_decide.py` và `check_specs.py` dùng `--self-test`; phần còn lại dùng `--selftest`. Chép một dòng workflow sang cổng khác là `argparse` thoát mã **2** với `unrecognized arguments` — đỏ to, nhưng ồn ào và dễ bị "sửa" bằng cách xoá cổng khỏi workflow.

---

## 3. Sửa gì, và sửa ở đâu

Nguyên tắc: **không sửa cổng nào để làm CI xanh.** Sửa **đường nối** để chế độ kiểm repo thực sự chạy, rồi sửa **cái cổng tìm ra**.

**(a) Nối đủ hai chế độ** — 7 dòng trong `.github/workflows/docs.yml`:

```yaml
run: python3 scripts/check_claims.py --selftest && python3 scripts/check_claims.py
```

`&&` chứ không `;`: selftest đỏ thì dừng, không chạy tiếp trên một bộ dò hỏng.

**(b) Sửa vi phạm thật mà cổng tìm ra.** `check_claims.py` báo `WHITEPAPER.md:738` — ô *"Cột mốc Nghiệm thu Đo lường được"* của `S8` viết **"Dự án đầu tiên tốt nghiệp tự động"** như một sự thật. Đó là câu về **thế giới** (chưa ai làm được ⇒ chưa ai chứng minh được nó *sẽ* là đầu tiên), không phải câu về **kế hoạch**. Sửa: gắn `[ĐỀ XUẤT]` — đúng nhãn cho một cột mốc **phải đạt**, không phải một thành tựu **đã có**.

> **Vì sao không thêm vào sổ đăng ký?** Sổ `pm/claims-registry.json` giữ các câu **đang được dùng như sự thật** và cần người ký + hạn. Câu này là **mục tiêu của sprint**, không phải tuyên bố về hiện tại. Nhãn `[ĐỀ XUẤT]` mới là phân loại đúng — và nó không đẻ thêm một hạn giả.

**(c) Dựng cổng để lỗi này không tái diễn.** `scripts/check_gate_wiring.py` — 4 bất biến, 4 phép thử, đọc **AST** chứ không grep:

- **Bất biến 1** — cổng nhận `--selftest` mà không đọc cờ ⇒ phải khai lý do **tên từng cổng** trong `EMPTY_FLAG_OK`. Miễn trừ phải viết ra; miễn trừ ngầm là cách một cổng chết.
- **Bất biến 2** — cổng có chế độ nội dung ⇒ workflow phải có **một lần gọi không kèm cờ**. Đây là bất biến bắt đúng 7 vi phạm ở §2.
- **Bất biến 3** — cổng được CI gọi ⇒ phải có trong sổ `CONTENT_MODE`. Cổng mới không lọt sổ.
- **Bất biến 4** — sổ nhắc tệp ⇒ tệp phải tồn tại. Sổ không trôi.

---

## 4. Kết quả

```
GATE WIRING: PASS — 36 kiểm tra · 21 cổng trong sổ · mỗi cổng có cả đường tự kiểm và đường kiểm repo
GATE WIRING SELFTEST: PASS — 4/4 (1 đối chứng + 3 phép phá)
CLAIMS: PASS — 31 kiểm tra · 5 bất biến · 3 tuyên bố về thế giới, 3 mục trong sổ đăng ký
```

Bốn phép thử — **một đối chứng, ba phép phá**, trên workflow **tổng hợp** trong `tmp/`:

| | Phép thử | Chiều phải đúng |
|---|---|---|
| `P0` | workflow gọi đủ 20 cổng, không cờ | **xanh** (đối chứng: cổng không đỏ vô cớ) |
| `P1` | bỏ `kvu_invariants.py` khỏi workflow | **đỏ** |
| `P2` | `receipt_lock.py --selftest` (không gọi lần hai) | **đỏ** |
| `P3` | thêm `scripts/khong_co_that.py` | **đỏ** |

`P0` là phép thử quan trọng nhất: không có nó, ba phép phá kia có thể cùng đỏ vì một lý do khác.

---

## 5. Tự áp dụng: cổng mới cũng phải qua cổng mới

Khi tôi thêm `check_gate_wiring.py` vào workflow, cổng **tự báo đỏ**:

```
- check_gate_wiring.py: được CI gọi nhưng không có trong CONTENT_MODE — thêm quyết định vào sổ
```

Đúng như thiết kế. Sổ `CONTENT_MODE` là **quyết định của người**, không phải thứ suy ra được từ việc cổng có tự khai hay không — nếu cổng tự thêm mình vào sổ thì bất biến 3 thành vô nghĩa (một cổng có thể tự khai "tôi đã nối"). Nên bước đăng ký là bước **viết tay**, và cổng đỏ cho tới khi tôi viết.

---

## 6. Ba câu hỏi

**"Sao không cho `--selftest` chạy luôn cả hai chế độ?"** Vì `--selftest` phải chạy được trên **workflow tổng hợp** trong `tmp/`. Nếu nó kiểm cả repo thật, phép phá `P1` (bỏ một cổng) sẽ đỏ vì repo thật chứ không vì cái tôi vừa phá — và phép thử mất khả năng phân biệt. Hai chế độ, hai câu hỏi, hai lần gọi.

**"Sáu tháng nữa thêm cổng thì sao?"** Bất biến 3 chặn: cổng mới được gọi trong workflow mà không có trong `CONTENT_MODE` ⇒ **ĐỎ**. Người thêm cổng buộc phải viết một dòng quyết định — cùng lúc với việc thêm cổng, không phải sau.

**"Có phải chỉ là chuyện đặt `&&` không?"** Không. Sửa `&&` chỉ làm cổng **chạy**; nó lập tức tìm ra một vi phạm thật trong `WHITEPAPER.md` đã nằm đó nhiều vòng. Phần giá trị nằm ở **cái cổng tìm ra**, không ở dấu `&&`.

---

## 7. Chưa làm

| | Việc | Vì sao chưa |
|---|---|---|
| **W1** | Thống nhất `--selftest` / `--self-test` thành một tên | Đổi 2 cổng + 3 dòng workflow + mọi tài liệu nhắc tên cờ. Việc cơ học, nhưng đụng `docs/06`, `docs/30`, `docs/36`. Để riêng một vòng |
| **W2** | Cho 5 cổng "cờ rỗng" một phép phá thật | Cần corpus tổng hợp cho mỗi cổng (thang 6 cổng, SDK giả, manifest giả). `EMPTY_FLAG_OK` ghi lý do — đó là trạng thái **đã khai**, không phải đã xong |
| **W3** | Chạy cổng trên **cả** `docs/` và `sdk/` sau mỗi `--selftest` | Trùng với W1 về mặt cơ học; làm cùng lúc sẽ rẻ hơn |
| **W4** | Đưa số cổng (21) vào `AGENTS.md` như một bất biến | `AGENTS.md §3` hiện chỉ nói "mọi cổng phải có trong workflow". Cổng mới kiểm được **cả hai chiều**; câu trong `AGENTS.md` nên nói đúng thế |

> **Điều đáng nhớ:** trong bốn vòng gần nhất tôi đã thêm 4 cổng, và **cả 4** đều được nối đúng ngay từ đầu (`--selftest &&` + chạy thật). Nhưng 7 cổng **cũ hơn** thì không. Lỗi không nằm ở người thêm cổng — nó nằm ở chỗ **không có gì kiểm việc nối cổng**. Đó là lý do cổng này tồn tại.
