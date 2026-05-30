#!/usr/bin/env python3
"""ph_scraper.py — Scrape trending Product Hunt launches for a time window.

Two paths, auto-selected:
  * APIFY (when APIFY_API_TOKEN set or --use-apify): a Product Hunt actor via the managed
    async run/poll lifecycle in apify_common (start -> poll to terminal with a wall-clock
    timeout -> fetch dataset items), guarded by a COST GATE. Reliable, costs Apify credits.
  * KEYLESS degrade: Product Hunt is JS-heavy and anti-bot, so the keyless path is the
    bundled Playwright scraper (scripts/ph_scrape.mjs). This Python wrapper shells out to
    it when no Apify token is present. Lower reliability/volume.

The Apify path enforces a cost gate: `--estimate-only` prints the projection and exits 0;
actual spend requires `--yes`; the run aborts if reported usage exceeds --max-cost-usd or
the timeout trips. The KEYLESS Playwright degrade is never gated.

Both emit one normalized schema. Stdlib only (the keyless path needs node + Playwright;
see SKILL.md). Implements the robomotion-gtm-skills `product-hunt-scraper` contract.

Examples:
  ph_scraper.py --time-period weekly --max-products 50
  ph_scraper.py --time-period daily --keywords "ai,agent" --output summary
  APIFY_API_TOKEN=xxx ph_scraper.py --time-period monthly --use-apify --estimate-only
  APIFY_API_TOKEN=xxx ph_scraper.py --time-period monthly --use-apify --yes --max-cost-usd 0.50
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apify_common  # noqa: E402  (vendored async run/poll + cost gate)

APIFY_ACTOR = os.environ.get("APIFY_PH_ACTOR", "tri_angle~product-hunt-scraper")
HERE = os.path.dirname(os.path.abspath(__file__))


def normalize(item):
    return {
        "name": item.get("name", "") or item.get("title", ""),
        "tagline": item.get("tagline", "") or item.get("description", ""),
        "description": item.get("description", "") or item.get("tagline", ""),
        "url": item.get("url", "") or item.get("website", "") or item.get("link", ""),
        "upvotes": item.get("upvotes", 0) or item.get("votesCount", 0) or item.get("votes", 0) or 0,
    }


def apify_input(period, max_products):
    return {"period": period, "maxItems": max_products}


def fetch_apify(period, max_products, token, max_cost_usd, timeout_s):
    body = apify_input(period, max_products)
    items = apify_common.run_actor(
        APIFY_ACTOR, body, max_cost_usd=max_cost_usd, timeout_s=timeout_s, tok=token)
    return [normalize(it) for it in items] if isinstance(items, list) else []


def fetch_keyless(period, max_products):
    script = os.path.join(HERE, "ph_scrape.mjs")
    try:
        out = subprocess.run(
            ["node", script, "--period", period, "--max", str(max_products)],
            capture_output=True, text=True, timeout=240,
        )
    except FileNotFoundError:
        sys.exit("ERROR: node not found. Keyless PH path needs node + Playwright "
                 "(`npx playwright install chromium`), or set APIFY_API_TOKEN.")
    if out.returncode != 0:
        sys.exit(f"ERROR: keyless PH scrape failed: {out.stderr.strip()[:400]}")
    try:
        items = json.loads(out.stdout or "[]")
    except json.JSONDecodeError:
        sys.exit(f"ERROR: keyless PH scrape returned non-JSON: {out.stdout[:200]}")
    return [normalize(it) for it in items]


def main():
    ap = argparse.ArgumentParser(description="Scrape trending Product Hunt launches.")
    ap.add_argument("--time-period", default="weekly", choices=["daily", "weekly", "monthly"])
    ap.add_argument("--max-products", type=int, default=50)
    ap.add_argument("--keywords", default="", help="comma-separated OR filter on name+tagline+description")
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

    # COST GATE (Apify path only). --estimate-only never spends; spend needs --yes.
    if use_apify and args.estimate_only:
        est = apify_common.estimate(
            APIFY_ACTOR, apify_input(args.time_period, args.max_products),
            max_cost_usd=args.max_cost_usd, timeout_s=args.apify_timeout,
            items_hint=args.max_products, label="product-hunt-scraper")
        json.dump(est, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if use_apify and not args.yes:
        sys.exit("ERROR: cost gate — the Apify path spends credits. Re-run with --yes to "
                 "confirm (and --max-cost-usd to cap), or --estimate-only to preview. The "
                 "keyless Playwright path runs without --yes when no token is set.")

    if use_apify:
        try:
            items = fetch_apify(args.time_period, args.max_products, token,
                                args.max_cost_usd, args.apify_timeout)
        except apify_common.CostGateError as e:
            sys.exit(f"ERROR: cost gate: {e}")
        except apify_common.ApifyError as e:
            sys.exit(f"ERROR: Apify: {e}")
    else:
        items = fetch_keyless(args.time_period, args.max_products)

    keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    if keywords:
        def keep(it):
            blob = (it["name"] + " " + it["tagline"] + " " + it["description"]).lower()
            return any(k in blob for k in keywords)
        items = [it for it in items if keep(it)]

    items.sort(key=lambda it: it["upvotes"], reverse=True)
    items = items[: args.max_products]

    if args.output == "summary":
        if not items:
            print("No Product Hunt launches found.")
            return
        for it in items:
            print(f"[{it['upvotes']:>5}^] {it['name']} — {it['tagline']}")
            print(f"        {it['url']}")
    else:
        json.dump(items, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
