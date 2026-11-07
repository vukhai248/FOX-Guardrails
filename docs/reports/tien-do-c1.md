# Tiến độ: đóng Lớp 4 + Phần C1 (cập nhật 07/11/2026, lần 2)

> Đọc file này trước khi làm tiếp. Mỗi mục ghi: đã làm gì, đang ở đâu, còn lại gì, lệnh để chạy tiếp.

## 1. Đã xong

| Việc | Ở đâu | Ghi chú |
| --- | --- | --- |
| Merge Lớp 1–4 vào `main` | PR #2 → `a50fd0b` | CI xanh 3.11 + 3.13, 656 test |
| Đóng sổ Lớp 4 trong `docs/DU-AN.md` + tài liệu học `docs/hoc/lop-4-dau-ra-policy-audit.md` | `main` `aac24a7` | Tick B5.3–B6.6, FG-16..21; quyết định Q26–Q27; mục L4-FN/FP/L3 ở Phần 12 |
| Bỏ Codex; Claude tự review bằng `tests/systematic` | bộ nhớ + `DU-AN.md` + `docs/plans/prompts/codex-review.md` | Q26 |
| **Sửa PII mã hoá đi vào LLM/khách** (bộ kiểm S6) | **PR #4** (`fix/encoded-pii`, head `da7155e`), **CHƯA MERGE** | Review cuối tìm ra và sửa 2 hồi quy độ trễ bình phương (trên 10 phút → 0,44 s); thêm bộ S7. S1–S7 = 0, 658 test. **Cần bạn quyết merge.** |

## 2. Phần C1: đang làm (nhánh `feat/c1-data`, worktree `D:/create/DATN/.worktrees/c1`)

| Hạng mục | Trạng thái | Chi tiết |
| --- | --- | --- |
| Hạ tầng chia/kiểm trùng | ✅ | `eval/datasets/common.py`: chia 30/70 theo `template_id` (salt cố định), trùng hẳn + gần trùng (Jaccard 5-gram ≥ 0,8) chuyển về dev |
| Biến thể T3 | ✅ | `eval/datasets/vi_cskh/transforms.py`: T3.1, 3.2, 3.4, 3.5, 3.8, 3.10, 3.11. Viết theo mô hình tấn công, không dựa vào code FOX |
| Bộ PII tổng hợp | ✅ build được | 130 mẫu (agent độc lập viết) → 291 ca (dev 88 / test 203), 14 loại thực thể, số giả đúng checksum. `eval/datasets/pii/` |
| Mẫu CSKH **hợp lệ** | ✅ | 200 mẫu (120 hard-benign + 80 clean, agent độc lập viết) → `eval/datasets/vi_cskh/cases.jsonl` |
| Mẫu CSKH **tấn công** | ⏸ hoãn | Bạn chọn (07/11): **tạm dùng BIPIA + JBB** cho phần tấn công. Bộ CSKH tiếng Việt hiện chỉ đo chặn nhầm. Mẫu tấn công VI bổ sung sau |
| BIPIA | ✅ | Tải xong + `external/bipia.py`: dev 150/150, test 300 tấn công + 150 sạch, 3 vị trí chèn |
| JailbreakBench | ✅ | Tải xong + `external/jbb.py`: 286 tấn công (152 thành công), 100 lành tính, 100 goal độc hại trần (báo riêng) |
| openpii `vi` | ✅ | 1.000 câu + `external/openpii.py` (ánh xạ nhãn trong `eval/datasets/SPLIT_REPORT.md`) |
| Duyệt mẫu gốc | ⏳ **bạn** | Đọc `eval/datasets/vi_cskh/templates/benign_templates.jsonl` và `eval/datasets/pii/templates/pii_templates.jsonl` (theo đặc tả, bạn duyệt toàn bộ mẫu gốc) |

`data/raw/` không được commit (nằm trong `.gitignore`). Nếu mất worktree c1, chạy lại `fetch.py` (bạn đã cho phép tải cả 3 bộ ngày 07/11).

Báo cáo tổng: `eval/datasets/SPLIT_REPORT.md`. Test builder: `tests/test_datasets.py`.

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
