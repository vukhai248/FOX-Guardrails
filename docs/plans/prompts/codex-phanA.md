# Prompt giao việc — Codex (Phần A, backend & bảo mật)

Dán nguyên khối dưới vào Codex, mở tại `D:/create/DATN/Agenttic-RAG-for-e-commerce`, nhánh `feat/a-backend`.

---

Bạn là kỹ sư backend của đồ án. Repo hiện tại là web e-commerce Agentic RAG (Next.js `web_ui/` + FastAPI/LangGraph `rag-service/` + Supabase).

Đọc trước, theo thứ tự:
1. `D:/create/DATN/FOX-Guardrails/docs/plans/E-phan-cong-agent.md` — vai trò của bạn, file bạn sở hữu, hợp đồng API (§3), quy tắc (§7).
2. `D:/create/DATN/FOX-Guardrails/docs/plans/A-hoan-thien-web.md` — hiện trạng lỗi H1–H12 và đặc tả các gói.

Phạm vi của bạn: **A1, A2, A4** (gồm cờ bench ở A4 mục 6 và khung `guard_client.py` mục 7), sau đó **A5-backend** (ghi `chat_logs` trong rag-service) và **A7** (`scripts/seed_bench.py`). Không làm UI (`page.tsx`, `components/`), đó là phần của agent khác.

Cách làm:
- Làm **từng gói một** theo thứ tự A1 → A2 → A4 → A5-backend → A7. Hết mỗi gói: chạy test, commit `feat(A<n>): …`, viết `docs/reports/codex-A<n>.md` (đã làm gì / file đổi / lệnh test + output thật / việc còn mở), rồi **dừng và chờ** tôi cho đi tiếp.
- Dựng `rag-service/tests/` với pytest nếu chưa có. Với route Next.js, tách logic (tính giá, kiểm tồn kho, kiểm chủ sở hữu) vào `web_ui/src/lib/server/` và viết unit test cho logic đó (cần thêm vitest thì ghi yêu cầu vào `docs/reports/requests.md`).
- Bám đúng hợp đồng API ở §3. Muốn đổi hợp đồng thì ghi vào `requests.md` và dừng hỏi.
- Migration chỉ được **thêm** (file mới trong `database/migrations/`). **Tuyệt đối không chạy `database/setup.sql`** và không tự chạy SQL lên Supabase: viết file, tôi sẽ chạy sau khi được duyệt.
- Chỉ dùng khoá Stripe **test**. Không commit `.env*`. Không in secret ra log.
- Không sửa system prompt của bot ngoài phần cần cho tool mới; nếu có sửa thì ghi vào `docs/CHANGELOG-bench.md`.

Bắt đầu với A1. Trước khi code, liệt kê ngắn (≤ 10 dòng) kế hoạch A1 và các file sẽ sửa.

---

## ✅ Kết quả nghiệm thu — Claude, 03/11/2026 (nhánh `feat/a-backend` @ `ad5658d`)

Claude đã tự chạy lại tại worktree `D:/create/DATN/.worktrees/a1-backend`: pytest → **53 passed**; Node/PGlite → **53/53 passed**; `tsc --noEmit` → **exit 0**. Đã đọc toàn bộ migration SQL, các file `order-*`/`payment-runtime`, cùng diff Python của `main.py`, `master_agent.py`, `guard_client.py` và hai tool mới.

| Gói | Kết quả | Ghi chú |
| --- | --- | --- |
| A1 | **Đạt** | `thread_id = <user_id\|anon>:<session_id>`; hết `max_turns` trả câu an toàn kèm `loop_exhausted` |
| A2 | **Đạt phần code**, chờ chạy thật | Giá và chủ đơn lấy từ server; webhook xác minh chữ ký, đối chiếu số tiền/tiền tệ và idempotent; RPC chỉ grant cho `service_role`; đã `REVOKE` quyền ghi `orders` từ client. **Migration đã được Claude duyệt** (xem dưới) |
| A4 | **Đạt phần code**, chờ chạy thật | Danh tính được inject sau `_sanitize_tool_args`, LLM không tự đặt được `current_user_id`; ticket ghi bằng client RLS; ba điểm cắm guard đã nối, kể cả nhánh hết vòng và nhánh fallback |

