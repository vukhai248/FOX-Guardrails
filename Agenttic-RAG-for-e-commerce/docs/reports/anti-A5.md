# Báo cáo Kiểm thử & Nghiệm thu: Gói A5-UI — Dữ liệu Thật Admin, Route Chat Logs & Tab Hội Thoại (H9)

**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `feat/a-frontend`  
**Ngày thực hiện**: 03/11/2026  
**Mục tiêu**: Khắc phục triệt để lỗ hổng H9 (Trang admin tự động rơi về `MOCK_ORDERS`, `MOCK_TICKETS`, `FALLBACK_PRODUCTS` khiến việc điều tra, giám sát hệ thống và đo lường hiển thị số liệu giả; thiếu route và giao diện xem nhật ký `chat_logs` theo phiên).

---

## 1. Các công việc đã thực hiện

1. **Kiểm Soát Mock Qua Biến Môi Trường**:
   - Thêm cờ cấu hình `process.env.NEXT_PUBLIC_ALLOW_MOCK_ADMIN === 'true'`.
   - Mặc định tắt cờ mock (`false`): Khi API `orders`, `tickets` hoặc `products` trả về rỗng hoặc gặp lỗi kết nối, trang Admin hiển thị danh sách rỗng chân thực từ DB (`Không tìm thấy đơn hàng nào.`, `Chưa có ticket nào`), tuyệt đối không tự động đổ dữ liệu giả MOCK_ORDERS ("Nguyễn Văn A - SĐT: 0987654321"). Chỉ khi bật rõ ràng `NEXT_PUBLIC_ALLOW_MOCK_ADMIN=true` mới dùng mock.

2. **Xây Dựng API Route Quản Trị `GET /api/admin/chat-logs`**:
   - Đường dẫn: `web_ui/src/app/api/admin/chat-logs/route.ts`.
   - Cơ chế bảo mật: Xác thực Bearer Token qua Supabase Auth, kiểm tra đặc quyền vai trò `admin` hoặc `staff` (trả về 403 Forbidden nếu không có quyền).
   - Truy vấn server-side bằng Supabase Service Role Client (không bị giới hạn bởi client RLS).
   - Hỗ trợ các bộ lọc động: `sessionId`, `riskLevel` (`high`, `medium`, `low`), `role` (`user`, `agent`, `tool`), cùng phân trang `limit` và `offset`.

3. **Bổ Sung Tab "Hội Thoại" (Chat Logs) Trên Trang Quản Trị Admin**:
   - Thêm nút chuyển Panel "Hội thoại" trên cả Sidebar Desktop (`[data-testid="admin-nav-chat-logs"]`) và Mobile Navigation Bar, kèm badge hiển thị số lượng bản ghi log.
   - Giao diện 2 cột chuyên nghiệp:
     - **Cột trái (Bảng nhật ký)**: Liệt kê các bản ghi trò chuyện với Session ID rút gọn, Vai trò (User, Agent, Tool), Nội dung câu hỏi/trả lời, Tool sử dụng, Huy hiệu mức độ rủi ro (`risk_level`), Huy hiệu quyết định can thiệp của Guardrail (`guard_decision_ids`), và thời gian chi tiết.
     - **Thanh công cụ**: Input tìm kiếm thời gian thực (theo Session ID, nội dung, User ID) và Dropdown lọc rủi ro (Tất cả, High, Medium, Low), cùng nút "Làm mới dữ liệu".
     - **Cột phải (Luồng hội thoại phiên)**: Khi click vào bất kỳ dòng log nào, hiển thị toàn bộ tiến trình trao đổi của `session_id` đó theo trình tự thời gian, trực quan hóa câu hỏi của khách hàng, phản hồi của AI và các can thiệp an ninh của FOX-Guardrails.

---

## 2. Danh sách file thay đổi

| STT | Đường dẫn file | Mô tả thay đổi |
| :---: | :--- | :--- |
| 1 | `web_ui/src/app/api/admin/chat-logs/route.ts` | Route API server-side truy vấn bảng `chat_logs`, kiểm tra quyền admin/staff. |
| 2 | `web_ui/src/app/admin/page.tsx` | Cập nhật `ActivePanel = ... \| 'chat_logs'`, state `chatLogs`, logic cờ `NEXT_PUBLIC_ALLOW_MOCK_ADMIN`, hàm `fetchChatLogs`, nút tab Hội thoại và Panel hiển thị nhật ký hội thoại 2 cột. |
| 3 | `web_ui/tests/e2e/a5_ui.spec.ts` | Bộ test Playwright E2E cho Gói A5 gồm 3 test case: chặn mock orders, bảo vệ route chat-logs 403, và kiểm tra hiển thị/lọc/xem chi tiết phiên trong tab Hội thoại. |
| 4 | `web_ui/tests/e2e/screenshots/a5/*` | 3 ảnh chụp màn hình CUA kiểm chứng thực tế: không có dữ liệu giả, bảng chat logs và chi tiết phiên. |
| 5 | `docs/reports/anti-A5.md` | Tài liệu báo cáo nghiệm thu Gói A5. |

