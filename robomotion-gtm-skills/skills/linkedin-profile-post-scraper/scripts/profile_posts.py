#!/usr/bin/env python3
"""profile_posts.py — scrape recent posts from specific LinkedIn profiles.

Primary path: Apify LinkedIn profile-posts actor (cookieless) when APIFY_API_TOKEN is
set. Keyless degrade: when APIFY_API_TOKEN is unset, fall back to the bundled Playwright
scraper (li_profile_posts_playwright.mjs) using a LinkedIn `li_at` session cookie (env
LI_AT). Both paths feed the same normalize()/filter pipeline; if neither a token nor a
cookie is available the script exits with instructions.

Date filtering and keyword filtering are done client-side (LinkedIn has no server-side
date filter). Deterministic — no LLM. Stdlib only (the keyless path shells out to
node/Playwright).

Examples:
  profile_posts.py --profiles "https://www.linkedin.com/in/x" --max-posts 20 --days 30
  profile_posts.py --profiles "u1,u2" --keywords "ai,automation" --output summary
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

DEFAULT_ACTOR = "apimaestro~linkedin-profile-posts"
APIFY_BASE = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
PROFILE_RE = re.compile(r"^https?://(www\.)?linkedin\.com/in/[^/?#]+/?$", re.I)


def http_post(url, body, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 method="POST", headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
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


def parse_dt(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def normalize(p, author_url):
    return {
        "author": p.get("authorName") or p.get("author", "") or author_url,
        "author_url": author_url,
        "text": p.get("text", ""),
        "posted_at": p.get("postedAtISO") or p.get("date") or p.get("publishedAt", ""),
        "reactions": p.get("numLikes") or p.get("reactions") or p.get("likesCount") or 0,
        "comments": p.get("numComments") or p.get("commentsCount") or 0,
        "shares": p.get("numShares") or p.get("sharesCount") or 0,
        "url": p.get("url") or p.get("postUrl", ""),
    }


def fetch_apify(profiles, max_posts, actor, token):
    url = APIFY_BASE.format(actor=urllib.parse.quote(actor, safe="~")) + "?token=" + token
    out = []
    for prof in profiles:
        body = {"profileUrl": prof, "username": prof, "urls": [prof],
                "maxPosts": max_posts, "limit": max_posts}
        try:
            data = http_post(url, body)
        except Exception as e:
            print(f"WARN: Apify failed for {prof}: {e}", file=sys.stderr)
            continue
        rows = data if isinstance(data, list) else data.get("items", [])
        for p in rows[:max_posts]:
            out.append(normalize(p, prof))
        time.sleep(0.3)
    return out


def fetch_playwright(profiles, max_posts):
    """Keyless degrade: bundled Playwright scraper with a li_at session cookie (env LI_AT)."""
    if not os.environ.get("LI_AT", "").strip():
        sys.exit("ERROR: APIFY_API_TOKEN unset and no LI_AT session cookie. LinkedIn profile "
                 "feeds are JS/auth-walled with no keyless public endpoint. Set "
                 "APIFY_API_TOKEN, or provide LI_AT to use the bundled Playwright degrade "
                 "(npx playwright install chromium first).")
    mjs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "li_profile_posts_playwright.mjs")
    cmd = ["node", mjs, "--profiles", ",".join(profiles),
           "--max-posts", str(max_posts), "--output", "-"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        sys.exit("ERROR: node not found — the keyless Playwright degrade needs Node.js + "
                 "playwright (npx playwright install chromium).")
    if res.returncode != 0:
        sys.exit(f"ERROR: Playwright degrade failed: {res.stderr.strip()}")
    try:
        raw = json.loads(res.stdout or "[]")
    except json.JSONDecodeError:
        sys.exit(f"ERROR: Playwright degrade returned non-JSON: {res.stdout[:200]}")
    return [normalize(p, p.get("_profile") or p.get("author", "")) for p in raw]


def main():
    ap = argparse.ArgumentParser(description="Scrape recent posts from LinkedIn profiles (Apify actor or keyless Playwright cookie degrade).")
    ap.add_argument("--profiles", required=True, help="comma-separated canonical /in/ profile URLs")
    ap.add_argument("--max-posts", type=int, default=20, help="cap per profile (default 20)")
    ap.add_argument("--keywords", default="", help="comma-separated OR content filter")
    ap.add_argument("--days", type=int, default=30, help="only posts from last N days (default 30)")
    ap.add_argument("--actor", default=DEFAULT_ACTOR, help="override Apify actor id")
    ap.add_argument("--output", default="json", choices=["json", "summary"])
    args = ap.parse_args()

    profiles = [u.strip() for u in args.profiles.split(",") if u.strip()]
    bad = [u for u in profiles if not PROFILE_RE.match(u)]
    if bad:
        sys.exit(f"ERROR: not canonical /in/<user> profile URLs: {bad}")

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if token:
        posts = fetch_apify(profiles, args.max_posts, args.actor, token)
    else:
        print("INFO: APIFY_API_TOKEN unset — keyless Playwright degrade via LI_AT cookie.",
              file=sys.stderr)
        posts = fetch_playwright(profiles, args.max_posts)

    # Client-side date filter (LinkedIn has no server-side date filter).
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    filtered = []
    for p in posts:
        dt = parse_dt(p.get("posted_at"))
        if dt is None:
            p["_date_unknown"] = True  # keep but flag (degrade to relative date)
            filtered.append(p)
        elif dt >= cutoff:
            filtered.append(p)

    # Keyword OR filter.
    kws = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    if kws:
        filtered = [p for p in filtered if any(k in (p["text"] or "").lower() for k in kws)]

    if args.output == "summary":
        for p in filtered:
            flag = " (date?)" if p.get("_date_unknown") else ""
            print(f"[{p['reactions']:>5} reacts] {p['posted_at']}{flag} — {p['author']}")
            print(f"   {(p['text'] or '')[:140]}")
            print(f"   {p['url']}")
    else:
        json.dump(filtered, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
