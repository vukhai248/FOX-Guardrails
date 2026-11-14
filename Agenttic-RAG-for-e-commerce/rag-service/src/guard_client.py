"""FOX-Guard plug-in point (Lớp 6). One environment variable switches it; the chat code never changes.

    FOX_GUARD_MODE=off       pass-through (baseline arm G0)
    FOX_GUARD_MODE=inproc    import the SDK: FOX_GUARD_CONFIG=<path to fox-guard.yaml>
    FOX_GUARD_MODE=sidecar   HTTP: FOX_GUARD_URL (default http://127.0.0.1:8091), FOX_GUARD_KEY,
                             FOX_GUARD_TIMEOUT (seconds, default 10)

Hooks: guard_input (customer message) · guard_context (each untrusted tool segment) · guard_output
(answer) · guard_restore_args (placeholders → owner's values, only for tool calls) · guard_log
(irreversible redaction for chat_logs).

Fail-closed: if the guard is unreachable, input is refused, a context segment is hidden and the
answer is replaced by a safe text; guard_log raises so chat_logging writes nothing.
"""
import logging
import os
import threading
from dataclasses import dataclass, field, replace

logger = logging.getLogger(__name__)

MODES = ("off", "inproc", "sidecar")
UNAVAILABLE_INPUT = "Xin lỗi, hệ thống kiểm tra an toàn đang tạm gián đoạn. Bạn vui lòng thử lại sau ít phút."
UNAVAILABLE_CONTEXT = "[nội dung tạm ẩn: chưa kiểm tra được an toàn]"
UNAVAILABLE_OUTPUT = "Xin lỗi, mình chưa thể gửi câu trả lời lúc này. Bạn vui lòng thử lại sau."


def _mode() -> str:
    mode = os.getenv("FOX_GUARD_MODE", "off").lower()
    if mode not in MODES:
        raise NotImplementedError(f"Unknown FOX_GUARD_MODE {mode!r}; use one of {MODES}")
    return mode


def build_context(**values):
    return {**values, "mode": os.getenv("FOX_GUARD_MODE", "off").lower(),
            "arm": os.getenv("FOX_GUARD_ARM", "")}


class GuardedText(str):
    """The text the app should use, plus the guard's verdict (a str, so callers need no change)."""

    action: str = "allow"
    decision_id: str | None = None
    flags: tuple[str, ...] = ()
    harden_prompt_text: str | None = None

    @classmethod
    def make(cls, text: str, action="allow", decision_id=None, flags=(), harden_prompt_text=None):
        obj = cls(text)
        obj.action, obj.decision_id, obj.flags = action, decision_id, tuple(flags)
        obj.harden_prompt_text = harden_prompt_text
        return obj


def _fox_ctx(ctx: dict) -> dict:
    user = ctx.get("user_id")
    return {"session_id": str(ctx.get("session_id") or "anonymous"),
            "user_ref": str(user) if user else None,
            "source": ctx.get("source"), "intent": ctx.get("intent") or None,
            "arm": ctx.get("arm") or None}


class _Inproc:
    def __init__(self, config_path: str):
        from fox_guard import Guard, GuardContext

        self._guard = Guard.from_config(config_path) if config_path else Guard()
        self._ctx = GuardContext
        self._lock = threading.Lock()  # classifier cache + PII vault are in-memory

    def check(self, station, text, ctx):
        with self._lock:
            d = getattr(self._guard, f"check_{station}")(text, self._ctx(station=station, **ctx))
        harden = self._guard.harden_prompt_text if "harden_prompt" in d.flags else None
        return {"action": d.action, "text": d.text, "decision_id": d.decision_id, "flags": d.flags,
                "harden_prompt_text": harden}

    def restore(self, text, ctx):
        with self._lock:
            return self._guard.restore(text, self._ctx(station="output", **ctx))

    def redact(self, text, ctx):
        with self._lock:
            return self._guard.redact_for_log(text, self._ctx(station="output", **ctx))


