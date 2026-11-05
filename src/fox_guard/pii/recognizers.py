"""Lớp 3: Vietnamese PII recognizers (format + checksum + context words), no models, no I/O."""

from dataclasses import dataclass

import regex

from fox_guard.normalize import NormalizedText
from fox_guard.normalize.vietnamese import no_diacritics

# 63 province codes used as the first three digits of a 12-digit CCCD (Thông tư 07/2016/TT-BCA).
CCCD_PROVINCES = frozenset(
    "001 002 004 006 008 010 011 012 014 015 017 019 020 022 024 025 026 027 030 031 033 034 035 036 037 038 "
    "040 042 044 045 046 048 049 051 052 054 056 058 060 062 064 066 067 068 070 072 074 075 077 079 080 082 "
    "083 084 086 087 089 091 092 093 094 095 096".split()
)
# Prefix of BHYT card = "mã đối tượng" (subset of the official list; context words also accept others).
BHYT_PREFIXES = frozenset("DN HC CH NN TK HT TB NO CT XK CA CK CB KC HD BT HN DT DK XD TS TC TQ TA TY HG LS "
                          "PV CC CN HS SV GB GD XN TE".split())

ENTITY_SEVERITY = {
    "VN_CCCD": "medium", "VN_CMND": "medium", "VN_PHONE": "medium", "EMAIL": "medium",
    "CREDIT_CARD": "high", "VN_BANK_ACCOUNT": "medium", "VN_TAX_ID": "low", "VN_PASSPORT": "medium",
    "VN_LICENSE_PLATE": "low", "VN_HEALTH_INSURANCE": "medium", "OTP": "high", "PASSWORD": "high",
    "PERSON": "low", "VN_ADDRESS": "low",
}
# When two matches overlap, the higher priority wins (a card number is not also a bank account).
# Tax id and bank account need an explicit context word, so they beat a look-alike phone number
# ("MST 0394217863", "stk 0912345678"); a bank account is also masked more strictly than a phone.
_PRIORITY = ["PASSWORD", "OTP", "CREDIT_CARD", "VN_CCCD", "VN_HEALTH_INSURANCE", "VN_PASSPORT", "EMAIL",
             "VN_TAX_ID", "VN_BANK_ACCOUNT", "VN_PHONE", "VN_CMND", "VN_LICENSE_PLATE", "VN_ADDRESS",
             "PERSON"]

_CONTEXT = {  # matched on the no-diacritics, lowercase window before the value
    "VN_CCCD": r"cccd|can cuoc|cmnd|chung minh|so dinh danh|dinh danh",
    "VN_CMND": r"cmnd|chung minh|cmt",
    "VN_BANK_ACCOUNT": r"stk|so tai khoan|tai khoan|so tk|\btk\b|chuyen khoan|\bck\b|ngan hang|"
                       r"vietcombank|vcb|"
                       r"techcombank|tcb|vietinbank|bidv|agribank|mb bank|mbbank|acb|tpbank|vpbank|sacombank|"
                       r"momo|zalopay",
    "VN_TAX_ID": r"mst|ma so thue|ma thue|tax",
    "VN_PASSPORT": r"ho chieu|passport",
    "VN_LICENSE_PLATE": r"bien so|bien kiem soat|\bbks\b|xe",
    "VN_HEALTH_INSURANCE": r"bhyt|bao hiem y te|the bao hiem",
}
_CONTEXT_RE = {key: regex.compile(rf"(?:{value})") for key, value in _CONTEXT.items()}

_D = r"(?<![\p{N}\p{L}])"  # left boundary: not inside a longer number or word
_E = r"(?![\p{N}\p{L}])"
_PHONE = regex.compile(_D + r"(?:\+84|0084|0)(?:3[2-9]|5[25689]|7[06-9]|8[1-9]|9\d)\d{7}" + _E
                       + r"|" + _D + r"(?:\+84|0)2\d{9}" + _E)
_EMAIL = regex.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*"
                       r"\.[A-Za-z]{2,}(?![\w-])")
_CARD = regex.compile(_D + r"(?:\d[ -]?){12,18}\d" + _E)
_DIGITS = {n: regex.compile(_D + rf"\d{{{n}}}" + _E) for n in (9, 10, 12, 13)}
_DIGIT_RUN = regex.compile(_D + r"\d{9,16}" + _E)
_TAX13 = regex.compile(_D + r"\d{10}-\d{3}" + _E)
_PASSPORT = regex.compile(r"(?<![\p{L}\p{N}])[A-Z]\d{7}(?![\p{L}\p{N}])")
_PLATE = regex.compile(r"(?<![\p{L}\p{N}])(\d{2})[A-Z]{1,2}\d?[- ]?\d{3}\.?\d{2}(?![\p{L}\p{N}])")
_BHYT = regex.compile(r"(?<![\p{L}\p{N}])([A-Z]{2})\d{13}(?![\p{L}\p{N}])")
_SECRET = regex.compile(
    r"(?i)(?P<cue>m[aã]\s*(?:otp|x[aá]c\s*(?:th[uự]c|nh[aậ]n)|pin)|otp|m[aã]\s*b[aả]o\s*m[aậ]t)"
    r"(?:\s*(?:c[uủ]a\s*(?:em|m[iì]nh|t[oô]i|anh|ch[iị]))?\s*(?:l[aà]|:|=|-)?\s*)(?P<value>\d{4,8})(?!\d)")
