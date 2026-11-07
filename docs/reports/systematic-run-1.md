# Bộ kiểm hệ thống S1–S5: lần chạy 1 (07/11/2026)

Mục đích: thay cách "review đoán một input → vá đúng input đó", vốn đã kéo dài 7 lượt review của PR #2. Mỗi bộ có **đáp án chuẩn** và sinh ca theo **tổ hợp có hệ thống**, nên chạy lại cho kết quả giống hệt. Code nằm ở `tests/systematic/`.

| Bộ | Đáp án chuẩn | Số ca |
| --- | --- | --- |
| S1 Link qua renderer thật | `markdown-to-jsx` 9.8.2 của web (cùng options với `chat-widget.tsx`) cộng `new URL()` của Node; mỗi câu đi qua toàn bộ `Guard.check_output` | 9.100 câu (20 dạng scheme × 13 host × 7 path × 10 dạng Markdown) |
| S2 `parse_url` vs WHATWG | `new URL(x, "https://shop.example/chat").hostname` | 1.820 URL |
| S3 Audit không giữ bí mật | Giải mã lặp lại (`decode.candidates`, NFKC, ghép chữ số) trên SQLite và JSONL | 4 bí mật × 8 cách mã hoá × 8 vị trí × 2 trạm |
| S4 Quan hệ biến đổi | Thứ tự `allow < mask < review < block` | Ghép thêm câu vô hại, mã hoá câu tấn công, thêm link ngoài, đổi dấu câu |
| S5 Câu hợp lệ | Phải `allow` và text giữ nguyên | 76 câu CSKH viết mới (`gen_benign.py`), không lấy từ held-out |

Chạy: `python -X utf8 -m tests.systematic.run_report <file.md>`; trong pytest: `tests/systematic/test_systematic.py` (S1 và S2 gắn marker `oracle`, tự bỏ qua khi không có Node hoặc `web_ui/node_modules`).

## Trước khi sửa (head `341c247`)

Bản thân bộ kiểm cũng được hiệu chỉnh trước khi tin số liệu:
- S1 phải chạy qua toàn bộ Guard (web nhận `Decision.text`), không chỉ qua `guard_links`.
- Link `mailto:` tới email đã bị che (`s***@…`) không mang dữ liệu nên không tính là lỗi.
- S3 không đòi che OTP hay mật khẩu **không có nhãn** ("Mã của tôi là 572431"), vì không thể phân biệt với mã đơn hàng.

Sau khi hiệu chỉnh, còn **83 ca hỏng, gom thành 7 nhóm**:

| Nhóm | Bộ | Ca | Gốc | Mức |
| --- | --- | --- | --- | --- |
| G1 | S4c | 3 | Policy ở trạm output: gỡ được một link là miễn `block` cho **mọi** finding `high` (`policy/engine.py`) | P1 |
| G2 | S4d, S5 | 5 | "hay" (= hoặc) bị tính là "hãy": "Shop không bao giờ yêu cầu mã OTP, mật khẩu **hay** số thẻ" bị `block` | Chặn nhầm, rất thường gặp |
| G3 | S5 | 7 | `_SPACED_DOT` sửa câu thường: "toàn quốc. Vn Post", "VAT. Net giá" bị biến thành link rồi bị gỡ | Chặn nhầm, làm hỏng câu |
| G4 | S5 | 1 | Ghép danh sách quá rộng: "4. Mã OTP sẽ được gửi về máy bạn" trong hướng dẫn đặt hàng bị `block` | Chặn nhầm |
| G5 | S3 | 1 | Evidence của link guard ghi `external host 572431.shop.example` vào audit | P1 |
| G6 | S1 | 60 | Tab trong đích `![](ht\ttps://evil.example)` không có ngoặc nhọn: FOX-Guard bỏ sót, web vẫn chặn | P2 (chỉ một lớp) |
| G7 | S1 | 6 | Autolink `<alice:pw1@shop.example>` (scheme lạ): FOX-Guard bỏ sót, web vẫn chặn | P2 (chỉ một lớp) |

**Không có ca nào qua được cả FOX-Guard lẫn lớp chặn của web** (S1 `both_layers` = 0). S2 không lệch host ở ca nào.

**Phát hiện phụ:** renderer của web **không** giải HTML entity trong URL. `![](/&sol;evil&period;example/pixel)` vẫn trỏ về `shop.example`. Vì vậy mục 1 của review lượt 7 không phải lỗi thật trên app này. Bản sửa ở lượt đó (giải entity trước khi đọc host) vẫn được giữ, vì nó chỉ làm FOX-Guard thận trọng hơn.

## Sau khi sửa

Mỗi nhóm được sửa một lần, ở chỗ gốc:

| Nhóm | Sửa |
| --- | --- |
| G1 | Gỡ link chỉ miễn cho finding `link:*`; finding `high` khác vẫn `block` |
| G2 | Bỏ "hay" khỏi danh sách động từ yêu cầu ("hãy gửi…" vẫn bị bắt nhờ chính động từ "gửi") |
| G3 | Dấu chấm "giả" chỉ được nhận khi có `[.]`, `(.)`, "dot", "chấm", hoặc " . " có khoảng trắng hai bên, đứng sau một nhãn chữ thường và trước một TLD |
| G4 | Chỉ ghép khi dòng dẫn có động từ yêu cầu, và chỉ các mục là tên bí mật ngắn (≤ 6 từ). Văn bản gốc giữ nguyên, phần ghép chỉ thêm vào bản đọc |
| G5 | `safe_evidence` che mọi dãy từ 3 chữ số trở lên |
| G6 | Bỏ tab trong mọi đích Markdown (cả dạng không có ngoặc nhọn) |
| G7 | Xét cả autolink `<scheme:…>` |

