# FOX-Guardrails — Plan tổng quan (v2)

> Ngày lập: 02/11/2026 · Thay thế plan v1 (18/10/2026, đã chuyển vào `docs/archive/plan-v1-2026-10-18.md`).
> Đọc file này trước. Chi tiết từng phần nằm ở các file cùng thư mục (mục lục ở §9).

---

## 0. Đọc nhanh

- **Sản phẩm:** một lớp guardrails "cắm vào là chạy" tên **FOX-Guard**. Lõi là thư viện Python, gồm 3 trạm kiểm tra: **đầu vào**, **ngữ cảnh** (dữ liệu truy xuất/kết quả tool) và **đầu ra**. Có hai cách cắm vào app: **(1)** gọi API sidecar hoặc SDK ở 3 điểm trong app; **(2)** proxy OpenAI-compatible (đổi `base_url`).
- **Phát hiện:** kết hợp **luật + chuẩn hoá Unicode/tiếng Việt**, **mô hình phân loại** (Prompt Guard 2) và **bộ nhận diện PII tiếng Việt** (Presidio + recognizer VN + NER). Có thêm **LLM judge** làm phương án so sánh.
- **Xử lý:** 4 mức theo đề tài: **cho phép · che (mask) · chặn · chuyển kiểm duyệt**. Mọi quyết định được ghi log kèm lý do, và log đã được che PII.
- **Ứng dụng thử nghiệm:** chính web **Agentic RAG e-commerce** (chatbot CSKH tiếng Việt). Phần A hoàn thiện web để có các điểm chèn tấn công thật: ghi chú đơn hàng, review, ticket, tool ghi.
- **Thực nghiệm:** BIPIA (indirect, EN) và JailbreakBench (direct, EN) được báo cáo **riêng**, theo đúng đề tài. Thêm bộ **CSKH tiếng Việt tự xây**, là đóng góp chính. So sánh: không guard / chỉ prompt / chỉ luật / chỉ mô hình / kết hợp (/ + judge).
- **Lịch:** 4 tuần + 1 tuần đệm (03/11 → 07/12/2026). Phần A và Phần B chạy **song song**, mỗi phần do một agent riêng (Codex / Antigravity). Bạn giữ vai trò duyệt, chạy thử, hiểu, viết báo cáo.

---

## 1. Đánh giá plan v1: giữ gì, bỏ gì

**Kết luận:** plan v1 **không dùng tiếp được làm plan thực thi**. Phần nghiên cứu nền và một số nguyên tắc thiết kế vẫn tốt, nên giữ lại. Những phần còn lại cần đập đi và xây lại.

Lý do:

1. Plan v1 viết theo giả định *"thời hạn không phải ràng buộc gấp"* (sổ quyết định A5). Giả định này giờ đã sai: bạn chỉ còn **1 tháng, chủ yếu buổi tối**.
2. Quy mô vượt sức một người trong 1 tháng: 957 dòng, 13 bước chuẩn hoá, 6 arm × 6 ô, lặp N=20, **29.000–35.000 lượt gọi LLM**, streaming theo segment với K=512, hash-chain log, HMAC span, registry phiên chống bypass...
3. Plan v1 coi app demo là "tuỳ chọn" và chỉ có dạng proxy. Trong khi đó bạn đã có web e-commerce thật để làm nền, và web này gọi Gemini SDK trực tiếp chứ không qua `base_url` OpenAI. Vì vậy proxy-only không cắm được vào web của bạn nếu không sửa web.
4. Plan v1 dày tới mức bạn không thể nắm hết để vấn đáp. Hội đồng hỏi vào bất kỳ chi tiết nào cũng có rủi ro.

