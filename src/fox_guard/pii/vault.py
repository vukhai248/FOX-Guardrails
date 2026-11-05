"""In-memory pseudonym vault: <PHONE_1> ↔ value per session, with owner and TTL. Never written to disk."""

import time
from dataclasses import dataclass, field

import regex

TAGS = {
    "VN_PHONE": "PHONE", "EMAIL": "EMAIL", "VN_CCCD": "CCCD", "VN_CMND": "CMND", "CREDIT_CARD": "CARD",
    "VN_BANK_ACCOUNT": "BANK_ACCOUNT", "VN_TAX_ID": "TAX_ID", "VN_PASSPORT": "PASSPORT",
    "VN_LICENSE_PLATE": "PLATE", "VN_HEALTH_INSURANCE": "BHYT", "OTP": "OTP", "PASSWORD": "PASSWORD",
    "PERSON": "PERSON", "VN_ADDRESS": "ADDRESS",
}
ENTITY_OF_TAG = {tag: entity for entity, tag in TAGS.items()}
PLACEHOLDER = regex.compile(r"<(" + "|".join(TAGS.values()) + r")_(\d{1,4})>")


def canonical(entity: str, value: str) -> str:
    """Same value written differently ('0912 345 678' vs '0912345678') gets the same placeholder."""
    if entity in ("EMAIL", "PERSON", "VN_ADDRESS", "PASSWORD"):
        return " ".join(value.split()).casefold()
    return regex.sub(r"[^0-9A-Za-z]", "", value).upper()


@dataclass
class Entry:
    entity: str
    value: str
    owner: str | None  # user_ref who supplied it; None = third party (review), never restored


@dataclass
class _Session:
    touched: float
    entries: dict[str, Entry] = field(default_factory=dict)
    by_key: dict[tuple[str, str], str] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)


class PiiVault:
    def __init__(self, ttl_seconds: float = 3600, clock=time.monotonic) -> None:
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._sessions: dict[str, _Session] = {}

    def _session(self, session_id: str) -> _Session:
        now = self._clock()
        for key in [k for k, s in self._sessions.items() if now - s.touched > self.ttl_seconds]:
            del self._sessions[key]
        session = self._sessions.setdefault(session_id, _Session(now))
        session.touched = now
        return session

    def placeholder(self, session_id: str, owner: str | None, entity: str, value: str) -> str:
        session = self._session(session_id)
        key = (entity, canonical(entity, value))
        if key in session.by_key:
            existing = session.entries[session.by_key[key]]
            if existing.owner is None and owner is not None:
                existing.owner = owner  # the user themselves later supplied the same value
            return session.by_key[key]
        tag = TAGS[entity]
        session.counters[tag] = session.counters.get(tag, 0) + 1
        name = f"<{tag}_{session.counters[tag]}>"
        session.entries[name] = Entry(entity, value, owner)
        session.by_key[key] = name
        return name

    def lookup(self, session_id: str, placeholder: str) -> Entry | None:
        return self._session(session_id).entries.get(placeholder)

    def owner_of_value(self, session_id: str, entity: str, value: str) -> str | None:
        session = self._session(session_id)
        name = session.by_key.get((entity, canonical(entity, value)))
        return session.entries[name].owner if name else None
