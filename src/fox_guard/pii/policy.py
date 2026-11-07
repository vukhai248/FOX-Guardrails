"""Lớp 3 station policy for PII (plan B5.2): pseudonymize before the LLM, mask/restore on output."""

import bisect
import html
from dataclasses import dataclass, field

import regex

from fox_guard.types import Finding, GuardContext

from .recognizers import ENTITY_SEVERITY, PiiMatch
from .vault import ENTITY_OF_TAG, PLACEHOLDER, TAGS, PiiVault

# Output may restore only these, and only for their owner. IDs, cards, accounts are always masked.
RESTORABLE = frozenset({"VN_PHONE", "EMAIL", "VN_ADDRESS"})
SECRET = frozenset({"OTP", "PASSWORD"})
# Context intents that legitimately need the customer's contact details in clear (partially masked).
CONTACT_INTENTS = frozenset({"address_change", "delivery_contact"})
# Context sources that carry the requesting customer's own data (their order, their ticket).
OWN_SOURCES = frozenset({"order_note", "ticket_note", "tool:order_lookup", "tool:create_support_ticket"})


def mask_value(entity: str, value: str) -> str:
    """Irreversible display/log mask. Same output for every call: safe for audit."""
    digits = regex.sub(r"\D", "", value)
    if entity in SECRET:
        return "[đã xoá]"
    if entity == "CREDIT_CARD":
        return "[số thẻ đã che]"
    if entity == "VN_BANK_ACCOUNT":
        return "[số tài khoản đã che]"
    if entity == "VN_PHONE" and len(digits) >= 7:
        return digits[:4] + "*" * (len(digits) - 7) + digits[-3:]
    if entity in ("VN_CCCD", "VN_CMND") and len(digits) >= 6:
        return digits[:4] + "*" * (len(digits) - 6) + digits[-2:]
    if entity in ("VN_PASSPORT", "VN_HEALTH_INSURANCE", "VN_TAX_ID"):
        compact = regex.sub(r"[^0-9A-Za-z]", "", value)
        return compact[:3] + "*" * max(len(compact) - 5, 1) + compact[-2:]
    if entity == "EMAIL" and "@" in value:
        local, domain = value.split("@", 1)
        return local[:1] + "***@" + domain
    if entity == "VN_LICENSE_PLATE":
        return value[:3] + "***"
    return {"PERSON": "[tên]", "VN_ADDRESS": "[địa chỉ]"}.get(entity, "[đã che]")


_PROVINCES = frozenset(
    "an giang|ba ria vung tau|bac giang|bac kan|bac lieu|bac ninh|ben tre|binh dinh|binh duong|binh phuoc|"
    "binh thuan|ca mau|can tho|cao bang|da nang|dak lak|dak nong|dien bien|dong nai|dong thap|gia lai|"
    "ha giang|ha nam|ha noi|ha tinh|hai duong|hai phong|hau giang|hoa binh|hung yen|khanh hoa|kien giang|"
    "kon tum|lai chau|lam dong|lang son|lao cai|long an|nam dinh|nghe an|ninh binh|ninh thuan|phu tho|"
    "phu yen|quang binh|quang nam|quang ngai|quang ninh|quang tri|soc trang|son la|tay ninh|thai binh|"
    "thai nguyen|thanh hoa|thua thien hue|hue|tien giang|tra vinh|tuyen quang|vinh long|vinh phuc|yen bai|"
    "ho chi minh|hcm|sai gon".split("|"))


def _province_key(part: str) -> str:
    from .recognizers import no_diacritics

    key = no_diacritics(part).lower().replace("đ", "d").strip(" .")
    return regex.sub(r"^(?:thanh pho|tp\.?|tinh)\s*", "", key).strip()


def province_only(address: str) -> str:
    """Keep only a component that is a known province/city ('…, Hà Nội, căn hộ 07A' → 'Hà Nội').

    Nothing verified → the whole address is masked, never a random last fragment (review A7)."""
    for part in reversed([p.strip() for p in address.split(",") if p.strip()]):
        if _province_key(part) in _PROVINCES:
            return part
    return "[địa chỉ]"


@dataclass
class PiiResult:
    text: str
    findings: list[Finding] = field(default_factory=list)
    changed: bool = False


def _finding(match: PiiMatch, detector: str | None = None, severity: str | None = None) -> Finding:
    return Finding(detector=detector or f"pii:{match.entity}", kind="pii",
                   severity=severity or ENTITY_SEVERITY[match.entity], span=(match.start, match.end),
                   evidence=mask_value(match.entity, match.value)[:120], technique=None)


