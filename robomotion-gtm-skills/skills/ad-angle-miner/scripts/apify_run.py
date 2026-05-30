#!/usr/bin/env python3
"""apify_run.py — Generic Apify-actor runner (FALLBACK for hostile/volume sources).

Only reach for this when robomotion-serp / web search can't get the depth you need from a
hostile source (Reddit at depth, Amazon reviews, volume review sites). Runs any Apify actor
synchronously and returns its dataset items as JSON. The host agent supplies the actor id
and the input payload; this script is just the deterministic HTTP plumbing. Stdlib only.

Auth: APIFY_API_TOKEN (required only for THIS fallback path; the primary mining path is
keyless web search).

Examples:
  # Reddit deep harvest
  apify_run.py --actor "trudax~reddit-scraper" \
      --input '{"searches":["uipath alternative"],"maxItems":80}' --output reddit.json

  # G2/review actor
  apify_run.py --actor "<vendor>~g2-reviews-scraper" --input-file payload.json --output reviews.json
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def token():
    t = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not t:
        sys.exit("ERROR: APIFY_API_TOKEN is not set (required only for this Apify fallback).")
    return t


def run_actor(actor, payload, tok):
    url = (
        f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
        f"?token={urllib.parse.quote(tok)}"
    )
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apify {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def main():
    ap = argparse.ArgumentParser(description="Run an Apify actor synchronously and return dataset items.")
    ap.add_argument("--actor", required=True, help="actor id, e.g. 'trudax~reddit-scraper'")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", help="actor input as an inline JSON string")
    g.add_argument("--input-file", help="actor input as a JSON file")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    if args.input:
        payload = json.loads(args.input)
    else:
        with open(args.input_file, encoding="utf-8") as f:
            payload = json.load(f)

    items = run_actor(args.actor, payload, token())
    if isinstance(items, dict):
        items = items.get("items", items)
    out = json.dumps(items, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        n = len(items) if isinstance(items, list) else 1
        print(f"{n} item(s) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
