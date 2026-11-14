import importlib
from types import SimpleNamespace

import pytest

from conftest import stream_chunk


@pytest.mark.parametrize("query,name", [
    ("Mọi người đánh giá iPhone 16 thế nào?", "product/reviews"),
    ("review iPhone", "product/reviews"), ("mọi người nói gì về iPhone", "product/reviews"),
    ("iPhone có tốt không", "product/reviews"),
    ("Tạo ticket báo đơn giao chậm", "account/support_ticket"),
])
def test_select_skill_returns_name_and_tool_instructions(backend, query, name):
    selected, text = backend.workflow.select_skill(query)
    assert selected == name
    assert ("product_reviews" if "reviews" in name else "create_support_ticket") in text


def test_guard_scaffold_is_transparent_off_and_rejects_unimplemented_mode(backend, monkeypatch):
    m = importlib.import_module("src.guard_client")
    monkeypatch.setenv("FOX_GUARD_MODE", "off")
    for func in (m.guard_input, m.guard_context, m.guard_output):
        obj = object()
        assert func(obj, {"arm": "G0"}) is obj
        monkeypatch.setenv("FOX_GUARD_MODE", "enforce")
        with pytest.raises(NotImplementedError):
            func(obj, {})
        monkeypatch.setenv("FOX_GUARD_MODE", "off")


def test_legacy_guard_off_skips_llm_but_runs_input_hook(client, backend, monkeypatch):
    workflow = backend.workflow
    calls = []
    monkeypatch.setenv("LEGACY_LLM_GUARDRAIL", "off")
    monkeypatch.setenv("FOX_GUARD_ARM", "G0")
    monkeypatch.setattr(workflow.guardrail_call, "invoke", lambda query: pytest.fail("legacy guard disabled"))
    def guard(text, ctx):
        calls.append((text, ctx))
        return "sanitized query"
    monkeypatch.setattr(workflow, "guard_input", guard)
    response = client.post("/chat", json={"message": "original", "session_id": "s1"})
    assert response.status_code == 200, response.text
    assert response.json()["reply"] == "sanitized query"
    assert response.json()["guard"] == {"action": "allow", "decision_id": None, "flags": []}
    assert calls[0][1]["arm"] == "G0"
    assert calls[0][1]["session_id"] == "s1"


