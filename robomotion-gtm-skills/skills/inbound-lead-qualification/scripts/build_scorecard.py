#!/usr/bin/env python3
"""build_scorecard.py — assemble the inbound-qualification scorecard CSV/JSON scaffold.

Merges the lead list with CRM/pipeline overlap flags (from crm_lookup.py) into a scorecard
the AGENT fills with qualification verdicts. The agent does the actual scoring against the
ICP rubric (size/industry/use-case/role) and writes status/score/reasoning per lead — this
script only joins inputs and emits the structured shell so output is consistent. Stdlib only.

After the agent fills verdicts, re-run with --finalize to emit the final scored CSV.

Example:
  build_scorecard.py --leads leads.csv --relationships flags.json --output scorecard.json
  build_scorecard.py --finalize --scorecard scorecard.json --format csv
"""
import argparse
import csv
import io
import json
import sys

VERDICT_FIELDS = ["qualification_status", "score", "reasoning"]
OUT_FIELDS = ["name", "email", "company", "title", "linkedin_url",
              "existing_relationship", "company_overlap",
              "qualification_status", "score", "reasoning"]


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser(description="Assemble / finalize the inbound qualification scorecard.")
    ap.add_argument("--leads", default="", help="CSV of inbound leads")
    ap.add_argument("--relationships", default="", help="crm_lookup.py flags JSON")
    ap.add_argument("--scorecard", default="", help="scorecard JSON to finalize")
    ap.add_argument("--finalize", action="store_true", help="emit final scored output")
    ap.add_argument("--format", default="json", choices=["json", "csv"])
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    if args.finalize:
        if not args.scorecard:
            sys.exit("ERROR: --finalize needs --scorecard.")
        with open(args.scorecard, encoding="utf-8") as f:
            rows = json.load(f)
        if args.format == "csv":
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=OUT_FIELDS)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in OUT_FIELDS})
            payload = buf.getvalue()
        else:
            payload = json.dumps(rows, ensure_ascii=False, indent=2)
        if args.output == "-":
            sys.stdout.write(payload if payload.endswith("\n") else payload + "\n")
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(payload if payload.endswith("\n") else payload + "\n")
        return

    if not args.leads:
        sys.exit("ERROR: --leads required to build a scorecard.")
    leads = load_csv(args.leads)
    flags = {}
    if args.relationships:
        with open(args.relationships, encoding="utf-8") as f:
            for r in json.load(f):
                key = (r.get("email", "").lower(), r.get("company", "").lower())
                flags[key] = r

    out = []
    for l in leads:
        email = (l.get("email") or l.get("Email") or "").strip().lower()
        company = (l.get("company") or l.get("Company") or "").strip()
        f = flags.get((email, company.lower()), {})
        out.append({
            "name": l.get("name") or l.get("Name") or "",
            "email": email,
            "company": company,
            "title": l.get("title") or l.get("Title") or "",
            "linkedin_url": l.get("linkedin_url") or l.get("LinkedIn URL") or "",
            "existing_relationship": f.get("existing_relationship", False),
            "company_overlap": f.get("company_overlap", False),
            # agent fills these; left blank as the scoring scaffold:
            "qualification_status": "",
            "score": "",
            "reasoning": "",
        })

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"scorecard scaffold for {len(out)} leads -> {args.output} "
              f"(agent fills {', '.join(VERDICT_FIELDS)})", file=sys.stderr)


if __name__ == "__main__":
    main()
