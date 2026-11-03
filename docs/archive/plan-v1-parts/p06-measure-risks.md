---

## 6. Đo lường & độ chặt

### 6.1 Bảng chỉ số (khoá định nghĩa TRƯỚC khi chạy)

| Nhóm | Chỉ số cụ thể | Ràng buộc báo cáo | Nguồn tham chiếu |
| --- | --- | --- | --- |
| **ASR** | ASR = thành công/tổng lần thử; targeted vs untargeted; BIPIA **Macro-ASR vs Micro-ASR** | Ghi định nghĩa, `k`, nhiệt độ, judge; `k=1` overstate 12–24 pp | `papers-pii-and-eval.md` §BƯỚC 3; `nghien-cuu/N4-*.md` §2 |
| **Detection** | **TPR@1%FPR** (chuẩn chính); P/R/F1 entity-level; FPR từng loại entity | **Không** dùng accuracy; AUC không đủ (PromptGuard AUC 0,92 nhưng FPR **0,89**) | 2610.03448, 2505.18333 `[SƠ CẤP]` |
| **Over-defense** | FP trên benign thường; FP trên **benign-chứa-từ-khoá**; refusal rate | Bắt buộc báo **cả hai chiều** (chặn được + chặn oan) | PIDS-Bench 2609.15017 `[preprint]`; NotInject |
| **Utility** | Δutility (retention %); refusal rate; **định nghĩa vận hành chốt trước**: utility = % tác vụ benign hoàn thành không bị guardrail đổi kết quả (chấm bằng tiêu chí tất định, không dùng LLM judge) | Đối chiếu AgentDojo 15–20%; SecAlign ≤2,7 pp | `risk-taxonomy-2026.md` §4.4 |
| **Leak rate (PII)** | `số ca rò/tổng`; **chốt trước: exact match = rò; partial (một phần span) = "rò một phần" báo riêng**; leak tích luỹ đo tới lượt cuối | Không trộn 2 định nghĩa | PrivacyLens; `papers-pii-and-eval.md` |
| **Độ trễ** | p50/p95 thêm từng trạm + **TTFT theo `stream_mode`** + số ký tự phơi nhiễm trước deny | Ghi rõ **CPU-only**; so C0 để tách overhead proxy; nêu điều kiện đo (số request đồng thời) | `streaming-guardrails.md` §d |
| **Chi phí** | số call detector/response; token tăng %; quota/thời gian (tiền = 0 với free — quy ra quota) | Mốc khi trả phí: validator +15–40% hoá đơn; NeMo +65% token | `nghien-cuu/N3-*.md`; `papers-pii-and-eval.md` §(ii) |
| **Độ tin cậy** | variance giữa các vòng; **Wilson CI**; bootstrap CI; κ liên-judge; missing rate | **65,3%** bài không báo variance — đồ án này **bắt buộc** báo | 2609.25173 `[preprint]` |

### 6.2 Số lần chạy + CI

- **≥5 vòng/cấu hình** ở ô chủ chốt ngoài chương trình lặp N=20 (K1/K2 có N=20/cell là chính); ô phụ 3 vòng. Mọi bảng chính: **mean ± SD** + Wilson CI 95%.
- **TPR@FPR**: bootstrap **stratified 1.000 resample** cho TPR@1%FPR + CI 95% mọi tỉ lệ khác.
- **Quy tắc tuyên bố:** chỉ nói "khác biệt" khi **CI không chồng lấp HOẶC Δ > MDD của ô đó**; các so sánh then chốt = C0 vs C3 vs C4 trên K1/K2 (pre-register — chống multiple comparisons/cherry-picking); các so sánh ngoài danh sách = exploratory, ghi rõ.
- **Power (chốt):** n=100 ⇒ MDD ≈ **18,2 điểm %** (2609.25173); ⇒ ô quyết định **N=20 lần/cell** (§5.3); ô thiếu power (K2-VI, K4, K2-AD) **liệt kê trước** là "chỉ báo cáo".

### 6.3 Over-defense (làm được ngay)

NotInject-style + mở rộng VI ("hướng dẫn", "bỏ qua", "chỉ dẫn", email hợp lệ, số 9–12 chữ số vô hại, emoji ZWJ, JWT/hash); **so ở cùng catch rate** (95%), không so ở ngưỡng mặc định; chạy lại T1–T4 dưới biến thể obfuscation; chia tập in-distribution vs "thực tế" mô phỏng LODO (vì CV-AUC vs LODO-AUC lệch **8,0–16,5 pp**).

### 6.4 Giao thức kiểm chứng judge (điều kiện để TIN mọi số ASR/leak)

