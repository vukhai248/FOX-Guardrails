"""Lớp 4 audit store (plan B6.5): one SQLite file, only already-redacted text, hashed user refs."""

import hashlib
import json
import os
import secrets
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    station TEXT NOT NULL,
    source TEXT,
    session_ref TEXT,
    user_ref_hash TEXT,
    arm TEXT,
    action TEXT NOT NULL,
    risk TEXT NOT NULL,
    reasons_json TEXT NOT NULL,
    findings_json TEXT NOT NULL,
    text_redacted TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    degraded INTEGER NOT NULL,
    config_version TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS decisions_ts_idx ON decisions (ts);
CREATE INDEX IF NOT EXISTS decisions_action_idx ON decisions (action, station);
CREATE TABLE IF NOT EXISTS reviews (
    decision_id TEXT NOT NULL REFERENCES decisions(id),
    reviewer TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('approve', 'reject')),
    note TEXT,
    ts TEXT NOT NULL
);
"""


class AuditStore:
    """Thread-safe append-only writer. Callers must pass text that is ALREADY irreversibly masked."""

    def __init__(self, path: str | Path, salt: str | None = None) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # No salt configured: a random per-process salt still hides user ids, but hashes then cannot
        # be linked across restarts. Set FOX_AUDIT_SALT to link sessions of the same user.
        self._salt = salt if salt else secrets.token_hex(16)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.executescript(_SCHEMA)

    @classmethod
    def open_existing(cls, path: str | Path) -> "AuditStore":
        """For read-only tools (CLI): a mistyped path must fail, not create an empty database."""
        if not Path(path).is_file():
            raise FileNotFoundError(f"Không có file audit: {path}")
        return cls(path)

    @classmethod
    def from_env(cls, path: str | Path, salt_env: str) -> "AuditStore":
        return cls(path, os.environ.get(salt_env))

    def hash_user(self, user_ref: str | None) -> str | None:
        if user_ref is None:
            return None
        return hashlib.sha256((self._salt + "\x1f" + user_ref).encode("utf-8")).hexdigest()

    def record(self, *, decision, ctx, station: str, text_redacted: str, config_version: str) -> None:
        row = (
            decision.decision_id, datetime.now(UTC).isoformat(), station, ctx.source,
            ctx.session_id, self.hash_user(ctx.user_ref), ctx.arm, decision.action, decision.risk,
            json.dumps(decision.reasons, ensure_ascii=False),
            json.dumps([f.model_dump() for f in decision.findings], ensure_ascii=False),
            text_redacted, round(decision.latency_ms, 3), int(decision.degraded), config_version,
        )
        with self._lock:
            self._conn.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
            self._conn.commit()

    def review(self, decision_id: str, reviewer: str, verdict: str, note: str = "") -> None:
        with self._lock:
            self._conn.execute("INSERT INTO reviews VALUES (?,?,?,?,?)",
                               (decision_id, reviewer, verdict, note, datetime.now(UTC).isoformat()))
            self._conn.commit()

    def get(self, decision_id: str) -> dict | None:
        cursor = self._conn.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,))
        row = cursor.fetchone()
        return dict(zip([c[0] for c in cursor.description], row, strict=True)) if row else None

    def export_jsonl(self, out: str | Path) -> int:
        target = Path(out)
        if target.resolve() == self.path.resolve() or (target.exists() and target.samefile(self.path)):
            raise ValueError("Refusing to export audit JSONL over its own SQLite database")
        cursor = self._conn.execute("SELECT * FROM decisions ORDER BY ts")
        names = [c[0] for c in cursor.description]
        count = 0
        with Path(out).open("w", encoding="utf-8") as stream:
            for row in cursor:
                stream.write(json.dumps(dict(zip(names, row, strict=True)), ensure_ascii=False) + "\n")
                count += 1
        return count

    def close(self) -> None:
        with self._lock:
            self._conn.close()
