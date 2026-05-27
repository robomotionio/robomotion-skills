"""Tests for calibration tracking."""

from __future__ import annotations

import pytest

from maggy.calibration import CalibrationTracker


def test_records_accuracy_and_error(tmp_path) -> None:
    tracker = CalibrationTracker(tmp_path / "calibration.db")
    tracker.record("claude", "planning", 0.8, 0.7)
    tracker.record("claude", "planning", 0.4, 0.5)

    assert tracker.accuracy("claude") == pytest.approx(0.9)
    assert tracker.calibration_error("claude") == pytest.approx(0.1)


def test_unknown_model_returns_zero(tmp_path) -> None:
    tracker = CalibrationTracker(tmp_path / "calibration.db")
    assert tracker.accuracy("codex") == 0.0
    assert tracker.calibration_error("codex") == 0.0


def test_accuracy_clamps_at_zero_for_large_errors(tmp_path) -> None:
    tracker = CalibrationTracker(tmp_path / "calibration.db")
    tracker.record("claude", "planning", 0.0, 2.0)
    assert tracker.accuracy("claude") >= 0.0