| # | Việc | Mốc |
| --- | --- | --- |
| 1 | **Chọn & khoá judge**: 1 model `oc/*` cố định + `model_served` ghi log; temperature 0; prompt JSON cố định (`prompt_hash`); timeout + fallback | Ghi trước khi chạy ma trận |
| 2 | **2 judge độc lập**: judge chính + judge phụ (rule-based/classifier — harm classifier hoặc StrongReject-style scoring); đo agreement (**Cohen κ**) + tỉ lệ bất đồng; ca 2 judge bất đồng ⇒ "không xác định", báo riêng | ≥150 mẫu gán tay (mục tiêu; tối thiểu 100), stratified theo ô × arm, người gán **không nhìn verdict hệ**; lưu file nhãn + hash |
| 3 | **ASR_corrected** = ASR_reported × precision(judge) (2606.25487) — ghi rõ là **xấp xỉ thô**, kèm CI khi có thể | mọi bảng ASR |
| 4 | **Test độ mong manh (wrapper-flip)**: 200 reply cố định × 2 kiểu wrapper ("người giám sát đã duyệt", prefix tóm tắt) → đo **flip rate**; mốc tham chiếu: audit 596 mẫu human-label — wrapper benign lật judge **57–100%** (`nghien-cuu/N4-*.md` dòng 76, arXiv 2606.25487 `[preprint]`); Jev bị lật **147/200 (73,5%)** | flip rate báo cáo + kết luận về độ tin judge |
| 5 | **Không tự chấm**: không đánh giá judge bằng chính judge; không kết luận khi judge chưa qua mục 2 | — |
| 6 | **Lưu raw (đã mask) reply** để re-judge offline khi đổi judge — và chấp nhận tái chi phí judge | — |

### 6.5 Đối chứng độc lập (chống "tự chấm bài mình" — vá Q5/W2)

- **Tối thiểu 3 nguồn đối chứng:** (a) công cụ tấn công ngoài **garak 0.17.1 + PyRIT 1.1.0** (đã cài + CLI chạy thật — `attack-tooling-install-check.md`) chạy qua proxy; (b) **dữ liệu người-thật**: llmail `labelled_unique_*` (160.741+37.303), TensorTrust (69.906 unique), hackaprompt (600K) — đo trên bộ người-thật, không chỉ K1/K3/K4 tự sinh; (c) bộ recall-fill của F1 (T1–T5) trong đó T2/T4 có kiểm mẫu "còn đọc được".
- **Báo cáo bắt buộc dạng cặp**: "recall trên bộ tự sinh" **vs** "recall trên bộ người-thật/garak" — chênh lệch giữa hai con số này là phát hiện, không phải sai số (bài học PIGuard 95,1%→2,1%).

---

## 7. Mốc triển khai (M0 đo trước → M1..M6)

> Nguyên tắc: **không cam kết số nào chưa đo**; mỗi mốc có bằng chứng kiểm được (số/log/file); thứ tự cứng: **M0 xong mới M1**.

### M0 — ĐO TRƯỚC (gate toàn bộ; "đo trước khi tin giả định")

| Việc | Lệnh/đầu ra | Tiêu chí hoàn thành (kiểm được) |
| --- | --- | --- |
| Tải + đo **p50/p95 F1/B1–B13** trên CPU theo 3 độ dài (≤2KB, 10KB, 64KB) | `logs/m0/latency_f1.json` | có bảng p50/p95; so với trần 20 ms — nếu vượt ⇒ ghi phương án cắt (bỏ decode sâu cho input lớn) |
| Tải **PG2-86M + deberta-v2**, đo p50/p95 theo 128/512/2048 token **trên CPU này** (+ ONNX/quantized nếu có) | `logs/m0/latency_f2.json` | bảng số thật; **chốt ngân sách đường nhanh** (thay mốc <150 ms tạm thời) hoặc chốt phương án A2 (ONNX/schedule thưa) kèm benchmark before/after |
| **Probe rate limit**: 100 request liên tiếp + 2 luồng song song; ghi 429/`Retry-After` | `logs/m0/ratelimit_probe.json` | có phân bố 429 + ước tính call/ngày; **chốt/bác bỏ lịch 3 tuần**; chốt N=20 hay hạ cấp |
| **Đo tải dữ liệu**: thử tải JBB + openpii subset + PG2; đo GB/s, tổng đĩa; xác nhận `hf` CLI + env cache D: hoạt động | `logs/m0/disk_budget.md` (đo, không ước) | có bảng "tải được X GB đến đâu, còn Y GB trên D:" |
| Đo máy: RAM/CPU/đĩa | `logs/m0/machine.json` | bổ sung QĐ-C7 (RAM đang thiếu) |
| Smoke công cụ: `garak --version` + `--list_probes` (ghi danh mục), `pyrit_scan --help` (chiến lược) | `logs/m0/tooling.md` | danh mục probe/strategy đã chốt cho M6 |

