---
description: "Unified status snapshot of the active brand: profile, engagements, recent insights, recent compliance violations, Python dependency mode."
argument-hint: "[--brand <slug>] [--json] [--quiet] [--section brand|engagements|insights|compliance|deps]"
allowed-tools: Read Bash Glob Grep
---

# /digital-marketing-pro:status — Unified Status Snapshot

Prints a complete status snapshot for the active Digital Marketing Pro brand. Wraps `scripts/dm-status.py` and surfaces health indicators that need attention.

In v3.0 and earlier, the SessionStart hook ran `setup.py` automatically at every Claude Code session start to print a 15-line brand summary banner across every project. v3.1 removed that hook because it fired globally regardless of context. v3.2 introduces this command as the explicit on-demand replacement, with a richer view than the old banner.

## Quick examples

```
/digital-marketing-pro:status                              # Full snapshot for active brand
/digital-marketing-pro:status --brand acme-corp            # Snapshot for a named brand
/digital-marketing-pro:status --quiet                      # One-line compact summary
/digital-marketing-pro:status --json                       # Machine-readable JSON
/digital-marketing-pro:status --section engagements        # Only the engagements section
```

## Sections

| Section | Contents |
|---------|----------|
| `brand` | Name, industry, voice, channels, languages, markets, competitors, primary goal |
| `engagements` | All engagements with current part, completed/blocked counts, days since update, pending decisions, versioned doc count |
| `insights` | Last 5 insights captured + days since last save + total count |
| `compliance` | Last 5 compliance violations + count in last 30 days |
| `deps` | Python version + mode (knowledge-only / lite / full) + available + missing packages |

## Health indicators surfaced

After the snapshot, the skill highlights items that need attention:

- Engagements not updated in 14+ days
- Engagements with pending re-run decisions awaiting action
- Recent compliance violations (last 30 days)
- Missing Python dependencies that affect feature availability

## Fast and read-only

This command never modifies state. It only reads from existing brand profile, engagement state, insights, and violations files. Safe to run at any time without side effects.

## See also

- [skills/status/SKILL.md](../skills/status/SKILL.md) — full skill specification
- [scripts/dm-status.py](../scripts/dm-status.py) — the underlying script
- [/digital-marketing-pro:brand-setup](brand-setup.md) — create or update a brand profile
- [/digital-marketing-pro:engagement status](engagement.md) — engagement-specific deep status
