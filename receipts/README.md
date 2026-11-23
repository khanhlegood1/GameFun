# `receipts/` — biên bản đo

**Trạng thái hôm nay: `0` biên bản. Đây là trạng thái ĐÚNG, không phải chỗ trống chưa điền.**

Repo này **không** gọi mạng: `scripts/check_egress_lock.py` chứng minh điều đó trên toàn repo,
không chỉ trên `scripts/`. Nên chưa có lần đo AI nào chạy thật, và do đó chưa có biên bản nào.

> Một tệp biên bản được tạo ra để "cho có dữ liệu" là một biên bản **giả** — và nó tệ hơn
> không có gì, vì nó làm một cổng báo xanh mà không chứng minh gì.

## Khi nào có tệp ở đây

Chỉ khi một lần đo **thật** đã chạy, và tệp được sinh bằng:

```bash
python3 scripts/receipt_lock.py --new \
    --date 2026-11-23 \
    --model-requested "…-latest" \
    --model-served   "…-2026-11-01" \
    --provider       "…" \
    --input          docs/WHITEPAPER.md
```

rồi **điền** `output_sha256` và `artifact_bytes` sau khi chạy. Chưa điền hai trường đó thì
biên bản chưa chứng minh gì.

## Hình dạng bắt buộc

`scripts/receipt_lock.py` kiểm **6 bất biến**:

| # | Bất biến |
|---|---|
| 1 | Đủ 8 trường: `receipt_id` · `date` · `model_requested` · `model_served` · `provider` · `input_sha256` · `output_sha256` · `artifact_bytes` |
| 2 | `model_served` ≠ `model_requested` ⇒ phải có `drift_note` |
| 3 | Tệp tổng hợp không trộn hai `model_served` khác nhau |
| 4 | Không có nội dung tài liệu — chỉ hash |
| 5 | `input_sha256` phải khớp tệp thật nếu tệp còn tồn tại |
| 6 | Không có `score` / `confidence` / `grade` / `pass` / `verdict` |

Bất biến 5 là lý do thư mục này tồn tại: nó là bản sao của một lỗi thật — một phép đo chạy trên
tệp **đã bị đột biến**, cho kết quả sai, và suýt được ghi vào quyết định. Xem `docs/35` §2.

## Không có hạn xem lại

Biên bản **không** có `review_by`. Hạn dành cho **lời khẳng định** (`pm/claims-registry.json`),
không dành cho **dữ liệu**. Đặt hạn cho dữ liệu là tự tạo một mục `OPEN` không bao giờ đóng được
— `docs/35` §6.
