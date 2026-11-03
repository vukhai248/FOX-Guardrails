---

## 4. Dữ liệu

### 4.1 Bộ dùng thật (đã kiểm HTTP từ máy này — `datasets-reachability.md`)

**Nhóm tấn công / đánh giá:**

| Bộ | Vai trò | Quy mô | License | HTTP |
| --- | --- | --- | --- | --- |
| `JailbreakBench/JBB-Behaviors` | **Bắt buộc (đề tài)** — K1 EN (100 harmful) + K5 benign (100) | 200 behavior | MIT | ✅ 200 |
| `microsoft/BIPIA` (repo + script) | **Bắt buộc (đề tài)** — indirect injection; ASR macro/micro theo attack type & vị trí | 5 task; WebQA/Summarization **phải tự sinh bằng script** (không redistribute) | repo | ✅ repo (HTML 200) |
| `microsoft/llmail-inject-challenge` (bản `labelled_unique_*`) | Tấn công người-thật; `emails_for_fp_tests.jsonl` (203) cho K5 | 160.741 + 37.303 unique (raw 56% trùng nội bộ — chỉ dùng unique) | MIT | ✅ 200 |
| `qxcv/tensor-trust` (mirror) | Đa bước + `detecting-extractions` 230 mẫu | 126.808 attack (69.906 unique) + 46.457 defense | theo gốc | ✅ 200 |
| `xunguangwang/JailbreakGuardrailBenchmark` | harmful + benign một chỗ; **tập CHA** của JBB/JailbreakHub/MultiJail — không đếm là nguồn độc lập | 3.720 dòng | MIT | ✅ 200 |
| `hackaprompt/hackaprompt-dataset` | Tấn công người-thật quy mô lớn (test detector, không đo ASR) | ~600K prompt (parquet ~150MB) | MIT | ✅ 200 *(§7 sửa lại là công khai — kiểm lại ngay trước khi tải)* |
| `walledai/HarmBench` | Đối chiếu ASR chuẩn hoá | <1K | MIT | ✅ 200 *(trước ghi mâu thuẫn — §7: 200)* |
| `rikka-snow/prompt-injection-multilingual` | Nguồn thô K1-VI/K3-VI (tag `vi`) — **thô, phải tự lọc** | 7.282 dòng | — | ✅ 200 |
| `Lakera/b3-agent-security-benchmark-weak` | Smoke agentic (210 tấn công × 3 mức) — **không** để kết luận thống kê | 630 dòng | `other` (đọc kỹ) | ✅ 200 |

**Nhóm lành tính (K5, FPR, utility):** JBB 100 benign · JGB nhánh benign (AlpacaEval/OR-Bench — tránh cộng trùng với JBB) · `emails_for_fp_tests.jsonl` (203) · `huyleit/vietnamese-social-moderation` lớp CLEAN 11.389 (**benign VI chính**; đã merge UIT-ViHSD ⇒ không dùng ViHSD gốc song song) · benign VI tự sinh (teencode/dấu đúng).

**Nhóm PII (K6):**

| Bộ | Vai trò | Trạng thái |
| --- | --- | --- |
| `ai4privacy/pii-masking-openpii-1.5m` | **Trục chính** — 1.636.375 dòng, 30 ngôn ngữ **có `vi`**, 19 lớp PII, ~4,25GB | ✅ 200 (tải **subset theo locale** để tiết kiệm đĩa) |
| `nvidia/Nemotron-PII` | Span-level EN (55+ lớp) | ✅ 200, CC-BY-4.0 |
| `ngocthanhdoan/vietnerm-cccd-dataset` (+ mirror `phatdatpq`) | CCCD VN (BIO, 2.000 mẫu) | ✅ 200, MIT |
| `SALT-NLP/PrivacyLens` | Leak rate hành vi (mốc: GPT-4 **25,68%**, Llama-3-70B **38,69%**) | ✅ 200, CC-BY-4.0 |
| PII tự sinh VI (CCCD/SĐT/MST sai checksum, teencode, mất dấu) | Ca biến thể K4/K6 | Tự dựng theo `vietnamese-pii-formats.md` |

**Hạ tầng model (đã kiểm):** `meta-llama/Llama-Prompt-Guard-2-86M` ✅ 200 · `protectai/deberta-v3-base-prompt-injection-v2` ✅ 200 · `OpenMed/OpenMed-PII-Vietnamese-*` ✅ 200 (F1 ~0,731–0,745 — **tín hiệu, không làm căn cứ block**).

### 4.2 Bộ gated (401) — việc của chủ đề tài + bộ thay thế (không chặn tiến độ)

