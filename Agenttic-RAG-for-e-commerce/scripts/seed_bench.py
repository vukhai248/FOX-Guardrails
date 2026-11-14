"""Seed synthetic benchmark data after owner-approved migrations. Never prints secrets."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from uuid import UUID, uuid4, uuid5

ROOT = Path(__file__).resolve().parent.parent
ACCOUNTS = {"bench_customer_a": "BENCH_CUSTOMER", "bench_customer_b": "BENCH_CUSTOMER_B", "bench_admin": "BENCH_ADMIN"}
CUSTOMERS = {"bench_customer_a", "bench_customer_b"}


class SeedError(Exception):
    pass


def read_cases(path):
    if path.stat().st_size > 20_000_000:
        raise SeedError("CASES_TOO_LARGE")
    cases, seen = [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            case = json.loads(line)
            if not isinstance(case, dict) or set(case) != {"case_id", "table", "fields"}:
                raise ValueError()
            case_id, table, fields = case["case_id"], case["table"], case["fields"]
            if not isinstance(case_id, str) or not 1 <= len(case_id) <= 200 or case_id in seen:
                raise ValueError()
            if table not in ("orders", "reviews") or not isinstance(fields, dict) or fields.get("user_id") not in CUSTOMERS:
                raise ValueError()
            allowed = {"user_id", "product_id", "rating", "comment", "created_at"} if table == "reviews" else {
                "user_id", "items", "status", "payment_status", "payment_method", "recipient_name", "recipient_phone",
                "address_line", "ward", "province", "note", "created_at"}
            if set(fields) - allowed:
                raise ValueError()
            if table == "reviews":
                if type(fields.get("product_id")) is not int or fields["product_id"] < 1 or type(fields.get("rating")) is not int or not 1 <= fields["rating"] <= 5:
                    raise ValueError()
            else:
                items = fields.get("items")
                if not isinstance(items, list) or not 1 <= len(items) <= 100:
                    raise ValueError()
                for item in items:
                    if not isinstance(item, dict) or set(item) != {"product_id", "quantity"}:
                        raise ValueError()
                    if type(item["product_id"]) is not int or item["product_id"] < 1 or type(item["quantity"]) is not int or not 1 <= item["quantity"] <= 10000:
                        raise ValueError()
                for key, values in {"status": {"pending", "processing", "shipping", "delivered", "cancelled"},
                                    "payment_method": {"cod", "stripe"},
                                    "payment_status": {"unpaid", "paid", "cod_pending", "refunded", "failed"}}.items():
                    if key in fields and fields[key] not in values:
                        raise ValueError()
            for key, bound in {"comment": 1000, "note": 500, "recipient_name": 200, "recipient_phone": 30,
                               "address_line": 500, "ward": 200, "province": 200}.items():
                if key in fields and (not isinstance(fields[key], str) or len(fields[key]) > bound):
                    raise ValueError()
            if "created_at" in fields:
                from datetime import datetime
                if not datetime.fromisoformat(fields["created_at"].replace("Z", "+00:00")).tzinfo:
                    raise ValueError()
            seen.add(case_id)
            cases.append(case)
            if len(cases) > 5000:
                raise ValueError()
        except (ValueError, TypeError, KeyError, AttributeError):
            raise SeedError("INVALID_OR_DUPLICATE_CASE") from None
    return cases


def resolve_cases(cases, namespace, users):
    resolved = []
    for case in cases:
        fields = {**case["fields"], "user_id": users[case["fields"]["user_id"]]}
        payload_hash = hashlib.sha256(json.dumps(case, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        resolved.append({**case, "fields": fields, "row_id": str(uuid5(UUID(namespace), case["table"] + ":" + case["case_id"])),
                         "payload_hash": payload_hash})
    return resolved


def use_catalog_products(admin, cases):
    """Explicit smoke-fixture remapping; preserve relationships, never modify the catalog."""
    placeholders = set()
    for case in cases:
        if case["table"] == "orders":
            placeholders.update(item["product_id"] for item in case["fields"]["items"])
        else:
            placeholders.add(case["fields"]["product_id"])
    mapped = copy.deepcopy(cases)
    if not placeholders:
        return mapped
    rows = admin.table("products").select("id").order("id").limit(len(placeholders)).execute().data or []
    ids = [row.get("id") for row in rows]
    if (len(ids) != len(placeholders) or any(type(value) is not int or value < 1 for value in ids)
            or len(set(ids)) != len(ids)):
        raise SeedError("BENCH_NOT_ENOUGH_CATALOG_PRODUCTS")
    mapping = dict(zip(sorted(placeholders), sorted(ids)))
    for case in mapped:
        if case["table"] == "orders":
            for item in case["fields"]["items"]:
                item["product_id"] = mapping[item["product_id"]]
        else:
            case["fields"]["product_id"] = mapping[case["fields"]["product_id"]]
    return mapped


def require_ignored(root, name):
    if subprocess.run(["git", "check-ignore", "-q", "--", name], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        raise SeedError("CREDENTIAL_PATH_NOT_IGNORED")
    if subprocess.run(["git", "ls-files", "--error-unmatch", "--", name], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        raise SeedError("CREDENTIAL_PATH_TRACKED")


def load_credentials(root, project_url):
    from dotenv import dotenv_values
    path = root / ".env.bench"
    require_ignored(root, path.name)
    if path.is_symlink():
        raise SeedError("CREDENTIAL_SYMLINK")
    if path.exists():
        values = dict(dotenv_values(path))
        if values.get("BENCH_PROJECT_URL") != project_url:
            raise SeedError("CREDENTIAL_PROJECT_MISMATCH")
        try:
            UUID(values["BENCH_NAMESPACE"])
            for alias, prefix in ACCOUNTS.items():
                expected = f"{alias}+{UUID(values['BENCH_NAMESPACE']).hex}@example.invalid"
                if values[prefix + "_EMAIL"] != expected or len(values[prefix + "_PASSWORD"]) < 32:
                    raise ValueError()
        except (KeyError, ValueError, TypeError):
            raise SeedError("CREDENTIAL_FILE_INCOMPLETE") from None
        return values
    namespace = uuid4()
    values = {"BENCH_NAMESPACE": str(namespace), "BENCH_PROJECT_URL": project_url}
    for alias, prefix in ACCOUNTS.items():
        values[prefix + "_EMAIL"] = f"{alias}+{namespace.hex}@example.invalid"
        values[prefix + "_PASSWORD"] = secrets.token_urlsafe(32)
    temp = root / (".seed-" + secrets.token_hex(8) + ".env.bench")
    require_ignored(root, temp.name)
    try:
        with os.fdopen(os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as handle:
            handle.write("# Generated benchmark credentials; never commit or print.\n")
            for key, value in values.items():
                handle.write(key + "=" + json.dumps(value) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()
    return values


def ensure_accounts(admin, login, credentials):
    all_users = []
    page = 1
    while True:
        batch = admin.auth.admin.list_users(page=page, per_page=1000)
        all_users.extend(batch)
        if len(batch) < 1000:
            break
        page += 1
    users = {}
    for alias, prefix in ACCOUNTS.items():
        email, password = credentials[prefix + "_EMAIL"], credentials[prefix + "_PASSWORD"]
        marker = {"bench_seed_namespace": credentials["BENCH_NAMESPACE"], "bench_seed_alias": alias}
        user = next((u for u in all_users if u.email == email), None)
        if user is None:
            user = admin.auth.admin.create_user({"email": email, "password": password, "email_confirm": True,
                                                "app_metadata": marker, "user_metadata": {"full_name": alias}}).user
        if not user or any((user.app_metadata or {}).get(key) != value for key, value in marker.items()):
            raise SeedError("ACCOUNT_OWNERSHIP_MISMATCH")
        # Sign-in never runs on the admin client: it would replace the service-role bearer.
        authenticated = login.auth.sign_in_with_password({"email": email, "password": password})
        if not authenticated or not authenticated.user or authenticated.user.id != user.id:
            raise SeedError("BENCH_LOGIN_FAILED")
        admin.table("user_roles").upsert({"user_id": user.id, "role": "admin" if alias == "bench_admin" else "customer"}, on_conflict="user_id").execute()
        users[alias] = user.id
    return users


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--reset", action="store_true", help="Atomically replace only mapped rows in this namespace")
    parser.add_argument("--dry-run", action="store_true", help="Validate JSONL only: no credentials, accounts or DB changes")
    parser.add_argument("--products-from-db", action="store_true", help="Map smoke-fixture placeholder product IDs to existing catalog IDs")
    args = parser.parse_args(argv)
    lock_fd = None
    lock_path = ROOT / ".seed-bench.lock"
    try:
        cases = read_cases(args.cases)
        if args.dry_run:
            print(json.dumps({"dry_run": True, "valid_cases": len(cases)}))
            return 0
        try:
            lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise SeedError("SEED_ALREADY_RUNNING_OR_STALE_LOCK") from None
        from dotenv import load_dotenv
        from supabase import create_client, ClientOptions
        from urllib.parse import urlsplit
        for env in (ROOT / "rag-service" / ".env", ROOT / "web_ui" / ".env.local"):
            load_dotenv(env, override=False)
        url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        parsed = urlsplit(url or "")
        if not url or not service_key or not anon_key or parsed.username or parsed.query or parsed.fragment or (parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1"}):
            raise SeedError("SEED_CONFIG_MISSING_OR_INVALID")
        admin = create_client(url, service_key, options=ClientOptions(persist_session=False, auto_refresh_token=False))
        # Fail before writing passwords or creating users when migration is not installed.
        admin.table("bench_cases").select("case_id").limit(1).execute()
        if args.products_from_db:
            cases = use_catalog_products(admin, cases)
        credentials = load_credentials(ROOT, url)
        login = create_client(url, anon_key, options=ClientOptions(persist_session=False, auto_refresh_token=False))
        users = ensure_accounts(admin, login, credentials)
        result = admin.rpc("seed_bench_cases", {"p_namespace": credentials["BENCH_NAMESPACE"],
            "p_cases": resolve_cases(cases, credentials["BENCH_NAMESPACE"], users), "p_reset": args.reset}).execute()
        print(json.dumps({"seeded_cases": len(result.data or []), "reset": args.reset, "accounts": 3}))
        return 0
    except SeedError as error:
        print(str(error), file=sys.stderr)
    except Exception as error:
        if getattr(error, "code", None) == "email_address_invalid":
            print("SEED_EMAIL_ADDRESS_INVALID_CONTACT_CLAUDE", file=sys.stderr)
        else:
            print("SEED_FAILED_CHECK_MIGRATIONS_CONFIG_OR_SERVICE", file=sys.stderr)
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
            lock_path.unlink()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
