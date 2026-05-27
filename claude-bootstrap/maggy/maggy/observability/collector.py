"""SQLite-backed observability signal storage."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    value REAL NOT NULL,
    created_at TEXT NOT NULL
);
"""


@contextmanager
def _connect(path: Path) -> Iterator[sqlite3.Connection]:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class ObservabilityCollector:
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._init_db()

    def record_signal(
        self, project: str, signal_type: str, value: float,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with _connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO signals (project, signal_type, value, created_at) "
                "VALUES (?, ?, ?, ?)",
                (project, signal_type, value, now),
            )
            conn.commit()

    def recent_signals(
        self, project: str, limit: int = 20,
    ) -> list[dict]:
        with _connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT project, signal_type, value, created_at "
                "FROM signals WHERE project = ? "
                "ORDER BY id DESC LIMIT ?",
                (project, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def _init_db(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(SCHEMA)
