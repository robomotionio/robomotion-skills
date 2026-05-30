#!/usr/bin/env python3
"""export_csv.py — render drafted LinkedIn messages into a tool-ready CSV.

Deterministic: maps a JSON list of per-lead message objects to the column layout
the target LinkedIn automation tool expects (Dripify / Expandi / Botdog /
PhantomBuster / generic). No LLM, stdlib only.

Input JSON: list of objects, e.g.
  {"linkedin_url":"...","first_name":"Ada","last_name":"Lovelace","company":"X",
   "title":"CTO","connection_request":"...","followup_1":"...","followup_2":"...",
   "inmail_subject":"...","inmail_body":"...","message":"..."}

Example:
  export_csv.py --input messages.json --tool phantombuster --output out.csv
"""
import argparse
import csv
import json
import sys

# Per-tool column order. Generic is the superset.
COLUMNS = {
    "generic": ["linkedin_url", "first_name", "last_name", "company", "title",
                "connection_request", "followup_1", "followup_2", "followup_3",
                "inmail_subject", "inmail_body", "message"],
    "dripify": ["linkedin_url", "first_name", "last_name", "company", "title",
                "connection_request", "followup_1", "followup_2", "followup_3"],
    "expandi": ["profileUrl", "firstName", "lastName", "companyName", "title",
                "connectionMessage", "followup1", "followup2", "followup3"],
    "botdog": ["linkedin_url", "first_name", "last_name", "company", "title",
               "connection_request", "followup_1", "followup_2"],
    "phantombuster": ["profileUrl", "firstName", "lastName", "companyName",
                      "message", "connection_request"],
}

# Map canonical field -> per-tool header for tools that rename columns.
ALIASES = {
    "profileUrl": "linkedin_url", "firstName": "first_name", "lastName": "last_name",
    "companyName": "company", "connectionMessage": "connection_request",
    "followup1": "followup_1", "followup2": "followup_2", "followup3": "followup_3",
}


def main():
    ap = argparse.ArgumentParser(description="Export LinkedIn messages to a tool-ready CSV.")
    ap.add_argument("--input", default="-", help="JSON list of message objects; default stdin")
    ap.add_argument("--tool", default="generic", choices=sorted(COLUMNS.keys()))
    ap.add_argument("--output", default="-", help="CSV path; default stdout")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    rows = json.loads(raw)
    if not isinstance(rows, list):
        rows = [rows]

    cols = COLUMNS[args.tool]
    out = sys.stdout if args.output == "-" else open(args.output, "w", newline="", encoding="utf-8")
    w = csv.writer(out)
    w.writerow(cols)
    for r in rows:
        line = []
        for c in cols:
            canon = ALIASES.get(c, c)
            line.append(r.get(canon, r.get(c, "")) or "")
        w.writerow(line)
    if out is not sys.stdout:
        out.close()
        print(f"{len(rows)} rows -> {args.output} ({args.tool} layout)", file=sys.stderr)


if __name__ == "__main__":
    main()
