#!/usr/bin/env python3
"""hn_fetch.py — Search Hacker News via the public Algolia HN API (keyless).

Deterministic, stdlib-only. A date-filtered HN collector for the industry scan / monitoring
legs. Returns stories/comments ranked by points. No LLM — the agent rates relevance.

Examples:
  hn_fetch.py --query "rpa automation" --days 7
  hn_fetch.py --query "uipath" --days 1 --output ${WORKSPACE}/hn.json
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

API = "https://hn.algolia.com/api/v1/search_by_date"


def fetch_page(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "robomotion-gtm-skills/industry-scanner"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("HN API: exhausted retries")


def normalize(hit):
    hid = hit.get("objectID")
    return {
        "id": hid,
        "title": hit.get("title") or hit.get("story_title") or "",
        "url": hit.get("url") or hit.get("story_url") or "",
        "author": hit.get("author", ""),
        "points": hit.get("points") or 0,
        "num_comments": hit.get("num_comments") or 0,
        "created_at": hit.get("created_at", ""),
        "hn_url": f"https://news.ycombinator.com/item?id={hid}" if hid else "",
        "text": hit.get("comment_text") or hit.get("story_text") or "",
    }


def main():
    ap = argparse.ArgumentParser(description="Search Hacker News via Algolia HN API (keyless).")
    ap.add_argument("--query", default="", help="search terms")
    ap.add_argument("--days", type=int, default=7, help="how many days back (default 7)")
    ap.add_argument("--tags", default="story", choices=["story", "comment", "ask_hn", "show_hn"])
    ap.add_argument("--max-results", type=int, default=50, help="cap on returned items")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    cutoff = int((datetime.now(timezone.utc) - timedelta(days=args.days)).timestamp())
    items, page = [], 0
    while len(items) < args.max_results and page < 20:
        params = {"tags": args.tags, "numericFilters": f"created_at_i>{cutoff}",
                  "hitsPerPage": 100, "page": page}
        if args.query:
            params["query"] = args.query
        data = fetch_page(params)
        hits = data.get("hits", [])
        if not hits:
            break
        items.extend(normalize(h) for h in hits)
        if page >= data.get("nbPages", 1) - 1:
            break
        page += 1
        time.sleep(0.2)

    items.sort(key=lambda it: it["points"], reverse=True)
    items = items[: args.max_results]
    out = json.dumps(items, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(items)} HN items -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
