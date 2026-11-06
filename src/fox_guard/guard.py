"""SDK entry points: Lớp 1 chuẩn hoá, Lớp 2 luật, Lớp 3 PII, Lớp 4 đầu ra + policy + audit."""

import re
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING
from uuid import uuid4

import regex

from .config import GuardConfig, load_config
from .types import Decision, GuardContext

if TYPE_CHECKING:
    from .normalize.views import NormalizedText

_FALLBACK = re.compile(
    r"(?:\d[\s.\-]?){3,}\d"                      # any run of 4+ digits (OTP, PIN, phone, card…)
    r"|[\w.+-]+@[\w-]+(?:\.[\w-]+)+"                 # emails
    # labelled secrets: "mật khẩu: …", "OTP 5724", "pass is …"
    r"|(?i:(?:m[aậ]t\s*kh[aẩ]u|\bmk\b|pass(?:word)?|pwd|otp|pin)\s*(?:l[aà]|:|=|is)?\s*)\S+")
# With or without a scheme ("shop.example/x?otp=…", review round 4). Over-matching only shortens
# what audit keeps, so a generic 2+ letter TLD is fine here (unlike the link guard).
_URL_TAIL = regex.compile(
    r"((?:(?:https?|ftp):)?//[^\s/?#<>\"']+|(?<![\w@.-])(?:[\p{L}\p{N}-]+\.)+\p{L}{2,}(?::\d+)?)"
    r"(?:[/?#][^\s<>\"']*)?", regex.IGNORECASE)
_PERCENT_RUN = re.compile(r"(?:%[0-9A-Fa-f]{2})+")


def _fallback_mask(text: str) -> str:
    """Used only when the PII engine fails: hide digit runs, emails and labelled secrets."""
    return _FALLBACK.sub("[đã che]", text)


def _strip_url_tails(text: str) -> str:
    """Audit keeps a URL's host only: paths/queries can hide encoded PII (%35%37…, review B2)."""
    def keep_host(m):
        return m.group(0) if m.group(0) == m.group(1) else m.group(1) + "/[đã lược]"

    # Any %XX left outside a URL can still decode to a secret: audit never needs it.
    return _PERCENT_RUN.sub("[đã lược]", _URL_TAIL.sub(keep_host, text))

_REASONS = {
    "unicode:tags": "Phát hiện ký tự Unicode Tags ẩn chứa nội dung.",
    "unicode:invisible": "Phát hiện ký tự Unicode vô hình bất thường.",
    "unicode:mixed_script": "Phát hiện một từ trộn nhiều hệ chữ dễ gây nhầm lẫn.",
    "unicode:encoded": "Phát hiện nội dung được giấu bằng mã hoá.",
    "unicode:oversize": "Văn bản quá dài; chỉ kiểm tra phần trong giới hạn cấu hình.",
    "oversize": "Văn bản quá dài; chỉ kiểm tra phần trong giới hạn cấu hình.",
    "pii:unknown_placeholder": "Câu trả lời chứa mã giả danh PII không do guard cấp (bot bịa hoặc bị dụ).",
    "solicitation": "Câu trả lời yêu cầu khách cung cấp thông tin nhạy cảm (CCCD, OTP, mật khẩu, thẻ…).",
    "link:external": "Câu trả lời chứa liên kết/ảnh ngoài danh sách cho phép; đã gỡ.",
    "link:lookalike": "Câu trả lời chứa tên miền giả dạng tên miền của shop.",
    "link:exfil": "Câu trả lời chứa liên kết mang thông tin cá nhân ra ngoài.",
}
_PII_NAMES = {
    "VN_PHONE": "số điện thoại", "EMAIL": "email", "VN_CCCD": "số CCCD", "VN_CMND": "số CMND",
    "CREDIT_CARD": "số thẻ", "VN_BANK_ACCOUNT": "số tài khoản", "VN_TAX_ID": "mã số thuế",
    "VN_PASSPORT": "số hộ chiếu", "VN_LICENSE_PLATE": "biển số xe", "VN_HEALTH_INSURANCE": "số thẻ BHYT",
    "OTP": "mã OTP", "PASSWORD": "mật khẩu", "PERSON": "họ tên", "VN_ADDRESS": "địa chỉ",
}


