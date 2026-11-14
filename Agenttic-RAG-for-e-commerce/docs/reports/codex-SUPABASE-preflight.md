# Supabase preflight — 03/11/2026

> Cập nhật sau: blocker đã được Claude xử lý bằng migration 0 tại 4067561. Sáu migration và seed đã chạy trên Supabase thật; xem codex-SUPABASE-execution.md. Nội dung dưới đây giữ làm bằng chứng kiểm tra trước khi bổ sung.

## 1. Đã kiểm tra

- Main đã merge tại b0eea73; không chỉnh code hoặc dữ liệu ChromaDB đang có thay đổi.
- Backup thật: D:/backups/supabase/20261103-213431-pre-migration. Có database.dump (snapshot chính), schema.sql, data.sql, roles.sql và manifest SHA-256.
- Khôi phục thử public/auth trên PostgreSQL 17 + pgvector local: 32 bảng, đủ pre-data/data/post-data, mọi số dòng khớp archive. Không kiểm replay ownership/ACL hay toàn bộ dịch vụ Supabase; Storage file contents không nằm trong backup DB.
- Kết nối đọc Supabase thật thành công; không áp dụng bất kỳ migration hoặc seed nào lên remote.

## 2. Blocker trong hướng dẫn 5 migration

Kết quả truy vấn read-only `to_regclass` trên Supabase thật:

```text
orders|t
products|t
reviews|t
chat_logs|f
user_roles|f
support_tickets|f
bench_cases|f
```

bench_cases vắng mặt là bình thường trước migration số 4. Ba bảng chat_logs/user_roles/support_tickets lại là prerequisite chưa được tạo bởi bất kỳ file nào trong 5 migration đã duyệt.

- database/migrations/2026-11_chat_logs_guard.sql:4 ALTER TABLE public.chat_logs nên thất bại ngay.
- scripts/seed_bench.py:183 upsert user_roles; thiếu bảng sẽ khiến seed không hoàn tất ngay cả khi vượt qua Auth.
- web_ui/src/lib/server/auth.ts:51 đọc user_roles; admin authorization cần bảng này.
- database/migrations/2026-11_seed_bench.sql:38 dùng support_tickets trong nhánh reset; công cụ ticket của web cũng cần bảng này.
- DDL của ba bảng có trong database/setup.sql:73,87,109, nhưng đầu file DROP TABLE CASCADE. KHÔNG chạy file này trên remote.

## 3. Tái hiện trên bản khôi phục local

Chạy đúng nội dung file từ main, đúng thứ tự, trên container kiểm tra riêng; các lệnh SQL dùng ON_ERROR_STOP=1:

```text
LOCAL_MIGRATION_OK 2026-11_payment_and_address.sql
LOCAL_MIGRATION_FAILED 2026-11_chat_logs_guard.sql
ERROR: relation "public.chat_logs" does not exist
```

Dừng ở số 2; chưa thử số 3–5 trong lượt này. Container local đã dừng/xóa. JSON output lưu trong thư mục backup: migration-preflight.json. Migration số 1 chỉ chạy local, KHÔNG chạy remote.

## 4. Việc cần Claude bổ sung

- Tạo và duyệt một migration prerequisite additive cho chat_logs, user_roles, support_tickets, gồm đúng schema, RLS, quyền server và policy cần thiết; không sao chép phần DROP từ setup.sql.
- Kiểm lại toàn bộ chuỗi prerequisite + 5 migration trên bản khôi phục trước khi áp dụng remote; kiểm user_roles với Auth/seed và support_tickets với luồng ticket/reset.
- Sau đó mới chạy chuỗi đã duyệt trên Supabase, seed theo lệnh đã giao; nếu gặp SEED_EMAIL_ADDRESS_INVALID_CONTACT_CLAUDE thì dừng, không tự đổi domain.
- checkout.session.expired trên webhook Stripe test: chưa kiểm/chưa thay đổi trong lượt preflight này.

Không có database remote mutation, migration, seed hoặc thay đổi Stripe từ lượt kiểm tra này.
