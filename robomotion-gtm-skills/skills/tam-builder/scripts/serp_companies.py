#!/usr/bin/env python3
"""serp_companies.py — keyless company-discovery degrade for tam-builder (no Apollo key).

Phase-1 fallback when APOLLO_API_KEY is not set. Runs a keyless web search (DuckDuckGo
HTML endpoint) for ICP-shaped queries (keyword tags + locations + size hints) and returns
candidate companies in the same record shape as apollo_companies.py (name, domain,
employees, industry, location, keywords, ...). Firmographics the search can't supply
(employees/industry/funding) are left blank for the agent / score_tam.py to fill or
estimate. Stdlib only.

This is a degrade path: lower precision and far less firmographic depth than Apollo
Company Search. Prefer apollo_companies.py when APOLLO_API_KEY is set (recommended, higher
quality). Public endpoints rate-limit; a Robomotion proxy / robomotion-serp Search node is
the production-grade equivalent.

Example:
  serp_companies.py --keyword-tags "saas,b2b" --locations "United States" \
      --num-results 50 --output companies.json
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

DDG = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/tam-builder-degrade)"
LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
SNIP_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(s):
    return html.unescape(TAG_RE.sub("", s)).strip()


def ddg_uddg(href):
    if "uddg=" in href:
        params = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if "uddg" in params:
            return urllib.parse.unquote(params["uddg"][0])
    return href


def search(query):
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
    for i, (href, title) in enumerate(links):
        out.append({"url": ddg_uddg(href), "title": strip_tags(title),
                    "snippet": strip_tags(snips[i]) if i < len(snips) else ""})
    return out


def domain_of(url):
    try:
        host = urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


# Aggregator/listicle hosts that are not themselves the company.
SKIP_HOSTS = {"linkedin.com", "crunchbase.com", "wikipedia.org", "facebook.com",
              "twitter.com", "x.com", "youtube.com", "medium.com", "g2.com",
              "capterra.com", "glassdoor.com", "indeed.com", "reddit.com",
              "github.com", "producthunt.com", "clutch.co"}


def main():
    ap = argparse.ArgumentParser(
        description="Keyless company-discovery degrade for TAM (no Apollo key).")
    ap.add_argument("--keyword-tags", default="", help="comma-separated industry/keyword tags")
    ap.add_argument("--locations", default="", help="comma-separated geos")
    ap.add_argument("--employee-ranges", nargs="*", default=[],
                    help='size hints for the query, e.g. "51,200" "201,500" (best-effort)')
    ap.add_argument("--num-results", type=int, default=50)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    def split(s):
        return [x.strip() for x in s.split(",") if x.strip()]

    tags = split(args.keyword_tags)
    locs = split(args.locations) or [""]
    size_hint = ""
    if args.employee_ranges:
        lo = args.employee_ranges[0].split(",")[0]
        size_hint = f"{lo}+ employees"

    results, seen = [], set()
    queries = []
    for tag in (tags or [""]):
        for loc in locs:
            parts = [f'"{tag}"' if tag else "", "companies", loc, size_hint]
            q = " ".join(p for p in parts if p).strip()
            if q:
                queries.append((q, tag, loc))

    for q, tag, loc in queries:
        for hit in search(q):
            dom = domain_of(hit["url"])
            if not dom or any(dom == s or dom.endswith("." + s) for s in SKIP_HOSTS):
                continue
            if dom in seen:
                continue
            seen.add(dom)
            results.append({
                "id": "",
                "name": hit["title"].split(" - ")[0].split(" | ")[0].strip() or dom,
                "domain": dom,
                "employees": None,   # keyless path can't supply firmographics
                "industry": tag,
                "keywords": tags,
                "location": loc,
                "founded_year": None,
                "funding_stage": "",
                "linkedin_url": "",
                "source": "serp",
                "result_title": hit["title"],
                "snippet": hit["snippet"],
            })
            if len(results) >= args.num_results:
                break
        if len(results) >= args.num_results:
            break
        time.sleep(1.0)  # be polite to the public endpoint

    payload = json.dumps(results[: args.num_results], ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(results)} companies (keyless serp degrade) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
