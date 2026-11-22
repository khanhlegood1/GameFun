# ProximaX — ví, lưu trữ, và cái mà bản phân tích kia bỏ sót

> **Tài liệu sống:** `docs/20-proximax-teardown-storage.md`
> **Trạng thái:** `SCOPING` — teardown + xác nhận lại kết luận
> **Ngày:** 22/11/2026
> **Đầu vào:** bản phân tích do người sáng lập soạn — 4 phần: (A) quản lý khoá/UX, (B) multisig, (C) tương thích hệ sinh thái, (D) mức độ cập nhật GitHub; rồi so sánh lưu trữ ProximaX / IPFS / Arweave / BNB Greenfield
> **Phương pháp:** kiểm chứng bằng GitHub API trên `proximax-storage` + đối chiếu với thiết kế đã chốt trong repo này
> **Liên quan:** `docs/11` (ADR-007 auth/wallet), `docs/05` §ADR-003 (R2 + wildcard subdomain), `docs/18` (§1.3 hash ≠ chất lượng)

---

## 0. Kết luận trước

**Kết luận cuối cùng của bản phân tích — "không dùng ProximaX" — là đúng.** Nhưng **ba trong bốn lý do đưa ra để tới đó là sai**, và một lý do sai là loại sai **quan trọng hơn**: nó đề xuất đúng thứ mà thiết kế của Game9K đã chủ động **từ chối**.

| Nội dung trong bản phân tích | Đánh giá |
|---|---|
| (D) GitHub "gần như đóng băng", "ngừng phát triển từ lâu" | ❌ **Sai.** `cpp-xpx-chain` có **`34` commit** từ 05/2025, mới nhất **18/03/2026** |
| (A) "Bắt buộc mua `XPX` để trả gas" là nhược điểm chí tử | ⚠️ **Đúng về sự thật, sai về so sánh.** **Solana cũng bắt buộc** — và đó là nền tảng đã chốt |
| (B) Multisig cấp giao thức là "điểm cộng của ProximaX" | ⚠️ **Cần nói rõ:** trên Solana, multisig **cũng** là native, không cần smart contract |
| (C) Non-EVM → không nối được Metamask/Phantom | ✅ **Đúng**, và đây là lý do đủ để loại — nhưng §2 cho thấy nó **đúng với cả Solana** |
| So sánh lưu trữ: "BNB Greenfield cho **state game, file save, UGC**" | ❌ **Sai, và đây là lỗi nguy hiểm nhất** — xem §3 |
| Đề xuất "embedded wallet + paymaster" cho Game9K | ⚠️ **Đã có** trong ADR-007, và bản phân tích **không biết** — xem §4 |
| "Giảm `95%+` tỷ lệ chuyển đổi" | ❌ **Không có nguồn.** Đúng loại số `AGENTS.md` cấm — xem §5 |

> **Câu một dòng:** bản phân tích **đi đúng hướng nhưng vì lý do sai**, và đề xuất một kiến trúc lưu trữ sẽ **làm hỏng đúng chỗ Game9K mạnh nhất**.

---

## 1. Kiểm chứng phần (D) — GitHub **không** đóng băng

Đây là phần dễ kiểm nhất, và bản phân tích sai rõ nhất.

### 1.1. Số đo *(quan sát trực tiếp, GitHub API, 22/11/2026)*

| Repo | Lần đẩy cuối | Sao | Ghi chú |
|---|---|---|---|
| `cpp-xpx-chain` | **18/03/2026** | 1 | **`34` commit** từ 01/05/2025 — sửa đồng bộ block, workflow Docker đa kiến trúc |
| `xpx-mainnet-chain-onboarding` | 15/01/2026 | 10 | Tài liệu hướng dẫn chạy node mainnet |
| `xpx-chain-devportal-docs` | 30/10/2025 | 1 | |
| `tsjs-xpx-chain-sdk` | 13/08/2025 *(commit cuối 30/04/2025)* | 5 | SDK TypeScript chính |
| `rust-xpx-chain-sdk`, `dart-xpx-chain-sdk`, `cpp-xpx-chain-sdk` | 02–04/2025 | 2–3 | Nhiều ngôn ngữ |
| **`xpx-chain-web-wallet`** | **10/11/2022** | 4 | ⚠️ **Đây là chỗ bản phân tích đúng** |
| `xpx-chain-mobile-wallet` | 24/01/2023 | 3 | ⚠️ Cũng đúng |