Merge thử với `feat/a-frontend` (`8264d41`): chỉ xung đột ở `.gitignore` (cả hai nhánh cùng thêm `.env.bench`) và `docs/reports/requests.md`. Claude sẽ tự gộp hai chỗ này khi merge. Response của `/api/orders*` khớp với các trang checkout, checkout-success và account của Anti.

**Duyệt migration `2026-11_payment_and_address.sql`:** chỉ thêm cột, ràng buộc và hàm mới, không xoá dữ liệu. Có bọc `BEGIN/COMMIT`, các hàm `SECURITY DEFINER` đều đặt `search_path = ''`. Ràng buộc mới tương thích với dữ liệu cũ. Sau migration, client không còn ghi trực tiếp vào `orders`. Đã kiểm trên nhánh frontend: checkout, checkout-success và account không ghi `orders` qua client nữa, nên **chỉ chạy migration sau khi đã merge frontend**.

### Việc tiếp theo (làm theo thứ tự)

**C1 — [Nên làm, nhỏ] Webhook lặp lại vô hạn với lỗi vĩnh viễn** (`order-handlers.ts:178-180`)
- Mọi lỗi từ `finalize_stripe_order` đều trả 503, nên Stripe sẽ gửi lại tới 3 ngày, kể cả với `PAYMENT_MISMATCH`/`NOT_FOUND` (lỗi không tự hết).
- Sửa: tách lỗi tạm thời (`OUT_OF_STOCK`, lỗi kết nối DB) → 503, khỏi lỗi vĩnh viễn (`PAYMENT_MISMATCH`, `NOT_FOUND`, `NOT_EDITABLE`) → 200 `{received:true}` kèm `console.error` chỉ ghi `order_id` và mã lỗi (không ghi PII). Thêm test.

**C2 — Hợp đồng `GET /api/admin/chat-logs`: giữ dạng object**
- `requests.md` của Codex ghi "giữ dạng mảng ở §3". Claude đã chấp nhận dạng của Anti `{chat_logs, total, limit, offset}` ở F3, route frontend đã chạy theo dạng này. **Lấy dạng object làm chuẩn.** Ở A5-backend Codex chỉ ghi bảng `chat_logs` từ rag-service, không làm lại route này. Sửa lại dòng tương ứng trong `requests.md`.

**A5-backend** (ghi `chat_logs`), rồi **A7** (`scripts/seed_bench.py`, tạo `bench_customer_a`/`bench_customer_b`/`bench_admin`) theo `A-hoan-thien-web.md`. Lưu ý:
- A7 ghi `BENCH_CUSTOMER_EMAIL` / `BENCH_CUSTOMER_PASSWORD` (của `bench_customer_a`) vào `.env.bench` ở **gốc repo**, vì Playwright của Anti đọc `web_ui/.env.bench` và `../.env.bench`. Chạy `git check-ignore` trước khi ghi. Không in mật khẩu.
- `bench_admin` phải có dòng `role='admin'` trong `public.user_roles`, vì đây là nguồn quyền duy nhất. Không dùng `user_metadata.role`.
- Seed chỉ chèn thêm, không chạy `setup.sql`. Nếu cần bảng hay cột mới, viết thành migration riêng để Claude duyệt.

Hết mỗi gói vẫn làm như cũ: test, commit, viết `codex-A<n>.md`, rồi dừng.

## ✅ Nghiệm thu lần 2 — Claude, 03/11/2026 (nhánh `feat/a-backend` @ `2df89f9`)

Claude chạy lại: pytest **90 passed**; Node/PGlite **69/69**; `tsc` exit 0; seed `--dry-run` ra `{"dry_run": true, "valid_cases": 2}`.

