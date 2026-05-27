"""Autonomous testing API — discover, generate, execute, evaluate, fix."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Query
from pydantic import BaseModel

from maggy.services.autonomous_tester import (
    AutonomousReport,
    TestGap,
    discover_gaps,
    execute_tests,
    run_autonomous,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/testing", tags=["testing"])


class GapResponse(BaseModel):
    gaps: list[dict]
    total: int


class ReportResponse(BaseModel):
    project: str
    tests_run: int
    passed: int
    failed: int
    auto_fixed: int
    needs_manual: int
    coverage: float
    gaps_found: int
    tests_generated: int
    next_actions: list[str]


@router.get("/gaps")
async def get_gaps(project_dir: str = Query(".")):
    """Discover test coverage gaps for a project."""
    gaps = discover_gaps(project_dir)
    return GapResponse(
        gaps=[{"file": g.file, "symbol": g.symbol, "kind": g.kind,
               "existing_tests": g.existing_tests} for g in gaps],
        total=len(gaps),
    )


@router.post("/run")
async def run_tests(project_dir: str = Query(".")):
    """Execute tests and return results."""
    results, coverage = execute_tests(project_dir)
    return {
        "results": [{"name": r.name, "passed": r.passed,
                      "error": r.error[:200]} for r in results],
        "coverage": coverage,
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
    }


@router.post("/autonomous")
async def autonomous_test(project_dir: str = Query(".")):
    """Full autonomous cycle: discover → generate → execute → evaluate → fix."""
    report = run_autonomous(project_dir)
    return report.__dict__
