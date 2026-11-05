# Báo cáo Đợt 1b — Lớp 1 chuẩn hoá ký tự (Claude tự làm), 05/11/2026

Nhánh `feat/b-core`, worktree `D:/create/DATN/.worktrees/b-core`. Base `c2a0bfb` (Codex B1/B2). Đợt này chủ đồ án giao Claude làm thay Codex.

## 1. Đã làm gì

| Gói | Việc | Commit |
| --- | --- | --- |
| F1 | Leet không đổi giá/số lượng/UUID/hex/`%XX`; một finding `mixed_script` cho mỗi text | `7708ca3` |
| F2 | Bảng `teencode_vi.tsv` 205 dòng; loader: trùng khoá sau bỏ dấu thì cờ mơ hồ thắng | `2dee00c` |
| F3 | Script sinh fixture; 42 câu hợp lệ + 39 câu tấn công; `%20`/`&amp;` thành view, không báo | `fddc89c` |
| — | Bản đọc ROT13/`-plain` không chép cảnh báo lên root (hết trùng); demo `scripts/demo_lop1.py` | `c98579f` |
| F4 | Viết lại tài liệu học Lớp 1 cho người không đọc code (99 dòng) | `4c979be` |
| Tự review | 2 lỗi do chính đợt này gây ra (mục 4) | `1057be8` |

## 2. Lỗi tìm thấy và cách xử lý

| Ca | Loại | Xử lý |
| --- | --- | --- |
| `25.990.000đ` → `25.990.oood`, UUID bị leet | Lỗi B2 (Claude tìm khi nghiệm thu B1/B2) | Sửa F1 |
| 8 finding `mixed_script` giống nhau | Lỗi B2 | Sửa F1 |
| `đt` (rõ) và `dt` (mơ hồ) trùng khoá sau bỏ dấu, dòng rõ thắng | Lỗi loader, lộ ra khi có bảng thật | Mơ hồ thắng |
| URL `?q=tai%20nghe` bị báo "đã mã hoá" | **Báo nhầm** trên câu hợp lệ | `-plain` codec |
| Câu homoglyph báo 2 lần (bản ROT13 chép lại) | Trùng | Không chép từ view |
| `amazon.com` → skeleton `arnazon.corn` | **Kỳ vọng fixture sai** (UTS #39 cố ý đổi `m`→`rn`) | Sửa kỳ vọng, ghi chú trong script và README |
| `ig` + U+0301 + `nore` | Bỏ sót đã biết | `xfail(strict=True)` + README; `vi_nodiac` vẫn đọc ra |
| Hex 64 ký tự | Bỏ sót đã biết (trùng độ dài sha256) | `xfail(strict=True)` + README |
| `quote()` chỉ mã hoá dấu cách | Fixture sai (không giấu gì) | Mã hoá toàn bộ byte |

## 3. Lệnh kiểm và output thật

```text
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m pytest -q
191 passed, 2 xfailed in 0.98s

C:/Users/Admin/anaconda3/envs/DL/python.exe -m ruff check src tests scripts
All checks passed!

pytest -q -s -m slow
B2 2KB p95=6.356 ms; samples=40

python -X utf8 scripts/gen_normalize_fixtures.py   (sinh lại)
benign=42 attacks=39 ; git status sạch → fixture tái lập được
```

Test lỗi mục 4 được kiểm cả hai chiều: chạy trên code cũ thì **hỏng**, trên code mới thì **qua**.

## 4. Tự review (subagent Sonnet không chạy được: lỗi quyền model)

Claude tự dò bằng ca cụ thể và tìm ra 2 lỗi do chính đợt này gây ra:

1. **Mất mức độ cảnh báo** (bảo mật). Khi gộp cảnh báo trùng giữa bản gốc và bản giải mã, nếu bản gốc có `invisible` mức low thì `invisible` mức medium giấu trong base64 bị bỏ. Sửa: chỉ bỏ khi bản gốc đã có cùng loại ở mức **bằng hoặc cao hơn**.
2. **Né leet**: quy tắc "token dưới 50% là chữ thì không đổi số" làm `b00` không được đọc thành `boo`. Quy tắc này thừa, vì giá và UUID đã có regex riêng. Đã bỏ.

Đã thử thêm, không có lỗi:
- 6 câu tiếng Việt bình thường không bị teencode đổi sai;
- `%XX` một phần (`bo%20qua%20moi`) không báo, vì chữ vẫn hiện rõ;
- `ign%6fre` vẫn báo `encoded`.

## 5. Còn mở

- Chưa chạy CI thật trên GitHub (chưa push). Python 3.11 chưa thử trên máy, chỉ chạy 3.13.
- Không dùng CUA: Lớp 1 là thư viện, không có giao diện.
- Fixture do cùng người viết code soạn (Claude). Ca kiểm độc lập vẫn nên có từ Phần C (tập dev/test của C).
- Lớp 1 vẫn **chưa chặn**: SDK luôn `allow`. `redact_for_log` chưa che PII (Lớp 3).
- `feat/b-core` chưa merge vào `main`. Chờ chủ đồ án đồng ý.