| Gói | Kết quả | Ghi chú |
| --- | --- | --- |
| C1 | **Đạt** | Lỗi vĩnh viễn trả 200 và log chỉ `order_id` + mã; lỗi khác vẫn 503 và không log chi tiết |
| C2 | **Đạt** | `requests.md` đã lấy dạng object làm chuẩn |
| A5-backend | **Đạt phần code** | Ghi 2 dòng/lượt bằng service role; reset `turn_tool_calls` mỗi lượt; guard bật mà chưa có B thì không ghi bản thô |
| A7 | **Đạt phần code** | Kiểm `.env.bench` có trong gitignore trước khi ghi; không in mật khẩu; quyền admin lấy từ `user_roles`; reset chỉ xoá dữ liệu do chính namespace đó seed |
| A3-backend (Codex tự làm thêm) | **Chấp nhận** | `/api/reviews` là endpoint form của Anti đang gọi mà chưa có; hợp đồng khớp form. `/health` kiểm kết nối thật |

**Duyệt 3 migration mới** (`chat_logs_guard`, `product_reviews`, `seed_bench`): chỉ thêm, không xoá dữ liệu, bọc `BEGIN/COMMIT`, hàm `SECURITY DEFINER` đặt `search_path = ''`, chỉ `service_role` gọi được. Frontend chỉ đọc `reviews` từ client và ghi review qua API, nên `REVOKE INSERT` trên `reviews` không làm hỏng form. Admin đọc `chat_logs` bằng service role. **Đã duyệt.** Chạy theo thứ tự trong `codex-HANDOFF-A.md` §4, sau khi merge và sao lưu.

**Ghi vào danh sách giới hạn, không cần sửa ngay:**
- `decrement_stock_for_order` raise `INVALID_PRODUCT` (sản phẩm bị xoá sau khi đã thanh toán) đang rơi vào nhánh 503, nên Stripe sẽ gửi lại tới 3 ngày. Hiếm gặp; xử lý bằng đối soát thủ công.
- `write_chat_turn` là lời gọi đồng bộ bên trong `async def /chat`, nên block event loop một lượt ghi DB. Khi Phần C đo latency, mọi arm đều chịu như nhau. Ghi rõ điều này trong phần phương pháp đo.
- Email bench `@example.invalid`: chưa chắc Supabase Auth chấp nhận tên miền `.invalid`. Nếu lần seed thật báo `email_address_invalid`, báo Claude trước khi đổi tên miền.

**Không có việc code mới cho Codex lúc này.** Bước tiếp theo là Claude merge, chủ đồ án chạy migration, rồi chạy seed thật (khi có dataset của C, hoặc chạy bằng file mẫu để tạo tài khoản cho A5.4).

## Kế hoạch còn lại của Phần A (giao trọn) — Claude, 03/11/2026

Thứ tự: **Đợt 1** (làm ngay trên `feat/a-backend`) → Claude merge, chủ đồ án chạy 4 migration và seed → **Đợt 3** (sửa lỗi QA). Sau mỗi đợt: test, commit, viết báo cáo, rồi dừng.

### Đợt 1 — Codex (việc nặng / rủi ro)

**K1 — `next build` không được đòi env thật.** Admin routes và `lib/server/auth.ts` đang tạo Supabase client ngay lúc nạp module, nên build trên máy sạch không có `.env.local` sẽ lỗi. Chuyển sang tạo client lúc gọi lần đầu. Thiếu env thì route trả 500 `INTERNAL_ERROR` với thông báo chung. `auth.ts` thuộc `lib/server`, là file của Codex. Admin routes là file của Anti: chỉ đổi phần import cho khớp, và ghi vào `requests.md`. Kiểm: build không có env vẫn qua.

**K2 — Phân loại lỗi webhook cho đủ.**
- `INVALID_PRODUCT` từ `finalize_stripe_order` (sản phẩm bị xoá sau khi khách đã trả tiền) là lỗi vĩnh viễn: trả 200, log `order_id` + mã.
- Xử lý thêm `checkout.session.expired`: gọi `fail_stripe_order` để đơn chưa trả không treo `pending` mãi. Phải idempotent, và không được động vào đơn đã `paid`.
- Viết test cho cả hai.

**K3 — Ghi `chat_logs` không được chặn event loop.** Trong `async def /chat`, gọi `write_chat_turn` qua `await asyncio.to_thread(...)`. Giữ nguyên hành vi: log lỗi thì vẫn trả 200. Test: một lượt ghi log chậm không làm request khác bị chờ. Phần C cần điều này để đo độ trễ cho đúng.

