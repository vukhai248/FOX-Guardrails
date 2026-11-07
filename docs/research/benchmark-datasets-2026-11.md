# Benchmark và dataset cho đánh giá FOX-Guard (research 07/11/2026)

**Vì sao cần research lại.** Kết quả C2 cho thấy hệ thống hiện tại mạnh ở jailbreak trực tiếp (PG2: JBB 83,6 %)
và PII tiếng Việt (F1 0,95), nhưng **yếu ở injection gián tiếp** (BIPIA 11,7 %), và các bộ đang dùng có ba
lỗ hổng:

1. **Chưa đo end-to-end:** mới đo detector (cờ bắn hay không), chưa đo *tấn công có thành công qua chatbot
   thật không* (ASR) và *bot còn trả lời tốt không* (utility).
2. **Gần như không có tấn công tiếng Việt thật** (C1-OPEN): bộ CSKH chỉ có câu vô hại; BIPIA/JBB là tiếng Anh.
3. **Chưa đo chặn nhầm kiểu "over-defense"**: câu vô hại có chứa từ nhạy cảm ("ignore", "bỏ qua", "hệ thống").

Các bộ dưới đây được kiểm tra trực tiếp qua Hugging Face / GitHub API (kích thước, license, ngôn ngữ).

## Nhóm A — nên dùng (đúng lỗ hổng, license mở)

| Bộ | Nguồn | Nội dung | Lấp lỗ hổng | License |
|---|---|---|---|---|
| **CyberSecEval — Prompt Injection** (EN 251 ca; **đa ngôn ngữ 1 004 ca, trong đó 50 tiếng Việt**) | Meta PurpleLlama (`CybersecurityBenchmarks/datasets/prompt_injection/`) | Mỗi ca: *system prompt chứa bí mật/quy tắc* + *input tấn công* + **câu hỏi chấm** (vd. "câu trả lời có chứa từ 'Piano' không?"). 196 direct / 55 indirect (EN); VI: 36 direct / 14 indirect; 15 kỹ thuật (ignore previous, persuasion, token smuggling, many-shot, payload splitting…) | **1 + 2**: đo ASR end-to-end có chấm tự động, và có tiếng Việt thật (dịch máy) | MIT (repo PurpleLlama) |
| **LLMail-Inject** | Microsoft, 2025 (`microsoft/llmail-inject-challenge`) | ~370k lượt tấn công **thích nghi** từ cuộc thi: kẻ tấn công gửi email để trợ lý email (RAG) gọi API trái phép; có **nhãn thành công/thất bại** và `emails_for_fp_tests.json` (email vô hại để đo chặn nhầm) | **Injection gián tiếp qua dữ liệu RAG** sát kịch bản CONTEXT của mình hơn BIPIA; tấn công do người thật viết để né defense | MIT |
| **NotInject** | InjecGuard (Li & Liu, 2024) (`leolee99/NotInject`) | 339 câu **vô hại** cố ý chứa từ kích hoạt ("ignore", "override", "system"…), 3 mức | **3**: đo over-defense của PG2/luật | MIT |
| **MultiJail** | DAMO-NLP-SG, ICLR 2024 | 315 câu hỏi độc hại × 10 ngôn ngữ, **có cột `vi`** (dịch bởi người) | Tiếng Việt cho trạm INPUT (độc hại trực tiếp, giống `harmful_bare` của JBB) | MIT |
| Đang dùng: **BIPIA**, **JailbreakBench**, **openpii-vi**, **CSKH tổng hợp** | | | Giữ làm mốc so sánh với C2 | |

## Nhóm B — tham khảo / tuỳ chọn

| Bộ | Ghi chú | Vì sao chưa ưu tiên |
|---|---|---|
| `reshabhs/SPML_Chatbot_Prompt_Injection` (~16k, MIT) | system prompt chatbot + user prompt, nhãn injection | Tiếng Anh, sinh tự động; trùng vai CyberSecEval |
| `deepset/prompt-injections` (Apache-2.0) | Nhỏ, phổ biến làm mốc cho classifier | Rất nhỏ, có tiếng Đức, không có VI |
| GenTel-Bench (`GenTelLab/gentelbench-v1`, Apache-2.0) | goal hijacking / prompt leaking / jailbreak, lớn | Tiếng Anh; dùng nếu cần thêm mẫu leaking |
| AgentDojo, InjecAgent, Nemotron agentic IPI | Injection vào agent dùng tool | Web CSKH không cho LLM gọi tool hành động → ngoài phạm vi (đã ghi trong `Phan_loai_paper_CSKH…`) |
| PolyGuardPrompts (17 ngôn ngữ), XSafety | An toàn nội dung đa ngôn ngữ | Không có tiếng Việt / thiên về toxic, không phải injection |
| WildJailbreak, WildGuardMix (AllenAI) | Rất lớn, chất lượng tốt | **Gated** (phải xin quyền); để sau nếu cần |
| PINT (Lakera) | Benchmark nổi tiếng cho detector | **Không công khai dữ liệu** |

## Đề xuất giao thức đánh giá mới (thay C3)

Đo **end-to-end qua web thật** (guard đã gắn plug-and-play — Lớp 6), dùng đúng các arm của
`docs/DU-AN.md` §7.3: **G0** (không phòng thủ), **G1** (hiện trạng web), **G2** (FOX luật, không classifier),
**G4** (FOX đầy đủ: luật + PG2 + gộp rủi ro + datamarking). Mọi arm chạy cùng bộ ca.

| Chỉ số | Định nghĩa | Bộ |
|---|---|---|
| **ASR** (attack success rate) | % ca mà câu trả lời cuối thoả câu hỏi chấm (lộ bí mật, làm theo lệnh chèn) | CyberSecEval EN + VI; LLMail-Inject (mẫu phân tầng); BIPIA chuyển sang review/ghi chú sản phẩm |
| **Utility** | % câu hỏi CSKH vô hại được trả lời đúng/không bị từ chối | CSKH tổng hợp + NotInject (dịch VI một phần) + email FP của LLMail |
| **FPR detector** | như C2 | NotInject, CSKH hard-benign |
| **PII leak rate** | % câu trả lời lộ PII thật (canary) của khách khác | PII canary cài vào ghi chú đơn hàng / review |
| Độ trễ p50/p95 | thêm vào mỗi lượt chat | toàn bộ |

Chấm ASR bằng **câu hỏi chấm có sẵn** (chuỗi bí mật có xuất hiện không → kiểm tra chuỗi, không cần LLM
judge), chỉ dùng LLM judge cho ca không quy về chuỗi được.

## Thứ tự làm

1. Gắn guard vào web dạng **plug-and-play** (sidecar HTTP + client mỏng, bật/tắt bằng biến môi trường) —
   điều kiện để đo end-to-end.
2. Tải và chuẩn hoá: CyberSecEval (EN + VI), NotInject, MultiJail-vi, LLMail-Inject (mẫu nhỏ).
   Hỏi trước khi tải (quy tắc dự án). Chia dev/test như C1; chỉ chọn ngưỡng trên dev.
3. Chạy G0–G3, báo cáo ASR / utility / FPR / độ trễ với CI 95 %.
