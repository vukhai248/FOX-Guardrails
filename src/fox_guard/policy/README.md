# Policy Lớp 4 — gộp rủi ro và chọn hành động

`decide(station, findings, text, pii_changed, link_edited, texts)` (`policy/engine.py:37-64`) nhận
finding của cả 3 lớp và trả `Verdict(action, text, risk, flags)`. `Guard._check` gọi hàm này sau khi
chạy luật, detector đầu ra và PII (`guard.py:131-134`).

## Gộp rủi ro

- Lấy mức cao nhất trong các finding nguy hiểm (`policy/engine.py:32-34`).
- PII **không** tính vào rủi ro vì PII được che chứ không phải tấn công; ngoại lệ là placeholder lạ
  (`policy/engine.py:33`).
- Chưa có classifier Lớp 5 nên chưa áp dụng luật "hai tín hiệu độc lập"; mức của luật giữ nguyên
  (`policy/engine.py:2-6`).

## Hành động theo trạm (`policy/engine.py:41-64`)

| Trạm | `high` | `medium` | Còn lại |
| --- | --- | --- | --- |
| `input` | `block` + câu từ chối | `review` + `harden_prompt`, `session_flagged` | `allow` |
| `context` | `block` cả đoạn + `require_confirmation` | `review` + `require_confirmation` | `allow` |
| `output` | `block` (solicitation/link exfil) | `review` | `mask` nếu PII/link đã sửa, không thì `allow` |

- `context` `high` ẩn cả đoạn vì chưa cắt được từng câu (Lớp 5) (`policy/engine.py:48-49`).
- `output` ưu tiên `solicitation`, rồi `link:exfil`, rồi `high` không phải link đã gỡ
  (`policy/engine.py:53-61`).
- Link ngoài/giả dạng đã bị gỡ tại chỗ nên trả `mask`, giữ phần trả lời còn dùng được
  (`policy/engine.py:59-61`).

## Câu thay thế

- Câu mặc định ở `config.py:47-58`; đổi được trong `fox-guard.yaml` mục `policy`
  (`fox-guard.yaml:21-22`).
- `harden_prompt_text` là lời nhắc app thêm vào prompt khi có flag `harden_prompt`
  (`guard.py:175-178`).

## Giới hạn

- Chưa có classifier/judge nên chưa dùng công thức "classifier + luật" của plan (`policy/engine.py:2-6`).
- `context` chỉ ẩn cả đoạn; cắt đúng câu là việc của Lớp 5.
