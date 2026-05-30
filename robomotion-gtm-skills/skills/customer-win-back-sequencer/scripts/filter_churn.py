#!/usr/bin/env python3
"""filter_churn.py — filter a churn list by recency window + min MRR.

Deterministic step 1 of the win-back composite: keep only accounts whose churn_date falls
within the recency window (default 3-18 months ago) and whose mrr_at_churn >= min_mrr.
The AGENT then researches each kept account and scores re-engagement. No LLM, stdlib only.


Input churn JSON/CSV: {company, domain, contact_email, contact_linkedin, churn_date,
mrr_at_churn, churn_reason}.

Examples:
  filter_churn.py --input churn.csv --min-months 3 --max-months 18 --min-mrr 500
  filter_churn.py --input churn.json --min-mrr 1000 --output pursue.json
"""
import argparse
import csv
import io
import json
import sys
from datetime import datetime, timezone


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%Y-%m"):
        try:
            return datetime.strptime(str(s).strip(), fmt).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def load(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    s = raw.lstrip()
    if s.startswith("[") or s.startswith("{"):
        d = json.loads(raw)
        return d if isinstance(d, list) else [d]
    return list(csv.DictReader(io.StringIO(raw)))


def to_float(v):
    try:
        return float(str(v).replace("$", "").replace(",", "").strip() or 0)
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description="Filter churn list by recency window + min MRR (deterministic).")
    ap.add_argument("--input", default="-", help="churn CSV or JSON; default stdin")
    ap.add_argument("--min-months", type=float, default=3, help="min months since churn (too recent below this)")
    ap.add_argument("--max-months", type=float, default=18, help="max months since churn (too stale above this)")
    ap.add_argument("--min-mrr", type=float, default=0, help="only pursue accounts above this MRR")
    ap.add_argument("--output", default="-", help="output JSON path; default stdout")
    args = ap.parse_args()

    rows = load(args.input)
    now = datetime.now(timezone.utc)
    kept, dropped = [], []
    for r in rows:
        cd = parse_date(r.get("churn_date"))
        mrr = to_float(r.get("mrr_at_churn"))
        reason = None
        if cd is None:
            reason = "unparseable_churn_date"
        else:
            months = (now - cd).days / 30.44
            r["_months_since_churn"] = round(months, 1)
            if months < args.min_months:
                reason = f"too_recent ({months:.1f}mo < {args.min_months})"
            elif months > args.max_months:
                reason = f"too_stale ({months:.1f}mo > {args.max_months})"
        if reason is None and mrr < args.min_mrr:
            reason = f"below_min_mrr ({mrr} < {args.min_mrr})"
        if reason:
            r["_dropped_reason"] = reason
            dropped.append(r)
        else:
            kept.append(r)

    print(f"INFO: {len(kept)} pursue, {len(dropped)} dropped "
          f"(window {args.min_months}-{args.max_months}mo, min MRR {args.min_mrr}).", file=sys.stderr)

    payload = json.dumps(kept, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        print(f"{len(kept)} accounts -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
