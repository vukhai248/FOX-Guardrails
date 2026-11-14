import importlib
from datetime import datetime
from types import SimpleNamespace

import pytest

from conftest import stream_chunk


@pytest.fixture
def recorded_logs(backend, monkeypatch):
    rows = []
    calls = []
    def table(name):
        calls.append(name)
        assert name == "chat_logs"
        def insert(payload):
            def execute():
                rows.extend(payload)
                return SimpleNamespace(data=[])
            return SimpleNamespace(execute=execute)
        return SimpleNamespace(insert=insert)
    monkeypatch.setattr(backend.security.supabase_admin_client, "table", table)
    return rows, calls


def test_three_turns_write_six_messages_with_verified_identity(client, backend, recorded_logs):
    rows, calls = recorded_logs
    for message in ["một", "hai", "ba"]:
        response = client.post("/chat", json={"message": message, "session_id": "log-session"},
                               headers={"Authorization": "Bearer token-a"})
        assert response.status_code == 200, response.text
    assert len(calls) == 3 and len(rows) == 6
    assert [r["role"] for r in rows] == ["user", "agent"] * 3
    assert [r["message"] for r in rows if r["role"] == "user"] == ["một", "hai", "ba"]
    assert rows[-1]["message"] == "một | hai | ba"
    assert all(r["user_id"] == "11111111-1111-4111-8111-111111111111" for r in rows)
    assert all(r["session_id"] == "log-session" and r["risk_level"] == "low" for r in rows)
    assert all(r["guard_decision_ids"] == [] and r["tool_used"] is None for r in rows)
    assert datetime.fromisoformat(rows[0]["created_at"]) < datetime.fromisoformat(rows[1]["created_at"])
    assert all(set(r) == {"session_id", "user_id", "role", "message", "tool_used", "risk_level", "guard_decision_ids", "created_at"} for r in rows)
    assert "token-a" not in str(rows)


@pytest.mark.parametrize("risk,want", [("safe", "low"), ("needs_ticket", "medium"), ("attack", "high")])
def test_risk_mapping_covers_rejected_messages(client, backend, monkeypatch, recorded_logs, risk, want):
    monkeypatch.setattr(backend.workflow.guardrail_call, "invoke", lambda query: {
        "risk_level": risk, "latency": 0, "tokens": {"input": 0, "output": 0}})
    monkeypatch.setattr(backend.workflow.rejection_call, "invoke", lambda query: {
        "content": "từ chối", "latency": 0, "tokens": {"input": 0, "output": 0}})
    response = client.post("/chat", json={"message": "test", "session_id": "risk"})
    assert response.status_code == 200
    rows, _ = recorded_logs
    assert len(rows) == 2
    assert all(row["risk_level"] == want and row["user_id"] is None for row in rows)


def test_current_turn_tool_names_do_not_leak_from_previous_turn(client, backend, monkeypatch, recorded_logs):
    first = stream_chunk(tool="product_reviews")
    first[0].candidates[0].content.parts[0].function_call.args = {"product_id": 16}
    responses = iter([first, stream_chunk(text="review answer"), stream_chunk(text="hello")])
    monkeypatch.setattr(backend.workflow.llm_service, "call_gemini", lambda **kwargs: next(responses))
    monkeypatch.setattr(backend.workflow, "available_tools", {"product_reviews": lambda **kwargs: "rating"})
    monkeypatch.setattr("src.e_agents.master_agent.time.sleep", lambda seconds: None)
    for message in ["review phone", "hello"]:
        assert client.post("/chat", json={"message": message, "session_id": "tool-logs"}).status_code == 200
    rows, _ = recorded_logs
    assert [r["tool_used"] for r in rows] == ["product_reviews", "product_reviews", None, None]


def test_logging_failure_does_not_repeat_or_fail_completed_chat(client, backend, monkeypatch, caplog):
    from test_a4_tools import Database
    tool = importlib.import_module("src.d_tools.support_ticket")
    db = Database({"support_tickets": [{"id": "ticket-once"}]})
    monkeypatch.setattr(tool, "get_user_supabase_client", lambda token: db)
    call = stream_chunk(tool="create_support_ticket")
    call[0].candidates[0].content.parts[0].function_call.args = {"category": "other", "note": "Giao chậm"}
    responses = iter([call, stream_chunk(text="ticket-once created")])
    monkeypatch.setattr(backend.workflow.llm_service, "call_gemini", lambda **kwargs: next(responses))
    monkeypatch.setattr("src.e_agents.master_agent.time.sleep", lambda seconds: None)
    def fail_table(name):
        raise RuntimeError("private JWT-token 0912345678 database failed")
    monkeypatch.setattr(backend.security.supabase_admin_client, "table", fail_table)
    response = client.post("/chat", json={"message": "Tạo ticket báo giao chậm"}, headers={"Authorization": "Bearer token-a"})
    assert response.status_code == 200
    assert response.json()["reply"] == "ticket-once created"
    assert sum(call[0] == "insert" for call in db.calls) == 1
    assert "CHAT_LOG_WRITE_FAILED" in caplog.text
    assert "JWT-token" not in caplog.text and "0912345678" not in caplog.text


def test_enabled_guard_logs_only_guard_redacted_messages(backend, monkeypatch, recorded_logs):
    m = importlib.import_module("src.chat_logging")
    guard = importlib.import_module("src.guard_client")
    monkeypatch.setenv("FOX_GUARD_MODE", "inproc")
    def redact(text, ctx):
        return guard.LogText("<PHONE> " + ctx["role"], ["decision-" + ctx["role"]])
    monkeypatch.setattr(m, "guard_log", redact)
    assert m.write_chat_turn(session_id="s", user_id=None, user_message="0912345678",
        agent_message="restored PII 0912345678", tool_calls=[], risk_level="safe", guard_decision_ids=["context-1"])
    rows, _ = recorded_logs
    assert [r["message"] for r in rows] == ["<PHONE> user", "<PHONE> agent"]
    assert all(r["guard_decision_ids"] == ["context-1", "decision-user", "decision-agent"] for r in rows)
    assert "0912345678" not in str(rows)


