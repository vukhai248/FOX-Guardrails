# Báo Cáo Khảo Sát & Kiểm Toán Dự Án (Security & PII Audit Report)
**Căn cứ theo bản kế hoạch:** `docs/handoff.md` (Mục 9 & 10)  
**Thời gian thực hiện:** 02/11/2026  
**Mục tiêu:** Rà soát thực tế mã nguồn, cơ sở dữ liệu và giao diện để phục vụ nghiên cứu phòng thủ Prompt Injection gián tiếp (IPI) và Bảo vệ PII.

---

## 1. Rà Soát 6 Điểm Kỹ Thuật Khi Khảo Sát Project (Theo Mục 9 `handoff.md`)

### Điểm 1: Cơ chế điều phối & gọi hàm (Tool Calling)
* **Hiện trạng trong mã nguồn:** 
  - Hệ thống sử dụng kiến trúc **Flat ReAct Agent** kết hợp **LangGraph StateGraph** (`rag-service/src/g_pipelines/workflow_1/workflow_1.py`).
  - LLM chính (`MasterAgent` trong `rag-service/src/e_agents/master_agent.py`) được cấu hình gọi hàm qua Google Gemini API (`call_gemini` với `tools=tools_schema`, `stream=True`).
  - Danh sách tool schema được chuẩn hóa theo chuẩn OpenAI/Gemini Function Calling (`PRODUCT_SEARCH_SCHEMA`, `POLICY_SEARCH_SCHEMA`, `PRODUCT_COMPARE_SCHEMA`, `ORDER_LOOKUP_SCHEMA`).
* **Kết luận đánh giá IPI:** LLM **tự quyết định gọi hàm** dựa trên ngữ cảnh hội thoại. Do đó, cần đánh giá cả 2 khía cạnh: (1) LLM có bị điều hướng gọi sai tool không, và (2) Khi dữ liệu do tool trả về có chứa mã độc gián tiếp (IPI), LLM có bị thao túng câu trả lời hoặc vi phạm an toàn không.

---

### Điểm 2: Nguồn dữ liệu do người dùng/bên ngoài nhập (Attack Surface)
* **Khảo sát Schema Database (`database/setup.sql`):**
  1. `public.orders` (`shipping_address TEXT NOT NULL`): Trường văn bản tự do do khách hàng nhập khi checkout giỏ hàng. Thường chứa địa chỉ nhà, tên người nhận, số điện thoại, và ghi chú giao hàng (ví dụ: "Giao giờ hành chính", hoặc bị kẻ xấu chèn IPI).
  2. `public.reviews` (`comment TEXT`): Đánh giá của khách hàng về sản phẩm. Kẻ xấu có thể đăng đánh giá chứa payload hướng dẫn bot nói xấu sản phẩm, đổi hướng sang shop khác, hoặc giả mạo thông báo của ban quản trị.
  3. `public.support_tickets` (`note TEXT`): Nội dung yêu cầu hỗ trợ từ khách hàng.
* **Kết luận đánh giá IPI:** Điểm chèn IPI thực tế và nguy hiểm nhất trong kịch bản CSKH là trường **`shipping_address` / ghi chú đơn hàng** trong bảng `orders` (tác động khi bot tra đơn) và **`comment`** trong bảng `reviews` (tác động khi bot tra cứu đánh giá/sản phẩm). Bảng `policies` là nguồn chính sách tĩnh của shop, không để người dùng sửa tự do.

---

### Điểm 3: Độ tin cậy của nguồn chính sách
* **Hiện trạng:**
  - Chính sách được lưu ở 2 nơi: bảng quan hệ `public.policies` trong Supabase (chỉ Admin có quyền ghi) và Vector Store `policies_collection` trong ChromaDB (`database/chroma_db`).
  - Tool `policy_search` (`rag-service/src/d_tools/policy/policy_search.py`) chỉ đọc từ ChromaDB vector store nội bộ, không có API cho người dùng ngoài chỉnh sửa.
* **Kết luận Threat Model:** Bảng chính sách là **nguồn tin cậy (Trusted Source)**. Kẻ tấn công không thể sửa trực tiếp bảng chính sách, mà chỉ có thể cố gắng giả mạo chính sách thông qua tin nhắn chat (Direct Prompt Injection) hoặc chèn nội dung giả mạo vào ghi chú đơn hàng/đánh giá (Indirect Prompt Injection).

---

### Điểm 4: Kiểm toán PII và rò rỉ dữ liệu (Data Minimization)
* **Khảo sát Tool `order_lookup.py` (`rag-service/src/d_tools/account/order_lookup.py`):**
  - Khi tra cứu chi tiết đơn hàng theo `order_id`:
    ```python
    f"- Shipping Address: {order.get('shipping_address', 'None')}\n"
    ```
    Hệ thống đang gửi **nguyên văn toàn bộ địa chỉ giao hàng** (bao gồm số nhà, tên đường, thông tin liên lạc) vào prompt của LLM bên ngoài (Google Gemini API).
  - Khi khách chỉ hỏi: *"Đơn hàng của tôi đang ở trạng thái nào rồi?"* hoặc *"Bao giờ hàng giao tới?"*, việc phơi bày 100% địa chỉ chi tiết vi phạm nguyên tắc bảo vệ dữ liệu tối thiểu (**Data Minimization**).
* **Kết luận & Giải pháp:** Cần xây dựng cơ chế phân loại mức độ chi tiết: mặc định chỉ trả về thông tin trạng thái, tỉnh/thành phố, sản phẩm và tổng tiền; thực hiện che mờ (masking) các thông tin nhạy cảm trước khi gửi tới LLM.

---

### Điểm 5: Render nội dung phía Frontend (UI/UX Vulnerability)
* **Khảo sát Component `chat-widget.tsx` (`web_ui/src/components/chat-widget.tsx`):**
  - Dòng 628: Tin nhắn AI được render trực tiếp bằng `<Markdown>{msg.message}</Markdown>`.
  - Nếu LLM bị IPI điều hướng sinh ra đường link độc hại (ví dụ: `[Xác minh CCCD tại đây](https://phishing-site.com/verify)`), giao diện sẽ render thành thẻ `<a>` có thể click trực tiếp.
* **Kết luận:** Cần cấu hình rule render Markdown để chặn hoặc cảnh báo khi link dẫn ra ngoài tên miền nội bộ của cửa hàng.

---

### Điểm 6: Ngôn ngữ hỗ trợ & Tập dữ liệu kiểm thử
* Toàn bộ hệ thống giao tiếp bằng **tiếng Việt 100%**.
* Bộ câu hỏi kiểm thử cần được xây dựng bằng tiếng Việt tự nhiên, bao gồm:
  - Mẫu hợp lệ (Benign): Hỏi tiến độ giao hàng, hỏi chính sách đổi trả hàng đã mua.
  - Mẫu khó (Hard-Benign): Khách nhắc đến "chứng minh thư", "địa chỉ", "đổi địa chỉ" một cách hợp lệ.
  - Mẫu tấn công (Attack / IPI): Đơn hàng có ghi chú mạo danh quản trị viên yêu cầu cấp CCCD/OTP, hoặc yêu cầu chuyển hướng khách sang website khác.
