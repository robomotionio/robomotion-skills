"""Tests for multi-agent coordination locks."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

from maggy.coordination.lock_manager import LockManager


class TestLockManager:
    def test_acquire_and_release(self, tmp_path):
        manager = LockManager(tmp_path / "locks.db")
        assert manager.acquire("maggy/a.py", "agent-1") is True
        assert manager.release("maggy/a.py", "agent-1") is True
        assert manager.release("maggy/a.py", "agent-1") is False

    def test_blocks_other_agent(self, tmp_path):
        manager = LockManager(tmp_path / "locks.db")
        assert manager.acquire("maggy/a.py", "agent-1") is True
        assert manager.acquire("maggy/a.py", "agent-2") is False

    def test_release_all_returns_count(self, tmp_path):
        manager = LockManager(tmp_path / "locks.db")
        manager.acquire("maggy/a.py", "agent-1")
        manager.acquire("maggy/b.py", "agent-1")
        manager.acquire("maggy/c.py", "agent-2")
        assert manager.release_all("agent-1") == 2
        assert manager.conflicts(["maggy/a.py", "maggy/c.py"]) == ["maggy/c.py"]

    def test_conflicts_returns_locked_paths(self, tmp_path):
        manager = LockManager(tmp_path / "locks.db")
        manager.acquire("maggy/a.py", "agent-1")
        manager.acquire("maggy/c.py", "agent-2")
        conflicts = manager.conflicts(["maggy/a.py", "maggy/b.py", "maggy/c.py"])
        assert conflicts == ["maggy/a.py", "maggy/c.py"]

    def test_expired_locks_are_removed(self, tmp_path):
        db_path = tmp_path / "locks.db"
        manager = LockManager(db_path)
        expired_at = datetime.now(timezone.utc) - timedelta(minutes=31)
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "INSERT INTO locks(file_path, agent_id, acquired_at, expires_at) "
                "VALUES (?, ?, ?, ?)",
                (
                    "maggy/a.py",
                    "agent-1",
                    expired_at.isoformat(),
                    expired_at.isoformat(),
                ),
            )
            conn.commit()
        assert manager.acquire("maggy/a.py", "agent-2") is True
