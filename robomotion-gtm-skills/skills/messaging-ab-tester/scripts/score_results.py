#!/usr/bin/env python3
"""score_results.py — Deterministically score messaging A/B variant metrics and apply the
significance gate, per the fixed framework in the design contract.

This is the deterministic half of the analysis: it normalizes per-variant metrics, computes
weighted scores per channel, applies the significance thresholds, and ranks variants. It does
NOT write the "why it won / ICP psychology" narrative — that is the host agent's synthesis,
written from this scored output.

Weights (fixed by contract):
  LinkedIn: engagement 30 / comment_quality 30 / impressions 20 / profile_visits 20
  Email:    open_rate 30 / reply_rate 40 / positive_reply_rate 30

Significance gate (fixed by contract):
  Email   : >= 50 sends/variant = directional; 200+ = confident.
            A winner requires > 20% relative lift over the runner-up.
  LinkedIn: >= 500 impressions/post = scorable; single posts are directional only.

Input JSON (per channel an array of variant objects). Numbers are raw counts/rates; the
script normalizes each metric to its max within the channel before weighting. Example:

  {
    "linkedin": [
      {"variant":"A","impressions":820,"engagements":48,"comment_quality":7,"profile_visits":12},
      {"variant":"B","impressions":760,"engagements":31,"comment_quality":4,"profile_visits":9}
    ],
    "email": [
      {"variant":"A","sends":210,"opens":105,"replies":18,"positive_replies":11},
      {"variant":"B","sends":205,"opens":78,"replies":9,"positive_replies":3}
    ]
  }

Run:
  score_results.py --input results.json --output scored.json
"""
import argparse
import json
import sys

LINKEDIN_WEIGHTS = {"engagement": 0.30, "comment_quality": 0.30,
                    "impressions": 0.20, "profile_visits": 0.20}
EMAIL_WEIGHTS = {"open_rate": 0.30, "reply_rate": 0.40, "positive_reply_rate": 0.30}


def safe_div(a, b):
    return a / b if b else 0.0


def derive_linkedin(v):
    imp = float(v.get("impressions", 0) or 0)
    return {
        "variant": v.get("variant", "?"),
        "impressions": imp,
        "engagement": safe_div(float(v.get("engagements", 0) or 0), imp),  # engagement rate
        "comment_quality": float(v.get("comment_quality", 0) or 0),       # 0-10 agent/manual rating
        "profile_visits": float(v.get("profile_visits", 0) or 0),
        "scorable": imp >= 500,
    }


def derive_email(v):
    sends = float(v.get("sends", 0) or 0)
    return {
        "variant": v.get("variant", "?"),
        "sends": sends,
        "open_rate": safe_div(float(v.get("opens", 0) or 0), sends),
        "reply_rate": safe_div(float(v.get("replies", 0) or 0), sends),
        "positive_reply_rate": safe_div(float(v.get("positive_replies", 0) or 0), sends),
        "directional": sends >= 50,
        "confident": sends >= 200,
    }


def normalize_and_score(rows, weights, metric_keys):
    """Min-max-ish normalize each metric to its max in the set, then weight-sum."""
    maxes = {k: max((r[k] for r in rows), default=0.0) for k in metric_keys}
    for r in rows:
        score = 0.0
        contrib = {}
        for k in metric_keys:
            norm = safe_div(r[k], maxes[k]) if maxes[k] else 0.0
            c = norm * weights[weight_key(k)]
            contrib[k] = round(c, 4)
            score += c
        r["weighted_score"] = round(score, 4)
        r["score_breakdown"] = contrib
    return rows


def weight_key(metric):
    # LinkedIn metric names already match weight keys except they are identical here.
    return metric


def rank(rows):
    return sorted(rows, key=lambda r: r["weighted_score"], reverse=True)


def call_winner_email(ranked):
    if len(ranked) < 1:
        return {"winner": None, "confidence": "none", "note": "no variants"}
    top = ranked[0]
    if not top["directional"]:
        return {"winner": top["variant"], "confidence": "insufficient",
                "note": "< 50 sends/variant — not even directional; do not call a winner"}
    if len(ranked) == 1:
        return {"winner": top["variant"],
                "confidence": "confident" if top["confident"] else "directional",
                "note": "single variant — no comparison"}
    runner = ranked[1]
    lift = safe_div(top["weighted_score"] - runner["weighted_score"], runner["weighted_score"])
    if lift <= 0.20:
        return {"winner": None, "confidence": "tie",
                "note": f"relative lift {lift:.0%} <= 20% threshold — too close to call"}
    conf = "confident" if top["confident"] and runner["confident"] else "directional"
    return {"winner": top["variant"], "runner_up": runner["variant"],
            "relative_lift": round(lift, 3), "confidence": conf,
            "note": f"{top['variant']} beats {runner['variant']} by {lift:.0%} (>20% gate)"}


def call_winner_linkedin(ranked):
    scorable = [r for r in ranked if r["scorable"]]
    if not scorable:
        return {"winner": ranked[0]["variant"] if ranked else None,
                "confidence": "insufficient",
                "note": "< 500 impressions/post — directional only, never confident"}
    top = scorable[0]
    if len(scorable) == 1:
        return {"winner": top["variant"], "confidence": "directional",
                "note": "single scorable post — directional"}
    runner = scorable[1]
    lift = safe_div(top["weighted_score"] - runner["weighted_score"], runner["weighted_score"])
    return {"winner": top["variant"], "runner_up": runner["variant"],
            "relative_lift": round(lift, 3), "confidence": "directional",
            "note": "LinkedIn organic single-post tests are directional by design"}


def main():
    ap = argparse.ArgumentParser(
        description="Score messaging A/B variants with the fixed weights + significance gate "
                    "(deterministic; agent writes the narrative).")
    ap.add_argument("--input", required=True, help="results JSON (linkedin/email arrays)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    try:
        with open(args.input, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        sys.exit(f"ERROR: input not found: {args.input}")
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: invalid JSON in {args.input}: {e}")

    out = {"channels": {}}

    if data.get("linkedin"):
        rows = [derive_linkedin(v) for v in data["linkedin"]]
        rows = normalize_and_score(rows, LINKEDIN_WEIGHTS,
                                   ["engagement", "comment_quality", "impressions", "profile_visits"])
        ranked = rank(rows)
        out["channels"]["linkedin"] = {
            "weights": LINKEDIN_WEIGHTS, "ranked": ranked,
            "verdict": call_winner_linkedin(ranked),
        }

    if data.get("email"):
        rows = [derive_email(v) for v in data["email"]]
        rows = normalize_and_score(rows, EMAIL_WEIGHTS,
                                   ["open_rate", "reply_rate", "positive_reply_rate"])
        ranked = rank(rows)
        out["channels"]["email"] = {
            "weights": EMAIL_WEIGHTS, "ranked": ranked,
            "verdict": call_winner_email(ranked),
        }

    if not out["channels"]:
        sys.exit("ERROR: input has neither 'linkedin' nor 'email' results.")

    # Surface per-channel winners so the agent can flag divergent results (signal, not noise).
    winners = {ch: d["verdict"].get("winner") for ch, d in out["channels"].items()}
    out["per_channel_winners"] = winners
    out["channels_disagree"] = len(set(v for v in winners.values() if v)) > 1

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"scored {len(out['channels'])} channel(s) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
