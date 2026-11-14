"""Read-only dependency readiness checks; no keys or provider error text in responses."""
from pathlib import Path

from supabase import create_client, ClientOptions
from configs.setting import settings


def probe_supabase():
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise RuntimeError("Missing public database configuration")
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY,
                           options=ClientOptions(postgrest_client_timeout=3, persist_session=False, auto_refresh_token=False))
    client.table("products").select("id").limit(1).execute()


def probe_chroma():
    directory = Path(settings.vector_db_absolute_path)
    if not (directory / "chroma.sqlite3").is_file():
        raise FileNotFoundError("Vector database is not initialized")
    import chromadb
    client = chromadb.PersistentClient(path=str(directory))
    return client.get_collection("products_collection").count()


def service_health():
    supabase_ok, chroma_ok, count = False, False, 0
    try:
        probe_supabase()
        supabase_ok = True
    except Exception:
        pass
    try:
        count = probe_chroma()
        chroma_ok = True
    except Exception:
        pass
    return {"status": "healthy" if supabase_ok and chroma_ok and count > 0 else "degraded",
            "service": "rag-service", "debug_mode": settings.DEBUG,
            "supabase_connected": supabase_ok, "chroma_connected": chroma_ok,
            "chroma_products_count": count}
