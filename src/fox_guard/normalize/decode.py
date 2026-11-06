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
# Hex must contain a letter a–f: an all-digit run is a card/account/order number, not encoded text.
_HEX = re.compile(r"(?i)(?<!\w)(?:0x)?(?=[0-9]*[a-f])(?:[0-9a-f]{2}){8,}(?!\w)")
_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})|\\U([0-9a-fA-F]{8})")
_PERCENT = re.compile(r"%[0-9a-fA-F]{2}")
_ENTITY = re.compile(r"&(?:#[0-9]+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);")


def readable(text: str) -> bool:
    """No binary/control garbage, and >=80% letters, digits or whitespace."""
    if len(text) < 8 or not all(ch.isprintable() or ch in "\n\r\t" for ch in text):
        return False
    return sum(ch.isalnum() or ch.isspace() for ch in text) / len(text) >= 0.8


def hides_text(pieces) -> bool:
    """Escapes that only spell spaces/punctuation (URL %20, &amp;) are ordinary text, not hiding."""
    return any(ch.isalnum() or ord(ch) >= 0x80 for piece in pieces for ch in piece)


_ENTITY_RUN = re.compile(r"(?:&(?:#[0-9]+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);)+")
_ESCAPE_RUN = re.compile(r"(?:\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8})+")
_PERCENT_RUN = re.compile(r"(?:%[0-9a-fA-F]{2})+")


def encoded_spans(text: str) -> list[tuple[int, int]]:
    """Spans this decoder could turn into hidden text: what the audit must not keep (review round 7).

    Same rules as candidates(): base64/hex tokens that decode to readable text, and runs of
    entities, \\u escapes or %XX that spell letters or digits (not "&amp;" or "%20" alone).
    """
    exclusions = [m.span() for pattern in (_UUID, _JWT, _HASH) for m in pattern.finditer(text)]
    spans = []
    for pattern, decode in ((_B64, lambda t: base64.b64decode(t + "=" * (-len(t) % 4), altchars=b"-_",
                                                              validate=True).decode("utf-8")),
                            (_HEX, lambda t: bytes.fromhex(t[2:] if t.lower().startswith("0x") else t)
                             .decode("utf-8"))):
        for match in pattern.finditer(text):
            if any(match.start() < right and match.end() > left for left, right in exclusions):
                continue
            try:
                if readable(decode(match.group())):
                    spans.append(match.span())
            except (ValueError, binascii.Error, UnicodeDecodeError):
                continue
    for pattern, decode in ((_ENTITY_RUN, html.unescape),
                            (_ESCAPE_RUN, lambda t: _ESCAPE.sub(lambda e: chr(int(e[1] or e[2], 16)), t)),
                            (_PERCENT_RUN, lambda t: unquote(t, encoding="latin-1"))):
        spans.extend(m.span() for m in pattern.finditer(text) if hides_text([decode(m.group())]))
    return sorted(spans)


def candidates(text: str):
    """Yield (decoded text, codec); never execute text or perform I/O.

    IDs are excluded as whole source spans before either base64 or hex scans.
    ROT13 and "*-plain" codecs are reading views, never independent findings.
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
            pieces = [unquote(m.group(), encoding="latin-1") for m in _PERCENT.finditer(text)]
            yield value, "percent" if hides_text(pieces) else "percent-plain"
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
            pieces = [html.unescape(m.group()) for m in _ENTITY.finditer(text)]
            yield value, "html" if hides_text(pieces) else "html-plain"
    value = codecs.decode(text, "rot_13")
    if value != text and readable(value):
        yield value, "rot13"
