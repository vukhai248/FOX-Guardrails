"""Eight-step FOX-Guard normalization, with raw retention and bounded decode views."""

import hashlib
import unicodedata
from collections import deque

from .decode import candidates
from .unicode import finding, mixed_script_signals, skeleton, strip_hidden
from .vietnamese import digit_view, vietnamese_views
from .views import NormalizedText

__all__ = ["NormalizedText", "normalize"]


def _views(raw: str, inspected: str, teencode_path=None) -> NormalizedText:
    base = unicodedata.normalize("NFC", inspected)
    clean, hidden_tags, signals = strip_hidden(base)
    nfkc = unicodedata.normalize("NFKC", clean)
    signals.extend(mixed_script_signals(clean))
    vi_nodiac, vi_teencode = vietnamese_views(nfkc, teencode_path)
    digits, positions, ends = digit_view(clean)
    return NormalizedText(
        raw=raw, sha256=hashlib.sha256(raw.encode("utf-8", "surrogatepass")).hexdigest(),
        base=base, clean=clean, nfkc=nfkc, skeleton=skeleton(nfkc),
        vi_nodiac=vi_nodiac, vi_teencode=vi_teencode, digits=digits,
        digits_map=positions, hidden_tags=hidden_tags, signals=signals, _digits_ends=ends,
    )


def normalize(text: str, *, max_chars: int = 20000, decode_max_depth: int = 2,
              teencode_path=None) -> NormalizedText:
    """Build detector views; this layer alone does not block requests.

    Step 8's inspection cap is applied before costly steps 1–7. Raw and its hash
    always cover the full input. Decoding uses a flat breadth-first queue, depth
    <=2, and a total accepted-output budget <=8x inspected input. Children contain
    steps 1–6 views and no children of their own. Child findings copied to root
    have span=None because decoded offsets are not offsets in root.clean.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(max_chars, int) or isinstance(max_chars, bool) or not 1 <= max_chars <= 20000:
        raise ValueError("max_chars must be an integer between 1 and 20000")
    if (not isinstance(decode_max_depth, int) or isinstance(decode_max_depth, bool)
            or not 0 <= decode_max_depth <= 2):
        raise ValueError("decode_max_depth must be an integer between 0 and 2")
    inspected = text[:max_chars]
    root = _views(text, inspected, teencode_path)
    if len(text) > max_chars:
        root.signals.append(finding("oversize", "medium", f"Inspection truncated at {max_chars} characters",
                                    span=(len(root.clean), len(root.clean))))
    budget = 8 * len(inspected)
    seen = {inspected, root.clean, root.nfkc}
    queue = deque([(root.nfkc, 0)])
    # Hidden tags are a separate view, already signaled by step 2; decoding it is
    # useful for a base64 payload hidden inside tags and shares the same budget.
    if root.hidden_tags:
        queue.append((root.hidden_tags, 0))
    encoded_codecs = set()
    while queue:
        source, depth = queue.popleft()
        if depth >= decode_max_depth:
            continue
        for value, codec in candidates(source):
            if value in seen or len(value) > budget:
                continue
            seen.add(value)
            budget -= len(value)
            child = _views(value, value, teencode_path)
            root.decoded.append(child)
            root.signals.extend(signal.model_copy(update={"span": None}) for signal in child.signals)
            if codec != "rot13" and not codec.endswith("-plain"):
                encoded_codecs.add(codec)
            queue.append((child.nfkc, depth + 1))
            if child.hidden_tags:
                queue.append((child.hidden_tags, depth + 1))
    if encoded_codecs:
        root.signals.append(finding("unicode:encoded", "medium",
                                    "Decoded views: " + ", ".join(sorted(encoded_codecs)), "T3.8"))
    return root
