# 🚀 Hướng Dẫn Cài Đặt & Chạy Local — Agentic RAG E-Commerce

Tài liệu hướng dẫn triển khai và vận hành hệ thống cục bộ (local) dành cho nhà phát triển và kiểm thử viên.

---

## 1. 🏗️ Tổng quan kiến trúc hệ thống

```text
               ┌────────────────────────────────────────────────────────┐
               │         Frontend: Next.js 16 (App Router)              │
               │         URL: http://localhost:3000                     │
               └───────────────────┬────────────────────────────────────┘
                                   │
                                   ▼
        ┌──────────────────────────────────────────────────────────────┐
        │  Backend RAG Service: FastAPI + LangGraph Workflow           │
        │  URL: http://127.0.0.1:8080                                  │
        └──────────────┬───────────────────────────────┬───────────────┘
                       │                               │
                       ▼                               ▼
        ┌─────────────────────────────┐  ┌─────────────────────────────┐
        │  Supabase Cloud (PostgreSQL)│  │  ChromaDB (Local Vector DB) │
        │  Dữ liệu sản phẩm, đơn hàng,│  │  Embeddings cho sản phẩm   │
        │  chính sách, review, auth   │  │  và chính sách cửa hàng     │
        └─────────────────────────────┘  └─────────────────────────────┘
```

- **Frontend (`web_ui/`)**: Next.js 16 (React 19, Tailwind CSS v4, Zustand, Lucide icons), tích hợp chat-widget hỏi đáp sản phẩm và chính sách.
- **Backend (`rag-service/`)**: FastAPI, LangGraph `workflow_1` (Multi-turn Agentic RAG, Gemini / Groq LLM, tools: `product_search`, `product_compare`, `policy_search`, `order_lookup`).
- **Cơ sở dữ liệu quan hệ**: Supabase (PostgreSQL với Row-Level Security - RLS).
- **Cơ sở dữ liệu vector**: ChromaDB lưu trữ cục bộ tại `database/chroma_db/`.

---

## 2. ⚙️ Yêu cầu môi trường tiên quyết (Prerequisites)

- **Hệ điều hành**: Windows 10/11 (khuyến nghị dùng PowerShell) hoặc Linux/macOS.
- **Node.js**: Phiên bản `>= 20.x` (khuyến nghị dùng `npm.cmd` trên Windows nếu lệnh `npm` gặp xung đột).
- **Python**: Phiên bản `3.11 - 3.13`. Khuyến nghị môi trường Conda tên `DL` (hoặc virtualenv).
- **Trình duyệt**: Google Chrome hoặc Microsoft Edge (cho kiểm thử E2E).

> [!IMPORTANT]
> **Lưu ý đặc biệt trên Windows:**
> Trước khi khởi chạy `rag-service`, bắt buộc phải đặt biến môi trường `$env:PYTHONUTF8=1` để tránh lỗi `UnicodeEncodeError: 'charmap'` khi pipeline ghi log có chứa ký tự đặc biệt hoặc emoji.

---

## 3. 🔑 Cấu hình biến môi trường

### 3.1 Backend (`rag-service/.env`)
Sao chép mẫu cấu hình từ `rag-service/.env.example` sang `rag-service/.env`:

```bash
cd rag-service
copy .env.example .env
```

Điền các thông tin cấu hình vào `rag-service/.env`:

