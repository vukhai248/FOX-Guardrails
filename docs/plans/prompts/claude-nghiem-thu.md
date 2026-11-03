# Prompt nghiệm thu — Claude Code

Khi một agent báo xong gói, gửi cho Claude:

> Nghiệm thu gói `<A1 | A2 | …>` của `<codex | anti>`. Báo cáo ở `docs/reports/<file>.md`, nhánh `<feat/a-backend | feat/a-frontend>`.

Claude sẽ: đọc báo cáo → xem diff của gói → chạy lại test → đối chiếu "Xong khi" (`A-hoan-thien-web.md`) và tiêu chí §6 (`E-phan-cong-agent.md`) → ghi kết quả vào `docs/reports/nghiem-thu-A.md` (Đạt / Đạt có điều kiện / Trả lại + lý do cụ thể + việc cần sửa) để bạn chuyển lại cho agent.
