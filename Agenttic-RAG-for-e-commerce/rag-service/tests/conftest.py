"""Offline service boundaries; the API, agent and LangGraph memory stay real."""

import importlib
import sys
from types import ModuleType, SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import MemorySaver


def stream_chunk(*, text=None, tool=None):
    part = SimpleNamespace(
        text=text,
        function_call=SimpleNamespace(name=tool, args={"queries": []}) if tool else None,
        thought_signature=None,
    )
    return [SimpleNamespace(
        usage_metadata=SimpleNamespace(prompt_token_count=7, candidates_token_count=3),
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))],
    )]


@pytest.fixture(scope="session")
def backend():
    # Do not load .env, construct retrievers, open Chroma or contact Supabase.
    # Keep registry and tools real; replace only external vector retrievers.
    patch = pytest.MonkeyPatch()
    settings_module = ModuleType("configs.setting")
    settings_module.settings = SimpleNamespace(
        DEBUG=False,
        SUPABASE_URL="https://offline.supabase.invalid",
        SUPABASE_ANON_KEY="offline-anon-key",
        SUPABASE_SERVICE_ROLE_KEY="offline-service-key",
    )
    patch.setitem(sys.modules, "configs.setting", settings_module)
    for module_name, class_name in (("product_retriever", "ProductRetriever"), ("policy_retriever", "PolicyRetriever")):
        retriever_module = ModuleType(f"src.c_retrieval.{module_name}")
        setattr(retriever_module, class_name, lambda **kwargs: SimpleNamespace(retrieve=lambda **kw: []))
        patch.setitem(sys.modules, retriever_module.__name__, retriever_module)
    workflow = importlib.import_module("src.g_pipelines.workflow_1.workflow_1")
    main = importlib.import_module("app.main")
    security = importlib.import_module("app.core.security")
    yield SimpleNamespace(workflow=workflow, main=main, security=security)
    patch.undo()


@pytest.fixture
def client(backend, monkeypatch):
    workflow = backend.workflow
    original_table = backend.security.supabase_admin_client.table
    def offline_logs(name):
        if name == "chat_logs":
            return SimpleNamespace(insert=lambda rows: SimpleNamespace(execute=lambda: SimpleNamespace(data=[])))
        return original_table(name)
    monkeypatch.setattr(backend.security.supabase_admin_client, "table", offline_logs)
    monkeypatch.setattr(backend.main, "workflow_app", workflow.builder.compile(checkpointer=MemorySaver()))
    users = {
        "token-a": "11111111-1111-4111-8111-111111111111",
        "token-a-refreshed": "11111111-1111-4111-8111-111111111111",
        "token-b": "22222222-2222-4222-8222-222222222222",
    }

    def get_user(token):
        user_id = users.get(token)
        return SimpleNamespace(user=SimpleNamespace(id=user_id) if user_id else None)

    monkeypatch.setattr(backend.security.supabase_anon_client.auth, "get_user", get_user)
    monkeypatch.setattr(workflow.guardrail_call, "invoke", lambda query: {
        "risk_level": "safe", "latency": 0, "tokens": {"input": 0, "output": 0},
    })

    def echo_history(**kwargs):
        queries = []
        for message in kwargs["messages"]:
            role = message.get("role") if isinstance(message, dict) else message.type
            if role in ("user", "human"):
                queries.append(message["content"] if isinstance(message, dict) else message.content)
        return stream_chunk(text=" | ".join(queries))

    monkeypatch.setattr(workflow.llm_service, "call_gemini", echo_history)
    with TestClient(backend.main.app) as test_client:
        yield test_client
