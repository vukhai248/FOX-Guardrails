# A7 — Chạy seed benchmark

Script: `scripts/seed_bench.py`. Chạy từ gốc **workspace đã merge** để `.env.bench` nằm đúng chỗ Playwright đọc. Dùng Python có các dependency của rag-service (`supabase`, `python-dotenv`); trên máy hiện tại là `C:/Users/Admin/anaconda3/envs/DL/python.exe`.

## Điều kiện trước khi chạy thật

1. Claude duyệt migration; chủ đồ án sao lưu DB, merge frontend rồi áp dụng các migration mới theo tài liệu bàn giao. Không chạy `database/setup.sql`.
2. Có `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY` trong environment hoặc `rag-service/.env`; có thể dùng tên NEXT_PUBLIC_SUPABASE_URL/ANON_KEY từ `web_ui/.env.local`. Script không in giá trị. Environment hiện có được ưu tiên.
3. C cung cấp JSONL chính thức và product_id tồn tại. Mẫu dưới chỉ kiểm cơ chế, chưa phải dataset đánh giá.

## Kiểm tra không có side effect

```powershell
& 'C:/Users/Admin/anaconda3/envs/DL/python.exe' scripts/seed_bench.py --cases scripts/fixtures/seed_bench.sample.jsonl --dry-run
```

Kết quả: `{"dry_run": true, "valid_cases": 2}`. Không nạp credential, không tạo tài khoản, không gọi DB. Product_id=1 trong mẫu chỉ là chỗ điền; dry-run không khẳng định sản phẩm này tồn tại trên server.

### Tạo tài khoản trước khi có dataset C (K4)

Sau merge, sao lưu và áp dụng migration đã duyệt, có thể chạy ngay mẫu trung tính với ID có thật:

```powershell
& 'C:/Users/Admin/anaconda3/envs/DL/python.exe' scripts/seed_bench.py --cases scripts/fixtures/seed_bench.sample.jsonl --products-from-db
```

Cờ này chỉ đọc `products.id` theo thứ tự tăng dần, ánh xạ các ID placeholder khác nhau sang các ID thật khác nhau, giữ liên kết giữa order/review. Không sửa catalog hay stock. Nếu không đủ sản phẩm thì dừng trước khi tạo credential/tài khoản. Chạy lại khi catalog không đổi vẫn idempotent; nếu tập ID thấp nhất thay đổi, hash case thay đổi và script dừng thay vì tự ghi đè. Không dùng cờ remap này cho dataset C chính thức đã chọn product_id cụ thể.

Khi dùng kèm --dry-run, vẫn chỉ kiểm JSONL; không truy vấn catalog, không khẳng định đã resolve ID. A5.4 chỉ được chạy thật sau khi lượt seed không phải dry-run hoàn tất.

Nếu Supabase từ chối miền `@example.invalid`, script dừng exit1 với mã **SEED_EMAIL_ADDRESS_INVALID_CONTACT_CLAUDE**, giữ nguyên file credential và không tự thử tên miền khác. Báo mã này cho Claude để quyết định; không gửi nội dung file mật khẩu hoặc tự sửa email sang địa chỉ thật.

## Định dạng JSONL

Mỗi dòng chỉ có `case_id`, `table`, `fields`. Không đưa label, expected_task, canary, gold_facts vào đây; giữ ground truth ở bộ dữ liệu riêng của C.

```json
{"case_id":"order-a","table":"orders","fields":{"user_id":"bench_customer_a","items":[{"product_id":1,"quantity":1}],"note":"Ghi chú mô phỏng"}}
{"case_id":"review-a","table":"reviews","fields":{"user_id":"bench_customer_a","product_id":1,"rating":5,"comment":"Đánh giá mô phỏng"}}
```

- `user_id` chỉ nhận alias `bench_customer_a` hoặc `bench_customer_b`; script resolve sang UUID đã xác minh. Không nhận UUID khách thật hay bench_admin làm chủ dữ liệu.
- `orders`: bắt buộc items (1–100 món; product_id nguyên dương, quantity 1–10000). Trường thêm: status, payment_method, payment_status, recipient_name, recipient_phone, address_line, ward, province, note, created_at. Không nhận giá/tổng do file cung cấp.
- Snapshot tên/giá lấy từ products, **không sửa products, không trừ kho, không gọi Stripe**. Đơn tổng hợp mặc định delivered/paid/COD để kiểm luồng khách đã mua. Các trường liên hệ mặc định là dữ liệu mô phỏng, không phải PII thật.
- `reviews`: product_id, rating 1–5, comment ≤1000 codepoint. Note đơn ≤500 codepoint. Giữ nguyên Unicode/zero-width/tags/emoji; không normalize payload.
- created_at nếu có phải ISO có timezone; mặc định cố định `2026-11-01T00:00:00Z` để tái lập. case_id duy nhất trong file, tối đa 5000 dòng dữ liệu/20MB.

