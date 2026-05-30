#!/usr/bin/env python3
"""signal_scan.py — Extract signal snippets from fetched newsletter messages by keyword
campaign, and emit either structured snippets (for the agent to synthesize into a digest)
or a templated markdown digest (LLM-free fallback).

Reads imap_fetch.py output + a keyword_campaigns JSON object
({competitors:[], pain_language:[], market_shifts:[], brand_mentions:[], ...}), substring-
matches each campaign's keywords, captures ~50-char-each-side context windows, and builds
per-campaign signal records (newsletter, date, keyword, context). With --digest it renders
a grouped markdown digest with per-campaign sections and topic-volume counts — but the
RICH synthesis (top trending topic, recommended actions) is the host agent's job over the
structured snippets. Deterministic, stdlib only.

Implements steps 3-5 of the robomotion-gtm-skills `newsletter-signal-scanner` contract.

Examples:
  signal_scan.py --input msgs.json --campaigns campaigns.json --output json
  signal_scan.py --input msgs.json --campaigns campaigns.json --digest \
      --output ${WORKSPACE}/newsletter-signals.md
"""
import argparse
import json
import sys
from datetime import datetime, timezone


def load_campaigns(path):
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        sys.exit("ERROR: --campaigns must be a JSON object {campaign_name: [keywords...]}.")
    # accept {name: [kw]} or {name: {keywords:[]}}
    norm = {}
    for k, v in obj.items():
        if isinstance(v, dict):
            norm[k] = v.get("keywords", [])
        elif isinstance(v, list):
            norm[k] = v
    return norm


def context_window(body, idx, klen, pad=50):
    start = max(0, idx - pad)
    end = min(len(body), idx + klen + pad)
    return body[start:end].replace("\n", " ").strip()


def scan(messages, campaigns):
    signals = []  # flat list of {campaign, keyword, newsletter, from, date, context}
    for msg in messages:
        body = msg.get("body", "") or ""
        low = body.lower()
        nl = msg.get("from", "")
        for cname, keywords in campaigns.items():
            for kw in keywords:
                k = kw.lower()
                idx = low.find(k)
                count = 0
                while idx != -1 and count < 5:
                    signals.append({
                        "campaign": cname,
                        "keyword": kw,
                        "newsletter": nl,
                        "subject": msg.get("subject", ""),
                        "date": msg.get("date", ""),
                        "message_id": msg.get("message_id", ""),
                        "context": context_window(body, idx, len(kw)),
                    })
                    count += 1
                    idx = low.find(k, idx + len(k))
    return signals


def topic_volume(signals):
    counts = {}
    for s in signals:
        counts[s["campaign"]] = counts.get(s["campaign"], 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def render_digest(signals, messages):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    vol = topic_volume(signals)
    senders = {m.get("from", "") for m in messages}
    with_signals = {s["message_id"] for s in signals}
    lines = [f"# Newsletter Signals — {today}", ""]
    lines.append(f"- Newsletters scanned: {len(senders)}")
    lines.append(f"- Emails with signals: {len(with_signals)} / {len(messages)}")
    if vol:
        top = next(iter(vol))
        lines.append(f"- Top topic by volume: **{top}** ({vol[top]} mentions)")
    lines.append("")
    by_campaign = {}
    for s in signals:
        by_campaign.setdefault(s["campaign"], []).append(s)
    titles = {
        "competitors": "Competitor Mentions",
        "pain_language": "ICP Pain Language",
        "market_shifts": "Market Shift Signals",
        "brand_mentions": "Your Brand Mentions",
    }
    for cname, rows in by_campaign.items():
        lines.append(f"## {titles.get(cname, cname)} ({len(rows)})")
        for r in rows:
            lines.append(f"- **{r['keyword']}** — {r['newsletter']} ({r['date']})")
            lines.append(f"  > …{r['context']}…")
        lines.append("")
    lines.append("## Recommended Actions")
    lines.append("_(Templated digest — for ranked, reasoned actions let the host agent "
                 "synthesize over the structured snippets JSON.)_")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Extract per-campaign newsletter signal snippets.")
    ap.add_argument("--input", required=True, help="JSON array from imap_fetch.py (or - for stdin)")
    ap.add_argument("--campaigns", required=True, help="JSON object of {campaign: [keywords]}")
    ap.add_argument("--digest", action="store_true", help="render a templated markdown digest (LLM-free)")
    ap.add_argument("--output", default="-", help="output path (default stdout)")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    messages = json.loads(raw)
    campaigns = load_campaigns(args.campaigns)
    signals = scan(messages, campaigns)

    if args.digest:
        payload = render_digest(signals, messages)
    else:
        payload = json.dumps({
            "topic_volume": topic_volume(signals),
            "signals": signals,
            "scanned": len(messages),
        }, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(signals)} signals -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
