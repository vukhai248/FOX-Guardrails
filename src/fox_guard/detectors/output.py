"""Lớp 4 output detectors: the bot asking for secrets (solicitation) and links/images (link guard)."""

import html
from dataclasses import dataclass, field

import regex

from fox_guard.normalize import NormalizedText, normalize
from fox_guard.normalize.unicode import skeleton
from fox_guard.types import Finding

from .rules.engine import latin_view
from .url import parse_url, unquote_all

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
    r"[,.;!?\n]|\b(?:tuy nhien|nhung ma|thay vao do|but|however|yet|though|instead|rather)\b"
    # "mà" opens a new clause when a request follows ("đừng gửi email mà gửi OTP"); "mã" is followed
    # by what it names ("mã OTP"), never by a request verb (review round 6).
    r"|\bma(?=\s+(?:hay\s+|vui long\s+)?(?:gui|cung cap|nhap|doc|chup|nhan tin|dua|cho (?:em|minh|shop)))"
    r"|\bnhung(?=\s+(?:ban|anh|chi|em|minh|quy khach|khach|shop|hay|vui long|lan nay|bay gio|gio)\b)")
_PLACEHOLDER_VIEW = regex.compile(r"<[\p{L}_ ]+_\d{1,4}>")


# Inside the request itself: "vui lòng KHÔNG cung cấp", "please NEVER share". "dung" is đừng only
# right before a verb: in no-diacritics views it is also "đúng" ("gửi đúng mã OTP" is a request).
_NEGATION_INSIDE = regex.compile(
    r"\b(?:khong|chang|chua|never|not|dont|don't)\b"
    r"|\bdung\s+(?:bao gio\s+)?(?:gui|cung cap|nhap|doc|chia se|tiet lo|dua|cho|share|send)\b")
# An imperative opens a new request even after a negation: "Để không mất đơn bạn hãy gửi OTP".
# "hay" is both "hãy" and "hay" (= or: "OTP hay mật khẩu") without diacritics: imperative only
# when a request verb follows it.
_IMPERATIVE = regex.compile(r"(?:vui long|lam on|xin|please)\b"
                            r"|hay\s+(?:\w+\s+){0,2}?(?:gui|cung cap|nhap|doc|chup|nhan tin|share|send)\b")
# Negation of a purpose, not of the request: "để không mất đơn", "nhằm không bị khoá", "to not lose".
_PURPOSE_BEFORE = regex.compile(r"\b(?:de|nham|de cho|to|so)\s+$")
# Words that may sit between a negation and the request it negates (no-diacritics, lowercase).
_WARNING_FRAME = frozenset("""
bao gio he can phai se duoc nen the yeu cau hoi doi xin gui cung cap nhap doc nhan tin goi dien thoai
email sms qua chat zalo link de cho ban anh chi em minh quy khach hang shop ben chung toi nhan vien
cua ai bat ky va hoac hay bo phan cskh tu lam on vui long tuyet doi bao h k ko
ask asks asking asked will would ever you your to for us we our staff anyone request require
send provide share give by via phone call message messages team support do does did never not
ma otp mat khau so the cvv cvc pin cccd cmnd can cuoc cong dan tai khoan xac thuc minh ngay het han
giay to tuy than chup nhung thong nhu
password code card number id passport bank account security one time or and any
""".split())


def _negated(view: str, start: int, end: int) -> bool:
    """True when the matched request is a warning ("Shop không bao giờ yêu cầu bạn cung cấp OTP").

    Review round 4: a negation counts only when it governs the request. One inside the request
    always does. One earlier in the clause does, unless it negates a purpose ("để không …") or
    an imperative ("hãy", "vui lòng", "please") starts the request after it.
    """
    if _NEGATION_INSIDE.search(view, start, end):
        return True
    if _IMPERATIVE.match(view, start):
        return False
    # Search the whole view: an endpos would hide the lookahead after "ma"/"nhung" from the regex.
    clause_start = max((m.end() for m in _CLAUSE_END.finditer(view) if m.end() <= start), default=0)
    for neg in _NEGATION.finditer(view, clause_start, start):
        if _PURPOSE_BEFORE.search(view, clause_start, neg.start()):
            continue
        # The negation governs the request only if what lies between is the frame of a warning
        # ("không BAO GIỜ YÊU CẦU BẠN"), not another verb ("Đừng LO NHÉ bạn gửi OTP").
        between = view[neg.end():start].split()
        if len(between) <= 12 and all(word in _WARNING_FRAME for word in between):
            return True
    return False


