# -*- coding: utf-8 -*-
import re
import requests
from pathlib import Path

html = Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch\sample_list.html").read_text(
    encoding="utf-8", errors="ignore"
)
js_urls = sorted(set(re.findall(r"https://static-product\.cellphones\.com\.vn/[a-zA-Z0-9]+\.js", html)))
print("js count", len(js_urls))

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
hits = set()
patterns = [
    r"https?://[a-zA-Z0-9._:-]+(?:api|graphql|gateway)[a-zA-Z0-9._:/-]*",
    r'["\'](/api/[^"\']+)["\']',
    r'baseURL:\s*["\']([^"\']+)["\']',
    r'baseUrl:\s*["\']([^"\']+)["\']',
    r'["\'](https?://api[^"\']+)["\']',
    r'["\'](https?://[^"\']*cellphones[^"\']*api[^"\']*)["\']',
    r'filterProduct[^"\']{0,40}',
    r'getListProduct[^"\']{0,40}',
    r'productList[^"\']{0,40}',
    r'/v\d+/[a-zA-Z0-9_/-]+',
]

for url in js_urls[:25]:
    try:
        t = requests.get(url, headers=headers, timeout=25).text
    except Exception as e:
        print("fail", url, e)
        continue
    print("scanned", url, "len", len(t))
    for pat in patterns:
        for m in re.finditer(pat, t):
            s = m.group(1) if m.lastindex else m.group(0)
            if len(s) > 5:
                hits.add(s[:200])

print("\n=== HITS ===")
for h in sorted(hits):
    print(h)

# Also try known CPS API endpoints
print("\n=== probe common endpoints ===")
probes = [
    "https://api.cellphones.com.vn/v2/products?cate_id=3&limit=20&page=1",
    "https://api.cellphones.com.vn/v1/products?cateId=3&limit=20",
    "https://cellphones.com.vn/lapi/LoadMoreProductCate/index/?cate_id=3&page=1",
    "https://cellphones.com.vn/lapi/product/getList/?cateId=3",
    "https://cdn-api.cellphones.com.vn/?query=products",
]
for u in probes:
    try:
        r = requests.get(u, headers=headers, timeout=15)
        print(r.status_code, len(r.content), u[:90], r.text[:120].replace("\n", " "))
    except Exception as e:
        print("ERR", u, e)
