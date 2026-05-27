"""API routes for monitor service — tracker polling."""

from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/monitor", tags=["monitor"])


@router.get("/status")
async def monitor_status(request: Request) -> dict:
    """Get active monitor status."""
    svc = getattr(request.app.state, "monitor", None)
    if not svc:
        return {"active": 0, "monitors": []}
    return svc.status()


@router.post("/start")
async def monitor_start(request: Request) -> dict:
    """Start monitoring current project's tracker."""
    svc = getattr(request.app.state, "monitor", None)
    if not svc:
        return {"ok": False, "error": "monitor not configured"}
    return {"ok": True, "active": len(svc.list_active())}


@router.post("/stop")
async def monitor_stop(request: Request) -> dict:
    """Stop all monitors."""
    svc = getattr(request.app.state, "monitor", None)
    if not svc:
        return {"ok": False}
    for cfg in svc.list_active():
        svc.remove(cfg.project_key)
    return {"ok": True}
