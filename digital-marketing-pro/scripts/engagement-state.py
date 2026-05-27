#!/usr/bin/env python3
"""
engagement-state.py — Engagement state and lifecycle management.

Manages the 12-Part engagement workflow per the methodology defined in
skills/context-engine/engagement-flow-methodology.md.

Capabilities:
- Initialise a new engagement directory tree
- Read / update _engagement.json state
- List parts and their status
- Mark parts started / completed
- Manage Stone vs Opinion intake (Part 1)
- Set up v1 / v2 directory structure (Part 3 / Part 4)
- Apply the Decision Matrix to determine v2 re-runs (Part 5 → Part 6)
- Maintain the Living Project Instruction File header
- Bump source document versions per the Update-Back rule (Part 7+)
- Output engagement summary / file tree

Storage:
    Default workspace: $CLAUDE_PLUGIN_DATA/digital-marketing-pro/brands/{brand}/engagements/{id}/
    Fallback workspace: ~/.claude-marketing/brands/{brand}/engagements/{id}/

Usage:
    python engagement-state.py init --brand acme --id 2026-q2
    python engagement-state.py status --brand acme --id 2026-q2
    python engagement-state.py mark-part-started --brand acme --id 2026-q2 --part 3
    python engagement-state.py mark-part-completed --brand acme --id 2026-q2 --part 3
    python engagement-state.py add-stone-fact --brand acme --id 2026-q2 --fact-json '{"category":"...","fact":"...","source":"..."}'
    python engagement-state.py add-opinion --brand acme --id 2026-q2 --hypothesis-json '{"category":"...","hypothesis":"...","client_evidence":"...","research_question":"..."}'
    python engagement-state.py decision-matrix --brand acme --id 2026-q2 --validation-file path/to/client-validation-document.json
    python engagement-state.py file-tree --brand acme --id 2026-q2
    python engagement-state.py bump-version --brand acme --id 2026-q2 --doc 3.1 --reason "Segment X CAC corrected"

All commands print JSON output to stdout; errors go to stderr with exit code 1.

Author: Indranil Banerjee
Plugin: Digital Marketing Pro
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1.0.0"

# Maps engagement part identifier to its directory + canonical name.
PART_DEFINITIONS: dict[str, dict[str, Any]] = {
    "1":  {"name": "Client Inputs",                       "dir": "part-01-client-inputs",                "type": "intake"},
    "2":  {"name": "External Research",                   "dir": "part-02-external-research",            "type": "research"},
    "3":  {"name": "Four Core Documents",                 "dir": "part-03-four-core-documents",          "type": "strategy", "subdocs": ["3.1", "3.2", "3.3", "3.4"]},
    "4":  {"name": "Competitive + Customer + Market",     "dir": "part-04-competitive-customer-market",  "type": "research", "subdocs": ["4.1", "4.2", "4.3", "4.4"]},
    "5":  {"name": "Client Validation Document",          "dir": "part-05-client-validation",            "type": "client-facing"},
    "6":  {"name": "Selective v2 Re-runs",                "dir": "part-06-v2-reruns",                    "type": "strategy"},
    "7":  {"name": "Preparation Documents",               "dir": "part-07-preparation",                  "type": "internal"},
    "8":  {"name": "Growth Plan + Yearly Planner",        "dir": "part-08-growth-plan",                  "type": "client-facing"},
    "9":  {"name": "Channel Strategy Fan-out",            "dir": "part-09-channel-strategy",             "type": "channel"},
    "10": {"name": "Execution Artefacts",                 "dir": "part-10-execution-artefacts",          "type": "channel"},
    "11": {"name": "AI Creative Instructions",            "dir": "part-11-ai-creative-instructions",     "type": "channel"},
    "12": {"name": "Continuous Improvement Loop",         "dir": "part-12-continuous-improvement",       "type": "continuous"},
}

# Decision Matrix rules per skills/context-engine/decision-matrix-rerun.md
DECISION_MATRIX_RULES: dict[str, list[str]] = {
    "competitors_changed":         ["3.1", "3.2", "3.3", "3.4", "4.1", "4.2"],
    "target_market_changed":       ["4.3", "4.4"],
    "audiences_changed":           ["3.2", "3.3", "3.4"],
    "positioning_changed":         ["3.3"],
    "budget_or_scope_changed":     ["3.4"],
    "pricing_or_offering_changed": ["3.1"],
    "unit_economics_changed":      ["3.1"],
    # "minor_corrections_only" deliberately not included — does not trigger any v2 re-run
}

VALID_PART_STATUSES = {"not_started", "in_progress", "awaiting_input", "blocked", "completed", "deferred"}

VERSION_PATTERN = re.compile(r"^v(\d+)(?:\.(\d+))?$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 with 'Z' suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def workspace_root() -> Path:
    """Return the workspace root, preferring CLAUDE_PLUGIN_DATA when set."""
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin_data:
        return Path(plugin_data) / "digital-marketing-pro"
    return Path.home() / ".claude-marketing"


def engagement_dir(brand: str, engagement_id: str) -> Path:
    """Return the absolute path to the engagement directory."""
    return workspace_root() / "brands" / brand / "engagements" / engagement_id


def engagement_state_path(brand: str, engagement_id: str) -> Path:
    """Return the absolute path to _engagement.json."""
    return engagement_dir(brand, engagement_id) / "_engagement.json"


def lif_path(brand: str, engagement_id: str) -> Path:
    """Return the absolute path to the Living Project Instruction File."""
    return engagement_dir(brand, engagement_id) / "living-instruction-file.md"


def stone_facts_path(brand: str, engagement_id: str) -> Path:
    return engagement_dir(brand, engagement_id) / "part-01-client-inputs" / "stone-facts.json"


def opinion_hypotheses_path(brand: str, engagement_id: str) -> Path:
    return engagement_dir(brand, engagement_id) / "part-01-client-inputs" / "opinion-hypotheses.json"


def write_json_atomic(path: Path, data: Any) -> None:
    """Atomically write JSON to disk: write to .tmp then rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    """Lowercase alphanumeric+hyphen identifier suitable for directory names."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def out(payload: Any) -> None:
    """Print a structured payload as JSON to stdout."""
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def err(message: str, exit_code: int = 1) -> None:
    print(f"engagement-state error: {message}", file=sys.stderr)
    sys.exit(exit_code)


# ---------------------------------------------------------------------------
# State template
# ---------------------------------------------------------------------------

def initial_state(brand: str, engagement_id: str) -> dict[str, Any]:
    """Build the initial _engagement.json state document."""
    parts = {}
    for part_id, definition in PART_DEFINITIONS.items():
        parts[part_id] = {
            "name": definition["name"],
            "type": definition["type"],
            "status": "not_started",
            "started_at": None,
            "completed_at": None,
            "subdocs": definition.get("subdocs", []),
            "notes": "",
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "brand": brand,
        "engagement_id": engagement_id,
        "created_at": now_iso(),
        "last_updated_at": now_iso(),
        "current_part": "1",
        "parts": parts,
        "rerun_decisions": [],
        "version_history": {},     # filled with {"3.1": [{"version": "v1.0", "updated_at": ..., "reason": ...}]}
        "lif_change_log": [],
        "schema_url": "https://github.com/indranilbanerjee/digital-marketing-pro/blob/main/references/engagement-state-schema.md",
    }


def initial_lif(brand: str, engagement_id: str) -> str:
    """Build the initial Living Project Instruction File markdown."""
    timestamp = now_iso()
    return f"""# Living Project Instruction File

