"""Asana provider plugin — wraps core IssueTrackerProvider protocol."""

from __future__ import annotations

import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/provider/asana", tags=["asana"])

_provider: Optional["AsanaProvider"] = None


class AsanaProvider:
    name = "asana"

    def __init__(self):
        self.token = os.environ.get("ASANA_TOKEN", "")
        self.workspace = os.environ.get("ASANA_WORKSPACE", "")

    @property
    def configured(self) -> bool:
        return bool(self.token and self.workspace)

    async def get_tasks(self, limit: int = 50) -> list[dict]:
        if not self.configured:
            return []
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"https://app.asana.com/api/1.0/workspaces/{self.workspace}/tasks/search",
                    headers={"Authorization": f"Bearer {self.token}"},
                    params={"limit": min(limit, 100), "opt_fields": "name,assignee, due_on,permalink_url,projects,completed"},
                )
                if resp.status_code != 200:
                    return []
                return [
                    {"id": f"asana-{t['gid']}", "title": t.get("name", ""),
                     "status": "open", "source": "asana", "provider": "asana",
                     "url": t.get("permalink_url", ""),
                     "assignee": t.get("assignee", {}).get("name", ""),
                     "updated_at": t.get("due_on", "")}
                    for t in resp.json().get("data", []) if not t.get("completed")
                ]
        except Exception as e:
            logger.debug("Asana fetch failed: %s", e)
        return []


def register(bus, manifest):
    global _provider
    _provider = AsanaProvider()
    logger.info("provider-asana: registered")


async def poll_inbox():
    if _provider:
        await _provider.get_tasks()


@router.get("/tasks")
async def list_tasks(request: Request, limit: int = 50):
    if not _provider:
        return {"tasks": [], "error": "not configured"}
    return {"tasks": await _provider.get_tasks(limit), "total": 0}


@router.get("/status")
async def status(request: Request):
    return {"configured": bool(_provider and _provider.configured), "workspace": _provider.workspace if _provider else ""}
