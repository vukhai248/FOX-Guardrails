"""Unicode transforms with contextual exceptions for legitimate emoji."""

import unicodedata
from functools import lru_cache
from pathlib import Path

import regex

from fox_guard.types import Finding

_DATA = Path(__file__).resolve().parent.parent / "data"
_FLAG = regex.compile("\U0001f3f4[\U000e0030-\U000e0039\U000e0061-\U000e007a]{1,6}\U000e007f")
_EP = regex.compile(r"\p{Extended_Pictographic}\Z")
_IGNORABLE = regex.compile(r"\p{Default_Ignorable_Code_Point}\Z")
_WORDS = regex.compile(r"\p{L}[\p{L}\p{M}\p{N}]*")
_SCRIPTS = {name: regex.compile(rf"\p{{Script={name}}}") for name in ("Latin", "Greek", "Cyrillic")}


def finding(detector, severity, evidence, technique=None, span=None):
    return Finding(
        detector=detector, kind="unicode", severity=severity,
        evidence=evidence, technique=technique, span=span,
    )


def strip_hidden(base: str) -> tuple[str, str, list[Finding]]:
    """Steps 2–3; tag payloads are collected before generic ignorable removal."""
    allowed_tags = {i for match in _FLAG.finditer(base) for i in range(match.start(), match.end())}
    categories = [unicodedata.category(ch) for ch in base]
    ignorables = [bool(_IGNORABLE.fullmatch(ch)) for ch in base]
    # Neighbours across a run, computed in linear time (not one scan per mark).
    left = []
    neighbour = ""
    for i, ch in enumerate(base):
        left.append(neighbour)
        if categories[i] not in {"Cf", "Mn"} and not ignorables[i]:
            neighbour = ch
    right = [""] * len(base)
    neighbour = ""
    for i in range(len(base) - 1, -1, -1):
        right[i] = neighbour
        if categories[i] not in {"Cf", "Mn"} and not ignorables[i]:
            neighbour = base[i]
    tags = []
    tag_count = 0
    output = []
    invisible = []
    for i, ch in enumerate(base):
        cp = ord(ch)
        if i in allowed_tags:
            output.append(ch)
            continue
        if 0xE0000 <= cp <= 0xE007F:
            tag_count += 1
            # LANGUAGE TAG and CANCEL TAG are controls, not hidden ASCII text.
            if 0xE0020 <= cp <= 0xE007E:
                tags.append(chr(cp - 0xE0000))
            continue
        before = base[i - 1] if i else ""
        after = base[i + 1] if i + 1 < len(base) else ""
        emoji_before = before
        if before == "\ufe0f" and i >= 2:
            emoji_before = base[i - 2]
        # Emoji modifiers may precede a ZWJ, e.g. person + skin tone + ZWJ + laptop.
        if emoji_before and 0x1F3FB <= ord(emoji_before) <= 0x1F3FF and i >= 2:
            emoji_before = base[i - 2]
        if ch == "\u200d" and _EP.fullmatch(emoji_before) and _EP.fullmatch(after):
            output.append(ch)
            continue
        is_vs = 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF
        if ch == "\ufe0f" and (
            _EP.fullmatch(before) or (before in "0123456789#*" and before and after == "\u20e3")
        ):
            output.append(ch)
            continue
        run_before, run_after = left[i], right[i]
        ascii_interior = bool(run_before and run_after and run_before.isascii() and run_after.isascii()
                              and run_before.isalpha() and run_after.isalpha())
        remove = (categories[i] == "Cf" or ignorables[i]
                  or is_vs or (categories[i] == "Mn" and ascii_interior))
        if remove:
            between_letters = bool(run_before and run_after and run_before.isalpha() and run_after.isalpha())
            invisible.append((len(output), between_letters))
        else:
            output.append(ch)
    clean = "".join(output)
    hidden_tags = "".join(tags)
    signals = []
    if tag_count:
        severity = "high" if sum(c.isalpha() for c in hidden_tags) >= 3 else "low"
        signals.append(finding("unicode:tags", severity, f"Unicode Tags: {tag_count} code points", "T3.2"))
    if invisible:
        severity = "medium" if any(middle for _, middle in invisible) else "low"
        anchor = invisible[0][0]
        signals.append(finding("unicode:invisible", severity,
                               f"Removed {len(invisible)} invisible code points", "T3.1", (anchor, anchor)))
    return clean, hidden_tags, signals


@lru_cache(maxsize=1)
def load_confusables() -> dict[int, str]:
    """Load the bundled, pinned Unicode 16.0.0 UTS #39 table once."""
    mapping = {}
    for line in (_DATA / "confusables.txt").read_text(encoding="utf-8").splitlines():
        content = line.split("#", 1)[0].strip()
        if not content:
            continue
        source, target, *_ = content.split(";")
        points = source.split()
        if len(points) != 1:
            raise ValueError("Unsupported multi-code-point confusables source")
        mapping[int(points[0], 16)] = "".join(chr(int(p, 16)) for p in target.split())
    return mapping


def skeleton(text: str) -> str:
    """UTS #39 skeleton: NFD, map each code point, then NFD again."""
    decomposed = unicodedata.normalize("NFD", text)
    mapped = decomposed.translate(load_confusables())
    return unicodedata.normalize("NFD", mapped)


def mixed_script_signals(clean: str) -> list[Finding]:
    """Inspect NFKC word scripts while retaining the original clean word span."""
    signals = []
    for match in _WORDS.finditer(clean):
        word = unicodedata.normalize("NFKC", match.group())
        scripts = [name for name, pattern in _SCRIPTS.items() if pattern.search(word)]
        if len(scripts) > 1:
            signals.append(finding("unicode:mixed_script", "medium", "Mixed scripts: " + ", ".join(scripts),
                                   "T3.4", match.span()))
    return signals
