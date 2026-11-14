# Báo cáo A5-backend — Nhật ký hội thoại thật

Ngày: 03/11/2026. Nhánh feat/a-backend, worktree D:/create/DATN/.worktrees/a1-backend. Base e6fb8bd (đã sửa C1/C2 của Claude); A4 tại ad5658d.

## 1. Đã làm gì

- Đọc review mới của Claude trong codex-phanA.md: A1 đạt, A2/A4 đạt code; chưa thay thế nghiệm thu với Supabase/Stripe thật. Đã sửa C1/C2 tại commit e6fb8bd, có báo cáo riêng codex-C1-C2.md.
- `/chat` ghi mỗi exchange hoàn tất thành 2 dòng `user` và `agent` (đúng enum DB), trong một insert batch. Ba lượt chat tạo 6 dòng, đủ cả nội dung khách và bot để admin xem hội thoại. Không replay lịch sử cũ vào DB mỗi lượt.
- Lưu session_id của request (UUID mới nếu thiếu), user_id xác minh từ JWT, message, tên tool của lượt hiện tại, risk_level hợp lệ low/medium/high, guard_decision_ids và created_at UTC. Timestamp agent sau user 1µs để thứ tự một cặp rõ ràng.
- HTTP session_id giới hạn 100 ký tự đúng schema DB; chuỗi dài hơn bị 422 trước gọi workflow, tránh caller cố dùng chuỗi dài để chat thành công mà không có audit log. UUID của frontend/A1 vẫn phù hợp.
- `turn_tool_calls` và `guard_decision_ids` được reset ở receive_node để không kéo tool/decision từ lượt trước; lịch sử LangGraph cũ vẫn giữ để agent dùng. Không lưu tool arguments/output/raw state/token vào chat_logs.
- Thêm `guard_client.LogText` và `guard_log` riêng cho text giám sát: off giữ baseline; enabled chưa có B thì từ chối chuẩn bị log. Writer chỉ nhận message do hook trả, chuẩn bị cả hai message xong mới insert; không fallback về raw nếu guard lỗi. Không dùng nhầm câu trả lời đã hoàn nguyên PII làm audit message. B sẽ triển khai che PII không hoàn nguyên và trả decision IDs tại hook này.
- Lỗi chuẩn bị/ghi log chỉ báo mã cố định CHAT_LOG_PREPARE_FAILED/CHAT_LOG_WRITE_FAILED, không in exception/PII/JWT. Giữ kết quả chat/tool đã hoàn tất để tránh client retry tạo ticket lần nữa. Chưa có hàng đợi bền vững/retry log.
- Migration mới chỉ thêm `guard_decision_ids text[] NOT NULL DEFAULT '{}'`, index lọc phiên/thời gian, bật RLS, thu hồi quyền client và cấp SELECT/INSERT cho service_role. Không xóa dữ liệu, không sửa migration A2, không chạy SQL lên Supabase.
- C2: admin chat-logs **dạng object `{chat_logs,total,limit,offset}`** là chuẩn mới được Claude chấp nhận. A5 không sửa route/admin UI của Anti.

## 2. File đổi

- database/migrations/2026-11_chat_logs_guard.sql.
- rag-service/src/chat_logging.py, src/guard_client.py, app/main.py, src/g_pipelines/workflow_1/workflow_1.py.
- rag-service/tests/test_chat_logging.py, tests/chat-logs-db.test.cjs và fixture offline conftest.py.
- docs/reports/codex-A5-plan.md, codex-A5.md, requests.md.

## 3. Lệnh kiểm thử và output thật

Trong rag-service (Python mặc định không có FastAPI, dùng env DL như các gói trước):

```powershell
& 'C:/Users/Admin/anaconda3/envs/DL/python.exe' -m pytest -q
& 'C:/Users/Admin/anaconda3/envs/DL/python.exe' -m compileall -q app src/chat_logging.py src/guard_client.py src/g_pipelines/workflow_1
```

TDD log RED **8 failed** trước code; session length RED HTTP 200 khác 422 trước khi thêm bound. Toàn suite cuối sau review và bổ sung transport/integration test:

```text
.....................................................................    [100%]
69 passed in 2.85s
```

Compileall exit 0. Test giữ FastAPI/LangGraph/tool code thật; chỉ thay dịch vụ từ xa. Có HTTP transport thật của Supabase SDK chứng minh insert batch một POST bằng service-role, payload whitelist, Unicode giữ nguyên và không lưu JWT/tool args. Có test guard-on dùng bản che riêng thay vì câu trả lời đã hoàn nguyên; guard thiếu/lỗi thì không insert một phần/raw.

Tại repo root:

