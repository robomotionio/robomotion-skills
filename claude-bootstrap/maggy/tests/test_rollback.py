"""Tests for rollback and savepoint recovery."""

from __future__ import annotations

import subprocess

import pytest

from maggy.recovery.rollback import RollbackManager


def _git(repo, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True)


def _init_repo(repo) -> None:
    _git(repo, "init")
    _git(repo, "config", "user.email", "maggy@example.com")
    _git(repo, "config", "user.name", "Maggy Tests")
    (repo / "tracked.txt").write_text("v1\n")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "init")


class TestRollbackManager:
    @pytest.mark.asyncio
    async def test_create_and_list_savepoints(self, tmp_path):
        _init_repo(tmp_path)
        manager = RollbackManager()
        tag = await manager.create_savepoint("session-1", str(tmp_path))
        assert tag == "maggy-save-session-1"
        assert await manager.list_savepoints(str(tmp_path)) == [tag]

    @pytest.mark.asyncio
    async def test_rollback_resets_worktree(self, tmp_path):
        _init_repo(tmp_path)
        manager = RollbackManager()
        await manager.create_savepoint("session-1", str(tmp_path))
        (tmp_path / "tracked.txt").write_text("changed\n")
        assert await manager.rollback("session-1", str(tmp_path)) is True
        assert (tmp_path / "tracked.txt").read_text() == "v1\n"

    @pytest.mark.asyncio
    async def test_delete_savepoint(self, tmp_path):
        _init_repo(tmp_path)
        manager = RollbackManager()
        await manager.create_savepoint("session-1", str(tmp_path))
        assert await manager.delete_savepoint("session-1", str(tmp_path)) is True
        assert await manager.list_savepoints(str(tmp_path)) == []
