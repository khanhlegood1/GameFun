# ADR-007 — Đăng nhập bằng email/Google, ví Web3 ẩn dưới nền

> **Tài liệu sống:** `docs/11-auth-wallet-ux.md`
> **Trạng thái:** `ACCEPTED` — quyết định kiến trúc, chưa thi công
> **Ngày:** 22/11/2026 · **Bối cảnh:** người dùng hỏi *"có khả thi về công nghệ tương đương không?"* sau khi thấy XWG cho đăng nhập bằng Google
> **Liên quan:** `A1` trong `docs/PRD.md`, `FR-FND-01`, `ADR-005`, `docs/08-legal-brief-vn-licensing.md` (Q4b)

---

## 0. Trả lời ngắn

**Có, khả thi — nhưng không phải bằng cách "gắn chết ví với email".**

Phải tách hai thứ mà câu hỏi đang gộp làm một:

| | Là gì | Có cần bí mật không |
|---|---|---|
| **Danh tính** (auth) | "Bạn là ai" — email OTP, Google OAuth, passkey | Không. Email **công khai**, không phải khoá |
| **Thẩm quyền** (authority) | "Ai được ký giao dịch chuyển tiền" | **Có.** Phải là một khoá riêng tư thật |

Vì vậy: **giữ email/Google làm danh tính vĩnh viễn** (đúng ý bạn), và **đặt một khoá ký riêng bên dưới** — nhưng khoá đó **không được dẫn xuất từ email**.

> ⚠️ **Không thể làm "ví deterministic từ email".** Email là thông tin công khai; nếu khoá suy ra được từ email thì ai biết email của bạn là lấy được ví. Nếu suy ra từ `HMAC(secret_của_server, email)` thì khoá phụ thuộc một secret của Game9K — mất secret là mất toàn bộ ví của toàn bộ người dùng, và Game9K trở thành **bên giữ tài sản** (xem §3, phương án C).

**Quyết định:** đi theo **3 giai đoạn**, mặc định là **passkey smart wallet** — không seed phrase, không nhà cung cấp nào giữ khoá, và **vẫn đăng nhập bằng email/Google**.

---

## 1. Vì sao XWG làm được "Sign in with Google" — và nó rẻ vì sao

XWG dùng **Firebase** làm identity provider (quan sát trực tiếp: popup Google trỏ tới `x-wallet-19864.firebaseapp.com`). Đó là **lớp đăng nhập**, không phải lớp ký giao dịch.

Cần phân biệt rõ 3 thứ mà màn hình đăng nhập không cho thấy:

1. **Đăng nhập** (Google OAuth) → tạo session trên server của họ.
2. **Ví** — XWG có "embedded/light wallet" riêng (whitepaper v2.0.0, tr. 30–31), nhưng **không công bố** khoá nằm ở đâu, ai giữ, có xuất được không.
3. **Ký giao dịch** — không công bố.

**Kết luận có thể nói chắc:** "đăng nhập bằng Google" **không** chứng minh họ có ví phi tập trung. Nó chỉ chứng minh họ có **lớp auth Web2**. Đây đúng là điều `A1` của Game9K đã cố định từ trước — và nó **miễn phí**, không cần ví on-chain nào cả.

---

## 2. Ràng buộc kỹ thuật thật của Solana

Đây là chỗ nhiều người hiểu sai, nên ghi rõ:

| Sự kiện | Chi tiết |
|---|---|
| Giao dịch Solana ký bằng **Ed25519** | Cố định ở tầng giao thức |
| Passkey (Face ID / Touch ID / Windows Hello) ký bằng **P-256 / secp256r1** | Do phần cứng bảo mật của Apple/Google chỉ hỗ trợ đường cong này; trình duyệt **không** mở Ed25519 qua WebAuthn |
| **Hai đường cong không tương thích** | Vì vậy passkey **không ký trực tiếp** được giao dịch Solana |
| **SIMD-0075 — precompile `secp256r1`** | Bật trên mainnet **06/2025**: cho phép verify chữ ký P-256 **on-chain**, tối đa 8 chữ ký mỗi instruction |
| Hệ quả | Passkey có thể **uỷ quyền** cho một ví trên Solana, nhưng **phong bì giao dịch vẫn cần một chữ ký Ed25519** (fee payer) |

Điểm cuối cùng là mấu chốt: **luôn có một chỗ nào đó giữ khoá Ed25519**. Câu hỏi không phải "làm sao tránh", mà là **"đặt nó ở đâu và ai chịu trách nhiệm"**. Ba phương án dưới đây chính là ba câu trả lời khác nhau.

---

## 3. Ba phương án — bảng quyết định

### A. MPC / TEE của bên thứ ba (Turnkey, Privy, Para…)

Passkey hoặc email mở một phiên; khoá Ed25519 nằm trong HSM/enclave của nhà cung cấp, chia sẻ theo MPC.

