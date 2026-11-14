# Báo cáo Kiểm thử Bổ sung QA2 (Post-Merge QA Wave 3 — Bổ sung Lần 12)

**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `qa/a-wave3`  
**Ngày thực hiện**: 03/11/2026  
**Tham chiếu chỉ đạo**: Phê duyệt nghiệm thu Lần 12 từ Claude Opus (`docs/reports/nghiem-thu-A.md` & `FOX-Guardrails/docs/plans/prompts/antigravity-phanA.md` dòng 319–328)  
**Trạng thái tổng thể**: **HOÀN TẤT ĐẦY ĐỦ CÁC MỤC QA2 (Phát hiện & ghi nhận 01 lỗi backend BUG-A-01)**

---

## 1. 📊 Bảng Đối Soát Toàn Diện 23 Dòng (14 Mục Checklist §5 + 9 Ca QA Plan)

| STT | Phân nhóm | Mục / Ca kiểm thử | Trạng thái | Ghi chú & Bằng chứng thực nghiệm |
| :---: | :--- | :--- | :---: | :--- |
| **1** | Checklist §5 | **Mục 1: Đặt hàng COD** | **ĐẠT** | Đơn COD tạo thành công, `status: 'pending'`, `payment_status: 'cod_pending'`, trừ kho sản phẩm chính xác 1 đơn vị. |
| **2** | Checklist §5 | **Mục 2: Chống can thiệp giá / user_id** | **ĐẠT** | Server tính tiền dựa trên `final_price` từ DB, bỏ qua hoàn toàn `price` và `user_id` giả mạo từ client. Khách không token nhận 401. |
| **3** | Checklist §5 | **Mục 3: Thanh toán Stripe Checkout thẻ test** | **ĐẠT** | Đơn `542da29f-442d-48b8-a9e6-d192a7ece2fc` thanh toán thẻ `4242...` qua Stripe thật, webhook nhận 200, đơn chuyển `paid/processing`, trừ kho 1001. |
| **4** | Checklist §5 | **Mục 4: Chống đọc chéo đơn hàng (PII)** | **ĐẠT** | User B gọi `GET /api/orders/542da29f...` bị từ chối với 404 NOT_FOUND. RLS DB và API Route bảo vệ PII tuyệt đối. |
| **5** | Checklist §5 | **Mục 5: Test A5.4 chặn leo quyền admin** | **ĐẠT** | Chạy thật với `bench_customer_a`, server `requireRole` chặn đứng cả 5 request leo quyền admin với 403 FORBIDDEN (8.2s). |
| **6** | Checklist §5 | **Mục 6: Replay Stripe Webhook (Idempotency)** | **ĐẠT** | Resend event `evt_1UXkA2DbFvbSAWxsDNZu1cIK`, webhook trả 200 OK, tồn kho sản phẩm 1001 giữ nguyên 20 (không bị trừ lần 2). |
| **7** | Checklist §5 | **Mục 7: Đánh giá sản phẩm đã mua** | **LỖI (BUG-A-01)** | Review lần 1 trả 201 Created, DB bảo toàn đúng từng codepoint. Gửi tiếp review lần 2 cho cùng sản phẩm vẫn trả 201 (chưa chặn trùng). |
| **8** | Checklist §5 | **Mục 8: Sửa ghi chú đơn không còn pending** | **ĐẠT** | `PATCH /api/orders/542da29f.../note` trên đơn đã `processing` trả về đúng HTTP 409 Conflict với code `NOT_EDITABLE`. |
| **9** | Checklist §5 | **Mục 9: Chatbot gọi đủ 5 tools** | **ĐẠT** | Đã gọi đủ: `policy_search`, `product_search`, `order_lookup`, `product_reviews`, `create_support_ticket`. DB đã có 2 ticket thật do agent tạo. |
| **10** | Checklist §5 | **Mục 10: Phiên chat độc lập khi không có session_id** | **ĐẠT** | 2 request không gửi `session_id` sinh 2 UUID độc lập, ghi vào bảng `chat_logs` với 2 session riêng biệt. |
| **11** | Checklist §5 | **Mục 11: Giới hạn độ dài session_id** | **ĐẠT** | `session_id` dài 105 ký tự bị FastAPI từ chối ngay với 422 Unprocessable Entity, proxy Next.js chuyển tiếp nguyên vẹn 422. |
| **12** | Checklist §5 | **Mục 12: Đăng nhập Admin (`bench_admin`)** | **ĐẠT** | Đăng nhập tài khoản `bench_admin` truy cập đủ 4 trang `/admin/{orders,users,tickets,chat-logs}`, số liệu lấy từ Supabase thật. |
| **13** | Checklist §5 | **Mục 13: Endpoint sức khỏe `/health`** | **ĐẠT** | `GET /health` trả về `healthy`, kết nối Supabase và ChromaDB đều `connected: true`. |
| **14** | Checklist §5 | **Mục 14: Benchmark seed idempotency & `--reset`** | **ĐẠT** | Chạy `seed_bench.py` lần 2 giữ nguyên; chạy `--reset` chỉ thay đúng 2 bản ghi bench, 37 orders và 19 reviews khác giữ nguyên vẹn. |
| **15** | anti-qa-plan | **Ca 1: Luồng đặt hàng & Idempotency** | **ĐẠT** | COD và Stripe Checkout thẻ test thành công, resend webhook không làm trừ kho lần 2. |
| **16** | anti-qa-plan | **Ca 2: Chống can thiệp giá & User ID** | **ĐẠT** | Giá tính theo DB server, không cho phép mạo danh ID người dùng khác đặt hàng. |
| **17** | anti-qa-plan | **Ca 3: Cách ly tài khoản & Bảo vệ PII** | **ĐẠT** | Khách B không xem được đơn của Khách A (404 NOT_FOUND), không rò rỉ dữ liệu cá nhân. |
| **18** | anti-qa-plan | **Ca 4: Multi-turn Chat & RAG Tools** | **ĐẠT** | Agent gọi tool `product_reviews` tóm tắt đánh giá thật; gọi `create_support_ticket` tạo ticket hợp lệ gắn với đơn hàng của user. |
| **19** | anti-qa-plan | **Ca 5: Xác thực A5.4 chặn leo quyền** | **ĐẠT** | `npx playwright test tests/e2e/a5_ui.spec.ts -g "A5.4"` passed 100% không bị skip. |
| **20** | anti-qa-plan | **Ca 6: Kiểm thử Hợp đồng Reviews API** | **LỖI (BUG-A-01)** | Khách chưa mua bị chặn 403 `NOT_PURCHASED`; khách đã mua review lần 1 được 201; nhưng review lặp lần 2 vẫn được 201 (BUG-A-01). |
| **21** | anti-qa-plan | **Ca 7: Cách ly hội thoại & Audit Log** | **ĐẠT** | Lịch sử chat cách ly theo session; session > 100 ký tự trả 422; `chat_logs` ghi nhận đầy đủ vai trò `user`/`agent`. |
| **22** | anti-qa-plan | **Ca 8: Giám sát Hệ thống qua `/health`** | **ĐẠT** | Endpoint trả về đầy đủ trạng thái kết nối các thành phần phụ thuộc backend. |
| **23** | anti-qa-plan | **Ca 9: Tính Bất biến & Reset Seed Bench (A7)** | **ĐẠT** | Cơ chế seed benchmark cô lập an toàn trong namespace, cờ `--reset` không gây ảnh hưởng dữ liệu shop. |

