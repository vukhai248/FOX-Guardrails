# Kế hoạch Kiểm thử Toàn diện Hệ thống (Post-Merge QA Plan)

**Người soạn thảo**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `feat/a-frontend`  
**Ngày cập nhật**: 03/11/2026 (Phiên bản đồng bộ H2 theo hợp đồng backend Codex)  
**Tham chiếu chỉ đạo**: Phản hồi nghiệm thu lần 5 từ Claude Opus & Bàn giao tổng hợp `codex-HANDOFF-A.md`

---

## 1. 🎯 Mục tiêu & Điều kiện Tiên quyết

### 1.1 Mục tiêu
Xác thực toàn diện tính toàn vẹn chức năng, luồng nghiệp vụ E-Commerce, hợp đồng API và các lớp phòng thủ an ninh mạng trên toàn bộ hệ thống sau khi **Claude Opus** thực hiện merge hai nhánh `feat/a-frontend` và `feat/a-backend`.

### 1.2 Điều kiện Tiên quyết (Prerequisites)
> [!IMPORTANT]
> **Bộ kiểm thử này CHỈ ĐƯỢC PHÉP CHẠY khi thỏa mãn toàn bộ các điều kiện sau:**
> 1. Nhánh `feat/a-frontend` và `feat/a-backend` đã được Claude Opus gộp (merge) thành công vào nhánh chung.
> 2. Chủ đồ án đã thực thi an toàn đủ 5 file migration theo đúng thứ tự trên Supabase (kèm bản sao lưu toàn bộ database trước khi chạy):
>    - `database/migrations/2026-11_payment_and_address.sql` (thu hồi quyền INSERT của client, chuyển tạo đơn sang RPC server).
>    - `database/migrations/2026-11_chat_logs_guard.sql` (thêm cột `guard_decision_ids text[]` và index `(session_id, created_at)`, khóa quyền đọc/ghi client, cấp cho service_role).
>    - `database/migrations/2026-11_product_reviews.sql` (thu hồi quyền ghi client, tạo RPC `create_product_review` ràng buộc chỉ khách đã mua mới được đánh giá).
>    - `database/migrations/2026-11_seed_bench.sql` (bảng mapping và RPC phục vụ benchmark seed).
>    - `database/migrations/2026-11_expired_checkout.sql` (bổ sung overload hàm RPC `fail_stripe_order(p_order_id uuid, p_session_id text)` xử lý sự kiện `checkout.session.expired` có chữ ký).
> 3. Đã chạy seed dữ liệu đánh giá benchmark theo [SEED-BENCH.md](../SEED-BENCH.md):
>    - Lệnh: `conda run -n DL python scripts/seed_bench.py --cases D:/create/DATN/FOX-Guardrails/eval/datasets/vi_cskh/seed_cases.jsonl`
>    - File `.env.bench` được tạo tự động tại gốc workspace chứa credentials của `bench_customer_a`, `bench_customer_b`, `bench_admin`.
> 4. **QUY TẮC KHỞI ĐỘNG MÔI TRƯỜNG BẮT BUỘC**:
>    - Phải tắt toàn bộ các tiến trình dev server cũ đang chiếm cổng 3000 và 8080.
>    - Khởi động lại dev server sạch từ đúng thư mục làm việc đã merge:
>      - Terminal 1 (Backend): `$env:PYTHONUTF8=1; cd rag-service; conda run -n DL uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload`
>      - Terminal 2 (Frontend): `cd web_ui; npm.cmd run dev`
>      - Terminal 3 (Stripe CLI): `stripe listen --forward-to localhost:3000/api/stripe/webhook`

---

## 2. 📋 Danh mục Các Ca Kiểm thử Trọng Yếu (Critical QA Test Cases)

