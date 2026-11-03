# Ghi chú đề tài (nguyên văn)


**Tên đề tài: Xây dựng hệ thống AI Guardrails phát hiện Prompt Injection và ngăn ngừa rò rỉ thông tin cá nhân trong ứng dụng mô hình ngôn ngữ lớn**

## Nội dung chính

Các ứng dụng sử dụng mô hình ngôn ngữ lớn (LLM) có thể tiếp nhận chỉ dẫn độc hại từ câu hỏi người dùng hoặc từ dữ liệu bên ngoài như tài liệu truy xuất, email và kết quả gọi công cụ. Những chỉ dẫn này có thể làm mô hình thay đổi hành vi, bỏ qua quy tắc hoặc tiết lộ thông tin nhạy cảm. Bên cạnh đó, dữ liệu đầu vào và câu trả lời của mô hình có thể chứa thông tin định danh cá nhân (PII), cần được phát hiện và xử lý trước khi truyền hoặc hiển thị.

Đề tài xây dựng hệ thống AI Guardrails giám sát đầu vào, ngữ cảnh truy xuất và đầu ra của một ứng dụng LLM. Hệ thống kết hợp luật phát hiện, mô hình phân loại và bộ nhận diện PII để đánh giá rủi ro, từ đó cho phép, che thông tin, chặn nội dung hoặc chuyển trường hợp chưa chắc chắn cho người kiểm duyệt. Với dữ liệu bên ngoài, hệ thống phân biệt nội dung phục vụ tác vụ và chỉ dẫn có khả năng thao túng mô hình. Các quyết định được ghi nhận kèm bằng chứng và lý do để hỗ trợ kiểm tra.

Nội dung thực hiện gồm xây dựng và chuẩn hóa dữ liệu; phát triển bộ phát hiện Prompt Injection và PII; thiết kế chính sách xử lý theo mức rủi ro; tích hợp lớp bảo vệ vào ứng dụng hỏi đáp RAG thử nghiệm; và xây dựng dashboard theo dõi cảnh báo, xem lại quyết định và thống kê hiệu quả.

Các bản ghi giám sát được che thông tin cá nhân trước khi lưu trữ.

Thực nghiệm so sánh các phương án sử dụng luật, mô hình phân loại và cơ chế kết hợp. Hiệu quả được đánh giá bằng precision, recall, F1, tỷ lệ chặn nhầm nội dung hợp lệ, tỷ lệ tấn công thành công và tỷ lệ rò rỉ PII trước/sau khi áp dụng guardrails. Đồng thời, đo mức ảnh hưởng đến chất lượng trả lời, độ trễ và chi phí. Dữ liệu được tách theo nguồn hoặc dạng tấn công để hạn chế trùng lặp giữa tập phát triển và tập đánh giá.

## Cơ sở dữ liệu ban đầu

Đề tài sử dụng BIPIA, benchmark công khai phục vụ đánh giá khả năng chống indirect prompt injection, làm nguồn chính cho các tình huống chỉ dẫn độc hại được nhúng trong dữ liệu bên ngoài. JailbreakBench được sử dụng bổ sung để đánh giá khả năng xử lý yêu cầu đối kháng trực tiếp; kết quả của hai nhóm tấn công được báo cáo riêng.
