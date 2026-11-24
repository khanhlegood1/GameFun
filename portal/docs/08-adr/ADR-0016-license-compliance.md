# ADR-0016 · License compliance: thay Redis 8, MinIO, Grafana

| | |
|---|---|
| **Trạng thái** | **Proposed — blocking S2** |
| **Ngày** | 2026-11-18 |
| **Người đề xuất** | AI (Claude) — soát license stack hiện tại |
| **Người quyết** | Principal Architect + Legal *(chờ ký)* |
| **Ảnh hưởng** | Hạ tầng, chi phí, pháp lý |
| **Liên quan** | [ADR-0008](ADR-0008-redis-streams.md), [ADR-0009](ADR-0009-clickhouse-olap.md), [ADR-0015](ADR-0015-opensource-stack.md) |

---

## Bối cảnh

Khi soát license cho ADR-0015, phát hiện **ba thành phần trong kiến trúc tham chiếu đang dùng license
không phù hợp với mô hình SaaS thương mại**. Đây không phải vấn đề lý thuyết: cả ba đều đã ghi trong
[NFR spec §1](../06-nfr/nfr-spec.md#1-kiến-trúc-tham-chiếu) như thành phần bắt buộc.

Số liệu license lấy từ GitHub API ngày 2026-11-18, đọc trực tiếp file `LICENSE`, không suy đoán.

## Vấn đề 1 — Redis (nghiêm trọng nhất)

| | |
|---|---|
| **Hiện tại** | `Redis 7` trong NFR §1 và [ADR-0008](ADR-0008-redis-streams.md) |
| **License Redis 8+** | **Tri-license**: RSALv2 **hoặc** SSPLv1 **hoặc** AGPLv3 |
| **License Redis 7.2 trở về trước** | BSD-3-Clause |

Đọc `LICENSE.txt` của `redis/redis` (2026-11-18) xác nhận nguyên văn:

> *"Starting with Redis 8, Redis Open Source is moving to a tri-licensing model... contributions are subject
> to your choice of: (a) the Redis Source Available License v2 (RSALv2); or (b) the Server Side Public License v1
> (SSPLv1); or (c) the GNU Affero General Public License v3 (AGPLv3). Redis Open Source 7.2 and prior releases
> remain subject to the BSDv3 clause license."*

**Vì sao đây là vấn đề:**

- **RSALv2** cấm cung cấp Redis như một dịch vụ cho bên thứ ba. Game9K không bán Redis, nhưng ranh giới
  "internal use" vs "service" với một nền tảng SaaS là vùng xám cần luật sư, không phải kỹ sư.
- **SSPLv1** yêu cầu mở source **toàn bộ stack** nếu cung cấp như dịch vụ. Không chấp nhận được.
- **AGPLv3** lây nhiễm với phần mềm kết nối qua network. Redis Streams là event bus của toàn hệ thống ⇒
  rủi ro lan sang API, worker, indexer.

**Quyết định:** chuyển sang **Valkey** (BSD-3-Clause, fork từ Redis 7.2 bởi Linux Foundation).

| | Redis 8 | **Valkey 8** |
|---|---|---|
| License | RSALv2 / SSPLv1 / AGPLv3 | **BSD-3-Clause** |
| Streams API | ✅ | ✅ tương thích 100% |
| Client (ioredis, redis-py) | ✅ | ✅ dùng nguyên, không đổi code |
| Stars | 77.5k | 27.7k |
| Vận hành | — | Đổi image, **không đổi code** |

**Đây là thay đổi 1 dòng trong Dockerfile / Terraform.** Không đổi code, không đổi API.
Chi phí migration ≈ 0. Không làm = nhận rủi ro pháp lý vĩnh viễn.

> **Ghi chú:** nếu chọn self-host Redis **7.2** (BSD) thì cũng hợp lệ về license, nhưng 7.2 không còn
> nhận security patch từ Redis Ltd. ⇒ phải tự backport. Valkey là lựa chọn đúng hơn.

## Vấn đề 2 — MinIO (object storage)

| | |
|---|---|
| **License** | **AGPL-3.0** |
| **Dùng cho** | Game bundle, thumbnail, evidence pack |

AGPL-3.0 với **phần mềm server** nghĩa là: nếu người dùng tương tác với MinIO qua network,
ta phải cung cấp source (của MinIO **và** phần dẫn xuất). MinIO là **storage độc lập**, API S3 chuẩn,
nên phần "dẫn xuất" trên lý thuyết là rỗng — nhưng đây là **rủi ro phải có ý kiến luật sư**, không phải
quyết định kỹ thuật.

**Ba lựa chọn:**

| Phương án | License | Đánh giá |
|---|---|---|
| **Cloudflare R2** (managed) | Thương mại, có egress free | ✅ **Chọn** — không self-host, không license risk, rẻ hơn S3 cho egress |
| AWS S3 | Thương mại | ✅ Được, nhưng egress đắt hơn R2 |
| `seaweedfs/seaweedfs` | **Apache-2.0** | ✅ Nếu bắt buộc self-host. 36k star. S3-compatible |
| MinIO self-host | AGPL-3.0 | ⚠️ Chỉ khi legal chấp nhận bằng văn bản |

**Quyết định:** **Cloudflare R2** cho GA1. `seaweedfs` là phương án self-host nếu cần chủ quyền dữ liệu.

## Vấn đề 3 — Grafana (observability)

| | |
|---|---|
| **License** | **AGPL-3.0** |
| **Dùng cho** | Dashboard D1–D5 trong [observability](../07-delivery/observability.md) |

Đây là **rủi ro thấp nhất** trong ba, và cần nói rõ vì sao:

Grafana là công cụ **hiển thị nội bộ**, không phải một phần của sản phẩm bán cho người dùng.
AGPL áp dụng khi *"người dùng tương tác với phần mềm qua network"*. Nhân viên nội bộ dùng dashboard
**không** phải "người dùng" theo cách hiểu thông thường, và ta không sửa Grafana.

**Quyết định:** **giữ Grafana**, nhưng:

1. Không fork, không patch Grafana.
2. Không expose Grafana ra internet công khai (chỉ qua VPN/SSO).
3. Nếu sau này cung cấp dashboard cho **studio** (đối tác bên ngoài) ⇒ **phải dùng giải pháp khác**
   (tự vẽ bằng Next.js, hoặc Grafana Cloud có license thương mại).

## Vấn đề 4 — Squads multisig

| | |
|---|---|
| **Program** | `Squads-Protocol/v4` — **AGPL-3.0** |
| **Client SDK** | `Squads-Protocol/public-v4-client` — **MIT** |

**Sử dụng program đã deploy on-chain không tạo ra tác phẩm dẫn xuất.** Ta gọi instruction qua CPI/transaction,
không copy code, không sửa program. ⇒ **Không có nghĩa vụ AGPL.**

**Nhưng:** nếu ta **fork** Squads program để sửa (ví dụ thêm logic timelock riêng), **thì** phải mở source.

**Quyết định:** dùng Squads v4 **đã deploy** (mainnet program ID chính thức). Không fork. Không copy code.

## Vấn đề 5 — Yellowstone gRPC

| | |
|---|---|
| **Repo** | `rpcpool/yellowstone-grpc` — **AGPL-3.0** |
| **Dùng cho** | Indexer ([ADR-0010](ADR-0010-rust-indexer.md)) |

Đây là **crate được import vào indexer** — không phải gọi qua network như Squads.

Phân tích: `yellowstone-grpc-client` được link vào binary indexer. Nếu indexer được cung cấp như
**dịch vụ network**, AGPL có thể áp dụng. Indexer trong Game9K là **thành phần nội bộ**, không expose
ra ngoài — nhưng binary vẫn là "phần mềm chạy trên server của ta".

**Ba phương án:**

| Phương án | Rủi ro | Chi phí |
|---|---|---|
| Dùng `yellowstone-grpc-client` (AGPL) | Trung bình — cần legal review | 0 |
| Dùng Geyser plugin chính thức của Agave | Thấp | Cao hơn (tự vận hành validator) |
| Poll RPC `getProgramAccounts` + `getSignaturesForAddress` | **Không** | Chậm hơn, tốn RPC credit |

**Quyết định tạm:** dùng `yellowstone-grpc-client`, **nhưng** coi đây là **rủi ro mở** cần legal review
trước GA. Đánh dấu `G-18` trong [gap register](../06-nfr/waf-review.md).
Nếu legal không chấp nhận: chuyển sang poll RPC cho GA1 (indexer chậm hơn nhưng đủ cho < 50 launch).

## Bảng tổng hợp

| Thành phần | License hiện tại | Rủi ro | Quyết định | Nỗ lực |
|---|---|---|---|---|
| Redis 8 | RSALv2/SSPLv1/AGPLv3 | **Cao** | → **Valkey** (BSD-3) | 1 dòng config |
| MinIO | AGPL-3.0 | **Cao** | → **Cloudflare R2** | Đổi SDK endpoint |
| Grafana | AGPL-3.0 | Thấp | Giữ, không expose | 0 |
| Squads v4 program | AGPL-3.0 | **Không** (không fork) | Giữ | 0 |
| `yellowstone-grpc-client` | AGPL-3.0 | Trung bình | Giữ + legal review (**G-18**) | 0 → 3 tuần nếu phải đổi |
| Payload CMS | MIT | Không | Giữ (schema riêng) | 0 |
| ALTCHA | MIT | Không | Giữ | 0 |
| Playgama bridge | LGPL-3.0 | Trung bình | **Chỉ đọc API**, không import | 0 |
| Anchor | Apache-2.0 | Không | Giữ | 0 |
| ClickHouse | Apache-2.0 | Không | Giữ | 0 |
| NestJS / Next.js | MIT | Không | Giữ | 0 |

## Hệ quả

**(+) Được:**
- Không còn thành phần nào trong stack bắt buộc phải mở source sản phẩm.
- Chi phí migration gần như 0 (Valkey là drop-in, R2 rẻ hơn S3).
- Có danh sách license để trả lời due-diligence của nhà đầu tư/đối tác.

**(−) Phải chấp nhận:**
- Valkey ít người biết hơn Redis ⇒ phải ghi trong runbook.
- R2 là vendor lock-in nhẹ (nhưng S3 API nên thoát được).
- `yellowstone-grpc` vẫn là rủi ro mở tới khi có legal opinion.

## Việc phải làm

| # | Việc | Owner | Hạn |
|---|---|---|---|
| 1 | Đổi image `redis:7` → `valkey/valkey:8` trong IaC + docker-compose | DevOps | trước S2 |
| 2 | Đổi MinIO → R2 trong PRD, NFR, ADR-0012 | Architect | trước S2 |
| 3 | Legal review AGPL cho `yellowstone-grpc-client` | Legal | trước S7 |
| 4 | Thêm `license-check` vào CI (chặn GPL/AGPL ở dependency của app) | DevOps | S2 |
| 5 | Ghi rõ "không expose Grafana ra internet" vào runbook | DevOps | S11 |

---

*Đây là ADR **blocking**: không ký thì không chốt hạ tầng ở S2, và rủi ro license sẽ theo dự án tới GA.*
