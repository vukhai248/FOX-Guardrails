"""Generate synthetic Vietnamese PII fixtures (labelled values) + hard negatives. Seeded, reproducible.

All values are fake but format/checksum-valid (Luhn cards, CCCD province codes, MST check digit).
Run: python -X utf8 scripts/gen_pii_fixtures.py
"""

import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
RNG = random.Random(20261105)
PROVINCES = ["001", "079", "048", "031", "092", "036", "075", "026"]
WORDS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def digits(n):
    return "".join(RNG.choice("0123456789") for _ in range(n))


def phone():
    return RNG.choice(["091", "098", "090", "086", "070", "035", "083", "056"]) + digits(7)


def cccd():
    return RNG.choice(PROVINCES) + RNG.choice("0123") + digits(8)


def luhn_complete(prefix, length):
    body = prefix + digits(length - len(prefix) - 1)
    for check in "0123456789":
        candidate = body + check
        total = 0
        for i, ch in enumerate(reversed(candidate)):
            n = int(ch)
            if i % 2:
                n = n * 2 - 9 if n > 4 else n * 2
            total += n
        if total % 10 == 0:
            return candidate
    raise AssertionError


def card():
    return luhn_complete(RNG.choice(["4", "51", "9704", "3530"]), 16)


def mst():
    while True:
        base = "0" + digits(8)
        check = 10 - sum(int(d) * w for d, w in zip(base, (31, 29, 23, 19, 17, 13, 7, 5, 3), strict=True)) % 11
        if check < 10:
            return base + str(check)


def spaced(value):
    style = RNG.choice(["space4", "dot", "every"])
    if style == "space4":
        return " ".join(value[i:i + 4] for i in range(0, len(value), 4))
    if style == "dot":
        return ".".join(value[i:i + 3] for i in range(0, len(value), 3))
    return " ".join(value)


def spelled(value):
    return " ".join(WORDS[int(d)] for d in value)


NAMES = ["Nguyễn Văn An", "Trần Thị Bình", "Lê Minh Châu", "Phạm Quốc Dũng", "Hoàng Thu Hà", "Vũ Đức Long"]
STREETS = ["Lý Thường Kiệt", "Nguyễn Trãi", "Lê Lợi", "Trần Hưng Đạo", "Hai Bà Trưng"]
WARDS = ["phường Hàng Bài", "phường Bến Nghé", "xã Tân Phú", "phường 7", "phường Thạch Thang"]
CITIES = ["quận Hoàn Kiếm, Hà Nội", "quận 1, TP Hồ Chí Minh", "huyện Củ Chi, TP Hồ Chí Minh",
          "quận Hải Châu, Đà Nẵng", "TP Huế"]

POS = []  # (station, template with {v}, entity, value)


def add(n, entity, maker, templates, transform=None):
    for _ in range(n):
        value = maker()
        shown = transform(value) if transform else value
        POS.append({"entity": entity, "value": shown, "text": RNG.choice(templates).format(v=shown)})


add(14, "VN_PHONE", phone, ["SĐT mình {v} nhé", "gọi em số {v} trước khi giao", "liên hệ {v}",
                            "Zalo {v} ạ", "sdt nguoi nhan: {v}", "My phone is {v}"])
add(6, "VN_PHONE", phone, ["số em {v} nha", "sdt {v}"], spaced)
add(4, "VN_PHONE", phone, ["số của em là {v}"], spelled)
add(12, "VN_CCCD", cccd, ["CCCD của em là {v}", "căn cước {v}", "số định danh {v}", "cccd: {v}"])
add(4, "VN_CCCD", cccd, ["cccd {v}"], spaced)
add(10, "CREDIT_CARD", card, ["thẻ {v} hết hạn 12/30", "số thẻ visa {v}", "card {v}", "thanh toán bằng thẻ {v}"])
add(4, "CREDIT_CARD", card, ["the {v}"], lambda v: " ".join(v[i:i + 4] for i in range(0, 16, 4)))
add(8, "VN_BANK_ACCOUNT", lambda: digits(RNG.choice([10, 12, 13])),
    ["stk vietcombank {v}", "chuyển khoản vào số tài khoản {v}", "STK: {v} chủ tài khoản shop", "ck tới {v}"])
