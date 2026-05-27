"""Lightweight shell command execution for terminal-like chat."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from maggy.api.auth import check_auth

router = APIRouter(prefix="/api/shell", tags=["shell"])

# Allowed command prefixes — safe, read-only or navigation commands
ALLOWED_COMMANDS = {
    "ls", "pwd", "cat", "head", "tail", "wc",
    "find", "grep", "rg", "tree", "file", "stat",
    "du", "df", "whoami", "date", "echo", "which",
    "git", "cd", "env", "printenv", "uname", "hostname",
}

# Blocked patterns — never allow these
BLOCKED_PATTERNS = [
    "rm ", "rm\t", "rmdir", "mkfs", "dd ",
    "sudo", "su ", "chmod", "chown", "chgrp",
    "> ", ">> ", "| rm", "; rm", "&& rm",
    "curl ", "wget ", "ssh ", "scp ",
    "kill ", "killall", "pkill",
    "mv ", "cp ", "mkdir ",  # write ops
    "pip ", "npm ", "brew ",
]

MAX_OUTPUT = 8000
TIMEOUT_S = 10


def _is_safe(cmd: str) -> bool:
    """Check if a command is in the allowlist."""
    stripped = cmd.strip()
    if not stripped:
        return False
    first_word = stripped.split()[0].split("/")[-1]
    if first_word not in ALLOWED_COMMANDS:
        return False
    lower = stripped.lower()
    for pat in BLOCKED_PATTERNS:
        if pat in lower:
            return False
    return True


class ShellRequest(BaseModel):
    command: str
    cwd: str | None = None


@router.post("/exec")
async def exec_command(
    request: Request,
    body: ShellRequest,
    x_api_key: str | None = Header(None),
) -> dict:
    """Execute a safe shell command and return output."""
    check_auth(request, x_api_key)

    cmd = body.command.strip()

    # Handle cd specially — just validate the path
    if cmd == "cd" or cmd.startswith("cd "):
        base = body.cwd if body.cwd else os.path.expanduser("~")
        if not os.path.isdir(base):
            base = os.path.expanduser("~")
        parts = cmd.split(None, 1)
        target = parts[1] if len(parts) > 1 else os.path.expanduser("~")
        target = os.path.expanduser(target)
        if not os.path.isabs(target):
            target = os.path.normpath(os.path.join(base, target))
        if os.path.isdir(target):
            return {"output": "", "cwd": target, "exit_code": 0}
        return {
            "output": f"cd: no such directory: {target}",
            "cwd": base,
            "exit_code": 1,
        }

    if not _is_safe(cmd):
        return {
            "output": f"Command not allowed: {cmd.split()[0]}\n"
                      f"Allowed: {', '.join(sorted(ALLOWED_COMMANDS))}",
            "cwd": body.cwd or os.getcwd(),
            "exit_code": 126,
        }

    cwd = body.cwd if body.cwd else None
    if not cwd or not os.path.isdir(cwd):
        cwd = os.path.expanduser("~")

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
            env={**os.environ, "TERM": "dumb", "NO_COLOR": "1"},
        )
        stdout, _ = await asyncio.wait_for(
            proc.communicate(), timeout=TIMEOUT_S
        )
        output = stdout.decode("utf-8", errors="replace")
        if len(output) > MAX_OUTPUT:
            output = output[:MAX_OUTPUT] + f"\n… (truncated, {len(stdout)} bytes total)"
        return {
            "output": output,
            "cwd": cwd,
            "exit_code": proc.returncode if proc.returncode is not None else 0,
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {
            "output": f"Command timed out after {TIMEOUT_S}s",
            "cwd": cwd,
            "exit_code": 124,
        }
    except Exception as e:
        return {
            "output": f"Error: {e}",
            "cwd": cwd,
            "exit_code": 1,
        }
