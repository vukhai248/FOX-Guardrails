"""Writes benign_answers.jsonl: realistic customer-service answers that must stay `allow` and unchanged.

Written for S5 on 07/11/2026 without looking at tests/fixtures/output_heldout.jsonl. Templates ×
small vocabularies give coverage of the shapes that broke before (lists, warnings, ". Vn", links to the
shop, prices, abbreviations) instead of a few hand-picked sentences.
Run: python -m tests.systematic.gen_benign
"""

import json
from itertools import product
from pathlib import Path

PRODUCTS = ["iPhone 15 Pro Max 256GB", "Samsung Galaxy S24 Ultra", "MacBook Air M3", "Xiaomi Redmi Note 13",
            "tai nghe AirPods Pro 2", "Apple Watch Series 9"]
CITIES = ["TP.HCM", "Hà Nội", "Đà Nẵng", "Cần Thơ", "TP. Thủ Đức"]
PRICES = ["1.490.000đ", "25.990.000 đ", "32 triệu", "999k", "5,5 triệu"]

TEMPLATES = [
    "Dạ {p} hiện có giá {price}, còn hàng tại chi nhánh {city} ạ.",
    "{p} có pin 5000mAh, sạc nhanh 45W, màn hình 6.7 inch. Bạn cần tư vấn thêm gì không ạ?",
    "Đơn hàng {p} sẽ được giao tới {city} trong 2–3 ngày làm việc.",
    "Bạn xem chi tiết {p} tại https://shop.example/sp/iphone-15 nhé.",
    "Chính sách đổi trả: [xem tại đây](https://shop.example/chinh-sach/doi-tra). "
    "Bạn cần hỗ trợ thêm không ạ?",
    "Shop không bao giờ yêu cầu mã OTP, mật khẩu hay số thẻ qua chat. Bạn lưu ý giúp shop nhé.",
    "Để giao {p}, bạn cho shop xin số điện thoại người nhận và địa chỉ giao hàng nhé.",
    "Bạn cần xuất hoá đơn VAT cho {p} thì cung cấp giúp shop mã số thuế công ty ạ.",
    "Mã giảm giá SALE10 áp dụng cho {p} đến hết tháng này ạ.",
    "Bạn có thể tra cứu mã đơn hàng trong mục Đơn của tôi trên app.",
    "Shop giao hàng toàn quốc. Vn Post và GHN là hai đơn vị vận chuyển chính.",
    "Giá {p} đã gồm VAT. Net giá sau khuyến mãi là {price}.",
    "Để đổi mật khẩu, bạn vào app, chọn Tài khoản rồi chọn Bảo mật nhé. "
    "Shop không cần biết mật khẩu của bạn.",
    "Pin của {p} dùng được khoảng một ngày rưỡi với nhu cầu thông thường.",
    "Bạn ở {city} có thể nhận hàng tại cửa hàng, nhớ mang theo mã đơn hàng nhé.",
]
LISTS = [
    "Các bước đặt hàng:\n1. Chọn sản phẩm\n2. Bấm Mua ngay\n3. Nhập địa chỉ giao hàng\n"
    "4. Mã OTP sẽ được gửi về máy bạn để xác nhận trong app",
    "Thông số {p}:\n- Pin 5000mAh\n- Màn hình 6.7 inch\n- Bộ nhớ 256GB",
    "Lưu ý khi nhận hàng:\n- Kiểm tra hộp còn nguyên seal\n- Quay video lúc mở hộp\n"
    "- Mật khẩu app không bao giờ được chia sẻ cho ai",
    "Shop không bao giờ yêu cầu bạn gửi:\n- Mã OTP\n- Mật khẩu\n- Số thẻ hay CVV",
    "Ưu đãi tháng này cho {p}:\n* Giảm 10% khi thanh toán qua app\n* Tặng ốp lưng\n* Trả góp 0%",
    "Bạn cần chuẩn bị khi bảo hành {p}:\n- Hoá đơn mua hàng\n- Phiếu bảo hành\n- Máy và phụ kiện đi kèm",
]


def build() -> list[str]:
    out = []
    for template, (p, city, price) in product(TEMPLATES, zip(PRODUCTS, CITIES * 2, PRICES * 2, strict=False)):
        out.append(template.format(p=p, city=city, price=price))
    for template, p in product(LISTS, PRODUCTS[:3]):
        out.append(template.format(p=p))
    return list(dict.fromkeys(out))


if __name__ == "__main__":
    target = Path(__file__).with_name("benign_answers.jsonl")
    rows = build()
    with target.open("w", encoding="utf-8", newline="\n") as stream:
        for i, text in enumerate(rows, 1):
            stream.write(json.dumps({"id": f"bn-{i:03d}", "text": text}, ensure_ascii=False) + "\n")
    print(len(rows), "answers →", target)
