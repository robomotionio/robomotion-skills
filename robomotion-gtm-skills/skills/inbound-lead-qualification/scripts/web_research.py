#!/usr/bin/env python3
"""web_research.py — keyless company/person web research for inbound-lead-enrichment.

For each lead, runs keyless web searches (DuckDuckGo HTML) for the company and person and
fetches the top result pages, returning raw search hits + extracted page text for the AGENT
to read and synthesize (company profile, role/seniority, LinkedIn URL). No LLM here — this
is the deterministic fetch layer; the agent does the actual enrichment reasoning.

This is the keyless degrade that always works. When APOLLO_API_KEY / DROPCONTACT_API_KEY /
a CRM key are present, the agent prefers those structured sources and uses this to fill gaps.

Stdlib only. Public search endpoints rate-limit; in production this maps to the Robomotion
serp Search + Extract Content nodes with a proxy.

Example:
  web_research.py --leads leads.csv --output research.json
  web_research.py --company "Acme Corp" --person "Jane Doe" --output research.json
"""
import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DDG = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/inbound-lead-qualification)"
LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
SNIP_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(s):
    return html.unescape(TAG_RE.sub(" ", s)).strip()


def ddg_unwrap(href):
    if "uddg=" in href:
        p = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if "uddg" in p:
            return urllib.parse.unquote(p["uddg"][0])
    return href


def search(query, limit=5):
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


def fetch_text(url, cap=3000):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode("utf-8", "ignore")
        text = strip_tags(re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I))
        return re.sub(r"\s+", " ", text)[:cap]
    except Exception:
        return ""


def research_lead(company, person, fetch_pages):
    block = {"company": company, "person": person, "company_hits": [],
             "person_hits": [], "linkedin_candidates": []}
    if company:
        hits = search(f'"{company}" company about', 5)
        block["company_hits"] = hits
        if fetch_pages and hits:
            block["company_page_text"] = fetch_text(hits[0]["url"])
        time.sleep(0.8)
    if person:
        q = f'"{person}"' + (f' "{company}"' if company else "") + " site:linkedin.com/in"
        hits = search(q, 5)
        block["person_hits"] = hits
        block["linkedin_candidates"] = [h["url"].split("?")[0] for h in hits
                                        if "linkedin.com/in" in h["url"]]
        time.sleep(0.8)
    return block


def main():
    ap = argparse.ArgumentParser(description="Keyless company/person web research (deterministic fetch).")
    ap.add_argument("--leads", default="", help="CSV with company and/or name columns")
    ap.add_argument("--company", default="", help="single-lead company")
    ap.add_argument("--person", default="", help="single-lead person name")
    ap.add_argument("--fetch-pages", action="store_true", help="also fetch the top company page text")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    leads = []
    if args.leads:
        with open(args.leads, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                leads.append({
                    "company": row.get("company") or row.get("Company") or "",
                    "person": row.get("name") or row.get("Name") or
                              f"{row.get('first_name','')} {row.get('last_name','')}".strip(),
                })
    elif args.company or args.person:
        leads = [{"company": args.company, "person": args.person}]
    else:
        sys.exit("ERROR: provide --leads CSV or --company/--person.")

    out = [research_lead(l["company"], l["person"], args.fetch_pages) for l in leads]
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"researched {len(out)} leads -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
