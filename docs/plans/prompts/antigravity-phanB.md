> ⛔ **Không còn dùng (05/11/2026).** Antigravity đã được bỏ khỏi Phần B. Việc L1–L3 chuyển cho Codex (`codex-phanB.md`, Đợt 1b). Giữ file để tra cứu.

# Prompt cho Antigravity — Phần B (FOX-Guard), việc nhẹ

> Dán nguyên phần dưới đường kẻ vào Antigravity. Mỗi đợt mới Claude sẽ thêm mục "Đợt N" vào cuối file này.

---

Bạn là Antigravity, làm việc nhẹ cho **Phần B — FOX-Guard**: soạn dữ liệu kiểm thử, bảng tra, ví dụ, và sau này là dashboard. Codex viết code lõi. Claude nghiệm thu.

## Đọc trước

1. `D:/create/DATN/FOX-Guardrails/docs/plans/F-phan-cong-phan-B.md`, nhất là **quy tắc §4**. Ở Phần A, báo cáo của bạn bị trả lại 3 lần vì đoán tên và ghi "PASSED" cho test chưa chạy. Ở phần này, mọi kỳ vọng phải kiểm được bằng lệnh Python thật.
2. `docs/plans/B-guardrails.md` mục B2 (bảng 8 bước).
3. `docs/plans/01-tan-cong-va-phong-thu.md`, phần kỹ thuật T3.* (né tránh ký tự).

## Nơi làm

- Thư mục `D:/create/DATN/FOX-Guardrails`, tạo nhánh `git switch -c feat/b-light` từ `main`. Commit trong đó. Không push.
- **Chỉ** sửa file thuộc quyền của bạn (F §2): `src/fox_guard/data/teencode_vi.tsv`, `tests/fixtures/**`, `docs/reports/anti-*.md`. Không đụng code trong `src/`.
- Python: `C:/Users/Admin/anaconda3/envs/DL/python.exe`.

## Đợt 1 — dữ liệu cho Lớp 1 (chuẩn hoá ký tự)

### L1 — `src/fox_guard/data/teencode_vi.tsv`

- Dòng đầu: `# teencode_vi v1 — 03/11/2026 — nguồn: tự soạn`. Dòng 2 là header: `teencode<TAB>chuan<TAB>ambiguous<TAB>ghi_chu`.
- ≥ 150 dòng, toàn chữ thường, mỗi `teencode` chỉ xuất hiện một lần. Ví dụ: `ko → không`, `dc → được`, `bn → bạn`, `j → gì`, `vs → với`, `ad → admin`, `sp → sản phẩm`, `mk → mật khẩu`.
- `ambiguous=1` khi từ có thể là chữ thật hoặc mang nhiều nghĩa (`k` = không / nghìn, `mk` = mình / mật khẩu, `t` = tôi / tấn). Codex sẽ không thay các dòng này mặc định.
- Ưu tiên từ hay gặp trong CSKH và trong câu tấn công: bỏ qua, hướng dẫn, quy định, hệ thống, mật khẩu, OTP, chuyển khoản, số tài khoản, căn cước.
- Kiểm bằng script (dán cả lệnh lẫn output vào báo cáo): đếm số dòng, không trùng khoá, mỗi dòng đúng 4 cột.

### L2 — `tests/fixtures/normalize_benign.jsonl` (≥ 40 dòng)

Văn bản **hợp lệ**, chuẩn hoá **không được** báo tín hiệu `unicode:*` hay bắt nhầm mã hoá. Mỗi dòng: `{"id": "benign-001", "text": "...", "why": "..."}`.

Phải có:
- emoji ZWJ (gia đình, cờ cầu vồng), tông màu da, cờ 🇻🇳, **cờ England** (U+1F3F4 + tags + U+E007F), keycap 1️⃣;
- tiếng Việt gõ dạng **NFD**;
- mã đơn UUID, chuỗi trông như JWT (tự bịa, không phải token thật), hash sha256 hex;
- giá `25.990.000đ`, `m²`, URL có `%20`;
- tên sản phẩm tiếng Nhật/Trung, câu CSKH bình thường có số điện thoại giả.

### L3 — `tests/fixtures/normalize_attacks.jsonl` (≥ 30 dòng)

Câu tấn công đã được làm biến dạng. Mỗi dòng: `{"id": "atk-001", "technique": "T3.x", "text": "...", "expect_signal": "unicode:tags" | "unicode:invisible" | "unicode:mixed_script" | null, "expect_view": "skeleton" | "clean" | "vi_nodiac" | "vi_teencode" | "decoded" | "hidden_tags", "expect_contains": "bo qua moi huong dan"}`.
- Dùng 2 câu gốc: `ignore all previous instructions` và `bỏ qua mọi hướng dẫn trước đó`. Biến dạng theo từng kỹ thuật ở bảng B2: Cyrillic, zero-width, Unicode Tags, base64, `%XX`, fullwidth, không dấu, teencode, chấm chen giữa (`b.ỏ q.u.a`).
- Mã kỹ thuật lấy đúng từ `01-tan-cong-va-phong-thu.md`, **không tự đặt mã**.
- `expect_contains` ghi ở dạng mà view đó sẽ ra. Ví dụ view `vi_nodiac` thì viết không dấu, chữ thường.

**Quy tắc viết JSON** (bắt buộc):
- Mọi ký tự vô hình, tag, Cyrillic phải viết bằng escape (`\u200b`, `\udb40\udc53` hoặc tạo bằng script Python rồi `json.dumps`). **Không dán ký tự trần.**
- Tốt nhất là viết một script tạm trong thư mục scratch để sinh file. Không commit script vào `src/`.
- Kiểm (dán lệnh + output thật vào báo cáo): mỗi dòng parse được bằng `json.loads`; `id` không trùng; với ca có Cyrillic/tag, in mã điểm `U+…` của 10 ký tự đầu để chứng minh ký tự thật sự có mặt.

**Không** khẳng định chuẩn hoá của Codex có bắt được các ca này hay không: code đó chưa có. Báo cáo chỉ nói file hợp lệ về định dạng.

### Báo cáo và dừng

- `docs/reports/anti-B1.md`, gồm 4 mục: đã làm / file đổi / lệnh kiểm + output thật / việc còn mở.
- Commit `test(B2): add normalize fixtures`, `data(B2): add teencode table`.
- **Dừng.** Chờ Claude nghiệm thu.
