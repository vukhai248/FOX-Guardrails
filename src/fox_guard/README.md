# FOX-Guard SDK — Đợt 1

- `types.py`: hợp đồng `GuardContext`, `Finding`, `Decision` (Pydantic v2).
- `config.py`: đọc YAML; mọi cấp cấu hình từ chối khoá lạ.
- `guard.py`: `Guard.from_config`, ba hàm `check_*`, `restore`, `redact_for_log`.
- Input: chuỗi Unicode và `GuardContext`; output: `Decision` chứa `clean`.
- `Finding.span` là khoảng nửa mở `[start, end)` trên `clean`, hoặc `None`.
- `Finding.evidence` tối đa 120 ký tự; bên tạo finding chịu trách nhiệm che PII.
- Đợt 1 luôn `allow`, kể cả khi `risk=high`; chưa chặn gì cho tới Đợt 4.
- `risk` là severity cao nhất trong tín hiệu; không có tín hiệu thì `low`.
- `restore` hiện trả nguyên văn; chưa có vault hay hoàn nguyên PII.
- `redact_for_log` hiện chỉ trả `clean`, chưa che PII (`TODO(B5)`).
- Classifier, links và audit trong YAML mới được kiểm tra cấu hình, chưa chạy.
- Xem `docs/api.md` cho SDK và endpoint sidecar dự kiến.