Tổ chức: **`98` repo công khai**, tạo **16/04/2018**.

### 1.2. Kết luận cần sửa

| Bản phân tích viết | Thực tế |
|---|---|
| *"tần suất cập nhật rất thấp hoặc đã ngừng phát triển tính năng mới từ lâu"* | **Sai với chain node và SDK** — vẫn có commit trong `2026` |
| *"gần như đóng băng trên GitHub"* | **Sai.** Đóng băng là **ví** (`2022`/`2023`), không phải toàn bộ tổ chức |

> ⚠️ **Vì sao lỗi này quan trọng:** nếu một nhà đầu tư hoặc đối tác kiểm tra và thấy `cpp-xpx-chain` có commit `18/03/2026`, **toàn bộ bản phân tích mất uy tín** — kể cả phần đúng. Một lập luận đúng nhưng dẫn chứng sai sẽ bị bỏ.

### 1.3. Cách viết đúng

> *"Ví chính thức của ProximaX (`xpx-chain-web-wallet`, `xpx-chain-mobile-wallet`) không được cập nhật từ `2022`/`2023`, trong khi chain node vẫn có commit. Nghĩa là: **hạ tầng còn sống, nhưng bề mặt người dùng bị bỏ**."*

Câu đó **mạnh hơn** câu cũ, vì nó chỉ đúng vào chỗ yếu thật: Game9K cần **ví cho người chơi**, và đó chính là phần đã chết.

---

## 2. Lỗi so sánh nghiêm trọng: "phải mua `XPX` để trả gas"

Bản phân tích dùng tiêu chí này để loại ProximaX. Nhưng **tiêu chí đó loại luôn Solana** — nền tảng đã chốt trong repo này.

| | Phải có token native để trả phí? | Ghi chú |
|---|---|---|
| ProximaX | ✅ `XPX` | |
| **Solana** | ✅ **`SOL`** | Đã chốt trong `docs/04`, `docs/11`, whitepaper |
| EVM | ✅ `ETH` / `BNB` / … | Trừ khi có paymaster |

> **Nếu "bắt buộc có token native" là lý do loại một chain, thì Game9K phải loại cả Solana.** Bản phân tích không thể dùng tiêu chí này cho ProximaX mà bỏ qua cho Solana — đó là **lập luận không nhất quán**, và người đọc sắc sảo sẽ thấy ngay.

### 2.1. Cách viết đúng

Điều **thật sự** đúng ở phần (A) không phải "có token native", mà là **thứ tự trải nghiệm**:

| Vấn đề thật | Cách Game9K đã giải |
|---|---|
| Người chơi phải **hiểu** về seed phrase | ADR-007: passkey, không hiện seed |
| Người chơi phải **có** token trước khi chơi | ADR-007: paymaster + trần chi trả, người chơi bắt đầu với `0` |
| Mất khoá là mất tài sản | ADR-007: 72h recovery, không giữ khoá người dùng |

Nghĩa là: bản phân tích **mô tả đúng vấn đề, gán sai nguyên nhân**. Nguyên nhân không phải "native token", mà là **không có lớp trừu tượng phía trên**.

---

## 3. Lỗi nguy hiểm nhất: BNB Greenfield cho "state game"

### 3.1. Bản phân tích đề xuất gì

> *"Lưu trữ State Game, dữ liệu người chơi, File Save, User Generated Content: Dùng **BNB Greenfield** hoặc EigenLayer DA để có tốc độ đọc/ghi cực nhanh, phí gas rẻ và tương thích hoàn toàn với Smart Contract của Game."*

### 3.2. Vì sao đề xuất này **làm hỏng** đúng chỗ Game9K mạnh nhất

| Yêu cầu của Game9K | Nếu đặt state game trên một chain công khai |
|---|---|
| **`verified_play` không được giả** | Ai cũng đọc và **ghi** được dữ liệu lên một storage công khai → mất tính toàn vẹn của nguồn đo |
| **`work`, `input_entropy`, `sybil_risk_score` không lộ** | Đây là **tín hiệu chống bot**. Đưa lên nơi công khai = **phát cho bot biết mình bị lọc vì gì** |
| **Xoá dữ liệu theo yêu cầu người dùng** | Storage phi tập trung **không xoá được**. Đây là **nghĩa vụ pháp lý**, không phải lựa chọn kỹ thuật |
| **Rời nhà cung cấp cloud** | Đã giải bằng kiến trúc |

