#!/usr/bin/env python3
"""reddit_search.py — Scrape/search Reddit posts from subreddits over a time window.

Two paths, auto-selected:
  * KEYLESS (default): hit Reddit's public listing JSON
    https://www.reddit.com/r/<sub>/<sort>.json?t=<time>&limit=<n>
    via urllib with a real User-Agent. No key, lower volume/reliability.
  * APIFY (when APIFY_API_TOKEN is set or --use-apify): run a Reddit scraper actor via the
    managed async run/poll lifecycle in apify_common (start -> poll to terminal with a
    wall-clock timeout -> fetch dataset items), guarded by a COST GATE. Reliable at scale.

The Apify path enforces a cost gate: `--estimate-only` prints the projection and exits 0;
actual spend requires `--yes`; the run is aborted if reported usage exceeds --max-cost-usd
or the timeout trips. The KEYLESS path is never gated.

Both emit the same normalized schema so the agent gets a stable contract. Stdlib only.
Implements the robomotion-gtm-skills `reddit-post-finder` contract.

Examples:
  reddit_search.py --subreddit saas,startups --sort top --time week --max-posts 50
  reddit_search.py --subreddit devops --keywords "ci,pipeline" --days 14 --output summary
  APIFY_API_TOKEN=xxx reddit_search.py --subreddit rpa --use-apify --estimate-only
  APIFY_API_TOKEN=xxx reddit_search.py --subreddit rpa --use-apify --yes --max-cost-usd 0.50
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apify_common  # noqa: E402  (vendored async run/poll + cost gate)

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills-reddit-post-finder/1.0)"
VALID_SORT = {"hot", "top", "new", "rising"}
VALID_TIME = {"hour", "day", "week", "month", "year", "all"}
# A public Reddit scraper actor on the Apify store.
APIFY_ACTOR = os.environ.get("APIFY_REDDIT_ACTOR", "trudax~reddit-scraper-lite")


def _get(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("exhausted retries")


def browse_url(sub, sort, t):
    sub = sub.strip().lstrip("/").removeprefix("r/").strip("/")
    base = f"https://www.reddit.com/r/{sub}/{sort}/"
    if sort == "top":
        return base + "?" + urllib.parse.urlencode({"t": t})
    return base


def normalize_listing(child, sub):
    d = child.get("data", {})
    return {
        "dataType": "post",
        "title": d.get("title", ""),
        "body": d.get("selftext", "") or "",
        "communityName": "r/" + (d.get("subreddit") or sub),
        "upVotes": d.get("ups", 0) or d.get("score", 0) or 0,
        "numberOfComments": d.get("num_comments", 0) or 0,
        "createdAt": datetime.fromtimestamp(
            d.get("created_utc", 0) or 0, timezone.utc).isoformat() if d.get("created_utc") else "",
        "url": "https://www.reddit.com" + d.get("permalink", "") if d.get("permalink") else d.get("url", ""),
        "_created_ts": d.get("created_utc", 0) or 0,
    }


def fetch_keyless(sub, sort, t, max_posts):
    url = browse_url(sub, sort, t) + ("&" if "?" in browse_url(sub, sort, t) else "?")
    url += urllib.parse.urlencode({"limit": min(max_posts, 100), "raw_json": 1})
    raw = _get(url, headers={"User-Agent": UA})
    data = json.loads(raw)
    children = data.get("data", {}).get("children", [])
    return [normalize_listing(c, sub) for c in children][:max_posts]


def normalize_apify(item, sub):
    ts = item.get("createdAt") or item.get("created", "")
    cts = 0
    if isinstance(ts, str) and ts:
        try:
            cts = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
        except ValueError:
            cts = 0
    return {
        "dataType": item.get("dataType", "post"),
        "title": item.get("title", ""),
        "body": item.get("body", "") or item.get("text", "") or "",
        "communityName": item.get("communityName") or ("r/" + sub),
        "upVotes": item.get("upVotes", 0) or item.get("score", 0) or 0,
        "numberOfComments": item.get("numberOfComments", 0) or item.get("comments", 0) or 0,
        "createdAt": ts if isinstance(ts, str) else "",
        "url": item.get("url", "") or item.get("link", ""),
        "_created_ts": cts,
    }


def apify_input(subs, sort, t, max_posts):
    return {
        "startUrls": [{"url": browse_url(s, sort, t)} for s in subs],
        "maxItems": max_posts * max(len(subs), 1),
        "skipComments": True,
        "searchPosts": True,
    }


def fetch_apify(subs, sort, t, max_posts, token, max_cost_usd, timeout_s):
    body = apify_input(subs, sort, t, max_posts)
    items = apify_common.run_actor(
        APIFY_ACTOR, body, max_cost_usd=max_cost_usd, timeout_s=timeout_s, tok=token)
    if not isinstance(items, list):
        return []
    sub0 = subs[0] if subs else ""
    return [normalize_apify(it, sub0) for it in items]


def main():
    ap = argparse.ArgumentParser(description="Search Reddit posts from subreddits (keyless or Apify).")
    ap.add_argument("--subreddit", required=True, help="comma-separated subreddit name(s), no r/ prefix")
    ap.add_argument("--keywords", default="", help="comma-separated OR client-side filter")
    ap.add_argument("--days", type=int, default=30, help="only posts from last N days (default 30)")
    ap.add_argument("--max-posts", type=int, default=50, help="per subreddit cap (default 50)")
    ap.add_argument("--sort", default="top", choices=sorted(VALID_SORT))
    ap.add_argument("--time", default="week", choices=sorted(VALID_TIME), help="window for top sort")
    ap.add_argument("--use-apify", action="store_true", help="force Apify path (else auto when token set)")
    ap.add_argument("--estimate-only", action="store_true",
                    help="Apify cost gate: print projected cost/limits and exit 0 (no spend)")
    ap.add_argument("--yes", action="store_true",
                    help="Apify cost gate: confirm actual spend (required to start a run)")
    ap.add_argument("--max-cost-usd", type=float, default=1.0,
                    help="Apify cost gate: abort the run if reported usage exceeds this (default 1.00)")
    ap.add_argument("--apify-timeout", type=int, default=600,
                    help="Apify run/poll wall-clock timeout in seconds (default 600)")
    ap.add_argument("--output", default="json", choices=["json", "summary"])
    args = ap.parse_args()

    subs = [s for s in (x.strip() for x in args.subreddit.split(",")) if s]
    keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.days)).timestamp()

    items = []
    use_apify = args.use_apify or bool(token)
    if use_apify and not token:
        sys.exit("ERROR: --use-apify requested but APIFY_API_TOKEN is not set.")

    # COST GATE (Apify path only). --estimate-only never spends; spend needs --yes.
    if use_apify and args.estimate_only:
        est = apify_common.estimate(
            APIFY_ACTOR, apify_input(subs, args.sort, args.time, args.max_posts),
            max_cost_usd=args.max_cost_usd, timeout_s=args.apify_timeout,
            items_hint=args.max_posts * max(len(subs), 1), label="reddit-post-finder")
        json.dump(est, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if use_apify and not args.yes:
        sys.exit("ERROR: cost gate — the Apify path spends credits. Re-run with --yes to "
                 "confirm (and --max-cost-usd to cap), or --estimate-only to preview. The "
                 "keyless Reddit-JSON path runs without --yes when no token is set.")

    if use_apify:
        try:
            items = fetch_apify(subs, args.sort, args.time, args.max_posts, token,
                                args.max_cost_usd, args.apify_timeout)
        except apify_common.CostGateError as e:
            sys.exit(f"ERROR: cost gate: {e}")
        except apify_common.ApifyError as e:
            sys.exit(f"ERROR: Apify: {e}")
    else:
        for sub in subs:
            try:
                items.extend(fetch_keyless(sub, args.sort, args.time, args.max_posts))
            except Exception as e:  # noqa: BLE001
                print(f"WARN: keyless fetch failed for r/{sub}: {e}", file=sys.stderr)
            time.sleep(0.5)

    # client-side date filter
    if args.days:
        items = [it for it in items if not it["_created_ts"] or it["_created_ts"] >= cutoff]

    # client-side OR keyword filter
    if keywords:
        def keep(it):
            blob = (it["title"] + " " + it["body"]).lower()
            return any(k in blob for k in keywords)
        items = [it for it in items if keep(it)]

    items.sort(key=lambda it: it["upVotes"], reverse=True)
    for it in items:
        it.pop("_created_ts", None)

    if args.output == "summary":
        if not items:
            print("No Reddit results.")
            return
        for it in items:
            print(f"[{it['upVotes']:>5}^ {it['numberOfComments']:>4}c] {it['title']}  ({it['communityName']})")
            print(f"        {it['url']}  {it['createdAt']}")
    else:
        json.dump(items, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
