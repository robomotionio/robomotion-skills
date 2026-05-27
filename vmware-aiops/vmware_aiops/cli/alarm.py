"""Alarm management commands: list, acknowledge, reset."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from vmware_aiops.cli._common import (
    ConfigOption,
    DryRunOption,
    TargetOption,
    _audit,
    _dry_run_print,
    _get_connection,
    _resolve_target,
    console,
)

alarm_app = typer.Typer(help="vCenter alarm management: list, acknowledge, reset.")


@alarm_app.command("list")
def alarm_list(
    target: TargetOption = None,
    config: ConfigOption = None,
) -> None:
    """List all active/triggered alarms across the vCenter inventory."""
    from vmware_aiops.ops.alarm_mgmt import list_alarms

    si, _ = _get_connection(target, config)
    alarms = list_alarms(si)
    if not alarms:
        console.print("[green]No active alarms.[/]")
        return
    table = Table(title="Active vCenter Alarms")
    table.add_column("Severity", style="bold")
    table.add_column("Entity")
    table.add_column("Type")
    table.add_column("Alarm Name")
    table.add_column("Acknowledged")
    table.add_column("Time")
    for a in alarms:
        sev = a["severity"]
        sev_style = {"critical": "red", "warning": "yellow", "info": "cyan"}.get(sev, "white")
        ack = "[green]✓[/]" if a.get("acknowledged") else "[dim]-[/]"
        table.add_row(
            f"[{sev_style}]{sev.upper()}[/]",
            a["entity_name"],
            a["entity_type"],
            a["alarm_name"],
            ack,
            a["time"],
        )
    console.print(table)


@alarm_app.command("acknowledge")
def alarm_acknowledge(
    entity_name: Annotated[str, typer.Argument(help="Entity name (VM/host/cluster)")],
    alarm_name: Annotated[str, typer.Argument(help="Alarm definition name")],
    target: TargetOption = None,
    config: ConfigOption = None,
    dry_run: DryRunOption = False,
) -> None:
    """Acknowledge a triggered vCenter alarm (marks as seen, does not clear it)."""
    from vmware_aiops.ops.alarm_mgmt import acknowledge_alarm

    if dry_run:
        _dry_run_print(
            target=_resolve_target(target),
            vm_name=entity_name,
            operation="acknowledge_alarm",
            api_call="alarmManager.AcknowledgeAlarm(alarm, entity)",
            parameters={"alarm_name": alarm_name},
            resource_label="Entity",
        )
        return
    si, _ = _get_connection(target, config)
    result = acknowledge_alarm(si, entity_name, alarm_name, _audit, _resolve_target(target))
    console.print(f"[green]✓ Acknowledged alarm '{alarm_name}' on '{entity_name}'[/]")
    _audit.log(
        target=_resolve_target(target),
        operation="acknowledge_alarm",
        resource=f"alarm/{entity_name}/{alarm_name}",
        result=str(result),
    )


@alarm_app.command("reset")
def alarm_reset(
    entity_name: Annotated[str, typer.Argument(help="Entity name (VM/host/cluster)")],
    alarm_name: Annotated[str, typer.Argument(help="Alarm definition name")],
    target: TargetOption = None,
    config: ConfigOption = None,
    dry_run: DryRunOption = False,
) -> None:
    """Reset a triggered alarm to cleared state (gray). Removes it from active list."""
    from vmware_aiops.ops.alarm_mgmt import reset_alarm

    if dry_run:
        _dry_run_print(
            target=_resolve_target(target),
            vm_name=entity_name,
            operation="reset_alarm",
            api_call="alarmManager.SetAlarmStatus(alarm, entity, status='gray')",
            parameters={"alarm_name": alarm_name},
            resource_label="Entity",
        )
        return
    si, _ = _get_connection(target, config)
    result = reset_alarm(si, entity_name, alarm_name, _audit, _resolve_target(target))
    console.print(f"[green]✓ Reset alarm '{alarm_name}' on '{entity_name}' → cleared[/]")
    _audit.log(
        target=_resolve_target(target),
        operation="reset_alarm",
        resource=f"alarm/{entity_name}/{alarm_name}",
        result=str(result),
    )
