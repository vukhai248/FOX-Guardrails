# -*- coding: utf-8 -*-
import re
import json
import requests
from pathlib import Path

js = Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch\js_cache\01d9849.js").read_text(
    encoding="utf-8", errors="ignore"
)

# Extract GetProductsByCateId full template
idx = js.find("query GetProductsByCateId")
print("idx", idx)
if idx >= 0:
    chunk = js[idx : idx + 3500]
    print(chunk)
    Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch\get_products_query_raw.txt").write_text(
        chunk, encoding="utf-8"
    )

# Also find filterByCateAndFilter
idx2 = js.find("filterByCateAndFilter")
print("\nfilterByCate idx", idx2)
if idx2 >= 0:
    print(js[idx2 : idx2 + 2500])

# Try reconstruct a working query
# From snippet:
# query GetProductsByCateId{
#   products(
#     filter: {
#       static: {
#         categories: [m],
#         excluded: {...}
#         province_id: ...
#       }
#     }
#     page: ...
#     size: ...
#     sort: ...
#   ) { general { ... } filterable { ... } }

# Search for field selection near GetProductsByCateId
m = re.search(
    r"query GetProductsByCateId\{[\s\S]{0,5000}?products\([\s\S]{0,2000}?\)\s*\{([\s\S]{0,4000}?)\}[\s\n]*\}",
    js,
)
if m:
    print("\n=== fields block ===")
    print(m.group(0)[:4000])

# Simpler: print 4000 chars after GetProductsByCateId
# Then try live API with reconstructed query

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://cellphones.com.vn",
    "Referer": "https://cellphones.com.vn/mobile.html",
    "X-Client-Type": "web",
}

# province_id 30 is often HCM / default in VN sites - from cookies cps_province
# From code: province_id from cookie, company stock etc.
# Looking at snippets: province_id: Y.id or similar

queries = []

# Try minimal fields first
q1 = """
query GetProductsByCateId {
  products(
    filter: {
      static: {
        categories: ["3"]
        province_id: 30
        stock: { from: 0 }
      }
    }
    page: 1
    size: 5
    sort: [{ view: "desc" }]
  ) {
    general {
      product_id
      name
      url_path
      attributes
    }
  }
}
"""

q2 = """
query GetProductsByCateId {
  products(
    filter: {
      static: {
        categories: [3]
        province_id: 30
      }
    }
    page: 1
    size: 5
  ) {
    general {
      product_id
      name
      url_path
    }
    filterable {
      price
      special_price
    }
  }
}
"""

# Extract exact field names used after products( in GetProductsByCateId by reading concatenated string parts
# The code builds query with .concat - let's find the return fields after the filter block
# Pattern: general { product_id name ...
for m in re.finditer(r"general\s*\{\s*product_id", js):
    print("\nGENERAL CTX:\n", js[m.start() : m.start() + 800])
    break

for m in re.finditer(r'url_path[\s\S]{0,200}attributes', js):
    print("\nATTR CTX:\n", js[m.start() - 100 : m.start() + 500])
    if m.start() > 0:
        break

# Live probe
for i, q in enumerate([q1, q2], 1):
    try:
        r = requests.post(
            "https://api.cellphones.com.vn/v2/graphql/query",
            headers=headers,
            json={"query": q, "variables": {}},
            timeout=30,
        )
        print(f"\n=== probe {i} status {r.status_code} ===")
        print(r.text[:800])
    except Exception as e:
        print("ERR", e)

# Extract province default from list HTML
list_html = Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch\sample_list.html").read_text(
    encoding="utf-8", errors="ignore"
)
for pat in [r"province_id[:\s]+(\d+)", r'"id":(\d+),"name":"[^"]*Hồ Chí Minh', r"company_id[:\s]+(\d+)"]:
    ms = re.findall(pat, list_html)
    if ms:
        print("list html", pat, ms[:5])
