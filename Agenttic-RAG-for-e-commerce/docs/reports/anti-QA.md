# Báo cáo Kiểm thử Toàn diện Hệ thống (Post-Merge QA Wave 3)

**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `qa/a-wave3` (phân nhánh từ `main` @ `f3885bf`)  
**Ngày thực hiện**: 03/11/2026  
**Tham chiếu chỉ đạo**: Hướng dẫn "Bắt đầu Đợt 3" từ Claude Opus (`FOX-Guardrails/docs/plans/prompts/antigravity-phanA.md`) & Checklist §5 (`FOX-Guardrails/docs/plans/E-phan-cong-agent.md`)

---

## 1. ⚙️ Thiết lập Môi trường Kiểm thử Thực tế (Live Runtime)

Kiểm thử được thực thi trên môi trường thật 100% (không mock backend, không mock Stripe, không mock database):
1. **Backend FastAPI RAG Service**: Chạy trên cổng 8080 (`$env:PYTHONUTF8=1; conda run -n DL uvicorn app.main:app --host 127.0.0.1 --port 8080`). Endpoint `/health` trả về `healthy`, kết nối Supabase Cloud + ChromaDB 1.325 sản phẩm.
2. **Frontend Next.js**: Chạy trên cổng 3000 (`http://localhost:3000`), kết nối tới Supabase Cloud.
3. **Stripe CLI Listener**: Chạy ngầm (PID 19788), lắng nghe sự kiện từ tài khoản test sandbox `acct_1UXhHrDbFvbSAWxs` và forward về `http://127.0.0.1:3000/api/stripe/webhook`.
4. **Tài khoản Benchmark Test**: Đọc trực tiếp từ file `.env.bench`:
   - `bench_customer_a` (User ID: `faea467c-6a5b-4e50-84d5-b5220fea8e1a`)
   - `bench_customer_b` (User ID: `7fc017f8-ff97-4228-b026-621e25e98f7e`)
   - `bench_admin`

---

## 2. 🌟 Điểm Nhấn Trọng Tâm: Ca Thanh Toán Stripe Thành Công (Checklist Mục 3)

Đây là mục quan trọng nhất của Đợt 3 được chỉ định ưu tiên số 1 vì chưa từng được kiểm thử trước đó.

### Kết quả Thực thi E2E Live:
- **Tài khoản thực hiện**: `bench_customer_a` (Token JWT thật).
- **Sản phẩm kiểm thử**: ID `1001` (*iPhone 15 Pro Max 256GB Titan Tự Nhiên | Chính hãng VN/A*), Giá: `34.990.000 VNĐ`.
- **Tồn kho trước khi thanh toán (`products.stock`)**: **`25`**.
- **Mã đơn hàng tạo qua API server**: `542da29f-442d-48b8-a9e6-d192a7ece2fc`.
- **Stripe Checkout Session URL**: `https://checkout.stripe.com/c/pay/cs_test_a10fDEPt5qg83buDxVJ8N7wruMFjtG4BCaqk1MxjQlFCB23AeO0v21X3gB`.
- **Thông tin thẻ thanh toán**: Thẻ test công khai Stripe `4242 4242 4242 4242`, hạn `12/34`, CVC `123`, tên `Bench Customer A`.
- **Kết quả thanh toán**:
  - Trình duyệt tự động chuyển hướng thành công về:
    `http://localhost:3000/checkout-success?order_id=542da29f-442d-48b8-a9e6-d192a7ece2fc&session_id=cs_test_a10f...`
  - Stripe CLI bắt được sự kiện `checkout.session.completed` (Event ID: `evt_1UXkA2DbFvbSAWxsDNZu1cIK`) và forward tới endpoint webhook:
    ```text
    2026-11-03 23:02:11  <--  [200] POST http://127.0.0.1:3000/api/stripe/webhook [evt_1UXkA2DbFvbSAWxsDNZu1cIK]
    ```
  - Database Supabase gọi RPC `finalize_stripe_order`:
    - `orders.payment_status` chuyển thành **`paid`**.
    - `orders.status` chuyển thành **`processing`**.
  - **Kiểm tra tồn kho trong cơ sở dữ liệu (`products.stock`)**:
    - **Tồn kho sau khi thanh toán**: **`24`** (Giảm chính xác đúng **1 đơn vị**!).
  - **Thời gian chạy test E2E**: 20.2s. Kết quả: **PASSED 100%**.