class Guard:
    """Three-station SDK.

    Lớp 1–2 report signals and rule findings, Lớp 3 pseudonymizes or masks PII, Lớp 4 adds the output
    detectors, turns findings into allow / mask / block / review and writes a redacted audit row.
    """

    def __init__(self, config: GuardConfig | None = None) -> None:
        from .pii.vault import PiiVault

        self.config = config if config is not None else GuardConfig()
        self.vault = PiiVault(ttl_seconds=self.config.pii.vault_ttl_minutes * 60)
        self.audit = None
        if self.config.audit.enabled:
            from .audit.store import AuditStore

            self.audit = AuditStore.from_env(self.config.audit.sqlite_path, self.config.audit.salt_env)

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
        from .detectors.output import find_solicitation, guard_links
        from .detectors.rules import rule_reasons, run_rules
        from .pii import policy as pii_policy
        from .pii.recognizers import detect_pii
        from .policy.engine import PolicyTexts, decide

        started = perf_counter()
        degraded = False
        output_failed = False
        normalized = self._normalize(text)
        findings = list(normalized.signals)
        try:
            findings.extend(run_rules(normalized, station))
        except Exception:  # B6.6: a failing detector degrades, it never blocks everything
            degraded = True
        working, link_edited = normalized.clean, False
        if station == "output":
            try:
                findings.extend(find_solicitation(normalized))
                # Links are judged on the unmasked text: masking first would hide PII in a query string.
                links = guard_links(working, self.config.links.allowlist)
                findings.extend(links.findings)
                link_edited = links.text != working
                working = links.text
            except Exception:
                degraded = True
                output_failed = True
        pii_changed = False
        if self.config.pii.enabled:
            try:
                target = self._normalize(working) if working != normalized.clean else normalized
                apply = {"input": pii_policy.apply_input, "context": pii_policy.apply_context,
                         "output": pii_policy.apply_output}[station]
                result = apply(target.clean, detect_pii(target), ctx, self.vault)
                findings.extend(result.findings)
                pii_changed, working = result.changed, result.text
            except Exception:
                # Fail safe for privacy: crude masking rather than sending raw numbers to the LLM.
                degraded = True
                masked = _fallback_mask(working)
                pii_changed, working = masked != working, masked
        cfg = self.config.policy
        verdict = decide(station, findings, working, pii_changed, link_edited,
                         PolicyTexts(cfg.refusal_text, cfg.context_hidden_text, cfg.output_safe_text,
                                     cfg.solicitation_text))
        if output_failed:
            # Unchecked links/solicitation must never reach the customer.
            verdict.action, verdict.text = "block", cfg.output_safe_text
        reasons = {**_REASONS, **rule_reasons()}
        try:
            from .pii.policy import safe_evidence

            findings = [f.model_copy(update={"evidence": safe_evidence(f.evidence)}) for f in findings]
        except Exception:
            degraded = True
            findings = [f.model_copy(update={"evidence": _fallback_mask(f.evidence)}) for f in findings]
        decision = Decision(
            decision_id=uuid4().hex,
            action=verdict.action,
            text=verdict.text,
            risk=verdict.risk,
            findings=findings,
            reasons=[self._reason(finding.detector, reasons) for finding in findings]
            + (["Một bộ kiểm bị lỗi; đã chạy chế độ giảm cấp."] if degraded else []),
            latency_ms=0.0,
            degraded=degraded,
            flags=verdict.flags,
        )
        decision.latency_ms = (perf_counter() - started) * 1000
        if self.audit is not None:
            self._audit(decision, ctx, station, normalized)
        return decision

    def _audit(self, decision: Decision, ctx: GuardContext, station: str, normalized) -> None:
        from .pii.policy import redact_text
        from .pii.recognizers import detect_pii

        try:
            redacted = _strip_url_tails(redact_text(normalized.clean, detect_pii(normalized)))
        except Exception:
            # Without a working PII engine the text cannot be proven clean: store nothing (review B4).
            redacted = "[không lưu: lỗi khi che PII]"
        self.audit.record(decision=decision, ctx=ctx, station=station, text_redacted=redacted,
                          config_version=self.config.config_version)

    @property
    def harden_prompt_text(self) -> str:
        """System reminder the app adds when a Decision carries the `harden_prompt` flag."""
        return self.config.policy.harden_prompt_text

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
