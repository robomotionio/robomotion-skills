#!/usr/bin/env python3
"""score_icp.py — deterministic 0-100 ICP-fit score + A/B/C tier per engager.

Engine step 4: turn enriched engagers into a tiered, auditable lead list. The score
combines two halves:

  FIT  (firmographic match to your ICP config): target titles, seniorities, employee
       ranges, industries, keywords.
  INTENT (how warm the engagement signal is): engagement_type weight (a thoughtful
       comment >> a like) combined with recency of the post they engaged.

Final score = fit_weight*FIT + intent_weight*INTENT  (defaults 0.6 / 0.4), 0-100.
Tiers from --tier-a / --tier-b thresholds (default A>=75, B>=50, else C).

Every lead carries a scoring_breakdown so a human/agent can audit WHY it tiered where it
did. The agent still does the final qualitative review (e.g. read the comment_text).

Deterministic, stdlib only — no network, no LLM.

Examples:
  score_icp.py --input enriched.json --icp icp.example.json --output scored.json
  score_icp.py --input enriched.json --icp icp.example.json --tier-a 80 --tier-b 55
"""
import argparse
import json
import sys
from datetime import datetime, timezone

# Intent weight by engagement type — a comment/repost signals far more than a passive like.
ENGAGEMENT_WEIGHT = {"comment": 1.0, "repost": 0.85, "reaction": 0.45, "like": 0.4}


def parse_emp(size):
    """Coerce company_size (int or 'min,max' or '51-200') to an int headcount estimate."""
    if size is None or size == "":
        return None
    if isinstance(size, (int, float)):
        return int(size)
    s = str(size).replace(" ", "")
    for sep in (",", "-", "to"):
        if sep in s:
            lo, _, hi = s.partition(sep)
            try:
                return (int(lo) + int(hi)) // 2
            except ValueError:
                return None
    try:
        return int(s)
    except ValueError:
        return None


def in_any_range(n, ranges):
    if n is None:
        return None
    for r in ranges:
        lo, hi = r
        if (lo is None or n >= lo) and (hi is None or n <= hi):
            return True
    return False


def recency_factor(posted_at, half_life_days):
    """1.0 for a post today, decaying linearly to 0 at 2*half_life. Unknown -> neutral 0.5."""
    if not posted_at:
        return 0.5
    dt = None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(posted_at[:26], fmt)
            break
        except (ValueError, TypeError):
            continue
    if dt is None:
        return 0.5
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - dt).days
    if age <= 0:
        return 1.0
    span = 2 * half_life_days
    return max(0.0, 1.0 - (age / span)) if span else 0.5


def fit_score(lead, icp):
    """0-100 firmographic fit + per-component breakdown. Components present in the ICP
    config share the weight equally; missing lead data on a component scores 0 for it."""
    title = (lead.get("title") or lead.get("headline") or "").lower()
    seniority = (lead.get("seniority") or "").lower()
    industry = (lead.get("industry") or "").lower()
    blob = " ".join(str(lead.get(k, "")) for k in
                    ("title", "headline", "company", "industry", "comment_text")).lower()
    emp = parse_emp(lead.get("company_size"))

    comps, bd = [], {}
    if icp.get("titles"):
        hit = any(t.lower() in title for t in icp["titles"])
        comps.append(("title", hit)); bd["title_match"] = hit
    if icp.get("seniorities"):
        hit = any(s.lower() in seniority or s.lower() in title for s in icp["seniorities"])
        comps.append(("seniority", hit)); bd["seniority_match"] = hit
    if icp.get("employee_ranges"):
        ranges = [tuple(r) for r in icp["employee_ranges"]]
        res = in_any_range(emp, ranges)
        comps.append(("employees", bool(res))); bd["employee_match"] = res
    if icp.get("industries"):
        hit = any(i.lower() in industry or i.lower() in blob for i in icp["industries"])
        comps.append(("industry", hit)); bd["industry_match"] = hit
    if icp.get("keywords"):
        hit = any(k.lower() in blob for k in icp["keywords"])
        comps.append(("keywords", hit)); bd["keyword_match"] = hit

    if not comps:
        return 50.0, {"note": "empty ICP config -> neutral fit"}
    hits = sum(1 for _, h in comps if h)
    score = 100.0 * hits / len(comps)
    bd["fit_components_hit"] = f"{hits}/{len(comps)}"
    bd["fit_score"] = round(score, 1)
    # Hard-exclude on negative keywords (e.g. intern/student) — zero the fit.
    if icp.get("exclude_keywords") and any(x.lower() in blob for x in icp["exclude_keywords"]):
        bd["excluded"] = True
        return 0.0, bd
    return score, bd


def intent_score(lead, half_life_days):
    etype = (lead.get("engagement_type") or "reaction").lower()
    ew = ENGAGEMENT_WEIGHT.get(etype, 0.45)
    rf = recency_factor(lead.get("posted_at") or lead.get("post_posted_at"), half_life_days)
    # Multiplicative: a stale like is weak; a fresh comment is hot.
    score = 100.0 * ew * rf
    bd = {"engagement_type": etype, "engagement_weight": ew,
          "recency_factor": round(rf, 3), "intent_score": round(score, 1)}
    if lead.get("comment_text"):
        bd["has_comment_text"] = True
    return score, bd


def main():
    ap = argparse.ArgumentParser(description="Deterministic ICP-fit + intent scoring with A/B/C tiers.")
    ap.add_argument("--input", required=True, help="JSON list of enriched engagers")
    ap.add_argument("--icp", required=True, help="ICP config JSON (see icp.example.json)")
    ap.add_argument("--fit-weight", type=float, default=0.6)
    ap.add_argument("--intent-weight", type=float, default=0.4)
    ap.add_argument("--half-life-days", type=int, default=14, help="recency half-life (default 14)")
    ap.add_argument("--tier-a", type=float, default=75.0)
    ap.add_argument("--tier-b", type=float, default=50.0)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        leads = json.load(f)
    with open(args.icp, encoding="utf-8") as f:
        icp = json.load(f)

    wsum = args.fit_weight + args.intent_weight
    fw = args.fit_weight / wsum if wsum else 0.5
    iw = args.intent_weight / wsum if wsum else 0.5

    out = []
    for lead in leads:
        fs, fbd = fit_score(lead, icp)
        is_, ibd = intent_score(lead, args.half_life_days)
        total = round(fw * fs + iw * is_, 1)
        tier = "A" if total >= args.tier_a else "B" if total >= args.tier_b else "C"
        scored = dict(lead)
        scored["icp_score"] = total
        scored["tier"] = tier
        scored["scoring_breakdown"] = {
            "weights": {"fit": round(fw, 2), "intent": round(iw, 2)},
            "fit": fbd, "intent": ibd,
            "total": total, "tier": tier,
        }
        out.append(scored)

    out.sort(key=lambda x: x["icp_score"], reverse=True)
    tiers = {"A": 0, "B": 0, "C": 0}
    for s in out:
        tiers[s["tier"]] += 1

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    print(f"scored {len(out)} leads -> A:{tiers['A']} B:{tiers['B']} C:{tiers['C']} "
          f"-> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
