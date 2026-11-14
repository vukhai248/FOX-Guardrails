import importlib
import json
from types import SimpleNamespace

import pytest


@pytest.fixture
def service(backend):
    from src.LLMService import LLMService
    return LLMService(SimpleNamespace(), backend.workflow.config)


@pytest.mark.parametrize("provider", ["gemini", "groq"])
def test_records_actual_provider_payload_only_when_enabled(service, monkeypatch, tmp_path, provider):
    bench = importlib.import_module("src.bench")
    monkeypatch.setattr(bench, "RECORD_DIR", tmp_path / "bench_records")
    calls = []
    def transport(**kwargs):
        calls.append(kwargs)
        return "provider response"
    if provider == "gemini":
        service._gemini_client = SimpleNamespace(models=SimpleNamespace(generate_content=transport))
    else:
        service._groq_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=transport)))
    messages = [{"role": "system", "content": "system rules"},
                {"role": "user", "content": "synthetic PII 0912345678"}]
    call = getattr(service, f"call_{provider}")
    monkeypatch.delenv("BENCH_RECORD", raising=False)
    call("offline-model", messages, **({"stream": False} if provider == "gemini" else {}))
    assert not bench.RECORD_DIR.exists()
    monkeypatch.setenv("BENCH_RECORD", "1")
    monkeypatch.setenv("FOX_GUARD_ARM", "G0")
    monkeypatch.setenv("BENCH_TEMPERATURE", "0")
    call("offline-model", messages, **({"stream": False} if provider == "gemini" else {}))
    record = json.loads(next(bench.RECORD_DIR.glob("*.jsonl")).read_text(encoding="utf-8"))
    assert record["provider"] == provider
    assert record["arm"] == "G0"
    assert record["messages"] == messages
    assert "synthetic PII 0912345678" in json.dumps(record["payload"])
    if provider == "gemini":
        assert calls[-1]["config"].temperature == record["payload"]["config"]["temperature"] == 0
        assert record["payload"]["config"]["system_instruction"] == "system rules"
        assert record["payload"]["contents"] == [c.model_dump(mode="json", exclude_none=True) for c in calls[-1]["contents"]]
    else:
        assert calls[-1]["temperature"] == record["payload"]["temperature"] == 0
        assert record["payload"] == calls[-1]


@pytest.mark.parametrize("value", ["nan", "inf", "-1", "3", "invalid"])
def test_invalid_bench_temperature_fails_before_network(service, monkeypatch, value):
    monkeypatch.setenv("BENCH_TEMPERATURE", value)
    monkeypatch.setattr(service, "_get_gemini_client", lambda: pytest.fail("unexpected network attempt"))
    with pytest.raises(ValueError, match="BENCH_TEMPERATURE"):
        service.call_gemini("offline-model", [{"role": "user", "content": "hi"}])


def test_each_provider_retry_is_recorded(service, monkeypatch, tmp_path):
    bench = importlib.import_module("src.bench")
    monkeypatch.setattr(bench, "RECORD_DIR", tmp_path)
    monkeypatch.setenv("BENCH_RECORD", "1")
    monkeypatch.setattr("time.sleep", lambda seconds: None)
    attempts = []
    def transport(**kwargs):
        attempts.append(kwargs)
        if len(attempts) == 1:
            raise RuntimeError("503 temporarily unavailable")
        return "ok"
    service._gemini_client = SimpleNamespace(models=SimpleNamespace(generate_content=transport))
    service.call_gemini("offline-model", [{"role": "user", "content": "hi"}], stream=False)
    assert len(next(tmp_path.glob("*.jsonl")).read_text(encoding="utf-8").splitlines()) == 2


def test_recording_failure_prevents_unrecorded_request(service, monkeypatch, tmp_path):
    bench = importlib.import_module("src.bench")
    path = tmp_path / "not-a-directory"
    path.write_text("file", encoding="utf-8")
    monkeypatch.setattr(bench, "RECORD_DIR", path)
    monkeypatch.setenv("BENCH_RECORD", "1")
    service._groq_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=lambda **kwargs: pytest.fail("payload must be recorded before sending"))))
    with pytest.raises(OSError):
        service.call_groq("offline-model", [{"role": "user", "content": "hi"}])


def test_signed_gemini_tool_followup_records_binary_signature_reversibly(service, monkeypatch, tmp_path):
    import base64
    bench = importlib.import_module("src.bench")
    monkeypatch.setattr(bench, "RECORD_DIR", tmp_path)
    monkeypatch.setenv("BENCH_RECORD", "1")
    calls = []
    def transport(**kwargs):
        calls.append(kwargs)
        return "ok"
    service._gemini_client = SimpleNamespace(models=SimpleNamespace(generate_content=transport))
    signature = b"\x00\xffsigned-tool\x80"
    messages = [{"role": "assistant", "content": None, "tool_calls": [{
        "id": "call-1", "type": "function", "thought_signature": signature,
        "function": {"name": "product_reviews", "arguments": '{"product_id":16}'},
    }]}, {"role": "tool", "tool_call_id": "call-1", "name": "product_reviews", "content": "5/5"}]
    assert service.call_gemini("offline-model", messages, stream=False) == ["ok"]
    record = json.loads(next(tmp_path.glob("*.jsonl")).read_text(encoding="utf-8"))
    encoded = record["messages"][0]["tool_calls"][0]["thought_signature"]
    assert encoded["__type__"] == "bytes"
    assert base64.b64decode(encoded["base64"]) == signature
    assert calls[0]["contents"][0].parts[0].thought_signature == signature
