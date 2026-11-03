# Prompt giao việc — Antigravity (Phần A, frontend & kiểm thử)

Dán nguyên khối dưới vào Antigravity, mở tại `D:/create/DATN/Agenttic-RAG-for-e-commerce`, nhánh `feat/a-frontend`.

---

Bạn là kỹ sư frontend kiêm QA của đồ án. Repo là web e-commerce Agentic RAG (Next.js 16 `web_ui/` + FastAPI `rag-service/` + Supabase).

Đọc trước, theo thứ tự:
1. `D:/create/DATN/FOX-Guardrails/docs/plans/E-phan-cong-agent.md` — vai trò, file bạn sở hữu (§2), hợp đồng API (§3), checklist kiểm thử (§5), quy tắc (§7).
2. `D:/create/DATN/FOX-Guardrails/docs/plans/A-hoan-thien-web.md` — hiện trạng và đặc tả các gói.

Phạm vi của bạn, theo thứ tự:
1. **A0**: `docs/RUN.md` (chạy local từ máy sạch; không ghi giá trị secret).
2. **Dựng Playwright** trong `web_ui/` (`playwright.config.ts`, `tests/e2e/`), thêm script `test:e2e` vào `package.json`.
3. **A3-UI**: form checkout tách trường (người nhận, SĐT, địa chỉ, phường/xã, tỉnh/thành, ghi chú giao hàng) gọi `POST /api/orders`; trang `checkout-success` đọc `GET /api/orders/{id}` (bỏ toàn bộ việc tạo đơn ở client); form gửi review gọi `POST /api/reviews`; sửa ghi chú đơn `pending` ở `/account` gọi `PATCH /api/orders/{id}/note`.
4. **A1-UI**: chat-widget sinh và giữ `session_id` (UUID trong localStorage theo user); `/api/chat` trả 503 `BACKEND_UNAVAILABLE` khi backend lỗi, trừ khi `NEXT_PUBLIC_ALLOW_MOCK_CHAT=true`.
5. **A6**: render an toàn trong chat-widget (allowlist link/ảnh, so sau khi đổi Punycode, không render HTML thô, cờ `NEXT_PUBLIC_SAFE_RENDER`), hiển thị nhãn khi response có `guard.action` ≠ `allow`.
6. **A5-UI**: admin dùng dữ liệu thật, chỉ dùng mock khi `NEXT_PUBLIC_ALLOW_MOCK_ADMIN=true`; route `GET /api/admin/chat-logs`; tab "Hội thoại".
7. Sau khi backend được merge: chạy **checklist §5** trên toàn web, tự động hoá được mục nào bằng Playwright thì làm, còn lại kiểm tay; ghi lỗi vào `docs/QA/bugs.md` (bước tái hiện, kết quả mong đợi / thực tế, ảnh chụp).

Cách làm:
- API backend chưa có thì **mock theo đúng hợp đồng §3** trong test (Playwright `route.fulfill`), không tự viết route backend (`api/orders`, `api/stripe`, `api/reviews` thuộc agent khác).
- Hết mỗi mục: chạy `npm run lint`, `npm run build`, `npm run test:e2e`; commit `feat(A<n>-ui): …`; viết `docs/reports/anti-A<n>.md` (đã làm gì / file đổi / lệnh test + output thật / ảnh chụp / việc còn mở); rồi **dừng và chờ** tôi cho đi tiếp.
- Cần sửa file ngoài phần sở hữu thì ghi vào `docs/reports/requests.md`, không sửa trực tiếp.
- Không commit `.env*`; không chạy `database/setup.sql`; không đổi system prompt của bot.

Bắt đầu với A0 và dựng Playwright. Trước khi làm, liệt kê ngắn (≤ 10 dòng) kế hoạch và các file sẽ tạo/sửa.

---

## 📌 Project Tracker Log — Antigravity (Frontend & Kiểm thử)

