"""Stable public contracts shared by the SDK, future sidecar, and evaluations."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Risk = Literal["low", "medium", "high"]


class GuardContext(BaseModel):
    """Request metadata; no user identifiers are persisted by the wave-1 SDK."""

    session_id: str
    user_ref: str | None = None
    station: Literal["input", "context", "output"]
    source: str | None = None
    intent: str | None = None
    lang: str | None = None
    arm: str | None = None


class Finding(BaseModel):
    """Detector evidence; spans use clean text, and callers must mask PII in evidence."""

    detector: str
    kind: Literal["injection", "pii", "solicitation", "link", "unicode"]
    severity: Risk
    score: float | None = None
    span: tuple[int, int] | None = None
    evidence: str = Field(max_length=120)
    technique: str | None = None

    @field_validator("span")
    @classmethod
    def validate_span(cls, value: tuple[int, int] | None) -> tuple[int, int] | None:
        if value is not None and not 0 <= value[0] <= value[1]:
            raise ValueError("span must satisfy 0 <= start <= end on clean text")
        return value


class Decision(BaseModel):
    """Application-facing result; wave 1 only normalizes and always allows."""

    decision_id: str
    action: Literal["allow", "mask", "block", "review"]
    text: str
    risk: Risk
    findings: list[Finding] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    latency_ms: float
    degraded: bool = False
    flags: list[str] = Field(default_factory=list)
