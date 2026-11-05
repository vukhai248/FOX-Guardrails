# Lớp 3 — PII tiếng Việt và giả danh hoá có hoàn nguyên

> Cập nhật 05/11/2026. Code: `src/fox_guard/pii/`. Đọc sau [Lớp 2](lop-2-luat.md).

## 1. Lớp này chặn rủi ro gì?

PII (thông tin cá nhân) bị rò theo 7 kiểu P1–P7 ([bảng](../plans/01-tan-cong-va-phong-thu.md:148)). Lớp 3 lo 5 kiểu, **kể cả khi không có ai tấn công**:

| Mã | Rò thế nào | Ví dụ trong shop | Lớp 3 làm gì |
| --- | --- | --- | --- |
| P1 | Tool đưa PII thừa sang nhà cung cấp LLM | `order_lookup` gửi nguyên địa chỉ + SĐT cho Gemini khi khách chỉ hỏi "đơn tới đâu rồi" | Chỉ giữ tỉnh/thành, SĐT thay bằng `<PHONE_2>` |
| P2 | Khách tự gõ PII, bị gửi thẳng cho LLM | "SĐT mình 0912345678, CCCD 0792…" | Thay bằng `<PHONE_1>`, `<CCCD_1>` trước khi gửi |
| P3 | Bot in PII không cần, hoặc của người khác | In đủ số thẻ, CCCD; in SĐT của người viết review | Che ở đầu ra; chỉ trả lại SĐT/email/địa chỉ **cho đúng chủ** |
| P5 | PII nằm trong log | `chat_logs`, audit | `redact_for_log` che không thể khôi phục |
| P6 | PII bị biến dạng để lọt bộ lọc | `0 9 1 2 . 3 4 5 . 6 7 8`, "không chín một hai…" | Đọc qua bản số của Lớp 1 |

P4 (bot **đòi** PII) thuộc Lớp 4. P7 (suy luận PII từ nhiều câu) nằm ngoài phạm vi.

## 2. Cách hoạt động (không cần đọc code)

**Nhận diện 14 loại:** SĐT, CCCD, CMND, thẻ ngân hàng, số tài khoản, mã số thuế, hộ chiếu, biển số xe, BHYT, OTP, mật khẩu, email, họ tên, địa chỉ.
- Số có quy tắc kiểm thì **kiểm thật**: thẻ theo thuật toán Luhn và đầu số Visa/Mastercard/NAPAS…; CCCD theo mã tỉnh và mã thế kỷ; MST theo chữ số kiểm tra.
- Số dễ trùng với số khác (CMND 9 số, số tài khoản, hộ chiếu) **chỉ được nhận khi có từ ngữ cảnh** ("stk", "chuyển khoản", "hộ chiếu"…), xét cả trước lẫn sau con số.
- **Không bắt nhầm** giá tiền (`25.990.000đ`, `990k`), mã đơn UUID, hash, mã giảm giá, năm, phần trăm.
- Họ tên: bắt sau "Người nhận:", "anh/chị…", hoặc chuỗi viết hoa bắt đầu bằng **họ phổ biến** (Nguyễn, Trần, Lê…), trừ tên địa danh và tên đường như "Hà Nội", "Lê Lợi".

**Giả danh hoá khác che thế nào?**
- **Che** là `0912***678`: mất hẳn, không lấy lại được.
- **Giả danh hoá** là thay bằng `<PHONE_1>`. Bản đồ `<PHONE_1> → 0912345678` nằm **trong bộ nhớ** của guard (theo phiên, tự hết hạn sau 60 phút, không ghi đĩa, không vào log), kèm **chủ** của giá trị. LLM vẫn làm được việc ("shop sẽ gọi `<PHONE_1>`"), còn Google không thấy số thật. Đến đầu ra, guard đổi `<PHONE_1>` lại thành số thật, **chỉ khi người đọc đúng là chủ**.

**Theo từng trạm:**

