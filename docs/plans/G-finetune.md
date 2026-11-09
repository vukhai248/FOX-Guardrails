# G — Fine-tune model cho FOX-Guard (đóng góp KHMT)

> Viết 09/11/2026 sau C4. Trạng thái: **kế hoạch, chưa làm**. Mọi bộ dữ liệu dưới đây đã kiểm metadata
> (licence, kích thước, gated) qua Hugging Face / GitHub API ngày 09/11; **chưa tải gì**.

## 1. Vì sao fine-tune

Kết quả C2–C4 (`eval/reports/SUMMARY.md`) cho thấy dùng model có sẵn chỉ cao ở đúng phân phối nó được huấn luyện:

| Chỗ yếu | Số hiện tại | Nguyên nhân |
| --- | --- | --- |
| Injection gián tiếp "giao việc" (BIPIA) | PG2 recall 11,7 % | PG2 bắt ý đồ ghi đè, không bắt "việc lạc đề" chèn trong dữ liệu |
| Tiếng Việt | chưa có bộ tấn công VI thật; CyberSecEval VI dịch máy 50 ca | PG2 không huấn luyện tiếng Việt (danh sách ngôn ngữ trên model card: cần xác nhận lại) |
| Over-defence | NotInject 15 %, JBB vô hại 20 % | thiên lệch theo từ kích hoạt |
| Trạm OUTPUT chỉ có luật | C3-5, C3-6; vi phạm logic không giảm (11 → 12/84) | luật từ vựng đã chạm giới hạn |
| E2E | ASR 21,6 → 16,6 %, G4 vs G2 p = 0,121 | classifier yếu ở các kỹ thuật thuyết phục / định dạng |

Đóng góp dự kiến: **(1) bộ dữ liệu prompt injection tiếng Việt cho CSKH thương mại điện tử** (chưa có bộ công khai
nào — tìm trên HF 09/11 không ra), **(2) model phát hiện injection VI–EN fine-tune có xử lý over-defence**,
**(3) model kiểm đầu ra**, cùng ablation so với PG2, deberta, PIGuard và luật.

## 2. Các model ("được đến đâu hay đến đó", theo thứ tự ưu tiên)

| # | Model | Trạm | Nhãn | Nền đề xuất | Ghi chú |
| --- | --- | --- | --- | --- | --- |
| **M1** | Injection classifier VI–EN | INPUT + CONTEXT | benign / injection | PG2 86M (mDeBERTa) **và** mDeBERTa-v3-base gốc để so | đóng góp chính |
| **M2** | Output checker | OUTPUT | ok / đòi bí mật / lộ dữ liệu / làm theo lệnh chèn | cùng nền M1 | thay phần từ vựng của Lớp 4 ở ca khó |
| M3 | Model nhỏ tiếng Việt | INPUT + CONTEXT | như M1 | PhoBERT-base hoặc ViSoBERT | so "đa ngôn ngữ vs chuyên tiếng Việt" |
| M4 | Judge LLM nhỏ (tuỳ chọn) | OUTPUT (ca `review`) | có/không vi phạm + lý do | Qwen 1.5–3B, LoRA trên A100 | chỉ khi M1–M2 xong |
| M5 | Multi-task (tuỳ chọn) | cả 3 | gộp nhãn M1 + M2 | một encoder, nhiều head | giảm độ trễ/bộ nhớ |

Phần cứng: 2 tài khoản Kaggle (~60 giờ GPU/tuần) + Colab Pro A100 80 GB. Model 86–300M train full fine-tune vài phút
đến dưới 1 giờ/lần; đủ chạy 3 seed cho mỗi cấu hình. Suy luận vẫn phải chạy được trên GTX 1650 (mục tiêu p95 ≤ 300 ms).

## 3. Dữ liệu

### 3.1 Nguồn có sẵn (đã kiểm 09/11)

Vai trò: **T** = được dùng để train, **D** = dev (chọn ngưỡng, early stop), **E** = chỉ để đánh giá, cấm train.

