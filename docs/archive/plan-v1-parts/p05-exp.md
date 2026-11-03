---

## 5. Thực nghiệm

### 5.1 Câu hỏi thực nghiệm RQ1–RQ5

> **Khoá trước khi chạy** (vá W1/W3): mọi tuyên bố ASR ghi rõ định nghĩa **targeted/untargeted**, `k` lần thử, nhiệt độ, judge; `k=1` overstate **12–24 điểm %**, temp 0→1 phồng tới **54 điểm %** (`papers-pii-and-eval.md` §(ii)); **mọi ΔASR dưới ~10 điểm % không được tuyên bố** nếu judge chưa qua kiểm chứng.

**RQ1 — Hiệu quả theo họ detector (tấn công một lượt).** *Bật guardrails (C1/C2/C3/C4) giảm ASR trên tấn công một lượt bao nhiêu so với C0, cùng model, cùng bộ ca?* Đo: ASR từng arm + TPR@1%FPR từng detector; so chênh lệch kèm CI. Dự đoán có cơ sở: C2/C3 mạnh nhất trên EN in-distribution (recall@1%FPR 97,5% công bố) nhưng **vẫn còn phần vượt** (0,0207; LODO 0,757; trần 38,8% — `risk-taxonomy-2026.md` §4.4); C4 không cộng tuyến tính (thêm lớp tăng bắt nhưng tăng FP/độ trễ — NVIDIA 75→83→99%, throughput 112,9→98,7).

**RQ2 — Khoảng cách ngôn ngữ VI vs EN.** *Cùng cấu hình, ASR_vi có cao hơn ASR_en không, họ nào lệch nhất?* Đo Δ kèm CI; recall F2/F3 trên VI ở **cùng FPR**; FPR của F1 trên VI lành; recall/precision PII entity-level VI vs EN. Dự đoán: dịch sang ngôn ngữ ít nguồn lực nâng ASR **<1% → 79%** (GPT-4); LlamaGuard −9%/−18% DSR trên ĐNÁ (`vietnamese-evasion-and-law.md` §B) — mọi số VI là **giả thuyết cần đo**, không trích như số đã biết.

**RQ3 — Đa lượt: scoring cấp phiên có cần thiết?** *Per-turn + scoring phiên (peak+accumulation, proxy-level, không cần LLM) bắt được bao nhiêu % chuỗi đa lượt @FPR mục tiêu, nhanh hơn per-turn thuần bao nhiêu lượt?* Đo: recall phiên @FPR≤1% (hiệu chuẩn trên benign sessions), **detection latency = lượt đầu bị chặn**; ASR live (block bật giữa phiên, ngân sách ≤10 lượt/≤3 retry, không restart). Biến thể: per-turn thuần · +session scoring · judge-đọc-cả-phiên (đối chứng âm — sụp −46pp dưới rewrite).

**RQ4 — Biến thể né tránh (tầng ký tự + tiếng Việt).** *Pipeline B1–B13 bắt được bao nhiêu % ca đơn lớp và ca tổ hợp?* Đo: recall từng lớp (homoglyph · zero-width · tags · base64/hex/ROT13 · fullwidth · NFC/NFD · mất dấu · teencode · chèn dấu cách) + tổ hợp A9; tỉ lệ "bắt được nhờ đúng 1 phép chuẩn hoá"; FPR trên VI lành. Dự đoán: đơn lớp phần lớn bắt được (≥90% kỳ vọng — chưa có số); tổ hợp là chỗ rơi.

**RQ5 — Cái giá và độ vững của số liệu.** *Guardrail tốn thêm gì (FPR, utility, độ trễ p50/p95, quota), và số ASR có đứng vững dưới chạy lặp + kiểm chứng judge?* Đo: FPR từng detector & hệ (thường + benign-chứa-từ-khoá); escalation/1k request; Δutility/retention/refusal; độ trễ thêm p50/p95 từng trạm (CPU) + TTFT theo `stream_mode`; số call detector/response; judge agreement + variance ≥5 lần.

### 5.2 Ma trận: arm C0–C5 × ô K1–K6

