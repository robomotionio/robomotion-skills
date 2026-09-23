#!/usr/bin/env python3
"""Google Trends through Scrape.do (added by Robomotion).

Needs SCRAPEDO_TOKEN. SCRAPEDO_GEO (or --geo) picks the country; each call
costs Scrape.do credits (10 at the time of writing).

    google_trends.py rising "sourdough" [--geo us] [--date "today 1-m"] [--gprop youtube|news]
    google_trends.py interest "sourdough" [--geo us] [--date "today 3-m"]
    google_trends.py trending [--geo tr] [--hours 24|48|168|4] [--cat 18]

rising    queries and topics searched more than before, "Breakout" first:
          the growth signal for a topic.
interest  searches over time (0-100) and whether the latest week is above
          the window's average.
trending  what the whole country is searching for right now.

Prints markdown; --json prints the raw response instead.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import http, scrapedo  # noqa: E402


def _geo(args) -> str:
    value = (args.geo or scrapedo.geo() or "us").strip().upper()
    return value


def _get(name: str, params: dict) -> dict:
    try:
        return http.request("GET", scrapedo.plugin_url(name, params), timeout=60, retries=2)
    except http.HTTPError as exc:
        body = getattr(exc, "body", "") or ""
        raise SystemExit(f"Scrape.do {name} failed: {exc} {body[:200]}")


def cmd_rising(args) -> str:
    params = {"q": args.query, "geo": _geo(args), "date": args.date, "gprop": args.gprop}
    queries = _get("trends", {**params, "data_type": "RELATED_QUERIES"})
    topics = _get("trends", {**params, "data_type": "RELATED_TOPICS"})
    if args.json:
        return json.dumps({"related_queries": queries.get("related_queries"),
                           "related_topics": topics.get("related_topics")}, indent=1)
    where = f"{_geo(args)}, {args.date}" + (f", {args.gprop}" if args.gprop else "")
    lines = [f"## Google Trends: rising around \"{args.query}\" ({where})", ""]
    rq = (queries.get("related_queries") or {}).get("rising") or []
    rt = (topics.get("related_topics") or {}).get("rising") or []
    if not rq and not rt:
        lines.append("No rising queries or topics: search interest here is too low or flat.")
    if rq:
        lines.append("Rising searches:")
        for row in rq[: args.limit]:
            lines.append(f"- {row.get('query')}: {row.get('value')}")
    if rt:
        lines.append("")
        lines.append("Rising topics:")
        for row in rt[: args.limit]:
            topic = row.get("topic") or {}
            kind = f" ({topic.get('type')})" if topic.get("type") else ""
            lines.append(f"- {topic.get('title')}{kind}: {row.get('value')}")
    lines.append("")
    lines.append("\"Breakout\" means growth above 5000%. Percentages compare with the previous period of the same length.")
    return "\n".join(lines)


def cmd_interest(args) -> str:
    data = _get("trends", {"q": args.query, "geo": _geo(args), "date": args.date,
                           "gprop": args.gprop, "data_type": "TIMESERIES"})
    if args.json:
        return json.dumps(data.get("interest_over_time"), indent=1)
    rows = ((data.get("interest_over_time") or {}).get("timeline_data")) or []
    points = []
    for row in rows:
        values = row.get("values") or [{}]
        points.append((row.get("date"), int(values[0].get("extracted_value") or 0)))
    lines = [f"## Google Trends: interest in \"{args.query}\" ({_geo(args)}, {args.date})", ""]
    if not points:
        lines.append("No data.")
        return "\n".join(lines)
    avg = sum(v for _, v in points) / len(points)
    last = points[-7:]
    last_avg = sum(v for _, v in last) / len(last)
    peak = max(points, key=lambda p: p[1])
    direction = "above" if last_avg > avg * 1.1 else "below" if last_avg < avg * 0.9 else "about level with"
    lines.append(f"Latest {len(last)} points average {last_avg:.0f}, {direction} the window average of {avg:.0f}. Peak {peak[1]} on {peak[0]}.")
    lines.append("")
    lines.append(" ".join(f"{d}: {v}" for d, v in points[-14:]))
    return "\n".join(lines)


def cmd_trending(args) -> str:
    data = _get("trending", {"geo": _geo(args), "hours": args.hours, "cat": args.cat, "hl": args.hl})
    if args.json:
        return json.dumps(data.get("trends"), indent=1)
    trends = data.get("trends") or []
    lines = [f"## Trending searches now ({_geo(args)}, last {args.hours}h)", ""]
    for row in trends[: args.limit]:
        volume = row.get("search_volume")
        growth = row.get("growth_percentage")
        extra = ", ".join(x for x in (
            f"{volume:,}+ searches" if isinstance(volume, int) else "",
            f"+{growth}%" if growth else "",
            row.get("status") or "",
        ) if x)
        related = ", ".join((row.get("related_queries") or [])[:4])
        lines.append(f"- {row.get('title')} ({extra})" + (f": {related}" if related else ""))
    if not trends:
        lines.append("Nothing returned.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--geo", help="two-letter country (default SCRAPEDO_GEO, else US)")
        p.add_argument("--limit", type=int, default=15)
        p.add_argument("--json", action="store_true")

    p = sub.add_parser("rising"); p.add_argument("query"); common(p)
    p.add_argument("--date", default="today 1-m"); p.add_argument("--gprop", choices=["youtube", "news", "images", "froogle"])
    p.set_defaults(func=cmd_rising)
    p = sub.add_parser("interest"); p.add_argument("query"); common(p)
    p.add_argument("--date", default="today 3-m"); p.add_argument("--gprop", choices=["youtube", "news", "images", "froogle"])
    p.set_defaults(func=cmd_interest)
    p = sub.add_parser("trending"); common(p)
    p.add_argument("--hours", type=int, choices=[4, 24, 48, 168], default=24)
    p.add_argument("--cat", type=int, help="Google Trends category id (e.g. 18 technology, 17 sports)")
    p.add_argument("--hl", default="en")
    p.set_defaults(func=cmd_trending)

    args = parser.parse_args(argv)
    if not scrapedo.enabled():
        print("Google Trends needs SCRAPEDO_TOKEN (a Scrape.do API token). Without it, use last30days.py alone.", file=sys.stderr)
        return 2
    print(args.func(args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
