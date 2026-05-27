"""JSON checkpoint persistence for fallback chains."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_DIR = Path.home() / ".maggy" / "checkpoints"


class CheckpointManager:
    def __init__(self, base_dir: Path = DEFAULT_DIR):
        self.base_dir = base_dir.expanduser()

    def write(self, session_id: str, data: dict) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        payload = _normalize(data)
        target = self._path(session_id)
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2))
        tmp.replace(target)

    def read(self, session_id: str) -> dict | None:
        path = self._path(session_id)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def delete(self, session_id: str) -> bool:
        path = self._path(session_id)
        if not path.exists():
            return False
        path.unlink()
        return True

    def list_checkpoints(self) -> list[str]:
        if not self.base_dir.exists():
            return []
        names = [path.stem for path in self.base_dir.glob("*.json")]
        return sorted(names)

    def _path(self, session_id: str) -> Path:
        safe_id = _sanitize_id(session_id)
        target = (self.base_dir / f"{safe_id}.json").resolve()
        if not str(target).startswith(str(self.base_dir.resolve())):
            raise ValueError(f"Invalid session id: {session_id!r}")
        return target


def _sanitize_id(session_id: str) -> str:
    import re
    if not session_id or not re.fullmatch(r"[a-zA-Z0-9_\-]+", session_id):
        raise ValueError(f"Invalid session id: {session_id!r}")
    return session_id


def _normalize(data: dict) -> dict:
    return {
        "goal": str(data.get("goal", "")),
        "constraints": list(data.get("constraints", [])),
        "progress": list(data.get("progress", [])),
        "model_history": list(data.get("model_history", [])),
        "current_subgoal": str(data.get("current_subgoal", "")),
        "fatigue_score": float(data.get("fatigue_score", 0.0)),
    }
