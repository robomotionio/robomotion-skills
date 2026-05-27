"""Tests for CheckpointManager persistence."""

from __future__ import annotations

from maggy.checkpoint import CheckpointManager


def _checkpoint() -> dict:
    return {
        "goal": "Ship Phase 2",
        "constraints": ["Keep tests green"],
        "progress": ["Planner added"],
        "model_history": ["claude"],
        "current_subgoal": "Add checkpoints",
        "fatigue_score": 0.2,
    }


class TestCheckpointManager:
    def test_write_and_read(self, tmp_path) -> None:
        mgr = CheckpointManager(tmp_path)
        mgr.write("session-1", _checkpoint())

        assert mgr.read("session-1") == _checkpoint()

    def test_read_missing_returns_none(self, tmp_path) -> None:
        mgr = CheckpointManager(tmp_path)
        assert mgr.read("missing") is None

    def test_delete_returns_true_when_removed(self, tmp_path) -> None:
        mgr = CheckpointManager(tmp_path)
        mgr.write("session-1", _checkpoint())

        assert mgr.delete("session-1") is True
        assert mgr.read("session-1") is None

    def test_list_checkpoints_returns_session_ids(self, tmp_path) -> None:
        mgr = CheckpointManager(tmp_path)
        mgr.write("b", _checkpoint())
        mgr.write("a", _checkpoint())

        assert mgr.list_checkpoints() == ["a", "b"]

    def test_path_traversal_rejected(self, tmp_path) -> None:
        import pytest
        mgr = CheckpointManager(tmp_path)
        with pytest.raises(ValueError, match="Invalid session id"):
            mgr.write("../../etc/passwd", _checkpoint())

    def test_read_corrupt_json_returns_none(self, tmp_path) -> None:
        mgr = CheckpointManager(tmp_path)
        mgr.write("sess-1", _checkpoint())
        path = tmp_path / "sess-1.json"
        path.write_text("{corrupt")
        assert mgr.read("sess-1") is None
