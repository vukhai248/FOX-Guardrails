import importlib
from types import SimpleNamespace

import pytest


@pytest.mark.parametrize("supabase,chroma,count,status", [(True,True,42,"healthy"),(False,True,42,"degraded"),(True,False,0,"degraded"),(True,True,0,"degraded")])
def test_health_reflects_dependency_probes(client,backend,monkeypatch,supabase,chroma,count,status):
    m=importlib.import_module("src.health")
    def db():
        if not supabase: raise RuntimeError("secret DB error")
    def vector():
        if not chroma: raise RuntimeError("secret vector path")
        return count
    monkeypatch.setattr(m,"probe_supabase",db)
    monkeypatch.setattr(m,"probe_chroma",vector)
    response=client.get("/health")
    assert response.status_code==200
    result=response.json()
    assert result["status"]==status
    assert result["supabase_connected"] is supabase
    assert result["chroma_connected"] is chroma
    assert result["chroma_products_count"]==count
    assert "secret" not in response.text


def test_health_supabase_probe_is_real_anon_read_with_bounded_timeout(backend,monkeypatch):
    import httpx
    from supabase import create_client
    m=importlib.import_module("src.health")
    requests=[]
    def transport(request):
        requests.append(request)
        return httpx.Response(200,json=[])
    http=httpx.Client(transport=httpx.MockTransport(transport))
    def factory(url,key,options):
        assert options.postgrest_client_timeout==3
        options.httpx_client=http
        return create_client(url,key,options=options)
    monkeypatch.setattr(m,"create_client",factory)
    m.probe_supabase()
    assert len(requests)==1
    assert requests[0].url.path=="/rest/v1/products"
    assert requests[0].headers["authorization"]=="Bearer offline-anon-key"
    assert requests[0].url.params["limit"]=="1"
    http.close()


def test_chroma_probe_does_not_create_missing_database_or_collection(backend,monkeypatch,tmp_path):
    import sys
    m=importlib.import_module("src.health")
    monkeypatch.setattr(m,"settings",SimpleNamespace(vector_db_absolute_path=str(tmp_path)))
    with pytest.raises(FileNotFoundError): m.probe_chroma()
    (tmp_path/"chroma.sqlite3").touch()
    def client(path):
        assert path==str(tmp_path)
        return SimpleNamespace(get_collection=lambda name:SimpleNamespace(count=lambda:7))
    monkeypatch.setitem(sys.modules,"chromadb",SimpleNamespace(PersistentClient=client))
    assert m.probe_chroma()==7
