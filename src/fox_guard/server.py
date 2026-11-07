"""Lớp 6 sidecar: FOX-Guard over HTTP, so any app can plug it in without importing the SDK.

    fox-guard serve --config fox-guard.yaml --port 8091

- One Guard per process: the classifier weights and the PII vault live here (load once, warm up).
- Every request needs header `X-FOX-Key` when a key is configured (env FOX_SIDECAR_KEY); without a key
  the CLI only binds to loopback.
- Guard calls are serialized by one lock: the classifier cache and the per-session PII vault are plain
  in-memory structures. Measured latency under load therefore includes queueing.
- Responses never echo the raw input: `text` is the guard's output (refusal / masked / restored).
"""

import hmac
import threading
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from . import __version__
from .guard import Guard
from .types import Decision, GuardContext

Station = Literal["input", "context", "output"]


class Ctx(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    user_ref: str | None = Field(default=None, max_length=200)
    source: str | None = Field(default=None, max_length=64)
    intent: str | None = Field(default=None, max_length=64)
    lang: str | None = Field(default=None, max_length=8)
    arm: str | None = Field(default=None, max_length=16)


class CheckRequest(BaseModel):
    station: Station
    text: str = Field(max_length=200_000)
    ctx: Ctx


class TextRequest(BaseModel):
    text: str = Field(max_length=200_000)
    ctx: Ctx


class TextResponse(BaseModel):
    text: str


class CheckResponse(Decision):
    harden_prompt_text: str | None = None


def create_app(guard: Guard, api_key: str | None) -> FastAPI:
    app = FastAPI(title="FOX-Guard sidecar", version=__version__)
    lock = threading.Lock()

    def require_key(x_fox_key: str | None = Header(default=None)) -> None:
        if api_key and not (x_fox_key and hmac.compare_digest(x_fox_key.encode(), api_key.encode())):
            raise HTTPException(status_code=401, detail="invalid X-FOX-Key")

    def context(ctx: Ctx, station: Station) -> GuardContext:
        return GuardContext(station=station, **ctx.model_dump())

    @app.get("/healthz")
    def healthz() -> dict:
        clf = guard.config.classifier
        return {"status": "ok", "version": __version__, "classifier": clf.use if clf.enabled else None}

    @app.post("/v1/check", response_model=CheckResponse, dependencies=[Depends(require_key)])
    def check(req: CheckRequest) -> CheckResponse:
        with lock:
            decision = getattr(guard, f"check_{req.station}")(req.text, context(req.ctx, req.station))
        harden = guard.harden_prompt_text if "harden_prompt" in decision.flags else None
        return CheckResponse(**decision.model_dump(), harden_prompt_text=harden)

    @app.post("/v1/restore", response_model=TextResponse, dependencies=[Depends(require_key)])
    def restore(req: TextRequest) -> TextResponse:
        """Placeholders back to the owner's values (tool arguments); no detection."""
        with lock:
            return TextResponse(text=guard.restore(req.text, context(req.ctx, "output")))

    @app.post("/v1/redact", response_model=TextResponse, dependencies=[Depends(require_key)])
    def redact(req: TextRequest) -> TextResponse:
        """Irreversible redaction for chat logs; never restores placeholders."""
        with lock:
            return TextResponse(text=guard.redact_for_log(req.text, context(req.ctx, "output")))

    return app


def warm_up(guard: Guard) -> None:
    """Load the classifier once at start-up instead of on the first customer message."""
    if guard.config.classifier.enabled:
        guard.check_input("warm up", GuardContext(session_id="warm-up", station="input"))
