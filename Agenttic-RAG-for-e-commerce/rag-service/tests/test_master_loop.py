import pytest

from conftest import stream_chunk


@pytest.mark.parametrize("max_turns", [0, 1, 3])
def test_exhausted_loop_returns_safe_answer_with_metrics(backend, monkeypatch, max_turns):
    workflow = backend.workflow
    monkeypatch.setattr(workflow.config.agent, "max_turns", max_turns)
    monkeypatch.setattr(workflow.llm_service, "call_gemini", lambda **kwargs: stream_chunk(tool="product_search"))
    monkeypatch.setattr("src.e_agents.master_agent.time.sleep", lambda seconds: None)
    tool_calls = []

    def search(**kwargs):
        tool_calls.append(kwargs)
        return "known tool result"

    result = workflow.master_agent.invoke(
        messages=[{"role": "user", "content": "repeat tools forever"}],
        available_tools={"product_search": search},
        tools_schema=[],
    )
    assert result is not None
    assert result["content"].startswith("Xin lỗi")
    assert result["loop_exhausted"] is True
    assert len(tool_calls) == len(result["tool_context"]) == max_turns
    assert result["tokens"] == {"input": 7 * max_turns, "output": 3 * max_turns}
    assert result["latency"] >= 0
    assert all(record["output"] == "known tool result" for record in result["tool_context"])


@pytest.mark.parametrize("tool_turns", [0, 2])
def test_final_answer_at_turn_limit_is_not_exhaustion(backend, monkeypatch, tool_turns):
    workflow = backend.workflow
    monkeypatch.setattr(workflow.config.agent, "max_turns", tool_turns + 1)
    responses = iter([stream_chunk(tool="product_search") for _ in range(tool_turns)] + [stream_chunk(text="finished")])
    monkeypatch.setattr(workflow.llm_service, "call_gemini", lambda **kwargs: next(responses))
    monkeypatch.setattr("src.e_agents.master_agent.time.sleep", lambda seconds: None)
    result = workflow.master_agent.invoke(
        messages=[{"role": "user", "content": "answer within budget"}],
        available_tools={"product_search": lambda **kwargs: "known tool result"},
        tools_schema=[],
    )
    assert result["content"] == "finished"
    assert result["loop_exhausted"] is False
    assert len(result["tool_context"]) == tool_turns


def test_workflow_preserves_exhaustion_and_resets_on_next_turn(client, backend, monkeypatch):
    workflow = backend.workflow
    monkeypatch.setattr(workflow.config.agent, "max_turns", 1)
    monkeypatch.setattr(workflow.llm_service, "call_gemini", lambda **kwargs: stream_chunk(tool="product_search"))
    monkeypatch.setattr("src.e_agents.master_agent.time.sleep", lambda seconds: None)
    payload = {"message": "tool loop", "session_id": "loop-session"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["reply"].startswith("Xin lỗi")
    graph_config = {"configurable": {"thread_id": "anon:loop-session"}}
    assert backend.main.workflow_app.get_state(graph_config).values["loop_exhausted"] is True

    # A rejected follow-up bypasses master_node; stale loop flags must not survive.
    monkeypatch.setattr(workflow.guardrail_call, "invoke", lambda query: {
        "risk_level": "attack", "latency": 0, "tokens": {"input": 0, "output": 0},
    })
    monkeypatch.setattr(workflow.rejection_call, "invoke", lambda query: {
        "content": "rejected", "latency": 0, "tokens": {"input": 0, "output": 0},
    })
    response = client.post("/chat", json={**payload, "message": "rejected follow-up"})
    assert response.status_code == 200, response.text
    assert response.json()["reply"] == "rejected"
    assert backend.main.workflow_app.get_state(graph_config).values["loop_exhausted"] is False
