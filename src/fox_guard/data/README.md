# Dữ liệu chuẩn hoá

## Unicode confusables

- Phiên bản: Unicode Security Mechanisms / UTS #39 **16.0.0**.
- Nguồn gốc: https://www.unicode.org/Public/security/16.0.0/confusables.txt
- Tải ngày: 2026-11-03; giữ nguyên bytes của bản chính thức.
- SHA-256: `95bd0aad6dced5ebc63436f459c06ab21a8d107cd842fb57f5c3a1e91bca8611`.
- License: Unicode License v3; bản đầy đủ trong `LICENSE-UNICODE.txt`.
- License gốc: https://www.unicode.org/license.txt (tải cùng ngày).
- Parser nạp một lần (`lru_cache`), không đọc file trong mỗi lần normalize.
- Các thuộc tính Unicode runtime đến từ Python `unicodedata` và `regex`,
  không giả định cùng phiên bản với bảng confusables.

## Teencode

`teencode_vi.tsv` thuộc Anti, được quản lý độc lập. Header bắt buộc:
`teencode`, `chuan`, `ambiguous`; dòng `#` là metadata/version.
Chỉ thay dòng `ambiguous=0`. Bảng chưa có → mapping rỗng, không đoán thay.
