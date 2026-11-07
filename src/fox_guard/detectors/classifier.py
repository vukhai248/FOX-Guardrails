"""Lớp 5 classifier (plan B4.1): a prompt-injection model run on the clean text.

- Local weights only (`classifier.model_dir`): the guard never downloads at runtime.
- Long text is split into overlapping token windows (512 / 64 by default); the score is the max over
  windows, so an instruction buried in a long review is not diluted.
- Scores are cached by sha256 of the text (bounded).
- The classifier alone never blocks: it yields `medium` at most; the policy combines it with rules
  (B6.1, docs/DU-AN.md §4.4.3).
"""

import hashlib
import logging
from collections import OrderedDict
from pathlib import Path

_CACHE_SIZE = 4096
_log = logging.getLogger("fox_guard")


def positive_label(id2label: dict[int, str]) -> int:
    """Index of the attack class.

    Named labels: "INJECTION" (deberta) / "MALICIOUS" (Prompt Guard 2) / "JAILBREAK", else the one
    label that is not "SAFE"/"BENIGN". Generic names only ("LABEL_0", "LABEL_1": the PG2 config ships
    without id2label): the highest index, the convention of binary classifiers (PG2 card: 1 = malicious).
    """
    labels = {i: name.upper() for i, name in id2label.items()}
    named = [i for i, name in labels.items() if name in ("INJECTION", "MALICIOUS", "JAILBREAK")]
    if named:
        return named[0]
    if all(name.startswith("LABEL_") for name in labels.values()):
        return max(labels)
    others = [i for i, name in labels.items() if name not in ("SAFE", "BENIGN")]
    return others[0] if len(others) == 1 else max(labels)


def resolve_device(device: str) -> str:
    if device != "auto":
        return device
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def local_path(model_dir: str, model_id: str) -> Path:
    return Path(model_dir) / model_id.replace("/", "-")


class Classifier:
    def __init__(
        self, model_id: str, model_dir: str, device: str = "cpu", window: int = 512, overlap: int = 64
    ):
        self.model_id = model_id
        self.path = local_path(model_dir, model_id)
        self.device = resolve_device(device)
        self.window = window
        self.overlap = overlap
        self._model = None
        self._tokenizer = None
        self._positive = 1
        self._warned = False
        self._cache: OrderedDict[str, float] = OrderedDict()

    @property
    def short_name(self) -> str:
        return "pg2" if "Prompt-Guard" in self.model_id else "deberta"

    def available(self) -> bool:
        return (self.path / "config.json").exists()

    def _load(self) -> None:
        if self._model is not None:
            return
        if not self.available():
            if not self._warned:  # degraded mode must be visible, once per process
                _log.warning("classifier weights not found at %s: Lớp 5 runs degraded", self.path)
                self._warned = True
            raise FileNotFoundError(f"classifier weights not found at {self.path}")
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(self.path)
        self._model = AutoModelForSequenceClassification.from_pretrained(self.path).to(self.device).eval()
        self._positive = positive_label({int(k): str(v) for k, v in self._model.config.id2label.items()})

    def n_tokens(self, text: str) -> int:
        """Token count (no special tokens); cheap next to a forward pass."""
        self._load()
        return len(self._tokenizer(text, add_special_tokens=False)["input_ids"])

    def score(self, text: str) -> float:
        """Max over ALL windows (calibration / eval). The guard uses `score_limited`."""
        return self.score_limited(text, None)[0]

    def score_limited(self, text: str, max_windows: int | None) -> tuple[float, int, int]:
        """(max score over the first `max_windows` windows, windows scored, windows in the text).

        Cost grows with text length; the guard bounds it per check so one long message cannot hold
        the model for tens of seconds (review of PR #9)."""
        if not text.strip() or max_windows == 0:
            return 0.0, 0, 0 if not text.strip() else 1
        key = hashlib.sha256(f"{max_windows}\0{text}".encode()).hexdigest()
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        self._load()
        import torch

        encoded = self._tokenizer(
            text,
            truncation=True,
            max_length=self.window,
            stride=self.overlap,
            return_overflowing_tokens=True,
            padding=True,
            return_tensors="pt",
        )
        total = int(encoded["input_ids"].shape[0])
        used = total if max_windows is None else min(total, max_windows)
        inputs = {k: encoded[k][:used].to(self.device) for k in ("input_ids", "attention_mask")}
        with torch.no_grad():
            probs = self._model(**inputs).logits.softmax(-1)[:, self._positive]
        result = (float(probs.max().item()), used, total)
        self._cache[key] = result
        if len(self._cache) > _CACHE_SIZE:
            self._cache.popitem(last=False)
        return result


def views_to_score(model, normalized) -> list[str]:
    """Texts the classifier reads, in budget priority: visible, concealed, then decoded views.

    A decoded view is scored only if it reads MORE naturally than the visible text, i.e. tokenizes
    no longer: ROT13 of an ordinary review is gibberish (more tokens) and is skipped — scoring it cost
    ~25 s on a long text and its noisy scores were counted as catches (review of PR #9); ROT13 of a
    ROT13-encoded attack, or a base64 payload, is shorter and is scored."""
    texts = [normalized.clean, normalized.hidden_tags]
    if normalized.decoded:
        limit = model.n_tokens(normalized.clean) if normalized.clean.strip() else 0
        texts += [c.clean for c in normalized.decoded if not limit or model.n_tokens(c.clean) <= limit]
    return [t for t in texts if t.strip()]


def guard_score(model, normalized, max_windows: int | None) -> tuple[float, bool]:
    """(max score, budget reached). The single scoring rule shared by the guard and eval/calibrate.py."""
    budget, score, partial = max_windows, 0.0, False
    for text in views_to_score(model, normalized):
        value, used, total = model.score_limited(text, budget)
        score, partial = max(score, value), partial or used < total
        if budget is not None:
            budget -= used
    return score, partial


_INSTANCES: dict[tuple, Classifier] = {}


def get_classifier(config) -> Classifier:
    """One shared instance per (model, dir, device): loading the weights costs seconds."""
    model_id = config.primary if config.use == "primary" else config.secondary
    key = (model_id, config.model_dir, config.device, config.window_tokens, config.overlap_tokens)
    if key not in _INSTANCES:
        _INSTANCES[key] = Classifier(
            model_id, config.model_dir, config.device, config.window_tokens, config.overlap_tokens
        )
    return _INSTANCES[key]
