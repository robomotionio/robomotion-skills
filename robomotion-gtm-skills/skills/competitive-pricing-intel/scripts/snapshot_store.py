#!/usr/bin/env python3
"""snapshot_store.py — Persist monitoring snapshots and diff them across runs.

Deterministic, stdlib-only. A snapshot is a JSON object of {key: value} observations for
one entity (e.g. a competitor's pricing fields, or content/review counts). This tool:

  save   — append a timestamped snapshot row to a CSV history file (the durable store).
  diff   — compare a new snapshot JSON against the most recent saved snapshot for the same
           entity and emit added / removed / changed keys.
  latest — print the most recent saved snapshot for an entity.

CSV columns: ts,entity,key,value  (one row per observed key; long-format for easy diffing).
This is the keyless/local fallback for monitoring history. When SUPABASE_* / Airtable are
configured the SKILL.md routes durable storage there instead; this CSV always works offline.

No LLM — the agent rates change severity and writes the report from the diff output.

Examples:
  snapshot_store.py save --entity acme --input ${WORKSPACE}/acme_pricing.json \
      --store ${WORKSPACE}/supabase/pricing_history.csv
  snapshot_store.py diff --entity acme --input ${WORKSPACE}/acme_pricing_now.json \
      --store ${WORKSPACE}/supabase/pricing_history.csv
"""
import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone


def load_input(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        sys.exit("ERROR: --input must be a JSON object of {key: value} observations.")
    # flatten one level: lists/dicts -> json string so they compare as values
    flat = {}
    for k, v in data.items():
        flat[str(k)] = v if isinstance(v, (str, int, float, bool)) or v is None else json.dumps(v, sort_keys=True, ensure_ascii=False)
    return flat


def read_history(store):
    rows = []
    if store and os.path.exists(store):
        with open(store, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
    return rows


def latest_snapshot(store, entity):
    rows = [r for r in read_history(store) if r.get("entity") == entity]
    if not rows:
        return None, None
    last_ts = max(r["ts"] for r in rows)
    snap = {r["key"]: r["value"] for r in rows if r["ts"] == last_ts}
    return last_ts, snap


def cmd_save(args):
    flat = load_input(args.input)
    ts = args.ts or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(os.path.abspath(args.store)) or ".", exist_ok=True)
    exists = os.path.exists(args.store)
    with open(args.store, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["ts", "entity", "key", "value"])
        for k, v in flat.items():
            w.writerow([ts, args.entity, k, "" if v is None else str(v)])
    print(json.dumps({"saved": True, "entity": args.entity, "ts": ts, "keys": len(flat),
                      "store": args.store}, indent=2))


def cmd_diff(args):
    new = load_input(args.input)
    new = {k: ("" if v is None else str(v)) for k, v in new.items()}
    prev_ts, prev = latest_snapshot(args.store, args.entity)
    if prev is None:
        print(json.dumps({"entity": args.entity, "first_run": True,
                          "note": "no prior snapshot — this run is the baseline",
                          "added": list(new.keys()), "removed": [], "changed": {}}, indent=2))
        return
    added = {k: new[k] for k in new if k not in prev}
    removed = {k: prev[k] for k in prev if k not in new}
    changed = {k: {"prev": prev[k], "current": new[k]} for k in new
               if k in prev and prev[k] != new[k]}
    print(json.dumps({
        "entity": args.entity, "first_run": False, "prev_ts": prev_ts,
        "added": added, "removed": removed, "changed": changed,
        "has_changes": bool(added or removed or changed),
    }, ensure_ascii=False, indent=2))


def cmd_latest(args):
    ts, snap = latest_snapshot(args.store, args.entity)
    print(json.dumps({"entity": args.entity, "ts": ts, "snapshot": snap or {}},
                     ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Persist and diff monitoring snapshots via a CSV history store (keyless).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("save", "diff", "latest"):
        sp = sub.add_parser(name)
        sp.add_argument("--entity", required=True, help="entity id (e.g. competitor slug)")
        sp.add_argument("--store", required=True, help="CSV history file path (e.g. ${WORKSPACE}/supabase/history.csv)")
        if name in ("save", "diff"):
            sp.add_argument("--input", required=True, help="JSON object of {key: value} observations")
        if name == "save":
            sp.add_argument("--ts", default="", help="override timestamp (default: now UTC)")
    args = ap.parse_args()
    {"save": cmd_save, "diff": cmd_diff, "latest": cmd_latest}[args.cmd](args)


if __name__ == "__main__":
    main()