### Ca 1: Đặt hàng COD & Thanh toán Stripe Thẻ Test `4242...` (Inventory & Idempotency)
- **Mục tiêu**: Kiểm tra luồng thanh toán đa phương thức, cập nhật trạng thái đơn hàng chính xác và trừ kho sản phẩm đúng 1 lần duy nhất (chống trừ kho kép).
- **Các bước thực hiện**:
  1. **Luồng COD**:
     - Đăng nhập tài khoản `bench_customer_a`.
     - Thêm sản phẩm (ví dụ: iPhone 15 Pro Max, số lượng 1) vào giỏ hàng.
     - Vào `/checkout`, kiểm tra thông tin địa chỉ tách trường.
     - Chọn phương thức: *Thu tiền khi nhận hàng (COD)* -> Bấm *Xác nhận đặt hàng*.
     - **Kỳ vọng**: Chuyển hướng sang `/checkout-success?order_id=...` (URL không lộ PII). Trạng thái đơn trong DB là `status: 'pending'`, `payment_status: 'cod_pending'`. Tồn kho (`products.stock`) của sản phẩm giảm đi đúng 1 đơn vị.
  2. **Luồng Stripe (Thẻ Test `4242...`)**:
     - Thêm sản phẩm vào giỏ hàng -> Chọn phương thức *Thẻ tín dụng / Stripe*.
     - Nhập số thẻ: `4242 4242 4242 4242`, ngày hết hạn hợp lệ trong tương lai, CVC bất kỳ -> Bấm thanh toán.
     - Stripe CLI bắt sự kiện `checkout.session.completed` hoặc `checkout.session.async_payment_succeeded` và chuyển tiếp webhook về `/api/stripe/webhook`.
     - **Kỳ vọng**: Đơn hàng chuyển sang `payment_status: 'paid'`. Tồn kho (`products.stock`) bị trừ chính xác 1 lần.
  3. **Kiểm tra Tính Bất Biến (Idempotency)**:
     - Không gửi lại payload thô (tránh sai chữ ký webhook). Sử dụng Stripe CLI để gửi lại sự kiện webhook đã ký hợp lệ:
       ```powershell
       stripe events resend <evt_id>
       ```
     - **Kỳ vọng**: API trả về `200 OK` với body đúng định dạng `{ received: true }`. Kiểm tra trong database Supabase: số lượng tồn kho `products.stock` **tuyệt đối không bị trừ thêm lần nữa**.

---

### Ca 2: Chống Can Thiệp Giá & ID Người Dùng (Price & User ID Tampering Protection)
- **Mục tiêu**: Đảm bảo kẻ tấn công không thể mua hàng với giá tùy biến (ví dụ: sửa 30 triệu thành 1.000 VNĐ) hoặc mạo danh người khác đặt hàng.
- **Các bước thực hiện**:
  1. Gửi request trực tiếp lên `POST /api/orders` với payload cố tình can thiệp giá và `user_id`:
     ```json
     {
       "items": [
         {
           "product_id": 1,
           "quantity": 1,
           "price": 1000
         }
       ],
       "user_id": "00000000-0000-0000-0000-000000000000",
       "recipient_name": "Attacker",
       "recipient_phone": "0988888888",
       "address_line": "123 Hack St",
       "ward": "Phường Phúc Xá",
       "province": "Thành phố Hà Nội",
       "note": "Ghi chú can thiệp",
       "payment_method": "cod"
     }
     ```
     *(Lưu ý: Schema đơn hàng không có trường `district`; chỉ gồm `recipient_name`, `recipient_phone`, `address_line`, `ward`, `province`, `note`).*
  2. **Kỳ vọng**:
     - Nếu gửi request mà **không kèm Bearer token**: API trả về ngay **401 `UNAUTHENTICATED`** (hệ thống không hỗ trợ đơn hàng khách vãng lai).
     - Khi gửi kèm Bearer token hợp lệ của user:
       - Hàm RPC server-side `create_shop_order` **hoàn toàn bỏ qua trường `price`** do client gửi lên.
       - Server tự động truy vấn giá niêm yết thực tế từ bảng `products` trong DB để tính cột tổng tiền `total`.
       - Server **hoàn toàn bỏ qua `user_id` giả mạo** trong body, chỉ sử dụng user ID từ token JWT đã xác thực.

---