---

## 2. 🔬 Chi tiết Thực thi 6 Hạng mục QA2 Bổ sung

### 2.1 Mục 8: Sửa ghi chú đơn hàng không còn pending $\rightarrow$ 409 `NOT_EDITABLE`
- **Request**: `PATCH http://localhost:3000/api/orders/542da29f-442d-48b8-a9e6-d192a7ece2fc/note`
  - Đơn hàng `542da29f...` hiện có trạng thái `processing` (đã thanh toán qua Stripe).
  - Header: `Authorization: Bearer <token_bench_customer_a>`
  - Body: `{"note": "Thử cập nhật ghi chú trên đơn đã xử lý"}`
- **Kết quả thực tế**:
  ```json
  HTTP/1.1 409 Conflict
  {
    "error": {
      "code": "NOT_EDITABLE",
      "message": "Chỉ được sửa ghi chú của đơn đang chờ xử lý."
    }
  }
  ```
- **Kết luận**: **ĐẠT**. Đúng mã HTTP 409 và chuẩn lỗi Hợp đồng API §3.

---

### 2.2 Mục 10: Hai request chat không có `session_id` $\rightarrow$ Sinh 2 session độc lập trong `chat_logs`
- **Request 1**: `POST http://127.0.0.1:8080/chat` với body `{"message": "Xin chào, tôi là khách ẩn danh 1"}`
  - Response 1: `session_id = "42e02c11-bdce-411f-b7f5-ff19232e1e82"`
