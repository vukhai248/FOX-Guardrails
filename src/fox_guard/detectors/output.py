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
    r"giay to tuy than|ma otp|otp|ma xac (?:thuc|nhan|minh)|mat khau|"
    r"ma pin|so pin(?! (?:sac|du phong|lithium))|pin code|pin number|so the|ma cvv|cvv|cvc|"
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
# Clause boundaries for negation scope. Views have no diacritics, so "mà"/"mã", "còn"/"con" and
# "nhưng"/"những" collide: only unambiguous conjunctions count, and "nhung" only when a subject or a
# request follows it ("…không cần địa chỉ nhưng bạn hãy gửi OTP", review B3).
_CLAUSE_END = regex.compile(
    r"[,.;!?\n]|\b(?:tuy nhien|nhung ma|but|however|yet|though)\b"
    r"|\bnhung(?=\s+(?:ban|anh|chi|em|minh|quy khach|khach|shop|hay|vui long|lan nay|bay gio|gio)\b)")
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
# TLDs for bare domains (no scheme). An explicit list: a blanket "2+ letters" rule would turn Vietnamese
# abbreviations such as TP.HCM / TP.HN, or "Node.js", "ASP.NET", "file.pdf" into links.
_TLDS = sorted("""
com net org info biz name pro mobi asia tel xyz top site online store shop app dev ai io co me tv cc gg
ly so to sh ws pw la link click live life world today news blog cloud tech space fun vip win bid loan
review work party date trade racing download stream cam rest icu buzz monster lat cyou sbs cfd quest
bond homes email group center best men page website digital agency global media network zone club
example invalid test ru cn tk ml ga cf gq vn us uk de fr jp kr sg th id ph my au ca in br es it nl eu
""".split(), key=len, reverse=True)
_IMAGE = regex.compile(r"!\[[^\]\n]{0,200}\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
_INLINE = regex.compile(r"\[([^\]\n]{0,200})\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
_REFDEF = regex.compile(r"(?m)^[ \t]*\[[^\]\n]{1,80}\]:[ \t]*<?(\S+?)>?(?:[ \t]+[\"'(].*)?$")
_BARE = regex.compile(
    # A placeholder (<PHONE_1>) inside a URL belongs to the URL: it is restored into a real value later.
    r"(?<![\w@/.-])(?:(?:https?|ftp)://|www\.)(?:[^\s<>()\[\]\"']|<[A-Z_]+_\d{1,4}>)+"
    r"|(?<![\w@/.-])(?:[\p{L}\p{N}-]+\.)+(?:" + "|".join(_TLDS) + r")"
    r"(?:/(?:[^\s<>()\[\]\"']|<[A-Z_]+_\d{1,4}>)*)?(?![\w-])",
    regex.IGNORECASE,
)
_SPACED_DOT = regex.compile(r"(?<=[\p{L}\p{N}])\s*(?:\.|\[\.\]|\(\.\)|\s+dot\s+|\s+cham\s+)\s*"
                            r"(?=(?:com|vn|net|org|example)\b)", regex.IGNORECASE)
REMOVED_LINK = "[liên kết ngoài đã bị gỡ]"


MALFORMED = "\x00malformed"


def _absolute(url: str) -> str:
    if "://" in url:
        return url
    return "http:" + url if url.startswith("//") else "http://" + url


def host_of(url: str) -> str:
    target = _absolute(url)
    try:
        host = (urlsplit(target).hostname or "").rstrip(".").lower()
    except ValueError:
        return MALFORMED
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
    """PII or one of our placeholders anywhere after the host (path, query, fragment)."""
    from fox_guard.pii.recognizers import detect_pii
    from fox_guard.pii.vault import PLACEHOLDER

    try:
        parts = urlsplit(_absolute(url))
    except ValueError:
        return False
    tail = unquote(" ".join((parts.path, parts.query, parts.fragment)).replace("+", " "))
    if PLACEHOLDER.search(tail):
        return True  # restored later into the real value: treat as PII now
    text = regex.sub(r"[&=/?#]", " ", tail).strip()
    return bool(text) and bool(detect_pii(normalize(text, decode_max_depth=0)))


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
        if host == MALFORMED:
            findings.append(Finding(detector="link:external", kind="link", severity="medium",
                                    evidence="malformed URL removed", technique="T2.12"))
            return False
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