| | INPUT (khách gõ) | CONTEXT (dữ liệu tool) | OUTPUT (trả lời) |
| --- | --- | --- | --- |
| CCCD, thẻ, STK, MST, hộ chiếu, BHYT | giả danh hoá | giả danh hoá | luôn **che** (thẻ, STK che toàn bộ) |
| OTP, mật khẩu | giả danh hoá | giả danh hoá | **xoá** |
| SĐT, email | giả danh hoá | giả danh hoá (hoặc che một phần nếu intent cần liên hệ) | trả lại **chỉ cho chủ** |
| Địa chỉ | giả danh hoá | hỏi "đơn tới đâu" → **chỉ còn tỉnh/thành**; đổi địa chỉ → giữ đủ | trả lại chỉ cho chủ |
| Họ tên | giữ (để bot xưng hô) | review của người khác → **che** | giữ |

Có PII thì `action = "mask"`. PII **không** làm tăng mức rủi ro: khách tự gõ số thẻ của mình không phải là tấn công. Ngoại lệ là khi bot đưa ra một placeholder lạ như `<PHONE_9>` mà guard chưa từng cấp: đây là dấu hiệu bot bịa hoặc bị dụ, nên được báo mức medium.

## 3. Chạy thử

```powershell
cd D:/create/DATN/.worktrees/b-core
./.venv/Scripts/python.exe -X utf8 scripts/demo_lop3.py
```

Output thật (05/11/2026):

```text
1. INPUT  (khách A gõ, gửi LLM):
   action=mask  text=SĐT mình <PHONE_1>, CCCD <CCCD_1>, đổi giúp số nhận hàng
2. CONTEXT (tool tra đơn của khách A, hỏi 'đơn tới đâu rồi'):
   action=mask  text=Người nhận: Nguyễn Văn An, SĐT <PHONE_2>, Hà Nội
3. CONTEXT (review của người khác):
   action=mask  text=Anh [tên] sđt <PHONE_3> khen máy chạy êm
4. OUTPUT cho chính khách A:
   action=mask  text=Dạ shop sẽ gọi 0912345678 để xác nhận, CCCD 0792******34 đã ghi nhận. Mã lạ: <PHONE_9>
5. OUTPUT nếu người khác đọc được:
   action=mask  text=Dạ shop sẽ gọi 0912***678 để xác nhận, CCCD 0792******34 đã ghi nhận. Mã lạ: <PHONE_9>
6. OUTPUT bot lỡ in số thẻ và OTP:
   action=mask  text=Thẻ [số thẻ đã che], mã OTP là [đã xoá]
7. LOG (che không hoàn nguyên được):
   SĐT 0912***678, [PHONE], thẻ [số thẻ đã che], mk: [đã xoá]
```

Đọc kết quả:
- Dòng 1: khách gõ SĐT kiểu "băm" mà vẫn bị bắt.
- Dòng 2: Gemini chỉ thấy "Hà Nội", không thấy số nhà.
- Dòng 4 và 5: cùng một câu trả lời, khách A thấy số thật, người khác chỉ thấy số đã che.
- Dòng 4: CCCD không bao giờ được trả lại nguyên số, kể cả cho chủ.
- Dòng 7: log không còn giá trị nào lấy lại được.

## 4. Đo được bao nhiêu? (con số thật)

| Bộ đo | Ai viết | Bắt được | Bắt nhầm |
| --- | --- | --- | --- |
| 125 câu tự sinh + 36 câu không có PII | Claude (cùng người viết code) | 100% | 0/36 |
| Red-team dev, 88 câu PII + 40 câu không PII | Tác tử khác (chỉ viết câu; số giả do script điền) | **69,3%** trước khi sửa → 98,9% sau khi sửa | 0/40 |
| **Held-out, 80 câu PII + 40 câu không PII** | Tác tử khác, viết sau khi code đã chốt, yêu cầu "khó hơn" | **90,0%** (72/80) | **2/40** |

Held-out theo loại:
- Bắt đủ: thẻ, email, họ tên, địa chỉ, số tài khoản, CCCD, MST, hộ chiếu, BHYT, SĐT (7/7 hoặc 4/4).
- Chưa đủ: mật khẩu 3/4, CMND 3/4, biển số 3/4.
- **OTP yếu nhất: 2/7**, vì người ta đọc "857371 đây ạ" mà không có từ "mã" hay "OTP" nào.

Hai lỗi bắt nhầm là tên cửa hàng trông như tên người ("Nguyễn Kim", "Hoàng Hà mobile"). Hậu quả chỉ là tên đó bị che, không bị chặn.

