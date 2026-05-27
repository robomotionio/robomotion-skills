"""Tests for reviewer evaluation service."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from maggy.services.reviewer_eval import (
    categorize_findings,
    compare_reviewers,
    evaluate_review,
)


# -- categorize_findings --


def test_categorize_security_keywords():
    """Security keywords detected."""
    text = "Found XSS vulnerability in auth token handling"
    cats = categorize_findings(text)
    assert cats["security"] > 0


def test_categorize_performance_keywords():
    """Performance keywords detected."""
    text = "Memory leak in cache, slow query needs index"
    cats = categorize_findings(text)
    assert cats["performance"] > 0


def test_categorize_multiple_categories():
    """Multiple categories detected in one review."""
    text = (
        "Bug in null check causes error. "
        "Naming convention violated. "
        "Auth vulnerability found."
    )
    cats = categorize_findings(text)
    assert cats["logic"] > 0
    assert cats["style"] > 0
    assert cats["security"] > 0


def test_categorize_empty_text():
    """Empty text returns zero counts."""
    cats = categorize_findings("")
    assert all(v == 0 for v in cats.values())


def test_categorize_no_matches():
    """Text with no category keywords returns zeros."""
    cats = categorize_findings("Everything looks good")
    assert all(v == 0 for v in cats.values())


# -- evaluate_review --


def test_evaluate_records_scores(tmp_path):
    """evaluate_review records to ReviewerTable."""
    from maggy.review_scores import ReviewerTable
    scores = ReviewerTable(tmp_path / "test.db")
    text = "XSS vulnerability found in auth flow"
    evaluate_review("coderabbit", text, "review", scores)
    hm = scores.heatmap()
    assert len(hm) > 0
    assert any(r["reviewer"] == "coderabbit" for r in hm)


# -- compare_reviewers --


def test_compare_delegates_to_table(tmp_path):
    """compare_reviewers returns table.compare()."""
    from maggy.review_scores import ReviewerTable
    scores = ReviewerTable(tmp_path / "test.db")
    scores.record("coderabbit", "security", 0.9, "review")
    scores.record("codex", "security", 0.5, "review")
    result = compare_reviewers(scores)
    assert "security" in result