_PASSWORD = regex.compile(
    r"(?i)(?P<cue>m[aậ]t\s*kh[aẩ]u|\bmk\b|\bpass(?:word)?\b|\bpwd\b)"
    r"(?:\s*(?:c[uủ]a\s*(?:em|m[iì]nh|t[oô]i|anh|ch[iị]))?\s*(?:l[aà]|:|=)\s*)(?P<value>[^\s,;]{4,64})")
_UNIT_AFTER = regex.compile(r"^\s?(?:đ|₫|vnd|vnđ|k\b|tr\b|triệu|nghìn|ngàn|%|gb|mah|w\b|cm|mm|kg|g\b)",
                            regex.IGNORECASE)
# UUIDs and hex hashes are IDs, not PII. A hash must contain a letter a–f: an all-digit run of 16+
# is a card or account number, never "hex" (that bug once let 4242424242424242 into logs).
_ID_TOKEN = regex.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"
                          r"|(?<![0-9a-fA-F])(?=[0-9a-fA-F]*[a-fA-F])[0-9a-fA-F]{16,}(?![0-9a-fA-F])")

# Person / address: keyword heuristics only (a learned NER is an open item, see README).
_NAME = r"\p{Lu}\p{Ll}+(?:\s+\p{Lu}\p{Ll}*){0,4}"
_PERSON = regex.compile(
    r"(?:(?i:người\s*nhận|nguoi\s*nhan|họ\s*(?:và\s*)?tên|ho\s*ten|tên\s*(?:khách|người\s*nhận)|ten)\s*[:\-]\s*"
    r"(?P<a>" + _NAME + r"))|(?:(?<![\p{L}])(?:anh|chị|chi|ông|ong|bà|ba|cô|chú|em)\s+(?P<b>\p{Lu}\p{Ll}+"
    r"(?:\s+\p{Lu}\p{Ll}+){1,3}))")
_ADMIN = (r"(?:phường|phuong|xã|xa|thị\s*trấn|quận|quan|huyện|huyen|thị\s*xã|thành\s*phố|thanh\s*pho|tp\.?|"
          r"tỉnh|tinh|p\.|q\.|ấp|thôn|khu\s*phố|tổ)(?!\p{L})")
_ADDRESS = regex.compile(
    r"(?i)(?:(?:số\s*nhà|so\s*nha|số|so|nhà)\s*)?(?<![\p{N}.,])\d{1,5}[a-z]?(?:/\d{1,4}[a-z]?)*\s*,?\s*"
    r"(?:(?:ngõ|ngo|ngách|ngach|hẻm|hem|kiệt|kiet)\s*\d{1,4}\s*,?\s*)?"
    r"(?:đường|duong|phố|pho|đ\.)?\s*[\p{L}0-9 .'-]{2,40}?,\s*" + _ADMIN + r"[^\n,;]{1,30}"
    r"(?:,\s*[^\n,;]{1,40}){0,3}")


@dataclass(frozen=True)
class PiiMatch:
    entity: str
    start: int
    end: int
    value: str
    confident: bool  # format/checksum AND context, or a format that is unambiguous on its own


def luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2:
            n = n * 2 - 9 if n > 4 else n * 2
        total += n
    return total % 10 == 0


def card_brand_ok(digits: str) -> bool:
    if digits.startswith("9704") and len(digits) in (16, 19):
        return True  # NAPAS
    if digits[0] == "4" and len(digits) in (13, 16, 19):
        return True  # Visa
    prefix2, prefix4 = int(digits[:2]), int(digits[:4])
    if (51 <= prefix2 <= 55 or 2221 <= prefix4 <= 2720) and len(digits) == 16:
        return True  # Mastercard
    if digits[:2] in ("34", "37") and len(digits) == 15:
        return True  # Amex
    return 3528 <= prefix4 <= 3589 and len(digits) in (16, 19)  # JCB


def tax_id_ok(digits: str) -> bool:
    """Community formula for the 10-digit MST check digit (documented, not an official spec)."""
    weights = (31, 29, 23, 19, 17, 13, 7, 5, 3)
    check = 10 - sum(int(d) * w for d, w in zip(digits[:9], weights, strict=True)) % 11
    return check < 10 and check == int(digits[9])


