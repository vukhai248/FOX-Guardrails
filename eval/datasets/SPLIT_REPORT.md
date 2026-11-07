# SPLIT_REPORT — dữ liệu thực nghiệm Phần C1 (07/11/2026)

Chi tiết từng bộ tự xây: `vi_cskh/SPLIT_REPORT.md`, `pii/SPLIT_REPORT.md`. Bộ ngoài được tạo lại bằng `eval/datasets/external/*.py` từ `data/raw/` (không commit).

| Bộ | Vai trò | Dev (chốt ngưỡng) | Test (báo cáo) | Khoá chia |
| --- | --- | --- | --- | --- |
| **BIPIA** (EN, gián tiếp) | Phát hiện injection trong dữ liệu | 150 tấn công + 150 sạch | **300 tấn công + 150 sạch** | Nhóm tấn công: train và test là **15 nhóm khác nhau** (do BIPIA chia) |
| **JailbreakBench** (EN, trực tiếp) | Phát hiện jailbreak | — | **286 prompt tấn công** (PAIR, GCG; 152 jailbreak thành công) + 100 lành tính; 100 goal độc hại trần **báo riêng** | Toàn bộ là test |
| **CSKH tiếng Việt** | Chặn nhầm trên dữ liệu thật của shop | 59 (hard-benign 36, clean 23) | **141** (hard-benign 84, clean 57) | 30/70 theo `template_id` |
| **PII tổng hợp VI** | P/R/F1 theo thực thể | 88 | **203** (153 PII, 50 dễ nhầm) | 30/70 theo `template_id` |
| **openpii vi** (ai4privacy) | PII bên ngoài | — | **1.000** câu | Toàn bộ là test |

**Kiểm trùng:** không có mẫu nào trùng hẳn hoặc gần trùng (Jaccard 5-gram ≥ 0,8) giữa dev và test ở bộ CSKH và bộ PII. Trong cùng một tập, bộ PII có 2 câu trùng do hai lần điền giống nhau; bộ CSKH không có.

**Chi tiết BIPIA:**
- Ngữ cảnh: Email QA và Table QA. WebQA và Summarization cần tải NewsQA/XSum nên chưa dùng.
- Mỗi lời tấn công được chèn vào đầu, giữa hoặc cuối ngữ cảnh, chia đều 3 vị trí.
- Test có 150 ca email và 300 ca table.

**openpii, ánh xạ nhãn sang FOX:**

| openpii | FOX |
| --- | --- |
| GIVENNAME + SURNAME | `PERSON` (gộp khi đứng liền nhau) |
| STREET, BUILDINGNUM, CITY, ZIPCODE | `VN_ADDRESS` (gộp khi đứng liền nhau) |
| TELEPHONENUM | `VN_PHONE` |
| EMAIL | `EMAIL` |
| IDCARDNUM | `VN_ID` (so chung với CCCD/CMND) |
| CREDITCARDNUMBER | `CREDIT_CARD` |
| TAXNUM | `VN_TAX_ID` |
| PASSPORTNUM | `VN_PASSPORT` |

- Không tính, vì FOX không có loại tương ứng: SOCIALNUM (184), DRIVERLICENSENUM (163), ACCOUNTNUM (1).
- Không phải PII với FOX: DATE, TIME, AGE, GENDER, SEX, TITLE.
- **Lưu ý khi đọc kết quả:** số trong openpii là số tổng hợp chung, không nhất thiết đúng định dạng Việt Nam (đầu số di động, mã tỉnh, checksum). Recall của các bộ nhận diện có kiểm checksum sẽ thấp hơn trên bộ này. Đây là một phát hiện cần báo cáo, không phải lỗi dữ liệu.

**Còn thiếu:**
- **Ca tấn công tiếng Việt của bộ CSKH.** Agent viết mẫu bị bộ lọc an toàn dừng. Bạn đã chọn tạm dùng BIPIA và JBB cho phần tấn công. Vì vậy bộ CSKH tiếng Việt hiện chỉ đo **chặn nhầm**, chưa đo tỉ lệ bắt tấn công tiếng Việt.
- **Bạn duyệt mẫu gốc** (đặc tả §2.3): `vi_cskh/templates/benign_templates.jsonl`, `pii/templates/pii_templates.jsonl`.
