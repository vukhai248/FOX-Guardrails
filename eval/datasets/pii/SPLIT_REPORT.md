# SPLIT_REPORT — bộ PII tổng hợp

130 mẫu gốc × 2 lần điền (seed `20261107`), cộng biến dạng T3.12 cho ~30% ca PII. Giá trị đều là số giả đúng định dạng/checksum.

| split | label | số ca |
| --- | --- | --- |
| dev | hard_negative | 30 |
| dev | pii | 58 |
| test | hard_negative | 50 |
| test | pii | 153 |

| split | thực thể | số span |
| --- | --- | --- |
| dev | ADDRESS | 7 |
| dev | BANK_ACCOUNT | 4 |
| dev | BHYT | 6 |
| dev | CARD | 5 |
| dev | CCCD | 5 |
| dev | CMND | 4 |
| dev | EMAIL | 5 |
| dev | OTP | 9 |
| dev | PASSPORT | 4 |
| dev | PASSWORD | 2 |
| dev | PERSON | 11 |
| dev | PHONE | 16 |
| dev | PLATE | 6 |
| dev | TAX_ID | 6 |
| test | ADDRESS | 21 |
| test | BANK_ACCOUNT | 16 |
| test | BHYT | 8 |
| test | CARD | 14 |
| test | CCCD | 12 |
| test | CMND | 15 |
| test | EMAIL | 19 |
| test | OTP | 7 |
| test | PASSPORT | 10 |
| test | PASSWORD | 13 |
| test | PERSON | 36 |
| test | PHONE | 21 |
| test | PLATE | 10 |
| test | TAX_ID | 13 |

Kiểm trùng mẫu gốc giữa dev/test: chuyển 0 trùng hẳn, 0 gần trùng sang dev. Trùng câu trong cùng tập: 2.
