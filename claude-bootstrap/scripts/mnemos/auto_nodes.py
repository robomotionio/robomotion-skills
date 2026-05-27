"""Fatigue-driven auto-node creation from tool signals.

Interval adapts to fatigue state:
  FLOW       (0.00-0.40): every 40 calls — low urgency, save tokens
  COMPRESS   (0.40-0.60): every 20 calls — context filling, capture more
  PRE_SLEEP  (0.60-0.75): every 10 calls — aggressive capture
  REM        (0.75-0.90): every 5 calls  — about to lose context
  EMERGENCY  (0.90+):     every call     — capture everything

Creates nodes from:
1. Git commits (ResultNode from commit message) — immediate
2. Edit clusters (ResultNode summarizing files touched) — periodic
3. New commits since last check — periodic
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
import uuid
from pathlib import Path

# Fatigue-driven intervals: state → tool calls between auto-adds
FATIGUE_INTERVALS = {
    "FLOW": 40,
    "COMPRESS": 20,
    "PRE_SLEEP": 10,
    "REM": 5,
    "EMERGENCY": 1,
}
DEFAULT_INTERVAL = 25

COOLDOWN_S = 120  # 2 min cooldown between periodic auto-adds
COUNTER_FILE = "auto-node-counter"
LAST_COMMIT_FILE = "last-auto-commit"
LAST_AUTO_NODE_FILE = "last-auto-node-ts"


def _get_fatigue_state(mnemos_dir: Path) -> tuple[float, str]:
    """Read current fatigue score and state."""
    fatigue_path = mnemos_dir / "fatigue.json"
    try:
        with open(fatigue_path) as f:
            data = json.load(f)
        score = data.get("score", 0.0)
        state = data.get("state", "FLOW")
        return score, state
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return 0.0, "FLOW"


def _get_interval(mnemos_dir: Path) -> int:
    """Get auto-add interval based on current fatigue state."""
    _, state = _get_fatigue_state(mnemos_dir)
    return FATIGUE_INTERVALS.get(state, DEFAULT_INTERVAL)


def should_run(mnemos_dir: Path) -> bool:
    """Check if we've hit the fatigue-driven interval threshold."""
    counter_path = mnemos_dir / COUNTER_FILE
    count = 0
    try:
        count = int(counter_path.read_text().strip())
    except (FileNotFoundError, ValueError):
        pass

    count += 1
    interval = _get_interval(mnemos_dir)

    if count < interval:
        counter_path.write_text(str(count))
        return False

    # Reset counter
    counter_path.write_text("0")

    # Check cooldown — shorter at higher fatigue
    _, state = _get_fatigue_state(mnemos_dir)
    cooldown = COOLDOWN_S
    if state == "PRE_SLEEP":
        cooldown = 60
    elif state == "REM":
        cooldown = 30
    elif state == "EMERGENCY":
        cooldown = 0

    ts_path = mnemos_dir / LAST_AUTO_NODE_FILE
    try:
        last_ts = float(ts_path.read_text().strip())
        if time.time() - last_ts < cooldown:
            return False
    except (FileNotFoundError, ValueError):
        pass

    return True


def detect_git_commit(tool_name: str, tool_input: dict,
                      tool_response: str | dict) -> str | None:
    """If this tool call was a git commit, return the commit message."""
    if tool_name != "Bash":
        return None

    cmd = ""
    if isinstance(tool_input, dict):
        cmd = tool_input.get("command", "")
    elif isinstance(tool_input, str):
        cmd = tool_input

    if "git commit" not in cmd:
        return None

    # Check response indicates success
    resp_text = ""
    if isinstance(tool_response, str):
        resp_text = tool_response
    elif isinstance(tool_response, dict):
        resp_text = tool_response.get("stdout", "")
        resp_text += tool_response.get("output", "")

    if not resp_text or "nothing to commit" in resp_text:
        return None

    # Extract commit message from the command
    msg_match = re.search(r'-m\s+["\'](.+?)["\']', cmd)
    if msg_match:
        return msg_match.group(1)

    # Try heredoc pattern
    heredoc_match = re.search(
        r"cat\s+<<'?EOF'?\n(.+?)\nEOF", cmd, re.DOTALL
    )
    if heredoc_match:
        return heredoc_match.group(1).strip().split("\n")[0]

    return None


def run_auto_add(mnemos_dir: Path) -> list[dict]:
    """Create auto-nodes from recent activity. Returns created nodes."""
    import sqlite3

    db_path = mnemos_dir / "mnemo.db"
    if not db_path.exists():
        return []

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    created = []

    # 1. New git commits since last check
    created.extend(_create_commit_nodes(mnemos_dir, conn))

    # 2. Summarize recent file edits
    created.extend(_create_edit_summary(mnemos_dir, conn))

    if created:
        ts_path = mnemos_dir / LAST_AUTO_NODE_FILE
        ts_path.write_text(str(time.time()))

    conn.close()
    return created


