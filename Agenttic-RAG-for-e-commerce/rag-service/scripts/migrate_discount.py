import sys
import os
import json

# Thêm thư mục root của rag-service vào sys.path để import configs
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from configs.setting import settings
from supabase import create_client

def run_migration():
    print("=== BẮT ĐẦU DI CHUYỂN DỮ LIỆU: CẬP NHẬT CỘT DISCOUNT ===")
    
    # 1. Kết nối Supabase
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE_KEY
    if not url or not key:
        print("Lỗi: Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong file .env")
        return
        
    supabase = create_client(url, key)
    
    # 2. Hướng dẫn tạo cột nếu chưa có
    print("\n[Bước 1] Đang kiểm tra cột 'discount' trong Database...")
    try:
        # Thử select cột discount để xem cột đã tồn tại chưa
        supabase.table("products").select("id, discount").limit(1).execute()
        print("  -> Cột 'discount' đã tồn tại trong database.")
    except Exception as e:
        print("  -> Cột 'discount' chưa tồn tại hoặc gặp lỗi.")
        print("  -> Vui lòng chạy lệnh SQL sau trong SQL Editor trên Dashboard Supabase của bạn trước:")
        print("     ALTER TABLE public.products ADD COLUMN IF NOT EXISTS discount NUMERIC DEFAULT 0.0;")
        print("  -> Hoặc chạy câu lệnh trên rồi khởi động lại script này.")
        return

    # 3. Tải toàn bộ sản phẩm hiện có bằng phân trang an toàn
    print("\n[Bước 2] Đang tải toàn bộ sản phẩm hiện có từ database...")
    products = []
    limit = 1000
    offset = 0
    while True:
        try:
            response = supabase.table("products")\
                .select("*")\
                .order("id", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            batch = response.data
            if not batch:
                break
            products.extend(batch)
            print(f"  -> Đã tải batch {offset} - {offset + len(batch) - 1} ({len(batch)} sản phẩm)")
            if len(batch) < limit:
                break
            offset += limit
        except Exception as ex:
            print(f"Lỗi khi tải sản phẩm: {ex}")
            return
            
    total_products = len(products)
    print(f"  -> Tổng số sản phẩm tải được: {total_products}")
    
    if total_products == 0:
        print("Không có sản phẩm nào để cập nhật.")
        return

    # 4. Tính toán discount và cập nhật hàng loạt (batch upsert)
    print("\n[Bước 3] Đang tính toán tỷ lệ giảm giá (discount) và chuẩn bị cập nhật...")
    updated_products = []
    for prod in products:
        p = prod.get("price") or 0
        fp = prod.get("final_price") or p
        
        # Tính toán phần trăm giảm giá làm tròn 2 chữ số thập phân
        if p > 0:
            discount = round((1 - (fp / p)) * 100, 2)
        else:
            discount = 0.0
            
        prod["discount"] = discount
        updated_products.append(prod)

    # 5. Ghi đè cập nhật hàng loạt bằng upsert
    print("\n[Bước 4] Đang ghi dữ liệu cập nhật xuống Supabase...")
    batch_size = 100
    success_count = 0
    for i in range(0, len(updated_products), batch_size):
        batch = updated_products[i:i+batch_size]
        try:
            res = supabase.table("products").upsert(batch).execute()
            success_count += len(res.data)
            print(f"  -> Đã cập nhật batch {i // batch_size + 1}: {len(res.data)} sản phẩm.")
        except Exception as ex:
            print(f"  -> Gặp lỗi khi cập nhật batch tại chỉ mục {i}: {ex}")

    print(f"\n=== HOÀN THÀNH DI CHUYỂN DỮ LIỆU ===")
    print(f"Đã cập nhật thành công {success_count}/{total_products} sản phẩm.")

if __name__ == "__main__":
    run_migration()