Lúc sửa trên tập dev, tôi tìm ra **lỗi thật**: bộ lọc "số tiền" coi chữ `đ` trong "**đ**ây", "**đ**ược" là đơn vị đồng. Nhờ vậy "0835687327 đây là số của em" từng **lọt hoàn toàn**. Đã sửa bằng cách kiểm ranh giới chữ.

Độ trễ: 3,5 ms (p95) cho 2 KB.

## 5. Code nằm ở đâu?

| File | Làm gì |
| --- | --- |
| [recognizers.py](../../src/fox_guard/pii/recognizers.py:1) | 14 bộ nhận diện, Luhn/CCCD/MST, ngữ cảnh trước–sau, chống trùng, chạy trên bản số |
| [vault.py](../../src/fox_guard/pii/vault.py:1) | Kho giả danh trong bộ nhớ: placeholder ổn định, chủ, hết hạn |
| [policy.py](../../src/fox_guard/pii/policy.py:1) | Chính sách 3 trạm, cách che, chỉ giữ tỉnh/thành, che cho log |
| [guard.py](../../src/fox_guard/guard.py:1) | Gắn vào `check_input/context/output`, `restore`, `redact_for_log` |
| [tests/test_pii.py](../../tests/test_pii.py:1) | Checksum, ca khó, vault, vòng hoàn nguyên đúng/sai chủ, log không còn PII, 2 bộ red-team |
| [scripts/gen_pii_fixtures.py](../../scripts/gen_pii_fixtures.py:1), [fill_pii_slots.py](../../scripts/fill_pii_slots.py:1), [eval_pii.py](../../scripts/eval_pii.py:1) | Sinh số giả hợp lệ, điền vào câu của tác tử khác, đo theo loại |

## 6. Giới hạn

- **Tên và địa chỉ chỉ theo từ khoá và họ phổ biến**, chưa có mô hình NER. Tên viết thường, chỉ có tên riêng ("bé Na"), hay địa chỉ không có phường/quận sẽ lọt. Spike NER (underthesea / GLiNER) vẫn là việc mở.
- **OTP đứng một mình** (6 số không kèm từ khoá) không phân biệt được với mã đơn hay số lượng. Lớp 4 bù một phần: bot sẽ không được phép **đòi** OTP.
- Kho giả danh nằm trong bộ nhớ của một process. Khi chạy sidecar nhiều worker (Lớp 6) phải dùng chung một kho.
- Không dùng Presidio: không có tiếng Việt, cần model spaCy vài trăm MB và chạy chậm trên CPU. Với số và mã của Việt Nam, regex kèm checksum và ngữ cảnh là đủ và dễ giải thích.
- Mọi bộ đo do AI viết. Số chính thức sẽ đo trên bộ PII của Phần C và trên `openpii` tiếng Việt.

## 7. Hội đồng có thể hỏi

- **Giả danh hoá khác che thế nào, sao không xoá luôn?** Xoá thì bot không làm được việc "đổi số nhận hàng". Giả danh hoá giữ được tác vụ, nhà cung cấp LLM không thấy số thật, và chỉ chủ mới được thấy lại.
- **Bản đồ placeholder để ở đâu, lỡ lộ thì sao?** Chỉ trong RAM, theo phiên, tự hết hạn sau 60 phút, không ghi đĩa và không vào log. Log dùng bản che không hoàn nguyên được, nên lộ log cũng không lộ PII.
- **Làm sao biết người đọc là chủ?** Mỗi giá trị nhớ `user_ref` của người cung cấp. SĐT trong review của người khác có chủ là "không ai", nên không bao giờ được trả lại.
- **Sao số tài khoản cần ngữ cảnh mà thẻ thì không?** Thẻ có Luhn và đầu số, gần như không trùng ngẫu nhiên. Số tài khoản chỉ là 9–16 chữ số, trùng với mã đơn hay số lượng, nên phải có chữ "stk", "ngân hàng"… mới nhận.
- **Có PII thì có chặn tin nhắn không?** Không. PII được **che**, không chặn. Chặn chỉ dành cho tấn công (Lớp 4). Khách tự gõ số điện thoại để đổi địa chỉ là hoàn toàn hợp lệ.
