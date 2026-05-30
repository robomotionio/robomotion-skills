#!/usr/bin/env python3
"""crm_lookup.py — check inbound leads against an existing CRM/customer base for relationships.

Flags which leads already exist as contacts/deals. Two backends:
  - HubSpot CRM search API when HUBSPOT_API_KEY is set (by email + company).
  - CSV degrade: match against a provided customer/CRM export (--crm-csv) by email/company.
The agent uses the flags to avoid enriching/qualifying a lead another rep already owns.

Stdlib only. Salesforce/Pipedrive follow the same shape — add their REST call where noted
or pass a CSV export.

Example:
  crm_lookup.py --leads leads.csv --crm-csv customers.csv --output flags.json
  HUBSPOT_API_KEY=... crm_lookup.py --leads leads.csv --output flags.json
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

HUBSPOT_SEARCH = "https://api.hubapi.com/crm/v3/objects/contacts/search"


def load_leads(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({
                "email": (row.get("email") or row.get("Email") or "").strip().lower(),
                "company": (row.get("company") or row.get("Company") or "").strip().lower(),
                "name": row.get("name") or row.get("Name") or "",
            })
    return rows


def hubspot_search(email):
    key = os.environ.get("HUBSPOT_API_KEY", "").strip()
    body = {"filterGroups": [{"filters": [
        {"propertyName": "email", "operator": "EQ", "value": email}]}],
        "properties": ["email", "company", "hs_lead_status"], "limit": 1}
    req = urllib.request.Request(HUBSPOT_SEARCH, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
                return bool(data.get("results"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            print(f"WARN: HubSpot {e.code}", file=sys.stderr)
            return False
        except urllib.error.URLError:
            return False


def main():
    ap = argparse.ArgumentParser(description="Check leads against CRM/customer base for existing relationships.")
    ap.add_argument("--leads", required=True, help="CSV of inbound leads (email/company)")
    ap.add_argument("--crm-csv", default="", help="CSV export of existing customers/contacts (degrade)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    leads = load_leads(args.leads)
    use_hubspot = bool(os.environ.get("HUBSPOT_API_KEY", "").strip())

    crm_emails, crm_companies = set(), set()
    if args.crm_csv and not use_hubspot:
        with open(args.crm_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                e = (row.get("email") or row.get("Email") or "").strip().lower()
                c = (row.get("company") or row.get("Company") or "").strip().lower()
                if e:
                    crm_emails.add(e)
                if c:
                    crm_companies.add(c)

    out = []
    for l in leads:
        if use_hubspot and l["email"]:
            existing = hubspot_search(l["email"])
            time.sleep(0.2)
            company_overlap = False
        else:
            existing = l["email"] in crm_emails if l["email"] else False
            company_overlap = l["company"] in crm_companies if l["company"] else False
        out.append({
            "name": l["name"], "email": l["email"], "company": l["company"],
            "existing_relationship": bool(existing),
            "company_overlap": bool(company_overlap),
            "source": "hubspot" if use_hubspot else ("crm_csv" if args.crm_csv else "none"),
        })

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        n = sum(1 for r in out if r["existing_relationship"] or r["company_overlap"])
        print(f"{n}/{len(out)} leads have an existing relationship/overlap -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
