#!/usr/bin/env python3
"""hn_search.py — Search Hacker News stories/comments via the public Algolia HN API.

Keyless. Stdlib only (urllib) so it runs on the base image with no pip install.
Implements the robomotion-gtm-skills `hacker-news-scraper` contract.

Examples:
  hn_search.py --query "robomotion" --days 30 --tags story
  hn_search.py --tags show_hn --days 7 --max-results 30        # launch discovery
  hn_search.py --query "rpa" --keywords "uipath,automation" --output summary
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

API = "https://hn.algolia.com/api/v1/search_by_date"
HITS_PER_PAGE = 100  # Algolia max
VALID_TAGS = {"story", "comment", "ask_hn", "show_hn"}


def fetch_page(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "robomotion-gtm-skills/hacker-news-scraper"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 ** attempt)  # 1,2,4s backoff
                continue
            raise
    raise RuntimeError("HN API: exhausted retries")


def normalize(hit):
    hid = hit.get("objectID")
    title = hit.get("title") or hit.get("story_title") or ""
    text = hit.get("comment_text") or hit.get("story_text") or ""
    return {
        "id": hid,
        "title": title,
        "url": hit.get("url") or hit.get("story_url") or "",
        "author": hit.get("author", ""),
        "points": hit.get("points") or 0,
        "num_comments": hit.get("num_comments") or 0,
        "created_at": hit.get("created_at", ""),
        "hn_url": f"https://news.ycombinator.com/item?id={hid}" if hid else "",
        "text": text,
    }


def main():
    ap = argparse.ArgumentParser(description="Search Hacker News via Algolia HN API (keyless).")
    ap.add_argument("--query", default="", help="search terms (may be empty if --tags drives it)")
    ap.add_argument("--days", type=int, default=7, help="how many days back (default 7)")
    ap.add_argument("--tags", default="story", choices=sorted(VALID_TAGS),
                    help="item type (default story)")
    ap.add_argument("--max-results", type=int, default=50, help="cap on returned items (default 50)")
    ap.add_argument("--keywords", default="", help="comma-separated OR client-side filter")
    ap.add_argument("--output", default="json", choices=["json", "summary"])
    args = ap.parse_args()

    cutoff = int((datetime.now(timezone.utc) - timedelta(days=args.days)).timestamp())
    keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]

    items, page, pages_max = [], 0, 50
    while len(items) < args.max_results and page < pages_max:
        params = {
            "tags": args.tags,
            "numericFilters": f"created_at_i>{cutoff}",
            "hitsPerPage": HITS_PER_PAGE,
            "page": page,
        }
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
        time.sleep(0.2)  # be polite

    # client-side OR keyword filter
    if keywords:
        def keep(it):
            blob = (it["title"] + " " + it["text"]).lower()
            return any(k in blob for k in keywords)
        items = [it for it in items if keep(it)]

    items.sort(key=lambda it: it["points"], reverse=True)
    items = items[: args.max_results]

    if args.output == "summary":
        if not items:
            print("No Hacker News results.")
            return
        for it in items:
            print(f"[{it['points']:>4}pts {it['num_comments']:>3}c] {it['title']}")
            print(f"        {it['hn_url']}  by {it['author']}  {it['created_at']}")
    else:
        json.dump(items, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
