"""Tests for background task manager."""
from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock

import pytest

from maggy.cli_bg_task import (
    TaskState,
    cancel_task,
    collect_result,
    get_status,
    is_active,
    start_task,
)


# -- TaskState --


def test_task_state_defaults():
    """New TaskState starts idle with empty fields."""
    state = TaskState()
    assert state.status == "idle"
    assert state.chunks_received == 0
    assert state.tool_events == []
    assert state.content == ""
    assert state.error == ""
    assert state.model == ""
    assert not state.cancel_event.is_set()


# -- start_task --


def test_start_task_returns_running_state():
    """start_task spawns thread and returns running state."""
    chunks = iter([
        {"type": "text", "content": "hello"},
        {"type": "done"},
    ])
    console = MagicMock()
    state = start_task(chunks, console)
    assert state.status in ("running", "done")
    # Wait for thread to finish
    time.sleep(0.3)
    assert state.status == "done"
    assert state.content == "hello"


def test_start_task_accumulates_tool_events():
    """Tool events are collected during background streaming."""
    chunks = iter([
        {"type": "tool_use", "tool": "Read", "input": {"file_path": "/a/b.py"}},
        {"type": "tool_use", "tool": "Bash", "input": {"command": "ls"}},
        {"type": "text", "content": "done"},
        {"type": "done"},
    ])
    console = MagicMock()
    state = start_task(chunks, console)
    time.sleep(0.3)
    assert len(state.tool_events) == 2
    assert state.chunks_received >= 4


def test_start_task_captures_error():
    """Error chunks set error field."""
    chunks = iter([
        {"type": "error", "content": "CLI not found"},
        {"type": "done"},
    ])
    console = MagicMock()
    state = start_task(chunks, console)
    time.sleep(0.3)
    assert state.error == "CLI not found"
    assert state.status == "done"


def test_start_task_captures_model():
    """Routing chunk sets model field."""
    chunks = iter([
        {"type": "routing", "model": "claude"},
        {"type": "text", "content": "hi"},
        {"type": "done"},
    ])
    console = MagicMock()
    state = start_task(chunks, console)
    time.sleep(0.3)
    assert state.model == "claude"


# -- cancel_task --


def test_cancel_stops_running_task():
    """cancel_task sets cancel event and status."""
    def slow_chunks():
        yield {"type": "text", "content": "a"}
        time.sleep(0.2)
        yield {"type": "text", "content": "b"}
        yield {"type": "done"}
    console = MagicMock()
    state = start_task(slow_chunks(), console)
    time.sleep(0.1)
    result = cancel_task(state)
    assert result is True
    time.sleep(0.5)
    assert state.status == "cancelled"


def test_cancel_idle_returns_false():
    """Cancelling idle state returns False."""
    state = TaskState()
    assert cancel_task(state) is False


# -- get_status --


def test_get_status_returns_snapshot():
    """get_status returns thread-safe dict snapshot."""
    state = TaskState()
    state.status = "running"
    state.chunks_received = 5
    state.model = "codex"
    snap = get_status(state)
    assert snap["status"] == "running"
    assert snap["chunks"] == 5
    assert snap["model"] == "codex"


# -- is_active --


def test_is_active_running():
    """is_active True when running."""
    state = TaskState()
    state.status = "running"
    assert is_active(state) is True


def test_is_active_idle():
    """is_active False when idle."""
    state = TaskState()
    assert is_active(state) is False


def test_is_active_done():
    """is_active False when done."""
    state = TaskState()
    state.status = "done"
    assert is_active(state) is False


# -- collect_result --


def test_collect_result_returns_events_and_content():
    """collect_result returns accumulated data."""
    state = TaskState()
    state.tool_events = ["Read a/b.py", "$ ls"]
    state.content = "final output"
    result = collect_result(state)
    assert result["tool_events"] == ["Read a/b.py", "$ ls"]
    assert result["content"] == "final output"