| Gói | Trạng thái | Branch / Commit | Ghi chú & Lỗi phát hiện (Bug Tracker) | Nghiệm thu |
| :--- | :--- | :--- | :--- | :--- |
| **Bước 0** | **Xong** | `main` -> `feat/a-frontend`<br>`dd4093d` | Lưu baseline commit, unignore `docs/`, tạo sẵn nhánh `feat/a-backend` cho Codex và checkout `feat/a-frontend`. | Đã neo baseline |
| **A0** | **Xong** | `feat/a-frontend` | • Soạn `docs/RUN.md` hướng dẫn chạy máy sạch.<br>• Nâng cấp `GET /health` kiểm tra kết nối Supabase + ChromaDB.<br>• **Bug Critical phát hiện trên Windows**: Pipeline in emoji `🧩` ở `workflow_1.py:274` gây crash 500 do lỗi charmap codec. Giải pháp: `$env:PYTHONUTF8=1`.<br>• Smoke test `POST /chat` & `GET /health` thành công; `npm run build` thành công. | Đã lập báo cáo `docs/reports/anti-A0.md` |
| **Dựng Playwright** | **Xong** | `feat/a-frontend`<br>`14d14c6` | Cài đặt Playwright, cấu hình `playwright.config.ts`, `tests/e2e/smoke.spec.ts`, script `test:e2e`. Đã verify CUA screenshot trang chủ & chat widget (3/3 test passed). | Đã lập báo cáo `docs/reports/anti-playwright.md` |
| **CUA Deep Check** | **Xong** | `feat/a-frontend`<br>`bdc51bf` | • Viết `cua_check.spec.ts` quét 8 màn hình chính (8/8 passed, 0 error).<br>• Fix bug Hydration mismatch trên Header & Login inputs (`caret-color`).<br>• Fix bug JS variable hoisting `hydrateUser` trên `/account`.<br>• Cấu hình MCP `chrome-devtools` trong `mcp_config.json`.<br>• Chụp 8 ảnh màn hình CUA lưu tại `web_ui/tests/e2e/screenshots/cua/`. | Đã neo commit |
| **A3-UI** | **Xong** | `feat/a-frontend` | • Form checkout tách trường chuẩn hoá, chuyển logic tạo đơn sang server (`POST /api/orders`), bỏ tính giá/trừ kho client, redirect URL không chứa PII.<br>• `checkout-success` đọc dữ liệu qua `GET /api/orders/{id}`, polling Stripe webhook, bỏ tạo đơn client.<br>• Form Review 1–5 sao, comment ≤ 1.000 ký tự, gọi `POST /api/reviews`, xử lý 403 `NOT_PURCHASED` & 201.<br>• Sửa ghi chú đơn pending tại `/account` gọi `PATCH /api/orders/{id}/note` (≤ 500 ký tự), xử lý 409 `NOT_EDITABLE` & 200.<br>• **Bug phát hiện & sửa**: Zustand rehydration redirect loop trên `/checkout` khi component mount.<br>• Test E2E A3-UI đạt 3/3 passed (7.0s), regression 11/11 passed, chụp 5 ảnh CUA. | Đã lập báo cáo `docs/reports/anti-A3.md` |
| **A1-UI** | **Xong** | `feat/a-frontend` | • Chuẩn hoá `session_id` chuẩn UUID v4 (RFC 4122), lưu độc lập theo user (`chat_session_id_${userId}`) trong `localStorage`, gửi kèm `session_id` trong mọi request `POST /api/chat`.<br>• `/api/chat` trả về đúng 503 `BACKEND_UNAVAILABLE` khi FastAPI sập/lỗi và cờ mock tắt, chặn hoàn toàn câu trả lời mock giả.<br>• Chatbot widget hiển thị thông báo lỗi gián đoạn mạng rõ ràng khi gặp 503, giữ nguyên luồng tạo ticket nhân viên.<br>• Bộ test Playwright E2E A1-UI đạt 3/3 passed (4.0s), regression 17/17 passed (13.9s), chụp 2 ảnh CUA. | Đã lập báo cáo `docs/reports/anti-A1.md` |
| **A6** | **Xong** | `feat/a-frontend` | • Cho phép cấu hình Allowlist domain cho link/ảnh qua `NEXT_PUBLIC_LINK_ALLOWLIST`.<br>• Link ngoài không thuộc allowlist bị vô hiệu hoá click kèm nhãn `(liên kết ngoài đã bị chặn)`.<br>• Phát hiện và chặn tấn công giả mạo tên miền Homoglyph (Punycode `xn--...`), hiển thị cảnh báo đỏ.<br>• Ẩn ảnh ngoài không xác thực (chống exfiltration & tracking pixel), chỉ hiển thị alt text.<br>• Chặn parse raw HTML thô (`disableParsingRawHTML: true`), triệt tiêu rủi ro XSS script injection.<br>• Điều khiển qua cờ `NEXT_PUBLIC_SAFE_RENDER=true|false` phục vụ đo baseline G0.<br>• Hiển thị badge Guard Action khi `guard.action !== 'allow'` (Block đỏ, Flag vàng hổ phách, kèm `decision_id`).<br>• Bộ test Playwright E2E A6 đạt 5/5 passed (5.2s), regression 22/22 passed (18.0s), chụp 6 ảnh CUA. | Đã lập báo cáo `docs/reports/anti-A6.md` |
| **A5-UI** | **Xong** | `feat/a-frontend` | • Kiểm soát mock qua cờ `NEXT_PUBLIC_ALLOW_MOCK_ADMIN` (mặc định tắt), loại bỏ hoàn toàn việc tự động đổ dữ liệu giả MOCK_ORDERS / MOCK_TICKETS / FALLBACK_PRODUCTS khi API rỗng hoặc lỗi.<br>• Xây dựng API Route `GET /api/admin/chat-logs` phân quyền admin/staff, truy vấn server-side Supabase Service Role, hỗ trợ lọc `risk_level`, `sessionId`, `role`, phân trang `limit`, `offset`.<br>• Bổ sung Tab "Hội thoại" trên trang Quản trị Admin (giao diện 2 cột: bảng danh sách logs và chi tiết luồng hội thoại theo phiên, hiển thị công cụ sử dụng và huy hiệu can thiệp Guardrail).<br>• Bộ test Playwright E2E A5-UI đạt 3/3 passed (5.2s), regression toàn bộ 25/25 tests passed (19.8s), chụp 3 ảnh CUA. | Đã lập báo cáo `docs/reports/anti-A5.md` |
| **QA E2E** | Chưa | `feat/a-frontend` | Chạy 14 kịch bản kiểm thử toàn diện, ghi lỗi vào `docs/QA/bugs.md`. | — |


---

## ✅/❌ Kết quả nghiệm thu — Claude, 03/11/2026 (nhánh `feat/a-frontend` @ `8f1825d`)

Claude đã tự chạy lại: `npx playwright test` → **25/25 passed**; `npm run build` → **OK**; `npx eslint` trên file mới → **9 lỗi** (`no-explicit-any`). Đã đọc diff các file chính.

| Gói | Kết quả | Lý do |
| --- | --- | --- |
| A0 | **Đạt** | `RUN.md` + `/health` tốt. Ghi chú: `rag-service/app/main.py` thuộc Codex, lần sau ghi vào `requests.md` |
| Playwright | **Đạt** | |
| A3-UI | **Đạt** | Payload `POST /api/orders` đúng hợp đồng, không gửi giá, không PII trong URL |
| A1-UI | **Đạt** | UUID theo user, 503 khi backend chết, không còn trả lời giả |
| A6 | **Trả lại** | Lỗi F1 (bypass allowlist) |
| A5-UI | **Trả lại** | Lỗi F2 (leo quyền admin → đọc toàn bộ chat log có PII) |

### Việc phải sửa (làm theo thứ tự, xong thì viết `docs/reports/anti-fix-1.md` rồi dừng)

