# FOX-Guardrails — Plan triển khai (bản chốt)

> **Bàn giao duy nhất:** `docs/plans/plan.md` · Ngày chốt: **2026-10-18** · Trạng thái: bản cuối, hợp nhất 3 nháp (`draft-A-system.md`, `draft-B-detection.md`, `draft-C-experiments.md`) + 2 phản biện (`review-1-consistency.md`, `review-2-adversarial.md`, đều ở `hermess/plans/`).
> Mọi số kèm nguồn dạng *tên file* trong `hermess/` (`research/`, `nghien-cuu/`, `notes/`, `evidence/`). Cột **tầng** theo quy ước `risk-taxonomy-2026.md`: `[SƠ CẤP]` nguồn gốc/đo thật · `[preprint]` arXiv 25xx/26xx chưa bình duyệt · `[THỨ CẤP]`/`[BLOG-VENDOR]` gián tiếp. `nghien-cuu/N4-phuong-phap-danh-gia.md` (dòng 104) tự cảnh báo: các số "ASR correction", "judge recall 0.06–0.65", "18,2 pp MDD" đều từ **preprint 2026**.
> Quy ước tên (chống lỗi nhầm đã xảy ra thật trong nháp B): **arm thực nghiệm = C0–C5** · **mục sổ quyết định = QĐ-Cn** · **ô ca = K1–K6** · **mốc = M0–M6**.

---

## 0. Tóm tắt điều hành

### 0.1 Sản phẩm

**Plugin guardrails dạng proxy OpenAI-compatible** (QĐ-A1, QĐ-A2): chèn giữa client và model, **1 điểm chặn** cho mọi app dùng OpenAI SDK:

```
client (SDK OpenAI / LangChain / curl)
   base_url = http://127.0.0.1:20129/v1        ← proxy (sản phẩm của đồ án)
        ▼
[TRẠM 1 INPUT] → [TRẠM 2 CONTEXT] → forward → [TRẠM 3 OUTPUT] → client
        ▼
   9router 127.0.0.1:20128/v1 (36 model; QĐ-C1, QĐ-C12)
```

3 trạm (input/context/output) × 3 họ phát hiện (F1 luật+Unicode · F2 classifier OSS · F3 LLM judge) × 4 mức can thiệp (block/mask/log/escalate); log **JSONL là nguồn sự thật** + SQLite làm chỉ mục; chạy **Python trực tiếp** trong lúc phát triển (v1), Dockerfile/compose là artefact bàn giao cuối.

### 0.2 Phạm vi v1 (chốt)

