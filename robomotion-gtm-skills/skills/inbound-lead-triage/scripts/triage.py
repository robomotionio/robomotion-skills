#!/usr/bin/env python3
"""triage.py — collect inbound leads, rank by source urgency, emit a triage queue.

Deterministic part of inbound-lead-triage: merge lead CSVs from multiple sources, assign a
source-urgency rank (demo request > trial signup > webinar reg > content download > chatbot,
configurable), apply recency, and emit a prioritized queue scaffold. The AGENT then qualifies
(inbound-lead-qualification), enriches (inbound-lead-enrichment), and drafts the recommended
response/route per lead. Stdlib only.

Default urgency weights (higher = more urgent), overridable via --urgency-config JSON:
  demo_request 100, trial_signup 80, webinar_reg 50, content_download 30, chatbot 40

Example:
  triage.py --inputs demo.csv:demo_request trial.csv:trial_signup content.csv:content_download \
      --output queue.json
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone

DEFAULT_URGENCY = {
    "demo_request": 100, "trial_signup": 80, "chatbot": 40,
    "webinar_reg": 50, "content_download": 30,
}


def parse_dt(s):
    if not s:
        return None
    s = s.strip()
    for fmt, n in (("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%d %H:%M:%S", 19),
                   ("%Y-%m-%d", 10), ("%m/%d/%Y", 10)):
        try:
            return datetime.strptime(s[:n], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description="Collect + urgency-rank inbound leads into a triage queue.")
    ap.add_argument("--inputs", nargs="+", required=True,
                    help="one or more CSV:source_type pairs, e.g. demo.csv:demo_request")
    ap.add_argument("--urgency-config", default="", help="JSON {source_type: weight} override")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    weights = dict(DEFAULT_URGENCY)
    if args.urgency_config:
        with open(args.urgency_config, encoding="utf-8") as f:
            weights.update(json.load(f))

    now = datetime.now(timezone.utc)
    leads = []
    for spec in args.inputs:
        if ":" not in spec:
            sys.exit(f"ERROR: --inputs item '{spec}' must be CSV:source_type.")
        path, source = spec.rsplit(":", 1)
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                created = (row.get("created_at") or row.get("date") or row.get("timestamp") or "")
                dt = parse_dt(created)
                recency_days = (now - dt).days if dt else None
                base = weights.get(source, 25)
                # recency boost: <=1d +20, <=3d +10, <=7d +5
                boost = 0
                if recency_days is not None:
                    if recency_days <= 1:
                        boost = 20
                    elif recency_days <= 3:
                        boost = 10
                    elif recency_days <= 7:
                        boost = 5
                leads.append({
                    "name": row.get("name") or row.get("Name") or "",
                    "email": (row.get("email") or row.get("Email") or "").strip().lower(),
                    "company": row.get("company") or row.get("Company") or "",
                    "title": row.get("title") or row.get("Title") or "",
                    "source": source,
                    "created_at": created,
                    "urgency_score": base + boost,
                    # agent fills downstream:
                    "icp_score": "",
                    "context": "",
                    "recommended_response": "",
                    "route": "",
                })

    # dedup by email keeping the highest-urgency entry
    by_email = {}
    for l in leads:
        k = l["email"] or (l["name"].lower() + "|" + l["company"].lower())
        if k not in by_email or l["urgency_score"] > by_email[k]["urgency_score"]:
            by_email[k] = l
    queue = sorted(by_email.values(), key=lambda x: x["urgency_score"], reverse=True)

    payload = json.dumps(queue, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(queue)} leads triaged (urgency-ranked) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
