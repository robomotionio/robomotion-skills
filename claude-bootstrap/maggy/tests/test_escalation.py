"""Tests for human escalation packets."""

from __future__ import annotations

from maggy.escalation.protocol import Escalator


class TestEscalator:
    def test_escalate_and_get(self, tmp_path):
        escalator = Escalator(tmp_path / "escalations.db")
        packet = escalator.escalate(
            "session-1",
            "blocked on merge conflict",
            {
                "agent_state": {"task": "coordination"},
                "suggested_actions": ["review lock owner"],
            },
        )
        loaded = escalator.get(packet.id)
        assert loaded is not None
        assert loaded.session_id == "session-1"
        assert loaded.agent_state == {"task": "coordination"}
        assert loaded.suggested_actions == ["review lock owner"]

    def test_list_pending_returns_unresolved(self, tmp_path):
        escalator = Escalator(tmp_path / "escalations.db")
        first = escalator.escalate("session-1", "needs input", {})
        escalator.escalate("session-2", "waiting on human", {})
        escalator.resolve(first.id, "continue with fallback")
        pending = escalator.list_pending()
        assert [packet.session_id for packet in pending] == ["session-2"]

    def test_resolve_marks_packet(self, tmp_path):
        escalator = Escalator(tmp_path / "escalations.db")
        packet = escalator.escalate("session-1", "needs approval", {})
        resolved = escalator.resolve(packet.id, "approved")
        assert resolved.resolved is True
        assert resolved.resolution == "approved"
