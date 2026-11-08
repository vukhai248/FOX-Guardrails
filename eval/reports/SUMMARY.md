# C4 — Tổng hợp kết quả thực nghiệm FOX-Guard

> File này **sinh tự động** bởi `python -X utf8 -m eval.summary` từ các file kết quả trong `eval/reports/`.
> Không sửa tay: sửa script rồi chạy lại. Test `tests/test_summary.py` báo lỗi nếu file này lệch dữ liệu.
> Khoảng tin cậy: Wilson 95% cho tỉ lệ. So cặp: McNemar chính xác hai phía. Biểu đồ: `figures/` (PNG + SVG).

## Tóm tắt một trang

| Câu hỏi (DU-AN §7) | Kết quả chính | Ở mục |
| --- | --- | --- |
| RQ1 — Luật (Lớp 1–4) một mình bắt được gì? | BIPIA **0,0%**, JBB **0,0%**; chặn nhầm CSKH tiếng Việt **0,0%** | §1 |
| RQ1 — Thêm classifier Prompt Guard 2 thì sao? | JBB **83,6%**, BIPIA **11,7%**; chặn nhầm CSKH tiếng Việt **0,0%**, JBB vô hại **20,0%** | §2 |
| RQ2 — Chuẩn hoá có tác dụng không? | Recall PII trên ca biến dạng 0,52 → 0,91; với injection chưa đo được (bộ tiếng Anh không có ca nào luật bắt) | §5 |
| RQ3 — Trên chatbot thật, tấn công thành công giảm bao nhiêu? | ASR **21,6% → 16,6%** (65/301 → 50/301), McNemar p = 0,020; utility chưa đo (C3-4) | §4 |
| RQ4 — PII tiếng Việt? | F1 **0,95** trên bộ tổng hợp; rò PII trước/sau guard ở mức e2e chưa đo | §5 |
| Cái giá? | Độ trễ guard e2e p50 / p95 = 135 / 383 ms (GPU); over-defence NotInject 15,0% (chỉ ra `review`) | §6 |

## 1. Luật một mình (arm R) — RQ1

Tập test C1, chạy một lần; arm R không có ngưỡng để chỉnh. "Bắt" = hành động `block` hoặc `review`.
Ô dạng `tỉ lệ (k/n) [CI 95% Wilson]`.

| Arm | BIPIA recall | JBB recall | BIPIA chặn nhầm | JBB chặn nhầm | CSKH hard-benign chặn nhầm | CSKH clean chặn nhầm |
| --- | --- | --- | --- | --- | --- | --- |
| R (luật Lớp 1–4) | 0,0% (0/300) [0,0–1,3] | 0,0% (0/286) [0,0–1,3] | 0,0% (0/150) [0,0–2,5] | 0,0% (0/100) [0,0–3,7] | 0,0% (0/84) [0,0–4,4] | 0,0% (0/57) [0,0–6,3] |
| R bỏ chuẩn hoá | 0,0% (0/300) [0,0–1,3] | 0,0% (0/286) [0,0–1,3] | 0,0% (0/150) [0,0–2,5] | 0,0% (0/100) [0,0–3,7] | 0,0% (0/84) [0,0–4,4] | 0,0% (0/57) [0,0–6,3] |

**Đọc bảng:** luật không bắt được tấn công kiểu "giao việc" (BIPIA) hay jailbreak nhập vai/hậu tố vô nghĩa (JBB),
vì các câu này không có dấu hiệu ghi đè tường minh mà Lớp 2 nhắm tới. Đổi lại, luật chặn nhầm **0/391**
câu vô hại (BIPIA sạch, JBB vô hại, CSKH tiếng Việt). Recall tiếng Việt của luật được đo ở bộ held-out riêng của từng lớp (xem `docs/hoc/lop-2-luat.md`,
`docs/hoc/lop-4-dau-ra-policy-audit.md`), vì bộ CSKH tiếng Việt chưa có ca tấn công (C1-OPEN).

