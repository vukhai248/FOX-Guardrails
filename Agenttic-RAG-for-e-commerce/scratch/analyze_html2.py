# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re, json
from pathlib import Path

ROOT = Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch")
html = (ROOT / "sample_product.html").read_text(encoding="utf-8", errors="ignore")
soup = BeautifulSoup(html, "html.parser")

# Extract full JSON-LD Product
for s in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(s.string or "")
    except Exception:
        continue
    if isinstance(data, dict) and data.get("@type") == "Product":
        out = ROOT / "product_jsonld.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Saved JSON-LD Product keys:", list(data.keys()))
        print("additionalProperty count:", len(data.get("additionalProperty") or []))
        print("image:", data.get("image"))
        print("price:", data.get("offers", {}).get("price"))
        print("brand:", data.get("brand"))
        break

# Gallery images
print("\n=== GALLERY IMAGES ===")
imgs = set()
for img in soup.select(".box-gallery img, .gallery-slide img, .thumbnail-slide img"):
    src = img.get("src") or img.get("data-src") or img.get("data-srcset") or ""
    if "catalog/product" in src or "cdn2.cellphones" in src:
        imgs.add(src.split()[0] if src else "")
print("count", len(imgs))
for i in list(imgs)[:12]:
    print(i[:160])

# Variants storage + color
print("\n=== VARIANTS ===")
for box in soup.select(".box-product-variants, .list-variants, .box-linked"):
    print("BOX class", box.get("class"), "text:", box.get_text(" | ", strip=True)[:300])

for a in soup.select("a.item-linked, .item-linked, .list-linked a, [class*='version'] a"):
    print("linked", a.get_text(strip=True)[:60], a.get("href"))

# Colors
for v in soup.select(".item-variant"):
    name = v.select_one(".item-variant-name")
    price = v.select_one(".item-variant-price")
    img = v.select_one("img")
    print(
        "color:",
        name.get_text(strip=True) if name else v.get_text(strip=True)[:40],
        "|",
        price.get_text(strip=True) if price else None,
        "| img",
        (img.get("src") if img else None),
    )

# Technical items
print("\n=== TECHNICAL ITEMS ===")
for item in soup.select(".technical-content-item")[:20]:
    print(item.get_text(" = ", strip=True)[:120])

# Description
print("\n=== DESCRIPTION BLOCKS ===")
for sel in [
    ".ksp-content",
    ".description-product",
    "#cpsContent",
    ".cps-block-content",
    ".product-description",
    ".block-content",
]:
    els = soup.select(sel)
    if els:
        print(sel, len(els), els[0].get_text(" ", strip=True)[:200])

# data-product-id
print("\nproduct ids:", [t.get("data-product-id") for t in soup.find_all(attrs={"data-product-id": True})][:5])

# LIST page - show more mechanism + nuxt
html2 = (ROOT / "sample_list.html").read_text(encoding="utf-8", errors="ignore")
print("\n=== LIST show-more / API ===")
# find api urls
for m in re.finditer(r"https?://[a-zA-Z0-9._/-]*(?:api|filter|product|graphql)[a-zA-Z0-9._/?=&%-]*", html2):
    u = m.group(0)
    if "cellphones" in u or "api" in u:
        print(u[:200])

# find filter endpoint patterns
for pat in [
    r"api\.cellphones[^\s\"']+",
    r"cellphones\.com\.vn/api[^\s\"']+",
    r"/lapi/[^\s\"']+",
    r"filterProduct[^\s\"']{0,80}",
    r"getProductList[^\s\"']{0,80}",
    r"category_id[^\s\"']{0,40}",
    r"show-more-product[^\s\"']{0,80}",
]:
    ms = re.findall(pat, html2)
    if ms:
        print("PAT", pat, "->", list(set(ms))[:8])

# extract product cards structure
soup2 = BeautifulSoup(html2, "html.parser")
card = soup2.select_one("div.product-info-container.product-item") or soup2.select_one(
    "div.product-info-container"
)
if card:
    print("\n=== CARD HTML (truncated) ===")
    print(str(card)[:1500])
    a = card.select_one("a.product__link")
    if a:
        print("href", a.get("href"))
    img = card.select_one("img")
    if img:
        print("img", img.get("src") or img.get("data-src"))
    for cls in ["product__name", "product-name", "product__price", "price", "sale-price"]:
        el = card.select_one(f".{cls}, [class*='{cls}']")
        if el:
            print(cls, el.get_text(strip=True)[:80])
