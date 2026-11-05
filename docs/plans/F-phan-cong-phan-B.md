# Phân công agent — Giai đoạn 2: FOX-Guard (Phần B)

> Ngày lập: 03/11/2026 · **Sửa 05/11/2026: bỏ Antigravity khỏi Phần B.** Chỉ còn Codex làm và Claude nghiệm thu. Prompt: `prompts/codex-phanB.md`. File `prompts/antigravity-phanB.md` không còn dùng.

## 1. Vai trò

| Ai | Vai trò |
| --- | --- |
| **Codex** | Làm toàn bộ: code `src/fox_guard/`, test, **mọi dữ liệu kiểm thử** (fixture, bảng teencode, câu hard-benign), ví dụ, dashboard (B10), tích hợp web (B9), tài liệu học cho lớp mình viết |
| **Claude** | Đầu não: giao việc, đọc diff, chạy lại test, kiểm tài liệu học khớp code, nghiệm thu. Mỗi lần nghiệm thu, Claude tự viết thêm một bộ **ca kiểm độc lập** (`tests/acceptance/`) mà Codex không thấy trước, để Codex không tự chấm bài của mình |
| **Bạn** | Đọc tài liệu học sau mỗi lớp, chấp nhận license Prompt Guard 2, chạy thử demo |

## 2. Nhánh và quyền sở hữu file

- Codex: worktree `D:/create/DATN/.worktrees/b-core`, nhánh `feat/b-core`. Sở hữu mọi file trong repo, **trừ** các file của Claude dưới đây.
- Claude sở hữu: `docs/plans/**`, `docs/DU-AN.md`, `tests/acceptance/**`. Codex không sửa; thấy sai thì ghi `docs/reports/requests.md`.
- Claude merge `feat/b-core` vào `main` sau mỗi đợt đã nghiệm thu (chỉ khi bạn đồng ý). Không ai push.

## 3. Lộ trình theo lớp bảo mật — mỗi lớp xong là DỪNG để bạn học

| Đợt | Lớp bảo mật | Codex | Tài liệu học (Codex viết, Claude kiểm) |
| --- | --- | --- | --- |
| 1 | **Lớp 1 — chuẩn hoá ký tự** (chữ tàng hình, Unicode Tags, homoglyph, mã hoá, biến thể tiếng Việt) | B1 hợp đồng + B2; **1b**: bảng teencode + 2 bộ fixture chuẩn hoá (trước đây của Anti) | `docs/hoc/lop-1-chuan-hoa.md` |
| 2 | **Lớp 2 — luật phát hiện prompt injection** | B3 + câu hard-benign CSKH + câu tấn công mẫu | `docs/hoc/lop-2-luat.md` |
| 3 | **Lớp 3 — PII tiếng Việt + giả danh hoá có hoàn nguyên** | B5.1, B5.2, spike NER + fixture PII giả + hard-negative số | `docs/hoc/lop-3-pii.md` |
| 4 | **Lớp 4 — kiểm đầu ra + policy + audit đã che** | B5.3, B5.4, B6.1, B6.2, B6.5, B6.6 + fixture câu bot đòi PII, link lạ | `docs/hoc/lop-4-dau-ra-policy-audit.md` |
| 5 | **Lớp 5 — classifier + khoanh vùng ngữ cảnh** | B4, B6.3, B6.4 + ví dụ SDK | `docs/hoc/lop-5-classifier-khoanh-vung.md` |
| 6 | **Tích hợp** | B7 sidecar, B9 cắm web, B8 proxy, B10 dashboard | `docs/hoc/lop-6-tich-hop.md` |

Điều kiện trước:
- Đợt 5 cần **bạn** bấm "Agree" license `meta-llama/Llama-Prompt-Guard-2-86M` trên Hugging Face và tập **dev** của Phần C để chốt ngưỡng. Phần C chưa giao. Claude sẽ giao trước Đợt 5.
- Đợt 6 (B9) cần Phần A đã merge vào web.

