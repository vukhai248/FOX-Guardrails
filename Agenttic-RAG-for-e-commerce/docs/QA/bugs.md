# Nhật ký Lỗi & Vấn đề Kỹ thuật (Bug Tracker — QA Wave 3 & QA2)

**Dự án**: Agentic RAG E-Commerce & FOX-Guardrails  
**Ngày cập nhật**: 03/11/2026  
**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA)  
**Trạng thái tổng thể**: **Phát hiện 1 lỗi Backend (BUG-A-01), giao Codex sửa ở gói K5**

---

## 1. 📋 Bảng Tổng hợp Lỗi theo Mức độ

| Mã lỗi | Tiêu đề | Mức độ | Phạm vi | Trạng thái |
| :--- | :--- | :---: | :---: | :---: |
| **BUG-A-01** | Cho phép cùng một người dùng tạo nhiều review trùng lặp cho cùng một sản phẩm | Medium | Backend (RPC `create_product_review` & bảng `reviews`) | **Mở (Chờ Codex sửa ở K5)** |

---

## 2. 🐛 Chi tiết Lỗi Chức năng (Functional Bugs)

### [BUG-A-01] Thiếu ràng buộc Unique / Kiểm tra trùng lặp khi gửi đánh giá sản phẩm (Review Duplication)
- **Mã lỗi**: `BUG-A-01 (backend)`
- **Phân loại**: Data Integrity / Business Logic Flaw
- **Phạm vi**: 
  - Database Function: `public.create_product_review(p_user_id, p_product_id, p_rating, p_comment)` (tại `database/migrations/2026-11_product_reviews.sql`)
  - Database Table: `public.reviews`
  - API Handler: `POST /api/reviews` (`web_ui/src/lib/server/review-handlers.ts`)
- **Mô tả hiện tượng**:
  - Khi một khách hàng đã mua sản phẩm hợp lệ (đơn `status <> 'cancelled'` và `payment_status IN ('paid', 'cod_pending')`), khách hàng có thể gọi `POST /api/reviews` nhiều lần cho cùng một sản phẩm.
  - Backend chấp nhận tất cả các lần gọi tiếp theo và trả về HTTP 201 Created thay vì từ chối với HTTP 409 Conflict.
  - Bằng chứng thực nghiệm tại QA2:
    - User A (`bench_customer_a`: `faea467c-6a5b-4e50-84d5-b5220fea8e1a`) gửi review lần 1 cho sản phẩm `135935`: thành công (201 Created, `review_id=0b3b9a10-0361-4761-8538-cd2bec74f02f`).
    - User A gửi tiếp review lần 2 cho cùng sản phẩm `135935`: backend vẫn trả về 201 Created (`review_id=cdc06905-1962-4266-ac48-7e499a416602`).
    - Trước đó, sản phẩm `1001` cũng đã bị ghi 4 review trùng từ cùng User A.
- **Nguyên nhân gốc (Root Cause Analysis)**:
  1. Trong migration `database/migrations/2026-11_product_reviews.sql`, hàm `public.create_product_review` chỉ kiểm tra điều kiện `o.payment_status IN ('paid','cod_pending')` mà KHÔNG kiểm tra xem user đã tồn tại review cho sản phẩm này chưa:
     ```sql
     -- Thiếu check:
     IF EXISTS (SELECT 1 FROM public.reviews WHERE user_id = p_user_id AND product_id = p_product_id) THEN
       RAISE EXCEPTION 'ALREADY_REVIEWED';
     END IF;
     ```
  2. Bảng `public.reviews` chưa có ràng buộc `UNIQUE (user_id, product_id)`.
  3. Handler `createReviewHandler` chưa xử lý mã lỗi `ALREADY_REVIEWED` để trả về HTTP 409 Conflict.
- **Các bước tái hiện (Reproduction Steps)**:
  1. Đăng nhập với tài khoản khách hàng đã mua sản phẩm (ví dụ `bench_customer_a`).
  2. Gửi request `POST /api/reviews` lần 1 với payload:
     `{"product_id": 135935, "rating": 5, "comment": "Đánh giá lần 1"}` $\rightarrow$ Trả về 201 Created.
  3. Gửi lại request `POST /api/reviews` lần 2 với cùng `product_id`:
     `{"product_id": 135935, "rating": 4, "comment": "Đánh giá lần 2"}`.
  4. Quan sát: Backend trả về 201 Created thay vì 409. Trong DB bảng `reviews` có 2 dòng cùng `(user_id, product_id)`.
- **Đề xuất khắc phục (Dành cho Codex ở đợt K5)**:
  1. Thêm migration bổ sung ràng buộc hoặc cập nhật hàm `public.create_product_review`:
     - Nếu đã tồn tại review của `(p_user_id, p_product_id)` $\rightarrow$ `RAISE EXCEPTION 'ALREADY_REVIEWED'`.
  2. Thêm ràng buộc `ALTER TABLE public.reviews ADD CONSTRAINT reviews_user_product_unique UNIQUE (user_id, product_id);` (lưu ý dọn dẹp các bản ghi trùng lặp trước khi add constraint).
  3. Trong `web_ui/src/lib/server/review-handlers.ts`, bắt lỗi `ALREADY_REVIEWED` và trả về:
     `if (code === 'ALREADY_REVIEWED') return error(code, 409, 'Bạn đã đánh giá sản phẩm này rồi.');`
  4. Sau khi K5 hoàn tất, thêm test case E2E "review lần 2 $\rightarrow$ HTTP 409 Conflict".

---

## 3. 💡 Ghi nhận Kỹ thuật & Khắc phục Môi trường (Environmental Fixes)

### [ENV-01] Xung đột IPv6 khi Next.js gọi Backend FastAPI trên Windows
- **Mức độ**: Medium (Ảnh hưởng môi trường Windows)
- **Hiện tượng**: `POST /api/chat` trả về HTTP 503 `BACKEND_UNAVAILABLE` dù Uvicorn đang chạy trên port 8080.
- **Nguyên nhân gốc**: Node.js v20+ ưu tiên phân giải `localhost` ra địa chỉ IPv6 `::1`. Do Uvicorn được bind trên IPv4 `--host 127.0.0.1`, các kết nối tới `::1:8080` bị Windows từ chối.
- **Khắc phục**: Cập nhật biến môi trường trong `web_ui/.env.local`:
  ```env
  NEXT_PUBLIC_RAG_SERVICE_URL=http://127.0.0.1:8080/chat
  ```
- **Kết quả**: Next.js proxy kết nối trực tiếp IPv4 thành công 100%, không còn bị timeout.

### [ENV-02] Lỗi Charmap Codec khi Python Uvicorn in ký tự tiếng Việt / Emoji trên Windows
- **Mức độ**: Low (Cấu hình chạy server)
- **Hiện tượng**: Pipeline ném ngoại lệ `'charmap' codec can't encode characters` dẫn đến HTTP 500.
- **Nguyên nhân gốc**: Console codepage mặc định trên Windows (CP1258 / CP936) không hỗ trợ đầy đủ các codepoint Unicode và emoji trong log pipeline.
- **Khắc phục**: Luôn thiết lập biến môi trường `$env:PYTHONUTF8=1` trước khi khởi chạy server (đã chuẩn hóa trong `docs/RUN.md`).
- **Kết quả**: RAG service ghi log tiếng Việt có dấu và emoji hoàn toàn ổn định.
