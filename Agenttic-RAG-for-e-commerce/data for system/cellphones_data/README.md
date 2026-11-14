# CellphoneS Crawler - Du lieu thu thap (co variants, mau sac, % giam gia)

## Tong quan
- Nguon: CellphoneS (cellphones.com.vn) qua API GraphQL cong khai
- Danh muc: laptop (category_id=380) + dien-thoai (category_id=3)
- Thoi gian thu thap: 2026-07-14
- Rate limit: 1 giay/trang API, tai anh song song 20 workers, gioi han concurrent cho product detail
- Cap nhat: 2026-07-14 - bo sung child products (mau sac, phien ban) va % giam gia

## Ket qua
| Danh muc | Tong SP | Co variants | Tong variants | Co anh parent | Co anh variant | Gia >0 | Co day du thong so chinh |
|----------|---------|-------------|---------------|---------------|----------------|--------|---------------------------|
| laptop | 1.135 | 987 | 1.162 | 100% | ~99% | 83.3% | ~96-99% |
| dien-thoai | 1.037 | 375 | 1.106 | 99.8% | ~99% | 38.2% | ~80-95% |

## File
- `{category}_products_variants.json`: du lieu day du, bao gom `variants`, `colors`, `discount_percent`, co cot `raw` va `attributes_json`
- `{category}_products_variants.csv`: du lieu CSV de doc, khong co cot `raw`, `variants`, `colors`
- `{category}_variants.csv`: chi danh sach child products voi parent_id, mau sac, gia, % giam gia
- `images/`: anh san pham (parent + variant), dat ten theo `product_id`

## Cot du lieu chinh (products)
product_id, name, brand, sku, url, category, price, special_price, final_price,
discount_percent, stock, review_count, average_rating, cpu, chipset, ram, storage,
display_size, display_resolution, battery, os, gpu, camera_primary, camera_secondary,
bluetooth, dimensions, weight, color, colors, variants, image_url, description

## Cot du lieu variants
parent_id, parent_name, product_id, name, sku, color, price, special_price,
final_price, discount_percent, stock, thumbnail, image_url

## Luu y
- San pham dien thoai co gia 0 thuong la tin don, ngung kinh doanh hoac sap ra mat, nen khong co child/variants.
- `discount_percent` duoc tinh tu `(price - special_price) / price * 100`.
- `color` cua parent lay tu child dau tien; `colors` la danh sach toan bo mau sac co san.
- File `*_valid.*` (tu crawler goc) chi giu san pham co gia > 0.
