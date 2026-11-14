# Báo cáo Đợt1 K1–K4 — 03/11/2026

Base2df89f9, feat/a-backend, worktree D:/create/DATN/.worktrees/a1-backend.
Spec: phần giao thêm trong FOX-Guardrails/docs/plans/prompts/codex-phanA.md.

## 1. Đã làm gì

- **K1:** thêm auth.ts chuẩn dựa trên module Anti, client admin/anon chỉ khởi tạo khi sử dụng; export proxy giữ nguyên tên supabaseAdmin để không bắt Anti sửa consumer. requireRole chỉ đọc user_roles, không tin user_metadata; thiếu cấu hình/khởi tạo lỗi trả500 INTERNAL_ERROR với thông báo chung. Module/route import không tạo client, không cần env.
- Worktree backend trước K vẫn có3 admin route baseline eager, chưa có auth.ts/chat-logs route. Đồng bộ **nguyên bản4 route Anti đã được duyệt từ e1850a9** sang backend, không tự sửa logic handler của Anti; hash-object so với source4/4 giống nhau. Việc mới chỉ nằm trong auth.ts. Không sửa nhánh/checkout đang làm của Anti; đã ghi requests.md.
- **K2:** INVALID_PRODUCT từ finalize là lỗi vĩnh viễn, acknowledge200/log chỉ order_id+code. Thêm xử lý signed checkout.session.expired qua fail_stripe_order(order_id,session_id). Mới chỉ hủy Stripe unpaid/pending có session phù hợp hoặc chưa bound; replay không đổi lần2, paid/COD/session khác không bị ảnh hưởng; không đụng kho.
- Hàm fail_stripe_order(uuid) cũ vẫn giữ nguyên để cleanup lỗi create. Migration mới chỉ thêm overload2 tham số, security definer/search_path rỗng/service-only; notify PostgREST reload schema. Không sửa migration đã được Claude duyệt.
- **K3:** /chat await asyncio.to_thread(write_chat_turn,...), giữ chờ kết quả ghi của chính request nhưng không giữ event loop trong lúc IO log. Lỗi helper vẫn trả200 cho chat đã hoàn tất. Workflow.invoke vẫn đồng bộ như baseline; không tuyên bố toàn bộ pipeline nonblocking.
- **K4:** --products-from-db remap ID placeholder trong mẫu sang ID thật có thứ tự, giữ quan hệ order/review và chỉ đọc catalog. Không đủ product dừng trước tạo credential/tài khoản. Dry-run vẫn không gọi DB. email_address_invalid được báo SEED_EMAIL_ADDRESS_INVALID_CONTACT_CLAUDE và exit1, không dump exception/email/password và không tự đổi domain.

## 2. File đổi

- web_ui/src/lib/server/auth.ts; các admin handler được đồng bộ từ e1850a9; order-handlers.ts và test admin-auth/orders/expired-checkout-db.
- database/migrations/2026-11_expired_checkout.sql (file mới, chờ Claude duyệt/chủ đồ án chạy).
- rag-service/app/main.py, tests/test_async_chat_logs.py.
- scripts/seed_bench.py, rag-service/tests/test_seed_bench.py, docs/SEED-BENCH.md.
- Báo cáo/kế hoạch K, requests.md và handoff tổng hợp.

## 3. Kiểm thử / output thật

- RED trước code:2 test admin auth thiếu module, INVALID_PRODUCT trả503 thay200, expiry không gọi RPC; test event loop thất bại khi first request đã chặn loop đến hết ghi log. K4 RED2 failed/15passed (chưa có remap và mã lỗi miền). Sau sửa các ca đều xanh.
- Pytest toàn suite: **93 passed in5.55s** (env DL; lệnh `C:/Users/Admin/anaconda3/envs/DL/python.exe -m pytest -q` tại rag-service).
- Node/PostgreSQL toàn suite: **77 tests,77pass,0fail,0skip**, chạy tuần tự như dưới. Test thực thi overload/migration lại, client bị chặn RPC, paid/COD/mismatched session bất biến; handler+SQL tái hiện sản phẩm đã xóa trước webhook, trả200 và log an toàn.

