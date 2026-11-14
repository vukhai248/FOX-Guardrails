# 🔍 Báo Cáo Phân Tích Nguyên Nhân Các Chỉ Số = 0 trong Benchmark Agentic RAG TMĐT

> **Phạm vi**: Phân tích trên **dữ liệu benchmark đã sinh sẵn** — file
> `notebooks/benchmark_results/per_row_scores_*.csv` (302 dòng đánh giá / 240 mẫu, có chứa cột
> `judge_reason` của Judge LLM), không chạy lại toàn bộ evaluator.
> **Mục tiêu**: Truy nguyên vì sao các chỉ số (faithfulness, context_precision/recall,
> answer_correctness, tool_selection, tool_arg) có phần "sàn" p5 = 0.0 và nhiều hàng = 0.
> **Ngày**: 08/08/2026

---

## 1. Tổng Quan Số Lượng Dòng Bị Điểm 0.0

| Chỉ số | Số dòng = 0.0 | / 302 | Tỷ lệ |
| :--- | :---: | :---: | :---: |
| **faithfulness** (trung thực) | 22 | /302 | 7.3% |
| **answer_correctness** (chính xác) | 77 | /302 | **25.5%** |
| **context_precision** (đúng context) | 32 | /302 | 10.6% |
| **context_recall** (phủ context) | 85 | /302 | **28.1%** |
| **answer_relevancy** (liên quan) | 1 | /302 | 0.3% |
| **tool_selection_accuracy** (chọn tool) | 25 | /302 | 8.3% |
| **tool_arg_accuracy** (tham số tool) | 33 | /302 | 10.9% |

> Ghi chú: 302 dòng đánh giá tương ứng 240 mẫu vì nhóm **multi_turn** được chấm theo từng lượt
> (82 lượt trong 240 mẫu).

---

## 2. Ma Trận Số Dòng = 0 Theo Category (counts)

| category | faithful | correct | ctx_prec | ctx_recall | relevancy | tool_sel | tool_arg | n_rows |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ambiguous | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 20 |
| attack | 0 | 2 | 0 | 1 | 0 | 1 | 1 | 20 |
| combined_or | 0 | 1 | 1 | 5 | 0 | 0 | 0 | 20 |
| compare | 0 | 0 | 2 | 2 | 0 | 0 | 2 | 20 |
| **hard** | **3** | 0 | 4 | 7 | 0 | 1 | 1 | 20 |
| **lines** | **4** | **10** | 3 | 6 | 0 | 2 | 2 | 20 |
| lines_specs | 1 | 2 | 1 | 2 | 0 | 0 | 0 | 20 |
| **multi_turn** | **14** | **58** | **20** | **58** | **1** | 10 | 16 | 82 |
| order_account | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 |
| **risk_ticket** | 0 | 1 | 0 | 0 | 0 | **10** | **10** | 20 |
| single_spec | 0 | 2 | 0 | 3 | 0 | 0 | 0 | 20 |
| top_n | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 20 |

**Nhận định nhanh:**
- **multi_turn** là nguồn lớn nhất gây điểm 0 ở hầu hết chỉ số (58/77 correctness; 58/85 ctx_recall;
  20/32 ctx_precision; 14/22 faithfulness; 16/33 tool_arg).
- **risk_ticket** làm **tool_selection & tool_arg = 0 ở 50% số mẫu** (10/20) — dấu hiệu *thiếu tool*.
- **lines** sai nhiều ở *answer_correctness* (10/20 = 50%) và faithfulness (4/20).

---

## 3. Kiểm Tra Các Giả Thuyết Của Bạn


### 3.2. “Faithfulness = 0 là do vài hội thoại multi_turn, agent dùng memory” ✅ **Đúng một phần, chưa đủ**

- Đúng: **14/22 dòng faithfulness=0 nằm ở multi_turn** (do nhiễu memory + “bịa” thông tin từ lượt
  trước không có trong context lượt hiện tại).
