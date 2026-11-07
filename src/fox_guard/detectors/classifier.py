"""Lớp 5 classifier (plan B4.1): a prompt-injection model run on the clean text.

- Local weights only (`classifier.model_dir`): the guard never downloads at runtime.
- Long text is split into overlapping token windows (512 / 64 by default); the score is the max over
  windows, so an instruction buried in a long review is not diluted.
- Scores are cached by sha256 of the text (bounded).
- The classifier alone never blocks: it yields `medium` at most; the policy combines it with rules
  (B6.1, docs/DU-AN.md §4.4.3).
"""

import hashlib
from collections import OrderedDict
from pathlib import Path

_CACHE_SIZE = 4096


def local_path(model_dir: str, model_id: str) -> Path:
    return Path(model_dir) / model_id.replace("/", "-")


class Classifier:
    def __init__(
        self, model_id: str, model_dir: str, device: str = "cpu", window: int = 512, overlap: int = 64
    ):
        self.model_id = model_id
        self.path = local_path(model_dir, model_id)
        self.device = device
        self.window = window
        self.overlap = overlap
        self._model = None
        self._tokenizer = None
        self._positive = 1
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
            raise FileNotFoundError(f"classifier weights not found at {self.path}")
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(self.path)
        self._model = AutoModelForSequenceClassification.from_pretrained(self.path).to(self.device).eval()
        labels = {int(k): str(v).upper() for k, v in self._model.config.id2label.items()}
        # "INJECTION" (deberta) / "MALICIOUS" (Prompt Guard 2): the non-benign label.
        self._positive = next(
            (i for i, name in labels.items() if name in ("INJECTION", "MALICIOUS", "JAILBREAK")),
            next((i for i, name in labels.items() if name not in ("SAFE", "BENIGN")), 1),
        )

    def score(self, text: str) -> float:
        if not text.strip():
            return 0.0
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
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
        inputs = {k: v.to(self.device) for k, v in encoded.items() if k in ("input_ids", "attention_mask")}
        with torch.no_grad():
            probs = self._model(**inputs).logits.softmax(-1)[:, self._positive]
        value = float(probs.max().item())
        self._cache[key] = value
        if len(self._cache) > _CACHE_SIZE:
            self._cache.popitem(last=False)
        return value


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
