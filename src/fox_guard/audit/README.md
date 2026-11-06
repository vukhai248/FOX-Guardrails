# Audit Lớp 4 — nhật ký quyết định đã che PII

`AuditStore` (`audit/store.py:42-102`) ghi một file SQLite. Audit mặc định tắt (`config.py:41`); bật
bằng `audit.enabled: true` (`fox-guard.yaml:24-27`).

## Bảng dữ liệu

- `decisions`: một dòng cho mỗi `Decision`, cột theo `audit/store.py:13-29` — id, ts, station, source,
  session_ref, user_ref_hash, arm, action, risk, reasons_json, findings_json, text_redacted,
  latency_ms, degraded, config_version.
- `reviews`: `decision_id`, reviewer, verdict (`approve`/`reject`), note, ts (`audit/store.py:32-38`).

## Chỉ lưu bản đã che

- `Guard._audit` gọi `redact_text` rồi `_strip_url_tails` trước khi ghi (`guard.py:163-173`).
- URL chỉ giữ host; path/query bị thay bằng `/[đã lược]` (`guard.py:28-33`).
- Nếu engine PII lỗi, không lưu text: `[không lưu: lỗi khi che PII]` (`guard.py:169-171`).
- Không lưu: text gốc, giá trị PII, placeholder có thể hoàn nguyên, user id thô.

## Salt băm user_ref

- `user_ref_hash = sha256(salt + 0x1f + user_ref)` (`audit/store.py:59-62`).
- Salt đọc từ biến môi trường `FOX_AUDIT_SALT` (`config.py:43-44`, `audit/store.py:55-57`); không đặt
  salt trong YAML.
- Không có salt: dùng salt ngẫu nhiên mỗi process; hash không liên kết được giữa các lần chạy
  (`audit/store.py:48-50`).

## CLI

- `fox-guard audit why <decision_id> --db ...` in lý do, finding và text đã che (`cli.py:80-95`).
- `fox-guard audit export <out.jsonl> --db ...` xuất toàn bộ quyết định (`cli.py:98-104`).
- `export_jsonl` từ chối ghi đè chính file SQLite (`audit/store.py:87-98`).

## Giới hạn

- Ghi tuần tự trong một process nhờ `threading.Lock` (`audit/store.py:51-53, 72-74`).
- Chưa có hash-chain chống sửa file; `reviews` chưa có giao diện duyệt.