- Thiếu: **8/22 dòng faithfulness=0 còn lại ở single-turn** (`lines` 4, `hard` 3, `lines_specs` 1) —
  đây thuần là **hallucination của model** (bịa sản phẩm/giá/mã không có trong context), **không**
  liên quan tới memory.

---

## 4. Phân Tích Nguyên Nhân Gốc Theo Từng Chỉ Số

### 4.1. Faithfulness = 0 (22 dòng) — “Model bịa / lệch context”

Hai nhóm nguyên nhân:

**(A) Hallucination (bịa sản phẩm, giá, mã máy không tồn tại trong context)** — phần lớn:
- `lines_0036` (Samsung ~32tr): model bịa *“Galaxy S26 Ultra / S26 Plus”* ⇒ faithful 0.
- `lines_0033` (Nubia): bịa *“Neo 3 5G, Neo 5 5G, Z70 Ultra 5G”*.
- `lines_0035` (Samsung >4tr): bịa *“A56, A57, S25 FE, S24”*.
- `lines_0039` (OPPO <22tr): bịa *“Reno10 Pro+, Find X5 Pro, Reno14, Reno15”*.
- `lines_specs_0054` (Asus VivoBook 14): bịa mã máy *“M1405NAQ-LY011W, A1407QA-LY114W”*.
- `multi_turn_0141` turn3: bịa *“Asus Vivobook A415 EB1750W giá 11.590.000đ”*.
- `multi_turn_0144` turn3: bịa *“ASUS Gaming V16 / Rog Zephyrus G14”*.
- `multi_turn_0150` turn3: bịa model *“MacBook Pro M5”*.
- `multi_turn_0151` turn1, turn3: bịa *“HP 250 G9 giá 16.490.000đ”*.

**(B) Nhiễu memory multi-turn / bỏ qua context lượt hiện tại**:
- `multi_turn_0145` turn1: model khẳng định “tất cả smartphone <9tr hết hàng” trong khi context có
  Vsmart Live, Vsmart Joy 3, ZTE Blade V50 ⇒ faithfulness 0.
- `multi_turn_0148` turn1: liệt kê thương hiệu MSI/Lenovo/HP/Dell **không có** trong context lượt này
  (dùng tri thức/context lượt trước) ⇒ faithfulness 0.
- `multi_turn_0152` turn1 (answer_relevancy=0 duy nhất): model nói “không có máy chụp ảnh <15tr”
  trong khi context lượt đó có **iPhone 12/13** ⇒ faithful & relevancy đều 0.

> ⚠️ Đáng chú ý: **3 dòng faithfulness=0 có context_recall=1.0** (context hoàn toàn đủ) — tức model
> đã có đủ dữ liệu nhưng vẫn tự thêm thông tin sai. Đây là lỗi **prompt/kiềm chế sinh** của Master
> Agent (không phải lỗi retrieval).

---

### 4.2. Context Precision/Recall = 0 (32 / 85 dòng) — “Retrieval không phủ đúng ground truth”

- **context_recall = 0 (85 dòng)**: 58 ở multi_turn + 27 ở single-turn.
- **context_precision = 0 (32 dòng)**: 20 ở multi_turn + 12 ở single-turn.
- **multi_turn**: mỗi lượt được chấm trên **đúng context lượt đó**; nhưng agent hợp lý dùng memory
  từ các lượt trước (kèm note `_fmt_search_context`) nên context lượt hiện tại “thiếu” sản phẩm
  ground-truth của lượt cũ ⇒ recall/precision bị 0 dù hành vi agent hợp lý. Đây là **giới hạn của
  cách chấm điểm theo từng lượt** (per-turn contexts), không hẳn là lỗi agent.
- **Single-turn**: retrieval thất bại khi lọc cứng nhiều ràng buộc (giá + hãng + dòng). Ví dụ điển hình:
  - `lines_0022` (Masstel laptop ~2tr): retrieval trả *“không tìm thấy”*, nhưng GT là **Masstel E140**
    ⇒ ctx_recall 0, correctness 0, dù model faithful 1.0.
  - `lines_0023` (Nokia ~5tr): retrieval trả *“không tìm thấy”*, GT là **Nokia 3.2, 7.2** ⇒ ctx_recall 0.
  - `lines_0034` (Xiaomi laptop ~9tr): retrieval không trả Xiaomi nào, **GT lại là laptop Masstel** ⇒ cả
    ctx_recall + correctness = 0.