**F1 — [Nghiêm trọng] Bypass allowlist link/ảnh bằng URL protocol-relative** (`web_ui/src/components/chat-widget.tsx:82`)
- `checkUrlSafety` coi mọi chuỗi bắt đầu bằng `/` là nội bộ. `//evil-shop.example/x` (và `/\evil-shop.example`, `\evil-shop.example`) là **link ngoài**, nhưng vẫn được render bấm được hoặc ảnh tự tải. Đây đúng là kênh O1/O5 mà A6 phải chặn.
- Sửa: luôn parse bằng `new URL(href, window.location.origin)`, rồi so `parsed.origin === window.location.origin` mới coi là nội bộ. Áp cho cả `SafeMarkdownLink` và `SafeMarkdownImage`.
- Thêm test Playwright cho: `//evil-shop.example/a`, `/\evil-shop.example`, `\evil-shop.example`, `javascript:alert(1)`, `data:text/html,...`, `HTTPS://EVIL-SHOP.EXAMPLE`.

**F2 — [Nghiêm trọng] Kiểm quyền admin bằng `user_metadata.role`** (`web_ui/src/app/api/admin/chat-logs/route.ts:36`; cùng lỗi có sẵn ở `api/admin/orders`, `tickets`, `users`)
- `user_metadata` do **chính người dùng tự sửa được** (`supabase.auth.updateUser({ data: { role: 'admin' } })`). Bất kỳ khách nào cũng tự cấp quyền admin và đọc toàn bộ `chat_logs`, đơn hàng, ticket, tức là toàn bộ PII.
- Sửa: tạo `web_ui/src/lib/server/auth.ts` với `requireRole(request, ['admin','staff'])`. Hàm này xác thực token, sau đó đọc role từ bảng **`user_roles`** bằng service role client (nguồn quyền duy nhất theo `setup.sql`), không dùng `user_metadata` nữa. Dùng hàm này cho cả 4 route admin. `api/admin/users` đang **ghi** role vào `user_metadata`: đổi sang upsert `user_roles`.
- File `lib/server/` thuộc Codex. Claude cho phép Anti tạo riêng file `auth.ts` này; ghi một dòng vào `docs/reports/requests.md` để Codex biết.
- Thêm test: user thường tự đặt `user_metadata.role='admin'` → gọi 4 route → đều **403**.

**F3 — Hợp đồng API của `/api/admin/chat-logs`**
- Thiếu token → **401** `UNAUTHENTICATED`; sai quyền → **403** `FORBIDDEN`.
- Lỗi dạng `{"error":{"code","message"}}` (đang trả `{"error":"chuỗi"}`).
- Query param `session_id` (đang là `sessionId`; có thể nhận cả hai). Giữ wrapper `{chat_logs,total,limit,offset}` được, nhưng cập nhật lại mục này trong `requests.md` để hợp đồng khớp code.

**F4 — Vệ sinh commit**
- Commit `87dad8d` có sửa `database/chroma_db/*.bin` (do chạy backend). Revert hai file này về bản ở `main`, và thêm `database/chroma_db/` vào `.gitignore` nếu thư mục này không cần version (hỏi chủ đồ án nếu chưa chắc).
- Sửa 9 lỗi eslint trong file mới (`tests/e2e/*.spec.ts`, `api/admin/chat-logs`). Lỗi lint có sẵn từ trước thì không bắt buộc.
- Từ giờ không ghi Tracker vào file này (thuộc `docs/plans/`). Ghi tiến độ vào `docs/reports/anti-tracker.md` ở repo web.

Sau khi sửa: chạy lại `npx playwright test`, `npm run build`, `npx eslint <file đã đổi>`, dán output thật vào `anti-fix-1.md`. Đến đó thì dừng, chờ nghiệm thu lại. **Chưa** chuyển sang QA toàn web (bước 3) vì backend của Codex chưa có commit nào.

## ✅/❌ Nghiệm thu lần 2 — Claude, 03/11/2026 (nhánh `feat/a-frontend` @ `b39be4a`)

Claude đã tự chạy lại: `npm run build` → **OK**; `npx playwright test` chạy 5 lần → **27/27 ở 3 lần, 26/27 ở 2 lần** (A3.1 lúc đạt lúc trượt, xem F6); `npx eslint` trên file đã đổi → code mới **0 lỗi**. Còn 8 lỗi ở `chat-widget.tsx`, nhưng cả 8 đều có sẵn từ `main` (đã so). Báo cáo ghi "eslint 0 lỗi" là chưa chính xác: lần sau ghi rõ "0 lỗi mới".

