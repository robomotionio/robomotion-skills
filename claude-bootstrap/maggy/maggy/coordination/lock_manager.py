"""SQLite-backed file locks for multi-agent coordination."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

LOCK_TTL = timedelta(minutes=30)
SCHEMA = """
CREATE TABLE IF NOT EXISTS locks (
    file_path TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    acquired_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_locks_file_path
    ON locks(file_path);
CREATE INDEX IF NOT EXISTS idx_locks_expires_at
    ON locks(expires_at);
"""


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


class LockManager:
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._init_db()

    def acquire(self, file_path: str, agent_id: str) -> bool:
        now, expires = _timestamps()
        with _connect(self._db_path) as conn:
            self._expire_locks(conn, now)
            try:
                conn.execute(
                    "INSERT INTO locks(file_path, agent_id, acquired_at, expires_at) "
                    "VALUES (?, ?, ?, ?)",
                    (file_path, agent_id, now, expires),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                row = conn.execute(
                    "SELECT agent_id FROM locks WHERE file_path = ?",
                    (file_path,),
                ).fetchone()
                if row and row["agent_id"] == agent_id:
                    conn.execute(
                        "UPDATE locks SET acquired_at = ?, expires_at = ? "
                        "WHERE file_path = ?",
                        (now, expires, file_path),
                    )
                    conn.commit()
                    return True
                return False

    def release(self, file_path: str, agent_id: str) -> bool:
        with _connect(self._db_path) as conn:
            self._expire_locks(conn, _now())
            cur = conn.execute(
                "DELETE FROM locks WHERE file_path = ? AND agent_id = ?",
                (file_path, agent_id),
            )
            conn.commit()
        return cur.rowcount > 0

    def release_all(self, agent_id: str) -> int:
        with _connect(self._db_path) as conn:
            self._expire_locks(conn, _now())
            cur = conn.execute("DELETE FROM locks WHERE agent_id = ?", (agent_id,))
            conn.commit()
        return cur.rowcount

    def conflicts(self, file_paths: list[str]) -> list[str]:
        if not file_paths:
            return []
        marks = ", ".join("?" for _ in file_paths)
        with _connect(self._db_path) as conn:
            self._expire_locks(conn, _now())
            rows = conn.execute(
                f"SELECT file_path FROM locks WHERE file_path IN ({marks})",
                file_paths,
            ).fetchall()
        locked = {row["file_path"] for row in rows}
        return [path for path in file_paths if path in locked]

    def _expire_locks(self, conn: sqlite3.Connection, now: str) -> None:
        conn.execute("DELETE FROM locks WHERE expires_at <= ?", (now,))

    def _init_db(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(SCHEMA)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _timestamps() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    return now.isoformat(), (now + LOCK_TTL).isoformat()
