# Luật phát hiện prompt injection (Lớp 2)

`run_rules(normalized, station) -> list[Finding]`: chạy mọi luật của trạm trên các view của Lớp 1.
`Guard.check_input/context/output` gọi hàm này; trạm lấy theo hàm được gọi, không theo `ctx.station`.

Gói luật: `packs/vi.yaml`, `packs/en.yaml`, `packs/structural.yaml`. Mỗi luật có `id`, `group` (1–8),
`technique` (T*), `stations`, `views`, `severity`, `reason` (tiếng Việt, hiện ở `Decision.reasons`),
`pattern`, và ≥ 2 `examples_pos` / ≥ 2 `examples_neg`. Ví dụ chạy trong `tests/test_rules.py`.

View luật được đọc:
- `vi_nodiac`, `vi_teencode`: đã bỏ dấu, chữ thường. Pattern tiếng Việt viết **không dấu**.
- `latin`: chỉ đổi chữ Cyrillic/Greek giống Latin về Latin, rồi bỏ dấu + chữ thường. Không dùng
  `skeleton` vì UTS #39 đổi cả chữ Latin thật (`m` → `rn`).
- `nfkc` (giữ hoa thường, gồm cả `＜|im_start|＞` fullwidth), `clean`.

Mức độ: luật nhóm 1–6 và 8 là `medium`; nhóm 7 (token điều khiển, thẻ delimiter, lệnh trong
HTML comment) là `high` tất định. Khớp trên chữ **đã giấu** (Unicode Tags giải ra, base64/hex/…)
thì nâng lên `high`. `span` chỉ có khi view khớp có cùng độ dài với `clean`. `evidence` đã che chữ số.

Câu phủ định ("Shop **không bao giờ** yêu cầu khách gửi OTP") không bị bắt nhờ điều kiện ở luật
đòi PII. Mỗi lần `search` có timeout 50 ms để chống regex chạy quá lâu.

CLI: `fox-guard rules list`, `fox-guard rules report cases.jsonl --out kq.csv` (luật nào bắt ca nào).
Dữ liệu kiểm: `scripts/gen_rule_fixtures.py` sinh 64 câu hard-benign + 42 câu tấn công.

Giới hạn: diễn đạt lại khác mẫu là lọt (Lớp 5 classifier bù); luật không hiểu ngữ cảnh;
phủ định chỉ xét từ đứng ngay trước; chưa có luật cho tiếng khác ngoài VI/EN.