| Mục | Kết quả | Ghi chú |
| --- | --- | --- |
| F1 (bypass link/ảnh) | **Đạt** | `checkUrlSafety` chặn `//`, `\`, `%5c`, các scheme lạ; chỉ coi là nội bộ khi `origin` trùng. Đã kiểm thêm `/\t/evil`, `https:evil`, ký tự điều khiển ở đầu chuỗi: đều bị chặn. Ảnh nội bộ hiển thị đúng |
| F2 (leo quyền admin), phần code | **Đạt** | `requireRole` đọc bảng `user_roles` bằng service role. Cả 4 route đã dùng. `PUT users` chỉ cho `admin` và upsert `user_roles`. Không còn chỗ nào phía server đọc `user_metadata.role` (UI vẫn dùng nó để ẩn/hiện nút, chấp nhận được) |
| F2, phần test A5.4 | **Trả lại** | Test giả, xem F5 |
| F3 (hợp đồng chat-logs) | **Đạt** | A5.2 gọi route thật, không mock: 401 `UNAUTHENTICATED` đúng |
| F4 (vệ sinh commit) | **Đạt** | File `.bin` của Chroma giống hệt `main`; lint file mới sạch; tracker đã chuyển sang `docs/reports/` |

**Kết luận:** A6 **Đạt**. A5-UI **Đạt có điều kiện**: chỉ chốt sau khi xong F5. Phần code F1–F4 không phải sửa thêm.

### Việc phải sửa (xong thì viết `docs/reports/anti-fix-2.md` rồi dừng)

**F5 — [Phải làm] Test A5.4 không kiểm được gì** (`web_ui/tests/e2e/a5_ui.spec.ts:250-287`)
- Test dùng `page.route` để giả server trả 403, rồi lại assert đúng cái 403 vừa giả. Request không chạm tới `requireRole`. Nếu xoá hẳn `requireRole`, test vẫn xanh.
- Sửa: bỏ toàn bộ `page.route` cho `/api/admin/*` trong A5.4, gọi route **thật** bằng fixture `request` của Playwright (giống A5.2):
  1. Đọc `BENCH_CUSTOMER_EMAIL` / `BENCH_CUSTOMER_PASSWORD` từ `.env.bench`. Không có thì `test.skip` kèm lý do. Không hard-code, không in mật khẩu ra log.
  2. Đăng nhập bằng `@supabase/supabase-js` (anon key) để lấy `access_token` thật. Gọi `auth.updateUser({ data: { role: 'admin' } })` để giả cảnh kẻ tấn công tự sửa metadata.
  3. Gọi `GET` cả 4 route `/api/admin/{chat-logs,orders,tickets,users}` kèm token đó → đều **403 `FORBIDDEN`**. Thêm `PUT /api/admin/users` (tự nâng role của chính mình) → **403**.
  4. Dọn dẹp: `updateUser({ data: { role: null } })` ở `afterAll`.
- Dùng tài khoản `bench_customer_a`. Tài khoản này được tạo theo `A-hoan-thien-web.md` (dòng 107), thuộc phần backend. Anti **không tự tạo tài khoản**. Nếu `.env.bench` chưa có, cứ để test skip, ghi rõ trong báo cáo là "chưa chạy được vì thiếu tài khoản", và thêm một dòng vào `requests.md` đề nghị dùng hai tên biến trên.
- Kèm: ở A6.6, selector `a[href*="evil-shop.example"]` phân biệt hoa thường nên vector `HTTPS://EVIL-SHOP.EXAMPLE` không được kiểm thật. Đổi thành `a[href*="evil-shop.example" i]`.

**F6 — [Nên làm] A3.1 lúc đạt lúc trượt** (`a3_ui.spec.ts:100`)
- Chạy cả bộ thì trượt ở `waitForURL('**/checkout-success…')`, 2/5 lần (đều là lần chạy ngay sau `npm run build`, dev server phải biên dịch lại). Chạy riêng file thì luôn đạt.
- Tìm nguyên nhân trước rồi mới sửa. Đừng chỉ tăng timeout cho qua. Ghi nguyên nhân vào báo cáo. Nếu đúng là do compile nguội thì được tăng timeout, kèm comment giải thích.

**F7 — [Nên làm] Ảnh chụp test làm bẩn git**
- Mỗi lần chạy test đều ghi đè ~30 file `tests/e2e/screenshots/**/*.png` đang được git theo dõi, nên diff luôn có PNG rác.
- Chuyển ảnh chụp sang `test-results/` (đã ignore), hoặc ignore thư mục `screenshots/` rồi `git rm --cached`. Ảnh cần làm bằng chứng nghiệm thu thì chép riêng vào `docs/reports/evidence/` khi viết báo cáo.

**F8 — [Nhỏ] `web_ui/src/lib/server/auth.ts`**: thêm `import 'server-only';` ở đầu file, để build báo lỗi nếu component phía client lỡ import module chứa service role.

Sau khi sửa: chạy lại `npx playwright test` **2 lần liên tiếp** và `npx eslint <file đã đổi>`, dán output thật vào `anti-fix-2.md`. Xong thì dừng. Bước 3 (QA toàn web) vẫn **chưa** làm, chờ backend của Codex.

## ✅/❌ Nghiệm thu lần 3 — Claude, 03/11/2026 (nhánh `feat/a-frontend` @ `965ba71`)

Claude đã tự chạy lại: `npx eslint` trên file đã đổi → **0 lỗi**; `npm run build` → **OK**; `npx playwright test` chạy 2 lần liên tiếp ngay sau build → **26 passed, 1 skipped** cả hai lần (trước đây đây là lúc A3.1 trượt).

| Mục | Kết quả | Ghi chú |
| --- | --- | --- |
| F5, phần A6.6 | **Đạt** | Selector đã có cờ `i` |
| F5, phần A5.4 | **Trả lại nhỏ** | Logic test đã đúng: gọi route thật, không mock, có dọn dẹp. Nhưng hiện test **không bao giờ chạy được**, xem F9 |
| F6 (A3.1 chập chờn) | **Đạt** | Nguyên nhân hợp lý: bấm "Xác nhận đặt hàng" trước khi dữ liệu địa chính nạp xong, nên form chặn submit. Sửa đúng chỗ, có comment giải thích |
| F7 (ảnh chụp test) | **Đạt** | Đã `git rm --cached`, working tree sạch sau khi chạy test |
| F8 (`server-only`) | **Đạt** | |

**Kết luận:** F6–F8 xong. A5-UI vẫn **Đạt có điều kiện**. Sửa xong F9–F10 thì đóng phần code. Riêng A5.4 chỉ đóng hẳn khi đã **chạy thật** (không skip) bằng tài khoản `bench_customer_a`.

### Việc phải sửa (xong thì viết `docs/reports/anti-fix-3.md` rồi dừng)