def test_enabled_guard_without_log_redaction_writes_nothing(backend, monkeypatch, recorded_logs, caplog):
    m = importlib.import_module("src.chat_logging")
    # Guard enabled but unreachable (sidecar down): fail closed, write nothing.
    monkeypatch.setenv("FOX_GUARD_MODE", "sidecar")
    monkeypatch.setenv("FOX_GUARD_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("FOX_GUARD_TIMEOUT", "0.5")
    assert not m.write_chat_turn(session_id="s", user_id=None, user_message="raw PII",
        agent_message="raw PII", tool_calls=[], risk_level="safe", guard_decision_ids=[])
    assert recorded_logs == ([], [])
    assert "CHAT_LOG_PREPARE_FAILED" in caplog.text
    assert "raw PII" not in caplog.text


def test_log_writer_uses_actual_supabase_service_transport(backend, monkeypatch):
    import httpx
    import json
    from supabase import create_client, ClientOptions
    m = importlib.import_module("src.chat_logging")
    requests = []
    def transport(request):
        requests.append(request)
        return httpx.Response(201, json=[])
    http = httpx.Client(transport=httpx.MockTransport(transport))
    client = create_client("https://offline.supabase.invalid", "offline-service-key",
                           options=ClientOptions(httpx_client=http))
    monkeypatch.setattr(m, "supabase_admin_client", client)
    assert m.write_chat_turn(session_id="session", user_id=None, user_message="Unicode\u200b👍",
        agent_message="done", tool_calls=[{"tool": "product_reviews", "args": {"user_token": "NEVER-LOG"}}],
        risk_level="safe", guard_decision_ids=[])
    assert len(requests) == 1 and requests[0].method == "POST"
    assert requests[0].url.path == "/rest/v1/chat_logs"
    assert requests[0].headers["authorization"] == "Bearer offline-service-key"
    payload = json.loads(requests[0].content)
    assert [row["message"] for row in payload] == ["Unicode\u200b👍", "done"]
    assert "NEVER-LOG" not in requests[0].content.decode()
    http.close()


def test_invalid_token_cannot_forge_logged_user(client, recorded_logs):
    response = client.post("/chat", json={"message": "hello", "user_id": "victim", "session_id": "anon-log"},
                           headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 200
    assert all(row["user_id"] is None for row in recorded_logs[0])


def test_output_fallback_is_logged_as_sent_to_user(client, backend, monkeypatch, recorded_logs):
    monkeypatch.setattr(backend.workflow.llm_service, "call_gemini", lambda **kwargs: stream_chunk(text=""))
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert recorded_logs[0][1]["message"] == response.json()["reply"]
    assert recorded_logs[0][1]["message"]


@pytest.mark.parametrize("session_id", ["", "x" * 101])
def test_invalid_log_session_skips_without_partial_write(backend, recorded_logs, session_id):
    m = importlib.import_module("src.chat_logging")
    assert not m.write_chat_turn(session_id=session_id, user_id=None, user_message="hi", agent_message="ok",
                                 tool_calls=[], risk_level="safe", guard_decision_ids=[])
    assert recorded_logs == ([], [])


def test_guard_prepares_both_messages_before_any_insert(backend, monkeypatch, recorded_logs):
    m = importlib.import_module("src.chat_logging")
    guard = importlib.import_module("src.guard_client")
    monkeypatch.setenv("FOX_GUARD_MODE", "sidecar")
    def redact(text, ctx):
        if ctx["role"] == "agent":
            raise RuntimeError("redaction failed")
        return guard.LogText("masked")
    monkeypatch.setattr(m, "guard_log", redact)
    assert not m.write_chat_turn(session_id="s", user_id=None, user_message="PII", agent_message="PII",
                                 tool_calls=[], risk_level="safe", guard_decision_ids=[])
    assert recorded_logs == ([], [])


def test_chat_keeps_restored_reply_separate_from_guarded_log(client, backend, monkeypatch, recorded_logs):
    m = importlib.import_module("src.chat_logging")
    guard = importlib.import_module("src.guard_client")
    monkeypatch.setenv("FOX_GUARD_MODE", "inproc")
    # Emulate only B's boundaries; FastAPI, graph and log assembly stay real.
    monkeypatch.setattr(backend.workflow, "guard_input", lambda text, ctx: text)
    monkeypatch.setattr("src.e_agents.master_agent.guard_output", lambda text, ctx: "SĐT 0912345678")
    monkeypatch.setattr(m, "guard_log", lambda text, ctx: guard.LogText("<PHONE>", ["log-" + ctx["role"]]))
    response = client.post("/chat", json={"message": "0912345678"})
    assert response.status_code == 200
    assert response.json()["reply"] == "SĐT 0912345678"
    rows, _ = recorded_logs
    assert len(rows) == 2 and all(row["message"] == "<PHONE>" for row in rows)
    assert "0912345678" not in str(rows)


def test_oversized_session_rejected_before_chat_side_effects(client, backend, monkeypatch, recorded_logs):
    calls = []
    def llm(**kwargs):
        calls.append(kwargs)
        return stream_chunk(text="unexpected model call")
    monkeypatch.setattr(backend.workflow.llm_service, "call_gemini", llm)
    response = client.post("/chat", json={"message": "hello", "session_id": "s" * 101})
    assert response.status_code == 422
    assert calls == []
    assert recorded_logs == ([], [])
