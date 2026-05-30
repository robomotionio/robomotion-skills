#!/usr/bin/env python3
"""normalize_campaigns.py — Normalize ad-campaign rows + build a channel rollup.

Ingests a CSV (or JSON) of per-campaign/ad-group/ad performance rows from Google, Meta,
LinkedIn, etc., maps the many possible column names to a standard schema, derives the usual
metrics (CTR, CPC, conv rate, CPA, ROAS) where they can be computed, and rolls everything
up to a channel level. Optionally applies funnel rates to compute funnel-adjusted CAC.

Deterministic only — no LLM. The host agent does the verdicts (Scale/Optimize/Pause),
waste narrative, winner selection, and reallocation reasoning (see ../SKILL.md).
Stdlib only.

Examples:
  normalize_campaigns.py --csv perf.csv --output normalized.json
  normalize_campaigns.py --csv perf.csv --funnel funnel.json --output normalized.json
"""
import argparse
import csv
import json
import sys


ALIASES = {
    "platform": "platform", "channel": "platform", "network": "platform", "source": "platform",
    "campaign": "campaign", "campaign name": "campaign",
    "ad group": "ad_group", "adgroup": "ad_group", "ad set": "ad_group", "adset": "ad_group",
    "ad": "ad", "ad name": "ad", "keyword": "keyword",
    "impressions": "impressions", "impr.": "impressions", "impr": "impressions",
    "clicks": "clicks", "link clicks": "clicks",
    "cost": "spend", "spend": "spend", "amount spent": "spend", "amount spent (usd)": "spend",
    "conversions": "conversions", "conv.": "conversions", "conv": "conversions",
    "results": "conversions", "leads": "conversions",
    "conv. value": "revenue", "conversion value": "revenue", "revenue": "revenue",
    "purchase value": "revenue", "value": "revenue",
    "ctr": "ctr", "cpc": "cpc", "avg. cpc": "cpc", "cpa": "cpa", "cost/conv.": "cpa",
    "roas": "roas",
}

NUMERIC = {"impressions", "clicks", "spend", "conversions", "revenue", "ctr", "cpc", "cpa", "roas"}


def num(v):
    if v is None:
        return 0.0
    s = str(v).strip().replace(",", "").replace("$", "").replace("%", "").replace("€", "").replace("£", "")
    if s == "" or s == "-" or s.lower() in ("n/a", "na", "--"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def canon(raw):
    out = {"platform": "", "campaign": "", "ad_group": "", "ad": "", "keyword": "",
           "impressions": 0.0, "clicks": 0.0, "spend": 0.0, "conversions": 0.0,
           "revenue": 0.0, "ctr": None, "cpc": None, "cpa": None, "roas": None}
    for k, v in raw.items():
        if k is None:
            continue
        key = ALIASES.get(str(k).strip().lower())
        if not key:
            continue
        out[key] = num(v) if key in NUMERIC else (str(v).strip() if v else "")
    # derive metrics when missing but computable
    if out["impressions"]:
        out["ctr"] = round(out["clicks"] / out["impressions"] * 100, 3)
    if out["clicks"]:
        out["cpc"] = round(out["spend"] / out["clicks"], 4)
    out["conv_rate"] = round(out["conversions"] / out["clicks"] * 100, 3) if out["clicks"] else None
    if out["conversions"]:
        out["cpa"] = round(out["spend"] / out["conversions"], 4)
    if out["spend"]:
        out["roas"] = round(out["revenue"] / out["spend"], 4) if out["revenue"] else out["roas"]
    return out


def rollup(rows, funnel):
    chans = {}
    for r in rows:
        p = r["platform"] or "unknown"
        c = chans.setdefault(p, {"platform": p, "impressions": 0.0, "clicks": 0.0,
                                 "spend": 0.0, "conversions": 0.0, "revenue": 0.0, "rows": 0})
        for f in ("impressions", "clicks", "spend", "conversions", "revenue"):
            c[f] += r[f]
        c["rows"] += 1
    for c in chans.values():
        c["ctr"] = round(c["clicks"] / c["impressions"] * 100, 3) if c["impressions"] else None
        c["cpc"] = round(c["spend"] / c["clicks"], 4) if c["clicks"] else None
        c["conv_rate"] = round(c["conversions"] / c["clicks"] * 100, 3) if c["clicks"] else None
        c["cpa"] = round(c["spend"] / c["conversions"], 4) if c["conversions"] else None
        c["roas"] = round(c["revenue"] / c["spend"], 4) if (c["spend"] and c["revenue"]) else None
        # funnel-adjusted CAC: conversions are leads -> apply downstream rates to closes
        if funnel and c["conversions"]:
            rate = 1.0
            for stage in ("lead_to_mql", "mql_to_sql", "sql_to_close"):
                rate *= float(funnel.get(stage, 1.0))
            closes = c["conversions"] * rate
            c["funnel_adj_cac"] = round(c["spend"] / closes, 2) if closes else None
            c["estimated_closes"] = round(closes, 2)
    return list(chans.values())


def main():
    ap = argparse.ArgumentParser(description="Normalize ad-campaign rows + channel rollup (deterministic).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--csv", help="performance CSV export")
    g.add_argument("--json", help="performance JSON array")
    ap.add_argument("--funnel", default="", help="JSON file with lead_to_mql / mql_to_sql / sql_to_close / avg_deal_size")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    if args.csv:
        with open(args.csv, newline="", encoding="utf-8-sig") as f:
            rows = [canon(r) for r in csv.DictReader(f)]
    else:
        with open(args.json, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("rows") or data.get("items") or [data]
        rows = [canon(r) for r in data]

    funnel = {}
    if args.funnel:
        with open(args.funnel, encoding="utf-8") as f:
            funnel = json.load(f)

    result = {"rows": rows, "channels": rollup(rows, funnel),
              "totals": {
                  "spend": round(sum(r["spend"] for r in rows), 2),
                  "clicks": sum(r["clicks"] for r in rows),
                  "conversions": sum(r["conversions"] for r in rows),
                  "impressions": sum(r["impressions"] for r in rows),
                  "revenue": round(sum(r["revenue"] for r in rows), 2),
              },
              "funnel": funnel}
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(rows)} rows, {len(result['channels'])} channels -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
