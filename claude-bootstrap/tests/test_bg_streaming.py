"""Tests for background task live streaming output."""
from __future__ import annotations

import time
from io import StringIO
from unittest.mock import MagicMock

from rich.console import Console

from maggy.cli_bg_task import start_task


def _capture_console() -> Console:
    """Create a console that captures output to a string buffer."""
    return Console(file=StringIO(), force_terminal=False, width=120)


def test_routing_chunk_prints_model():
    """Routing event prints model name to console."""
    chunks = iter([
        {"type": "routing", "model": "local"},
        {"type": "done"},
    ])
    console = _capture_console()
    state = start_task(chunks, console)
    time.sleep(0.3)
    output = console.file.getvalue()
    assert "local" in output


def test_tool_use_chunk_prints_label():
    """Tool use event prints tool label to console."""
    chunks = iter([
        {"type": "tool_use", "tool": "Read", "input": {"file_path": "/a.py"}},
        {"type": "done"},
    ])
    console = _capture_console()
    state = start_task(chunks, console)
    time.sleep(0.3)
    output = console.file.getvalue()
    assert "Read" in output
    assert "/a.py" in output


def test_text_chunk_silent():
    """Text chunks accumulate silently — no live print."""
    chunks = iter([
        {"type": "text", "content": "hello world"},
        {"type": "done"},
    ])
    console = _capture_console()
    state = start_task(chunks, console)
    time.sleep(0.3)
    output = console.file.getvalue()
    assert "hello world" not in output
    assert state.content == "hello world"


def test_error_chunk_silent():
    """Error chunks stored in state — no live print."""
    chunks = iter([
        {"type": "error", "content": "CLI crashed"},
        {"type": "done"},
    ])
    console = _capture_console()
    state = start_task(chunks, console)
    time.sleep(0.3)
    output = console.file.getvalue()
    assert "CLI crashed" not in output
    assert state.error == "CLI crashed"


def test_multiple_tools_stream_live():
    """Multiple tool events all stream live."""
    chunks = iter([
        {"type": "routing", "model": "codex"},
        {"type": "tool_use", "tool": "Read", "input": {"file_path": "/x"}},
        {"type": "tool_use", "tool": "Bash", "input": {"command": "ls"}},
        {"type": "text", "content": "result"},
        {"type": "done"},
    ])
    console = _capture_console()
    state = start_task(chunks, console)
    time.sleep(0.3)
    output = console.file.getvalue()
    assert "codex" in output
    assert "Read" in output
    assert "$ ls" in output
    assert "result" not in output