| | |
|---|---|
| ✅ | Nhanh nhất để có; có sẵn recovery bằng email; UX tốt nhất thị trường hiện nay |
| ❌ | **Khoá của người dùng nằm ở hạ tầng vendor.** Vendor đóng cửa / đổi chính sách / freeze tài khoản → người dùng mất đường ký |
| ❌ | Chi phí theo ví (theo bậc), cộng dồn theo MAU — đúng loại chi phí xấu với sản phẩm miễn phí cho người chơi |
| ❌ | **Vướng câu hỏi Q4b của legal brief:** nhà cung cấp Mỹ giữ khoá cho người dùng Việt Nam là thêm một dòng "bên xử lý dữ liệu" phải khai |
| **Kết luận** | **Không chọn làm mặc định.** Giữ làm phương án dự phòng nếu tiến độ Phase 1 trượt |

### B. Passkey smart wallet tự vận hành (precompile `secp256r1`) — **CHỌN**

Ví là một **PDA** do chương trình smart-wallet của Game9K sở hữu. Khoá P-256 nằm trong **secure enclave của thiết bị người dùng**, không rời khỏi đó. Khi ký: passkey ký *ý định*, precompile verify on-chain, PDA thực thi. Phí giao dịch do **paymaster của Game9K** trả.

```
Người dùng                    Game9K                    Solana
   │  đăng nhập email/Google     │                          │
   ├────────────────────────────►│  session (Supabase)      │
   │  tạo passkey (Face ID)      │                          │
   ├────────────────────────────►│  tạo PDA + lưu P-256 pubkey on-chain
   │                             │                          │
   │  mua token                  │                          │
   │  ── passkey ký intent ──►   │  ghép tx, ký fee payer   │
   │                             ├─────────────────────────►│ verify P-256 (SIMD-0075)
   │                             │                          │ PDA thực thi
```

| | |
|---|---|
| ✅ | **Không seed phrase, không 12 từ.** Người dùng chỉ thấy "xác nhận bằng Face ID" |
| ✅ | **Không ai giữ khoá của người dùng** — kể cả Game9K. Đây là điểm ăn tiền so với A |
| ✅ | **Chống phishing bằng toán học**: chữ ký WebAuthn gắn với `origin`, nên trang giả không xin được chữ ký |
| ✅ | **Khớp stack hiện tại**: chỉ Solana, không thêm chuỗi, không thêm vendor lõi |
| ✅ | Đăng nhập **vẫn** bằng email/Google — đúng yêu cầu |
| ❌ | **Phải vận hành paymaster** → Game9K trả phí giao dịch. Naive paymaster = lỗ hổng rút cạn SOL (xem §4) |
| ❌ | **Thiết bị-bound**: mất hết thiết bị là mất đường ký → **bắt buộc** có luồng khôi phục (xem §5) |
| ❌ | Không nên tự viết chương trình: WebAuthn ký `authenticatorData ‖ SHA-256(clientDataJSON)`, on-chain phải dựng lại đúng phong bì đó. Đây là chỗ implementation non tay bị mất tiền → dùng chương trình đã audit (ví dụ hướng tiếp cận của LazorKit / mẫu `Keyless`), không tự chế |

### C. Server giữ khoá, email OTP mở khoá — **đúng nghĩa đen của câu hỏi, nhưng REJECT làm mặc định**

Khoá mã hoá nằm trong DB của Game9K; mỗi lần đăng nhập, email OTP xác minh rồi server giải mã để ký.

| | |
|---|---|
| ✅ | UX đơn giản nhất; chạy trên mọi thiết bị; không phụ thuộc phần cứng |
| ❌ | **Game9K trở thành bên giữ tài sản.** Rò rỉ DB = mất tiền người dùng, và biến sản phẩm thành mục tiêu tấn công có giá trị cao |
| ❌ | Trái với chính luận điểm bán hàng: "không cần tin chúng tôi" |
| ❌ | **Rủi ro pháp lý nặng hơn hẳn**: giữ khoá hộ người dùng là dấu hiệu của dịch vụ lưu ký/trung gian thanh toán — đúng loại câu hỏi mà legal brief đang chờ luật sư trả lời, và không nên tự tạo thêm rủi ro khi chưa có kết luận |
| **Kết luận** | **Chỉ cho phép ở một phạm vi hẹp**: số dư nhỏ, có hạn mức, có nhãn "ví tạm — nâng cấp để tự quản", và **không** dùng cho giao dịch Launchpad |

---

## 4. Paymaster: chỗ dễ mất tiền nhất

Nếu Game9K trả phí giao dịch, paymaster phải bị chặn cứng — không phải một API mở:

| Chốt | Giá trị đề xuất |
|---|---|
| Chỉ tài trợ **danh sách instruction được phép** | `buy_priority`, `claim_stream`, `ragequit`, `register_passkey`. **Không** tài trợ `transfer` tuỳ ý |
| Trần theo ví | `≤ 0,02 SOL/ngày`, `≤ 0,20 SOL/tháng` |
| Trần toàn hệ thống | Ngân sách tháng đặt trong config; chạm trần thì **hạ xuống chế độ người dùng tự trả phí**, không chặn giao dịch |
| Chỉ ký khi có session hợp lệ | Kiểm `pop_state`, `sybil_risk_score < 0,5`, không ở `cooldown` |
| Ký **sau** khi passkey đã ký | Paymaster chỉ thêm chữ ký fee payer vào phong bì đã có chữ ký P-256; **không** bao giờ ký hộ nội dung |
| Ghi log | Mỗi lần tài trợ ghi `audit_logs` với `correlation_id` |