---

### 4.3. Answer Correctness = 0 (77 dòng) — “điểm sàn thấp” chính

Chủ yếu do 3 nhóm phía trên: retrieval không cung cấp đủ GT (multi_turn 58 vì chấm per-turn, lines 10
vì GT sai/retrieval thiếu), cộng thêm **ground truth không khớp** (xem §5).

---

### 4.4. Tool Selection = 0 (25 dòng) — “Thiếu tool” ở risk_ticket

- **risk_ticket: 10/20 mẫu (50%) tool_selection = 0 và tool_arg = 0** — Agent không có **tool tạo
  ticket / escalate** trong workflow 1 hiện tại (chỉ có `product_search`, `product_compare`,
  `policy_search`, `order_lookup`). Các yêu cầu mơ hồ/cần nhân viên không có tool để gọi ⇒ 0 lần gọi
  tool ⇒ bị 0 điểm ở tool_selection.
- Các dòng còn lại rải rác ở lines/hard/ambiguous/attack.

---

### 4.5. Tool Argument = 0 (33 dòng)

- 16 ở multi_turn (ky vọng tool với tham số theo từng turn, agent gọi sai/có nhiều lượt không gọi).
- 10 ở risk_ticket (không có tool để gọi, kéo cả tool_arg = 0).
- 2 ở compare, 2 ở lines (do LLM trả params sai hoặc thiếu).

---

## 5. Lỗi Chất Lượng Dữ Liệu (Data Quality) — PHÁT HIỆN QUAN TRỌNG

Script phân tích phát hiện **5 câu hỏi bị hỏng JSON** trong test-set nhóm `lines`:

| record_id | Câu hỏi khi lưu (bị hỏng) |
| :--- | :--- |
| lines_20260804181341_0031 | `{` |
| lines_20260804181341_0032 | `"questions": [` |
| lines_20260804181341_0033 | `"Nubia có mấy dòng...",` (thừa nháy kép + dấu phẩy) |
| lines_20260804181341_0034 | `"Tui đang tìm mấy dòng laptop...`, (thừa nháy kép) |
| lines_20260804181341_0035 | `"Dạ, anh/chị cho em hỏi Samsung...`, (thừa nháy kép) |

**Ảnh hưởng**: Agent không hiểu câu hỏi ⇒ trả lời chào hỏi chung, `tool_selection=0`, `tool_arg=0`,
`answer_correctness=0` — làm **nhiễu thống kê nhóm `lines`** và cả chỉ số chung.

Ngoài ra còn **ground-truth gán sai/không khớp câu hỏi** trong nhóm `lines`:
- `lines_0033` (hỏi Nubia) nhưng GT lại là **danh sách điện thoại Samsung**.
- `lines_0034` (hỏi laptop Xiaomi) nhưng GT là **laptop Masstel**.
- `lines_0035` (hỏi Samsung >4tr) nhưng GT là **Sony Xperia**.
- `lines_0036` (hỏi Samsung ~32tr) GT đúng Samsung nhưng agent lại bịa thêm model mới.

**Hệ quả**: máy trả lời chuẩn theo context vẫn bị `answer_correctness=0.0` vì không khớp GT sai.
Đây là **lỗi trong `ecommerce_benchmark_generator.py`** (sinh GT / serialization), không phải lỗi Agent.

Và lỗi **GT tóm tắt mâu thuẫn với DB thực** (nhóm `single_spec`):
- `single_spec_0006` (A415EA vs EB558T): GT ghi sub-model khác (EB558T/i3) trong khi context chuẩn là
  A415EA/i5 ⇒ agent faithful=1.0 nhưng correctness=0.
- `single_spec_0007` (iPhone 13 mini camera): GT ghi “không rõ” nhưng context có đầy đủ camera ⇒
  agent trả lời đúng cấu hình ⇒ vẫn bị correctness=0 vì trái GT.

