"""Tests for CLI session management commands."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from maggy.cli import app

runner = CliRunner()


@patch("maggy.cli._client")
def test_spawn_creates_session(mock_client):
    """maggy spawn posts to execute endpoint."""
    mock_client.ensure_server.return_value = True
    mock_client.spawn.return_value = {
        "session_id": "abc123",
    }
    result = runner.invoke(
        app, ["spawn", "add unit tests"],
    )
    assert result.exit_code == 0
    assert "abc123" in result.output
    mock_client.spawn.assert_called_once()


@patch("maggy.cli._client")
def test_ps_lists_sessions(mock_client):
    """maggy ps shows all sessions."""
    mock_client.ensure_server.return_value = True
    mock_client.all_sessions.return_value = [
        {
            "id": "abc",
            "project": "edubites-core",
            "model": "claude",
            "status": "running",
            "type": "chat",
        },
    ]
    result = runner.invoke(app, ["ps"])
    assert result.exit_code == 0
    assert "edubites-core" in result.output


@patch("maggy.cli._client")
def test_kill_stops_session(mock_client):
    """maggy kill sends delete to session."""
    mock_client.ensure_server.return_value = True
    mock_client.kill_session.return_value = {"ok": True}
    result = runner.invoke(app, ["kill", "abc123"])
    assert result.exit_code == 0
    mock_client.kill_session.assert_called_once_with("abc123")
