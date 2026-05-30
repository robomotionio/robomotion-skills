#!/usr/bin/env python3
"""review_scraper.py — Scrape product reviews from G2, Capterra, or Trustpilot.

Single skill, platform dispatch. G2/Trustpilot take a review-page --url; Capterra takes
a --company-name. Two paths, auto-selected:
  * APIFY (when APIFY_API_TOKEN set or --use-apify): a per-platform review actor run via
    the managed async run/poll lifecycle in apify_common (start -> poll to terminal with a
    wall-clock timeout -> fetch dataset items), guarded by a COST GATE. Some actors are
    pay-per-result, so the gate matters.
  * KEYLESS degrade: review sites are JS + anti-bot, so the keyless path is the bundled
    Playwright scraper (scripts/review_scrape.mjs). Lower reliability/volume.

The Apify path enforces a cost gate: `--estimate-only` prints the projection and exits 0;
actual spend requires `--yes`; the run aborts if reported usage exceeds --max-cost-usd or
the timeout trips. The KEYLESS Playwright degrade is never gated.

Reviews are normalized into a common schema (platform extras preserved). Stdlib only
(keyless path needs node + Playwright; see SKILL.md).
Implements the robomotion-gtm-skills `review-site-scraper` contract.

Examples:
  review_scraper.py --platform g2 --url https://www.g2.com/products/foo/reviews --max-reviews 50
  review_scraper.py --platform capterra --company-name "Foo App" --output summary
  review_scraper.py --platform trustpilot --url https://www.trustpilot.com/review/foo.com --days 90
  APIFY_API_TOKEN=xxx review_scraper.py --platform g2 --url <url> --use-apify --estimate-only
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apify_common  # noqa: E402  (vendored async run/poll + cost gate)

HERE = os.path.dirname(os.path.abspath(__file__))

# Per-platform Apify actor slugs (overridable via env).
ACTORS = {
    "g2": os.environ.get("APIFY_G2_ACTOR", "jupri~g2-reviews-scraper"),
    "capterra": os.environ.get("APIFY_CAPTERRA_ACTOR", "jupri~capterra-scraper"),
    "trustpilot": os.environ.get("APIFY_TRUSTPILOT_ACTOR", "nikita-sviridenko~trustpilot-reviews-scraper"),
}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def normalize(platform, item):
    text = (item.get("text") or item.get("review") or item.get("body")
            or item.get("comment") or "")
    rating = item.get("rating") or item.get("score") or item.get("stars")
    author = (item.get("author") or item.get("reviewer") or item.get("name")
              or item.get("userName") or "")
    if isinstance(author, dict):
        author = author.get("name", "")
    date = (item.get("date") or item.get("publishedDate") or item.get("reviewDate")
            or item.get("createdAt") or "")
    url = item.get("url") or item.get("reviewUrl") or item.get("link") or ""
    rid = (item.get("id") or item.get("reviewId") or url
           or hashlib.sha1(text[:200].encode("utf-8")).hexdigest())
    rec = {
        "platform": platform,
        "id": str(rid),
        "text": text,
        "rating": _num(rating),
        "author": author,
        "date": date,
        "url": url,
    }
    if platform == "g2":
        rec.update({
            "author_title": item.get("authorTitle", "") or item.get("title", ""),
            "author_company": item.get("authorCompany", "") or item.get("company", ""),
            "company_size": item.get("companySize", ""),
            "industry": item.get("industry", ""),
        })
    elif platform == "capterra":
        rec.update({
            "ease_of_use": _num(item.get("easeOfUse")),
            "customer_service": _num(item.get("customerService")),
            "features": _num(item.get("features")),
            "job_title": item.get("jobTitle", "") or item.get("title", ""),
            "industry": item.get("industry", ""),
        })
    elif platform == "trustpilot":
        rec.update({
            "experienced_date": item.get("experiencedDate", "") or item.get("dateOfExperience", ""),
            "likes": item.get("likes", 0) or item.get("numberOfLikes", 0) or 0,
            "input_source": item.get("inputSource", "") or item.get("source", ""),
        })
    return rec


def apify_input(platform, url, company, max_reviews):
    if platform == "capterra":
        return {"query": company, "maxItems": max_reviews, "maxReviews": max_reviews}
    return {"startUrls": [{"url": url}], "maxItems": max_reviews, "maxReviews": max_reviews}


def fetch_apify(platform, url, company, max_reviews, token, max_cost_usd, timeout_s):
    actor = ACTORS[platform]
    body = apify_input(platform, url, company, max_reviews)
    items = apify_common.run_actor(
        actor, body, max_cost_usd=max_cost_usd, timeout_s=timeout_s, tok=token)
    return [normalize(platform, it) for it in items] if isinstance(items, list) else []


def fetch_keyless(platform, url, company, max_reviews):
    script = os.path.join(HERE, "review_scrape.mjs")
    cmd = ["node", script, "--platform", platform, "--max", str(max_reviews)]
    if url:
        cmd += ["--url", url]
    if company:
        cmd += ["--company", company]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    except FileNotFoundError:
        sys.exit("ERROR: node not found. Keyless review path needs node + Playwright "
                 "(`npx playwright install chromium`), or set APIFY_API_TOKEN.")
    if out.returncode != 0:
        sys.exit(f"ERROR: keyless review scrape failed: {out.stderr.strip()[:400]}")
    try:
        items = json.loads(out.stdout or "[]")
    except json.JSONDecodeError:
        sys.exit(f"ERROR: keyless review scrape returned non-JSON: {out.stdout[:200]}")
    return [normalize(platform, it) for it in items]


def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y/%m/%d", "%B %d, %Y", "%d %B %Y"):
        try:
            return datetime.strptime(s[:19] if "T" in s else s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(description="Scrape G2/Capterra/Trustpilot reviews (platform dispatch).")
    ap.add_argument("--platform", required=True, choices=["g2", "capterra", "trustpilot"])
    ap.add_argument("--url", default="", help="review-page URL (required for g2 / trustpilot)")
    ap.add_argument("--company-name", dest="company", default="", help="company/product name (required for capterra)")
    ap.add_argument("--max-reviews", type=int, default=50)
    ap.add_argument("--keywords", default="", help="comma-separated OR client-side filter on review text")
    ap.add_argument("--days", type=int, default=0, help="only reviews from last N days (0 = no limit)")
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

    # input validation per dispatch
    if args.platform in ("g2", "trustpilot") and not args.url:
        sys.exit(f"ERROR: --url is required for platform '{args.platform}'.")
    if args.platform == "capterra" and not args.company:
        sys.exit("ERROR: --company-name is required for platform 'capterra'.")

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    use_apify = args.use_apify or bool(token)
    if args.use_apify and not token:
        sys.exit("ERROR: --use-apify requested but APIFY_API_TOKEN is not set.")

    # COST GATE (Apify path only). --estimate-only never spends; spend needs --yes.
    if use_apify and args.estimate_only:
        # Trustpilot/Capterra actors are pay-per-result (~$0.20-0.50/product); flag a hint.
        est = apify_common.estimate(
            ACTORS[args.platform],
            apify_input(args.platform, args.url, args.company, args.max_reviews),
            max_cost_usd=args.max_cost_usd, timeout_s=args.apify_timeout,
            items_hint=args.max_reviews, label=f"review-site-scraper:{args.platform}")
        json.dump(est, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if use_apify and not args.yes:
        sys.exit("ERROR: cost gate — the Apify path spends credits (some review actors are "
                 "pay-per-result). Re-run with --yes to confirm (and --max-cost-usd to cap), "
                 "or --estimate-only to preview. The keyless Playwright path runs without "
                 "--yes when no token is set.")

    if use_apify:
        try:
            items = fetch_apify(args.platform, args.url, args.company, args.max_reviews,
                                token, args.max_cost_usd, args.apify_timeout)
        except apify_common.CostGateError as e:
            sys.exit(f"ERROR: cost gate: {e}")
        except apify_common.ApifyError as e:
            sys.exit(f"ERROR: Apify: {e}")
    else:
        items = fetch_keyless(args.platform, args.url, args.company, args.max_reviews)

    keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    if keywords:
        items = [it for it in items if any(k in (it["text"] or "").lower() for k in keywords)]

    if args.days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
        kept = []
        for it in items:
            d = parse_date(it.get("date", "") or it.get("experienced_date", ""))
            if d is None or d >= cutoff:
                kept.append(it)
        items = kept

    items = items[: args.max_reviews]

    if args.output == "summary":
        if not items:
            print("No reviews found.")
            return
        for it in items:
            r = it.get("rating")
            print(f"[{r if r is not None else '?'}★] {it.get('author','')}  {it.get('date','')}")
            print(f"    {(it.get('text','') or '')[:200]}")
            if it.get("url"):
                print(f"    {it['url']}")
    else:
        json.dump(items, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
