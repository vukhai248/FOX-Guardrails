"""SDK entry points: Lớp 1 chuẩn hoá + Lớp 2 luật; chưa chặn gì cho tới Lớp 4 (policy)."""

from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING
from uuid import uuid4

from .config import GuardConfig, load_config
from .types import Decision, GuardContext

if TYPE_CHECKING:
    from .normalize.views import NormalizedText

_RISK_ORDER = {"low": 0, "medium": 1, "high": 2}
_REASONS = {
    "unicode:tags": "Phát hiện ký tự Unicode Tags ẩn chứa nội dung.",
    "unicode:invisible": "Phát hiện ký tự Unicode vô hình bất thường.",
    "unicode:mixed_script": "Phát hiện một từ trộn nhiều hệ chữ dễ gây nhầm lẫn.",
    "unicode:encoded": "Phát hiện nội dung được giấu bằng mã hoá.",
    "unicode:oversize": "Văn bản quá dài; chỉ kiểm tra phần trong giới hạn cấu hình.",
    "oversize": "Văn bản quá dài; chỉ kiểm tra phần trong giới hạn cấu hình.",
}


class Guard:
    """Three-station SDK; chưa chặn gì cho tới Lớp 4.

    Normalization signals and rule findings are reported; classifier, policy, PII masking,
    restoration, and audit are not active yet, so action is always "allow".
    """

    def __init__(self, config: GuardConfig | None = None) -> None:
        self.config = config if config is not None else GuardConfig()

    @classmethod
    def from_config(cls, path: str | Path) -> "Guard":
        """Load validated YAML configuration; unknown keys raise validation errors."""
        return cls(load_config(path))

    def _normalize(self, text: str) -> "NormalizedText":
        # Keep contract/config imports independent of the normalization package.
        from .normalize import normalize

        return normalize(
            text,
            max_chars=self.config.normalize.max_chars,
            decode_max_depth=self.config.normalize.decode_max_depth,
        )

    def _check(self, text: str, station: str) -> Decision:
        from .detectors.rules import rule_reasons, run_rules

        started = perf_counter()
        normalized = self._normalize(text)
        findings = [*normalized.signals, *run_rules(normalized, station)]
        reasons = {**_REASONS, **rule_reasons()}
        risk = max((finding.severity for finding in findings), key=_RISK_ORDER.__getitem__, default="low")
        decision = Decision(
            decision_id=uuid4().hex,
            action="allow",
            text=normalized.clean,
            risk=risk,
            findings=findings,
            reasons=[
                reasons.get(finding.detector, f"Phát hiện tín hiệu bất thường: {finding.detector}.")
                for finding in findings
            ],
            latency_ms=0.0,
        )
        decision.latency_ms = (perf_counter() - started) * 1000
        return decision

    def check_input(self, text: str, ctx: GuardContext) -> Decision:
        """Normalize customer input and run station rules; chưa chặn gì cho tới Lớp 4.

        The station comes from the method, never from ctx.station, so a mislabeled context
        cannot switch off context-only rules.
        """
        return self._check(text, "input")

    def check_context(self, text: str, ctx: GuardContext) -> Decision:
        """Normalize an untrusted context segment and run station rules; chưa chặn gì cho tới Lớp 4."""
        return self._check(text, "context")

    def check_output(self, text: str, ctx: GuardContext) -> Decision:
        """Normalize a generated answer and run station rules; chưa chặn gì cho tới Lớp 4."""
        return self._check(text, "output")

    def restore(self, text: str, ctx: GuardContext) -> str:
        """Pass text through in wave 1; placeholder restoration is reserved for B5."""
        return text

    def redact_for_log(self, text: str, ctx: GuardContext) -> str:
        """Return clean only in wave 1; PII privacy for logging is not implemented."""
        # TODO(B5): irreversibly mask PII for guard_log; never restore placeholders here.
        return self._normalize(text).clean