def _rewrite(text: str, matches: list[PiiMatch], replace) -> str:
    out, cursor = [], 0
    for m in matches:
        out.append(text[cursor:m.start])
        out.append(replace(m))
        cursor = m.end
    out.append(text[cursor:])
    return "".join(out)


def apply_input(clean: str, matches: list[PiiMatch], ctx: GuardContext, vault: PiiVault) -> PiiResult:
    """Everything the customer typed is pseudonymized before the LLM, except names (for greeting)."""
    hidden = [m for m in matches if m.entity != "PERSON"]
    text = _rewrite(clean, hidden,
                    lambda m: vault.placeholder(ctx.session_id, ctx.user_ref, m.entity, m.value))
    return PiiResult(text, [_finding(m) for m in matches], bool(hidden))


def apply_context(clean: str, matches: list[PiiMatch], ctx: GuardContext, vault: PiiVault) -> PiiResult:
    own = ctx.source in OWN_SOURCES
    owner = ctx.user_ref if own else None

    def replace(m: PiiMatch) -> str:
        if m.entity == "PERSON":
            return mask_value("PERSON", m.value) if ctx.source == "review" else m.value
        if m.entity == "VN_ADDRESS":
            if own and ctx.intent == "address_change":
                return m.value
            if own and ctx.intent == "order_status":
                return province_only(m.value)
        if m.entity in ("VN_PHONE", "EMAIL") and own and ctx.intent in CONTACT_INTENTS:
            return mask_value(m.entity, m.value)
        return vault.placeholder(ctx.session_id, owner, m.entity, m.value)

    text = _rewrite(clean, matches, replace)
    return PiiResult(text, [_finding(m) for m in matches], text != clean)


def restore_placeholders(text: str, ctx: GuardContext, vault: PiiVault) -> PiiResult:
    """Placeholders → real value only for the owner and only for RESTORABLE entities; else masked."""
    findings: list[Finding] = []

    def replace(match) -> str:
        entry = vault.lookup(ctx.session_id, match.group())
        if entry is None:
            # The model invented or was fed a placeholder we never issued: suspicious, keep it visible.
            findings.append(Finding(detector="pii:unknown_placeholder", kind="pii", severity="medium",
                                    span=match.span(), evidence=match.group()[:120]))
            return match.group()
        if entry.entity in RESTORABLE and entry.owner is not None and entry.owner == ctx.user_ref:
            # A phone typed as "0 9 1 2 . 3 4 5 …" comes back in its plain form; spelled-out numbers
            # ("không chín một …") stay as written.
            plain = regex.sub(r"[\s.\-]", "", entry.value)
            return plain if entry.entity == "VN_PHONE" and plain.isdigit() else entry.value
        return mask_value(entry.entity, entry.value)

    restored = PLACEHOLDER.sub(replace, text)
    return PiiResult(restored, findings, restored != text)


def apply_output(clean: str, matches: list[PiiMatch], ctx: GuardContext, vault: PiiVault) -> PiiResult:
    """Raw PII printed by the bot is masked unless it is the requester's own contact value."""

    def replace(m: PiiMatch) -> str:
        if m.entity == "PERSON":
            return m.value
        if m.entity in RESTORABLE and ctx.user_ref is not None and \
                vault.owner_of_value(ctx.session_id, m.entity, m.value) == ctx.user_ref:
            return m.value
        return mask_value(m.entity, m.value)

    raw_pass = _rewrite(clean, matches, replace)
    restored = restore_placeholders(raw_pass, ctx, vault)
    findings = [_finding(m) for m in matches] + restored.findings
    return PiiResult(restored.text, findings, restored.text != clean)


def redact_text(clean: str, matches: list[PiiMatch]) -> str:
    """Irreversible redaction for logs: every PII value masked, every placeholder reduced to its tag."""
    text = _rewrite(clean, matches, lambda m: mask_value(m.entity, m.value))
    return PLACEHOLDER.sub(lambda m: f"[{m.group(1)}]", text)


# Tokens are split with \S+ first and then tested: "\S*(?:…)\S*" backtracked quadratically on one long
# token without spaces ("9," * 10000 took 7.5 s, check S7).
_TOKEN = regex.compile(r"\S+")
_ENCODED_MARK = regex.compile(r"%[0-9A-Fa-f]{2}|&#?[A-Za-z0-9]+;|\\[uU][0-9A-Fa-f]{4}")