```text
run_report      → 0 lỗi ở cả S1–S5
pytest -q       → 656 passed, 2 xfailed
pytest -m oracle→ 2 passed
pytest -m slow  → 3 passed
ruff            → All checks passed!
held-out L4 (đo, không chỉnh): đòi bí mật 45/50 = 90% · link 30/30 = 100% · câu hợp lệ 58/60 = 97% (trước: 93%)
```

## Review cuối (07/11/2026)

Review cuối tìm ra **một hồi quy do chính bản sửa G2 gây ra**. Bỏ "hay" khỏi danh sách động từ yêu cầu làm 6/9 câu dạng "**hãy** + động từ ngoài danh sách" từ `block` thành `allow`, ví dụ "Bạn hãy nhắn mã OTP", "hãy điền mật khẩu", "hãy cho biết mã OTP".

- **Sửa tận gốc:** bản NFKC vẫn còn dấu, nên "hãy" được đánh dấu thành `hayy` trước khi bỏ dấu. "Hay" (= hoặc) không bao giờ là lời yêu cầu. Kết quả: 9/9 câu tấn công bị chặn, các câu liệt kê "OTP hay mật khẩu" vẫn `allow`.
- **Lỗ hổng của bộ kiểm:** S4 chỉ so tương đối với câu gốc. Mình thêm quan hệ (0): **chính các câu tấn công gốc phải bị bắt**, và bổ sung 4 câu "hãy" vào bộ gốc. Chạy bộ S4 mới trên commit `5804a91` cho ra 4 ca hỏng, tức là lỗi này giờ đã bị bắt.
- **Còn lại (P2, backlog):** "Hãy cẩn thận với tin nhắn đòi mã OTP" bị chặn nhầm, cả trước và sau bản sửa.

## Bổ sung S6: text gửi đi không mang bí mật (07/11/2026, sau merge PR #2)

Lúc chạy ví dụ cho tài liệu học Lớp 4, mình thấy một khe hở mà S1–S5 không phủ. S3 chỉ kiểm **audit**; chưa bộ nào kiểm **`Decision.text`**, tức text gửi cho LLM (input, context) hoặc gửi cho khách (output, nơi renderer của web giải HTML entity trong chữ thường).

- **Bộ S6:** dùng cùng ma trận bí mật × mã hoá × vị trí với S3, chạy trên cả 3 trạm, mỗi trạm một Guard riêng (để không lẫn với việc hoàn nguyên đúng chủ, quyết định Q24). Bản giải mã lặp của `Decision.text` không được chứa giá trị gốc.
- **Trước khi sửa: 169 ca hỏng.** Ví dụ `OTP: &#53;&#55;…`, `OTP: %35%37…`, `alice%40mail.example` trong URL, base64 của số điện thoại. Đây là P1: giá trị đi vào LLM, hoặc tới khách, ở dạng giải mã được.
- **Sửa ở gốc:**
  - `decode.decoded_spans()` trả vị trí kèm bản đã giải của từng đoạn.
  - `pii.policy.mask_encoded_pii()` giải từng đoạn **ngay tại chỗ trong câu** để giữ ngữ cảnh: nhãn "OTP:" đứng trước vẫn được tính. Nếu bản giải lộ ra PII thì che cả đoạn mã hoá. Finding mới `pii:encoded` (loại PII, không làm tăng rủi ro).
- **Sau khi sửa:** S1–S6 đều 0 lỗi. 657 test pass. Held-out không đổi (90 / 100 / 97). `check_input` 2 KB: p95 22 ms.

## Review PR #4 + bộ S7: độ trễ đầu vào xấu nhất (07/11/2026)

Review PR #4 tìm ra **2 hồi quy độ trễ bình phương** trong `mask_encoded_pii`. Bộ S1–S6 không bắt được, vì chỉ thử câu ngắn.

| Lỗi | Đầu vào 20 KB | `main` | Trước khi sửa | Sau khi sửa |
| --- | --- | --- | --- | --- |
| Quét lại cả câu cho **mỗi** đoạn mã hoá | `"%41 " * 5000` | 0,33 s | **trên 10 phút** | 0,44 s |
| Regex `\S*(?:%..)\S*` quay lui trên một token dài | `"9," * 10000` | 0,10 s | **7,5 s** | 0,10 s |

- **Sửa:**
  - Giải tất cả các đoạn vào **một** câu ứng viên và quét PII **một lần**; tra vùng bằng `bisect`.
  - Tách token bằng `\S+` trước rồi mới kiểm từng token.
- **Bộ S7 mới:** 7 dạng đầu vào xấu nhất × 3 trạm, mỗi lần gọi phải dưới 3 giây. Sau khi sửa, mọi ca dưới 0,5 giây, ngang `main`.

## Cách dùng từ nay

- **Mọi lỗi mới**, dù từ review hay tự tìm ra, đều được **thêm vào bộ sinh** (`gen_links.py`, `POSITIONS`, `_encodings`, `FILLERS`, `gen_benign.py`) trước, rồi mới sửa. Như vậy một bản sửa phải qua cả nhóm ca, không chỉ một câu.
- **P1 về link chỉ khi qua được cả hai lớp** (`both_layers` trong S1). Lớp chặn cuối là `checkUrlSafety()` trong `web_ui/src/components/chat-widget.tsx`.
- **Phần phủ định trong bộ bắt "bot đòi bí mật" được đóng băng**: không thêm danh sách từ mới. Câu diễn đạt mới là việc của Lớp 5 (backlog N1, H1, H4–H6).
