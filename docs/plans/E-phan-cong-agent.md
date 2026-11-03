# Phân công agent — Giai đoạn 1: hoàn thiện & kiểm thử web (Phần A)

> Ngày lập: 02/11/2026 · Áp dụng cho `A-hoan-thien-web.md`. Phần B/C sẽ phân công sau khi Phần A được nghiệm thu.

## 1. Phân tầng

| Tầng | Agent | Model | Vai trò ở giai đoạn 1 |
| --- | --- | --- | --- |
| 1 — Review / nghiệm thu | Claude Code | Opus 5.5 high | Không code Phần A. Đọc báo cáo + diff, chạy test, nghiệm thu theo tiêu chí; chỉ tự sửa lỗi nhỏ khi review |
| 2 — Backend & bảo mật | Codex | GPT 6.1 sol high | Phần có rủi ro cao: session, vòng tool, thanh toán + webhook, migration, API server, tool mới, cờ bench, seed |
| 3 — Frontend & kiểm thử | Antigravity | Gemini 3.88 flash high | UI, render an toàn, admin, tài liệu chạy, bộ test Playwright, QA toàn web |

Lý do: thanh toán, RLS, webhook và thay đổi agent loop sai một chỗ là thành lỗ hổng, nên giao cho model suy luận mạnh. UI và kiểm thử khối lượng lớn, ít rủi ro, giao cho model nhanh. Tầng 1 chỉ đọc kết quả nên tốn ít quota nhất.

## 2. Quyền sở hữu file (chống sửa trùng)

| Codex sở hữu | Antigravity sở hữu |
| --- | --- |
| `rag-service/**` | `web_ui/src/app/**/page.tsx`, `web_ui/src/components/**`, `web_ui/src/store/**` |
| `database/migrations/**` | `web_ui/src/app/api/chat/**`, `web_ui/src/app/api/admin/**` |
| `web_ui/src/app/api/orders/**`, `api/stripe/**`, `api/reviews/**`, `web_ui/src/lib/server/**` | `web_ui/tests/e2e/**`, `playwright.config.ts` |
| `scripts/seed_bench.py` | `docs/RUN.md`, `docs/QA/**` |

Cần sửa file của bên kia thì **ghi yêu cầu** vào `docs/reports/requests.md` thay vì sửa trực tiếp. `package.json` của `web_ui`: Antigravity sở hữu; Codex muốn thêm dependency thì ghi yêu cầu.

## 3. Hợp đồng API (cả hai làm theo ngay, không chờ nhau)

Lỗi luôn có dạng `{"error": {"code": "...", "message": "..."}}`. Xác thực bằng header `Authorization: Bearer <supabase access token>`.

| Endpoint | Request | Response |
| --- | --- | --- |
| `POST /api/orders` | `{items:[{product_id:int, quantity:int}], payment_method:"stripe"\|"cod", recipient_name, recipient_phone, address_line, ward, province, note?}` | `201 {order_id, status, payment_status, total, checkout_url?}` · lỗi: `UNAUTHENTICATED` 401, `EMPTY_CART` / `INVALID_PRODUCT` / `OUT_OF_STOCK` / `INVALID_FIELD` 400 |
| `GET /api/orders/{id}` | — | `200 {order_id, status, payment_status, payment_method, total, items, recipient_name, recipient_phone, address_line, ward, province, note, created_at}` · `404 NOT_FOUND` nếu không phải chủ |
| `PATCH /api/orders/{id}/note` | `{note}` (≤ 500 ký tự) | `200 {order_id, note}` · `409 NOT_EDITABLE` nếu đơn không còn `pending` |
| `POST /api/stripe/webhook` | Stripe gọi | nội bộ |
| `POST /api/reviews` | `{product_id, rating:1..5, comment}` (≤ 1.000 ký tự) | `201 {review_id}` · `403 NOT_PURCHASED` |
| `POST /chat` (FastAPI) | như hiện tại + `session_id` | thêm `guard: {action:"allow", decision_id:null, flags:[]}` (giá trị mặc định khi guard tắt) |
| `/api/chat` (Next) | — | `503 {error:{code:"BACKEND_UNAVAILABLE"}}` khi FastAPI lỗi và `NEXT_PUBLIC_ALLOW_MOCK_CHAT` ≠ `true` |
| `GET /api/admin/chat-logs?session_id=&limit=` | admin | `200 [{session_id, user_id, role, message, tool_used, risk_level, created_at}]` |

Cột mới của `orders` theo `A-hoan-thien-web.md` A2.1. Cho tới khi migration chạy, Antigravity mock theo hợp đồng này trong test.

## 4. Giai đoạn và thứ tự