**Engagement:** {engagement_id}
**Brand:** {brand}
**Started:** {timestamp}
**Last updated:** {timestamp}
**Current part:** 1

---

## Quick Status

- **Engagement phase:** Setup
- **Active campaigns:** 0
- **Open review items:** 0
- **Outstanding corrections:** 0

---

## Currently True — Strategic Facts

(Populated as the engagement progresses through Parts 2–7. Stone facts captured in Part 1 will appear here once they are first referenced by a downstream document.)

---

## Recent Corrections (Last 30 Days)

(Populated as Update-Back corrections are applied per the Update-Back Rule.)

---

## Open Items Requiring Resolution

### Pending Validation
(none yet)

### Stress-Test Findings
(none yet)

### Open Opinions (Unresolved Hypotheses)
(populated from Part 1 opinion-hypotheses.json once the engagement starts)

---

## Current Part Status

**Part 1: Client Inputs**

- Started: {timestamp}
- Status: in_progress
- Progress: 0 of 3 deliverables completed (stone-facts.json / opinion-hypotheses.json / intake-questionnaire.md)
- Next required action: collect Stone vs Opinion intake from client
- Blocked on: nothing

---

## Version History (Source Docs)

(Populated as documents are produced and bumped per the Update-Back Rule.)

---

## Engagement Health Indicators