| Tên biến | Bắt buộc | Mô tả |
| :--- | :--- | :--- |
| `PORT` | Có | Cổng backend (mặc định: `8080`). |
| `HOST` | Có | Địa chỉ lắng nghe (mặc định: `0.0.0.0` hoặc `127.0.0.1`). |
| `DEBUG` | Có | Chế độ debug (khuyến nghị: `True` khi chạy local). |
| `SUPABASE_URL` | Có | URL project Supabase (dạng: `https://<project-id>.supabase.co`). |
| `SUPABASE_SERVICE_ROLE_KEY` | Có | Secret API Key quyền cao của Supabase để backend truy vấn DB. |
| `SUPABASE_ANON_KEY` | Có | Public Anon Key của Supabase để verify token client. |
| `GEMINI_API_KEY` | Có | Google Gemini API Key để chạy mô hình ngôn ngữ cho Master Agent. |
| `GROQ_API_KEY` | Tùy chọn | Groq API Key dự phòng khi chuyển đổi LLM provider. |
| `VECTOR_DB_DIR` | Có | Đường dẫn tương đối hoặc tuyệt đối tới ChromaDB (mặc định: `../database/chroma_db`). |
| `LEGACY_LLM_GUARDRAIL` | Tùy chọn | Cơ chế guardrail LLM cũ (giá trị: `on` / `off`, mặc định: `on`). |
| `LEGACY_PROMPT_DEFENSE` | Tùy chọn | Bộ lọc phòng vệ prompt injection cũ (giá trị: `on` / `off`, mặc định: `on`). |
| `FOX_GUARD_MODE` | Tùy chọn | Chế độ bảo vệ FOX-Guardrails. Hiện tại **chỉ chấp nhận duy nhất giá trị `off`** (các giá trị khác sẽ báo lỗi cho tới khi triển khai Phần B; mặc định: `off`). |
| `FOX_GUARD_ARM` | Tùy chọn | Tên cụm kiểm nghiệm FOX-Guardrails phục vụ A/B testing đối chuẩn. |
| `BENCH_RECORD` | Tùy chọn | Bật ghi dữ liệu đánh giá benchmark (đặt giá trị **`1`** để bật; giá trị khác hoặc `true` sẽ không ghi gì). Dữ liệu được ghi dưới dạng JSONL cục bộ vào `rag-service/bench_records/YYYY-MM-DD.jsonl` (đã gitignore), **không ghi vào cơ sở dữ liệu**. |
| `BENCH_TEMPERATURE` | Tùy chọn | Nhiệt độ lấy mẫu (sampling temperature) cho LLM khi chạy benchmark (số thực từ `0.0` đến `2.0`; bỏ biến thì giữ cấu hình mặc định). |

### 3.2 Frontend (`web_ui/.env.local`)
Sao chép mẫu cấu hình từ `web_ui/.env.example` sang `web_ui/.env.local`:

```bash
cd web_ui
copy .env.example .env.local
```

Điền các thông tin cấu hình vào `web_ui/.env.local`:

| Tên biến | Bắt buộc | Mô tả |
| :--- | :--- | :--- |
| `APP_URL` | Có | URL gốc của website frontend (mặc định: `http://localhost:3000`). |
| `NEXT_PUBLIC_SUPABASE_URL` | Có | URL Supabase project. |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Có | Public Key của Supabase dùng trên giao diện web. |
| `SUPABASE_SERVICE_ROLE_KEY` | Có | Service Role Key dùng trong các API route phân quyền phía server. |
| `NEXT_PUBLIC_RAG_SERVICE_URL` | Có | URL trỏ tới FastAPI backend (mặc định: `http://localhost:8080/chat`). |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Có | Public Key Stripe Test Mode (`pk_test_...`). |
| `STRIPE_SECRET_KEY` | Có | Secret Key Stripe Test Mode (chỉ sử dụng khóa bắt đầu bằng `sk_test_...`). |
| `STRIPE_WEBHOOK_SECRET` | Có | Signing secret của Stripe Webhook (bắt đầu bằng `whsec_...`). |
| `NEXT_PUBLIC_ALLOW_MOCK_CHAT` | Tùy chọn | Mặc định `false`. Nếu bật `true`, khi backend sập thì frontend trả lời giả lập. |
| `NEXT_PUBLIC_ALLOW_MOCK_ADMIN` | Tùy chọn | Mặc định `false`. Chỉ dùng dữ liệu thật, không đổ số liệu giả trong admin. |
| `NEXT_PUBLIC_SAFE_RENDER` | Tùy chọn | Mặc định `true`. Bật chế độ render an toàn, chặn link ngoài và ẩn ảnh lạ. |

