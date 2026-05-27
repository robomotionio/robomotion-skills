#!/usr/bin/env python3
"""
action-doctor.py
================
Per-action readiness diagnostic for Digital Marketing Pro.

For every action in the connector_resolver ACTION_SPECS table, report:
  - Which connector(s) would unlock it
  - Whether any of those connectors are currently configured
  - The resolved mode (real / manifest_ready / stub_unconfigured)
  - For unconfigured actions, the exact one-step setup hint

This is the canonical pre-flight check before running campaign-audit /
launch-campaign, and the answer to "which of the 14 stub actions are
actually live in my environment right now?"

Usage:
    python action-doctor.py --brand acme                     # full readiness map
    python action-doctor.py --brand acme --action inventory  # one action
    python action-doctor.py --brand acme --channel google_ads  # filter by channel
    python action-doctor.py --brand acme --json              # machine-readable
    python action-doctor.py --brand acme --summary           # one-line counts only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Cross-platform safety: force UTF-8 stdout on Windows cp1252 consoles.
# Without this, any non-ASCII character in the report crashes with
# UnicodeEncodeError. errors='replace' means worst case we emit a "?".
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from connector_resolver import (  # noqa: E402
    ACTION_SPECS,
    _load_mcp_json,
    find_connector,
    is_connector_configured,
    resolve_action,
)


def _per_action_readiness(brand, channel=None):
    """Resolve every action and bucket by mode."""
    active_servers = _load_mcp_json()
    rows = []
    for action_id, spec in sorted(ACTION_SPECS.items()):
        kwargs = {"channel": channel} if channel else {}
        if spec["operation"] != "local":
            candidates = spec["candidate_connectors"](kwargs) or []
            configured = []
            for c in candidates:
                info = find_connector(c)
                if info is None:
                    continue
                ok, _ = is_connector_configured(c, info, active_servers)
                if ok:
                    configured.append(c)
            mode = "manifest_ready" if configured else "stub_unconfigured"
        else:
            candidates = []
            configured = []
            mode = "real"
        rows.append({
            "action": action_id,
            "script": spec["script"],
            "operation": spec["operation"],
            "purpose": spec["purpose"],
            "candidate_connectors": candidates,
            "configured_connectors": configured,
            "mode": mode,
        })
    return rows


def _summary_counts(rows):
    counts = {"real": 0, "manifest_ready": 0, "stub_unconfigured": 0}
    for r in rows:
        counts[r["mode"]] = counts.get(r["mode"], 0) + 1
    return counts


def _format_text_report(brand, rows, counts):
    """Pretty terminal-friendly report."""
    lines = []
    total = len(rows)
    lines.append(f"DMP action readiness for brand '{brand}': "
                 f"{counts.get('real', 0)} real, "
                 f"{counts.get('manifest_ready', 0)} manifest-ready, "
                 f"{counts.get('stub_unconfigured', 0)} stub-unconfigured "
                 f"(total {total})")
    lines.append("")
    lines.append(f"{'ACTION':22s}  {'MODE':18s}  {'OP':6s}  {'CONNECTOR(S)':45s}")
    lines.append("-" * 95)
    for r in rows:
        if r["mode"] == "real":
            conn_display = "(local execution -- no connector needed)"
        elif r["mode"] == "manifest_ready":
            conn_display = f"[OK] {', '.join(r['configured_connectors'])}"
        else:
            conn_display = f"[--] needs one of: {', '.join(r['candidate_connectors'][:3])}"
            if len(r["candidate_connectors"]) > 3:
                conn_display += f" (+{len(r['candidate_connectors']) - 3} more)"
        lines.append(f"{r['action']:22s}  {r['mode']:18s}  {r['operation']:6s}  {conn_display}")
    lines.append("")
    unconfigured = [r for r in rows if r["mode"] == "stub_unconfigured"]
    if unconfigured:
        lines.append(f"To unlock the {len(unconfigured)} stub-unconfigured action(s):")
        lines.append("  python scripts/connector-status.py --action setup-guide --name <connector>")
        lines.append("  ... then add the printed snippet to .mcp.json under mcpServers.")
        lines.append("")
        lines.append("Or run any individual action -- it returns the same setup hint inline.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Per-action readiness diagnostic for Digital Marketing Pro."
    )
    parser.add_argument("--brand", default="default",
                        help="Brand slug (used for write-side actions; readiness is brand-agnostic)")
    parser.add_argument("--action",
                        help="Drill into a single action and print resolve_action's full response.")
    parser.add_argument("--channel",
                        help="Channel context for actions that need one (google_ads / meta_ads / "
                             "email / facebook / linkedin / etc.)")
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON.")
    parser.add_argument("--summary", action="store_true",
                        help="Print only the one-line summary counts.")
    args = parser.parse_args()

    # Single-action drill-in
    if args.action:
        kwargs = {"channel": args.channel} if args.channel else {}
        result = resolve_action(args.action, args.brand, **kwargs)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
        return

    rows = _per_action_readiness(args.brand, channel=args.channel)
    counts = _summary_counts(rows)

    if args.summary:
        print(f"{counts.get('real', 0)} real | "
              f"{counts.get('manifest_ready', 0)} manifest-ready | "
              f"{counts.get('stub_unconfigured', 0)} stub-unconfigured "
              f"(total {len(rows)})")
        return

    if args.json:
        print(json.dumps({
            "brand": args.brand,
            "channel_filter": args.channel,
            "summary": counts,
            "total_actions": len(rows),
            "actions": rows,
        }, indent=2))
    else:
        print(_format_text_report(args.brand, rows, counts))


if __name__ == "__main__":
    main()
