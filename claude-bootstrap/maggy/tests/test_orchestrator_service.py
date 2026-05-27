"""Tests for OrchestratorService — team lifecycle."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maggy.orchestrator.models import Task
from maggy.services.orchestrator import OrchestratorService, TeamSession

_MOD = "maggy.services.orchestrator"


def _make_service(**overrides) -> OrchestratorService:
    cfg = MagicMock()
    cfg.orchestrator.max_concurrent = 3
    cfg.orchestrator.workspace_root = "/tmp/maggy-ws"
    cfg.orchestrator.container_timeout = 600
    return OrchestratorService(cfg=cfg, **overrides)


def _make_task(title: str = "Add auth") -> Task:
    return Task(title=title, source="test", source_ref="t1")


class TestSpawnTeam:
    @pytest.mark.asyncio
    async def test_creates_team_session(self):
        svc = _make_service()
        subtasks = [_make_task("sub-1"), _make_task("sub-2")]
        with patch.object(svc, "_run_team", new_callable=AsyncMock):
            session = await svc.spawn_team("parent-1", subtasks)
        assert isinstance(session, TeamSession)
        assert session.task_id == "parent-1"
        assert len(session.subtasks) == 2

    @pytest.mark.asyncio
    async def test_lists_active_teams(self):
        svc = _make_service()
        subtasks = [_make_task()]
        with patch.object(svc, "_run_team", new_callable=AsyncMock):
            await svc.spawn_team("t1", subtasks)
        teams = svc.list_teams()
        assert len(teams) == 1


class TestRunOne:
    @pytest.mark.asyncio
    async def test_container_lifecycle(self):
        svc = _make_service()
        subtask = _make_task()
        session = TeamSession(
            team_id="tm1", task_id="p1", subtasks=[subtask],
        )
        with patch(f"{_MOD}.async_create_container", new_callable=AsyncMock, return_value="cid1"), \
             patch(f"{_MOD}.async_start_container", new_callable=AsyncMock), \
             patch(f"{_MOD}.async_wait_container", new_callable=AsyncMock, return_value=0), \
             patch(f"{_MOD}.container_logs", return_value="done"), \
             patch(f"{_MOD}.async_remove_container", new_callable=AsyncMock), \
             patch(f"{_MOD}.route_subtask", return_value=MagicMock(id="rs1", agent="claude")):
            result = await svc._run_one(subtask, session)
        assert result.status == "succeeded"

    @pytest.mark.asyncio
    async def test_container_failure(self):
        svc = _make_service()
        subtask = _make_task()
        session = TeamSession(
            team_id="tm1", task_id="p1", subtasks=[subtask],
        )
        with patch(f"{_MOD}.async_create_container", new_callable=AsyncMock, side_effect=RuntimeError("no docker")):
            result = await svc._run_one(subtask, session)
        assert result.status == "failed"


class TestCancelTeam:
    @pytest.mark.asyncio
    async def test_cancel_sets_status(self):
        svc = _make_service()
        subtasks = [_make_task()]
        with patch.object(svc, "_run_team", new_callable=AsyncMock):
            session = await svc.spawn_team("t1", subtasks)
        await svc.cancel_team(session.team_id)
        assert svc.get_team(session.team_id).status == "cancelled"
