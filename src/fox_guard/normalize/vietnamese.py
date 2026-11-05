"""Vietnamese reading views and reversible source coordinates for digit views."""

import csv
import unicodedata
from functools import lru_cache
from pathlib import Path

import regex

_DATA = Path(__file__).resolve().parent.parent / "data"
_TOKEN = regex.compile(r"[\p{L}\p{N}]+")
_FRAGMENT = regex.compile(r"(?<!\w)\p{L}(?:[.\-]\p{L})+(?!\w)")
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"})
_NUMBERS = {
    "không": "0", "một": "1", "hai": "2", "ba": "3", "bốn": "4", "tư": "4",
    "năm": "5", "lăm": "5", "sáu": "6", "bảy": "7", "bẩy": "7", "tám": "8", "chín": "9",
}
_NUMBER_RUN = regex.compile(
    r"(?<!\w)(?:" + "|".join(_NUMBERS) + r")(?:\s+(?:" + "|".join(_NUMBERS) + r")){5,}(?!\w)",
    regex.IGNORECASE,
)
_DIGIT_GAP = regex.compile(r"(?<=\d)[\s.\-]+(?=\d)")
# Leet must not rewrite prices, quantities or identifiers (runs on the no-diacritics view).
_NO_LEET = regex.compile(
    r"\d[\d.,]*(?:d|k|tr|trieu|vnd|%)\d*(?!\p{L})"
    r"|(?<![\p{L}\p{N}])[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}(?![\p{L}\p{N}])"
    r"|(?<![\p{L}\p{N}])[0-9a-f]{16,}(?![\p{L}\p{N}])"
    r"|%[0-9a-f]{2}"
)


def no_diacritics(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")


@lru_cache(maxsize=16)
def load_teencode(path: str) -> dict[str, str]:
    """Missing Anti table means an explicit empty mapping, never built-in guesses."""
    source = Path(path)
    if not source.exists():
        return {}
    with source.open(encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader((line for line in stream if not line.startswith("#")), delimiter="\t")
        required = {"teencode", "chuan", "ambiguous"}
        if not required.issubset(rows.fieldnames or []):
            raise ValueError("teencode TSV requires teencode, chuan, ambiguous columns")
        mapping = {}
        ambiguous = set()
        for row in rows:
            # Keys are looked up without diacritics, so "đt" and "dt" collide; ambiguity wins.
            key = no_diacritics(row["teencode"].lower())
            if row["ambiguous"].strip() == "0":
                mapping.setdefault(key, no_diacritics(row["chuan"].lower()))
            elif row["ambiguous"].strip() == "1":
                ambiguous.add(key)
            else:
                raise ValueError("teencode ambiguous must be 0 or 1")
        return {key: value for key, value in mapping.items() if key not in ambiguous}


def vietnamese_views(nfkc: str, teencode_path=None) -> tuple[str, str]:
    plain = no_diacritics(nfkc).lower()
    joined = _FRAGMENT.sub(lambda m: m.group().replace(".", "").replace("-", ""), plain)
    table = load_teencode(str(Path(teencode_path) if teencode_path else _DATA / "teencode_vi.tsv"))
    protected = [m.span() for m in _NO_LEET.finditer(joined)]

    def replace(match):
        token = match.group()
        if not any(ch.isalpha() for ch in token):
            return token
        if token in table:
            return table[token]
        start, end = match.span()
        if any(a < end and start < b for a, b in protected):
            return token
        token = token.translate(_LEET)
        return table.get(token, token)

    return joined, _TOKEN.sub(replace, joined)


def digit_view(clean: str) -> tuple[str, list[int], list[int]]:
    """Only 6+ consecutive number words become digits; all coordinates stay on clean."""
    chars = []
    starts = []
    ends = []
    cursor = 0
    for match in _NUMBER_RUN.finditer(clean):
        for i in range(cursor, match.start()):
            chars.append(clean[i])
            starts.append(i)
            ends.append(i + 1)
        for word in regex.finditer(r"\S+", match.group()):
            chars.append(_NUMBERS[word.group().lower()])
            starts.append(match.start() + word.start())
            ends.append(match.start() + word.end())
        cursor = match.end()
    for i in range(cursor, len(clean)):
        chars.append(clean[i])
        starts.append(i)
        ends.append(i + 1)
    text = "".join(chars)
    removed = {i for gap in _DIGIT_GAP.finditer(text) for i in range(gap.start(), gap.end())}
    kept = [i for i in range(len(text)) if i not in removed]
    return "".join(chars[i] for i in kept), [starts[i] for i in kept], [ends[i] for i in kept]