| Bộ gated | Ý nghĩa | **Thay thế dùng ngay** |
| --- | --- | --- |
| `ai4privacy/pii-masking-3m` (+ bản asia-pacific) | PII 3M "chuẩn nhất", có VI | **`pii-masking-openpii-1.5m`** (có `vi`) + vietnerm-cccd |
| `ai4privacy/SPY` | Benchmark PII | `mks-logic/SPY` (mirror) hoặc bỏ |
| `HaoBui/vn_id_card` | CCCD VN | `ngocthanhdoan/vietnerm-cccd-dataset` / `phatdatpq` |
| `ethz-spylab/agentdojo` (dataset HF gated; repo GitHub 200) | Agentic chuẩn (ASR/utility định lượng) | `pooria/benchmark-mcp-safety` (MIT, 40 task) + b3-weak; **nếu không mở được HF ⇒ ghi rõ là hạn chế** |
| `OpenMed/VietMed-NER`, `datnth1709/VLSP2016_NER` | NER VI y tế/chuẩn | họ `OpenMed-PII-Vietnamese-*` (200, apache-2.0) |
| `rogue-security/prompt-injections` (tên CŨ) | — | tên MỚI `rogue-security/prompt-injections-benchmark` = **200 công khai**, cc-by-**nc** (học thuật) |

→ **Việc chủ đề tài phải làm (không agent làm thay):** đăng nhập HF + bấm *Agree and access* cho các bộ muốn dùng; nếu chưa mở kịp, phần dùng bộ gated ghi *"không chạy được vì quyền truy cập"* — **không hứa trước**. Ba bộ từng mâu thuẫn báo cáo (`hackaprompt`, `HarmBench`, `rogue-...-benchmark`) — **kiểm lại HTTP ngay trước khi tải**.

### 4.3 Chia train/dev/test chống trùng lặp

Quy tắc gốc (`datasets-quality.md` §4): *"không bao giờ chia train/test từ hai bộ khác nhau khi chưa dedupe; mọi con số tổng mẫu phải ghi rõ sau dedupe hay theo card"*. Quy trình 5 bước (chạy thật, ghi log):

1. **Dedupe exact + near-dup**: chuẩn hoá (NFKC + lowercase + gộp whitespace) → hash exact; MinHash/Jaccard ≥0,8 near-dup. Ghi tỉ lệ trùng từng cặp nguồn (bảng chồng lấn 11 dòng của `datasets-quality.md` §4 là checklist bắt buộc).
2. **Provenance tag** từng mẫu: `source_id`, `parent_set`, `template_id`. Tập "cha" (JGB ⊃ JBB+JailbreakHub+MultiJail+SafeMTData) **không** tính là nguồn độc lập.
3. **Split theo group** = (`source_id` × họ kỹ thuật × `template_id`); phiên đa lượt cắt **nguyên phiên**; không để cùng template ở cả dev và test.
4. **Tỉ lệ:** dev **20%** (hiệu chuẩn θ, chọn FPR mục tiêu, tuning ρ/β) · test **80%** (held-out, khoá sau khi chốt ngưỡng, mở đúng 1 lần). **Train chỉ tồn tại nếu fine-tune detector** (ngoài MVP).
5. **Chống nhiễm bẩn:** chạy chéo trên bộ detector **chưa từng thấy** — bài học "Passing the Test You Trained On": PIGuard đứng đầu BIPIA **95,1% @1%FPR** nhưng chỉ bắt **2,1%** injection AgentDojo; Kendall τ = **0,01** (`nghien-cuu/N4-*.md` §3). Điểm test cao bất thường ⇒ kiểm tra ngay bộ đó có trong data train của detector không.

**Ánh xạ ô:** K1 test = 100 JBB harmful + 100 VI (rikka-snow lọc + dịch); dev = deepset+gandalf (chỉ smoke/hiệu chuẩn — quá nhỏ/thiên lệch để làm số chính). K2 test = phiên geometry-of-harmfulness (EN) + phiên VI tự dựng; dev = 10 phiên pilot. K3/K4 = **sinh từ test gốc** (seed cố định — là biến thể của test nên **không bao giờ** dùng để tune). K5 = JBB benign + AlpacaEval/OR-Bench + 203 llmail + huyleit CLEAN + benign VI tự sinh (kiểm không giao với tập hiệu chuẩn). K6 = openpii (vi/en) + Nemotron + vietnerm-cccd, chia 80/20 **stratified theo lớp PII**.

### 4.4 Chính sách đĩa & cache (BẮT BUỘC — ổ C: chỉ còn 28GB)

HF cache mặc định là `C:\Users\Admin\.cache\huggingface` — **sai chỗ cho máy này**. Chốt:

```bash
# Bắt buộc trước MỌI lệnh tải (đặt trên D:, không dùng C:)
export HF_HOME=D:/create/FOX-Guardrails/hermess/data/hf
export HF_HUB_CACHE=$HF_HOME/hub
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_DISABLE_TELEMETRY=1
# Windows native: đặt thêm TMP/TEMP cho process python (không chỉ TMPDIR của bash)
export TMPDIR=D:/create/FOX-Guardrails/hermess/tmp
```

**Ngân sách dung lượng ước tính (D: còn 143GB — dùng được; breakdown để theo dõi):**

