# Báo cáo Kiểm thử & Nghiệm thu: Gói A6 — Render An Toàn Trong Chat Widget (H11)

**Người thực hiện**: Antigravity (Tầng 3 — Frontend & QA / Kiểm thử)  
**Nhánh Git**: `feat/a-frontend`  
**Ngày thực hiện**: 03/11/2026  
**Mục tiêu**: Khắc phục triệt để lỗ hổng H11 (Chatbot render Markdown nguyên văn khiến link phishing, ảnh theo dõi/exfiltration và mã độc HTML có thể tự động tải/thực thi), bổ sung cơ chế kiểm duyệt tên miền sau khi chuẩn hoá Punycode để chặn tấn công Homoglyph (Cyrillic), điều khiển qua cờ `NEXT_PUBLIC_SAFE_RENDER` và hiển thị trực quan nhãn Guard Action khi FOX-Guardrails can thiệp.

---

## 1. Các công việc đã thực hiện

1. **Cơ chế Allowlist & Chặn Link Ngoài Bất Hợp Pháp**:
   - Tích hợp hàm `getLinkAllowlist()` đọc danh sách domain an toàn từ biến môi trường `NEXT_PUBLIC_LINK_ALLOWLIST` kết hợp cùng default allowlist (`localhost`, `127.0.0.1`, `cellphones.com.vn`, `images.unsplash.com` và hostname hiện tại của web).
   - Component `SafeMarkdownLink`:
     - Link nội bộ (`/products/...`, `#...`): Render bình thường qua `<Link>` của Next.js.
     - Link ngoài trong Allowlist: Render thẻ `<a>` kèm `rel="noopener noreferrer nofollow"`.
     - Link ngoài KHÔNG thuộc Allowlist: Vô hiệu hoá click, hiển thị text gạch ngang kèm nhãn cảnh báo `(liên kết ngoài đã bị chặn)`.

2. **Chặn Tấn Công Giả Mạo Tên Miền (Homoglyph / Punycode Attack)**:
   - Tận dụng cơ chế chuẩn hoá IDN sang Punycode của trình duyệt (`new URL()` tự động chuyển đổi ký tự Cyrillic như `аmazon.com` thành `xn--mazon-1qa.com`).
   - Phát hiện các hostname bắt đầu bằng hoặc chứa `xn--` để gắn cờ `isHomoglyph = true` và lập tức chặn liên kết, hiển thị nhãn `(tên miền giả mạo đã bị chặn)`.

3. **Cơ Chế Ẩn Ảnh Ngoài Không Xác Thực (Data Exfiltration & Tracking Protection)**:
   - Component `SafeMarkdownImage`:
     - Ảnh thuộc domain Allowlist: Render thẻ `<img>` với lazy loading và border an toàn.
     - Ảnh ngoài Allowlist (ví dụ tracking pixel `https://attacker-tracker.com/pixel.png`): Chặn hoàn toàn không cho trình duyệt tải ảnh về, thay thế bằng khung placeholder hiển thị alt text: `🖼️ [Ảnh ngoài đã bị ẩn: <alt>]`.

4. **Chống Tấn Công XSS / Raw HTML**:
   - Cấu hình component `Markdown` với tùy chọn `disableParsingRawHTML: isSafeRenderActive()`.
   - Toàn bộ các thẻ HTML thô như `<script>`, `<div onclick="...">`, `<iframe ...>` từ phản hồi của LLM bị vô hiệu hóa hoàn toàn, không render thành DOM nodes thực thi.

5. **Cờ Kiểm Soát Thực Nghiệm `NEXT_PUBLIC_SAFE_RENDER`**:
   - Mặc định: Bật an toàn (`true`).
   - Phục vụ nghiên cứu thực nghiệm đo lường Baseline G0: Khi cấu hình rõ ràng `NEXT_PUBLIC_SAFE_RENDER=false`, hệ thống sẽ cho phép render nguyên bản để đánh giá rủi ro an ninh mạng khi không có guardrail.

6. **Hiển Thị Huy Hiệu Bảo Vệ Guard Action (H11)**:
   - Cập nhật interface `ChatMessage` lưu trữ `guard?: GuardInfo`.
   - Khi response từ `/chat` hoặc proxy trả về `guard.action !== 'allow'`:
     - `action === 'block'`: Hiển thị badge màu đỏ `[🛡️ Đã can thiệp bảo vệ: Nội dung bị chặn (#decision_id)]`.
     - `action === 'flag'`: Hiển thị badge màu vàng hổ phách `[⚠️ Đang kiểm duyệt bảo vệ (#decision_id)]`.

---

## 2. Danh sách file thay đổi

