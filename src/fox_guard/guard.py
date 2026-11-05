"""SDK entry points: Lớp 1 chuẩn hoá + Lớp 2 luật + Lớp 3 PII; chưa chặn gì cho tới Lớp 4 (policy)."""

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
    "pii:unknown_placeholder": "Câu trả lời chứa mã giả danh PII không do guard cấp (bot bịa hoặc bị dụ).",
}
_PII_NAMES = {
    "VN_PHONE": "số điện thoại", "EMAIL": "email", "VN_CCCD": "số CCCD", "VN_CMND": "số CMND",
    "CREDIT_CARD": "số thẻ", "VN_BANK_ACCOUNT": "số tài khoản", "VN_TAX_ID": "mã số thuế",
    "VN_PASSPORT": "số hộ chiếu", "VN_LICENSE_PLATE": "biển số xe", "VN_HEALTH_INSURANCE": "số thẻ BHYT",
    "OTP": "mã OTP", "PASSWORD": "mật khẩu", "PERSON": "họ tên", "VN_ADDRESS": "địa chỉ",
}


class Guard:
    """Three-station SDK; chưa chặn gì cho tới Lớp 4.

    Lớp 1 signals and Lớp 2 rule findings are reported. Lớp 3 pseudonymizes or masks PII, so
    action is "mask" when PII text was replaced, otherwise "allow". Policy and audit come later.
    """

    def __init__(self, config: GuardConfig | None = None) -> None:
        from .pii.vault import PiiVault

        self.config = config if config is not None else GuardConfig()
        self.vault = PiiVault(ttl_seconds=self.config.pii.vault_ttl_minutes * 60)

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

    def _check(self, text: str, station: str, ctx: GuardContext) -> Decision:
        from .detectors.rules import rule_reasons, run_rules
        from .pii import policy
        from .pii.recognizers import detect_pii

        started = perf_counter()
        normalized = self._normalize(text)
        findings = [*normalized.signals, *run_rules(normalized, station)]
        output_text, action = normalized.clean, "allow"
        if self.config.pii.enabled:
            apply = {"input": policy.apply_input, "context": policy.apply_context,
                     "output": policy.apply_output}[station]
            result = apply(normalized.clean, detect_pii(normalized), ctx, self.vault)
            findings.extend(result.findings)
            output_text = result.text
            action = "mask" if result.changed else "allow"
        reasons = {**_REASONS, **rule_reasons()}
        # PII presence is handled by masking, not by risk; only injection-like signals raise risk.
        risky = [f for f in findings if f.kind != "pii" or f.detector == "pii:unknown_placeholder"]
        risk = max((f.severity for f in risky), key=_RISK_ORDER.__getitem__, default="low")
        decision = Decision(
            decision_id=uuid4().hex,
            action=action,
            text=output_text,
            risk=risk,
            findings=findings,
            reasons=[self._reason(finding.detector, reasons) for finding in findings],
            latency_ms=0.0,
        )
        decision.latency_ms = (perf_counter() - started) * 1000
        return decision

    @staticmethod
    def _reason(detector: str, reasons: dict[str, str]) -> str:
        if detector in reasons:
            return reasons[detector]
        if detector.startswith("pii:"):
            return f"Phát hiện {_PII_NAMES.get(detector[4:], 'thông tin cá nhân')}; đã che hoặc giả danh hoá."
        return f"Phát hiện tín hiệu bất thường: {detector}."

    def check_input(self, text: str, ctx: GuardContext) -> Decision:
        """Customer input: normalize, rules, pseudonymize PII before the LLM.

        The station comes from the method, never from ctx.station, so a mislabeled context
        cannot switch off context-only rules.
        """
        return self._check(text, "input", ctx)

    def check_context(self, text: str, ctx: GuardContext) -> Decision:
        """Untrusted tool data: normalize, rules, PII per source/intent (B5.2 table)."""
        return self._check(text, "context", ctx)

    def check_output(self, text: str, ctx: GuardContext) -> Decision:
        """Generated answer: normalize, rules, mask raw PII, restore placeholders for their owner."""
        return self._check(text, "output", ctx)

    def restore(self, text: str, ctx: GuardContext) -> str:
        """Replace placeholders only (no detection): owner's phone/email/address back, rest masked."""
        from .pii.policy import restore_placeholders

        return restore_placeholders(text, ctx, self.vault).text

    def redact_for_log(self, text: str, ctx: GuardContext) -> str:
        """Irreversible redaction for guard_log: never restores, never returns a placeholder value."""
        from .pii.policy import redact_text
        from .pii.recognizers import detect_pii

        normalized = self._normalize(text)
        return redact_text(normalized.clean, detect_pii(normalized))
