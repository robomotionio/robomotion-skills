"""Routing rules summary display for CLI."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

console = Console()


def cmd_rules(client) -> None:
    """Show comprehensive routing rules summary."""
    try:
        data = client.routing_rules()
    except (Exception, SystemExit):
        data = {}
    if not data or data.get("mode") == "unconfigured":
        console.print("[dim]Routing not configured.[/dim]")
        return
    sections = [
        _fmt_overrides(data.get("task_type_overrides", {})),
        _fmt_phases(data.get("pipeline_phases", {})),
        _fmt_perf(data.get("model_performance", {})),
        _fmt_conventions(data.get("conventions", [])),
        _fmt_stakes(data.get("stakes", {})),
        _fmt_cascade(data.get("cascade", {})),
    ]
    body = "\n\n".join(s for s in sections if s)
    mode = data.get("mode", "dynamic")
    console.print(Panel(body, title=f"Rules ({mode})", border_style="cyan"))


def _fmt_overrides(overrides: dict) -> str:
    """Format task-type override rules."""
    if not overrides:
        return ""
    lines = ["[bold]Task Overrides[/bold]"]
    for tt, info in overrides.items():
        m = info.get("model", "?")
        r = info.get("reason", "")
        c = info.get("confidence", 1.0)
        lines.append(f"  {tt:<14} -> {m}  [dim]({r}, {c:.0%})[/dim]")
    return "\n".join(lines)


def _fmt_phases(phases: dict) -> str:
    """Format pipeline phase overrides."""
    if not phases:
        return ""
    lines = ["[bold]Pipeline Phases[/bold]"]
    for phase, info in phases.items():
        m = info.get("model", "?")
        r = info.get("reason", "")
        c = info.get("confidence", 1.0)
        lines.append(f"  {phase:<14} -> {m}  [dim]({r}, {c:.0%})[/dim]")
    return "\n".join(lines)


def _fmt_perf(perf: dict) -> str:
    """Format model performance with strengths + weaknesses."""
    if not perf:
        return ""
    lines = ["[bold]Model Performance[/bold]"]
    for model, info in perf.items():
        s = ", ".join(info.get("strengths", []))
        w = ", ".join(info.get("weaknesses", []))
        rate = info.get("success_rate", 0)
        n = info.get("tasks_completed", 0)
        unit = "task" if n == 1 else "tasks"
        parts = [f"  {model:<10}"]
        if s:
            parts.append(f"[green]+{s}[/green]")
        if w:
            parts.append(f"[red]-{w}[/red]")
        parts.append(f"[dim]{rate:.0%} ({n} {unit})[/dim]")
        lines.append("  ".join(parts))
    return "\n".join(lines)


def _fmt_conventions(conventions: list) -> str:
    """Format team conventions."""
    if not conventions:
        return ""
    lines = [f"[bold]Conventions ({len(conventions)})[/bold]"]
    for c in conventions:
        src = c.get("source", "")
        text = c.get("text", "")
        if len(text) > 60:
            text = text[:57] + "..."
        lines.append(f"  [dim]{src}:[/dim] {text}")
    return "\n".join(lines)


def _fmt_stakes(stakes: dict) -> str:
    """Format stakes classification patterns."""
    if not stakes:
        return ""
    lines = ["[bold]Stakes[/bold]"]
    for level in ("high", "medium", "low"):
        data = stakes.get(level, {})
        fps = data.get("file_patterns", [])
        tts = data.get("task_types", [])
        kws = data.get("keywords", [])
        if not (fps or tts or kws):
            continue
        tag = f"[red]{level}[/red]" if level == "high" else level
        lines.append(f"  {tag}:")
        if fps:
            lines.append(f"    files: {', '.join(fps)}")
        if tts:
            lines.append(f"    tasks: {', '.join(tts)}")
        if kws:
            lines.append(f"    keys:  {', '.join(kws)}")
    return "\n".join(lines)


def _fmt_cascade(cascade: dict) -> str:
    """Format cascade execution policy."""
    if not cascade:
        return ""
    on = "on" if cascade.get("enabled") else "off"
    bl = cascade.get("min_blast", 0)
    st = cascade.get("min_stakes", "?")
    mx = cascade.get("max_attempts", 0)
    return (
        f"[bold]Cascade[/bold]  {on}, "
        f"blast >= {bl}, stakes >= {st}, max {mx}"
    )