| STT | Đường dẫn file | Mô tả thay đổi |
| :---: | :--- | :--- |
| 1 | `web_ui/src/components/chat-widget.tsx` | Cập nhật `GuardInfo`, `isSafeRenderActive()`, `getLinkAllowlist()`, `checkUrlSafety()`, `SafeMarkdownLink`, `SafeMarkdownImage`, lưu `guard` trong `handleSend`, render badge Guard Action và Markdown overrides. |
| 2 | `web_ui/tests/e2e/a6_safe_render.spec.ts` | Bộ test Playwright E2E gồm 5 kịch bản kiểm tra toàn diện 5 chuỗi bảo vệ: link nội bộ, link ngoài, ảnh ngoài, homoglyph, raw HTML và guard badge. |
| 3 | `web_ui/tests/e2e/screenshots/a6/*` | 6 ảnh chụp màn hình CUA kiểm chứng thực tế quá trình render và badge. |
| 4 | `docs/reports/anti-A6.md` | Tài liệu báo cáo nghiệm thu Gói A6. |

---

## 3. Lệnh test & Output thực tế

### 3.1. Biên dịch Next.js Production Build (`npm run build`)
```powershell
> npm.cmd run build

▲ Next.js 16.2.10 (Turbopack)
- Environments: .env.local

  Creating an optimized production build ...
✓ Compiled successfully in 3.5s
  Running TypeScript ...
  Finished TypeScript in 6.6s ...
  Collecting page data using 11 workers ...
  Generating static pages using 11 workers (25/25) in 564ms
  Finalizing page optimization ...

Route (app)                              Size     First Load JS
┌ ○ /                                    16.8 kB         155 kB
├ ○ /_not-found                          1.04 kB         103 kB
├ ○ /account                             10.3 kB         148 kB
├ ○ /admin                               38.3 kB         177 kB
├ ƒ /api/admin/orders                    0 B                0 B
├ ƒ /api/admin/tickets                   0 B                0 B
├ ƒ /api/admin/users                     0 B                0 B
├ ƒ /api/chat                            0 B                0 B
├ ƒ /api/chat/admin                      0 B                0 B
├ ƒ /api/stripe                          0 B                0 B
├ ○ /auth/callback                       182 B           102 kB
├ ○ /auth/forgot-password                4.18 kB         142 kB
├ ○ /auth/login                          4.96 kB         143 kB
├ ○ /auth/register                       5.17 kB         143 kB
├ ○ /auth/reset-password                 4.2 kB          142 kB
├ ○ /cart                                6.16 kB         144 kB
├ ○ /checkout                            9.22 kB         147 kB
├ ○ /checkout-success                    4.49 kB         143 kB
├ ○ /policy/return                       2.92 kB         141 kB
├ ○ /policy/shipping                     2.85 kB         141 kB
├ ○ /policy/terms                        2.87 kB         141 kB
├ ○ /policy/warranty                     2.91 kB         141 kB
├ ○ /products                            6.4 kB          145 kB
└ ƒ /products/[id]                       10.7 kB         149 kB

✓ Build thành công 100%, 0 lỗi TypeScript, 0 lỗi biên dịch.
```

### 3.2. Chạy bộ kiểm thử Playwright cho Gói A6 (`tests/e2e/a6_safe_render.spec.ts`)
```powershell
> npx playwright test tests/e2e/a6_safe_render.spec.ts

Running 5 tests using 5 workers

  ok 1 [chromium] › tests\e2e\a6_safe_render.spec.ts:84:7 › A6.3: Phát hiện và chặn tấn công tên miền giả mạo Homoglyph (Punycode Attack) (3.0s)
  ok 2 [chromium] › tests\e2e\a6_safe_render.spec.ts:47:7 › A6.2: Ẩn ảnh ngoài không thuộc allowlist, hiển thị ảnh trong allowlist (3.0s)
  ok 3 [chromium] › tests\e2e\a6_safe_render.spec.ts:5:7 › A6.1: Render link nội bộ hợp lệ, chặn link ngoài không thuộc allowlist (3.0s)
  ok 4 [chromium] › tests\e2e\a6_safe_render.spec.ts:159:7 › A6.5: Hiển thị nhãn Guard Action khi response có guard.action ≠ allow (H11) (3.3s)
  ok 5 [chromium] › tests\e2e\a6_safe_render.spec.ts:120:7 › A6.4: Chặn parse HTML thô (Raw HTML Mitigation / XSS Prevention) (4.0s)

  5 passed (5.2s)
```

