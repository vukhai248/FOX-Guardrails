"""TokenHarbor is the main LLM, Gemini the fallback; responses keep the Gemini chunk shape."""
import importlib
from types import SimpleNamespace

import pytest

from conftest import stream_chunk


def completion(text=None, tool=None, args="{}"):
    calls = [SimpleNamespace(id="x", function=SimpleNamespace(name=tool, arguments=args))] if tool else None
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text, tool_calls=calls))],
                           usage=SimpleNamespace(prompt_tokens=11, completion_tokens=5))


@pytest.fixture
def llm(backend, monkeypatch):
    service = backend.workflow.llm_service
    monkeypatch.setattr(service.settings, "TOKENHARBOR_API_KEY", "test-key", raising=False)
    monkeypatch.setattr(service, "_tokenharbor_off_until", 0.0)
    return service


def harbor(service, monkeypatch, fn):
    seen = []

    def create(**kwargs):
        seen.append(kwargs)
        return fn(**kwargs)

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(service, "_get_tokenharbor_client", lambda: client)
    return seen


def test_tokenharbor_answers_and_agent_runs_its_tool_call(backend, llm, monkeypatch):
    m = importlib.import_module("src.e_agents.master_agent")
    monkeypatch.setattr(m.time, "sleep", lambda s: None)
    replies = iter([completion(tool="lookup", args='{"q": "iPhone 16"}'), completion(text="Có ạ.")])
    seen = harbor(llm, monkeypatch, lambda **kw: next(replies))
    monkeypatch.setattr(llm, "call_gemini", lambda **kw: pytest.fail("Gemini must not be called"))
    called = []
    result = backend.workflow.master_agent.invoke(
        [{"role": "system", "content": "sys"}, {"role": "user", "content": "iPhone 16?"}],
        available_tools={"lookup": lambda **kw: called.append(kw) or "1 sản phẩm"},
        tools_schema=[{"name": "lookup", "parameters": {"type": "object"}}], guard_ctx={"session_id": "s"})
    assert called == [{"q": "iPhone 16"}] and result["content"] == "Có ạ."
    second = seen[1]["messages"]
    assert second[-2]["tool_calls"][0]["function"]["name"] == "lookup"
    assert "thought_signature" not in str(second)
    assert second[-1]["role"] == "tool" and second[-1]["tool_call_id"] == second[-2]["tool_calls"][0]["id"]
    assert seen[0]["tools"][0]["type"] == "function"


def test_quota_error_falls_back_to_gemini_and_pauses_tokenharbor(llm, monkeypatch):
    def out_of_quota(**kw):
        raise RuntimeError("Error code: 429 - rate limit exceeded")

    seen = harbor(llm, monkeypatch, out_of_quota)
    monkeypatch.setattr(llm, "call_gemini", lambda *a, **kw: stream_chunk(text="gemini"))
    assert llm.call_llm("gemini-x", [{"role": "user", "content": "hi"}])[0].candidates[0].content.parts[0].text \
        == "gemini"
    llm.call_llm("gemini-x", [{"role": "user", "content": "hi"}])
    assert len(seen) == 1  # second turn skipped TokenHarbor (cool-down)


def test_other_error_falls_back_without_pause(llm, monkeypatch):
    def broken(**kw):
        raise ConnectionError("network down")

    seen = harbor(llm, monkeypatch, broken)
    monkeypatch.setattr(llm, "call_gemini", lambda *a, **kw: stream_chunk(text="gemini"))
    llm.call_llm("m", [{"role": "user", "content": "hi"}])
    llm.call_llm("m", [{"role": "user", "content": "hi"}])
    assert len(seen) == 2


def test_no_key_means_gemini_only(backend, monkeypatch):
    service = backend.workflow.llm_service
    monkeypatch.setattr(service.settings, "TOKENHARBOR_API_KEY", "", raising=False)
    monkeypatch.setattr(service, "_get_tokenharbor_client", lambda: pytest.fail("no key: no TokenHarbor"))
    monkeypatch.setattr(service, "call_gemini", lambda *a, **kw: stream_chunk(text="g"))
    assert service.call_llm("m", [{"role": "user", "content": "hi"}])[0].candidates[0].content.parts[0].text == "g"


def test_guardrail_classifier_reads_tokenharbor_text(backend, llm, monkeypatch):
    harbor(llm, monkeypatch, lambda **kw: completion(text="safe"))
    assert backend.workflow.guardrail_call.invoke("Áo còn size M không?")["risk_level"] == "safe"
