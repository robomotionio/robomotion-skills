#!/usr/bin/env python3
"""fetch_campaign.py — pull campaign metrics + sequence copy + replies from an outreach tool.

Deterministic I/O only (stdlib). NO LLM. Supports Instantly and Lemlist REST, or a CSV
passthrough (keyless). Emits a normalized campaign bundle that analyze_sequence.py and the
agent consume. The agent classifies replies and grades copy itself.

Auth (only for the chosen --tool):
  instantly -> INSTANTLY_API_KEY
  lemlist   -> LEMLIST_API_KEY
  csv       -> --metrics-csv / --replies-csv / --copy-csv (no key)

Bundle shape:
  {campaign, metrics:{sends,opens,replies,bounces, by_touch:[...], by_variant:[...]},
   copy:[{touch,variant,subject,body}], replies:[{date,from,text}]}

Example:
  fetch_campaign.py --tool instantly --campaign "Q1 Cold" --output bundle.json
  fetch_campaign.py --tool csv --metrics-csv m.csv --replies-csv r.csv --copy-csv c.csv \
      --campaign "Q1 Cold" --output bundle.json
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def http(url, headers=None, data=None, method="GET"):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR: outreach API HTTP {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"ERROR: network: {e}")


def need(var):
    v = os.environ.get(var, "").strip()
    if not v:
        sys.exit(f"ERROR: {var} is not set (required for this --tool). "
                 "Use --tool csv for a keyless path.")
    return v


def read_csv(path):
    if not path:
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
                for r in csv.DictReader(f)]


def inum(v):
    try:
        return int(float(str(v).replace(",", "")))
    except (ValueError, TypeError):
        return 0


def from_instantly(campaign):
    key = need("INSTANTLY_API_KEY")
    hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    base = "https://api.instantly.ai/api/v2"
    analytics = http(f"{base}/campaigns/analytics?" + urllib.parse.urlencode({"id": campaign}), headers=hdr)
    m = analytics if isinstance(analytics, dict) else (analytics[0] if analytics else {})
    metrics = {
        "sends": inum(m.get("emails_sent") or m.get("sent")),
        "opens": inum(m.get("opens") or m.get("opened")),
        "replies": inum(m.get("replies") or m.get("replied")),
        "bounces": inum(m.get("bounces") or m.get("bounced")),
        "by_touch": [], "by_variant": [],
    }
    return {"campaign": campaign, "metrics": metrics, "copy": [], "replies": []}


def from_lemlist(campaign):
    key = need("LEMLIST_API_KEY")
    # lemlist uses HTTP basic with the api key as password and empty user
    import base64
    auth = base64.b64encode(f":{key}".encode()).decode()
    hdr = {"Authorization": f"Basic {auth}"}
    base = "https://api.lemlist.com/api"
    stats = http(f"{base}/campaigns/{urllib.parse.quote(campaign)}/stats", headers=hdr)
    metrics = {
        "sends": inum(stats.get("nbSent") or stats.get("sent")),
        "opens": inum(stats.get("nbOpen") or stats.get("opened")),
        "replies": inum(stats.get("nbReplied") or stats.get("replied")),
        "bounces": inum(stats.get("nbBounced") or stats.get("bounced")),
        "by_touch": [], "by_variant": [],
    }
    return {"campaign": campaign, "metrics": metrics, "copy": [], "replies": []}


def from_csv(campaign, metrics_csv, replies_csv, copy_csv):
    metrics = {"sends": 0, "opens": 0, "replies": 0, "bounces": 0, "by_touch": [], "by_variant": []}
    for row in read_csv(metrics_csv):
        rec = {"touch": row.get("touch", ""), "variant": row.get("variant", ""),
               "sends": inum(row.get("sends") or row.get("sent")),
               "opens": inum(row.get("opens") or row.get("opened")),
               "replies": inum(row.get("replies") or row.get("replied")),
               "bounces": inum(row.get("bounces") or row.get("bounced"))}
        metrics["sends"] += rec["sends"]
        metrics["opens"] += rec["opens"]
        metrics["replies"] += rec["replies"]
        metrics["bounces"] += rec["bounces"]
        if rec["touch"]:
            metrics["by_touch"].append(rec)
        if rec["variant"]:
            metrics["by_variant"].append(rec)
    copy = [{"touch": r.get("touch", ""), "variant": r.get("variant", ""),
             "subject": r.get("subject", ""), "body": r.get("body", "")}
            for r in read_csv(copy_csv)]
    replies = [{"date": r.get("date", ""), "from": r.get("from", ""),
                "text": r.get("text") or r.get("body", "")}
               for r in read_csv(replies_csv)]
    return {"campaign": campaign, "metrics": metrics, "copy": copy, "replies": replies}


def main():
    ap = argparse.ArgumentParser(description="Pull outreach campaign metrics/copy/replies into a bundle.")
    ap.add_argument("--tool", required=True, choices=["instantly", "lemlist", "csv"])
    ap.add_argument("--campaign", required=True, help="campaign name or id")
    ap.add_argument("--metrics-csv", default="", help="metrics CSV (--tool csv)")
    ap.add_argument("--replies-csv", default="", help="replies CSV (--tool csv)")
    ap.add_argument("--copy-csv", default="", help="copy CSV (--tool csv)")
    ap.add_argument("--output", default="-", help="output bundle JSON (default stdout)")
    args = ap.parse_args()

    if args.tool == "csv":
        bundle = from_csv(args.campaign, args.metrics_csv, args.replies_csv, args.copy_csv)
    elif args.tool == "instantly":
        bundle = from_instantly(args.campaign)
    else:
        bundle = from_lemlist(args.campaign)

    out = json.dumps(bundle, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"campaign bundle -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
