# Tiến độ Lớp 5 (classifier), cập nhật 07/11/2026

> Đọc file này trước khi làm tiếp Lớp 5.

## Đã xong (nhánh `feat/lop-5-classifier`)

| Việc | File | Kết quả |
| --- | --- | --- |
| Tải deberta (Apache-2.0, 715 MB, chỉ `safetensors` + tokenizer, không pickle) | `models/protectai-deberta-v3-base-prompt-injection-v2/` (gitignore) | ✅ |
| Bộ bọc classifier: chỉ dùng trọng số cục bộ, cửa sổ 512/64 token, lấy max, cache sha256 | `src/fox_guard/detectors/classifier.py` | ✅ |
| Gắn vào guard: chấm trên clean + Tags ẩn + bản giải mã; thiếu trọng số hoặc chưa có ngưỡng thì giảm cấp, không chặn | `src/fox_guard/guard.py` (`_classify`) | ✅ |
| Gộp rủi ro B6.1: luật medium + classifier ≥ θ_low thì high; classifier một mình tối đa medium | `src/fox_guard/policy/engine.py` (`merge_risk`) | ✅ |
| Cấu hình: `classifier.enabled/use/model_dir/device/window/overlap/stations`; `rules.enabled` (cho arm M) | `src/fox_guard/config.py`, `fox-guard.yaml` (để **tắt**) | ✅ |
| Chốt ngưỡng trên dev | `eval/calibrate.py` → `eval/reports/thresholds_deberta.json` | θ_low 0,999324 · θ_high 0,999991 |
| Đo C2 arm M-deberta, H-deberta (dev rồi test một lần) | `eval/run_detectors.py`, `eval/reports/lop5-deberta_2026-11-07.md` | BIPIA bắt 5,7% (chặn nhầm 3,3%) · JBB bắt 12,9% (0%) · CSKH chặn nhầm 2,4% |
| Test không cần model | `tests/test_classifier.py` | 7 test + 1 test `@model` |
| Thử tăng tốc CPU | `eval/reports/lop5-deberta_2026-11-07.md` | int8 động của PyTorch bị **loại** (sai điểm). ONNX không đủ đạt 300 ms ở 512 token. Hướng còn lại: GPU hoặc PG2 |
| **B6.3 khoanh vùng** | `src/fox_guard/policy/localize.py`, `guard._localize_and_mark` | CONTEXT high chỉ cắt câu bị chèn (`mask` + cờ `localized`). Ẩn cả đoạn khi: không câu nào tự giải thích được cảnh báo (ví dụ Tags ẩn), cắt hơn 60% số câu, hoặc phần giữ lại vẫn còn cảnh báo |
| **B6.4 datamarking** | như trên; `policy.datamarking` (mặc định **tắt**, bật theo arm) | Thẻ bọc có mã ngẫu nhiên mỗi request; escape `« »`; chuỗi giả thẻ ghi finding `datamark:delimiter` (T2.5) |
| Test khoanh vùng | `tests/test_localize.py` | 7 test |

## Còn lại

1. **Bạn:** chấp nhận license `meta-llama/Llama-Prompt-Guard-2-86M` trên Hugging Face, tạo token read, rồi chạy `hf auth login`. Sau đó Claude tải PG2 vào `models/`, chạy `python -X utf8 -m eval.calibrate --use primary`, rồi đo arm M-pg2 và H-pg2 (thêm vào `ARMS` trong `run_detectors.py`).
2. **Tăng tốc:** đo lại với PG2. Nếu vẫn chậm thì chạy classifier trên GPU, hoặc chỉ chấm ở trạm CONTEXT.
3. ~~B6.3–6.4~~ **xong.** Còn lại: đo khoanh vùng giữ được bao nhiêu utility khi có ca tấn công tiếng Việt (C1-OPEN), hoặc qua end-to-end C3.
4. **B4.2 / B4.3 (✂️, có thể cắt):** điểm theo phiên, LLM judge. Judge có thể là cách duy nhất bắt injection kiểu "giao việc" của BIPIA.
5. Cập nhật `docs/DU-AN.md` (mục 4.5, Phần 10, Phần 12) và tài liệu học `docs/hoc/lop-5-classifier-khoanh-vung.md` khi Lớp 5 xong.

## Lệnh

```bash
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m eval.calibrate --device cuda
C:/Users/Admin/anaconda3/envs/DL/python.exe -X utf8 -m eval.run_detectors --split dev --arm H-deberta --device cuda --tag _H-deberta
```
