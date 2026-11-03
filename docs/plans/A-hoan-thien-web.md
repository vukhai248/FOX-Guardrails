# Phần A — Hoàn thiện web e-commerce để làm nền thử nghiệm

> Giao cho: **agent A** · Repo: `D:/create/DATN/Agenttic-RAG-for-e-commerce` · Nhánh: `feat/web-hoan-thien` (mỗi gói một commit hoặc PR nhỏ).
> Mục tiêu: web chạy như một shop thật **đủ để bench guardrails**: có dữ liệu do khách/người ngoài nhập mà bot sẽ đọc, có tool ghi, thanh toán không giả mạo được, log và ticket thật.
> **Không** viết logic guardrail trong web (đó là Phần B). Hợp đồng A↔B ở `00-tong-quan.md` §5.

---

## 1. Hiện trạng (khảo sát 02/11/2026)

Kiến trúc: Next.js 16 (`web_ui/`) → API route `/api/chat` → FastAPI `rag-service/app/main.py` → LangGraph `workflow_1` gồm 3 bước: receive → guardrail (LLM 1 từ: safe/needs_ticket/attack) → master agent (Gemini, vòng tool). Tool hiện có: `product_search`, `product_compare`, `policy_search`, `order_lookup`. Dữ liệu ở Supabase (RLS) và ChromaDB.

Lỗi và lỗ hổng tìm được (đều cần sửa trước khi bench):

| # | Vấn đề | Vị trí | Vì sao quan trọng |
| --- | --- | --- | --- |
| H1 | `session_id` mặc định là `"default-session"` → mọi request không gửi session dùng **chung một thread** bộ nhớ LangGraph | `rag-service/app/main.py:72` | Người này đọc được lịch sử hội thoại của người khác; làm bẩn thực nghiệm đa lượt |
| H2 | Vòng tool hết `max_turns` thì `invoke` **không return** → `None` → `master_node` lỗi | `rag-service/src/e_agents/master_agent.py:53-204` | Ca tấn công tiêu tốn tài nguyên (O8) làm sập request thay vì bị chặn |
| H3 | Đơn Stripe được tạo **ở client** từ `localStorage` và tham số URL `user_id`, `address`; `user_id` mặc định là UUID toàn số 0; không xác minh với Stripe | `web_ui/src/app/checkout-success/page.tsx:14-80` | Ai cũng tạo được đơn "đã thanh toán" giả, gán cho user bất kỳ |
| H4 | `success_url` chứa `user_id` và **địa chỉ** trong URL | `web_ui/src/app/api/stripe/route.ts:45` | PII lọt vào URL, lịch sử trình duyệt, log server |
| H5 | Giá và tổng tiền lấy từ client (cả Stripe lẫn COD) | `api/stripe/route.ts:23-37`, `checkout/page.tsx:297` | Sửa giá được |
| H6 | Trừ tồn kho ở client | `checkout-success/page.tsx:82+` | Bảng `products` chỉ có policy SELECT nên lệnh này thất bại im lặng hoặc sai |
| H7 | Review chỉ hiển thị, **không có form gửi**; bot **không đọc** review | `products/[id]/page.tsx:226-871`; `rag-service/src/d_tools/*` | Bề mặt chèn gián tiếp chính của CSKH chưa tồn tại thật |
| H8 | `shipping_address` là một chuỗi tự do trộn tên, SĐT, ghi chú | `database/setup.sql:58` | Không tách được "ghi chú cho shipper" (dữ liệu không tin cậy) khỏi địa chỉ (PII) |
| H9 | `chat_logs` không được ghi ở đâu; trang admin rơi về `MOCK_ORDERS`/`MOCK_TICKETS` | `admin/page.tsx:96-474` | Không có dữ liệu thật cho dashboard/điều tra |
| H10 | `/api/chat` **tự trả lời giả** khi FastAPI lỗi ("Mock Fallback") | `web_ui/src/app/api/chat/route.ts:49-120` | Khi bench, nếu backend chết thì đang đo câu trả lời giả mà không biết |
| H11 | Chat-widget render Markdown nguyên văn (link, ảnh) | `web_ui/src/components/chat-widget.tsx` (~dòng 628) | Link phishing/ảnh exfil bấm hoặc tự tải được (O1, O5) |
| H12 | Không có tool ghi nào cho bot | `workflow_1.py:40-52` | Thiếu bề mặt "tấn công tool" (T2.10) |

