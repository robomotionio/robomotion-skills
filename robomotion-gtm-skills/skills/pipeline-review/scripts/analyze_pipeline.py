#!/usr/bin/env python3
"""analyze_pipeline.py — deterministic pipeline metrics over normalized deals.

Reads a deals JSON (from fetch_deals.py or any source matching the standard record) and
computes the NUMBERS only — counts, rates, per-stage velocity, stage-to-stage conversion,
weighted pipeline, slippage, per-owner performance, forecast coverage. NO LLM, no
narrative: the host agent reads this metrics JSON and writes the exec summary + diagnostic
prose + recommendations. Keeping metrics computed (not model-estimated) keeps them
trustworthy.

Standard record fields used: id, name, stage, amount, source, created_at, closed_at,
owner. Optional: expected_close_date, last_activity_at, stage_entered_at (for slippage and
per-stage age). Stage roles + an ORDERED funnel are supplied by flags so the skill stays
CRM-agnostic.

Example:
  analyze_pipeline.py --deals deals.json \
    --stage-order "Lead,Qualified,Demo,Proposal,Negotiation,Closed Won,Closed Lost" \
    --qualified-stages "Qualified,Demo,Proposal,Negotiation" \
    --won-stages "Closed Won" --lost-stages "Closed Lost" \
    --period-start 2025-01-01 --period-end 2025-03-31 \
    --expected-cycle-days 45 --target-pipeline 500000 \
    --stage-probabilities "Lead=0.05,Qualified=0.2,Demo=0.4,Proposal=0.6,Negotiation=0.8" \
    --output metrics.json
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone


def parse_dt(s):
    if not s:
        return None
    s = str(s).strip()
    # epoch millis (HubSpot/Pipedrive sometimes)
    if s.isdigit() and len(s) >= 12:
        try:
            return datetime.fromtimestamp(int(s) / 1000, tz=timezone.utc)
        except (ValueError, OSError):
            return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(s[:26] if "." in s else s[:19] if "T" in s else s, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def csl(s):
    return {x.strip().lower() for x in s.split(",") if x.strip()}


def ordered_csl(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def kv_floats(s):
    """Parse 'Lead=0.05,Qualified=0.2' -> {'lead':0.05,'qualified':0.2} (keys lowercased)."""
    out = {}
    for part in s.split(","):
        if "=" in part:
            k, _, v = part.partition("=")
            try:
                out[k.strip().lower()] = float(v.strip())
            except ValueError:
                continue
    return out


def days_between(a, b):
    if not a or not b:
        return None
    return (b - a).days


def median(vals):
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    n = len(vals)
    mid = n // 2
    return vals[mid] if n % 2 else (vals[mid - 1] + vals[mid]) / 2


# Default stage win-probabilities when none supplied — a conventional MEDDIC-ish ramp the
# agent can override. Matched by substring against the deal's stage (lowercased).
DEFAULT_STAGE_PROB = {
    "lead": 0.05, "prospect": 0.05, "new": 0.05,
    "qualified": 0.20, "discovery": 0.20, "sql": 0.20,
    "demo": 0.40, "meeting": 0.35, "evaluation": 0.45,
    "proposal": 0.60, "quote": 0.60,
    "negotiation": 0.80, "contract": 0.85, "verbal": 0.90,
    "commit": 0.90,
}


def stage_probability(stage_l, explicit):
    if stage_l in explicit:
        return explicit[stage_l]
    for key, p in DEFAULT_STAGE_PROB.items():
        if key in stage_l:
            return p
    return None


def coverage_tier(ratio):
    if ratio is None:
        return None
    if ratio >= 4.0:
        return "healthy"
    if ratio >= 3.0:
        return "adequate"
    if ratio >= 2.0:
        return "thin"
    return "at-risk"


def main():
    ap = argparse.ArgumentParser(description="Deterministic pipeline metrics.")
    ap.add_argument("--deals", required=True, help="normalized deals JSON path")
    ap.add_argument("--stage-order", default="",
                    help="ordered, comma-separated funnel stages (for stage-to-stage conversion)")
    ap.add_argument("--qualified-stages", default="", help="comma-separated stages that count as qualified")
    ap.add_argument("--won-stages", default="", help="comma-separated won stage names")
    ap.add_argument("--lost-stages", default="", help="comma-separated lost stage names")
    ap.add_argument("--stage-probabilities", default="",
                    help="comma-separated Stage=prob pairs for weighted pipeline (else built-in ramp)")
    ap.add_argument("--period-start", default="", help="YYYY-MM-DD inclusive")
    ap.add_argument("--period-end", default="", help="YYYY-MM-DD inclusive")
    ap.add_argument("--expected-cycle-days", type=int, default=0, help="for stuck-deal flagging")
    ap.add_argument("--target-pipeline", type=float, default=0.0, help="for coverage ratio")
    ap.add_argument("--quota", type=float, default=0.0,
                    help="revenue quota/target for the period (coverage = weighted pipeline / quota)")
    ap.add_argument("--output", default="-", help="output metrics JSON (default stdout)")
    args = ap.parse_args()

    with open(args.deals, encoding="utf-8") as f:
        deals = json.load(f)

    won = csl(args.won_stages)
    lost = csl(args.lost_stages)
    qualified = csl(args.qualified_stages)
    stage_order = ordered_csl(args.stage_order)
    explicit_prob = kv_floats(args.stage_probabilities)
    p_start = parse_dt(args.period_start)
    p_end = parse_dt(args.period_end)
    now = datetime.now(timezone.utc)

    def in_period(d):
        if not (p_start or p_end):
            return True
        c = parse_dt(d.get("created_at"))
        if not c:
            return True
        if p_start and c < p_start:
            return False
        if p_end and c > p_end:
            return False
        return True

    scoped = [d for d in deals if in_period(d)]

    total = len(scoped)
    stage_counts = Counter()
    source_counts = Counter()
    source_won = Counter()
    source_amt = defaultdict(float)
    won_amounts, lost_count, won_count, open_count = [], 0, 0, 0
    open_amount, qualified_count = 0.0, 0
    cycle_days, stuck = [], []
    pipeline_value = 0.0
    weighted_pipeline = 0.0

    # per-stage accumulators (open deals only, for age/velocity & weighted value)
    stage_open_count = Counter()
    stage_open_amount = defaultdict(float)
    stage_age_open = defaultdict(list)   # age in current stage (or since creation) for open deals
    stage_weighted = defaultdict(float)

    # per-owner accumulators
    owner_won = Counter()
    owner_closed = Counter()
    owner_won_amts = defaultdict(list)
    owner_open_amt = defaultdict(float)

    # slippage / no-show: open deals whose expected_close_date is already in the past
    slipped, expected_to_close = 0, 0

    def stage_age(d, created):
        """Days the deal has sat in its current stage (fallback: age since creation)."""
        entered = parse_dt(d.get("stage_entered_at"))
        ref = entered or created
        return days_between(ref, now)

    for d in scoped:
        stage = (d.get("stage") or "").strip()
        st_l = stage.lower()
        stage_counts[stage or "(blank)"] += 1
        src = (d.get("source") or "(blank)").strip() or "(blank)"
        source_counts[src] += 1
        owner = (d.get("owner") or "(unassigned)").strip() or "(unassigned)"
        amt = d.get("amount")
        try:
            amt = float(amt) if amt not in (None, "") else None
        except (ValueError, TypeError):
            amt = None
        created = parse_dt(d.get("created_at"))
        closed = parse_dt(d.get("closed_at"))

        is_won = st_l in won
        is_lost = st_l in lost
        is_open = not (is_won or is_lost)

        if st_l in qualified or is_won:
            qualified_count += 1

        if is_won:
            won_count += 1
            owner_won[owner] += 1
            owner_closed[owner] += 1
            if amt:
                won_amounts.append(amt)
                owner_won_amts[owner].append(amt)
            source_won[src] += 1
            if amt:
                source_amt[src] += amt
            cd = days_between(created, closed or now)
            if cd is not None:
                cycle_days.append(cd)
        elif is_lost:
            lost_count += 1
            owner_closed[owner] += 1
        else:
            open_count += 1
            stage_open_count[stage or "(blank)"] += 1
            if amt:
                open_amount += amt
                pipeline_value += amt
                stage_open_amount[stage or "(blank)"] += amt
                owner_open_amt[owner] += amt
            # weighted pipeline = amount x stage probability
            prob = stage_probability(st_l, explicit_prob)
            if amt and prob is not None:
                weighted_pipeline += amt * prob
                stage_weighted[stage or "(blank)"] += amt * prob
            # per-stage age
            age_in_stage = stage_age(d, created)
            if age_in_stage is not None:
                stage_age_open[stage or "(blank)"].append(age_in_stage)
            # stuck: open longer than expected cycle
            age = days_between(created, now)
            if args.expected_cycle_days and age is not None and age > args.expected_cycle_days:
                stuck.append({"id": d.get("id"), "name": d.get("name"), "stage": stage,
                              "amount": amt, "age_days": age, "owner": owner})
            # slippage: expected close already passed but still open
            ecd = parse_dt(d.get("expected_close_date"))
            if ecd:
                expected_to_close += 1
                if ecd < now:
                    slipped += 1

    closed_total = won_count + lost_count
    win_rate = (won_count / closed_total) if closed_total else None
    qual_rate = (qualified_count / total) if total else None
    avg_cycle = (sum(cycle_days) / len(cycle_days)) if cycle_days else None
    med_cycle = median(cycle_days)
    avg_won = (sum(won_amounts) / len(won_amounts)) if won_amounts else None

    # coverage: open pipeline / target; weighted-coverage: weighted / quota (or target)
    coverage = (open_amount / args.target_pipeline) if args.target_pipeline else None
    quota = args.quota or args.target_pipeline
    weighted_coverage = (weighted_pipeline / quota) if quota else None

    # ---- per-stage block: count, open value, weighted value, avg/median age ----
    per_stage = []
    stage_keys = stage_order if stage_order else list(stage_counts.keys())
    # include any stages present but not in the declared order
    for k in stage_counts:
        if k not in stage_keys:
            stage_keys.append(k)
    for stg in stage_keys:
        ages = stage_age_open.get(stg, [])
        per_stage.append({
            "stage": stg,
            "open_deals": stage_open_count.get(stg, 0),
            "open_value": round(stage_open_amount.get(stg, 0.0), 2),
            "weighted_value": round(stage_weighted.get(stg, 0.0), 2),
            "avg_age_days": round(sum(ages) / len(ages), 1) if ages else None,
            "median_age_days": median(ages),
        })

    # ---- stage-to-stage conversion (requires --stage-order) ----
    # Conversion[i] = count(deals that have reached stage i+1 or beyond, incl. won) /
    #                 count(deals that reached stage i or beyond). A deal "reached" stage S
    #                 if its current stage index >= S's index, OR it is won (terminal).
    conversion = []
    if stage_order:
        idx = {s.lower(): i for i, s in enumerate(stage_order)}
        # treat won as the terminal stage index = len; lost deals are excluded from the
        # forward-conversion denominator at the stage they died (they reached their stage).
        reached = [0] * (len(stage_order) + 1)  # reached[i] = # deals that got to stage>=i
        for d in scoped:
            st_l = (d.get("stage") or "").strip().lower()
            if st_l in lost:
                # a lost deal reached up to its (unknown post-mortem) stage; use its stage idx
                di = idx.get(st_l)
                if di is None:
                    continue
                for i in range(di + 1):
                    reached[i] += 1
                continue
            if st_l in won:
                di = len(stage_order)  # reached everything
            else:
                di = idx.get(st_l)
                if di is None:
                    continue
            for i in range(di + 1):
                reached[i] += 1
        for i in range(len(stage_order)):
            denom = reached[i]
            numer = reached[i + 1]
            conversion.append({
                "from_stage": stage_order[i],
                "to_stage": stage_order[i + 1] if i + 1 < len(stage_order) else "(closed/won)",
                "reached_from": denom,
                "reached_to": numer,
                "conversion_rate": round(numer / denom, 4) if denom else None,
            })

    # ---- per-owner block ----
    owners = sorted(set(list(owner_closed) + list(owner_open_amt)))
    owner_rows = []
    for o in owners:
        cl = owner_closed.get(o, 0)
        w = owner_won.get(o, 0)
        amts = owner_won_amts.get(o, [])
        owner_rows.append({
            "owner": o,
            "won": w,
            "closed": cl,
            "win_rate": round(w / cl, 4) if cl else None,
            "avg_won_amount": round(sum(amts) / len(amts), 2) if amts else None,
            "open_pipeline_value": round(owner_open_amt.get(o, 0.0), 2),
        })
    owner_rows.sort(key=lambda r: (r["win_rate"] is not None, r["win_rate"] or 0), reverse=True)

    source_rows = []
    for src, cnt in source_counts.most_common():
        w = source_won.get(src, 0)
        source_rows.append({"source": src, "deals": cnt, "won": w,
                            "won_value": round(source_amt.get(src, 0.0), 2),
                            "win_rate": (w / cnt) if cnt else None})

    slippage_rate = round(slipped / expected_to_close, 4) if expected_to_close else None

    metrics = {
        "period": {"start": args.period_start, "end": args.period_end},
        "volume": {
            "total_deals": total, "open": open_count, "won": won_count, "lost": lost_count,
            "open_pipeline_value": round(open_amount, 2),
        },
        "qualification": {
            "qualified_deals": qualified_count,
            "qualification_rate": round(qual_rate, 4) if qual_rate is not None else None,
        },
        "source_attribution": source_rows,
        "stage_distribution": dict(stage_counts),
        "per_stage": per_stage,
        "stage_conversion": conversion,
        "velocity": {
            "avg_cycle_days_won": round(avg_cycle, 1) if avg_cycle is not None else None,
            "median_cycle_days_won": med_cycle,
            "won_count_with_dates": len(cycle_days),
        },
        "stuck_deals": sorted(stuck, key=lambda x: (x["age_days"] or 0), reverse=True),
        "slippage": {
            "open_with_expected_close": expected_to_close,
            "slipped_past_expected_close": slipped,
            "slippage_rate": slippage_rate,
        },
        "win_loss": {
            "won": won_count, "lost": lost_count, "closed_total": closed_total,
            "win_rate": round(win_rate, 4) if win_rate is not None else None,
            "avg_won_amount": round(avg_won, 2) if avg_won is not None else None,
        },
        "by_owner": owner_rows,
        "forecast": {
            "open_pipeline_value": round(pipeline_value, 2),
            "weighted_pipeline_value": round(weighted_pipeline, 2),
            "target_pipeline": args.target_pipeline or None,
            "quota": quota or None,
            "coverage_ratio": round(coverage, 2) if coverage is not None else None,
            "coverage_tier": coverage_tier(coverage),
            "weighted_coverage_ratio": round(weighted_coverage, 2) if weighted_coverage is not None else None,
            "weighted_coverage_tier": coverage_tier(weighted_coverage),
        },
        "data_quality": {
            "deals_missing_amount": sum(1 for d in scoped if not d.get("amount")),
            "deals_missing_source": sum(1 for d in scoped if not (d.get("source") or "").strip()),
            "deals_missing_created_at": sum(1 for d in scoped if not parse_dt(d.get("created_at"))),
            "deals_missing_owner": sum(1 for d in scoped if not (d.get("owner") or "").strip()),
            "deals_missing_stage": sum(1 for d in scoped if not (d.get("stage") or "").strip()),
            "open_deals_missing_expected_close": sum(
                1 for d in scoped
                if (d.get("stage") or "").strip().lower() not in won
                and (d.get("stage") or "").strip().lower() not in lost
                and not parse_dt(d.get("expected_close_date"))),
            "stages_without_probability": sorted({
                (d.get("stage") or "").strip() for d in scoped
                if (d.get("stage") or "").strip().lower() not in won
                and (d.get("stage") or "").strip().lower() not in lost
                and stage_probability((d.get("stage") or "").strip().lower(), explicit_prob) is None
                and (d.get("stage") or "").strip()}),
        },
    }

    out = json.dumps(metrics, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"metrics for {total} deals -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
