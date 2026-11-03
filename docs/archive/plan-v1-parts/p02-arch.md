---

## 2. Kiến trúc

### 2.1 Ba trạm và luồng request

```
 client (SDK OpenAI) — base_url = http://127.0.0.1:20129/v1
        │  POST /v1/chat/completions {model, messages[], stream?, tools?, stream_options?}
        ▼
 [0] HTTP layer : schema strict (pydantic), registry phiên (2.8), route, whitelist path
        │
        ▼
 [1] TRẠM 1 — INPUT : chuẩn hoá → F1 → (F2 khi luật chạm) → verdict → action
        │              nhìn: role=user; system nếu policy bật
        ▼
 [2] TRẠM 2 — CONTEXT: quét role=tool, RAG chunk, system, lịch sử assistant
        │              + đánh giá toàn phiên (state, multi-turn) — chỗ indirect injection nằm
        ▼
 [3] FORWARD : HTTPX async → 9router 127.0.0.1:20128/v1 (giữ nguyên model/params/headers)
        │
        ├──── stream=false ─────────────┬──── stream=true ─────────────────────┐
        │  [4] TRẠM 3 — OUTPUT         │  [4'] TRẠM 3 — OUTPUT theo SEGMENT       │
        │  quét CẢ CỤC: text +          │  đệm câu + overlap K=512; tool-call JSON │
        │  tool_calls[].arguments       │  đệm riêng; verdict trước khi phát        │
        └───────────────┬───────────────┴──────────────┬──────────────────────────┘
                        ▼                              ▼
 [5] LOG + STATE : JSONL (nguồn sự thật, hash-chain) + SQLite (phiên/escalations) + metrics
                        │
                        ▼
                 client (JSON hoặc SSE byte-compatible OpenAI)
```

| # | Bước | Việc cụ thể | Đầu ra |
| --- | --- | --- | --- |
| 0 | HTTP layer | Schema strict; **từ chối có mã** shape lạ (2.8); tính `sid` server-side; route: chat/completions + completions qua trạm, models = passthrough khai báo | `RequestCtx` |
| 1 | TRẠM 1 INPUT | (a) chuẩn hoá Unicode (13 bước, §3.2); (b) **F1 luật chạy trước** (rẻ, tất định); (c) điểm vùng nghi ngờ → F2; (d) mơ hồ + có ngân sách → F3 **async** (2.6); (e) gộp verdict (§3.5) | `Verdict(station=input)` |
| 2 | TRẠM 2 CONTEXT | Quét mọi nội dung **không do người dùng gõ lượt này**: tool output, RAG chunk, system, lịch sử assistant; + scoring toàn phiên (peak+accumulation) | `Verdict(station=context)` |
| 3 | FORWARD | HTTPX async; giữ nguyên payload (trừ phần mask); chuyển tiếp `stream_options.include_usage` (QĐ-C10) | response upstream |
| 4/4' | TRẠM 3 OUTPUT | non-stream: quét **cả cục** (text + tool arguments + markdown); stream: quét theo **segment** (2.5) | `Verdict(station=output)` |
| 5 | LOG + STATE | Mọi `Finding` + verdict + action → JSONL (hash-chain, §4.5); SQLite (phiên, đếm, hàng đợi escalate); metrics | log + bản ghi |