Điểm cần giữ: `_mask_pii_address` + thẻ `<untrusted_customer_note>` trong `order_lookup.py` là một phòng thủ mức prompt. **Không xoá**, chuyển ra sau cờ cấu hình để làm arm G1 (xem A4).

---

## 2. Các gói việc

Thứ tự đề xuất: A0 → A1 → (A2 ‖ A3) → A4 → A5 → A6 → A7. A8 chỉ làm nếu còn thời gian.

### A0 — Chạy được local + tài liệu chạy

- Viết `docs/RUN.md`: biến môi trường cần có (không ghi giá trị bí mật), lệnh chạy `rag-service` (cổng 8080 như `api/chat/route.ts` đang mặc định), lệnh chạy web, cách nạp ChromaDB, cách chạy `setup.sql` và migration mới.
- Thêm `GET /health` kiểm cả Supabase lẫn Chroma.
- **Xong khi:** người khác làm theo `docs/RUN.md` trên máy sạch và chat được một câu hỏi sản phẩm.

### A1 — Sửa lỗi nền (H1, H2, H10)

- H1: client sinh `session_id` (UUID, lưu `localStorage` theo user). Server: thiếu thì tự sinh `uuid4`. `thread_id = f"{user_id or 'anon'}:{session_id}"`.
- H2: hết `max_turns` thì trả câu trả lời an toàn ("Xin lỗi, yêu cầu quá phức tạp…") + ghi cờ `loop_exhausted=true` vào kết quả.
- H10: mock fallback chỉ bật khi `NEXT_PUBLIC_ALLOW_MOCK_CHAT=true` (mặc định **tắt**). Tắt thì trả 503 có thông báo rõ.
- **Xong khi:** có test pytest cho H1 (2 user khác nhau không thấy lịch sử của nhau) và H2 (tool loop giả → không `None`); tắt backend thì web báo lỗi, không trả lời giả.

### A2 — Thanh toán thật (Stripe test mode) + tạo đơn phía server (H3–H6)

Chỉ dùng **khoá test** của Stripe. Không bao giờ dùng khoá live.

1. Migration `database/migrations/2026-11_payment_and_address.sql`:
   - `orders`: thêm `payment_method` (`stripe` | `cod`), `payment_status` (`unpaid` | `paid` | `cod_pending` | `refunded` | `failed`), `stripe_session_id` (unique, nullable), `paid_at`, `recipient_name`, `recipient_phone`, `address_line`, `ward`, `province`, `note` (ghi chú giao hàng, tối đa 500 ký tự). Giữ `shipping_address` (ghép từ các trường mới) để không vỡ code cũ.
   - Hàm SQL `decrement_stock_for_order(order_id uuid)` (security definer, chạy trong transaction, báo lỗi nếu thiếu hàng).
2. `POST /api/orders` (server, Next.js route): xác thực JWT Supabase từ header; **lấy giá từ bảng `products`** bằng service role; kiểm tồn kho; tạo đơn `status=pending`.
   - `stripe`: tạo Checkout Session với `metadata.order_id`; `success_url=/checkout-success?order_id=<id>&session_id={CHECKOUT_SESSION_ID}`. URL **không chứa PII**.
   - `cod`: `payment_status=cod_pending`, trừ kho ngay.
3. `POST /api/stripe/webhook`: xác minh chữ ký (`STRIPE_WEBHOOK_SECRET`). Khi có `checkout.session.completed` thì `payment_status=paid`, `status=processing`, gọi `decrement_stock_for_order`. Xử lý **idempotent** theo `stripe_session_id`.
4. `checkout-success`: đọc đơn qua `GET /api/orders/<id>` (kiểm chủ sở hữu) và hiển thị trạng thái; chờ webhook thì poll vài giây. **Bỏ** toàn bộ phần tạo đơn ở client.
5. Form checkout tách trường: người nhận, SĐT, địa chỉ, phường/xã, tỉnh/thành, **ghi chú giao hàng**.
- **Xong khi:** (a) chạy `stripe listen --forward-to localhost:3000/api/stripe/webhook`, thanh toán bằng thẻ test 4242… → đơn `paid` và tồn kho giảm; (b) sửa giá ở DevTools không đổi được tổng tiền; (c) mở `/checkout-success?order_id=<đơn người khác>` → 404; (d) không còn PII trong URL.

### A3 — Bề mặt dữ liệu do khách nhập (H7, H8)

