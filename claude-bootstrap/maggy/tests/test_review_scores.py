"""Tests for reviewer reward table."""
from __future__ import annotations

import pytest

from maggy.review_scores import ReviewerTable


@pytest.fixture
def table(tmp_path):
    """Create ReviewerTable with temp DB."""
    return ReviewerTable(tmp_path / "test_reviews.db")


# -- record + heatmap --


def test_record_and_heatmap(table):
    """Recording scores appears in heatmap."""
    table.record("coderabbit", "security", 0.9, "review")
    table.record("coderabbit", "security", 0.8, "review")
    hm = table.heatmap()
    assert len(hm) == 1
    assert hm[0]["reviewer"] == "coderabbit"
    assert hm[0]["category"] == "security"
    assert hm[0]["avg_score"] == pytest.approx(0.85, abs=0.01)


def test_heatmap_empty(table):
    """Empty table returns empty heatmap."""
    assert table.heatmap() == []


def test_multiple_reviewers(table):
    """Different reviewers tracked separately."""
    table.record("coderabbit", "security", 0.9, "review")
    table.record("codex", "security", 0.7, "review")
    hm = table.heatmap()
    assert len(hm) == 2
    reviewers = {r["reviewer"] for r in hm}
    assert reviewers == {"coderabbit", "codex"}


# -- best_reviewer --


def test_best_reviewer_insufficient_data(table):
    """Returns None with fewer than MIN_SAMPLES."""
    table.record("coderabbit", "security", 0.9, "review")
    assert table.best_reviewer("security") is None


def test_best_reviewer_enough_data(table):
    """Returns best after MIN_SAMPLES recordings."""
    for _ in range(3):
        table.record("coderabbit", "logic", 0.9, "review")
        table.record("codex", "logic", 0.5, "review")
    assert table.best_reviewer("logic") == "coderabbit"


# -- compare --


def test_compare_empty(table):
    """Empty table returns empty compare."""
    assert table.compare() == {}


def test_compare_multiple(table):
    """Compare returns per-category per-reviewer scores."""
    table.record("coderabbit", "security", 0.9, "review")
    table.record("codex", "security", 0.6, "review")
    table.record("coderabbit", "style", 0.3, "review")
    table.record("codex", "style", 0.8, "review")
    result = table.compare()
    assert "security" in result
    assert "style" in result
    assert result["security"]["coderabbit"] > result["security"]["codex"]
    assert result["style"]["codex"] > result["style"]["coderabbit"]