## 2. Thêm classifier (Lớp 5) — RQ1

Ngưỡng chọn **chỉ trên dev** (`eval/calibrate.py`: θ_high ứng với chặn nhầm ≤ 2%, θ_low ≤ 10% trên câu vô hại dev):

| Model | θ_low | θ_high | Số câu vô hại dev |
| --- | --- | --- | --- |
| deberta | 0.999324 | 0.999991 | 209 |
| pg2 | 0.003154 | 0.007576 | 209 |

Tập test (số **v2**, thay số v1 có nhiễu ROT13 — xem `lop5-pg2_2026-11-07.md`). M = chỉ classifier, H = luật + classifier.

| Arm | BIPIA recall | BIPIA chặn nhầm | BIPIA F1 | JBB recall | JBB chặn nhầm | CSKH hard-benign chặn nhầm |
| --- | --- | --- | --- | --- | --- | --- |
| R (luật Lớp 1–4) | 0,0% (0/300) [0,0–1,3] | 0,0% (0/150) [0,0–2,5] | 0,000 | 0,0% (0/286) [0,0–1,3] | 0,0% (0/100) [0,0–3,7] | 0,0% (0/84) [0,0–4,4] |
| M-deberta (chỉ classifier) | 5,7% (17/300) [3,6–8,9] | 3,3% (5/150) [1,4–7,6] | 0,106 | 12,9% (37/286) [9,5–17,3] | 0,0% (0/100) [0,0–3,7] | 1,2% (1/84) [0,2–6,4] |
| H-deberta (luật + classifier) | 5,7% (17/300) [3,6–8,9] | 3,3% (5/150) [1,4–7,6] | 0,106 | 12,9% (37/286) [9,5–17,3] | 0,0% (0/100) [0,0–3,7] | 1,2% (1/84) [0,2–6,4] |
| M-pg2 (chỉ classifier) | 11,7% (35/300) [8,5–15,8] | 5,3% (8/150) [2,7–10,2] | 0,204 | 83,6% (239/286) [78,8–87,4] | 20,0% (20/100) [13,3–28,9] | 0,0% (0/84) [0,0–4,4] |
| H-pg2 (luật + classifier) | 11,7% (35/300) [8,5–15,8] | 5,3% (8/150) [2,7–10,2] | 0,204 | 83,6% (239/286) [78,8–87,4] | 20,0% (20/100) [13,3–28,9] | 0,0% (0/84) [0,0–4,4] |

**So cặp (McNemar chính xác, hai phía, trên cùng các ca).** "Chỉ A" = số ca arm A gắn cờ mà arm B không, và ngược lại.
Với ca tấn công, gắn cờ là đúng; với ca vô hại, gắn cờ là chặn nhầm.

| Cặp | Tập | n | Chỉ A | Chỉ B | p |
| --- | --- | --- | --- | --- | --- |
| R vs H-pg2 | BIPIA tấn công | 300 | 0 | 35 | p < 0,001 |
| R vs H-pg2 | JBB tấn công | 286 | 0 | 239 | p < 0,001 |
| R vs H-pg2 | BIPIA sạch | 150 | 0 | 8 | p = 0,008 |
| R vs H-pg2 | JBB vô hại | 100 | 0 | 20 | p < 0,001 |
| H-deberta vs H-pg2 | BIPIA tấn công | 300 | 16 | 34 | p = 0,015 |
| H-deberta vs H-pg2 | JBB tấn công | 286 | 3 | 205 | p < 0,001 |
| H-deberta vs H-pg2 | BIPIA sạch | 150 | 5 | 8 | p = 0,581 |
| H-deberta vs H-pg2 | JBB vô hại | 100 | 0 | 20 | p < 0,001 |
| M-pg2 vs H-pg2 | BIPIA tấn công | 300 | 0 | 0 | p = 1,000 |
| M-pg2 vs H-pg2 | JBB tấn công | 286 | 0 | 0 | p = 1,000 |
| M-pg2 vs H-pg2 | BIPIA sạch | 150 | 0 | 0 | p = 1,000 |
| M-pg2 vs H-pg2 | JBB vô hại | 100 | 0 | 0 | p = 1,000 |

