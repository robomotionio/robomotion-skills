#!/usr/bin/env python3
"""luma_search.py — Luma search mode (full guest profiles) via the Apify Luma actor.

Search mode discovers events by topic+location and returns full event data including
featured guest profiles (LinkedIn/X/bio). Requires APIFY_API_TOKEN — the Apify Luma
actor is the only path to full registered-guest profiles. Without the token, use the
keyless direct-scrape mode (luma_scrape_pw.mjs), which yields hosts + metadata only.

Normalizes people records and (optionally) emits CSV or JSON. Stdlib only.

Example:
  luma_search.py --search "AI agents San Francisco" --output json
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

ACTOR = os.environ.get("APIFY_LUMA_ACTOR", "apify~luma-scraper")


def token():
    t = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not t:
        sys.exit("ERROR: APIFY_API_TOKEN not set. Search mode needs the Apify Luma actor; "
                 "without it use the keyless direct-scrape (luma_scrape_pw.mjs, hosts only).")
    return t


def apify_run(run_input):
    url = (f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={urllib.parse.quote(token())}")
    data = json.dumps(run_input).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apify {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def normalize(rec):
    """Map one Apify result record (event + guests) into flat people rows."""
    rows = []
    event_name = rec.get("name") or rec.get("eventName") or ""
    event_date = rec.get("startAt") or rec.get("start_at") or rec.get("event_date") or ""
    guests = rec.get("guests") or rec.get("hosts") or rec.get("people") or []
    if isinstance(rec.get("host"), dict):
        guests = [rec["host"]] + list(guests)
    for g in guests:
        if not isinstance(g, dict):
            continue
        name = g.get("name") or g.get("fullName") or ""
        if not name:  # skip null names
            continue
        rows.append({
            "name": name,
            "bio": g.get("bio") or "",
            "linkedin_url": g.get("linkedinUrl") or g.get("linkedin") or "",
            "x": g.get("twitter") or g.get("twitterHandle") or "",
            "instagram": g.get("instagram") or "",
            "website": g.get("website") or "",
            "company": g.get("company") or "",
            "event_name": event_name,
            "event_date": event_date,
            "role": g.get("role") or "guest",
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="Luma search mode (full guest profiles, Apify).")
    ap.add_argument("--search", required=True, help="topic + location to discover events")
    ap.add_argument("--max-events", type=int, default=20)
    ap.add_argument("--output", default="json", choices=["json", "csv"])
    args = ap.parse_args()

    recs = apify_run({"search": args.search, "maxItems": args.max_events})
    people, seen = [], set()
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        for row in normalize(rec):
            key = (row["name"].strip().lower(),
                   row["linkedin_url"].split("?")[0].lower())
            if key in seen:
                continue
            seen.add(key)
            people.append(row)

    if args.output == "csv":
        w = csv.writer(sys.stdout)
        cols = ["name", "title_company", "linkedin_url", "x", "instagram",
                "website", "company", "event_name", "event_date", "role", "bio"]
        w.writerow(cols)
        for p in people:
            w.writerow([p["name"], "", p["linkedin_url"], p["x"], p["instagram"],
                        p["website"], p["company"], p["event_name"], p["event_date"],
                        p["role"], p["bio"]])
    else:
        print(json.dumps({"mode": "search", "search": args.search, "people": people},
                         ensure_ascii=False, indent=2))
    print(f"{len(people)} people across events -> ({args.output})", file=sys.stderr)


if __name__ == "__main__":
    main()
