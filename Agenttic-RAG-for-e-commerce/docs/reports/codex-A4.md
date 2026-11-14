# Báo cáo A4 — Tool đọc/ghi và điểm cắm guard

Ngày: 03/11/2026. Nhánh: `feat/a-backend`; base `f1733bf`; worktree `D:/create/DATN/.worktrees/a1-backend`.

## 1. Đã làm gì

- Đọc lại session **Hoàn thiện từng phần Opus**: A1/A2 đã commit; A2 dừng tại f1733bf. Tiếp tục đúng gói A4, không sửa frontend hay plan của Opus.
- Thêm `ToolResult(tool, trusted, untrusted)` và `Segment(source, ref_id, text)`. `render()`/`str()` chỉ ghép sau khi agent gọi guard từng segment. Layout tùy chọn và renderer giữ nguyên output legacy của order_lookup; raw customer text vẫn ở segment để B kiểm trước masking/render.
- `product_reviews` dùng client anon đọc rating/comment mới nhất, giới hạn 1–20; resolve tên duy nhất hoặc yêu cầu chọn mã sản phẩm. Comment giữ nguyên codepoint trong segment review; không đọc user_id/email khách đánh giá.
- `order_lookup` chi tiết trả structured recipient/address/payment/note; vẫn lọc owner. Masking/wrapper cũ mặc định on, flag off trả raw cho bench; test snapshot chứng minh output đơn legacy không đổi. Ghi chú là segment order_note.
- `create_support_ticket` bắt buộc user và JWT, dùng client RLS, kiểm owner của order_id trước insert, validate category/UUID/note. Không dùng admin fallback cho việc ghi, không echo note trong kết quả, trả ticket_id sau insert thành công. Nguồn danh tính do agent inject; schema/args không nhận identity hoặc JWT từ LLM.
- Đăng ký hai tool vào registry/workflow; skill mới và tên skill/intent được đưa vào state và guard context. Không sửa FULL_MASTER_PROMPT, có CHANGELOG-bench.
- Guard hooks input/context/output đã nối, gồm output bình thường, hết vòng và từ chối. FOX_GUARD_MODE mặc định off pass-through; mode khác off báo chưa triển khai, không giả vờ đã bảo vệ. FOX_GUARD_ARM được truyền như nhãn, chưa gán nghĩa các arm.
- Legacy LLM guard có thể tắt riêng. Gemini/Groq hỗ trợ BENCH_TEMPERATURE và BENCH_RECORD; ghi messages cùng payload SDK ngay trước mỗi lần thử network, không ghi header/key. Lỗi ghi record thì không gửi request không được ghi. Record local được gitignore.
- `/chat` thêm guard mặc định đúng E §3: `{action:"allow", decision_id:null, flags:[]}` khi FOX off.

## 2. File đổi

- `rag-service/src/d_tools/`: tool_result.py, product_reviews.py, support_ticket.py, account/order_lookup.py, registry __init__.py.
- `rag-service/src/e_agents/master_agent.py`, `src/g_pipelines/workflow_1/workflow_1.py`, `app/main.py`.
- `rag-service/src/guard_client.py`, `src/bench.py`, `src/LLMService.py`.
- Hai skill markdown mới trong `src/f_prompts/skills/`; `tests/conftest.py` và tests/test_a4_{tools,pipeline,bench}.py.
- `.gitignore`, `docs/CHANGELOG-bench.md`, báo cáo/kế hoạch A4 và bàn giao requests.md.
- Không thêm migration; không chạy SQL lên Supabase hoặc setup.sql; không đọc/in/ghi secret; không sửa package.json/UI.

## 3. Lệnh test và output thật

Python mặc định thiếu FastAPI; đã dùng đúng env DL của session trước. Baseline trước code:

```powershell
& 'C:/Users/Admin/anaconda3/envs/DL/python.exe' -m pytest -q
```

Tại `rag-service`: **16 passed in 1.10s**.

TDD: tools **9 failed → 9 passed**; pipeline/guard **10 failed → xanh**; bench **9 failed → xanh**. Có test bổ sung luồng chat thật, SDK JWT header và input lỗi (input malformed RED 2 failed → xanh). Toàn suite trước review:

```text
...................................................                      [100%]
51 passed in 1.74s
```

`git diff --check`: exit 0. `git check-ignore -v --no-index` cho bench_records và .env.bench: khớp ignore. Chưa tạo record chứa dữ liệu thật trong repo.

Các dependency remote được thay tại transport: LangGraph, FastAPI, MasterAgent, code tool, Supabase SDK và model/schema Gemini vẫn chạy thật. Hai câu hỏi nghiệm thu chạy qua `/chat` với tool-call LLM giả lập; không tuyên bố model thật tự chọn tool đúng từ kết quả này.

