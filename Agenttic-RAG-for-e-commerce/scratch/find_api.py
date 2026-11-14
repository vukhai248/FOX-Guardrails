# -*- coding: utf-8 -*-
"""Find CellphoneS list/pagination API from HTML/JS."""
import re
from pathlib import Path

ROOT = Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch")
html = (ROOT / "sample_list.html").read_text(encoding="utf-8", errors="ignore")

patterns = [
    r"https?://[a-zA-Z0-9._/-]*api[a-zA-Z0-9._/?=&%-]*",
    r"[\"'](/api/[^\"']+)[\"']",
    r"[\"'](https?://[^\"']*graphql[^\"']*)[\"']",
    r"filterUrl[\"']?\s*[:=]\s*[\"']([^\"']+)",
    r"baseURL[\"']?\s*[:=]\s*[\"']([^\"']+)",
    r"endpoint[\"']?\s*[:=]\s*[\"']([^\"']+)",
    r"loadMore[^\n]{0,120}",
    r"showMore[^\n]{0,120}",
    r"pageSize[^\n]{0,80}",
    r"current_page[^\n]{0,80}",
    r"products\?[^\s\"']{0,100}",
    r"catalog/category[^\s\"']{0,80}",
    r"rest/V1[^\s\"']{0,100}",
    r"api-gateway[^\s\"']{0,100}",
    r"cdn-api[^\s\"']{0,100}",
    r"cellphones\.com\.vn/[a-zA-Z0-9_/-]*filter[a-zA-Z0-9_/-]*",
]

found = set()
for pat in patterns:
    for m in re.finditer(pat, html, re.I):
        s = m.group(0) if m.lastindex is None else (m.group(1) if m.lastindex >= 1 else m.group(0))
        if len(s) > 8 and "static-product" not in s and ".css" not in s and ".js" not in s:
            found.add(s[:200])

print("=== API-like strings ===")
for s in sorted(found)[:80]:
    print(s)

# Look near button__show-more-product
idx = html.find("button__show-more-product")
if idx >= 0:
    print("\n=== context around show-more ===")
    print(html[max(0, idx - 200) : idx + 400])

# category id
for pat in [r"category_id[\"']?\s*[:=]\s*[\"']?(\d+)", r"categoryId[\"']?\s*[:=]\s*[\"']?(\d+)", r"cate_id[\"']?\s*[:=]\s*[\"']?(\d+)"]:
    ms = re.findall(pat, html)
    if ms:
        print("IDs", pat, set(ms))

# __NUXT__ product list payload snippet
m = re.search(r"window\.__NUXT__\s*=", html)
if m:
    chunk = html[m.start() : m.start() + 5000]
    print("\n=== NUXT start ===")
    print(chunk[:2000])
