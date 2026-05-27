"""Account switching guidance — detect profiles, suggest re-auth."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

console = Console()

_PROVIDERS = {
    ".claude": ("anthropic", "claude auth login"),
    ".codex": ("openai", "codex auth login"),
}


@dataclass
class AccountProfile:
    """Represents a CLI auth profile."""

    name: str
    provider: str
    auth_command: str
    is_active: bool = False


def detect_accounts(home: Path | None = None) -> list[AccountProfile]:
    """Discover CLI auth profiles from home dir."""
    root = home or Path.home()
    accounts: list[AccountProfile] = []
    for dirname, (provider, cmd) in _PROVIDERS.items():
        path = root / dirname
        if path.exists():
            accounts.append(AccountProfile(
                name=dirname.lstrip("."),
                provider=provider,
                auth_command=cmd,
            ))
    return accounts


def suggest_switch(provider: str) -> str:
    """Return CLI instructions to switch accounts."""
    if provider == "anthropic":
        return (
            "Claude quota hit. Switch account:\n"
            "  claude auth login\n"
            "Then restart your session."
        )
    if provider == "openai":
        return (
            "OpenAI/Codex quota hit. Switch account:\n"
            "  codex auth login\n"
            "Then restart your session."
        )
    return f"Quota hit for {provider}. Re-authenticate."


def render_switch_guide(provider: str) -> None:
    """Print Rich-formatted switch instructions."""
    guide = suggest_switch(provider)
    console.print(f"[yellow]{guide}[/yellow]")
