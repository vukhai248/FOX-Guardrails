# Báo cáo Khắc phục & Nghiệm thu Lần 3 (F9, F10)

**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `feat/a-frontend`  
**Ngày thực hiện**: 03/11/2026  
**Tham chiếu chỉ đạo**: Biên bản nghiệm thu Lần 3 của Claude Opus (Lead Architect)

---

## 1. Tóm tắt kết quả 2 hạng mục F9 & F10

| Mã mục | Vấn đề được chỉ ra | Trạng thái | Commit neo | Minh chứng kiểm chứng |
| :---: | :--- | :---: | :---: | :--- |
| **F10** | `.env.bench` (chứa password bench) chưa được gitignore | **ĐÃ XONG** | `1685009` | Thêm `.env.bench` và `*.env.bench` vào `.gitignore`. Kiểm tra `git check-ignore -v --no-index`: khớp dòng 48 ở cả root và `web_ui`. |
| **F9** | Playwright runner không nạp `.env.local` Supabase + assertion A5.4 đang skip lỗi login thật | **ĐÃ XONG** | `ef61dbf` | Dùng `@next/env` nạp biến trong `playwright.config.ts`. A5.4 chỉ skip khi thiếu biến `BENCH_*`, đăng nhập thất bại chuyển thành `expect(loginError).toBeNull()`. |

---

## 2. Chi tiết phân tích & Giải pháp kỹ thuật

### F10 — Bảo vệ Bảo mật File `.env.bench` qua `.gitignore`
- **Vấn đề**: File `.env.bench` dùng để cung cấp tài khoản kiểm thử khách hàng benchmark (`BENCH_CUSTOMER_EMAIL`, `BENCH_CUSTOMER_PASSWORD`) do backend Codex khởi tạo, nhưng file này chưa nằm trong `.gitignore`.
- **Giải pháp**:
  - Bổ sung vào `.gitignore` gốc:
    ```gitignore
    # Environment files
    .env
    .env.local
    .env.development.local
    .env.test.local
    .env.production.local
    .env.bench
    *.env.bench
    web/.env.local
    rag-service/.env
    ```
- **Kiểm chứng thực tế bằng lệnh theo yêu cầu**:
  - Lệnh: `git check-ignore -v --no-index .env.bench web_ui/.env.bench`
  - Output:
    ```
    .gitignore:48:*.env.bench	.env.bench
    .gitignore:48:*.env.bench	web_ui/.env.bench
    ```

### F9 — Nạp Biến Môi Trường cho Playwright Runner & Chuẩn Hóa Assertion Test A5.4
- **Phân tích Nguyên nhân**:
  - `playwright.config.ts` chạy trong tiến trình Node độc lập, không tự động nạp các file `.env.local` của Next.js (chỉ server Next.js mới nạp). Do đó `process.env.NEXT_PUBLIC_SUPABASE_URL` và `process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY` luôn là `undefined` trong runner. Kể cả khi có file `.env.bench`, test vẫn dừng ở đoạn kiểm tra biến Supabase và bị skip sai lệch.
  - Ngoài ra, đoạn code cũ gọi `test.skip(true, ...)` khi `loginError`. Theo chỉ dẫn của Claude Opus, khi đã có biến cấu hình thì việc đăng nhập thất bại là lỗi thật (fail test), không được ém nhẹm bằng skip.
- **Giải pháp**:
  1. Trong `web_ui/playwright.config.ts`:
     - Sử dụng hàm `loadEnvConfig(process.cwd())` từ package `@next/env` (đi kèm sẵn trong Next.js) để nạp toàn bộ `.env.local`, `.env`.
     - Đồng thời nạp các biến từ `.env.bench` nếu file tồn tại.
  2. Trong `web_ui/tests/e2e/a5_ui.spec.ts`:
     - Bỏ hàm parse thủ công, đọc trực tiếp `process.env.BENCH_CUSTOMER_EMAIL` và `process.env.BENCH_CUSTOMER_PASSWORD`.
     - **Chỉ skip khi thiếu biến**:
       ```typescript
       if (!email || !password) {
         test.skip(true, 'Bỏ qua test vì chưa cấu hình BENCH_CUSTOMER_EMAIL / BENCH_CUSTOMER_PASSWORD trong .env.bench (thuộc tài khoản backend của Codex)');
         return;
       }
       ```
     - Khi đã có biến: Đổi lỗi đăng nhập sang assertion nghiêm ngặt:
       ```typescript
       expect(loginError, `Đăng nhập bench_customer thất bại: ${loginError?.message}`).toBeNull();
       expect(authData?.session, 'Phiên đăng nhập không tồn tại sau khi signInWithPassword').toBeTruthy();
       ```