| Hạng mục v1 | Quyết định | Ghi chú |
| --- | --- | --- |
| Research nền (`hermess/research/*`, `hermess/nghien-cuu/*`) | **Giữ** làm tài liệu tham khảo | Không chép lại; plan v2 trích khi cần |
| Bảng định dạng PII Việt Nam (CCCD, SĐT, MST, thẻ, BHYT…) | **Giữ** | Chuyển sang `B-guardrails.md` B5.1 |
| Phát hiện Unicode/homoglyph/zero-width/tags (đã đo trên máy) | **Giữ, rút gọn** 13 bước → 8 bước | `B-guardrails.md` B2 |
| Nguyên tắc: luật tất định được chặn một mình; classifier đơn lẻ không tự chặn | **Giữ, đơn giản hoá** | `B-guardrails.md` B6.1 |
| PII mặc định = mask, không block | **Giữ** | |
| Log phải che PII | **Giữ** (đề tài yêu cầu) | Bỏ hash-chain/HMAC |
| Proxy OpenAI-compatible là sản phẩm duy nhất | **Sửa**: proxy thành adapter phụ (gói B8) | Đường chính là SDK + sidecar |
| Streaming theo câu, overlap K=512, deny-frame SSE | **Bỏ** | Proxy chỉ có `hold` (đệm cả câu trả lời rồi mới kiểm) |
| 9router + model free làm nạn nhân | **Bỏ khỏi đường chính** | Dùng chính LLM của web (Gemini/Groq). 9router chỉ dùng nếu cần judge rẻ |
| Ma trận 6 arm × 6 ô, N=20, 29–35k call | **Bỏ** | Thay bằng §3 của `C-du-lieu-va-thuc-nghiem.md` (~1k call ở kịch bản tối thiểu, ~5–9k ở kịch bản đầy đủ) |
| Hash-chain log, HMAC span, chống oracle, registry phiên, chống bypass `/v1/completions` | **Bỏ** | Ghi vào "giới hạn / hướng phát triển" |
| 3 venv tách (attack/data/pii) | **Bỏ** | 1 môi trường cho FOX-Guard + 1 cho web; NER xung đột phụ thuộc thì chạy process riêng (xem `B-guardrails.md` B5.1) |
| Pháp lý: hạn 72h, 10/15 ngày… | **Rút gọn** | Một đoạn trong báo cáo, không thành tính năng |
| Bản phân loại paper CSKH (01/11) | **Giữ** làm danh sách đọc | `docs/research/Phan_loai_paper_CSKH_Thuong_mai_dien_tu.md` |

---

## 2. Phạm vi chốt (v2)

### 2.1 Đề tài → hạng mục làm (bảng đối chiếu cho hội đồng)

| Câu trong `de-tai.md` | Làm ở đâu | Mức |
| --- | --- | --- |
| "chỉ dẫn độc hại từ câu hỏi người dùng" (direct PI) | Trạm INPUT: luật + classifier (B3, B4) | Bắt buộc |
| "…hoặc từ dữ liệu bên ngoài như tài liệu truy xuất, email, kết quả gọi công cụ" (indirect PI) | Trạm CONTEXT: kiểm kết quả tool (`order_lookup`, `product_reviews`, `policy_search`…) trước khi đưa vào LLM (B3, B4, B9) | Bắt buộc |
| "PII … cần được phát hiện và xử lý trước khi truyền hoặc hiển thị" | PII ở cả 3 trạm: **giả danh hoá có hoàn nguyên** trước khi gửi LLM; mask khi hiển thị; chặn bot **đòi** PII không cần thiết (B5) | Bắt buộc, **đầy đủ** |
| "kết hợp luật phát hiện, mô hình phân loại và bộ nhận diện PII" | F1 luật, F2 classifier, PII engine; F3 LLM judge là phương án so sánh | Bắt buộc (F3: nên có) |
| "cho phép, che thông tin, chặn nội dung hoặc chuyển … người kiểm duyệt" | Policy engine 4 hành động `allow / mask / block / review` (B6) | Bắt buộc |
| "phân biệt nội dung phục vụ tác vụ và chỉ dẫn có khả năng thao túng" | Trạm CONTEXT: khoanh vùng đoạn bị chèn và **chỉ cắt đoạn đó** (giữ phần dữ liệu hợp lệ) + bọc datamarking; bộ **hard-benign** (ghi chú giao hàng hợp lệ là chỉ dẫn cho shipper, không phải cho bot) | Bắt buộc |
| "quyết định được ghi nhận kèm bằng chứng và lý do" | Audit store (SQLite): findings, rule_id, điểm, lý do, đoạn bằng chứng (đã che) (B6) | Bắt buộc |
| "tích hợp lớp bảo vệ vào ứng dụng hỏi đáp RAG thử nghiệm" | Cắm vào web e-commerce qua 3 hook (B9) + proxy demo (B8) | Bắt buộc (proxy: nên có) |
| "dashboard theo dõi cảnh báo, xem lại quyết định và thống kê" | Streamlit dashboard (B10) | Bắt buộc |
| "bản ghi giám sát được che PII trước khi lưu" | Audit store chỉ nhận text đã mask; có test tự động (B6) | Bắt buộc |
| "so sánh … luật, mô hình phân loại và cơ chế kết hợp" | Arm R / M / H (+J) — `C-du-lieu-va-thuc-nghiem.md` | Bắt buộc |
| "precision, recall, F1, tỷ lệ chặn nhầm, ASR, tỷ lệ rò PII trước/sau" | Detector-level + end-to-end (C) | Bắt buộc |
| "ảnh hưởng chất lượng trả lời, độ trễ, chi phí" | Task success, latency p50/p95, token/call (C) | Bắt buộc |
| "dữ liệu tách theo nguồn hoặc dạng tấn công" | Split theo `template_id` (CSKH, PII) và theo dạng tấn công (BIPIA attack-train/test) (C §2.5) | Bắt buộc |
| "BIPIA nguồn chính … JailbreakBench bổ sung … báo cáo riêng" | C §2.1, C §2.2, báo cáo 2 bảng riêng | Bắt buộc |