| Bộ | Loại | Licence | Cỡ | Vai trò | Ghi chú |
| --- | --- | --- | --- | --- | --- |
| PIGuard `train.json` (github leolee99/PIGuard) | tấn công + vô hại, gộp 20 nguồn + dữ liệu MOF | MIT | 43 MB | T | **không dùng `valid.json`** (chứa NotInject, BIPIA); phải lọc trùng với bộ E |
| deepset/prompt-injections | injection EN/DE | Apache-2.0 | < 1k | T | |
| xTRam1/safe-guard-prompt-injection | injection | chưa ghi | 10–100k | T? | cần xem licence trong card |
| reshabhs/SPML_Chatbot_Prompt_Injection | injection vào chatbot có system prompt | MIT | 10–100k | T | gần bối cảnh CSKH |
| Lakera/gandalf_ignore_instructions, mosscap | tấn công đòi mật khẩu | MIT | 1k / 100k+ | T | hợp bài "đòi bí mật" |
| jackhhao/jailbreak-classification | jailbreak / benign | Apache-2.0 | 1–10k | T | |
| TrustAIRLab/in-the-wild-jailbreak-prompts | jailbreak thật | MIT | 10–100k | T | |
| neuralchemy/Prompt-injection-dataset | injection | Apache-2.0 | 10–100k | T | |
| allenai/wildjailbreak | tấn công đối kháng + **vô hại đối chứng** | ODC-BY | gated | T | bạn phải tự bấm đồng ý điều khoản |
| allenai/wildguardmix | prompt + **response** có nhãn hại / từ chối | ODC-BY | gated | T (M2) | nguồn chính cho M2 |
| nvidia/Aegis-AI-Content-Safety-Dataset-2.0 | prompt + response an toàn | CC-BY-4.0 | 10–100k | T (M2) | |
| nvidia/Nemotron-RL-Agentic-Indirect-Prompt-Injection-v1 | injection gián tiếp qua tool | CC-BY-4.0 | 1–10k | T | gần bài "review độc" |
| microsoft/BIPIA **train** split | injection gián tiếp | (repo) | | T | **chỉ split train**; split test là E |
| microsoft/llmail-inject-challenge **Phase 1** | email tấn công thích nghi | MIT | 100k+ | T | Phase 2 mẫu 600 đang là E → giữ nguyên là E |
| GitHub microsoft/TaskTracker | task drift / injection gián tiếp | MIT | lớn | T | |
| GitHub uiuc-kang-lab/InjecAgent, liu00222/Open-Prompt-Injection | injection qua tool / tổng hợp | MIT | | T hoặc E | chọn một vai trò, ghi rõ |
| hackaprompt/hackaprompt-dataset | 600k lượt tấn công | MIT | gated | T | |
| ai4privacy/open-pii-masking-500k | PII | "other" | | T (M2 lộ dữ liệu) | đọc licence trước |
| 5CD-AI/Vietnamese-Ecommerce-Multi-turn-Chat | hội thoại TMĐT tiếng Việt | Apache-2.0 | 1–10k | T (vô hại VI) | |
| ura-hcmut/Vietnamese-Customer-Support-QA (CSConDa) | CSKH tiếng Việt | CC-BY-NC-4.0, gated | 1–10k | T (vô hại VI) | phi thương mại: dùng được cho đồ án |
| Bộ toxic tiếng Việt (ViHSD, thach124/…) | câu độc hại VI | Apache / chưa rõ | | T (vô hại-khó / phân biệt) | không phải injection |
| PKU-Alignment/BeaverTails | QA an toàn | **CC-BY-NC** | 300k | T (M2) | phi thương mại |
| **Đang là bộ đánh giá — cấm train** | | | | | |
| JBB, BIPIA test, CyberSecEval (EN + VI), NotInject, LLMail Phase 2 mẫu, MultiJail, CSKH test C1, held-out từng lớp | | | | **E** | |
| PINT (Lakera) | benchmark ẩn | xin quyền | | E (tuỳ chọn) | để so với PIGuard trên cùng thước |

