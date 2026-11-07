"""T3 evasion transforms applied to attack templates (docs/plans/01-tan-cong-va-phong-thu.md §T3).

Written from the threat-model definitions only, not from FOX-Guard's normalizer, so the bench does
not inherit the defender's assumptions. Each transform is deterministic given its seed.
"""

import base64
import random
import unicodedata

ZW = ["​", "‌", "‍", "⁠"]
# Latin → look-alike Cyrillic/Greek letters (subset of Unicode confusables).
HOMO = {
    "a": "а",
    "e": "е",
    "o": "о",
    "p": "р",
    "c": "с",
    "x": "х",
    "i": "і",
    "y": "у",
    "A": "А",
    "E": "Е",
    "O": "О",
    "P": "Р",
    "C": "С",
    "H": "Н",
    "K": "К",
    "M": "М",
    "T": "Т",
    "B": "В",
}
# Common Vietnamese chat abbreviations (written for this bench).
TEEN = [
    ("không", "ko"),
    ("Không", "Ko"),
    ("được", "dc"),
    ("gì", "j"),
    ("quy", "wy"),
    ("qua", "wa"),
    ("với", "vs"),
    ("biết", "bit"),
    ("vậy", "v"),
    ("rồi", "r"),
    ("số điện thoại", "sđt"),
    ("tài khoản", "tk"),
    ("mật khẩu", "mk"),
    ("chuyển khoản", "ck"),
    ("anh", "a"),
    ("em", "e"),
    ("phải", "fai"),
    ("nhé", "nha"),
    ("trước", "trc"),
    ("hướng dẫn", "hd"),
]


def zero_width(text: str, rng: random.Random) -> str:
    out = []
    for ch in text:
        out.append(ch)
        if ch.isalpha() and rng.random() < 0.25:
            out.append(rng.choice(ZW))
    return "".join(out)


def unicode_tags(text: str, rng: random.Random) -> str:
    """Visible harmless sentence + the whole payload as invisible Unicode Tags (ASCII smuggling).

    Tags only carry ASCII, so the payload is first stripped of diacritics, as real attacks do."""
    ascii_text = unicodedata.normalize("NFKD", text.replace("đ", "d").replace("Đ", "D"))
    ascii_text = "".join(ch for ch in ascii_text if ord(ch) < 128)
    hidden = "".join(chr(0xE0000 + ord(ch)) for ch in ascii_text)
    return rng.choice(["Sản phẩm dùng ổn, giao nhanh. ", "Cảm ơn shop. ", "Hàng đúng mô tả. "]) + hidden


def homoglyph(text: str, rng: random.Random) -> str:
    return "".join(HOMO[ch] if ch in HOMO and rng.random() < 0.35 else ch for ch in text)


def fullwidth(text: str, rng: random.Random) -> str:
    return "".join(chr(ord(ch) + 0xFEE0) if "!" <= ch <= "~" and rng.random() < 0.6 else ch for ch in text)


def b64(text: str, rng: random.Random) -> str:
    lead = rng.choice(["Ghi chú (mã hoá): ", "Nội dung: ", "Decode giúp: "])
    return lead + base64.b64encode(text.encode("utf-8")).decode()


def no_diacritics(text: str, rng: random.Random) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")


def teencode(text: str, rng: random.Random) -> str:
    for full, short in TEEN:
        if rng.random() < 0.8:
            text = text.replace(full, short)
    return text


TRANSFORMS = {
    "T3.1": zero_width,
    "T3.2": unicode_tags,
    "T3.4": homoglyph,
    "T3.5": fullwidth,
    "T3.8": b64,
    "T3.10": no_diacritics,
    "T3.11": teencode,
}
