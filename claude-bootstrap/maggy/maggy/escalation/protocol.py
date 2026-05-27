"""Human escalation packets with SQLite persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS escalations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    context TEXT NOT NULL,
    agent_state TEXT NOT NULL,
    suggested_actions TEXT NOT NULL,
    created_at TEXT NOT NULL,
    resolved INTEGER NOT NULL,
    resolution TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_escalations_pending
    ON escalations(resolved, created_at);
"""


@dataclass
class EscalationPacket:
    id: str
    session_id: str
    reason: str
    context: dict[str, object]
    agent_state: dict[str, object]
    suggested_actions: list[str]
    created_at: str
    resolved: bool
    resolution: str


@contextmanager
def _connect(path: Path) -> Iterator[sqlite3.Connection]:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class Escalator:
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._init_db()

    def escalate(
        self, session_id: str, reason: str, context: dict[str, object]
    ) -> EscalationPacket:
        packet = _build_packet(session_id, reason, context)
        with _connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO escalations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _serialize(packet),
            )
            conn.commit()
        return packet

    def resolve(self, escalation_id: str, guidance: str) -> EscalationPacket:
        with _connect(self._db_path) as conn:
            conn.execute(
                "UPDATE escalations SET resolved = 1, resolution = ? WHERE id = ?",
                (guidance, escalation_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM escalations WHERE id = ?",
                (escalation_id,),
            ).fetchone()
        if not row:
            raise KeyError(escalation_id)
        return _from_row(row)

    def list_pending(self) -> list[EscalationPacket]:
        with _connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM escalations WHERE resolved = 0 ORDER BY created_at",
            ).fetchall()
        return [_from_row(row) for row in rows]

    def get(self, escalation_id: str) -> EscalationPacket | None:
        with _connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM escalations WHERE id = ?",
                (escalation_id,),
            ).fetchone()
        return _from_row(row) if row else None

    def _init_db(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(SCHEMA)


def _build_packet(
    session_id: str, reason: str, context: dict[str, object]
) -> EscalationPacket:
    return EscalationPacket(
        id=str(uuid.uuid4()),
        session_id=session_id,
        reason=reason,
        context=context,
        agent_state=_dict_field(context, "agent_state"),
        suggested_actions=_list_field(context, "suggested_actions"),
        created_at=datetime.now(timezone.utc).isoformat(),
        resolved=False,
        resolution="",
    )


def _dict_field(context: dict[str, object], key: str) -> dict[str, object]:
    value = context.get(key, {})
    return value if isinstance(value, dict) else {}


def _list_field(context: dict[str, object], key: str) -> list[str]:
    value = context.get(key, [])
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _serialize(packet: EscalationPacket) -> tuple[object, ...]:
    return (
        packet.id,
        packet.session_id,
        packet.reason,
        json.dumps(packet.context),
        json.dumps(packet.agent_state),
        json.dumps(packet.suggested_actions),
        packet.created_at,
        int(packet.resolved),
        packet.resolution,
    )


def _safe_json(raw: str, fallback: object) -> object:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return fallback


def _from_row(row: sqlite3.Row) -> EscalationPacket:
    return EscalationPacket(
        id=row["id"],
        session_id=row["session_id"],
        reason=row["reason"],
        context=_safe_json(row["context"], {}),
        agent_state=_safe_json(row["agent_state"], {}),
        suggested_actions=_safe_json(row["suggested_actions"], []),
        created_at=row["created_at"],
        resolved=bool(row["resolved"]),
        resolution=row["resolution"],
    )
