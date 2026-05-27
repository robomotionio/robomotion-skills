"""Unified Task Provider — abstracts over native, github, asana, monday trackers.

Per-project: each project picks its tracker. Native uses _project_specs/todos/.
Plugins implement the same protocol for external trackers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass
class Task:
    id: str
    title: str
    status: str = "pending"  # pending, in_progress, done
    source: str = "native"
    url: str = ""
    assignee: str = ""
    labels: list[str] = field(default_factory=list)
    updated_at: str = ""


class TaskProvider(Protocol):
    """Protocol that every tracker plugin implements."""

    async def list_tasks(self, project_path: str, config: dict) -> list[Task]: ...
    async def create_task(self, project_path: str, config: dict, title: str, body: str = "") -> Task: ...
    async def update_task(self, project_path: str, config: dict, task_id: str, status: str) -> Task: ...
    async def delete_task(self, project_path: str, config: dict, task_id: str) -> bool: ...


class NativeTaskProvider:
    """Reads/writes _project_specs/todos/active.md and backlog.md.

    Format:
      ## Active
      - [ ] Task title  <!-- id: specs-1 -->
      - [ ] Another task  <!-- id: specs-2 -->

      ## Backlog
      - [x] Done task  <!-- id: specs-3 -->
    """

    ID_PATTERN = "<!-- id: {} -->"

    async def list_tasks(self, project_path: str, config: dict = None) -> list[Task]:
        spec_dir = Path(project_path) / "_project_specs" / "todos"
        tasks: list[Task] = []

        for todo_file, default_status in [("active.md", "pending"), ("backlog.md", "done")]:
            path = spec_dir / todo_file
            if not path.exists():
                continue
            content = path.read_text()
            for line in content.split("\n"):
                stripped = line.strip()
                if not stripped.startswith("- ["):
                    continue

                # Extract status from checkbox
                is_done = "- [x]" in stripped[:5]
                status = "done" if is_done else default_status

                # Extract title (everything after checkbox, before id comment)
                title = stripped
                title = title.replace("- [ ] ", "").replace("- [x] ", "").replace("- [X] ", "")
                task_id = f"specs-{len(tasks)}"

                # Extract inline ID if present
                if "<!-- id:" in title:
                    parts = title.split("<!-- id:")
                    title = parts[0].strip()
                    task_id = parts[1].replace("-->", "").strip()

                if title:
                    tasks.append(Task(
                        id=task_id, title=title, status=status,
                        source="_project_specs",
                        url=str(path),
                    ))

        return tasks

    async def create_task(self, project_path: str, config: dict,
                          title: str, body: str = "") -> Task:
        spec_dir = Path(project_path) / "_project_specs" / "todos"
        spec_dir.mkdir(parents=True, exist_ok=True)

        active_path = spec_dir / "active.md"
        task_id = f"specs-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        content = active_path.read_text() if active_path.exists() else "## Active\n\n"
        if "## Active" not in content:
            content = "## Active\n\n" + content

        # Insert task after ## Active header
        lines = content.split("\n")
        inserted = False
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if line.startswith("## Active") and not inserted:
                new_lines.append(f"- [ ] {title} <!-- id: {task_id} -->")
                if body:
                    new_lines.append(f"  {body}")
                inserted = True

        if not inserted:
            new_lines.append(f"- [ ] {title} <!-- id: {task_id} -->")

        active_path.write_text("\n".join(new_lines))

        return Task(
            id=task_id, title=title, status="pending",
            source="_project_specs", url=str(active_path),
        )

    async def update_task(self, project_path: str, config: dict,
                          task_id: str, status: str) -> Task:
        """Update status. If status=done, move from active.md to backlog.md."""
        spec_dir = Path(project_path) / "_project_specs" / "todos"
        active_path = spec_dir / "active.md"
        backlog_path = spec_dir / "backlog.md"

        task_line = ""
        found_in = ""

        # Find task in active.md or backlog.md
        for fpath in [active_path, backlog_path]:
            if not fpath.exists():
                continue
            for line in fpath.read_text().split("\n"):
                if task_id in line:
                    task_line = line.strip()
                    found_in = str(fpath)
                    break
            if found_in:
                break

        if not task_line:
            raise ValueError(f"Task {task_id} not found")

        title = task_line.replace("- [ ] ", "").replace("- [x] ", "").replace("- [X] ", "")
        title = title.split("<!-- id:")[0].strip()

        if status == "done":
            # Move to backlog.md
            _remove_line(active_path, task_id)
            _ensure_header(backlog_path, "## Backlog")
            with backlog_path.open("a") as f:
                f.write(f"\n- [x] {title} <!-- id: {task_id} -->\n")
            return Task(id=task_id, title=title, status="done",
                       source="_project_specs", url=str(backlog_path))
        else:
            # Update status in place
            new_marker = "- [ ]" if status == "pending" else "- [ ]"
            _replace_line(found_in, task_id, f"{new_marker} {title} <!-- id: {task_id} -->")
            return Task(id=task_id, title=title, status=status,
                       source="_project_specs", url=found_in)

    async def delete_task(self, project_path: str, config: dict,
                          task_id: str) -> bool:
        spec_dir = Path(project_path) / "_project_specs" / "todos"
        for fpath in [spec_dir / "active.md", spec_dir / "backlog.md"]:
            if _remove_line(fpath, task_id):
                return True
        return False


def _remove_line(path: Path, task_id: str) -> bool:
    """Remove a line containing task_id from file. Returns True if removed."""
    if not path.exists():
        return False
    lines = path.read_text().split("\n")
    new_lines = [l for l in lines if task_id not in l]
    if len(new_lines) != len(lines):
        path.write_text("\n".join(new_lines))
        return True
    return False


def _replace_line(fpath: str, task_id: str, new_line: str):
    """Replace line containing task_id with new_line."""
    path = Path(fpath)
    if not path.exists():
        return
    lines = path.read_text().split("\n")
    for i, line in enumerate(lines):
        if task_id in line:
            lines[i] = new_line
            break
    path.write_text("\n".join(lines))


def _ensure_header(path: Path, header: str):
    """Ensure file starts with header."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(header + "\n\n")
    elif header not in path.read_text():
        path.write_text(header + "\n\n" + path.read_text())


def get_provider(tracker_type: str) -> TaskProvider:
    """Get the task provider for a tracker type."""
    if tracker_type == "native" or not tracker_type:
        return NativeTaskProvider()

    # Try to load from installed plugins
    try:
        from maggy.plugins.manager import get_plugin_manager
        pm = get_plugin_manager()
        for pid, module in pm._modules.items():
            if hasattr(module, "get_task_provider"):
                provider = module.get_task_provider(tracker_type)
                if provider:
                    return provider
    except Exception:
        pass

    return NativeTaskProvider()