add(6, "VN_TAX_ID", mst, ["MST {v} xuất hoá đơn giúp em", "mã số thuế công ty: {v}"])
add(6, "VN_CMND", lambda: digits(9), ["CMND {v}", "số chứng minh {v}"])
add(5, "VN_PASSPORT", lambda: RNG.choice("BCN") + digits(7), ["hộ chiếu {v}", "passport {v}"])
add(5, "VN_LICENSE_PLATE", lambda: f"{RNG.randint(11, 99)}{RNG.choice(['A', 'F', 'K', 'LD'])}-{digits(3)}.{digits(2)}",
    ["biển số {v}", "xe biển {v}"])
add(5, "VN_HEALTH_INSURANCE", lambda: RNG.choice(["DN", "HS", "GD"]) + digits(13), ["thẻ BHYT {v}", "bhyt {v}"])
add(8, "OTP", lambda: digits(RNG.choice([4, 6, 8])), ["Mã OTP là {v}", "otp: {v}", "mã xác thực {v}", "ma otp {v}"])
add(6, "PASSWORD", lambda: RNG.choice(["Abc@", "Shop#", "xyz!"]) + digits(4), ["mật khẩu: {v}", "mk là {v}",
                                                                              "password: {v}"])
add(8, "EMAIL", lambda: f"synthetic.{digits(3)}@example.com", ["email {v}", "gửi về {v} giúp", "mail: {v}"])
add(6, "PERSON", lambda: RNG.choice(NAMES), ["Người nhận: {v}", "họ tên: {v}", "giao cho chị {v}", "anh {v} nhận"])
add(8, "VN_ADDRESS", lambda: f"{RNG.randint(1, 300)} {RNG.choice(STREETS)}, {RNG.choice(WARDS)}, {RNG.choice(CITIES)}",
    ["địa chỉ: {v}", "giao tới {v}", "nhà ở {v}"])

NEG = [
    "Giá 25.990.000đ, giảm còn 23.490.000đ", "Đơn 3f2a8c1e-9b7d-4e2a-a1b2-c3d4e5f60718 tới đâu rồi",
    "Mã giảm giá SALE2026 còn dùng được không", "Năm 2026 có mẫu mới không", "Giảm 15% cho đơn từ 500k",
    "Serial SN-77A1-B2, IMEI 35-209900", "Pin 5000mAh, sạc 67W, nặng 199g", "Mua 2 cái, mỗi cái 1.250.000đ",
    "Mã sản phẩm 100234567 còn hàng không", "Đặt 12 cái hôm 12/11/2026", "Màn hình 6,7 inch 120Hz",
    "RAM 16GB, ổ 512GB", "Tổng đơn 34.990.000 VNĐ", "Bảo hành 12 tháng, đổi trả 30 ngày",
    "sha 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", "Giờ mở cửa 8:00 - 21:00",
    "Hotline tổng đài 1900 1234", "Mã vận đơn GHN123456 đang giao", "Phòng 1205 tầng 12",
    "Model WH-1000XM5, giá 7.490.000đ", "Mua 3 tặng 1, tiết kiệm 2.000.000đ",
    "Shop không bao giờ hỏi mã OTP hay mật khẩu", "Mình quên mật khẩu, lấy lại thế nào",
    "CCCD có cần khi nhận hàng không?", "Có hỗ trợ trả góp thẻ tín dụng không", "Số lượng tồn 1325 sản phẩm",
    "Khuyến mãi 11.11 giảm tới 50%", "iPhone 15 Pro Max 256GB", "Tai nghe giá 990k", "Mã đơn #A7712 đã giao",
    "Lượt xem 123456789 trên video", "Tỉ số 2-1, mình rất vui", "Giao trong 2-3 ngày", "Version 2.4.6",
    "Điểm thưởng 4500 điểm", "Tháng 7/2025 có đợt sale lớn",
]


def write(name, rows, prefix):
    with (OUT / name).open("w", encoding="utf-8", newline="\n") as stream:
        for i, row in enumerate(rows, 1):
            stream.write(json.dumps({"id": f"{prefix}-{i:03d}", **row}, ensure_ascii=False) + "\n")


write("pii_positive.jsonl", POS, "pii")
write("pii_hard_negative.jsonl", [{"text": t} for t in NEG], "pneg")
print(f"positive={len(POS)} hard_negative={len(NEG)}")
