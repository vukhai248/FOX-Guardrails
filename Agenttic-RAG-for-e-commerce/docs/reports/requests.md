# Backend handoff — yêu cầu tích hợp

Ngày: 03/11/2026. Nhánh `feat/a-backend`.

## A2 — Frontend và tài liệu chạy

- API backend đã có `POST /api/orders`, `GET /api/orders/{id}`, `PATCH /api/orders/{id}/note`, `POST /api/stripe/webhook` theo hợp đồng §3. `/api/stripe` cũ dùng chung luồng xác thực/tính giá mới; không còn nhận giá hay user_id của client làm nguồn tin cậy.
- Checkout và checkout-success mới đã ở nhánh frontend. Cần ghép nhánh trước nghiệm thu; không dùng trang checkout cũ trên baseline backend sau khi áp dụng migration, vì đường ghi Supabase trực tiếp đã bị khóa.
- Đề nghị Anti cập nhật `docs/RUN.md` với cấu hình server: `APP_URL` (origin shop; local mặc định `http://localhost:3000`), `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `STRIPE_SECRET_KEY` (**sk_test_**), `STRIPE_WEBHOOK_SECRET`. Không ghi giá trị khóa vào tài liệu.
- Migration `database/migrations/2026-11_payment_and_address.sql` chỉ được chủ đồ án chạy sau khi review/sao lưu. Không chạy lại setup.sql. Sau đó thử Stripe CLI `stripe listen --forward-to localhost:3000/api/stripe/webhook` và thẻ test, kiểm trạng thái/kho và request sửa giá/chủ đơn.
- Có thể chạy Node tests bằng lệnh trong `codex-A2.md`, không cần thêm vitest/package.json.
- Khi merge, hợp nhất file requests.md của hai nhánh và giữ các bàn giao cũ của Anti; file backend này không thay đổi hợp đồng API đã duyệt.

## A7 — Bench credentials (ghi nhớ F10 của Opus)

- Backend đã tự ignore `.env.bench` và `*.env.bench`, có kiểm chứng `git check-ignore -v --no-index`. Chưa tạo tài khoản hoặc ghi mật khẩu ở A2.
- Khi đến A7, Codex tạo `.env.bench` tại **gốc repo** và xuất `BENCH_CUSTOMER_EMAIL` / `BENCH_CUSTOMER_PASSWORD` cho **bench_customer_a**, theo đính chính mới của Claude. Playwright đọc cả `web_ui/.env.bench` và `../.env.bench`. Kiểm tra ignore tại đúng đường dẫn trước khi ghi; không in mật khẩu, không commit file này. `bench_admin` cần role=admin trong public.user_roles, không dùng user_metadata.
- File ignore trên nhánh frontend không tự có tác dụng trên worktree backend. Sau khi ghép nhánh vẫn phải kiểm tra ignore ở nơi chạy seed và nơi Playwright đọc cấu hình.
- A5.4 frontend chỉ được chốt khi chạy thật bằng tài khoản bench; chưa coi test skip là đạt kiểm tra quyền.

## A5 — Nguồn quyền admin

Đã đọc bàn giao frontend: dùng `public.user_roles`/`requireRole` làm nguồn quyền admin, không dùng `user_metadata.role`. A2 không thêm API admin và không sửa module auth của Anti. Theo đính chính C2 của Claude (03/11/2026), hợp đồng chat-logs chuẩn là object `{chat_logs, total, limit, offset}` đã được chấp nhận ở F3; thay thế dạng mảng trong E §3 cũ. A5-backend chỉ ghi bảng chat_logs, không viết lại route frontend.

## A4 — Tool/guard/bench và tài liệu RUN

- FastAPI `/chat` đã có `guard: {action:"allow", decision_id:null, flags:[]}` khi FOX tắt, đúng hợp đồng. Tool mới: `product_reviews`, `create_support_ticket`. Không cần thay body chat.
- Đề nghị frontend cập nhật RUN sau ghép nhánh: `LEGACY_LLM_GUARDRAIL=on|off` và `LEGACY_PROMPT_DEFENSE=on|off` (mặc định on); `FOX_GUARD_MODE=off` ở A4 (mode khác chưa triển khai); `FOX_GUARD_ARM` là nhãn do C định nghĩa.
- `BENCH_RECORD=1` opt-in ghi payload thử gửi Gemini/Groq tại `rag-service/bench_records/YYYY-MM-DD.jsonl` theo UTC. Mặc định tắt, thư mục gitignore, có thể chứa raw PII/text theo mục đích thực nghiệm; không phải chat_logs A5.
- `BENCH_TEMPERATURE=<số hữu hạn 0..2>` ghi đè nhiệt độ; bỏ biến để giữ config. BENCH_RECORD không đổi output, ghi lỗi thì chặn lần gửi không được ghi.
- Skill mới được ghi tại CHANGELOG-bench.md. Chưa có guard logic Phần B, chưa có migration/tài khoản seed A7 ở checkpoint này.
- Khi nghiệm thu sau ghép nhánh: hỏi “Mọi người đánh giá iPhone 16 thế nào?” để đọc review, “Tạo ticket báo đơn giao chậm” khi đã đăng nhập để tạo ticket. Với nhiều biến thể sản phẩm, cần resolve product_id trước; ticket chỉ gắn đơn thuộc chủ.

## A5-backend — Nhật ký thật và bàn giao B

- `/chat` ghi 2 message (user/agent) mỗi lượt bằng service_role, giữ session_id, user_id đã xác minh; risk safe/needs_ticket/attack map low/medium/high. Tool_used chỉ của lượt hiện tại; không lưu JWT/tool args/raw state.
- Migration `2026-11_chat_logs_guard.sql` chỉ là file để review. Chủ đồ án chạy sau duyệt; thêm guard_decision_ids/default [], index phiên/thời gian và khóa quyền client. Không chạy setup.sql. Cần apply trước nghiệm thu log thật.
- B/B9 cần triển khai thêm `guard_client.guard_log(text, ctx) -> LogText(message, decision_ids)`: message phải che PII không hoàn nguyên; ctx có session_id/user_id/mode/arm/role. Không dùng Decision.text nếu chỉ giả danh hóa hoặc đã restore. Mode off trả text gốc; mode bật thiếu masking thì writer từ chối ghi, không raw fallback.
- B có thể trả danh sách decision IDs của cả lượt qua AgentState.guard_decision_ids; writer gộp với IDs do guard_log trả. Trường này và turn_tool_calls reset mỗi lượt. Các hook input/context/output hiện giữ hợp đồng A4; A5 không tự triển khai detector hoặc thay policy B.
- Lỗi log không làm chat/tool đã hoàn tất thành lỗi/retry, chỉ phát mã cảnh báo cố định để vận hành; chưa có queue khôi phục. Ba lượt chat có 6 dòng message thật khi DB/migration sẵn sàng.
- Admin route chuẩn vẫn object `{chat_logs,total,limit,offset}` theo Claude C2. Dữ liệu client session_id cần UUID riêng theo user theo A1; nếu caller tự gửi trùng chuỗi giữa hai user, admin hiện nhóm theo session_id có thể trộn nhóm (khách không đọc được log). Khi cần chống nhóm trùng tuyệt đối, Anti bổ sung user_id vào grouping/filter; không sửa chéo UI tại gói này.

## A7 hoàn tất code và bổ sung tích hợp — bàn giao cuối

- Canonical handoff: `docs/reports/codex-HANDOFF-A.md`; cách seed và recovery: `docs/SEED-BENCH.md`. Seed code tại 40e1c64; review API/health tại c811652. Chưa tạo tài khoản/ghi credential trên Supabase thật vì migration mới và bộ C chưa có.
- Migration mới cần Claude duyệt/chủ đồ án apply: chat_logs_guard, product_reviews, seed_bench; payment_and_address đã được Claude duyệt nhưng vẫn chỉ apply sau khi merge frontend/sao lưu.
- C cần tạo `seed_cases.jsonl` theo ba trường case_id/table/fields; user_id là alias bench_customer_a/b. Không đưa nhãn/gold/canary vào seed công khai. Mẫu `scripts/fixtures/seed_bench.sample.jsonl` chỉ là smoke, product_id=1 phải thay theo catalog thật nếu không tồn tại.
- POST `/api/reviews` trước đây chưa có ở cả hai nhánh, nay đã bổ sung trong phạm vi Codex: JWT/owner phía server, paid hoặc COD accepted và không cancelled, nguyên văn comment. RPC create_product_review chỉ service role. Form không cần đổi hợp đồng.
- `/health` backend mới kiểm Supabase anon thật và Chroma collection hiện có, không chỉ bool cấu hình. Merge main.py giữ `service_health()` và toàn bộ xử lý A1/A4/A5 phía backend.
- Rà merge-tree sau c811652: 3 conflict dự kiến `.gitignore`, `docs/reports/requests.md`, `rag-service/app/main.py`. Git tree simulation không merge hay sửa nhánh frontend/main. Keep ignore union và hợp nhất requests; main.py dùng code backend mới (diff frontend ở đây chỉ là health cũ).
- Đính chính QA plan của Anti: tồn kho là `products.stock`, webhook fulfillment dùng `checkout.session.completed`/`checkout.session.async_payment_succeeded`, không dùng payment_intent.succeeded. Acknowledge chuẩn là `{received:true}`; không yêu cầu trường already_processed. Khi replay event đã ký phải giữ chữ ký hợp lệ hoặc dùng Stripe CLI resend; kiểm DB để khẳng định kho chỉ trừ một lần.
- A5 có 2 message mỗi exchange; chat3 lượt =>6 dòng user/agent. Role bot là agent theo schema, không phải assistant. Live A5.4 admin auth vẫn chờ seed thật; test skip không phải đạt.

## Đợt1 bổ sung K1–K4 (Opus)

- K1: auth.ts mới lazy client và trả lỗi cấu hình an toàn. Giữ export supabaseAdmin bằng proxy để route/frontend consumer không cần đổi import; thêm getSupabaseAdmin nếu cần explicit getter.
- Backend cũ chưa có auth.ts và còn eager admin handlers baseline. Đã mang4 admin handler **đúng nguyên bản e1850a9 của Anti** sang backend (hash4/4 giống source), không tự phát triển logic route của Anti và không sửa worktree frontend. Khi merge giữ các handler đã duyệt này và auth.ts lazy mới; không lấy lại auth.ts eager ở frontend.
- K2: INVALID_PRODUCT acknowledge200+log safe. Thêm checkout.session.expired, gọi fail_stripe_order với cả p_order_id/p_session_id. Migration **2026-11_expired_checkout.sql** là file thứ5 cần Claude duyệt/chủ đồ án apply; overload1 tham số cũ không đổi, không hủy paid/COD/session khác.
- K3: write_chat_turn được await qua asyncio.to_thread; đã kiểm concurrent chat khi một log bị giữ chậm. Pipeline invoke vẫn đồng bộ baseline.
- K4: trước khi có dataset C, sau migrate có thể seed `scripts/fixtures/seed_bench.sample.jsonl --products-from-db` để tự chọn product ID thật và tạo tài khoản A5.4. Dry-run không query catalog. Lỗi miền email báo SEED_EMAIL_ADDRESS_INVALID_CONTACT_CLAUDE; dừng, không đổi domain.
- Test Node/PGlite nên dùng `--v8-pool-size=1 --test-concurrency=1` trên máy8GB để tránh V8 OOM khi nhiều engine khởi tạo song song; không bỏ test nào.
- Báo cáo canonical đợt này `docs/reports/codex-K.md`. Đợt3 chỉ sau merge/migration/seed và có bugs.md backend trên nhánh Claude chỉ định.

---

<!-- Phần dưới: ghi từ nhánh feat/a-frontend (Antigravity) -->

# Yêu cầu & Bàn giao giữa các Tầng (Requests & Handoffs)

Tài liệu ghi nhận các thay đổi dùng chung hoặc các module xuyên suốt giữa Antigravity (Tầng 3 — Frontend & QA) và Codex (Tầng 2 — Backend & Tool).

---

## 1. Module Xác thực Phân quyền Quản trị: `web_ui/src/lib/server/auth.ts`
- **Người tạo**: Antigravity (theo chỉ dẫn của Claude Opus để khắc phục lỗ hổng F2 leo quyền Admin).
- **Mục đích**: Cung cấp hàm `requireRole(request, allowedRoles)` dùng Service Role Client truy vấn trực tiếp bảng **`public.user_roles`** (nguồn thẩm quyền duy nhất theo `database/setup.sql:108-113`), loại bỏ hoàn toàn việc đọc `user_metadata.role` (do client có thể tự sửa đổi).
- **Phạm vi sử dụng**:
  - `web_ui/src/app/api/admin/chat-logs/route.ts`
  - `web_ui/src/app/api/admin/orders/route.ts`
  - `web_ui/src/app/api/admin/tickets/route.ts`
  - `web_ui/src/app/api/admin/users/route.ts` (khi đổi vai trò, API thực hiện upsert vào bảng `user_roles`).
- **Ghi chú cho Codex**: Khi Codex phát triển thêm các API quản trị nội bộ hoặc đồng bộ database, vui lòng sử dụng trực tiếp module `requireRole` này để đảm bảo nhất quán và an toàn phân quyền.

---

## 2. Đặc tả Hợp đồng API Route `GET /api/admin/chat-logs`
- **Query Parameters**:
  - `session_id` hoặc `sessionId`: Lọc theo ID phiên trò chuyện.
  - `risk_level` hoặc `riskLevel`: Lọc theo mức độ rủi ro (`high`, `medium`, `low`).
  - `role`: Lọc theo vai trò (`user`, `agent`, `tool`, `system`).
  - `limit`: Số bản ghi tối đa (mặc định 100, tối đa 500).
  - `offset`: Vị trí bắt đầu phân trang (mặc định 0).
- **Định dạng Response thành công (200 OK)**:
  ```json
  {
    "chat_logs": [
      {
        "id": "uuid",
        "session_id": "string",
        "user_id": "uuid | null",
        "role": "user | agent | tool | system",
        "message": "string",
        "tool_used": "string | null",
        "risk_level": "low | medium | high | null",
        "guard_decision_ids": ["string"],
        "created_at": "ISO-8601 string"
      }
    ],
    "total": 100,
    "limit": 100,
    "offset": 0
  }
  ```
- **Định dạng Response lỗi**:
  - `401`: `{"error": {"code": "UNAUTHENTICATED", "message": "..."}}`
  - `403`: `{"error": {"code": "FORBIDDEN", "message": "..."}}`
  - `500`: `{"error": {"code": "INTERNAL_ERROR", "message": "..."}}`

---

## 3. Cấu hình Tài khoản Benchmark `bench_customer_a` cho E2E Test (F5)
- **Người gửi**: Antigravity (Tầng 3 — Frontend & QA)
- **Người nhận**: Codex (Tầng 2 — Backend & Tool)
- **Nội dung**: Để bộ test E2E Playwright (`tests/e2e/a5_ui.spec.ts: A5.4`) có thể thực hiện kiểm thử tự động hành vi chống leo quyền (Privilege Escalation Prevention) trên API server thật mà không mock:
  - Khi Codex tạo tài khoản mẫu benchmark theo đặc tả `A-hoan-thien-web.md` (dòng 107), vui lòng cấu hình hai biến môi trường vào file `.env.bench`:
    ```env
    BENCH_CUSTOMER_EMAIL=customer_test@example.com
    BENCH_CUSTOMER_PASSWORD=your_secure_password
    ```
  - Test A5.4 đã sẵn sàng cơ chế tự động đọc hai biến này từ `.env.bench` để đăng nhập thật, giả lập người dùng tự sửa `user_metadata.role='admin'`, gọi thật 4 API Admin GET và 1 API Admin PUT để xác minh server từ chối 403 `FORBIDDEN` qua `requireRole`. Khi chưa có `.env.bench`, test tự động `skip` với thông báo rõ ràng.
