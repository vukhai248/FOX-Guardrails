# Báo cáo Khắc phục & Nghiệm thu Đóng góp Review Claude Opus (F1, F2, F3, F4)

**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `feat/a-frontend`  
**Ngày thực hiện**: 03/11/2026  
**Tham chiếu chỉ đạo**: Phản hồi review nghiệm thu gói A của Claude Opus (Lead Architect)

---

## 1. Tóm tắt kết quả khắc phục 4 điểm Review

Toàn bộ 4 điểm đóng góp và yêu cầu an ninh từ Claude Opus đã được Antigravity thực hiện triệt để, tuân thủ nguyên tắc **Defensive Coding** (hiểu trước, sửa tối thiểu, kiểm chứng sau):

| Mã mục | Vấn đề được Claude Opus chỉ ra | Trạng thái | Minh chứng kiểm chứng |
| :---: | :--- | :---: | :--- |
| **F1** | Bypass Allowlist Link/Ảnh trong A6 qua protocol-relative (`//`), backslash (`/\`), URL-encode (`%5c`) và ảnh nội bộ bị chặn oan | **ĐÃ HOÀN TẤT** | Test case `A6.6` chạy 6 vector bypass + ảnh nội bộ -> **PASSED**. Screenshot `a6_bypass_vectors_blocked.png`. |
| **F2** | Lỗ hổng leo quyền Admin A5 do tin cậy `user_metadata.role` (người dùng tự sửa được qua Supabase client) | **ĐÃ HOÀN TẤT** | Tạo `web_ui/src/lib/server/auth.ts` dùng Service Role tra cứu bảng `public.user_roles`. Chặn 403 `FORBIDDEN`. Test case `A5.4` -> **PASSED**. |
| **F3** | Lệch chuẩn API Contract `GET /api/admin/chat-logs` (`sessionId` vs `session_id`, mã lỗi 401/403) | **ĐÃ HOÀN TẤT** | Hỗ trợ song song cả 2 param `session_id` & `sessionId`, format lỗi chuẩn `{ error: { code, message } }`. Test case `A5.2` -> **PASSED**. |
| **F4** | Vệ sinh commit (ChromaDB binary), `.gitignore`, dọn sạch ESLint `any`, chuyển Tracker và tài liệu bàn giao Codex | **ĐÃ HOÀN TẤT** | Revert 2 file binary ChromaDB về `main`, thêm vào `.gitignore`, `eslint` sạch 0 lỗi, tạo `requests.md` và `anti-tracker.md`. |

---

## 2. Chi tiết từng hạng mục

### F1 — Sửa lỗ hổng Bypass Allowlist Link/Ảnh trong `web_ui/src/components/chat-widget.tsx`
- **Nguyên nhân gốc**: 
  - Hàm kiểm tra `checkUrlSafety` cũ chỉ kiểm tra `rawUrl.startsWith('/')` để cho phép URL nội bộ. Tuy nhiên, trên trình duyệt (đặc biệt Windows Chromium):
    - `//evil.com` là protocol-relative URL dẫn ra ngoài.
    - `/\evil.com` hoặc `\evil.com` bị tự động chuẩn hoá thành `//evil.com`.
    - `%5c` hoặc `%2f%2f` qua URL decode có thể lọt qua bộ lọc chuỗi cơ bản.
    - Component `SafeMarkdownImage` chỉ kiểm tra hostname trong allowlist mà bỏ qua các ảnh nội bộ an toàn bắt đầu bằng `/`.
- **Giải pháp xử lý**:
  - Chặn đứng mọi URL chứa `\`, `%5c`, `%5C`, `%2f%2f` hoặc bắt đầu bằng `//`.
  - Chặn các protocol scheme nguy hiểm: `javascript:`, `data:`, `vbscript:`, `file:`.
  - Luôn parse bằng `new URL(trimmed, baseOrigin)`. Chỉ coi là nội bộ an toàn khi `parsed.origin === baseOrigin && trimmed.startsWith('/') && !trimmed.startsWith('//') && !trimmed.includes('\\')`.
  - Cập nhật `SafeMarkdownImage` cho phép ảnh nội bộ an toàn (`isInternal || safe`).
- **Kiểm chứng**:
  - Viết mới test `A6.6` trong `web_ui/tests/e2e/a6_safe_render.spec.ts` kiểm thử 6 vector bypass và ảnh nội bộ:
    1. Protocol-relative: `//evil-shop.example` -> Bị chặn
    2. Backslash bypass: `/\evil-shop.example` -> Bị chặn
    3. Backslash thuần: `\evil-shop.example` -> Bị chặn
    4. URL-encoded backslash: `/%5cevil-shop.example` -> Bị chặn
    5. JavaScript scheme: `javascript:alert(1)` -> Bị chặn
    6. Internal safe image: `/images/phone.png` -> Cho phép hiển thị

### F2 — Ngăn chặn Leo quyền Admin (Privilege Escalation)
- **Nguyên nhân gốc**:
  - Supabase client cho phép người dùng tự gọi `supabase.auth.updateUser({ data: { role: 'admin' } })`. Nếu server đọc `user.user_metadata?.role` thì bất kỳ người dùng nào cũng có thể leo quyền quản trị viên.
  - Bảng thẩm quyền duy nhất trong schema (`database/setup.sql:108-113`) là `public.user_roles`.
- **Giải pháp xử lý**:
  - Xây dựng module dùng chung `web_ui/src/lib/server/auth.ts`:
    - Đọc Bearer token từ header `Authorization`.
    - Dùng Supabase Client xác thực JWT lấy `user_id`.
    - Dùng Service Role Client (bỏ qua RLS) truy vấn trực tiếp bảng `public.user_roles` để lấy danh sách role thực tế của user.
    - So sánh với `allowedRoles`: Nếu thiếu/sai token trả 401 `UNAUTHENTICATED`, nếu không có quyền admin trả 403 `FORBIDDEN`.
  - Tích hợp bảo vệ 4 API route quản trị:
    - `/api/admin/chat-logs/route.ts`
    - `/api/admin/orders/route.ts`
    - `/api/admin/tickets/route.ts`
    - `/api/admin/users/route.ts`: Khi Admin cập nhật role của user khác, thực hiện upsert trực tiếp vào bảng `public.user_roles` bằng Service Role Client (kèm đồng bộ `user_metadata`).
- **Kiểm chứng**:
  - Test case `A5.4`: User cố tình cập nhật `user_metadata.role = 'admin'` nhưng trong bảng `user_roles` là role `customer`. Khi truy cập API admin lập tức bị từ chối với status 403 và mã lỗi `FORBIDDEN` -> **PASSED**.

### F3 — Chuẩn hoá Hợp đồng API `GET /api/admin/chat-logs`
- **Giải pháp xử lý**:
  - Cập nhật `web_ui/src/app/api/admin/chat-logs/route.ts`:
    - Chấp nhận song song cả 2 tham số truy vấn: `session_id` và `sessionId`.
    - Chấp nhận `risk_level` và `riskLevel`.
    - Chuẩn hoá định dạng lỗi nhất quán:
      ```json
      {
        "error": {
          "code": "UNAUTHENTICATED" | "FORBIDDEN" | "INTERNAL_ERROR",
          "message": "Chi tiết lỗi"
        }
      }
      ```
    - Chuẩn hoá cấu trúc trả về 200: `{ chat_logs: [...], total, limit, offset }`.
- **Kiểm chứng**:
  - Test case `A5.2`: Không có Bearer token trả về 401 `UNAUTHENTICATED` -> **PASSED**.
  - Test case `A5.3`: UI Admin gọi `GET /api/admin/chat-logs?limit=50&offset=0` tải dữ liệu thật, xem chi tiết và lọc theo mức độ rủi ro -> **PASSED**.

### F4 — Vệ sinh Commit, Gitignore, ESLint & Bàn giao
- **Xử lý binary ChromaDB**:
  - Đã revert 2 file `database/chroma_db/3452f77e-119a-43a3-91d5-8323bcf61c94/{data_level0.bin, length.bin}` về nguyên trạng commit gốc của nhánh `main`.
  - Thêm `database/chroma_db/` vào `.gitignore` để ngăn vĩnh viễn việc track binary nặng vào git.
- **Dọn sạch ESLint**:
  - Thay thế toàn bộ các kiểu dữ liệu `any` còn sót lại trong các file spec test E2E (`a3_ui.spec.ts`, `a5_ui.spec.ts`, `a6_safe_render.spec.ts`) và các API route bằng các kiểu tường minh (`Record<string, unknown>`, `Page`, `Route`).
  - Lệnh `npx eslint` quét sạch **0 errors, 0 warnings**.
- **Tài liệu bàn giao**:
  - `docs/reports/requests.md`: Mô tả chi tiết việc xây dựng `web_ui/src/lib/server/auth.ts` và hợp đồng API chat-logs để Codex nắm và tái sử dụng khi xây dựng API backend.
  - `docs/reports/anti-tracker.md`: Chuyển bảng Tracker Log về repo tài liệu frontend.

---

## 3. Tổng hợp Bằng chứng Thực thi Kiểm thử

### 3.1. Build Kiểm tra Kiểu TypeScript & Production
- Lệnh: `npm.cmd run build` trong thư mục `web_ui`
- Kết quả:
  ```
  ▲ Next.js 16.2.10 (Turbopack)
  ✓ Compiled successfully in 5.3s
  Finished TypeScript in 8.0s ...
  ✓ Generating static pages using 11 workers (26/26) in 436ms
  ```
- **26/26 routes biên dịch hoàn hảo, 0 lỗi TypeScript**.

### 3.2. Regression Test Toàn bộ Playwright Suite
- Lệnh: `npx.cmd playwright test` trong thư mục `web_ui`
- Kết quả: **27 passed (25.5s)**:
  - `a1_ui.spec.ts`: 3/3 passed (H1 UUID session_id, phân tách session, H10 chặn mock reply khi 503)
  - `a3_ui.spec.ts`: 3/3 passed (A3.1 form checkout tách trường, A3.2 review 403, A3.3 sửa ghi chú đơn hàng)
  - `a5_ui.spec.ts`: 4/4 passed (A5.1 tắt mock, A5.2 auth 401, A5.3 UI chat logs thật, A5.4 chặn leo quyền F2)
  - `a6_safe_render.spec.ts`: 6/6 passed (A6.1 allowlist link, A6.2 ẩn ảnh ngoài, A6.3 chặn homoglyph, A6.4 chặn raw HTML, A6.5 guard badge, A6.6 chặn 6 vector bypass F1)
  - `cua_check.spec.ts`: 8/8 passed (kiểm tra giao diện 8 trang cốt lõi)
  - `smoke.spec.ts`: 3/3 passed (kiểm tra homepage, chat widget mở, backend RAG service 8080)

---

## 4. Danh sách các file thay đổi trong đợt này

1. `web_ui/src/components/chat-widget.tsx`: Nâng cấp hàm `checkUrlSafety` chặn protocol-relative, backslash, hex-encode; hỗ trợ ảnh nội bộ.
2. `web_ui/src/lib/server/auth.ts`: Module xác thực server-side mới, tra cứu bảng `public.user_roles`.
3. `web_ui/src/app/api/admin/chat-logs/route.ts`: Dùng `requireRole`, hỗ trợ param `session_id`/`sessionId`, chuẩn mã lỗi 401/403.
4. `web_ui/src/app/api/admin/orders/route.ts`: Bảo vệ quyền admin qua `requireRole`.
5. `web_ui/src/app/api/admin/tickets/route.ts`: Bảo vệ quyền admin qua `requireRole`.
6. `web_ui/src/app/api/admin/users/route.ts`: Dùng `requireRole`, upsert trực tiếp vào `public.user_roles` khi phân quyền.
7. `web_ui/tests/e2e/a6_safe_render.spec.ts`: Bổ sung test A6.6 kiểm chứng 6 vector bypass F1, dọn sạch type `any`.
8. `web_ui/tests/e2e/a5_ui.spec.ts`: Cập nhật A5.2 kiểm tra lỗi chuẩn F3, bổ sung A5.4 kiểm tra leo quyền F2, dọn sạch type `any`.
9. `web_ui/tests/e2e/a3_ui.spec.ts`: Dọn sạch type `any`.
10. `.gitignore`: Bổ sung bỏ qua `database/chroma_db/`.
11. `docs/reports/requests.md`: Tài liệu bàn giao auth và contract API cho Codex.
12. `docs/reports/anti-tracker.md`: Tài liệu Tracker Log của Antigravity.
13. `docs/reports/anti-fix-1.md`: Báo cáo chi tiết này.
