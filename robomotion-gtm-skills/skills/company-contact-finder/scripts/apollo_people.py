#!/usr/bin/env python3
"""apollo_people.py — find decision-makers at a named company via Apollo People Search.

Cheapest-first primary path for company-contact-finder. Filters Apollo People Search by
the company's domain (or name) and target titles, returning name/title/LinkedIn/location.
Emails are NOT revealed here (free search). Stdlib only.

Auth: APOLLO_API_KEY (X-Api-Key header). Optional here — caller degrades to serp when unset.

Example:
  apollo_people.py --company "Acme Corp" --domain acme.com \
      --titles "CFO,VP Finance,Head of Finance" --num-results 10 --output contacts.json
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/search"
ORG_URL = "https://api.apollo.io/api/v1/mixed_companies/search"
PER_PAGE = 100


def api_key():
    k = os.environ.get("APOLLO_API_KEY", "").strip()
    if not k:
        sys.exit("ERROR: APOLLO_API_KEY not set (this script is the Apollo path; "
                 "degrade to the serp script when no key).")
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
    return u.split("?")[0].rstrip("/").lower().replace("http://", "https://")


def resolve_domain(company, key):
    """Best-effort: resolve a company name to its primary domain via Org Search."""
    data = post(ORG_URL, {"q_organization_name": company, "per_page": 1}, key)
    orgs = data.get("organizations") or data.get("accounts") or []
    if orgs:
        return orgs[0].get("primary_domain", "") or ""
    return ""


def normalize(p):
    org = p.get("organization") or {}
    return {
        "name": p.get("name") or f"{p.get('first_name','')} {p.get('last_name','')}".strip(),
        "first_name": p.get("first_name", ""),
        "last_name": p.get("last_name", ""),
        "title": p.get("title", ""),
        "company": org.get("name", ""),
        "company_domain": org.get("primary_domain", ""),
        "linkedin_url": p.get("linkedin_url", ""),
        "location": ", ".join(x for x in (p.get("city"), p.get("state"), p.get("country")) if x),
        "email": "",  # free search does not reveal email
        "source": "apollo",
    }


def main():
    ap = argparse.ArgumentParser(description="Apollo People Search at a named company (free).")
    ap.add_argument("--company", required=True, help="company name")
    ap.add_argument("--domain", default="", help="company domain (skips name->domain resolution)")
    ap.add_argument("--titles", required=True, help="comma-separated target titles")
    ap.add_argument("--num-results", type=int, default=10)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    key = api_key()
    titles = [t.strip() for t in args.titles.split(",") if t.strip()]
    domain = args.domain.strip() or resolve_domain(args.company, key)

    base = {"person_titles": titles, "per_page": PER_PAGE}
    if domain:
        base["q_organization_domains"] = domain
    else:
        base["q_organization_name"] = args.company

    results, seen, page = [], set(), 1
    while len(results) < args.num_results:
        data = post(SEARCH_URL, dict(base, page=page), key)
        people = data.get("people", [])
        if not people:
            break
        for p in people:
            item = normalize(p)
            lk = norm_linkedin(item["linkedin_url"])
            if lk and lk in seen:
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
        time.sleep(0.3)

    out = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(results)} contacts -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
