#!/usr/bin/env python3
"""serp_people.py — keyless degrade for company-contact-finder (no Apollo key).

Runs a keyless web search (DuckDuckGo HTML endpoint) for
`site:linkedin.com/in "<company>" "<title>"` queries and returns candidate LinkedIn
profile URLs with the result title/snippet. The agent reads these and resolves
name/title; this script does deterministic fetch+parse only. Stdlib only.

This is a degrade path: lower precision than Apollo, no email. Prefer apollo_people.py
when APOLLO_API_KEY is set. Note: public search endpoints rate-limit; a Robomotion
proxy / robomotion-serp Search node is the production-grade equivalent.

Example:
  serp_people.py --company "Acme Corp" --titles "CFO,VP Finance" --num-results 10
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request

DDG = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/company-contact-finder)"
LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
SNIP_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(s):
    return html.unescape(TAG_RE.sub("", s)).strip()


def ddg_uddg(href):
    """DDG wraps results in /l/?uddg=<encoded>; unwrap to the real URL."""
    if "uddg=" in href:
        q = urllib.parse.urlparse(href).query
        params = urllib.parse.parse_qs(q)
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
            raise
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
    else:
        return []
    out = []
    links = LINK_RE.findall(body)
    snips = SNIP_RE.findall(body)
    for i, (href, title) in enumerate(links):
        url = ddg_uddg(href)
        out.append({
            "url": url,
            "title": strip_tags(title),
            "snippet": strip_tags(snips[i]) if i < len(snips) else "",
        })
    return out


def main():
    ap = argparse.ArgumentParser(description="Keyless LinkedIn-profile search degrade (no Apollo).")
    ap.add_argument("--company", required=True)
    ap.add_argument("--titles", required=True, help="comma-separated target titles")
    ap.add_argument("--num-results", type=int, default=10)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    titles = [t.strip() for t in args.titles.split(",") if t.strip()]
    seen, results = set(), []
    for title in titles:
        q = f'site:linkedin.com/in "{args.company}" "{title}"'
        for hit in search(q):
            if "linkedin.com/in" not in hit["url"]:
                continue
            key = hit["url"].split("?")[0].rstrip("/").lower()
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "name": "",  # agent resolves from title/snippet
                "title": title,
                "company": args.company,
                "linkedin_url": hit["url"].split("?")[0],
                "location": "",
                "email": "",
                "source": "serp",
                "result_title": hit["title"],
                "snippet": hit["snippet"],
            })
            if len(results) >= args.num_results:
                break
        if len(results) >= args.num_results:
            break
        time.sleep(1.0)  # be polite to the public endpoint

    out = json.dumps(results[: args.num_results], ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(results)} candidates -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
