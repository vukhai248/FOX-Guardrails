# Báo Cáo Nghiệm Thu Gói A0 — Antigravity (Frontend & Kiểm thử)

- **Gói công việc**: A0 — Chạy được local + Tài liệu chạy `docs/RUN.md`
- **Người thực hiện**: Antigravity (Gemini 3.8 Flash High)
- **Nhánh**: `feat/a-frontend`
- **Ngày thực hiện**: 02/11/2026

---

## 1. Đã làm gì

1. **Khởi tạo nhánh làm việc**:
   - Lưu baseline commit trên `main` (`chore: save baseline before Phase A implementation`).
   - Mở khóa thư mục `docs/` trong `.gitignore` để lưu trữ tài liệu chạy và báo cáo nghiệm thu.
   - Bổ sung `.session-history/` và `.design/` vào `.gitignore` để chống nhiễu tracking.
   - Tạo nhánh `feat/a-backend` sẵn sàng cho Codex và checkout nhánh `feat/a-frontend` cho Antigravity.
2. **Nâng cấp Endpoint Kiểm tra Sức khỏe (`GET /health`)**:
   - Cập nhật hàm `health_check()` trong `rag-service/app/main.py`.
   - Bổ sung cơ chế tự động kiểm tra kết nối tới ChromaDB (`ChromaVectorDatabase().count_documents("products_collection")`).
   - Trả về chi tiết: `status`, `service`, `debug_mode`, `supabase_connected`, `chroma_connected`, `chroma_products_count`.
3. **Phát hiện và Xử lý Lỗi Mã Hóa Hệ Thống trên Windows (Critical Bug)**:
   - **Hiện tượng**: Khi gọi API `/chat`, request sập với lỗi 500: `'charmap' codec can't encode character '\U0001f9e9'`.
   - **Nguyên nhân**: File `workflow_1.py:274` in ra console biểu tượng emoji `🧩 Injected skill for query: ...`. Trên Windows PowerShell, encoding mặc định của Python là `cp1252`/`charmap` dẫn đến `UnicodeEncodeError`.
   - **Giải pháp**: Thiết lập biến môi trường bắt buộc `$env:PYTHONUTF8=1` trước khi chạy Uvicorn.
4. **Soạn thảo Hoàn chỉnh Tài liệu `docs/RUN.md`**:
   - Mô tả kiến trúc tổng thể, cổng dịch vụ, môi trường yêu cầu (Node.js >= 20, Conda env `DL`).
   - Cảnh báo rõ ràng tuyệt đối không chạy lại `database/setup.sql` để bảo vệ dữ liệu.
   - Hướng dẫn cấu hình `.env` và `.env.local` không lộ secret.
   - Hướng dẫn khởi chạy chi tiết từng bước cho Backend và Frontend.
   - Kịch bản Smoke Test xác minh kết quả.

---

## 2. Danh sách file thay đổi / tạo mới

| File | Trạng thái | Mô tả |
| :--- | :--- | :--- |
| `docs/RUN.md` | Tạo mới | Hướng dẫn triển khai local chi tiết. |
| `rag-service/app/main.py` | Sửa đổi | Bổ sung kiểm tra kết nối ChromaDB vào `GET /health`. |
| `.gitignore` | Sửa đổi | Bỏ chặn `docs/`, thêm `.session-history/` và `.design/`. |
| `docs/reports/anti-A0.md` | Tạo mới | Báo cáo nghiệm thu gói A0. |

---

## 3. Lệnh kiểm thử & Output thực tế

### 3.1 Kiểm tra GET /health
- **Lệnh**:
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -Method Get | ConvertTo-Json
  ```
- **Output thực tế**:
  ```json
  {
      "status":  "healthy",
      "service":  "rag-service",
      "debug_mode":  true,
      "supabase_connected":  true,
      "chroma_connected":  true,
      "chroma_products_count":  1325
  }
  ```

### 3.2 Kiểm tra Smoke Test POST /chat
- **Lệnh**:
  ```powershell
  $jsonStr = '{"message":"Shop co chinh sach doi tra the nao?", "session_id":"test-session-a0"}'
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonStr)
  Invoke-RestMethod -Uri "http://127.0.0.1:8080/chat" -Method Post -Body $bytes -ContentType "application/json; charset=utf-8" | ConvertTo-Json -Depth 5
  ```
- **Output thực tế**:
  ```json
  {
      "reply": "Dạ bên em hỗ trợ đổi trả 1 đổi 1 trong vòng 30 ngày kể từ ngày nhận hàng nếu sản phẩm gặp lỗi kỹ thuật từ nhà sản xuất...",
      "tool_used": "policy_search",
      "sources": [],
      "session_id": "test-session-a0"
  }
  ```

### 3.3 Kiểm tra Build Frontend Web
- **Lệnh**:
  ```powershell
  cd web_ui && npm.cmd run build
  ```
- **Output thực tế**:
  ```text
  ▲ Next.js 16.2.10 (Turbopack)
  ✓ Compiled successfully in 5.2s
  ✓ Generating static pages using 11 workers (25/25) in 667ms
  Finalizing page optimization ...
  Route (app)                              Size     First Load JS
  ┌ ○ /                                    ...
  ...
  Command exited with code 0.
  ```

---

## 4. Việc còn mở / Bàn giao tiếp theo
- Dựng khung kiểm thử tự động **Playwright** trong `web_ui/` (`playwright.config.ts`, `tests/e2e/`) và thêm script `test:e2e` vào `package.json`.
- Chuyển sang thực hiện **A3-UI** (tách trường form checkout, kết nối form review, sửa ghi chú đơn hàng).
