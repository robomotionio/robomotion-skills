"""LLM-based task decomposition for parallel execution.

Asks an LLM to split a complex task into 2-5 independent subtasks.
Falls back to a single-task list if decomposition fails.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from .models import Task

if TYPE_CHECKING:
    from maggy.adapters.pi import PiAdapter

logger = logging.getLogger(__name__)

_PROMPT = (
    "Split this task into 2-5 independent subtasks that can run in parallel.\n"
    "Return a JSON array of objects with keys: title, source_ref.\n"
    "Each subtask must be self-contained.\n\n"
    "Task: {title}\nDescription: {description}\n\n"
    "Return ONLY the JSON array, no markdown."
)

MAX_SUBTASKS = 5


def should_decompose(
    blast: int, file_count: int, user_requested: bool = False,
) -> bool:
    """Decide whether a task warrants decomposition."""
    return user_requested or blast >= 7 or file_count >= 5


async def decompose_task(
    pi: "PiAdapter", title: str, description: str,
) -> list[Task]:
    """Ask LLM to split task into subtasks."""
    prompt = _PROMPT.format(title=title, description=description)
    try:
        result = await pi.send_prompt("claude", prompt, "/tmp")
        if not result.success:
            return [_fallback_task(title)]
        return _parse_subtasks(result.output, title)
    except Exception as exc:
        logger.warning("Decomposition failed: %s", exc)
        return [_fallback_task(title)]


def _parse_subtasks(raw: str, fallback_title: str) -> list[Task]:
    """Parse JSON array into Task list, capped at MAX_SUBTASKS."""
    try:
        items = json.loads(raw)
        if not isinstance(items, list) or not items:
            return [_fallback_task(fallback_title)]
    except (json.JSONDecodeError, ValueError):
        return [_fallback_task(fallback_title)]
    tasks = [
        Task(
            title=item["title"],
            source="decomposer",
            source_ref=item.get("source_ref", "decomposed"),
        )
        for item in items[:MAX_SUBTASKS]
        if isinstance(item, dict) and "title" in item
    ]
    return tasks or [_fallback_task(fallback_title)]


def _fallback_task(title: str) -> Task:
    """Single-task fallback when decomposition fails."""
    return Task(title=title, source="decomposer", source_ref="fallback")