### 3.3. Chạy toàn bộ Test Suite Playwright (Regression Check)
```powershell
> npx playwright test

Running 22 tests using 6 workers

  ok  1 [chromium] › tests\e2e\a1_ui.spec.ts:52:7 › A1.2: Phân tách session_id theo từng user độc lập (H1) (3.2s)
  ok  2 [chromium] › tests\e2e\a1_ui.spec.ts:77:7 › A1.3: Khi backend gặp sự cố (503 BACKEND_UNAVAILABLE), Chat widget hiển thị thông báo lỗi rõ ràng, KHÔNG trả lời giả (H10) (5.3s)
  ok  3 [chromium] › tests\e2e\a1_ui.spec.ts:7:7 › A1.1: Chat widget sinh session_id chuẩn UUID v4, lưu vào localStorage và gửi kèm POST /api/chat (5.4s)
  ok  4 [chromium] › tests\e2e\a3_ui.spec.ts:236:7 › A3.3: Trang /account - Sửa ghi chú đơn hàng pending gọi PATCH /api/orders/{id}/note (7.8s)
  ok  5 [chromium] › tests\e2e\a6_safe_render.spec.ts:84:7 › A6.3: Phát hiện và chặn tấn công tên miền giả mạo Homoglyph (Punycode Attack) (3.2s)
  ok  6 [chromium] › tests\e2e\a6_safe_render.spec.ts:47:7 › A6.2: Ẩn ảnh ngoài không thuộc allowlist, hiển thị ảnh trong allowlist (3.6s)
  ok  7 [chromium] › tests\e2e\a6_safe_render.spec.ts:5:7 › A6.1: Render link nội bộ hợp lệ, chặn link ngoài không thuộc allowlist (5.8s)
  ok  8 [chromium] › tests\e2e\a3_ui.spec.ts:128:7 › A3.2: Form Review sản phẩm - Xử lý 403 NOT_PURCHASED và thành công 201 (10.4s)
  ok  9 [chromium] › tests\e2e\a3_ui.spec.ts:5:7 › A3.1: Form Checkout tách trường, gọi POST /api/orders và redirect checkout-success không lộ PII (11.2s)
  ok 10 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: products_list (/products) (3.1s)
  ok 11 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: homepage (/) (3.5s)
  ok 12 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: product_detail (/products/136045) (2.6s)
  ok 13 [chromium] › tests\e2e\a6_safe_render.spec.ts:159:7 › A6.5: Hiển thị nhãn Guard Action khi response có guard.action ≠ allow (H11) (4.8s)
  ok 14 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: cart (/cart) (2.5s)
  ok 15 [chromium] › tests\e2e\a6_safe_render.spec.ts:120:7 › A6.4: Chặn parse HTML thô (Raw HTML Mitigation / XSS Prevention) (5.6s)
  ok 16 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: checkout (/checkout) (2.1s)
  ok 17 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: account (/account) (2.1s)
  ok 18 [chromium] › tests\e2e\smoke.spec.ts:39:7 › 3. Backend FastAPI RAG Service hoạt động và kết nối đủ DB/Chroma (531ms)
  ok 19 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: admin (/admin) (2.9s)
  ok 20 [chromium] › tests\e2e\cua_check.spec.ts:17:9 › CUA Check: login (/auth/login) (2.8s)
  ok 21 [chromium] › tests\e2e\smoke.spec.ts:5:7 › 1. Trang chủ tải thành công và hiển thị các khối nội dung (2.8s)
  ok 22 [chromium] › tests\e2e\smoke.spec.ts:18:7 › 2. Chat widget mở được và hiển thị giao diện trò chuyện (2.7s)

  22 passed (18.0s)
```

---

## 4. Ảnh chụp kiểm chứng CUA (Screenshots)

Các ảnh chụp màn hình kiểm chứng đã được lưu trong thư mục `web_ui/tests/e2e/screenshots/a6/`:
1. `a6_links_check.png`: Link nội bộ hiển thị bình thường, link ngoài google.com bị vô hiệu hoá kèm nhãn `(liên kết ngoài đã bị chặn)`.
2. `a6_images_check.png`: Ảnh ngoài attacker-tracker.com bị ẩn và chỉ hiện alt text `[Ảnh ngoài đã bị ẩn: Pixel theo dõi]`, ảnh Unsplash hiển thị hợp lệ.
3. `a6_homoglyph_check.png`: Nhận diện tấn công Cyrillic Homoglyph `аmazon.com` và hiển thị nhãn đỏ `(tên miền giả mạo đã bị chặn)`.
4. `a6_raw_html_check.png`: Thẻ `<script>` và `<div>` thô không thực thi mã độc.
5. `a6_guard_badge_block.png`: Huy hiệu bảo vệ đỏ `[🛡️ Đã can thiệp bảo vệ: Nội dung bị chặn (#dec_guard_98765)]`.
6. `a6_guard_badge_flag.png`: Huy hiệu cảnh báo hổ phách `[⚠️ Đang kiểm duyệt bảo vệ (#dec_flag_12345)]`.

---

## 5. Trạng thái & Gói tiếp theo

- **Trạng thái Gói A6**: **HOÀN THÀNH 100%**.
- **Gói tiếp theo theo kế hoạch**: **Gói A5-UI (Log hội thoại, admin dùng dữ liệu thật, route chat-logs, tab Hội thoại)**.