def create_commit_node(mnemos_dir: Path, commit_msg: str) -> dict | None:
    """Create a ResultNode immediately from a detected git commit."""
    import sqlite3

    db_path = mnemos_dir / "mnemo.db"
    if not db_path.exists():
        return None

    conn = sqlite3.connect(str(db_path))
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    node_id = str(uuid.uuid4())
    content = commit_msg[:200]

    conn.execute(
        "INSERT INTO mnemo_nodes "
        "(id, type, task_id, content, activation_weight, "
        "status, origin, confidence, scope_tags, "
        "created_at, last_accessed, access_count) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (node_id, "result", "auto-commit", content,
         1.0, "active", "auto-commit", 0.9, "[]",
         now, now, 0),
    )
    conn.commit()
    conn.close()

    return {"id": node_id, "type": "result", "content": content}


def _create_commit_nodes(
    mnemos_dir: Path, conn: object
) -> list[dict]:
    """Create ResultNodes from git commits since last check."""
    last_commit_path = mnemos_dir / LAST_COMMIT_FILE
    last_hash = ""
    try:
        last_hash = last_commit_path.read_text().strip()
    except FileNotFoundError:
        pass

    cwd = str(mnemos_dir.parent)
    try:
        if last_hash:
            result = subprocess.run(
                ["git", "log", f"{last_hash}..HEAD",
                 "--format=%H|%s", "--no-merges"],
                capture_output=True, text=True, cwd=cwd,
            )
        else:
            result = subprocess.run(
                ["git", "log", "-5",
                 "--format=%H|%s", "--no-merges"],
                capture_output=True, text=True, cwd=cwd,
            )
    except Exception:
        return []

    if result.returncode != 0 or not result.stdout.strip():
        return []

    lines = result.stdout.strip().split("\n")
    nodes = []
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    latest_hash = ""

    for line in lines:
        parts = line.split("|", 1)
        if len(parts) != 2:
            continue
        commit_hash, msg = parts
        if not latest_hash:
            latest_hash = commit_hash
        if len(msg) < 5:
            continue

        node_id = str(uuid.uuid4())
        conn.execute(
            "INSERT OR IGNORE INTO mnemo_nodes "
            "(id, type, task_id, content, activation_weight, "
            "status, origin, confidence, scope_tags, "
            "created_at, last_accessed, access_count) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (node_id, "result", "auto-commit", msg[:200],
             0.8, "active", "auto-commit", 0.9, "[]",
             now, now, 0),
        )
        nodes.append({"id": node_id, "type": "result",
                       "content": msg[:200]})

    if latest_hash:
        last_commit_path.write_text(latest_hash)
    if nodes:
        conn.commit()

    return nodes


def _create_edit_summary(
    mnemos_dir: Path, conn: object
) -> list[dict]:
    """Summarize recent file edits into a ResultNode."""
    signals_path = mnemos_dir / "signals.jsonl"
    if not signals_path.exists():
        return []

    try:
        with open(signals_path, "rb") as f:
            f.seek(0, 2)
            pos = f.tell()
            read_size = min(32768, pos)
            if read_size == 0:
                return []
            f.seek(pos - read_size)
            chunk = f.read().decode("utf-8", errors="replace")
    except Exception:
        return []

    lines = chunk.strip().split("\n")

    # At higher fatigue, look at fewer recent signals (more focused)
    _, state = _get_fatigue_state(mnemos_dir)
    window = {"FLOW": 50, "COMPRESS": 30, "PRE_SLEEP": 20,
              "REM": 10, "EMERGENCY": 5}.get(state, 50)
    recent = lines[-window:]

    edited_files: dict[str, int] = {}
    error_count = 0
    for line in recent:
        try:
            sig = json.loads(line)
        except Exception:
            continue
        tool = sig.get("tool", "")
        fp = sig.get("file_path", "")
        if tool in ("Edit", "Write", "MultiEdit") and fp:
            short = fp.split("/")[-1] if "/" in fp else fp
            edited_files[short] = edited_files.get(short, 0) + 1
        if not sig.get("success", True):
            error_count += 1

    if not edited_files:
        return []

    top_files = sorted(edited_files.items(), key=lambda x: -x[1])[:8]
    file_list = ", ".join(
        f"{f}({c}x)" if c > 1 else f for f, c in top_files
    )
    content = f"Editing: {file_list}"
    if error_count > 3:
        content += f" ({error_count} errors)"

    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    node_id = str(uuid.uuid4())
    conn.execute(
        "INSERT OR IGNORE INTO mnemo_nodes "
        "(id, type, task_id, content, activation_weight, "
        "status, origin, confidence, scope_tags, "
        "created_at, last_accessed, access_count) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (node_id, "result", "auto-edit", content,
         0.6, "active", "auto-edit", 0.7, "[]",
         now, now, 0),
    )
    conn.commit()

    return [{"id": node_id, "type": "result", "content": content}]
