#!/usr/bin/env python3
"""wayback_scraper.py — Search the Wayback Machine CDX API for archived snapshots of a
URL/domain and optionally fetch cached page content. Keyless, stdlib only.

Implements the robomotion-gtm-skills `web-archive-scraper` contract.

Examples:
  wayback_scraper.py --url example.com/customers --match exact --limit 25
  wayback_scraper.py --url example.com --match domain --from 2018-01-01 --to 2020-12-31 --limit 50
  wayback_scraper.py --url example.com/pricing --fetch --output summary
  wayback_scraper.py --url example.com/case-studies --match prefix --fetch-all --limit 10 --output csv
"""
import argparse
import csv
import html.parser
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

CDX = "http://web.archive.org/cdx/search/cdx"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills-web-archive-scraper/1.0)"
COLLAPSE_FIELD = {"day": "timestamp:8", "month": "timestamp:6", "year": "timestamp:4"}


def _get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 4:
                time.sleep(2 ** attempt + 2)  # CDX ~15 req/min; back off generously
                continue
            raise
        except urllib.error.URLError:
            if attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("exhausted retries")


class _TextExtractor(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "head"}

    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            t = data.strip()
            if t:
                self.parts.append(t)


def strip_html(raw):
    try:
        text = raw.decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        text = str(raw)
    p = _TextExtractor()
    try:
        p.feed(text)
    except Exception:  # noqa: BLE001
        return re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+\n", "\n", " ".join(p.parts)).strip()


def query_cdx(args):
    params = {
        "url": args.url,
        "matchType": args.match,
        "output": "json",
        "limit": args.limit,
        "collapse": COLLAPSE_FIELD.get(args.collapse, "") if args.collapse != "none" else "",
        "fl": "original,timestamp,statuscode,mimetype",
    }
    if args.from_:
        params["from"] = args.from_.replace("-", "")
    if args.to:
        params["to"] = args.to.replace("-", "")
    if args.status and args.status != "any":
        params["filter"] = f"statuscode:{args.status}"
    params = {k: v for k, v in params.items() if v != ""}
    url = CDX + "?" + urllib.parse.urlencode(params)
    rows = json.loads(_get(url).decode("utf-8") or "[]")
    if not rows:
        return []
    header, data = rows[0], rows[1:]
    return [dict(zip(header, row)) for row in data]


def to_record(row):
    ts = row.get("timestamp", "")
    orig = row.get("original", "")
    dt = ""
    if len(ts) >= 14:
        try:
            dt = datetime.strptime(ts[:14], "%Y%m%d%H%M%S").isoformat()
        except ValueError:
            dt = ts
    return {
        "url": orig,
        "timestamp": ts,
        "datetime": dt,
        "status_code": row.get("statuscode", ""),
        "mime_type": row.get("mimetype", ""),
        "archive_url": f"https://web.archive.org/web/{ts}/{orig}",
        "raw_url": f"https://web.archive.org/web/{ts}id_/{orig}",  # id_ strips toolbar
        "content": "",
    }


def main():
    ap = argparse.ArgumentParser(description="Search the Wayback Machine CDX API (keyless).")
    ap.add_argument("--url", required=True, help="target URL/domain to search in the archive")
    ap.add_argument("--match", default="exact", choices=["exact", "prefix", "host", "domain"])
    ap.add_argument("--from", dest="from_", default="", help="range start YYYY-MM-DD")
    ap.add_argument("--to", default="", help="range end YYYY-MM-DD")
    ap.add_argument("--limit", type=int, default=25, help="max snapshots (default 25)")
    ap.add_argument("--fetch", action="store_true", help="fetch content of the most recent snapshot")
    ap.add_argument("--fetch-all", action="store_true", help="fetch content of ALL matched snapshots")
    ap.add_argument("--status", default="200", help="HTTP status filter (default 200; 'any' for all)")
    ap.add_argument("--collapse", default="day", choices=["none", "day", "month", "year"])
    ap.add_argument("--output", default="json", choices=["json", "csv", "summary"])
    args = ap.parse_args()

    rows = query_cdx(args)
    records = [to_record(r) for r in rows][: args.limit]

    if args.fetch_all:
        targets = records
    elif args.fetch and records:
        targets = [max(records, key=lambda r: r["timestamp"])]
    else:
        targets = []
    for rec in targets:
        try:
            rec["content"] = strip_html(_get(rec["raw_url"]))
        except Exception as e:  # noqa: BLE001
            rec["content"] = f"[fetch failed: {e}]"
        time.sleep(4)  # CDX/content ~15 req/min

    if args.output == "summary":
        if not records:
            print("No archived snapshots found.")
            return
        for r in records:
            flag = "  *content*" if r["content"] else ""
            print(f"{r['datetime'] or r['timestamp']}  [{r['status_code']}] {r['url']}{flag}")
            print(f"    {r['archive_url']}")
    elif args.output == "csv":
        buf = io.StringIO()
        fields = ["url", "timestamp", "datetime", "status_code", "mime_type",
                  "archive_url", "raw_url", "content"]
        w = csv.DictWriter(buf, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow(r)
        sys.stdout.write(buf.getvalue())
    else:
        json.dump(records, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
