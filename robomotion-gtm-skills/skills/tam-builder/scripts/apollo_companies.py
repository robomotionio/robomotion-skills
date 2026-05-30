#!/usr/bin/env python3
"""apollo_companies.py — Apollo Organization Search for TAM building.

Discovers ICP-matching companies via Apollo's organization-search API over the configured
filters (employee ranges, keyword tags, locations) and returns normalized company records
(name, domain, employees, industry, location, keywords, founded, funding stage where
present). Scoring/tiering is a separate deterministic step (score_tam.py). Stdlib only.

Auth: APOLLO_API_KEY (required — Apollo is the TAM engine).

Example:
  apollo_companies.py --employee-ranges "51,200" "201,500" \
      --keyword-tags "saas,b2b" --locations "United States" \
      --num-results 1000 --output companies.json
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

ORG_URL = "https://api.apollo.io/api/v1/mixed_companies/search"
PER_PAGE = 100


def api_key():
    k = os.environ.get("APOLLO_API_KEY", "").strip()
    if not k:
        sys.exit("ERROR: APOLLO_API_KEY not set. This is the Apollo path (recommended, "
                 "higher quality, full firmographics). Without a key, run the keyless "
                 "degrade instead: serp_companies.py (company discovery, no firmographics).")
    return k


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


def normalize(o):
    return {
        "id": o.get("id"),
        "name": o.get("name", ""),
        "domain": o.get("primary_domain", "") or o.get("website_url", ""),
        "employees": o.get("estimated_num_employees") or o.get("organization_num_employees"),
        "industry": o.get("industry", ""),
        "keywords": o.get("keywords", []) or [],
        "location": ", ".join(x for x in (o.get("city"), o.get("state"), o.get("country")) if x),
        "founded_year": o.get("founded_year"),
        "funding_stage": o.get("latest_funding_stage", "") or "",
        "linkedin_url": o.get("linkedin_url", ""),
    }


def main():
    ap = argparse.ArgumentParser(description="Apollo Organization Search for TAM (Company Search).")
    ap.add_argument("--employee-ranges", nargs="*", default=[], help='e.g. "51,200" "201,500"')
    ap.add_argument("--keyword-tags", default="", help="comma-separated industry/keyword tags")
    ap.add_argument("--locations", default="", help="comma-separated geos")
    ap.add_argument("--num-results", type=int, default=1000)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    key = api_key()

    def split(s):
        return [x.strip() for x in s.split(",") if x.strip()]

    base = {"per_page": PER_PAGE}
    if args.employee_ranges:
        base["organization_num_employees_ranges"] = args.employee_ranges
    if args.keyword_tags:
        base["q_organization_keyword_tags"] = split(args.keyword_tags)
    if args.locations:
        base["organization_locations"] = split(args.locations)

    out, seen, page = [], set(), 1
    while len(out) < args.num_results:
        data = post(ORG_URL, dict(base, page=page), key)
        orgs = data.get("organizations") or data.get("accounts") or []
        if not orgs:
            break
        for o in orgs:
            item = normalize(o)
            key_id = (item["domain"] or item["name"]).lower()
            if key_id in seen:
                continue
            seen.add(key_id)
            out.append(item)
            if len(out) >= args.num_results:
                break
        pag = data.get("pagination", {})
        if page >= pag.get("total_pages", page):
            break
        page += 1
        time.sleep(0.3)

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(out)} companies -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
