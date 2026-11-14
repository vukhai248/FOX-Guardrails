import sys
import os
import json
from datetime import datetime

# Thêm thư mục root của rag-service vào sys.path để import được configs
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from configs.setting import settings
from supabase import create_client

def load_json(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_description_to_specs(description_str):
    """
    Hàm phân tích chuỗi description gộp thông số (ngăn cách bởi dấu chấm phẩy ';')
    thành một dictionary chứa các cặp Key-Value thông số kỹ thuật.
    """
    specs = {}
    if not description_str or not isinstance(description_str, str):
        return specs
        
    # Tách chuỗi bằng dấu chấm phẩy
    parts = description_str.split(';')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if ':' in part:
            # Tách ở dấu hai chấm đầu tiên
            subparts = part.split(':', 1)
            k = subparts[0].strip()
            v = subparts[1].strip()
            if k and v:
                specs[k] = v
    return specs

def clean_specs_keys(specs_dict):
    """
    Hàm làm sạch các key trong specs dictionary: loại bỏ các key không mong muốn,
    đồng thời chuẩn hóa tên key để tránh key rác.
    """
    cleaned = {}
    ignored_keys = {
        'gia', 'gia_ban', 'price', 'final_price', 'special_price', 
        'key_selling_points', 'short_description', 'description', 
        'attributes_json', 'raw', 'url', 'thumbnail', 'image_url',
        'product_id', 'id', 'name', 'sku', 'brand', 'category',
        'image', 'small_image', 'status', 'tax_vat', 'url_key', 'url_path', 
        'tien_coc', 'msrp_enabled', 'smember_sms', 'title_price', 
        'options_container', 'product_condition', 'product_feed_type', 
        'sim_special_group', 'use_smd_colorswatch', 'mobile_accessory_type', 
        'change_layout_preorder', 'fe_minimum_down_payment', 'hc_maximum_down_payment', 
        'hc_minimum_down_payment', 'short_description_show_time', 
        'short_description_hidden_time', 'msrp_display_actual_price_type', 
        'basic', 'full_by_group', 'visibility_date', 'short_name', 'related_name', 
        'ads_base_image', 'macbook_anh_bao_mat', 'macbook_anh_dong_chip', 
        'macbook_anh_intelligence', 'macbook_anh_dong_chip',
        'available_tags', 'availableTags', 'warranty_tags', 'warrantyTags', 'promo_tags', 'promoTags'
    }
    
    for k, v in specs_dict.items():
        k_lower = k.lower().strip()
        if k_lower in ignored_keys:
            continue
        # Bỏ các key rỗng hoặc giá trị null
        if not k.strip() or v is None or str(v).strip().lower() in ['null', 'undefined', '']:
            continue
            
        cleaned[k.strip()] = v
    return cleaned

def import_products(supabase, data, category_label, batch_size=100):
    total = len(data)
    print(f"\nImporting {total} items for category: {category_label}...")
    
    # Danh sách các cột của bảng products trong DB
    db_columns = [
        'id', 'name', 'brand', 'sku', 'url', 'category', 'price', 
        'special_price', 'final_price', 'discount', 'stock', 'thumbnail', 'image_url', 
        'cpu', 'ram', 'storage', 'display_size', 'display_resolution', 
        'battery', 'os', 'gpu', 'weight', 'dimensions', 
        'included_accessories', 'camera_primary', 'camera_secondary', 
        'camera_video', 'description', 'key_selling_points', 'specs'
    ]
    
    formatted_data = []
    for item in data:
        formatted_item = {}
        
        # Map ID sản phẩm
        if 'product_id' in item:
            formatted_item['id'] = item['product_id']
        elif 'id' in item:
            formatted_item['id'] = item['id']
            
        # 1. Parse đặc điểm nổi bật (key_selling_points) và các thuộc tính từ attributes_json
        ksp = None
        attr_specs = {}
        attr_json_str = item.get('attributes_json', '{}')
        if attr_json_str:
            try:
                if isinstance(attr_json_str, dict):
                    attrs = attr_json_str
                else:
                    attrs = json.loads(attr_json_str, strict=False)
                
                ksp = attrs.get('key_selling_points', None)
                # Lấy tất cả thuộc tính trong attributes_json làm specs gốc
                for k, v in attrs.items():
                    attr_specs[k] = v
            except:
                pass
                
        # 2. Parse thông số kỹ thuật từ chuỗi description gộp
        desc_str = item.get('description', '')
        desc_specs = parse_description_to_specs(desc_str)
        
        # 3. Gộp cả hai nguồn thông số kỹ thuật: Ưu tiên thuộc tính chi tiết trong attributes_json
        combined_specs = {**desc_specs, **attr_specs}
        cleaned_specs = clean_specs_keys(combined_specs)
        
        for col in db_columns:
            if col == 'id':
                continue
            
            if col == 'category':
                formatted_item['category'] = category_label
                continue
                
            if col == 'key_selling_points':
                formatted_item['key_selling_points'] = ksp
                continue
                
            if col == 'specs':
                formatted_item['specs'] = cleaned_specs
                continue
                
            if col == 'discount':
                disc = item.get('discount')
                if disc is not None:
                    try:
                        formatted_item['discount'] = float(disc)
                    except:
                        formatted_item['discount'] = 0.0
                else:
                    p = item.get('price') or 0
                    fp = item.get('final_price') or p
                    if p > 0:
                        formatted_item['discount'] = round((1 - (fp / p)) * 100, 2)
                    else:
                        formatted_item['discount'] = 0.0
                continue
                
            val = item.get(col, None)
            if val == "":
                formatted_item[col] = None
            else:
                formatted_item[col] = val
                
        formatted_data.append(formatted_item)

    # Loại bỏ trùng lặp id NGAY TRONG PYTHON
    unique_data = []
    seen_ids = set()
    for item in formatted_data:
        item_id = item['id']
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            unique_data.append(item)
            
    unique_total = len(unique_data)
    print(f"  -> Filtered out {total - unique_total} duplicate items. Unique items to import: {unique_total}")

    # Chia batch để upsert
    for i in range(0, unique_total, batch_size):
        batch = unique_data[i:i+batch_size]
        try:
            res = supabase.table("products").upsert(batch).execute()
            print(f"  -> Upserted batch {i // batch_size + 1}: {len(res.data)} items.")
        except Exception as e:
            print(f"  -> Error upserting batch starting at index {i}: {e}")

def import_policies(supabase):
    print("\nImporting sample policies into 'policies' table...")
    policies = [
        {
            "title": "Chính sách đổi trả 1-đổi-1 sản phẩm công nghệ",
            "category": "return_refund",
            "content": """Chính sách đổi trả sản phẩm tại Website TMĐT Điện tử:
1. Thời gian áp dụng: Trong vòng 30 ngày kể từ ngày nhận hàng thành công.
2. Điều kiện áp dụng đổi trả:
- Sản phẩm bị lỗi kỹ thuật (lỗi phần cứng) từ phía nhà sản xuất.
- Sản phẩm còn nguyên hộp, đầy đủ phụ kiện đi kèm, hóa đơn mua hàng và phiếu bảo hành.
- Sản phẩm không bị trầy xước, nứt vỡ, ẩm ướt hoặc có dấu hiệu tự ý can thiệp phần cứng.
3. Hình thức đổi trả:
- Đổi mới 1-đổi-1 sản phẩm cùng model hoặc nâng cấp lên model cao hơn (bù chênh lệch).
- Trường hợp hết hàng đổi mới, hỗ trợ hoàn tiền 100% giá trị sản phẩm trên hóa đơn mua hàng."""
        },
        {
            "title": "Chính sách bảo hành chính hãng thiết bị điện tử",
            "category": "warranty",
            "content": """Quy định bảo hành sản phẩm Laptop và Điện thoại di động:
1. Thời hạn bảo hành: 
- Đối với Laptop: Bảo hành chính hãng 24 tháng kể từ ngày kích hoạt hóa đơn.
- Đối với Điện thoại: Bảo hành chính hãng 12 tháng kể từ ngày kích hoạt.
- Phụ kiện đi kèm (bộ sạc, cáp kết nối): Bảo hành 6 tháng.
2. Các trường hợp được bảo hành miễn phí:
- Thiết bị hư hỏng linh kiện do lỗi sản xuất dưới điều kiện sử dụng bình thường.
- Số Serial/IMEI trên thiết bị còn nguyên vẹn, trùng khớp với hóa đơn mua hàng.
3. Các trường hợp từ chối bảo hành:
- Thiết bị bị hỏng do tai nạn rơi vỡ, va đập, vô nước hoặc sử dụng sai điện áp nguồn.
- Thiết bị đã qua sửa chữa tại các cửa hàng không thuộc hệ thống bảo hành ủy quyền của hãng."""
        },
        {
            "title": "Chính sách giao hàng và vận chuyển toàn quốc",
            "category": "shipping",
            "content": """Chính sách giao nhận hàng hóa tại Website TMĐT:
1. Thời gian giao hàng:
- Nội thành (Hà Nội & TP. HCM): Giao hàng hỏa tốc trong vòng 2 giờ đối với các sản phẩm có nhãn Express, hoặc giao tiêu chuẩn trong ngày.
- Các tỉnh thành khác: Giao hàng tiêu chuẩn từ 2 - 4 ngày làm việc.
2. Phí vận chuyển:
- Miễn phí vận chuyển toàn quốc cho tất cả các đơn hàng có giá trị trên 5,000,000đ.
- Đối với đơn hàng dưới 5,000,000đ, áp dụng phí ship đồng giá 30,000đ.
3. Đồng kiểm khi nhận hàng:
- Khách hàng được quyền khui hộp kiểm tra ngoại quan sản phẩm (không bật nguồn, không kích hoạt máy) trước khi thanh toán cho shipper."""
        }
    ]
    
    try:
        res = supabase.table("policies").select("*").execute()
        existing = len(res.data) if res.data else 0
        if existing == 0:
            res_insert = supabase.table("policies").insert(policies).execute()
            print(f"-> Successfully imported {len(res_insert.data)} policies.")
        else:
            res_upsert = supabase.table("policies").upsert(policies).execute()
            print(f"-> Policies updated/upserted ({len(res_upsert.data)} records).")
    except Exception as e:
        print(f"-> Error importing policies: {e}")

def main():
    print("Connecting to Supabase...")
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    
    # Xác định đường dẫn tương đối từ gốc dự án
    project_root = os.path.dirname(parent_dir)
    laptop_file = os.path.join(project_root, "data for system", "cellphones_data", "laptop", "laptop_products_cleaned.json")
    phone_file = os.path.join(project_root, "data for system", "cellphones_data", "dien-thoai", "dien-thoai_products_cleaned.json")
    
    # 1. Import Laptop
    print(f"Loading laptops from: {laptop_file}")
    laptops = load_json(laptop_file)
    if laptops:
        import_products(supabase, laptops, "laptop", batch_size=100)
    else:
        print("No laptop data found.")
        
    # 2. Import Điện thoại
    print(f"Loading phones from: {phone_file}")
    phones = load_json(phone_file)
    if phones:
        import_products(supabase, phones, "phone", batch_size=100)
    else:
        print("No phone data found.")
        
    # 3. Import chính sách mẫu
    import_policies(supabase)
    
    print("\nData ingestion process finished successfully.")

if __name__ == "__main__":
    main()