- **Request 2**: `POST http://127.0.0.1:8080/chat` với body `{"message": "Xin chào, tôi là khách ẩn danh 2"}`
  - Response 2: `session_id = "d1010234-e0c2-44f9-b9dd-ccc0a4fb344c"`
- **Kiểm tra Database thật (`chat_logs`)**:
  - Session 1 (`42e02c11...`): Tìm thấy đúng 2 bản ghi (`role='user'` và `role='agent'`).
  - Session 2 (`d1010234...`): Tìm thấy đúng 2 bản ghi (`role='user'` và `role='agent'`).
  - Hai session hoàn toàn tách biệt, không dùng chung ID hay gộp chung ngữ cảnh.
- **Kết luận**: **ĐẠT**.

---

### 2.3 Mục 9: Bổ sung 3 câu chat Tools (`order_lookup`, `product_reviews`, `create_support_ticket`)

#### a) Tra cứu đơn hàng (`order_lookup`):
- **Request**: `POST http://127.0.0.1:8080/chat`
  - Header: `Authorization: Bearer <token_bench_customer_a>`
  - Body: `{"message": "Kiểm tra trạng thái đơn hàng 542da29f-442d-48b8-a9e6-d192a7ece2fc giúp tôi", "user_token": "<token>"}`
- **Kết quả thực tế**:
  - `tool_used`: `order_lookup`
  - Phản hồi từ Agent:
    > "Dạ đơn hàng `542da29f-442d-48b8-a9e6-d192a7ece2fc` của anh/chị đặt ngày 03/11/2026 hiện đang ở trạng thái **Đang xử lý** ạ.  
    > Thông tin đơn hàng cụ thể:  
    > - Sản phẩm: iPhone 15 Pro Max 256GB Titan Tự Nhiên (Chính hãng VN/A) - Số lượng: 1  
    > - Tổng tiền: 29,990,000 VNĐ (Đã thanh toán)  
    > - Địa chỉ nhận: Phường Phúc Xá, Thành phố Hà Nội"
- **Kết luận**: **ĐẠT**. Tool đọc chính xác thông tin đơn hàng thật của user.

#### b) Hỏi đánh giá sản phẩm (`product_reviews`):
- **Request**: `POST http://127.0.0.1:8080/chat`
  - Body: `{"message": "Mọi người đánh giá iPhone 15 Pro Max 256GB Titan Tự Nhiên thế nào?"}`
- **Kết quả thực tế**:
  - `tool_used`: `product_reviews`
  - Agent gọi tool truy vấn bảng `reviews` của sản phẩm 1001.
- **Kết luận**: **ĐẠT**.

#### c) Tạo ticket hỗ trợ (`create_support_ticket`) & Ghi vào Database:
- **Request**: `POST http://127.0.0.1:8080/chat`
  - Header: `Authorization: Bearer <token_bench_customer_a>`
  - Body: `{"message": "Tạo ticket hỗ trợ báo đơn 542da29f-442d-48b8-a9e6-d192a7ece2fc giao chậm giúp tôi", "user_token": "<token>"}`
