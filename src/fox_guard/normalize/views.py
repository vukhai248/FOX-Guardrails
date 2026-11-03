"""Normalization views and coordinates in the application-facing clean text."""

from dataclasses import dataclass, field

from fox_guard.types import Finding


@dataclass
class NormalizedText:
    """Raw is immutable by convention; decoded nodes are flat, steps-1–6 views.

    digits_map[i] is the clean start position of digits[i]. Use span_in_clean
    to include the full final word when a written-number token became a digit.
    Findings on decoded nodes use local clean coordinates; root copies use None.
    """

    raw: str
    sha256: str
    base: str
    clean: str
    nfkc: str
    skeleton: str
    vi_nodiac: str
    vi_teencode: str
    digits: str
    digits_map: list[int]
    hidden_tags: str
    decoded: list["NormalizedText"] = field(default_factory=list)
    signals: list[Finding] = field(default_factory=list)
    _digits_ends: list[int] = field(default_factory=list, repr=False)

    def span_in_clean(self, start: int, end: int) -> tuple[int, int]:
        """Map a half-open digits span back to clean, including source word ends."""
        if not 0 <= start <= end <= len(self.digits):
            raise ValueError("digits span is out of bounds")
        if start == end:
            anchor = self.digits_map[start] if start < len(self.digits_map) else len(self.clean)
            return anchor, anchor
        return self.digits_map[start], self._digits_ends[end - 1]
