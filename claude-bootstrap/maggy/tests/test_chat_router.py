"""Tests for blast-score estimation and task-type detection."""

from __future__ import annotations

from maggy.services.chat_router import (
    DEFAULT_BLAST,
    estimate_blast,
    estimate_type,
)


def test_blast_hi_scores_low():
    """Trivial greeting should score 1, not 5."""
    assert estimate_blast("hi") == 1


def test_blast_exit_scores_low():
    """Exit-like messages should score 1."""
    assert estimate_blast("exit") == 1


def test_blast_empty_returns_default():
    """Empty string uses DEFAULT_BLAST."""
    assert estimate_blast("") == DEFAULT_BLAST


def test_blast_security_audit_scores_high():
    """Multiple high-tier keywords → blast >= 7."""
    score = estimate_blast("security audit migration")
    assert score >= 7


def test_blast_fix_typo_scores_low():
    """Low-tier keywords → blast <= 3."""
    score = estimate_blast("fix typo in readme")
    assert score <= 3


def test_type_security_detected():
    """Security keywords map to security type."""
    assert estimate_type("fix auth vulnerability") == "security"


def test_type_general_default():
    """No keyword matches → general."""
    assert estimate_type("hello world") == "general"


def test_type_search_detected():
    """Search queries map to search type."""
    assert estimate_type("find the utils module") == "search"


def test_type_search_grep():
    """grep-like queries map to search type."""
    assert estimate_type("grep for config files") == "search"


def test_blast_search_scores_low():
    """Search queries should score low blast (cheap model)."""
    score = estimate_blast("find the utils module")
    assert score <= 3


# ── Model forcing ────────────────────────────────────────────────────


def test_parse_force_claude():
    """'use claude' extracts model and cleans message."""
    from maggy.services.chat_router import parse_model_force
    msg, model = parse_model_force("use claude and review the code")
    assert model == "claude"
    assert "use claude" not in msg
    assert "review the code" in msg


def test_parse_force_codex():
    """'use codex' extracts codex as forced model."""
    from maggy.services.chat_router import parse_model_force
    _, model = parse_model_force("use codex to fix this bug")
    assert model == "codex"


def test_parse_force_none():
    """No 'use X' directive returns None."""
    from maggy.services.chat_router import parse_model_force
    msg, model = parse_model_force("fix the login bug")
    assert model is None
    assert msg == "fix the login bug"


def test_parse_force_case_insensitive():
    """'Use Claude' works regardless of casing."""
    from maggy.services.chat_router import parse_model_force
    _, model = parse_model_force("Use Claude to check this")
    assert model == "claude"


# ── Review type detection ────────────────────────────────────────────


def test_type_review_detected():
    """Review keywords map to review type."""
    assert estimate_type("review the authentication code") == "review"


def test_type_code_review_detected():
    """'code review' maps to review type."""
    assert estimate_type("do a code review of the PR") == "review"