| Bước | Ai | Việc | Đầu ra |
| --- | --- | --- | --- |
| 0 | **Bạn** (hoặc Claude) | Commit hiện trạng repo web làm baseline; tạo 2 nhánh/worktree `feat/a-backend`, `feat/a-frontend`; chuẩn bị khoá **test** Stripe + Stripe CLI; **sao lưu Supabase** | Baseline commit |
| 1 | Codex | A1 → A2 → A4 (+ cờ bench) | Báo cáo `docs/reports/codex-A1.md`… |
| 1 | Antigravity | A0 (`RUN.md`) → A3-UI (form review, sửa ghi chú, form checkout tách trường) → A6 → A5-UI (admin thật, tab hội thoại) + dựng Playwright | `docs/reports/anti-A0.md`… |
| 2 | Codex | A5-backend (ghi `chat_logs`), A7 `seed_bench.py`, sửa theo `requests.md` | |
| 2 | Antigravity | Nối UI với API thật; viết test E2E (§5) | |
| 3 | Antigravity | **QA toàn web**: chạy checklist §5 trên bản đã merge, ghi lỗi vào `docs/QA/bugs.md` | Danh sách lỗi có bước tái hiện |
| 3 | Codex | Sửa lỗi backend trong `bugs.md` | |
| 4 | **Claude** | Nghiệm thu (§6) | `docs/reports/nghiem-thu-A.md` |

Merge: `feat/a-backend` vào `main` trước, `feat/a-frontend` rebase lên rồi merge. Giữa chừng có thể merge từng gói đã nghiệm thu.

## 5. Checklist kiểm thử web (Antigravity viết thành Playwright khi được, còn lại kiểm tay)

1. Đăng ký, đăng nhập, đăng xuất; vào `/account` khi chưa đăng nhập thì bị chuyển hướng.
2. Thêm giỏ → checkout **COD** → đơn `pending` / `cod_pending`, tồn kho giảm.
3. Checkout **Stripe test** (thẻ 4242…) → về `/checkout-success?order_id=…` → trạng thái chuyển `paid` sau webhook.
4. Sửa giá trong request (DevTools / gọi API tay) → tổng tiền vẫn theo DB.
5. Mở `/checkout-success?order_id=<đơn của user khác>` → không thấy đơn.
6. URL sau thanh toán không chứa tên, SĐT, địa chỉ.
7. Gửi review khi chưa mua → bị từ chối; đã mua → thành công; comment chứa zero-width/emoji/Unicode Tags được lưu đúng từng codepoint.
8. Sửa ghi chú đơn `pending` được; đơn đã giao thì không.
9. Chat: hỏi sản phẩm, chính sách, tra đơn, "mọi người đánh giá X thế nào", "tạo ticket giúp tôi" → đúng tool.
10. Hai user khác nhau chat → không thấy lịch sử của nhau; không gửi `session_id` → không dùng chung phiên.
11. Tắt FastAPI → widget báo lỗi, **không** trả lời giả.
12. Chat-widget: link nội bộ bấm được; link ngoài/ảnh ngoài/link homoglyph bị ẩn; HTML thô không render.
13. Admin: đơn, ticket, hội thoại là dữ liệu thật (không còn MOCK khi cờ tắt).
14. `seed_bench.py` chạy 2 lần cho cùng kết quả; `--reset` chỉ xoá dữ liệu bench.

## 6. Tiêu chí nghiệm thu của Claude (mỗi gói)

- [ ] Báo cáo gói đủ 4 mục: đã làm gì / file đổi / lệnh test + output / việc còn mở.
- [ ] Tiêu chí "Xong khi" của gói trong `A-hoan-thien-web.md` đạt, có bằng chứng (output test, ảnh chụp).
- [ ] Đọc kỹ diff các file nhạy cảm: route orders/stripe/reviews, migration, RLS, `master_agent.py`, `main.py`.
- [ ] Không có khoá thật, `.env`, PII thật trong commit; không còn PII trong URL.
- [ ] Không đổi prompt hệ thống của bot ngoài phần tool mới (hoặc đã ghi vào `docs/CHANGELOG-bench.md`).
- [ ] Chạy lại test (pytest, Playwright) trên máy và đều xanh.

Kết quả: **Đạt** / **Đạt có điều kiện** (lỗi nhỏ, ghi vào `requests.md`) / **Trả lại** (kèm lý do cụ thể).

## 7. Quy tắc chung cho cả hai agent

- **Không bao giờ chạy lại `database/setup.sql`**: file này `DROP TABLE` toàn bộ. Chỉ viết migration mới dạng cộng thêm; **bạn** chạy migration lên Supabase sau khi Claude duyệt file SQL.
- Chỉ dùng khoá **test** của Stripe; không commit `.env*`.
- Không sửa `FOX-Guardrails/docs/plans/*`. Thấy plan sai thì ghi vào `docs/reports/requests.md`.
- Commit nhỏ theo gói, message dạng `feat(A2): …`.
- Hết mỗi gói: viết báo cáo, rồi dừng chờ bạn chuyển sang gói tiếp (để nghiệm thu từng bước, tránh lệch xa).
