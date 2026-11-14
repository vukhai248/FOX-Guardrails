# Báo cáo Hoàn thành Gói G1 & G2 — Tài liệu Vận hành & Kế hoạch QA Toàn Web

**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `feat/a-frontend`  
**Ngày thực hiện**: 03/11/2026  
**Tham chiếu chỉ đạo**: Phân công nhiệm vụ G1 & G2 từ Claude Opus (Lead Architect)

---

## 1. Tóm tắt kết quả thực hiện

Antigravity đã hoàn thành trọn vẹn cả 2 nhiệm vụ G1 và G2 theo đúng nguyên tắc **Defensive Coding** và quy chuẩn bảo mật:

| Mã mục | Nhiệm vụ | Trạng thái | Commit neo | Minh chứng & Sản phẩm bàn giao |
| :---: | :--- | :---: | :---: | :--- |
| **G1** | Cập nhật tài liệu vận hành máy sạch `docs/RUN.md` | **ĐÃ XONG** | `de3bcf6` | Bổ sung đầy đủ biến môi trường Web & RAG backend (chỉ ghi tên biến, không ghi secret), hướng dẫn Stripe CLI webhook, và quy trình migration an toàn (chỉ chạy sau merge frontend, cấm chạy `setup.sql`). |
| **G2** | Xây dựng Kế hoạch QA Toàn diện Hệ thống `docs/reports/anti-qa-plan.md` | **ĐÃ XONG** | `c9d2c74` | Soạn thảo 5 ca kiểm thử trọng yếu (COD/Stripe test card, chống can thiệp giá/user_id, cách ly đơn hàng 404, chat tool review/ticket, test A5.4 chạy thật không skip). |

---

## 2. Chi tiết các nội dung đã hoàn thành

### G1 — Cập nhật `docs/RUN.md`
1. **Biến môi trường Web (`web_ui/.env.local`)**:
   - Thêm các biến: `APP_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.
   - `STRIPE_SECRET_KEY`: Khóa bí mật Stripe Test Mode (chỉ sử dụng khóa bắt đầu bằng `sk_test_`).
   - `STRIPE_WEBHOOK_SECRET`: Signing secret của Stripe Webhook (`whsec_...`).
   - Bổ sung hướng dẫn chuyển tiếp Stripe Webhook cục bộ bằng Stripe CLI:
     ```powershell
     stripe listen --forward-to localhost:3000/api/stripe/webhook
     ```
2. **Biến môi trường RAG Service (`rag-service/.env`)**:
   - Thêm các biến cờ điều khiển: `LEGACY_LLM_GUARDRAIL` (`on`), `LEGACY_PROMPT_DEFENSE` (`on`), `FOX_GUARD_MODE` (`off`), `FOX_GUARD_ARM`, `BENCH_RECORD`, `BENCH_TEMPERATURE`.
3. **Quy trình An toàn Cơ sở Dữ liệu & Migration**:
   - Ghi chú rõ file migration: `database/migrations/2026-11_payment_and_address.sql` do chủ đồ án chạy trên Supabase SQL Editor.
   - **Bắt buộc chỉ chạy sau khi đã merge nhánh frontend** (vì sau migration, quyền `INSERT` trực tiếp của client vào bảng `orders` bị thu hồi, toàn bộ luồng tạo đơn chuyển qua RPC server).
   - Sao lưu dữ liệu bảng `orders` trước khi bấm chạy script.
   - **Tuyệt đối không bao giờ chạy lại `database/setup.sql`** (chứa lệnh `DROP TABLE ... CASCADE` xoá vĩnh viễn dữ liệu).

### G2 — Kế hoạch QA Toàn Web (`docs/reports/anti-qa-plan.md`)
1. **Ca 1 (COD & Stripe Test Card `4242...`)**:
   - Đặt hàng COD: Trạng thái `pending`, `cod_pending`, tồn kho giảm đúng 1 đơn vị.
   - Thanh toán Stripe test card `4242...`: Chuyển `paid`, trừ kho đúng 1 lần.
   - Kiểm tra Idempotency: Gửi lại webhook lần 2 trả về `200` và **không trừ thêm kho**.
2. **Ca 2 (Chống can thiệp Giá & Danh tính - Tampering Protection)**:
   - Gửi payload `POST /api/orders` cố tình sửa `price` thấp hoặc gán `user_id` giả mạo.
   - Server RPC tự động bỏ qua giá từ client, tự query giá niêm yết từ DB; tự lấy `user_id` từ JWT token.
3. **Ca 3 (Cách ly Đơn hàng Chéo Tài khoản - PII Protection)**:
   - Khách B gọi `GET /api/orders/{id}` của Khách A: Server từ chối **404 NOT_FOUND** (chuẩn OWASP API Security: không trả về 403 để tránh lộ sự tồn tại của đơn hàng).
4. **Ca 4 (Hội thoại Multi-turn Agentic RAG Thực tế)**:
   - *"Mọi người đánh giá iPhone 16 thế nào?"*: Gọi tool `product_reviews` truy vấn đánh giá thật từ bảng `reviews`.
   - *"Tạo ticket báo đơn giao chậm"*: Gọi tool `create_support_ticket` tạo ticket trong `support_tickets`.
5. **Ca 5 (Kiểm thử Tự động A5.4 Chạy Thật Không Skip - Kỳ vọng)**:
   - Sẽ chạy test A5.4 với tài khoản `bench_customer_a` được seed từ gói A7 của Codex sau khi merge.
   - Kỳ vọng xác minh toàn bộ 4 route GET Admin và 1 route PUT Admin đều từ chối **403 `FORBIDDEN`** qua `requireRole` tra cứu bảng `public.user_roles`. Kỳ vọng test đạt **PASSED (KHÔNG BỊ SKIP)** khi có credentials thật từ `.env.bench`.
6. **Quy tắc thực thi cốt lõi**:
   - **Bắt buộc tự khởi động dev server sạch từ đúng thư mục đã merge** (không dùng lại process dev server cũ trên port 3000/8080 của agent khác).

---

## 3. Trạng thái Sẵn sàng Bàn giao

- **Lịch sử Commit trên nhánh `feat/a-frontend`**:
  - `de3bcf6`: `docs(run): update RUN.md with stripe webhook, rag flags and migration note (G1)`
  - `c9d2c74`: `docs(qa): add comprehensive qa plan for post-merge verification (G2)`
- **Quy tắc dừng**: Antigravity **dừng lại tại đây** và không tự ý chạy test QA. Mọi kịch bản kiểm thử toàn hệ thống sẽ được kích hoạt ngay sau khi Claude Opus hoàn tất merge hai nhánh và chủ đồ án chạy migration thành công.
