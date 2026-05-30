#!/usr/bin/env python3
"""calendar_to_csv.py — render an agent-built content calendar JSON to CSV.

Deterministic glue for the seo-content-engine playbook. The host agent produces the
prioritized content calendar (sequencing, funnel stage, brief) as JSON; this script
just emits a clean, capacity-checked CSV the team can drop into a sheet.

Input JSON: array of items, each with any of these keys (missing -> blank):
  week, publish_date, title, url_slug, funnel_stage, content_type, primary_keyword,
  secondary_keywords (list or str), word_count, priority, internal_links (list),
  cta, status, owner, notes

Validates against --capacity (pieces per period) and warns (stderr) on any period
that exceeds it — never silently over-schedules.

Example:
  calendar_to_csv.py --input calendar.json --capacity 3 --period week \
      --output content-calendar-2026-05-30.csv
"""
import argparse
import csv
import json
import sys
from collections import Counter

COLUMNS = ["week", "publish_date", "title", "url_slug", "funnel_stage", "content_type",
           "primary_keyword", "secondary_keywords", "word_count", "priority",
           "internal_links", "cta", "status", "owner", "notes"]


def flatten(v):
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return "" if v is None else str(v)


def main():
    ap = argparse.ArgumentParser(description="Render an SEO content calendar JSON to CSV.")
    ap.add_argument("--input", required=True, help="calendar JSON (array of items)")
    ap.add_argument("--capacity", type=int, default=0,
                    help="max pieces per period for an over-schedule warning (0=skip)")
    ap.add_argument("--period", default="week", choices=["week", "publish_date"],
                    help="field to group capacity check on (default week)")
    ap.add_argument("--output", default="-", help="output CSV path (default stdout)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        items = json.load(f)
    if not isinstance(items, list):
        sys.exit("ERROR: --input must be a JSON array of calendar items.")

    rows = [{c: flatten(it.get(c)) for c in COLUMNS} for it in items]

    if args.capacity > 0:
        counts = Counter(r[args.period] for r in rows if r[args.period])
        for period, n in sorted(counts.items()):
            if n > args.capacity:
                print(f"WARNING: {args.period}={period} has {n} pieces "
                      f"(> capacity {args.capacity}) — rebalance.", file=sys.stderr)

    if args.output == "-":
        w = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} calendar rows -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
