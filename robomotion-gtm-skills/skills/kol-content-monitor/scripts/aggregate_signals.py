#!/usr/bin/env python3
"""aggregate_signals.py — Deterministic aggregation + signal tagging for kol-content-monitor.

The host agent first scrapes posts (LinkedIn via linkedin-profile-post-scraper / X via
x-mention-tracker), filters by engagement, and labels each post with a 1-3 word topic
(that topic labeling is the LLM step — the agent does it). This script then does the
deterministic math: group posts by topic, count distinct KOLs + posts + total engagement per
topic, compare this run's per-topic counts to a stored history to detect spikes, and tag each
topic with signal types:

  Convergence : >= --convergence (default 3) distinct KOLs on a topic this week
  Spike       : posts this week >= --spike-factor x last week's (default 2x)
  Underdog    : exactly 1 KOL on the topic
  Controversy : avg comment/reaction ratio >= --controversy-ratio (default 0.5)

Input: a JSON array of posts, each at least:
  {topic, kol, engagement, comments?, url, platform?, text?}
History (optional): a CSV written by a prior run (--history) of per-topic weekly counts.

Stdlib only. Implements steps 4-5 of the robomotion-gtm-skills `kol-content-monitor` contract
. The digest narrative (step 6) is the agent's.

Examples:
  aggregate_signals.py --input posts.json --history ${WORKSPACE}/kol_topics.csv \
      --output ${WORKSPACE}/topics.json
"""
import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone


def load_history(path):
    """Return {topic: last_week_post_count} from the most recent prior run."""
    prev = {}
    if path and os.path.exists(path):
        rows = []
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if rows:
            last_run = max((r.get("run_ts", "") for r in rows), default="")
            for r in rows:
                if r.get("run_ts") == last_run:
                    try:
                        prev[r["topic"]] = int(r["posts"])
                    except (KeyError, ValueError):
                        pass
    return prev


def append_history(path, topics, run_ts):
    if not path:
        return
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["run_ts", "topic", "posts", "kols"])
        for t in topics:
            w.writerow([run_ts, t["topic"], t["posts"], t["kols"]])


def main():
    ap = argparse.ArgumentParser(description="Aggregate KOL posts by topic + tag spike/convergence signals.")
    ap.add_argument("--input", required=True, help="JSON array of topic-labeled posts (or - for stdin)")
    ap.add_argument("--history", default="", help="CSV of prior per-topic weekly counts (read+append)")
    ap.add_argument("--convergence", type=int, default=3, help="distinct-KOL threshold for Convergence")
    ap.add_argument("--spike-factor", type=float, default=2.0, help="this/last week ratio for Spike")
    ap.add_argument("--controversy-ratio", type=float, default=0.5, help="comment/reaction ratio for Controversy")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    posts = json.loads(raw)
    prev = load_history(args.history)

    groups = {}
    for p in posts:
        topic = (p.get("topic") or "").strip()
        if not topic:
            continue
        g = groups.setdefault(topic, {"topic": topic, "kols": set(), "posts": 0,
                                      "engagement": 0, "comments": 0, "items": []})
        g["kols"].add(p.get("kol", "") or p.get("author", ""))
        g["posts"] += 1
        g["engagement"] += int(p.get("engagement", 0) or 0)
        g["comments"] += int(p.get("comments", 0) or 0)
        g["items"].append({"url": p.get("url", ""), "kol": p.get("kol", ""),
                           "engagement": int(p.get("engagement", 0) or 0),
                           "platform": p.get("platform", ""),
                           "excerpt": (p.get("text", "") or "")[:280]})

    topics = []
    for topic, g in groups.items():
        nkols = len([k for k in g["kols"] if k])
        signals = []
        if nkols >= args.convergence:
            signals.append("Convergence")
        if nkols == 1:
            signals.append("Underdog")
        last = prev.get(topic, 0)
        if last > 0 and g["posts"] >= last * args.spike_factor:
            signals.append("Spike")
        ratio = (g["comments"] / g["engagement"]) if g["engagement"] else 0
        if ratio >= args.controversy_ratio:
            signals.append("Controversy")
        # best posts by engagement
        items = sorted(g["items"], key=lambda x: x["engagement"], reverse=True)
        topics.append({
            "topic": topic,
            "kols": nkols,
            "posts": g["posts"],
            "total_engagement": g["engagement"],
            "comment_ratio": round(ratio, 3),
            "last_week_posts": last,
            "signals": signals,
            "best_posts": items[:5],
        })

    topics.sort(key=lambda t: t["total_engagement"], reverse=True)
    run_ts = datetime.now(timezone.utc).isoformat()
    append_history(args.history, topics, run_ts)

    payload = json.dumps({"run_ts": run_ts, "topics": topics,
                          "spike_available": bool(prev)}, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(topics)} topics -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
