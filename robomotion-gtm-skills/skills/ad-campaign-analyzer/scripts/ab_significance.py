#!/usr/bin/env python3
"""ab_significance.py — Deterministic statistical-significance test for an A/B ad pair.

Computes significance in-flow (NOT by an LLM) so the host agent never hallucinates p-values
— it only narrates the verdict this script returns. Stdlib only (math).

Two modes:
  - CTR test (two-proportion z-test): needs clicks + impressions per variant.
    Minimum sample guard: 100 clicks/variant.
  - CPA test (two-proportion z-test on conversion-per-click): needs conversions + clicks
    per variant. Minimum sample guard: 30 conversions/variant.

Returns z, two-sided p, 95% significance flag, the lift, and a 'not enough data' flag when
sample sizes are below the minimums (so the agent refuses to over-claim on thin data).

Examples:
  ab_significance.py --metric ctr --a-clicks 320 --a-impr 12000 --b-clicks 410 --b-impr 12500
  ab_significance.py --metric cpa --a-conv 45 --a-clicks 900 --b-conv 60 --b-clicks 880
"""
import argparse
import json
import math
import sys


def norm_cdf(x):
    """Standard normal CDF via erf (stdlib)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def two_prop_ztest(x1, n1, x2, n2):
    """Two-sided two-proportion z-test. Returns (z, p, p1, p2)."""
    if n1 <= 0 or n2 <= 0:
        return None
    p1 = x1 / n1
    p2 = x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return (0.0, 1.0, p1, p2)
    z = (p2 - p1) / se
    p = 2 * (1 - norm_cdf(abs(z)))
    return (z, p, p1, p2)


def main():
    ap = argparse.ArgumentParser(description="A/B statistical significance for an ad pair (deterministic).")
    ap.add_argument("--metric", choices=["ctr", "cpa"], required=True,
                    help="ctr = two-prop z-test on clicks/impr; cpa = z-test on conv/clicks")
    # CTR inputs
    ap.add_argument("--a-clicks", type=float, default=0)
    ap.add_argument("--b-clicks", type=float, default=0)
    ap.add_argument("--a-impr", type=float, default=0)
    ap.add_argument("--b-impr", type=float, default=0)
    # CPA inputs
    ap.add_argument("--a-conv", type=float, default=0)
    ap.add_argument("--b-conv", type=float, default=0)
    ap.add_argument("--alpha", type=float, default=0.05, help="significance level (default 0.05)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    enough = True
    reason = ""
    if args.metric == "ctr":
        x1, n1, x2, n2 = args.a_clicks, args.a_impr, args.b_clicks, args.b_impr
        if args.a_clicks < 100 or args.b_clicks < 100:
            enough, reason = False, "need >=100 clicks per variant for a CTR verdict"
        unit = "CTR"
    else:  # cpa -> conversion rate per click
        x1, n1, x2, n2 = args.a_conv, args.a_clicks, args.b_conv, args.b_clicks
        if args.a_conv < 30 or args.b_conv < 30:
            enough, reason = False, "need >=30 conversions per variant for a CPA/CVR verdict"
        unit = "conversion rate"

    res = two_prop_ztest(x1, n1, x2, n2)
    if res is None:
        out = {"metric": args.metric, "enough_data": False,
               "reason": "zero denominator (impressions/clicks)", "significant": False}
    else:
        z, p, p1, p2 = res
        lift = ((p2 - p1) / p1 * 100) if p1 else None
        out = {
            "metric": args.metric, "unit": unit,
            "a_rate": round(p1, 5), "b_rate": round(p2, 5),
            "lift_pct": round(lift, 2) if lift is not None else None,
            "z": round(z, 4), "p_value": round(p, 5),
            "alpha": args.alpha,
            "significant": bool(enough and p < args.alpha),
            "winner": (("B" if p2 > p1 else "A") if (enough and p < args.alpha) else None),
            "enough_data": enough,
            "reason": reason or ("significant" if p < args.alpha else "not statistically significant"),
        }

    payload = json.dumps(out, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")


if __name__ == "__main__":
    main()
