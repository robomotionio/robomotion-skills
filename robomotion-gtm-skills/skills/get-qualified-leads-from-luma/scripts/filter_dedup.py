#!/usr/bin/env python3
"""filter_dedup.py — merge parallel Luma searches, filter by timeframe, dedup by name.

Takes one or more luma_search.py output files (run in parallel over topic+location keyword
variations) and:
  - filters events to the timeframe by event_date (Luma returns events from all time)
  - merges + dedups attendees by lowercased name (skips null/empty names)
Emits the merged people list the AGENT then qualifies. Stdlib only.

Example:
  filter_dedup.py --inputs s1.json s2.json s3.json --since-days 30 --output people.json
"""
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta


def parse_dt(s):
    if not s:
        return None
    for fmt, n in (("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%d", 10)):
        try:
            return datetime.strptime(str(s)[:n], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description="Merge+filter+dedup parallel Luma search outputs.")
    ap.add_argument("--inputs", nargs="+", required=True, help="luma_search.py JSON files")
    ap.add_argument("--since-days", type=int, default=30, help="keep events within N days (0=all)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    cutoff = None
    if args.since_days > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.since_days)

    people, seen = [], set()
    for path in args.inputs:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        rows = data.get("people", data) if isinstance(data, dict) else data
        for p in rows:
            name = (p.get("name") or "").strip()
            if not name:  # skip null/None names
                continue
            ed = parse_dt(p.get("event_date"))
            if cutoff and ed and ed < cutoff:
                continue  # stale event
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            people.append(p)

    payload = json.dumps({"people": people}, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(people)} unique attendees (timeframe-filtered) -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
