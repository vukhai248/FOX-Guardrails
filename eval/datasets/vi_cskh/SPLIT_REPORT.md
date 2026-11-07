# SPLIT_REPORT — bộ CSKH tiếng Việt

Seed `20261107`, chia theo `template_id` (dev ≈ 30% mẫu gốc). Nguồn mẫu: `benign_templates.jsonl` 200 mẫu.

| split | label | source | số ca |
| --- | --- | --- | --- |
| dev | clean | chat | 15 |
| dev | clean | review | 8 |
| dev | hard_benign | chat | 6 |
| dev | hard_benign | order_note | 18 |
| dev | hard_benign | review | 12 |
| test | clean | chat | 35 |
| test | clean | review | 22 |
| test | hard_benign | chat | 34 |
| test | hard_benign | order_note | 22 |
| test | hard_benign | review | 28 |

Biến thể T3: 0 ca ().
Kiểm trùng giữa dev/test: chuyển 0 mẫu trùng hẳn và 0 mẫu gần trùng (Jaccard 5-gram ≥ 0,8) sang dev. Trùng trong cùng một tập: 0 ca.

**Chưa có ca tấn công**: `templates/attack_templates.jsonl` chưa có. Xem ghi chú trong PR.
