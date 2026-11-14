# Thay đổi baseline liên quan benchmark

## 03/11/2026 — A4 backend

- Giữ nguyên FULL_MASTER_PROMPT và các prompt guard/rejection hiện có.
- Thêm skill `product/reviews` cho `product_reviews` và `account/support_ticket` cho `create_support_ticket`; chỉ định khi được tạo ticket, không đoán order_id, không bịa kết quả.
- `select_skill` trả `(skill_name, text)`, ưu tiên ticket/review trước các từ khóa đơn hàng/sản phẩm; lưu tên skill trong state và truyền vào guard context làm intent. Giữ các nhánh chọn skill trước đây.
- Đăng ký schema hai tool mới; identity và JWT của tool ticket được inject từ auth context, không nhận từ model và không lưu trong tool args.
- Mặc định giữ guard LLM legacy và masking/wrapper địa chỉ legacy **on**. `LEGACY_LLM_GUARDRAIL=off`, `LEGACY_PROMPT_DEFENSE=off` cho phép Phần C dựng arm; không tự định nghĩa ý nghĩa G0/G1.
- Khung FOX guard mặc định off; mode khác off báo chưa triển khai. Chưa có detector/masking FOX/logic quyết định ở A4.
- `BENCH_RECORD=1` ghi local các lần thử gửi Gemini/Groq gồm messages, payload SDK, arm, mode, timestamp UTC; retry là dòng riêng. Đây là payload ở ranh giới SDK trước network, không phải bằng chứng nhà cung cấp đã nhận. Record có thể chứa PII tổng hợp/nguyên văn theo mục đích đo lường; không phải chat_logs A5 đã che PII. Mặc định không ghi.
- `BENCH_TEMPERATURE` hữu hạn trong [0,2] ghi đè nhiệt độ cho Gemini/Groq, kể cả 0; không đổi config dùng chung. Không bật cờ thì giữ baseline.
- Signature nhị phân trong messages được biểu diễn `{__type__: "bytes", base64: "..."}` trong record; không sửa bytes gửi SDK.
