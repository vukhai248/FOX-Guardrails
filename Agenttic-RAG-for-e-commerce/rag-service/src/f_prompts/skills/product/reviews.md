# Đánh giá sản phẩm

Khi người dùng hỏi đánh giá, review, mọi người nói gì, hoặc sản phẩm có tốt không:
- Gọi `product_reviews` để đọc đánh giá thật. Không bịa nhận xét hay rating.
- Tên khớp nhiều dung lượng của cùng một mẫu (128GB, 256GB…) → tool đọc chung, không cần chọn.
- Nếu tool trả danh sách `product_id=…` (nhiều mẫu khác nhau), gọi lại với `product_id` đúng mẫu khách hỏi; không rõ thì hỏi khách chọn. Không gọi lại bằng cùng một tên.
- Chỉ tóm tắt từ kết quả đã lấy; ghi rõ khi chưa có đánh giá.
