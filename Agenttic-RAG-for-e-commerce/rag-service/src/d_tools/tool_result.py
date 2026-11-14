"""Keep customer text separate until context guards have inspected it."""
from dataclasses import dataclass, field
from typing import Callable, Literal

Source = Literal["review", "order_note", "ticket_note", "product_desc"]


@dataclass
class Segment:
    source: Source
    ref_id: str
    text: str

    def __post_init__(self):
        if self.source not in {"review", "order_note", "ticket_note", "product_desc"}:
            raise ValueError("Unknown untrusted source")


@dataclass
class ToolResult:
    tool: str
    trusted: str
    untrusted: list[Segment] = field(default_factory=list)
    # Optional layout preserves legacy order output without putting raw PII in trusted.
    render_parts: list[str | int] | None = field(default=None, repr=False)
    segment_renderer: Callable[[str], str] | None = field(default=None, repr=False)

    def render(self) -> str:
        texts = [self.segment_renderer(s.text) if self.segment_renderer else s.text for s in self.untrusted]
        if self.render_parts is not None:
            return "".join(texts[p] if isinstance(p, int) else p for p in self.render_parts)
        return "\n".join([self.trusted, *texts])

    __str__ = render
