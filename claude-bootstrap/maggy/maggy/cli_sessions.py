"""Session management for Maggy CLI — spawn, list, kill."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

console = Console()


def spawn_session(client, task: str, project: str) -> None:
    """Spawn a background execution session."""
    data = client.spawn(task, project)
    sid = data.get("session_id", "?")
    console.print(
        f"[green]Spawned[/green] session "
        f"[bold]{sid}[/bold] for {project}",
    )


def list_all(client) -> None:
    """Show all sessions (chat + executor)."""
    sessions = client.all_sessions()
    if not sessions:
        console.print("[dim]No active sessions.[/dim]")
        return
    t = Table(title="All Sessions")
    t.add_column("ID", width=12)
    t.add_column("Project")
    t.add_column("Model")
    t.add_column("Type")
    t.add_column("Status")
    for s in sessions:
        t.add_row(
            str(s.get("id", "?")),
            s.get("project", "?"),
            s.get("model", "?"),
            s.get("type", "?"),
            s.get("status", "?"),
        )
    console.print(t)


def kill_session(client, session_id: str) -> None:
    """Kill a session by ID."""
    client.kill_session(session_id)
    console.print(
        f"[yellow]Killed[/yellow] session [bold]{session_id}[/bold]",
    )