**K4 — Seed đủ dùng trước khi C có dataset.** Thêm `--products-from-db` (hoặc chỉ ghi rõ trong tài liệu) để file mẫu dùng `product_id` có thật, tạo được 3 tài khoản cho A5.4. Ghi trong `SEED-BENCH.md` cách xử lý nếu Supabase từ chối email `@example.invalid`: dừng, báo mã lỗi, **không** tự đổi tên miền.

Báo cáo: `docs/reports/codex-K.md`.

### Đợt 3 — Codex: sửa lỗi backend từ `docs/QA/bugs.md`
- Chỉ sửa lỗi được đánh dấu backend. Mỗi lỗi: test tái hiện (RED), sửa, rồi GREEN. Nếu cần bảng hay cột mới thì viết migration mới để Claude duyệt.
- Làm trên nhánh tích hợp Claude chỉ định. Báo cáo `docs/reports/codex-QA-fix.md`.

## ✅ Nghiệm thu lần 3 — Claude, 03/11/2026 (nhánh `feat/a-backend` @ `5c0580e`)

**K1–K4: Đạt.** Claude chạy lại: pytest **93 passed**, Node/PGlite **77/77** (`--v8-pool-size=1 --test-concurrency=1`).

- K1: `auth.ts` lazy, proxy `supabaseAdmin` giữ import cũ, `requireRole` chỉ đọc `user_roles`. Việc chép 4 admin route nguyên bản `e1850a9` sang backend có ghi `requests.md`, nội dung trùng frontend nên merge không xung đột ở đó. Khi merge, `auth.ts` giữ **bản backend**.
- K2: kho Stripe chỉ trừ lúc `finalize`, nên huỷ đơn hết hạn không cần trả kho. Migration `2026-11_expired_checkout.sql` (overload 2 tham số, service-only, chỉ đụng đơn `stripe/unpaid/pending` cùng session): **Claude đã duyệt**, là migration thứ 5.
- K3, K4: đúng yêu cầu, có test.

Ghi nhận, chưa phải sửa bây giờ: `finalize` gặp `OUT_OF_STOCK` (kho hết giữa lúc tạo đơn và lúc khách trả) đang trả 503 nên Stripe retry mãi, trong khi khách đã trả tiền. Ít xảy ra với dữ liệu bench; nếu QA gặp thì xử lý ở Đợt 3.

**Không có việc code mới cho Codex.** Chờ Claude merge, chủ đồ án chạy 5 migration và seed, rồi Đợt 3.

## ✅ Nghiệm thu migration/seed/Stripe — Claude, 03/11/2026

Đạt (xem `nghiem-thu-A.md` Lần 11). Claude kiểm lại DB thật bằng truy vấn chỉ đọc.

### K5 — BUG-A-01: một user review cùng sản phẩm nhiều lần
- QA tìm ra `bench_customer_a` có 3 review cho sản phẩm 1001. Đây là kênh khuếch đại tấn công chèn gián tiếp: một kẻ tấn công spam nhiều review độc.
- Sửa trong một migration mới `2026-11_review_unique.sql`:
  - `create_product_review` raise `ALREADY_REVIEWED` nếu `(user_id, product_id)` đã có; route trả 409.
  - Thêm unique index `(user_id, product_id)`.
- **Dữ liệu trùng hiện có**: migration phải đếm trước. Nếu trùng chỉ thuộc user bench (có `bench_seed_namespace` trong `raw_app_meta_data`) thì giữ bản mới nhất, xoá bản cũ, và ghi số dòng xoá. Nếu có trùng của user **không** phải bench thì `RAISE EXCEPTION 'NON_BENCH_DUPLICATE_REVIEWS'` và dừng, không xoá.
- Test RED → GREEN trên PGlite. Chạy thử trên bản khôi phục bằng `D:/backups/supabase/20261103-213431-pre-migration/migration_chain_test.py` (thêm file vào `ORDER`).
- **Không** chạy lên Supabase thật trước khi Claude duyệt SQL. Báo cáo `docs/reports/codex-K5.md`.

Làm K5 trước. Xong K5 thì làm Phần B Đợt 1 (`codex-phanB.md`); hai việc ở hai repo khác nhau.
