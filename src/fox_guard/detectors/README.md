# Detector đầu ra Lớp 4 — bot đòi PII và link nguy hiểm

`Guard._check` chỉ chạy các detector này ở trạm `output` (`guard.py:106-116`). Luật prompt injection
Lớp 2 có README riêng ở `rules/README.md`.

## 1. Bot đòi PII (`detectors/output.py:14-59`)

- `_SECRET_ITEMS` liệt kê thứ shop không bao giờ được hỏi: CCCD/CMND, ảnh giấy tờ, OTP, mật khẩu,
  PIN, số thẻ, CVV, ngày hết hạn, số tài khoản (`output.py:17-23`).
- `_ASK` là động từ yêu cầu: vui lòng, gửi, cung cấp, please, provide… (`output.py:24-28`).
- `_SOLICIT` ghép động từ + tối đa 50 ký tự + loại bí mật (`output.py:30`).
- Câu phủ định trong cùng mệnh đề không bị bắt, ví dụ "Shop không bao giờ yêu cầu OTP"
  (`output.py:29, 40-43`).
- Placeholder của guard (`<CCCD_1>`) được bỏ trước khi kiểm vì đó là tên thực thể, không phải yêu cầu
  (`output.py:37, 53-54`).
- Khớp → finding `solicitation`, `high`, kỹ thuật T2.4 (`output.py:57-58`).

## 2. Link guard (`detectors/output.py:62-198`)

- `guard_links(text, allowlist)` gỡ ảnh ngoài, thay link ngoài bằng `[liên kết ngoài đã bị gỡ]`, đánh
  dấu domain giả dạng và link chứa PII (`output.py:84, 144-198`).
- Nhận markdown inline, ảnh, reference `[x]: url`, URL trần, domain không scheme, domain viết tách
  `evil . example` (`output.py:72-83, 186-190`).
- Host được chuẩn hoá Punycode/IDNA (`output.py:96-105`).
- `link:external` medium; `link:lookalike` high khi skeleton host trùng allowlist
  (`output.py:112-118, 166-168`); `link:exfil` high khi path/query chứa PII hoặc placeholder
  (`output.py:121-134, 162-165`).
- Link thuộc allowlist và không chứa PII được giữ (`output.py:160-161`).

## Nối với policy

- `solicitation` → `block`; `link:exfil` → `block`; link ngoài bị gỡ → `mask`
  (`policy/engine.py:53-61`).
- Không có network: chỉ phân tích chuỗi, không tải link, không theo redirect (`output.py:144-198`).

## Giới hạn

- Solicitation dựa trên mẫu từ vựng; câu diễn đạt lạ có thể lọt. Phần phủ định đã **đóng băng** (không thêm danh sách từ); câu mới là việc của Lớp 5.
- Link guard là **lớp thứ hai**. Lớp chặn cuối là renderer của web (`checkUrlSafety` trong `chat-widget.tsx`). Bộ kiểm `tests/systematic/` (S1) so với chính renderer đó.
- Link guard không kiểm nội dung trang đích.
