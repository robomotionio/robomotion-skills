"""Tests for cli_rules — routing rules summary display."""
from __future__ import annotations

from unittest.mock import MagicMock

from maggy.cli_rules import (
    _fmt_cascade,
    _fmt_conventions,
    _fmt_overrides,
    _fmt_perf,
    _fmt_phases,
    _fmt_stakes,
    cmd_rules,
)

_OVERRIDES = {
    "docs": {
        "model": "claude", "reason": "prose",
        "confidence": 0.9, "source": "benchmark",
    },
    "security": {
        "model": "claude", "reason": "deep reasoning",
        "confidence": 1.0, "source": "rule",
    },
}

_PHASES = {
    "spec": {
        "model": "claude", "reason": "docs",
        "confidence": 1.0, "source": "rule",
    },
    "tdd_green": {
        "model": "auto", "reason": "blast routing",
        "confidence": 1.0, "source": "rule",
    },
}

_PERF = {
    "claude": {
        "strengths": ["security", "tests"],
        "weaknesses": ["cost"],
        "success_rate": 1.0,
        "tasks_completed": 6,
    },
}

_CONVENTIONS = [
    {
        "text": "TDD: RED then GREEN then VALIDATE",
        "applies_to": ["all"],
        "source": "bootstrap",
    },
]

_STAKES = {
    "high": {
        "file_patterns": ["auth", "billing"],
        "task_types": ["security"],
        "keywords": ["production"],
    },
    "medium": {
        "file_patterns": ["api"],
        "task_types": ["feature"],
        "keywords": [],
    },
    "low": {
        "file_patterns": [],
        "task_types": ["docs"],
        "keywords": [],
    },
}

_CASCADE = {
    "enabled": True, "min_blast": 5,
    "min_stakes": "medium", "max_attempts": 3,
    "quality_threshold": 3,
}

_FULL_DATA = {
    "mode": "dynamic",
    "task_type_overrides": _OVERRIDES,
    "pipeline_phases": _PHASES,
    "model_performance": _PERF,
    "conventions": _CONVENTIONS,
    "stakes": _STAKES,
    "cascade": _CASCADE,
}


def test_fmt_overrides_shows_model():
    result = _fmt_overrides(_OVERRIDES)
    assert "claude" in result
    assert "docs" in result
    assert "prose" in result


def test_fmt_overrides_empty():
    assert _fmt_overrides({}) == ""


def test_fmt_phases_shows_phase():
    result = _fmt_phases(_PHASES)
    assert "spec" in result
    assert "tdd_green" in result
    assert "auto" in result


def test_fmt_perf_shows_weaknesses():
    result = _fmt_perf(_PERF)
    assert "security" in result
    assert "cost" in result
    assert "claude" in result


def test_fmt_conventions_shows_text():
    result = _fmt_conventions(_CONVENTIONS)
    assert "TDD" in result
    assert "bootstrap" in result


def test_fmt_stakes_shows_levels():
    result = _fmt_stakes(_STAKES)
    assert "high" in result.lower()
    assert "files: auth" in result
    assert "tasks: docs" in result
    assert "keys:" in result


def test_fmt_cascade_shows_policy():
    result = _fmt_cascade(_CASCADE)
    assert "5" in result
    assert "medium" in result
    assert "3" in result


def test_cmd_rules_mock_client():
    client = MagicMock()
    client.routing_rules.return_value = _FULL_DATA
    cmd_rules(client)
    client.routing_rules.assert_called_once()


def test_cmd_rules_unconfigured():
    client = MagicMock()
    client.routing_rules.return_value = {"mode": "unconfigured"}
    cmd_rules(client)  # should not raise


def test_cmd_rules_client_error():
    client = MagicMock()
    client.routing_rules.side_effect = ConnectionError("down")
    cmd_rules(client)  # should not raise
