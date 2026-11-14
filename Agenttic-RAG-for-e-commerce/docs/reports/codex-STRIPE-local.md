# Stripe sandbox local — 03/11/2026

## 1. Đã làm

- Chrome MCP xác nhận tài khoản `test sandbox`, ID `acct_1UXhHrDbFvbSAWxs`, đang ở sandbox/test. Chưa có destination webhook đăng ký trên Dashboard.
- APP_URL hiện tại là http://localhost:3000; chọn Stripe CLI forwarding thay vì đăng ký localhost làm webhook HTTPS.
- Cài Stripe CLI 1.55.6 qua package chính thức @stripe/cli. Chủ tài khoản đã tự xác nhận OAuth và Authorize cho đúng sandbox; CLI báo authorized thành công.
- Bật listener chỉ cho account hiện tại và ba sự kiện Checkout: completed, async_payment_succeeded, expired. Forward tới http://127.0.0.1:3000/api/stripe/webhook.
- Thay STRIPE_SECRET_KEY local trước đó trả401 bằng test key có sẵn của chính sandbox. GET /v1/account trả200 và đúng account ID trước khi lưu. Không tạo hoặc rotate API key.
- Cập nhật STRIPE_WEBHOOK_SECRET theo listener vào web_ui/.env.local đã gitignore. Không đưa khóa vào báo cáo/Git/tool output. Khởi động Next.js local từ main.

## 2. File / runtime

- docs/RUN.md: lệnh listener có đủ expired và giới hạn account; phân biệt local với endpoint HTTPS khi deploy.
- docs/reports/codex-SUPABASE-execution.md: đánh dấu blocker Stripe local đã giải quyết.
- web_ui/.env.local: thay hai giá trị local, file ignored, không commit.
- Bằng chứng runtime riêng ngoài repo: D:/create/DATN/.test-tools/stripe/expiry-smoke-result.json; listener.json và next-server.json lưu PID/cấu hình. Private logs/signing secret cũng nằm ngoài repo và không được chia sẻ.

## 3. Kiểm tra thật

Tạo một đơn synthetic thuộc bench_customer_a qua POST /api/orders, dùng một sản phẩm có tồn kho và Stripe sandbox thật. Không dùng thẻ hoặc thu tiền:

```text
create_order_http 201
real_test_checkout_created pending unpaid
stripe_expire_http 200
EXPIRY_END_TO_END_PASS; stock unchanged; synthetic cancelled order retained
```

Stripe tạo event `checkout.session.expired` thật; CLI nhận và chuyển về route. Log delivery:

```text
[200] POST http://127.0.0.1:3000/api/stripe/webhook [evt_1UXjZPDbFvbSAWxsEyqhpwwx]
```

Session test được xác nhận livemode=false; DB chuyển pending/unpaid -> cancelled/failed, stock_decremented_at vẫn NULL và stock sản phẩm không đổi. Đơn synthetic ID c443cd06-0a2a-452e-9707-2bca4b13213a được giữ lại để đối soát, không xóa dữ liệu.

Hai lần replay cùng payload event thực tế, ký bằng listener secret local (kiểm bổ sung, không phải delivery tự phát từ Stripe):

```text
signed_replay 1 HTTP 200
signed_replay 2 HTTP 200
invalid_signature_control HTTP 400 INVALID_SIGNATURE
```

Không có thay đổi source code; không cần chạy lại toàn bộ build/unit suite cho cấu hình local và tài liệu.

## 4. Giới hạn / bàn giao

- Listener và Next.js đang chạy nền tại thời điểm bàn giao. Phải chạy lại khi máy/process dừng; lệnh nằm trong RUN.md. PID hiện tại: Stripe19788, Next21600 (chỉ là thông tin tại thời điểm chạy).
- Chưa tạo webhook cloud trên Dashboard vì chưa có URL HTTPS triển khai. Nếu deploy sau, dùng endpoint/signing secret của môi trường triển khai đó.
- Kiểm lần này chứng minh đường tạo Checkout -> expire -> delivery có chữ ký -> cập nhật DB, kèm replay và chữ ký sai. Không thực hiện thanh toán thành công hay kiểm async_payment_succeeded end-to-end.
- Ba sự kiện đã nằm trong subscription local; không tuyên bố toàn bộ QA Đợt3 đã hoàn tất.
