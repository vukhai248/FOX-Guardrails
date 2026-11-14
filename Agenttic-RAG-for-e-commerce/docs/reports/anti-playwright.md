# Báo Cáo Nghiệm Thu Khung Kiểm Thử Playwright — Antigravity

- **Gói công việc**: Dựng khung kiểm thử tự động Playwright E2E
- **Người thực hiện**: Antigravity (Gemini 3.8 Flash High)
- **Nhánh**: `feat/a-frontend`
- **Ngày thực hiện**: 02/11/2026

---

## 1. Đã làm gì

1. **Cài đặt thư viện Playwright**:
   - Thêm `@playwright/test` vào `web_ui/package.json` (`devDependencies`).
   - Tải bộ browser engine Chromium và Chrome Headless Shell phục vụ chạy headless trên máy Windows.
2. **Cấu hình `playwright.config.ts`**:
   - Thư mục test: `./tests/e2e`.
   - `baseURL: http://localhost:3000`.
   - Cấu hình webServer tự động tái sử dụng server dev hiện có (`reuseExistingServer: true`).
   - Xuất report HTML và list console.
   - Thêm script `"test:e2e": "playwright test"` vào `package.json`.
3. **Soạn thảo Bộ Kiểm thử Khói (Smoke Test Suite) & Kiểm tra Trực quan (CUA Check)**:
   - File `web_ui/tests/e2e/smoke.spec.ts` gồm 3 kịch bản:
     1. `Trang chủ tải thành công và hiển thị các khối nội dung`: Kiểm tra page load, verify tiêu đề trang `4Customer`, chụp ảnh màn hình CUA `homepage.png`.
     2. `Chat widget mở được và hiển thị giao diện trò chuyện`: Nhấp mở floating button `title="Trò chuyện với trợ lý AI"`, verify header `Trực tuyến tư vấn`, chụp ảnh màn hình CUA `chat_opened.png`.
     3. `Backend FastAPI RAG Service hoạt động`: Gọi `GET http://127.0.0.1:8080/health` và assert `status: 'healthy'`, `supabase_connected: true`, `chroma_connected: true`.
4. **Cấu hình Git Ignore**:
   - Bổ sung `playwright-report/` và `test-results/` vào `.gitignore` để không làm bẩn Git tree.

---

## 2. Danh sách file thay đổi / tạo mới

| File | Trạng thái | Mô tả |
| :--- | :--- | :--- |
| `web_ui/package.json` | Sửa đổi | Bổ sung script `test:e2e` và dependency `@playwright/test`. |
| `web_ui/package-lock.json` | Sửa đổi | Cập nhật lockfile. |
| `web_ui/playwright.config.ts` | Tạo mới | File cấu hình kiểm thử E2E Playwright. |
| `web_ui/tests/e2e/smoke.spec.ts` | Tạo mới | Bộ kiểm thử smoke test và chụp ảnh màn hình CUA. |
| `web_ui/tests/e2e/screenshots/*.png` | Tạo mới | Ảnh chụp xác minh giao diện trang chủ & chat widget. |
| `.gitignore` | Sửa đổi | Bỏ qua các thư mục log / report của Playwright. |
| `docs/reports/anti-playwright.md` | Tạo mới | Báo cáo nghiệm thu thiết lập Playwright. |

---

## 3. Lệnh kiểm thử & Output thực tế

- **Lệnh chạy**:
  ```powershell
  cd web_ui && npm.cmd run test:e2e
  ```
- **Output thực tế**:
  ```text
  > agentic-rag-web@0.1.0 test:e2e
  > playwright test

  Running 3 tests using 3 workers

    ok 2 [chromium] › tests\e2e\smoke.spec.ts:39:7 › E2E Smoke Test Suite › 3. Backend FastAPI RAG Service hoạt động và kết nối đủ DB/Chroma (175ms)
    ok 1 [chromium] › tests\e2e\smoke.spec.ts:5:7 › E2E Smoke Test Suite › 1. Trang chủ tải thành công và hiển thị các khối nội dung (3.7s)
    ok 3 [chromium] › tests\e2e\smoke.spec.ts:18:7 › E2E Smoke Test Suite › 2. Chat widget mở được và hiển thị giao diện trò chuyện (3.9s)

    3 passed (7.0s)
  ```
- **Ảnh chụp xác minh CUA**:
  - `web_ui/tests/e2e/screenshots/homepage.png`
  - `web_ui/tests/e2e/screenshots/chat_opened.png`
- **Build verification**: `npm.cmd run build` chạy thành công không có lỗi biên dịch.

---

## 4. Việc còn mở / Bàn giao tiếp theo
- Khởi động **Gói A3-UI**:
  - Tách trường form checkout (`recipient_name`, `recipient_phone`, `address_line`, `ward`, `province`, `note`).
  - Cập nhật trang `/checkout-success` đọc từ `GET /api/orders/{id}` (bỏ hoàn toàn logic tạo đơn client-side).
  - Thêm form gửi đánh giá sản phẩm (gọi `POST /api/reviews`).
  - Thêm tính năng sửa ghi chú đơn hàng trạng thái `pending` tại `/account` (gọi `PATCH /api/orders/{id}/note`).
