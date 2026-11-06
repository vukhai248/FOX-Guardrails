# Tiến độ: đóng Lớp 4 + Phần C1 (dừng ngày 07/11/2026)

> Đọc file này trước khi làm tiếp. Mỗi mục ghi: đã làm gì, đang ở đâu, còn lại gì, lệnh để chạy tiếp.

## 1. Đã xong

| Việc | Ở đâu | Ghi chú |
| --- | --- | --- |
| Merge Lớp 1–4 vào `main` | PR #2 → `a50fd0b` | CI xanh 3.11 + 3.13, 656 test |
| Đóng sổ Lớp 4 trong `docs/DU-AN.md` + tài liệu học `docs/hoc/lop-4-dau-ra-policy-audit.md` | `main` `aac24a7` | Tick B5.3–B6.6, FG-16..21; quyết định Q26–Q27; mục L4-FN/FP/L3 ở Phần 12 |
| Bỏ Codex; Claude tự review bằng `tests/systematic` | bộ nhớ + `DU-AN.md` + `docs/plans/prompts/codex-review.md` | Q26 |
| **Sửa PII mã hoá đi vào LLM/khách** (bộ kiểm S6) | **PR #4** (`fix/encoded-pii`, head `918d8a4`), **CHƯA MERGE** | Trước khi sửa: 169 ca hỏng. Sau khi sửa: S1–S6 = 0, 657 test, held-out không đổi. **Cần bạn quyết merge.** |

## 2. Phần C1: đang làm (nhánh `feat/c1-data`, worktree `D:/create/DATN/.worktrees/c1`)

| Hạng mục | Trạng thái | Chi tiết |
| --- | --- | --- |
| Hạ tầng chia/kiểm trùng | ✅ | `eval/datasets/common.py`: chia 30/70 theo `template_id` (salt cố định), trùng hẳn + gần trùng (Jaccard 5-gram ≥ 0,8) chuyển về dev |
| Biến thể T3 | ✅ | `eval/datasets/vi_cskh/transforms.py`: T3.1, 3.2, 3.4, 3.5, 3.8, 3.10, 3.11. Viết theo mô hình tấn công, không dựa vào code FOX |
| Bộ PII tổng hợp | ✅ build được | 130 mẫu (agent độc lập viết) → 291 ca (dev 88 / test 203), 14 loại thực thể, số giả đúng checksum. `eval/datasets/pii/` |
| Mẫu CSKH **hợp lệ** | ✅ | 200 mẫu (120 hard-benign + 80 clean, agent độc lập viết) → `eval/datasets/vi_cskh/cases.jsonl` |
| Mẫu CSKH **tấn công** | ⛔ **chờ bạn** | Agent viết 180 mẫu bị bộ lọc an toàn dừng, không tạo được mẫu nào. Claude **không** thử lách lại. Cần bạn chọn một trong 3 cách (mục 4) |
| Tải BIPIA | ✅ | `data/raw/bipia/` trong worktree c1 (Email + Table + 2 file tấn công, MIT). Chưa viết bộ chuyển sang `cases.jsonl` |
| Tải JailbreakBench | ✅ | `data/raw/jbb/` (2 CSV + 4 artifact PAIR/GCG, MIT). Chưa viết bộ chuyển |
| Tải openpii `vi` | ❌ lỗi tạm | API datasets-server của Hugging Face báo lỗi xác thực tạm thời. Chạy lại: `python -X utf8 -m eval.datasets.external.fetch openpii` |
| Duyệt mẫu gốc | ⏳ **bạn** | Đọc `eval/datasets/vi_cskh/templates/benign_templates.jsonl` và `eval/datasets/pii/templates/pii_templates.jsonl` (theo đặc tả, bạn duyệt toàn bộ mẫu gốc) |

`data/raw/` không được commit (nằm trong `.gitignore`). Nếu mất worktree c1, chạy lại `fetch.py` (bạn đã cho phép tải cả 3 bộ ngày 07/11).

## 3. Việc tiếp theo (thứ tự đề xuất)

1. **Bạn**: quyết merge PR #4.
2. **Bạn**: chọn cách làm mẫu tấn công (mục 4), rồi duyệt mẫu gốc.
3. Claude:
   - viết bộ chuyển BIPIA (`eval/datasets/external/bipia.py`: Email/Table × tấn công; dev = attack-train, test = attack-test; dương = có chèn, âm = sạch cùng task; lấy mẫu ~600 test / ~200 dev) và JBB (`jbb.py`: dương = prompt trong artifacts; âm = 100 behavior benign; báo riêng "goal trần");
   - chạy lại openpii;
   - viết `eval/datasets/SPLIT_REPORT.md` tổng hợp;
   - mở PR C1.
4. Sau C1 là C2 (`run_detectors.py`, `metrics.py`), rồi **Lớp 5**. Lớp 5 cần **bạn tự bấm Agree license** `meta-llama/Llama-Prompt-Guard-2-86M` trên Hugging Face.

## 4. Câu hỏi đang chờ bạn: mẫu tấn công tiếng Việt

- **(a)** Bạn tự viết, hoặc tự giao cho OpenCode, theo schema trong `docs/plans/C-du-lieu-va-thuc-nghiem.md` §2.3 (khoảng 180 mẫu: review 60, order_note 45, ticket_note 20, chat 55). Claude chỉ ghép, sinh biến thể, chia tập.
- **(b)** Tạm chỉ dùng BIPIA + JBB cho phần tấn công; bộ CSKH tiếng Việt chỉ đo chặn nhầm (hard-benign/clean) trước.
- **(c)** Tạm dùng các bộ held-out tiếng Việt đã có của Lớp 2–4 làm nguồn mẫu tấn công. Ghi rõ giới hạn: các bộ này đã dùng để đo, nên không còn độc lập hoàn toàn.

## 5. Lệnh hay dùng

```bash
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m eval.datasets.vi_cskh.build
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m eval.datasets.pii.build
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m eval.datasets.external.fetch openpii
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m tests.systematic.run_report out.md
```
