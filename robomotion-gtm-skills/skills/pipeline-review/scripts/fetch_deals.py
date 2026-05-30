#!/usr/bin/env python3
"""fetch_deals.py — pull deals from a CRM into a normalized deal-record JSON.

Deterministic I/O only (stdlib urllib). NO LLM. Supports HubSpot, Pipedrive, and Close
REST APIs; Salesforce via SOQL; or a CSV passthrough (no key). Emits standard deal rows
that analyze_pipeline.py consumes.

Standard deal record:
  {id, name, stage, amount, source, created_at, closed_at, owner, is_won, is_lost}

Auth (only for the chosen --crm):
  hubspot    -> HUBSPOT_API_KEY        (private-app token, Bearer)
  pipedrive  -> PIPEDRIVE_API_TOKEN    (query param)
  close      -> CLOSE_API_KEY          (HTTP basic, key as username)
  salesforce -> SALESFORCE_ACCESS_TOKEN + SALESFORCE_INSTANCE_URL
  csv        -> --csv path (no key)

Example:
  fetch_deals.py --crm hubspot --output deals.json
  fetch_deals.py --crm csv --csv export.csv \
     --map "name=Deal Name,stage=Stage,amount=Amount,created_at=Create Date" --output deals.json
"""
import argparse
import base64
import csv
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
        sys.exit(f"ERROR: {var} is not set (required for this --crm). "
                 "Use --crm csv with --csv for a keyless path.")
    return v


def std(d):
    """Coerce a partial dict into the standard record with safe defaults."""
    return {
        "id": str(d.get("id", "")),
        "name": d.get("name", ""),
        "stage": d.get("stage", ""),
        "amount": _num(d.get("amount")),
        "source": d.get("source", ""),
        "created_at": d.get("created_at", ""),
        "closed_at": d.get("closed_at", ""),
        "owner": d.get("owner", ""),
    }


def _num(v):
    try:
        return float(str(v).replace(",", "").replace("$", "")) if v not in (None, "") else None
    except (ValueError, TypeError):
        return None


def from_hubspot():
    tok = need("HUBSPOT_API_KEY")
    hdr = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
    base = "https://api.hubapi.com/crm/v3/objects/deals"
    props = ["dealname", "dealstage", "amount", "createdate", "closedate", "hs_deal_stage_probability",
             "hubspot_owner_id", "deal_source"]
    after, rows = None, []
    while True:
        q = {"limit": 100, "properties": ",".join(props)}
        if after:
            q["after"] = after
        data = http(base + "?" + urllib.parse.urlencode(q), headers=hdr)
        for r in data.get("results", []):
            p = r.get("properties", {})
            rows.append(std({
                "id": r.get("id"), "name": p.get("dealname"), "stage": p.get("dealstage"),
                "amount": p.get("amount"), "source": p.get("deal_source"),
                "created_at": p.get("createdate"), "closed_at": p.get("closedate"),
                "owner": p.get("hubspot_owner_id"),
            }))
        after = (data.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
    return rows


def from_pipedrive():
    tok = need("PIPEDRIVE_API_TOKEN")
    base = "https://api.pipedrive.com/v1/deals"
    start, rows = 0, []
    while True:
        q = {"api_token": tok, "limit": 100, "start": start}
        data = http(base + "?" + urllib.parse.urlencode(q))
        for d in data.get("data") or []:
            rows.append(std({
                "id": d.get("id"), "name": d.get("title"),
                "stage": d.get("stage_id"), "amount": d.get("value"),
                "source": (d.get("source_name") or d.get("origin")),
                "created_at": d.get("add_time"), "closed_at": d.get("close_time"),
                "owner": (d.get("owner_name") or (d.get("user_id") or {}).get("name")
                          if isinstance(d.get("user_id"), dict) else d.get("user_id")),
            }))
        more = (data.get("additional_data") or {}).get("pagination", {})
        if not more.get("more_items_in_collection"):
            break
        start = more.get("next_start", start + 100)
    return rows


def from_close():
    tok = need("CLOSE_API_KEY")
    auth = base64.b64encode(f"{tok}:".encode()).decode()
    hdr = {"Authorization": f"Basic {auth}"}
    base = "https://api.close.com/api/v1/opportunity/"
    skip, rows = 0, []
    while True:
        data = http(base + "?" + urllib.parse.urlencode({"_limit": 100, "_skip": skip}), headers=hdr)
        for o in data.get("data", []):
            rows.append(std({
                "id": o.get("id"), "name": o.get("lead_name"),
                "stage": o.get("status_label"), "amount": (o.get("value") or 0) / 100.0,
                "source": o.get("source"), "created_at": o.get("date_created"),
                "closed_at": o.get("date_won") or o.get("date_lost"),
                "owner": o.get("user_name"),
            }))
        if not data.get("has_more"):
            break
        skip += 100
    return rows


def from_salesforce():
    tok = need("SALESFORCE_ACCESS_TOKEN")
    inst = need("SALESFORCE_INSTANCE_URL").rstrip("/")
    hdr = {"Authorization": f"Bearer {tok}"}
    soql = ("SELECT Id,Name,StageName,Amount,LeadSource,CreatedDate,CloseDate,Owner.Name "
            "FROM Opportunity")
    url = f"{inst}/services/data/v59.0/query?q=" + urllib.parse.quote(soql)
    rows = []
    while url:
        data = http(url, headers=hdr)
        for o in data.get("records", []):
            rows.append(std({
                "id": o.get("Id"), "name": o.get("Name"), "stage": o.get("StageName"),
                "amount": o.get("Amount"), "source": o.get("LeadSource"),
                "created_at": o.get("CreatedDate"), "closed_at": o.get("CloseDate"),
                "owner": (o.get("Owner") or {}).get("Name"),
            }))
        nxt = data.get("nextRecordsUrl")
        url = inst + nxt if nxt else None
    return rows


def from_csv(path, mapping):
    fields = ("id", "name", "stage", "amount", "source", "created_at", "closed_at", "owner")
    m = {}
    for pair in mapping.split(","):
        if "=" in pair:
            k, _, v = pair.partition("=")
            m[k.strip()] = v.strip()
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rec = {}
            for fld in fields:
                col = m.get(fld, fld)
                rec[fld] = r.get(col, "")
            rows.append(std(rec))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Pull CRM deals into a normalized deal-record JSON.")
    ap.add_argument("--crm", required=True,
                    choices=["hubspot", "pipedrive", "close", "salesforce", "csv"])
    ap.add_argument("--csv", default="", help="CSV path (when --crm csv)")
    ap.add_argument("--map", default="",
                    help='CSV column map "std_field=Column,..." (when --crm csv)')
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    if args.crm == "csv":
        if not args.csv:
            sys.exit("ERROR: --crm csv requires --csv <path>")
        rows = from_csv(args.csv, args.map)
    else:
        rows = {"hubspot": from_hubspot, "pipedrive": from_pipedrive,
                "close": from_close, "salesforce": from_salesforce}[args.crm]()

    out = json.dumps(rows, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(rows)} deals -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