- **Days since last LIF update:** 0
- **Days since last source doc update:** N/A
- **Open review items aging > 14 days:** 0
- **Compliance violations in last 30 days:** 0

---

## Notes

(Free-form section for engagement-specific notes that future skill runs should consider.)
"""


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> None:
    """Initialise a new engagement directory tree."""
    brand_slug = slugify(args.brand)
    engagement_slug = slugify(args.id)
    if not brand_slug or not engagement_slug:
        err("brand and id must contain at least one alphanumeric character")
    root = engagement_dir(brand_slug, engagement_slug)
    if root.exists() and any(root.iterdir()):
        err(f"engagement directory already exists and is not empty: {root}")

    # Create the part directories
    for definition in PART_DEFINITIONS.values():
        (root / definition["dir"]).mkdir(parents=True, exist_ok=True)

    # Create v1 / v2 subdirectories for Parts 3 + 4
    for part_id in ("3", "4"):
        part_dir = root / PART_DEFINITIONS[part_id]["dir"]
        (part_dir / "v1").mkdir(exist_ok=True)
        (part_dir / "v2").mkdir(exist_ok=True)

    # Create reports + assets supporting directories
    (root / "reports" / "monthly").mkdir(parents=True, exist_ok=True)
    (root / "reports" / "quarterly").mkdir(exist_ok=True)
    (root / "reports" / "annual").mkdir(exist_ok=True)

    # Write initial state and LIF
    state = initial_state(brand_slug, engagement_slug)
    state["parts"]["1"]["status"] = "in_progress"
    state["parts"]["1"]["started_at"] = now_iso()
    write_json_atomic(engagement_state_path(brand_slug, engagement_slug), state)
    lif_path(brand_slug, engagement_slug).write_text(
        initial_lif(brand_slug, engagement_slug), encoding="utf-8"
    )

    # Write empty Stone / Opinion intake files so downstream skills find them
    stone_init = {
        "engagement_id": engagement_slug,
        "captured_at": now_iso(),
        "facts": [],
    }
    opinion_init = {
        "engagement_id": engagement_slug,
        "captured_at": now_iso(),
        "hypotheses": [],
    }
    write_json_atomic(stone_facts_path(brand_slug, engagement_slug), stone_init)
    write_json_atomic(opinion_hypotheses_path(brand_slug, engagement_slug), opinion_init)

    out({
        "status": "ok",
        "action": "initialised",
        "brand": brand_slug,
        "engagement_id": engagement_slug,
        "engagement_dir": str(root),
        "current_part": "1",
        "next_action": "Capture Stone vs Opinion intake. Use add-stone-fact / add-opinion commands or edit stone-facts.json / opinion-hypotheses.json directly.",
    })


def cmd_status(args: argparse.Namespace) -> None:
    """Print the current engagement status."""
    state_path = engagement_state_path(args.brand, args.id)
    state = read_json(state_path)
    parts_summary = []
    for part_id in sorted(state["parts"].keys(), key=lambda x: int(x)):
        part = state["parts"][part_id]
        parts_summary.append({
            "part": part_id,
            "name": part["name"],
            "status": part["status"],
            "started_at": part["started_at"],
            "completed_at": part["completed_at"],
        })
    out({
        "brand": state["brand"],
        "engagement_id": state["engagement_id"],
        "current_part": state["current_part"],
        "last_updated_at": state["last_updated_at"],
        "parts": parts_summary,
        "rerun_decisions_count": len(state.get("rerun_decisions", [])),
    })


def cmd_mark_part_started(args: argparse.Namespace) -> None:
    state_path = engagement_state_path(args.brand, args.id)
    state = read_json(state_path)
    part = str(args.part)
    if part not in state["parts"]:
        err(f"unknown part: {part}")
    if state["parts"][part]["status"] == "completed":
        err(f"part {part} is already completed; use mark-part-started --force to reopen", exit_code=2)
    state["parts"][part]["status"] = "in_progress"
    state["parts"][part]["started_at"] = state["parts"][part]["started_at"] or now_iso()
    state["current_part"] = part
    state["last_updated_at"] = now_iso()
    write_json_atomic(state_path, state)
    out({"status": "ok", "action": "part_started", "part": part})


def cmd_mark_part_completed(args: argparse.Namespace) -> None:
    state_path = engagement_state_path(args.brand, args.id)
    state = read_json(state_path)
    part = str(args.part)
    if part not in state["parts"]:
        err(f"unknown part: {part}")
    state["parts"][part]["status"] = "completed"
    state["parts"][part]["completed_at"] = now_iso()
    state["last_updated_at"] = now_iso()

    # Auto-advance current_part to the next not-yet-completed part if available
    next_part = None
    for candidate in sorted(state["parts"].keys(), key=lambda x: int(x)):
        if state["parts"][candidate]["status"] not in ("completed", "deferred"):
            next_part = candidate
            break
    if next_part:
        state["current_part"] = next_part
    write_json_atomic(state_path, state)
    out({"status": "ok", "action": "part_completed", "part": part, "next_part": next_part})


def cmd_set_part_status(args: argparse.Namespace) -> None:
    if args.status not in VALID_PART_STATUSES:
        err(f"invalid status; must be one of {sorted(VALID_PART_STATUSES)}")
    state_path = engagement_state_path(args.brand, args.id)
    state = read_json(state_path)
    part = str(args.part)
    if part not in state["parts"]:
        err(f"unknown part: {part}")
    state["parts"][part]["status"] = args.status
    if args.note:
        state["parts"][part]["notes"] = args.note
    state["last_updated_at"] = now_iso()
    write_json_atomic(state_path, state)
    out({"status": "ok", "part": part, "set_to": args.status})


def cmd_add_stone_fact(args: argparse.Namespace) -> None:
    """Append a Stone fact to part-01-client-inputs/stone-facts.json."""
    try:
        fact = json.loads(args.fact_json)
    except json.JSONDecodeError as exc:
        err(f"invalid --fact-json: {exc}")

    required = {"category", "fact", "source"}
    missing = required - set(fact.keys())
    if missing:
        err(f"fact missing required keys: {sorted(missing)}")

    facts_path = stone_facts_path(args.brand, args.id)
    if not facts_path.exists():
        err(f"engagement not initialised; run `init` first ({facts_path} not found)")
    container = read_json(facts_path)
    new_id = f"stone-{len(container['facts']) + 1:03d}"
    fact_entry = {
        "id": new_id,
        "captured_at": now_iso(),
        **fact,
    }
    container["facts"].append(fact_entry)
    container["captured_at"] = now_iso()
    write_json_atomic(facts_path, container)
    out({"status": "ok", "action": "stone_fact_added", "id": new_id})


def cmd_add_opinion(args: argparse.Namespace) -> None:
    """Append an Opinion hypothesis to part-01-client-inputs/opinion-hypotheses.json."""
    try:
        hypothesis = json.loads(args.hypothesis_json)
    except json.JSONDecodeError as exc:
        err(f"invalid --hypothesis-json: {exc}")

    required = {"category", "hypothesis", "client_evidence", "research_question"}
    missing = required - set(hypothesis.keys())
    if missing:
        err(f"hypothesis missing required keys: {sorted(missing)}")

    file_path = opinion_hypotheses_path(args.brand, args.id)
    if not file_path.exists():
        err(f"engagement not initialised; run `init` first ({file_path} not found)")
    container = read_json(file_path)
    new_id = f"opinion-{len(container['hypotheses']) + 1:03d}"
    hyp_entry = {
        "id": new_id,
        "captured_at": now_iso(),
        "status": "open",
        **hypothesis,
    }
    container["hypotheses"].append(hyp_entry)
    container["captured_at"] = now_iso()
    write_json_atomic(file_path, container)
    out({"status": "ok", "action": "opinion_added", "id": new_id})


def cmd_decision_matrix(args: argparse.Namespace) -> None:
    """Apply the Decision Matrix to determine which v2 re-runs are needed."""
    triggers: list[str] = []

    if args.validation_file:
        validation_path = Path(args.validation_file)
        if not validation_path.exists():
            err(f"validation file not found: {validation_path}")
        try:
            validation = json.loads(validation_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            err(f"invalid JSON in validation file: {exc}")
        triggers = validation.get("triggers", [])
        if not isinstance(triggers, list):
            err("validation file 'triggers' must be a list")
    elif args.triggers:
        triggers = [t.strip() for t in args.triggers.split(",") if t.strip()]
    else:
        err("provide either --validation-file or --triggers")

    triggered_reruns: set[str] = set()
    unknown_triggers: list[str] = []
    for trigger in triggers:
        if trigger in DECISION_MATRIX_RULES:
            triggered_reruns.update(DECISION_MATRIX_RULES[trigger])
        elif trigger == "minor_corrections_only":
            # Explicitly recognised; produces no v2 re-runs.
            continue
        else:
            unknown_triggers.append(trigger)

    if unknown_triggers:
        out({
            "status": "warning",
            "unknown_triggers": unknown_triggers,
            "valid_triggers": sorted(DECISION_MATRIX_RULES.keys()) + ["minor_corrections_only"],
            "triggered_reruns": sorted(triggered_reruns),
        })
        return

    decision_record = {
        "timestamp": now_iso(),
        "triggers": triggers,
        "triggered_reruns": sorted(triggered_reruns),
        "user_decision": "pending",
        "executed_reruns": [],
        "skipped_reruns": [],
    }

    state_path = engagement_state_path(args.brand, args.id)
    state = read_json(state_path)
    state.setdefault("rerun_decisions", []).append(decision_record)
    state["last_updated_at"] = now_iso()
    write_json_atomic(state_path, state)

    out({
        "status": "ok",
        "action": "decision_matrix_applied",
        "triggers": triggers,
        "triggered_reruns": sorted(triggered_reruns),
        "next_action": "Review the triggered re-runs with the user, then call `record-rerun-execution` to log what actually ran.",
    })


def cmd_record_rerun_execution(args: argparse.Namespace) -> None:
    """Update the most recent decision record with what was actually executed."""
    state_path = engagement_state_path(args.brand, args.id)
    state = read_json(state_path)
    if not state.get("rerun_decisions"):
        err("no rerun decisions on record; run decision-matrix first")
    decision = state["rerun_decisions"][-1]
    decision["user_decision"] = args.user_decision
    decision["executed_reruns"] = [r.strip() for r in (args.executed or "").split(",") if r.strip()]
    decision["skipped_reruns"] = [r.strip() for r in (args.skipped or "").split(",") if r.strip()]
    decision["notes"] = args.notes or ""
    decision["recorded_at"] = now_iso()
    state["last_updated_at"] = now_iso()
    write_json_atomic(state_path, state)
    out({"status": "ok", "action": "rerun_execution_recorded", "decision": decision})


def cmd_bump_version(args: argparse.Namespace) -> None:
    """Bump a source document's version per the Update-Back Rule."""
    doc_id = args.doc.strip()
    if not re.match(r"^\d+(\.\d+)?$", doc_id):
        err("--doc must be like '3.1' or '4.2' or '9.5'")
    state_path = engagement_state_path(args.brand, args.id)
    state = read_json(state_path)
    history = state.setdefault("version_history", {}).setdefault(doc_id, [])
    if not history:
        new_version = "v1.0"
    else:
        last = history[-1]["version"]
        match = VERSION_PATTERN.match(last)
        if not match:
            err(f"invalid prior version on record: {last}")
        major = int(match.group(1))
        minor = int(match.group(2)) if match.group(2) else 0
        if args.bump == "major":
            new_version = f"v{major + 1}.0"
        else:
            new_version = f"v{major}.{minor + 1}"
    entry = {
        "version": new_version,
        "updated_at": now_iso(),
        "reason": args.reason,
        "previous_version": history[-1]["version"] if history else None,
    }
    history.append(entry)
    state["last_updated_at"] = now_iso()
    write_json_atomic(state_path, state)
    out({"status": "ok", "action": "version_bumped", "doc": doc_id, "version": new_version})


