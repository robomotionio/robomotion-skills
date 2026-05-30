#!/usr/bin/env python3
"""influencer_discovery.py — discover top LinkedIn influencers/voices by topic.

Primary path: Apify influencer-database/filter actor (indexed profiles, accurate
follower counts + email flags) when APIFY_API_TOKEN is set. Degrade path: keyless web
search for candidate /in/ profiles (no follower precision) — the agent then ranks by
serp prominence + relevance.

Deterministic fetch + client-side filtering/sorting only — no LLM. Stdlib only.


Examples:
  influencer_discovery.py --topic "artificial intelligence" --min-followers 50000 --max-results 100
  influencer_discovery.py --topic "saas" --country US --has-email --output summary
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_ACTOR = "apimaestro~linkedin-influencers-database"
APIFY_BASE = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
DDG_HTML = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/linkedin-influencer-discovery)"


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


def normalize_apify(it):
    return {
        "full_name": it.get("fullName") or it.get("name", ""),
        "username": it.get("username") or it.get("handle", ""),
        "biography": it.get("biography") or it.get("bio", ""),
        "follower_count": it.get("followerCount") or it.get("followers") or 0,
        "following_count": it.get("followingCount") or it.get("following") or 0,
        "main_topic": it.get("mainTopic") or it.get("topic", ""),
        "topics": it.get("topics", []),
        "category": it.get("category", ""),
        "linkedin_url": it.get("linkedinUrl") or it.get("profileUrl") or it.get("url", ""),
        "has_email": bool(it.get("email") or it.get("hasEmail")),
        "external_url": it.get("externalUrl", ""),
        "country": it.get("country", ""),
        "city": it.get("city", ""),
        "is_verified": bool(it.get("isVerified", False)),
        "source": "apify-index",
    }


def fetch_apify(topic, category, country, language, max_results, actor, token):
    url = APIFY_BASE.format(actor=urllib.parse.quote(actor, safe="~")) + "?token=" + token
    body = {"topic": topic, "keyword": topic, "maxResults": max_results, "limit": max_results}
    if category:
        body["category"] = category
    if country:
        body["country"] = country
    if language:
        body["language"] = language
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 method="POST", headers={"Content-Type": "application/json"})
    data = json.loads(http(req, timeout=180))
    rows = data if isinstance(data, list) else data.get("items", [])
    return [normalize_apify(r) for r in rows]


def serp_degrade(topic, max_results):
    """Keyless: candidate /in/ profiles via DuckDuckGo. No follower metrics."""
    import html
    queries = [
        f'top {topic} influencers on LinkedIn',
        f'{topic} thought leaders site:linkedin.com/in',
    ]
    out, seen = [], set()
    for q in queries:
        data = urllib.parse.urlencode({"q": q}).encode()
        req = urllib.request.Request(DDG_HTML, data=data, headers={"User-Agent": UA})
        try:
            page = http(req, timeout=30)
        except Exception as e:
            print(f"WARN: serp degrade failed: {e}", file=sys.stderr)
            continue
        for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S):
            href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
            if "uddg=" in href:
                href = urllib.parse.unquote(re.sub(r"^.*uddg=", "", href).split("&")[0])
            if "linkedin.com/in/" not in href:
                continue
            key = href.split("?")[0].rstrip("/").lower()
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "full_name": html.unescape(title.strip()), "username": "", "biography": "",
                "follower_count": 0, "following_count": 0, "main_topic": topic, "topics": [],
                "category": "", "linkedin_url": href.split("?")[0], "has_email": False,
                "external_url": "", "country": "", "city": "", "is_verified": False,
                "source": "serp-degrade",
            })
            if len(out) >= max_results:
                break
        time.sleep(0.5)
    return out


def main():
    ap = argparse.ArgumentParser(description="Discover top LinkedIn influencers by topic (Apify index or serp degrade).")
    ap.add_argument("--topic", required=True, help="e.g. 'artificial intelligence', 'saas'")
    ap.add_argument("--category", default="", help="coarse category (technology, business, ...)")
    ap.add_argument("--country", default="", help="country filter")
    ap.add_argument("--language", default="", help="language filter")
    ap.add_argument("--min-followers", type=int, default=0)
    ap.add_argument("--max-followers", type=int, default=0, help="0 = no upper bound")
    ap.add_argument("--has-email", action="store_true", help="only profiles with an email")
    ap.add_argument("--max-results", type=int, default=100, help="cap (default 100, up to 1000)")
    ap.add_argument("--actor", default=DEFAULT_ACTOR, help="override Apify actor id")
    ap.add_argument("--output", default="json", choices=["json", "summary"])
    args = ap.parse_args()

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if token:
        try:
            rows = fetch_apify(args.topic, args.category, args.country, args.language,
                               args.max_results, args.actor, token)
        except Exception as e:
            print(f"WARN: Apify actor failed ({e}); serp degrade.", file=sys.stderr)
            rows = serp_degrade(args.topic, args.max_results)
    else:
        print("INFO: APIFY_API_TOKEN unset — serp degrade (no follower metrics; rank by relevance).",
              file=sys.stderr)
        rows = serp_degrade(args.topic, args.max_results)

    # Client-side filters.
    def keep(r):
        f = r.get("follower_count", 0) or 0
        if args.min_followers and f < args.min_followers:
            return False
        if args.max_followers and f > args.max_followers:
            return False
        if args.has_email and not r.get("has_email"):
            return False
        return True

    rows = [r for r in rows if keep(r)]
    rows.sort(key=lambda r: r.get("follower_count", 0) or 0, reverse=True)
    rows = rows[: args.max_results]

    if args.output == "summary":
        for r in rows:
            fc = r["follower_count"]
            print(f"[{fc:>9,} followers] {r['full_name']} — {r['main_topic']}"
                  f"{' (email)' if r['has_email'] else ''}")
            print(f"   {r['linkedin_url']}  [{r['source']}]")
    else:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