Mỗi đợt: agent viết code + test → báo cáo → **dừng**. Claude nghiệm thu → Claude báo bạn đọc tài liệu học → bạn đọc xong mới sang đợt sau.

## 4. Quy tắc chung (rút từ lỗi đã gặp ở Phần A)

1. **Không đoán tên.** Mọi tên hàm, field, biến môi trường, mã lỗi, giá trị cấu hình phải lấy từ code hoặc plan. Tài liệu viết ra phải ghi nguồn `file:dòng`. Ở Phần A, tài liệu đoán sai tên event Stripe, giá trị cờ, tên bảng đã phải trả lại 3 lần.
2. **Chỉ ghi kết quả thật.** Dán output thật của lệnh. Test bị skip **không** phải đạt. Chưa chạy thì ghi "chưa chạy".
3. **Không thêm móc test vào code chạy thật** (bài học `x-mock-rag-url` ở Phần A). Muốn test thì tách hàm thuần, hoặc tiêm phụ thuộc qua tham số.
4. **RED trước GREEN**: viết test thất bại trước, rồi mới viết code.
5. Môi trường: `C:/Users/Admin/anaconda3/envs/DL/python.exe` (Python 3.13). Đường dẫn luôn dạng `D:/…`. Đặt `PIP_CACHE_DIR=D:/create/DATN/.cache/pip`, `HF_HOME=D:/create/DATN/FOX-Guardrails/.cache/hf` (ổ C còn ~2 GB).
6. **Thư viện mới**: hỏi Claude qua `requests.md` trước khi cài. Cài xong phải ghi vào cả `pyproject.toml` và `requirements.txt`, và chạy lại pytest của `rag-service` (env DL dùng chung với web).
7. **Không PII thật** trong fixture, test, log, báo cáo. Chỉ dùng số tự sinh, có ghi `synthetic`. Thẻ dùng số test công khai (ví dụ `4242 4242 4242 4242`).
8. **Không tải model gated**, không in `HF_TOKEN`. Không đưa khoá nào vào commit.
9. **Không chỉnh luật/ngưỡng để qua một ví dụ** nếu làm hỏng hard-benign. Ngưỡng classifier chỉ chốt trên tập dev.
10. Test không được phụ thuộc `hermess/` (thư mục này bị gitignore, CI không có). Cần ca nào thì chép vào `tests/fixtures/`.
11. Viết chuỗi có ký tự vô hình bằng escape `\uXXXX` / `\U000EXXXX` trong JSON hoặc Python, không dán ký tự trần (dán trần dễ mất ký tự mà không ai thấy).
12. Báo cáo mỗi đợt có 4 mục: đã làm gì / file đổi / lệnh test + output thật / việc còn mở.

## 5. Mẫu tài liệu học (`docs/hoc/lop-N-*.md`, ≤ 150 dòng)

1. **Lớp này chặn tấn công gì**: mã kỹ thuật T*/P* trong `01-tan-cong-va-phong-thu.md`, 2–3 ví dụ cụ thể với shop.
2. **Cách hoạt động** bằng lời thường, ≤ 10 dòng, không code.
3. **Chạy thử**: 1–3 lệnh copy-paste được, kèm **output thật** đã chạy.
4. **Code nằm ở đâu**: bảng file → làm gì (link `file:dòng`).
5. **Giới hạn và cách né**: lớp này không chặn được gì, vì sao cần lớp khác.
6. **3–5 câu hội đồng có thể hỏi** + hướng trả lời.

## 6. Kế hoạch chính

`docs/DU-AN.md` là **kế hoạch chính và file theo dõi duy nhất** của đồ án. **Chỉ Claude** cập nhật, sau mỗi lần nghiệm thu: "Bảng theo dõi nhanh" ở đầu file, trạng thái tính năng (Phần 3), trạng thái lớp (Phần 4), bảng tick (Phần 9.2), cập nhật thực tế triển khai (Phần 10), quyết định (Phần 11), lỗi và việc mở (Phần 12). Agent không sửa file này; thấy sai thì ghi `docs/reports/requests.md`.