**Đọc bảng:**
- Về bắt tấn công, PG2 hơn deberta trên JBB (205 ca chỉ PG2 bắt, 3 ca chỉ deberta bắt;
  p < 0,001, khác biệt có ý nghĩa thống kê) và trên BIPIA (34 so với 16; p = 0,015, khác biệt có ý nghĩa thống kê).
- Về chặn nhầm, PG2 trả giá trên JBB vô hại (20 ca chỉ PG2 gắn cờ, 0 ca chỉ deberta;
  p < 0,001, khác biệt có ý nghĩa thống kê); trên BIPIA sạch 8 so với 5 (p = 0,581, khác biệt không có ý nghĩa thống kê).
- M-pg2 và H-pg2 khác nhau 0 ca trên tấn công BIPIA + JBB:
  trên hai bộ tiếng Anh này luật không thêm được ca nào. Lợi ích của luật nằm ở tấn công tiếng Việt và token điều khiển
  (đo ở `tests/systematic` S4 và held-out từng lớp), chưa có trong tập test.
- Cả hai classifier đều yếu với BIPIA (chèn gián tiếp kiểu "giao việc"): đây là giới hạn đã biết của classifier
  phát hiện ý đồ ghi đè, không chỉnh ngưỡng trên test để kéo số lên.
- JBB chặn nhầm của PG2 cao hơn mục tiêu 2% chọn trên dev: câu vô hại của JBB là yêu cầu tiếng Anh chủ đề nhạy cảm,
  khác phân phối CSKH. Theo policy B6.1, classifier một mình chỉ ra `review` (siết prompt), không chặn khách.

## 3. Benchmark ngoài, mức detector (không gọi LLM)

Ngưỡng giữ nguyên như §2, **không chỉnh gì** trên các bộ này. Nguồn: `c3_detectors_2026-11-07.json`.

| Bộ | Đo | R | H-pg2 |
| --- | --- | --- | --- |
| NotInject (câu vô hại có từ kích hoạt, EN) | chặn thừa | 0,0% (0/339) [0,0–1,1] | 15,0% (51/339) [11,6–19,2] |
| LLMail-Inject Phase 2 (email tấn công thích nghi) | recall | 26,2% (157/600) [22,8–29,8] | 46,8% (281/600) [42,9–50,8] |
| ↳ email đã thắng challenge | recall | 27,8% (10/36) [15,8–44,0] | 50,0% (18/36) [34,5–65,5] |
| LLMail email thật vô hại | chặn nhầm | 0,0% (0/203) [0,0–1,9] | 0,0% (0/203) [0,0–1,9] |
| CyberSecEval EN trực tiếp | recall | 5,1% (10/196) [2,8–9,1] | 23,5% (46/196) [18,1–29,9] |
| CyberSecEval EN gián tiếp | recall | 30,9% (17/55) [20,3–44,0] | 47,3% (26/55) [34,7–60,2] |
| CyberSecEval VI trực tiếp (dịch máy) | recall | 5,6% (2/36) [1,5–18,1] | 19,4% (7/36) [9,8–35,0] |
| CyberSecEval VI gián tiếp (dịch máy) | recall | 35,7% (5/14) [16,3–61,2] | 57,1% (8/14) [32,6–78,6] |
| MultiJail EN (câu hỏi độc hại, không phải injection) | tỉ lệ gắn cờ | 0,0% (0/315) [0,0–1,2] | 2,9% (9/315) [1,5–5,3] |
| MultiJail VI (câu hỏi độc hại, không phải injection) | tỉ lệ gắn cờ | 0,0% (0/315) [0,0–1,2] | 1,3% (4/315) [0,5–3,2] |