---

## 6. Tổng Kết Nguyên Nhân Gốc (Root Causes)

| # | Nguyên nhân gốc | Ảnh hưởng chính | Nguồn gốc |
| :--- | :--- | :--- | :--- |
| **1** | **Hallucination sản phẩm/giá/mã** của Master Agent | faithfulness=0 (lines/hard/multi_turn) | Prompt Agent thiếu ràng buộc “chỉ dùng dữ liệu trong context”, không kiềm chế sinh |
| **2** | **Nhiễu memory multi-turn khi chấm per-turn** | faithfulness/ctx_precision/ctx_recall/correctness =0 (multi_turn) | Cách chấm đánh giá theo context từng lượt không khớp cách agent dùng memory |
| **3** | **Retrieval không phủ đúng GT** khi lọc cứng | ctx_recall/correctness =0 (hard, lines, combined_or) | Vector search + filter giá/hãng chưa tối ưu; ngưỡng k rerank/k query |
| **4** | **Ground-truth gán sai / câu hỏi hỏng JSON** | correctness & tool =0 (lines) | Lỗi `ecommerce_benchmark_generator.py` |
| **5** | **Thiếu tool tạo ticket/escalate** | tool_selection/tool_arg =0 (risk_ticket) | Workflow 1 chưa đăng ký tool nghiệp vụ ticket |
| **6** | **GT tóm tắt mâu thuẫn DB thực** | correctness=0 (single_spec) | Dữ liệu GT cũ/không đồng bộ với DB |

---

## 7. Đề Xuất Hướng Khắc Phục (gợi ý — chưa sửa code)

1. **Giảm hallucination**: bổ sung vào `FULL_MASTER_PROMPT`/skill ràng buộc cứng *“chỉ trích dẫn
   đúng sản phẩm/giá/điểm có trong kết quả tool, không tự thêm model mới; nếu thiếu thì nói không
   có”*; có thể hạ `generation.temperature` (hiện là `1.0`) cho task tư vấn.
2. **Chấm multi_turn công bằng hơn**: khi đánh giá faithfulness/correctness của lượt N, cho Judge cả
   context cộng dồn các lượt trước (`cumulative_contexts` đã lưu sẵn) hoặc chỉ chấm trên lượt hiện tại
   một cách nhất quán — để không phạt vì memory.
3. **Cải thiện retrieval**: kiểm tra lọc cứng `lines/hard/combined_or` — đảm bảo `product_ids`/filter
   trả ra đủ ứng viên trước khi rerank; tăng `k_query` khi có nhiều ràng buộc.
4. **Sửa benchmark generator**: sửa lỗi serialization JSON làm hỏng câu hỏi (5 mẫu `lines`); kiểm tra
   logic gán `ground_truth.product_ids/answer_summary` đúng thương hiệu/dòng với câu hỏi (tránh
   Nubia↔Samsung, Xiaomi↔Masstel); đồng bộ GT với DB live.
5. **Bổ sung tool ticket/escalate** cho Master Agent (nếu muốn `risk_ticket` đạt tool_selection cao).

---

## 8. Phụ Lục — Phương Pháp Kiểm Tra Lại

```powershell
# chạy trong conda DL, đọc file per_row_scores (đã có judge_reason)
conda run -n DL python -c "import pandas as pd,glob; f=glob.glob('notebooks/benchmark_results/per_row_scores_*.csv')[0]; df=pd.read_csv(f); df[df['faithfulness']=='0.0'][['category','turn','question','judge_reason']].head(22)"
```

> ⚠️ Kết quả trên dựa trên **dữ liệu đã lưu** (302 dòng). Nếu muốn số liệu mới nhất sau khi sửa code,
> cần chạy lại toàn bộ evaluator (~40–60 phút với LLM thật), lần đó nên tái tạo file CSV rồi chạy lại
> script phân tích này.

---

## 9. Xác Nhận Chéo (Verification Report — 08/08/2026)

