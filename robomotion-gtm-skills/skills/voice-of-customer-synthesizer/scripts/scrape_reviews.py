#!/usr/bin/env python3
"""scrape_reviews.py — pull G2 / Capterra / Trustpilot reviews via Apify review actors.

Review sites are JS-heavy and anti-bot, so the Apify actor path is the reliable primary.
Stdlib only (urllib). Deterministic I/O: pick an actor per host, run it sync, normalize
the dataset into review rows, filter to the time window. NO LLM — the host agent does the
theme clustering, proof-point extraction, and objection mapping over the emitted JSON.

Auth: APIFY_API_TOKEN env var (required — review sites block direct scraping).

Per-host default actors (override with --actor):
  g2.com         -> apify/g2-reviews-scraper  (set via --actor if your account differs)
  capterra.com   -> apify/capterra-scraper
  trustpilot.com -> nikita-sevalnev~trustpilot-reviews-scraper

Example:
  scrape_reviews.py \
    --product "Acme"  --url "https://www.trustpilot.com/review/acme.com" \
    --competitor "Rival=https://www.trustpilot.com/review/rival.com" \
    --months 3  --output reviews.json
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

RUN_URL = ("https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
           "?token={token}")

DEFAULT_ACTORS = {
    "g2.com": "apify~g2-reviews-scraper",
    "capterra.com": "apify~capterra-scraper",
    "trustpilot.com": "nikita-sevalnev~trustpilot-reviews-scraper",
}


def token():
    t = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not t:
        sys.exit("ERROR: APIFY_API_TOKEN is not set (required — review sites are "
                 "anti-bot; the Apify actor is the reliable scrape path).")
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


def run_actor(actor, start_urls, tok):
    url = RUN_URL.format(actor=actor, token=urllib.parse.quote(tok))
    body = {"startUrls": [{"url": u} for u in start_urls], "maxItems": 500}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:300]
        if e.code == 402:
            sys.exit("ERROR: Apify quota/credit exceeded (HTTP 402).")
        sys.exit(f"ERROR: Apify actor '{actor}' HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"ERROR: network calling Apify: {e}")


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


def scrape_target(label, url, months, actor_override, tok):
    actor = actor_for(url, actor_override)
    if not actor:
        sys.exit(f"ERROR: no default Apify actor for host of {url}. Pass --actor "
                 "with the actor id (e.g. owner~actor-name) for this review site.")
    items = run_actor(actor, [url], tok)
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
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    tok = token()
    all_rows = []
    for u in args.url:
        all_rows.extend(scrape_target(args.product, u, args.months, args.actor, tok))
    for spec in args.competitor:
        if "=" not in spec:
            sys.exit(f"ERROR: --competitor must be 'Name=URL', got: {spec}")
        name, _, u = spec.partition("=")
        all_rows.extend(scrape_target(name.strip(), u.strip(), args.months, args.actor, tok))

    out = json.dumps(all_rows, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(all_rows)} reviews -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
