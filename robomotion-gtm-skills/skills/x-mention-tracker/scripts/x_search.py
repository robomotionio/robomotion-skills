#!/usr/bin/env python3
"""Search public X posts with native since and until operators.

Two paths, auto-selected:
  * Apify: a selected Tweet Actor with a managed run and cost gate.
  * Keyless: a best-effort Playwright scraper behind X's login wall.

The Apify path requires --yes before spending. It sends a server-side charge cap,
then aborts on a reported budget breach or timeout. Estimate mode never starts a run.

Both paths emit one normalized schema.

Examples:
  x_search.py --query "robomotion" --since 2025-01-01 --until 2025-02-01
  x_search.py --query "from:levelsio" --max-posts 30 --output summary
  APIFY_API_TOKEN=xxx x_search.py --query "rpa" --use-apify --estimate-only
  APIFY_API_TOKEN=xxx x_search.py --query "rpa" --use-apify --yes --max-cost-usd 0.50
"""
import argparse
from datetime import date
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apify_common  # noqa: E402  (vendored async run/poll + cost gate)

DEFAULT_APIFY_ACTOR = "apidojo~tweet-scraper"
XQUIK_APIFY_ACTOR = "xquik~x-tweet-scraper"
APIFY_ACTOR = os.environ.get(
    "APIFY_TWITTER_ACTOR",
    DEFAULT_APIFY_ACTOR,
)
HERE = os.path.dirname(os.path.abspath(__file__))


def positive_int(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def positive_amount(value):
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a finite positive number")
    return parsed


def iso_date(value):
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from error


def build_term(query, since, until):
    term = query.strip()
    if not term:
        raise ValueError("query cannot be empty")
    if since:
        term += f" since:{since}"
    if until:
        term += f" until:{until}"
    return term.strip()


def normalize(item):
    author = item.get("author") or {}
    if isinstance(author, str):
        author = {"userName": author}
    tid = str(
        item.get("id")
        or item.get("restId")
        or item.get("id_str")
        or item.get("tweetId")
        or ""
    )
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


def is_xquik_actor(actor_id):
    return actor_id.replace("/", "~", 1) == XQUIK_APIFY_ACTOR


def apify_input(term, max_tweets, actor_id=APIFY_ACTOR):
    if not is_xquik_actor(actor_id):
        return {
            "searchTerms": [term],
            "maxTweets": max_tweets,
            "maxItems": max_tweets,
            "searchMode": "live",
        }

    return {
        "searchTerms": [term],
        "maxItems": max_tweets,
        "queryType": "Latest",
        "outputVariant": "rich",
        "fieldStyle": "camelCase",
        "includeSearchTerms": True,
    }


def fetch_apify(term, max_tweets, token, max_cost_usd, timeout_s):
    body = apify_input(term, max_tweets, APIFY_ACTOR)
    items = apify_common.run_actor(
        APIFY_ACTOR,
        body,
        max_cost_usd=max_cost_usd,
        timeout_s=timeout_s,
        tok=token,
    )
    posts = []
    for item in items if isinstance(items, list) else []:
        result_type = item.get("resultType") if isinstance(item, dict) else None
        if result_type == "diagnostic":
            status = item.get("status", "unknown")
            message = item.get("message", "No diagnostic message returned.")
            print(f"Actor diagnostic ({status}): {message}", file=sys.stderr)
            continue
        if result_type == "run-report" or not isinstance(item, dict):
            continue
        posts.append(normalize(item))
    return posts


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
    ap = argparse.ArgumentParser(
        description="Search X posts with native date filtering."
    )
    ap.add_argument(
        "--query",
        required=True,
        help="search query (since:/until: appended automatically)",
    )
    ap.add_argument(
        "--since",
        type=iso_date,
        default="",
        help="start date YYYY-MM-DD (inclusive)",
    )
    ap.add_argument(
        "--until",
        type=iso_date,
        default="",
        help="end date YYYY-MM-DD (exclusive)",
    )
    ap.add_argument("--max-posts", type=positive_int, default=50)
    ap.add_argument(
        "--keywords",
        default="",
        help="comma-separated OR client-side filter",
    )
    ap.add_argument(
        "--use-apify",
        action="store_true",
        help="force Apify path (auto when token set)",
    )
    ap.add_argument(
        "--estimate-only",
        action="store_true",
        help="Apify cost gate: print projected limits and exit without spending",
    )
    ap.add_argument(
        "--yes",
        action="store_true",
        help="Apify cost gate: confirm spend before starting a run",
    )
    ap.add_argument(
        "--max-cost-usd",
        type=positive_amount,
        default=1.0,
        help="Apify cost gate: hard maximum charge (default 1.00)",
    )
    ap.add_argument(
        "--apify-timeout",
        type=positive_int,
        default=600,
        help="Apify run wall-clock timeout in seconds (default 600)",
    )
    ap.add_argument("--output", default="json", choices=["json", "summary"])
    args = ap.parse_args()

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    use_apify = args.use_apify or args.estimate_only or bool(token)
    if use_apify and not token and not args.estimate_only:
        sys.exit("ERROR: --use-apify requested but APIFY_API_TOKEN is not set.")

    if args.since and args.until and args.since >= args.until:
        ap.error("--since must be earlier than --until")
    try:
        term = build_term(args.query, args.since, args.until)
    except ValueError as error:
        ap.error(str(error))

    # COST GATE (Apify path only). --estimate-only never spends; spend needs --yes.
    if use_apify and args.estimate_only:
        est = apify_common.estimate(
            APIFY_ACTOR,
            apify_input(term, args.max_posts, APIFY_ACTOR),
            max_cost_usd=args.max_cost_usd,
            timeout_s=args.apify_timeout,
            items_hint=args.max_posts,
            label="x-mention-tracker",
        )
        json.dump(est, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if use_apify and not args.yes:
        sys.exit(
            "ERROR: the Apify path spends credits. Re-run with --yes "
            "and --max-cost-usd, or use --estimate-only. "
            "The keyless path needs no confirmation."
        )

    if use_apify:
        try:
            items = fetch_apify(
                term,
                args.max_posts,
                token,
                args.max_cost_usd,
                args.apify_timeout,
            )
        except apify_common.CostGateError as error:
            sys.exit(f"ERROR: cost gate: {error}")
        except apify_common.ApifyError as error:
            sys.exit(f"ERROR: Apify: {error}")
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
            print(
                f"[{it['likeCount']:>5}♥ {it['retweetCount']:>4}rt] "
                f"@{a['userName']}: {it['text'][:160]}"
            )
            print(f"        {it['url']}  {it['createdAt']}")
    else:
        json.dump(items, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
