#!/usr/bin/env python3
"""extract_commenters.py — pull everyone who commented on LinkedIn post(s).

Primary path: Apify LinkedIn post-comments actor (cookieless) when APIFY_API_TOKEN is
set. Keyless degrade: when APIFY_API_TOKEN is unset, fall back to the bundled Playwright
scraper (li_comments_playwright.mjs) using a LinkedIn `li_at` session cookie (env LI_AT).
Both paths emit the same row shape; if neither a token nor a cookie is available the
script exits with instructions.

Deterministic fetch + heuristic headline parsing only — no LLM. Stdlib only (the keyless
path shells out to node/Playwright).

Examples:
  extract_commenters.py --post-urls "https://www.linkedin.com/posts/x_y-activity-123" --max-comments 100
  extract_commenters.py --post-urls "u1,u2" --dedup --output csv
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_ACTOR = "apimaestro~linkedin-post-comments-replies-no-cookies"
APIFY_BASE = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"


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


def parse_headline(headline):
    """Heuristic: split 'Title at Company' / 'Title @ Company'. Keep raw if ambiguous."""
    if not headline:
        return "", ""
    for sep in (" at ", " @ ", " | "):
        if sep in headline:
            left, right = headline.split(sep, 1)
            return left.strip(), right.strip()
    return "", ""


def normalize(c, post_url):
    headline = c.get("headline") or c.get("commenterHeadline") or c.get("occupation", "")
    title, company = parse_headline(headline)
    return {
        "name": c.get("name") or c.get("commenterName") or c.get("authorName", ""),
        "headline": headline,
        "title": title,
        "company": company,
        "linkedin_url": c.get("profileUrl") or c.get("commenterProfileUrl")
                        or c.get("authorProfileUrl", ""),
        "comment_text": c.get("text") or c.get("commentText") or c.get("comment", ""),
        "post_url": post_url,
        "profile_image_url": c.get("profileImageUrl") or c.get("authorProfileImage", ""),
    }


def fetch_apify(post_urls, max_comments, actor, token):
    url = APIFY_BASE.format(actor=urllib.parse.quote(actor, safe="~")) + "?token=" + token
    out = []
    for purl in post_urls:
        body = {"postUrl": purl, "postIds": [purl], "urls": [purl],
                "maxComments": max_comments, "limit": max_comments}
        try:
            data = http_post(url, body)
        except Exception as e:
            print(f"WARN: Apify failed for {purl}: {e}", file=sys.stderr)
            continue
        rows = data if isinstance(data, list) else data.get("items", [])
        for c in rows[:max_comments]:
            out.append(normalize(c, purl))
        time.sleep(0.3)
    return out


def fetch_playwright(post_urls, max_comments):
    """Keyless degrade: bundled Playwright scraper with a li_at session cookie (env LI_AT)."""
    if not os.environ.get("LI_AT", "").strip():
        sys.exit("ERROR: APIFY_API_TOKEN unset and no LI_AT session cookie. LinkedIn comment "
                 "threads are auth/JS-walled with no keyless public endpoint. Set "
                 "APIFY_API_TOKEN, or provide LI_AT to use the bundled Playwright degrade "
                 "(npx playwright install chromium first).")
    mjs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "li_comments_playwright.mjs")
    cmd = ["node", mjs, "--post-urls", ",".join(post_urls),
           "--max-comments", str(max_comments), "--output", "-"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        sys.exit("ERROR: node not found — the keyless Playwright degrade needs Node.js + "
                 "playwright (npx playwright install chromium).")
    if res.returncode != 0:
        sys.exit(f"ERROR: Playwright degrade failed: {res.stderr.strip()}")
    try:
        return json.loads(res.stdout or "[]")
    except json.JSONDecodeError:
        sys.exit(f"ERROR: Playwright degrade returned non-JSON: {res.stdout[:200]}")


def main():
    ap = argparse.ArgumentParser(description="Extract LinkedIn post commenters (Apify actor or keyless Playwright cookie degrade).")
    ap.add_argument("--post-urls", required=True, help="comma-separated LinkedIn post URLs")
    ap.add_argument("--max-comments", type=int, default=100, help="cap per post (default 100)")
    ap.add_argument("--dedup", action="store_true", help="dedup commenters across posts by profile URL")
    ap.add_argument("--actor", default=DEFAULT_ACTOR, help="override Apify actor id")
    ap.add_argument("--output", default="json", choices=["json", "csv", "summary"])
    args = ap.parse_args()

    post_urls = [u.strip() for u in args.post_urls.split(",") if u.strip()]
    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if token:
        rows = fetch_apify(post_urls, args.max_comments, args.actor, token)
    else:
        print("INFO: APIFY_API_TOKEN unset — keyless Playwright degrade via LI_AT cookie.",
              file=sys.stderr)
        rows = fetch_playwright(post_urls, args.max_comments)

    if args.dedup:
        seen, deduped = set(), []
        for r in rows:
            key = (r.get("linkedin_url") or "").rstrip("/").lower()
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            deduped.append(r)
        rows = deduped

    if args.output == "summary":
        for r in rows:
            print(f"{r['name']} — {r['title'] or r['headline']}"
                  f"{(' @ ' + r['company']) if r['company'] else ''}")
            print(f"   {r['linkedin_url']}")
            if r["comment_text"]:
                print(f"   \"{r['comment_text'][:100]}\"")
    elif args.output == "csv":
        w = csv.writer(sys.stdout)
        cols = ["name", "headline", "title", "company", "linkedin_url", "comment_text", "post_url"]
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    else:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