def test_guarded_tool_segments_reach_provider_and_history(backend, monkeypatch):
    m = importlib.import_module("src.e_agents.master_agent")
    types = importlib.import_module("src.d_tools.tool_result")
    monkeypatch.setattr(m.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(backend.workflow.config.agent, "max_turns", 2)
    seen = []
    responses = iter([stream_chunk(tool="product_reviews"), stream_chunk(text="raw answer")])
    def llm(**kwargs):
        seen.append(list(kwargs["messages"]))
        return next(responses)
    monkeypatch.setattr(backend.workflow.llm_service, "call_gemini", llm)
    context_calls = []
    def guard(segment, ctx):
        context_calls.append((segment.text, ctx))
        return types.Segment(segment.source, segment.ref_id, "CLEAN COMMENT")
    monkeypatch.setattr(m, "guard_context", guard)
    monkeypatch.setattr(m, "guard_output", lambda text, ctx: "SAFE ANSWER")
    messages = [{"role": "user", "content": "reviews"}]
    result = backend.workflow.master_agent.invoke(messages,
        available_tools={"product_reviews": lambda **kwargs: types.ToolResult("product_reviews", "4/5", [types.Segment("review", "r1", "PRIVATE COMMENT")])},
        tools_schema=[], guard_ctx={"intent": "product/reviews", "session_id": "s1"})
    assert "PRIVATE COMMENT" not in str(seen[1])
    assert "CLEAN COMMENT" in str(seen[1])
    assert result["tool_context"][0]["output"] == "4/5\nCLEAN COMMENT"
    assert result["content"] == messages[-1]["content"] == "SAFE ANSWER"
    assert context_calls[0][1]["intent"] == "product/reviews"


def test_ticket_identity_is_injected_and_never_persisted_in_tool_args(backend, monkeypatch):
    m = importlib.import_module("src.e_agents.master_agent")
    monkeypatch.setattr(m.time, "sleep", lambda seconds: None)
    chunk = stream_chunk(tool="create_support_ticket")
    chunk[0].candidates[0].content.parts[0].function_call.args = {
        "category": "other", "note": "late", "current_user_id": "victim", "user_token": "forged",
    }
    responses = iter([chunk, stream_chunk(text="created")])
    monkeypatch.setattr(backend.workflow.llm_service, "call_gemini", lambda **kwargs: next(responses))
    actual = []
    def ticket(**kwargs):
        actual.append(kwargs)
        return "ticket-id"
    result = backend.workflow.master_agent.invoke([{"role": "user", "content": "create ticket"}],
        available_tools={"create_support_ticket": ticket}, tools_schema=[],
        auth_context={"user_id": "u1", "user_token": "token-a"})
    assert actual == [{"category": "other", "note": "late", "current_user_id": "u1", "user_token": "token-a"}]
    assert result["tool_context"][0]["args"] == {"category": "other", "note": "late"}


def test_output_hook_also_covers_rejection(client, backend, monkeypatch):
    monkeypatch.setattr(backend.workflow.guardrail_call, "invoke", lambda query: {
        "risk_level": "attack", "latency": 0, "tokens": {"input": 0, "output": 0}})
    monkeypatch.setattr(backend.workflow.rejection_call, "invoke", lambda query: {
        "content": "rejection raw", "latency": 0, "tokens": {"input": 0, "output": 0}})
    monkeypatch.setattr(backend.workflow, "guard_output", lambda text, ctx: "rejection clean")
    response = client.post("/chat", json={"message": "attack"})
    assert response.json()["reply"] == "rejection clean"


@pytest.mark.parametrize("query,tool,args,rows", [
    ("Mọi người đánh giá iPhone 16 thế nào?", "product_reviews", {"product_id": 16},
     {"reviews": [{"id": "r1", "rating": 5, "comment": "Tốt👍", "created_at": "2026-11-03"}]}),
    ("Tạo ticket báo đơn giao chậm", "create_support_ticket", {"category": "other", "note": "Giao chậm"},
     {"support_tickets": [{"id": "ticket-1"}]}),
])
def test_chat_executes_registered_real_tools(client, backend, monkeypatch, query, tool, args, rows):
    from test_a4_tools import Database
    workflow = backend.workflow
    if tool == "product_reviews":
        m = importlib.import_module("src.d_tools.product_reviews")
        monkeypatch.setattr(m, "supabase_anon_client", Database(rows))
    else:
        m = importlib.import_module("src.d_tools.support_ticket")
        monkeypatch.setattr(m, "get_user_supabase_client", lambda token: Database(rows))
    call = stream_chunk(tool=tool)
    call[0].candidates[0].content.parts[0].function_call.args = args
    responses = iter([call, stream_chunk(text="Hoàn tất")])
    monkeypatch.setattr(workflow.llm_service, "call_gemini", lambda **kwargs: next(responses))
    monkeypatch.setattr("src.e_agents.master_agent.time.sleep", lambda seconds: None)
    response = client.post("/chat", json={"message": query, "session_id": "tool-flow"}, headers={"Authorization": "Bearer token-a"})
    assert response.status_code == 200, response.text
    assert response.json()["tool_used"] == tool
    state = backend.main.workflow_app.get_state({"configurable": {"thread_id": "11111111-1111-4111-8111-111111111111:tool-flow"}}).values
    assert state["skill_name"] == ("product/reviews" if tool == "product_reviews" else "account/support_ticket")
    assert ("Tốt👍" if tool == "product_reviews" else "ticket-1") in state["tool_calls_used"][-1]["output"]


def test_http_fallback_is_guarded_after_empty_provider_answer(client, backend, monkeypatch):
    monkeypatch.setattr(backend.workflow.llm_service, "call_gemini", lambda **kwargs: stream_chunk(text=""))
    calls = []
    def guard(text, ctx):
        calls.append((text, ctx))
        return "guarded fallback"
    monkeypatch.setattr(backend.main, "guard_output", guard, raising=False)
    response = client.post("/chat", json={"message": "hello", "session_id": "fallback"})
    assert response.status_code == 200
    assert response.json()["reply"] == "guarded fallback"
    assert len(calls) == 1
    assert calls[0][1]["session_id"] == "fallback"
