#!/usr/bin/env python3
"""analyze_emails.py — deterministic email-performance metrics for sales coaching.

NO LLM. Reads an emails CSV (the rep's sent campaigns/templates + outcomes) and computes
reply rates per template and a top-vs-bottom split so the agent can reconstruct the rep's
winning patterns. The agent reads the actual copy + replies to judge *why* and to grade.

CSV shape (case-insensitive headers; extra columns ignored):
  template, sends, replies, positive_replies   (one row per template/variant)
optional: subject, body  (passed through for the agent to grade)

Example:
  analyze_emails.py --input emails.csv --top-n 3 --output email_metrics.json
"""
import argparse
import csv
import json
import sys


def inum(v):
    try:
        return int(float(str(v).replace(",", "")))
    except (ValueError, TypeError):
        return 0


def rate(num, den):
    return round(num / den, 4) if den else None


def main():
    ap = argparse.ArgumentParser(description="Deterministic email-performance metrics (reply rates).")
    ap.add_argument("--input", required=True, help="emails CSV (template,sends,replies,positive_replies)")
    ap.add_argument("--top-n", type=int, default=3, help="how many top/bottom templates to flag")
    ap.add_argument("--output", default="-", help="output metrics JSON (default stdout)")
    args = ap.parse_args()

    rows = []
    with open(args.input, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rl = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
            sends = inum(rl.get("sends") or rl.get("sent"))
            replies = inum(rl.get("replies") or rl.get("replied"))
            pos = inum(rl.get("positive_replies") or rl.get("positive"))
            rows.append({
                "template": rl.get("template") or rl.get("subject") or f"row{len(rows)+1}",
                "subject": rl.get("subject", ""),
                "body": rl.get("body", ""),
                "sends": sends, "replies": replies, "positive_replies": pos,
                "reply_rate": rate(replies, sends),
                "positive_rate": rate(pos, sends),
            })

    total_sends = sum(r["sends"] for r in rows)
    total_replies = sum(r["replies"] for r in rows)

    # rank only templates with enough volume to be meaningful (>=100 sends preferred,
    # else all) — keep the threshold note for the agent.
    ranked = sorted([r for r in rows if r["reply_rate"] is not None],
                    key=lambda r: r["reply_rate"], reverse=True)
    enough = [r for r in ranked if r["sends"] >= 100]
    pool = enough if enough else ranked

    result = {
        "summary": {
            "templates": len(rows),
            "total_sends": total_sends,
            "total_replies": total_replies,
            "overall_reply_rate": rate(total_replies, total_sends),
            "min_sends_for_ranking": 100,
            "ranking_pool_met_threshold": bool(enough),
        },
        "top_templates": pool[: args.top_n],
        "bottom_templates": pool[-args.top_n:][::-1] if len(pool) > args.top_n else [],
        "templates": rows,
    }

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"email metrics for {len(rows)} templates -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
