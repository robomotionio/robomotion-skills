#!/usr/bin/env python3
"""dedup_history.py — recurring-monitor dedup against a workspace CSV history.

Stateless scripts emit a JSON array; this helper splits that array into "new" vs
"seen" items keyed on a stable field (default `url`), appends the new keys to a
workspace history CSV with a first-seen timestamp, and prints only the new items.
Run it after the fetch script so a recurring monitor surfaces only fresh records.

If SUPABASE_URL + SUPABASE_KEY are set you may instead persist to Supabase from the
host flow; this helper covers the keyless workspace-CSV path. Stdlib only.

Example:
  reddit_search.py --subreddit saas --output json > ${WORKSPACE}/run.json
  dedup_history.py --input ${WORKSPACE}/run.json --history ${WORKSPACE}/reddit_seen.csv \
      --key url > ${WORKSPACE}/new.json
"""
import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone


def load_seen(path):
    seen = {}
    if path and os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("key"):
                    seen[row["key"]] = row.get("first_seen", "")
    return seen


def append_seen(path, keys):
    if not path or not keys:
        return
    exists = os.path.exists(path)
    now = datetime.now(timezone.utc).isoformat()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["key", "first_seen"])
        for k in keys:
            w.writerow([k, now])


def main():
    ap = argparse.ArgumentParser(description="Dedup a JSON array against a workspace CSV history.")
    ap.add_argument("--input", required=True, help="JSON array file from the fetch script (or - for stdin)")
    ap.add_argument("--history", required=True, help="workspace CSV path holding seen keys + first_seen")
    ap.add_argument("--key", default="url", help="item field used as the dedup key (default url)")
    ap.add_argument("--output", default="-", help="write the NEW-only JSON array here (default stdout)")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    items = json.loads(raw)
    if not isinstance(items, list):
        sys.exit("ERROR: input must be a JSON array.")

    seen = load_seen(args.history)
    fresh, new_keys = [], []
    for it in items:
        k = str(it.get(args.key, "")).strip()
        if not k:
            fresh.append(it)  # no key -> can't dedup, treat as new
            continue
        if k in seen:
            continue
        fresh.append(it)
        new_keys.append(k)

    append_seen(args.history, new_keys)

    payload = json.dumps(fresh, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    print(f"{len(fresh)} new / {len(items)} total ({len(seen)} previously seen)", file=sys.stderr)


if __name__ == "__main__":
    main()
