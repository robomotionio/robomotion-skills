#!/usr/bin/env python3
"""test_schedule.py — Lay out a deterministic A/B test schedule + split plan from the design
contract's rules. The host agent writes the variants and the strategic rationale; this just
produces the calendar and the significance-threshold table so the test design is consistent.

LinkedIn: consecutive posts, one per day, same time of day, organic only.
Email:    list split evenly across variants (>= 50/variant min), same send time/sender/CTA.

Significance thresholds emitted for the report:
  Email   : >= 50 sends/variant directional, 200+ confident, >20% relative lift to win.
  LinkedIn: >= 500 impressions/post scorable, single posts directional.

Example:
  test_schedule.py --channel both --num-variants 4 --start 2026-06-02 --post-time 09:00 \
      --linkedin-impressions 6000 --email-list 1200 --output schedule.json
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta


def build_linkedin(start, post_time, n, impressions):
    posts = []
    d = start
    for i in range(n):
        posts.append({
            "variant": chr(ord("A") + i),
            "post_date": d.isoformat(),
            "post_time": post_time,
            "format": "single organic post, similar length/format to the others",
        })
        d += timedelta(days=1)
    per_post = impressions // n if impressions and n else None
    return {
        "method": "consecutive daily organic posts, same time of day, no paid boost",
        "posts": posts,
        "expected_impressions_per_post": per_post,
        "scorable": (per_post is not None and per_post >= 500),
        "significance": {
            "scorable_threshold_impressions": 500,
            "note": "single-post organic tests are directional, never 'confident'",
        },
    }


def build_email(start, send_time, n, list_size, duration_days):
    per_variant = list_size // n if list_size and n else None
    return {
        "method": "A/B sequences, list split evenly, same send time/sender/CTA — only "
                  "the message changes",
        "send_date": start.isoformat(),
        "send_time": send_time,
        "duration_days": duration_days,
        "variants": [chr(ord("A") + i) for i in range(n)],
        "list_size": list_size,
        "sends_per_variant": per_variant,
        "directional": (per_variant is not None and per_variant >= 50),
        "confident": (per_variant is not None and per_variant >= 200),
        "significance": {
            "directional_threshold_sends": 50,
            "confident_threshold_sends": 200,
            "winner_relative_lift": 0.20,
            "note": "< 50 sends/variant = not directional; > 20% relative lift to call a winner",
        },
    }


def main():
    ap = argparse.ArgumentParser(
        description="Generate an A/B messaging test schedule + significance plan "
                    "(deterministic; agent writes variants + rationale).")
    ap.add_argument("--channel", choices=["linkedin", "email", "both"], required=True)
    ap.add_argument("--num-variants", type=int, default=4, help="3-5 (default 4)")
    ap.add_argument("--start", default="", help="start date YYYY-MM-DD (default today)")
    ap.add_argument("--post-time", default="09:00", help="LinkedIn post time HH:MM (default 09:00)")
    ap.add_argument("--send-time", default="09:00", help="email send time HH:MM (default 09:00)")
    ap.add_argument("--linkedin-impressions", type=int, default=0,
                    help="expected total LinkedIn impressions available")
    ap.add_argument("--email-list", type=int, default=0, help="email list size available")
    ap.add_argument("--duration-days", type=int, default=0,
                    help="email test window days (default 4: 3-5 day rule)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    if not 3 <= args.num_variants <= 5:
        print(f"WARNING: {args.num_variants} variants is outside the 3-5 sweet spot.",
              file=sys.stderr)

    if args.start:
        try:
            start = datetime.strptime(args.start, "%Y-%m-%d").date()
        except ValueError:
            sys.exit("ERROR: --start must be YYYY-MM-DD")
    else:
        start = date.today()

    duration = args.duration_days or 4  # 3-5 day default for email
    out = {"channel": args.channel, "num_variants": args.num_variants,
           "start": start.isoformat(), "plan": {}}

    if args.channel in ("linkedin", "both"):
        out["plan"]["linkedin"] = build_linkedin(
            start, args.post_time, args.num_variants, args.linkedin_impressions)
    if args.channel in ("email", "both"):
        out["plan"]["email"] = build_email(
            start, args.send_time, args.num_variants, args.email_list, duration)

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"schedule ({args.channel}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