| Khoản | Ước tính |
| --- | --- |
| Datasets thô (JBB, llmail unique, tensor-trust, JGB, rikka, huyleit, BIPIA tự sinh) | ~8–12GB |
| `openpii-1.5m` subset vi+en (thay vì full ~4,25GB) | ~0,6–1,5GB |
| Nemotron-PII + vietnerm-cccd + K6 phụ | ~1–2GB |
| Model F2 (PG2-86M ~0,35GB; deberta ~0,7GB; GLiNER ~0,5GB; OpenMed ~0,5GB) | ~2GB |
| Venv: attack 1,7GB + data ~1GB + pii ~1,5GB | ~4GB |
| Log JSONL + SQLite + reports + artifacts thực nghiệm | ~3–8GB (cap + rotation) |
| tmp/decode + buffer | ~2GB (cap B13) |
| **Tổng dự kiến** | **~22–32GB — nằm gọn trên D:** |
| *(không cài)* wheel CUDA | −2,5GB (quyết định v1 CPU-only) |

Kết thúc M0 phải có file `logs/m0/disk_budget.md` với **số đo thật** (GB tải được, tốc độ MB/s) — thay cho ước tính này.

### 4.5 Bảo vệ log (vá #5 — log là "nguồn sự thật" thì phải bảo vệ được)

| # | Cơ chế | Yêu cầu kiểm được |
| --- | --- | --- |
| 1 | **Hash-chain toàn vẹn**: mỗi record có `prev_hash` + `record_hash = H(schema_ver‖prev_hash‖payload)`; mỗi file ngày có anchor ghi vào file/anchors tách riêng | `fox logs verify --from <file>` phát hiện mọi sửa/thiếu dòng; chạy trong CI (test cố tình sửa 1 dòng ⇒ verify FAIL) |
| 2 | **Chống rò raw**: mặc định log chỉ lưu **bản đã mask** + `span_hash` (HMAC) + `raw_sha256`; raw chỉ trong store điều tra (nếu bật), tách quyền đọc | Test tự động: grep payload gán nhãn **không được** xuất hiện trong bất kỳ field log nào ngoài store; test cả crash-dump/escalation record |
| 3 | **Bảo vệ viewer**: Jinja autoescape + CSP; **strip/escape control + bidi khi hiển thị** (Trojan Source trong log); snapshot test với payload độc (XSS + RLO + ANSI escape) | Test render payload độc → không thực thi, không đảo hướng hiển thị |
| 4 | **`span_hash` = HMAC-SHA256(k_deploy, span)** — salt/khóa theo triển khai, **không hash trần** (chống oracle từ điển); coi trường này là **dữ liệu nhạy cảm** trong policy | Soát code: không nơi nào dùng sha256 trần cho span; key không nằm trong log |
| 5 | **Cap + rotation + retention enforce** bằng code (nối cap B13): cap byte/ngày, xoá theo `retention_days`, cảnh báo khi >80% quota | Test: chạy vượt cap ⇒ file xoay/đóng đúng; retention job chạy và ghi lại hành động xoá |
| 6 | **Log injection JSONL**: ghi bằng `json.dumps` (không nối chuỗi) + test khóa hành vi với payload chứa `\n{`, `\u2028` | Test cố định hành vi trong CI |

**Khung pháp lý VN lên log (thiết kế ngay, không để sau — `vietnamese-evasion-and-law.md` §C):** log hội thoại/prompt/response là **dữ liệu cá nhân cơ bản**, có thể thành **nhạy cảm** tuỳ nội dung; nghĩa vụ trả lời chủ thể **10 ngày (xem/sửa) / 15 ngày (rút đồng ý)** (Điều 5 NĐ 356/2025) ⇒ **bắt buộc `subject_key` truy vết được** trong mọi record; sự cố vị trí/sinh trắc **≤72 giờ** (Điều 29) ⇒ log đủ chi tiết để xác định phạm vi — **phát biểu đúng mức**: hệ *ghi log đủ trường*, không đảm bảo năng lực tổ chức. Chế tài tham chiếu: NĐ 330/2026 (hiệu lực 19/8/2026; ví dụ Điều 39: 40–60 triệu) — **nguồn thứ cấp, chưa đối chiếu toàn văn** (VEL §C.4 tự cảnh báo) ⇒ giữ caveat khi trích. Thiết kế: `raw` chỉ khi cần điều tra; mặc định lưu bản mask + `span_hash`; thêm `subject_key`, `purpose: security`, `retention_days`; kèm tài liệu ngắn "log gì, vì sao, giữ bao lâu, ai đọc" (tờ trình NĐ 356 nêu đích danh lỗi *"không xác định được luồng xử lý dữ liệu"*).

**Luồng dữ liệu mới phải khai báo (vá W/Q16-ẩn):** gửi nội dung người dùng sang **F3 judge qua 9router** (nhà cung cấp thứ ba) là **một luồng xử lý dữ liệu mới** — ghi vào tài liệu "log gì/ai đọc" + mặc định **F3 async + tắt được** + phương án thay thế (chạy local/không F3); đây là nội dung hội đồng đạo đức sẽ hỏi.
