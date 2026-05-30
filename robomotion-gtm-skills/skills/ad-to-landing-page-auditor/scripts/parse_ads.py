#!/usr/bin/env python3
"""parse_ads.py — Normalize an ad inventory (CSV or JSON) into a clean table.

Builds the ad inventory that drives the audit: one row per ad with platform, headline(s),
body, CTA, landing-page URL, and (optional) known click->conv rate. Also emits the set of
UNIQUE landing-page URLs (one per line) so fetch_landing_page.py can pull each LP once.

Deterministic parse only — no LLM. Message-match and friction SCORING is the agent's job
(see ../SKILL.md). Stdlib only.

Examples:
  parse_ads.py --csv ads_export.csv --urls-out urls.txt --output inventory.json
  parse_ads.py --json ads.json --urls-out urls.txt
"""
import argparse
import csv
import json
import sys


# Accepted column aliases (lowercased, stripped) -> canonical field.
ALIASES = {
    "platform": "platform", "channel": "platform", "network": "platform",
    "headline": "headline", "headline 1": "headline", "headline1": "headline",
    "title": "headline", "ad headline": "headline",
    "headlines": "headlines",
    "body": "body", "description": "body", "description 1": "body",
    "ad copy": "body", "primary text": "body",
    "cta": "cta", "call to action": "cta", "button": "cta",
    "landing page url": "landing_url", "landing_url": "landing_url",
    "final url": "landing_url", "url": "landing_url", "destination url": "landing_url",
    "lp": "landing_url", "link": "landing_url",
    "conv rate": "conv_rate", "conversion rate": "conv_rate", "cvr": "conv_rate",
    "click to conv": "conv_rate", "known_conv_rate": "conv_rate",
}


def canon_row(raw):
    out = {"platform": "", "headline": "", "headlines": [], "body": "",
           "cta": "", "landing_url": "", "conv_rate": ""}
    extra_headlines = []
    for k, v in raw.items():
        if k is None:
            continue
        key = ALIASES.get(str(k).strip().lower())
        v = (v or "").strip() if isinstance(v, str) else v
        if key == "headlines" and isinstance(v, str) and v:
            extra_headlines.extend([h.strip() for h in v.split("|") if h.strip()])
        elif key and key != "headlines":
            if key == "headline" and out["headline"] and v:
                extra_headlines.append(v)  # multiple headline columns
            elif key:
                out[key] = v
    if out["headline"]:
        extra_headlines.insert(0, out["headline"])
    out["headlines"] = list(dict.fromkeys([h for h in extra_headlines if h])) or (
        [out["headline"]] if out["headline"] else []
    )
    return out


def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [canon_row(r) for r in csv.DictReader(f)]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("ads") or data.get("items") or [data]
    rows = []
    for r in data:
        rows.append(canon_row({k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                               for k, v in r.items()}))
    # preserve explicit list headlines if present in source JSON
    for src, dst in zip(data, rows):
        if isinstance(src.get("headlines"), list):
            dst["headlines"] = [h for h in src["headlines"] if h]
        if dst["headlines"] and not dst["headline"]:
            dst["headline"] = dst["headlines"][0]
    return rows


def main():
    ap = argparse.ArgumentParser(description="Normalize an ad inventory (CSV/JSON) for the auditor.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--csv", help="ad-export CSV")
    g.add_argument("--json", help="ad-list JSON")
    ap.add_argument("--urls-out", default="", help="write unique LP URLs (one per line) here")
    ap.add_argument("--output", default="-", help="normalized inventory JSON (default stdout)")
    args = ap.parse_args()

    rows = load_csv(args.csv) if args.csv else load_json(args.json)
    # assign stable ids
    for i, r in enumerate(rows):
        r["ad_id"] = i + 1

    if args.urls_out:
        seen, urls = set(), []
        for r in rows:
            u = r["landing_url"]
            if u and u not in seen:
                seen.add(u)
                urls.append(u)
        with open(args.urls_out, "w", encoding="utf-8") as f:
            f.write("\n".join(urls) + ("\n" if urls else ""))
        print(f"{len(urls)} unique LP URL(s) -> {args.urls_out}", file=sys.stderr)

    payload = json.dumps(rows, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(rows)} ad(s) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