- **Làm:** (a) prompt injection **trực tiếp và gián tiếp** ở tầng văn bản (EN + VI, kể cả tầng ký tự: homoglyph/zero-width/tags/mã hoá/biến thể VN); (b) **PII** định danh VN + EN ở cả 3 trạm (mặc định **mask**); (c) đo lường trung thực: ASR, TPR@FPR, over-defense, độ trễ, độ rò, độ bền của judge, độ bền của chính guardrail (fuzz ngưỡng).
- **Hoãn khỏi v1 (không hứa — vá #1):** nhóm `harmful/toxicity` (nháp A §3.2 có `harmful.default: block` nhưng B/C **không có detector nào**) và **egress markdown sanitize** (`egress_md`) — cả hai đưa vào mục "ranh giới" + backlog v2; plan **không** tuyên bố mặc định block nội dung độc hại.
- **Ngoài tầm với của proxy (khai báo, không hứa — mục 1.4):** trạng thái phía server, client gọi thẳng provider, cross-modal, reasoning trace, log/telemetry/kênh phụ, tool thực thi nội bộ app, memory/RAG poisoning.

### 0.3 Ba khoảng trống đồ án chiếm

| # | Khoảng trống | Bằng chứng "đang trống" | Đóng góp dự kiến |
| --- | --- | --- | --- |
| 1 | **Tiếng Việt + tầng ký tự**: không có benchmark/normalizer chuẩn cho injection & PII tiếng Việt; các họ né tránh tầng ký tự chưa ai đo trên VI | *"chưa xác định được benchmark/cuộc thi công khai chuyên về prompt injection hoặc PII-leak cho tiếng Việt"* — `vietnamese-evasion-and-law.md` §B.4; LlamaGuard giảm DSR **9%** / jailbreak đa ngữ **18%** trên 10 ngôn ngữ ĐNÁ gồm VI (SEALGuard) — §B.2; demo trên máy: base64/teencode/VI có dấu **0/5 phép biến đổi nào bắt** — `evidence/homoglyph-demo-tren-may.txt` | Pipeline 13 bước + bộ test A1–A9 tiếng Việt + recognizer định dạng VN + **số recall-theo-lớp kèm FPR** (số chưa ai có cho VI) |
| 2 | **Guardrail chỉ có nghĩa khi "đứng giữa"**: sản phẩm thị trường tự thừa nhận không enforce / bỏ qua streaming / không kiểm tool-args | Cloudflare REST *"evaluates the response and logs the result, but does not enforce it"*; TrueFoundry *"output guardrails are skipped for streamed responses"*; Bedrock async *"PII will pass through unmasked"*; APISIX *"tool-call arguments themselves are not sent to Lakera"* — `streaming-guardrails.md` §b.2/§b.3/§b.8/§c.4; Portkey `Deny FALSE` (HTTP 246) — `plugin-architecture.md` §1.B | Proxy **chặn thật** ở cả 3 trạm: deny-frame chuẩn SSE OpenAI, đệm theo câu + đệm tool-call arguments, fail-buffered khi lỗi |
| 3 | **Đo lường trung thực**: hiện **0 số tự đo** (draft-C tự khai); số công khai bị bơm bởi benchmark ≠ phân phối thật | PG2 công bố AUC 0,998 nhưng LODO AUROC chỉ **0,757**, obfuscation còn **0,0207** (`risk-taxonomy-2026.md` §4.4, `[preprint]`); judge recall **0,06–0,65**, đổi judge lệch tới **82 điểm %**, wrapper lật **57–100%** (`papers-pii-and-eval.md` §(ii) + `nghien-cuu/N4-*.md` dòng 76 — arXiv 2606.25487); **65,3%** bài không báo variance (N4) | Giao thức: pre-register so sánh chính, N=20/cell cho ô quyết định, Wilson CI, kiểm chứng judge bằng ≥150 mẫu gán tay + 2 judge độc lập, đối chứng bằng garak/PyRIT + dữ liệu người thật, khai báo trần/sàn |

### 0.4 Kết quả kỳ vọng (đo được; không hứa số trước khi đo)

1. **Δ ASR** giữa C0 (không guardrail) và C3/C4 (guardrail) trên K1+K2, kèm CI + số lần lặp — endpoint chính #1.
2. **FPR hệ trên tập lành** (thường + benign-chứa-từ-khoá) — endpoint chính #2; **mốc tham chiếu thiết kế** (không phải kết quả): ≤5% (đối chiếu Lakera **5,7%** trong Palit — `plugin-architecture.md` §2.2; production 5–15% — `nghien-cuu/N3-*.md`).
3. **Số tự đo đầu tiên** cho VI & tầng ký tự: recall theo từng lớp né tránh + độ trễ CPU thật + TTFT theo `stream_mode` (tài liệu công khai **không có** số TTFT của bất kỳ guardrail streaming nào — `streaming-guardrails.md` §d).
4. **Artefact bàn giao:** proxy chạy được (C0 pass-through + guardrail), bộ test T1–T5, log JSONL có hash-chain + verify, trang log tĩnh, bộ dữ liệu + manifests tái lập, báo cáo theo khung chỉ số mục 6.
5. **Các tuyên bố trần/sàn phải có:** pattern matching có trần **35–45%** trên indirect injection tinh vi (`risk-taxonomy-2026.md` §4.4); không defense nào đạt 0% ASR (sàn ~15%); mọi defense mất **15–20%** utility (AgentDojo). Recall lớp Unicode **tất định** kỳ vọng ≥90% (vì tất định — sẽ kiểm bằng T1); recall **tổ hợp chỉ báo cáo, không đặt mục tiêu**.

### 0.5 Ràng buộc máy (đã đo trên máy này)

| Hạng mục | Số thật | Hệ quả |
| --- | --- | --- |
| GPU | GTX 1650 **4GB** VRAM; torch đang là **2.14.1+cpu, CUDA=False** (`attack-tooling-install-check.md` §1) | **v1 chạy CPU-only** — không cài wheel CUDA (~2,5GB); GTX 1650 để dành v2 (QĐ mục 9-Q13) |
| Đĩa | **C: còn 28GB (90% đầy) · D: còn 143GB** (đo `df -h` + `Get-PSDrive`, số QĐ-C7 "146GB" đã cũ) | Toàn bộ cache/dữ liệu/log đặt trên **D:** (mục 4.4); C: **không** dùng cho cache |
| Docker | Daemon **chưa chạy** (QĐ-C9) | Phát triển bằng `uv`/Python trực tiếp; Dockerfile = artefact cuối |
| Model | 9router `127.0.0.1:20128`, **36 model**, nhóm `oc/*` JSON / `ag/*` SSE (QĐ-C1/C2); **không SLA, rate limit chưa đo** | Pin model + canary + probe rate limit ở **M0** trước khi cam kết lịch chạy |
| Path | Tool native không dịch `/d/...`; **luôn dùng `D:/create/...`** (QĐ-C13) | Mọi lệnh trong phụ lục 10.2 theo dạng này |
| RAM | **chưa đo** (T14 của review-1) — việc của M0 | Ghi vào `logs/m0/machine.json` |

### 0.6 Sáu vá bắt buộc từ phản biện → vị trí áp dụng

| # | Vá | Áp ở |
| --- | --- | --- |
| 1 | Một nghĩa "mặc định can thiệp" duy nhất: PII mask cả 3 trạm; block chỉ bởi luật tất định hoặc quorum ≥2 họ; harmful/toxicity + egress → hoãn v1 | §2.4, §3.5 |
| 2 | Tách **ngân sách đường nhanh (p95)** khỏi **trần timeout**; F3 **async, ngoài hot path**; số phải đo ở M0 | §2.6, §6.5, §7-M0 |
| 3 | Sửa ước lượng call: judge **theo segment**, +sinh/dịch dữ liệu VI (~400–800), probe rate limit ở M0, **MVP gồm C3** | §5.4 |
| 4 | Tầng bằng chứng: N3/N4 ở `hermess/nghien-cuu/`; "wrapper lật 57–100%" thuộc N4/arXiv 2606.25487; ghi rõ số nào từ preprint 2026; agent-hooks là **draft spec** | §0 header, bảng số liệu các mục, §10.1 |
| 5 | Bảo vệ log: hash-chain, test chống rò raw, bảo vệ viewer, **salt (HMAC) cho `span_hash`** | §4.5, §2.9 |
| 6 | Khai báo xử lý bypass: `/v1/completions` **được kiểm** (không passthrough), `messages[]` lạ theo schema strict, **registry phiên phía server** | §2.8 |

---

## 1. Bài toán & phạm vi

### 1.1 Pain point có số

| # | Vấn đề | Số liệu | Nguồn · tầng |
| --- | --- | --- | --- |
| 1 | Indirect injection qua tool output/RAG là kênh chính | Injection đặt **cuối tool response**: ASR tới **70%**; có secondary detector giữa tool output và model: **<25% → 8%**; đánh đổi **15–20% utility**; **không defense nào đạt 0% ASR** (sàn ~15%) | `risk-taxonomy-2026.md` §4.1/§4.2/§4.4 · `[SƠ CẤP]` (AgentDojo, arXiv 2406.13352) |
| 2 | Bộ phát hiện mạnh nhất vẫn có trần khi phân phối thật lệch | PG2 86M: AUC **0,998** EN, recall@1%FPR **97,5%**, APR **81,2%**; nhưng **0,0207** dưới obfuscation, **AUROC 0,757** LODO; trần pattern InjecAgent DH-base **38,8%** (198/510) | `risk-taxonomy-2026.md` §4.2/§4.4 · `[SƠ CẤP]` + `[preprint]` (2510.01529, 2602.14161) |
| 3 | Bật block theo classifier mặc định phá trải nghiệm | Over-defense ở **cùng mức bắt 95%**: PG2 **40,1%** · PIGuard **44,0%** · Claude **52,2%**; cutoff 0,5 chỉ bắt **52,6%** (PG2) | `jev-model.md` §3.4 · bench cộng đồng |
| 4 | FPR thực địa của guardrail thương mại cao | Lakera FPR **54,9%** trên benign "jailbreak-shaped" (BELLS-O, 28 hệ thống); median FPR theo lớp **30,5%** vs **10,2%** | `nghien-cuu/N3-pain-point-cong-cu.md` (dẫn arXiv 2606.20668) · độc lập |
| 5 | Judge/decision model không dùng làm chốt được | Jev recall **82,9% → 3,88%** khi chèn "counterfeit policy"; câu lịch sự lật **147/200 (73,5%)** phiếu | `jev-model.md` §3.1/§3.8 · `[SƠ CẤP]` (Datadog, 123.805 request) |
| 6 | Kênh exfil qua markdown/ảnh | EchoLeak (CVE-2025-32711): CVSS **9,3, zero-click**; vượt redact link bằng reference-style `[text][ref]`; exfil bằng ảnh auto-fetch; vượt CSP bằng proxy trong allowlist | `risk-taxonomy-2026.md` §3.5 · `[SƠ CẤP]` |
| 7 | Tầng ký tự vẫn hạ được guardrail / lừa được người | Microsoft 03/09/2026: chiến dịch phishing chèn **1 ký tự U+E0020** giữa từ khoá; Chrome chỉ hiện Punycode cho **1.189/1.855** IDN homograph; **84%** người thử không nhận ra biến thể Amazon | `notes/quyet-dinh.md` C15 · `[THỨ CẤP→SƠ CẤP]` tổng hợp |
| 8 | Đa lượt nhân ASR | Crescendo (GPT-4): ASR nhị phân **98%**; với ngân sách 1 lần thử **40,0/31,7/28,0%** → 10 lần thử **80,4/70,9/77,0%**; X-Teaming **94,3%** (GPT-4o) | `multiturn-attacks-part1.md` §; `multiturn-attacks-part2.md` · `[SƠ CẤP]` |
| 9 | Ngôn ngữ ít nguồn lực né được guardrail | Dịch prompt sang tiếng ít nguồn lực: ASR GPT-4 **<1% → 79%**; LlamaGuard **−9%/+18%** DSR trên ĐNÁ (gồm VI) | `vietnamese-evasion-and-law.md` §B.1/§B.2 (arXiv 2310.02446, 2507.08898) · `[SƠ CẤP]` |
| 10 | Rò PII qua output là kênh thật | PrivacyLens: GPT-4 leak **25,68%**, Llama-3-70B **38,69%**; log ghi nguyên prompt/response = lưu mọi PII đi qua | `draft-C` §3.1C (PrivacyLens) · `risk-taxonomy-2026.md` §3.2 · `[SƠ CẤP]`+`[THỨ CẤP]` |

### 1.2 Input / output của hệ thống

**Input (mặt API):** request OpenAI-compatible gửi tới proxy —
`POST /v1/chat/completions` `{model, messages[], stream?, stream_options?, tools?, n?, temperature, …}`; và `POST /v1/completions` (legacy — **được kiểm**, mục 2.8); `GET /v1/models` (chuyển tiếp khai báo). Ngoài ra: config `fox-guardrails.yaml`, dữ liệu test, manifest thực nghiệm.

**Output:**
1. Response đã qua 3 trạm: cho qua (allow) · **mask** (thay span PII bằng placeholder) · **block** (JSON error có cấu trúc / deny-frame SSE) · **escalate** (ghi hàng đợi + hành động mặc định an toàn).
2. **Log JSONL** (nguồn sự thật) + SQLite (phiên, escalations) + metrics — schema ở 10.3.
3. Trang log tĩnh (`fox logs report`) + lệnh điều tra `fox logs why --record <id>` (tiêu chí nghiệm thu ở §3.6).

### 1.3 Ranh giới phạm vi

- **Trong:** văn bản đi qua proxy trên 2 chiều; định danh PII theo định dạng VN+EN; tấn công EN+VI; đo lường; proxy + test + log + báo cáo.
- **Ngoài (không hứa):** harmful/toxicity đầu ra (v1), egress sanitize markdown (v1 — dù EchoLeak là động lực: ghi rõ động lực vẫn tồn tại, chỉ chưa làm), cross-modal, fine-tune model (v2+), app demo RAG đầy đủ (tuỳ chọn — harness tự viết là client chuẩn), UI/UX sản phẩm.
- **Tư thế khoa học:** "đo được + khả thi", không claim "sản phẩm dùng được"; mọi tuyên bố thiếu số phải có nhãn `[cần đo — M0/Mx]`.

### 1.4 Cái gì KHÔNG chặn được ở tầng proxy (khai báo tường minh)

| # | Điểm mù | Vì sao proxy không thấy | Bằng chứng |
| --- | --- | --- | --- |
| 1 | **Trạng thái phía server** (vector DB/RAG store, memory persistence, DB kết quả tool) | Proxy chỉ thấy `messages[]`; kho dữ liệu và tool chạy trong app; `/v1/embeddings` thậm chí **không hỗ trợ** qua router (QĐ-C11) | `draft-A` §1.3; `risk-taxonomy-2026.md` §4.3(a) |
| 2 | **Gọi thẳng provider** (đổi `base_url` 1 dòng → `127.0.0.1:20128`) | Request không đi qua proxy; giới hạn kiến trúc, không phải lỗi cấu hình | `plugin-architecture.md` §1.B; `draft-A` §5.2 |
| 3 | **Cross-modal** (payload trong ảnh/audio/video) | Proxy v1 chỉ kiểm text; part ảnh bị đánh cờ "không hỗ trợ" nhưng không đọc | `risk-taxonomy-2026.md` §4.3(b) |
| 4 | **Reasoning trace** mã hoá/opaque | Chỉ có ciphertext; Leaky Thoughts đo rò **24,7%–49,5%** qua trace | `risk-taxonomy-2026.md` §3.1/§4.3(c) |
| 5 | **Log/telemetry tầng sau + kênh phụ** (timing, độ dài token, logprob, cache-hit) | Ngoài ranh giới proxy | `risk-taxonomy-2026.md` §4.3(a), §4.1 hàng 7 |
| 6 | **Tool thực thi nội bộ app** (đọc file, gửi mail) khi kết quả không quay lại `messages` | Proxy chỉ thấy arguments; đây là **điểm mù công nghiệp** (APISIX cũng tự nhận) | `streaming-guardrails.md` §c.4; `draft-A` §5.2 #3 |
| 7 | **Memory/RAG poisoning sau khi đã lọt** | Injection sống trong memory/kho RAG qua nhiều phiên; ASR **90% ở tỉ lệ đầu độc 0,0002%** | `risk-taxonomy-2026.md` §4.1 |
| 8 | **Chuỗi agent/inter-agent, excessive agency, rogue agent** | Proxy chỉ thấy 1 luồng HTTP; 60% tổ chức không kill được agent sai `[BLOG-VENDOR⚠]` | `risk-taxonomy-2026.md` §4.1/§4.3 |

**Hệ quả viết báo cáo:** các mục này vào thẳng phần "ranh giới", kèm câu chốt: *biện pháp khả thi cho #2 nằm ngoài sản phẩm (egress policy/keys); phần còn lại cần kiểm ở tầng app/sandbox — không tính vào điểm số của guardrail.*
