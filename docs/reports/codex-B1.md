# Phần B Đợt1 — B1/B2, 03/11/2026

## 1. Đã làm gì

- Đọc giao việc mới và kiểm tra xung đột trước khi thực thi. Claude yêu cầu K5 trước B: K5 đã hoàn thành tại fix/a-k5, commit58e190c, 82Node/93Python/34PostgreSQL local checks; chưa áp dụng migration thật. Sau đó mới viết B1/B2.
- B làm tại D:/create/DATN/.worktrees/b-core, feat/b-core từ bc03e73. Anti làm QA2 trên web repo qa/a-wave3; không sửa checkout/file/env/server của Anti. Merge-tree K5 với QA branch mới nhất5ecee8c trả0, chưa merge thật. Phụ thuộc chức năng: test review409 của Anti chờ Claude tích hợp và duyệt/áp dụng K5.
- B1: models GuardContext/Finding/Decision, evidence<=120, span không âm/đảo, list factory; YAML có extra=forbid ở từng tầng. Guard.from_config +3trạm +restore +redact_for_log; UUID và latency thật, risk lớn nhất, reasons tiếng Việt. Đợt1 luôn allow, chưa policy hay che PII.
- B2:8bước chuẩn hoá, giữ raw/hash, ngoại lệ emojiZWJ/cờTags/keycap/NFD; UTS39 skeleton, VI/teencode/leet, numeric view có map về clean;6decoder +ROT13 view, độ sâu2/tổng ngân sách8x, loại UUID/JWT/hash, cap20k. Finding evidence chỉ là tóm tắt kỹ thuật; decoded finding đưa lên root có spanNone khi không map được.
- Dữ liệu confusables chính thức Unicode16.0.0 được ghim SHA/license trong data/README.md. Bảng nạp cache một lần. Không tải model và không cài thư viện mới.
- Có tài liệu API và tài liệu học <=150dòng với output thật3ca. README từng thư mục module<=40dòng.

## 2. File đổi / phân quyền

- src/fox_guard/types.py, config.py, guard.py, __init__.py, README.md.
- src/fox_guard/normalize/**, data/confusables.txt, data/LICENSE-UNICODE.txt, data/README.md.
- tests/test_contract_*.py, tests/test_normalize.py, tests/fixtures/evidence_unicode.json.
- pyproject.toml chỉ thêm pytest pythonpath=['src'] để kiểm đúng worktree, không vô tình import package editable của checkout khác.
- .gitattributes giữ nguyên bytes của confusables/license khi checkout Windows; xác minh SHA upstream=worktree=Git blob và text attribute unset cho hai file.
- docs/api.md, docs/hoc/lop-1-chuan-hoa.md, báo cáo và execution ledger.
- tests/fixtures/evidence_unicode.json là ngoại lệ được prompt giao đích danh Codex, dù toàn bộ fixture còn lại thuộc Anti. Không viết teencode_vi.tsv hoặc normalize_benign/attacks của Anti. Không sửa docs/plans hoặc tracker Claude.

## 3. Lệnh kiểm + output thật

Môi trường: DL Python3.13; tất cả dependency đã có. Để giữ editable binding của Anti nguyên vẹn, cài package vào venv riêng có dùng thư viện hệ thống:

```powershell
C:/Users/Admin/anaconda3/envs/DL/python.exe -m venv --system-site-packages --without-pip .venv
./.venv/Scripts/python.exe -m pip install --no-deps --no-build-isolation -e '.[core,dev]'
```

Output: Successfully installed fox-guard-0.1.0. Pip xác nhận fox-guard trong DL nằm ngoài venv nên không gỡ/chỉnh nó. .venv gitignored; không nâng dependency. Baseline trước code:2passed, Ruff0.

RED đã quan sát: module types/config chưa có; Guard exports chưa có; normalizer entrypoint chưa có. B2 thêm3regression chuỗi invisible/Mn liên tiếp từng fail rồi sửa. Kết quả cuối của lượt kiểm root:

```powershell
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m pytest -q
```

```text
95 passed, 2 skipped in 0.65s
```

Hai skip chỉ do chưa có normalize_benign.jsonl và normalize_attacks.jsonl của Anti. Chưa tính là integration đạt. Test hiện đã sẵn sàng chạy từng file khi chúng được merge; nếu kỳ vọng sai thì ghi requests.md, không sửa fixture Anti.

```powershell
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m pytest -q -s -m slow
```

```text
B2 2KB p95=4.825 ms; samples=40
1 passed, 96 deselected in 0.29s
```

Đây là benchmark warm sau lazy load,40samples; không phải cold-start SLA. Ví dụ thật trong API docs có cold SDK latency74.6662ms; không che giấu khác biệt này.

```powershell
C:/Users/Admin/anaconda3/envs/DL/python.exe -m ruff check src tests
```

```text
All checks passed!
```

Review độc lập B1 contracts:24tests passed. Review toàn nhánh chốt không còn finding sau hai sửa B2: lookup TSV có số phải trước leet (token toàn số vẫn giữ nguyên), và segmentation trên NFKC phải map lại clean cả ký tự compatibility/ligature/punctuation. Các regression đều RED trước GREEN; reviewer kiểm lại15focused tests passed, không dựa vào decoded ROT13 để che lỗi root.

Root chạy nguyên đoạn demo từ tài liệu học và so output khớp chính xác. Learning doc<=150dòng và mọi README module<=40dòng. `git diff --check` qua. Bản confusables bytes khớp SHA đã ghi.

## 4. Còn mở / bàn giao

- Dừng ở B1/B2, không làm B3 trước Claude nghiệm thu và chủ đồ án đọc tài liệu học.
- Anti L1–L3 chưa có trong worktree: default teencode mapping rỗng có chủ đích; leet vẫn hoạt động. Tích hợp dataset và bảng Anti cần nghiệm thu sau merge. Không tự lấy dữ liệu uncommitted từ checkout của Anti.
- normalize có tín hiệu nhưng SDK vẫn allow. restore pass-through; redact_for_log chỉ clean với TODO(B5), không tuyên bố riêng tư PII đã hoạt động. Chưa có sidecar endpoint thật; docs ghi rõ dự kiến B7.
- Script detection chỉ Latin/Greek/Cyrillic. Chuẩn hoá có false-negative theo các giới hạn nêu README; decoding chất lượng/budget không bảo đảm bắt mọi encoding. Hash raw vẫn O(n) theo toàn văn.
- Không thay đổi Supabase, Stripe, model hoặc web trong đợt B. Không push, không merge.
- Commit B:5788f78(types/config), bc66f50(SDK/docs), f662f60(normalize),42b79de/768ba3d/ed8ef9f(review regressions); commit bàn giao chứa báo cáo/learning doc và cấu hình đường dẫn kiểm thử. Claude có thể nghiệm thu từ feat/b-core.
