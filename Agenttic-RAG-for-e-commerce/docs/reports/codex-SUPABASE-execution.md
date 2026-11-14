# Thực thi Supabase thật — 03/11/2026

## 1. Đã làm

- Đọc migration 0 và nghiệm thu lần 10 tại main 4067561. Phần bổ sung của Claude giải quyết đúng ba bảng thiếu, tương thích bot tạo ticket low/open bằng JWT khách.
- Tính lại SHA-256 của cả bốn backup, khớp manifest. Backup chính: D:/backups/supabase/20261103-213431-pre-migration/database.dump.
- Chạy lại migration_chain_test.py với Python `-X utf8`: SUMMARY 27/27 passed. Lần đầu console Windows không in được tiếng Việt; chạy lại ở UTF-8 thành công, không sửa migration.
- Áp dụng nguyên văn sáu file đã duyệt lên PostgreSQL Supabase qua Session pooler, dùng psql ON_ERROR_STOP=1; từng file tự BEGIN/COMMIT. Không dùng SQL Editor UI; không thay đổi nội dung SQL. Cả sáu exit0 và có COMMIT.
- Chạy seed đúng lệnh được giao: thành công, không gặp email_address_invalid và không đổi miền email.

## 2. File và bằng chứng

Thứ tự thực thi remote:

1. 2026-11_base_tables.sql
2. 2026-11_payment_and_address.sql
3. 2026-11_chat_logs_guard.sql
4. 2026-11_product_reviews.sql
5. 2026-11_seed_bench.sql
6. 2026-11_expired_checkout.sql

Log từng file + hash SQL + thời điểm commit: D:/backups/supabase/20261103-213431-pre-migration/remote-migration-4067561/results.json và các file .sql.log cùng thư mục. Không chứa mật khẩu.

Thông tin đăng nhập benchmark được script lưu trong .env.bench đã gitignore. Không chép credential vào báo cáo/Git. Không chạm database/setup.sql, dữ liệu ChromaDB hoặc push.

## 3. Kiểm tra sau chạy — output thật

```text
REMOTE_MIGRATIONS_COMPLETE_6_OF_6
```

Supabase có 9 bảng public: bench_cases, chat_logs, orders, policies, policy_chunks, products, reviews, support_tickets, user_roles. Trước seed, dữ liệu cũ giữ nguyên: orders18/products1345/reviews10. Các RPC create_shop_order/create_product_review/seed_bench_cases và cả hai overload fail_stripe_order tồn tại.

Lệnh seed tại repo web:

```powershell
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 scripts/seed_bench.py --cases scripts/fixtures/seed_bench.sample.jsonl --products-from-db
```

```json
{"seeded_cases": 2, "reset": false, "accounts": 3}
```

Đọc lại qua Supabase SDK: namespace có2 mapping; cả3 tài khoản login thành công, DB role lần lượt customer/customer/admin.

```powershell
npx.cmd playwright test tests/e2e/a5_ui.spec.ts --grep 'A5.4:' --workers=1 --reporter=line
```

```text
1 passed (11.9s)
```

A5.4 dùng tài khoản benchmark thật, kiểm API từ chối khách tự gán user_metadata.role=admin; lần này không skip. Đây là kiểm focused sau migration/seed, không phải nghiệm thu toàn bộ QA Đợt3.

## 4. Còn mở

> Cập nhật sau: blocker Stripe **local** bên dưới đã được giải quyết sau khi chủ tài khoản đăng nhập/cấp quyền. Listener nhận đủ ba event và expired end-to-end đạt; xem codex-STRIPE-local.md. Endpoint HTTPS trên Dashboard vẫn chưa tạo vì website đang chạy localhost. Các gạch đầu dòng tiếp theo ghi nhận trạng thái ban đầu của lượt migration/seed.

- Stripe: khóa STRIPE_SECRET_KEY local có tiền tố test nhưng GET /v1/webhook_endpoints trả401. Không in khóa hoặc body lỗi, không dùng live key.
- Chrome MCP mở được https://dashboard.stripe.com/test/webhooks nhưng chuyển tới đăng nhập. Cần chủ tài khoản đăng nhập đúng Stripe test; chưa thay đổi bất kỳ webhook nào.
- Chưa thêm checkout.session.expired, chưa xác minh signing secret hoặc delivery webhook thật. Nếu key local không hợp lệ cần cập nhật bằng key test đúng trước khi thử thanh toán thật.
- Anti có thể bắt đầu QA web dựa trên migration/seed đã xong; QA thanh toán cần giải quyết Stripe trước.
