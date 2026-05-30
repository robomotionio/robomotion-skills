#!/usr/bin/env python3
"""x_search.py — Search/scrape X posts for a query with reliable date
filtering (native since:/until: operators in the search term).

Two paths, auto-selected:
  * APIFY (when APIFY_API_TOKEN set or --use-apify): a tweet-scraper actor via the managed
    async run/poll lifecycle in apify_common (start -> poll to terminal with a wall-clock
    timeout -> fetch dataset items), guarded by a COST GATE. searchTerms / searchMode=live.
  * KEYLESS degrade: X is login-walled and anti-bot, so the keyless path is the bundled
    Playwright scraper (scripts/x_scrape.mjs). Best-effort, low reliability.

The Apify path enforces a cost gate: `--estimate-only` prints the projection and exits 0;
actual spend requires `--yes`; the run aborts if reported usage exceeds --max-cost-usd or
the timeout trips. The KEYLESS Playwright degrade is never gated.

Both emit one normalized schema. Stdlib only (keyless path needs node + Playwright; see
SKILL.md). Implements the robomotion-gtm-skills `x-mention-tracker` contract.

Examples:
  x_search.py --query "robomotion" --since 2025-01-01 --until 2025-02-01
  x_search.py --query "from:levelsio" --max-posts 30 --output summary
  APIFY_API_TOKEN=xxx x_search.py --query "rpa" --use-apify --estimate-only
  APIFY_API_TOKEN=xxx x_search.py --query "rpa" --use-apify --yes --max-cost-usd 0.50
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apify_common  # noqa: E402  (vendored async run/poll + cost gate)

APIFY_ACTOR = os.environ.get("APIFY_TWITTER_ACTOR", "apidojo~tweet-scraper")
HERE = os.path.dirname(os.path.abspath(__file__))


def build_term(query, since, until):
    term = query.strip()
    if since:
        term += f" since:{since}"
    if until:
        term += f" until:{until}"
    return term.strip()


def normalize(item):
    author = item.get("author") or {}
    if isinstance(author, str):
        author = {"userName": author}
    tid = str(item.get("id") or item.get("id_str") or item.get("tweetId") or "")
    url = item.get("twitterUrl") or item.get("url") or item.get("tweetUrl") or ""
    if not url and tid and author.get("userName"):
        url = f"https://x.com/{author['userName']}/status/{tid}"
    return {
        "id": tid,
        "text": item.get("text", "") or item.get("fullText", "") or "",
        "fullText": item.get("fullText", "") or item.get("text", "") or "",
        "likeCount": item.get("likeCount", 0) or item.get("favorite_count", 0) or 0,
        "retweetCount": item.get("retweetCount", 0) or item.get("retweet_count", 0) or 0,
        "replyCount": item.get("replyCount", 0) or item.get("reply_count", 0) or 0,
        "viewCount": item.get("viewCount", 0) or item.get("views", 0) or 0,
        "createdAt": item.get("createdAt", "") or item.get("created_at", ""),
        "author": {
            "userName": author.get("userName", "") or author.get("screen_name", ""),
            "name": author.get("name", ""),
        },
        "url": url,
    }


def apify_input(term, max_tweets):
    return {"searchTerms": [term], "maxTweets": max_tweets, "maxItems": max_tweets,
            "searchMode": "live"}


def fetch_apify(term, max_tweets, token, max_cost_usd, timeout_s):
    body = apify_input(term, max_tweets)
    items = apify_common.run_actor(
        APIFY_ACTOR, body, max_cost_usd=max_cost_usd, timeout_s=timeout_s, tok=token)
    return [normalize(it) for it in items] if isinstance(items, list) else []


def fetch_keyless(term, max_tweets):
    script = os.path.join(HERE, "x_scrape.mjs")
    try:
        out = subprocess.run(
            ["node", script, "--term", term, "--max", str(max_tweets)],
            capture_output=True, text=True, timeout=240,
        )
    except FileNotFoundError:
        sys.exit("ERROR: node not found. Keyless X path needs node + Playwright "
                 "(`npx playwright install chromium`), or set APIFY_API_TOKEN.")
    if out.returncode != 0:
        sys.exit(f"ERROR: keyless X scrape failed (X is login-walled): {out.stderr.strip()[:400]}")
    try:
        items = json.loads(out.stdout or "[]")
    except json.JSONDecodeError:
        sys.exit(f"ERROR: keyless X scrape returned non-JSON: {out.stdout[:200]}")
    return [normalize(it) for it in items]


def main():
    ap = argparse.ArgumentParser(description="Search X posts with native date filtering.")
    ap.add_argument("--query", required=True, help="search query (since:/until: appended automatically)")
    ap.add_argument("--since", default="", help="start date YYYY-MM-DD (inclusive)")
    ap.add_argument("--until", default="", help="end date YYYY-MM-DD (exclusive)")
    ap.add_argument("--max-posts", type=int, default=50)
    ap.add_argument("--keywords", default="", help="comma-separated OR client-side filter")
    ap.add_argument("--use-apify", action="store_true", help="force Apify path (auto when token set)")
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

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    use_apify = args.use_apify or bool(token)
    if args.use_apify and not token:
        sys.exit("ERROR: --use-apify requested but APIFY_API_TOKEN is not set.")

    term = build_term(args.query, args.since, args.until)

    # COST GATE (Apify path only). --estimate-only never spends; spend needs --yes.
    if use_apify and args.estimate_only:
        est = apify_common.estimate(
            APIFY_ACTOR, apify_input(term, args.max_posts),
            max_cost_usd=args.max_cost_usd, timeout_s=args.apify_timeout,
            items_hint=args.max_posts, label="x-mention-tracker")
        json.dump(est, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if use_apify and not args.yes:
        sys.exit("ERROR: cost gate — the Apify path spends credits. Re-run with --yes to "
                 "confirm (and --max-cost-usd to cap), or --estimate-only to preview. The "
                 "keyless Playwright path runs without --yes when no token is set.")

    if use_apify:
        try:
            items = fetch_apify(term, args.max_posts, token,
                                args.max_cost_usd, args.apify_timeout)
        except apify_common.CostGateError as e:
            sys.exit(f"ERROR: cost gate: {e}")
        except apify_common.ApifyError as e:
            sys.exit(f"ERROR: Apify: {e}")
    else:
        items = fetch_keyless(term, args.max_posts)

    # dedup by tweet id
    seen, deduped = set(), []
    for it in items:
        k = it["id"] or it["url"]
        if k in seen:
            continue
        seen.add(k)
        deduped.append(it)
    items = deduped

    keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    if keywords:
        items = [it for it in items if any(k in (it["text"]).lower() for k in keywords)]

    items.sort(key=lambda it: it["likeCount"], reverse=True)
    items = items[: args.max_posts]

    if args.output == "summary":
        if not items:
            print("No tweets found.")
            return
        for it in items:
            a = it["author"]
            print(f"[{it['likeCount']:>5}♥ {it['retweetCount']:>4}rt] @{a['userName']}: {it['text'][:160]}")
            print(f"        {it['url']}  {it['createdAt']}")
    else:
        json.dump(items, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