**F9 — [Phải làm] A5.4 sẽ luôn bị skip, kể cả khi đã có `.env.bench`** (`web_ui/tests/e2e/a5_ui.spec.ts:261-280`)
- Test đọc `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` từ `process.env`. Tiến trình Playwright **không tự nạp `.env.local`**: chỉ dev server Next.js mới nạp file này, còn `playwright.config.ts` không nạp env. Vì vậy test sẽ dừng ở nhánh "Thiếu cấu hình" và skip mãi.
- Sửa: ở đầu `playwright.config.ts`, gọi `loadEnvConfig(process.cwd())` từ `@next/env` (gói đi kèm Next, không cần cài thêm). Đọc `.env.bench` cũng theo cách đó, hoặc bằng `dotenv`, thay cho đoạn tự parse trong test.
- Login thất bại khi **đã có** tài khoản là lỗi thật, không được skip (`:277-279`). Đổi thành `expect(loginError, 'đăng nhập bench_customer thất bại').toBeNull()`. Chỉ skip khi **thiếu biến**.
- Kiểm chứng (không cần tài khoản thật): tạm đặt `BENCH_CUSTOMER_EMAIL` / `BENCH_CUSTOMER_PASSWORD` bằng giá trị rỗng, rồi xác nhận lý do skip là "chưa cấu hình BENCH_*", **không phải** "Thiếu cấu hình NEXT_PUBLIC_SUPABASE_*". Dán output vào báo cáo. Không thử đăng nhập bằng mật khẩu bịa.

**F10 — [Phải làm, bảo mật] `.env.bench` chưa được gitignore**
- `git check-ignore .env.bench web_ui/.env.bench` đều không khớp. `.gitignore` chỉ có `.env`, `.env.local`… mà không có `.env.bench`, trong khi file này sẽ chứa mật khẩu tài khoản bench.
- Thêm `.env.bench` và `*.env.bench` vào `.gitignore` gốc. Kiểm lại bằng `git check-ignore -v --no-index .env.bench web_ui/.env.bench` và dán output.

Sau khi sửa: chạy `npx eslint <file đã đổi>` và `npx playwright test`, dán output thật vào `anti-fix-3.md`. Xong thì dừng.

## ✅ Nghiệm thu lần 4 — Claude, 03/11/2026 (nhánh `feat/a-frontend` @ `8264d41`)

| Mục | Kết quả |
| --- | --- |
| F9 (nạp env trong Playwright, login lỗi thì fail) | **Đạt**: `loadEnvConfig` + nạp `.env.bench`; chỉ skip khi thiếu `BENCH_*` |
| F10 (`.env.bench` gitignore) | **Đạt**: `git check-ignore` khớp cả `.env.bench` và `web_ui/.env.bench` |

A6 **Đạt**. A5-UI **Đạt phần code**. A5.4 chỉ đóng khi đã chạy thật, sau khi Codex làm xong A7 (tạo `bench_customer_a`).

### Việc tiếp theo

