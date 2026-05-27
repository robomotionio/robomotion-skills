---
description: "Per-action readiness diagnostic. Shows which campaign-audit and launch-campaign actions are live (manifest-ready) vs blocked (stub-unconfigured) in the current environment, with one-step setup hints for the blocked ones."
argument-hint: "[--brand <slug>] [--action <id>] [--channel <name>] [--json] [--summary]"
allowed-tools: Bash Read
---

# /digital-marketing-pro:doctor — Per-Action Readiness Check

Resolves every action in the campaign-audit and launch-campaign skill surfaces against the currently configured connectors and reports which mode each one is in:

| Mode | What it means |
|------|---------------|
| `real`              | Action runs end-to-end with no external API. Always available. |
| `manifest_ready`    | A matching connector is configured; the action returns the exact HTTP request manifest for the orchestrator (Claude via MCP) to execute. |
| `stub_unconfigured` | No matching connector is configured; the action returns a structured stub plus a copy-paste setup hint. |

## Quick examples

```
/digital-marketing-pro:doctor                              # full readiness map for default brand
/digital-marketing-pro:doctor --brand acme                 # for a named brand
/digital-marketing-pro:doctor --action inventory --channel google_ads
/digital-marketing-pro:doctor --summary                    # one-line counts
/digital-marketing-pro:doctor --json                       # machine-readable
```

## What it does NOT do

- It does not execute write/launch actions. For that, run the action through the orchestrator (`/digital-marketing-pro:launch-campaign`) which respects approval gates.
- It does not make any network call. It probes `.mcp.json` membership and env-var presence only — credentials are never read or echoed.

## Output sections

1. **Summary line** — count of actions in each of the three modes
2. **Per-action table** — action name, mode, operation type, configured connector or list of candidate connectors
3. **Unlock guide** — for any stub-unconfigured action, the exact next step

## See also

- [scripts/action-doctor.py](../scripts/action-doctor.py) — the underlying script
- [scripts/connector_resolver.py](../scripts/connector_resolver.py) — the resolver and ACTION_SPECS table
- [scripts/connector-status.py](../scripts/connector-status.py) — the broader connector dashboard (categories, setup guides)
- [/digital-marketing-pro:check](check.md) — pre-publish quality gate
- [/digital-marketing-pro:status](status.md) — brand snapshot

## Run

```bash
python scripts/action-doctor.py "$@"
```