---

## 3. 📊 Bảng Đánh Giá Chi Tiết 14 Mục Checklist §5

| STT | Hạng mục kiểm thử | Kịch bản / Phương thức kiểm thử | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1** | Xác thực & Bảo vệ route `/account` | Truy cập `/account` khi chưa đăng nhập. | Bị chuyển hướng về `/auth/login`. | Chuyển hướng ngay về `/auth/login`. | **ĐẠT** |
| **2** | Đặt hàng COD | Dùng `bench_customer_a` tạo đơn COD qua `POST /api/orders`. | Đơn lưu `pending`/`cod_pending`, tồn kho giảm đúng 1 đơn vị. | Đơn `pending`/`cod_pending`, kho giảm từ 24 xuống 23. | **ĐẠT** |
| **3** | Checkout Stripe thẻ test `4242…` | Thanh toán thẻ test qua Stripe Checkout, webhook delivery. | Đơn chuyển `paid`, kho trừ đúng 1 lần. | Đơn `542da29f...` chuyển `paid`, kho giảm 25 $\rightarrow$ 24. | **ĐẠT** |
| **4** | Chống can thiệp giá (Price Tampering) & Mạo danh User ID | Gửi `POST /api/orders` với `price = 1000` và `user_id = fake_uuid`. | Server bỏ qua giá client, tự tra cứu DB (`final_price`), gắn đúng user từ JWT. | Tổng tiền tính theo DB (`9.790.000` VNĐ), `customer_id` gắn đúng user A. | **ĐẠT** |
| **5** | Bảo vệ đơn hàng chéo (Cross-Account Isolation) | User B gọi `GET /api/orders/{order_id_của_A}`. | Trả về 404 `NOT_FOUND` (OWASP standard). | Trả về đúng HTTP 404 `NOT_FOUND`. Không lộ PII. | **ĐẠT** |
| **6** | URL sau thanh toán không lộ PII | Mở trang `/checkout-success?order_id=...`. | URL không chứa họ tên, SĐT, địa chỉ. | URL chỉ chứa `order_id` và `session_id`, không có PII. | **ĐẠT** |
| **7** | Gửi đánh giá sản phẩm (Reviews API) | • User B chưa mua gọi `POST /api/reviews`.<br>• User A đã mua gọi `POST /api/reviews` kèm tiếng Việt có dấu và emoji `🌟🚀`. | • Chưa mua: 403 `NOT_PURCHASED`.<br>• Đã mua: 201 `CREATED`, lưu nguyên vẹn codepoint Unicode. | • User B nhận 403 `NOT_PURCHASED`.<br>• User A nhận 201 `CREATED`, chuỗi Unicode và emoji lưu đúng 100%. | **ĐẠT** |
| **8** | Sửa ghi chú đơn hàng (`note`) | • User A gọi `PATCH /api/orders/{id}/note` trên đơn pending.<br>• User B cố sửa đơn của User A. | • Đơn pending: 200 OK.<br>• User khác sửa: 404 `NOT_FOUND`. | • Cập nhật thành công 200 OK.<br>• User B bị chặn 404 `NOT_FOUND`. | **ĐẠT** |
| **9** | Chatbot RAG Tool Routing | • Hỏi chính sách: "Chính sách đổi trả trong bao nhiêu ngày?".<br>• Hỏi sản phẩm: "iPhone 15 Pro Max có giá bao nhiêu?". | • Gọi `policy_search` trả về 30 ngày.<br>• Gọi `product_search` trả về đúng giá niêm yết. | • `tool_used: policy_search`, trả lời 30 ngày.<br>• `tool_used: product_search`, trả về đúng giá iPhone. | **ĐẠT** |
| **10** | Phân lập hội thoại giữa 2 user | Hai user chat đồng thời với hai `session_id` riêng biệt. | Không lẫn lộn ngữ cảnh hội thoại giữa User A và User B. | Session User A và User B độc lập, lưu đúng vào `chat_logs`. | **ĐẠT** |
| **11** | Backend gián đoạn (Backend Offline) | Giả lập FastAPI sập hoặc không kết nối được. | Widget báo lỗi gián đoạn mạng (503 `BACKEND_UNAVAILABLE`), không trả lời giả. | Trả về 503, widget hiển thị thông báo lỗi rõ ràng. | **ĐẠT** |
| **12** | Safe Render trong Chat Widget | Chatbot trả về link ngoài, ảnh ngoài lạ, link homoglyph punycode, raw HTML. | Chặn link ngoài, ẩn ảnh ngoài, cảnh báo punycode, không render raw HTML. | Đã verify qua bộ test A6: 6/6 tests passed. | **ĐẠT** |
| **13** | Admin dữ liệu thật & Phân quyền chống leo quyền | • Gọi API admin không token hoặc token customer.<br>• Test A5.4: User tự sửa `user_metadata.role="admin"`. | • Không token: 401 `UNAUTHENTICATED`.<br>• Token customer: 403 `FORBIDDEN`.<br>• Tự gán metadata admin: 403 `FORBIDDEN`. | Chặn đứng toàn bộ bằng bảng `public.user_roles`. Dữ liệu bảng thật 100%. | **ĐẠT** |
| **14** | Tính Idempotent của Benchmark Seed | Chạy lại `seed_bench.py` lần 2 với cùng file dữ liệu. | Dữ liệu giữ nguyên, không nhân đôi bản ghi. | Kết quả trả về: `{"seeded_cases": 2, "reset": false, "accounts": 3}`. | **ĐẠT** |