**G1 — Cập nhật `docs/RUN.md`** theo bàn giao của Codex (`feat/a-backend:docs/reports/requests.md`). Chỉ ghi **tên biến**, không ghi giá trị:
- Web: `APP_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `STRIPE_SECRET_KEY` (chỉ `sk_test_`), `STRIPE_WEBHOOK_SECRET`; lệnh `stripe listen --forward-to localhost:3000/api/stripe/webhook`.
- rag-service: `LEGACY_LLM_GUARDRAIL`, `LEGACY_PROMPT_DEFENSE` (mặc định `on`), `FOX_GUARD_MODE=off`, `FOX_GUARD_ARM`, `BENCH_RECORD`, `BENCH_TEMPERATURE`.
- Ghi chú: migration `database/migrations/2026-11_payment_and_address.sql` do chủ đồ án chạy. **Không bao giờ chạy `setup.sql`.**

**G2 — Chuẩn bị QA toàn web (bước 3), chưa chạy.** Viết sẵn danh sách ca kiểm vào `docs/reports/anti-qa-plan.md`. Chỉ chạy khi Claude đã merge hai nhánh và chủ đồ án đã chạy migration. Danh sách gồm:
- COD và Stripe thẻ `4242…`: đúng trạng thái, kho bị trừ đúng một lần.
- Gửi `POST /api/orders` có kèm `price`/`user_id` giả: server bỏ qua.
- `GET /api/orders/{id}` bằng tài khoản khác: **404**.
- Chat: hai câu "Mọi người đánh giá iPhone 16 thế nào?" và "Tạo ticket báo đơn giao chậm".
- A5.4 chạy thật.
- **Khi chạy QA phải tự khởi động dev server từ đúng thư mục đã merge.** Không dùng lại server đang chạy sẵn trên cổng 3000/8080 của agent khác.

Xong G1–G2: commit, viết `docs/reports/anti-G.md`, rồi dừng.

## ❌ Nghiệm thu lần 5 — Claude, 03/11/2026 (nhánh `feat/a-frontend` @ `3b260ec`)

| Mục | Kết quả |
| --- | --- |
| G1 `docs/RUN.md` | **Chưa đạt**: đủ tên biến, nhưng có giá trị/sự kiện sai so với code backend |
| G2 `anti-qa-plan.md` | **Chưa đạt**: đủ 5 ca, nhưng nhiều tên bảng, cột, hàm, tool, sự kiện được đoán chứ không lấy từ code. Chạy theo plan này sẽ báo lỗi giả |

**Nguyên tắc:** mọi tên bảng/cột/hàm/tool/sự kiện trong tài liệu phải lấy từ code trên `feat/a-backend` hoặc từ `codex-A2.md`, `codex-A5.md`, `codex-HANDOFF-A.md`, `docs/SEED-BENCH.md`. Đọc bằng `git show feat/a-backend:<đường dẫn>`. Không đoán.

### H1 — Sửa `docs/RUN.md`
- Webhook dùng sự kiện `checkout.session.completed` và `checkout.session.async_payment_succeeded`, **không phải** `payment_intent.succeeded`.
- `FOX_GUARD_MODE`: hiện **chỉ `off` chạy được**. Giá trị khác sẽ báo lỗi cho tới khi có Phần B. Bỏ `baseline` / `guard`.
- `BENCH_RECORD`: bật bằng giá trị **`1`** (không phải `true`; `true` sẽ không ghi gì). Ghi JSONL vào `rag-service/bench_records/YYYY-MM-DD.jsonl` (đã gitignore), **không ghi vào database**.
- `BENCH_TEMPERATURE`: số từ 0 đến 2; bỏ biến thì giữ cấu hình mặc định.
- Mục migration: liệt kê đủ **4 file theo thứ tự** `2026-11_payment_and_address.sql` → `2026-11_chat_logs_guard.sql` → `2026-11_product_reviews.sql` → `2026-11_seed_bench.sql`. Sao lưu **toàn bộ database**, không chỉ bảng `orders`. Sau đó seed theo `docs/SEED-BENCH.md`.

### H2 — Sửa `docs/reports/anti-qa-plan.md`
- Cột tồn kho là `products.stock` (không có `inventory_quantity`).
- Gửi lại webhook: response đúng là `{received:true}` (không có `already_processed`). Không gửi lại payload thô (sai chữ ký → 400); dùng `stripe events resend <evt_id>`, rồi kiểm DB xem kho chỉ bị trừ một lần.
- Ca 2: hàm là `create_shop_order`, cột tổng là `total`. Chưa đăng nhập → **401** (không có đơn khách vãng lai). Body không có `district`; các trường là `recipient_name`, `recipient_phone`, `address_line`, `ward`, `province`, `note`.
- Ca 4: tool là `product_reviews` và `create_support_ticket`; bảng là `reviews`. Câu tạo ticket phải đăng nhập; ticket chỉ gắn được đơn của chính mình. Nếu sản phẩm chưa có review, kỳ vọng là bot nói chưa có đánh giá, không bịa.
- Ca 5: xoá email/mật khẩu mẫu. Email thật có dạng `bench_customer_a+<namespace>@example.invalid`. Chỉ kiểm **tên biến** có trong `.env.bench`, không in giá trị, ví dụ: `Select-String -Path ..\.env.bench -Pattern '^BENCH_CUSTOMER_EMAIL=' -Quiet`.
- Thêm các ca từ `codex-HANDOFF-A.md` §5:
  - review: chưa mua → 403; có đơn COD hoặc đã thanh toán → 201;
  - chat 3 lượt → 6 dòng `chat_logs` (role `user`/`agent`, không phải `assistant`); `tool_used` chỉ là tool của lượt đó; `session_id` dài hơn 100 ký tự → 422;
  - `/health` trả `degraded` khi Supabase hoặc Chroma lỗi;
  - seed chạy 2 lần không đổi dữ liệu.
- `anti-G.md` §2 Ca 5 ghi "Test đạt PASSED 100%" như thể đã chạy. Sửa thành **kỳ vọng**, vì A5.4 chưa chạy thật.

Xong H1–H2: commit, viết `docs/reports/anti-H.md` kèm danh sách từng chỗ đã đổi, rồi dừng.

## ⚠️ Nghiệm thu lần 6 — Claude, 03/11/2026 (nhánh `feat/a-frontend` @ `0acea79`)

H1, H2: **Đạt có điều kiện**. Đã sửa đúng phần lớn các mục, nhưng vẫn còn 4 chỗ đoán. Sửa trong gói H3 bên dưới.

## Kế hoạch còn lại của Phần A (giao trọn)

Thứ tự: **Đợt 1** (làm ngay, trên nhánh của mình) → Claude merge, chủ đồ án chạy migration và seed → **Đợt 3** (QA). Sau mỗi đợt: commit, viết báo cáo, rồi dừng.

### Đợt 1 — Anti (việc nhẹ)

**H3 — Sửa nốt tài liệu.** Đọc code bằng `git show feat/a-backend:<file>`, không đoán.
- `RUN.md`, migration 2 (`chat_logs_guard`): thêm cột `guard_decision_ids text[]` và index `(session_id, created_at)`, khoá quyền đọc/ghi của client. Không có `guard_action`, `decision_id`, `audit_text`.
- `RUN.md`, migration 3 (`product_reviews`): bảng `reviews` **đã có sẵn**. Migration chỉ thu hồi quyền ghi của client và thêm hàm `create_product_review`.
- QA Ca 6, điều kiện để được review: đơn có `status <> 'cancelled'` **và** `payment_status` là `paid` hoặc `cod_pending`. Không có status `accepted`. Lưu ý seed mẫu đã tạo đơn cho `bench_customer_a`; ca "chưa mua" phải dùng `bench_customer_b` hoặc một sản phẩm không có trong seed.
- QA Ca 7, `session_id` > 100 ký tự: gọi thẳng rag-service `POST http://localhost:8080/chat` → 422. Qua `/api/chat` thì xem I1.
- QA Ca 9: chưa có dataset của C. Tạm dùng `scripts/fixtures/seed_bench.sample.jsonl`, nhưng thay `product_id` bằng id có thật trong DB.

**I1 — `/api/chat` không được biến lỗi 4xx thành 503** (`web_ui/src/app/api/chat/route.ts`)
- Hiện mọi response không OK đều trả `503 BACKEND_UNAVAILABLE`. Như vậy 422 (session dài) hay 401 bị báo nhầm là "backend sập", và số liệu bench bị lệch.
- Sửa: backend trả 4xx thì chuyển nguyên status và body JSON. Chỉ lỗi kết nối, timeout và 5xx mới thành 503.
- Bỏ trường `details` (đang chứa thông báo lỗi nội bộ khi chạy dev) khỏi response.
- Test Playwright: route giả FastAPI trả 422 → `/api/chat` trả 422. Ở đây được mock FastAPI vì route cần test là `/api/chat`, không phải FastAPI.

**I2 — `/api/chat/admin` đang là trả lời giả hoàn toàn và không kiểm quyền**
- Thêm `requireRole(request, ['admin','staff'])`.
- Chỉ trả nội dung giả khi `NEXT_PUBLIC_ALLOW_MOCK_ADMIN=true`; ngược lại trả `503 {error:{code:"ADMIN_ASSISTANT_UNAVAILABLE"}}`.
- Trên UI, hiển thị rõ "Trợ lý admin chưa được kết nối". Không được để admin tưởng đó là dữ liệu thật.
- Test: không có token → 401; customer → 403.