```powershell
$env:PGLITE_MODULE_PATH='D:/create/DATN/.test-tools/a2/node_modules/@electric-sql/pglite'
node --v8-pool-size=1 --test --test-concurrency=1 web_ui/src/lib/server/__tests__/*.test.cjs rag-service/tests/*-db.test.cjs
```

- Lượt mặc định chạy nhiều PGlite song song bị V8 **Fatal process out of memory: Zone**; chạy payment-db riêng với pool1 và toàn suite tuần tự qua. Máy8GB RAM, còn khoảng6GB virtual lúc kiểm, có các Node process khác; không dừng process của người dùng. Không coi crash hạ tầng là test xanh; đã dùng chế độ ít tài nguyên để kiểm đủ suite, không bỏ test.
- Build thực sự không có env: xóa NEXT_PUBLIC_SUPABASE_URL/ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, STRIPE_SECRET_KEY/WEBHOOK_SECRET trong process; worktree chỉ có .env.example. `npm.cmd run build` exit0, TypeScript qua, **29/29**, có route admin/chat-logs. Không dùng dummy env trong lần kiểm K1 này.
- `npx.cmd eslint src/lib/server/auth.ts src/lib/server/order-handlers.ts src/app/api/admin`: exit0.
- Hash4 admin route so e1850a9: identical. Seed sample --products-from-db --dry-run: exit0, valid_cases2; không tạo credential trong repo.
- Review độc lập: **43/43 Node/PGlite** focus và **18/18 pytest** concurrency/seed đều qua; tự kiểm hash4 admin route và whitespace. Không còn Critical/Important/Minor trong K scope. Reviewer không lặp build/full suite đã báo, không gọi remote.

## 4. Còn mở / bàn giao

- Migration K2 mới cần Claude duyệt và chủ đồ án apply sau migration trước; bốn migration cũ đã được Claude duyệt ở nghiệm thu lần2. Không tự chạy DDL hoặc seed lên Supabase.
- Chưa chứng minh PostgREST cache/RPC overload trên dịch vụ thật hay Stripeexpired thật; local PostgreSQL/SDK boundary đã kiểm. Cần thêm event expired vào cấu hình webhook test khi nghiệm thu.
- --products-from-db dành cho smoke fixture trước khi C có dataset. Catalog thay đổi các ID thấp nhất có thể đổi remap/hash; script dừng thay vì tự ghi đè, cần đối soát hoặc reset đúng phạm vi. Dataset C chính thức không dùng remap.
- Email .invalid chưa thử thật. Nếu bị từ chối, giữ nguyên namespace/credential, báo mã cho Claude; không tự chọn email thật/domain khác.
- Logging đã offload nhưng vẫn là ghi không có queue/recovery, có thể chờ timeout/thread-pool dưới tải cao. C nên báo cả latency của DB log; không suy ra toàn pipeline đã async.
- Đợt3 chưa bắt đầu: chờ Claude merge, chủ đồ án migrate/seed, Anti ghi docs/QA/bugs.md và chỉ định nhánh tích hợp. Không tự dựng lỗi QA giả hoặc sửa UI ngoài phạm vi.

### Phân định review được chấp nhận

- PostgREST overload/cache ở Supabase thật, apply migration, event expired thật và miền email .invalid chưa được nghiệm thu. Local SQL và request boundary không thay thế các bước đó.
- Frontend integration và concurrency toàn pipeline chưa được chứng minh; review chỉ xác nhận off-thread log và yêu cầu K. Pipeline model vẫn baseline sync, worker pool/DB timeout vẫn là giới hạn hiệu năng phải đo.
- Đồng bộ admin routes là dùng lại code đã duyệt e1850a9, không sửa nhánh Anti. Proxy giữ consumer import tương thích; khi merge auth.ts phải giữ bản K1.

Đối chiếu kỹ thuật: [PostgREST RPC/overloads và schema cache](https://docs.postgrest.org/en/v16/references/api/functions.html), [Stripe event types](https://docs.stripe.com/api/events/types). Payload/tên tham số đã đối chiếu SDK/local PostgreSQL; chưa gọi dịch vụ thật.
