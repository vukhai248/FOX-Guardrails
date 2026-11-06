# Sổ việc hoãn sau review (backlog)

Quy tắc từ 06/11/2026: mỗi lượt review, lỗi quan trọng (lọt PII, lọt tấn công, trả dữ liệu cho sai chủ) thì sửa ngay. Lỗi nhỏ, khó hoặc đã ổn thì ghi vào đây để làm sau. Mỗi dòng có nguồn để kiểm lại.

## Đã chốt lượt review 3 (PR #1), commit `387bb8a`

| Mục | Kết luận |
| --- | --- |
| 1 Vault fullwidth, 2 Email trong evidence, 6 Cờ giả, 8 Span lệch | Đã sửa từ trước trên `feat/lop-4` (A1, R4, A5, A8). Review chạy trên commit cũ `5c045ec` |
| 3 Emoji U+FE0F làm lọt mật khẩu/OTP | Đã sửa: bản bỏ dấu giữ đúng độ dài từng ký tự (`_fold`) |
| 4 Email có phần trước `@` giống hash | Đã sửa: EMAIL không bị loại như ID |
| 5 Địa chỉ nuốt ", email …" | Đã sửa: phần đuôi địa chỉ không bắt đầu bằng nhãn liên hệ |
| 7 `%20` không liên quan nâng mức | Đã sửa: chỉ nâng khi bản văn bản thường không khớp |

## Đã chốt lượt review 4 (PR #2 @ `5107339`)

5 mục P1, sửa theo nhóm nguyên nhân chứ không theo từng câu. Test D1–D6 hỏng trước khi sửa.

| Mục | Sửa |
| --- | --- |
| 1 Tên miền quốc tế (`straße`) | Host không phải ASCII hoặc có `xn--` không bao giờ khớp allowlist |
| 2 Tham chiếu nhiều dòng, `//host` | `_REFDEF` nhận đích ở dòng sau; mọi `//host/…` trong văn bản đều bị gỡ (sửa luôn H3). Thêm: `javascript:`, `data:` bị gỡ |
| 3 Placeholder trong hostname | Kiểm placeholder và PII trên toàn URL, giải `%XX` lặp tới khi ổn định |
| 4 Audit URL không scheme | Audit cắt đuôi cả URL không có `//` và xoá mọi chuỗi `%XX` |
| 5 Phủ định ở vế mục đích | Phủ định chỉ tính khi giữa nó và lời yêu cầu chỉ có từ của khung câu cảnh báo. Phủ định nằm trong lời yêu cầu luôn được tính. Sửa luôn 3 câu cảnh báo từng bị chặn nhầm ("Xin bạn đừng gửi…", "Vui lòng không cung cấp…", "Please never share…") |

## Đã chốt lượt review 5 (PR #2 @ `1c44bc6`)

Gốc chung của mục 1 và 3: Python `urlsplit` hiểu URL khác trình duyệt. Mình thay bằng một bộ tách URL theo quy tắc WHATWG (`detectors/url.py`), dùng chung cho link guard và audit.

| Mục | Sửa |
| --- | --- |
| 1 `https:///evil.example` | Bộ tách mới bỏ mọi `/` và `\` trước host như trình duyệt. URL http(s) không đọc được host thì bị gỡ. Thêm: `https:\\`, `https:evil`, `/\evil`, `%2E` trong host, `shop.example@evil.example`, tab trong `<…>` |
| 2 Email `%40` trong query | Chỉ tách giá trị theo dấu phân cách URL; giữ `.` và `@` |
| 3 Mật khẩu trong `user:pass@host` | Audit chỉ giữ `scheme://host` từ bộ tách mới; link có userinfo bị coi là mang PII. Đã kiểm cả SQLite và JSONL |
| 4 Lời dẫn + danh sách Markdown | Lời dẫn kết thúc bằng `:` được ghép với danh sách bên dưới; câu cảnh báo phủ định vẫn `allow` |

## Đã chốt lượt review 6 (PR #2 @ `8c8b98b`)

| Mục | Sửa |
| --- | --- |
| 1 Audit giải mã host sau bước che (lỗi do lượt 5 gây ra) | Đổi thứ tự: thu gọn URL trước, che PII sau. Dãy số trong host được thay bằng `***` |
| 2 Đích Markdown có ngoặc `a(b)` | Đọc đích theo CommonMark (ngoặc cân bằng, `<…>`). Link tới shop chỉ được giữ khi phần sau host gồm toàn ký tự an toàn: không `%`, `@`, `(`, `\`, dấu nháy. Cả nhóm lỗi "PII mã hoá trong link của shop" bị chặn từ gốc |
| 3 "đừng gửi email **mà** gửi OTP" | "mà" + động từ yêu cầu mở vế mới; sửa luôn lỗi `finditer(endpos)` làm lookahead không nhìn thấy phía sau |
| 4 Bản rõ che lấp chỉ dẫn mã hoá | Bản giải mã được xét thêm sau bản rõ; lần khớp chỉ có trong bản giải mã thì nâng lên `high` |

## Đã chốt lượt review 7 (PR #2 @ `839e49c`)

Từ lượt này áp dụng tiêu chí mới trong `docs/plans/prompts/codex-review.md`: P1 chỉ gồm dữ liệu rời khỏi hệ thống, trả PII cho sai chủ, và hồi quy.

| Mục | Kết luận | Sửa |
| --- | --- | --- |
| 1 HTML entity trong đích ảnh | P1, ảnh tải từ host ngoài | `parse_url` giải entity trước khi đọc host |
| 2 `xignore…` che lấp bản mã hoá | P1, hồi quy do lượt 6 | So với các lần luật thực sự khớp trên bản rõ |
| 3 Audit giữ `&#53;&#55;…` | P1, bí mật giải mã được trong log | Audit xoá mọi đoạn mà bộ giải mã đọc được: base64/hex, entity, `\u`, `%XX` |
| 4 "gửi mã dùng để không bị hủy đơn (OTP)" | **P2, hoãn (N1)** | Phạm vi phủ định, để Lớp 5 |