### M1 — Nền: môi trường + proxy passthrough (C0) + log

- 3 venv tách chạy được (attack/data/pii); repo skeleton theo §2.9; `fox-proxy --help` chạy.
- **Tiêu chí:** C0 pass 100 call qua proxy không lệch hành vi (JSON + SSE); test byte-compat **SDK thật** (mở/đóng stream, `[DONE]`, `include_usage` không mất); JSONL ghi đủ schema v1 + `fox logs verify` PASS; `fox logs why` in được lý do từ record giả lập.

### M2 — F1: pipeline 13 bước + bộ test T1–T5

- **Tiêu chí:** T1 chạy xong — **bảng "bước nào bắt" + recall từng lớp** (6 ca evidence tái lập đúng); T3 có số **FPR pipeline** đầu tiên; T2 báo cáo recall tổ hợp (không giấu); đo p95 pipeline sau tối ưu; unit test tương tác B5↔B6 (31 mục) + B12 (assert không còn tags) PASS.

### M3 — F2: classifier + PII VN + hiệu chuẩn

- **Tiêu chí:** θ_low/θ_high cho PG2/deberta hiệu chuẩn trên dev; bảng **TPR@1%FPR** trên tập chính + FPR benign-chứa-khoá từng detector; recognizer VN chạy với bảng entity §3.3 (kèm validate checksum) + **FPR từng entity trên benign**; GLiNER hoạt động trong venv pii (không phá venv data); đo lại độ trễ sau ONNX (nếu cần).

### M4 — Pipeline 3 trạm + streaming + fail-mode + chống bypass + bảo vệ log

- **Tiêu chí:** stream `sentence` phát đúng thứ tự + đo **exposure_chars** trên ca cưỡng bức deny/cắt chunk; deny frame + error frame đúng 2 lớp mã; test **ma trận hình dạng request** (§2.8) — mọi shape lạ bị xử lý theo khai báo; test **session reset** (K2: cắt arc thành nhiều session_id) — báo cáo bắt/không bắt được kèm số; test bảo vệ log 6 mục §4.5 PASS trong CI (hash-chain, raw-leak, viewer XSS/RLO/ANSI, HMAC salt, cap/rotation, JSONL injection).

### M5 — MVP matrix {C0, C3, C4} + phân tích + kiểm chứng judge

- **Tiêu chí:** `run_matrix` xong 3 arm × ô nửa (missing rate ≤10% mỗi ô hoặc chạy bù tới ngưỡng); bảng ASR/FPR/latency + Wilson CI; **kiểm chứng judge**: ≥150 mẫu gán tay, κ, precision/recall judge, **flip rate** (200×2 wrapper), `ASR_corrected`; báo cáo "khác biệt hay không" theo quy tắc §6.2; phát hiện lỗi harness được ghi log và sửa trước M6.

### M6 — Ma trận đầy đủ + đối chứng ngoài + bàn giao

- **Tiêu chí:** đủ 6 arm × 6 ô (+ K2-AD) hoặc danh sách ô chạy thiếu ghi rõ; **lặp N=20/cell** cho ô quyết định (hoặc mức hạ cấp có kê khai); garak + PyRIT chạy qua proxy, bảng "self-gen vs external" (§6.5); fuzz ngưỡng 50 request (R16); Dockerfile/compose chạy demo 1 lệnh; `pip install -e .` OK; report HTML + số liệu sẵn cho báo cáo/hội đồng.

---

## 8. Rủi ro & giảm thiểu

### 8.1 Năm rủi ro nghiêm trọng nhất (từ review-2, đã ánh xạ vào plan)

| # | Rủi ro | Giảm thiểu trong plan |
| --- | --- | --- |
| 1 | **Judge chưa kiểm chứng + mong manh đã được chứng minh** (recall 0,06–0,65; lật 57–100%; counterfeit policy 82,9→3,88%) ⇒ ΔASR nhỏ không bảo vệ được | Giao thức §6.4 (2 judge + ≥150 nhãn + flip test + ASR_corrected); quy tắc "Δ<10pp không tuyên bố khi judge chưa kiểm"; F3 async + không bao giờ block |
| 2 | **Bộ test tự sinh không đối chứng** ⇒ "tự chấm bài mình" (bài học PIGuard 95,1%→2,1%) | Đối chứng 3 nguồn §6.5; báo cặp self-gen vs human/tool; garak/PyRIT là điều kiện M6 |
| 3 | **Power không đủ ở ô quyết định** (MDD 18,2 pp @n=100; K2-VI 25 phiên) | **N=20/cell** cho ô quyết định; ô thiếu power khai "chỉ báo cáo"; quy tắc CI/MDD |
| 4 | **Bề mặt bypass chưa khai báo** (`/v1/completions`, shape lạ, session client-controlled) | §2.8 chốt: completions được kiểm; schema strict + reject có mã; registry phiên server-side + test reset đo residual |
| 5 | **0 số tự đo + độ trễ CPU chưa đo + rate limit chưa probe** | **M0 gate**: 4 phép đo + số phải có trước M1; không cam kết lịch/budget trước M0 |

