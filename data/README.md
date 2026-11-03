# Dữ liệu

| Thư mục | Nội dung | Commit? |
| --- | --- | --- |
| `raw/` | File tải về từ BIPIA, JailbreakBench (nguyên bản) | ❌ không |
| `processed/` | Dữ liệu đã chuẩn hóa về schema chung, đã chia tập phát triển / đánh giá | ❌ không |

## Nguồn dữ liệu

- **BIPIA** — https://github.com/microsoft/BIPIA (nguồn chính; kiểm tra license trước khi tải, một số ngữ cảnh như WebQA/Summarization cần tự sinh theo hướng dẫn trong repo gốc).
- **JailbreakBench** — https://github.com/JailbreakBench/jailbreakbench · dataset `JailbreakBench/JBB-Behaviors` trên HuggingFace (100 hành vi độc hại + 100 lành tính).

Dữ liệu không được commit vào repo; quy trình tải và chuẩn hóa: `docs/plans/C-du-lieu-va-thuc-nghiem.md` §2.
