# eval/

Khung đánh giá hiệu quả guardrails.

Dự kiến chứa:

- `datasets/` — trình nạp và dữ liệu đã chuẩn hóa cho đánh giá (BIPIA, JailbreakBench).
- `runners/` — chạy các phương án (luật / mô hình / kết hợp) trên tập đánh giá.
- `reports/` — kết quả đánh giá (số liệu + bảng tổng hợp).

Chỉ số dự kiến: precision, recall, F1, tỷ lệ chặn nhầm nội dung hợp lệ, tỷ lệ tấn công thành công, tỷ lệ rò rỉ PII trước/sau, độ trễ và chi phí. Chi tiết: `docs/plans/C-du-lieu-va-thuc-nghiem.md`.

Chưa có code — Phần C dựng sau khi FOX-Guard có B6.