- **Kiểm chứng xác nhận**:
  - Xác nhận nạp env qua script Node:
    ```
    SUPABASE_URL: true ANON_KEY: true
    ```
  - Chạy test A5.4 khi chưa có tài khoản: Test skip chính xác với lý do:
    `Bỏ qua test vì chưa cấu hình BENCH_CUSTOMER_EMAIL / BENCH_CUSTOMER_PASSWORD trong .env.bench (thuộc tài khoản backend của Codex)`, xác nhận **không còn bị vướng** ở nhánh thiếu biến Supabase.

---

## 3. Bằng chứng Thực thi Kiểm thử Nghiệm thu

### 3.1. ESLint trên các file đã sửa đổi
- **Lệnh**: `npx.cmd eslint playwright.config.ts tests/e2e/a5_ui.spec.ts`
- **Output**:
  ```
  Command exited with code 0. No output from the command.
  ```
  -> **0 errors, 0 warnings**.

### 3.2. Chạy Playwright Toàn Suite
- **Lệnh**: `npx.cmd playwright test`
- **Output thật**:
  ```
  Running 27 tests using 6 workers

  ok  1 [chromium] › tests\e2e\a1_ui.spec.ts:52:7 › Gói A1-UI: Sửa lỗi nền Chatbot (H1 Session ID UUID & H10 Chặn Mock Fake Reply) › A1.2: Phân tách session_id theo từng user độc lập (H1) (6.9s)
  ok  4 [chromium] › tests\e2e\a1_ui.spec.ts:7:7 › Gói A1-UI: Sửa lỗi nền Chatbot (H1 Session ID UUID & H10 Chặn Mock Fake Reply) › A1.1: Chat widget sinh session_id chuẩn UUID v4, lưu vào localStorage và gửi kèm POST /api/chat (6.9s)
  ok  5 [chromium] › tests\e2e\a1_ui.spec.ts:77:7 › Gói A1-UI: Sửa lỗi nền Chatbot (H1 Session ID UUID & H10 Chặn Mock Fake Reply) › A1.3: Khi backend gặp sự cố (503 BACKEND_UNAVAILABLE), Chat widget hiển thị thông báo lỗi rõ ràng, KHÔNG trả lời giả (H10) (7.0s)
  ok  2 [chromium] › tests\e2e\a3_ui.spec.ts:248:7 › Gói A3-UI: Customer Data Surface & Order Workflow › A3.3: Trang /account - Sửa ghi chú đơn hàng pending gọi PATCH /api/orders/{id}/note (8.4s)
  ok  8 [chromium] › tests\e2e\a5_ui.spec.ts:108:7 › Gói A5-UI: Dữ liệu thật Admin & Nhật ký hội thoại Chat Logs (H9, F2, F3) › A5.2: API Route GET /api/admin/chat-logs từ chối 401 UNAUTHENTICATED nếu thiếu hoặc sai token (F3) (1.0s)
  -  11 [chromium] › tests\e2e\a5_ui.spec.ts:224:7 › Gói A5-UI: Dữ liệu thật Admin & Nhật ký hội thoại Chat Logs (H9, F2, F3) › A5.4: Chặn đứng tấn công leo quyền (F2 Privilege Escalation) khi user tự sửa user_metadata.role="admin"
  ok  6 [chromium] › tests\e2e\a3_ui.spec.ts:140:7 › Gói A3-UI: Customer Data Surface & Order Workflow › A3.2: Form Review sản phẩm - Xử lý 403 NOT_PURCHASED và thành công 201 (9.6s)
  ok  3 [chromium] › tests\e2e\a3_ui.spec.ts:5:7 › Gói A3-UI: Customer Data Surface & Order Workflow › A3.1: Form Checkout tách trường, gọi POST /api/orders và redirect checkout-success không lộ PII (10.3s)
  ok  7 [chromium] › tests\e2e\a5_ui.spec.ts:71:7 › Gói A5-UI: Dữ liệu thật Admin & Nhật ký hội thoại Chat Logs (H9, F2, F3) › A5.1: Khi cờ mock tắt (mặc định), Admin không dùng số liệu giả MOCK_ORDERS / MOCK_TICKETS (3.9s)
  ok 10 [chromium] › tests\e2e\a6_safe_render.spec.ts:5:7 › Gói A6: Render an toàn trong Chat Widget (H11 - Allowlist, Homoglyph Punycode, Chặn Raw HTML, Guard Badge) › A6.1: Render link nội bộ hợp lệ, chặn link ngoài không thuộc allowlist (3.3s)
  ok  9 [chromium] › tests\e2e\a5_ui.spec.ts:124:7 › Gói A5-UI: Dữ liệu thật Admin & Nhật ký hội thoại Chat Logs (H9, F2, F3) › A5.3: Tab "Hội thoại" trong Admin hiển thị danh sách chat logs, lọc rủi ro và xem chi tiết phiên (H9) (5.4s)
  ok 12 [chromium] › tests\e2e\a6_safe_render.spec.ts:47:7 › Gói A6: Render an toàn trong Chat Widget (H11 - Allowlist, Homoglyph Punycode, Chặn Raw HTML, Guard Badge) › A6.2: Ẩn ảnh ngoài không thuộc allowlist, hiển thị ảnh trong allowlist (4.3s)
  ok 13 [chromium] › tests\e2e\a6_safe_render.spec.ts:84:7 › Gói A6: Render an toàn trong Chat Widget (H11 - Allowlist, Homoglyph Punycode, Chặn Raw HTML, Guard Badge) › A6.3: Phát hiện và chặn tấn công tên miền giả mạo Homoglyph (Punycode Attack) (3.9s)
  ok 15 [chromium] › tests\e2e\a6_safe_render.spec.ts:159:7 › Gói A6: Render an toàn trong Chat Widget (H11 - Allowlist, Homoglyph Punycode, Chặn Raw HTML, Guard Badge) › A6.5: Hiển thị nhãn Guard Action khi response có guard.action ≠ allow (H11) (3.4s)
  ok 14 [chromium] › tests\e2e\a6_safe_render.spec.ts:120:7 › Gói A6: Render an toàn trong Chat Widget (H11 - Allowlist, Homoglyph Punycode, Chặn Raw HTML, Guard Badge) › A6.4: Chặn parse HTML thô (Raw HTML Mitigation / XSS Prevention) (4.2s)
  ok 18 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA & UI Deep Check Suite › CUA Check: products_list (/products) (2.5s)
  ok 17 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA & UI Deep Check Suite › CUA Check: homepage (/) (2.7s)
  ok 19 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA & UI Deep Check Suite › CUA Check: product_detail (/products/136045) (2.1s)
  ok 16 [chromium] › tests\e2e\a6_safe_render.spec.ts:218:7 › Gói A6: Render an toàn trong Chat Widget (H11 - Allowlist, Homoglyph Punycode, Chặn Raw HTML, Guard Badge) › A6.6: Chặn triệt để các vector Bypass Allowlist (F1 - Protocol-relative, Backslash, Schemes nguy hiểm) (4.3s)
  ok 20 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA & UI Deep Check Suite › CUA Check: cart (/cart) (2.1s)
  ok 21 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA & UI Deep Check Suite › CUA Check: checkout (/checkout) (2.1s)
  ok 27 [chromium] › tests\e2e\smoke.spec.ts:39:7 › E2E Smoke Test Suite › 3. Backend FastAPI RAG Service hoạt động và kết nối đủ DB/Chroma (431ms)
  ok 22 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA & UI Deep Check Suite › CUA Check: account (/account) (2.8s)
  ok 24 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA & UI Deep Check Suite › CUA Check: login (/auth/login) (2.8s)
  ok 23 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA & UI Deep Check Suite › CUA Check: admin (/admin) (2.9s)
  ok 25 [chromium] › tests\e2e\smoke.spec.ts:5:7 › E2E Smoke Test Suite › 1. Trang chủ tải thành công và hiển thị các khối nội dung (2.5s)
  ok 26 [chromium] › tests\e2e\smoke.spec.ts:18:7 › E2E Smoke Test Suite › 2. Chat widget mở được và hiển thị giao diện trò chuyện (2.3s)

  1 skipped
  26 passed (20.8s)
  ```

---

## 4. Kết luận

- Toàn bộ 2 điểm F9 và F10 đã được giải quyết hoàn tất, neo commit rõ ràng.
- Antigravity đã đóng gói toàn bộ các phần việc thuộc phạm vi của mình, sẵn sàng để Claude Opus nghiệm thu chốt.
