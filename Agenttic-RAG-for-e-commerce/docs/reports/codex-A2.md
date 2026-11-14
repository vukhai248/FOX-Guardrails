# Báo cáo Codex — A2: đơn hàng server và Stripe test

Ngày 03/11/2026. Nhánh `feat/a-backend`, worktree `D:/create/DATN/.worktrees/a1-backend`.
Base A2: `db7f3d4`. Tiếp tục từ A1 theo chỉ dẫn của chủ đồ án.

## 1. Đã làm gì

- Xác minh phản hồi Opus F10: ignore ở frontend không bảo vệ backend. Đã tự thêm `.env.bench` và `*.env.bench` vào `.gitignore` backend **trước khi tạo bất kỳ file mật khẩu bench nào**. Chưa tạo `.env.bench`/tài khoản bench ở A2.
- API tạo đơn xác thực Bearer token với Supabase Auth bằng anon key, lấy **verified user ID**, bỏ qua user_id/giá/tổng tiền/trạng thái của client. RPC dùng service role, lấy `products.final_price`, kiểm sản phẩm và tồn kho, lưu snapshot item và tổng tiền server.
- COD: tạo đơn pending/cod_pending và trừ kho trong cùng transaction; thiếu một sản phẩm thì rollback toàn bộ. Gộp quantity của product trùng, kiểm số nguyên và giới hạn input. VND dùng giá DB làm tròn đến đồng để thống nhất Checkout và order total.
- Stripe: lưu pending/unpaid trước, tạo Checkout từ snapshot server, metadata chỉ có order_id. URL thành công chỉ có order_id/session_id; origin lấy từ `APP_URL`, không lấy header Origin của khách. Chỉ chấp nhận khóa `sk_test_`, không có fallback mock key/URL.
- Webhook đọc raw body, xác minh chữ ký Stripe SDK; chỉ xử lý test session payment đã paid, kiểm order/session/currency/amount. Khóa row order và product theo thứ tự ID; cập nhật paid/processing và trừ kho một lần trong transaction. Lặp webhook trả thành công mà không trừ thêm.
- Thêm cột địa chỉ/thanh toán/note, giữ shipping_address cũ và legacy rows; thêm dấu nội bộ `stock_decremented_at` để idempotent. Các RPC security definer cố định search_path và chỉ grant EXECUTE cho service_role. Revoke quyền client INSERT/UPDATE/DELETE orders để không bypass API qua policy insert-own cũ. Owner SELECT/RLS giữ nguyên.
- GET đơn lọc đồng thời id và owner; không phải chủ/mã sai đều 404. PATCH note giữ nguyên codepoint, tối đa 500, chỉ pending; atomic update còn lọc owner và status để tránh race.
- Khi Checkout lỗi, không tạo thanh toán giả. Nếu đã tạo session mà lưu liên kết lỗi, thử expire session; nếu trạng thái expire không chắc chắn, giữ đơn unpaid cho webhook/đối soát thay vì tự đánh dấu thất bại.

## 2. File đổi

- `.gitignore`: bảo vệ file mật khẩu bench trên chính nhánh backend.
- `database/migrations/2026-11_payment_and_address.sql`: schema, stock/payment transactions và quyền thực thi. **Chưa chạy lên Supabase.**
- `web_ui/src/lib/server/order-core.ts`: validation, Unicode note, tạo payload Checkout, projection response.
- `web_ui/src/lib/server/order-handlers.ts`: luồng create/detail/note/webhook, hợp đồng lỗi và xử lý lỗi bên ngoài.
- `web_ui/src/lib/server/payment-runtime.ts`: Supabase/Stripe server-only adapters, cấu hình lazy, test-mode gate.
- Routes `api/orders`, `api/orders/[id]`, `api/orders/[id]/note`, `api/stripe`, `api/stripe/webhook`.
- `web_ui/src/lib/server/__tests__/`: 3 suite Node; TS loader và SQL fixture tối thiểu. Không chạy setup.sql trong test.
- `docs/reports/codex-A2-plan.md`, `codex-A2.md`, `requests.md`: tiến độ, bằng chứng và bàn giao.

Không sửa UI, `package.json`, lockfile, prompt hoặc các file của FOX-Guardrails.

## 3. Test và output thật

### Môi trường và cách chạy