---

## 3. Lệnh test & Output thực tế

### 3.1. Biên dịch Next.js Production Build (`npm run build`)
```powershell
> npm.cmd run build

▲ Next.js 16.2.10 (Turbopack)
- Environments: .env.local

  Creating an optimized production build ...
✓ Compiled successfully in 4.2s
  Running TypeScript ...
  Finished TypeScript in 7.4s ...
  Collecting page data using 11 workers ...
  Generating static pages using 11 workers (26/26) in 501ms
  Finalizing page optimization ...

Route (app)                              Size     First Load JS
┌ ○ /                                    16.8 kB         155 kB
├ ○ /_not-found                          1.04 kB         103 kB
├ ○ /account                             10.3 kB         148 kB
├ ○ /admin                               41.2 kB         180 kB
├ ƒ /api/admin/chat-logs                 0 B                0 B
├ ƒ /api/admin/orders                    0 B                0 B
├ ƒ /api/admin/tickets                   0 B                0 B
├ ƒ /api/admin/users                     0 B                0 B
├ ƒ /api/chat                            0 B                0 B
├ ƒ /api/chat/admin                      0 B                0 B
├ ƒ /api/stripe                          0 B                0 B
...
✓ Build thành công 100%, bổ sung route /api/admin/chat-logs, 0 lỗi TypeScript.
```

### 3.2. Chạy bộ kiểm thử Playwright cho Gói A5 (`tests/e2e/a5_ui.spec.ts`)
```powershell
> npx playwright test tests/e2e/a5_ui.spec.ts

Running 3 tests using 3 workers

  ok 1 [chromium] › tests\e2e\a5_ui.spec.ts:107:7 › A5.2: API Route GET /api/admin/chat-logs từ chối truy cập 403 nếu không có token admin (534ms)
  ok 2 [chromium] › tests\e2e\a5_ui.spec.ts:70:7 › A5.1: Khi cờ mock tắt (mặc định), Admin không dùng số liệu giả MOCK_ORDERS / MOCK_TICKETS (2.1s)
  ok 3 [chromium] › tests\e2e\a5_ui.spec.ts:123:7 › A5.3: Tab "Hội thoại" trong Admin hiển thị danh sách chat logs, lọc rủi ro và xem chi tiết phiên (H9) (3.5s)

  3 passed (5.2s)
```