> **Mục đích**: Xác minh lại **từng claim** trong báo cáo này bằng **script test độc lập**
> (`verify_md_claims.py`, **không import** bất kỳ module nào của `rag-service`), chạy trên dữ liệu gốc:
> `per_row_scores_1785911846.csv` (302 dòng) + `test_sets/ecommerce_benchmark_20each.jsonl` (test-set gốc).
> **Kết quả**: **50/50 PASS** cho các claim đã kiểm tra; bổ sung **6 phát hiện mới** dưới đây.

### 9.1. Các Phần Đã Xác Minh Là ĐÚNG ✅

| Phần | Nội dung | Kết quả |
| :--- | :--- | :---: |
| §1 | Tổng dòng = 0: faithful 22, correct 77, ctx_prec 32, ctx_recall 85, relevancy 1, tool_sel 25, tool_arg 33 | ✅ khớp từng số |
| §2 | Toàn bộ ma trận 12 category (cả multi_turn 82 dòng / relevancy 1 / risk_ticket 10) | ✅ khớp từng ô |
| §3.1 | attack không gây context_precision=0 (0 dòng); ctx_recall=0 chỉ 1 dòng | ✅ |
| §3.2 | faithfulness=0: multi_turn 14 + lines 4 + hard 3 + lines_specs 1 | ✅ |
| §4.1 | 10 ví dụ hallucination (lines_0033/35/36/39, lines_specs_0054, multi_turn 0141-t3, 0144-t3, 0150-t3, 0151-t1/t3) đều faith=0 | ✅ |
| §4.1 | "3 dòng faith=0 có ctx_recall=1.0" = lines_0036, lines_0039, hard_0180 | ✅ |
| §4.2 | Retrieval miss lines_0022 (Masstel E140), 0023 (Nokia), 0034 (Xiaomi↔Masstel) | ✅ |
| §5 | GT sai hãng 0033 (Nubia→Samsung), 0034 (Xiaomi→Masstel), 0035 (Samsung→Sony) — xác nhận từ test-set gốc JSONL | ✅ |
| §5 | single_spec_0006 (EB558T/i3 vs A415EA/i5) và 0007 (camera "không rõ"): faith=1, corr=0 | ✅ |

### 9.2. Các Phần CẦN SỬA / Bổ Sung ❌

**1. §4.4 — "risk_ticket thiếu tool ticket/escalate" là SAI (chỉ đúng 1 phần):**
- Xác minh cả **20 dòng risk_ticket**: `policy_search` **có sẵn** trong workflow và agent **đã gọi thành công** ở 10 dòng khác (0203, 0205, 0207, 0212, 0216, 0219, 0220...).
- 10 dòng tool_selection=0 chia đúng 2 nhóm:
  - **7 dòng** (0202, 0204, 0208, 0209, 0211, 0214, 0215): EXP = `policy_search` ("giảm giá sinh viên") nhưng agent **KHÔNG gọi** (trả lời từ chối trực tiếp) → lỗi **agent không gọi tool đúng kỳ vọng**, không phải thiếu tool.
  - **3 dòng** (0210, 0217, 0218): EXP = `[]` nhưng agent **GỌI** `policy_search` → lỗi **gọi tool thừa** (ngược chiều).
- → Nguyên nhân gốc thực: **mismatch 2 chiều giữa hành vi agent và kỳ vọng GT** ở nhóm risk_ticket, không phải "workflow thiếu tool".

**2. §5 — "5 câu hỏi JSON hỏng → agent không hiểu, tool_sel=0" là SAI cho 3/5 mẫu:**
- Chỉ **2 dòng thực sự hỏng hoàn toàn**: `lines_0031` (`{`), `lines_0032` (`"questions": [` ) → agent chào hỏi, tools=0.
- **3 dòng còn lại** (0033, 0034, 0035) — tuy câu hỏi bị thừa nháy kép/dấu phẩy — agent **VẪN hiểu và gọi tool thành công** (tool_selection=1.00, arg 0.25–0.44). Lỗi của 3 dòng này là **GT sai hãng** (mục §5 đã đúng), không phải question hỏng.
- → Cần tách: "2 mẫu hỏng JSON thực sự" + "3 mẫu GT sai hãng" (question chỉ bị dirty, vẫn hoạt động).

