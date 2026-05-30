#!/usr/bin/env python3
"""aggregate_intent.py — group job postings by company and compute a signal strength.

Deterministic step for job-posting-intent: takes the raw jobs JSON (from jobs.py over the
intent titles) and aggregates per company. Signal strength = count of relevant postings,
boosted by recency and by how many distinct intent titles the company is hiring for. The
agent then qualifies each company vs. ICP and writes the outreach angle/personalization.

Stdlib only. No LLM here — scoring is a transparent rule the agent can override.

Example:
  aggregate_intent.py --input jobs.json \
      --intent-titles "data engineer,ml engineer" --output companies.json
"""
import argparse
import json
import sys
from datetime import datetime, timezone


def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s[:len(fmt) + 2].rstrip("Z"), fmt.rstrip("Z")).replace(
                tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description="Aggregate job postings into per-company intent signals.")
    ap.add_argument("--input", required=True, help="jobs JSON from jobs.py")
    ap.add_argument("--intent-titles", default="", help="comma-separated intent titles (for title-diversity boost)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        jobs = json.load(f)
    intent = [t.strip().lower() for t in args.intent_titles.split(",") if t.strip()]
    now = datetime.now(timezone.utc)

    by_company = {}
    for j in jobs:
        co = (j.get("company") or "").strip()
        if not co:
            continue
        key = co.lower()
        entry = by_company.setdefault(key, {
            "company": co, "postings": [], "matched_titles": set(),
        })
        entry["postings"].append({
            "title": j.get("title", ""), "location": j.get("location", ""),
            "apply_url": j.get("apply_url") or j.get("url", ""),
            "description": j.get("description", ""), "source": j.get("source", ""),
        })
        tl = (j.get("title") or "").lower()
        for it in intent:
            if it in tl:
                entry["matched_titles"].add(it)

    out = []
    for entry in by_company.values():
        count = len(entry["postings"])
        title_diversity = len(entry["matched_titles"]) or 1
        # recency boost: newest posting within 30d -> 1.5x, else 1.0
        recency_boost = 1.0
        for p in entry["postings"]:
            d = parse_date(p.get("date", "")) if isinstance(p, dict) else None
            if d and (now - d).days <= 30:
                recency_boost = 1.5
                break
        signal_strength = round(count * title_diversity * recency_boost, 2)
        out.append({
            "company": entry["company"],
            "posting_count": count,
            "matched_intent_titles": sorted(entry["matched_titles"]),
            "signal_strength": signal_strength,
            "postings": entry["postings"],
            "icp_verdict": "",        # agent fills
            "decision_maker": "",     # agent fills (via company-contact-finder)
            "outreach_angle": "",     # agent fills
            "personalization": "",    # agent fills from posting text
        })

    out.sort(key=lambda c: c["signal_strength"], reverse=True)
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(out)} companies -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
