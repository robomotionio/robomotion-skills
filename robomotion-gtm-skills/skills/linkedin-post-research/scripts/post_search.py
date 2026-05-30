#!/usr/bin/env python3
"""post_search.py — search LinkedIn posts by keyword.

Primary path: Apify LinkedIn posts-search actor (cookieless, full engagement metrics)
when APIFY_API_TOKEN is set. Degrade path: keyless web search restricted to public
LinkedIn post URLs (titles/URLs only, NO engagement metrics) via DuckDuckGo HTML.

Deterministic fetch only — the agent does relevance judgement. Stdlib only.


Examples:
  post_search.py --keywords "rpa,workflow automation" --max-items 50 --sort-by relevance
  post_search.py --keywords "agentic ai" --output summary           # serp degrade if no token
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Default Apify actor for LinkedIn posts search (override with --actor).
DEFAULT_ACTOR = "apimaestro~linkedin-posts-search-scraper-no-cookies"
APIFY_BASE = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
DDG_HTML = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/linkedin-post-research)"


def http(req, timeout=120):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "ignore")
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


def apify_search(keywords, max_items, sort_by, actor, token):
    url = APIFY_BASE.format(actor=urllib.parse.quote(actor, safe="~")) + "?token=" + token
    items = []
    for kw in keywords:
        body = json.dumps({
            "searchQuery": kw, "keywords": kw,
            "maxItems": max_items, "limit": max_items,
            "sortBy": sort_by,
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            data = json.loads(http(req))
        except Exception as e:
            print(f"WARN: Apify actor failed for '{kw}': {e}", file=sys.stderr)
            continue
        for it in (data if isinstance(data, list) else data.get("items", [])):
            items.append(normalize_apify(it, kw))
        time.sleep(0.3)
    return items


def normalize_apify(it, kw):
    author = it.get("author") or {}
    return {
        "author": it.get("authorName") or author.get("name") or it.get("author_name", ""),
        "author_headline": author.get("headline") or it.get("authorHeadline", ""),
        "author_profile_url": author.get("profileUrl") or it.get("authorProfileUrl", ""),
        "keyword": kw,
        "reactions": it.get("numLikes") or it.get("reactions") or it.get("likesCount") or 0,
        "comments": it.get("numComments") or it.get("commentsCount") or 0,
        "shares": it.get("numShares") or it.get("sharesCount") or 0,
        "date": it.get("postedAtISO") or it.get("date") or it.get("publishedAt", ""),
        "post_preview": (it.get("text") or "")[:280],
        "full_text": it.get("text", ""),
        "url": it.get("url") or it.get("postUrl", ""),
        "activity_id": it.get("activityId") or it.get("urn") or it.get("url", ""),
        "hashtags": it.get("hashtags", []),
        "is_repost": bool(it.get("isRepost", False)),
        "source": "apify",
    }


def serp_degrade(keywords, max_items):
    """Keyless fallback: public LinkedIn post URLs via DuckDuckGo HTML. No metrics."""
    import html
    import re
    items = []
    for kw in keywords:
        q = f'site:linkedin.com/posts "{kw}"'
        data = urllib.parse.urlencode({"q": q}).encode()
        req = urllib.request.Request(DDG_HTML, data=data, headers={"User-Agent": UA})
        try:
            page = http(req, timeout=30)
        except Exception as e:
            print(f"WARN: serp degrade failed for '{kw}': {e}", file=sys.stderr)
            continue
        for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S):
            href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
            href = urllib.parse.unquote(re.sub(r"^.*uddg=", "", href).split("&")[0]) if "uddg=" in href else href
            if "linkedin.com/posts" not in href:
                continue
            items.append({
                "author": "", "author_headline": "", "author_profile_url": "",
                "keyword": kw, "reactions": 0, "comments": 0, "shares": 0, "date": "",
                "post_preview": html.unescape(title.strip()), "full_text": "",
                "url": href, "activity_id": href, "hashtags": [], "is_repost": False,
                "source": "serp-degrade",
            })
            if len([i for i in items if i["keyword"] == kw]) >= max_items:
                break
        time.sleep(0.5)
    return items


def main():
    ap = argparse.ArgumentParser(description="Search LinkedIn posts by keyword (Apify or serp degrade).")
    ap.add_argument("--keywords", required=True, help="comma-separated search keywords")
    ap.add_argument("--max-items", type=int, default=50, help="cap per keyword (default 50)")
    ap.add_argument("--sort-by", default="relevance", choices=["relevance", "date_posted"])
    ap.add_argument("--actor", default=DEFAULT_ACTOR, help="override Apify actor id")
    ap.add_argument("--output", default="json", choices=["json", "csv", "summary"])
    args = ap.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    token = os.environ.get("APIFY_API_TOKEN", "").strip()

    if token:
        items = apify_search(keywords, args.max_items, args.sort_by, args.actor, token)
        if not items:
            print("WARN: Apify returned nothing; falling back to serp degrade.", file=sys.stderr)
            items = serp_degrade(keywords, args.max_items)
    else:
        print("INFO: APIFY_API_TOKEN unset — serp degrade (no engagement metrics).", file=sys.stderr)
        items = serp_degrade(keywords, args.max_items)

    # Dedup across keywords by activity_id.
    seen, deduped = set(), []
    for it in items:
        aid = it.get("activity_id") or it.get("url")
        if aid in seen:
            continue
        seen.add(aid)
        deduped.append(it)

    if args.sort_by == "date_posted":
        deduped.sort(key=lambda x: x.get("date", ""), reverse=True)
    else:
        deduped.sort(key=lambda x: (x.get("reactions", 0) or 0), reverse=True)

    if args.output == "summary":
        for it in deduped:
            print(f"[{it['reactions']:>5} reacts {it['comments']:>4}c] {it['author'] or '(serp)'}")
            print(f"   {it['post_preview'][:120]}")
            print(f"   {it['url']}")
    elif args.output == "csv":
        import csv
        w = csv.writer(sys.stdout)
        cols = ["author", "author_headline", "keyword", "reactions", "comments", "shares",
                "date", "post_preview", "url", "activity_id", "is_repost", "source"]
        w.writerow(cols)
        for it in deduped:
            w.writerow([it.get(c, "") for c in cols])
    else:
        json.dump(deduped, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
