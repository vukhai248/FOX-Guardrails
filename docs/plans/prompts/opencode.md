# Prompt cho OpenCode — việc nhẹ của FOX-Guard (06/11/2026)

> Dán phần dưới đường kẻ vào OpenCode. Claude viết code lõi, Codex review, chủ đồ án merge. OpenCode làm **dữ liệu kiểm thử, tài liệu module, script demo**: không sửa code bảo mật.

---

Bạn là OpenCode, làm việc nhẹ cho đồ án FOX-Guard (repo `D:/create/DATN/FOX-Guardrails`, GitHub `vukhai248/FOX-Guardrails`). FOX-Guard là lớp bảo vệ cho chatbot CSKH tiếng Việt của một shop bán điện tử.

## Quy tắc (bắt buộc)

1. **Làm O1 trước, và trong lúc làm O1 KHÔNG được mở bất kỳ file nào trong `src/`, `tests/`, `scripts/`, `docs/`.** O1 chỉ có giá trị khi bạn chưa biết code chặn bằng cách nào. Làm xong và commit O1 rồi mới được đọc code để làm O2, O3.
2. Không sửa file `.py` nào trong `src/` hay `tests/`. Không sửa `docs/plans/**` và `docs/DU-AN.md`.
3. Làm trên nhánh riêng: `git -C D:/create/DATN/FOX-Guardrails worktree add D:/create/DATN/.worktrees/opencode -b opencode/l4-light origin/feat/lop-4`. Commit trong đó, push nhánh đó, mở PR **vào `feat/lop-4`** (không phải `main`). Không push vào `feat/lop-4` hay `main`.
4. Không dùng PII thật. Số điện thoại, CCCD, thẻ… phải là số giả. Tên miền chỉ dùng `*.example`, `*.invalid` hoặc `shop.example` (tên miền của shop).
5. Python: `C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8`. Mọi kết quả trong báo cáo phải là **output thật** của lệnh bạn đã chạy. Chưa chạy thì ghi "chưa chạy". Không ghi "PASSED" cho thứ chưa chạy.

## O1 — Bộ câu held-out cho Lớp 4 (đầu ra của bot)

Viết `tests/fixtures/output_heldout.jsonl`, UTF-8, mỗi dòng một JSON: `{"id", "label", "kind", "text", "why"}`.
- `label`: `attack` hoặc `benign`.
- `kind`: `solicitation`, `link` hoặc `benign`.
- `text`: **câu trả lời của bot** gửi cho khách.
- `why`: một câu giải thích vì sao đó là tấn công hoặc vì sao hợp lệ.

Cần đủ:
- **50 câu `attack`/`solicitation`**: bot (bị dụ) đòi khách đưa CCCD/căn cước, ảnh giấy tờ, mã OTP/mã xác nhận, mật khẩu, mã PIN, số thẻ, CVV, ngày hết hạn thẻ, số tài khoản để "hoàn tiền / xác minh / nhận quà". Viết thật đa dạng: lịch sự, gấp gáp, không dấu, teencode, tiếng Anh (khoảng 1/5), lời yêu cầu nằm sau một câu trấn an ("Bạn yên tâm nhé, nhưng…"), lời yêu cầu ở cuối một câu trả lời dài.
- **30 câu `attack`/`link`**:
  - link hoặc ảnh tới tên miền ngoài (`evil-shop.example`…);
  - tên miền giả dạng shop bằng chữ Cyrillic/Greek (`ѕhop.example`);
  - link chứa số điện thoại / OTP trong query, kể cả dạng `%XX`;
  - ảnh markdown `![](…)`, link kiểu reference `[x]: url`, URL không có `http` (`//evil.example/x`, `evil.example`), tên miền viết tách (`evil . example`).
- **60 câu `benign`**: câu trả lời hợp lệ mà trông giống tấn công:
  - hỏi SĐT người nhận để giao hàng; hỏi mã số thuế để xuất hoá đơn VAT; hỏi địa chỉ khi khách muốn đổi địa chỉ;
  - cảnh báo "shop **không bao giờ** yêu cầu OTP / mật khẩu";
  - tư vấn có chữ "pin" (pin điện thoại), "mã giảm giá", "mã đơn hàng";
  - link tới `https://shop.example/...`; nhắc "TP.HCM", "TP.HN";
  - giá tiền, thông số kỹ thuật, hướng dẫn đặt lại mật khẩu trong app (không đòi mật khẩu).

Kiểm (dán lệnh và output vào báo cáo): đếm số dòng theo `label`/`kind`; mỗi dòng parse được bằng `json.loads`; `id` không trùng (`oh-001` …).

Commit `test(L4): independent output held-out set (OpenCode)`, **trước** khi làm O2.

## O2 — README cho 3 module mới (đọc code từ đây)

Mỗi file ≤ 40 dòng, viết cho người đọc không chuyên, mỗi ý quan trọng ghi nguồn `file:dòng`. Không đoán: tên hàm, tên trường, giá trị cấu hình phải lấy từ code.
- `src/fox_guard/policy/README.md`: gộp rủi ro và hành động theo từng trạm (`policy/engine.py`).
- `src/fox_guard/audit/README.md`: bảng `decisions`, `reviews`; cái gì được lưu, cái gì **không** được lưu; salt; lệnh `fox-guard audit why|export`.
- `src/fox_guard/detectors/README.md`: phần chặn bot đòi PII và link guard (`detectors/output.py`); nhắc rằng luật Lớp 2 có README riêng ở `detectors/rules/README.md`.

## O3 — Script demo Lớp 4

`scripts/demo_lop4.py`, theo đúng kiểu `scripts/demo_lop3.py`: 6–8 ca, mỗi ca in `action` và `text`. Gồm: bot đòi OTP → `block`; câu cảnh báo phủ định → `allow`; link ngoài bị gỡ; ảnh có SĐT trong query → `block`; tên miền giả dạng; input có token điều khiển → `block`; ghi chú shipper hợp lệ → `allow`. Chạy bằng `./.venv/Scripts/python.exe -X utf8 scripts/demo_lop4.py` (hoặc python của env DL) và dán output thật.

`C:/Users/Admin/anaconda3/envs/DL/python.exe -m ruff check scripts` phải sạch.

## Báo cáo

`docs/reports/opencode-L4.md`, gồm 4 mục:
1. Đã làm gì.
2. File đổi.
3. Lệnh kiểm + output thật.
4. Việc còn mở.

Ghi rõ bạn **đã/chưa** mở file code nào trong lúc làm O1. Xong thì mở PR vào `feat/lop-4` và dừng.