```powershell
$env:PGLITE_MODULE_PATH='D:/create/DATN/.test-tools/a2/node_modules/@electric-sql/pglite'
node --test rag-service/tests/chat-logs-db.test.cjs
```

TDD migration RED do file chưa tồn tại; GREEN **1 test, 1 pass, 0 fail, 0 skipped**. PostgreSQL nhúng thực thi migration hai lần, giữ row cũ và default [], service_role đọc/ghi được, anon/authenticated bị từ chối SELECT/INSERT, enum/null constraint còn hiệu lực. Không thực thi setup.sql ngay cả trong test.

Kiểm tra cuối cả regression C1/A2 và migration A5:

```powershell
node --test web_ui/src/lib/server/__tests__/*.test.cjs rag-service/tests/chat-logs-db.test.cjs
```

**58 tests, 58 pass, 0 fail, 0 skipped**; `git diff --check` exit 0. TypeScript/lint C1 đã qua trước commit e6fb8bd; A5 không đổi TypeScript.

## 4. Còn mở / quyết định

- Migration A5 cần Claude duyệt và chủ đồ án chạy. Chưa chạy lên Supabase; trước khi apply, log có thể thất bại do thiếu cột và sẽ có mã lỗi vận hành. A2 chỉ được apply sau khi đã merge frontend như review mới yêu cầu.
- Chưa có B: FOX enabled vẫn chưa triển khai. Hook guard_log là điểm bàn giao, không phải detector/PII masker; enabled không tự dùng reply hoặc raw message nếu thiếu bản che. Phải kiểm end-to-end lại khi B cung cấp masking/decision metadata.
- Guard off giữ raw baseline theo arm; BENCH_RECORD A4 độc lập với chat_logs, không thay thế giám sát A5. Không tự dùng record bench làm nguồn log.
- Ghi log đồng bộ bằng một POST qua Supabase client hiện có. DB không khả dụng có thể làm chậm request đến timeout của SDK; lỗi không làm lặp lại tool, nhưng log thất bại chưa được khôi phục tự động. Chưa tuyên bố độ bền/latency production.
- Theo review, test lỗi ghi log đã được nâng lên chạy code create_support_ticket thật với transport RLS giả lập: dù log lỗi, HTTP vẫn 200 và chỉ có đúng một lần insert ticket.
- Giữ session_id đúng request và user_id được xác minh. Theo A1, frontend sinh UUID riêng theo user; admin hiện nhóm theo session_id, nên nếu người gọi cố dùng cùng chuỗi session cho hai user thì admin có thể hiển thị chung nhóm (khách không được quyền đọc log). Việc thay filter/nhóm admin không thuộc A5-backend.
- Chưa smoke admin browser với DB thật hoặc dùng model/provider thật. Test local chứng minh code/payload/quyền SQL fixture; chưa chứng minh cấu hình Supabase đang chạy.
- A7 chưa thực hiện; chưa tạo tài khoản/password bench. Bàn giao ghi nhớ .env.bench tại gốc repo và bench_admin role trong user_roles theo Claude.

### Review độc lập trước checkpoint

- Đã đọc cả C1/C2 commit và toàn bộ A5 runtime/migration/tests. Reviewer tự chạy **58 Node/SQL pass**, cuối cùng **69 pytest pass**. Không có finding Critical/Important hoặc Minor còn mở.
- Minor về test chưa chứng minh ticket không bị tạo lặp đã sửa bằng code tool thật/transport RLS giả; reviewer kiểm lại đúng một insert và HTTP 200 khi log lỗi.
- Reviewer kiểm lại bound session_id 100 ký tự trước workflow; không còn đường chat thành công nhưng cố tình vượt giới hạn cột để bỏ audit.
- Chấp nhận phân định chất lượng masking/detection thật thuộc B, hiện enabled từ chối ghi nếu thiếu triển khai; cần nghiệm thu lại khi B đã nối, chưa được coi A5 là bộ che PII hoàn chỉnh.
- Chấp nhận phân định Supabase/migration deployed/admin rendering/provider thật: chưa chạy môi trường live; cần chủ đồ án duyệt/chạy migration và QA sau merge. Test offline không thay thế nghiệm thu đó.
- Chấp nhận phân định recovery/latency log đồng bộ và nhóm admin khi session_id cố trùng giữa user: đã ghi giới hạn cụ thể phía trên, không tự mở rộng qua queue/UI trong gói này.
- Chấp nhận phân định đối soát tài chính sau acknowledge lỗi webhook vĩnh viễn: C1 chỉ sửa retry theo review Claude, không tự refund hay sửa đơn. Giữ đối soát thủ công theo order_id/mã lỗi.
- Exception disclosure của endpoint baseline nằm ngoài patch này; log writer mới chỉ phát mã cố định. Không tuyên bố endpoint baseline đã được rà soát toàn diện.
