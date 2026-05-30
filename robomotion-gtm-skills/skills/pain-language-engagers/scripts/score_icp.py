#!/usr/bin/env python3
"""score_icp.py — deterministic 0-100 fit + tier A/B/C with a PAIN x ICP x ROLE intent model.

The score combines a FIT component (does this person match the ICP config?) and an INTENT
component (how strongly did they voice/resonate with the pain?). The intent model is the
per-skill differentiator:
  - post AUTHORS score higher than ENGAGERS (they VOICED the pain, not just liked it),
  - more matched_pain_terms => higher intent (stronger expressed pain),
  - commenters > reactors (a comment is a stronger signal than a like).

Score = round(FIT_WEIGHT*fit + INTENT_WEIGHT*intent)  (each sub-score 0-100).
Tiers:  A >= --tier-a (default 75), B >= --tier-b (default 50), else C.
Every lead gets a scoring_breakdown so the ranking is auditable.

ICP config (icp.example.json):
  {"target_titles":[...], "target_seniorities":[...], "target_industries":[...],
   "company_size_min":N, "company_size_max":N, "exclude_titles":[...],
   "competitors":[...], "geos":[...]}

Example:
  score_icp.py --input enriched.json --icp icp.example.json \
      --fit-weight 0.55 --intent-weight 0.45 --output scored.json
"""
import argparse
import json
import sys


def lc(s):
    return (s or "").lower()


def lc_list(xs):
    return [lc(x) for x in (xs or []) if x]


def fit_score(lead, icp):
    """0-100 ICP fit. Disqualifiers (exclude title / competitor) zero it out."""
    title = lc(lead.get("title") or lead.get("headline"))
    seniority = lc(lead.get("seniority"))
    industry = lc(lead.get("industry"))
    company = lc(lead.get("company"))
    loc = lc(lead.get("location"))
    size = lead.get("company_size")
    bd = {}

    # hard disqualifiers
    for x in lc_list(icp.get("exclude_titles")):
        if x and x in title:
            return 0, {"disqualified": f"exclude_title:{x}"}
    for x in lc_list(icp.get("competitors")):
        if x and x in company:
            return 0, {"disqualified": f"competitor:{x}"}

    score = 0.0
    # title match (the strongest fit signal): 40
    titles = lc_list(icp.get("target_titles"))
    if titles:
        if any(t in title for t in titles):
            score += 40; bd["title"] = 40
        else:
            bd["title"] = 0
    else:
        score += 20; bd["title"] = "n/a(+20)"

    # seniority: 20
    sens = lc_list(icp.get("target_seniorities"))
    if sens:
        if any(s in seniority for s in sens):
            score += 20; bd["seniority"] = 20
        else:
            bd["seniority"] = 0
    else:
        score += 10; bd["seniority"] = "n/a(+10)"

    # industry: 15
    inds = lc_list(icp.get("target_industries"))
    if inds:
        if any(i in industry for i in inds):
            score += 15; bd["industry"] = 15
        else:
            bd["industry"] = 0
    else:
        score += 8; bd["industry"] = "n/a(+8)"

    # company size band: 15
    lo, hi = icp.get("company_size_min"), icp.get("company_size_max")
    if (lo or hi) and isinstance(size, (int, float)) and size:
        ok = (lo is None or size >= lo) and (hi is None or size <= hi)
        score += 15 if ok else 0
        bd["company_size"] = 15 if ok else 0
    else:
        score += 8; bd["company_size"] = "n/a(+8)"

    # geo: 10
    geos = lc_list(icp.get("geos"))
    if geos:
        if any(g in loc for g in geos):
            score += 10; bd["geo"] = 10
        else:
            bd["geo"] = 0
    else:
        score += 5; bd["geo"] = "n/a(+5)"

    return min(100.0, score), bd


def intent_score(lead, max_terms_ref=3):
    """0-100 expressed-pain intent. AUTHOR >> ENGAGER; more pain terms => higher;
    comment > reaction."""
    role = lc(lead.get("role"))
    terms = [t for t in (lead.get("matched_pain_terms") or []) if t]
    n = len(terms)
    bd = {}

    # base by role: author VOICED the pain
    if role == "author" or lead.get("author_intent"):
        base = 70; bd["role"] = "author(+70)"
    else:
        base = 35; bd["role"] = "engager(+35)"

    # pain-term strength: up to +20, scaled by count vs reference
    term_pts = min(20.0, (n / max(1, max_terms_ref)) * 20.0)
    bd["pain_terms"] = round(term_pts, 1)
    bd["pain_terms_matched"] = terms

    # engagement quality: comment beats a bare reaction (engagers only; authors capped)
    eng = lc(lead.get("engagement_type"))
    comment = (lead.get("comment_text") or "").strip()
    if role != "author":
        if comment or "comment" in eng:
            base += 10; bd["engagement_quality"] = "comment(+10)"
        else:
            bd["engagement_quality"] = "reaction(+0)"

    return min(100.0, base + term_pts), bd


def tier(score, a, b):
    return "A" if score >= a else ("B" if score >= b else "C")


def main():
    ap = argparse.ArgumentParser(description="Deterministic pain x ICP x role fit/intent scoring.")
    ap.add_argument("--input", required=True, help="enriched.json (or engagers.json)")
    ap.add_argument("--icp", required=True, help="ICP config JSON (see icp.example.json)")
    ap.add_argument("--fit-weight", type=float, default=0.55)
    ap.add_argument("--intent-weight", type=float, default=0.45)
    ap.add_argument("--tier-a", type=float, default=75.0)
    ap.add_argument("--tier-b", type=float, default=50.0)
    ap.add_argument("--max-terms-ref", type=int, default=3,
                    help="pain-term count that saturates the term bonus")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        leads = json.load(f)
    if isinstance(leads, dict):
        sys.exit("ERROR: --input looks like a degrade plan, not leads.")
    with open(args.icp, encoding="utf-8") as f:
        icp = json.load(f)

    wf, wi = args.fit_weight, args.intent_weight
    tot = wf + wi or 1.0
    wf, wi = wf / tot, wi / tot  # normalize

    out = []
    for lead in leads:
        fit, fbd = fit_score(lead, icp)
        intent, ibd = intent_score(lead, args.max_terms_ref)
        score = round(wf * fit + wi * intent)
        row = dict(lead)
        row["fit_score"] = round(fit)
        row["intent_score"] = round(intent)
        row["score"] = score
        row["tier"] = tier(score, args.tier_a, args.tier_b)
        row["scoring_breakdown"] = {
            "weights": {"fit": round(wf, 3), "intent": round(wi, 3)},
            "fit": fbd, "intent": ibd}
        out.append(row)

    out.sort(key=lambda r: r["score"], reverse=True)

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    a = sum(1 for r in out if r["tier"] == "A")
    b = sum(1 for r in out if r["tier"] == "B")
    print(f"scored {len(out)} leads -> A:{a} B:{b} C:{len(out)-a-b} -> {args.output}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
