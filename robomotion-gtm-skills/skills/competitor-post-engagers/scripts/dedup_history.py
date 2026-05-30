#!/usr/bin/env python3
"""dedup_history.py — cross-run dedup of engagers by normalized profile_url.

Engine step 2: between extraction and (paid) enrichment, drop anyone you've already seen
in a prior run so you never re-extract / re-enrich the same person. Maintains a workspace
CSV history of every profile_url ever processed; optionally mirrors to Supabase.

This is the credit-saving gate: run it BEFORE enrich_apollo.py so Apollo credits are only
spent on net-new engagers.

Auth: none for CSV. Optional Supabase: SUPABASE_URL + SUPABASE_KEY (+ --supabase-table).
Stdlib only (Supabase via REST/urllib).

Examples:
  # Drop anyone already in history.csv; append the survivors to history; emit fresh rows:
  dedup_history.py --input engagers.json --history ${WORKSPACE}/history.csv \
      --output new_engagers.json

  # Report only (don't write history) to preview the net-new count:
  dedup_history.py --input engagers.json --history ${WORKSPACE}/history.csv --dry-run
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request


def norm_url(u):
    if not u:
        return ""
    u = u.split("?")[0].rstrip("/").lower()
    return u.replace("http://", "https://")


def load_history_csv(path):
    seen = set()
    if path and os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                for col in ("profile_url", "linkedin_url", "url"):
                    if row.get(col):
                        seen.add(norm_url(row[col]))
    return seen


def append_history_csv(path, rows):
    if not path:
        return
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["profile_url", "competitor", "post_url"])
        for r in rows:
            w.writerow([norm_url(r.get("profile_url")), r.get("competitor", ""),
                        r.get("post_url", "")])


def load_history_supabase(table):
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if not (url and key):
        return None
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}?select=profile_url"
    req = urllib.request.Request(endpoint, headers={"apikey": key,
                                "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
        return {norm_url(x.get("profile_url")) for x in data if x.get("profile_url")}
    except urllib.error.HTTPError as e:
        print(f"WARN: Supabase read {e.code}: {e.read().decode('utf-8','ignore')[:200]}",
              file=sys.stderr)
        return None
    except Exception as e:
        print(f"WARN: Supabase read failed: {e}", file=sys.stderr)
        return None


def insert_history_supabase(table, rows):
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if not (url and key) or not rows:
        return
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    body = json.dumps([{"profile_url": norm_url(r.get("profile_url")),
                        "competitor": r.get("competitor", ""),
                        "post_url": r.get("post_url", "")} for r in rows]).encode()
    req = urllib.request.Request(
        endpoint, data=body, method="POST",
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "application/json", "Prefer": "resolution=ignore-duplicates"})
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        print(f"WARN: Supabase insert {e.code}: {e.read().decode('utf-8','ignore')[:200]}",
              file=sys.stderr)
    except Exception as e:
        print(f"WARN: Supabase insert failed: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Cross-run dedup of engagers by normalized profile_url.")
    ap.add_argument("--input", required=True, help="JSON list of engagers from extract_engagers.py")
    ap.add_argument("--history", default="", help="workspace CSV of previously-seen profile_urls")
    ap.add_argument("--supabase-table", default="engager_history",
                    help="Supabase table (used only if SUPABASE_URL/KEY set)")
    ap.add_argument("--dry-run", action="store_true", help="report net-new count; do not write history")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        engagers = json.load(f)

    seen = load_history_csv(args.history)
    sb_seen = load_history_supabase(args.supabase_table)
    if sb_seen is not None:
        seen |= sb_seen

    fresh, batch_seen = [], set()
    for e in engagers:
        k = norm_url(e.get("profile_url"))
        if not k:
            fresh.append(e)  # keep nameless/urlless rows; agent can still review
            continue
        if k in seen or k in batch_seen:
            continue
        batch_seen.add(k)
        fresh.append(e)

    if not args.dry_run:
        append_history_csv(args.history, fresh)
        insert_history_supabase(args.supabase_table, fresh)

    payload = json.dumps(fresh, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    print(f"net-new {len(fresh)} / {len(engagers)} engagers "
          f"({len(engagers) - len(fresh)} already seen)"
          f"{' [dry-run]' if args.dry_run else ''} -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