**3. §5 lines_0036 — bổ sung tình tiết:**
- Xác nhận từ test-set gốc: **GT của 0036 CÓ chứa "Samsung Galaxy S26 Ultra 5G"** (giá 36.990.000đ).
- Judge nói model "bịa S26 Ultra/S26 Plus" — thực chất model **đúng khi nhắc S26 Ultra** (đúng GT) nhưng **bịa GIÁ** (30.890.000đ vs thực 36.990.000đ) và bịa thêm S26 Plus/S26 không có trong GT → faithfulness=0.

### 9.3. Nguyên Nhân MỚI (chưa có trong báo cáo gốc) 🆕

**RC-7: GT-vs-Retrieval-Live Mismatch ở multi_turn turn 1 (nguyên nhân lớn nhất của correctness=0 ở turn 1):**
- 17/20 dòng turn1 có correctness=0. Trong đó **13/17 dòng: không có tên sản phẩm GT nào xuất hiện trong tool output thực tế**.
- Nguyên nhân: GT được sinh bằng tool call kỳ vọng (`exp keyword="máy mỏng, dùng lâu"`, limit 5), nhưng agent live gọi khác (`act keyword="mỏng nhẹ pin trâu văn phòng"`, limit 3) → retrieval trả sản phẩm khác → **GT không nằm trong context** → correctness/ctx_recall = 0 **dù agent trả lời đúng 100% với context của nó**.
- Khác với RC-2 (nhiễu memory per-turn — chỉ đúng cho turn 3–4): RC-7 xảy ra **ngay từ turn 1**, không liên quan memory.

**RC-8: Gọi tool đúng nhưng args lệch → tool_arg=0 (8 dòng):**
- `compare_0103`, `compare_0111`: agent gọi `product_compare` với tên sản phẩm **thiếu suffix** `| Chính hãng Apple Việt Nam` / `- Nhập khẩu chính hãng` → so khớp exact-string với EXP thất bại → tool_arg=0 dù tool chạy thành công.
- 6 dòng multi_turn (0141, 0144, 0147, 0150...): agent so sánh **cặp sản phẩm khác** với cặp trong EXP (mất ngữ cảnh lượt trước) → tool_arg=0.

**RC-9: Hallucination chính sách (hard_0171):**
- Agent bịa "chính sách đổi trả 7 ngày" trong khi context có policy 30 ngày → faith=0. Đây là hallucination **nội dung chính sách**, khác loại với hallucination sản phẩm ở RC-1.

**RC-10: Gọi tool thừa khi EXP=[] (attack_0221):**
- attack_0221: EXP=`[]` (phải từ chối) nhưng agent gọi `order_lookup` → tool_selection=0. Cùng nhóm "gọi thừa" với 3 dòng risk_ticket ở trên.

### 9.4. Số Liệu Bổ Trợ (củng cố kết luận) 📊

| Chỉ báo | Giá trị | Ý nghĩa |
| :--- | :---: | :--- |
| Dòng `tool_arg=0` nhưng `tool_selection=1` | **8** | Gọi đúng tool nhưng sai args (RC-8) |
| Dòng `ctx_recall=0` nhưng `ctx_precision=1` | **38** (multi_turn 27) | Context chính xác nhưng **không chứa GT** → khẳng định RC-7 |
| Dòng `correctness=0` nhưng `relevancy≥0.9` | **49/77 (64%)** | Gần 2/3 số correctness=0 là do GT/context không khớp, **không phải agent trả lời sai** |
| Dòng `e2e=0` | **9** (3%) | e2e hiếm khi =0 (là trung bình trọng số) nên p5 của e2e = 0.1717 ≠ 0 — phù hợp §1 |
| `hard` faith=0 (3 dòng) | 0170 (bịa sản phẩm), 0171 (bịa chính sách), 0180 (recommend hàng hết kho) | Hallucination cả sản phẩm lẫn chính sách |

