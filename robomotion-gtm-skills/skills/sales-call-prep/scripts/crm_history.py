#!/usr/bin/env python3
"""crm_history.py — reconstruct one company's prior-interaction record from a CRM.

Deterministic I/O only (stdlib). NO LLM. Searches a CRM for a company (by name or domain)
and pulls its associated deals + contacts so the agent can build the prior-interaction
timeline and set has_prior_contact. The agent reads the output and writes the strategy.

Auth (only for the chosen --crm):
  hubspot    -> HUBSPOT_API_KEY        (Bearer; search Companies + associated Deals/Contacts)
  pipedrive  -> PIPEDRIVE_API_TOKEN    (search Organizations + Deals/Persons)

Salesforce/Close and outreach tools are agent-routed (their APIs are read directly by the
agent); this script covers the two most common no-config CRMs. With no CRM key, the agent
states "true cold meeting" and runs pure web research.

Example:
  crm_history.py --crm hubspot --company "Acme" --domain acme.com --output history.json
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def http(url, headers=None, data=None, method="GET"):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR: CRM API HTTP {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"ERROR: network: {e}")


def need(var):
    v = os.environ.get(var, "").strip()
    if not v:
        sys.exit(f"ERROR: {var} is not set (required for --crm {var.split('_')[0].lower()}).")
    return v


def hubspot(company, domain):
    tok = need("HUBSPOT_API_KEY")
    hdr = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
    # search company by domain (preferred) or name
    filters = []
    if domain:
        filters.append({"propertyName": "domain", "operator": "EQ", "value": domain})
    elif company:
        filters.append({"propertyName": "name", "operator": "CONTAINS_TOKEN", "value": company})
    body = json.dumps({"filterGroups": [{"filters": filters}],
                       "properties": ["name", "domain"], "limit": 5}).encode()
    res = http("https://api.hubapi.com/crm/v3/objects/companies/search",
               headers=hdr, data=body, method="POST")
    companies = res.get("results", [])
    if not companies:
        return {"crm": "hubspot", "found": False, "company": company, "deals": [], "contacts": []}
    cid = companies[0]["id"]
    deals = http(f"https://api.hubapi.com/crm/v3/objects/companies/{cid}/associations/deals", headers=hdr)
    contacts = http(f"https://api.hubapi.com/crm/v3/objects/companies/{cid}/associations/contacts", headers=hdr)

    deal_recs = []
    for a in deals.get("results", [])[:25]:
        d = http(f"https://api.hubapi.com/crm/v3/objects/deals/{a['id']}"
                 "?properties=dealname,dealstage,amount,createdate,closedate", headers=hdr)
        p = d.get("properties", {})
        deal_recs.append({"name": p.get("dealname"), "stage": p.get("dealstage"),
                          "amount": p.get("amount"), "created_at": p.get("createdate"),
                          "closed_at": p.get("closedate")})
    contact_recs = []
    for a in contacts.get("results", [])[:25]:
        c = http(f"https://api.hubapi.com/crm/v3/objects/contacts/{a['id']}"
                 "?properties=firstname,lastname,email,jobtitle", headers=hdr)
        p = c.get("properties", {})
        contact_recs.append({"name": f"{p.get('firstname','')} {p.get('lastname','')}".strip(),
                             "email": p.get("email"), "title": p.get("jobtitle")})
    return {"crm": "hubspot", "found": True,
            "company": companies[0]["properties"].get("name", company),
            "deals": deal_recs, "contacts": contact_recs}


def pipedrive(company, domain):
    tok = need("PIPEDRIVE_API_TOKEN")
    term = company or domain
    res = http("https://api.pipedrive.com/v1/organizations/search?"
               + urllib.parse.urlencode({"api_token": tok, "term": term, "limit": 5}))
    items = ((res.get("data") or {}).get("items") or [])
    if not items:
        return {"crm": "pipedrive", "found": False, "company": company, "deals": [], "contacts": []}
    org_id = items[0]["item"]["id"]
    deals = http(f"https://api.pipedrive.com/v1/organizations/{org_id}/deals?"
                 + urllib.parse.urlencode({"api_token": tok, "limit": 50})) or {}
    persons = http(f"https://api.pipedrive.com/v1/organizations/{org_id}/persons?"
                   + urllib.parse.urlencode({"api_token": tok, "limit": 50})) or {}
    deal_recs = [{"name": d.get("title"), "stage": d.get("stage_id"), "amount": d.get("value"),
                  "created_at": d.get("add_time"), "closed_at": d.get("close_time")}
                 for d in (deals.get("data") or [])]
    contact_recs = [{"name": p.get("name"),
                     "email": (p.get("email") or [{}])[0].get("value") if isinstance(p.get("email"), list) else p.get("email"),
                     "title": p.get("job_title")}
                    for p in (persons.get("data") or [])]
    return {"crm": "pipedrive", "found": True,
            "company": items[0]["item"].get("name", company),
            "deals": deal_recs, "contacts": contact_recs}


def main():
    ap = argparse.ArgumentParser(description="Reconstruct one company's CRM prior-interaction record.")
    ap.add_argument("--crm", required=True, choices=["hubspot", "pipedrive"])
    ap.add_argument("--company", default="", help="company name")
    ap.add_argument("--domain", default="", help="company domain (preferred for matching)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()
    if not (args.company or args.domain):
        sys.exit("ERROR: provide --company and/or --domain.")

    result = (hubspot if args.crm == "hubspot" else pipedrive)(args.company, args.domain)
    result["has_prior_contact"] = bool(result.get("deals") or result.get("contacts"))

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"CRM history (found={result['found']}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
