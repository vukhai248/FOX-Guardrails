# eval/datasets — dữ liệu thực nghiệm (Phần C1)

| Bộ | Nguồn | Cách tạo | Chia dev/test |
| --- | --- | --- | --- |
| `vi_cskh/` | Tự xây (đóng góp chính) | Mẫu gốc trong `templates/` (bạn duyệt) → `build.py` thêm biến thể T3 (zero-width, Unicode Tags, homoglyph, fullwidth, base64, không dấu, teencode) cho ~40% ca tấn công | 30/70 theo `template_id` |
| `pii/` | Tự xây | Mẫu câu có chỗ trống `{PHONE}`… → `build.py` điền **số giả đúng checksum** (Luhn, mã tỉnh CCCD, chữ số kiểm tra MST), sinh span vàng, thêm biến dạng T3.12 | 30/70 theo `template_id` |
| BIPIA | microsoft/BIPIA (MIT) | `external/fetch.py bipia` (Email QA, Table QA) | attack-train = dev, attack-test = test |
| JailbreakBench | JBB-Behaviors + artifacts (MIT) | `external/fetch.py jbb` | toàn bộ là test |
| openpii `vi` | ai4privacy (CC-BY-4.0, PII tổng hợp) | `external/fetch.py openpii` (1.000 dòng `vi`, đọc qua API, không tải file 1–4 GB) | toàn bộ là test |

**Nguyên tắc:**
- Mẫu gốc do **tác tử độc lập** viết. Tác tử này không đọc code của FOX-Guard, chỉ đọc mô hình tấn công `docs/plans/01-tan-cong-va-phong-thu.md`.
- Biến thể T3 viết theo định nghĩa trong mô hình tấn công, **không** dựa vào bộ chuẩn hoá của FOX-Guard.
- Mọi biến thể của một mẫu gốc nằm cùng một phía dev/test. Mẫu trùng hẳn hoặc gần trùng (Jaccard 5-gram ≥ 0,8) giữa hai phía được chuyển hết về dev.
- **Chốt ngưỡng trên dev; test chạy một lần.** Không chỉnh code theo test.
- Không có PII thật; tên miền chỉ dùng `shop.example` và `*.example`.
- Dữ liệu tải về nằm ở `data/raw/` (không commit).

```bash
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m eval.datasets.vi_cskh.build
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m eval.datasets.pii.build
```
