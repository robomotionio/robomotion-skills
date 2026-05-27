"""Tests for account switching guidance."""

from __future__ import annotations

from maggy.services.account_guide import (
    AccountProfile,
    detect_accounts,
    suggest_switch,
)


def test_account_profile_dataclass():
    """AccountProfile stores provider and auth command."""
    p = AccountProfile(
        name="claude-work", provider="anthropic",
        auth_command="claude auth login",
    )
    assert p.provider == "anthropic"
    assert "login" in p.auth_command


def test_detect_accounts_finds_claude(tmp_path):
    """Detects Claude accounts from ~/.claude directory."""
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "credentials.json").write_text("{}")
    accounts = detect_accounts(home=tmp_path)
    providers = [a.provider for a in accounts]
    assert "anthropic" in providers


def test_detect_accounts_finds_codex(tmp_path):
    """Detects Codex accounts from ~/.codex directory."""
    (tmp_path / ".codex").mkdir()
    accounts = detect_accounts(home=tmp_path)
    providers = [a.provider for a in accounts]
    assert "openai" in providers


def test_suggest_switch_anthropic():
    """Suggests claude auth login for anthropic quota hit."""
    guide = suggest_switch("anthropic")
    assert "claude" in guide.lower()
    assert "login" in guide.lower() or "auth" in guide.lower()


def test_suggest_switch_openai():
    """Suggests codex auth for openai quota hit."""
    guide = suggest_switch("openai")
    assert "codex" in guide.lower() or "openai" in guide.lower()
