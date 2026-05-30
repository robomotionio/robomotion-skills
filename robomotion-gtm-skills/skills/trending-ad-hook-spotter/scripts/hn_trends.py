#!/usr/bin/env python3
"""hn_trends.py — Recency-bounded Hacker News scan for trend detection (keyless).

Pulls recent stories / front-page items matching ICP keywords from the free Algolia HN API,
bounded to the last N days (recency is everything for trends). Returns items with an
engagement-velocity proxy (points + comments per hour since posting) so the host agent can
score and cluster them. Deterministic — no LLM; the agent does trend clustering, scoring,
and hook translation (see ../SKILL.md). Stdlib only.

Examples:
  hn_trends.py --keywords "rpa,workflow automation,ai agents" --days 7 --output hn.json
  hn_trends.py --keywords "observability" --tags front_page --days 3
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
HITS = 100


def fetch(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "robomotion-gtm-skills/trending-ad-hook-spotter"})
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


def velocity(points, comments, created_at_i, now_i):
    hours = max(1.0, (now_i - created_at_i) / 3600.0)
    return round((points + 1.5 * comments) / hours, 3)


def main():
    ap = argparse.ArgumentParser(description="Recency-bounded HN scan for trend detection (keyless).")
    ap.add_argument("--keywords", required=True, help="comma-separated ICP keywords")
    ap.add_argument("--days", type=int, default=7, help="recency window in days (default 7)")
    ap.add_argument("--tags", default="story", help="HN tags (story | front_page | comment)")
    ap.add_argument("--max-per-keyword", type=int, default=40, help="cap items per keyword")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    now_i = int(datetime.now(timezone.utc).timestamp())
    cutoff = int((datetime.now(timezone.utc) - timedelta(days=args.days)).timestamp())
    kws = [k.strip() for k in args.keywords.split(",") if k.strip()]

    seen, items = set(), []
    for kw in kws:
        page = 0
        kept = 0
        while kept < args.max_per_keyword and page < 10:
            data = fetch({"query": kw, "tags": args.tags,
                          "numericFilters": f"created_at_i>{cutoff}", "hitsPerPage": HITS, "page": page})
            hits = data.get("hits", [])
            if not hits:
                break
            for h in hits:
                hid = h.get("objectID")
                if hid in seen:
                    continue
                seen.add(hid)
                created_i = h.get("created_at_i") or cutoff
                pts = h.get("points") or 0
                ncom = h.get("num_comments") or 0
                items.append({
                    "id": hid,
                    "matched_keyword": kw,
                    "title": h.get("title") or h.get("story_title") or "",
                    "url": h.get("url") or h.get("story_url") or "",
                    "hn_url": f"https://news.ycombinator.com/item?id={hid}",
                    "points": pts,
                    "num_comments": ncom,
                    "created_at": h.get("created_at", ""),
                    "velocity": velocity(pts, ncom, created_i, now_i),
                })
                kept += 1
                if kept >= args.max_per_keyword:
                    break
            if page >= data.get("nbPages", 1) - 1:
                break
            page += 1
            time.sleep(0.2)

    items.sort(key=lambda x: x["velocity"], reverse=True)
    result = {"keywords": kws, "days": args.days, "platform": "hackernews",
              "item_count": len(items), "items": items}
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(items)} HN items -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
