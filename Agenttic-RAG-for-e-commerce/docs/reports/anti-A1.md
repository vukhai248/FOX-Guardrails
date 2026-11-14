# Báo Cáo Nghiệm Thu Gói A1-UI — Antigravity

- **Gói công việc**: A1-UI (Sửa lỗi nền Chatbot: H1 Session ID & H10 Chặn Mock Fake Reply)
- **Người thực hiện**: Antigravity (Gemini 3.8 Flash High)
- **Nhánh**: `feat/a-frontend`
- **Ngày thực hiện**: 03/11/2026
- **Liên quan**: Lỗi H1, H10 trong `A-hoan-thien-web.md` và Hợp đồng API §3 trong `E-phan-cong-agent.md`

---

## 1. Đã làm gì

1. **Chuẩn hoá Session ID chuẩn UUID v4 RFC 4122 (`web_ui/src/components/chat-widget.tsx`)**:
   - Thay thế việc sinh chuỗi ngẫu nhiên `sess_...` cũ bằng thuật toán sinh **UUID v4 (RFC 4122)** chuẩn hóa (`crypto.randomUUID()` với fallback RFC 4122).
   - Đảm bảo `session_id` được lưu trữ độc lập theo từng tài khoản người dùng trong `localStorage` (`chat_session_id_${userId || 'guest'}`).
   - Tự động phát hiện và nâng cấp các chuỗi session cũ không hợp lệ lên UUID v4.
   - Gửi kèm `session_id` chuẩn UUID trong mọi request `POST /api/chat`.

2. **Chặn trả lời giả (Mock Fake Reply) khi Backend AI sập (`web_ui/src/app/api/chat/route.ts`)**:
   - Đưa khối Mock Fallback ra sau cờ môi trường `NEXT_PUBLIC_ALLOW_MOCK_CHAT` (mặc định tắt `false`).
   - Khi dịch vụ FastAPI Backend (`rag-service:8080`) bị tắt, lỗi timeout hoặc trả mã lỗi HTTP:
     - Nếu cờ `NEXT_PUBLIC_ALLOW_MOCK_CHAT` không bật: Trả về ngay mã lỗi HTTP **`503`** với body chuẩn Hợp đồng API §3:
       ```json
       {
         "error": {
           "code": "BACKEND_UNAVAILABLE",
           "message": "Hệ thống AI tư vấn hiện đang tạm thời gián đoạn kết nối. Vui lòng thử lại sau ít phút hoặc tạo ticket để nhân viên hỗ trợ trực tiếp."
         }
       }
       ```
     - Tuyệt đối không sinh câu trả lời ảo (no fake recommendations) che giấu sự cố của backend.

3. **Cải tiến Error-Handling phía Giao diện Chatbot (`web_ui/src/components/chat-widget.tsx`)**:
   - Xử lý mã `503` và mã lỗi `BACKEND_UNAVAILABLE` từ `/api/chat`: hiển thị tin nhắn cảnh báo bảo trì/gián đoạn mạng rõ ràng cho người dùng thay vì thông báo chung chung.
   - Giữ nguyên luồng hỗ trợ nhân viên (tab "Gặp nhân viên" / Support Ticket) để người dùng không bị bế tắc khi AI backend gặp sự cố.

4. **Xây dựng Bộ Test Playwright E2E cho A1-UI (`web_ui/tests/e2e/a1_ui.spec.ts`)**:
   - `A1.1`: Kiểm tra `session_id` sinh đúng chuẩn Regex UUID v4, lưu vào `localStorage` và gửi kèm trong body `POST /api/chat`.
   - `A1.2`: Kiểm tra phân tách `session_id` theo từng user độc lập (hai user khác nhau không dùng chung session).
   - `A1.3`: Kiểm tra khi backend trả về `503 BACKEND_UNAVAILABLE`, chat widget hiển thị đúng thông báo lỗi và không xuất hiện bất kỳ nội dung mock giả nào (`MacBook Air M3`, `Dell XPS 13`).
   - Chụp 2 ảnh màn hình bằng chứng CUA vào `web_ui/tests/e2e/screenshots/a1/`.

---

## 2. Danh sách file thay đổi / tạo mới

