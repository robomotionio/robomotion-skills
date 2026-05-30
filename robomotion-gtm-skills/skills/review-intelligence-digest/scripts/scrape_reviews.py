#!/usr/bin/env python3
"""scrape_reviews.py — pull G2 / Capterra / Trustpilot reviews via Apify review actors.

Review sites are JS-heavy and anti-bot, so the Apify actor path is the reliable primary.
Stdlib only (urllib). Deterministic I/O: pick an actor per host, run it via the managed
async run/poll lifecycle in apify_common (start -> poll to terminal with a wall-clock
timeout -> fetch dataset items) under a COST GATE, normalize the dataset into review rows,
filter to the time window. NO LLM — the host agent does the theme clustering, proof-point
extraction, and objection mapping over the emitted JSON.

Auth: APIFY_API_TOKEN env var — OPTIONAL. With a token this is the reliable, cost-gated
scrape path (review sites are anti-bot). WITHOUT a token, use the keyless Playwright
`fetch_page.mjs` degrade path (see SKILL.md) to render review pages directly — partial
coverage, no key. The Apify path is COST-GATED: `--estimate-only` prints the projection
and exits 0; actual spend requires `--yes`; the run aborts if reported usage exceeds
--max-cost-usd or the timeout trips. The Playwright degrade path is not gated.

Per-host default actors (override with --actor):
  g2.com         -> apify/g2-reviews-scraper  (set via --actor if your account differs)
  capterra.com   -> apify/capterra-scraper
  trustpilot.com -> nikita-sevalnev~trustpilot-reviews-scraper

Example:
  scrape_reviews.py \
    --product "Acme"  --url "https://www.trustpilot.com/review/acme.com" \
    --competitor "Rival=https://www.trustpilot.com/review/rival.com" \
    --months 3  --estimate-only
  scrape_reviews.py --product "Acme" --url "..." --yes --max-cost-usd 1.50 --output reviews.json
"""
import argparse
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apify_common  # noqa: E402  (vendored async run/poll + cost gate)

DEFAULT_ACTORS = {
    "g2.com": "apify~g2-reviews-scraper",
    "capterra.com": "apify~capterra-scraper",
    "trustpilot.com": "nikita-sevalnev~trustpilot-reviews-scraper",
}

MAX_ITEMS = 500


def token():
    t = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not t:
        sys.exit(
            "ERROR: APIFY_API_TOKEN is not set. This script is the Apify (paid, reliable) "
            "scrape path. Without a token, use the KEYLESS fallback instead: render each "
            "review page with Playwright via fetch_page.mjs (see SKILL.md) — e.g.\n"
            "  cd <skill>/scripts && npm install && npx playwright install chromium\n"
            "  node fetch_page.mjs --url '<review-page>' --out page.txt\n"
            "then synthesize the digest from the dumped text (partial coverage; review "
            "sites are anti-bot, so set APIFY_API_TOKEN for full, reliable extraction).")
    return t


def host_of(url):
    return urllib.parse.urlparse(url).netloc.lower().replace("www.", "")


def actor_for(url, override):
    if override:
        return override
    h = host_of(url)
    for key, actor in DEFAULT_ACTORS.items():
        if key in h:
            return actor
    return None


def apify_input(start_urls):
    return {"startUrls": [{"url": u} for u in start_urls], "maxItems": MAX_ITEMS}


def run_actor(actor, start_urls, tok, max_cost_usd, timeout_s):
    return apify_common.run_actor(
        actor, apify_input(start_urls), max_cost_usd=max_cost_usd,
        timeout_s=timeout_s, tok=tok)


def first(d, *keys):
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return ""