Đã dùng Node v24.16.0, dependency app từ lockfile qua `npm ci --ignore-scripts --no-audit --no-fund` (603 packages). Không đổi dependency app. PostgreSQL WASM PGlite 0.5.14 được cài ở thư mục công cụ ngoài repo bằng:

```powershell
npm.cmd install --prefix D:\create\DATN\.test-tools\a2 @electric-sql/pglite --ignore-scripts --no-audit --no-fund
```

DB tests tạo PostgreSQL **trong RAM**, fixture handwritten gồm products/orders/RLS/roles; không đọc/chạy setup.sql, không kết nối Supabase, không reset DB thật.

Tại root worktree:

```powershell
$env:PGLITE_MODULE_PATH='D:\create\DATN\.test-tools\a2\node_modules\@electric-sql\pglite'
node --test web_ui\src\lib\server\__tests__\*.test.cjs
```

```text
tests 53
pass 53
fail 0
skipped 0
```

31 test logic/route, 15 test SQL và luồng handler+DB+chữ ký SDK, 7 test adapter/chữ ký/config. Test adapter dùng Supabase SDK thật với fetch offline để kiểm Bearer/anon key/service key, owner filter và conditional note update. Test tích hợp xác minh webhook ký thật bằng SDK, áp transaction SQL thật, gửi lặp và kiểm stock.

Chu kỳ test-first: suite DB ban đầu fail vì migration chưa tồn tại, suite handler fail vì chưa có implementation. Hai regression bổ sung đã thấy RED rồi GREEN: session thiếu ID gây TypeError → trả 400; SQL LIKE coi dấu `_` là wildcard → đổi sang so prefix chính xác. Các test này hiện nằm trong suite 53/53.

Tại `rag-service`:

```powershell
& 'C:\Users\Admin\anaconda3\envs\DL\python.exe' -m pytest -q
```

```text
16 passed in 1.77s
```

Tại `web_ui`:

```powershell
npx.cmd tsc --noEmit --incremental false
npx.cmd eslint src/lib/server/order-core.ts src/lib/server/order-handlers.ts src/lib/server/payment-runtime.ts src/app/api/orders src/app/api/stripe
```

Cả hai exit 0, không output lỗi. Lint này chỉ áp cho code production mới/đổi, không tuyên bố toàn repository không có lỗi có sẵn.

Build ban đầu thiếu env: compile/TypeScript qua nhưng dừng ở route admin baseline (`supabaseUrl is required` khi createClient ở module scope). Không sửa file admin. Chạy lại bằng biến giả (chỉ trong process, không tạo .env, không dùng endpoint/khóa thật):

```powershell
$env:NEXT_PUBLIC_SUPABASE_URL='https://offline.supabase.invalid'
$env:NEXT_PUBLIC_SUPABASE_ANON_KEY='offline-anon-key'
$env:SUPABASE_SERVICE_ROLE_KEY='offline-service-key'
npm.cmd run build
```

```text
Compiled successfully in 4.7s
Finished TypeScript in 6.1s
Generating static pages ... (27/27)
```

Exit 0. Build liệt kê đủ 5 route orders/stripe mới/đổi.

```powershell
git check-ignore -v --no-index .env.bench web_ui/.env.bench local.env.bench
```

```text
.gitignore:37:*.env.bench  .env.bench
.gitignore:37:*.env.bench  web_ui/.env.bench
.gitignore:37:*.env.bench  local.env.bench
```

`git diff --check`: exit 0. Các dòng cảnh báo LF→CRLF là cấu hình Git Windows, không phải lỗi whitespace.

## 4. Việc còn mở / quyết định

