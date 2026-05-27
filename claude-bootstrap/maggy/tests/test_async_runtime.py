"""Tests for async Docker runtime wrappers."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from maggy.orchestrator.async_runtime import (
    async_create_container,
    async_start_container,
    async_wait_container,
)
from maggy.orchestrator.models import RunSpec

_MOD = "maggy.orchestrator.async_runtime"


def _make_spec(**overrides) -> RunSpec:
    defaults = dict(
        task_id="t1", agent="claude", identity="default",
        workspace="/tmp/ws", image="polyphony:latest",
    )
    defaults.update(overrides)
    return RunSpec(**defaults)


class TestAsyncCreateContainer:
    @pytest.mark.asyncio
    async def test_returns_container_id(self):
        spec = _make_spec()
        with patch(f"{_MOD}.create_container", return_value="abc123"):
            cid = await async_create_container(spec)
        assert cid == "abc123"

    @pytest.mark.asyncio
    async def test_propagates_error(self):
        spec = _make_spec()
        with patch(
            f"{_MOD}.create_container",
            side_effect=RuntimeError("docker not found"),
        ):
            with pytest.raises(RuntimeError, match="docker not found"):
                await async_create_container(spec)


class TestAsyncStartContainer:
    @pytest.mark.asyncio
    async def test_delegates_to_sync(self):
        with patch(f"{_MOD}.start_container") as mock:
            await async_start_container("abc123")
        mock.assert_called_once_with("abc123")


class TestAsyncWaitContainer:
    @pytest.mark.asyncio
    async def test_returns_exit_code(self):
        with patch(f"{_MOD}.wait_container", return_value=0):
            code = await async_wait_container("abc123")
        assert code == 0
