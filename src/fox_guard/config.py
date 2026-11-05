"""Validated YAML configuration, including inactive future detector sections."""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class _ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NormalizeConfig(_ConfigModel):
    max_chars: int = Field(default=20000, gt=0, le=20000)
    decode_max_depth: int = Field(default=2, ge=0, le=2)


class ClassifierConfig(_ConfigModel):
    primary: str = "meta-llama/Llama-Prompt-Guard-2-86M"
    secondary: str = "protectai/deberta-v3-base-prompt-injection-v2"
    theta_low: float | None = Field(default=None, ge=0, le=1)
    theta_high: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def validate_threshold_order(self) -> "ClassifierConfig":
        if self.theta_low is not None and self.theta_high is not None and self.theta_low > self.theta_high:
            raise ValueError("theta_low must not exceed theta_high")
        return self


class LinksConfig(_ConfigModel):
    allowlist: list[str] = Field(default_factory=list)


class PiiConfig(_ConfigModel):
    enabled: bool = True
    vault_ttl_minutes: int = Field(default=60, gt=0, le=24 * 60)


class AuditConfig(_ConfigModel):
    sqlite_path: str = "var/fox_guard.sqlite"


class GuardConfig(_ConfigModel):
    config_version: str = "0.1.0"
    normalize: NormalizeConfig = Field(default_factory=NormalizeConfig)
    classifier: ClassifierConfig = Field(default_factory=ClassifierConfig)
    pii: PiiConfig = Field(default_factory=PiiConfig)
    links: LinksConfig = Field(default_factory=LinksConfig)
    audit: AuditConfig = Field(default_factory=AuditConfig)


def load_config(path: str | Path) -> GuardConfig:
    """Read UTF-8 YAML; reject unknown keys instead of silently discarding typos."""
    with Path(path).open(encoding="utf-8") as stream:
        content = yaml.safe_load(stream)
    if not isinstance(content, dict):
        raise ValueError(f"Configuration {path} must contain a YAML mapping")
    return GuardConfig.model_validate(content)
