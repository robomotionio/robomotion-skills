#!/usr/bin/env python3
"""apollo_search.py — Phase 1: free Apollo.io People Search (no enrichment, no credits).

Discovers ICP-matching people via Apollo's people-search API and returns a deduplicated
discovery set (name, title, company, LinkedIn URL, location). Emails are NOT revealed here
(that is Phase 2 — apollo_enrich.py — which costs credits). Stdlib only.

Auth: APOLLO_API_KEY env var (sent as X-Api-Key header).

Example:
  apollo_search.py --titles "VP of Sales,Head of Sales" --seniorities vp,director \
      --employee-ranges "51,200" "201,500" --locations "United States" \
      --keyword-tags saas --num-results 1000 --existing existing.csv --output leads.json
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/search"
PER_PAGE = 100  # Apollo max


def api_key():
    k = os.environ.get("APOLLO_API_KEY", "").strip()
    if not k:
        sys.exit("ERROR: APOLLO_API_KEY is not set. This is the Apollo path (recommended, "
                 "higher quality). Without a key, run the keyless degrade instead: "
                 "serp_search.py (LinkedIn-profile people discovery, no email).")
    return k


def post(url, body, key):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "Cache-Control": "no-cache",
                 "X-Api-Key": key, "Accept": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apollo API {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def norm_linkedin(u):
    if not u:
        return ""
    u = u.split("?")[0].rstrip("/").lower()
    return u.replace("http://", "https://")


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


def normalize(p):
    org = p.get("organization") or {}
    return {
        "id": p.get("id"),
        "name": p.get("name") or f"{p.get('first_name','')} {p.get('last_name','')}".strip(),
        "first_name": p.get("first_name", ""),
        "last_name": p.get("last_name", ""),
        "title": p.get("title", ""),
        "company": org.get("name", ""),
        "company_domain": org.get("primary_domain", "") or org.get("website_url", ""),
        "linkedin_url": p.get("linkedin_url", ""),
        "location": ", ".join(x for x in (p.get("city"), p.get("state"), p.get("country")) if x),
        "email_status": p.get("email_status", ""),  # 'verified' shown only after enrich
    }


def main():
    ap = argparse.ArgumentParser(description="Apollo.io free People Search (Phase 1).")
    ap.add_argument("--titles", required=True, help="comma-separated target job titles")
    ap.add_argument("--seniorities", default="", help="comma-separated: owner,founder,c_suite,vp,director,manager,...")
    ap.add_argument("--employee-ranges", nargs="*", default=[], help='e.g. "51,200" "201,500"')
    ap.add_argument("--locations", default="", help="comma-separated geos")
    ap.add_argument("--keyword-tags", default="", help="comma-separated industry/keyword tags")
    ap.add_argument("--exclude-titles", default="", help="comma-separated titles to drop (client-side)")
    ap.add_argument("--num-results", type=int, default=5000, help="discovery cap (default 5000)")
    ap.add_argument("--existing", default="", help="CSV of existing contacts to dedup by LinkedIn URL")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    key = api_key()
    seen = load_existing(args.existing)
    excludes = [t.strip().lower() for t in args.exclude_titles.split(",") if t.strip()]

    def split(s):
        return [x.strip() for x in s.split(",") if x.strip()]

    base = {"person_titles": split(args.titles), "per_page": PER_PAGE}
    if args.seniorities:
        base["person_seniorities"] = split(args.seniorities)
    if args.employee_ranges:
        base["organization_num_employees_ranges"] = args.employee_ranges
    if args.locations:
        base["person_locations"] = split(args.locations)
    if args.keyword_tags:
        base["q_organization_keyword_tags"] = split(args.keyword_tags)

    results, page = [], 1
    while len(results) < args.num_results:
        body = dict(base, page=page)
        data = post(SEARCH_URL, body, key)
        people = data.get("people", [])
        if not people:
            break
        for p in people:
            item = normalize(p)
            lk = norm_linkedin(item["linkedin_url"])
            if lk and lk in seen:
                continue  # dedup before any enrich
            if excludes and any(x in item["title"].lower() for x in excludes):
                continue
            if lk:
                seen.add(lk)
            results.append(item)
            if len(results) >= args.num_results:
                break
        pag = data.get("pagination", {})
        if page >= pag.get("total_pages", page):
            break
        page += 1
        time.sleep(0.3)  # respect rate limits

    out = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(results)} leads -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
