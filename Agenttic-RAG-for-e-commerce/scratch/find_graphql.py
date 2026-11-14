# -*- coding: utf-8 -*-
"""Extract GraphQL product-list queries from CellphoneS JS bundles."""
import re
import requests
from pathlib import Path

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://cellphones.com.vn",
    "Referer": "https://cellphones.com.vn/",
}

html = Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch\sample_list.html").read_text(
    encoding="utf-8", errors="ignore"
)
js_urls = sorted(set(re.findall(r"https://static-product\.cellphones\.com\.vn/[a-zA-Z0-9]+\.js", html)))

# Prefer larger bundles
sizes = []
for url in js_urls:
    try:
        r = requests.head(url, headers=headers, timeout=15)
        cl = int(r.headers.get("Content-Length") or 0)
    except Exception:
        cl = 0
    sizes.append((cl, url))
sizes.sort(reverse=True)

out_dir = Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch\js_cache")
out_dir.mkdir(exist_ok=True)

keywords = [
    "productListCate",
    "productsFilter",
    "filterProducts",
    "GetProducts",
    "products(",
    "categoryId",
    "cateId",
    "query Get",
    "query products",
    "productsCate",
    "listProduct",
]

collected = []
for cl, url in sizes[:8]:
    name = url.rsplit("/", 1)[-1]
    path = out_dir / name
    if not path.exists() or path.stat().st_size < 1000:
        print("download", url, cl)
        t = requests.get(url, headers=headers, timeout=60).text
        path.write_text(t, encoding="utf-8", errors="ignore")
    else:
        t = path.read_text(encoding="utf-8", errors="ignore")
    print("scan", name, "len", len(t))
    for kw in keywords:
        for m in re.finditer(re.escape(kw), t):
            start = max(0, m.start() - 80)
            end = min(len(t), m.end() + 200)
            snippet = t[start:end].replace("\n", " ")
            collected.append((kw, snippet))

print("\n=== snippets ===")
seen = set()
for kw, snip in collected:
    key = snip[:120]
    if key in seen:
        continue
    seen.add(key)
    print(f"[{kw}] {snip[:280]}")
    if len(seen) > 60:
        break

# Search for GraphQL query strings with product
print("\n=== graphql query strings ===")
all_text = ""
for cl, url in sizes[:5]:
    name = url.rsplit("/", 1)[-1]
    all_text += (out_dir / name).read_text(encoding="utf-8", errors="ignore")

for m in re.finditer(r'["\']((?:query|mutation)\s+[A-Za-z0-9_]+[^"\']{20,500})["\']', all_text):
    q = m.group(1)
    if re.search(r"product|cate|filter", q, re.I):
        print(q[:400])
        print("---")

# Try graphql endpoint with common queries
print("\n=== probe graphql ===")
gq_url = "https://api.cellphones.com.vn/v2/graphql/query"
candidates = [
    {
        "query": """
        query getProductList($filter: ProductFilterInput, $page: Int, $size: Int, $order: ProductOrderInput) {
          products(filter: $filter, page: $page, size: $size, order: $order) {
            total
            items { id name url price special_price }
          }
        }
        """,
        "variables": {"filter": {"category_id": 3}, "page": 1, "size": 5},
    },
    {
        "query": """
        query products($filter: FilterEqualTypeInput) {
          products(filter: {category_id: {eq: "3"}}, pageSize: 5, currentPage: 1) {
            total_count
            items { id name }
          }
        }
        """
    },
]

# Also search literal "graphql/query" call bodies nearby in JS
for m in re.finditer(r"graphql/query", all_text):
    print("ctx:", all_text[max(0, m.start() - 50) : m.end() + 100].replace("\n", " ")[:200])

# Find strings containing 'productListCatePage'
idx = all_text.find("productListCatePage")
while idx != -1 and idx < all_text.find("productListCatePage") + 500000:
    print("\nPAGE CTX:", all_text[idx : idx + 500].replace("\n", " "))
    idx = all_text.find("productListCatePage", idx + 1)
    break

# Find URL path after axios/fetch for category products
for m in re.finditer(r'["\'](/v2/[^"\']+)["\']', all_text):
    print("path", m.group(1))
for m in re.finditer(r'["\'](https://api\.cellphones\.com\.vn[^"\']+)["\']', all_text):
    print("full", m.group(1))
