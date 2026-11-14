import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def seed():
    path = Path(__file__).resolve().parents[2] / "scripts" / "seed_bench.py"
    spec = importlib.util.spec_from_file_location("seed_bench_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text(".env.bench\n*.env.bench\n", encoding="utf-8")
    return tmp_path


def test_cases_preserve_unicode_and_resolve_only_bench_aliases(seed, tmp_path):
    path = tmp_path / "cases.jsonl"
    record = {"case_id": "review-1", "table": "reviews", "fields": {
        "product_id": 1, "user_id": "bench_customer_a", "rating": 5, "comment": "Tốt\u200b👍\U000e0001"}}
    path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    cases = seed.read_cases(path)
    assert cases == [record]
    users = {"bench_customer_a": "11111111-1111-4111-8111-111111111111"}
    resolved = seed.resolve_cases(cases, "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", users)
    assert resolved[0]["fields"]["comment"] == "Tốt\u200b👍\U000e0001"
    assert resolved[0]["fields"]["user_id"] == users["bench_customer_a"]
    assert resolved == seed.resolve_cases(cases, "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", users)
    assert record["fields"]["user_id"] == "bench_customer_a"


@pytest.mark.parametrize("patch", [
    {"table": "products"}, {"case_id": ""}, {"label": "attack"},
    {"fields": {"user_id": "real-user", "product_id": 1, "rating": 5}},
    {"fields": {"user_id": "bench_admin", "product_id": 1, "rating": 5}},
    {"fields": {"user_id": "bench_customer_a", "product_id": 1, "rating": 0}},
    {"fields": {"user_id": "bench_customer_a", "product_id": 1, "rating": 5, "comment": "x" * 1001}},
])
def test_invalid_cases_rejected_before_any_credentials_or_network(seed, tmp_path, patch):
    record = {"case_id": "r1", "table": "reviews", "fields": {"user_id": "bench_customer_a", "product_id": 1, "rating": 5}, **patch}
    path = tmp_path / "cases.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(seed.SeedError):
        seed.read_cases(path)


def test_duplicate_case_ids_are_rejected(seed, tmp_path):
    record = {"case_id": "r1", "table": "reviews", "fields": {"user_id": "bench_customer_a", "product_id": 1, "rating": 5}}
    path = tmp_path / "cases.jsonl"
    path.write_text((json.dumps(record) + "\n") * 2, encoding="utf-8")
    with pytest.raises(seed.SeedError):
        seed.read_cases(path)


def test_credentials_are_generated_once_ignored_and_project_bound(seed, repo):
    values = seed.load_credentials(repo, "https://offline.supabase.invalid")
    again = seed.load_credentials(repo, "https://offline.supabase.invalid")
    assert values == again
    assert values["BENCH_CUSTOMER_EMAIL"].startswith("bench_customer_a+")
    assert len(values["BENCH_CUSTOMER_PASSWORD"]) >= 32
    assert len({values[key] for key in values if key.endswith("PASSWORD")}) == 3
    assert (repo / ".env.bench").exists()
    assert not subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=repo, capture_output=True, text=True).stdout.count(".env.bench")
    with pytest.raises(seed.SeedError):
        seed.load_credentials(repo, "https://different.supabase.invalid")


