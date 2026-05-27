"""Competitor intelligence API — per-project competitor tracking."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from maggy.services.competitor_intel import CompetitorIntel

router = APIRouter(prefix="/api/competitor-intel", tags=["competitors"])


def _get_intel(request: Request, project: str = "maggy") -> CompetitorIntel:
    """Get or create CompetitorIntel for a project."""
    key = f"_competitor_{project}"
    if not hasattr(request.app.state, key):
        setattr(request.app.state, key, CompetitorIntel(project))
    return getattr(request.app.state, key)


@router.get("/{project}")
async def list_competitors(request: Request, project: str):
    """List all tracked competitors for a project."""
    ci = _get_intel(request, project)
    return {
        "project": project,
        "competitors": ci.get_competitors(),
        "total": len(ci.get_competitors()),
    }


@router.get("/{project}/moves")
async def list_moves(request: Request, project: str, limit: int = Query(20, le=100)):
    """Get recent competitor moves for a project."""
    ci = _get_intel(request, project)
    return {"project": project, "moves": ci.get_moves(limit)}


@router.get("/{project}/briefing")
async def get_briefing(request: Request, project: str):
    """Get latest competitor briefing for a project."""
    ci = _get_intel(request, project)
    return ci.get_briefing()


@router.post("/{project}/scan")
async def scan_competitors(request: Request, project: str):
    """Run a competitor scan (X + Reddit + Grok)."""
    ci = _get_intel(request, project)
    moves = ci.scan_moves()
    return {"project": project, "new_moves": len(moves), "moves": [m.__dict__ for m in moves]}


@router.post("/{project}/discover")
async def discover_competitors(request: Request, project: str):
    """Auto-discover new competitors via Grok."""
    ci = _get_intel(request, project)
    discovered = ci.discover_competitors()
    return {"project": project, "discovered": len(discovered)}


@router.post("/{project}/add")
async def add_competitor(request: Request, project: str,
                         name: str, domain: str,
                         x_handle: str = "", website: str = ""):
    """Manually add a competitor to track."""
    ci = _get_intel(request, project)
    c = ci.add_competitor(name, domain, x_handle, website)
    return {"added": c.name, "domain": c.domain}
