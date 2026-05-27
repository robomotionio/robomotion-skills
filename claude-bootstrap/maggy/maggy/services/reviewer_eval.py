"""Reviewer evaluation — categorize findings, record, compare."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from maggy.review_scores import ReviewerTable

CATEGORIES: dict[str, frozenset[str]] = {
    "security": frozenset({
        "auth", "xss", "injection", "csrf",
        "vulnerability", "permission", "secret",
        "token", "encrypt", "sanitize",
    }),
    "performance": frozenset({
        "performance", "memory", "cache", "latency",
        "optimize", "leak", "slow", "batch", "index",
    }),
    "style": frozenset({
        "naming", "convention", "format", "lint",
        "readability", "import", "unused",
    }),
    "logic": frozenset({
        "bug", "error", "null", "undefined",
        "race", "boundary", "exception", "crash",
    }),
    "architecture": frozenset({
        "pattern", "coupling", "separation",
        "dependency", "abstraction", "interface",
        "module", "refactor",
    }),
}


def categorize_findings(text: str) -> dict[str, int]:
    """Count keyword hits per category in review text."""
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    return {
        cat: len(words & keywords)
        for cat, keywords in CATEGORIES.items()
    }


def evaluate_review(
    reviewer: str, text: str,
    task_type: str, scores: "ReviewerTable",
) -> None:
    """Categorize findings and record to ReviewerTable."""
    cats = categorize_findings(text)
    total = sum(cats.values())
    if total == 0:
        return
    for cat, count in cats.items():
        if count > 0:
            score = count / total
            scores.record(reviewer, cat, score, task_type)


def compare_reviewers(scores: "ReviewerTable") -> dict:
    """Return side-by-side reviewer comparison."""
    return scores.compare()