### Ca 3: Kiểm Soát Quyền Truy Cập Chéo Đơn Hàng (Cross-Account Isolation / PII Protection)
- **Mục tiêu**: Ngăn chặn rò rỉ thông tin cá nhân (PII) khi người dùng cố tình đoán `order_id` của khách hàng khác.
- **Các bước thực hiện**:
  1. Dùng tài khoản `bench_customer_a` tạo một đơn hàng thành công, ghi nhận mã đơn: `ORDER_ID_A`.
  2. Đăng xuất và đăng nhập bằng tài khoản `bench_customer_b` (hoặc gọi API không có token).
  3. Gửi request `GET /api/orders/ORDER_ID_A`.
  4. Truy cập giao diện trực tiếp tại: `/account` và `/checkout-success?order_id=ORDER_ID_A`.
- **Kỳ vọng**:
  - API `GET /api/orders/ORDER_ID_A` từ chối và trả về đúng **404 NOT_FOUND** (tuân thủ chuẩn OWASP API Security: không trả về 403 để tránh để lộ sự tồn tại của đơn hàng).
  - Không có bất kỳ thông tin PII nào (Tên, Số điện thoại, Địa chỉ giao hàng) của Khách hàng A bị rò rỉ sang phiên của Khách hàng B.

---

### Ca 4: Kiểm Thử Hội Thoại Multi-turn Agentic RAG Thực Tế
- **Mục tiêu**: Đảm bảo Master Agent và các Tool (`product_reviews`, `create_support_ticket`) hoạt động chính xác với dữ liệu thật, không hallucination.
- **Các bước thực hiện**:
  1. **Câu hỏi 1 (Đọc Đánh Giá - Tool `product_reviews`)**:
     - Mở Chat widget, nhập: *"Mọi người đánh giá iPhone 16 thế nào?"*.
     - **Kỳ vọng**: Master Agent gọi tool `product_reviews` truy vấn bảng `reviews`.
       - Nếu sản phẩm có review: Trích xuất đánh giá sao và bình luận trung thực từ khách hàng.
       - Nếu sản phẩm chưa có review trong database: Master Agent trả lời rõ ràng là **"Chưa có đánh giá"**, tuyệt đối không bịa đặt review giả.
  2. **Câu hỏi 2 (Tạo Ticket Hỗ Trợ - Tool `create_support_ticket`)**:
     - Trong cùng phiên chat, nhập tiếp: *"Tạo ticket báo đơn giao chậm"*.
     - **Kỳ vọng**:
       - Người dùng bắt buộc phải đăng nhập; nếu chưa đăng nhập, bot yêu cầu đăng nhập trước khi tạo ticket.
       - Bot gọi tool `create_support_ticket` tạo thành công một bản ghi trong bảng `support_tickets` liên kết với `customer_id` của tài khoản hiện tại.
       - Ticket chỉ gắn được với đơn hàng thuộc sở hữu của chính user đó; không thể gắn `order_id` của tài khoản khác. Phản hồi cung cấp `ticket_id` đã tạo.

---

### Ca 5: Kiểm Thử Tự Động A5.4 Chạy Thật với Tài Khoản `bench_customer_a`
- **Mục tiêu**: Chốt nghiệm thu hoàn toàn gói **A5-UI**, chứng minh module `requireRole` chặn đứng tấn công leo quyền quản trị viên trên API server thật.
- **Các bước thực hiện**:
  1. Kiểm tra sự tồn tại của biến trong file `.env.bench` ở gốc repo (không in giá trị secret):
     ```powershell
     Select-String -Path ..\.env.bench -Pattern '^BENCH_CUSTOMER_EMAIL=' -Quiet
     Select-String -Path ..\.env.bench -Pattern '^BENCH_CUSTOMER_PASSWORD=' -Quiet
     ```
     *(Email thật được tạo qua seed có dạng `bench_customer_a+<namespace>@example.invalid`).*
  2. Chạy kịch bản test Playwright A5.4:
     ```powershell
     cd web_ui
     npx.cmd playwright test tests/e2e/a5_ui.spec.ts -g "A5.4" --reporter=list
     ```
- **Kỳ vọng**:
  - Test nạp credentials từ `.env.bench` thành công, đăng nhập tài khoản thật qua Supabase client.
  - Tự cập nhật `user_metadata.role = 'admin'` ở phía client.
  - Gọi cả 4 route `GET /api/admin/{chat-logs,orders,tickets,users}` và 1 route `PUT /api/admin/users`.
  - Toàn bộ 5 request đều nhận phản hồi **403 `FORBIDDEN`** do máy chủ kiểm tra bảng quyền lực duy nhất `public.user_roles`.
  - Test **PASSED (KHÔNG BỊ SKIP)**.

