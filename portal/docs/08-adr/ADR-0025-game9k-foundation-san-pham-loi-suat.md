# ADR-0025 — "Game9K Foundation" làm sản phẩm lợi suất: **không**, và vì sao

**Trạng thái:** Proposed — chờ PO ký
**Ngày:** 2026-11-22
**Người đề xuất:** AI agent · **Người quyết:** Project Owner (Lê Xuân Khánh)
**Liên quan:** [ADR-0024](ADR-0024-san-pham-loi-suat-tach-roi.md) · [ADR-0011](ADR-0011-legal-posture.md) · [`changelog/README.md` §6](../../changelog/README.md)

> ⚠️ **Tài liệu này không phải ý kiến pháp lý.** Nó tổng hợp ràng buộc công khai
> để PO biết **phải hỏi luật sư câu gì**. Mọi kết luận dưới đây cần luật sư có
> giấy phép xác nhận trước khi dùng làm cơ sở hành động.

---

## 1. Câu hỏi

PO hỏi: *"Nếu thành lập một pháp nhân khác tên **Game9K Foundation** để làm sản phẩm
lợi suất Basis?"*

Đây là một ý **đúng hướng** — tách pháp nhân là cách chuẩn để tách rủi ro. Nhưng nó
gặp **ba ràng buộc cụ thể** mà từ "Foundation" tự nó tạo ra.

---

## 2. Ba ràng buộc — kiểm được, không phải quan điểm

### 2.1 "Foundation" là **hình thức pháp lý**, không phải chữ trang trí

Nếu dùng **Cayman Foundation Company** (cấu trúc phổ biến nhất cho quỹ mã hoá):