Không có 6 chốt này thì paymaster là một cái faucet mở bằng bot.

---

## 5. Khôi phục: điều kiện để phương án B dùng được thật

Không có seed phrase nghĩa là **không có câu hỏi bảo mật để trả lời**. Vì vậy phải thiết kế khôi phục ngay từ đầu, không để "làm sau":

| Tình huống | Cách xử lý |
|---|---|
| Đổi máy, còn email | Đăng nhập email → **magic link** → thêm **passkey mới** vào cùng PDA (đa thiết bị, tối đa 5) |
| Mất hết thiết bị, còn email | Magic link + **thời gian chờ 72h** trước khi passkey mới có hiệu lực; trong 72h đó gửi thông báo tới mọi kênh đã biết để chủ ví kịp chặn |
| Mất email | Khôi phục qua **passkey còn lại**; nếu mất cả hai → ví chuyển sang trạng thái chỉ-đọc, tài sản vẫn on-chain, không ai lấy được |
| Muốn tự quản hoàn toàn | **Xuất khoá / chuyển sang ví ngoài** (Phantom, Solflare) — luôn có đường ra |

Điểm cuối là điều kiện đạo đức của thiết kế: **không được khoá người dùng trong ví của mình**.

---

## 6. Quyết định

| Giai đoạn | Làm gì | Vì sao |
|---|---|---|
| **0 — MVP (chưa có tiền thật)** | Giữ nguyên `A1`: email/Google → tài khoản Web2 thuần, **không có ví on-chain**. Chơi game, tích `SPARK`, vote Arena đều chạy | Chi phí 0, rủi ro 0, và đã đúng từ đầu. Thêm ví lúc này chỉ thêm bề mặt tấn công |
| **1 — Mở Launchpad** | **Phương án B**: passkey smart wallet + paymaster có trần. Người chơi mới không thấy "ví", chỉ thấy "xác nhận bằng Face ID" | Không seed phrase, không vendor giữ khoá, chống phishing |
| **2 — Tuỳ chọn** | Đường **nâng cấp** sang ví tự quản (SIWS hiện có vẫn giữ nguyên cho người đã có ví) | Tôn trọng người dùng Web3 sẵn có, và cho người mới đường ra |

**Không làm:** phương án C làm mặc định; dẫn xuất khoá từ email; tự viết chương trình smart-wallet khi chưa audit.

### Điều kiện để Phase 1 được coi là xong

1. Chương trình smart-wallet có **audit độc lập** hoặc dùng bản đã audit của bên khác.
2. Test trên `LiteSVM`: passkey giả, replay, chữ ký sai `lowS`, 8 chữ ký/instruction.
3. Luồng khôi phục 72h chạy được **end-to-end** trên devnet.
4. Paymaster: bắn thử 1.000 giao dịch rác → xác nhận chạm trần và **không** tài trợ instruction lạ.
5. Đo lại: nếu paymaster vượt ngân sách dự kiến thì **hạ xuống phương án A** (vendor MPC) chứ không bỏ tính năng.

---

## 7. Nguồn

| Nội dung | Nguồn | Loại |
|---|---|---|
| SIMD-0075, precompile `secp256r1`, mainnet 06/2025, tối đa 8 chữ ký/instruction | `devrels.xyz/articles/passkeys-on-solana-secp256r1`; `learn.blueshift.gg` (Embedded Wallets) | Tài liệu kỹ thuật |
| WebAuthn ký `authenticatorData ‖ SHA-256(clientDataJSON)`; cần dựng lại phong bì on-chain | `learn.blueshift.gg`, `blog.getpara.com/solana-passkeys` | Tài liệu kỹ thuật |
| Hai kiến trúc: passkey-native PDA vs. MPC (LazorKit vs. Turnkey) | `devrels.xyz`, `blog.getpara.com` | Tài liệu kỹ thuật (có nêu tên sản phẩm — không phải khuyến nghị mua) |
| XWG dùng Firebase cho identity | **Quan sát trực tiếp** popup đăng nhập Google, 22/11/2026 | Bằng chứng |
| XWG có "embedded light wallet" nhưng không công bố nơi giữ khoá | Whitepaper XWG v2.0.0, tr. 30–31 | Tự công bố |

> **Không** tuyên bố bất kỳ phương án nào là "an toàn". Mọi phương án đều có một chỗ phải tin: A tin vendor, B tin phần cứng thiết bị + chương trình đã audit, C tin Game9K. Việc của ADR này là **chọn chỗ đáng tin nhất cho một sản phẩm chưa có pháp nhân** — và đó là B.
