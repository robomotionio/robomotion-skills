"""Tests for DualPlanner orchestration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from maggy.adapters.pi import RunResult
from maggy.services.planner import DualPlanner


def _result(output: str) -> RunResult:
    return RunResult(model="test", success=True, output=output)


@pytest.mark.asyncio
async def test_plan_uses_claude_prompt() -> None:
    pi = MagicMock()
    pi.send_prompt = AsyncMock(return_value=_result("Primary plan"))
    planner = DualPlanner(pi)

    plan = await planner.plan("Fix auth", "Add logout flow", "/tmp/work")

    assert plan == "Primary plan"
    pi.send_prompt.assert_awaited_once()
    args = pi.send_prompt.await_args.args
    assert args[0] == "claude"
    assert args[2] == "/tmp/work"
    assert args[3] == 5
    assert "Fix auth" in args[1]
    assert "Add logout flow" in args[1]


@pytest.mark.asyncio
async def test_counter_check_uses_codex_prompt() -> None:
    pi = MagicMock()
    pi.send_prompt = AsyncMock(return_value=_result("Looks good"))
    planner = DualPlanner(pi)

    review = await planner.counter_check("1. Update auth\n2. Add tests", "/tmp/work")

    assert review == "Looks good"
    args = pi.send_prompt.await_args.args
    assert args[0] == "codex"
    assert args[2] == "/tmp/work"
    assert args[3] == 5
    assert "1. Update auth" in args[1]
    assert "Flag conflicts as 'CONFLICT:'" in args[1]


@pytest.mark.asyncio
async def test_dual_plan_collects_conflicts() -> None:
    pi = MagicMock()
    pi.send_prompt = AsyncMock(
        side_effect=[
            _result("1. Update auth\n2. Add tests"),
            _result("CONFLICT: use middleware\nkeep step 2"),
        ]
    )
    planner = DualPlanner(pi)

    result = await planner.dual_plan("Fix auth", "Add logout flow", "/tmp/work")

    assert result.primary_plan.startswith("1. Update auth")
    assert result.counter_check.startswith("CONFLICT:")
    assert result.conflicts == ["use middleware"]
