"""Behavioral signal collection from Claude Code hooks.

Hooks receive rich JSON on stdin (tool_name, tool_input, tool_response).
Instead of relying on agent cooperation (manually setting scope_tags),
we passively observe tool call patterns to derive fatigue signals.

Signals collected:
    - File paths from Read/Edit/Write tool calls (scope scatter)
    - Re-reads: same file Read'd more than once (context loss)
    - Tool errors from PostToolUse (struggling agent)
    - Edit frequency to same file (fix-retry loops)

Storage: .mnemos/signals.jsonl (append-only, one JSON line per event)
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


SIGNALS_FILE = 'signals.jsonl'
# Rolling window for fatigue computation
WINDOW_SIZE = 30


def append_signal(project_dir: str, signal: dict) -> None:
    """Append a signal event to signals.jsonl. Must be fast (<1ms)."""
    signals_path = Path(project_dir).resolve() / '.mnemos' / SIGNALS_FILE
    signals_path.parent.mkdir(parents=True, exist_ok=True)
    signal['ts'] = time.time()
    with open(signals_path, 'a') as f:
        f.write(json.dumps(signal) + '\n')


def read_recent_signals(project_dir: str, limit: int = WINDOW_SIZE) -> list[dict]:
    """Read the last N signals from the log. Reads from tail for speed."""
    signals_path = Path(project_dir).resolve() / '.mnemos' / SIGNALS_FILE
    if not signals_path.exists():
        return []

    try:
        # Read last N lines efficiently
        lines = _tail(str(signals_path), limit)
        signals = []
        for line in lines:
            line = line.strip()
            if line:
                try:
                    signals.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return signals
    except OSError:
        return []


def compute_scope_scatter(signals: list[dict]) -> float:
    """Scope scatter: how many different directories is the agent touching?

    Low scatter (focused on 1-2 dirs) = 0.0 (no fatigue).
    High scatter (bouncing across 8+ dirs) = 1.0 (max fatigue).

    Only considers file-bearing tool calls (Read, Edit, Write, Glob, Grep).
    """
    dirs = []
    for s in signals:
        fp = s.get('file_path', '')
        if fp:
            # Normalize to parent directory (2 levels deep max)
            parts = Path(fp).parts
            if len(parts) >= 3:
                dirs.append('/'.join(parts[:3]))
            elif len(parts) >= 2:
                dirs.append('/'.join(parts[:2]))
            elif parts:
                dirs.append(parts[0])

    if not dirs:
        return 0.0

    unique_dirs = len(set(dirs))
    total = len(dirs)

    # 1-2 unique dirs in 30 calls = very focused = 0.0
    # 3-4 = mild scatter = 0.2-0.4
    # 5-7 = moderate = 0.4-0.7
    # 8+ = high scatter = 0.7-1.0
    ratio = unique_dirs / max(total, 1)
    # Scale: ratio of 0.1 (1 dir in 10 calls) = 0, ratio of 0.5+ = 1.0
    return min(1.0, max(0.0, (ratio - 0.1) / 0.4))


def compute_reread_ratio(signals: list[dict]) -> float:
    """Re-read ratio: how often does the agent re-read files it already read?

    High re-reads = agent lost context of what it saw = context degradation.
    Returns 0.0-1.0.
    """
    reads = [s['file_path'] for s in signals
             if s.get('tool') == 'Read' and s.get('file_path')]

    if len(reads) < 3:
        return 0.0

    seen = set()
    rereads = 0
    for fp in reads:
        if fp in seen:
            rereads += 1
        seen.add(fp)

    return min(1.0, rereads / max(len(reads), 1))


def compute_error_density(signals: list[dict]) -> float:
    """Error density: ratio of failed tool calls in recent window.

    High error rate = agent is struggling/confused.
    Returns 0.0-1.0.
    """
    outcomes = [s for s in signals if 'success' in s]
    if not outcomes:
        return 0.0

    errors = sum(1 for s in outcomes if not s['success'])
    return min(1.0, errors / max(len(outcomes), 1))


def extract_signal_from_pre_tool(hook_input: dict) -> dict | None:
    """Extract a signal from PreToolUse hook JSON input.

    Returns a signal dict to append, or None if not relevant.
    """
    tool = hook_input.get('tool_name', '')
    tool_input = hook_input.get('tool_input', {})

    # Extract file path from various tool inputs
    file_path = (
        tool_input.get('file_path')
        or tool_input.get('path')
        or ''
    )

    # For Bash, try to extract paths from command
    if tool == 'Bash' and not file_path:
        cmd = tool_input.get('command', '')
        # Don't log bash commands as file signals
        return {'tool': 'Bash', 'event': 'pre'}

    if tool in ('Read', 'Edit', 'Write', 'Glob', 'Grep'):
        return {
            'tool': tool,
            'event': 'pre',
            'file_path': _normalize_path(file_path)
        }

    return {'tool': tool, 'event': 'pre'}


def extract_signal_from_post_tool(hook_input: dict) -> dict | None:
    """Extract a signal from PostToolUse hook JSON input.

    Captures success/failure for error density computation.
    """
    tool = hook_input.get('tool_name', '')
    tool_input = hook_input.get('tool_input', {})
    response = hook_input.get('tool_response', {})

    file_path = (
        tool_input.get('file_path')
        or tool_input.get('path')
        or ''
    )

    # Determine success/failure
    success = True
    if isinstance(response, dict):
        # Check for common error indicators
        if response.get('error') or response.get('is_error'):
            success = False
        # Bash exit code
        if 'exit_code' in response and response['exit_code'] != 0:
            success = False
    elif isinstance(response, str):
        # String responses with error markers
        if response.startswith('Error:') or response.startswith('error:'):
            success = False

    return {
        'tool': tool,
        'event': 'post',
        'file_path': _normalize_path(file_path),
        'success': success
    }


def _normalize_path(file_path: str) -> str:
    """Normalize file path to relative form for consistent comparison."""
    if not file_path:
        return ''
    p = Path(file_path)
    # Convert absolute paths to relative if within CWD
    try:
        return str(p.relative_to(Path.cwd()))
    except ValueError:
        return str(p)


def _tail(filepath: str, n: int) -> list[str]:
    """Read last n lines from a file efficiently."""
    try:
        with open(filepath, 'rb') as f:
            # Seek to end
            f.seek(0, 2)
            size = f.tell()
            if size == 0:
                return []

            # Read backwards in chunks
            chunk_size = min(size, n * 500)  # ~500 bytes per line estimate
            f.seek(max(0, size - chunk_size))
            data = f.read().decode('utf-8', errors='replace')
            lines = data.strip().split('\n')
            return lines[-n:]
    except OSError:
        return []


def get_session_stats(project_dir: str) -> dict:
    """Get summary stats from signal log for diagnostics."""
    signals = read_recent_signals(project_dir, limit=100)
    if not signals:
        return {'total_signals': 0}

    tools = {}
    files_read = set()
    rereads = 0
    errors = 0
    total_outcomes = 0
    seen_reads = set()

    for s in signals:
        tool = s.get('tool', 'unknown')
        tools[tool] = tools.get(tool, 0) + 1

        fp = s.get('file_path', '')
        if s.get('tool') == 'Read' and fp:
            if fp in seen_reads:
                rereads += 1
            seen_reads.add(fp)
            files_read.add(fp)

        if 'success' in s:
            total_outcomes += 1
            if not s['success']:
                errors += 1

    return {
        'total_signals': len(signals),
        'tool_calls': tools,
        'unique_files_read': len(files_read),
        'rereads': rereads,
        'errors': errors,
        'total_outcomes': total_outcomes,
        'error_rate': errors / max(total_outcomes, 1)
    }
