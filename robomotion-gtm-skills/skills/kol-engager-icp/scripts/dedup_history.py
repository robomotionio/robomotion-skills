#!/usr/bin/env python3
"""dedup_history.py — Stage 5: cross-run dedup by normalized profile_url.

KOL audiences overlap heavily run-to-run (the same in-market people engage many KOLs). This
filters out leads already seen in prior runs, using a workspace CSV ledger as the source of
truth and (optionally) Supabase for a shared, multi-machine ledger.

Flow: load seen keys (CSV + Supabase) -> drop input rows whose normalized profile_url is
already seen -> append the survivors to the ledger (and Supabase) -> write the new rows.
Idempotent: re-running the same input yields zero new rows. Stdlib only.

Auth: none for CSV. Optional Supabase: SUPABASE_URL + SUPABASE_KEY (+ --supabase-table).

Examples:
  dedup_history.py --input scored.json --history ${WORKSPACE}/kol_leads_seen.csv \
      --output new_leads.json
  dedup_history.py --input scored.json --history seen.csv --supabase-table kol_leads \
      --output new_leads.json
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

FIELDS = ["profile_url_norm", "name", "title", "company", "profile_url",
          "kol_source", "post_topic", "icp_tier", "icp_score", "first_seen"]


def norm_url(u):
    if not u:
        return ""
    return u.split("?")[0].rstrip("/").lower().replace("http://", "https://")


def load_csv_seen(path):
    seen = set()
    if not path or not os.path.exists(path):
        return seen
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = row.get("profile_url_norm") or norm_url(
                row.get("profile_url") or row.get("linkedin_url") or "")
            if k:
                seen.add(k)
    return seen


def append_csv(path, rows):
    if not path:
        return
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)


# ------------------------------- Supabase (optional) -------------------------

def supabase_cfg():
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_KEY", "").strip() or \
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return (url, key) if url and key else (None, None)


def sb_req(url, key, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"apikey": key, "Authorization": f"Bearer {key}",
               "Content-Type": "application/json"}
    if method == "POST":
        headers["Prefer"] = "return=minimal"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                txt = r.read().decode("utf-8")
                return json.loads(txt) if txt.strip() else []
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            print(f"WARN: Supabase {e.code}: {e.read().decode('utf-8','ignore')[:160]}",
                  file=sys.stderr)
            return None
        except urllib.error.URLError as e:
            print(f"WARN: Supabase network: {e}", file=sys.stderr)
            return None


def sb_load_seen(table):
    url, key = supabase_cfg()
    if not url:
        return set()
    q = f"{url}/rest/v1/{urllib.parse.quote(table)}?select=profile_url_norm"
    data = sb_req(q, key)
    if not isinstance(data, list):
        return set()
    return {r.get("profile_url_norm") for r in data if r.get("profile_url_norm")}


def sb_insert(table, rows):
    url, key = supabase_cfg()
    if not url or not rows:
        return
    q = f"{url}/rest/v1/{urllib.parse.quote(table)}"
    payload = [{k: r.get(k) for k in FIELDS} for r in rows]
    sb_req(q, key, method="POST", body=payload)


def main():
    ap = argparse.ArgumentParser(description="Cross-run dedup by normalized profile_url.")
    ap.add_argument("--input", required=True, help="scored.json (or any rows with profile_url)")
    ap.add_argument("--history", default="", help="workspace CSV ledger path")
    ap.add_argument("--supabase-table", default="", help="optional Supabase table for shared ledger")
    ap.add_argument("--no-append", action="store_true",
                    help="dedup only; do not record survivors in the ledger")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        rows = json.load(f)

    seen = load_csv_seen(args.history)
    if args.supabase_table:
        seen |= sb_load_seen(args.supabase_table)

    new_rows, batch_seen, ledger = [], set(), []
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for r in rows:
        k = norm_url(r.get("profile_url") or r.get("linkedin_url") or "")
        if k and (k in seen or k in batch_seen):
            continue
        if k:
            batch_seen.add(k)
        new_rows.append(r)
        ledger.append({
            "profile_url_norm": k,
            "name": r.get("name", ""),
            "title": r.get("title") or r.get("headline", ""),
            "company": r.get("company", ""),
            "profile_url": r.get("profile_url") or r.get("linkedin_url", ""),
            "kol_source": r.get("kol_source", ""),
            "post_topic": r.get("post_topic", ""),
            "icp_tier": r.get("icp_tier", ""),
            "icp_score": r.get("icp_score", ""),
            "first_seen": now,
        })

    if not args.no_append:
        append_csv(args.history, ledger)
        if args.supabase_table:
            sb_insert(args.supabase_table, ledger)

    payload = json.dumps(new_rows, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    dropped = len(rows) - len(new_rows)
    print(f"{len(new_rows)} new ({dropped} already-seen dropped) -> {args.output}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
