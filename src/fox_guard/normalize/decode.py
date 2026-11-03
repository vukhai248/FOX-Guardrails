"""Conservative, bounded decoder candidates; orchestration enforces global budgets."""

import base64
import binascii
import codecs
import html
import re
from urllib.parse import unquote

_UUID = re.compile(r"(?i)(?<![\w-])[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}(?![\w-])")
_JWT = re.compile(r"(?<![\w.-])[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+(?![\w.-])")
_HASH = re.compile(r"(?i)(?<![\w])[0-9a-f]{64}(?!\w)|(?<!\w)[0-9a-f]{40}(?!\w)|(?<!\w)[0-9a-f]{32}(?!\w)")
_B64 = re.compile(r"(?<![\w+/=-])[A-Za-z0-9+/_-]{8,}={0,2}(?![\w+/=-])")
_HEX = re.compile(r"(?i)(?<!\w)(?:0x)?(?:[0-9a-f]{2}){8,}(?!\w)")
_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})|\\U([0-9a-fA-F]{8})")
_PERCENT = re.compile(r"%[0-9a-fA-F]{2}")
_ENTITY = re.compile(r"&(?:#[0-9]+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);")


def readable(text: str) -> bool:
    """No binary/control garbage, and >=80% letters, digits or whitespace."""
    if len(text) < 8 or not all(ch.isprintable() or ch in "\n\r\t" for ch in text):
        return False
    return sum(ch.isalnum() or ch.isspace() for ch in text) / len(text) >= 0.8


def candidates(text: str):
    """Yield (decoded text, codec); never execute text or perform I/O.

    IDs are excluded as whole source spans before either base64 or hex scans.
    ROT13 is a reading view, never an independent finding.
    """
    exclusions = [m.span() for pattern in (_UUID, _JWT, _HASH) for m in pattern.finditer(text)]

    def excluded(start, end):
        return any(start < right and end > left for left, right in exclusions)

    for match in _B64.finditer(text):
        if excluded(*match.span()):
            continue
        token = match.group()
        try:
            padded = token + "=" * (-len(token) % 4)
            value = base64.b64decode(padded, altchars=b"-_", validate=True).decode("utf-8")
        except (ValueError, binascii.Error, UnicodeDecodeError):
            continue
        if readable(value):
            yield value, "base64"
    for match in _HEX.finditer(text):
        if excluded(*match.span()):
            continue
        token = match.group()
        if token.lower().startswith("0x"):
            token = token[2:]
        try:
            value = bytes.fromhex(token).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            continue
        if readable(value):
            yield value, "hex"
    if _PERCENT.search(text):
        try:
            value = unquote(text, encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            value = ""
        if value != text and readable(value):
            yield value, "percent"
    if _ESCAPE.search(text):
        try:
            value = _ESCAPE.sub(lambda m: chr(int(m[1] or m[2], 16)), text)
            # JSON-style supplementary characters can be encoded as surrogate pairs.
            value = value.encode("utf-16", "surrogatepass").decode("utf-16")
        except (ValueError, UnicodeError):
            value = ""
        if value != text and readable(value):
            yield value, "unicode"
    if _ENTITY.search(text):
        value = html.unescape(text)
        if value != text and readable(value):
            yield value, "html"
    value = codecs.decode(text, "rot_13")
    if value != text and readable(value):
        yield value, "rot13"
