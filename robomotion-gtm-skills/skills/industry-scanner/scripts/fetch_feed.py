#!/usr/bin/env python3
"""fetch_feed.py — Fetch and parse an RSS/Atom blog feed into normalized items.

Deterministic, stdlib-only (urllib + xml.etree). Used to measure content cadence,
authorship, and recent topics for a blog. No LLM — the agent interprets cadence/themes.

Tries the given URL; if it's an HTML page (not a feed), probes common feed paths
(/feed, /rss, /atom.xml, /blog/feed, /feed.xml).

Examples:
  fetch_feed.py --url https://competitor.com/blog
  fetch_feed.py --url https://competitor.com/feed --max-items 50 --output ${WORKSPACE}/feed.json
"""
import argparse
import gzip
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills-feed/1.0; +https://agentskills.io)"
PROBE_PATHS = ["", "/feed", "/rss", "/rss.xml", "/atom.xml", "/feed.xml", "/blog/feed", "/index.xml"]


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw.decode(r.headers.get_content_charset() or "utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ConnectionError):
        return None


def strip_ns(tag):
    return tag.split("}", 1)[-1] if "}" in tag else tag


def parse_feed(text):
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None
    items = []
    # RSS: channel/item ; Atom: feed/entry
    for el in root.iter():
        if strip_ns(el.tag) in ("item", "entry"):
            d = {"title": "", "link": "", "author": "", "date": ""}
            for c in el:
                t = strip_ns(c.tag)
                if t == "title":
                    d["title"] = (c.text or "").strip()
                elif t == "link":
                    d["link"] = (c.get("href") or c.text or "").strip()
                elif t in ("creator", "author"):
                    # atom author may nest <name>
                    name = c.findtext("{*}name") if list(c) else None
                    d["author"] = (name or c.text or "").strip()
                elif t in ("pubDate", "published", "updated", "date"):
                    if not d["date"]:
                        d["date"] = (c.text or "").strip()
            if d["title"] or d["link"]:
                items.append(d)
    return items


def parse_date(s):
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except (ValueError, TypeError):
            continue
    m = re.search(r"\d{4}-\d{2}-\d{2}", s or "")
    if m:
        try:
            return datetime.strptime(m.group(0), "%Y-%m-%d")
        except ValueError:
            pass
    return None


def main():
    ap = argparse.ArgumentParser(description="Fetch + parse an RSS/Atom blog feed (keyless).")
    ap.add_argument("--url", required=True, help="blog or feed URL (feed path auto-probed)")
    ap.add_argument("--max-items", type=int, default=50, help="cap returned items (default 50)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    items, feed_url = None, ""
    base = args.url.rstrip("/")
    for p in PROBE_PATHS:
        cand = args.url if p == "" else urllib.parse.urljoin(base + "/", p.lstrip("/"))
        text = fetch(cand)
        if not text:
            continue
        parsed = parse_feed(text)
        if parsed:
            items, feed_url = parsed, cand
            break

    if items is None:
        print(json.dumps({"feed_url": "", "error": "no parseable RSS/Atom feed found",
                          "items": [], "stats": {"count": 0}}, indent=2))
        return

    # sort by parsed date desc where available
    for it in items:
        dt = parse_date(it["date"])
        it["_dt"] = dt.isoformat() if dt else ""
    items.sort(key=lambda x: x["_dt"], reverse=True)
    items = items[: args.max_items]

    # cadence: span between newest and oldest dated items
    dated = [parse_date(i["date"]) for i in items if parse_date(i["date"])]
    cadence = {}
    if len(dated) >= 2:
        span_days = (max(dated) - min(dated)).days or 1
        cadence = {
            "newest": max(dated).date().isoformat(),
            "oldest": min(dated).date().isoformat(),
            "span_days": span_days,
            "posts_per_month": round(len(dated) / (span_days / 30.0), 2),
        }
    authors = sorted({i["author"] for i in items if i["author"]})

    result = {
        "feed_url": feed_url,
        "items": items,
        "authors": authors,
        "cadence": cadence,
        "stats": {"count": len(items)},
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(items)} feed items -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
