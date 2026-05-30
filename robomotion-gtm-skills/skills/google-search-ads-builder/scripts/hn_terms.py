#!/usr/bin/env python3
"""hn_terms.py — Mine technical-buyer terminology from Hacker News (keyless).

Hits the free public Algolia HN API to pull recent stories/comments matching a query, so
the campaign builder can fold real technical-buyer framing into keyword research. Returns
the matching items plus a frequency-ranked term list (simple tokenization) the agent can
fold into seed keywords. Deterministic — no LLM. Stdlib only.

Examples:
  hn_terms.py --query "workflow automation" --days 365 --max-results 100
  hn_terms.py --query "rpa" --tags comment --output hn.json
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone, timedelta

API = "https://hn.algolia.com/api/v1/search_by_date"
HITS = 100
STOP = set("""the a an and or for to of in on with your you our we they it is are be this that
how what why when which who from at by as into out about can will just like more most some any
get use using used than then them their there here over under not no yes vs about new app apps
software tool tools company product products people work works working""".split())


def fetch(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "robomotion-gtm-skills/google-search-ads-builder"})
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


def tokens(text):
    for w in re.findall(r"[a-z][a-z0-9\-\.]{2,}", text.lower()):
        w = w.strip(".-")
        if w and w not in STOP and not w.isdigit():
            yield w


def main():
    ap = argparse.ArgumentParser(description="Mine HN terminology for keyword research (keyless).")
    ap.add_argument("--query", required=True, help="search terms")
    ap.add_argument("--days", type=int, default=365, help="days back (default 365)")
    ap.add_argument("--tags", default="(story,comment)", help="HN tags filter (default story+comment)")
    ap.add_argument("--max-results", type=int, default=100, help="cap on items (default 100)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    cutoff = int((datetime.now(timezone.utc) - timedelta(days=args.days)).timestamp())
    items, page, freq = [], 0, Counter()
    while len(items) < args.max_results and page < 20:
        data = fetch({"query": args.query, "tags": args.tags,
                      "numericFilters": f"created_at_i>{cutoff}", "hitsPerPage": HITS, "page": page})
        hits = data.get("hits", [])
        if not hits:
            break
        for h in hits:
            title = h.get("title") or h.get("story_title") or ""
            text = h.get("comment_text") or h.get("story_text") or ""
            # strip tags, then decode HTML entities (HN comment_text is HTML-escaped)
            blob = html.unescape(re.sub(r"<[^>]+>", " ", f"{title} {text}"))
            for t in tokens(blob):
                freq[t] += 1
            items.append({
                "id": h.get("objectID"),
                "title": title,
                "points": h.get("points") or 0,
                "num_comments": h.get("num_comments") or 0,
                "created_at": h.get("created_at", ""),
                "url": h.get("url") or h.get("story_url") or "",
            })
            if len(items) >= args.max_results:
                break
        if page >= data.get("nbPages", 1) - 1:
            break
        page += 1
        time.sleep(0.2)

    result = {
        "query": args.query,
        "item_count": len(items),
        "top_terms": [{"term": t, "count": c} for t, c in freq.most_common(60)],
        "items": items,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(items)} HN items, {len(freq)} terms -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
