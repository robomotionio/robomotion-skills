#!/usr/bin/env python3
"""serp_search.py — keyless people/company discovery degrade for apollo-lead-finder.

Phase-1 fallback when APOLLO_API_KEY is not set. Runs a keyless web search (DuckDuckGo
HTML endpoint) for `site:linkedin.com/in "<title>" "<keyword/location>"` queries and
returns a discovery set shaped like apollo_search.py's output (name/title/company/
linkedin_url/location). Emails are LEFT BLANK here (the keyless path cannot reveal verified
emails); apollo_enrich.py's keyless degrade can optionally pattern-guess them later.

This is a degrade path: lower precision and coverage than Apollo People Search, no email.
Prefer apollo_search.py when APOLLO_API_KEY is set (the recommended, higher-quality route).
Public search endpoints rate-limit; a Robomotion proxy / robomotion-serp Search node is the
production-grade equivalent. Stdlib only.

Example:
  serp_search.py --titles "VP of Sales,Head of Sales" --keyword-tags saas \
      --locations "United States" --num-results 50 --existing existing.csv --output leads.json
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
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/apollo-lead-finder-degrade)"
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


def norm_linkedin(u):
    if not u:
        return ""
    return u.split("?")[0].rstrip("/").lower().replace("http://", "https://")


def load_existing(path):
    seen = set()
    if not path:
        return seen
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for col in ("linkedin_url", "linkedin", "LinkedIn URL", "linkedinUrl"):
                if row.get(col):
                    seen.add(norm_linkedin(row[col]))
    return seen


def main():
    ap = argparse.ArgumentParser(
        description="Keyless LinkedIn-profile people-discovery degrade (no Apollo key).")
    ap.add_argument("--titles", required=True, help="comma-separated target job titles")
    ap.add_argument("--keyword-tags", default="", help="comma-separated industry/keyword tags")
    ap.add_argument("--locations", default="", help="comma-separated geos")
    ap.add_argument("--exclude-titles", default="", help="comma-separated titles to drop")
    ap.add_argument("--num-results", type=int, default=50, help="discovery cap (default 50)")
    ap.add_argument("--existing", default="", help="CSV of existing contacts to dedup by LinkedIn URL")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    def split(s):
        return [x.strip() for x in s.split(",") if x.strip()]

    titles = split(args.titles)
    tags = split(args.keyword_tags)
    locs = split(args.locations)
    excludes = [t.lower() for t in split(args.exclude_titles)]
    seen = load_existing(args.existing)
    results = []

    # Build query variations: title x (keyword | location) anchored to LinkedIn profiles.
    quals = tags + locs or [""]
    for title in titles:
        for qual in quals:
            q = f'site:linkedin.com/in "{title}"'
            if qual:
                q += f' "{qual}"'
            for hit in search(q):
                if "linkedin.com/in" not in hit["url"]:
                    continue
                lk = norm_linkedin(hit["url"])
                if not lk or lk in seen:
                    continue
                if excludes and any(x in title.lower() for x in excludes):
                    continue
                seen.add(lk)
                results.append({
                    "id": "",
                    "name": "",  # agent resolves from result_title/snippet
                    "first_name": "",
                    "last_name": "",
                    "title": title,
                    "company": "",  # agent resolves from snippet
                    "company_domain": "",
                    "linkedin_url": hit["url"].split("?")[0],
                    "location": qual if qual in locs else "",
                    "email": "",  # keyless path: no verified email
                    "email_status": "",
                    "source": "serp",
                    "result_title": hit["title"],
                    "snippet": hit["snippet"],
                })
                if len(results) >= args.num_results:
                    break
            if len(results) >= args.num_results:
                break
            time.sleep(1.0)  # be polite to the public endpoint
        if len(results) >= args.num_results:
            break

    out = json.dumps(results[: args.num_results], ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(results)} leads (keyless serp degrade) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
