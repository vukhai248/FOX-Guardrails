"""Deterministic, combinatorial link corpus for S1 (render oracle) and S2 (URL parser vs WHATWG).

Each dimension is small; the corpus is their product, so a run is reproducible and covers every
combination instead of the one input a reviewer happened to try.
"""

from itertools import product

BS = "\\"

# How the "scheme + slashes" part is written. Includes every form a review round found.
PREFIXES = [
    "https://", "http://", "HTTPS://", "https:", "https:/", "https:///", "https:" + BS * 2, "https:/" + BS,
    "//", BS * 2, "/" + BS, "", "www.", "ht\ttps://",
    # encoded slashes / colon
    "https&colon;//", "&#47;&#47;", "&sol;&sol;", "https:%2F%2F", "/&#47;", "&#x2F;&#x2F;",
]
HOSTS = [
    "evil.example", "shop.example", "www.shop.example", "shop.example@evil.example", "alice:pw1@shop.example",
    "ѕhop.example", "straße.example", "evil%2Eexample", "203.0.113.5", "shop.example.evil.example",
    "evil.example:443", "EVIL.EXAMPLE", "evil.example.",
]
PATHS = ["/p", "", "/a(b)", "/x?e=alice%40mail.example", "/x?p=0912345678", "/sp/iphone-15", "?q=iphone+15"]


def url_variants():
    for prefix, host, path in product(PREFIXES, HOSTS, PATHS):
        yield prefix + host + path


FORMS = {
    "inline": "Xem [ở đây]({u}) nhé",
    "image": "Ảnh ![sp]({u}) đây",
    "angle": "Xem [ở đây](<{u}>) nhé",
    "title": 'Xem [ở đây]({u} "tiêu đề") nhé',
    "refdef": "[x]: {u}\n\nXem [ở đây][x] và ![ảnh][x]",
    "refdef_multiline": "[x]:\n  {u}\n\nXem [ở đây][x] và ![ảnh][x]",
    "bare": "Xem {u} nhé",
    "bare_comma": "Link: {u}, rất tiện",
    "autolink": "Xem <{u}> nhé",
    "paren": "(xem {u})",
}


def link_cases():
    """(form, url, text) for every form × url."""
    for url in url_variants():
        for form, template in FORMS.items():
            yield form, url, template.format(u=url)


def is_benign(url: str) -> bool:
    """URLs an answer should be allowed to keep: plain https/relative links to the shop."""
    for prefix in ("https://shop.example", "https://www.shop.example", "http://shop.example"):
        if url.startswith(prefix) and url[len(prefix):][:1] in ("", "/", "?"):
            return "@" not in url and "%" not in url and "(" not in url and "0912345678" not in url
    return False
