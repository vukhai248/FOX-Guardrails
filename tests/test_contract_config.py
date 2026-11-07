"""B1 configuration loads the sample and refuses typos at every nesting level."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from fox_guard.config import GuardConfig, load_config


def test_load_sample_config():
    config = load_config(Path(__file__).resolve().parents[1] / "fox-guard.yaml")
    assert config.config_version == "0.1.0"
    assert config.normalize.max_chars == 20000
    assert config.normalize.decode_max_depth == 2
    assert config.classifier.primary == "meta-llama/Llama-Prompt-Guard-2-86M"
    # Lớp 5: thresholds chosen on dev (eval/reports/thresholds_deberta.json); classifier off by default.
    assert config.classifier.enabled is False
    assert 0 < config.classifier.theta_low <= config.classifier.theta_high <= 1
    assert config.links.allowlist == ['shop.example']
    assert config.audit.enabled is True
    assert config.audit.sqlite_path == "var/fox_guard.sqlite"


@pytest.mark.parametrize("section", [None, "normalize", "classifier", "links", "audit"])
def test_unknown_configuration_keys_fail_with_location(tmp_path, section):
    content = {"unexpected": True} if section is None else {section: {"unexpected": True}}
    path = tmp_path / "guard.yaml"
    path.write_text(yaml.safe_dump(content), encoding="utf-8")
    with pytest.raises(ValidationError, match="unexpected") as error:
        load_config(path)
    assert error.value.errors()[0]["loc"] == (("unexpected",) if section is None else (section, "unexpected"))


@pytest.mark.parametrize("values", [
    {"max_chars": 0}, {"max_chars": 20001}, {"decode_max_depth": -1}, {"decode_max_depth": 3},
])
def test_normalization_config_respects_resource_limits(values):
    with pytest.raises(ValidationError):
        GuardConfig(normalize=values)


@pytest.mark.parametrize("values", [
    {"theta_low": -0.1}, {"theta_high": 1.1}, {"theta_low": 0.9, "theta_high": 0.2},
])
def test_classifier_thresholds_are_valid_when_supplied(values):
    with pytest.raises(ValidationError):
        GuardConfig(classifier=values)


def test_config_list_defaults_are_independent():
    first, second = GuardConfig(), GuardConfig()
    first.links.allowlist.append("synthetic.invalid")
    assert second.links.allowlist == []


@pytest.mark.parametrize("content", ["- not-a-mapping\n", "null\n", "42\n"])
def test_config_rejects_non_mapping_yaml(tmp_path, content):
    path = tmp_path / "guard.yaml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_config(path)