Điểm thứ ba là điểm **tuyệt đối**: quyền xoá dữ liệu cá nhân **không tương thích** với "lưu vĩnh viễn / phi tập trung". Bản phân tích đề xuất đúng một công nghệ mà Game9K **không thể** dùng cho dữ liệu người chơi.

### 3.3. Game9K đã chốt gì — và nó đúng

`docs/05` §ADR-003 chốt: **Cloudflare R2 private 100%**, ba bucket `quarantine` / `builds` / `recordings`, chỉ đọc qua **Worker R2 Binding có prefix-lock**, và **wildcard subdomain theo `version_id`** để cô lập origin.

| Tiêu chí | R2 (đã chốt) | Greenfield (bản phân tích đề xuất) |
|---|---|---|
| Đọc/ghi state game | ✅ Qua Worker, độ trễ edge | ⚠️ Qua chain + storage provider |
| **Xoá được** theo yêu cầu | ✅ Có | ❌ Không |
| **Riêng tư** | ✅ Private 100%, binding có prefix-lock | ❌ Công khai theo thiết kế |
| Bảo vệ `input_entropy` khỏi bot | ✅ Không lộ | ❌ Lộ |
| Chi phí | Rẻ, không phí gas | Phí gas + phí lưu trữ |

> **Không đổi gì.** Mục này chỉ **xác nhận lại** lựa chọn đã có, và ghi rõ vì sao đề xuất thay thế **không dùng được**.

### 3.4. Chỗ Greenfield/Arweave **thật sự** dùng được

Không phải "không bao giờ". Chỉ là **không** cho dữ liệu người chơi:

| Dùng được | Vì sao |
|---|---|
| **Bản build game đã kiểm định** (ZIP + `base_sha256`) — lưu dài hạn | Công khai là **tính năng**: ai cũng kiểm được hash |
| **Metadata NFT / asset công khai** | Không có dữ liệu cá nhân |
| **Bản công bố của whitepaper/yellow paper** | Cần vĩnh viễn, không cần xoá |

Và ngay cả ở đây, **R2 vẫn rẻ hơn** cho giai đoạn đầu. Arweave chỉ có nghĩa khi cần **bảo đảm vĩnh viễn** — thứ Game9K chưa cần ở Pre-Seed.

---

## 4. Bản phân tích không biết: những thứ đã có trong repo

Đây là phần **tốt nhất** của bản phân tích — và nó vô tình **đề xuất lại** đúng thứ đã chốt.