## 4. Việc còn mở / quyết định

- Chưa gọi LLM/Supabase thật; cần nghiệm thu hai câu hỏi với service thật sau ghép frontend và áp dụng migration A2 được duyệt. Test HTTP chứng minh header JWT/anon đúng ở ranh giới SDK, chưa thay thế kiểm RLS trên Supabase thật.
- A2 vẫn còn kiểm tích hợp Stripe/migration như báo cáo trước. Không merge/rebase/push hai nhánh ở lượt A4.
- Chưa làm A5-backend/A7. Chưa ghi chat_logs, chưa tạo tài khoản bench/mật khẩu. Record bench là opt-in và có thể chứa raw text để đo rò PII; không dùng nó thay cho log giám sát đã che PII của A5.
- Masking legacy chỉ giữ nguyên cơ chế địa chỉ/số điện thoại cũ; không coi đây là bộ che mọi loại PII (tên, email, v.v.). Phần B mới triển khai guard thật và truyền decision metadata.
- Đơn legacy đã qua migration A2 có mặc định unpaid/cod và địa chỉ mới null. Không suy diễn trạng thái thanh toán lịch sử từ các mặc định này; giữ output cũ cho đơn đó. Test snapshot bao gồm cả row cũ trước migration lẫn các default sau migration. Đơn có trường địa chỉ/ghi chú mới hoặc trạng thái thanh toán thực khác unpaid có thêm thông tin chi tiết; danh sách đơn gần đây giữ format cũ.
- Note ticket giới hạn 2000 ký tự ở tool; category dùng đúng enum DB, đơn giao chậm dùng other. Không thêm workflow ticket/refund hoặc guard policy mới.
- `docs/RUN.md` thuộc frontend: ghi đề nghị cập nhật tại requests.md thay vì sửa chéo.
- Payload record dùng ngày UTC, có messages và payload SDK đã chuyển đổi; retry có thể chưa đến nhà cung cấp nên chỉ đếm là attempted egress. Không log credential vận chuyển.

Nguồn đối chiếu kỹ thuật: [Google Gen AI SDK](https://github.com/googleapis/python-genai), [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security); đã kiểm SDK đang cài bằng test local.

### Sửa theo review

- Reproduce lỗi signature nhị phân của Gemini khi BENCH_RECORD bật bằng luồng call_gemini đầy đủ (RED 1 failed). Record dùng tagged base64 để khôi phục nguyên bytes; payload SDK vẫn giữ bytes gốc. Regression đã qua.
- Bổ sung migrated-default legacy snapshot (RED 1 failed), giữ format cũ như quyết định phía trên.
- HTTP fallback khi provider trả rỗng cũng đi qua guard_output (RED HTTP 1 failed), tránh một nhánh trả lời bỏ qua điểm cắm.
- Tăng chất lượng fixture: registry/tool thật được import, chỉ thay constructor retriever từ xa; không còn thay toàn registry như A1.
- Kiểm lại sau sửa: **53 passed in 1.66s**; compileall các file/module Python đổi exit 0; `git diff --check` exit 0. Không có build/TypeScript mới vì A4 chỉ đổi Python và tài liệu, không đổi JavaScript.

### Kết quả review độc lập cuối

- Reviewer tự chạy lại **53 passed in 1.78s**, whitespace check qua; không còn finding Critical/Important/Minor. Hai schema tool mới được kiểm bằng Google SDK đang cài. Kết luận đủ điều kiện commit checkpoint code A4, chưa phải nghiệm thu dịch vụ thật/merge.
- Chấp nhận phân định live Supabase/RLS/ticket persistence và tương thích DB đã migrate: chưa chạy trực tiếp; cần nghiệm thu sau duyệt migration A2. Chi phí nếu chỉ dựa test offline là chưa phát hiện lệch cấu hình/quyền/schema trên server thật.
- Chấp nhận phân định model thật chọn tool và nhà cung cấp nhận payload: chỉ kiểm transport giả lập và attempted request ở SDK boundary. Chi phí là phải chạy hai câu hỏi nghiệm thu với model/service thật trước chốt end-to-end.
- FOX detection/PII masking/policy/mode bật/decision metadata thuộc B; scaffold không giả định đã có bảo vệ. Chi phí: chưa chạy được arm có guard thật cho tới B.
- Frontend integration, chat_logs/admin A5, seed A7 và Stripe acceptance vẫn ở gói/nhánh tương ứng; không tự mở rộng hoặc merge trong A4. Giữ nhánh/worktree để chủ đồ án nghiệm thu rồi chuyển gói tiếp.
