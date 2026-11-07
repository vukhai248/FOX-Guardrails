"""SDK entry points: Lớp 1 chuẩn hoá, Lớp 2 luật, Lớp 3 PII, Lớp 4 đầu ra + policy + audit."""

import re
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING
from uuid import uuid4

import regex

from .config import GuardConfig, load_config
from .types import Decision, Finding, GuardContext

if TYPE_CHECKING:
    from .normalize.views import NormalizedText

_FALLBACK = re.compile(
    r"(?:\d[\s.\-]?){3,}\d"                      # any run of 4+ digits (OTP, PIN, phone, card…)
    r"|[\w.+-]+@[\w-]+(?:\.[\w-]+)+"                 # emails
    # labelled secrets: "mật khẩu: …", "OTP 5724", "pass is …"
    r"|(?i:(?:m[aậ]t\s*kh[aẩ]u|\bmk\b|pass(?:word)?|pwd|otp|pin)\s*(?:l[aà]|:|=|is)?\s*)\S+")
# With or without a scheme ("shop.example/x?otp=…", review round 4). Over-matching only shortens
# what audit keeps, so a generic 2+ letter TLD is fine here (unlike the link guard).
# Userinfo ("alice:pass@host") is matched as part of the URL so it is never kept (review round 5).
_URL_TAIL = regex.compile(
    r"(?:(?:[a-z][a-z0-9+.-]*:)?[/\\]{2,}|(?:https?|ftp):[/\\]*)[^\s<>\"']+"
    r"|(?<![\w@.:-])(?:[^\s/@<>\"':]+:[^\s/@<>\"']+@)?(?:[\p{L}\p{N}-]+\.)+\p{L}{2,}(?::\d+)?"
    r"(?:[/?#\\][^\s<>\"']*)?", regex.IGNORECASE)


def _drop_encoded(text: str) -> str:
    """Audit keeps nothing a decoder could read back: base64/hex, entities, \\u escapes, %XX
    ("OTP: &#53;&#55;…" decodes to the OTP, review round 7)."""
    from .normalize.decode import _PERCENT_RUN, encoded_spans

    out, cursor = [], 0
    for start, end in encoded_spans(text):
        if start >= cursor:
            out.append(text[cursor:start] + "[đã lược]")
            cursor = end
    return _PERCENT_RUN.sub("[đã lược]", "".join(out) + text[cursor:])


def _fallback_mask(text: str) -> str:
    """Used only when the PII engine fails: hide digit runs, emails and labelled secrets."""
    return _FALLBACK.sub("[đã che]", text)


