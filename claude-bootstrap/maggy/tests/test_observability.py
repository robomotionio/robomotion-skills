"""Tests for observability signal collection."""

from __future__ import annotations

from maggy.observability import ObservabilityCollector


def test_records_and_reads_recent_signals(tmp_path) -> None:
    collector = ObservabilityCollector(tmp_path / "signals.db")
    collector.record_signal("maggy", "fatigue", 0.4)
    collector.record_signal("maggy", "budget", 0.9)

    rows = collector.recent_signals("maggy")

    assert len(rows) == 2
    assert rows[0]["signal_type"] == "budget"
    assert rows[1]["signal_type"] == "fatigue"


def test_limits_recent_signals(tmp_path) -> None:
    collector = ObservabilityCollector(tmp_path / "signals.db")
    collector.record_signal("maggy", "fatigue", 0.2)
    collector.record_signal("maggy", "fatigue", 0.5)

    rows = collector.recent_signals("maggy", limit=1)

    assert len(rows) == 1
    assert rows[0]["value"] == 0.5