### 3.3. Chạy toàn bộ Test Suite Playwright (Toàn bộ 25 kịch bản E2E)
```powershell
> npx playwright test

Running 25 tests using 6 workers

  ok  1 [chromium] › tests\e2e\a1_ui.spec.ts:52:7 › A1.2: Phân tách session_id theo từng user độc lập (H1) (5.2s)
  ok  2 [chromium] › tests\e2e\a1_ui.spec.ts:7:7 › A1.1: Chat widget sinh session_id chuẩn UUID v4, lưu vào localStorage và gửi kèm POST /api/chat (5.5s)
  ok  3 [chromium] › tests\e2e\a1_ui.spec.ts:77:7 › A1.3: Khi backend gặp sự cố (503 BACKEND_UNAVAILABLE), Chat widget hiển thị thông báo lỗi rõ ràng, KHÔNG trả lời giả (H10) (5.5s)
  ok  4 [chromium] › tests\e2e\a5_ui.spec.ts:107:7 › A5.2: API Route GET /api/admin/chat-logs từ chối truy cập 403 nếu không có token admin (1.4s)
  ok  5 [chromium] › tests\e2e\a3_ui.spec.ts:236:7 › A3.3: Trang /account - Sửa ghi chú đơn hàng pending gọi PATCH /api/orders/{id}/note (8.1s)
  ok  6 [chromium] › tests\e2e\a3_ui.spec.ts:128:7 › A3.2: Form Review sản phẩm - Xử lý 403 NOT_PURCHASED và thành công 201 (9.2s)
  ok  7 [chromium] › tests\e2e\a6_safe_render.spec.ts:5:7 › A6.1: Render link nội bộ hợp lệ, chặn link ngoài không thuộc allowlist (2.5s)
  ok  8 [chromium] › tests\e2e\a5_ui.spec.ts:70:7 › A5.1: Khi cờ mock tắt (mặc định), Admin không dùng số liệu giả MOCK_ORDERS / MOCK_TICKETS (4.8s)
  ok  9 [chromium] › tests\e2e\a3_ui.spec.ts:5:7 › A3.1: Form Checkout tách trường, gọi POST /api/orders và redirect checkout-success không lộ PII (10.2s)
  ok 10 [chromium] › tests\e2e\a5_ui.spec.ts:123:7 › A5.3: Tab "Hội thoại" trong Admin hiển thị danh sách chat logs, lọc rủi ro và xem chi tiết phiên (H9) (6.1s)
  ok 11 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: homepage (/) (2.0s)
  ok 12 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: products_list (/products) (1.9s)
  ok 13 [chromium] › tests\e2e\a6_safe_render.spec.ts:47:7 › A6.2: Ẩn ảnh ngoài không thuộc allowlist, hiển thị ảnh trong allowlist (5.6s)
  ok 14 [chromium] › tests\e2e\a6_safe_render.spec.ts:84:7 › A6.3: Phát hiện và chặn tấn công tên miền giả mạo Homoglyph (Punycode Attack) (4.6s)
  ok 15 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: product_detail (/products/136045) (1.7s)
  ok 16 [chromium] › tests\e2e\a6_safe_render.spec.ts:159:7 › A6.5: Hiển thị nhãn Guard Action khi response có guard.action ≠ allow (H11) (4.4s)
  ok 17 [chromium] › tests\e2e\a6_safe_render.spec.ts:120:7 › A6.4: Chặn parse HTML thô (Raw HTML Mitigation / XSS Prevention) (5.5s)
  ok 18 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: cart (/cart) (2.9s)
  ok 19 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: admin (/admin) (2.6s)
  ok 20 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: checkout (/checkout) (2.7s)
  ok 21 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: account (/account) (2.7s)
  ok 22 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: login (/auth/login) (2.4s)
  ok 23 [chromium] › tests\e2e\smoke.spec.ts:39:7 › 3. Backend FastAPI RAG Service hoạt động và kết nối đủ DB/Chroma (270ms)
  ok 24 [chromium] › tests\e2e\smoke.spec.ts:5:7 › 1. Trang chủ tải thành công và hiển thị các khối nội dung (2.2s)
  ok 25 [chromium] › tests\e2e\smoke.spec.ts:18:7 › 2. Chat widget mở được và hiển thị giao diện trò chuyện (1.6s)

  25 passed (19.8s)
```

---

## 4. Ảnh chụp kiểm chứng CUA (Screenshots)

Các ảnh chụp màn hình kiểm chứng đã được lưu trong thư mục `web_ui/tests/e2e/screenshots/a5/`:
1. `a5_real_empty_orders.png`: Xác minh bảng Đơn hàng không nạp dữ liệu giả `MOCK_ORDERS`, hiển thị "Không tìm thấy đơn hàng nào." chân thực khi DB rỗng.
2. `a5_chat_logs_table.png`: Bảng danh sách nhật ký hội thoại hiển thị Session ID, Role badge, Tool used, Guard Decision IDs, Risk Level và thời gian.
3. `a5_chat_logs_session_detail.png`: Cột chi tiết phiên hội thoại hiển thị đầy đủ tiến trình trao đổi giữa User và AI theo trình tự thời gian cùng các can thiệp an ninh Guardrail.

---

## 5. Trạng thái & Gói tiếp theo

- **Trạng thái Gói A5-UI**: **HOÀN THÀNH 100%**.
- **Tiến độ tổng thể Phần A (Antigravity)**: Đã hoàn thành toàn bộ 6/6 gói công việc frontend độc lập:
  - Bước 0: Baseline & Phân nhánh.
  - A0: RUN.md & Health Check Supabase/ChromaDB.
  - Dựng Playwright & CUA Deep Check 8 màn hình.
  - A3-UI: Customer Data Surface, Tách form Checkout, Review form 403, Sửa ghi chú đơn 409.
  - A1-UI: UUID Session v4 độc lập theo user, chặn Fake Mock Reply khi backend 503.
  - A6: Safe Render Markdown, Allowlist link/ảnh, Punycode Homoglyph, Chặn raw HTML, Guard Badge.
  - A5-UI: Dữ liệu thật Admin, cờ `NEXT_PUBLIC_ALLOW_MOCK_ADMIN`, route `chat-logs`, Tab Hội thoại.
- **Bước tiếp theo**: Chờ nhánh Backend (`feat/a-backend` của Codex) hoàn tất và merge vào để thực hiện **Checklist kiểm thử toàn diện §5 trên toàn bộ hệ thống Web & RAG**.
