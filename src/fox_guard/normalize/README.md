# Chuẩn hoá B2

`normalize(text, *, max_chars=20000, decode_max_depth=2, teencode_path=None)`
trả `NormalizedText`, giữ nguyên `raw` và SHA-256 của toàn văn.

1. NFC → `base`.
2. Giải mã tags → `hidden_tags`; giữ black-flag + 1–6 tag a–z/0–9 + cancel.
3. Bỏ ký tự vô hình → `clean`; giữ emoji ZWJ, VS16 sau emoji/keycap hợp lệ.
4. NFKC → `nfkc`.
5. Skeleton UTS #39 và finding trộn Latin/Greek/Cyrillic trong một từ.
6. View bỏ dấu, ghép mảnh, teencode/leet và chuỗi số.
7. View giải mã UTF-8 in được, ≥8 ký tự, ≥80% chữ/số/khoảng trắng.
8. Cắt phần kiểm ở ≤20.000 ký tự trước bước 1; signal `oversize` khi cắt.

`decoded` là danh sách phẳng BFS sâu ≤2; từng node chạy lại bước 1–6,
`decoded` của node con rỗng. Tổng độ dài output giải mã ≤8× input đã cắt.
UUID/JWT/hash hex 32/40/64 được loại trước scan base64/hex.
ROT13 và `%20`/`&amp;` chỉ giải ra dấu cách/dấu câu là view, không sinh finding. Child findings đưa lên root
có `span=None`; span nội bộ từng node tính trên `clean` của node đó.

`digits_map[i]` là vị trí bắt đầu trên `clean`. `span_in_clean(a,b)`
trả khoảng nguồn đầy đủ, gồm cả từ cuối khi đổi số viết bằng chữ.
Chỉ chuỗi ≥6 từ số mới được đổi. Không sửa `clean` bằng các view đọc.
Bảng `data/teencode_vi.tsv` (205 dòng); `ambiguous=1` không thay, trùng khoá sau bỏ dấu thì mơ hồ thắng.
Leet bỏ qua giá/số lượng (`25.990.000đ`, `990k`, `2tr5`), UUID, hex ≥16 và `%XX`.
Bảng được cache theo path; dùng đường dẫn mới hoặc khởi động lại khi cập nhật.

Giới hạn: không giải mã nén/mã tự chế; skeleton có thể đổi `m` thành `rn`,
nên view Việt lấy từ NFKC. Script detection chỉ xét Latin/Greek/Cyrillic;
NFC/category dùng Python UCD, thuộc tính emoji dùng phiên bản `regex` đã cài.
Raw/hash vẫn cần O(n) theo toàn input; giới hạn 50ms được đo với text 2KB.

Bỏ sót đã biết (test `xfail(strict=True)` trong `tests/test_normalize.py`):

| Ca | Vì sao | Lớp nào bù |
| --- | --- | --- |
| `atk-016` `iǵnore` | NFC gộp thành `ǵ` có sẵn, không còn dấu rời để báo | `vi_nodiac` vẫn ra `ignore` → luật Lớp 2 |
| `atk-021` hex 64 ký tự | Trùng độ dài sha256 nên bị loại trừ có chủ đích | Classifier Lớp 5; hex độ dài khác vẫn giải |
