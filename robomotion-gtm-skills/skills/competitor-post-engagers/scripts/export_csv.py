#!/usr/bin/env python3
"""export_csv.py — flatten scored engagers to a CSV for handoff.

Engine step 5 (delivery): turn scored.json into a flat CSV ready for the user, a
contact-cache import, or an Agent Teams channel attachment. Optionally filter to a minimum
tier so you only export the warm A/B leads.

Stdlib only, no network.

Examples:
  export_csv.py --input scored.json --output leads.csv
  export_csv.py --input scored.json --min-tier B --output ab_leads.csv
"""
import argparse
import csv
import json
import sys

TIER_RANK = {"A": 3, "B": 2, "C": 1}
COLUMNS = ["name", "title", "headline", "company", "company_domain", "company_size",
           "industry", "email", "profile_url", "engagement_type", "comment_text",
           "competitor", "post_url", "source", "icp_score", "tier"]


def main():
    ap = argparse.ArgumentParser(description="Flatten scored engagers to CSV.")
    ap.add_argument("--input", required=True, help="scored.json from score_icp.py")
    ap.add_argument("--min-tier", choices=["A", "B", "C"], default="C",
                    help="export only leads at or above this tier (default C = all)")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        leads = json.load(f)

    floor = TIER_RANK[args.min_tier]
    kept = [l for l in leads if TIER_RANK.get(l.get("tier", "C"), 1) >= floor]

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for l in kept:
            w.writerow({c: l.get(c, "") for c in COLUMNS})

    print(f"exported {len(kept)}/{len(leads)} leads (>= tier {args.min_tier}) -> {args.output}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
