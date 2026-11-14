# Dữ liệu

| Thư mục | Nội dung | Commit? |
| --- | --- | --- |
| `raw/` | Tệp benchmark gốc và các đợt tải ứng viên | ❌ không |
| `processed/` | Dữ liệu đã chuẩn hóa về schema chung, đã chia tập phát triển / đánh giá | ❌ không |

## Nguồn dữ liệu

- **BIPIA** — https://github.com/microsoft/BIPIA (nguồn chính; kiểm tra license trước khi tải, một số ngữ cảnh như WebQA/Summarization cần tự sinh theo hướng dẫn trong repo gốc).
- **JailbreakBench** — https://github.com/JailbreakBench/jailbreakbench · dataset `JailbreakBench/JBB-Behaviors` trên HuggingFace (100 hành vi độc hại + 100 lành tính).

Dữ liệu không được commit vào repo; quy trình tải và chuẩn hóa: `docs/plans/C-du-lieu-va-thuc-nghiem.md` §2.

Các nguồn ứng viên cũ nằm trong `raw/eda01/` và `raw/eda01_vi/`. Các nguồn bổ sung đã kiểm
kích thước và digest nằm trong `raw/eda05/<nguồn>/`. [Nhật ký EDA 0.5](../docs/research/eda-0.5-data-review.md)
liên kết tới notebook, revision và đề xuất sử dụng của từng nguồn.

[EDA 01](../notebooks/01_eda_data.ipynb) phân tích các nguồn đã chọn và chứa toàn bộ hàm phân tích
của bước này. Các notebook, manifest và helper dùng chung của EDA 0.5 nằm trong
[`notebooks/00_5_eda_data/`](../notebooks/00_5_eda_data/).
