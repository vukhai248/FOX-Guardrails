import os
import sys
import io
import time
import json
import random
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Ensure UTF-8 output encoding for console prints
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Headers to mimic a real browser and bypass basic bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1"
}

# Mapping categories to their main URLs on CellphoneS
CATEGORIES = {
    "dien-thoai": "https://cellphones.com.vn/mobile.html",
    "laptop": "https://cellphones.com.vn/laptop.html",
    "am-thanh": "https://cellphones.com.vn/thiet-bi-am-thanh.html",
    "mic-thu-am": "https://cellphones.com.vn/thiet-bi-am-thanh/micro-thu-am.html",
    "dong-ho": "https://cellphones.com.vn/do-choi-cong-nghe.html",
    "camera": "https://cellphones.com.vn/phu-kien/camera.html",
    "phu-kien": "https://cellphones.com.vn/phu-kien.html",
    "pc": "https://cellphones.com.vn/may-tinh-de-ban.html",
    "man-hinh": "https://cellphones.com.vn/man-hinh.html",
    "may-in": "https://cellphones.com.vn/may-in.html",
    "tivi": "https://cellphones.com.vn/tivi.html",
    "dien-may": "https://cellphones.com.vn/dien-may.html"
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data for system")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "scraped_products.json")

def fetch_html(url):
    """Fetches HTML with retries and delays to avoid getting blocked."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Random delay between 1.0 and 2.5 seconds
            time.sleep(random.uniform(1.0, 2.5))
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                print(f"[WARN] 404 Not Found: {url}")
                return None
            else:
                print(f"[WARN] Status {response.status_code} for {url}. Attempt {attempt+1}/{max_retries}")
        except Exception as e:
            print(f"[WARN] Error fetching {url}: {e}. Attempt {attempt+1}/{max_retries}")
    return None

def extract_subpages(category_name, main_url):
    """Extracts sub-category/brand page links from the main category page."""
    html = fetch_html(main_url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    subpage_links = []
    
    # Prefix for brands/subpages, e.g., 'https://cellphones.com.vn/mobile/' or '/mobile/'
    prefix = main_url.replace(".html", "/")
    relative_prefix = "/" + prefix.split("cellphones.com.vn/")[1]
    
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        # Check if the href matches prefix patterns
        if href.startswith(prefix) or href.startswith(relative_prefix):
            # Normalize to absolute URL
            full_url = href if href.startswith("http") else "https://cellphones.com.vn" + href
            # Exclude main page itself or anchors/empty pages
            if full_url != main_url and not full_url.endswith("#") and full_url not in subpage_links:
                subpage_links.append(full_url)
                
    return subpage_links

def extract_products_from_page(page_url):
    """Extracts product URLs from a category or brand listing page."""
    html = fetch_html(page_url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    product_links = []
    
    # We found products are under class 'product-info' or 'product-item'
    items = soup.find_all(class_=["product-info", "product-item"])
    for item in items:
        # Find the product link anchor
        a = item.find("a", class_="product__link")
        if not a:
            a = item.find("a", href=True)
        if a and a.get("href"):
            href = a["href"].strip()
            # Normalize URL
            full_url = href if href.startswith("http") else "https://cellphones.com.vn" + href
            if full_url.endswith(".html") and full_url not in product_links:
                product_links.append(full_url)
                
    return product_links

def parse_product_detail(product_url, category_name):
    """Parses product detail page to extract all required fields."""
    html = fetch_html(product_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Product Name
    name = ""
    h1 = soup.find("h1")
    if h1:
        name = h1.text.strip()
    else:
        title_tag = soup.find("title")
        if title_tag:
            name = title_tag.text.strip().split(" | ")[0].split(" giá ")[0]
            
    # 2. Brand
    brand = "Khác"
    # Try finding brand from specs or JSON-LD
    
    # 3. Prices
    sale_price = None
    base_price = None
    
    sale_p_tag = soup.find(class_="sale-price")
    if sale_p_tag:
        try:
            # Extract numbers from string like '30.890.000đ'
            price_str = "".join(filter(str.isdigit, sale_p_tag.text))
            sale_price = float(price_str) if price_str else None
        except ValueError:
            pass
            
    base_p_tag = soup.find(class_="base-price")
    if base_p_tag:
        try:
            price_str = "".join(filter(str.isdigit, base_p_tag.text))
            base_price = float(price_str) if price_str else None
        except ValueError:
            pass
            
    if not base_price and sale_price:
        base_price = sale_price
        
    # 4. Technical Specifications
    specs = {}
    tech_table = soup.find(class_="technical-content")
    if tech_table:
        rows = tech_table.find_all(class_="technical-content-item")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].text.strip()
                val = cols[1].text.strip()
                specs[key] = val
                
    # Detect Brand from specs
    for k, v in specs.items():
        if any(b_word in k.lower() for b_word in ["thương hiệu", "hãng sản xuất", "nhà sản xuất"]):
            brand = v.strip()
            break
            
    # If brand is still Khác, try parsing from product name
    if brand == "Khác" and name:
        first_word = name.split()[0]
        # Common brands
        if first_word.lower() in ["iphone", "ipad", "macbook", "apple"]:
            brand = "Apple"
        elif first_word.lower() in ["samsung", "galaxy"]:
            brand = "Samsung"
        elif first_word.lower() in ["xiaomi", "redmi", "poco"]:
            brand = "Xiaomi"
        else:
            brand = first_word
            
    # 5. Image URLs
    images = []
    # Try extracting from schema JSON-LD
    schema_scripts = soup.find_all("script", type="application/ld+json")
    for script in schema_scripts:
        try:
            data = json.loads(script.string or script.text)
            if isinstance(data, dict):
                if data.get("@type") == "Product" and "image" in data:
                    img = data["image"]
                    if isinstance(img, list):
                        images.extend(img)
                    elif isinstance(img, str):
                        images.append(img)
        except Exception:
            pass
            
    # Extract from gallery elements
    gallery = soup.find(class_=["gallery-slide", "gallery-product-detail"])
    if gallery:
        img_tags = gallery.find_all("img")
        for img in img_tags:
            src = img.get("src") or img.get("data-src")
            if src and "placehoder" not in src and "favicon" not in src:
                if not src.startswith("http"):
                    src = "https:" + src if src.startswith("//") else "https://cellphones.com.vn" + src
                images.append(src)
                
    images = list(dict.fromkeys(images)) # Deduplicate
    
    # 6. Description Text
    desc_text = ""
    # Standard description div
    desc_div = soup.find(id="description")
    if not desc_div:
        desc_div = soup.find(class_=["cps-block-content", "description", "detail-content-description"])
        
    if desc_div:
        # Get paragraphs
        paras = desc_div.find_all(["p", "h2", "h3", "li"])
        if paras:
            desc_text = "\n".join([p.text.strip() for p in paras if p.text.strip()])
        else:
            desc_text = desc_div.text.strip()
    else:
        # Fallback to large div containing text
        for div in soup.find_all("div"):
            if div.get("class") and any("content" in c for c in div.get("class")):
                text = div.text.strip()
                if len(text) > 400:
                    desc_text = text
                    break
                    
    # Format specs as readable text to append to description if needed (for RAG quality)
    specs_str = "\n".join([f"{k}: {v}" for k, v in specs.items()])
    
    # Return standard dictionary matching database schema
    return {
        "url": product_url,
        "category": category_name,
        "brand": brand,
        "name": name,
        "price": sale_price or base_price or 0.0,
        "original_price": base_price or sale_price or 0.0,
        "stock": random.randint(20, 100), # Mock stock
        "description": desc_text,
        "specs": specs,
        "images": images,
        "rating_avg": 5.0 # default rating
    }

def main():
    print("=== CELLPHONES PRODUCT CRAWLER FOR RAG SYSTEM ===")
    
    # Load already scraped products if output file exists to enable resuming
    scraped_data = []
    scraped_urls = set()
    
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                scraped_data = json.load(f)
                scraped_urls = {item["url"] for item in scraped_data}
            print(f"[INFO] Loaded {len(scraped_data)} existing scraped products. Resuming...")
        except Exception as e:
            print(f"[WARN] Error reading output file, starting fresh: {e}")
            
    # Step 1: Collect Product URLs for each category
    all_category_urls = {}
    for cat_name, main_url in CATEGORIES.items():
        print(f"\n--- Collecting links for category: {cat_name} ---")
        product_urls = []
        
        # A. Collect from Main Page
        print(f"Fetching main page: {main_url}")
        main_links = extract_products_from_page(main_url)
        product_urls.extend(main_links)
        print(f"Found {len(main_links)} product links on main page.")
        
        # B. Collect from Subpages (Brands/Filters)
        print("Extracting brand/subpage filters...")
        subpages = extract_subpages(cat_name, main_url)
        print(f"Found {len(subpages)} subpages to scrape.")
        
        # Limit subpages to top 5 to keep crawling fast and prevent server load
        for sub_url in subpages[:5]:
            print(f"Fetching subpage: {sub_url}")
            sub_links = extract_products_from_page(sub_url)
            product_urls.extend(sub_links)
            
        product_urls = list(set(product_urls)) # Deduplicate
        all_category_urls[cat_name] = product_urls
        print(f"Total unique product links for {cat_name}: {len(product_urls)}")
        
    # Step 2: Scrape Details for each URL
    total_to_scrape = sum(len(urls) for urls in all_category_urls.values())
    print(f"\nTotal product URLs to scrape details: {total_to_scrape}")
    
    scraped_count = 0
    
    for cat_name, urls in all_category_urls.items():
        print(f"\nScraping details for category: {cat_name}")
        for url in tqdm(urls, desc=f"Scraping {cat_name}"):
            if url in scraped_urls:
                continue
                
            try:
                product_data = parse_product_detail(url, cat_name)
                if product_data and product_data["name"]:
                    scraped_data.append(product_data)
                    scraped_urls.add(url)
                    scraped_count += 1
                    
                    # Save progress every 5 products
                    if scraped_count % 5 == 0:
                        os.makedirs(OUTPUT_DIR, exist_ok=True)
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(scraped_data, f, ensure_ascii=False, indent=2)
                else:
                    print(f"\n[WARN] Failed to parse product details: {url}")
            except Exception as e:
                print(f"\n[ERROR] Exception scraping {url}: {e}")
                
    # Final Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n=== SUCCESS ===")
    print(f"Successfully scraped {scraped_count} new products.")
    print(f"Total products in dataset: {len(scraped_data)}")
    print(f"Data saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