---

### Ca 6: Kiểm Thử Quyền Đánh Giá Sản Phẩm (Reviews API Contract)
- **Mục tiêu**: Xác thực ràng buộc nghiệp vụ chỉ khách hàng đã mua sản phẩm mới được gửi đánh giá (`POST /api/reviews`).
- **Các bước thực hiện**:
  1. Kiểm tra trường hợp **Chưa mua hàng**:
     - Lưu ý: Dataset seed mẫu đã tạo sẵn đơn hàng cho `bench_customer_a`. Vì vậy, để kiểm tra ca "chưa mua", sử dụng tài khoản `bench_customer_b` (chưa có đơn hàng nào) hoặc dùng `bench_customer_a` đánh giá một sản phẩm chưa từng có trong đơn hàng nào của user này.
     - Gửi request `POST /api/reviews` với rating 5 sao:
     - **Kỳ vọng**: API từ chối và trả về **403 FORBIDDEN** với mã lỗi `NOT_PURCHASED`.
  2. Kiểm tra trường hợp **Đã mua hàng hợp lệ**:
     - Điều kiện đủ điều kiện đánh giá theo RPC `create_product_review`: Đơn hàng phải có `status <> 'cancelled'` **VÀ** `payment_status` thuộc một trong hai giá trị: `'paid'` (đã thanh toán trực tuyến) hoặc `'cod_pending'` (đơn COD đang xử lý giao hàng).
     - Dùng tài khoản có đơn thỏa mãn điều kiện trên gửi `POST /api/reviews`:
     - **Kỳ vọng**: API chấp nhận và trả về **201 CREATED**. Bản ghi được lưu vào bảng `reviews`.
  3. Kiểm tra các trường hợp **Không đủ điều kiện**:
     - Đơn hàng ở trạng thái bị hủy (`status: 'cancelled'`), chưa thanh toán (`payment_status: 'unpaid'`), hoặc đã hoàn tiền (`payment_status: 'refunded'`):
     - **Kỳ vọng**: Không đủ điều kiện đánh giá, API trả về **403 FORBIDDEN** (`NOT_PURCHASED`).
  4. Đánh giá chứa ký tự tiếng Việt có dấu, ký tự Unicode đặc biệt hoặc emoji:
     - **Kỳ vọng**: Dữ liệu lưu và đọc ra giữ nguyên vẹn 100% đúng codepoint Unicode, không bị lỗi font hay biến dạng ký tự.

---

### Ca 7: Kiểm Thử Cách Ly Lịch Sử Chat, Audit Log & Giới Hạn Session ID
- **Mục tiêu**: Đảm bảo bảo mật phiên hội thoại khách hàng, ghi nhận nhật ký audit log đầy đủ và phòng chống tràn bộ nhớ.
- **Các bước thực hiện**:
  1. **Cách ly phiên chat**:
     - Hai người dùng đăng nhập tài khoản khác nhau trên 2 trình duyệt riêng biệt.
     - Kiểm tra không xảy ra rò rỉ hay nhìn thấy lịch sử câu hỏi của nhau trong chat widget.
  2. **Kiểm tra giới hạn độ dài `session_id`**:
     - Gửi request trực tiếp tới FastAPI `POST http://localhost:8080/chat` hoặc qua proxy frontend `POST /api/chat` với `session_id` dài vượt quá 100 ký tự.
     - **Kỳ vọng**: Backend từ chối ngay với mã lỗi **422 Unprocessable Entity** trước khi chuyển tiếp vào mô hình bot. Proxy `/api/chat` chuyển tiếp nguyên vẹn mã trạng thái 422 về client (không bị nuốt thành 503).
  3. **Kiểm tra Nhật ký Hội thoại (`chat_logs`)**:
     - Thực hiện hội thoại liên tục 3 lượt hỏi đáp qua lại (multi-turn).
     - Truy vấn bảng `chat_logs` trong cơ sở dữ liệu:
     - **Kỳ vọng**: Có đúng 6 dòng nhật ký được ghi lại với role là `user` và `agent` (không phải `assistant`). Trường `tool_used` chỉ ghi nhận danh sách công cụ được gọi trong chính lượt đó.
     - Nếu cơ chế ghi log DB tạm thời gián đoạn, client không được tự ý retry gây trùng lặp ticket.