## Việc hoãn

Các ca dưới đây do bộ held-out `tests/fixtures/output_heldout.jsonl` (OpenCode, PR #3) phát hiện. **Không sửa bằng cách thêm đúng các câu này vào regex**, vì làm vậy là tune trên held-out. Khi làm thì viết câu dev mới cùng loại, rồi đo lại held-out đúng một lần.

| # | Loại lỗi | Ví dụ (id held-out) | Mức | Ghi chú |
| --- | --- | --- | --- | --- |
| H1 | Thiếu từ vựng tiếng Anh khi bot đòi bí mật: passport photo, online banking password, PIN, confirmation code, bank account number, card expiry, one-time password | oh-009, 010, 027, 040 | Cao | Lớp 5 (classifier) cũng phủ được |
| H2 | Teencode rút gọn "số tk + mk" | oh-018 | TB | Cần bảng teencode cho "tk", "mk" ở đầu ra |
| ~~H3~~ | ~~URL `//host/path` trần trong câu~~ | oh-061, 079 | — | **Đã sửa ở lượt 4** bằng quy tắc chung cho `//host` (không dựa trên câu held-out) |
| H4 | Phủ định bị cắt sớm khi danh sách dài hoặc khi có câu tiếp theo | oh-089, 129, 131 | TB | Bị chặn nhầm (false positive), không gây lọt dữ liệu |
| H5 | "mã PIN máy" (PIN mở khoá điện thoại) bị coi là đòi PIN | oh-091 | Thấp | |
| H6 | Hướng dẫn đổi mật khẩu trong app ("nhập mật khẩu cũ") bị chặn | oh-099 | TB | Cần phân biệt "nhập vào app" với "gửi cho shop" |
| R6 | Cờ giả: `hidden_tags` chỉ giải phần ẩn, câu ghép ẩn + hiện chưa được luật thấy trọn | Review 3 mục 6 | Thấp | Đã có tín hiệu `unicode:tags`. Muốn chặn hẳn thì luật chạy trên `hidden_tags + clean` |
| L1 | Link guard đọc Markdown bằng regex, không dùng parser CommonMark thật. Ví dụ HTML entity trong `href` (`ht&#9;tps:`) và `[a](ht\ttps://…)` không có ngoặc nhọn (CommonMark không coi là link) | Lượt 5, tự dò | TB | Cách chắc nhất: web hiển thị câu trả lời của bot với ảnh ngoài tắt và HTML thô tắt |
| L2 | "ASP.NET" bị gỡ như một link | Lượt 1 | Thấp | Chặn nhầm đã chấp nhận |
| N1 | Phủ định chi phối động từ khác nhưng nằm **trong** lời yêu cầu: "Bạn gửi mã dùng để không bị hủy đơn (OTP) nhé" → `allow` | Lượt 7 | TB | Không vá thêm regex phủ định; Lớp 5 (classifier/judge) nhận diện ý đồ đòi bí mật |
| L3 | Base64 trong query của link tới chính shop (`?t=MDkx…` là số điện thoại) không bị gỡ | Lượt 6, tự dò | Thấp | Dữ liệu chỉ tới máy chủ của shop. Muốn chặn thì chỉ cho query theo danh sách khoá (`q`, `page`, `sort`) |
| R0 | Tính độc lập O1: phiên chính của OpenCode đã đọc code trước, giao cho subagent mới viết | PR #3 báo cáo | Thấp | Lần sau giao O1 cho một phiên chỉ có prompt O1 |

## Số đo Lớp 4 trên held-out (đo 1 lần, 06/11/2026, commit `387bb8a`)

| Nhóm | Bắt đúng |
| --- | --- |
| Bot đòi bí mật (50) | 45/50 = 90% |
| Link nguy hiểm (30) | 28/30 = 93% |
| Câu hợp lệ cho qua (60) | 55/60 = 92% (chặn nhầm 8%) |

Đo lại sau lượt 4 (không chỉnh theo held-out): bot đòi bí mật 45/50 = 90%, link 30/30 = 100%, câu hợp lệ 56/60 = 93%.

Đây là số kiểm nội bộ, **không phải kết quả đồ án**. Kết quả chính thức dùng benchmark chuẩn (BIPIA, JailbreakBench) và bộ CSKH tiếng Việt chia theo template (xem `docs/DU-AN.md`).