- Form gửi review ở trang sản phẩm: chỉ user đăng nhập; chỉ người **đã có đơn chứa sản phẩm đó** (kiểm ở server qua `POST /api/reviews`); rating 1–5; comment ≤ 1.000 ký tự. Lưu **nguyên văn**, không lọc. Lọc là việc của guard, và phải giữ nguyên để test.
- Trang tài khoản: khách xem và sửa **ghi chú giao hàng** của đơn còn `pending`.
- Ticket: giữ luồng tạo ticket hiện có ở widget/account; thêm trường `note` hiển thị trong admin.
- **Xong khi:** tạo được review và ghi chú chứa ký tự đặc biệt (zero-width, Unicode tags, emoji) và đọc ra **đúng từng byte** (có test so sánh codepoint).

### A4 — Tool cho bot đọc/ghi dữ liệu do người ngoài nhập (H7, H12)

1. `rag-service/src/d_tools/tool_result.py`: lớp `ToolResult(tool: str, trusted: str, untrusted: list[Segment])`, với `Segment(source: str, ref_id: str, text: str)`. `source` thuộc {`review`, `order_note`, `ticket_note`, `product_desc`}. Có `render() -> str` và `__str__ = render`, để `master_agent.py:169-182` vẫn chạy như cũ. B9 sẽ duyệt `untrusted` để kiểm từng đoạn **trước khi** render.
2. Tool mới `product_reviews(product_id: int | None, product_name: str | None, limit: int = 5)`: trả review mới nhất (rating + comment) dưới dạng `untrusted` segment `source=review`.
3. `order_lookup`: trả thêm `recipient_name`, `recipient_phone`, địa chỉ có cấu trúc, `payment_status`, `note` (segment `source=order_note`). Chuyển `_mask_pii_address` + thẻ `<untrusted_customer_note>` ra sau cờ `LEGACY_PROMPT_DEFENSE=on|off` (mặc định `on` để giữ hành vi hiện tại; bench sẽ bật/tắt theo arm).
4. Tool ghi `create_support_ticket(category, note, order_id=None)`: cần đăng nhập; insert qua client RLS của user; trả `ticket_id`. Cập nhật schema tool, `select_skill` và skill markdown (khi nào được tạo ticket).
5. `select_skill`: thêm từ khoá "đánh giá", "review", "mọi người nói gì", "có tốt không". Trả thêm tên skill (để B9 map sang `intent`).
6. Cờ cho thực nghiệm (Phần C cần để dựng các arm G0/G1):
   - `LEGACY_LLM_GUARDRAIL=on|off`: `off` thì `guardrail_node` bỏ qua guardrail LLM cũ và luôn coi là `safe`.
   - `BENCH_RECORD=1`: bọc `LLMService.call_gemini` / `call_groq` để ghi **payload gửi đi** (messages) ra `bench_records/<ngày>.jsonl` (gitignore). Dùng để đo PII rò tới nhà cung cấp LLM. Mặc định tắt.
   - `BENCH_TEMPERATURE=<số>`: ghi đè `generation.temperature` khi bench.
7. Điểm cắm cho Phần B (chỉ tạo khung, **chưa** có logic): `rag-service/src/guard_client.py` với 3 hàm `guard_input(text, ctx)`, `guard_context(segment, ctx)`, `guard_output(text, ctx)`. Khi `FOX_GUARD_MODE=off` thì hàm trả nguyên văn. Gọi 3 hàm này ở: `workflow_1.guardrail_node` (input), `master_agent` ngay sau khi tool trả `ToolResult` (context, mỗi segment), và trước khi trả `final_answer` (output). Đọc thêm `FOX_GUARD_ARM` để chọn arm (giá trị do C định nghĩa).
- **Xong khi:** hỏi "Mọi người đánh giá iPhone 16 thế nào?" → bot gọi `product_reviews`; hỏi "Tạo ticket báo đơn giao chậm" → ticket xuất hiện trong DB; có unit test cho `ToolResult.render()` không đổi output cũ của `order_lookup` khi `LEGACY_PROMPT_DEFENSE=on`.

### A5 — Log hội thoại, ticket, admin dùng dữ liệu thật (H9)