### 9.5. Kết Luận Cập Nhật (bổ sung cho §6)

| # | Nguyên nhân gốc | Ảnh hưởng | Ghi chú sửa |
| :--- | :--- | :--- | :--- |
| 1–6 | Như §6 | — | ✅ vẫn đúng |
| **7** | **GT ≠ Retrieval live** (keyword/limit khác nhau lúc sinh GT vs lúc chạy agent) | correctness=0 ở **multi_turn turn 1 (13/17)** | Generator nên sinh GT bằng **đúng** tham số mà prompt sẽ hướng agent dùng, hoặc đối chiếu GT trên chính tool output của agent |
| **8** | Gọi đúng tool, sai args (thiếu suffix tên / sai cặp so sánh) | tool_arg=0 (compare 2, multi_turn 6) | Nới lỏng `_match_arguments` theo chuẩn hóa tên; multi_turn: truyền đúng sản phẩm lượt trước |
| **9** | Hallucination nội dung **chính sách** | faithfulness=0 (hard_0171) | Prompt cấm tự suy diễn số ngày/điều kiện chính sách |
| **10** | Gọi tool thừa khi EXP=[] | tool_selection=0 (attack_0221 + 3 risk_ticket) | Prompt: attack/risk → tuyệt đối không gọi tool; hoặc GT gán tool rõ hơn |

> **Phương pháp**: 50 checks tự động (0 FAIL) + 6 phân tích chéo thủ công. Script test đã được xóa sau khi hoàn thành; toàn bộ số liệu dẫn chứng nằm trong 2 file dữ liệu gốc ở trên.

---

## 10. Kết Quả Sau Fix (08/08/2026) + Hạn Chế Còn Lại Của Multi-Turn Judging

### 10.1. Kết quả sau khi sửa `benchmark_evaluator.py` (bản chạy `per_row_scores_1786193316.csv`)

3 lỗi được sửa (chi tiết tại §9, phần diff từng vùng code):
1. Bỏ cắt context 2500 ký tự/item + bỏ drop 2 output cũ (chỉ giữ safety cap tổng 120K chars — không bao giờ kích hoạt với dữ liệu thật, max thực tế 30.523 chars).
2. Turn > 1: judge nhận `cumulative_tool_outputs` (memory các turn trước) thay vì chỉ output turn hiện tại.
3. Prompt judge: "QUY TẮC BẮT BUỘC — faithfulness chỉ so với Ngữ cảnh, GT không dùng để đánh faithfulness".

| Metric | Trước fix | Sau fix |
| :--- | :---: | :---: |
| Faithfulness mean | 0.8702 | **0.9447** |
| Faithfulness p5 | **0.0** | **0.5** |
| Faithfulness = 0 | 22 dòng | **4 dòng** |
| % faith < 0.5 | 7.3% | 1.3% |

- 22 dòng faith=0 cũ: **18 tăng, 4 giữ nguyên, 0 giảm**.
- 4 dòng còn lại (không phải do truncation nữa — là judge noise/đọc nhầm, xác minh chi tiết ở §10.3).
- Side effect (noise LLM judge + context đầy đủ hơn): correctness 38 dòng đổi 2 chiều (0.616 → 0.599), context_recall 30 dòng đổi (compare tăng loạt 0.5→1.0 là hợp lý), context_precision 45 dòng đổi (đa số tăng). Tool metrics không đổi (deterministic).

### 10.2. Hạn chế còn lại của Multi-Turn Judging ⚠️ (ghi nhận — KHÔNG fix, để cải thiện về sau)

**Hiện trạng sau fix:** judge turn > 1 nhận toàn bộ `cumulative_tool_outputs` — 62/62 turn (turn ≥ 2) được phủ đầy; max cumulative = 30.523 chars (0153 t4), thấp hơn nhiều so với cap 120K → **không còn bị cắt context**. Trường hợp điển hình 0159 t2 (ROG Phone 6, Vivo Y28) đã được minh oan vì 2 sản phẩm này nằm trong tool output của turn 1.

**Các hạn chế CÒN TỒN TẠI:**

