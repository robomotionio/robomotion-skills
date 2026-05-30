#!/usr/bin/env python3
"""analyze_deals.py — deterministic win/loss + velocity metrics for sales coaching.

NO LLM. Reads a deals CSV and computes win rate, win/loss profile dimensions, and velocity
(avg cycle, bottleneck stage) so the agent can find the rep's sweet-spot and kill-zone.
The agent interprets the patterns and writes the deal skill grade.

CSV shape (case-insensitive headers; extra columns ignored):
  deal, stage, amount, outcome, created_at, closed_at, industry, size
  outcome in: won|lost|open

Example:
  analyze_deals.py --input deals.csv --output deal_metrics.json
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone


def pdate(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s[:19] if "T" in s else s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def fnum(v):
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except (ValueError, TypeError):
        return None


def main():
    ap = argparse.ArgumentParser(description="Deterministic win/loss + velocity metrics.")
    ap.add_argument("--input", required=True, help="deals CSV")
    ap.add_argument("--output", default="-", help="output metrics JSON (default stdout)")
    args = ap.parse_args()

    rows = []
    with open(args.input, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append({(k or "").strip().lower(): (v or "").strip() for k, v in r.items()})

    won = lost = open_ = 0
    cycle_won = []
    win_by_industry = defaultdict(lambda: [0, 0])  # [won, total_closed]
    win_by_size = defaultdict(lambda: [0, 0])
    lost_at_stage = Counter()
    won_amounts = []

    for d in rows:
        outcome = (d.get("outcome") or "").lower()
        ind = d.get("industry") or "(unknown)"
        size = d.get("size") or "(unknown)"
        created = pdate(d.get("created_at"))
        closed = pdate(d.get("closed_at"))
        if outcome in ("won", "win"):
            won += 1
            win_by_industry[ind][0] += 1
            win_by_industry[ind][1] += 1
            win_by_size[size][0] += 1
            win_by_size[size][1] += 1
            if created and closed:
                cycle_won.append((closed - created).days)
            amt = fnum(d.get("amount"))
            if amt:
                won_amounts.append(amt)
        elif outcome in ("lost", "loss"):
            lost += 1
            win_by_industry[ind][1] += 1
            win_by_size[size][1] += 1
            lost_at_stage[d.get("stage") or "(blank)"] += 1
        else:
            open_ += 1

    closed_total = won + lost

    def win_rates(table):
        return {k: {"won": v[0], "closed": v[1],
                    "win_rate": round(v[0] / v[1], 4) if v[1] else None}
                for k, v in table.items()}

    result = {
        "summary": {
            "deals": len(rows), "won": won, "lost": lost, "open": open_,
            "win_rate": round(won / closed_total, 4) if closed_total else None,
            "avg_cycle_days_won": round(sum(cycle_won) / len(cycle_won), 1) if cycle_won else None,
            "avg_won_amount": round(sum(won_amounts) / len(won_amounts), 2) if won_amounts else None,
        },
        "win_rate_by_industry": win_rates(win_by_industry),
        "win_rate_by_size": win_rates(win_by_size),
        "loss_stage_distribution": dict(lost_at_stage),
    }

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"deal metrics for {len(rows)} deals -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
