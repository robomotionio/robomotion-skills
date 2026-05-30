#!/usr/bin/env python3
"""score_tam.py — deterministic 0-100 fit scoring + tier assignment for the TAM.

Takes Apollo company records (from apollo_companies.py) and a scoring config (weights, tier
thresholds, target industries/sizes/stages/geos) and produces a fit score 0-100 + tier
(1/2/3) per company, with a transparent breakdown the agent can audit/override. No LLM —
the agent can re-score fuzzy industry-fit judgments separately if desired.

Scoring config JSON shape:
{
  "weights": {"industry": 0.35, "size": 0.25, "stage": 0.2, "geo": 0.2},
  "tiers": {"1": 75, "2": 50},                 # >=75 tier1, >=50 tier2, else tier3
  "target_industries": ["software", "saas"],
  "target_sizes": [[51,200],[201,500]],         # employee ranges that score full
  "target_stages": ["series a","series b"],
  "target_geos": ["united states"]
}

Example:
  score_tam.py --input companies.json --config scoring.json --output scored.json
"""
import argparse
import json
import sys


def in_any_range(n, ranges):
    if n is None:
        return False
    for r in ranges:
        if len(r) == 2 and r[0] <= n <= r[1]:
            return True
    return False


def contains_any(text, terms):
    t = (text or "").lower()
    return any(term.lower() in t for term in terms)


def main():
    ap = argparse.ArgumentParser(description="Score + tier the TAM (deterministic 0-100).")
    ap.add_argument("--input", required=True, help="companies JSON from apollo_companies.py")
    ap.add_argument("--config", required=True, help="scoring config JSON")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        companies = json.load(f)
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)

    weights = cfg.get("weights", {"industry": 0.35, "size": 0.25, "stage": 0.2, "geo": 0.2})
    tiers = cfg.get("tiers", {"1": 75, "2": 50})
    t1 = float(tiers.get("1", 75))
    t2 = float(tiers.get("2", 50))
    ind = cfg.get("target_industries", [])
    sizes = cfg.get("target_sizes", [])
    stages = cfg.get("target_stages", [])
    geos = cfg.get("target_geos", [])

    out = []
    for c in companies:
        kw_blob = " ".join(c.get("keywords") or []) + " " + (c.get("industry") or "")
        dims = {
            "industry": 1.0 if (not ind or contains_any(kw_blob, ind)) else 0.0,
            "size": 1.0 if (not sizes or in_any_range(c.get("employees"), sizes)) else 0.0,
            "stage": 1.0 if (not stages or contains_any(c.get("funding_stage"), stages)) else 0.0,
            "geo": 1.0 if (not geos or contains_any(c.get("location"), geos)) else 0.0,
        }
        score = round(100 * sum(weights.get(k, 0) * v for k, v in dims.items()), 1)
        tier = 1 if score >= t1 else (2 if score >= t2 else 3)
        out.append(dict(c, fit_score=score, tier=tier,
                        scoring_breakdown={k: {"hit": dims[k], "weight": weights.get(k, 0)}
                                           for k in dims}))

    out.sort(key=lambda c: c["fit_score"], reverse=True)
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        t1n = sum(1 for c in out if c["tier"] == 1)
        t2n = sum(1 for c in out if c["tier"] == 2)
        print(f"{len(out)} scored (tier1={t1n} tier2={t2n}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