def cmd_file_tree(args: argparse.Namespace) -> None:
    """Print the engagement directory file tree."""
    root = engagement_dir(args.brand, args.id)
    if not root.exists():
        err(f"engagement not initialised: {root}")
    tree = []
    for path in sorted(root.rglob("*")):
        if path.name.endswith(".tmp"):
            continue
        rel = path.relative_to(root)
        depth = len(rel.parts) - 1
        prefix = "  " * depth
        marker = "/" if path.is_dir() else ""
        tree.append(f"{prefix}{rel.parts[-1]}{marker}")
    out({
        "engagement_dir": str(root),
        "file_count": sum(1 for p in root.rglob("*") if p.is_file() and not p.name.endswith(".tmp")),
        "tree": tree,
    })


def cmd_lif_show(args: argparse.Namespace) -> None:
    """Emit the Living Project Instruction File contents."""
    path = lif_path(args.brand, args.id)
    if not path.exists():
        err(f"LIF not found: {path}")
    out({
        "lif_path": str(path),
        "contents": path.read_text(encoding="utf-8"),
    })


def cmd_lif_log_change(args: argparse.Namespace) -> None:
    """Append a change-log entry to _engagement.json under lif_change_log."""
    state_path = engagement_state_path(args.brand, args.id)
    state = read_json(state_path)
    entry = {
        "timestamp": now_iso(),
        "section": args.section,
        "summary": args.summary,
    }
    state.setdefault("lif_change_log", []).append(entry)
    state["last_updated_at"] = now_iso()
    write_json_atomic(state_path, state)
    out({"status": "ok", "action": "lif_change_logged", "entry": entry})