| Ràng buộc | Nguồn |
|---|---|
| Là tổ chức **"not for profit"** — không chia lợi nhuận cho thành viên | [Foundation Companies Act (2025 Revision)](https://www.cima.ky/upimages/lawsregulations/FoundationCompaniesAct2025Revision_1742317042.pdf) |
| **Không** được kinh doanh thương mại với công chúng trừ khi điều lệ quy định rõ | Cùng nguồn, và [hướng dẫn cấu trúc](https://www.expanship.com/ky/blog/types-of-companies-in-cayman-islands) |
| Không phát hành cổ phần; quản trị theo **mục tiêu**, không theo cổ đông | Cùng nguồn |
| Mọi phân phối làm mất khả năng trả nợ là **"prohibited distribution"** — có thể là **tội hình sự** với giám đốc | Cùng nguồn |

**Hệ quả trực tiếp:** một Foundation **không thể** là nơi nhận lợi nhuận từ chiến
lược Basis rồi chia cho cổ đông. Nếu lợi suất được chia cho người góp vốn, cấu trúc
đó **không phải** Foundation — nó là một công ty thương mại mang tên "Foundation".

> Đây là chỗ dễ sai nhất: nhiều dự án đặt tên "Foundation" cho một thực thể thương
> mại. Tên không làm nên hình thức pháp lý. Nếu PO muốn **thực thể thương mại**, hãy
> gọi nó là công ty — và dùng đúng loại công ty.

### 2.2 Quản lý tài sản của người khác **có toàn quyền** = cần giấy phép CIMA

Chiến lược Basis vận hành như một **quỹ**: người gửi vốn, bên vận hành quyết định
mở/đóng vị thế. Theo **Securities Investment Business Act (SIBA)** của Cayman:

| Hoạt động | Có thuộc SIBA? |
|---|---|
| "Managing securities belonging to another person **in circumstances involving the exercise of discretion**" | **Có** |
| Chỉ cần **đăng ký** (Registered Person) thay vì giấy phép đầy đủ, **nếu** khách hàng **toàn bộ** là nhà đầu tư tinh vi | Có điều kiện |
| Bán cho **công chúng** | Cần **giấy phép đầy đủ** của CIMA |

Nguồn: [Harneys — Securities investment business in the Cayman Islands](https://www.harneys.com/insights/securities-investment-business-in-the-cayman-islands/),
[Stuart's Law — SIBL guidance](https://www.stuartslaw.com/cms/document/SIBL_Guidance_Note.pdf).

**Với sản phẩm lợi suất cho người chơi game, khách hàng là công chúng — không phải
nhà đầu tư tinh vi.** Nghĩa là con đường "đăng ký nhẹ" **không áp dụng**. Con đường
còn lại là giấy phép đầy đủ, với vốn yêu cầu và nghĩa vụ báo cáo.

### 2.3 Rủi ro lớn nhất: nhìn như một quỹ đầu tư **bán cho công chúng**

Đây là điểm tôi muốn PO cân nhắc kỹ nhất, vì nó **không** phải vấn đề kỹ thuật.

Một sản phẩm mà: (a) người dùng gửi tiền, (b) bên vận hành mở vị thế, (c) lợi suất
đến từ chênh lệch thị trường — **về hình thức rất giống một quỹ**. Nếu bán cho công
chúng ở Mỹ, nó có thể bị xem là chào bán **chứng khoán** theo Howey, và không có
miễn trừ Reg CF cho loại này (Reg CF dành cho *phát hành chứng khoán của chính công
ty*, không dành cho *quản lý tiền của người khác*).

**Điều này khác hoàn toàn với launchpad.** Launchpad bán quyền kinh tế có điều kiện
gắn với một phiên bản game (ADR-0011). Sản phẩm lợi suất là **dịch vụ quản lý tiền**.
Hai thứ này không cùng loại giấy phép, không cùng cơ quan quản lý.

---

## 3. Quyết định

### 3.1 Không dùng tên "Foundation" cho một thực thể thương mại

| Nếu muốn | Dùng |
|---|---|
| Thực thể **kinh doanh**, nhận vốn, chia lợi nhuận | Công ty thương mại (Delaware C-Corp hoặc Cayman exempted company) — **không** gọi là Foundation |
| Thực thể **phi lợi nhuận**, giữ giao thức / tiêu chuẩn / tài sản chung | Foundation — nhưng **không** vận hành sản phẩm lợi suất |
| Vận hành sản phẩm lợi suất | Thực thể **được cấp phép** (hoặc hợp tác với bên đã có giấy phép) |

### 3.2 Ba phương án, xếp theo mức rủi ro tăng dần

| # | Phương án | Rủi ro pháp lý | Chi phí | Nhận xét |
|---|---|---|---|---|
| **A** | **Không tự vận hành.** Tích hợp một giao thức lợi suất **đã có giấy phép** (hoặc đã có ý kiến pháp lý), Game9K chỉ làm giao diện phân phối | **Chưa xác định** — xem ⚠️ dưới | Thấp | Mất phần lớn biên lợi nhuận, nhưng **không** tạo ra nghĩa vụ quản lý quỹ |
| **B** | Thực thể riêng, **chỉ nhà đầu tư tinh vi**, không bán cho người chơi | Trung bình | Trung bình | Thu hẹp thị trường gần như về 0 với sản phẩm game |
| **C** | Tự vận hành, bán cho công chúng | **Cao** | Cao | Cần giấy phép đầy đủ + ý kiến pháp lý ở từng thị trường |

> ### ⚠️ Sửa lại (2026-11-22): "phân phối" **không** tự động là rủi ro thấp
>
> Bản đầu của ADR này ghi phương án A là "rủi ro thấp nhất" vì **không giữ tiền**. Đó là
> kết luận theo trực giác, và nó **có thể sai**.
>
> Theo **SIBA** của Cayman, danh sách hoạt động bị điều chỉnh **không chỉ** có "quản lý":
> *"making arrangements in relation to the securities **with a view to another person dealing
> in securities**"* = **securities arranging** — cũng nằm trong danh sách phải có giấy phép.
>
> Nghĩa là: nếu Game9K đưa giao diện cho người chơi tiếp cận sản phẩm của bên thứ ba **và
> thu phí**, Game9K có thể đang **arranging securities**.
>
> **Không giữ tiền không đồng nghĩa không bị điều chỉnh.** Xem
> [`docs/12-decisions/2026-11-22-doi-thu-loi-suat-va-hop-tac.md` §4](../12-decisions/2026-11-22-doi-thu-loi-suat-va-hop-tac.md)

**Đề xuất của AI: phương án A** — vẫn là phương án ít rủi ro **vận hành** nhất, nhưng
**rủi ro pháp lý chưa xác định** cho tới khi có câu trả lời cho câu hỏi thứ 4 dưới đây. Lý do không phải vì nó dễ, mà vì nó **đúng với
điều PO muốn**: tách hẳn khỏi launchpad (ADR-0024). Phương án A tách biệt **hoàn
toàn** — Game9K không giữ tiền, không quản lý vị thế, không chịu rủi ro funding.
Nếu muốn giữ biên lợi nhuận, có thể thu **phí phân phối**, thứ không cần giấy phép
quản lý quỹ.

### 3.3 Nếu vẫn chọn C: ba câu phải hỏi luật sư **trước** khi làm gì

1. Thực thể vận hành chiến lược Basis cho người dùng Game9K có thuộc SIBA (Cayman)
   hoặc tương đương ở nơi đăng ký không?
2. Sản phẩm này có bị xem là chào bán chứng khoán ở Mỹ không, và có miễn trừ nào áp
   dụng cho **quản lý tiền của người khác** (không phải phát hành chứng khoán của
   chính mình) không?
3. Nếu người dùng là người chơi game (không phải nhà đầu tư tinh vi), có yêu cầu
   **công bố rủi ro** hay **giới hạn** nào bắt buộc không?
4. **Nếu Game9K chỉ hiển thị/phân phối sản phẩm của bên đã có giấy phép và thu phí phân
   phối, hoạt động đó có phải "securities arranging" theo SIBA không?** Có miễn trừ nào cho
   phân phối thuần kỹ thuật (không giới thiệu, không thu phí) không?

> Ba câu này **khác** ba câu đang chờ ở [`changelog/README.md` §6](../../changelog/README.md).
> Không gộp chúng vào cùng một lần hỏi luật sư — chúng thuộc hai lĩnh vực khác nhau.

---

## 4. Hệ quả

**Nếu chọn A (đề xuất):**
- Không cần thành lập pháp nhân mới cho sản phẩm lợi suất.
- ADR-0024 vẫn áp dụng nguyên vẹn: không chung kho tiền, không chung điểm, không
  chung quyền quản trị.
- Phải kiểm đối tác: giấy phép của họ, và **hợp đồng phải nói rõ ai chịu rủi ro gì**.

**Nếu chọn B hoặc C:**
- Phải có ý kiến pháp lý **trước** khi viết code.
- ADR-0024 §5 điều kiện (c) chưa thoả ⇒ CI vẫn chặn code (xem
  [`check_yield_isolation.py`](../../scripts/check_yield_isolation.py)).

## 5. Điều ADR này KHÔNG nói

- **Không** chọn nơi thành lập. Delaware / Cayman / Singapore / VN đều có thể đúng,
  phụ thuộc câu trả lời của luật sư.
- **Không** nói sản phẩm lợi suất có nên làm hay không. PO đã quyết **có** ở
  [ADR-0024](ADR-0024-san-pham-loi-suat-tach-roi.md). ADR này chỉ nói **bằng cách nào**.
- **Không** thay thế ADR-0011. ADR-0011 nói về bond và launchpad; ADR này nói về
  một dòng sản phẩm **khác loại**.

## 6. Tự kiểm — ADR này sai ở đâu?

1. **Tôi không phải luật sư.** Ba ràng buộc ở §2 dựa trên luật công khai, nhưng áp
   dụng luật vào một cấu trúc cụ thể là việc của người có giấy phép. Nếu luật sư nói
   khác, ADR này sai và phải sửa.
2. **§2.2 có thể quá chặt.** Có thể có miễn trừ tôi chưa thấy (ví dụ: cấu trúc trong
   đó người dùng **tự** mở vị thế, không ai quản lý hộ). Nếu vậy, phương án C rẻ hơn
   đáng kể. **Phải hỏi luật sư câu này.**
3. **"Not for profit" không có nghĩa là không được có lãi.** Foundation có thể có
   thặng dư; cái bị cấm là **chia** thặng dư cho thành viên. Nếu PO muốn Foundation
   **giữ** lợi nhuận để tái đầu tư vào giao thức, điều đó có thể hợp lệ — nhưng đó
   **không** phải sản phẩm lợi suất cho người dùng.
