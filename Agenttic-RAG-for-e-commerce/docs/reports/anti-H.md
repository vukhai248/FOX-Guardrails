# Báo cáo Hoàn thành Gói H1 & H2 — Chuẩn Hóa Tài Liệu Vận Hành & Kế Hoạch QA

**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `feat/a-frontend`  
**Ngày thực hiện**: 03/11/2026  
**Tham chiếu chỉ đạo**: Phản hồi Nghiệm thu lần 5 từ Claude Opus (`docs/reports/nghiem-thu-A.md`) & Bàn giao tổng hợp `codex-HANDOFF-A.md`

---

## 1. 🎯 Tổng Quan Kết Quả

Antigravity đã rà soát toàn bộ mã nguồn backend trên nhánh `feat/a-backend` và hoàn thành 100% các yêu cầu chuẩn hóa thuộc hai gói **H1** và **H2**, xóa bỏ toàn bộ các suy đoán về tên biến, sự kiện webhook, tên cột database, tên hàm RPC, schema và công cụ hội thoại:

| Gói | Nhiệm vụ | Trạng thái | Tập tin xử lý | Tóm tắt kết quả |
| :---: | :--- | :---: | :--- | :--- |
| **H1** | Sửa `docs/RUN.md` | **ĐÃ XONG** | `docs/RUN.md` | Chuẩn hóa sự kiện Stripe webhook, giới hạn `FOX_GUARD_MODE=off`, giá trị `BENCH_RECORD=1` ghi JSONL cục bộ, dải giá trị `BENCH_TEMPERATURE` [0, 2], liệt kê đủ 4 file migration theo thứ tự và sao lưu toàn bộ DB. |
| **H2** | Sửa `docs/reports/anti-qa-plan.md` & đính chính `anti-G.md` | **ĐÃ XONG** | `docs/reports/anti-qa-plan.md`<br>`docs/reports/anti-G.md` | Đổi sang `products.stock`, RPC `create_shop_order`, tổng tiền `total`, bỏ `district`, tool `product_reviews`/`create_support_ticket`, bảng `reviews`, format email bench `.invalid`, bổ sung đủ 4 ca kiểm thử từ `codex-HANDOFF-A.md` §5 (Review API, Chat log/session length, Health degraded, Seed idempotency & reset). Đính chính Ca 5 trong `anti-G.md` thành kỳ vọng. |

---

## 2. 📋 Chi Tiết Từng Điểm Đã Sửa Đổi

### 2.1 Gói H1 — Sửa `docs/RUN.md`
1. **Sự kiện Stripe Webhook**:
   - *Trước đây*: Ghi nhận sự kiện `payment_intent.succeeded`.
   - *Đã sửa*: Cập nhật chính xác 2 sự kiện backend xử lý là `checkout.session.completed` và `checkout.session.async_payment_succeeded`.
2. **Cờ `FOX_GUARD_MODE`**:
   - *Trước đây*: Liệt kê các giá trị `off` / `baseline` / `guard`.
   - *Đã sửa*: Ghi rõ hiện tại **chỉ chấp nhận duy nhất giá trị `off`** (bất kỳ giá trị nào khác sẽ ném `NotImplementedError` cho tới khi triển khai Phần B; mặc định: `off`).
3. **Cờ `BENCH_RECORD`**:
   - *Trước đây*: Ghi bật/tắt bằng `true` / `false` và ghi vào database.
   - *Đã sửa*: Ghi rõ kích hoạt bằng giá trị **`1`** (giá trị khác hoặc `true` sẽ không ghi gì). Dữ liệu được ghi dưới dạng JSONL cục bộ vào `rag-service/bench_records/YYYY-MM-DD.jsonl` (đã gitignore), **không ghi vào cơ sở dữ liệu**.
4. **Cờ `BENCH_TEMPERATURE`**:
   - *Trước đây*: Chỉ ghi ví dụ `0.0`.
   - *Đã sửa*: Ghi rõ là số thực từ `0.0` đến `2.0`; nếu bỏ biến thì giữ cấu hình mặc định của model.
5. **Quy trình Migration & Sao lưu**:
   - *Trước đây*: Chỉ nêu 1 file migration và sao lưu bảng `orders`.
   - *Đã sửa*: 
     - Yêu cầu sao lưu **toàn bộ cơ sở dữ liệu** (schema & data) trước khi chạy migration.
     - Liệt kê đủ **4 file migration theo đúng thứ tự bắt buộc**:
       1. `database/migrations/2026-11_payment_and_address.sql`
       2. `database/migrations/2026-11_chat_logs_guard.sql`
       3. `database/migrations/2026-11_product_reviews.sql`
       4. `database/migrations/2026-11_seed_bench.sql`
     - Bổ sung bước seed dữ liệu benchmark theo [SEED-BENCH.md](SEED-BENCH.md) sau khi áp dụng đủ 4 migration.

---

### 2.2 Gói H2 — Sửa `docs/reports/anti-qa-plan.md`
1. **Ca 1 (COD & Stripe Test Card)**:
   - Cột tồn kho: Sử dụng chính xác cột **`products.stock`** (thay cho `inventory_quantity`).
   - Webhook idempotency: Phản hồi chuẩn xác từ server là **`{ received: true }`** (không có trường `already_processed`).
   - Kiểm tra gửi lại: Không gửi payload thô để tránh lỗi sai chữ ký (400), hướng dẫn sử dụng lệnh Stripe CLI:
     ```powershell
     stripe events resend <evt_id>
     ```
     Sau đó kiểm tra DB để xác nhận tồn kho `products.stock` không bị trừ thêm lần nữa.
