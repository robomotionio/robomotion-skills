#!/usr/bin/env python3
"""apify_google_ads.py — FALLBACK Google-ads scrape via an Apify actor.

Only use this when the Transparency Center SPA is too anti-bot for the Playwright
path (scrape_google_ads.mjs) in a given run. Runs a Google-ads Apify actor
synchronously and returns its dataset items mapped to the creative schema. Stdlib only.

Auth: APIFY_API_TOKEN (required for THIS fallback only; the primary path is keyless).

Example:
  apify_google_ads.py --domain hubspot.com --max-ads 50 --output ads.json
  apify_google_ads.py --domain stripe.com --actor "scraping-solutions/google-ads-transparency-scraper"
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Default actor; override with --actor if a different Google-ads actor is preferred.
DEFAULT_ACTOR = "scraping-solutions~google-ads-transparency-scraper"


def token():
    t = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not t:
        sys.exit("ERROR: APIFY_API_TOKEN is not set (required only for this Apify fallback path).")
    return t


def run_actor(actor, payload, tok):
    url = (
        f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
        f"?token={urllib.parse.quote(tok)}"
    )
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apify {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def normalize(item, max_ads):
    """Map an actor's dataset item to the google-ad-scraper schema (best-effort)."""
    return {
        "advertiserId": item.get("advertiserId") or item.get("advertiser_id") or "",
        "advertiserName": item.get("advertiserName") or item.get("advertiser") or "",
        "creativeId": item.get("creativeId") or item.get("creative_id") or item.get("id") or "",
        "originalUrl": item.get("originalUrl") or item.get("url") or item.get("adUrl") or "",
        "imageUrl": item.get("imageUrl") or item.get("image") or "",
        "variantFormat": (item.get("format") or item.get("type") or "TEXT").upper(),
        "variantContent": item.get("text") or item.get("content") or item.get("headline") or "",
        "variants": item.get("variants") or [],
        "variantCount": item.get("variantCount") or 1,
        "startDate": item.get("startDate") or item.get("firstShown") or item.get("first_seen") or "",
    }


def main():
    ap = argparse.ArgumentParser(description="Apify fallback: scrape Google ads from the Transparency Center.")
    ap.add_argument("--domain", default="", help="target domain (recommended)")
    ap.add_argument("--company", default="", help="company name (if no domain)")
    ap.add_argument("--max-ads", type=int, default=50, help="cap on ads (default 50)")
    ap.add_argument("--country", default="US", help="geo / library region (default US)")
    ap.add_argument("--actor", default=DEFAULT_ACTOR, help="Apify actor id (override if needed)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    if not args.domain and not args.company:
        ap.error("at least one of --domain or --company is required")

    tok = token()
    query = args.domain or args.company
    payload = {
        "queries": [query],
        "domain": args.domain,
        "region": args.country,
        "maxItems": args.max_ads,
    }
    items = run_actor(args.actor, payload, tok)
    if isinstance(items, dict):
        items = items.get("items", [])
    ads = [normalize(it, args.max_ads) for it in items][: args.max_ads]

    out = json.dumps(ads, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(ads)} ads -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