---

### Ca 8: Kiểm Thử API Sức Khỏe Hệ Thống (`/health`)
- **Mục tiêu**: Đảm bảo endpoint `/health` phản ánh trung thực tình trạng kết nối backend tới các dịch vụ phụ thuộc.
- **Các bước thực hiện**:
  1. Khi hệ thống hoạt động bình thường:
     - Gọi `GET /health` -> Trả về `status: "healthy"`, `supabase_connected: true`, `chroma_connected: true`.
  2. Giả lập ngắt kết nối Supabase hoặc ChromaDB, hoặc collection ChromaDB bị rỗng:
     - Gọi `GET /health` -> Trả về `status: "degraded"`.
     - **Kỳ vọng**: Không làm lộ thông tin exception stack trace, API credentials hay secret keys ra bên ngoài.

---

### Ca 9: Kiểm Thử Tính Bất Biến (Idempotency) & Reset Benchmark Seed (A7)
- **Mục tiêu**: Xác thực cơ chế seed dữ liệu benchmark có khả năng tái lập và an toàn dữ liệu.
- **Các bước thực hiện**:
  1. **Chuẩn bị dữ liệu mẫu**:
     - Do bộ dataset chính thức từ Tầng C đang hoàn thiện, tạm thời sử dụng file fixture có sẵn `scripts/fixtures/seed_bench.sample.jsonl`.
     - Sử dụng cờ `--products-from-db` để script tự động lấy các `product_id` hợp lệ có sẵn trong cơ sở dữ liệu Supabase, không cần sửa tay `product_id` trong file fixture.
  2. **Kiểm tra tính Idempotent**:
     - Chạy script seed lần 2 với cùng một file dữ liệu JSONL kèm cờ `--products-from-db`:
       ```powershell
       conda run -n DL python scripts/seed_bench.py --cases scripts/fixtures/seed_bench.sample.jsonl --products-from-db
       ```
     - **Kỳ vọng**: Dữ liệu và các ID bản ghi được giữ nguyên vẹn, không sinh thêm dòng rác hay nhân đôi bản ghi.
  3. **Kiểm tra cơ chế Reset có kiểm soát (`--reset`)**:
     - Chạy lệnh seed kèm cờ `--reset` và `--products-from-db`:
       ```powershell
       conda run -n DL python scripts/seed_bench.py --cases scripts/fixtures/seed_bench.sample.jsonl --products-from-db --reset
       ```
     - **Kỳ vọng**: Script chỉ xóa và tái tạo các dòng dữ liệu nằm trong namespace mapping của file credential hiện tại; tuyệt đối không xóa dữ liệu thật của cửa hàng hoặc namespace khác.
     - Nếu một đơn hàng bench đang có ticket ngoại lai tham chiếu tới: script từ chối reset (`BENCH_REFERENCED`) để tránh phá vỡ toàn vẹn dữ liệu.

---

## 3. 📝 Quy trình Ghi nhận Lỗi (Bug Reporting Protocol)

Nếu phát hiện bất kỳ lỗi sai khác nào so với kết quả mong đợi trong quá trình thực thi các ca kiểm thử trên:
1. Tạo hoặc cập nhật file: `docs/QA/bugs.md`.
2. Format mẫu ghi nhận bug:
   ```markdown
   ### [BUG-00X] Tiêu đề ngắn gọn của lỗi
   - **Mức độ**: Critical / High / Medium / Low
   - **Ca kiểm thử**: Ca 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 / 9
   - **Các bước tái hiện**:
     1. ...
     2. ...
   - **Kết quả mong đợi**: ...
   - **Kết quả thực tế**: ...
   - **Bằng chứng**: Ảnh chụp / Log API đính kèm tại `docs/reports/evidence/`
   ```
