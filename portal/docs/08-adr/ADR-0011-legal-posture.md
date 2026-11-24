# ADR-0011 · Lập trường pháp lý: bond là quyền kinh tế có điều kiện, không phải chứng khoán; không marketing lợi nhuận

| | |
|---|---|
| **Trạng thái** | Proposed — cần legal opinion |
| **Ngày** | 2026-11-14 |
| **Người đề xuất** | AI (Claude) — sinh trong P01/P03 |
| **Người quyết** | Principal Architect *(chờ ký)* |
| **Ảnh hưởng** | Toàn hệ thống |
| **Liên quan** | xem cuối file |

## Bối cảnh & vấn đề

Đây là **quyết định có điều kiện**, chưa được chốt. Ghi lại để không ai quên.

**Lập trường dự kiến:**
- Bond **không** cam kết lợi nhuận; giá trị đến từ thị trường thứ cấp và quyền ưu tiên beta.
- Không có "revenue share cố định"; phần thưởng cho holder là **không tồn tại** — chỉ player nhận reward từ pool.
- Bond **không** phải equity, không có quyền biểu quyết, không có quyền nhận cổ tức.
- Không presale, không private round, không marketing "x100".
- Geo-fence: chặn launchpad ở jurisdiction chưa có opinion (mặc định: chặn US, mở VN/SEA sau khi có opinion).

**Điều kiện tiên quyết để mở launchpad ở VN:** legal opinion về:
1. Bond có bị coi là "chứng khoán" theo Nghị định 155/2020 không?
2. Game9K có cần giấy phép trò chơi điện tử trực tuyến (Nghị định 147/2024)?
3. Nghĩa vụ thuế của creator nhận USDC.

**Nếu legal opinion nói "có rủi ro cao":** phương án fallback là **bỏ bond**, chỉ dùng revenue-share off-chain (studio nhận % doanh thu theo hợp đồng, không có token). Điều này làm mất phần lớn giá trị sản phẩm nhưng vẫn giữ portal + rating.

**Trạng thái:** chưa chốt. **Blocking cho GA.**


## Hệ quả & rủi ro còn lại

Ghi trong phần "Hệ quả" ở trên. Rủi ro còn lại phải được theo dõi trong [WAF gap register](../06-nfr/waf-review.md#7-gap-register-tổng-hợp-có-owner--ngày) hoặc backlog.

## Tài liệu tham chiếu

- [PRD](../01-requirements/PRD-game9k.md)
- [Kiến trúc](../05-contracts/overview.md)
- [NFR](../06-nfr/nfr-spec.md)
- [Roadmap](../07-delivery/roadmap.md)

---
*Template AI-Agile · mọi ADR phải có trạng thái rõ (Proposed/Accepted/Deprecated/Superseded) và người quyết có tên.*