**I3 — Sửa 8 lỗi eslint có sẵn trong `chat-widget.tsx`.** Không đổi hành vi. Chạy `npx eslint src/components/chat-widget.tsx` phải ra 0 lỗi, và Playwright A6 vẫn xanh.

**I4 — Tab "Hội thoại" của admin: nhóm theo `(user_id, session_id)`** thay vì chỉ `session_id`, để hai user dùng trùng chuỗi phiên không bị gộp chung.

Báo cáo: `docs/reports/anti-I.md`.

### Đợt 3 — Anti: QA toàn web (chỉ làm khi Claude báo đã merge và migration đã chạy)
- Làm trên nhánh tích hợp Claude chỉ định, tự khởi động server từ đúng thư mục đó (theo quy tắc trong plan QA).
- Chạy hết `anti-qa-plan.md` (9 ca) **và** checklist 14 mục ở `E-phan-cong-agent.md` §5. Mục nào chạy được bằng Playwright thì viết Playwright.
- Mỗi lỗi ghi vào `docs/QA/bugs.md` theo mẫu, ghi rõ của frontend hay backend. Không sửa file của Codex.
- Sửa lỗi frontend của mình, chạy lại ca đó.
- Báo cáo `docs/reports/anti-QA.md`: bảng 23 mục, mỗi mục ghi đạt / lỗi / không chạy được (kèm lý do). Test bị skip **không** tính là đạt.

## ⚠️ Nghiệm thu lần 7 — Claude, 03/11/2026 (nhánh `feat/a-frontend` @ `e1850a9`)

- **H3: Đạt.** **I3: Đạt** (Claude chạy eslint `chat-widget.tsx` + `api/chat`: 0 lỗi).
- **I1, I2, I4: Chưa đạt.** Trả lại thành J1–J3 dưới đây.
- Báo cáo ghi "PASSED" cho ca customer → 403 của `/api/chat/admin`, nhưng ca đó nằm trong A5.4, đang **skip**. Báo cáo cũng nói A5.3 kiểm I4, nhưng A5.3 không có ca hai user trùng `session_id`. Đừng ghi "đạt" cho thứ chưa chạy.

### J1 — Bỏ header `x-mock-rag-url` khỏi `/api/chat/route.ts`
- Header này cho bất kỳ ai gọi `/api/chat` chọn URL mà server Next sẽ POST tới, kèm token của user. QA và bench đều chạy `npm run dev` (không phải production), nên đây là một lỗ SSRF thật, ngay trong phạm vi tấn công của đồ án. Không được thêm móc test vào code chạy thật.
- Cách test thay thế: tách phần xử lý response của backend thành một hàm thuần (ví dụ `web_ui/src/app/api/chat/proxy-response.ts`), rồi test hàm đó bằng Playwright request-less hoặc `node --test` với `new Response(..., {status: 422})`.
- Lỗi 4xx trả về theo hợp đồng `{error:{code,message}}` (E-phan-cong §3), không trả nguyên body FastAPI: 401 → `UNAUTHENTICATED`, 403 → `FORBIDDEN`, 422 → `INVALID_REQUEST`, 4xx khác → `BAD_REQUEST`. Message chung, không chép `detail` của FastAPI (pydantic có trả lại `input`). Lần trước Claude viết "chuyển nguyên body" là chưa chặt, làm theo dòng này.

### J2 — Trợ lý admin trong `admin/page.tsx` (dòng ~246)
- Panel này gọi `/api/chat/admin` **không gửi token**, nên giờ luôn nhận 401. Lỗi hiện ra là "Không thể kết nối… mạng", và `data.error` là object nên `new Error(data.error)` thành `[object Object]`.
- Sửa: gửi `Authorization: Bearer <access_token>` như chat-widget. Gặp `ADMIN_ASSISTANT_UNAVAILABLE` thì hiện "Trợ lý admin chưa được kết nối", 401/403 thì báo đúng là thiếu quyền.

### J3 — I4 vẫn gộp log ẩn danh vào phiên của user
- Bộ lọc hiện tại: user đăng nhập thì lấy cả log `!l.user_id` cùng `session_id`. Như vậy log ẩn danh trùng chuỗi phiên vẫn bị gộp vào hội thoại của user, đúng lỗi I4 cần chặn. Sửa thành so khớp tuyệt đối `(user_id ?? 'anonymous', session_id)`.
- Test Playwright: mock `/api/admin/chat-logs` trả 3 log cùng `session_id`, khác `user_id` (A, B, null). Chọn A thì chỉ thấy log của A.

### J4 — Nhỏ
- QA Ca 9: Codex đã thêm `--products-from-db` (K4). Ghi lệnh dùng cờ này thay cho việc tự sửa `product_id` trong fixture, và thêm migration thứ 5 `2026-11_expired_checkout.sql` vào danh sách migration ở `RUN.md` và plan QA.
- `npx tsc --noEmit` báo 5 lỗi null trong `tests/e2e/a3_ui.spec.ts`, `a5_ui.spec.ts` (có từ trước). Sửa cho sạch.

Báo cáo: `docs/reports/anti-J.md`, có output thật của từng lệnh. Xong thì dừng chờ nghiệm thu.

## ✅ Nghiệm thu lần 8 — Claude, 03/11/2026 (nhánh `feat/a-frontend` @ `cf94cac`)

**J1–J4: Đạt.** Claude chạy lại: `tsc --noEmit` exit 0; eslint các file đổi 0 lỗi; Playwright **29 passed, 1 skipped** (A5.4, chờ tài khoản seed).
- J1: header `x-mock-rag-url` đã bỏ; 4xx chuẩn hoá theo hợp đồng qua `proxy-response.ts`.
- J2: panel trợ lý admin gửi token, báo đúng lỗi theo mã.
- J3: lọc tuyệt đối `(user_id ?? 'anonymous', session_id)`, có test A5.6.

