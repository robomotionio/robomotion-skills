#!/usr/bin/env python3
"""fetch_customers.py — pull the customer/account list from a CRM into customers.csv.

Deterministic I/O only (stdlib). NO LLM. Emits the columns detect_signals.py expects:
account, mrr, renewal_date. Use only when the customer list lives in a CRM; otherwise
export a CSV directly (keyless path).

Auth (only for the chosen --crm):
  hubspot    -> HUBSPOT_API_KEY        (Bearer; reads Companies)
  pipedrive  -> PIPEDRIVE_API_TOKEN    (reads Organizations)
  salesforce -> SALESFORCE_ACCESS_TOKEN + SALESFORCE_INSTANCE_URL (Accounts via SOQL)

Field names vary by CRM config; override with --mrr-field / --renewal-field.

Example:
  fetch_customers.py --crm hubspot --mrr-field mrr --renewal-field renewal_date \
      --output customers.csv
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def http(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
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
        sys.exit(f"ERROR: {var} is not set (required for this --crm).")
    return v


def from_hubspot(mrr_field, renewal_field):
    tok = need("HUBSPOT_API_KEY")
    hdr = {"Authorization": f"Bearer {tok}"}
    base = "https://api.hubapi.com/crm/v3/objects/companies"
    props = ["name", mrr_field, renewal_field]
    after, rows = None, []
    while True:
        q = {"limit": 100, "properties": ",".join(props)}
        if after:
            q["after"] = after
        data = http(base + "?" + urllib.parse.urlencode(q), headers=hdr)
        for r in data.get("results", []):
            p = r.get("properties", {})
            rows.append({"account": p.get("name", ""), "mrr": p.get(mrr_field, ""),
                         "renewal_date": p.get(renewal_field, "")})
        after = (data.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
    return rows


def from_pipedrive(mrr_field, renewal_field):
    tok = need("PIPEDRIVE_API_TOKEN")
    base = "https://api.pipedrive.com/v1/organizations"
    start, rows = 0, []
    while True:
        q = {"api_token": tok, "limit": 100, "start": start}
        data = http(base + "?" + urllib.parse.urlencode(q))
        for d in data.get("data") or []:
            rows.append({"account": d.get("name", ""), "mrr": d.get(mrr_field, ""),
                         "renewal_date": d.get(renewal_field, "")})
        more = (data.get("additional_data") or {}).get("pagination", {})
        if not more.get("more_items_in_collection"):
            break
        start = more.get("next_start", start + 100)
    return rows


def from_salesforce(mrr_field, renewal_field):
    tok = need("SALESFORCE_ACCESS_TOKEN")
    inst = need("SALESFORCE_INSTANCE_URL").rstrip("/")
    hdr = {"Authorization": f"Bearer {tok}"}
    soql = f"SELECT Name,{mrr_field},{renewal_field} FROM Account"
    url = f"{inst}/services/data/v59.0/query?q=" + urllib.parse.quote(soql)
    rows = []
    while url:
        data = http(url, headers=hdr)
        for o in data.get("records", []):
            rows.append({"account": o.get("Name", ""), "mrr": o.get(mrr_field, ""),
                         "renewal_date": o.get(renewal_field, "")})
        nxt = data.get("nextRecordsUrl")
        url = inst + nxt if nxt else None
    return rows


def main():
    ap = argparse.ArgumentParser(description="Pull CRM customer/account list into customers.csv.")
    ap.add_argument("--crm", required=True, choices=["hubspot", "pipedrive", "salesforce"])
    ap.add_argument("--mrr-field", default="mrr", help="CRM field holding MRR/ARR")
    ap.add_argument("--renewal-field", default="renewal_date", help="CRM field holding renewal date")
    ap.add_argument("--output", default="-", help="output CSV path (default stdout)")
    args = ap.parse_args()

    fn = {"hubspot": from_hubspot, "pipedrive": from_pipedrive, "salesforce": from_salesforce}[args.crm]
    rows = fn(args.mrr_field, args.renewal_field)

    f = open(args.output, "w", newline="", encoding="utf-8") if args.output != "-" else sys.stdout
    try:
        w = csv.DictWriter(f, fieldnames=["account", "mrr", "renewal_date"])
        w.writeheader()
        w.writerows(rows)
    finally:
        if f is not sys.stdout:
            f.close()
            print(f"{len(rows)} customers -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