### 2.2 Trong phạm vi

- Prompt injection **trực tiếp và gián tiếp** ở dạng **văn bản**, tiếng Việt và tiếng Anh, gồm cả các dạng né tránh ở mức ký tự: chữ tàng hình (zero-width, Unicode tags), chữ trông giống nhau (homoglyph), mã hoá, biến thể tiếng Việt.
- PII tiếng Việt và tiếng Anh: phát hiện, che/giả danh hoá, chặn bot đòi PII, che PII trong log.
- Tấn công lợi dụng tool **trong giới hạn tool của web**: điều khiển bot gọi tool ghi (tạo ticket), đổi tham số, gọi tool với ID đơn của người khác. Trường hợp cuối là kiểm tra phân quyền backend, **không tính** vào thành tích của detector.
- Rò dữ liệu qua **link/ảnh markdown** trong câu trả lời: chặn link ngoài danh sách cho phép, xoá ảnh ngoài.

### 2.3 Ngoài phạm vi (ghi vào phần "giới hạn" của báo cáo)

Tấn công qua ảnh/âm thanh; đầu độc dữ liệu huấn luyện hay backdoor; tấn công cần truy cập trọng số (gradient, attention); MCP tool poisoning và lây nhiễm đa agent; đầu độc memory dài hạn; streaming từng token; fine-tune LLM backbone; nội dung độc hại hay toxicity nói chung. Riêng toxicity: JailbreakBench chỉ dùng để đo **phát hiện yêu cầu đối kháng trực tiếp**, không cam kết lọc nội dung độc hại ở đầu ra.

---

## 3. Kiến trúc tổng thể

```text
                ┌──────────────────────── Web e-commerce (Phần A) ───────────────────────┐
 Khách hàng ──▶ │ Next.js chat-widget ─▶ FastAPI /chat ─▶ LangGraph workflow_1          │
                │                                  │                                     │
                │   [HOOK 1] check_input(user_msg) │   MasterAgent (Gemini, tool loop)   │
                │                                  │     │ gọi tool: order_lookup,        │
                │                                  │     │ product_reviews, policy_search,│
                │                                  │     │ create_support_ticket …        │
                │   [HOOK 2] check_context(tool_output, source=tool:<tên>)  ◀── mỗi lần │
                │   [HOOK 3] check_output(final_answer)                                  │
                └──────────────┬─────────────────────────────────────────────────────────┘
                               │ SDK in-process HOẶC HTTP sidecar
                               ▼
        ┌─────────────────────────── FOX-Guard (Phần B) ───────────────────────────┐
        │ normalize (Unicode, tiếng Việt, decode)                                   │
        │ F1 luật PI · F2 classifier PI · F3 LLM judge (tuỳ chọn)                   │
        │ PII engine (Presidio + recognizer VN + NER) · solicitation · link guard   │
        │ policy engine → allow / mask / block / review                             │
        │ PII vault (giả danh hoá ↔ hoàn nguyên) · audit store (SQLite, đã che PII) │
        │ adapters: SDK · sidecar FastAPI · proxy OpenAI-compatible (hold)          │
        └───────────────┬───────────────────────────────────────────────────────────┘
                        ▼
              Dashboard Streamlit: cảnh báo · hàng đợi kiểm duyệt · thống kê · kết quả thực nghiệm
```

