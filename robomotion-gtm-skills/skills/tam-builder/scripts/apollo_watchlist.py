#!/usr/bin/env python3
"""apollo_watchlist.py — build a persona watchlist for Tier 1-2 companies.

For each Tier 1-2 company in the scored TAM, find watchlist-persona people (name, title,
company, LinkedIn URL). No enrichment / no credits. Stdlib only.

Paid vs. fallback:
  - If APOLLO_API_KEY is set -> free Apollo People Search per company (recommended).
  - If NOT set -> keyless degrade: a `site:linkedin.com/in "<company>" "<title>"` web
    search (DuckDuckGo HTML) per company; returns LinkedIn-profile candidates with the
    result title/snippet for the agent to resolve (name often blank, no email).

Example:
  apollo_watchlist.py --input scored.json --titles "VP Sales,Head of RevOps,CRO" \
      --max-tier 2 --per-company 5 --output watchlist.json
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/search"
PER_PAGE = 100

DDG = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/tam-builder-degrade)"
LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
SNIP_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def _strip(s):
    return html.unescape(TAG_RE.sub("", s)).strip()


def _uddg(href):
    if "uddg=" in href:
        params = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if "uddg" in params:
            return urllib.parse.unquote(params["uddg"][0])
    return href


def ddg_search(query):
    data = urllib.parse.urlencode({"q": query}).encode()
    req = urllib.request.Request(DDG, data=data, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "ignore")
            break
        except (urllib.error.HTTPError, urllib.error.URLError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return []
    else:
        return []
    out, links = [], LINK_RE.findall(body)
    snips = SNIP_RE.findall(body)
    for i, (href, title) in enumerate(links):
        out.append({"url": _uddg(href), "title": _strip(title),
                    "snippet": _strip(snips[i]) if i < len(snips) else ""})
    return out


def keyless_company_people(company, titles, per_company, seen):
    """Keyless degrade: serp for LinkedIn profiles at this company for the persona titles."""
    rows = []
    for title in titles:
        if len(rows) >= per_company:
            break
        q = f'site:linkedin.com/in "{company}" "{title}"'
        for hit in ddg_search(q):
            if "linkedin.com/in" not in hit["url"]:
                continue
            lk = hit["url"].split("?")[0].rstrip("/").lower()
            if lk in seen:
                continue
            seen.add(lk)
            rows.append({
                "name": "",  # agent resolves from result_title/snippet
                "title": title,
                "company": company,
                "company_domain": "",
                "linkedin_url": hit["url"].split("?")[0],
                "source": "serp",
                "result_title": hit["title"],
                "snippet": hit["snippet"],
            })
            if len(rows) >= per_company:
                break
        time.sleep(1.0)  # polite to the public endpoint
    return rows


def post(url, body, key):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json", "Cache-Control": "no-cache",
        "X-Api-Key": key, "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apollo API {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def main():
    ap = argparse.ArgumentParser(description="Apollo People Search watchlist for Tier 1-2 companies (free).")
    ap.add_argument("--input", required=True, help="scored TAM JSON from score_tam.py")
    ap.add_argument("--titles", required=True, help="comma-separated persona titles")
    ap.add_argument("--max-tier", type=int, default=2, help="include companies up to this tier")
    ap.add_argument("--per-company", type=int, default=5)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    key = os.environ.get("APOLLO_API_KEY", "").strip()
    titles = [t.strip() for t in args.titles.split(",") if t.strip()]
    with open(args.input, encoding="utf-8") as f:
        companies = [c for c in json.load(f) if c.get("tier", 3) <= args.max_tier]

    if not key:
        print("WARN: APOLLO_API_KEY not set -> keyless serp watchlist degrade "
              "(LinkedIn-profile candidates, agent resolves names, no email).", file=sys.stderr)

    watchlist, seen = [], set()
    for c in companies:
        domain = c.get("domain", "")
        if not key:
            for row in keyless_company_people(c.get("name", ""), titles, args.per_company, seen):
                watchlist.append(dict(row, tier=c.get("tier")))
            continue
        base = {"person_titles": titles, "per_page": min(PER_PAGE, max(args.per_company, 1))}
        if domain:
            base["q_organization_domains"] = domain
        else:
            base["q_organization_name"] = c.get("name", "")
        data = post(SEARCH_URL, dict(base, page=1), key)
        added = 0
        for p in data.get("people", []):
            lk = (p.get("linkedin_url") or "").split("?")[0].rstrip("/").lower()
            if lk and lk in seen:
                continue
            if lk:
                seen.add(lk)
            watchlist.append({
                "name": p.get("name", ""),
                "title": p.get("title", ""),
                "company": c.get("name", ""),
                "company_domain": domain,
                "tier": c.get("tier"),
                "linkedin_url": p.get("linkedin_url", ""),
            })
            added += 1
            if added >= args.per_company:
                break
        time.sleep(0.3)

    payload = json.dumps(watchlist, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(watchlist)} personas across {len(companies)} companies -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