class _Sidecar:
    def __init__(self, url: str, key: str | None, timeout: float):
        import httpx

        headers = {"X-FOX-Key": key} if key else {}
        self._http = httpx.Client(base_url=url.rstrip("/"), headers=headers, timeout=timeout)

    def _post(self, path, body):
        response = self._http.post(path, json=body)
        response.raise_for_status()
        return response.json()

    def check(self, station, text, ctx):
        return self._post("/v1/check", {"station": station, "text": text, "ctx": ctx})

    def restore(self, text, ctx):
        return self._post("/v1/restore", {"text": text, "ctx": ctx})["text"]

    def redact(self, text, ctx):
        return self._post("/v1/redact", {"text": text, "ctx": ctx})["text"]


_BACKENDS: dict[tuple, object] = {}
_BACKENDS_LOCK = threading.Lock()


def _backend():
    mode = _mode()
    if mode == "inproc":
        key = (mode, os.getenv("FOX_GUARD_CONFIG", ""))
        factory = lambda: _Inproc(key[1])  # noqa: E731
    else:
        key = (mode, os.getenv("FOX_GUARD_URL", "http://127.0.0.1:8091"), os.getenv("FOX_GUARD_KEY") or None,
               float(os.getenv("FOX_GUARD_TIMEOUT", "10")))
        factory = lambda: _Sidecar(*key[1:])  # noqa: E731
    with _BACKENDS_LOCK:
        if key not in _BACKENDS:
            _BACKENDS[key] = factory()
        return _BACKENDS[key]


def _check(station, text, ctx):
    return _backend().check(station, text, _fox_ctx(ctx))


def guard_input(text, ctx):
    if _mode() == "off":
        return text
    try:
        d = _check("input", text, ctx)
    except Exception:
        logger.warning("FOX_GUARD_UNAVAILABLE station=input")
        return GuardedText.make(UNAVAILABLE_INPUT, "block", flags=("guard_unavailable",))
    return GuardedText.make(d["text"], d["action"], d.get("decision_id"), d.get("flags") or (),
                            d.get("harden_prompt_text"))


def guard_context(segment, ctx):
    if _mode() == "off":
        return segment
    try:
        d = _check("context", segment.text, {**ctx, "source": segment.source})
        text = d["text"]
    except Exception:
        logger.warning("FOX_GUARD_UNAVAILABLE station=context")
        text = UNAVAILABLE_CONTEXT
    return replace(segment, text=text)


def guard_output(text, ctx):
    if _mode() == "off":
        return text
    try:
        d = _check("output", text, ctx)
    except Exception:
        logger.warning("FOX_GUARD_UNAVAILABLE station=output")
        return GuardedText.make(UNAVAILABLE_OUTPUT, "block", flags=("guard_unavailable",))
    return GuardedText.make(d["text"], d["action"], d.get("decision_id"), d.get("flags") or ())


def guard_restore_args(args: dict, ctx: dict) -> dict:
    """Placeholders (<PHONE_1>…) in tool arguments back to the owner's values, for the call only.

    The caller keeps the masked args for history/logs; only the function call sees real values."""
    if _mode() == "off" or not args:
        return args

    def restore(value):
        if isinstance(value, str) and "<" in value:
            try:
                return _backend().restore(value, _fox_ctx(ctx))
            except Exception:
                logger.warning("FOX_GUARD_UNAVAILABLE restore")
                return value
        if isinstance(value, list):
            return [restore(v) for v in value]
        return value

    return {k: restore(v) for k, v in args.items()}


@dataclass
class LogText:
    message: str
    decision_ids: list[str] = field(default_factory=list)


def guard_log(text, ctx) -> LogText:
    """Irreversible redaction for chat_logs, separate from the restored customer-facing reply.

    Off keeps the baseline text. Enabled modes raise if the guard is unreachable: chat_logging then
    writes nothing rather than raw PII.
    """
    if _mode() == "off":
        return LogText(text)
    return LogText(_backend().redact(text, _fox_ctx(ctx)))
