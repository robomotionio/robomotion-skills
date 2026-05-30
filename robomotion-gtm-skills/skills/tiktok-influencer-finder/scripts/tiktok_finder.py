#!/usr/bin/env python3
"""tiktok_finder.py — find TikTok creators/influencers matching a niche.

Primary path: Apify TikTok influencer-discovery actor (built-in fit scoring) when
APIFY_API_TOKEN is set. Degrade path: keyless web search for candidate tiktok.com/@handle
profiles (no engagement metrics, no actor fit score — the agent estimates fit).

Deterministic fetch + client-side range/threshold filtering only — no LLM. Stdlib only.


Examples:
  tiktok_finder.py --description "B2B SaaS founders sharing growth tips" --min-followers 10000 --min-fit 0.6
  tiktok_finder.py --description "vegan cooking creators" --location US --output summary
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

DEFAULT_ACTOR = "clockworks~tiktok-scraper"
APIFY_BASE = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
DDG_HTML = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/tiktok-influencer-finder)"


def http(req, timeout=180):
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
    handle = it.get("handle") or it.get("uniqueId") or it.get("authorMeta", {}).get("name", "")
    followers = (it.get("followers") or it.get("fans")
                 or it.get("authorMeta", {}).get("fans") or 0)
    return {
        "creator": it.get("creator") or it.get("nickname")
                   or it.get("authorMeta", {}).get("nickName", ""),
        "handle": handle,
        "profile_url": it.get("profileUrl") or (f"https://www.tiktok.com/@{handle}" if handle else ""),
        "followers": followers,
        "engagement_rate": it.get("engagementRate") or it.get("engagement_rate") or 0,
        "location": it.get("location") or it.get("region", ""),
        "content_focus": it.get("contentFocus") or it.get("signature")
                         or it.get("authorMeta", {}).get("signature", ""),
        "fit_score": it.get("fitScore") or it.get("fit_score"),
        "fit_description": it.get("fitDescription") or it.get("fit_description", ""),
        "source": "apify",
    }


def fetch_apify(description, keywords, per_keyword, location, actor, token):
    url = APIFY_BASE.format(actor=urllib.parse.quote(actor, safe="~")) + "?token=" + token
    body = {"description": description, "searchQueries": [description],
            "keywords": keywords, "resultsPerPage": per_keyword,
            "maxItems": per_keyword * max(keywords, 1)}
    if location:
        body["location"] = location
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 method="POST", headers={"Content-Type": "application/json"})
    data = json.loads(http(req))
    rows = data if isinstance(data, list) else data.get("items", [])
    return [normalize_apify(r) for r in rows]


def serp_degrade(description, max_items):
    import html
    out, seen = [], set()
    q = f'{description} TikTok creators site:tiktok.com'
    data = urllib.parse.urlencode({"q": q}).encode()
    req = urllib.request.Request(DDG_HTML, data=data, headers={"User-Agent": UA})
    try:
        page = http(req, timeout=30)
    except Exception as e:
        print(f"WARN: serp degrade failed: {e}", file=sys.stderr)
        return out
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S):
        href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        if "uddg=" in href:
            href = urllib.parse.unquote(re.sub(r"^.*uddg=", "", href).split("&")[0])
        mh = re.search(r"tiktok\.com/@([A-Za-z0-9._]+)", href)
        if not mh:
            continue
        handle = mh.group(1)
        if handle in seen:
            continue
        seen.add(handle)
        out.append({
            "creator": html.unescape(title.strip()), "handle": handle,
            "profile_url": f"https://www.tiktok.com/@{handle}", "followers": 0,
            "engagement_rate": 0, "location": "", "content_focus": "",
            "fit_score": None, "fit_description": "", "source": "serp-degrade",
        })
        if len(out) >= max_items:
            break
    return out


def main():
    ap = argparse.ArgumentParser(description="Find TikTok creators by niche (Apify discovery actor or serp degrade).")
    ap.add_argument("--description", required=True, help="detailed niche + content style + audience")
    ap.add_argument("--keywords", type=int, default=5, help="number of search keywords (max 5)")
    ap.add_argument("--profiles-per-keyword", type=int, default=10, help="profiles per keyword (max 10)")
    ap.add_argument("--min-followers", type=int, default=0)
    ap.add_argument("--max-followers", type=int, default=0, help="0 = no upper bound")
    ap.add_argument("--min-fit", type=float, default=0.0, help="minimum fit score 0-1 (default 0.0)")
    ap.add_argument("--location", default="", help="country/region filter")
    ap.add_argument("--actor", default=DEFAULT_ACTOR, help="override Apify actor id")
    ap.add_argument("--output", default="json", choices=["json", "csv", "summary"])
    args = ap.parse_args()

    n_keywords = max(1, min(args.keywords, 5))
    per_kw = max(1, min(args.profiles_per_keyword, 10))
    max_items = n_keywords * per_kw

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if token:
        try:
            rows = fetch_apify(args.description, n_keywords, per_kw, args.location, args.actor, token)
        except Exception as e:
            print(f"WARN: Apify actor failed ({e}); serp degrade.", file=sys.stderr)
            rows = serp_degrade(args.description, max_items)
    else:
        print("INFO: APIFY_API_TOKEN unset — serp degrade (no metrics; agent estimates fit).",
              file=sys.stderr)
        rows = serp_degrade(args.description, max_items)

    analyzed = len(rows)

    def keep(r):
        f = r.get("followers", 0) or 0
        if args.min_followers and f < args.min_followers:
            return False
        if args.max_followers and f > args.max_followers:
            return False
        if args.location and r.get("location") and args.location.lower() not in r["location"].lower():
            return False
        fs = r.get("fit_score")
        if args.min_fit and fs is not None and fs < args.min_fit:
            return False
        return True

    matched = [r for r in rows if keep(r)]
    matched.sort(key=lambda r: ((r.get("fit_score") or 0), (r.get("followers") or 0)), reverse=True)

    print(f"INFO: analyzed {analyzed}, matched {len(matched)}.", file=sys.stderr)

    if args.output == "summary":
        for r in matched:
            fs = f"{r['fit_score']:.2f}" if r.get("fit_score") is not None else "n/a"
            print(f"[fit {fs} | {r['followers']:>9,} followers] @{r['handle']} — {r['creator']}")
            print(f"   {r['profile_url']}  [{r['source']}]")
    elif args.output == "csv":
        import csv
        w = csv.writer(sys.stdout)
        cols = ["creator", "handle", "profile_url", "followers", "engagement_rate",
                "location", "content_focus", "fit_score", "fit_description", "source"]
        w.writerow(cols)
        for r in matched:
            w.writerow([r.get(c, "") for c in cols])
    else:
        json.dump({"analyzed": analyzed, "matched": len(matched), "creators": matched},
                  sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
