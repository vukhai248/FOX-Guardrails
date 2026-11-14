# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re, json, sys
from pathlib import Path

ROOT = Path(r"D:\create\Agenttic-RAG-for-e-commerce\scratch")


def analyze_product(path: Path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    print("=" * 60)
    print("PRODUCT:", path.name)
    print("=" * 60)

    print("\n=== TITLE ===")
    print(soup.title.string if soup.title else None)

    print("\n=== H1 ===")
    for h in soup.select("h1")[:5]:
        print(repr(h.get_text(strip=True)[:150]))

    print("\n=== JSON-LD ===")
    for s in soup.find_all("script", type="application/ld+json")[:8]:
        raw = s.string or s.get_text() or ""
        try:
            data = json.loads(raw)
        except Exception as e:
            print("parse err", e, raw[:150])
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            print("type:", t)
            if t in ("Product", "ProductGroup", "BreadcrumbList", "Offer"):
                print(json.dumps(item, ensure_ascii=False)[:2500])
                print("---")

    print("\n=== META ===")
    for prop in [
        "og:title",
        "og:image",
        "og:description",
        "product:price:amount",
        "product:brand",
        "description",
    ]:
        m = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if m:
            print(prop, ":", (m.get("content") or "")[:180])

    print("\n=== CLASS SNIPPETS containing price/name/spec ===")
    interesting = re.compile(
        r"price|product-name|product__|box-detail|technical|thong-so|kts|spec|gallery|variant|color|mau|brand|sku",
        re.I,
    )
    seen = set()
    for tag in soup.find_all(True, class_=True):
        classes = " ".join(tag.get("class") or [])
        if not interesting.search(classes):
            continue
        key = classes[:80]
        if key in seen:
            continue
        seen.add(key)
        txt = tag.get_text(" ", strip=True)[:80]
        print(f"[{classes[:100]}] -> {txt}")
        if len(seen) > 40:
            break

    print("\n=== data attributes product ===")
    for tag in soup.find_all(attrs={"data-product": True})[:3]:
        print(tag.name, tag.get("data-product")[:300])
    for attr in ["data-id", "data-product-id", "data-sku", "data-price", "data-name"]:
        els = soup.find_all(attrs={attr: True})
        if els:
            print(attr, "count", len(els), "sample", els[0].get(attr)[:120])

    print("\n=== SCRIPT windows / __NEXT / product config ===")
    for s in soup.find_all("script"):
        txt = s.string or ""
        if not txt:
            continue
        if any(
            k in txt
            for k in [
                "productDetail",
                "product_id",
                "window.product",
                "variants",
                "technical",
                "sku",
                "listPrice",
            ]
        ):
            # print first matching chunk
            for m in re.finditer(
                r".{0,40}(productDetail|variants|technical|listPrice|product_id).{0,120}",
                txt,
            ):
                print(m.group(0)[:200])
                break
            print("script len", len(txt), "src", s.get("src"))
            # try find json blobs
            for pat in [
                r"window\.__NUXT__\s*=",
                r"productDetail\s*[:=]",
                r"var\s+product\s*=",
            ]:
                if re.search(pat, txt):
                    print("FOUND", pat)


def analyze_list(path: Path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    print("=" * 60)
    print("LIST:", path.name)
    print("=" * 60)

    # product cards
    candidates = [
        ".product-info",
        ".product-info-container",
        ".product-list-item",
        ".product-item",
        ".product-card",
        "div.product-info",
        "a.product__link",
        ".list-product",
        ".products-container",
        "[class*='product-info']",
        "[class*='product-list']",
    ]
    for sel in candidates:
        els = soup.select(sel)
        if els:
            print(sel, "->", len(els))
            print("  sample class:", els[0].get("class"), "text:", els[0].get_text(" ", strip=True)[:100])

    # links to product pages
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and "cellphones.com.vn" in href or (
            href.startswith("/") and href.endswith(".html")
        ):
            name = a.get_text(strip=True)[:60]
            if name and len(name) > 5:
                links.append((href, name))
    print("\nproduct-like links sample:")
    for h, n in links[:15]:
        print(n, "->", h)

    # pagination / load more
    for sel in [".pagination", ".btn-show-more", ".view-more", "[class*='show-more']", "[class*='load-more']"]:
        els = soup.select(sel)
        if els:
            print(sel, els[0].get_text(" ", strip=True)[:80], els[0].get("class"))

    # look for API endpoints in scripts
    print("\n=== API hints in scripts ===")
    for s in soup.find_all("script"):
        txt = s.string or ""
        if not txt:
            continue
        for m in re.finditer(r"https?://[^\s\"']+api[^\s\"']+", txt, re.I):
            print(m.group(0)[:200])
        for m in re.finditer(r"[\"'](/[a-z0-9_/-]*filter[a-z0-9_/-]*)[\"']", txt, re.I):
            print("path", m.group(1))
        if "graphql" in txt.lower() or "getProducts" in txt or "category" in txt and "api" in txt.lower():
            for m in re.finditer(r".{0,30}(graphql|getProducts|api/v[0-9]).{0,80}", txt, re.I):
                print(m.group(0)[:150])


if __name__ == "__main__":
    analyze_product(ROOT / "sample_product.html")
    print("\n\n")
    analyze_list(ROOT / "sample_list.html")
