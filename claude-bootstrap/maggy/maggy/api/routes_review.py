"""Reviewer performance API routes."""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request

from maggy.api.auth import check_auth

router = APIRouter(prefix="/api/reviewers", tags=["reviewers"])


def _require_scores(request: Request):
    scores = getattr(request.app.state, "reviewer_scores", None)
    if scores is None:
        raise HTTPException(
            status_code=503,
            detail="Reviewer scores not available.",
        )
    return scores


@router.get("/heatmap")
async def reviewer_heatmap(
    request: Request,
    x_api_key: str | None = Header(None),
) -> list[dict]:
    """Reviewer performance heatmap."""
    check_auth(request, x_api_key)
    scores = _require_scores(request)
    return scores.heatmap()


@router.get("/compare")
async def reviewer_compare(
    request: Request,
    x_api_key: str | None = Header(None),
) -> dict:
    """Side-by-side reviewer comparison."""
    check_auth(request, x_api_key)
    scores = _require_scores(request)
    return scores.compare()