def mask_encoded_pii(text: str) -> tuple[str, int]:
    """Mask encoded pieces that hide PII: "OTP: &#53;&#55;…", "alice%40mail.example", base64 of a phone.

    The LLM reads such encodings, and the customer's browser decodes HTML entities, so the normal
    PII pass (which sees only the encoded form) is not enough (systematic check S6, 07/11/2026).
    Each piece is decoded IN PLACE and the whole sentence re-scanned, so a label before it ("OTP:")
    still counts. Returns (text, number of pieces masked).
    """
    from fox_guard.detectors.url import unquote_all
    from fox_guard.normalize import normalize
    from fox_guard.normalize.decode import _unescape, decoded_spans

    from .recognizers import detect_pii

    pieces = [(s, e, d) for s, e, d in decoded_spans(text, min_len=4)]
    for m in _TOKEN.finditer(text):
        if not _ENCODED_MARK.search(m.group()):
            continue
        decoded = _unescape(unquote_all(html.unescape(m.group())))
        if decoded != m.group():
            pieces.append((m.start(), m.end(), decoded))
    if not pieces:
        return text, 0
    # Non-overlapping pieces, widest first at each position (a whole URL token beats a %XX run in it).
    chosen, last_end = [], -1
    for start, end, decoded in sorted(pieces, key=lambda p: (p[0], p[0] - p[1])):
        if start >= last_end:
            chosen.append((start, end, decoded))
            last_end = end
    # Decode every piece in place in ONE candidate sentence and scan it ONCE. Re-scanning the whole
    # text per piece was quadratic: 5,000 "%41" tokens took over ten minutes (final review, PR #4).
    parts, regions, cursor, offset = [], [], 0, 0
    for start, end, decoded in chosen:
        parts.append(text[cursor:start])
        offset += start - cursor
        regions.append((offset, offset + len(decoded), start, end, regex.sub(r"[\s.\-]", "", decoded)))
        parts.append(decoded)
        offset += len(decoded)
        cursor = end
    parts.append(text[cursor:])
    candidate = "".join(parts)
    normalized = normalize(candidate, decode_max_depth=0)
    aligned = normalized.clean == candidate
    starts = [r[0] for r in regions]
    hidden = set()
    for match in detect_pii(normalized):
        value = regex.sub(r"[\s.\-]", "", match.value)
        if aligned:  # regions overlapping the match, found by bisection
            first = max(bisect.bisect_right(starts, match.start) - 1, 0)
            candidates = range(first, bisect.bisect_left(starts, match.end))
        else:        # positions shifted: fall back to the value itself (still linear per match)
            candidates = range(len(regions))
        for index in candidates:
            r_start, r_end, start, end, squashed = regions[index]
            inside = aligned and match.start < r_end and match.end > r_start
            if (inside or (value and value in squashed)) and match.value not in text[start:end]:
                hidden.add(index)
    if not hidden:
        return text, 0
    out, cursor = [], 0
    for index in sorted(hidden):
        _, _, start, end, _ = regions[index]
        out.append(text[cursor:start] + "[đã che]")
        cursor = end
    return "".join(out) + text[cursor:], len(hidden)


def safe_evidence(evidence: str) -> str:
    """Evidence leaves the guard (Decision, audit, CLI): mask every PII value found in it.

    Applied to all findings in one place, so no detector can leak user text through evidence
    (review findings R2 email in a rule match, R5 phone inside a URL host)."""
    from fox_guard.normalize import normalize

    from .recognizers import detect_pii

    normalized = normalize(evidence, decode_max_depth=0)
    masked = redact_text(normalized.clean, detect_pii(normalized))
    # Belt and braces: evidence never needs a number. 3+ digits covers OTPs that no detector can
    # label, e.g. a host "572431.shop.example" quoted by the link guard (systematic run 1, S3).
    # Digits next to "*" belong to an already masked value ("0912***678") and stay readable.
    return regex.sub(r"(?<![\d*])\d(?:[\s.\-]?\d){2,}(?![\d*])", "[đã che]", masked)[:120]


__all__ = ["RESTORABLE", "PiiResult", "apply_context", "apply_input", "apply_output", "mask_value",
           "province_only", "redact_text", "restore_placeholders", "ENTITY_OF_TAG", "TAGS"]