| File | Trạng thái | Mô tả |
| :--- | :--- | :--- |
| `web_ui/src/app/api/chat/route.ts` | Sửa đổi | Kiểm tra cờ `NEXT_PUBLIC_ALLOW_MOCK_CHAT`, trả về 503 `BACKEND_UNAVAILABLE` khi FastAPI lỗi. |
| `web_ui/src/components/chat-widget.tsx` | Sửa đổi | Sinh UUID v4 cho `session_id`, lưu theo user, xử lý lỗi 503 hiển thị thông báo rõ ràng. |
| `web_ui/tests/e2e/a1_ui.spec.ts` | Tạo mới | Bộ kiểm thử Playwright E2E tự động cho gói A1-UI (3 tests). |
| `web_ui/tests/e2e/screenshots/a1/*.png` | Tạo mới | 2 ảnh chụp màn hình CUA kiểm thử A1. |
| `docs/reports/anti-A1.md` | Tạo mới | Báo cáo nghiệm thu gói A1-UI. |
| `FOX-Guardrails/docs/plans/prompts/antigravity-phanA.md` | Sửa đổi | Cập nhật Project Tracker Log cho gói A1-UI. |

---

## 3. Lệnh kiểm thử & Output thực tế

### 3.1. Chạy bộ kiểm thử E2E A1-UI
- **Lệnh thực hiện**:
  ```powershell
  cd web_ui && npx playwright test tests/e2e/a1_ui.spec.ts
  ```
- **Output thực tế (3/3 Passed, 4.0s)**:
  ```text
  Running 3 tests using 3 workers

    ok 2 [chromium] › tests\e2e\a1_ui.spec.ts:52:7 › Gói A1-UI › A1.2: Phân tách session_id theo từng user độc lập (H1) (2.3s)
    ok 1 [chromium] › tests\e2e\a1_ui.spec.ts:7:7 › Gói A1-UI › A1.1: Chat widget sinh session_id chuẩn UUID v4, lưu vào localStorage và gửi kèm POST /api/chat (2.6s)
    ok 3 [chromium] › tests\e2e\a1_ui.spec.ts:77:7 › Gói A1-UI › A1.3: Khi backend gặp sự cố (503 BACKEND_UNAVAILABLE), Chat widget hiển thị thông báo lỗi rõ ràng, KHÔNG trả lời giả (H10) (2.6s)

    3 passed (4.0s)
  ```

### 3.2. Chạy toàn bộ Test Suite E2E (Kiểm tra hồi quy toàn diện)
- **Lệnh thực hiện**:
  ```powershell
  cd web_ui && npx playwright test
  ```
- **Output thực tế (17/17 Passed, 13.9s, 0 regression)**:
  ```text
  Running 17 tests using 6 workers
    17 passed (13.9s)
  ```

### 3.3. Kiểm tra biên dịch Production Build
- **Lệnh thực hiện**:
  ```powershell
  cd web_ui && npm.cmd run build
  ```
- **Output thực tế**:
  ```text
  ✓ Compiled successfully in 4.3s
  Running TypeScript ...
  Finished TypeScript in 7.4s ...
  ✓ Generating static pages using 11 workers (25/25) in 695ms
  Finalizing page optimization ...
  0 errors, 0 warnings.
  ```

### 3.4. Ảnh chụp màn hình CUA nghiệm thu (`web_ui/tests/e2e/screenshots/a1/`)
1. `chat_uuid_session.png`: Giao diện trò chuyện chat bot với session ID chuẩn UUID v4 trong localStorage.
2. `chat_backend_unavailable_503.png`: Giao diện chatbot hiển thị cảnh báo lỗi mạng 503 khi backend sập, hoàn toàn không sinh câu trả lời mock giả.

---

## 4. Việc còn mở / Bàn giao tiếp theo
- Gói A1-UI đã hoàn thành dứt điểm, đã kiểm chứng và đạt toàn bộ tiêu chí thiết kế.
- Chuyển sang thực hiện **Gói A6** (Render an toàn trong chat-widget: allowlist link/ảnh, Punycode homoglyph check, chặn HTML thô, cờ `NEXT_PUBLIC_SAFE_RENDER`, hiển thị nhãn khi response có `guard.action` ≠ `allow`).