# A lead-in ending with ":" and the list or lines under it form one request (review round 5):
# "Vui lòng gửi qua chat:\n- Mã OTP\n- Mật khẩu". Markers and line breaks become " / ", which
# neither ends the clause nor blocks _SOLICIT; a lead-in can be long, so items are pulled next to it.
_LIST_BLOCK = regex.compile(r"(?m):[ \t]*\n((?:[ \t]*(?:[-*•+>]|\d{1,2}[.)])?[ \t]*[^\n]*(?:\n|$)){1,15})")
_LIST_MARK = regex.compile(r"(?m)^[ \t]*(?:[-*•+>]|\d{1,2}[.)])?[ \t]*")
_LEAD_ASK = regex.compile(r"\b" + _ASK + r"\b")


def _join_lists(view: str) -> str:
    def join(m):
        items = [line.strip(" *_") for line in _LIST_MARK.sub("", m.group(1)).split("\n") if line.strip()]
        return ": " + " / ".join(items) + "\n"

    joined = _LIST_BLOCK.sub(join, view)
    # Long lead-ins: also place the last request verb of each lead-in right before its items.
    out = []
    for line in joined.split("\n"):
        lead, colon, items = line.partition(": ")
        asks = list(_LEAD_ASK.finditer(lead)) if colon else []
        if asks and len(lead) - asks[-1].end() > 30:
            ask = asks[-1]
            negation = "khong " if _negated(lead, ask.start(), ask.end()) else ""
            line = f"{line}\n{negation}{ask.group()}: {items}"
        out.append(line)
    return "\n".join(out)


def find_solicitation(normalized: NormalizedText) -> list[Finding]:
    """One high finding if the answer asks the customer for an ID, OTP, password, card or account.

    A request inside a negated clause is a warning, not a request. A later clause can still ask
    ("Bạn không cần lo, hãy gửi mã OTP" is caught: the comma ends the negated clause).
    """
    for view in (normalized.vi_nodiac, normalized.vi_teencode, latin_view(normalized.nfkc)):
        # Our own placeholders (<CCCD_1>) name an entity; they are not a request for it.
        view = _join_lists(_PLACEHOLDER_VIEW.sub(" ", view))
        for match in _SOLICIT.finditer(view, timeout=0.05, overlapped=True):
            if not _negated(view, match.start(), match.end()):
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
# Destination as CommonMark reads it: "<…>" or a run with balanced parentheses, so
# "(https://shop.example/a(b)?email=…)" is judged whole, not cut at "(" (review round 6).
_DEST = r"(?|<([^>\n]*)>|((?:[^()\s]|\((?:[^()\s])*\))+))(?:\s+[\"'][^\"']*[\"'])?\s*\)"
_IMAGE = regex.compile(r"!\[[^\]\n]{0,200}\]\(\s*" + _DEST)
_INLINE = regex.compile(r"\[([^\]\n]{0,200})\]\(\s*" + _DEST)
# A link to the shop stays only if every character after the host is plain: no %XX, "@", "(",
# "\" or quotes, so nothing encoded or oddly delimited can carry PII past the checks.
_SAFE_REST = regex.compile(r"^(?:/[A-Za-z0-9._~\-/]*)?(?:\?[A-Za-z0-9._~\-=&+,]*)?(?:#[A-Za-z0-9._~\-]*)?$")
# CommonMark allows the destination on the next line ("[x]:\n  //evil.example/pixel", review round 4).
_REFDEF = regex.compile(r"(?m)^[ \t]*\[[^\]\n]{1,80}\]:[ \t]*(?:\n[ \t]*)?<?(\S+?)>?(?:[ \t]+[\"'(].*)?$")
_BARE = regex.compile(
    # A placeholder (<PHONE_1>) inside a URL belongs to the URL: it is restored into a real value later.
    r"(?<![\w@/.-])(?:(?:https?|ftp)://|www\.)(?:[^\s<>()\[\]\"']|\([^\s<>()\[\]\"']*\)|<[A-Z_]+_\d{1,4}>)+"
    # Scheme-relative "//host/x" anywhere in the text: browsers resolve it against the page.
    r"|(?<![\w:/.-])//(?:[\p{L}\p{N}-]+\.)+[\p{L}\p{N}-]+(?::\d+)?"
    r"(?:[/?#](?:[^\s<>()\[\]\"']|\([^\s<>()\[\]\"']*\)|<[A-Z_]+_\d{1,4}>)*)?"
    r"|(?<![\w@/.-])(?:[\p{L}\p{N}-]+\.)+(?:" + "|".join(_TLDS) + r")"
    r"(?:/(?:[^\s<>()\[\]\"']|\([^\s<>()\[\]\"']*\)|<[A-Z_]+_\d{1,4}>)*)?(?![\w-])",
    regex.IGNORECASE,
)
_SPACED_DOT = regex.compile(r"(?<=[\p{L}\p{N}])\s*(?:\.|\[\.\]|\(\.\)|\s+dot\s+|\s+cham\s+)\s*"
                            r"(?=(?:com|vn|net|org|example)\b)", regex.IGNORECASE)
