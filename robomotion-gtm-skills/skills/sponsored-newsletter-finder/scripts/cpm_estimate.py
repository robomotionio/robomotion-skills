#!/usr/bin/env python3
"""cpm_estimate.py — Deterministic CPM / cost-band estimate from a subscriber count.

When a newsletter's sponsorship pricing is undisclosed, estimate a cost band from size
benchmarks (label as estimate). Pure arithmetic — no LLM, no network. The host agent uses
this inside its scoring/budget-allocation reasoning.

Benchmarks (per the design contract):
  micro  <5k     : $50-150
  small  5k-20k  : $100-500
  mid    20k-50k : $500-2k
  large  50k+    : $1k-10k

Examples:
  cpm_estimate.py --subscribers 12000
  cpm_estimate.py --subscribers 12K --json
  cpm_estimate.py --subscribers 80000 --open-rate 42
"""
import argparse
import json
import re
import sys

BANDS = [
    (0, 5000, "micro", 50, 150),
    (5000, 20000, "small", 100, 500),
    (20000, 50000, "mid", 500, 2000),
    (50000, float("inf"), "large", 1000, 10000),
]


def parse_subs(s):
    s = str(s).strip().lower().replace(",", "").replace("+", "")
    m = re.match(r"([\d\.]+)\s*([km]?)", s)
    if not m:
        sys.exit(f"ERROR: cannot parse subscriber count '{s}'.")
    n = float(m.group(1))
    if m.group(2) == "k":
        n *= 1_000
    elif m.group(2) == "m":
        n *= 1_000_000
    return int(n)


def band_for(n):
    for lo, hi, name, cmin, cmax in BANDS:
        if lo <= n < hi:
            return name, cmin, cmax
    return "large", 1000, 10000


def main():
    ap = argparse.ArgumentParser(description="Estimate newsletter sponsorship cost band from subscriber count.")
    ap.add_argument("--subscribers", required=True, help="subscriber count (e.g. 12000, 12K, 1.2M)")
    ap.add_argument("--open-rate", type=float, default=0.0, help="open rate %% (optional; refines effective reach)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    n = parse_subs(args.subscribers)
    name, cmin, cmax = band_for(n)
    # rough CPM range from the cost band against assumed reach (opens if given, else subs)
    reach = int(n * args.open_rate / 100) if args.open_rate else n
    cpm_min = round(cmin / max(reach, 1) * 1000, 2)
    cpm_max = round(cmax / max(reach, 1) * 1000, 2)
    result = {
        "subscribers": n,
        "size_band": name,
        "cost_min_usd": cmin,
        "cost_max_usd": cmax,
        "assumed_reach": reach,
        "implied_cpm_min": cpm_min,
        "implied_cpm_max": cpm_max,
        "estimate": True,
    }
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"{n:,} subs -> {name} band: ${cmin}-${cmax}/send (estimate)")
        print(f"  assumed reach {reach:,} -> implied CPM ${cpm_min}-${cpm_max}")


if __name__ == "__main__":
    main()