def test_unignored_credentials_are_refused_before_write(seed, tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    with pytest.raises(seed.SeedError):
        seed.load_credentials(tmp_path, "https://offline.supabase.invalid")
    assert not (tmp_path / ".env.bench").exists()


def test_owned_accounts_get_roles_and_existing_users_are_not_reset(seed, repo):
    credentials = seed.load_credentials(repo, "https://offline.supabase.invalid")
    users, creates, roles, signins = [], [], [], []
    def create_user(payload):
        creates.append(payload)
        user = SimpleNamespace(id=str(len(users) + 1), email=payload["email"], app_metadata=payload["app_metadata"])
        users.append(user)
        return SimpleNamespace(user=user)
    admin = SimpleNamespace(auth=SimpleNamespace(admin=SimpleNamespace(list_users=lambda **kw: users, create_user=create_user)),
        table=lambda name: SimpleNamespace(upsert=lambda payload, **kw: SimpleNamespace(execute=lambda: roles.append((name, payload)))))
    def signin(payload):
        signins.append(payload)
        return SimpleNamespace(user=next(user for user in users if user.email == payload["email"]))
    login = SimpleNamespace(auth=SimpleNamespace(sign_in_with_password=signin))
    first = seed.ensure_accounts(admin, login, credentials)
    assert seed.ensure_accounts(admin, login, credentials) == first
    assert len(creates) == 3 and len(signins) == 6
    assert len(first) == 3
    assert any(name == "user_roles" and payload["role"] == "admin" for name, payload in roles)
    assert all("role" not in payload.get("user_metadata", {}) for payload in creates)
    users[0].app_metadata = {}
    with pytest.raises(seed.SeedError):
        seed.ensure_accounts(admin, login, credentials)
    assert len(creates) == 3


def test_dry_run_and_lock_failure_do_not_write_credentials(seed, repo, capsys, monkeypatch):
    path = repo / "cases.jsonl"
    path.write_text('', encoding="utf-8")
    monkeypatch.setattr(seed, "ROOT", repo)
    assert seed.main(["--cases", str(path), "--dry-run"]) == 0
    assert not (repo / ".env.bench").exists()
    (repo / ".seed-bench.lock").write_text("active", encoding="utf-8")
    assert seed.main(["--cases", str(path)]) == 1
    assert not (repo / ".env.bench").exists()
    assert (repo / ".seed-bench.lock").read_text(encoding="utf-8") == "active"


def test_existing_credentials_must_keep_exact_synthetic_email(seed, repo):
    values = seed.load_credentials(repo, "https://offline.supabase.invalid")
    path = repo / ".env.bench"
    path.write_text(path.read_text(encoding="utf-8").replace(values["BENCH_CUSTOMER_EMAIL"], "bench_customer_a+real@example.com"), encoding="utf-8")
    with pytest.raises(seed.SeedError):
        seed.load_credentials(repo, "https://offline.supabase.invalid")


def test_real_auth_sdk_keeps_admin_bearer_after_customer_signins(seed,repo):
    import base64
    import time
    import httpx
    from uuid import uuid4
    from supabase import create_client, ClientOptions
    credentials=seed.load_credentials(repo,"https://offline.supabase.invalid")
    users=[];requests=[]
    def b64(value):
        return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip('=')
    def transport(request):
        requests.append(request)
        if request.url.path=="/auth/v1/admin/users":
            if request.method=="GET": return httpx.Response(200,json={"users":users})
            body=json.loads(request.content)
            user={"id":str(uuid4()),"email":body["email"],"app_metadata":body["app_metadata"],
                  "user_metadata":body["user_metadata"],"aud":"authenticated","created_at":"2026-11-01T00:00:00Z"}
            users.append(user)
            return httpx.Response(200,json=user)
        if request.url.path=="/auth/v1/token":
            body=json.loads(request.content)
            user=next(u for u in users if u["email"]==body["email"])
            token=b64({"alg":"HS256","typ":"JWT"})+'.'+b64({"sub":user["id"],"exp":int(time.time())+3600,"role":"authenticated"})+'.dGVzdA'
            return httpx.Response(200,json={"access_token":token,"token_type":"bearer","expires_in":3600,"refresh_token":"offline-refresh","user":user})
        if request.url.path=="/rest/v1/user_roles":return httpx.Response(201,json=[])
        raise AssertionError("Unexpected SDK path")
    http=httpx.Client(transport=httpx.MockTransport(transport))
    options=lambda:ClientOptions(httpx_client=http,persist_session=False,auto_refresh_token=False)
    admin=create_client("https://offline.supabase.invalid","offline-service-key",options=options())
    login=create_client("https://offline.supabase.invalid","offline-anon-key",options=options())
    result=seed.ensure_accounts(admin,login,credentials)
    assert len(result)==3
    roles=[r for r in requests if r.url.path=="/rest/v1/user_roles"]
    assert len(roles)==3
    assert all(r.headers["authorization"]=="Bearer offline-service-key" for r in roles)
    assert all("role" not in u["user_metadata"] for u in users)
    http.close()


def test_catalog_mapping_uses_existing_ids_and_keeps_order_review_links(seed):
    original=[{"case_id":"o","table":"orders","fields":{"user_id":"bench_customer_a","items":[{"product_id":1,"quantity":1}]}},
              {"case_id":"r","table":"reviews","fields":{"user_id":"bench_customer_a","product_id":1,"rating":5,"comment":"Tốt\u200b"}}]
    calls=[]
    class Query:
        def select(self,columns):calls.append(("select",columns));return self
        def order(self,column):calls.append(("order",column));return self
        def limit(self,n):calls.append(("limit",n));return self
        def execute(self):return SimpleNamespace(data=[{"id":42}])
    admin=SimpleNamespace(table=lambda name:Query() if name=="products" else None)
    mapped=seed.use_catalog_products(admin,original)
    assert mapped[0]["fields"]["items"][0]["product_id"]==42
    assert mapped[1]["fields"]["product_id"]==42
    assert mapped[1]["fields"]["comment"]=="Tốt\u200b"
    assert original[0]["fields"]["items"][0]["product_id"]==1
    assert calls==[("select","id"),("order","id"),("limit",1)]


def test_email_address_invalid_stops_without_domain_fallback(seed,repo,monkeypatch,capsys):
    import supabase
    class InvalidEmail(Exception):code="email_address_invalid"
    path=repo/"cases.jsonl";path.write_text('',encoding="utf-8")
    monkeypatch.setattr(seed,"ROOT",repo)
    for key,value in {"SUPABASE_URL":"https://offline.supabase.invalid","SUPABASE_SERVICE_ROLE_KEY":"offline-service","SUPABASE_ANON_KEY":"offline-anon"}.items():
        monkeypatch.setenv(key,value)
    query=SimpleNamespace(execute=lambda:None)
    db=SimpleNamespace(table=lambda name:SimpleNamespace(select=lambda column:SimpleNamespace(limit=lambda n:query)))
    monkeypatch.setattr(supabase,"create_client",lambda *args,**kwargs:db)
    attempts=[]
    def accounts(*args):
        attempts.append(1)
        raise InvalidEmail("must not print address/password")
    monkeypatch.setattr(seed,"ensure_accounts",accounts)
    assert seed.main(["--cases",str(path)])==1
    captured=capsys.readouterr()
    assert "SEED_EMAIL_ADDRESS_INVALID_CONTACT_CLAUDE" in captured.err
    assert "address/password" not in captured.err
    assert attempts==[1]
    credentials=seed.load_credentials(repo,"https://offline.supabase.invalid")
    assert all(credentials[prefix+"_EMAIL"].endswith("@example.invalid") for prefix in seed.ACCOUNTS.values())