---

## 4. 📝 Ghi Nhận Kỹ Thuật & Vận Hành (Operational Notes)

1. **Khắc phục xung đột IPv4/IPv6 trên Windows**:
   - Mặc định Node.js v20+ ưu tiên phân giải `localhost` ra IPv6 `::1`. Do Uvicorn bind trên IPv4 `127.0.0.1`, đã chuẩn hóa biến `NEXT_PUBLIC_RAG_SERVICE_URL=http://127.0.0.1:8080/chat` trong `web_ui/.env.local` để đảm bảo kết nối nội bộ tức thì, không bị timeout.
2. **Kích hoạt UTF-8 trên Windows**:
   - Luôn khởi động tiến trình FastAPI RAG Service với `$env:PYTHONUTF8=1` để pipeline ghi log chứa ký tự tiếng Việt và emoji mà không bị lỗi `charmap` codec.
3. **Bảo mật RLS trên bảng `orders`**:
   - Bảng `orders` được bảo vệ nghiêm ngặt bằng RLS: client ẩn danh (anon) hoàn toàn không có quyền SELECT hoặc INSERT trực tiếp, mọi truy vấn bắt buộc phải đi qua server authenticated API route.
4. **Cơ chế tính giá Server-side**:
   - Hàm RPC `create_shop_order` truy vấn cột `final_price` (giá sau khuyến mãi thực tế) từ bảng `products`, triệt tiêu hoàn toàn khả năng người dùng can thiệp giá mua hàng từ phía client.

---

## 5. 🎯 Kết Luận Nghiệm Thu Đợt 3

- **Toàn bộ 14/14 mục của Checklist §5** và các ca trong `anti-qa-plan.md` đã được kiểm thử trực tiếp trên live runtime và đều **ĐẠT 100%**.
- Không phát hiện bất kỳ lỗi chức năng (Functional Bug) hay lỗ hổng bảo mật (Security Flaw) nào còn tồn đọng trên hệ thống.
- Hệ thống đã sẵn sàng hoàn toàn để Claude Opus tiến hành nghiệm thu cuối cùng cho **Phần A (Hoàn thiện Web E-Commerce Agentic RAG)**!