#### Chuyển tiếp Stripe Webhook khi chạy Local
Để nhận các sự kiện `checkout.session.completed`, `checkout.session.async_payment_succeeded` và `checkout.session.expired` trên môi trường phát triển local, sử dụng Stripe CLI. Đây là listener chuyển tiếp về máy, không phải endpoint HTTPS đã đăng ký trên Dashboard:
```powershell
# 1. Đăng nhập Stripe CLI
npx.cmd --yes @stripe/cli@1.55.6 login

# 2. Lắng nghe và chuyển tiếp webhook về endpoint Next.js
npx.cmd --yes @stripe/cli@1.55.6 listen --events checkout.session.completed,checkout.session.async_payment_succeeded,checkout.session.expired --events-from '@self' --forward-to http://127.0.0.1:3000/api/stripe/webhook
```
> [!TIP]
> Terminal sẽ in ra dòng: `Your webhook signing secret is whsec_...`. Sao chép mã secret này vào biến `STRIPE_WEBHOOK_SECRET` trong file `web_ui/.env.local`.

Listener và Next.js phải cùng đang chạy để nhận webhook. `STRIPE_SECRET_KEY` trong `.env.local` phải là khóa `sk_test_...` hợp lệ thuộc cùng sandbox; đăng nhập CLI không tự cập nhật khóa cho ứng dụng. Khi triển khai lên host công khai, đăng ký endpoint HTTPS `/api/stripe/webhook` trên đúng Stripe sandbox và dùng signing secret riêng của endpoint đó.

> [!CAUTION]
> Tuyệt đối **không commit các file `.env` hoặc `.env.local`** lên repository Git để tránh lộ thông tin bảo mật và secret key.

---

## 4. 🚀 Hướng dẫn khởi chạy từng bước

### 4.1 Khởi động Backend RAG Service

Mở một cửa sổ PowerShell mới tại thư mục gốc dự án:

```powershell
# 1. Chuyển vào thư mục backend
cd "d:\create\DATN\Agenttic-RAG-for-e-commerce\rag-service"

# 2. Cài đặt các thư viện Python (nếu chưa cài)
conda run -n DL pip install -r requirements.txt

# 3. Kích hoạt UTF-8 và khởi chạy server trên cổng 8080
$env:PYTHONUTF8=1
conda run -n DL uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

**Kiểm tra sức khỏe Backend:**
Mở trình duyệt hoặc PowerShell khác và gọi:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -Method Get | ConvertTo-Json
```
Kết quả phản hồi mong đợi:
```json
{
  "status": "healthy",
  "service": "rag-service",
  "debug_mode": true,
  "supabase_connected": true,
  "chroma_connected": true,
  "chroma_products_count": 1325
}
```

---

### 4.2 Khởi động Frontend Web

Mở một cửa sổ PowerShell khác tại thư mục gốc dự án:

```powershell
# 1. Chuyển vào thư mục web_ui
cd "d:\create\DATN\Agenttic-RAG-for-e-commerce\web_ui"

# 2. Cài đặt gói dependencies
npm.cmd install

# 3. Khởi chạy Next.js development server
npm.cmd run dev
```

Giao diện web sẵn sàng phục vụ tại: **`http://localhost:3000`**.

Để kiểm tra build production hoàn chỉnh:
```powershell
npm.cmd run build
```

---

## 5. 🗄️ Quản lý Cơ sở dữ liệu & ChromaDB

