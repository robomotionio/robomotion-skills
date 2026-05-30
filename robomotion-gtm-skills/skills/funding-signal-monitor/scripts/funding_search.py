#!/usr/bin/env python3
"""funding_search.py — aggregate recent funding announcements across keyless web sources.

Searches funding sources and returns raw announcement hits for the AGENT to extract
company/stage/amount/date from (no LLM here — deterministic fetch + dedup only):
  - tech press / Crunchbase via keyless web search (DuckDuckGo HTML) over
    `"<industry>" "raises" "Series A" site:techcrunch.com` / `site:crunchbase.com`
  - Hacker News via the FREE public Algolia API (front-page funding stories)
Dedups hits by normalized company-name guess + URL; multi-source mentions are merged (a
`sources` list), raising confidence not count. X/Reddit depth is optional (Apify).

Stdlib only. Public search endpoints rate-limit; in production this maps to the Robomotion
serp Search + Extract Content nodes with a proxy.

Example:
  funding_search.py --industries "fintech,devtools" --stages "Series A,Series B" \
      --recency-days 30 --output funding.json
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

DDG = "https://html.duckduckgo.com/html/"
HN = "https://hn.algolia.com/api/v1/search_by_date"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/funding-signal-monitor)"
LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
SNIP_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")
PRESS_SITES = ["techcrunch.com", "crunchbase.com", "venturebeat.com"]


def strip_tags(s):
    return html.unescape(TAG_RE.sub(" ", s)).strip()


def ddg_unwrap(href):
    if "uddg=" in href:
        p = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if "uddg" in p:
            return urllib.parse.unquote(p["uddg"][0])
    return href


def ddg_search(query, limit=10):
    data = urllib.parse.urlencode({"q": query}).encode()
    req = urllib.request.Request(DDG, data=data, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "ignore")
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return []
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return []
    else:
        return []
    out, links = [], LINK_RE.findall(body)
    snips = SNIP_RE.findall(body)
    for i, (href, title) in enumerate(links[:limit]):
        out.append({"url": ddg_unwrap(href), "title": strip_tags(title),
                    "snippet": strip_tags(snips[i]) if i < len(snips) else ""})
    return out


def hn_search(query, days):
    cutoff = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    params = {"query": query, "tags": "story",
              "numericFilters": f"created_at_i>{cutoff}", "hitsPerPage": 50}
    url = HN + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []
    out = []
    for h in data.get("hits", []):
        out.append({"url": h.get("url") or
                    f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                    "title": h.get("title") or "", "snippet": "",
                    "created_at": h.get("created_at", "")})
    return out


def company_guess(title):
    # crude: text before "raises"/"closes"/"secures"
    m = re.split(r"\b(raises|closes|secures|lands|nabs|bags)\b", title, flags=re.I)
    return strip_tags(m[0]).strip(" -–—:|") if m else title.strip()


def main():
    ap = argparse.ArgumentParser(description="Aggregate funding announcements (keyless serp + HN).")
    ap.add_argument("--industries", default="", help="comma-separated industry filters")
    ap.add_argument("--stages", default="Series A,Series B,Series C",
                    help="comma-separated funding stages")
    ap.add_argument("--recency-days", type=int, default=30)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    industries = [i.strip() for i in args.industries.split(",") if i.strip()] or [""]
    stages = [s.strip() for s in args.stages.split(",") if s.strip()]

    hits = []
    for ind in industries:
        for stage in stages:
            for site in PRESS_SITES:
                ind_q = f'"{ind}" ' if ind else ""
                q = f'{ind_q}"raises" "{stage}" site:{site}'
                hits.extend(dict(h, stage_hint=stage, industry_hint=ind, src=site)
                            for h in ddg_search(q, 8))
                time.sleep(0.8)
        hn_q = f'{ind} funding raise'.strip()
        hits.extend(dict(h, stage_hint="", industry_hint=ind, src="hackernews")
                    for h in hn_search(hn_q, args.recency_days))
        time.sleep(0.3)

    # dedup by company guess; merge sources
    merged = {}
    for h in hits:
        cg = company_guess(h["title"]).lower()
        if not cg or len(cg) > 80:
            continue
        entry = merged.setdefault(cg, {
            "company_guess": company_guess(h["title"]),
            "stage_hint": h.get("stage_hint", ""),
            "industry_hint": h.get("industry_hint", ""),
            "sources": [], "titles": [],
            # agent fills the structured fields:
            "company": "", "stage": "", "amount": "", "date": "", "fit_note": "",
        })
        entry["sources"].append({"src": h.get("src", ""), "url": h["url"],
                                 "title": h["title"], "snippet": h.get("snippet", "")})
        entry["titles"].append(h["title"])
        if not entry["stage_hint"] and h.get("stage_hint"):
            entry["stage_hint"] = h["stage_hint"]

    out = sorted(merged.values(), key=lambda e: len(e["sources"]), reverse=True)
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(out)} candidate companies ({len(hits)} raw hits) -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
