#!/usr/bin/env python3
"""dedup_history.py — cross-RUN dedup by normalized profile_url (workspace CSV history).

A run can produce leads you already surfaced last week. This drops any lead whose
normalized profile_url is already in the history CSV, then appends the survivors to the
history so the next run won't re-surface them. Optional Supabase mirror when SUPABASE_URL
+ SUPABASE_KEY are set (table default 'pain_lead_history').

History CSV columns: profile_url, name, first_seen_run, role
(in-run dedup is already done by extract_engagers.py; this is the durable cross-run layer.)

Example:
  dedup_history.py --input scored.json --history ${WORKSPACE}/lead_history.csv \
      --run-id 2026-05-30 --output new_leads.json
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
    return u.split("?")[0].rstrip("/").lower().replace("http://", "https://")


def load_history(path):
    seen = set()
    if not path or not os.path.exists(path):
        return seen
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for col in ("profile_url", "linkedin_url", "url"):
                if row.get(col):
                    seen.add(norm_url(row[col]))
    return seen


def append_history(path, rows, run_id):
    if not path:
        return
    exists = os.path.exists(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["profile_url", "name", "first_seen_run", "role"])
        for r in rows:
            w.writerow([norm_url(r.get("profile_url")), r.get("name", ""), run_id,
                        r.get("role", "")])


def supabase_push(rows, run_id, table):
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip() or \
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key or not rows:
        return 0
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    body = json.dumps([
        {"profile_url": norm_url(r.get("profile_url")), "name": r.get("name", ""),
         "role": r.get("role", ""), "first_seen_run": run_id,
         "score": r.get("score"), "tier": r.get("tier")}
        for r in rows]).encode("utf-8")
    req = urllib.request.Request(
        endpoint, data=body, method="POST",
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "application/json",
                 "Prefer": "resolution=ignore-duplicates,return=minimal"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        print(f"WARN: supabase push {e.code}: {e.read().decode('utf-8','ignore')[:160]}",
              file=sys.stderr)
        return 0
    except Exception as e:
        print(f"WARN: supabase push failed: {e}", file=sys.stderr)
        return 0


def main():
    ap = argparse.ArgumentParser(description="Cross-run dedup by profile_url (CSV + optional Supabase).")
    ap.add_argument("--input", required=True, help="scored.json / engagers.json")
    ap.add_argument("--history", required=True, help="workspace history CSV (created if absent)")
    ap.add_argument("--run-id", default="", help="label for this run (e.g. a date)")
    ap.add_argument("--no-append", action="store_true",
                    help="report new leads but do NOT write them to history")
    ap.add_argument("--supabase-table", default="pain_lead_history")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        leads = json.load(f)
    if isinstance(leads, dict):
        sys.exit("ERROR: --input looks like a degrade plan, not leads.")

    seen = load_history(args.history)
    fresh, dup = [], 0
    for lead in leads:
        u = norm_url(lead.get("profile_url"))
        if u and u in seen:
            dup += 1
            continue
        if u:
            seen.add(u)  # in-batch guard too
        fresh.append(lead)

    if not args.no_append:
        append_history(args.history, fresh, args.run_id)
        supabase_push(fresh, args.run_id, args.supabase_table)

    payload = json.dumps(fresh, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    print(f"{len(fresh)} new leads ({dup} seen-before dropped) -> {args.output}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