### 5.1 Quy trình thực thi Migration an toàn
> [!CAUTION]
> **CẢNH BÁO NGUY HIỂM VỀ DỮ LIỆU**:
> 1. Tuyệt đối **KHÔNG BAO GIỜ CHẠY LẠI file `database/setup.sql`** trên cơ sở dữ liệu Supabase đang hoạt động. File này chứa các lệnh `DROP TABLE ... CASCADE` sẽ xóa vĩnh viễn toàn bộ dữ liệu sản phẩm, đơn hàng và tài khoản!
> 2. **Sao lưu trước khi chạy**: Thực hiện xuất backup **toàn bộ cơ sở dữ liệu** (toàn bộ database schema & data, không chỉ riêng bảng `orders`) trước khi thực hiện migration.
> 3. **Thời điểm thực thi**: **CHỈ CHẠY SAU KHI ĐÃ MERGE FRONTEND** vào nhánh chính.
> 4. **Thứ tự thực thi migration bắt buộc** (do chủ đồ án chạy lần lượt trên Supabase SQL Editor):
>    0. `database/migrations/2026-11_base_tables.sql` (**chạy đầu tiên**: tạo `user_roles`, `chat_logs`, `support_tickets` nếu chưa có; Supabase thật chưa có 3 bảng này. Khách chỉ được tạo ticket `open`/`low` gắn đơn của mình và chỉ sửa `note`).
>    1. `database/migrations/2026-11_payment_and_address.sql` (thu hồi quyền INSERT trực tiếp của client vào bảng `orders`, chuyển luồng tạo đơn/trừ kho sang RPC).
>    2. `database/migrations/2026-11_chat_logs_guard.sql` (thêm cột `guard_decision_ids text[]` và index `(session_id, created_at)`, khóa quyền đọc/ghi của client `anon`, `authenticated`, chỉ cấp quyền `SELECT`, `INSERT` cho `service_role`).
>    3. `database/migrations/2026-11_product_reviews.sql` (bảng `reviews` đã có sẵn; migration thu hồi quyền ghi `INSERT`, `UPDATE`, `DELETE` của client `anon`, `authenticated`, tạo hàm RPC `create_product_review` ràng buộc chỉ khách đã mua mới được đánh giá).
>    4. `database/migrations/2026-11_seed_bench.sql` (khởi tạo bảng mapping và RPC phục vụ bộ dữ liệu đánh giá benchmark).
>    5. `database/migrations/2026-11_expired_checkout.sql` (bổ sung overload hàm RPC `fail_stripe_order(p_order_id uuid, p_session_id text)` xử lý sự kiện `checkout.session.expired` có chữ ký).
> 5. **Khởi tạo dữ liệu Benchmark (Seed)**: Sau khi chạy đủ 6 migration (0 → 5), thực hiện seed dữ liệu benchmark theo hướng dẫn tại [SEED-BENCH.md](SEED-BENCH.md).

### 5.2 Dữ liệu Vector ChromaDB
- ChromaDB đã được nạp sẵn dữ liệu vector của hơn 1.300 sản phẩm và bộ quy tắc chính sách tại thư mục: `database/chroma_db/`.
- Nếu cần nạp lại từ đầu từ nguồn dữ liệu thô:
  ```powershell
  cd "d:\create\DATN\Agenttic-RAG-for-e-commerce\rag-service"
  $env:PYTHONUTF8=1
  conda run -n DL python scripts/ingest.py
  ```

---

## 6. 🧪 Kiểm tra hoạt động ban đầu (Smoke Test)

### 6.1 Test Chat API Trực tiếp qua PowerShell
```powershell
$jsonStr = '{"message":"Shop có những chính sách đổi trả nào?", "session_id":"smoke-test-1"}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonStr)
Invoke-RestMethod -Uri "http://127.0.0.1:8080/chat" -Method Post -Body $bytes -ContentType "application/json; charset=utf-8" | ConvertTo-Json -Depth 5
```
Backend sẽ trả về phản hồi chi tiết với `tool_used: "policy_search"` và câu trả lời chính sách đổi trả 30 ngày.

### 6.2 Test Giao diện Web Người dùng
1. Mở trình duyệt truy cập `http://localhost:3000`.
2. Kiểm tra danh sách sản phẩm hiển thị trên trang chủ.
3. Nhấp vào biểu tượng Chat Widget ở góc dưới bên phải màn hình.
4. Gửi câu hỏi: *"iPhone 15 Pro Max có giá bao nhiêu?"*.
5. Kiểm tra bot phản hồi đúng thông số và giá từ cơ sở dữ liệu.
