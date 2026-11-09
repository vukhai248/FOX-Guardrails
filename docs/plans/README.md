# docs/plans — đọc theo thứ tự

> **Kế hoạch chính và bảng tick tiến độ:** [`../DU-AN.md`](../DU-AN.md). Các file dưới đây là đặc tả gốc cho agent đọc khi code.

1. [`00-tong-quan.md`](00-tong-quan.md): phạm vi, kiến trúc, sổ quyết định, chia việc, lịch 4 tuần. **Đọc trước.**
2. [`01-tan-cong-va-phong-thu.md`](01-tan-cong-va-phong-thu.md): các vụ tấn công 2022–2026, mã kỹ thuật T*, mục tiêu O*, PII P*, bản đồ phòng thủ.
3. [`A-hoan-thien-web.md`](A-hoan-thien-web.md): Phần A, hoàn thiện web e-commerce (agent A).
4. [`B-guardrails.md`](B-guardrails.md): Phần B, FOX-Guard (agent B).
5. [`C-du-lieu-va-thuc-nghiem.md`](C-du-lieu-va-thuc-nghiem.md): dữ liệu, arm, chỉ số, quy trình chạy (agent C).
6. [`D-hoc-va-van-dap.md`](D-hoc-va-van-dap.md): lộ trình hiểu, câu hỏi hội đồng, kịch bản demo (chủ đồ án).
7. [`G-finetune.md`](G-finetune.md): fine-tune model (M1 injection VI–EN, M2 kiểm đầu ra), dữ liệu có sẵn + bộ FOX-VI tự dựng, chỉ số (đề xuất 09/11).

Plan v1 (18/10/2026) đã được thay thế, lưu ở `../archive/plan-v1-2026-10-18.md` để tra cứu.

**Giao việc cho agent:** đưa agent file `00-tong-quan.md` + file phần của nó + `01-tan-cong-va-phong-thu.md`. Yêu cầu agent báo lại theo từng gói (đã làm gì, chạy thử thế nào, còn gì).

**Phân công agent (giai đoạn 1 — web):** [`E-phan-cong-agent.md`](E-phan-cong-agent.md); prompt dán sẵn ở [`prompts/`](prompts/).

**Phân công agent (giai đoạn 2 — FOX-Guard):** [`F-phan-cong-phan-B.md`](F-phan-cong-phan-B.md); prompt `prompts/codex-phanB.md`, `prompts/antigravity-phanB.md`. Tài liệu học từng lớp: [`../hoc/`](../hoc/README.md).
