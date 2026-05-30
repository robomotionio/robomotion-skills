#!/usr/bin/env python3
"""slack_alert.py — deliver the top-N qualified Luma leads (Slack, else workspace file).

Formats the top N leads (after the agent has qualified + scored them). Delivery modes:
  - SLACK_WEBHOOK_URL set -> POST to the incoming webhook.
  - SLACK_BOT_TOKEN set   -> chat.postMessage to --channel.
  - NEITHER set (default fallback) -> write the formatted alert to --out-file (or
    ${WORKSPACE}/luma_alert.txt) so the pipeline still produces a deliverable. The agent
    can then relay it via whatever channel is available.
Reads a qualified-leads JSON (agent output), takes the top N by score, formats a message.
Stdlib only.

Example:
  slack_alert.py --leads qualified.json --top-n 5 --channel "#leads"
  slack_alert.py --leads qualified.json --top-n 5 --out-file alert.txt   # keyless fallback
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

WEBHOOK_ENV = "SLACK_WEBHOOK_URL"
TOKEN_ENV = "SLACK_BOT_TOKEN"
POST_MSG = "https://slack.com/api/chat.postMessage"


def post_json(url, body, headers):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def fmt(leads, top_n):
    lines = [f":dart: *Top {min(top_n, len(leads))} qualified Luma leads*"]
    for l in leads[:top_n]:
        name = l.get("name", "?")
        company = l.get("company", "")
        event = l.get("event_name", "") or l.get("event", "")
        verdict = l.get("qualification_status") or l.get("verdict") or ""
        score = l.get("score", "")
        li = l.get("linkedin_url", "")
        seg = f"• *{name}*"
        if company:
            seg += f" — {company}"
        if event:
            seg += f"  _(from {event})_"
        if verdict or score != "":
            seg += f"  [{verdict}{' ' + str(score) if score != '' else ''}]"
        if li:
            seg += f"\n   {li}"
        lines.append(seg)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Post top-N qualified Luma leads to Slack.")
    ap.add_argument("--leads", required=True, help="qualified leads JSON (agent output)")
    ap.add_argument("--top-n", type=int, default=5)
    ap.add_argument("--channel", default="", help="channel for bot-token mode")
    ap.add_argument("--out-file", default="",
                    help="keyless fallback: write the alert here when no Slack creds are set")
    args = ap.parse_args()

    with open(args.leads, encoding="utf-8") as f:
        data = json.load(f)
    leads = data.get("people", data) if isinstance(data, dict) else data
    # sort by score desc when present
    leads = sorted(leads, key=lambda l: (l.get("score") if isinstance(l.get("score"), (int, float))
                                         else -1), reverse=True)
    text = fmt(leads, args.top_n)

    webhook = os.environ.get(WEBHOOK_ENV, "").strip()
    token = os.environ.get(TOKEN_ENV, "").strip()
    if webhook:
        resp = post_json(webhook, {"text": text}, {})
        print(f"posted to webhook: {resp}", file=sys.stderr)
    elif token:
        if not args.channel:
            sys.exit("ERROR: --channel required in SLACK_BOT_TOKEN mode.")
        resp = post_json(POST_MSG, {"channel": args.channel, "text": text},
                         {"Authorization": f"Bearer {token}"})
        print(f"chat.postMessage: {resp}", file=sys.stderr)
    else:
        # Keyless fallback: no Slack creds -> write the alert to a workspace file.
        out_file = args.out_file or "luma_alert.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"WARN: no {WEBHOOK_ENV}/{TOKEN_ENV} -> wrote alert to {out_file} "
              "(relay it via an available channel).", file=sys.stderr)
        print(text)


if __name__ == "__main__":
    main()
