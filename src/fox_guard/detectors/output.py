"""Lớp 4 output detectors: the bot asking for secrets (solicitation) and links/images (link guard)."""

from dataclasses import dataclass, field
from urllib.parse import unquote, urlsplit

import regex

from fox_guard.normalize import NormalizedText, normalize
from fox_guard.normalize.unicode import skeleton
from fox_guard.types import Finding

from .rules.engine import latin_view

# ---------------------------------------------------------------- solicitation (B5.3, P4 / O3)
# Things a shop's customer service never needs from the customer in chat. Phone, address and tax id
# are deliberately absent: they are legitimately asked for (address_change, vat_invoice).
_SECRET_ITEMS = (
    r"(?:so\s+)?(?:cccd|can cuoc(?: cong dan)?|cmnd|chung minh(?: nhan dan| thu)?|anh (?:chup )?giay to|"
    r"giay to tuy than|ma otp|otp|ma xac (?:thuc|nhan|minh)|mat khau|ma pin|\bpin\b|so the|ma cvv|cvv|cvc|"
    r"ngay het han(?: the)?|so tai khoan|ma bao mat|"
    r"one[- ]time (?:code|password)|password|card number|security code|id card|passport number|bank account)"
)
_ASK = (  # "can" = cần, but not the "căn" of "căn cước" (no-diacritics views merge the two)
    r"(?:vui long|lam on|xin|hay|can(?!\s+cuoc)|phai|bat buoc|de nghi|yeu cau|"
    r"cho (?:em|minh|shop|ben em) xin|"
    r"gui|cung cap|nhap|doc|chup|nhan tin|please|provide|send|enter|share|tell us|give us|confirm)"
)
_NEGATION = regex.compile(r"\b(?:khong|chang|dung|chua|never|not|dont|don't|no one|nobody)\b")
_SOLICIT = regex.compile(r"\b" + _ASK + r"\b[^\n.?!;]{0,50}?\b" + _SECRET_ITEMS + r"\b")
_CLAUSE_END = regex.compile(r"[,.;!?\n]")
_PLACEHOLDER_VIEW = regex.compile(r"<[\p{L}_ ]+_\d{1,4}>")


def _negated(view: str, start: int) -> bool:
    """A negation earlier in the same clause ("Shop không bao giờ yêu cầu bạn cung cấp OTP")."""
    clause_start = max((m.end() for m in _CLAUSE_END.finditer(view, 0, start)), default=0)
    return bool(_NEGATION.search(view, clause_start, start))


def find_solicitation(normalized: NormalizedText) -> list[Finding]:
    """One high finding if the answer asks the customer for an ID, OTP, password, card or account.

    A request inside a negated clause is a warning, not a request. A later clause can still ask
    ("Bạn không cần lo, hãy gửi mã OTP" is caught: the comma ends the negated clause).
    """
    for view in (normalized.vi_nodiac, normalized.vi_teencode, latin_view(normalized.nfkc)):
        # Our own placeholders (<CCCD_1>) name an entity; they are not a request for it.
        view = _PLACEHOLDER_VIEW.sub(" ", view)
        for match in _SOLICIT.finditer(view, timeout=0.05, overlapped=True):
            if not _negated(view, match.start()):
                return [Finding(detector="solicitation", kind="solicitation", severity="high",
                                evidence=regex.sub(r"\d", "*", match.group())[:120], technique="T2.4")]
    return []


