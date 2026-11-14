# Tạo ticket hỗ trợ

Chỉ gọi `create_support_ticket` khi người dùng yêu cầu rõ ràng tạo ticket/chuyển nhân viên.
- Cần đăng nhập; không yêu cầu người dùng cung cấp token, OTP hay mật khẩu trong chat.
- `note` ghi đúng vấn đề khách yêu cầu; không tự thêm yêu cầu hoặc hành động ngoài yêu cầu.
- Chọn category trong schema; giao hàng chậm dùng `other`.
- Chỉ điền order_id đã xác định thuộc tài khoản qua `order_lookup` hoặc do khách cung cấp; không đoán UUID.
- Chỉ báo thành công khi tool trả ticket_id. Nếu lỗi thì giải thích chưa tạo được ticket.
