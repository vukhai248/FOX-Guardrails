# scratch/check_db_count.py
import os
from dotenv import load_dotenv
from supabase import create_client

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.local')
load_dotenv(dotenv_path)

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if url and key:
    client = create_client(url, key)
    res = client.table("products").select("id", count="exact").limit(1).execute()
    print("Exact count of products in DB:", res.count)
else:
    print("Missing configs!")