**Vì sao 3 trạm:** trạm 2 là nơi indirect injection nằm (số 70%/8% ở §1.1#1) và là trạm "kiểm được ngữ cảnh đã nhét vào `messages`" — **không** kiểm được kho dữ liệu (khai báo §1.4); trạm 3 là chốt cuối cho PII rò qua câu trả lời (OWASP: phát hiện ở output *"is a last line and it is porous"* — `risk-taxonomy-2026.md` §LLM02, dẫn qua bài test-guide `[THỨ CẤP]`). Thị trường ủng hộ thiết kế nhiều trạm theo "trust boundary" thay vì quét mọi chunk (AWS/baristalabs 23/07/2026 — `streaming-guardrails.md` §e.1).

### 2.2 Streaming: mode `sentence` + overlap K=512 (mặc định)

Hai yêu cầu kéo ngược nhau: *"A guardrail wants to accumulate text before judging. Streaming wants to release text before judging."* (`streaming-guardrails.md` §a). **Chọn `stream_mode: sentence`** làm mặc định; 3 chế độ cấu hình được: `hold` (đệm toàn bộ — chính xác nhất, mất streaming), `window` (cửa sổ trượt — nhanh nhất), `pass` (chuyển thô + log — **chỉ** để đo baseline C0/C5). Có thể đổi mặc định **chỉ sau khi M0 đo TTFT** (§7).

Đặc tả đệm (đủ để code):

1. **Phân đoạn câu**: cắt tại `.`, `!`, `?`, `\n\n`, `。？！`; tôn trọng số thập phân `1.234` và viết tắt VN (`vd.`, `etc.`) — ranh giới câu là điều kiện dừng chuẩn hoá (SentGuard: `τ_i = inf{ t>τ_{i−1} : b(y≤t)=1 }`).
2. **Đệm phát**: giữ **câu hiện tại chưa phát + đuôi overlap K=512 ký tự** của câu trước (`K` cấu hình được). **K=512 là sàn, không phải tuỳ chọn trang trí**: cửa sổ 512 ký tự bắt **96/128** cặp, quét trong nội bộ chunk chỉ **38/128** (`streaming-guardrails.md` §c.1, arXiv 2608.10279).
3. **Trigger kiểm** (cái nào trước): (a) hết câu; (b) đệm ≥ `max_segment_chars=600` (chặn câu "bất tử"); (c) quá `max_hold_ms=1500` kể từ lần phát trước → phát phần chắc chắn an toàn tới **ranh giới từ an toàn gần nhất**, giữ đuôi lại.
4. **Không bao giờ rescan toàn prefix** — chi phí quadratic: chunk 512 ký tự → **13.261 ms**; chunk 8 ký tự → **829.640 ms** (~62×; response 16.384 ký tự) (`streaming-guardrails.md` §c.1/D5/D6). Chỉ quét `(đuôi overlap + segment mới)` + máy trạng thái "mẫu dở".
5. **Ngân sách gọi detector**: F1 luật chạy mọi segment; F2/F3 theo lịch **"1 lần/đầu response + 1 lần/mỗi 5 segment"** — đối chiếu: Bedrock quét mỗi 50 ký tự tốn **100 lần đánh giá** cho 5.000 ký tự; batch 1.000 ký tự còn **5 lần** (**giảm 20×**) (`streaming-guardrails.md` §c.3/D9).
6. **PII bị cắt qua nhiều chunk** — 3 lớp + 1 tổng quát hoá (vá R5):
   - (a) overlap `K=512` bao mọi entity ≤512 ký tự (thẻ 16–19 số, CCCD 12, IBAN — `vietnamese-pii-formats.md` Phần A);
   - (b) máy trạng thái "mẫu dở": đuôi kết thúc giữa run `[0-9+\-.\s]{8,}` hoặc giữa `local@dom…` ⇒ **không phát** tới khi có ký tự kết thúc;
   - (c) `hold` khi policy `pii_critical` (chốt chặn cuối cho phiên nhạy cảm);
   - (d) **tổng quát hoá "mẫu dở" thành prefix-trie cho MỌI recognizer** (không chỉ số/email): không phát phần đuôi khớp tiền tố của mẫu dở — entity có chữ (`[A-Z]{2}\d{13}` BHYT, hộ chiếu `[A-Z]\d{7}`, biển số `51A-123.45`, địa chỉ dài) bị flush tại `max_segment_chars` vẫn có thể cắt; phơi nhiễm công bố **theo lớp PII**, không một số chung.

### 2.3 Sự thật không thể tránh: token đã phát thì KHÔNG rút lại được

Đã kiểm chứng chéo 5–6 nguồn (`streaming-guardrails.md` §c.2): SentGuard limitations *"content already released before a later unsafe decision cannot be withdrawn"*; NeMo `stream_first: True` = *"the user has already received the tokens"*; TrueFoundry *"it cannot retract content already shown or acted on"*; comment code TanStack *"can only append to what the consumer saw, never retract it"*. **Retract chỉ tồn tại ở tầng UI** — tác giả tự nói *"a real improvement even though it isn't a fix"* ⇒ **không dùng trong thiết kế**; ghi vào báo cáo như giới hạn.

Hệ quả thiết kế: (i) ngăn phơi nhiễm ở **tầng đệm** (span nguy hiểm không ra khỏi buffer trước khi có verdict); (ii) khai báo `buffered_output: true` cho `sentence`/`hold`; `residual_exposure ≈ 1 segment + K` cho `window`; **full** cho `pass` — kèm câu tuyên bố theo draft spec `agent-hooks` (§12.1a — **draft spec**, repo gốc `responsibleai/agent-hooks`, refreshed 2026-07-15; mirror `github.itlym.cn` bỏ khi trích).

Khi phát hiện giữa dòng, đúng **3 hành vi** (phân biệt mức "rút lại"):

| Hành vi | Mô tả | Mặc định của ta |
| --- | --- | --- |
| **Sever + deny frame** | Cắt stream: 1 chunk SSE cuối + `finish_reason`, mọi token sau không phát; body "provider-compatible" để SDK render như refusal bình thường | Documented cho **injection high-severity đã đủ căn cứ** (F1 tất định / quorum) |
| **Redact tại chỗ** | `flushBuffer()` → `redactContent(...)` — chỉ áp cho phần **còn trong buffer**; thay span bằng placeholder rồi phát tiếp | Documented cho **PII mức mask** |
| **Retract** | Không tồn tại ở tầng protocol | **Không dùng** (như trên) |

**Tách 2 loại frame kết stream (vá M7):** (a) *vi phạm nội dung* → 1 chunk content refusal + `finish_reason` + `[DONE]` (không phải `error`); (b) *lỗi hạ tầng* (detector/breaker chết) → error event có mã lớp. Phân biệt này cần cho byte-compat **và** cho cách đo "ký tự phơi nhiễm trước deny".

### 2.4 CHỐT — Mặc định can thiệp (một nghĩa duy nhất, áp cho log/manifest/policy)

> **Nguyên tắc chốt:** *PII ⇒ mask ở mọi trạm. Injection ⇒ **chỉ luật tất định được block một mình**; classifier/judge chỉ góp phiếu và **block cần quorum ≥2 họ độc lập**. Không có mặc định `block` nào khác trong v1.*

| Trạm | Injection (deterministic) | Injection (không tất định) | PII | Ngoài phạm vi v1 |
| --- | --- | --- | --- | --- |
| **1 INPUT** | **block** (kèm log lý do) | phiếu; **block khi quorum ≥2 họ ≥ MEDIUM**; còn lại log/escalate | **mask** trước khi gửi model | — |
| **2 CONTEXT** | **block/locate**: cách ly span độc (placeholder + bọc "untrusted content") khi tất định | phiếu; quorum như trạm 1; escalate khi lặp ≥3 lần/phiên | **mask** | — |
| **3 OUTPUT** | **sever+deny** (stream) / chặn cục (JSON) | phiếu; quorum | **mask** (redact trong buffer) | harmful/toxicity & egress markdown = **HOÃN, không hứa** |

- **Vì sao mask là mặc định PII, không block:** mask là mức duy nhất giữ utility (PII xuất hiện trong yêu cầu hợp lệ: địa chỉ giao hàng, tra cứu đơn hàng); chặn ở input bằng mask là biện pháp "sớm" nhất (OWASP khuyến nghị uỷ quyền trước khi truy hồi; Bedrock cấu hình `ANONYMIZE`).
- **Vì sao không block theo classifier đơn lẻ:** over-defense **40,1%** (PG2) ⇒ block méo vận hành; block chỉ khi **luật tất định** hoặc **quorum quy định ở §3.5**. Quyền veto của **khối PII tất định (checksum/allowlist) là veto cho mức MASK** (buộc mask dù F2 im lặng) — **không** phải veto block (chốt M2: tách "checksum ⇒ F1 veto" khỏi "ML/NER ⇒ F2 phiếu").
- **Escalate** = severity HIGH nhưng dưới ngưỡng block, hoặc ≥3 lần chạm cùng phiên → **hàng đợi async + hành động mặc định an toàn theo timeout**; ngân sách: escalate chỉ cho HIGH/tín hiệu đặc biệt (FPR guardrail tham chiếu **5,7%** ⇒ escalate mọi "medium" = ~57 ca/1k request — không khả thi cho một người trực; `plugin-architecture.md` §2.2).
- **Escalate không hứa "người trực 24/7"** và **không hứa năng lực 72 giờ** (Điều 29 NĐ 356/2025): phát biểu đúng = *"log đủ chi tiết (timestamp, chủ thể, loại dữ liệu, bằng chứng) để một tổ chức có thể thực hiện nghĩa vụ"* (vá P3).
- **on_low_conf (vá R15):** entity rủi ro cao (CCCD, thẻ, số tài khoản) **không bao giờ log-only** — mask trước, khôi phục sau theo yêu cầu; entity khác: log.

### 2.5 Đệm tool-call & vòng đời segment (chi tiết code)

- Delta `tool_calls[].function.arguments` được **đệm riêng** tới khi JSON hoàn chỉnh rồi mới quét và phát — tránh đúng lỗi APISIX tự thừa nhận (*"tool-call arguments themselves are not sent to Lakera"*).
- Verdict theo segment: `allow` (phát) · `redact` (phát bản đã mask) · `sever` (dừng, deny frame) được tính từ findings của segment + state phiên.
- Kiểm byte-compat bằng **SDK thật** (Python/JS/LangChain), không chỉ curl: `[DONE]`, `include_usage` không mất (QĐ-C10), frame deny parse được như refusal.

### 2.6 Ngân sách độc lập: đường nhanh (p95) ≠ trần timeout (vá #2)

Hai khái niệm **tách hẳn** (trước đây bị trộn — B/C nói "<100 ms input, <150 ms output" trong khi A đặt timeout F2 150 ms / F3 1.500 ms):

| Khái niệm | Định nghĩa | Số hiện có | Trạng thái |
| --- | --- | --- | --- |
| **Ngân sách đường nhanh** (hot path) | p50/p95 **độ trễ THÊM** của F1 + (F2 khi luật chạm) trên một segment, đo trên CPU máy này | Mốc tham chiếu ban đầu: <100 ms input / <150 ms output — **là mốc, không phải cam kết** | `[cần đo — M0]`; chốt sau khi có bảng p50/p95 thật |
| **Trần timeout** (hard) | Thời gian tối đa 1 detector được chạy trước khi bị cắt (breaker) | F1 **20 ms** · F2 **150 ms** · F3 **1.500 ms** | Giữ; nhưng F2 150 ms có thể **phải nới** nếu M0 cho thấy PG2-86M CPU chậm hơn nhiều (92,4 ms/512 tok **trên A100** — `risk-taxonomy-2026.md` §4.2) |
| **F3 tư thế** | **Async, ngoài hot path**: verdict của judge áp cho *lượt/segment sau* hoặc cho phân tích offline; response hiện tại không chờ judge | Judge chỉ chạy trong dải mơ hồ (0,3 ≤ score < 0,8) + theo lịch segment | Chốt — tránh cộng dồn >1,5–2 s/lượt (gateway floor ~430 ms — `jev-model.md` §3.7) |

**Ghi rõ trong plan:** các số ngân sách **phải đo ở M0 trước khi cam kết**; nếu F2 CPU vượt p95 mục tiêu → phương án đã định trước: (a) ONNX + quantization + model nhỏ (`plugin-architecture.md` §1.A); (b) F2 chỉ chạy trên segment "chạm luật" + lịch thưa hơn — cả hai đều có sẵn trong tài liệu nghiên cứu.

### 2.7 Fail-mode theo trạm (+ chống treo, + chống oracle)

| Trạm | Fail-mode mặc định | Lý do | Đối chiếu thị trường (ta chọn KHÁC) |
| --- | --- | --- | --- |
| 1 INPUT | **fail-closed** (lỗi có cấu trúc, không gửi model) | Điểm sớm nhất, rẻ nhất; thử lại được | Portkey `Deny FALSE` (request vẫn gửi, HTTP 246); Cloudflare: lỗi ⇒ *"request will proceed without evaluation"*; APISIX `fail_open: true` |
| 2 CONTEXT | **fail-open + log** (nhánh luật tất định đã match thì fail-closed) | Cách ly sai 1 chunk RAG phá câu trả lời đúng (utility 15–20%); trạm 3 còn chốt cuối | Cùng nhóm trên |
| 3 OUTPUT (non-stream) | **fail-closed** | Response sinh xong — chặn/mask không "phí" gì | NeMo `stream_first: False` style |
| 3 OUTPUT (stream) | **fail-buffered**: dừng phát tiếp, chuyển đệm; không kịp quét ⇒ kết stream bằng frame lỗi | Theo draft spec `agent-hooks`: *buffer until combined verdict permits (MUST) hoặc khai `buffered_output:false`* | APISIX mặc định `fail_open: false` = buffer |

- **Chống treo (bắt buộc, vì fail-closed là vũ khí DoS):** timeout cứng mỗi detector + **circuit breaker** (fail liên tiếp N lần ⇒ tắt T giây, đếm trong metrics); nối **cap đầu vào B13 ↔ cap log/queue**; có soak test ở M6 (vá M3).
- **Chống oracle (vá R16):** phía client chỉ thấy **2 lớp mã** (violation / guard-unavailable) — mọi chi tiết (rule_id, score, ngưỡng, họ đồng thuận) **chỉ trong log**; đo jitter độ trễ; thêm ô fuzz ngưỡng (~50 request biến thiên quanh ngưỡng) vào M6. Đây là bề mặt oracle **có chủ đích tối thiểu** — cần 2 lớp mã để phân biệt "chặn do vi phạm" vs "chặn do sự cố"; chi tiết hơn là không an toàn.

### 2.8 Chống bypass ở tầng API (vá #6 + R3/R4/R9)

| Đường | Chốt xử lý v1 | Ghi chú |
| --- | --- | --- |
| `POST /v1/completions` (legacy) | **ĐƯỢC KIỂM qua đủ 3 trạm** (field `prompt` — string hoặc array — đi cùng pipeline; completion đi qua trạm 3). **Không** passthrough im lặng (thay đổi so với draft-A bước 0) | Chặn hẳn cũng là phương án hợp lệ nhưng phá tương thích client cũ; chọn "kiểm" vì rẻ và không mất tương thích |
| Các path `/v1/*` khác | **Whitelist khai báo**: `/v1/models` passthrough (không nội dung); path lạ → **lỗi có cấu trúc (404/400 + mã)**, không forward mù | Test "API surface" liệt kê mọi path được chuyển tiếp (M4) |
| `messages[]` dạng lạ | **Schema strict (pydantic)**: `content` dạng mảng part → quét mọi `text` part, part ảnh/audio → **đánh cờ + log** (unsupported, khai báo §1.4-3); `role` lạ (`developer`, `function`, …) → **từ chối có mã** (hoặc map về role tương đương đã khai báo — chọn từ chối ở v1); `n>1` → **quét mọi `choices[*]`**; `stream` không phải bool / `stream_options` lạ → chuẩn hoá hoặc từ chối có mã | Chống "silent failure" (bài học `nghien-cuu/N4` §(ii)); test ma trận hình dạng request ở M4 |
| `tools` schema đổi giữa phiên | Log + đánh cờ phiên (tool descriptor drift) | §3.4 |
| **Session key do client gửi** | **Registry phiên phía server**: `sid = HMAC(k_srv, H(system_prompt_đầu) ‖ H(tin_nhắn_đầu) ‖ identity_hint ‖ model)`. Header `x-session-id` của client chỉ là **gợi ý** — lệch fingerprint thì fingerprint thắng. Detect reset: cùng `session_family` xuất hiện với `sid` mới trong cửa sổ thời gian → liên kết lại + gắn cờ "suspected reset" | Attacker đổi system prompt/tin nhắn đầu mỗi lượt ⇒ mỗi request là "phiên mới" — registry vẫn gom theo `session_family`; **giới hạn đo được**: không có định danh app do server cấp thì không đảm bảo 100%; test K2 "cắt arc thành nhiều session_id cùng user" (M4/M5) **đo residual này và công bố** |
| Client gọi thẳng 9router | **Không chặn được** (ranh giới, §1.4-2); giữ arm C0 để **định lượng khoảng cách có/không guardrail**; khuyến nghị ngoài sản phẩm: egress policy/keys | Nói ở phần "tính thực tiễn" của báo cáo, không giấu trong phụ lục |

### 2.9 Đóng gói & vận hành (chốt theo QĐ-A §6 + review)

| Hạng mục | Chốt v1 | Ghi chú |
| --- | --- | --- |
| Chạy | Python trực tiếp (`uv venv` + `uv run`); **3 venv tách** (attack / data / pii — bài học gliner↔datasets, §4.4) | Dockerfile + compose = artefact M6 (daemon chưa bật — QĐ-C9) |
| Log | **JSONL append-only = nguồn sự thật** (+hash-chain §4.5); SQLite = chỉ mục dựng lại từ JSONL | 1 file/ngày; rotation + retention enforce bằng code |
| Trang log | Trang tĩnh `fox logs report --out report.html` trước; `/logs` live nếu còn thời gian | Viewer có autoescape + CSP + strip control/bidi (R7) |
| Gói pip | `pyproject.toml` + console-script `fox-proxy`, cài từ M1 | Publish PyPI = tuỳ chọn |
| Config | `fox-guardrails.yaml` + env override; **ghi hash config vào mọi record** | Config là biến của thực nghiệm (manifest) |

*Module/file dự kiến:* giữ nguyên danh sách của draft-A §8 (`src/fox_guardrails/**` 24 mục + `tests/`) và **bổ sung tầng harness** (vá T10): `experiments/run_matrix.py` · `experiments/analyze.py --replay-policy` · `experiments/manifests/` · `logs/` · `experiments/generate_vi.py` (sinh/dịch dữ liệu VI, seed cố định) · `experiments/canary.py`.