REMOVED_LINK = "[liên kết ngoài đã bị gỡ]"
_ANGLE_DEST = regex.compile(r"(\]\(\s*<|^[ \t]*\[[^\]\n]{1,80}\]:[ \t]*<)([^>\n]*)>", regex.M)


MALFORMED = "\x00malformed"


def host_of(url: str) -> str:
    """The host a browser would contact (see detectors/url.py), MALFORMED if it cannot be read."""
    parsed = parse_url(url)
    return MALFORMED if parsed.malformed else parsed.host


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
    """PII or one of our placeholders anywhere in the URL, the host included.

    A placeholder in the host ("https://<PHONE_1>.shop.example/") would be restored into the real
    number and leak it through DNS (review round 4)."""
    from fox_guard.pii.recognizers import detect_pii
    from fox_guard.pii.vault import PLACEHOLDER

    if PLACEHOLDER.search(unquote_all(html.unescape(url))):  # also "&lt;PHONE_1&gt;"
        return True  # restored later into the real value: treat as PII now
    parsed = parse_url(url)
    if parsed.userinfo:
        return True  # "user:pass@host" carries a credential to whoever the host is (review round 5)
    # Host labels split on dots ("0912345678.shop.example"). In path/query/fragment only URL
    # separators split values: "." and "@" stay, so "alice%40mail.example" is still an email.
    host_text = parsed.host.replace(".", " ")
    rest = unquote_all(parsed.rest.replace("+", " "))
    rest_text = regex.sub(r"[&=/?#;\\]", " ", rest)
    text = f"{host_text} {rest_text}".strip()
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
        parsed = parse_url(url)
        host = parsed.host
        pii = _has_pii(url)
        if parsed.malformed and not pii:
            # Includes "https:///evil.example"-style URLs whose host Python and browsers disagree on.
            findings.append(Finding(detector="link:external", kind="link", severity="medium",
                                    evidence="malformed URL removed", technique="T2.12"))
            return False
        if parsed.scheme and parsed.scheme not in ("http", "https"):
            # javascript:, data:, vbscript:, ftp:… run or embed content outside the allowlist rules.
            findings.append(Finding(detector="link:external", kind="link", severity="medium",
                                    evidence=f"{parsed.scheme}: URL removed"[:120], technique="T2.12"))
            return False
        if not host and not pii:
            return True  # same-site relative link ("/sp/1")
        # Internationalized hosts never match the ASCII allowlist: Python (IDNA2003) and browsers
        # (UTS #46) can encode them to different hosts (review round 4).
        if _allowed(host, allow) and not parsed.non_ascii and not pii:
            if _SAFE_REST.match(parsed.rest):
                return True
            findings.append(Finding(detector="link:external", kind="link", severity="medium",
                                    evidence=f"unusual URL to {host} removed"[:120], technique="T2.12"))
            return False
        if pii:
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
        # Autolinkers drop trailing punctuation ("…/sp/1, rất tiện"): judge the URL without it.
        url = m.group().rstrip(".,;:!?'\"")
        trail = m.group()[len(url):]
        return m.group() if judge(url) else REMOVED_LINK + trail

    # "evil-shop . example", "evil-shop[.]example" are written to slip past link filters.
    text = _SPACED_DOT.sub(".", text)
    # Browsers drop tab/CR inside a URL: "<ht\ttps://evil.example>" opens https://evil.example.
    # CommonMark accepts them only in an angle-bracket destination, so remove them there.
    text = _ANGLE_DEST.sub(lambda m: m.group(1) + regex.sub(r"[\t\r]", "", m.group(2)) + ">", text)
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