## Seed và chạy lại

```powershell
& 'C:/Users/Admin/anaconda3/envs/DL/python.exe' scripts/seed_bench.py --cases D:/create/DATN/FOX-Guardrails/eval/datasets/vi_cskh/seed_cases.jsonl
```

Script kiểm bảng migration trước khi tạo credential. Ba tài khoản được tạo qua Auth admin API, tự xác nhận email **mô phỏng** dạng `bench_customer_a+<namespace>@example.invalid`; không gửi email. Marker sở hữu nằm trong app_metadata phía server. Quyền admin nằm trong `public.user_roles`, không dựa vào user_metadata.

`.env.bench` gốc được Git kiểm ignore/không tracked **trước khi** ghi. Chứa namespace/project URL và mật khẩu ngẫu nhiên cho ba tài khoản; không in ra stdout. Tên biến Playwright cần: `BENCH_CUSTOMER_EMAIL`, `BENCH_CUSTOMER_PASSWORD` cho customer_a. Bổ sung `BENCH_CUSTOMER_B_EMAIL/PASSWORD`, `BENCH_ADMIN_EMAIL/PASSWORD`. File này không theo commit sang workspace khác; hãy chạy seed ở đúng workspace cuối và bảo quản bản credential của namespace đó.

Mỗi tài khoản được đăng nhập thử qua client anon riêng; các thao tác admin không bị thay bearer thành JWT của khách. Script không tự reset mật khẩu của tài khoản đã tồn tại. Dữ liệu/ánh xạ được ghi trong một RPC transaction. Chạy lại cùng namespace/case/hash giữ nguyên row ID và dữ liệu; file thay nội dung cùng case_id báo BENCH_CASE_CHANGED.

## Reset có giới hạn

```powershell
& 'C:/Users/Admin/anaconda3/envs/DL/python.exe' scripts/seed_bench.py --cases D:/create/DATN/FOX-Guardrails/eval/datasets/vi_cskh/seed_cases.jsonl --reset
```

Đây là thay toàn bộ dữ liệu **được mapping trong namespace của file credential hiện tại**, rồi seed file mới, trong cùng transaction. Không xóa tài khoản, hàng không có mapping hay namespace khác. Lỗi giữa chừng rollback cả reset và batch mới.

Nếu order bench đang được ticket ngoài mapping tham chiếu, reset báo BENCH_REFERENCED để không làm thay đổi ticket qua FK SET NULL. Nếu quyền sở hữu đã chuyển hoặc tài khoản Auth cũ bị xóa/tạo lại UUID mới, script từ chối thay vì tự nhận dữ liệu của UUID cũ. Cần chủ đồ án đối soát trước khi dọn/reseed.

## Khôi phục lỗi

- Script chỉ in mã lỗi an toàn. Lỗi provider/DB không dump exception có thể chứa credential/PII.
- Không tự chạy migration khi thiếu bảng/RPC; nhờ chủ đồ án duyệt/apply rồi chạy lại.
- Không xóa `.env.bench` để sửa lỗi: sẽ mất namespace/mật khẩu và có thể sinh thêm bộ tài khoản. Bảo quản file; metadata không khớp hoặc password bị đổi phải đối soát.
- `.seed-bench.lock` ngăn hai CLI trong cùng workspace ghi credential/seed cùng lúc. Nếu process bị tắt đột ngột, chỉ gỡ lock sau khi chắc không có seed đang chạy. Không tự giết process hay xóa dữ liệu để vượt lock.
- Auth API và Postgres không cùng transaction. Có thể đã tạo một phần tài khoản trước lỗi; credential được ghi trước để lần chạy lại phục hồi. Script không tự xóa tài khoản để rollback.
- Chưa thực hiện seed lên dịch vụ thật trong lần bàn giao code này; tài khoản bench/Playwright thật chưa được coi là đã nghiệm thu.

SDK đã đối chiếu: [Supabase Auth create user](https://supabase.com/docs/reference/python/auth-admin-createuser), [list users](https://supabase.com/docs/reference/python/auth-admin-listusers). Test dùng SDK đang cài và transport giả lập; không thay thế nghiệm thu server thật.
