#!/usr/bin/env python3
"""score_icp.py — Stage 4: deterministic ICP-fit + intent scoring (0-100, tier A/B/C).

KOL audiences are BROAD, so the ICP filter must be STRICT. This script scores each enriched
engager on three deterministic axes and emits a transparent breakdown:

  ICP FIT (0-60)   title/seniority match, target vs exclude titles, industry match,
                   company-size band, geo, competitor employment (hard zero).
  INTENT (0-25)    engagement_type (comment > reaction) x recency of the post engaged.
  TOPIC (0-15)     the engaged post cleared the topic-relevance gate; comment text mentions
                   the topic -> stronger.

score = icp_fit + intent + topic, capped 0-100. Tier from --tier-a / --tier-b cutoffs.
HARD GATES (force tier C / drop): competitor employer, an excluded title, or ICP fit below
--min-icp-fit. By default only tier A/B survivors are written (--keep-c to keep all).

This is deterministic only — the agent does final human-readable review. Stdlib only.

Examples:
  score_icp.py --input enriched.json --icp icp.json --output scored.json
  score_icp.py --input enriched.json --icp icp.json --tier-a 75 --tier-b 55 --keep-c \
      --output scored_all.json
"""
import argparse
import json
import sys


def load_icp(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    # normalize all keyword lists to lowercase
    for k in ("target_titles", "exclude_titles", "target_seniorities", "industries",
              "competitors", "geos", "company_sizes"):
        cfg[k] = [str(x).strip().lower() for x in cfg.get(k, []) if str(x).strip()]
    cfg["topic_keywords"] = [str(x).strip().lower()
                             for x in cfg.get("topic_keywords", []) if str(x).strip()]
    return cfg


def any_in(needles, hay):
    return any(n in hay for n in needles)


def score_icp_fit(row, icp):
    """0-60 firmographic fit, plus hard-gate flags."""
    title = str(row.get("title") or row.get("headline") or "").lower()
    seniority = str(row.get("seniority") or "").lower()
    industry = str(row.get("industry") or "").lower()
    company = str(row.get("company") or "").lower()
    size = str(row.get("company_size") or "").lower()
    geo = str(row.get("location") or row.get("geo") or "").lower()

    bd, pts, gates = {}, 0.0, []

    # competitor employer = hard drop
    if icp["competitors"] and any_in(icp["competitors"], company):
        gates.append("competitor_employer")
    # excluded title = hard drop
    if icp["exclude_titles"] and any_in(icp["exclude_titles"], title):
        gates.append("excluded_title")

    # target titles (25)
    if icp["target_titles"]:
        if any_in(icp["target_titles"], title):
            bd["title_match"] = 25
        else:
            bd["title_match"] = 0
    else:
        bd["title_match"] = 12  # neutral when not specified
    pts += bd["title_match"]

    # seniority (12)
    if icp["target_seniorities"]:
        bd["seniority_match"] = 12 if (seniority and seniority in icp["target_seniorities"]) \
            or any_in(icp["target_seniorities"], title) else 0
    else:
        bd["seniority_match"] = 6
    pts += bd["seniority_match"]

    # industry (10)
    if icp["industries"]:
        bd["industry_match"] = 10 if industry and any_in(icp["industries"], industry) else 0
    else:
        bd["industry_match"] = 5
    pts += bd["industry_match"]

    # company size (8)
    if icp["company_sizes"]:
        bd["size_match"] = 8 if size and size in icp["company_sizes"] else 0
    else:
        bd["size_match"] = 4
    pts += bd["size_match"]

    # geo (5)
    if icp["geos"]:
        bd["geo_match"] = 5 if geo and any_in(icp["geos"], geo) else 0
    else:
        bd["geo_match"] = 3
    pts += bd["geo_match"]

    return round(min(60.0, pts), 1), bd, gates


def score_intent(row):
    """0-25 from engagement type x recency of the engaged post."""
    etype = str(row.get("engagement_type") or "reaction").lower()
    base = 18 if "comment" in etype else 10  # commenters > reactors

    days = row.get("posted_days_ago")
    if days is None:
        days = row.get("post_age_days")
    if isinstance(days, (int, float)):
        if days <= 7:
            recency = 7
        elif days <= 14:
            recency = 5
        elif days <= 30:
            recency = 3
        else:
            recency = 1
    else:
        recency = 3  # unknown -> neutral
    val = min(25.0, base + recency)
    return round(val, 1), {"engagement_base": base, "recency_bonus": recency}


def score_topic(row, icp):
    """0-15: engaged a topic-relevant post; comment mentions the topic -> stronger."""
    bd, pts = {}, 0.0
    # the post itself was gated to be topic-relevant in stage 1
    bd["post_topic_gate"] = 8
    pts += 8
    comment = str(row.get("comment_text") or "").lower()
    if comment and icp["topic_keywords"] and any_in(icp["topic_keywords"], comment):
        bd["comment_topic_mention"] = 7
        pts += 7
    else:
        bd["comment_topic_mention"] = 0
    return round(min(15.0, pts), 1), bd


def tier_of(score, gates, icp_fit, args):
    if gates:
        return "C"
    if icp_fit < args.min_icp_fit:
        return "C"
    if score >= args.tier_a:
        return "A"
    if score >= args.tier_b:
        return "B"
    return "C"


def main():
    ap = argparse.ArgumentParser(description="Deterministic ICP-fit + intent scoring (0-100, A/B/C).")
    ap.add_argument("--input", required=True, help="enriched.json from enrich_apollo.py")
    ap.add_argument("--icp", required=True, help="ICP config JSON (see icp.example.json)")
    ap.add_argument("--tier-a", type=float, default=70.0, help="min score for tier A")
    ap.add_argument("--tier-b", type=float, default=50.0, help="min score for tier B")
    ap.add_argument("--min-icp-fit", type=float, default=25.0,
                    help="min ICP-fit (of 60) to qualify above tier C")
    ap.add_argument("--keep-c", action="store_true", help="also write tier C / gated rows")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    icp = load_icp(args.icp)
    with open(args.input, encoding="utf-8") as f:
        rows = json.load(f)

    scored = []
    for row in rows:
        icp_fit, icp_bd, gates = score_icp_fit(row, icp)
        intent, intent_bd = score_intent(row)
        topic, topic_bd = score_topic(row, icp)
        total = round(min(100.0, icp_fit + intent + topic), 1)
        tier = tier_of(total, gates, icp_fit, args)
        out = dict(row)
        out["icp_score"] = total
        out["icp_tier"] = tier
        out["icp_gates"] = gates
        out["scoring_breakdown"] = {
            "icp_fit": {"total": icp_fit, **icp_bd},
            "intent": {"total": intent, **intent_bd},
            "topic": {"total": topic, **topic_bd},
            "hard_gates": gates,
        }
        scored.append(out)

    scored.sort(key=lambda r: r["icp_score"], reverse=True)
    written = scored if args.keep_c else [r for r in scored if r["icp_tier"] in ("A", "B")]

    n_a = sum(1 for r in scored if r["icp_tier"] == "A")
    n_b = sum(1 for r in scored if r["icp_tier"] == "B")
    n_c = sum(1 for r in scored if r["icp_tier"] == "C")
    payload = json.dumps(written, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    print(f"scored {len(scored)}: A={n_a} B={n_b} C={n_c}; wrote {len(written)} "
          f"({'A/B/C' if args.keep_c else 'A/B only'}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
