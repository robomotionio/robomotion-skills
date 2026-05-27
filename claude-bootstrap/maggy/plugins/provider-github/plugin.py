"""GitHub Issues provider plugin.

Wraps the core IssueTrackerProvider protocol. Auto-registers
FastAPI routes and heartbeat jobs for inbox polling.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/provider/github", tags=["github"])


class GitHubProvider:
    """GitHub Issues API wrapper implementing IssueTrackerProvider protocol."""

    def __init__(self, token: str = "", org: str = "", repos: str = ""):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.org = org or os.environ.get("GITHUB_ORG", "")
        self.repos = repos or os.environ.get("GITHUB_REPOS", "")
        self._client = None

    @property
    def name(self) -> str:
        return "github"

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(
                base_url="https://api.github.com",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                } if self.token else {"Accept": "application/vnd.github+json"},
                timeout=30,
            )
        return self._client

    async def get_tasks(self, project: str = "", limit: int = 50) -> list[dict]:
        """Fetch open issues from configured repos."""
        if not self.token:
            return []
        repos = [r.strip() for r in self.repos.split(",") if r.strip()]
        if not repos:
            return []

        client = await self._get_client()
        tasks = []
        for repo in repos:
            try:
                resp = await client.get(f"/repos/{repo}/issues", params={
                    "state": "open", "per_page": min(limit, 100),
                    "sort": "updated", "direction": "desc",
                })
                if resp.status_code == 200:
                    for issue in resp.json():
                        if "pull_request" not in issue:
                            tasks.append({
                                "id": f"github-{issue['number']}",
                                "title": issue.get("title", ""),
                                "status": "open",
                                "source": "github",
                                "provider": "github",
                                "repo": repo,
                                "url": issue.get("html_url", ""),
                                "labels": [l["name"] for l in issue.get("labels", [])],
                                "assignee": issue.get("assignee", {}).get("login", ""),
                                "updated_at": issue.get("updated_at", ""),
                            })
            except Exception as e:
                logger.debug("GitHub fetch failed for %s: %s", repo, e)
        return tasks

    async def create_task(self, repo: str, title: str, body: str = "",
                          labels: list[str] = None) -> Optional[str]:
        """Create a new issue."""
        if not self.token:
            return None
        client = await self._get_client()
        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        try:
            resp = await client.post(f"/repos/{repo}/issues", json=payload)
            if resp.status_code == 201:
                return resp.json().get("html_url", "")
        except Exception as e:
            logger.debug("GitHub create failed: %s", e)
        return None

    async def get_task(self, repo: str, issue_number: int) -> Optional[dict]:
        """Get a single issue."""
        if not self.token:
            return None
        client = await self._get_client()
        try:
            resp = await client.get(f"/repos/{repo}/issues/{issue_number}")
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "id": f"github-{data['number']}",
                    "title": data.get("title", ""),
                    "status": data.get("state", ""),
                    "body": data.get("body", ""),
                    "url": data.get("html_url", ""),
                    "labels": [l["name"] for l in data.get("labels", [])],
                }
        except Exception as e:
            logger.debug("GitHub get failed: %s", e)
        return None


# ── Plugin registration ──────────────────────────────────────────────────

_provider: Optional[GitHubProvider] = None


def register(bus, manifest):
    """Called by PluginManager on load."""
    global _provider
    config = getattr(manifest, 'config', manifest.get('config', {}))
    _provider = GitHubProvider()
    logger.info("provider-github: registered")


async def fetch_tasks(payload: dict):
    """Hook handler: fetch tasks from GitHub."""
    if not _provider:
        return
    tasks = await _provider.get_tasks()
    # Publish to event bus for downstream consumers
    logger.info("provider-github: fetched %d tasks", len(tasks))


async def poll_inbox():
    """Heartbeat job: periodically refresh GitHub tasks."""
    if not _provider:
        return
    tasks = await _provider.get_tasks()
    logger.debug("provider-github: heartbeat polled %d tasks", len(tasks))


# ── API routes ───────────────────────────────────────────────────────────

@router.get("/tasks")
async def list_tasks(request: Request, limit: int = 50):
    if not _provider:
        return {"tasks": [], "error": "provider not configured"}
    tasks = await _provider.get_tasks(limit=limit)
    return {"tasks": tasks, "total": len(tasks)}


@router.get("/status")
async def status(request: Request):
    return {
        "configured": bool(_provider and _provider.token),
        "org": _provider.org if _provider else "",
        "repos": _provider.repos.split(",") if _provider else [],
    }
