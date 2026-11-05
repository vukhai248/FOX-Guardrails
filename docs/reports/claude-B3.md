# Báo cáo B3 — Lớp 2 luật phát hiện prompt injection (Claude), 05/11/2026

Nhánh `feat/b-core` từ `main` @ `777fd0d` (đã merge Lớp 1). Theo yêu cầu của chủ đồ án, Claude làm và nghiệm thu đợt này. Subagent chỉ dùng để viết bộ câu kiểm độc lập.

## 1. Đã làm gì

| Việc | Commit |
| --- | --- |
| Engine luật: model `Rule` kiểm chặt (khoá lạ, regex sai, < 2 ví dụ đều bị từ chối); view `latin` (chỉ đổi chữ giống Latin, không `m`→`rn`); khớp trong chữ bị giấu thì nâng lên high; evidence che chữ số; span chỉ khi view thẳng hàng với `clean` | `1a4d46d` |
| 21 luật / 8 nhóm (`vi.yaml` 10, `en.yaml` 7, `structural.yaml` 4); luật đòi PII bỏ qua câu phủ định | `1a4d46d` |
| Guard chạy luật ở 3 trạm; trạm lấy theo hàm được gọi, không theo `ctx.station`; lý do tiếng Việt cho từng luật | `1a4d46d` |
| CLI `fox-guard rules list`, `fox-guard rules report CASES --out CSV` | `1a4d46d` |
| 64 câu hard-benign + 42 câu tấn công CSKH (sinh bằng `scripts/gen_rule_fixtures.py`) | `1a4d46d` |
| Mở rộng luật theo red-team dev (tác tử khác viết, chưa thấy luật) | `e68dc2a` |
| Quá thời gian regex → finding `rules:timeout`, không bỏ qua im lặng | `a10e4f1` |
| Đóng băng bộ held-out + test mức sàn; `scripts/eval_rules_redteam.py`, `scripts/demo_lop2.py` | `e090b2c` |
| Tài liệu học `docs/hoc/lop-2-luat.md`, README module, cập nhật `docs/api.md` | commit báo cáo |

## 2. Số đo (output thật)

| Bộ | Người viết | Recall | FPR |
| --- | --- | --- | --- |
| Ví dụ luật + fixture của Claude | Claude | 100% | 0% |
| Red-team dev (40 + 40) | Tác tử khác, trước khi sửa luật | 62,5% | 0% |
| **Red-team held-out (48 + 52)** | Tác tử khác, sau khi chốt luật; **không sửa luật theo bộ này** | **64,6%** | **0%** |

```text
pytest -q                → 411 passed, 2 xfailed
ruff check src tests scripts → All checks passed!
pytest -m slow           → B2 2KB p95 ≈ 5–6 ms ; B3 rules 2KB p95 ≈ 13 ms
eval held-out            → attacks=48 benign=52 recall=64.58% precision=100.00% FPR=0.00%
                            recall by group: {1: 5/6, 2: 3/6, 3: 4/6, 4: 3/6, 5: 3/6, 6: 4/6, 7: 6/6, 8: 3/6}
stress 20.000 ký tự adversarial → ≤ ~200 ms, không treo
```

## 3. Tự review: lỗi tìm thấy và đã sửa

1. Câu phủ định ("Shop **không bao giờ** yêu cầu khách gửi OTP") bị bắt nhầm. Đã thêm điều kiện bỏ qua câu phủ định ở luật đòi PII, và thêm ví dụ âm/dương.
2. Mở rộng luật "quên/xoá + hết + hướng dẫn" có rủi ro bắt nhầm câu tự kể ("Mình quên hết hướng dẫn rồi"). Đã chặn trường hợp có đại từ chủ ngữ đứng ngay trước động từ.
3. "Chế độ nhà phát triển" là câu hỏi kỹ thuật hợp lệ về điện thoại, nên đã bỏ `developer` khỏi luật đổi vai.
4. Luật dựa vào `ctx.station`: app ghi nhầm trạm là tắt được luật dữ liệu. Giờ trạm lấy theo hàm.
5. Regex quá thời gian bị bỏ qua im lặng, có thể bị lợi dụng để lách. Giờ phát finding `rules:timeout`.

## 4. Còn mở

- 17/48 câu held-out lọt: lệnh lịch sự chôn trong review dài, giả thẩm quyền kể chuyện, many-shot viết tắt. Để classifier ở Lớp 5 lo, không nới luật (sợ bắt nhầm).
- Mọi bộ đo do AI viết. Số chính thức sẽ đo trên bộ CSKH Phần C (chủ đồ án duyệt mẫu gốc), BIPIA và JailbreakBench.
- Lớp 2 vẫn **chưa chặn**: `action` luôn `allow` cho tới Lớp 4.
- Subagent Haiku/Sonnet không chạy được (lỗi định tuyến model trên tài khoản), nên phải dùng subagent cùng model.