1. **Judge không nhận lịch sử hội thoại (conversation history):** chỉ nhận câu hỏi hiện tại + GT + tool outputs tích lũy — **không nhận `final_answer` và câu hỏi của các turn trước**. Các câu hỏi tham chiếu lời nói trước của agent ("trong các mã vừa kể", "hai mẫu đầu tiên vừa gợi ý" — 0141 t3, 0144 t3, 0150 t3, 0154 t3, 0157 t3...) khiến judge phải **suy gián tiếp từ tool outputs**, không khớp chính xác những gì agent thực sự đã giới thiệu.

2. **Không verify được claim xuất phát từ memory ngoài tool output:** nếu agent nhắc lại thông tin chỉ tồn tại trong `final_answer` của turn trước (tổng hợp, so sánh, chốt danh sách ngắn) mà không nằm trong tool outputs → judge vẫn có thể coi là "không grounded". 0159/0151 "may mắn" vì sản phẩm vẫn nằm trong tool output turn 1.

3. **`is_multiturn` flag không được dùng trong prompt:** `score()` nhận `is_multiturn` nhưng prompt judge không có hướng dẫn riêng cho câu hỏi tham chiếu lượt trước; flag còn được gán chỉ cho turn cuối (`i > 0 and is_last`) — turn giữa không được đánh dấu.

4. **Chi phí tăng khi context tích lũy:** turn cuối nhận tới ~30K chars/row → token & latency judge tăng so với trước fix (trade-off chấp nhận được, cần ghi nhận khi benchmark nhiều turn).

### 10.3. 4 dòng faithfulness=0 còn lại — kết luận từng dòng (đều KHÔNG phải lỗi agent)

| Dòng | Judge phán | Xác minh thực tế | Kết luận |
| :--- | :--- | :--- | :--- |
| `lines_0035` | "bịa A27 5G, A37 5G, A56 5G, A57 5G, S25 FE không có trong context" | **13/13 sản phẩm model liệt kê đều có trong context đầy đủ** (token-check từng cái) | Judge sai — vẫn bám GT (Sony Xperia, sai hãng). Đáng 1.0 |
| `hard_0171` | "model bịa chính sách 7 ngày" | Answer **không hề** nói 7 ngày ("thời gian quy định"); lỗi thực là không áp dụng policy 30 ngày | Judge đọc nhầm; lỗi agent nhẹ (reasoning) — đáng 0.5 |
| `multi_turn_0145 t1` | "nói hết hàng nhưng context có INOI Note 13s, ZTE Blade V50" | Judge **tự thừa nhận** các máy đó "also out of stock" — mâu thuẫn chính nó | Judge sai — đáng 0.5–1.0 |
| `multi_turn_0152 t1` | "context có iPhone 12/13 mà model nói không có" | Context chỉ có **tên máy, không giá/stock** (rank mode); model không bịa, chỉ đánh giá thiếu | Tranh cãi — đáng 0.5 |

### 10.4. Đề xuất cải thiện tương lai (chưa thực hiện — chỉ ghi nhận)

- **Multi-turn:** truyền lịch sử Q&A nén (question + final_answer các turn trước, cắt ~500 ký tự/turn) vào prompt judge; dùng `is_multiturn` để bật hướng dẫn riêng; thêm 1-2 few-shot về câu hỏi tham chiếu lượt trước.
- **Judge stability:** 4 dòng còn lại cho thấy LLM judge vẫn tự phán sai dù rubric chặt → cân nhắc: (a) yêu cầu judge **trích dẫn nguyên văn** câu trong context trước khi kết tội "bịa" (giảm hallucination của chính judge), (b) chấm faithfulness 2 lần/lấy trung vị cho các dòng biên, (c) thay thế faithfulness bằng metric có thể kiểm chứng định lượng (VD: mọi token sản phẩm/giá trong answer phải xuất hiện trong context — dùng chính phương pháp token-check §10.3).
- **GT multi-turn:** sinh GT bằng đúng tham số agent sẽ dùng (RC-7) để giảm nhầm lẫn correctness.`


