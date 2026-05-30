#!/usr/bin/env python3
"""leadership_scan.py — detect recent leadership changes via Apollo two-phase.

Phase 1 (free): people-search by organization domain + target titles.
Strict local title post-filter (drops 50-60% of fuzzy matches before spending credits).
Phase 2 (credits, --enrich): enrich-by-id for employment history + current-role start_date
+ LinkedIn URL + verified email. Then keep only people whose current-role start_date falls
within --lookback-days.

Without APOLLO_API_KEY the script cannot run the structured detection — it exits telling
you to use the serp/web-automation degrade in a flow (LLM start-date inference, no verified
email). Deterministic; the agent does relevance scoring. Stdlib only.

Examples:
  leadership_scan.py --domains companies.json --titles "CMO,VP Marketing,Head of Growth" \
      --enrich --lookback-days 90 --output movers.json
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

APOLLO_SEARCH = "https://api.apollo.io/api/v1/mixed_people/search"
APOLLO_ENRICH = "https://api.apollo.io/api/v1/people/match"


def post(url, body, key, timeout=45):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", "X-Api-Key": key,
                                          "Accept": "application/json", "Cache-Control": "no-cache"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apollo {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit("ERROR: Apollo network error")


def split(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def load_domains(arg):
    if arg.endswith(".json") or arg == "-":
        raw = sys.stdin.read() if arg == "-" else open(arg, encoding="utf-8").read()
        data = json.loads(raw)
        data = data if isinstance(data, list) else [data]
        out = []
        for d in data:
            if isinstance(d, dict):
                out.append({"company": d.get("company") or d.get("name", ""), "domain": d.get("domain", "")})
            else:
                out.append({"company": "", "domain": str(d)})
        return out
    return [{"company": "", "domain": x} for x in split(arg)]


def title_matches(person_title, targets):
    pt = (person_title or "").lower()
    return any(t.lower() in pt for t in targets)


def parse_start(pp):
    for emp in (pp.get("employment_history") or []):
        if emp.get("current"):
            sd = emp.get("start_date")
            if sd:
                for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
                    try:
                        return datetime.strptime(sd, fmt).replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue
    return None


def main():
    ap = argparse.ArgumentParser(description="Detect recent leadership changes via Apollo two-phase.")
    ap.add_argument("--domains", required=True, help="JSON/CSV list or comma-separated domains")
    ap.add_argument("--titles", required=True, help="comma-separated target VP+/C-suite titles")
    ap.add_argument("--per-company", type=int, default=10, help="search results per company (default 10)")
    ap.add_argument("--enrich", action="store_true", help="enrich matches for start_date + email (credits)")
    ap.add_argument("--lookback-days", type=int, default=90, help="keep movers whose start_date is within N days")
    ap.add_argument("--output", default="-", help="output JSON path; default stdout")
    args = ap.parse_args()

    key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not key:
        sys.exit("ERROR: APOLLO_API_KEY unset. This structured two-phase detection needs Apollo. "
                 "Degrade in a flow: serp/web-automation search ('{company}' '{title}' appointed "
                 "OR joined OR promoted) + LLM start-date inference (no verified email).")

    companies = load_domains(args.domains)
    targets = split(args.titles)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.lookback_days)

    movers = []
    for co in companies:
        dom = co.get("domain", "").strip()
        if not dom:
            continue
        data = post(APOLLO_SEARCH, {"q_organization_domains": dom, "person_titles": targets,
                                    "page": 1, "per_page": args.per_company}, key)
        for p in data.get("people", []):
            if not title_matches(p.get("title"), targets):  # strict local post-filter
                continue
            org = p.get("organization") or {}
            person = {
                "id": p.get("id"), "name": p.get("name", ""), "title": p.get("title", ""),
                "company": org.get("name", "") or co.get("company", ""), "domain": dom,
                "linkedin_url": p.get("linkedin_url", ""), "email": "",
                "email_status": p.get("email_status", ""), "start_date": "", "recent_mover": None,
            }
            if args.enrich and person["id"]:
                ed = post(APOLLO_ENRICH, {"id": person["id"], "reveal_personal_emails": False}, key)
                pp = ed.get("person") or {}
                person["email"] = pp.get("email", "") or ""
                person["email_status"] = pp.get("email_status", person["email_status"])
                sd = parse_start(pp)
                if sd:
                    person["start_date"] = sd.date().isoformat()
                    person["recent_mover"] = sd >= cutoff
                time.sleep(0.2)
            movers.append(person)
        time.sleep(0.3)

    # When enriched, keep only recent movers; without enrich, return all matches (agent infers).
    if args.enrich:
        kept = [m for m in movers if m["recent_mover"]]
    else:
        kept = movers

    payload = json.dumps(kept, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        print(f"{len(kept)} leaders (of {len(movers)} matched) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
