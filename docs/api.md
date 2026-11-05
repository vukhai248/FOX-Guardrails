# FOX-Guard API — Đợt 1

SDK hiện chuẩn hoá ký tự ở cả ba trạm và **chưa chặn gì cho tới Đợt 4**.
Mọi `check_*` luôn trả `action="allow"`, kể cả khi `risk="high"`.
Classifier, PII, policy và audit chưa chạy; khai báo trong YAML chỉ được kiểm tra cấu hình.
Nguồn: `src/fox_guard/guard.py:25`, `src/fox_guard/config.py:39`.

## Hợp đồng dữ liệu

| Model | Trường |
| --- | --- |
| `GuardContext` | `session_id`, `station` bắt buộc; `user_ref`, `source`, `intent`, `lang`, `arm` mặc định `None` |
| `Finding` | `detector`, `kind`, `severity`, `evidence` bắt buộc; `score`, `span`, `technique` mặc định `None` |
| `Decision` | `decision_id`, `action`, `text`, `risk`, `latency_ms` bắt buộc; `findings`, `reasons`, `flags` mặc định list rỗng riêng từng instance; `degraded=False` |

`station`: `input | context | output`. `action`: `allow | mask | block | review`.
`severity` và `risk`: `low | medium | high`.
`kind`: `injection | pii | solicitation | link | unicode`.
Nguồn: `src/fox_guard/types.py:10`, `src/fox_guard/types.py:22`, `src/fox_guard/types.py:41`.

`Finding.evidence` dài tối đa 120 ký tự; bên tạo finding phải che PII trước khi đưa vào.
Validator này chỉ giới hạn độ dài, chưa thực hiện che PII.
`span` là khoảng nửa mở `[start, end)` trên view `clean`, thoả `0 <= start <= end`,
hoặc `None` nếu không ánh xạ được (ví dụ một số view giải mã).
Nguồn: `src/fox_guard/types.py:22`.

## SDK đang dùng được

```python
from fox_guard import Guard, GuardContext

guard = Guard.from_config("fox-guard.yaml")
ctx = GuardContext(session_id="synthetic-demo", station="input", lang="vi")
decision = guard.check_input("Xin chào\u200b shop", ctx)
print(decision.model_dump_json())
```

Output thật từ lệnh trên trong worktree (ID và độ trễ đổi giữa các lần chạy):

```json
{"decision_id":"6a4dcdbcaf3d419fa89c42615b67eb60","action":"allow","text":"Xin chào shop","risk":"low","findings":[{"detector":"unicode:invisible","kind":"unicode","severity":"low","score":null,"span":[8,8],"evidence":"Removed 1 invisible code points","technique":"T3.1"}],"reasons":["Phát hiện ký tự Unicode vô hình bất thường."],"latency_ms":74.6662000019569,"degraded":false,"flags":[]}
```

Lần gọi đầu này gồm cả nạp bảng confusables; đây là thời gian SDK của một lần chạy,
không phải p95 của benchmark chuẩn hoá.

`Guard.from_config(path)` nhận `str` hoặc `pathlib.Path`, đọc YAML UTF-8.
Khoá lạ ở mọi cấp gây `pydantic.ValidationError` với vị trí khoá; YAML không phải mapping gây `ValueError`.
`normalize.max_chars` nằm trong `[1, 20000]`; `decode_max_depth` trong `[0, 2]`.
Ngưỡng classifier có thể `null`; nếu cung cấp thì nằm trong `[0, 1]` và `theta_low <= theta_high`.
Nguồn: `src/fox_guard/config.py:9`, `src/fox_guard/config.py:13`, `src/fox_guard/config.py:18`, `src/fox_guard/config.py:47`.

| Hàm | Kết quả Đợt 1 |
| --- | --- |
| `check_input(text: str, ctx: GuardContext) -> Decision` | Chuẩn hoá đầu vào khách hàng |
| `check_context(text: str, ctx: GuardContext) -> Decision` | Chuẩn hoá một đoạn dữ liệu ngữ cảnh |
| `check_output(text: str, ctx: GuardContext) -> Decision` | Chuẩn hoá câu trả lời |
| `restore(text: str, ctx: GuardContext) -> str` | Trả nguyên văn; chưa có vault B5 |
| `redact_for_log(text: str, ctx: GuardContext) -> str` | Trả `clean` trực tiếp từ chuẩn hoá; chưa che PII (`TODO(B5)`) |

Đặt `ctx.station` tương ứng với hàm được gọi. Đợt 1 chưa dùng metadata để quyết định policy.
`Decision.text` là `clean`; `risk` là severity cao nhất trong `findings`, mặc định `low`.
Mỗi finding có một lý do tiếng Việt. `decision_id` là `uuid4().hex` mới;
`latency_ms` đo bằng đồng hồ đơn điệu, gồm thời gian chuẩn hoá và tạo kết quả.
Nguồn: `src/fox_guard/guard.py:49`, `src/fox_guard/guard.py:69`.

`redact_for_log` dành cho `guard_log` của web và không gọi `restore`.
Đợt 1 **chưa bảo đảm riêng tư PII khi ghi log**; chức năng che không thể hoàn nguyên thuộc B5.
Nguồn: `src/fox_guard/guard.py:81`, `src/fox_guard/guard.py:85`.

## Sidecar dự kiến — B7, chưa triển khai

Đặc tả nguồn: `docs/plans/B-guardrails.md:86`.

| Endpoint | Request / response dự kiến |
| --- | --- |
| `POST /v1/guard/input` | JSON `{text, context: GuardContext}` → `Decision` |
| `POST /v1/guard/context` | Cùng body, kiểm một đoạn context → `Decision` |
| `POST /v1/guard/output` | Cùng body, kiểm đầu ra → `Decision` |
| `GET /v1/decisions?action=&station=&since=` | Danh sách quyết định audit có bộ lọc |
| `POST /v1/decisions/{id}/review` | JSON `{verdict: "approve" | "reject", note}` |
| `GET /healthz` | Kiểm tra sức khoẻ dịch vụ |

Ví dụ curl cho sidecar tương lai; chưa thể chạy ở Đợt 1:

```bash
curl -X POST http://localhost:8091/v1/guard/input \
  -H 'Content-Type: application/json' \
  -H 'X-FOX-Key: <configured-key>' \
  -d '{"text":"Xin chào shop","context":{"session_id":"synthetic-demo","station":"input","lang":"vi"}}'
```

Header `X-FOX-Key` và lệnh phục vụ sidecar thuộc kế hoạch B7
(`docs/plans/B-guardrails.md:260`); chưa phải khả năng của CLI hiện tại.