2. **Ca 2 (Chống can thiệp Giá & Danh tính)**:
   - Đổi tên hàm RPC thành **`create_shop_order`** (thay cho `create_order_rpc`).
   - Đổi tên cột tổng tiền thành **`total`** (thay cho `total_amount`).
   - Loại bỏ trường `district` khỏi body (schema chỉ gồm `recipient_name`, `recipient_phone`, `address_line`, `ward`, `province`, `note`).
   - Ghi rõ: Nếu gửi request khi chưa đăng nhập, API lập tức từ chối **401 `UNAUTHENTICATED`** (hệ thống không hỗ trợ đơn hàng khách vãng lai).
3. **Ca 4 (Hội thoại Multi-turn Agentic RAG)**:
   - Tên công cụ chuẩn hóa: **`product_reviews`** và **`create_support_ticket`** (thay cho `review_summary` và `create_ticket`).
   - Tên bảng database: **`reviews`** (thay cho `product_reviews`).
   - Xử lý đánh giá: Nếu sản phẩm chưa có review trong database, bot phản hồi rõ ràng **"Chưa có đánh giá"**, tuyệt đối không bịa đặt.
   - Xử lý tạo ticket: Bắt buộc đăng nhập; ticket chỉ gắn được với đơn hàng thuộc sở hữu của chính user; nếu gắn đơn hàng của người khác thì tool từ chối.
4. **Ca 5 (Kiểm thử Tự động A5.4 Chạy Thật)**:
   - Xóa bỏ toàn bộ email/mật khẩu mẫu.
   - Định dạng email tài khoản seed: `bench_customer_a+<namespace>@example.invalid`.
   - Kiểm tra sự tồn tại của biến trong `.env.bench` bằng lệnh PowerShell không in giá trị secret:
     ```powershell
     Select-String -Path ..\.env.bench -Pattern '^BENCH_CUSTOMER_EMAIL=' -Quiet
     Select-String -Path ..\.env.bench -Pattern '^BENCH_CUSTOMER_PASSWORD=' -Quiet
     ```
5. **Bổ sung 4 Ca Kiểm Thử từ `codex-HANDOFF-A.md` §5**:
   - **Ca 6 (Reviews API Contract)**:
     - Chưa mua hàng -> **403 `FORBIDDEN`** (`NOT_PURCHASED`).
     - Đơn COD có status `accepted` hoặc đơn đã thanh toán (`paid`) -> **201 `CREATED`**.
     - Đơn bị hủy (`cancelled`), chưa thanh toán (`unpaid`), đã hoàn tiền (`refunded`) -> không đủ điều kiện (403).
     - Kiểm tra chuỗi Unicode/tiếng Việt/emoji giữ nguyên 100% đúng codepoint.
   - **Ca 7 (Cách ly Chat, Audit Log & Session ID)**:
     - Cách ly phiên giữa các người dùng riêng biệt.
     - `session_id` vượt quá 100 ký tự -> backend trả về **422 Unprocessable Entity** ngay trước khi gọi bot.
     - Sau 3 lượt hỏi đáp qua lại -> bảng `chat_logs` có đúng 6 bản ghi với role `user` và `agent` (không phải `assistant`). Trường `tool_used` chỉ ghi nhận danh sách tool của chính lượt đó. Lỗi ghi log không gây retry trùng lặp.
   - **Ca 8 (API Sức Khỏe `/health`)**:
     - Mất kết nối Supabase/Chroma hoặc collection Chroma rỗng -> trả về `status: "degraded"`.
     - Tuyệt đối không làm lộ exception stack trace hay API keys ra bên ngoài.
   - **Ca 9 (Benchmark Seed Idempotency & Reset)**:
     - Chạy script seed lần 2 với cùng file JSONL: giữ nguyên dữ liệu và ID bản ghi (idempotent, không nhân đôi rows).
     - Chạy cờ `--reset`: chỉ xóa và thay thế dữ liệu thuộc mapped namespace của file credential hiện tại, tuyệt đối không đụng dữ liệu thật hay namespace khác.
     - Nếu đơn hàng bench có ticket ngoại lai tham chiếu: từ chối reset (`BENCH_REFERENCED`) để bảo toàn dữ liệu.

---

### 2.3 Đính chính `docs/reports/anti-G.md`
- Tại Mục 2, Ca 5: Đã điều chỉnh câu chữ từ *"Test đạt PASSED 100%"* thành **"Kỳ vọng test đạt PASSED (KHÔNG BỊ SKIP) khi có credentials thật từ `.env.bench` sau khi merge"**, phản ánh đúng bản chất đây là mục tiêu kiểm thử post-merge chứ chưa được thực thi trên môi trường thật.
- Cập nhật tên tool trong Ca 4 sang `product_reviews` và `create_support_ticket`.

---

## 3. 🔍 Trạng Thái Git & Sẵn Sàng Bàn Giao

Toàn bộ các thay đổi đều tuân thủ nguyên tắc **Defensive Coding**: chỉnh sửa tập trung vào tài liệu, bảo toàn 100% logic code đã qua kiểm thử của cả hai nhánh, không tạo xung đột mới.

- **Các file đã cập nhật**:
  - `docs/RUN.md` (khắc phục H1)
  - `docs/reports/anti-qa-plan.md` (khắc phục H2)
  - `docs/reports/anti-G.md` (đính chính Ca 5)
  - `docs/reports/anti-H.md` (báo cáo bàn giao mới)
