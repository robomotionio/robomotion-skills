"""Project registry backed by Maggy config."""

from __future__ import annotations

from maggy.config import MaggyConfig, ProjectConfig


class ProjectRegistry:
    """Manage configured projects in memory."""

    def __init__(self, cfg: MaggyConfig):
        self._projects = {project.name: project for project in cfg.projects}

    def list(self) -> list[ProjectConfig]:
        return list(self._projects.values())

    def get(self, name: str) -> ProjectConfig | None:
        return self._projects.get(name)

    def add(self, project: ProjectConfig) -> None:
        if project.name in self._projects:
            raise ValueError(f"Project {project.name!r} already exists")
        self._projects[project.name] = project

    def remove(self, name: str) -> bool:
        return self._projects.pop(name, None) is not None
