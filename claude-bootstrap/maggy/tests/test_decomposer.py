"""Tests for LLM-based task decomposition."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from maggy.orchestrator.decomposer import (
    decompose_task,
    should_decompose,
)


class TestShouldDecompose:
    def test_high_blast_triggers(self):
        assert should_decompose(blast=7, file_count=2) is True

    def test_many_files_triggers(self):
        assert should_decompose(blast=3, file_count=5) is True

    def test_user_override_triggers(self):
        assert should_decompose(blast=1, file_count=1, user_requested=True) is True

    def test_low_complexity_skips(self):
        assert should_decompose(blast=3, file_count=2) is False


class TestDecomposeTask:
    @pytest.mark.asyncio
    async def test_returns_subtasks(self):
        mock_pi = AsyncMock()
        mock_pi.send_prompt.return_value = AsyncMock(
            success=True,
            output='[{"title":"Add model","source":"decomposer","source_ref":"t1"},'
                   '{"title":"Add tests","source":"decomposer","source_ref":"t1"}]',
        )
        result = await decompose_task(mock_pi, "Build auth", "Add JWT auth")
        assert len(result) == 2
        assert result[0].title == "Add model"

    @pytest.mark.asyncio
    async def test_fallback_on_failure(self):
        mock_pi = AsyncMock()
        mock_pi.send_prompt.return_value = AsyncMock(
            success=False, output="error",
        )
        result = await decompose_task(mock_pi, "Build auth", "Add JWT auth")
        assert len(result) == 1
        assert result[0].title == "Build auth"

    @pytest.mark.asyncio
    async def test_caps_at_five_subtasks(self):
        items = [
            {"title": f"sub-{i}", "source": "decomposer", "source_ref": "t1"}
            for i in range(8)
        ]
        mock_pi = AsyncMock()
        mock_pi.send_prompt.return_value = AsyncMock(
            success=True,
            output=str(items).replace("'", '"'),
        )
        result = await decompose_task(mock_pi, "Big task", "Lots of work")
        assert len(result) <= 5