- `rag-service` ghi `chat_logs` cho mỗi lượt: `session_id`, `user_id`, `role`, `message`, `tool_used`, `risk_level`, cột mới `guard_decision_ids` (text[]). Khi guard bật, `message` phải là **bản đã che PII** do guard trả về. Đây là yêu cầu "bản ghi giám sát được che PII trước khi lưu".
- Trang admin: chỉ dùng mock khi `NEXT_PUBLIC_ALLOW_MOCK_ADMIN=true`; mặc định đọc thật qua `/api/admin/*`. Có tab "Hội thoại" xem `chat_logs` theo phiên.
- **Xong khi:** chat 3 lượt → thấy đủ 3 dòng trong admin; tắt cờ mock thì không còn số liệu giả.

### A6 — Render an toàn trong chat-widget (H11)

- `markdown-to-jsx` overrides:
  - `img`: chỉ cho domain trong `NEXT_PUBLIC_LINK_ALLOWLIST` (mặc định: domain shop + CDN ảnh sản phẩm). Ngoài danh sách thì hiển thị alt text kèm nhãn "ảnh ngoài đã bị ẩn".
  - `a`: ngoài allowlist thì hiển thị dạng text (không bấm được) kèm cảnh báo.
  - Không render HTML thô.
- So domain sau khi đổi về Punycode/ASCII, để chặn `аmazon` Cyrillic.
- Cờ `NEXT_PUBLIC_SAFE_RENDER=true|false` để thực nghiệm đo được cả hai trạng thái.
- Hiển thị nhãn khi guard chặn hoặc chuyển kiểm duyệt (dữ liệu nhãn lấy từ response `/chat`: thêm trường `guard: {action, decision_id}`).
- **Xong khi:** có test component với 5 chuỗi: link nội bộ, link ngoài, ảnh ngoài, link homoglyph, HTML thô.

### A7 — Seed dữ liệu bench (cơ chế; nội dung do C cung cấp)

- `scripts/seed_bench.py --cases eval/datasets/vi_cskh/seed_cases.jsonl --reset`:
  - Tạo 3 tài khoản test: `bench_customer_a`, `bench_customer_b`, `bench_admin`. Mật khẩu sinh ngẫu nhiên, ghi vào `.env.bench` (đã gitignore). Không in ra màn hình.
  - Nạp đơn hàng (kèm `note`) và review theo file JSONL. Mỗi dòng có `case_id`, `table`, `fields`.
  - Ghi bảng ánh xạ `bench_cases(case_id, table, row_id)` (RLS deny-all), để ground truth không bao giờ vào ngữ cảnh của bot.
  - `--reset` chỉ xoá hàng có trong `bench_cases`.
- **Xong khi:** chạy 2 lần liên tiếp cho kết quả giống nhau; `--reset` không đụng dữ liệu không thuộc bench.

### A8 — (Nếu còn thời gian) tính năng web thật bổ sung

Theo thứ tự giá trị cho đồ án: (1) yêu cầu đổi/trả hàng, tạo ticket có `order_id` (thêm tool ghi); (2) hỏi-đáp sản phẩm (Q&A) công khai, thêm một bề mặt chèn; (3) seller portal sửa mô tả sản phẩm (bề mặt `product_desc`); (4) email xác nhận đơn (chỉ log, không gửi thật).

---

## 3. Quy tắc cho agent A

- Không commit `.env*`, khoá Stripe, khoá Supabase. Chỉ dùng khoá **test**.
- Mỗi gói: test tự động (pytest cho Python, ít nhất test API route cho Next.js) + cập nhật `docs/RUN.md` nếu cách chạy đổi.
- Không sửa prompt hệ thống của bot ngoài phần cần cho tool mới. Prompt thay đổi làm lệch baseline thực nghiệm. Nếu buộc phải sửa thì ghi vào `docs/CHANGELOG-bench.md`.
- Báo lại cho bạn (chủ đồ án) sau mỗi gói, dạng 3 dòng: đã làm gì, chạy thử thế nào, còn gì chưa xong.

## 4. Bạn (chủ đồ án) phải giải thích được

- Vì sao đơn hàng phải tạo ở server và xác nhận bằng webhook (H3–H5).
- Vì sao `ghi chú giao hàng` là **dữ liệu không tin cậy** dù nó đến từ chính DB của shop.
- RLS chặn được gì (đọc đơn người khác) và **không** chặn được gì (bot bị dụ nói sai, đòi CCCD).
- `ToolResult` tách `trusted`/`untrusted` để làm gì (điều kiện để guard chỉ cắt đoạn bị chèn).