# ---------------------------------------------------------------- link guard (B5.4, O1 / O5)
_IMAGE = regex.compile(r"!\[[^\]\n]{0,200}\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
_INLINE = regex.compile(r"\[([^\]\n]{0,200})\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
_REFDEF = regex.compile(r"(?m)^[ \t]*\[[^\]\n]{1,80}\]:[ \t]*<?(\S+?)>?(?:[ \t]+[\"'(].*)?$")
_BARE = regex.compile(
    r"(?<![\w@/.-])(?:(?:https?|ftp)://|www\.)[^\s<>()\[\]\"']+"
    r"|(?<![\w@/.-])(?:[\p{L}\p{N}-]+\.)+(?:com|vn|net|org|info|xyz|top|site|online|store|shop|io|co|me|"
    r"link|click|app|biz|example|ru|cn|tk)(?:/[^\s<>()\[\]\"']*)?(?![\w-])",
    regex.IGNORECASE,
)
_SPACED_DOT = regex.compile(r"(?<=[\p{L}\p{N}])\s*(?:\.|\[\.\]|\(\.\)|\s+dot\s+|\s+cham\s+)\s*"
                            r"(?=(?:com|vn|net|org|example)\b)", regex.IGNORECASE)
REMOVED_LINK = "[liên kết ngoài đã bị gỡ]"


def host_of(url: str) -> str:
    target = url if "://" in url else "http://" + url
    host = (urlsplit(target).hostname or "").rstrip(".").lower()
    try:
        return host.encode("idna").decode("ascii")
    except UnicodeError:
        return host


def _allowed(host: str, allowlist: list[str]) -> bool:
    return any(host == a or host.endswith("." + a) for a in allowlist)


def _lookalike(host: str, allowlist: list[str]) -> bool:
    try:
        shown = host.encode("ascii").decode("idna") if "xn--" in host else host
    except UnicodeError:
        shown = host
    skel = skeleton(shown).casefold()
    return any(skel == skeleton(a).casefold() and host != a for a in allowlist)


def _has_pii(url: str) -> bool:
    from fox_guard.pii.recognizers import detect_pii

    query = unquote(urlsplit(url if "://" in url else "http://" + url).query.replace("+", " "))
    return bool(query) and bool(detect_pii(normalize(query.replace("&", " ").replace("=", " "),
                                                     decode_max_depth=0)))


@dataclass
class LinkResult:
    text: str
    findings: list[Finding] = field(default_factory=list)
    exfil: bool = False


def guard_links(text: str, allowlist: list[str]) -> LinkResult:
    """Remove external images, neutralise external links, flag look-alike hosts and PII in queries."""
    allow = [host_of(a) for a in allowlist]
    findings: list[Finding] = []
    exfil = False

    def judge(url: str) -> bool:
        """True if the URL may stay; records findings otherwise."""
        nonlocal exfil
        host = host_of(url)
        if not host:
            return True
        if _allowed(host, allow) and not _has_pii(url):
            return True
        if _has_pii(url):
            exfil = True
            findings.append(Finding(detector="link:exfil", kind="link", severity="high",
                                    evidence=f"PII in query of {host}"[:120], technique="T2.12"))
        elif _lookalike(host, allow):
            findings.append(Finding(detector="link:lookalike", kind="link", severity="high",
                                    evidence=f"look-alike host {host}"[:120], technique="T3.4"))
        else:
            findings.append(Finding(detector="link:external", kind="link", severity="medium",
                                    evidence=f"external host {host}"[:120], technique="T2.12"))
        return False

    def drop_image(m):
        return m.group() if judge(m.group(1)) else ""

    def inline(m):
        return m.group() if judge(m.group(2)) else f"{m.group(1)} {REMOVED_LINK}".strip()

    def refdef(m):
        return m.group() if judge(m.group(1)) else REMOVED_LINK

    def bare(m):
        return m.group() if judge(m.group()) else REMOVED_LINK

    # "evil-shop . example", "evil-shop[.]example" are written to slip past link filters.
    text = _SPACED_DOT.sub(".", text)
    text = _IMAGE.sub(drop_image, text)
    text = _INLINE.sub(inline, text)
    text = _REFDEF.sub(refdef, text)
    protected = regex.compile(regex.escape(REMOVED_LINK))
    parts, cursor = [], 0
    for keep in protected.finditer(text):
        parts.append(_BARE.sub(bare, text[cursor:keep.start()]))
        parts.append(keep.group())
        cursor = keep.end()
    parts.append(_BARE.sub(bare, text[cursor:]))
    return LinkResult("".join(parts), findings, exfil)
