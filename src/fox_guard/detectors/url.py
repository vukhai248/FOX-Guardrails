"""Browser-like URL splitting for the link guard and the audit (review round 5).

Python's urlsplit and a browser disagree on many inputs, and every disagreement is a bypass:
"https:///evil.example" (urlsplit: empty host, browser: evil.example), "https:\\\\evil.example",
"/\\evil.example", tabs or newlines inside the scheme, "%2E" in the host, "user:pass@host".
This follows the WHATWG URL rules for http(s) closely enough that the host we judge is the host
the browser will contact. When in doubt it reports a host rather than none, so the link is judged
(and usually removed) instead of trusted.
"""

import html
from dataclasses import dataclass
from urllib.parse import unquote

import regex

SPECIAL = frozenset({"http", "https", "ftp", "ws", "wss"})
_SCHEME = regex.compile(r"^([a-zA-Z][a-zA-Z0-9+.-]*):")
_HOST_OK = regex.compile(r"^(?:[\p{L}\p{N}_-]+(?:\.[\p{L}\p{N}_-]+)*\.?|\[[0-9a-fA-F:.]+\])$")


@dataclass(frozen=True)
class ParsedUrl:
    scheme: str      # "" for scheme-less input
    userinfo: str    # "user:pass" part before "@", "" if none
    host: str        # lowercased, percent-decoded, IDNA-encoded; "" if the URL has no host
    rest: str        # path + query + fragment, raw
    malformed: bool  # a host was expected but cannot be read safely
    non_ascii: bool  # host was written with non-ASCII characters or as punycode


def unquote_all(text: str) -> str:
    """Decode %XX until stable (bounded): "%2540" hides "%40" hides "@"."""
    for _ in range(4):
        decoded = unquote(text)
        if decoded == text:
            break
        text = decoded
    return text


def parse_url(url: str) -> ParsedUrl:
    # Markdown renderers decode HTML entities in a destination: "/&sol;evil&period;example" is
    # "//evil.example" by the time the browser sees it (review round 7).
    url = html.unescape(url)
    # Browsers drop ASCII tab/newline anywhere and trim C0 controls and spaces at both ends.
    url = regex.sub(r"[\t\n\r]", "", url).strip("\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c"
                                                  "\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19"
                                                  "\x1a\x1b\x1c\x1d\x1e\x1f ")
    match = _SCHEME.match(url)
    scheme = match.group(1).lower() if match else ""
    body = url[match.end():] if match else url
    if scheme and scheme not in SPECIAL:
        return ParsedUrl(scheme, "", "", body, False, False)
    if not scheme:
        if regex.match(r"[/\\]{2}", body):
            pass                      # "//host", "\\host", "/\host": host-relative
        elif body[:1] in ("/", "\\", "?", "#", ".") or not body:
            return ParsedUrl("", "", "", body, False, False)   # same-site relative path
        # else a bare "evil.example/x" written as a link: judge it as a host
    # Special schemes: any run of "/" or "\" (even none) before the authority.
    body = body.lstrip("/\\")
    cut = regex.search(r"[/\\?#]", body)
    authority, rest = (body[:cut.start()], body[cut.start():]) if cut else (body, "")
    userinfo, _, hostport = authority.rpartition("@")
    if hostport.startswith("["):
        host = hostport[:hostport.find("]") + 1] if "]" in hostport else hostport
    else:
        host = hostport.split(":", 1)[0]
    host = unquote_all(host).lower()
    non_ascii = not host.isascii() or "xn--" in host
    if not host or not _HOST_OK.match(host):
        return ParsedUrl(scheme, userinfo, host, rest, True, non_ascii)
    host = host.rstrip(".")
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        pass
    return ParsedUrl(scheme, userinfo, host, rest, False, non_ascii)