def parse_date(d):
    s = first(d, "date", "reviewDate", "publishedDate", "createdAt", "time")
    if not s:
        return None
    s = str(s)
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%d %B %Y"):
        try:
            return datetime.strptime(s[:19] if "T" in s else s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # epoch
    try:
        return datetime.fromtimestamp(int(float(s)), tz=timezone.utc)
    except (ValueError, OSError):
        return None


def normalize(item, product, source):
    rating = first(item, "rating", "stars", "score", "overallRating")
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = None
    dt = parse_date(item)
    return {
        "product": product,
        "source": source,
        "rating": rating,
        "title": first(item, "title", "reviewTitle", "headline"),
        "body": first(item, "text", "body", "review", "content", "comment"),
        "pros": first(item, "pros", "likeMost", "likes"),
        "cons": first(item, "cons", "dislikeMost", "dislikes"),
        "reviewer_role": first(item, "reviewerRole", "jobTitle", "position", "role"),
        "reviewer_company": first(item, "reviewerCompany", "company", "companySize"),
        "date": dt.isoformat() if dt else "",
        "_dt": dt,
    }


def scrape_target(label, url, months, actor_override, tok, max_cost_usd, timeout_s):
    actor = actor_for(url, actor_override)
    if not actor:
        sys.exit(f"ERROR: no default Apify actor for host of {url}. Pass --actor "
                 "with the actor id (e.g. owner~actor-name) for this review site.")
    try:
        items = run_actor(actor, [url], tok, max_cost_usd, timeout_s)
    except apify_common.CostGateError as e:
        sys.exit(f"ERROR: cost gate: {e}")
    except apify_common.ApifyError as e:
        sys.exit(f"ERROR: Apify: {e}")
    cutoff = None
    if months and months > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(days=30 * months)
    rows = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict):
            continue
        row = normalize(it, label, host_of(url))
        if cutoff and row["_dt"] and row["_dt"] < cutoff:
            continue
        row.pop("_dt", None)
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser(
        description="Scrape G2/Capterra/Trustpilot reviews via Apify actors (keyed).")
    ap.add_argument("--product", required=True, help="your product name (label)")
    ap.add_argument("--url", action="append", default=[], required=True,
                    help="your review page URL (repeatable)")
    ap.add_argument("--competitor", action="append", default=[],
                    help='competitor as "Name=https://review-url" (repeatable)')
    ap.add_argument("--months", type=int, default=3,
                    help="time window in months; 0 = all (default 3)")
    ap.add_argument("--actor", default="",
                    help="override Apify actor id (owner~actor) for non-default sites")
    ap.add_argument("--estimate-only", action="store_true",
                    help="Apify cost gate: print projected cost/limits per target and exit 0 (no spend)")
    ap.add_argument("--yes", action="store_true",
                    help="Apify cost gate: confirm actual spend (required to start any run)")
    ap.add_argument("--max-cost-usd", type=float, default=2.0,
                    help="Apify cost gate: abort a target's run if reported usage exceeds this "
                         "(default 2.00; this composite may scrape several targets)")
    ap.add_argument("--apify-timeout", type=int, default=600,
                    help="Apify run/poll wall-clock timeout in seconds per target (default 600)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    tok = token()

    # assemble every (label, url) target so the gate can preview/guard each one
    targets = [(args.product, u) for u in args.url]
    for spec in args.competitor:
        if "=" not in spec:
            sys.exit(f"ERROR: --competitor must be 'Name=URL', got: {spec}")
        name, _, u = spec.partition("=")
        targets.append((name.strip(), u.strip()))

    # COST GATE (Apify path only). --estimate-only never spends; spend needs --yes.
    if args.estimate_only:
        ests = []
        for label, u in targets:
            actor = actor_for(u, args.actor)
            ests.append(apify_common.estimate(
                actor or "(no default actor — pass --actor)", apify_input([u]),
                max_cost_usd=args.max_cost_usd, timeout_s=args.apify_timeout,
                items_hint=MAX_ITEMS, label=f"{label} @ {host_of(u)}"))
        json.dump({"estimate_only": True, "targets": ests,
                   "max_cost_usd_per_target": args.max_cost_usd}, sys.stdout,
                  ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if not args.yes:
        sys.exit("ERROR: cost gate — the Apify review scrape spends credits (some review "
                 "actors are pay-per-result). Re-run with --yes to confirm (and "
                 "--max-cost-usd to cap per target), or --estimate-only to preview. The "
                 "fragile Playwright fetch_page.mjs degrade path (see SKILL.md) is not gated.")

    all_rows = []
    for label, u in targets:
        all_rows.extend(scrape_target(label, u, args.months, args.actor, tok,
                                      args.max_cost_usd, args.apify_timeout))

    out = json.dumps(all_rows, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(all_rows)} reviews -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
