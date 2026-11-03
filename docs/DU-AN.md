# Sổ dự án FOX-Guardrails — một file duy nhất

> **Đề tài:** AI Guardrails phát hiện Prompt Injection và ngăn ngừa rò rỉ PII trong ứng dụng LLM.
> **Cập nhật lần cuối:** 03/11/2026 · Người cập nhật: Claude (sau mỗi lần nghiệm thu).
> **Cách dùng:** đọc file này trước tiên. Mọi file khác là **chi tiết** của một mục ở đây (cột "Chi tiết" chỉ tới). Muốn biết "đang ở đâu, đã có gì, làm bằng gì, việc tiếp là gì" thì chỉ cần file này.

---

## Mục lục

1. [Tóm tắt đồ án](#1-tóm-tắt-đồ-án)
2. [Tiến độ tổng — đang ở đâu](#2-tiến-độ-tổng--đang-ở-đâu)
3. [Kiến trúc tổng thể](#3-kiến-trúc-tổng-thể)
4. [Công nghệ sử dụng](#4-công-nghệ-sử-dụng)
5. [Phần A — Web e-commerce: những gì đã bàn giao](#5-phần-a--web-e-commerce-những-gì-đã-bàn-giao)
6. [Phần B — FOX-Guard: thiết kế và tiến độ từng lớp](#6-phần-b--fox-guard-thiết-kế-và-tiến-độ-từng-lớp)
7. [Phần C — Dữ liệu và thực nghiệm](#7-phần-c--dữ-liệu-và-thực-nghiệm)
8. [Lịch và mốc kiểm](#8-lịch-và-mốc-kiểm)
9. [Nhật ký](#9-nhật-ký)
10. [Sổ quyết định](#10-sổ-quyết-định)
11. [Việc mở, rủi ro, lỗi đã biết](#11-việc-mở-rủi-ro-lỗi-đã-biết)
12. [Vận hành: repo, môi trường, chạy, sao lưu](#12-vận-hành-repo-môi-trường-chạy-sao-lưu)
13. [Học và chuẩn bị bảo vệ](#13-học-và-chuẩn-bị-bảo-vệ)
14. [Bản đồ tài liệu chi tiết](#14-bản-đồ-tài-liệu-chi-tiết)

---

## 1. Tóm tắt đồ án

| | |
| --- | --- |
| **Vấn đề** | Chatbot CSKH đọc dữ liệu do người ngoài viết (review, ghi chú đơn, ticket). LLM không tách được "lệnh" với "dữ liệu", nên ai viết được dữ liệu là điều khiển được bot: dụ khách vào link lạ, đòi CCCD/OTP, nói sai chính sách. PII của khách còn bị gửi nguyên văn sang nhà cung cấp LLM và nằm trong log. |
| **Sản phẩm** | **FOX-Guard**: thư viện Python kiểm 3 trạm: **đầu vào** (câu khách gõ), **ngữ cảnh** (kết quả tool/dữ liệu truy xuất), **đầu ra** (câu bot trả lời). Mỗi lần kiểm ra 1 trong 4 hành động: **cho phép / che PII / chặn / chuyển kiểm duyệt**, kèm lý do và log đã che PII. |
| **Cắm vào app** | (1) SDK hoặc sidecar HTTP gọi ở 3 điểm hook trong app (đường chính); (2) proxy OpenAI-compatible: app chỉ đổi `base_url` (đường phụ). |
| **Ứng dụng thử nghiệm** | Web **Agentic RAG e-commerce** tiếng Việt (repo `Agenttic-RAG-for-e-commerce`). Phần A đã hoàn thiện web để có điểm chèn tấn công thật. |
| **Thực nghiệm** | BIPIA (gián tiếp, EN) và JailbreakBench (trực tiếp, EN), báo cáo **riêng**. Cộng bộ **CSKH tiếng Việt tự xây** (đóng góp chính). So sánh: không guard / hiện trạng / chỉ luật / chỉ mô hình / kết hợp (+ judge). |
| **Trong phạm vi** | Prompt injection trực tiếp và gián tiếp dạng văn bản (VI + EN), kể cả né tránh ký tự; PII VI + EN ở cả 3 trạm; lạm dụng tool ghi của web; rò dữ liệu qua link/ảnh markdown. |
| **Ngoài phạm vi** | Ảnh/âm thanh; đầu độc dữ liệu huấn luyện; tấn công cần trọng số model; MCP/đa agent; memory dài hạn; streaming từng token; toxicity nói chung. |
| **Đóng góp** | (1) Bộ test CSKH tiếng Việt cho PI gián tiếp + PII; (2) guard 3 trạm có chuẩn hoá ký tự/tiếng Việt và giả danh hoá PII có hoàn nguyên; (3) số đo end-to-end trên chatbot thật, gồm cả utility và rò PII. |

Chi tiết: [`plans/00-tong-quan.md`](plans/00-tong-quan.md) §0–§2, [`de-tai.md`](de-tai.md).

---

## 2. Tiến độ tổng — đang ở đâu

### 2.1 Bảng tiến độ

| Phần | Nội dung | Trạng thái | Ước % | Ghi chú |
| --- | --- | --- | --- | --- |
| **A** | Hoàn thiện web làm testbed | 🟡 QA lần cuối | 90% | Code xong, đã merge `main`, đã chạy 6 migration + seed trên Supabase thật. Còn QA2 (Anti) + K5 (Codex) |
| **B** | FOX-Guard | 🟡 Bắt đầu | 5% | B0 khung repo xong (`e65a746`). Đợt 1 (B1 + B2) đã giao, chưa bắt đầu |
| **C** | Dữ liệu + thực nghiệm | ⚪ Chưa giao | 0% | Cần trước Đợt 5 của B (chốt ngưỡng classifier) |
| **D** | Học + vấn đáp + báo cáo | ⚪ Chưa bắt đầu | 0% | Bắt đầu đọc tài liệu học sau Lớp 1 |

### 2.2 Đang làm ngay bây giờ

| Ai | Việc | Prompt | Xong khi |
| --- | --- | --- | --- |
| Antigravity | **QA2**: bổ sung các ca QA còn thiếu (3 câu chat, 409, `--reset`, replay webhook, bảng 23 mục, danh sách bản ghi QA) | [`prompts/antigravity-phanA.md`](plans/prompts/antigravity-phanA.md) → "Nghiệm thu Đợt 3" | `docs/reports/anti-QA2.md` |
| Codex | **K5**: sửa BUG-A-01 (một user review một sản phẩm nhiều lần), rồi **Phần B Đợt 1** | [`prompts/codex-phanA.md`](plans/prompts/codex-phanA.md) K5 → [`prompts/codex-phanB.md`](plans/prompts/codex-phanB.md) | `codex-K5.md`, rồi `codex-B1.md` |
| Claude | Nghiệm thu từng gói khi agent báo xong; cập nhật file này | — | — |

### 2.3 Việc của bạn (chủ đồ án)

- [ ] Hugging Face: tự bấm **Agree** license `meta-llama/Llama-Prompt-Guard-2-86M` (cần trước Đợt 5 của B).
- [ ] Chuyển `D:/backups/supabase/db-password.txt` vào trình quản lý mật khẩu rồi xoá file.
- [ ] Sau QA2: quyết định có dọn bản ghi QA (≈ 17 đơn, ≥ 3 review của tài khoản bench) hay giữ lại.
- [ ] Xác nhận ngày nộp/bảo vệ (đang giả định sau 07/12/2026).
- [ ] Đọc tài liệu học mỗi lớp khi Claude báo (mục 13).

---

## 3. Kiến trúc tổng thể

### 3.1 Sơ đồ

```text
                ┌──────────────────────── Web e-commerce (Phần A) ───────────────────────┐
 Khách hàng ──▶ │ Next.js (web_ui) ─▶ /api/chat ─▶ FastAPI /chat (rag-service)           │
                │                                    │                                   │
                │  [HOOK 1] guard_input(câu khách)   ▼                                   │
                │                          LangGraph workflow_1                          │
                │                          ├─ guardrail LLM cũ (arm "hiện trạng")         │
                │                          └─ MasterAgent (Gemini, vòng ReAct gọi tool)  │
                │                               tool: product_search, product_compare,   │
                │                               policy_search, order_lookup,             │
                │                               product_reviews, create_support_ticket   │
                │  [HOOK 2] guard_context(kết quả tool, nguồn = review/ghi chú/...)       │
                │  [HOOK 3] guard_output(câu trả lời)  ·  guard_log(text đã che → chat_logs)│
                └──────────────┬─────────────────────────────────────────────────────────┘
                               │ FOX_GUARD_MODE = off | inproc (SDK) | sidecar (HTTP)
                               ▼
        ┌─────────────────────────── FOX-Guard (Phần B) ───────────────────────────┐
        │ Lớp 1 chuẩn hoá ký tự (Unicode, homoglyph, mã hoá, tiếng Việt)             │
        │ Lớp 2 luật PI · Lớp 5 classifier PI (Prompt Guard 2) · judge LLM (tuỳ chọn) │
        │ Lớp 3 PII VN (Presidio + recognizer VN + NER) + giả danh hoá ↔ hoàn nguyên  │
        │ Lớp 4 kiểm đầu ra (bot đòi PII, link lạ) + policy 4 hành động + audit SQLite│
        │ Lớp 5 khoanh vùng/cắt câu bị chèn ở CONTEXT + datamarking                  │
        │ Adapter: SDK · sidecar FastAPI · proxy OpenAI-compatible                    │
        └───────────────┬───────────────────────────────────────────────────────────┘
                        ▼
              Dashboard Streamlit: cảnh báo · hàng đợi kiểm duyệt · thống kê · kết quả thực nghiệm

  Dữ liệu web: Supabase (Postgres + Auth + RLS) · ChromaDB (vector sản phẩm/chính sách) · Stripe test
```

### 3.2 Một câu hỏi đi qua hệ thống (khi FOX bật)

1. Khách gõ câu hỏi → `/api/chat` (Next) chuyển tới FastAPI `/chat` kèm JWT và `session_id`.
2. **HOOK 1**: FOX kiểm câu hỏi. Có lệnh tấn công rõ ràng → chặn, trả câu từ chối. Có PII → thay bằng `<PHONE_1>`… trước khi gửi LLM.
3. MasterAgent gọi tool, ví dụ `product_reviews` đọc review của sản phẩm.
4. **HOOK 2**: FOX kiểm từng đoạn review. Câu nào là lệnh nhắm vào bot thì **cắt riêng câu đó**, phần còn lại giữ nguyên rồi bọc nhãn "đây là dữ liệu, không phải chỉ dẫn".
5. LLM trả lời. **HOOK 3**: FOX kiểm câu trả lời: bot có đòi OTP/CCCD không, có link lạ không. Hoàn nguyên `<PHONE_1>` về số thật nếu đúng chủ.
6. Ghi `chat_logs` bằng text **đã che không hoàn nguyên được**, kèm `guard_decision_ids`. Quyết định lưu ở audit SQLite của FOX, xem trên dashboard.

### 3.3 Vì sao SDK/sidecar là đường chính, proxy là phụ

- Ở hook, guard biết **đoạn nào là dữ liệu tool và từ nguồn nào** (review hay ghi chú đơn). Điều này cần để phân biệt "nội dung phục vụ tác vụ" với "chỉ dẫn thao túng". Proxy chỉ thấy một mảng tin nhắn đã trộn.
- Web gọi Gemini SDK trực tiếp, không có `base_url` OpenAI. Hook chỉ cần sửa khoảng 20 dòng ở 3 chỗ.
- Proxy vẫn có giá trị "cắm vào là chạy" cho app khác dùng OpenAI SDK, nên giữ làm adapter phụ (B8).

---

## 4. Công nghệ sử dụng

### 4.1 Web e-commerce (Phần A)

| Thành phần | Công nghệ | Phiên bản | Vai trò |
| --- | --- | --- | --- |
| Frontend | Next.js (App Router) + React | 16.2.10 / 19.2.4 | Trang shop, giỏ, checkout, tài khoản, admin, chat-widget; API route phía server |
| Giao diện | Tailwind CSS, Zustand, markdown-to-jsx | 4 / 5.0 / 9.8 | Style, state giỏ hàng, render câu trả lời bot (đã chặn HTML thô) |
| Backend AI | Python + FastAPI + LangGraph | Python 3.13 (env DL) | `/chat`, `/health`; đồ thị workflow_1 |
| LLM | Gemini (google-genai), Groq làm judge benchmark cũ | — | MasterAgent gọi tool kiểu ReAct |
| Embedding | OpenRouter API | — | Vector hoá sản phẩm, chính sách |
| Vector DB | ChromaDB (local, `database/chroma_db/`) | — | 1.325 sản phẩm trong `products_collection` + chính sách |
| CSDL + Auth | Supabase (Postgres, Auth, Row Level Security) | supabase-js 2.110 | Sản phẩm, đơn, review, ticket, log, phân quyền |
| Thanh toán | Stripe **test mode** (Checkout + webhook có chữ ký) + Stripe CLI listener | stripe 22.3, CLI 1.55.6 | Thanh toán giả lập bằng thẻ test `4242…` |
| Kiểm thử | pytest, Node test + PGlite (Postgres chạy trong Node), Playwright | Playwright 1.64 | Unit backend, test SQL/RPC, E2E trình duyệt |

### 4.2 FOX-Guard (Phần B)

| Nhóm | Thư viện | Dùng cho |
| --- | --- | --- |
| Lõi | pydantic, PyYAML, regex, typer | Kiểu dữ liệu `Decision`/`Finding`, cấu hình `fox-guard.yaml`, regex Unicode, CLI `fox-guard` |
| Sidecar | FastAPI, uvicorn, httpx, idna | API `/v1/guard/*`, gọi judge, đổi tên miền sang Punycode |
| Classifier | transformers, torch (CPU), tokenizers, sentencepiece, onnxruntime | Prompt Guard 2 (86M, đa ngôn ngữ), deberta-v3 prompt-injection (EN) |
| PII | presidio-analyzer, presidio-anonymizer (kéo theo spaCy), phonenumbers | Khung nhận diện + recognizer VN tự viết (CCCD, SĐT, thẻ Luhn, MST…) |
| NER tên/địa chỉ | **chưa chọn**: underthesea / GLiNER / OpenMed (spike B5.1) | Tên người, địa chỉ tiếng Việt |
| Dashboard | Streamlit, pandas, plotly | Cảnh báo, hàng đợi duyệt, thống kê |
| Audit | SQLite (thư viện chuẩn) | Lưu quyết định đã che PII |
| Dev | pytest, pytest-benchmark, ruff; GitHub Actions (Python 3.11 + 3.13) | Test, đo độ trễ, lint, CI |
| Dữ liệu Unicode | `confusables.txt` (Unicode UTS #39) | Phát hiện chữ trông giống nhau (Cyrillic `а` vs Latin `a`) |

Môi trường: conda `DL` (Python 3.13.13) dùng chung cho web và FOX; package khai báo hỗ trợ Python ≥ 3.11. Danh sách đầy đủ và phiên bản đã kiểm: [`../requirements.txt`](../requirements.txt), [`../pyproject.toml`](../pyproject.toml).

---

## 5. Phần A — Web e-commerce: những gì đã bàn giao

Repo `D:/create/DATN/Agenttic-RAG-for-e-commerce`, nhánh `main` (đã merge `feat/a-backend` + `feat/a-frontend` ngày 03/11/2026). Codex làm backend, Antigravity làm frontend/QA, Claude nghiệm thu.

### 5.1 Thành phần đã bàn giao

| Gói | Đã làm gì | Lớp bảo mật / ý nghĩa cho đồ án | Kiểm bằng |
| --- | --- | --- | --- |
| **A0** Chạy local | `docs/RUN.md` chạy từ máy sạch; `/health` kiểm thật Supabase + Chroma | Có môi trường đo lặp lại được | Smoke test |
| **A1** Sửa lỗi nền chat | `session_id` UUID riêng theo user; server không trộn phiên; tắt câu trả lời giả khi backend sập (trả 503) | Chống rò hội thoại giữa user; bench không bị "câu trả lời giả" làm sai số | pytest, Playwright A1 |
| **A2** Thanh toán | Tạo đơn bằng RPC phía server (giá lấy từ DB, client không gửi giá); Stripe Checkout test; webhook **kiểm chữ ký**, chỉ nhận test mode; trừ kho đúng 1 lần (`stock_decremented_at`); phiên hết hạn → huỷ đơn; COD → `cod_pending`; địa chỉ tách trường; URL không chứa PII | Trước đây giá và trạng thái thanh toán sửa được từ trình duyệt | PGlite 77 test, QA thật (đơn `542da29f…` paid) |
| **A3** Review + ghi chú đơn | `POST /api/reviews` chỉ cho người đã mua (`paid`/`cod_pending`, không `cancelled`), giữ nguyên từng codepoint Unicode; sửa ghi chú khi đơn còn `pending` (≤ 500 ký tự) | Đây là **2 kênh chèn gián tiếp** chính của thực nghiệm | PGlite, Playwright A3, QA |
| **A4** Tool mới + điểm cắm | Tool `product_reviews`, `create_support_ticket` (tool ghi, chạy dưới JWT khách); `guard_client.py` với `guard_input/context/output/log`; cờ `FOX_GUARD_MODE`, `FOX_GUARD_ARM`, `BENCH_RECORD=1`, `BENCH_TEMPERATURE`, `LEGACY_LLM_GUARDRAIL`, `LEGACY_PROMPT_DEFENSE` | Chỗ để B9 cắm FOX; cờ tạo các arm G0/G1 | pytest |
| **A5** Log + admin thật | `chat_logs` 2 dòng/lượt kèm `guard_decision_ids`; admin đọc dữ liệu thật; quyền admin chỉ lấy từ bảng `user_roles` (không tin `user_metadata`); tab "Hội thoại" tách theo (user, phiên) | Có dữ liệu thật cho dashboard; chống leo quyền | Playwright A5.4 (chạy thật), A5.6 |
| **A6** Render an toàn | Chat-widget: link ngoài allowlist bị gỡ, ảnh ngoài bị ẩn, cảnh báo Punycode/homoglyph, chặn HTML thô, badge hành động guard | Chặn kênh rò dữ liệu qua link/ảnh ở phía trình duyệt | Playwright A6 6/6 |
| **A7** Seed bench | `scripts/seed_bench.py`: tạo 3 tài khoản bench (`bench_customer_a/b`, `bench_admin`), nạp ca test vào DB, chạy lại không nhân đôi, `--reset` chỉ xoá dữ liệu bench | Thực nghiệm chạy lại được, không đụng dữ liệu thật | pytest, chạy thật 03/11 |
| **K1–K4, I/J** Sửa sau review | Build không cần env; webhook phân loại lỗi vĩnh viễn; ghi log không chặn event loop; bỏ header test `x-mock-rag-url` (lỗ SSRF); trợ lý admin phải có quyền | Vá lỗ do chính agent tạo ra | pytest, Playwright |
| **Migration 0–5** | Đã chạy trên Supabase thật 03/11 (xem 5.2) | — | Chạy thử trên bản khôi phục 27/27, rồi chạy thật 6/6 |

### 5.2 Cơ sở dữ liệu (Supabase, sau 6 migration)

| Bảng | Nội dung | Ai đọc/ghi |
| --- | --- | --- |
| `products` | 1.345 sản phẩm, `stock` | Công khai đọc; kho chỉ đổi qua RPC |
| `orders` | Đơn + địa chỉ tách trường, `payment_method`, `payment_status`, `stripe_session_id`, `stock_decremented_at`, `note` | Khách đọc đơn của mình; tạo/sửa chỉ qua API server + RPC |
| `reviews` | Đánh giá 1–5 sao + comment | Công khai đọc; ghi chỉ qua RPC `create_product_review` |
| `support_tickets` | Ticket CSKH (`note` chứa luồng chat 2 chiều) | Khách tạo ticket `open`/`low` gắn đơn của mình, chỉ sửa `note`; admin qua server |
| `chat_logs` | Log hội thoại + `guard_decision_ids` | Chỉ server (service role) |
| `user_roles` | Quyền admin/staff/customer | Chỉ server |
| `bench_cases` | Bản đồ dữ liệu bench | Chỉ server |
| `policies`, `policy_chunks` | Chính sách shop | Công khai đọc |

Migration theo thứ tự: `2026-11_base_tables` → `payment_and_address` → `chat_logs_guard` → `product_reviews` → `seed_bench` → `expired_checkout`. **Không bao giờ chạy `database/setup.sql`** (file này xoá toàn bộ bảng).

### 5.3 Số đo kiểm thử hiện tại (trên `main`)

pytest **93 passed** · Node/PGlite **77/77** · `next build` + `tsc` qua · Playwright **29 passed + A5.4 chạy thật** · QA thật: 14 mục checklist có kết quả, còn thiếu một số ca (QA2).

Chi tiết: [`plans/A-hoan-thien-web.md`](plans/A-hoan-thien-web.md), [`plans/E-phan-cong-agent.md`](plans/E-phan-cong-agent.md), nhật ký nghiệm thu `Agenttic-RAG-for-e-commerce/docs/reports/nghiem-thu-A.md` (Lần 1–12).

---

## 6. Phần B — FOX-Guard: thiết kế và tiến độ từng lớp

Repo `D:/create/DATN/FOX-Guardrails`. Codex làm code lõi (worktree `.worktrees/b-core`, nhánh `feat/b-core`), Antigravity làm dữ liệu kiểm thử + dashboard (nhánh `feat/b-light`). Sau mỗi lớp: **dừng**, Claude nghiệm thu, bạn đọc tài liệu học rồi mới sang lớp sau.

### 6.1 Hợp đồng (B1) — thứ các phần khác dựa vào

- `GuardContext`: `session_id`, `user_ref`, `station` (input/context/output), `source` (review, order_note, tool:…), `intent`, `lang`, `arm`.
- `Finding`: detector nào, loại gì (injection/pii/solicitation/link/unicode), mức (low/medium/high), điểm, vị trí, bằng chứng **đã che** ≤ 120 ký tự, mã kỹ thuật T*.
- `Decision`: `decision_id`, `action` (allow/mask/block/review), `text` đã xử lý, `risk`, `findings`, `reasons` (tiếng Việt), `latency_ms`, `degraded`, `flags` (`harden_prompt`, `require_confirmation`, `session_flagged`).
- SDK: `Guard.from_config`, `check_input/context/output`, `restore` (hoàn nguyên PII), `redact_for_log` (che không hoàn nguyên, cho log).

### 6.2 Sáu lớp

| Lớp (Đợt) | Chặn cái gì | Cách làm (ngắn) | Gói | Trạng thái | Tài liệu học |
| --- | --- | --- | --- | --- | --- |
| **1** Chuẩn hoá ký tự | Lệnh giấu bằng chữ tàng hình, Unicode Tags, chữ Cyrillic giả Latin, base64/hex, không dấu/teencode tiếng Việt | Tạo nhiều "view" của text (NFC, bỏ ký tự vô hình, NFKC, skeleton confusable, không dấu, teencode, số, giải mã) để luật và classifier đọc; **không sửa bản gốc** | B1, B2 | 🔵 Đã giao | `hoc/lop-1-chuan-hoa.md` |
| **2** Luật PI | "Bỏ qua mọi hướng dẫn", giả admin/[SYSTEM], đòi system prompt, lệnh nhắm vào bot nằm trong review/ghi chú, token điều khiển `<\|im_start\|>` | Gói luật YAML VI/EN chạy trên các view; luật cấu trúc tất định = high, còn lại = medium | B3 | ⚪ | `hoc/lop-2-luat.md` |
| **3** PII + giả danh hoá | CCCD, SĐT, thẻ, STK, MST, BHYT, OTP, tên, địa chỉ bị gửi sang LLM / hiện ra / ghi log | Presidio + recognizer VN (kiểm Luhn, mã tỉnh…) + NER; thay bằng `<PHONE_1>` trước khi gửi LLM, hoàn nguyên khi hiển thị đúng chủ | B5.1, B5.2 | ⚪ | `hoc/lop-3-pii.md` |
| **4** Đầu ra + policy + audit | Bot bị dụ đòi OTP/CCCD; link/ảnh lạ, link homoglyph, link chứa PII; quyết định thiếu lý do; log lộ PII | Luật solicitation theo intent; link guard Punycode + allowlist; gộp rủi ro (classifier một mình **không** được chặn); audit SQLite chỉ nhận text đã che | B5.3, B5.4, B6 | ⚪ | `hoc/lop-4-dau-ra-policy-audit.md` |
| **5** Classifier + khoanh vùng | Câu tấn công diễn đạt lại mà luật không bắt; review lẫn câu độc với nội dung hợp lệ | Prompt Guard 2 (ngưỡng chốt trên tập dev); cắt đúng câu bị chèn, giữ phần hợp lệ; bọc datamarking có mã ngẫu nhiên | B4, B6.3, B6.4 | ⚪ (cần license + tập dev) | `hoc/lop-5-classifier-khoanh-vung.md` |
| **6** Tích hợp | — | Sidecar `fox-guard serve`; cắm 3 hook vào web; proxy OpenAI-compatible (hold mode); dashboard Streamlit | B7, B8, B9, B10 | ⚪ (cần A xong) | `hoc/lop-6-tich-hop.md` |

### 6.3 Đã bàn giao trong Phần B

| Mốc | Nội dung | Commit |
| --- | --- | --- |
| B0 khung repo | Package `fox_guard` (src layout), CLI `fox-guard`, `pyproject.toml` (nhóm core/ml/pii/dash/dev), `fox-guard.yaml`, CI ruff + pytest (3.11, 3.13), `.env.example`, xoá thư mục giữ chỗ v1; thư viện cài vào DL | `e65a746` |

Chi tiết: [`plans/B-guardrails.md`](plans/B-guardrails.md) (đặc tả từng gói), [`plans/F-phan-cong-phan-B.md`](plans/F-phan-cong-phan-B.md) (phân công, 12 quy tắc cho agent).

---

## 7. Phần C — Dữ liệu và thực nghiệm

**Trạng thái:** chưa giao agent. Claude sẽ giao trước Đợt 5 của B.

| Nội dung | Tóm tắt |
| --- | --- |
| Dữ liệu | BIPIA (gián tiếp, EN), JailbreakBench (trực tiếp, EN), bộ CSKH tiếng Việt tự xây (attack + hard-benign + clean), bộ PII; tách dev/test **theo template** để không "học thuộc đề" |
| Arm | **G0** không phòng thủ · **G1** hiện trạng web (guardrail LLM + bọc thẻ) · **G2** FOX chỉ luật · **G3** FOX chỉ classifier · **G4** FOX kết hợp (đề xuất) · **G5** G4 + judge |
| Chỉ số | Detector-level: P/R/F1, FPR (riêng hard-benign), AUROC. End-to-end: ASR (chấm bằng **canary**), task success, FPR, PII rò tới LLM / hiển thị / trong log, tỉ lệ bot đòi PII, độ trễ p50/p95, chi phí |
| Thống kê | Wilson 95%, McNemar (G0 vs G4 cùng ca), lặp 3 lần arm chính; đăng ký trước `eval/PREREG.md` |
| Gói | C1 dữ liệu · C2 chạy detector-level · C3 end-to-end · C4 tổng hợp bảng/biểu đồ · C5 (có thể) garak/promptfoo |

Chi tiết: [`plans/C-du-lieu-va-thuc-nghiem.md`](plans/C-du-lieu-va-thuc-nghiem.md).

---

## 8. Lịch và mốc kiểm

| Tuần | Kế hoạch gốc | Thực tế | Mốc kiểm |
| --- | --- | --- | --- |
| **T1** 03–09/11 | A0–A3; B0–B3; C1 | A0–A7 + migration xong 03/11 (sớm). B0 xong; B1–B2 đã giao | Web chạy + 1 đơn Stripe có webhook ✅ · `check_input` bắt 6 ca Unicode ⏳ |
| **T2** 10–16/11 | A4–A7; B4–B7; C1–C2 | — | **Gate:** bảng P/R/F1/FPR cho R/M/H. Chưa có thì cắt B8 và judge |
| **T3** 17–23/11 | B9, B10, B8, judge; C3 | — | Demo 5 kịch bản chạy; có số ASR G0 vs G4 |
| **T4** 24–30/11 | Sửa lỗi, tối ưu; C3 đủ + C4 | — | Báo cáo đủ chương + slide nháp |
| **Đệm** 01–07/12 | Chạy bù, tập vấn đáp | — | — |

Thứ tự cắt khi trễ: B8 proxy → judge → lặp 3 lần còn 1 → tính năng web thêm. **Không cắt:** luật + classifier + PII + policy 4 hành động + audit đã che + cắm vào web + dashboard + 3 bảng kết quả riêng.

---

## 9. Nhật ký

| Ngày | Sự kiện | Tham chiếu |
| --- | --- | --- |
| 18/10/2026 | Plan v1 (đã thay thế) | `archive/plan-v1-2026-10-18.md` |
| 02/11/2026 | Plan v2 + phân công Phần A; baseline web `dd4093d` | `plans/00…E` |
| 02–03/11 | Codex A1–A7, C1–C2, K1–K4; Anti A0, A1-UI, A3-UI, A5-UI, A6, F–J; 12 lần nghiệm thu | `nghiem-thu-A.md` |
| 03/11 | Merge hai nhánh web vào `main` (`262458e`); tất cả test xanh | Lần 9 |
| 03/11 | Codex sao lưu Supabase, phát hiện thiếu 3 bảng; Claude thêm migration 0, chạy thử trên bản khôi phục 27/27 (`4067561`) | Lần 10 |
| 03/11 | Codex chạy 6 migration + seed trên Supabase thật; Stripe CLI listener; webhook hết hạn chạy thật | Lần 11 |
| 03/11 | Anti QA Đợt 3: thanh toán thẻ test thành công; phát hiện BUG-A-01; giao QA2 + K5 | Lần 12 |
| 03/11 | B0: dựng khung FOX-Guard, cài thư viện, giao Đợt 1 Phần B (`e65a746`) | `F-phan-cong-phan-B.md` |
| 03/11 | Tạo sổ dự án này | — |

---

## 10. Sổ quyết định

| # | Quyết định | Lý do |
| --- | --- | --- |
| Q1 | Phạm vi: PI trực tiếp + gián tiếp, dạng văn bản | Thu hẹp đề tài cho 1 tháng |
| Q2 | PII làm đầy đủ ở 3 trạm, có giả danh hoá + hoàn nguyên | Đề tài yêu cầu |
| Q3 | Cắm chính bằng SDK/sidecar, proxy là phụ | Hook biết nguồn dữ liệu; web không dùng `base_url` |
| Q4 | Testbed = web Agentic RAG e-commerce của bạn | Có sẵn, tiếng Việt, có tool và dữ liệu do khách nhập |
| Q5 | Phần A chỉ làm "đủ để bench + vá thanh toán", ≈ 25% công sức | Trọng tâm là guard |
| Q6 | Classifier chính Prompt Guard 2 86M, phụ deberta-v3 (EN) | Chạy CPU được, đa ngôn ngữ (phải tự đo tiếng Việt) |
| Q7 | Audit = SQLite + xuất JSONL; bỏ hash-chain | Đơn giản, dashboard đọc dễ |
| Q8 | Dashboard = Streamlit riêng | Nhanh, cùng ngôn ngữ với lõi |
| Q9 | LLM thực nghiệm = chính model của web, temperature cố định | Đo trên hệ thống thật |
| Q10 | ASR chấm bằng canary; judge chỉ phụ trợ | Tránh judge sai/bị lừa |
| Q11 | Tiếng Việt là chính; tiếng Anh qua BIPIA/JBB | Web 100% tiếng Việt |
| Q12 | Classifier đơn lẻ không bao giờ tự chặn; chỉ luật tất định hoặc ≥ 2 tín hiệu | Giảm chặn nhầm (FPR) |
| Q13 | Chia việc 3 tầng: Codex (nặng, rủi ro) · Antigravity (nhẹ, UI, QA, dữ liệu) · Claude (nghiệm thu) | Model mạnh cho chỗ dễ thành lỗ hổng |
| Q14 | Bỏ A8 (tính năng web tuỳ chọn) | Review + ghi chú + ticket đã đủ kênh chèn |
| Q15 | Thêm migration 0 tạo `user_roles`/`chat_logs`/`support_tickets`, quyền chặt hơn `setup.sql` (khách chỉ sửa `note` ticket) | DB thật chưa có 3 bảng; `setup.sql` cũ cho khách tự sửa trạng thái ticket |
| Q16 | Dùng env conda DL Python 3.13 cho cả web và FOX | Bạn yêu cầu; package vẫn hỗ trợ ≥ 3.11 |
| Q17 | Phần B chia theo 6 lớp bảo mật, mỗi lớp dừng để bạn học | Vừa làm vừa hiểu, tránh đến cuối mới đọc code |
| Q18 | Stripe webhook local qua Stripe CLI, chưa đăng ký endpoint trên Dashboard | Web chạy localhost |

---

## 11. Việc mở, rủi ro, lỗi đã biết

### 11.1 Lỗi và việc mở

| Mã | Mô tả | Ai | Trạng thái |
| --- | --- | --- | --- |
| BUG-A-01 | Một user review một sản phẩm nhiều lần (đã thấy 3 bản trùng) → kênh spam review độc | Codex K5 | Đã giao |
| QA2 | Bổ sung ca QA còn thiếu: tool ticket chưa từng chạy thật (DB 0 ticket), 409 ghi chú, `--reset`, replay webhook thanh toán | Anti | Đã giao |
| A-OPEN-1 | Hết hàng đúng lúc khách đang trả tiền → webhook trả 503, Stripe gửi lại mãi trong khi khách đã trả | Codex | Ghi nhận, xử lý nếu QA gặp |
| A-OPEN-2 | Ghi `chat_logs` không có hàng đợi; dưới tải cao có thể chậm | — | Giới hạn, báo cáo độ trễ |
| OPS-1 | File mật khẩu DB dạng chữ thường `D:/backups/supabase/db-password.txt` | Bạn | Cần xoá |
| OPS-2 | Bản ghi QA trên DB thật (~17 đơn, ≥ 3 review bench) | Bạn quyết | Chờ QA2 |
| OPEN-1 | Ngày nộp/bảo vệ | Bạn | Chưa rõ |
| OPEN-2 | License Prompt Guard 2 | Bạn | Chưa |
| OPEN-3 | Phần C chưa giao agent | Claude | Trước Đợt 5 B |

### 11.2 Rủi ro chính

| Rủi ro | Cách xử lý |
| --- | --- |
| Rate limit Gemini/Groq free làm chậm thực nghiệm | Xoay key, chạy đêm, kịch bản tối thiểu, cache theo ca × arm |
| Prompt Guard 2 yếu trên tiếng Việt | Luật VI + view không dấu bù; báo cáo đúng số (cũng là một phát hiện) |
| Chặn nhầm ghi chú giao hàng hợp lệ | Classifier đơn lẻ không chặn; CONTEXT chỉ cắt khi rủi ro high |
| Agent đoán tên, báo "PASSED" khi chưa chạy (đã xảy ra nhiều lần ở Phần A) | 12 quy tắc ở `F-phan-cong-phan-B.md` §4; Claude chạy lại mọi test |
| Bạn không kịp hiểu code | Tài liệu học sau mỗi lớp + mục "bạn phải giải thích được" |
| Ổ C gần đầy (~2 GB) | Cache pip và model ở `D:/create/DATN/.cache` |

---

## 12. Vận hành: repo, môi trường, chạy, sao lưu

| Mục | Giá trị |
| --- | --- |
| Repo web | `D:/create/DATN/Agenttic-RAG-for-e-commerce` — nhánh `main` (QA đang ở `qa/a-wave3`) |
| Repo FOX | `D:/create/DATN/FOX-Guardrails` — nhánh `main`; Codex dùng `D:/create/DATN/.worktrees/b-core` |
| Python | `C:/Users/Admin/anaconda3/envs/DL/python.exe` (3.13). Đặt `PYTHONUTF8=1` khi chạy rag-service trên Windows |
| Biến cache | `PIP_CACHE_DIR=D:/create/DATN/.cache/pip`, `HF_HOME=D:/create/DATN/FOX-Guardrails/.cache/hf` |
| Chạy web | 3 tiến trình theo `Agenttic-RAG-for-e-commerce/docs/RUN.md`: rag-service `127.0.0.1:8080`, Next.js `:3000`, Stripe CLI listener (3 event Checkout). Phải bật lại sau khi khởi động máy |
| Tài khoản bench | Trong `.env.bench` (gitignore). Không in mật khẩu |
| Sao lưu DB | `D:/backups/supabase/20261103-213431-pre-migration/` (`database.dump` là bản chính; manifest SHA-256; script chạy thử chuỗi migration `migration_chain_test.py`) |
| Quy tắc cứng | Không chạy `database/setup.sql`; migration chỉ cộng thêm và chạy thử trên bản khôi phục trước; chỉ khoá Stripe `sk_test_`; không commit `.env*`; không PII thật trong test; không push khi bạn chưa đồng ý |

---

## 13. Học và chuẩn bị bảo vệ

- **Sau mỗi lớp của Phần B**: đọc `docs/hoc/lop-N-*.md` (mục lục [`hoc/README.md`](hoc/README.md)). Mỗi file có: lớp chặn tấn công gì, cách hoạt động bằng lời thường, lệnh chạy thử kèm output thật, code ở đâu, giới hạn, câu hội đồng có thể hỏi.
- **Nền chung**: [`plans/01-tan-cong-va-phong-thu.md`](plans/01-tan-cong-va-phong-thu.md) (các vụ tấn công thật 2022–2026, mã kỹ thuật T*, mục tiêu O*, PII P*).
- **Lộ trình theo tuần, 28 câu hội đồng, 7 kịch bản demo, khung báo cáo**: [`plans/D-hoc-va-van-dap.md`](plans/D-hoc-va-van-dap.md).
- **Năm ý phải nói trong 1 phút**: vấn đề → giải pháp 3 trạm 4 hành động → cắm vào là chạy → đo thế nào → giới hạn trung thực (xem D §2).

Phần A cũng có lớp bảo mật đáng học (dùng cho chương "Thiết kế"): giá do server tính, webhook có chữ ký, RLS + quyền theo cột, quyền admin chỉ từ `user_roles`, render an toàn. Xem bảng 5.1.

---

## 14. Bản đồ tài liệu chi tiết

| Muốn biết | Đọc |
| --- | --- |
| Toàn cảnh (file này) | `docs/DU-AN.md` |
| Phạm vi, kiến trúc, quyết định gốc, lịch | `docs/plans/00-tong-quan.md` |
| Tấn công & phòng thủ, mã T*/O*/P* | `docs/plans/01-tan-cong-va-phong-thu.md` |
| Đặc tả Phần A / B / C | `docs/plans/A-…`, `B-guardrails.md`, `C-…` |
| Học, vấn đáp, demo | `docs/plans/D-hoc-va-van-dap.md`, `docs/hoc/` |
| Phân công agent A / B | `docs/plans/E-phan-cong-agent.md`, `F-phan-cong-phan-B.md` |
| Prompt giao việc (kèm lịch sử nghiệm thu từng agent) | `docs/plans/prompts/*.md` |
| Nghiệm thu Phần A theo lần | `Agenttic-RAG-for-e-commerce/docs/reports/nghiem-thu-A.md` |
| Báo cáo từng gói của agent | `Agenttic-RAG-for-e-commerce/docs/reports/*.md`, `FOX-Guardrails/docs/reports/*.md` |
| Lỗi QA | `Agenttic-RAG-for-e-commerce/docs/QA/bugs.md` |
| Chạy web, seed | `Agenttic-RAG-for-e-commerce/docs/RUN.md`, `docs/SEED-BENCH.md` |
| API FOX-Guard (khi có) | `FOX-Guardrails/docs/api.md` |
| Research nền | `docs/research/`, `hermess/` (không commit) |
