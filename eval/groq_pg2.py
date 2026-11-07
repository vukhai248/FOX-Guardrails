"""Prompt Guard 2 (86M) through the Groq API — an EVAL-ONLY backend while the weights are not local.

The guard itself stays local-only at runtime (detectors/classifier.py). This module registers an
object with the same interface (`model_id`, `short_name`, `score`) in the classifier registry, so
eval/calibrate.py and eval/run_detectors.py run unchanged with `--device groq`.

- Groq returns the MALICIOUS probability as the message text ("0.9996…").
- Groq rejects inputs over the model's 512-token context, and the tokenizer is gated, so long text
  is split into overlapping character windows (halved again if still too long); score = max, the
  same rule as the local classifier.
- Scores are cached on disk (var/, gitignored) by sha256, so re-runs cost no API calls.
- Latency measured with this backend is network latency, not model latency.

Key: GROQ_API_KEY in the environment only; never written to a file.
"""

import hashlib
import json
import os
import threading
from pathlib import Path

from fox_guard.config import ClassifierConfig
from fox_guard.detectors import classifier as clf_module

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "var" / "groq_pg2_cache.jsonl"
GROQ_MODEL = "meta-llama/llama-prompt-guard-2-86m"
WINDOW_CHARS = 1200
OVERLAP_CHARS = 200
MIN_WINDOW = 150


def char_windows(text: str, size: int, overlap: int) -> list[str]:
    if len(text) <= size:
        return [text]
    out, start = [], 0
    while start < len(text):
        out.append(text[start:start + size])
        if start + size >= len(text):
            break
        start += size - overlap
    return out


class GroqPromptGuard:
    def __init__(self, model_id: str):
        from groq import Groq

        self.model_id = model_id
        self.short_name = "pg2"
        self._client = Groq(max_retries=10)
        self._lock = threading.Lock()
        self._cache: dict[str, float] = {}
        if CACHE.exists():
            for line in CACHE.read_text("utf-8").splitlines():
                row = json.loads(line)
                self._cache[row["k"]] = row["s"]

    def available(self) -> bool:
        return True

    def _call(self, text: str) -> float:
        from groq import BadRequestError

        try:
            messages = [{"role": "user", "content": text}]
            r = self._client.chat.completions.create(model=GROQ_MODEL, messages=messages)
            return float(r.choices[0].message.content.strip())
        except BadRequestError as e:
            if "context_length" not in str(e) or len(text) <= MIN_WINDOW:
                raise
            # Every window strictly shorter than `text`, so the recursion always shrinks.
            size = len(text) // 2 + 1
            return max(self._call(w) for w in char_windows(text, size, min(OVERLAP_CHARS, size // 2)))

    def n_tokens(self, text: str) -> int:
        """No tokenizer here (gated): characters as a stand-in, same ordering for the decoded-view rule."""
        return len(text)

    def score_limited(self, text: str, max_windows: int | None) -> tuple[float, int, int]:
        """Eval backend: always scores the whole text (no window budget)."""
        return self.score(text), 1, 1

    def score(self, text: str) -> float:
        if not text.strip():
            return 0.0
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if key in self._cache:
            return self._cache[key]
        value = max(self._call(w) for w in char_windows(text, WINDOW_CHARS, OVERLAP_CHARS))
        with self._lock:
            self._cache[key] = value
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            with CACHE.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"k": key, "s": value}) + "\n")
        return value


def register() -> None:
    """Make get_classifier(use=primary, device=groq) return the Groq backend."""
    if not os.environ.get("GROQ_API_KEY"):
        raise SystemExit("GROQ_API_KEY is not set")
    cfg = ClassifierConfig(enabled=True, use="primary", device="groq")
    key = (cfg.primary, cfg.model_dir, cfg.device, cfg.window_tokens, cfg.overlap_tokens)
    clf_module._INSTANCES[key] = GroqPromptGuard(cfg.primary)
