"""Build the synthetic Vietnamese PII bench (Phần C §2.4) from slot templates.

Templates (eval/datasets/pii/templates/pii_templates.jsonl) contain tokens such as {PHONE}; this
script fills them with FAKE values that are format/checksum valid, records gold spans, and adds
T3.12 obfuscated variants. No real personal data is used.

python -X utf8 -m eval.datasets.pii.build
"""

import random
import re
import uuid
from collections import Counter
from pathlib import Path

from ..common import read_jsonl, resolve_leaks, split_of, within_split_duplicates, write_jsonl

HERE = Path(__file__).resolve().parent
SEED = 20261107
FILLS_PER_TEMPLATE = 2  # two different fillings per template
OBFUSCATE_SHARE = 0.30  # share of PII cases that get a T3.12 obfuscated copy
TOKEN = re.compile(r"\{([A-Z_]+)\}")

# Mobile prefixes (Viettel, Vinaphone, Mobifone, Vietnamobile, Gmobile) after the 2018 renumbering.
PHONE_PREFIX = [
    "032",
    "033",
    "034",
    "035",
    "036",
    "037",
    "038",
    "039",
    "086",
    "096",
    "097",
    "098",
    "081",
    "082",
    "083",
    "084",
    "085",
    "088",
    "091",
    "094",
    "070",
    "076",
    "077",
    "078",
    "079",
    "089",
    "090",
    "093",
    "052",
    "056",
    "058",
    "092",
    "059",
    "099",
]
PROVINCE = ["001", "079", "048", "031", "092", "037", "038", "040", "045", "046", "056", "074", "075", "089"]
SURNAME = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
MIDDLE = ["Văn", "Thị", "Minh", "Ngọc", "Hữu", "Thanh", "Quốc", "Gia", "Thu", "Đức"]
GIVEN = ["An", "Bình", "Châu", "Dũng", "Hà", "Hùng", "Lan", "Linh", "Nam", "Phương", "Quân", "Trang", "Tuấn"]
STREET = ["Hoa Sữa", "Cây Gạo", "Bằng Lăng", "Phượng Vĩ", "Hoa Lan", "Sao Mai", "Bình Minh"]
WARD = ["Phường Tân Lập", "Phường An Hoà", "Xã Đông Sơn", "Phường Thạnh Lộc", "Phường Yên Hoà"]
CITY = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "Bình Dương"]
BHYT_PREFIX = ["DN", "HC", "GD", "HS", "SV", "TE", "CN", "HT"]
DIGIT_WORDS = "không một hai ba bốn năm sáu bảy tám chín".split()


def luhn_complete(prefix: str, length: int, rng: random.Random) -> str:
    body = prefix + "".join(rng.choice("0123456789") for _ in range(length - len(prefix) - 1))
    total = 0
    for i, ch in enumerate(reversed(body)):
        d = int(ch)
        if i % 2 == 0:
            d = d * 2 - 9 if d * 2 > 9 else d * 2
        total += d
    return body + str((10 - total % 10) % 10)


def tax_id(rng: random.Random) -> str:
    weights = [31, 29, 23, 19, 17, 13, 7, 5, 3]
    while True:
        body = [rng.randint(0, 9) for _ in range(9)]
        check = 10 - sum(d * w for d, w in zip(body, weights, strict=True)) % 11
        if check < 10:
            return "".join(map(str, body)) + str(check)


def fake(token: str, rng: random.Random) -> str:
    digits = lambda n: "".join(rng.choice("0123456789") for _ in range(n))  # noqa: E731
    match token:
        case "PHONE":
            return rng.choice(PHONE_PREFIX) + digits(7)
        case "EMAIL":
            return f"{rng.choice(GIVEN).lower()}.{digits(3)}@mail.example"
        case "CCCD":
            return (
                rng.choice(PROVINCE)
                + str(rng.choice([0, 1, 2, 3]))
                + f"{rng.randint(60, 99):02d}"
                + digits(6)
            )
        case "CMND":
            return rng.choice(["0", "1", "2", "3"]) + digits(8)
        case "CARD":
            return luhn_complete(rng.choice(["4", "9704", "51", "52"]), 16, rng)
        case "BANK_ACCOUNT":
            return digits(rng.choice([10, 12, 13, 14]))
        case "TAX_ID":
            return tax_id(rng)
        case "PASSPORT":
            return rng.choice("BCN") + digits(7)
        case "PLATE":
            return f"{rng.randint(11, 99)}{rng.choice('ABCDEFGHKL')}-{digits(3)}.{digits(2)}"
        case "BHYT":
            return rng.choice(BHYT_PREFIX) + digits(13)
        case "OTP":
            return digits(6)
        case "PASSWORD":
            return rng.choice(["Shop", "Matkhau", "Abc", "Linh"]) + rng.choice("@#!$") + digits(4)
        case "PERSON":
            return f"{rng.choice(SURNAME)} {rng.choice(MIDDLE)} {rng.choice(GIVEN)}"
        case "ADDRESS":
            return (
                f"số {rng.randint(1, 199)} đường {rng.choice(STREET)}, {rng.choice(WARD)}, {rng.choice(CITY)}"
            )
        # hard negatives
        case "PRICE":
            return rng.choice(
                ["1.490.000đ", "25.990.000 đ", "999k", "32 triệu", "5,5 triệu", "12.500.000 VNĐ"]
            )
        case "ORDER_ID":
            return f"DH{rng.randint(20260101, 20261231)}-{digits(4)}"
        case "SKU":
            return rng.choice(["SP-IP15-256", "SS-S24U-512", "MBA-M3-13", "AP2-USBC", "XM-RN13-8"])
        case "COUPON":
            return rng.choice(["SALE10", "FREESHIP50", "TET2026", "BLACKFRIDAY", "NEWUSER"])
        case "SERIAL":
            return luhn_complete("35", 15, rng)  # IMEI shape: a Luhn number that is not PII
        case "UUID":
            return str(uuid.UUID(int=rng.getrandbits(128)))
        case "DATE":
            return f"{rng.randint(1, 28):02d}/{rng.randint(1, 12):02d}/2026"
        case "QTY":
            return str(rng.randint(1, 20))
        case "HOTLINE":
            return rng.choice(["1900 6789", "1800 1234", "1900 2097"])
        case "TRACKING":
            return f"GHN{digits(9)}VN"
    raise ValueError(f"unknown token {token}")


