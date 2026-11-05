# Báo cáo B5.1–B5.2 — Lớp 3 PII tiếng Việt + giả danh hoá (Claude), 05/11/2026

Nhánh `feat/b-core` từ `main` @ `70c1339`. Claude làm và nghiệm thu; subagent chỉ viết câu kiểm độc lập.

## 1. Đã làm gì

| Việc | Commit |
| --- | --- |
| 14 bộ nhận diện (regex + Luhn/BIN, mã tỉnh CCCD, check digit MST, ngữ cảnh), chạy cả trên view số của Lớp 1; chống trùng theo thứ tự ưu tiên | `f1664f6` |
| `PiiVault` trong bộ nhớ: placeholder ổn định theo phiên, chủ (`user_ref`), TTL | `f1664f6` |
| Chính sách 3 trạm theo `source`/`intent` (bảng B5.2); `restore`, `redact_for_log` hoạt động thật; cấu hình `pii.enabled`, `pii.vault_ttl_minutes` | `f1664f6` |
| PII không tăng `risk` (chỉ `action="mask"`); placeholder lạ → medium | `f1664f6` |
| Sửa Lớp 1: hex toàn chữ số không còn bị coi là chữ mã hoá (số thẻ từng bị báo `encoded`) | `f1664f6` |
| Sửa theo red-team dev: đơn vị tiền cần ranh giới chữ; ngữ cảnh sau giá trị; mở rộng OTP/mật khẩu; tên theo họ phổ biến | `b967922` |
| Held-out + test mức sàn; demo, README, tài liệu học | `1978cd0`, docs |

## 2. Số đo (output thật)

| Bộ | Recall | Bắt nhầm |
| --- | --- | --- |
| Tự sinh 125 + 36 | 100% | 0/36 |
| Red-team dev 88 + 40 (trước → sau khi sửa) | 69,3% → 98,9% | 0/40 |
| **Held-out 80 + 40 (không sửa theo)** | **90,0%** | **2/40** |

```text
pytest -q            → 589 passed, 2 xfailed
ruff                 → All checks passed!
p95 2KB              → chuẩn hoá 5,5 ms · luật 12,2 ms · PII 3,5 ms
held-out theo loại   → OTP 2/7, PASSWORD 3/4, CMND 3/4, PLATE 3/4, các loại khác đủ
```

## 3. Lỗi tự tìm và đã sửa

1. **Số thẻ viết liền không bị che trong log**, vì bộ loại trừ ID coi mọi chuỗi ≥ 16 ký tự hexa là hash. Đã sửa: hash phải có chữ a–f. Có test `redact_for_log` chạy trên toàn bộ fixture, không được còn giá trị gốc nào.
2. **Lớp 1 báo nhầm số thẻ là "đã mã hoá"** (`4242…` là hex hợp lệ, giải ra `BBBB…`). Đã sửa: hex phải có chữ a–f.
3. **Chữ `đ` trong "đây", "được" bị coi là đơn vị đồng**, làm số đứng trước bị bỏ qua. Đã sửa bằng ranh giới chữ.
4. MST trông như SĐT (`039…`) bị nhận nhầm. Đã sửa: MST và STK cần từ ngữ cảnh nên được ưu tiên hơn.
5. "Mã sản phẩm 100234567, tổng…" bị nhận là địa chỉ (`tổ` khớp vào đầu chữ `tổng`). Đã sửa bằng ranh giới chữ.
6. SĐT gõ dạng "băm" được trả lại y nguyên dạng băm. Giờ trả lại dạng chuẩn.

## 4. Còn mở

- **Spike NER** (underthesea / GLiNER) chưa làm. Tên viết thường hoặc chỉ có tên riêng bị lọt.
- OTP đứng một mình (2/7 held-out). Lớp 4 sẽ chặn bot **đòi** OTP.
- Tên cửa hàng giống tên người bị che (2/40 held-out).
- Vault một process; sidecar nhiều worker cần kho chung (Lớp 6).
- Không dùng Presidio (lý do: không có tiếng Việt, spaCy nặng, chậm trên CPU). Thư viện vẫn khai báo trong extra `pii`, có thể bỏ khi dọn phụ thuộc.