Không dùng: `Necent/llm-jailbreak-prompt-injection-dataset` (gộp 30+ nguồn, có VI, nhưng gated và không rõ đã gộp
các bộ E chưa → rủi ro rò dữ liệu); PolyGuardMix (17 ngôn ngữ, **không có tiếng Việt**).

### 3.2 Tự xây: FOX-VI (phần đóng góp dữ liệu)

Không có bộ injection tiếng Việt công khai, nên phải dựng. Mục tiêu ~6–10k mẫu, cân bằng nhãn:

| Phần | Cách làm | Nhãn |
| --- | --- | --- |
| VI-ATK-direct | dịch có kiểm tay + viết lại theo văn phong VI các mẫu T (không phải E) theo đủ kỹ thuật: bỏ qua hướng dẫn, nhập vai, giả system, thuyết phục, ép định dạng, chia nhỏ payload, teencode / bỏ dấu / chèn ký tự | injection |
| VI-ATK-indirect | chèn lệnh vào **review, mô tả sản phẩm, ghi chú đơn, email** thật của shop thử nghiệm (giống luồng `product_reviews`), nhiều vị trí (đầu / giữa / cuối), nhiều độ dài | injection |
| VI-HARD-benign | câu CSKH **vô hại có từ kích hoạt** ("bỏ qua bước này", "hệ thống báo lỗi", "quên mật khẩu thì làm sao", "đổi vai trò tài khoản") — theo ý tưởng NotInject, nhưng tự viết, không chép NotInject | benign |
| VI-benign | câu hỏi CSKH thường (CSConDa, 5CD-AI e-commerce, câu web thật đã ẩn danh) | benign |
| VI-OUT (cho M2) | câu trả lời của bot: thường / từ chối / đòi OTP-mật khẩu-CCCD / lộ PII người khác / làm theo lệnh chèn (gửi link ngoài, quảng cáo lạc đề) | 4 nhãn M2 |

Sinh dữ liệu: dùng **Gemini hoặc model chạy local / Colab** (Q28: không gửi prompt tấn công qua TokenHarbor).
Mỗi mẫu sinh ra có mã nguồn + kỹ thuật (T-code) + seed. **Bạn duyệt một mẫu ngẫu nhiên** (đề xuất 300 câu) và ghi
tỉ lệ nhãn sai; nếu > 5 % thì sửa prompt sinh rồi sinh lại.

Chống rò dữ liệu (bắt buộc, có test tự động):
- Khử trùng gần giống (MinHash / n-gram 8, ngưỡng Jaccard 0,8) giữa **mọi** tập T và **mọi** tập E; báo cáo số mẫu bị loại.
- Chia FOX-VI theo **khuôn mẫu sinh / kỹ thuật**, không theo câu: một khuôn chỉ nằm ở một trong train / dev / test.
- Ngưỡng chọn trên dev; test chạy **một lần** cho mỗi model đã chốt (như C2).

## 4. Phương pháp fine-tune

1. **Baseline**: PG2 zero-shot (đang dùng), deberta-protectai, **PIGuard** (mới thêm), luật R.
2. **M1-a**: fine-tune toàn bộ PG2 86M trên T(EN) + FOX-VI train. Cross-entropy có trọng số lớp, lr 2e-5, 3–5 epoch, early stop theo PR-AUC dev.
3. **M1-b**: như M1-a nhưng nền mDeBERTa-v3-base gốc (không kế thừa PG2) → tách đóng góp của "khởi tạo từ PG2".
4. **M1-c (chống over-defence)**: thêm VI-HARD-benign + chiến lược MOF của PIGuard (mẫu vô hại chứa từ kích hoạt
   được sinh tự động từ chính các từ mà model đang thiên lệch) → đo trên NotInject (E) và VI-HARD test.
