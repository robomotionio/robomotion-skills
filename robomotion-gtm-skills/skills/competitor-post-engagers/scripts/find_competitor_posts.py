#!/usr/bin/env python3
"""find_competitor_posts.py — discover a competitor's recent LinkedIn post URLs.

Engine step 0: feed extract_engagers.py. Given a competitor company or profile LinkedIn
URL, list its recent posts so you can pick the top performers to mine for engagers.
Ranks posts locally by engagement so you spend the engager-extraction budget only on the
posts whose audience is biggest (cost control — never one extract call per post blindly).

Source priority:
  1. Apify profile-posts actor (APIFY_API_TOKEN) — primary. Same cost-confirm discipline:
     --estimate-only prints projected cost; --yes required to actually spend.
  2. Web-search degrade — if no Apify token, emit a ready-to-run search query string the
     host agent can run with its own web-search to surface recent post URLs by hand.

Stdlib only.

Output (JSON): [{post_url, posted_at?, like_count?, comment_count?, engagement, competitor}]
sorted by engagement desc, capped at --top-n.

Examples:
  find_competitor_posts.py --profile-url "https://linkedin.com/company/acme" \
      --competitor Acme --days-back 30 --top-n 3 --estimate-only
  find_competitor_posts.py --profile-url "https://linkedin.com/company/acme" \
      --competitor Acme --top-n 3 --yes --output posts.json
  # No Apify token -> prints a web-search query to run by hand:
  find_competitor_posts.py --profile-url "https://linkedin.com/company/acme" --competitor Acme
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

APIFY_BASE = "https://api.apify.com/v2"
DEFAULT_ACTOR = "harvestapi~linkedin-profile-posts"
DEFAULT_PRICE_PER_1K = 2.0


def apify_req(url, token, method="GET", body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(
        f"{url}{sep}token={token}", data=data, method=method,
        headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apify {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def engagement(p):
    return (p.get("likeCount") or p.get("reactionCount") or p.get("likes")
            or p.get("numLikes") or 0) + \
           (p.get("commentCount") or p.get("comments") or p.get("numComments") or 0)


def web_search_degrade(profile_url, competitor, days_back):
    """No Apify token: hand the agent a search query to surface recent post URLs."""
    handle = profile_url.rstrip("/").split("/")[-1]
    query = (f'site:linkedin.com/posts "{competitor or handle}" '
             f'(recent OR latest) -inurl:company')
    out = {
        "_degrade": "web-search",
        "instruction": ("No APIFY_API_TOKEN set. Run this query with your web-search tool, "
                        "then pass the discovered /posts/ URLs straight to extract_engagers.py "
                        "--post-urls. Prefer posts from the last "
                        f"{days_back} days with visibly high reactions/comments."),
        "search_query": query,
        "profile_url": profile_url,
        "competitor": competitor,
    }
    print(json.dumps(out, indent=2))
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(description="Discover a competitor's recent LinkedIn post URLs.")
    ap.add_argument("--profile-url", required=True, help="competitor company or profile LinkedIn URL")
    ap.add_argument("--competitor", default="", help="competitor name tag for the output rows")
    ap.add_argument("--days-back", type=int, default=30, help="recency window (default 30)")
    ap.add_argument("--top-n", type=int, default=3, help="keep top N posts by engagement")
    ap.add_argument("--actor", default=DEFAULT_ACTOR, help=f"Apify actor (default {DEFAULT_ACTOR})")
    ap.add_argument("--max-posts", type=int, default=50, help="posts to scan before ranking")
    ap.add_argument("--estimate-only", action="store_true", help="print projected cost, no spend")
    ap.add_argument("--yes", action="store_true", help="confirm Apify spend")
    ap.add_argument("--price-per-1k", type=float, default=DEFAULT_PRICE_PER_1K)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not token:
        web_search_degrade(args.profile_url, args.competitor, args.days_back)

    actor = args.actor.replace("/", "~")
    est_cost = (args.max_posts / 1000.0) * args.price_per_1k
    print(f"[cost-estimate] actor={actor} scan~{args.max_posts} posts "
          f"~${est_cost:.4f} (estimate only)", file=sys.stderr)
    if args.estimate_only:
        print(json.dumps({"actor": actor, "scan_posts": args.max_posts,
                          "est_cost_usd": round(est_cost, 4)}, indent=2))
        sys.exit(0)
    if not args.yes:
        sys.exit("REFUSED: Apify run would spend credits. Re-run with --yes (or --estimate-only). "
                 "No spend made.")

    actor_input = {"profileUrls": [args.profile_url], "urls": [args.profile_url],
                   "maxPosts": args.max_posts, "postedLimit": f"{args.days_back}d"}
    run = apify_req(f"{APIFY_BASE}/acts/{actor}/runs", token, "POST", actor_input)
    run_id = (run.get("data") or {}).get("id")
    dataset_id = (run.get("data") or {}).get("defaultDatasetId")
    if not run_id:
        sys.exit(f"ERROR: Apify did not return a run id: {json.dumps(run)[:300]}")
    for _ in range(120):
        time.sleep(5)
        st = apify_req(f"{APIFY_BASE}/actor-runs/{run_id}", token)
        status = ((st.get("data") or {}).get("status") or "").upper()
        dataset_id = (st.get("data") or {}).get("defaultDatasetId") or dataset_id
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
    items = apify_req(f"{APIFY_BASE}/datasets/{dataset_id}/items?clean=true&format=json", token)
    if isinstance(items, dict):
        items = items.get("items") or items.get("data") or []

    posts = []
    for p in items if isinstance(items, list) else []:
        if not isinstance(p, dict):
            continue
        url = p.get("postUrl") or p.get("url") or p.get("postLink") or p.get("link")
        if not url:
            continue
        posts.append({
            "post_url": url,
            "posted_at": p.get("postedAt") or p.get("date") or p.get("publishedAt") or "",
            "like_count": p.get("likeCount") or p.get("reactionCount") or p.get("likes") or 0,
            "comment_count": p.get("commentCount") or p.get("comments") or 0,
            "engagement": engagement(p),
            "competitor": args.competitor,
        })
    posts.sort(key=lambda x: x["engagement"], reverse=True)
    posts = posts[: args.top_n]

    payload = json.dumps(posts, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(posts)} top posts -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