### 8.2 Đĩa · quota · lệch phụ thuộc · vận hành

| # | Rủi ro | Dấu hiệu | Giảm thiểu |
| --- | --- | --- | --- |
| 6 | **Đĩa đầy (C: 28GB)** — HF cache mặc định rơi vào C: + openpii ~4,25GB + model + venv + wheel CUDA | lỗi ghi khi tải | §4.4: `HF_HOME`/`HF_DATASETS_CACHE`/`TMPDIR` trên **D:**; subset theo locale; budget đo ở M0; không cài CUDA wheel (v1) |
| 7 | **Xung đột phụ thuộc (ca thật gliner↔datasets)** — `gliner 0.2.29` ghim `huggingface-hub 0.36.2` ⇒ `import datasets` vỡ (`BucketNotFoundError`) | ImportError | **3 venv tách** (attack/data/pii) + ghim phiên bản trong manifest; không dùng 1 requirements chung (bài học đã trả giá — `attack-tooling-install-check.md` §2) |
| 8 | **Model free đổi hành vi/rút giữa ma trận** | `model_served` khác; canary lệch | Canary 20 ca/ngày trên cả model dự phòng; Δ>5pp ⇒ chạy lại baseline; ASR tương đối theo ngày; phương án B (§5.6.5) |
| 9 | **Bộ gated chưa mở** | tải 401 | Bảng thay thế §4.2 chạy song song; phần gated ghi "không chạy được", không hứa |
| 10 | **Trùng lặp/contamination** (JBB⊂AdvBench/HarmBench; JGB là tập cha; llmail 56% trùng; ≥8 mirror) | test cao bất thường so dev | Dedupe 2 tầng trước chia; `labelled_unique`; 1 bản gốc/họ; bảng chồng lấn; kiểm "detector từng thấy dữ liệu chưa" |
| 11 | **Trộn loại nguồn khi trích số** (`[PAPER-mô phỏng]` vs `[VENDOR]` vs đo thật) | hội đồng không phân biệt được bằng chứng/marketing | Cột **tầng** ở mọi bảng + câu cảnh báo chung; vendor numbers (AWS 88/99%) ghi nhãn vendor |
| 12 | **Đo proxy ≠ đo guardrail** | số lạ khi tắt detector | C0 làm mốc đo overhead riêng; test byte-compat SSE trước; soak/load test M6 (vá M3) |
| 13 | **Tool tấn công tự cập nhật giữa các ngày** | kết quả đổi giữa ngày | Pin phiên bản (garak 0.17.1, PyRIT 1.1.0, promptfoo 0.124.x) + ghi manifest; nâng cấp phải chạy lại canary |
| 14 | **Đạo đức/pháp lý** (nội dung độc trong log; dữ liệu người thật — TensorTrust có mật khẩu người chơi, llmail là email; license NC; redistribute BIPIA WebQA/Summarization) | — | Quy trình: lọc trước khi lưu (blacklist/format), mask trong log/demo, không phát tán payload nguyên văn, nhãn cảnh báo trong artifact; bộ NC chỉ học thuật; **không redistribute** WebQA/Summarization (chạy script tại chỗ); `subject_key`/retention/purpose (NĐ 356/2025) |
| 15 | **Chuỗi phụ thuộc tiến độ** (M0→M1→…; probe xong mới chốt lịch) | trễ dây chuyền | MVP 4.500–7.000 call tách khỏi ma trận; ô nào xong ô đó; phân tích theo mẫu hoàn thành + sensitivity; risk list này đọc ở mỗi mốc |
| 16 | **Fail-closed thành DoS** (payload lớn, decode bomb, bão request) | timeout dây chuyền | Cap B13 + breaker + reason codes + soak test (M6); ngưỡng breaker cấu hình được và ghi log |
| 17 | **Số liệu BIPIA 2 phiên bản** (paper arXiv vs ACM; 626.250/86.250 từ alphaxiv) | trích dẫn lệch | Đối chiếu repo/paper khi trích con số, chốt trước khi viết báo cáo |
| 18 | **Trộn ngôn ngữ thật** (A4: "dữ liệu nhiều thứ tiếng" nhưng plan chỉ EN/VI) | câu hỏi hội đồng | Khai giới hạn rõ: EN+VI là phạm vi; ô `multi` (rikka-snow, có zh/fr) chạy 50 ca/arm C0-vs-C4 nếu ngân sách — nếu không, ghi "chưa đo" (vá P5) |