- **Kết quả thực tế**:
  - `tool_used`: `create_support_ticket`
  - Phản hồi từ Agent:
    > "Dạ em đã tạo ticket hỗ trợ (mã: 8b07dca2-2737-4f77-b1b7-05f136052a80) cho đơn hàng của anh/chị về vấn đề giao chậm rồi ạ. Bộ phận liên quan sẽ kiểm tra và liên hệ hỗ trợ mình sớm nhất nhé."
  - **Kiểm tra trực tiếp trong Database thật (`support_tickets`)**:
    - `id`: `8b07dca2-2737-4f77-b1b7-05f136052a80`
    - `customer_id`: `faea467c-6a5b-4e50-84d5-b5220fea8e1a` (khớp chính xác User A ID)
    - `order_id`: `542da29f-442d-48b8-a9e6-d192a7ece2fc`
    - `category`: `other`
    - `created_by`: `agent`
    - `status`: `open`
    - `note`: `Báo đơn hàng 542da29f-442d-48b8-a9e6-d192a7ece2fc giao chậm`
- **Kết luận**: **ĐẠT**. Tool ghi duy nhất của Agent đã chạy thật và tạo bản ghi thành công trong Supabase!

---

### 2.4 Mục 7: Đánh giá chặt chẽ & Tái hiện BUG-A-01
- **Kịch bản**: Sử dụng sản phẩm `135935` (Laptop Lenovo Yoga Slim 7) nằm trong đơn COD hợp lệ `cb83ab57-5f99-4951-9868-9fbb354c4630` của User A nhưng **chưa từng có review nào**.
- **Bước 1: Gửi Review lần 1**:
  - Payload: `{"product_id": 135935, "rating": 5, "comment": "Đánh giá Laptop Lenovo Yoga Slim 7 test QA2 🚀 Màn hình OLED cực nét 💯! (Unicode chuẩn test)."}`
  - Kết quả API: **HTTP 201 Created**, `review_id = "0b3b9a10-0361-4761-8538-cd2bec74f02f"`.
  - Đọc lại DB: Chuỗi comment khớp từng ký tự/codepoint Unicode 100%.
- **Bước 2: Tái hiện lỗi review trùng (BUG-A-01)**:
  - Gửi tiếp review lần 2 với cùng `product_id: 135935` bằng cùng tài khoản User A.
  - Kết quả API: **HTTP 201 Created** (thay vì 409 Conflict), sinh thêm `review_id = "cdc06905-1962-4266-ac48-7e499a416602"`.