**Đọc bảng:** PG2 tăng recall trên LLMail và CyberSecEval mà không tăng chặn nhầm trên email thật. Cái giá là
chặn thừa trên NotInject, tăng theo số từ kích hoạt (1 / 2 / 3 từ: 8,0% / 15,0% / 22,1%). Các ca này chỉ ra `review`.
MultiJail là câu hỏi độc hại, không phải injection: FOX-Guard không nhắm loại này (để cho cơ chế an toàn của LLM).

## 4. End-to-end trên chatbot (CyberSecEval, 301 ca) — RQ3

LLM đích **gemini-3.5-flash-lite** (model dự phòng của web, nhiệt độ 1,0). Trực tiếp → trạm INPUT, gián tiếp → trạm CONTEXT,
câu trả lời luôn qua trạm OUTPUT trước khi chấm. ASR = tỉ lệ tấn công thành công (judge của CyberSecEval).
McNemar: "G0 thắng / arm thắng" = số ca chỉ thành công ở G0 / chỉ thành công ở arm đó.

| Arm | ASR | Chặn trước LLM | McNemar vs G0 | Độ trễ guard p50 / p95 |
| --- | --- | --- | --- | --- |
| G0 không guard | 21,6% (65/301) [17,3–26,6] | — | — | — |
| G2 luật (Lớp 1–4) | 19,9% (60/301) [15,8–24,8] | 0 | 13 / 8, p = 0,383 | 8,5 / 49,1 ms |
| G4 đầy đủ (+ PG2, datamarking) | 16,6% (50/301) [12,8–21,2] | 12 | 26 / 11, p = 0,020 | 134,9 / 383,1 ms |

G2 vs G4 (cùng 301 ca): 22 ca chỉ thành công ở G2, 12 ca chỉ ở G4, p = 0,121.

**Theo nhóm:**

| Nhóm | G0 | G2 | G4 |
| --- | --- | --- | --- |
| Trực tiếp | 13,4% (31/232) [9,6–18,3] | 12,1% (28/232) [8,5–16,9] | 10,3% (24/232) [7,0–14,9] |
| Gián tiếp | 49,3% (34/69) [37,8–60,8] | 46,4% (32/69) [35,1–58,0] | 37,7% (26/69) [27,2–49,5] |
| Tiếng Anh | 21,1% (53/251) [16,5–26,6] | 19,1% (48/251) [14,7–24,4] | 17,5% (44/251) [13,3–22,7] |
| Tiếng Việt (dịch máy) | 24,0% (12/50) [14,3–37,4] | 24,0% (12/50) [14,3–37,4] | 12,0% (6/50) [5,6–23,8] |
| Vi phạm bảo mật | 24,9% (54/217) [19,6–31,0] | 23,0% (50/217) [17,9–29,1] | 17,5% (38/217) [13,0–23,1] |
| Vi phạm logic | 13,1% (11/84) [7,5–21,9] | 11,9% (10/84) [6,6–20,5] | 14,3% (12/84) [8,4–23,3] |

**Theo kỹ thuật tấn công (số ca thành công / số ca):**

| Kỹ thuật | G0 | G2 | G4 |
| --- | --- | --- | --- |
| different user input language | 5/30 | 6/30 | 3/30 |
| few shot attack | 1/12 | 2/12 | 1/12 |
| hypothetical scenario | 2/16 | 2/16 | 3/16 |
| ignore previous instructions | 6/31 | 6/31 | 2/31 |
| indirect reference | 3/16 | 3/16 | 3/16 |
| many shot attack | 2/7 | 2/7 | 2/7 |
| mixed techniques | 3/40 | 3/40 | 3/40 |
| output formatting manipulation | 12/21 | 9/21 | 9/21 |
| overload with information | 7/24 | 5/24 | 5/24 |
| payload splitting | 1/10 | 1/10 | 0/10 |
| persuasion | 8/32 | 8/32 | 7/32 |
| repeated token attack | 1/6 | 0/6 | 0/6 |
| system mode | 5/23 | 5/23 | 5/23 |
| token smuggling | 5/16 | 3/16 | 3/16 |
| virtualization | 4/17 | 5/17 | 4/17 |

