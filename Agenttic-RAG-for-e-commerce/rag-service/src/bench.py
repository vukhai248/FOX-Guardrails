"""Opt-in local records of attempted LLM requests, without transport credentials."""
import json
import base64
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

RECORD_DIR = Path(__file__).resolve().parents[1] / "bench_records"
_write_lock = Lock()


def temperature(default):
    raw = os.getenv("BENCH_TEMPERATURE")
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        raise ValueError("BENCH_TEMPERATURE must be a finite number in [0, 2]") from None
    if not math.isfinite(value) or not 0 <= value <= 2:
        raise ValueError("BENCH_TEMPERATURE must be a finite number in [0, 2]")
    return value


def _serialize(value):
    if isinstance(value, bytes):
        return {"__type__": "bytes", "base64": base64.b64encode(value).decode("ascii")}
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    raise TypeError(f"Unsupported bench payload type: {type(value).__name__}")


def record_request(provider, messages, payload):
    if os.getenv("BENCH_RECORD") != "1":
        return
    now = datetime.now(timezone.utc)
    record = {"timestamp": now.isoformat(), "provider": provider,
              "arm": os.getenv("FOX_GUARD_ARM", ""), "mode": os.getenv("FOX_GUARD_MODE", "off"),
              "messages": messages, "payload": payload}
    line = json.dumps(record, ensure_ascii=False, default=_serialize)
    with _write_lock:
        RECORD_DIR.mkdir(parents=True, exist_ok=True)
        with (RECORD_DIR / f"{now:%Y-%m-%d}.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
