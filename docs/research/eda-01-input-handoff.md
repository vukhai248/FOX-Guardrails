# EDA 01 · Bàn giao dữ liệu FOX INPUT

[Notebook đã chạy](../../notebooks/01_eda_data.ipynb) đọc 14 tệp có hash được ghim từ tám nguồn.
Tổng cộng có 395.051 dòng gốc và 91.411 dòng sau bộ lọc theo từng nguồn.
[EDA 0.5](eda-0.5-data-review.md) lưu quyết định chọn và để ngoài phạm vi của các nguồn khác.

## Số liệu dùng để quyết định

Bảng dưới đếm văn bản ứng viên có nhãn nguồn sau chuẩn hóa, bỏ exact duplicate,
cách ly thành phần liên thông với benchmark FOX hoặc split test/val gốc và kiểm xung đột nhãn.
Nhãn và ngôn ngữ vẫn cần rà. Tỷ lệ 45% VI, 45% EN và 10% trộn là kịch bản dự toán.
Cột thiếu áp dụng giả định 0/1 cân bằng trong từng ngôn ngữ.

| Ngôn ngữ | Nhãn ứng viên | Text duy nhất | Nhóm liên thông | Thiếu để đạt 10k | Thiếu để đạt 40k |
|---|---:|---:|---:|---:|---:|
| VI | 0 | 12.264 | 4.442 | 0 | 0 |
| VI | 1 | 3.725 | 1.468 | 0 | 5.275 |
| EN | 0 | 9.325 | 8.299 | 0 | 0 |
| EN | 1 | 3.102 | 2.676 | 0 | 5.898 |
| Trộn VI–EN | 0 | 18 | 18 | 482 | 1.982 |
| Trộn VI–EN | 1 | 51 | 51 | 449 | 1.949 |

Tổng gồm 28.485 văn bản. Khi chỉ giữ `variant=orig` của GuardSpec, tổng giảm còn 18.284.
Số mẫu VI dương còn 1.472, tương ứng 1.342 nhóm. Mốc 10k theo tỷ lệ trên còn thiếu câu trộn
ở cả hai nhãn, và thiếu 778 mẫu VI dương nếu dùng cấu hình chỉ lấy bản gốc.
Số liệu theo nhóm là số nhóm chạm từng ô. Một nhóm có thể xuất hiện ở nhiều ô.

## Chọn trường và duyệt theo nguồn

| Nguồn | Text đưa vào INPUT | Quyết định khi load và transform |
|---|---|---|
| SecAI | `text` | Dùng `injection` làm nhãn ứng viên. Giữ `group`, `lang`, `intent` và `pii` riêng. Rà ngôn ngữ ở câu trộn hoặc ngắn. |
| VI–EN | `text` | Giữ `primary_language` và `attack_type`. Chuyển 125 dòng train thuộc Refusal Bypass hoặc Steganography sang rà nhãn. Mẫu đã đọc có yêu cầu có hại đơn thuần trong Refusal Bypass. |
| GuardSpec | `text` | Giữ tag, `group`, `variant`, upstream và quyền dùng từng dòng. Tách 3.182 dòng train có indirect/tool poisoning sang CONTEXT và 1.338 dòng chưa ánh xạ rõ sang rà nhãn. |
| Aya | `inputs` | Giữ `language_code` và `annotation_type`. Còn 8.676 dòng VI và 3.846 dòng EN train sau cách ly. Đưa vào hàng chờ gán nhãn. |
| OASST2 | `text` của prompter VI/EN | Giữ ID tin nhắn, ID hội thoại và cờ chất lượng. Còn 19.653 dòng train sau cách ly, gồm 48 dòng VI. Đưa vào hàng chờ gán nhãn. |
| TrustAIRLab, deepset, jackhhao | `prompt` hoặc `text` | Giữ ở dự phòng cho đợt rà EN. Kiểm nhãn nguồn, ngôn ngữ và họ prompt. Ví dụ 62/180 mẫu deepset được bộ nhận diện đánh dấu ngôn ngữ khác VI/EN. |

Nhãn `0` nghĩa là không thấy hành vi prompt attack trong đơn vị INPUT đang xét. Những trường về PII,
độ an toàn nội dung và kết quả tấn công giữ riêng. Ca thiếu ngữ cảnh hoặc chưa gán nhãn có trạng thái duyệt.
Tập xuất chỉ nhận nhãn đã duyệt `0` hoặc `1`.

## Cách ly và các trường hợp cần kiểm

- **Trùng nguồn.** GuardSpec và jackhhao có 864 nội dung trùng nhau trên các lát cắt đã đọc.
  GuardSpec và OASST2 có 666. Nạp cả hai nguồn rồi chọn một bản đại diện có provenance rõ,
  hoặc giới hạn theo upstream trước khi rút mẫu.
- **Benchmark và split gốc.** OASST2 train có 30 dòng khớp text LLMail Phase 2 và 2.001 dòng được
  cách ly theo nhóm liên thông với benchmark hoặc split gốc. Các khớp chuỗi có thể là chủ đề email.
  Notebook ghi cụ thể số dòng theo nguồn, split và benchmark.
- **Gần trùng.** So 1.268 lượt text tham chiếu lấy mẫu với 54.911 text ứng viên duy nhất.
  GuardSpec val có 32/100 lượt đạt cosine character 4-gram từ 0,85 và 13/100 từ 0,92.
  Aya test lần lượt là 5/100 và 2/100. Đây là danh sách cần rà, chưa phải nhãn trùng.
  Bản dịch, paraphrase và khuôn khác chữ vẫn cần truy lineage hoặc đánh giá thủ công.
- **Độ dài.** 1.360/8.676 dòng Aya VI và 3.656/15.140 dòng TrustAIRLab vượt cửa sổ 512 token
  theo tokenizer PG2 cục bộ. Ca dài cần policy cửa sổ và cách gán nhãn theo đoạn.
- **Mẫu khó.** Dùng strata có sẵn như GuardSpec hardneg, nhóm cần rà của VI–EN, ca dài và câu trộn.
  Chưa có nhãn độ khó độc lập hay kết quả PG2 chạy trên pool này.

## Cấu trúc ELT đề xuất

1. **Extract** đọc đúng revision/path/hash từ manifest đã có. Ghi lại source, split và khóa dòng.
2. **Load** bảng staging có `text_raw`, `source_label`, `source_language`, `source_ref`,
   `upstream_source`, `license`, `origin_group_id` và `variant` khi nguồn có.
3. **Transform** ghi `label_status`, `label`, `language`, `entry_point`, `exact_hash`,
   `duplicate_group_id`, `token_count` và `benchmark_match`. Kiểm nhãn và ngôn ngữ theo
   strata, nối các biến thể rồi chia tập theo nhóm. Giữ split nguồn để truy vết.
4. **Xuất huấn luyện** chỉ nhận text và nhãn 0/1 đã duyệt. Báo lại độ phủ theo ngôn ngữ × nhãn,
   nguồn và nhóm. Dùng tập dev để chọn ngưỡng. TMĐT giữ vai trò lát cắt đánh giá.

Ưu tiên bổ sung mẫu dương VI/EN từ các họ còn thiếu và câu trộn ở cả hai nhãn.
Chốt quota sau khi có kết quả rà nhãn và nhóm. Các con số trên là dự toán cho ELT trước khi tạo tập train.