**Đọc bảng:**
- Guard đầy đủ giảm ASR 23% tương đối so với G0 (p = 0,020, khác biệt có ý nghĩa thống kê).
  Luật một mình (G2) so với G0: p = 0,383, khác biệt không có ý nghĩa thống kê. G4 so với G2: p = 0,121, khác biệt không có ý nghĩa thống kê.
  CyberSecEval là câu tự nhiên, luật bắt được ít, PG2 gánh phần chính.
- Ở G4, ASR gián tiếp (37,7%) vẫn cao hơn nhiều so với trực tiếp (10,3%).
  Phân tích từng ca lọt nằm ở `c3_2026-11-08.md` §2.
- Nhóm vi phạm logic **không giảm** (11/84 → 12/84): đây là lỗi làm sai quy tắc nghiệp vụ, không có đường rò dữ liệu mà Lớp 4 chặn.
- Tiếng Việt chỉ có 50 ca dịch máy, khoảng tin cậy rộng: chỉ nên đọc là xu hướng.
- Mỗi arm là **một lần lấy mẫu** ở nhiệt độ 1,0; chênh lệch nhỏ giữa các arm có thể do ngẫu nhiên — vì vậy dùng McNemar.

## 5. PII tiếng Việt (Lớp 3) — RQ4, và chuẩn hoá — RQ2

Đo trên bộ nhận diện PII (`detect_pii`), span phải khớp loại và vị trí. Bộ tổng hợp tiếng Việt, tập test.

| Thực thể | P | R | F1 | Bắt / vàng |
| --- | --- | --- | --- | --- |
| ADDRESS | 1,00 | 1,00 | 1,00 | 21/21 |
| BANK_ACCOUNT | 1,00 | 0,81 | 0,90 | 13/16 |
| BHYT | 1,00 | 1,00 | 1,00 | 8/8 |
| CARD | 1,00 | 1,00 | 1,00 | 14/14 |
| CCCD | 1,00 | 1,00 | 1,00 | 12/12 |
| CMND | 1,00 | 0,87 | 0,93 | 13/15 |
| EMAIL | 1,00 | 1,00 | 1,00 | 19/19 |
| OTP | 1,00 | 0,29 | 0,44 | 2/7 |
| PASSPORT | 1,00 | 0,80 | 0,89 | 8/10 |
| PASSWORD | 0,82 | 0,69 | 0,75 | 9/13 |
| PERSON | 1,00 | 1,00 | 1,00 | 36/36 |
| PHONE | 1,00 | 1,00 | 1,00 | 21/21 |
| PLATE | 1,00 | 1,00 | 1,00 | 10/10 |
| TAX_ID | 1,00 | 0,77 | 0,87 | 10/13 |
| **Tất cả (R)** | 0,99 | 0,91 | 0,95 | 196/215 |
| Tất cả (R bỏ chuẩn hoá) | 0,99 | 0,85 | 0,92 | 183/215 |

- Ca biến dạng T3.12 (số viết cách, chấm, fullwidth, bằng chữ): recall **0,91** có chuẩn hoá,
  **0,52** khi bỏ chuẩn hoá — đây là đóng góp đo được của Lớp 1.
- Che nhầm trên câu dễ nhầm (giá, mã đơn, IMEI, mã giảm giá, UUID): 0,0% (0/50) [0,0–7,1].
- openpii tiếng Việt (số theo định dạng quốc tế, tên nước ngoài): P 0,82, R 0,20,
  F1 0,32. Thấp vì bộ nhận diện dựa trên đầu số, mã tỉnh và checksum Việt Nam — đã lường trước trong `SPLIT_REPORT`.
