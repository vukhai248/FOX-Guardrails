# Báo cáo A7 — Seed benchmark

Base 0cdf528, nhánh feat/a-backend. Tiếp tục toàn bộ phần Codex còn lại theo yêu cầu bàn giao một lần.

## Đã làm gì

- CLI JSONL + dry-run, resolve alias bench, giới hạn input và giữ nguyên Unicode. Không đưa nhãn/ground truth vào bảng công khai.
- Credential ngẫu nhiên tại .env.bench gốc; check-ignore/tracked/symlink trước ghi; namespace/project bound; lock chống CLI đồng thời. Tài khoản có marker app_metadata, role thật trong user_roles và login qua client anon riêng.
- Migration mới chứa bảng mapping private, UUID/hash idempotency và RPC seed/reset nguyên batch trong transaction; chỉ service_role được gọi. Không ghi đè row không mapping, không đụng stock, không thanh toán.
- Reset chỉ namespace hiện tại; khóa row rồi kiểm ownership, từ chối order có ticket tham chiếu. Không tự xóa user hay reset mật khẩu.
- C chưa cung cấp dataset chính thức (eval/datasets mới có .gitkeep); kèm mẫu trung tính và tài liệu [SEED-BENCH](../SEED-BENCH.md).

## File đổi

- scripts/seed_bench.py, scripts/fixtures/seed_bench.sample.jsonl.
- database/migrations/2026-11_seed_bench.sql; .gitignore thêm lock.
- rag-service/tests/test_seed_bench.py, seed-bench-db.test.cjs.
- docs/SEED-BENCH.md, báo cáo/kế hoạch A7 và handoff tổng hợp.

## Kiểm thử

- Trước code: test Python thất bại do module chưa tồn tại; PostgreSQL 4 test thất bại do migration chưa tồn tại. Sau code, fixture Git tạm chứng minh file mật khẩu bị ignore và chạy lại dùng cùng credential; test mock SDK thật chứng minh bearer admin vẫn là service role sau login 3 khách.
- PostgreSQL: **6/6 pass**, gồm chạy hai lần không đổi snapshot, reset giữ hàng thật/namespace khác, rollback cả batch/reset khi lỗi, quyền client bị chặn, collision row, ticket tham chiếu, chuyển ownership/tài khoản tạo lại.
- Dry-run mẫu: exit0, `{"dry_run": true, "valid_cases": 2}`; không tạo credential trong repo hoặc gọi remote.
- Kết quả toàn bộ suite cuối ghi trong [codex-HANDOFF-A.md](codex-HANDOFF-A.md).

## Còn mở / review

- Reviewer độc lập chạy Python/SQL, tìm hai lỗi Important: reset chưa khóa review trước ownership check; mapping tồn tại chưa đối chiếu UUID user sau tạo lại account. Đã thêm khóa review và owner equality. Regression tái hiện lỗi thứ hai RED rồi GREEN; reviewer xác nhận không còn Critical/Important. Khóa đa-session được đọc code, chưa chứng minh bằng PGlite một connection.
- Auth không tham gia transaction DB: credential giữ trước để recovery, không auto delete user. Mất/đổi credential, xóa/tạo lại Auth user hoặc chỉnh sở hữu cần đối soát thủ công; không có đường tự takeover.
- Chưa apply migration, tạo Auth user, ghi credential hoặc seed trên Supabase thật. Chưa có dataset C chính thức. Các bước này nằm trong checklist vận hành sau review/merge; không báo tài khoản hay A5.4 đã chạy thật.
- Không triển khai B/C/A8 hoặc sửa UI; phần bổ sung API review và health phát hiện khi rà tích hợp có báo cáo riêng.