def _strip_url_tails(text: str) -> str:
    """Audit keeps a URL's host only: paths/queries can hide encoded PII (%35%37…, review B2)."""
    from .detectors.url import parse_url
    from .normalize.decode import _PERCENT_RUN

    def keep_host(m):
        parsed = parse_url(m.group(0))
        plain = "%" not in m.group(0) and not regex.search(r"\d{3,}", parsed.host)
        if plain and not parsed.userinfo and not parsed.rest.strip("/\\"):
            return m.group(0)                      # "https://shop.example", "TP.HCM"
        if not parsed.host or parsed.malformed:
            return "[đã lược]"
        prefix = f"{parsed.scheme}://" if parsed.scheme else ""
        # Host as the browser sees it, nothing else. Digit runs in it can be a phone that was
        # percent-encoded and only became visible by decoding the host (review round 6).
        host = regex.sub(r"\d{3,}", "***", parsed.host)
        return f"{prefix}{host}/[đã lược]"

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
    "pii:encoded": "Phát hiện thông tin cá nhân viết ở dạng mã hoá (%XX, &#…;, base64…); đã che.",
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
        if self.config.rules.enabled:
            try:
                findings.extend(run_rules(normalized, station))
            except Exception:  # B6.6: a failing detector degrades, it never blocks everything
                degraded = True
        clf = self.config.classifier
        if clf.enabled and station in clf.stations:
            try:
                findings.extend(self._classify(normalized))
            except Exception:  # missing weights or a model error: degrade, never block (B6.6)
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
                # Encoded PII first ("OTP: &#53;…", "alice%40mail…"): the LLM and the browser can
                # read it back, the normal pass below cannot see it (systematic check S6).
                working, hidden_pieces = pii_policy.mask_encoded_pii(working)
                if hidden_pieces:
                    findings.append(Finding(detector="pii:encoded", kind="pii", severity="medium",
                                            evidence=f"{hidden_pieces} đoạn mã hoá chứa PII đã che"))
                target = self._normalize(working) if working != normalized.clean else normalized
                apply = {"input": pii_policy.apply_input, "context": pii_policy.apply_context,
                         "output": pii_policy.apply_output}[station]
                result = apply(target.clean, detect_pii(target), ctx, self.vault)
                findings.extend(result.findings)
                pii_changed, working = result.changed or bool(hidden_pieces), result.text
            except Exception:
                # Fail safe for privacy: crude masking rather than sending raw numbers to the LLM.
                degraded = True
                masked = _fallback_mask(working)
                pii_changed, working = masked != working, masked
        cfg = self.config.policy
        if station == "context" and cfg.datamarking:
            from .policy.localize import looks_like_delimiter

            if looks_like_delimiter(normalized.vi_nodiac):  # data imitating our wrapper (T2.5)
                findings.append(Finding(detector="datamark:delimiter", kind="injection", severity="medium",
                                        evidence="delimiter-like text in untrusted data", technique="T2.5"))
        verdict = decide(station, findings, working, pii_changed, link_edited,
                         PolicyTexts(cfg.refusal_text, cfg.context_hidden_text, cfg.output_safe_text,
                                     cfg.solicitation_text))
        if output_failed:
            # Unchecked links/solicitation must never reach the customer.
            verdict.action, verdict.text = "block", cfg.output_safe_text
        if station == "context":
            self._localize_and_mark(verdict, working, ctx)
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

    def _sentence_is_injection(self, sentence: str) -> bool:
        """B6.3: does this piece on its own raise an injection alarm (rule, concealed text, classifier)?"""
        from .detectors.rules import run_rules

        n = self._normalize(sentence)
        found = [f for f in n.signals if f.severity == "high"]
        if self.config.rules.enabled:
            found += run_rules(n, "context")
        clf = self.config.classifier
        if clf.enabled and clf.theta_high is not None:
            from .detectors.classifier import get_classifier

            if get_classifier(clf).score(n.clean) >= clf.theta_high:
                return True
        return any(f.kind in ("injection", "unicode") and f.severity in ("medium", "high") for f in found)

    def _localize_and_mark(self, verdict, working: str, ctx: GuardContext) -> None:
        """CONTEXT: cut only the injected sentences (B6.3), then wrap what remains (B6.4)."""
        from .policy.localize import datamark, localize

        cfg = self.config.policy
        if verdict.action == "block" and cfg.localize:
            try:
                result = localize(working, self._sentence_is_injection, cfg.localized_text,
                                  cfg.localize_max_share)
            except Exception:
                result = None  # localization is an improvement, never a reason to leak: keep it hidden
            if result is not None:
                verdict.action, verdict.text = "mask", result[0]
                verdict.flags = [*verdict.flags, "localized"]
        if cfg.datamarking and verdict.action != "block":
            verdict.text = datamark(verdict.text, ctx.source)

    def _classify(self, normalized) -> list[Finding]:
        """Lớp 5: score clean text plus any hidden/decoded text; thresholds come from the dev split.

        >= theta_high → medium; [theta_low, theta_high) → low. A classifier finding alone never
        exceeds medium; the policy raises it to high only together with a rule (B6.1)."""
        from .detectors.classifier import get_classifier

        cfg = self.config.classifier
        if cfg.theta_low is None or cfg.theta_high is None:
            raise ValueError("classifier enabled without calibrated theta_low/theta_high")
        model = get_classifier(cfg)
        texts = [normalized.clean, normalized.hidden_tags, *(child.clean for child in normalized.decoded)]
        score = max(model.score(t) for t in texts if t)
        if score < cfg.theta_low:
            return []
        severity = "medium" if score >= cfg.theta_high else "low"
        return [Finding(detector=f"classifier:{model.short_name}", kind="injection", severity=severity,
                        score=round(score, 4), evidence=f"score {score:.3f}")]

    def _audit(self, decision: Decision, ctx: GuardContext, station: str, normalized) -> None:
        from .pii.policy import redact_text
        from .pii.recognizers import detect_pii

        try:
            # URLs are reduced (and their hosts decoded) first, then the PII pass runs on the result,
            # so nothing decoded later can skip masking (review round 6).
            reduced = self._normalize(_strip_url_tails(normalized.clean))
            redacted = _drop_encoded(redact_text(reduced.clean, detect_pii(reduced)))
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