5. **M3**: PhoBERT / ViSoBERT trên FOX-VI → so đa ngôn ngữ và chuyên tiếng Việt.
6. **M2**: cùng quy trình, 4 nhãn, dữ liệu WildGuardMix / Aegis (response) + VI-OUT + câu trả lời thật C3 (`raw_response` đã lưu).
7. Tuỳ chọn: **distill** M1 sang model nhỏ hơn (PG2 22M) để giảm độ trễ CPU; **M4** LoRA cho judge LLM nhỏ.

Mỗi cấu hình chạy **3 seed**, báo cáo trung bình ± độ lệch chuẩn. Ghi cấu hình + hash dữ liệu vào `eval/reports/ft_*.json`.
Tích hợp: thay `classifier.primary` trong `fox-guard.yaml` (đã có sẵn khe), M2 thêm vào trạm OUTPUT; policy B6.1 giữ nguyên
(classifier một mình chỉ `review`) trừ khi số đo cho phép đổi.

## 5. Chỉ số

**Mức detector** (từng tập E, tách theo ngôn ngữ và kỹ thuật):
- Recall (TPR), FPR, Precision, F1 — kèm CI Wilson 95 %.
- **PR-AUC và ROC-AUC** (không phụ thuộc ngưỡng — so model công bằng).
- **TPR @ FPR = 1 % và 5 %** (chuẩn của guard model: chặn nhầm phải rất thấp).
- **Over-defence accuracy** trên NotInject và VI-HARD (theo cách báo cáo của PIGuard: benign / malicious / over-defence, và trung bình ba số).
- **ECE** (độ hiệu chỉnh xác suất) — vì policy dùng ngưỡng θ_low / θ_high.
- McNemar từng cặp model trên cùng ca (đã có trong `eval/summary.py`).

**Mức hệ thống**:
- E2E: ASR G0 / G2 / G4 / **G5 (M1 + M2)**, McNemar, theo nhóm trực tiếp / gián tiếp / VI / vi phạm logic.
- **Utility** (C3-4): bộ câu CSKH vô hại qua G0 vs G5 — tỉ lệ bị chặn / `review` và chất lượng trả lời (judge + kiểm tay mẫu).
- Độ trễ p50 / p95 trên GTX 1650 và CPU; kích thước model; số tham số.

**Mức dữ liệu** (cho chương dữ liệu): số mẫu theo nguồn / kỹ thuật / nhãn; tỉ lệ nhãn sai khi bạn duyệt; số mẫu bị loại vì trùng.

## 6. Lịch đề xuất (hạn ~07/12)

| Tuần | Việc | Kết quả |
| --- | --- | --- |
| 10–16/11 | Tải + lọc T (EN), dựng FOX-VI v1 (sinh + bạn duyệt 300 câu), script khử trùng + chia; baseline PIGuard | dữ liệu khoá, báo cáo dữ liệu |
| 17–23/11 | M1-a/b/c, M3 trên Kaggle/Colab, 3 seed; chọn ngưỡng dev; test một lần | bảng M1 vs baseline |
| 24–30/11 | M2 + tích hợp G5 + e2e + utility; (tuỳ chọn) distill / M4 | bảng E2E G5 |
| 01–07/12 | Viết báo cáo, slide, dashboard demo | |

Nếu chậm: cắt M4, M5, M3 trước; M1 + FOX-VI là phần không được cắt.

## 7. Cần bạn quyết

1. Đồng ý **giữ nguyên các bộ E hiện tại là cấm train** (để số C2–C4 còn so được)?
2. Bấm đồng ý điều khoản các bộ gated: wildjailbreak, wildguardmix, hackaprompt, CSConDa (tài khoản HF của bạn).
3. Bạn duyệt mẫu FOX-VI (300 câu) — hay muốn người khác duyệt chéo để có độ đồng thuận (Cohen's κ)?
4. Model nào báo cáo là "của đồ án": M1-a (từ PG2, licence Llama 4 — phải ghi "Built with Llama") hay M1-b (mDeBERTa, MIT)?