Vì sao chọn **SDK/sidecar làm đường chính, proxy làm phụ** (quyết định của tôi, bạn đã giao):

- Ở hook, guard **biết chính xác** đoạn text nào là dữ liệu tool, đến từ nguồn nào (`review` hay `order_note`). Đây là điều kiện để "phân biệt nội dung phục vụ tác vụ và chỉ dẫn thao túng" chạy chính xác. Proxy chỉ thấy một mảng `messages[]` đã trộn.
- Web của bạn gọi Gemini SDK, không có `base_url` OpenAI. Hook chỉ cần khoảng 20 dòng sửa ở 3 chỗ. Proxy thì đòi viết lại `LLMService`.
- Proxy vẫn có giá trị "plug-and-play thật" cho app khác dùng OpenAI SDK, nên giữ làm gói B8 chạy song song. Hội đồng hỏi "app khác cắm thế nào?" thì demo được.

---

## 4. Sổ quyết định v2

| # | Quyết định | Ai chốt | Lý do |
| --- | --- | --- | --- |
| Q1 | Phạm vi: PI trực tiếp + gián tiếp, dạng văn bản | Bạn | Thu hẹp đề tài |
| Q2 | PII làm **đầy đủ**: 3 trạm, recognizer VN, NER tên/địa chỉ, giả danh hoá, chặn đòi PII, log đã che | Bạn | Đề tài đã chốt PII |
| Q3 | Dạng cắm: lõi Python + SDK + sidecar (chính); proxy OpenAI-compatible (phụ, B8) | Tôi (bạn giao) | §3 |
| Q4 | Ứng dụng thử nghiệm = web Agentic RAG e-commerce | Bạn | Có sẵn, tiếng Việt, có tool và dữ liệu do khách nhập |
| Q5 | Phần A làm "tối thiểu để bench + sửa thanh toán"; tính năng web thật khác để sau | Tôi (bạn giao) | Đủ điểm chèn thật; thanh toán hiện giả mạo được (xem A §1) |
| Q6 | Classifier chính: `Llama-Prompt-Guard-2-86M` (đa ngôn ngữ); phụ: `protectai/deberta-v3-base-prompt-injection-v2` (EN) | Tôi | Chạy CPU được; PG2 có hỗ trợ đa ngôn ngữ (phải tự đo trên tiếng Việt) |
| Q7 | Store log = SQLite một file + xuất JSONL khi cần | Tôi | Dashboard đọc dễ; bỏ hash-chain |
| Q8 | Dashboard = Streamlit (Python) | Tôi | Nhanh, cùng ngôn ngữ với lõi; không đụng admin page Next.js |
| Q9 | LLM cho thực nghiệm = chính model web đang dùng (Gemini flash-lite / Groq), temperature cố định thấp khi bench | Tôi | Đo trên hệ thống thật; không phụ thuộc 9router |
| Q10 | ASR chấm bằng **canary** (domain/cụm từ/mã giả do attacker cài) trước, LLM judge chỉ phụ trợ + kiểm tay mẫu | Tôi | Tránh độ không tin cậy của judge (plan v1 §1.1 #5) |
| Q11 | Tiếng Việt là chính (web 100% tiếng Việt); tiếng Anh qua BIPIA/JBB | Tôi | |

Câu còn mở (không chặn việc bắt đầu; mặc định đề xuất trong ngoặc):

- O1. Ngày nộp/bảo vệ chính xác? (giả định: sau 07/12/2026)
- O2. HF account đã chấp nhận license Llama để tải Prompt Guard 2 chưa? (Nếu chưa: bạn tự bấm "Agree". Agent không làm thay được. Trong lúc chờ thì dùng deberta.)
- O3. Có muốn gắn dashboard vào trang admin Next.js không? (Mặc định: không, Streamlit riêng.)

---

## 5. Chia việc cho agent

| Phần | File | Agent đề xuất | Repo / thư mục | Chạy song song với |
| --- | --- | --- | --- | --- |
| **A** Hoàn thiện web | `A-hoan-thien-web.md` | Agent 1 (vd. Antigravity) | `Agenttic-RAG-for-e-commerce` (nhánh `feat/web-hoan-thien`) | B1–B8, C1 |
| **B** Guardrails | `B-guardrails.md` | Agent 2 (vd. Codex) | `FOX-Guardrails` | A, C1 |
| **C** Dữ liệu & thực nghiệm | `C-du-lieu-va-thuc-nghiem.md` | Agent 3, hoặc Agent 2 sau B6 | `FOX-Guardrails/eval` | C1 từ tuần 1; C2–C4 sau khi B6 và A xong |
| Tấn công & phòng thủ (tham khảo chung) | `01-tan-cong-va-phong-thu.md` | Mọi agent đọc | — | — |
| Học & vấn đáp | `D-hoc-va-van-dap.md` | **Bạn** | — | Suốt 4 tuần |

**Hợp đồng giữa A và B** (để hai agent không giẫm chân nhau):

1. B **không sửa** code web cho tới gói B9. Đến B9 thì chỉ sửa đúng 3 điểm hook + 1 file client (`rag-service/src/guard_client.py`), trên nhánh riêng, sau khi A đã merge A1–A4.
2. A **không viết logic guard** trong web. Phần `_mask_pii_address` + thẻ `<untrusted_customer_note>` hiện có được giữ lại **sau cờ cấu hình** làm arm "chỉ prompt" (G1) để so sánh.
3. A cung cấp cho B và C: script seed dữ liệu bench (A7), tài khoản test, và cách bật/tắt guard bằng biến môi trường `FOX_GUARD_MODE=off|inproc|sidecar` và `FOX_GUARD_ARM=<tên arm>` (A cài sẵn điểm đọc biến, B9 cắm logic).
4. Nội dung tấn công (payload) do C viết (`eval/datasets/vi_cskh/*.jsonl`). A chỉ viết **cơ chế** nạp vào DB.

---

## 6. Lịch (gợi ý; 03/11 → 07/12/2026)

Giả định: bạn có khoảng 15–20 giờ/tuần, cộng thêm vài buổi ban ngày remote; agent làm song song.

| Tuần | Phần A (web) | Phần B (guard) | Phần C (dữ liệu/thực nghiệm) | Việc của **bạn** | Mốc kiểm (gate) |
| --- | --- | --- | --- | --- | --- |
| **T1** 03–09/11 | A0 chạy local, A1 sửa lỗi nền, A2 thanh toán, A3 ghi chú đơn + form review | B0 khung repo, B1 contract, B2 chuẩn hoá, B3 luật PI | C1 tải BIPIA/JBB, viết generator bộ CSKH tiếng Việt | Đọc `01-…` + survey §2–3 + BIPIA; tải PG2 (O2) | Cuối T1: web chạy local + 1 đơn Stripe test có webhook; `fox_guard.check_input` bắt được 6 ca evidence Unicode |
| **T2** 10–16/11 | A4 tool `product_reviews` + `create_support_ticket`, A5 log/ticket thật, A6 render link an toàn, A7 seed bench | B4 classifier, B5 PII đầy đủ, B6 policy + audit, B7 sidecar | C1 chốt bộ dữ liệu + split; C2 chạy detector-level lần 1 | Gán tay/kiểm 10% mẫu (học nhãn); chốt ngưỡng cùng agent | **Gate T2:** có bảng P/R/F1/FPR detector-level cho R, M, H. Nếu chưa có thì cắt B8 và F3 |
| **T3** 17–23/11 | A8 (nếu dư): sửa nhỏ theo yêu cầu B9 | B9 cắm vào web, B10 dashboard, B8 proxy (song song), F3 judge | C3 chạy end-to-end lần 1 (kịch bản tối thiểu) | Chạy demo end-to-end tự tay; viết chương 1–2 báo cáo | Cuối T3: demo 5 kịch bản (D §4) chạy được; có số ASR G0 vs G4 |
| **T4** 24–30/11 | Đóng băng web | Sửa lỗi, tối ưu độ trễ | C3 chạy đầy đủ + lặp 3 lần arm chính; C4 bảng/biểu đồ | Viết chương 3–5; slide | Cuối T4: bản báo cáo đủ chương + slide nháp |
| **Đệm** 01–07/12 | — | — | Chạy bù | Tập vấn đáp (D §3), tập demo | — |

**Thứ tự cắt khi trễ** (cắt từ trên xuống, không cắt phần in đậm):

1. B8 proxy, chỉ giữ một demo nhỏ "đổi `base_url`" bằng curl.
2. F3 LLM judge, ghi là hướng phát triển.
3. Lặp 3 lần → còn 1 lần, kèm khoảng tin cậy Wilson.
4. A8 và mọi tính năng web ngoài danh sách.
5. **Không cắt:** F1 + F2 + PII + policy 4 hành động + audit đã che + cắm vào web + dashboard + BIPIA/JBB/bộ tiếng Việt báo cáo riêng.

---

## 7. Rủi ro chính

| Rủi ro | Dấu hiệu | Cách xử lý |
| --- | --- | --- |
| Rate limit Gemini/Groq free làm chậm thực nghiệm end-to-end | 429 liên tục | Web đã có xoay vòng key; chạy đêm; dùng kịch bản tối thiểu (C §3.4); cache kết quả theo `case_id × arm` |
| Prompt Guard 2 yếu trên tiếng Việt | Recall VI thấp trên dev | Luật VI + view không dấu bù lại; báo cáo đúng số (đây cũng là một phát hiện); nếu dư thời gian thì fine-tune nhẹ (B4, mức "có thể") |
| FPR cao trên ghi chú giao hàng hợp lệ | Hard-benign bị chặn | Không chặn context theo classifier đơn lẻ; context chỉ cắt đoạn khi rủi ro `high` (luật tất định hoặc ≥ 2 tín hiệu) (`B-guardrails.md` B6.1–B6.3) |
| Hai agent sửa trùng file web | Conflict khi merge | Hợp đồng §5; B9 làm sau khi A merge |
| Bạn không kịp hiểu code agent viết | Không giải thích được khi vấn đáp | Mỗi gói đều có mục "bạn phải giải thích được" (D §2); agent phải viết README ngắn cho mỗi module |
| Số liệu bị "tự chấm bài mình" (bộ test do chính mình sinh) | Điểm cao bất thường | Báo cáo riêng BIPIA/JBB (ngoài) và bộ tự xây; split theo template; khai báo rõ giới hạn |

---

## 8. Tiêu chí "xong đồ án"

- [ ] `pip install -e .` cài được FOX-Guard; `fox-guard serve` chạy sidecar; có ví dụ 10 dòng tích hợp.
- [ ] Web e-commerce bật/tắt guard bằng biến môi trường; 5 kịch bản demo chạy được.
- [ ] Dashboard hiển thị cảnh báo, cho duyệt `review`, có thống kê và kết quả thực nghiệm.
- [ ] Log không chứa PII thô (có test tự động).
- [ ] Ba bảng kết quả riêng: BIPIA (EN, gián tiếp), JailbreakBench (EN, trực tiếp), CSKH tiếng Việt (gián tiếp + trực tiếp + PII). Mỗi bảng có R / M / H (/ J), FPR, ASR trước/sau, rò PII trước/sau, độ trễ, chi phí.
- [ ] Báo cáo có mục giới hạn trung thực (§2.3) và bạn trả lời được các câu ở `D-hoc-va-van-dap.md` §3.

---

## 9. Mục lục tài liệu

| File | Nội dung | Ai đọc |
| --- | --- | --- |
| `00-tong-quan.md` | File này | Tất cả |
| `01-tan-cong-va-phong-thu.md` | Dòng thời gian các vụ tấn công 2022–2026, phân loại kỹ thuật, ví dụ CSKH, bản đồ phòng thủ | Tất cả |
| `A-hoan-thien-web.md` | Gói A0–A8 cho agent làm web | Agent A |
| `B-guardrails.md` | Gói B0–B10 cho agent làm guard | Agent B |
| `C-du-lieu-va-thuc-nghiem.md` | Dữ liệu, arm, chỉ số, quy trình chạy | Agent C, bạn |
| `D-hoc-va-van-dap.md` | Lộ trình hiểu theo tuần, câu hỏi hội đồng, kịch bản demo | Bạn |
| `../research/` | Survey 2602.10453, bản đồ phương pháp, phân loại paper CSKH, 23 paper | Tham khảo |
| `../archive/` | Plan v1 và bản trùng | Chỉ tra cứu |
| `../../hermess/` | Research thô (không commit) | Tra số liệu gốc |