| Bản phân tích đề xuất | Trạng thái thật |
|---|---|
| "Embedded wallet dựa trên Account Abstraction / Passkeys" | ✅ **ADR-007**, đã hợp nhất (`docs/11`, PR #41) |
| "Tự động tạo khoá qua Email/Social Login" | ✅ ADR-007 — nhưng qua **passkey**, không qua khoá do server giữ |
| "Game9K đứng ra tài trợ phí gas (Paymaster)" | ✅ ADR-007 — có **trần chi trả** (`gas_sponsorships`) |
| "Ẩn sự phức tạp ở phía backend" | ✅ ADR-007 — chia **danh tính** và **thẩm quyền** |
| "Không bắt người chơi cài ví lạ" | ✅ ADR-007 — không ví extension nào |

> **Hệ quả:** phần khuyến nghị kỹ thuật của bản phân tích **không còn gì để làm**. Nó nên được đọc là **xác nhận độc lập** rằng ADR-007 đi đúng hướng — chứ không phải một đề xuất mới.

### 4.1. Chỗ bản phân tích **vượt** ADR-007

Có một điểm đáng ghi: bản phân tích nêu **`EIP-7702`** và **`Safe` + role-based permissions + timelock**. ADR-007 đã có paymaster và recovery, nhưng **chưa** có:

| Thiếu | Có nên thêm? |
|---|---|
| **Timelock** cho thao tác quản trị (đổi paymaster cap, đổi module) | ✅ **Có.** Rẻ, và là thứ nhà đầu tư hỏi |
| **Role-based permission** cho ví của studio (nhiều người, mức chi khác nhau) | ✅ **Có**, khi studio có `≥ 2` người nhận tiền |
| **Multisig native của Solana** cho két sắt studio | ⚠️ Cần kiểm với `docs/04` trước — có thể đã có |

> Đây là **đóng góp thật** của bản phân tích, và nó nhỏ, cụ thể, làm được. Nên tách khỏi phần còn lại.

---

## 5. Con số không có nguồn

> *"sẽ làm giảm `95%+` tỷ lệ chuyển đổi người dùng (conversion rate)"*

Không có nguồn, không có định nghĩa "conversion" đo cái gì, không có mẫu. Đây đúng loại trích dẫn `AGENTS.md` cấm — và nếu đưa vào deck thì đó là **khẳng định không kiểm chứng được**, y như `100M+ MAU` ở `docs/14` §A4.

**Cách viết an toàn:** *"Cài thêm một ví extension là một bước bỏ ngang; tỉ lệ bỏ ngang của bước này chưa được đo trong bối cảnh của chúng tôi."*

---

## 6. Giữ nguyên: ba điều bản phân tích nói đúng

| Mã | Nội dung | Vì sao đúng |
|---|---|---|
| **P1** | **Không dùng ví ProximaX gốc làm ví chính** | Ví đó không cập nhật từ `2022`, và không nối được hệ sinh thái nào |
| **P2** | **Không chọn chain vì whitepaper 2019** | Kiến trúc "monolithic chain làm mọi thứ" đã bị thay bằng mô hình module — đúng, và là lập luận tốt |
| **P3** | **Không xây trên hạ tầng có < `10` repo đang hoạt động** | `98` repo nhưng phần lớn im lặng; rủi ro bảo trì là thật |

---

## 7. Từ chối

| Mã | Nội dung | Lý do |
|---|---|---|
| **R1** | Viết "GitHub ProximaX đóng băng" | §1 — **sai**, kiểm được trong `30` giây |
| **R2** | Dùng "bắt buộc token native" làm tiêu chí loại chain | §2 — loại luôn Solana, tức là loại chính Game9K |
| **R3** | Đặt **state game / file save / UGC** lên Greenfield, Arweave hay bất kỳ storage công khai | §3 — không xoá được, lộ `input_entropy`, phá tính toàn vẹn của `verified_play` |
| **R4** | Đưa `95%+` vào bất kỳ tài liệu nào | §5 — không nguồn |
| **R5** | Trình bày "embedded wallet + paymaster" như đề xuất mới | §4 — đã có từ ADR-007 (PR #41) |
| **R6** | Đổi R2 sang storage phi tập trung ở giai đoạn này | §3.3 — R2 rẻ hơn, xoá được, riêng tư |

---

## 8. Việc **không** làm trong tài liệu này

- Không đổi `docs/04` (Solana), `docs/11` (ADR-007), `docs/05` §ADR-003 (R2), `docs/02` (**34** bảng).
- Không thêm bảng `timelock`/`role` vào schema — đó là việc của một ADR riêng, khi studio có nhu cầu thật.
- Không đổi whitepaper, deck, 4 PDF.
- Không kết luận về giá trị đầu tư của `XPX` hay của ProximaX như một dự án.

## 9. Thứ tự thi công

| # | Việc | Vì sao |
|---|---|---|
| **1** | **Sửa phần (D)** trong bản phân tích: nói *"ví ngừng cập nhật"*, không nói *"GitHub đóng băng"* | Sai kiểm được sẽ làm mất uy tín cả tài liệu |
| **2** | **Bỏ** khuyến nghị Greenfield cho state game; thay bằng *"R2 đã chốt ở ADR-003, vì quyền xoá + riêng tư"* | §3 |
| **3** | Xoá `95%+`, hoặc thay bằng câu "chưa đo" | §5 |
| **4** | Tách **timelock + role-based permission** thành một ADR nhỏ | §4.1 — phần đóng góp thật, và làm được |
| **5** | Ghi vào tài liệu giới thiệu: *"ví ProximaX không được cập nhật từ `2022`, chain vẫn có commit"* — dùng làm ví dụ về **kiểm chứng trước khi tin một bản phân tích** | Bài học dùng lại được |