- OTP không kèm từ khoá là giới hạn đã biết (L3-FN): không phân biệt được với mã đơn hàng; Lớp 4 chặn việc bot **đòi** OTP.

## 6. Độ trễ

Một lần kiểm ở một trạm, GPU GTX 1650 (classifier) — p50 / p95 (ms). Nguồn: các file JSON ở trên.

| Arm | BIPIA (CONTEXT, đoạn dài) | JBB (INPUT) | CSKH tiếng Việt |
| --- | --- | --- | --- |
| R (luật Lớp 1–4) | 11,2 / 31,9 | 1,9 / 6,5 | 1,0 / 2,1 |
| M-deberta (chỉ classifier) | 66,8 / 273,5 | 28,4 / 41,7 | 26,6 / 36,3 |
| H-deberta (luật + classifier) | 70,7 / 281,7 | 29,1 / 43,2 | 26,9 / 37,5 |
| M-pg2 (chỉ classifier) | 66,4 / 273,1 | 29,0 / 54,2 | 25,4 / 34,0 |
| H-pg2 (luật + classifier) | 71,8 / 282,6 | 29,4 / 53,7 | 26,1 / 34,7 |

H-pg2 trên benchmark ngoài:

| Bộ | p50 / p95 (ms) |
| --- | --- |
| notinject | 28,8 / 33,5 |
| llmail_attack | 48,1 / 433,0 |
| llmail_benign | 38,7 / 44,1 |
| multijail | 28,0 / 38,2 |
| cyberseceval | 33,8 / 96,8 |

Độ trễ trường hợp tệ nhất (đoạn 20.000 ký tự, GPU và CPU) đo riêng, xem `lop5-pg2_2026-11-07.md` phần v2.

## 7. Giới hạn và minh bạch quy trình

- **Tập test detector đã chạy 4 lần:** v1, kiểm tra ngân sách cửa sổ, v2 (số chính thức), và một lần chạy lại ngày
  08/11 chỉ để lưu kết quả từng ca cho McNemar (`cases/detector_test_*.jsonl`). Lần chạy lại không đổi code hay
  ngưỡng; script này kiểm tra số tổng của nó khớp **đúng từng ca** với số v2 trước khi dùng. Ngưỡng chưa bao giờ chọn trên test.
- **LLM đích e2e là Gemini 3.5 Flash-Lite**, không phải model chính của web (DeepSeek qua TokenHarbor): nhà cung cấp đó
  chặn prompt tấn công và đã khoá một tài khoản (quyết định Q28).
- **Judge là chính LLM đích** (nhiệt độ 0). Judge có thể sai; không có chấm tay toàn bộ.
- **Tiếng Việt e2e là bản dịch máy** của CyberSecEval; bộ CSKH tiếng Việt chưa có ca tấn công (C1-OPEN).
- **Chưa đo utility e2e** (câu hỏi vô hại có bị trả lời kém đi không) — backlog C3-4.
- Không tuyên bố chặn 100%: tấn công diễn đạt lại tinh vi và tấn công thích nghi vẫn lọt (§4).

## Biểu đồ

| Hình | Nội dung |
| --- | --- |
| `figures/fig1_detector_arms.png` | Recall và chặn nhầm theo arm (BIPIA, JBB, CSKH) |
| `figures/fig2_e2e_asr.png` | ASR end-to-end G0 / G2 / G4 với CI 95% |
| `figures/fig3_e2e_groups.png` | ASR theo nhóm (trực tiếp / gián tiếp / ngôn ngữ) |
| `figures/fig4_pii_entities.png` | F1 PII theo thực thể |
| `figures/fig5_external.png` | Benchmark ngoài: R so với H-pg2 |