- Đây là **checkpoint code backend**, chưa phải nghiệm thu A2 với Supabase/Stripe test thật. Migration chỉ là file mới, cần chủ đồ án duyệt/chạy sau sao lưu. Chưa chạy Stripe CLI/thẻ 4242, chưa thử thanh toán dịch vụ thật hay E2E toàn web sau ghép nhánh.
- Đã thử khởi động bản build để smoke HTTP trực tiếp ở cổng 3101, nhưng hệ thống phê duyệt tự động từ chối lệnh `next start` với lý do `blocked by policy`. Không khởi động lại bằng đường vòng; phần kiểm HTTP production này chưa chạy. Test các hàm route đã đăng ký và build vẫn có bằng chứng ở trên.
- Docker daemon không chạy; dùng PostgreSQL PGlite để kiểm SQL thực thi và quyền. Engine nhúng một kết nối không chứng minh contention đa process trên Supabase. Cần thử hai đơn tranh món cuối trên DB thật sau duyệt; code dùng row locks và cùng thứ tự khóa để tránh oversell/deadlock giữa các đơn.
- Theo đặc tả, Stripe chưa reserve kho khi unpaid. Nếu hàng hết trước webhook, transaction rollback và webhook trả 503 để retry, đơn tạm còn unpaid dù Stripe đã thu tiền; cần đối soát, bổ sung hàng rồi replay hoặc xử lý hoàn tiền thủ công. Không triển khai workflow refund/reservation mới ngoài A2.
- Lỗi DB/nhà cung cấp ở bước lưu session/expire có thể để lại đơn unpaid cần đối soát. Không tự trả URL giả hoặc đánh dấu paid trong các nhánh lỗi.
- Giá dùng `final_price` DB, làm tròn nguyên VND; địa chỉ cấu trúc legacy để nullable nhằm giữ đơn cũ. Không tự suy luận trạng thái thanh toán đơn legacy.
- UI checkout/checkout-success và tài liệu RUN thuộc frontend; đã ghi bàn giao ở requests.md. Nhánh frontend đã có F9/F10 tại `8264d41`, nhưng backend vẫn tự mang ignore để an toàn độc lập. A7 sau này phải xuất BENCH_CUSTOMER_EMAIL/PASSWORD đúng tên và kiểm ignore trước khi ghi.
- Không thay hợp đồng HTTP đã duyệt. PATCH note được bổ sung trong A2 để đáp ứng frontend A3, vẫn đúng owner và API §3.
- Dừng sau checkpoint A2, chưa làm A4/A5/A7.

### Review độc lập

- Reviewer đọc staged diff, schema baseline và đặc tả A2; tự chạy Node/PGlite: **53 passed, 0 failed**; staged whitespace check qua. Không có finding Critical/Important/Minor. Kết luận đạt cho checkpoint code A2 backend, chưa thay thế nghiệm thu tích hợp.
- Chấp nhận phân định review: Supabase thật, tranh kho đa process và thanh toán Stripe thật cần chủ đồ án duyệt migration rồi kiểm thử; hiện chưa có bằng chứng cho các môi trường đó.
- Chấp nhận quyết định thiếu kho sau khi Stripe trả paid: giữ rollback + retry + đối soát như đã nêu; chi phí nếu không xử lý đối soát là Stripe đã thu tiền nhưng đơn/kho chưa hoàn tất.
- Chấp nhận phân định UI: checkout mới cần merge frontend; bản UI baseline ghi client trực tiếp sẽ không tương thích sau migration. Chi phí nếu chạy backend branch riêng như bản hoàn thiện là luồng checkout cũ bị từ chối.
- Reviewer xác nhận admin baseline còn tin `user_metadata.role`; bản sửa nằm ở frontend/A5, không thuộc diff A2. Phải ghép các bản sửa frontend đã nghiệm thu trước triển khai/QA toàn hệ thống; không coi nhánh backend riêng là toàn bộ hệ thống đã an toàn.
- Refund, hoàn kho do hủy đơn và dọn session Checkout bỏ dở chưa triển khai vì ngoài checkpoint này; chi phí là cần quy trình vận hành/đối soát thủ công. Không bổ sung tính năng ngoài gói chỉ để mở rộng phạm vi review.

Nguồn kỹ thuật đã đối chiếu: [Stripe webhook raw-body/signature](https://docs.stripe.com/events/manage-webhook-endpoints#signature-errors), [Stripe fulfillment](https://docs.stripe.com/checkout/fulfillment), [PGlite](https://pglite.dev/docs/about). API SDK cũng được đối chiếu trực tiếp bằng package đã cài và thực thi test cục bộ.

Kiểm tra cuối trước commit: Node/PGlite **53 passed, 0 failed, 0 skipped**; pytest **16 passed in 2.08s**; TypeScript và eslint file production mới/đổi đều exit 0. Ignore bench khớp tại cả root và web_ui. Không tạo/track file mật khẩu bench. Worktree giữ nguyên để chờ nghiệm thu và gói A4.
