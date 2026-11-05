# PII tiếng Việt + giả danh hoá (Lớp 3)

`detect_pii(normalized) -> list[PiiMatch]` (`recognizers.py`): 14 loại thực thể, chạy trên `clean` và
view `digits` của Lớp 1 (bắt số bị "băm" `0 9 1 2 . 3 4 5…` hay viết bằng chữ), span luôn trên `clean`.

| Thực thể | Cách nhận | Thực thể | Cách nhận |
| --- | --- | --- | --- |
| `VN_PHONE` | đầu số di động / số bàn VN | `CREDIT_CARD` | 13–19 số, **Luhn** + BIN |
| `VN_CCCD` | 12 số, mã tỉnh + thế kỷ | `VN_CMND` | 9 số **có ngữ cảnh** |
| `VN_BANK_ACCOUNT` | 9–16 số **có ngữ cảnh** (stk, ngân hàng…) | `VN_TAX_ID` | check digit MST + ngữ cảnh |
| `VN_PASSPORT`, `VN_LICENSE_PLATE` | mẫu + ngữ cảnh | `VN_HEALTH_INSURANCE` | mã đối tượng hoặc ngữ cảnh |
| `OTP` | 4–8 số sau/trước "mã OTP, mã xác nhận…" | `PASSWORD` | sau "mật khẩu, mk, pass" và có số/ký hiệu |
| `EMAIL` | regex | `PERSON`, `VN_ADDRESS` | từ khoá + họ phổ biến / đơn vị hành chính |

Ngữ cảnh xét 30 ký tự trước và 25 ký tự sau giá trị. Số đứng ngay trước đơn vị (`đ`, `k`, `%`, `GB`…, có
ranh giới chữ) là giá/số lượng, bỏ qua. UUID và hash hex (phải có chữ a–f) bị loại.

`PiiVault` (`vault.py`): `<PHONE_1>` ổn định trong phiên, lưu giá trị + **chủ** (`user_ref`) trong bộ
nhớ, hết hạn theo TTL (`pii.vault_ttl_minutes`), không ghi đĩa, không vào log.

Chính sách theo trạm (`policy.py`, bảng B5.2):
- INPUT: giả danh hoá mọi PII (trừ tên) trước khi gửi LLM.
- CONTEXT: theo `source` + `intent`. Dữ liệu của chính khách (`tool:order_lookup`, `order_note`…) có
  `intent=order_status` thì địa chỉ chỉ còn tỉnh/thành; `address_change` thì giữ đủ. Review của người
  khác: tên bị che, số liên lạc giả danh hoá với chủ `None` (không bao giờ hoàn nguyên).
- OUTPUT: placeholder → giá trị thật **chỉ** cho SĐT/email/địa chỉ **đúng chủ**; còn lại che.
  Thẻ, STK che toàn bộ; OTP, mật khẩu xoá. Placeholder lạ giữ nguyên + finding medium.
- `redact_text` (dùng cho `Guard.redact_for_log`): che mọi giá trị, placeholder chỉ còn `[PHONE]`.

PII không làm tăng `risk` (chỉ `action="mask"`). Chỉ `pii:unknown_placeholder` mới tăng.

Giới hạn: tên/địa chỉ chỉ theo từ khoá và họ phổ biến (chưa có NER); tên viết thường hoặc chỉ có tên
riêng bị lọt; vault trong bộ nhớ một process (sidecar nhiều worker cần vault chung, Lớp 6).
