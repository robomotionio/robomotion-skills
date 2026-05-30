#!/usr/bin/env python3
"""score_accounts.py — deterministic churn-risk composite scoring + tiering.

NO LLM. Takes a per-account signals JSON and computes the composite score and tier with
FIXED weights (the design contract). The host agent decides which signals are present
(it reads support tickets, comms, usage, billing — often with help from
detect_signals.py for the threshold-/keyword-based ones), then this script does the
deterministic arithmetic so the model never invents scores. The agent writes the
root-cause hypotheses, save plays, and talk tracks.

Weights (severity -> points): critical=25, high=15, medium=8, low=3 ; composite capped 100.
Tiers: Red 70-100, Orange 40-69, Yellow 20-39, Green 0-19.

Input JSON: a list of accounts:
  [{"account":"Acme","mrr":1200,"renewal_date":"2025-07-01",
    "signals":[{"name":"unresolved ticket >7d","severity":"high","lens":"support","note":"..."},
               {"name":"login drop >30%","severity":"medium","lens":"usage"}]}]

Output: each account with composite score, tier, per-lens breakdown, and MRR-at-risk roll-up.

Example:
  score_accounts.py --input signals.json --output scored.json
  score_accounts.py --input signals.json --prior last_week_scored.json --output scored.json
"""
import argparse
import json
import sys
from collections import Counter

WEIGHTS = {"critical": 25, "high": 15, "medium": 8, "low": 3}
VALID_LENS = {"support", "communication", "engagement", "usage", "commercial",
              "relationship", "sentiment"}


def tier_of(score):
    if score >= 70:
        return "Red"
    if score >= 40:
        return "Orange"
    if score >= 20:
        return "Yellow"
    return "Green"


def score_account(acct):
    by_lens = Counter()
    total = 0
    cleaned = []
    for s in acct.get("signals", []):
        sev = str(s.get("severity", "")).lower().strip()
        if sev not in WEIGHTS:
            # unknown severity -> treat as low, but flag
            sev = "low"
        pts = WEIGHTS[sev]
        total += pts
        lens = str(s.get("lens", "")).lower().strip()
        if lens in VALID_LENS:
            by_lens[lens] += pts
        cleaned.append({
            "name": s.get("name", ""),
            "severity": sev,
            "lens": lens,
            "points": pts,
            "note": s.get("note", ""),
        })
    composite = min(total, 100)
    return {
        "account": acct.get("account", ""),
        "mrr": acct.get("mrr"),
        "renewal_date": acct.get("renewal_date", ""),
        "composite_score": composite,
        "tier": tier_of(composite),
        "lens_breakdown": dict(by_lens),
        "signals": cleaned,
        "signal_count": len(cleaned),
    }


def main():
    ap = argparse.ArgumentParser(description="Deterministic churn-risk composite scoring + tiering.")
    ap.add_argument("--input", required=True, help="per-account signals JSON")
    ap.add_argument("--prior", default="", help="prior run's scored JSON for week-over-week movement")
    ap.add_argument("--output", default="-", help="output scored JSON (default stdout)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        accounts = json.load(f)
    if not isinstance(accounts, list):
        sys.exit("ERROR: input must be a JSON array of accounts.")

    scored = [score_account(a) for a in accounts]
    scored.sort(key=lambda a: a["composite_score"], reverse=True)

    # week-over-week movement
    if args.prior:
        try:
            with open(args.prior, encoding="utf-8") as f:
                prior = {a["account"]: a for a in json.load(f).get("accounts", [])}
        except (OSError, ValueError, KeyError):
            prior = {}
        for a in scored:
            p = prior.get(a["account"])
            if p:
                a["prior_score"] = p.get("composite_score")
                a["score_delta"] = a["composite_score"] - (p.get("composite_score") or 0)
                a["prior_tier"] = p.get("tier")
            else:
                a["prior_score"] = None
                a["score_delta"] = None
                a["prior_tier"] = "(new)"

    tier_counts = Counter(a["tier"] for a in scored)
    mrr_at_risk = {}
    for tier in ("Red", "Orange", "Yellow"):
        mrr_at_risk[tier] = round(
            sum((a.get("mrr") or 0) for a in scored if a["tier"] == tier), 2)

    lens_dist = Counter()
    for a in scored:
        for lens, pts in a["lens_breakdown"].items():
            lens_dist[lens] += pts

    result = {
        "summary": {
            "total_accounts": len(scored),
            "tier_counts": dict(tier_counts),
            "mrr_at_risk_by_tier": mrr_at_risk,
            "signal_distribution_by_lens": dict(lens_dist),
        },
        "accounts": scored,
    }

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"scored {len(scored)} accounts -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