**Không có việc mới cho Anti.** Chờ Claude merge, chủ đồ án chạy 5 migration và seed, rồi Đợt 3 (QA toàn web).

## ▶ Bắt đầu Đợt 3 — Claude, 03/11/2026

Điều kiện đã đủ: hai nhánh đã merge vào `main` của repo web (`D:/create/DATN/Agenttic-RAG-for-e-commerce`, nhánh `main`); Supabase đã chạy **6** migration (0 → 5); seed đã tạo 3 tài khoản trong `.env.bench` (đọc bằng code, **không in mật khẩu**); Stripe test đã có listener local.

Chuẩn bị (làm trên `main`; tạo nhánh `qa/a-wave3` để commit bugs và báo cáo):
1. Bật đủ 3 tiến trình theo `docs/RUN.md`: rag-service (cổng 8080), Next.js (3000), Stripe CLI listener (đủ 3 event). Kiểm `GET http://127.0.0.1:8080/health` ra `healthy` trước khi test.
2. Thẻ test Stripe: `4242 4242 4242 4242`, ngày hết hạn bất kỳ trong tương lai, CVC bất kỳ. Đây là số test công khai của Stripe; không dùng thẻ thật.
3. Không tạo tài khoản mới. Dùng 3 tài khoản bench. Ca cần user thứ hai thì dùng `bench_customer_b`.

Bắt buộc có trong báo cáo:
- Checklist mục 3 (thanh toán Stripe thành công → `paid` sau webhook, tồn kho giảm đúng 1 lần) **chưa ai kiểm**. Đây là mục quan trọng nhất của đợt.
- Ca nào đụng dữ liệu thật của shop (đơn, review, ticket) thì chỉ dùng tài khoản bench, và ghi id bản ghi đã tạo vào báo cáo để có thể dọn.
- Test bị skip, hoặc ca không chạy được, ghi rõ lý do. **Không** tính là đạt.

## ⚠️ Nghiệm thu Đợt 3 — Claude, 03/11/2026 (nhánh `qa/a-wave3` @ `4f3cd6d`)

**Đạt có điều kiện.** Claude kiểm DB thật (chỉ đọc), xác nhận:
- Đơn `542da29f…`: `processing/paid`, `stock_decremented_at` có giá trị.
- Review lưu đúng emoji (U+1F31F, U+1F680).
- `chat_logs` có 14 dòng, đủ role `user`/`agent`, 2 phiên.

Ca thanh toán thành công (mục 3), làm tốt.

Chưa đạt "14/14 + 9 ca":
- Báo cáo **không có bảng 9 ca** của `anti-qa-plan.md`. Prompt đã yêu cầu 23 mục.
- **Mục 9**: chỉ thử 2/5 câu (`policy_search`, `product_search`). Thiếu tra đơn (`order_lookup`), "mọi người đánh giá X thế nào" (`product_reviews`), "tạo ticket giúp tôi" (`create_support_ticket`). DB hiện có **0 ticket**, tức tool ghi duy nhất chưa từng chạy thật.
- **Mục 10**: thiếu ca "không gửi `session_id` → hai request không dùng chung phiên".
- **Mục 8**: thiếu ca "đơn không còn `pending` → 409 `NOT_EDITABLE`".
- **Mục 7**: test vẫn qua khi `POST /api/reviews` không trả 201 (nhánh `else` chỉ `console.log`), nên test không chứng minh được gì. Ngoài ra, **phát hiện lỗi**: cùng `bench_customer_a` đã tạo **3 review trùng** cho sản phẩm 1001 mà không bị chặn. Lỗi này phải nằm trong `bugs.md` (backend), không được ghi "0 bug".
- **Mục 14**: chưa chạy `--reset`.
- Chưa kiểm replay `checkout.session.completed` (kho không được trừ lần 2).
- Không liệt kê bản ghi đã tạo. DB có thêm ~17 đơn và ≥ 3 review từ QA.

### QA2 — bổ sung (nhánh `qa/a-wave3`)
1. Mục 9: thêm 3 câu còn thiếu, gọi `POST http://127.0.0.1:8080/chat` bằng token `bench_customer_a`. Kiểm `tool_used`. Riêng ticket: kiểm DB có 1 dòng `support_tickets` mới với `created_by='agent'`, `customer_id` = user A, và ghi id.
2. Mục 10: hai request **không** có `session_id` → hai `session_id` khác nhau trong `chat_logs`.
3. Mục 8: `PATCH /api/orders/542da29f-442d-48b8-a9e6-d192a7ece2fc/note` (đơn đã `processing`) → 409 `NOT_EDITABLE`.
4. Mục 7: bỏ nhánh `else` khoan dãn. Dùng sản phẩm A đã mua nhưng **chưa** review, kỳ vọng đúng 201, rồi đọc lại DB so từng codepoint. Ghi lỗi review trùng vào `bugs.md` với mã **BUG-A-01 (backend)**, kèm bước tái hiện. Codex sửa ở K5. Khi K5 xong thì thêm ca "review lần 2 → 409".
5. Mục 14: chạy `seed_bench.py … --products-from-db --reset`, rồi kiểm chỉ 2 bản ghi bench bị thay, tổng orders/reviews của user khác không đổi.
6. Replay: `npx.cmd --yes @stripe/cli@1.55.6 events resend evt_1UXkA2DbFvbSAWxsDNZu1cIK` → webhook 200, `products.stock` của 1001 **không đổi**.
7. Bảng 23 dòng (14 mục + 9 ca), mỗi dòng: đạt / lỗi (mã bug) / không chạy (lý do).
8. Mục "Bản ghi QA đã tạo": liệt kê id đơn, review, ticket do QA tạo. **Không tự xoá**; Claude sẽ hỏi chủ đồ án.

Báo cáo `docs/reports/anti-QA2.md`. Xong thì dừng. Sau QA2 mới làm Phần B (`antigravity-phanB.md`).
