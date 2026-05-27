"""Git-backed rollback savepoints for Maggy sessions."""

from __future__ import annotations

import asyncio
import re

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_\-]+$")


def _validate_session_id(session_id: str) -> None:
    if not _SAFE_ID.match(session_id):
        raise ValueError(f"Invalid session_id: {session_id!r}")


class RollbackManager:
    async def create_savepoint(self, session_id: str, working_dir: str) -> str:
        _validate_session_id(session_id)
        tag = _tag_name(session_id)
        code, output = await _run_git(working_dir, "tag", tag)
        if code != 0:
            raise RuntimeError(output or f"failed to create {tag}")
        return tag

    async def rollback(self, session_id: str, working_dir: str) -> bool:
        _validate_session_id(session_id)
        code, _ = await _run_git(working_dir, "reset", "--hard", _tag_name(session_id))
        return code == 0

    async def list_savepoints(self, working_dir: str) -> list[str]:
        code, output = await _run_git(working_dir, "tag", "--list", "maggy-save-*")
        if code != 0 or not output:
            return []
        return output.splitlines()

    async def delete_savepoint(self, session_id: str, working_dir: str) -> bool:
        code, _ = await _run_git(working_dir, "tag", "-d", _tag_name(session_id))
        return code == 0


async def _run_git(working_dir: str, *args: str) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        "git",
        *args,
        cwd=working_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout, _ = await proc.communicate()
    text = (stdout or b"").decode("utf-8", errors="replace").strip()
    return proc.returncode or 0, text


def _tag_name(session_id: str) -> str:
    return f"maggy-save-{session_id}"
