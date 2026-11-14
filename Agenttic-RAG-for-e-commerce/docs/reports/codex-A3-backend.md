# Hoàn tất tích hợp backend A3 và health

## Đã làm gì

Rà cả hai nhánh phát hiện chưa có POST /api/reviews, dù form Anti gọi endpoint này. Bổ sung ở file Codex sở hữu theo API E §3: JWT server xác minh, 403 NOT_PURCHASED, rating1–5, comment≤1000 codepoint, lưu nguyên văn. RPC kiểm đơn thuộc user có product_id, không cancelled, đã paid hoặc COD được chấp nhận (cod_pending). Unpaid Stripe/refunded không đủ điều kiện. Không tin user_id trong body.

Review còn phát hiện /health backend luôn healthy và bản frontend chỉ kiểm cấu hình Supabase. Bổ sung probe Supabase anon thật với timeout3s, probe collection Chroma đã tồn tại; degraded nếu lỗi hoặc collection rỗng. Không tạo DB/collection thiếu hoặc trả exception/key.

## File đổi

- web_ui/src/lib/server/review-handlers.ts, src/app/api/reviews/route.ts, tests reviews.test.cjs/review-db.test.cjs.
- database/migrations/2026-11_product_reviews.sql (file mới, không chạy remote).
- rag-service/src/health.py, app/main.py, tests/test_health.py.

## Test và review

- TDD endpoint/migration ban đầu chưa tồn tại; thêm implementation → **5/5 Node/SQL pass**. Reviewer tái hiện product_id vượt PostgreSQL int thành 500; test RED rồi cap2147483647 như order-core, trả400 trước DB. Các test kiểm owner injection, Unicode/codepoint, chưa mua, client grant/RPC và route registration.
- Health RED **6 failed** → **6 passed**. Có HTTP transport thật Supabase SDK kiểm anon bearer/timeout; outage/empty và không create vector DB thiếu.
- Reviewer độc lập kiểm lại hai finding và xác nhận không còn finding trong API/health. Các route bắt buộc thuộc backend đều có.
- TypeScript, ESLint code production liên quan exit0; Next production build với env giả thành công, **28/28**, liệt kê /api/reviews. Không gọi dịch vụ thật. Toàn suite cuối ở handoff tổng hợp.

## Còn mở

- Migration cần duyệt/apply, nghiệm thu form review và health bằng dịch vụ thật sau merge. Không thay UI/route admin.
- Merge main.py phải giữ health mới từ backend thay bản frontend cũ; ghi rõ trong handoff. Không tự merge hai nhánh trong lần giao code.