def cccd_ok(digits: str) -> bool:
    # Province code, then century/gender digit 0–3 (born 1900–2099), then 2-digit birth year.
    return digits[:3] in CCCD_PROVINCES and digits[3] in "0123"


def _context(lowered: str, start: int, entity: str) -> bool:
    window = lowered[max(0, start - 30):start]
    return bool(_CONTEXT_RE[entity].search(window))


def _scan(text: str) -> list[PiiMatch]:
    lowered = no_diacritics(text).lower()
    out: list[PiiMatch] = []
    ids = [m.span() for m in _ID_TOKEN.finditer(text)]

    def inside_id(a, b):
        return any(a < right and left < b for left, right in ids)

    def add(entity, start, end, confident):
        if not inside_id(start, end):
            out.append(PiiMatch(entity, start, end, text[start:end], confident))

    def is_amount(end):
        return bool(_UNIT_AFTER.match(text[end:end + 8]))

    for m in _SECRET.finditer(text):
        add("OTP", m.start("value"), m.end("value"), True)
    for m in _PASSWORD.finditer(text):
        add("PASSWORD", m.start("value"), m.end("value"), True)
    for m in _EMAIL.finditer(text):
        add("EMAIL", *m.span(), True)
    for m in _PHONE.finditer(text):
        if not is_amount(m.end()):
            add("VN_PHONE", *m.span(), True)
    for m in _CARD.finditer(text):
        digits = regex.sub(r"\D", "", m.group())
        if 13 <= len(digits) <= 19 and luhn_ok(digits) and card_brand_ok(digits):
            add("CREDIT_CARD", *m.span(), True)
    for m in _DIGITS[12].finditer(text):
        if cccd_ok(m.group()) and not is_amount(m.end()):
            add("VN_CCCD", *m.span(), _context(lowered, m.start(), "VN_CCCD"))
    for m in _DIGITS[9].finditer(text):
        if _context(lowered, m.start(), "VN_CMND") and not is_amount(m.end()):
            add("VN_CMND", *m.span(), True)
    for m in _DIGITS[10].finditer(text):
        if tax_id_ok(m.group()) and _context(lowered, m.start(), "VN_TAX_ID"):
            add("VN_TAX_ID", *m.span(), True)
    for m in _TAX13.finditer(text):
        if tax_id_ok(m.group()[:10]) and _context(lowered, m.start(), "VN_TAX_ID"):
            add("VN_TAX_ID", *m.span(), True)
    for m in _DIGIT_RUN.finditer(text):
        if _context(lowered, m.start(), "VN_BANK_ACCOUNT") and not is_amount(m.end()):
            add("VN_BANK_ACCOUNT", *m.span(), True)
    for m in _PASSPORT.finditer(text):
        if _context(lowered, m.start(), "VN_PASSPORT"):
            add("VN_PASSPORT", *m.span(), True)
    for m in _PLATE.finditer(text):
        if 11 <= int(m.group(1)) <= 99 and _context(lowered, m.start(), "VN_LICENSE_PLATE"):
            add("VN_LICENSE_PLATE", *m.span(), True)
    for m in _BHYT.finditer(text):
        if m.group(1) in BHYT_PREFIXES or _context(lowered, m.start(), "VN_HEALTH_INSURANCE"):
            add("VN_HEALTH_INSURANCE", *m.span(), True)
    for m in _PERSON.finditer(text):
        group = "a" if m.group("a") else "b"
        add("PERSON", m.start(group), m.end(group), False)
    for m in _ADDRESS.finditer(text):
        add("VN_ADDRESS", m.start(), m.end(), False)
    return out


def _resolve(matches: list[PiiMatch]) -> list[PiiMatch]:
    rank = {name: i for i, name in enumerate(_PRIORITY)}
    chosen: list[PiiMatch] = []
    for match in sorted(matches, key=lambda m: (rank[m.entity], -(m.end - m.start))):
        if all(match.end <= c.start or c.end <= match.start for c in chosen):
            chosen.append(match)
    return sorted(chosen, key=lambda m: m.start)


def detect_pii(normalized: NormalizedText) -> list[PiiMatch]:
    """Detect PII on clean, plus the digits view (catches '0 9 1 2 . 3 4 5…' and written numbers).

    Every span is on `clean`. Digits-view hits are mapped back with span_in_clean.
    """
    matches = _scan(normalized.clean)
    if normalized.digits != normalized.clean:
        for m in _scan(normalized.digits):
            if m.entity in ("PERSON", "VN_ADDRESS", "EMAIL", "PASSWORD"):
                continue
            start, end = normalized.span_in_clean(m.start, m.end)
            matches.append(PiiMatch(m.entity, start, end, normalized.clean[start:end], m.confident))
    return _resolve(matches)