def cmd_list_engagements(args: argparse.Namespace) -> None:
    """List engagements for a brand (or all brands)."""
    base = workspace_root() / "brands"
    if not base.exists():
        out({"engagements": [], "workspace": str(workspace_root())})
        return
    results = []
    brand_filter = slugify(args.brand) if args.brand else None
    for brand_dir in sorted(base.iterdir()):
        if not brand_dir.is_dir():
            continue
        if brand_filter and brand_dir.name != brand_filter:
            continue
        engagements_dir = brand_dir / "engagements"
        if not engagements_dir.exists():
            continue
        for eng_dir in sorted(engagements_dir.iterdir()):
            state_file = eng_dir / "_engagement.json"
            if state_file.exists():
                try:
                    s = read_json(state_file)
                    results.append({
                        "brand": s.get("brand", brand_dir.name),
                        "engagement_id": s.get("engagement_id", eng_dir.name),
                        "current_part": s.get("current_part"),
                        "last_updated_at": s.get("last_updated_at"),
                    })
                except (json.JSONDecodeError, OSError):
                    results.append({
                        "brand": brand_dir.name,
                        "engagement_id": eng_dir.name,
                        "error": "state file unreadable",
                    })
    out({"engagements": results, "workspace": str(workspace_root())})


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="engagement-state.py",
        description="Engagement state management for the Digital Marketing Pro plugin's 12-Part methodology.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_brand_id(p: argparse.ArgumentParser) -> None:
        p.add_argument("--brand", required=True, help="Brand slug (e.g., 'acme')")
        p.add_argument("--id", required=True, help="Engagement ID (e.g., '2026-q2')")

    p_init = sub.add_parser("init", help="Initialise a new engagement directory tree")
    add_brand_id(p_init)

    p_status = sub.add_parser("status", help="Print engagement status")
    add_brand_id(p_status)

    p_started = sub.add_parser("mark-part-started", help="Mark a part as in_progress")
    add_brand_id(p_started)
    p_started.add_argument("--part", required=True, help="Part identifier (e.g., '3')")

    p_completed = sub.add_parser("mark-part-completed", help="Mark a part as completed")
    add_brand_id(p_completed)
    p_completed.add_argument("--part", required=True)

    p_set_status = sub.add_parser("set-part-status", help="Set arbitrary status on a part")
    add_brand_id(p_set_status)
    p_set_status.add_argument("--part", required=True)
    p_set_status.add_argument("--status", required=True, help=f"One of: {sorted(VALID_PART_STATUSES)}")
    p_set_status.add_argument("--note", default="")

    p_stone = sub.add_parser("add-stone-fact", help="Append a Stone fact to Part 1 intake")
    add_brand_id(p_stone)
    p_stone.add_argument("--fact-json", required=True, help='JSON: {"category":"...","fact":"...","source":"..."}')

    p_opinion = sub.add_parser("add-opinion", help="Append an Opinion hypothesis to Part 1 intake")
    add_brand_id(p_opinion)
    p_opinion.add_argument(
        "--hypothesis-json",
        required=True,
        help='JSON: {"category":"...","hypothesis":"...","client_evidence":"...","research_question":"..."}',
    )

    p_dm = sub.add_parser("decision-matrix", help="Apply the Decision Matrix for v2 re-runs")
    add_brand_id(p_dm)
    p_dm.add_argument("--validation-file", help="Path to a JSON validation file with a 'triggers' array")
    p_dm.add_argument(
        "--triggers",
        help=f"Comma-separated triggers; valid: {sorted(DECISION_MATRIX_RULES.keys())} or 'minor_corrections_only'",
    )

    p_rec = sub.add_parser("record-rerun-execution", help="Record what actually ran after a decision")
    add_brand_id(p_rec)
    p_rec.add_argument("--user-decision", required=True, choices=["approved", "modified", "rejected"])
    p_rec.add_argument("--executed", default="", help="Comma-separated doc IDs that were re-run")
    p_rec.add_argument("--skipped", default="", help="Comma-separated doc IDs that were skipped")
    p_rec.add_argument("--notes", default="")

    p_bump = sub.add_parser("bump-version", help="Bump a source document version (Update-Back Rule)")
    add_brand_id(p_bump)
    p_bump.add_argument("--doc", required=True, help="Document ID (e.g., '3.1')")
    p_bump.add_argument("--reason", required=True, help="Reason for the version bump")
    p_bump.add_argument("--bump", default="minor", choices=["minor", "major"])

    p_tree = sub.add_parser("file-tree", help="Print engagement directory file tree")
    add_brand_id(p_tree)

    p_lif = sub.add_parser("lif-show", help="Print the Living Project Instruction File")
    add_brand_id(p_lif)

    p_lif_log = sub.add_parser("lif-log-change", help="Log an LIF change in _engagement.json")
    add_brand_id(p_lif_log)
    p_lif_log.add_argument("--section", required=True)
    p_lif_log.add_argument("--summary", required=True)

    p_list = sub.add_parser("list-engagements", help="List engagements (optionally filter by brand)")
    p_list.add_argument("--brand", default=None)

    return parser


COMMAND_HANDLERS = {
    "init": cmd_init,
    "status": cmd_status,
    "mark-part-started": cmd_mark_part_started,
    "mark-part-completed": cmd_mark_part_completed,
    "set-part-status": cmd_set_part_status,
    "add-stone-fact": cmd_add_stone_fact,
    "add-opinion": cmd_add_opinion,
    "decision-matrix": cmd_decision_matrix,
    "record-rerun-execution": cmd_record_rerun_execution,
    "bump-version": cmd_bump_version,
    "file-tree": cmd_file_tree,
    "lif-show": cmd_lif_show,
    "lif-log-change": cmd_lif_log_change,
    "list-engagements": cmd_list_engagements,
}


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = COMMAND_HANDLERS.get(args.command)
    if not handler:
        err(f"unknown command: {args.command}")
    try:
        handler(args)
    except FileNotFoundError as exc:
        err(str(exc))
    except (PermissionError, OSError) as exc:
        err(f"filesystem error: {exc}")


if __name__ == "__main__":
    main()