**Arm (yếu tố chính):**

| Arm | Nội dung | Vai trò |
| --- | --- | --- |
| **C0** | Passthrough (không detector) | Baseline + "nhánh gọi thẳng" định lượng chênh lệch |
| **C1** | Chỉ F1 (luật+Unicode+decode, local) | Chốt tất định — họ duy nhất block một mình |
| **C2** | Chỉ F2 (PG2 + deberta; PII: Presidio+recognizer VN+GLiNER) | Trần classifier đơn lẻ |
| **C3** | **F1+F2 (quorum, §3.5) — cấu hình ship đề xuất (PA-B)** | **MVP bắt buộc có** (vá #3) |
| **C4** | F1+F2+F3 cascade đầy đủ, **enforce** | Hiệu quả thực chiến (chặn đổi quỹ đạo đa lượt) |
| **C5** | = C4 nhưng **log-only** | Trần phát hiện; cho replay policy không tốn call |

Mức can thiệp (block/mask/log/escalate) là **yếu tố trong-arm**, đo live ở C4/C5 và **replay offline** từ log C5 cho ca một lượt (policy là hàm tất định của findings; replay **không** thay được live cho đa lượt — caveat W7: F2/F3 không tất định, replay không replay được escalate/timeout/attacker-adaptive).

**Ô (cell) dữ liệu — 1.320 ca/arm:**

| Ô | Loại | EN | VI | Tổng | Nguồn | Chỉ số chính |
| --- | --- | --- | --- | --- | --- | --- |
| K1 | Một lượt | 100 | 100 | 200 | JBB harmful 100 · rikka-snow `vi` + dịch JBB 100 (gán tay mẫu nhỏ kiểm) | ASR, TPR@FPR |
| K2 | Đa lượt (phiên 8 lượt) | 40 phiên (320) | 25 phiên (200) | 520 | geometry-of-harmfulness (EN) · VI tự dựng theo công thức 9 bước (`multiturn-attacks-part2.md` §4.2) | Recall phiên @FPR, detection latency, ASR live |
| K3 | Mã hoá + vô hình | 100 | 100 | 200 | **tự sinh** từ K1 (seed cố định; CipherChat-style + 9 kỹ thuật) | Recall theo lớp |
| K4 | Tiếng Việt chuyên biệt (A1–A9) | — | 100 | 100 | **tự sinh** từ K1-VI + VEL A10 | Recall theo lớp |
| K5 | Lành tính/over-defense | 100 | 100 | 200 | JBB benign · JGB benign · llmail 203 · huyleit CLEAN · VI tự sinh | FPR, refusal, utility |
| K6 | PII leak | 50 | 50 | 100 | openpii (vi/en) · Nemotron · vietnerm | Leak rate, mask P/R |

**Ô phụ (không nhân ma trận chính):** K2-AD adaptive live — 30 phiên EN × 8 lượt × 2 call (attacker+victim) = 480 call/arm, chỉ chạy **C0 và C4** (PyRIT/Crescendomation). Ô `multi` 50 ca/arm (C0 vs C4) tuỳ ngân sách — nếu không chạy: khai "chỉ EN/VI".

### 5.3 Định nghĩa "ô quyết định" + thiết kế lặp N=20/cell

- **Ô quyết định** (nơi plan phải kết luận được — vá W4): so sánh **C0 vs C3 vs C4 trên K1 và K2**. Power analysis: **MDD ≈ 18,2 điểm % ở n=100** (`nghien-cuu/N4-*.md` §4, arXiv 2609.25173 `[preprint]`); hai defense lệch thật 5 điểm % bị xếp sai thứ tự **~21%** nếu chạy 1 lần ⇒ **chốt: ô quyết định chạy lặp N=20 lần/cell** (mẫu "Adaptive Adversaries", arXiv 2607.18063: N=5/cell cho khác biệt lớn, **replicate N=20/cell cho so sánh then chốt**).
- **Cách hiện thực hoá trong ngân sách:** mỗi cell = một **bộ ca rút gọn đã khoá** — K1r = 50 EN + 50 VI = **100 call**; K2r = 10 phiên × 8 = **80 call**; mỗi vòng lặp = 1 lần chạy độc lập (seed khác) trên bộ rút gọn; 3 arm × 2 cell × 20 vòng = **10.800 call** (khoản lớn nhất của ngân sách — xem 5.4).
- **Hạ cấp có kê khai:** nếu probe M0 cho thấy ngân sách ngày không đủ, hạ N=20 → **N=10 → N=5**, mỗi lần hạ ghi rõ trong báo cáo ("hạ cấp độ chặt") — **không** đổi kết luận âm thầm. Ô **không đủ power** (K2-VI 25 phiên; K4 100 ca; K2-AD 30 phiên) phải liệt kê trước là *"chỉ báo cáo, không kết luận"*.

### 5.4 Ngân sách lượt gọi — ước lượng ĐÃ SỬA (vá #3)

> Sửa so với draft-C (≈15.500): (a) overhead judge tính **theo segment** — 1 call/đầu response + 1 call/mỗi 5 segment; 1 response 2.000–6.000 ký tự ≈ 10–30 segment ⇒ **~3–7 call judge/response** ở C4/C5, không phải 20% × số ca; (b) thêm **sinh/dịch dữ liệu tiếng Việt ~400–800 call** (một lần); (c) **chốt N=20/cell** cho ô quyết định (mới); (d) giả định rate limit **chưa có bằng chứng → probe ở M0**.

| Khối | Call ước tính | Cách tính |
| --- | --- | --- |
| Ma trận chính, 1 vòng (6 arm × 1.320) | **7.920** | 6 × (200+520+200+100+200+100) |
| **Lặp ô quyết định N=20/cell** (C0/C3/C4 × K1r/K2r) | **+10.800** | 3 arm × (100+80) × 20 vòng |
| Judge theo segment (C4+C5) | **+5.000–10.000** | 2.640 response × 2–4 call/response trung bình; **đếm lại từ log C5** sau khi runner ghi segment thật |
| Sinh/dịch dữ liệu VI (dịch K1-VI, dựng K2-VI, K4, benign VI) | **+400–800** | một lần, không nhân arm; model sinh pinned + kiểm tay mẫu |
| K2-AD adaptive live (C0 vs C4) | **+960** | 30 × 8 × 2 × 2 arm |
| Kiểm chứng judge (150×2 judge + 200×2 wrapper) | **+700** | §6.4 |
| Sub-study streaming (TTFT/exposure: 50 × 4 mode × 2 trạng thái) | **+400** | draft-A §2.7 |
| Smoke / API-shape / fuzz ngưỡng | **+300** | §2.8 + R16 |
| Buffer missing/retry (+10%) | **+2.500–3.100** | tách khỏi dòng "missing rate" — xem 5.6 |
| **TỔNG (đầy đủ)** | **≈ 29.000–35.000** | giảm còn **≈17.000–23.000** nếu bỏ tầng lặp N=20 (kịch bản tối thiểu) |

**MVP (chạy trước để có số sớm + phát hiện lỗi harness):** arms **{C0, C3, C4}** (vá #3: thay {C0,C2,C4} cũ — C3 là cấu hình ship), ô giảm nửa (K1 100 · K2 160 · K3 100 · K4 50 · K5 100 · K6 50 = 560/arm):

| Khối MVP | Call |
| --- | --- |
| Victim 3 arm × 560 | 1.680 |
| Judge theo segment (chỉ C4) | +1.700–3.900 |
| Lặp tối thiểu + smoke + verify | +700 |
| Sinh/dịch VI (chia sẻ một lần) | +400–800 |
| **Tổng MVP** | **≈ 4.500–7.000** |

**Khả thi / lịch:** rate limit 9router free **chưa đo** (QĐ-C1) ⇒ **cấm cam kết lịch trước M0**. Sau probe: nếu ≥2.000 call/ngày, MVP ~**2–3 ngày**; ma trận đầy đủ lập lịch như **~3 tuần có đệm**; ô chủ chốt chạy trước, chạy nền qua đêm, dừng ô nào xong ô đó, ghi ngân sách đã dùng theo ngày.

### 5.5 Quy trình chạy (thứ tự cố định)

| Bước | Việc | Đầu ra |
| --- | --- | --- |
| 0 | Môi trường: 3 venv tách (`attack`/`data`/`pii`) theo §4.4 + env cache trên D: | venv import OK checklist |
| 1 | Tải dữ liệu (venv-data): JBB, deepset, rikka-snow, llmail (`labelled_unique_*` + 203 FP), qxcv/tensor-trust, JGB, huyleit, openpii subset, Nemotron, vietnerm; clone BIPIA + tự sinh WebQA/Summarization | hash từng file vào manifest |
| 2 | Snapshot router: `curl /v1/models` → `logs/env/models_<date>.json`; smoke `oc/space-bunny-free`; **pin model victim + 1 dự phòng tương đương**; canary script | snapshot + pin ghi manifest |
| 3 | Khởi động proxy `--port 20129`; kiểm passthrough `/v1/models` + 1 call; **đo overhead proxy ở C0** (tách độ trễ proxy khỏi độ trễ guardrail) | log latency C0 baseline |
| 4 | Smoke 10 ca × 6 arm qua proxy: JSON/SSE đúng + log đủ trường + hash-chain verify | smoke PASS |
| 5 | Ma trận chính: `run_matrix.py --manifest manifests/matrix.yml --arm C4 ...` (asyncio, checkpoint theo `case_id`); thứ tự C0→C1→C2→C3→C4→C5; ô chủ chốt trước; replay offline từ C5 cho policy | logs/run_*.jsonl |
| 6 | garak (đối chứng độc lập #1): `--list_probes` chốt danh mục → chạy qua proxy (`--model_type openai`, option file trỏ `base_url` proxy) | report garak |
| 7 | PyRIT (đối chứng #2, adaptive): `pyrit_scan` cho K2-AD sau khi chốt chiến lược trong 1.1.0 | report PyRIT |
| 8 | Phân tích: `analyze.py --logs ... --out reports/` → bảng ASR/TPR/FPR/leak/latency + CI + **missing rate từng ô**; `--replay-policy` cho mask/block/escalate offline | reports/*.md |

**Nguyên tắc tái lập:** mỗi run = `run_id` + bản copy manifest + hash của: config YAML · git commit harness · dataset (file hash / revision HF) · prompt judge. Victim temp 0, judge temp 0, seed lưu; **vẫn lưu raw output (đã mask)** để **re-judge offline** khi đổi judge.

### 5.6 Rate limit & canary (kế hoạch B khi model free đổi)

1. **Probe trước (M0):** 100 request liên tiếp lên 1 model phụ → ghi status/429/`Retry-After` → `logs/m0/ratelimit_probe.json`; probe riêng **2 luồng song song** (K2-AD cần attacker+victim đồng thời — áp lực ×2).
2. **Client-side token-bucket + hàng đợi bền:** checkpoint theo `case_id` (resume sau crash); backoff exponential + jitter; cap retry ≤3/lượt; **429 = missing, không phải fail** — loại khỏi mẫu số, **báo missing rate từng ô**; ca missing **chạy bù có ngân sách** tách riêng (không nằm trong "+10%").
3. **Pin model cho ma trận; xoay chỉ cho judge/call phụ trợ** — mọi lần xoay ghi `model_served`.
4. **Canary phát hiện đổi hành vi:** 20 ca cố định/ngày trên **cả model chính lẫn dự phòng**, so với baseline cùng ngày; ngưỡng cảnh báo đề xuất **Δ>5 điểm %** (chốt trước khi chạy); vượt ngưỡng ⇒ chạy lại baseline, báo cáo **ASR tương đối theo baseline cùng ngày** — **không so số tuyệt đối giữa các tuần** (W6/không so được khi model đổi sau lưng router).
5. **Phương án B (T16):** nếu pool free ngừng phục vụ giữa ma trận → kịch bản đã định: hoàn thành **F1+F2 offline + judge cho tập nhỏ**; mọi bảng ghi ngày chạy + `model_served`; phần không chạy được ghi "không chạy được vì hạ tầng", không nội suy.