- **Kết luận**: **LỖI BACKEND (BUG-A-01)**. Đã ghi nhận đầy đủ vào [bugs.md](file:///d:/create/DATN/Agenttic-RAG-for-e-commerce/docs/QA/bugs.md) kèm các bước tái hiện và giải pháp sửa tại K5.

---

### 2.5 Mục 14: Kiểm tra tính năng `--reset` của `seed_bench.py`
- **Lệnh thực thi**:
  ```powershell
  cd "d:\create\DATN\Agenttic-RAG-for-e-commerce"
  $env:PYTHONUTF8=1
  conda run -n DL python scripts/seed_bench.py --cases scripts/fixtures/seed_bench.sample.jsonl --products-from-db --reset
  ```
- **Kết quả lệnh**:
  ```json
  {"seeded_cases": 2, "reset": true, "accounts": 3}
  ```
- **Đối soát Database trước và sau khi `--reset`**:
  - `bench_cases`: Giữ nguyên đúng 2 dòng (`smoke-order-a` và `smoke-review-a`).
  - Tổng số `orders`: Giữ nguyên 37 đơn (không đơn nào của user khác bị xóa).
  - Tổng số `reviews`: Giữ nguyên 19 đánh giá (chỉ bản ghi review seed của bench được thay thế).
- **Kết luận**: **ĐẠT**. Cơ chế `--reset` thực hiện đúng phạm vi namespace bench mà không tác động tới dữ liệu shop.

---

### 2.6 Mục 6: Replay Stripe Webhook Idempotency
- **Lệnh thực thi**:
  ```powershell
  npx.cmd --yes @stripe/cli@1.55.6 events resend evt_1UXkA2DbFvbSAWxsDNZu1cIK
  ```
- **Kết quả thực tế**:
  - Stripe CLI gửi lại event thành công (Exit Code 0).
  - Webhook endpoint `/api/stripe/webhook` xử lý thành công, trả về HTTP 200 `{ "received": true }`.
  - Tồn kho sản phẩm 1001 trong bảng `products`:
    - Trước khi replay: `stock = 20`.
    - Sau khi replay: `stock = 20` (không bị trừ thêm).
- **Kết luận**: **ĐẠT**. Cơ chế Idempotency xử lý webhook hoạt động chính xác tuyệt đối.

---

## 3. 📋 Danh sách Toàn bộ Bản ghi QA đã Tạo (Cần xin ý kiến Dọn dẹp)

> [!IMPORTANT]
> Toàn bộ các bản ghi dưới đây được QA tạo ra trong quá trình kiểm thử tự động và thủ công trên Supabase thật. Antigravity **không tự ý xoá bất kỳ bản ghi nào** theo đúng cam kết; danh sách này được tổng hợp chi tiết để Claude Opus tham vấn chủ đồ án về phương án dọn dẹp hoặc giữ lại phục vụ benchmark.

### 3.1 Danh sách Đơn hàng (`orders`) do QA tạo (17 đơn)
Tất cả các đơn dưới đây gắn với User A ID `faea467c-6a5b-4e50-84d5-b5220fea8e1a`:
1. `542da29f-442d-48b8-a9e6-d192a7ece2fc` | Stripe / paid | Tổng: 29.990.000 VNĐ | Status: `processing` *(Đơn thanh toán thẻ test live)*
2. `013dd046-5c27-442f-b805-5b49069f212f` | COD / cod_pending | Tổng: 29.990.000 VNĐ | Status: `pending`
3. `8f7240a8-5670-45da-a990-779684a9d493` | COD / cod_pending | Tổng: 13.990.000 VNĐ | Status: `pending`
4. `cb83ab57-5f99-4951-9868-9fbb354c4630` | COD / cod_pending | Tổng: 40.990.000 VNĐ | Status: `pending`
5. `da5ab853-7881-4174-8936-a6732e97e24a` | COD / cod_pending | Tổng: 70.990.000 VNĐ | Status: `pending`
6. `03d64444-dbe6-4db2-bec3-857c31cd6742` | COD / cod_pending | Tổng: 29.990.000 VNĐ | Status: `pending`
7. `9c84f2a5-eb60-4955-aa08-835fc27b6e72` | COD / cod_pending | Tổng: 55.490.000 VNĐ | Status: `pending`
8. `ddbf26af-3864-4082-a7e1-7cd662d8c2a5` | COD / cod_pending | Tổng: 3.390.000 VNĐ | Status: `pending`
9. `b37f81c5-4485-4a01-9aeb-cf445185873d` | COD / cod_pending | Tổng: 22.990.000 VNĐ | Status: `pending`
10. `8f19ecfa-2629-4ee4-9ddd-8a6a6701dffd` | COD / cod_pending | Tổng: 29.990.000 VNĐ | Status: `pending`
11. `b4a632d0-88a6-4aff-8443-8f36cb1e94d2` | COD / cod_pending | Tổng: 9.790.000 VNĐ | Status: `pending`
12. `3d1dd37f-a4f2-4651-b684-aa116577ff6d` | COD / cod_pending | Tổng: 3.390.000 VNĐ | Status: `pending`
13. `c3d36aed-a523-46d4-af80-679b8314c955` | COD / cod_pending | Tổng: 3.390.000 VNĐ | Status: `pending`
14. `979b9782-afc2-4d55-96c9-87ecc0ac4543` | COD / cod_pending | Tổng: 9.790.000 VNĐ | Status: `pending`
15. `4f842629-bca1-44e2-8499-7a8db4a3a744` | COD / cod_pending | Tổng: 29.990.000 VNĐ | Status: `pending`
16. `071c60b1-a03f-4f17-a5d5-4e9c1e419372` | COD / cod_pending | Tổng: 3.390.000 VNĐ | Status: `pending`
17. `2651cc0c-6334-4a70-9841-610adf2ba57b` | COD / cod_pending | Tổng: 3.390.000 VNĐ | Status: `pending`

### 3.2 Danh sách Đánh giá (`reviews`) do QA tạo (8 đánh giá)
1. `d14e6c0a-9cf4-4eb6-a5ad-c418082fed71` | Sản phẩm 1001 | 5 sao | "Hàng chính hãng VN/A rất đẹp! 🌟 Giá hợp lý, giao nhanh 🚀 (test Unicode chuẩn)."
2. `8eb18186-eb19-4f07-acaf-845ad7169b5a` | Sản phẩm 1001 | 5 sao | Trùng nội dung trên (test duplicate 1)
3. `7a237122-d0b3-4232-8955-dba4d107e03d` | Sản phẩm 1001 | 5 sao | Trùng nội dung trên (test duplicate 2)
4. `c9ad48b6-8f65-4f0d-9a5c-3efb0de66677` | Sản phẩm 1001 | 5 sao | Trùng nội dung trên (test duplicate 3)
5. `a51e0cd4-f441-4a71-8629-650bd6b2d4bc` | Sản phẩm 136045 | 5 sao | "Đánh giá Nubia Neo 5 GT test QA2 🚀 Hiệu năng cực tốt 💯! (Unicode chuẩn test)."
6. `4910fd2b-848d-4003-8b04-94f2200b6a91` | Sản phẩm 136045 | 4 sao | "Đánh giá lặp lần 2 xem backend có chặn không" (bằng chứng BUG-A-01)
7. `0b3b9a10-0361-4761-8538-cd2bec74f02f` | Sản phẩm 135935 | 5 sao | "Đánh giá Laptop Lenovo Yoga Slim 7 test QA2 🚀 Màn hình OLED cực nét 💯! (Unicode chuẩn test)."
8. `cdc06905-1962-4266-ac48-7e499a416602` | Sản phẩm 135935 | 4 sao | "Đánh giá lặp lần 2 cho Lenovo Yoga Slim 7 xem backend có chặn không" (bằng chứng BUG-A-01)

### 3.3 Danh sách Ticket Hỗ trợ (`support_tickets`) do Agent tạo (2 tickets)
1. `cad7a999-ffce-4c89-a484-10e084572409` | Order: `542da29f-442d-48b8-a9e6-d192a7ece2fc` | CreatedBy: `agent` | Category: `other` | Status: `open` | Note: "Đơn hàng 542da29f-442d-48b8-a9e6-d192a7ece2fc giao chậm"
2. `8b07dca2-2737-4f77-b1b7-05f136052a80` | Order: `542da29f-442d-48b8-a9e6-d192a7ece2fc` | CreatedBy: `agent` | Category: `other` | Status: `open` | Note: "Báo đơn hàng 542da29f-442d-48b8-a9e6-d192a7ece2fc giao chậm"

---

## 4. 🎯 Kết luận & Kiến nghị

1. **Gói QA2 đã hoàn tất 100%** theo đúng 8 yêu cầu chi tiết của Claude Opus. Toàn bộ 23 mục kiểm thử đã được xác thực bằng dữ liệu và kịch bản chạy thật trên môi trường tích hợp.
2. **BUG-A-01 (backend)** đã được xác nhận bằng chứng đầy đủ trong code, database và kịch bản test tự động. Lỗi này chuyển giao cho Codex xử lý ở đợt K5.
3. **Phần A của Antigravity (Tầng 3)** đã sẵn sàng cho bước nghiệm thu cuối cùng để chuyển giao sang Phần B.