def obfuscate(value: str, rng: random.Random) -> tuple[str, str]:
    """T3.12: spaced digits, dotted groups, fullwidth or spelled-out digits."""
    if not re.fullmatch(r"\d{6,}", value):
        return value, ""
    kind = rng.choice(["spaced", "dotted", "fullwidth", "words"])
    if kind == "spaced":
        return " ".join(value), kind
    if kind == "dotted":
        return ".".join(value[i : i + 3] for i in range(0, len(value), 3)), kind
    if kind == "fullwidth":
        return "".join(chr(ord(c) + 0xFEE0) for c in value), kind
    return " ".join(DIGIT_WORDS[int(c)] for c in value), kind


def fill(template: dict, rng: random.Random, obf: bool) -> dict:
    text, spans, pos, kinds = "", [], 0, []
    for m in TOKEN.finditer(template["text"]):
        text += template["text"][pos : m.start()]
        value = fake(m.group(1), rng)
        if obf and template["label"] == "pii":
            value, kind = obfuscate(value, rng)
            kinds.append(kind)
        if template["label"] == "pii":
            spans.append(
                {"entity": m.group(1), "start": len(text), "end": len(text) + len(value), "value": value}
            )
        text += value
        pos = m.end()
    text += template["text"][pos:]
    return {"text": text, "spans": spans, "obfuscation": [k for k in kinds if k]}


def main() -> None:
    path = HERE / "templates" / "pii_templates.jsonl"
    templates = read_jsonl(path)
    rng = random.Random(SEED)
    cases = []
    for t in templates:
        split = split_of(t["template_id"])
        for i in range(FILLS_PER_TEMPLATE):
            base = fill(t, rng, obf=False)
            cases.append(
                {
                    "case_id": f"{t['template_id']}-{i}",
                    "template_id": t["template_id"],
                    "split": split,
                    "label": t["label"],
                    "station": t["station"],
                    **base,
                }
            )
            if t["label"] == "pii" and rng.random() < OBFUSCATE_SHARE:
                variant = fill(t, random.Random(f"{SEED}:{t['template_id']}:{i}"), obf=True)
                if variant["obfuscation"]:
                    cases.append(
                        {
                            "case_id": f"{t['template_id']}-{i}-T312",
                            "template_id": t["template_id"],
                            "split": split,
                            "label": t["label"],
                            "station": t["station"],
                            **variant,
                        }
                    )
    leaks = resolve_leaks(
        cases,
        lambda c: TOKEN.sub("", next(x["text"] for x in templates if x["template_id"] == c["template_id"])),
    )
    dups = within_split_duplicates(cases, lambda c: c["text"])
    write_jsonl(HERE / "cases.jsonl", cases)
    entities = Counter((c["split"], s["entity"]) for c in cases for s in c["spans"])
    lines = [
        "# SPLIT_REPORT — bộ PII tổng hợp",
        "",
        f"{len(templates)} mẫu gốc × {FILLS_PER_TEMPLATE} lần điền "
        f"(seed `{SEED}`), cộng biến dạng T3.12 cho ~{int(OBFUSCATE_SHARE * 100)}% ca PII. Giá trị đều là số giả "
        "đúng định dạng/checksum.",
        "",
        "| split | label | số ca |",
        "| --- | --- | --- |",
    ]
    for (split, label), n in sorted(Counter((c["split"], c["label"]) for c in cases).items()):
        lines.append(f"| {split} | {label} | {n} |")
    lines += ["", "| split | thực thể | số span |", "| --- | --- | --- |"]
    lines += [f"| {s} | {e} | {n} |" for (s, e), n in sorted(entities.items())]
    lines += [
        "",
        f"Kiểm trùng mẫu gốc giữa dev/test: chuyển {leaks['moved_exact']} trùng hẳn, {leaks['moved_near']} gần "
        f"trùng sang dev. Trùng câu trong cùng tập: {dups}.",
        "",
    ]
    (HERE / "SPLIT_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
