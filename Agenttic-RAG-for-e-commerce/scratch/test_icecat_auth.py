# scratch/test_icecat_auth.py
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load env từ .env.local ở thư mục gốc (lùi 1 thư mục)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.local')
load_dotenv(dotenv_path)

print("Python executable:", sys.executable)
print("Supabase URL:", os.getenv("NEXT_PUBLIC_SUPABASE_URL"))

try:
    from IceCat import IceCat
    print("✅ Import thư viện IceCat thành công!")
except Exception as e:
    print("❌ Lỗi import IceCat:", e)

# Test kết nối Supabase
try:
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("❌ Thiếu Supabase config trong .env.local")
    else:
        client = create_client(url, key)
        # Query thử 1 dòng sản phẩm
        res = client.table("products").select("id").limit(1).execute()
        print("✅ Kết nối Supabase thành công! Dữ liệu mẫu:", res.data)
except Exception as e:
    print("❌ Lỗi kết nối Supabase:", e)
