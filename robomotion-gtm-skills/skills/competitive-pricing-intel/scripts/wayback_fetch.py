#!/usr/bin/env python3
"""wayback_fetch.py — Pull historical snapshots of a pricing page from the Wayback Machine.

Deterministic, stdlib-only. Uses the keyless Wayback CDX API to list snapshot timestamps
for a URL, then fetches the page text of the most recent N snapshots so the agent can diff
pricing changes over time. No LLM, no scoring.

Examples:
  wayback_fetch.py --url https://competitor.com/pricing
  wayback_fetch.py --url https://competitor.com/pricing --snapshots 3 --output ${WORKSPACE}/wb.json
"""
import argparse
import gzip
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills-pricing/1.0; +https://agentskills.io)"
CDX = "https://web.archive.org/cdx/search/cdx"


def http_get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw.decode(r.headers.get_content_charset() or "utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ConnectionError) as e:
        return None


class TextExtract(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._stack = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)

    def handle_endtag(self, tag):
        if self._stack:
            self._stack.pop()

    def handle_data(self, data):
        if any(s in self.SKIP for s in self._stack):
            return
        t = data.strip()
        if t:
            self.parts.append(t)


PRICE_RE = re.compile(r"(?:\$|€|£|USD|EUR)\s?\d[\d,]*(?:\.\d+)?(?:\s?/\s?(?:mo|month|yr|year|seat|user))?", re.I)


def page_text(html):
    p = TextExtract()
    try:
        p.feed(html)
    except Exception:
        pass
    text = re.sub(r"\s+", " ", " ".join(p.parts)).strip()
    prices = sorted(set(m.group(0) for m in PRICE_RE.finditer(text)))
    return text, prices


def list_snapshots(url):
    params = {"url": url, "output": "json", "fl": "timestamp,original,statuscode",
              "filter": "statuscode:200", "collapse": "timestamp:6"}
    data = http_get(CDX + "?" + urllib.parse.urlencode(params))
    if not data:
        return []
    try:
        rows = json.loads(data)
    except json.JSONDecodeError:
        return []
    return rows[1:] if rows and isinstance(rows[0], list) else []


def main():
    ap = argparse.ArgumentParser(description="Fetch historical pricing-page snapshots from the Wayback Machine (keyless).")
    ap.add_argument("--url", required=True, help="pricing page URL")
    ap.add_argument("--snapshots", type=int, default=3, help="how many recent snapshots to fetch (default 3)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    rows = list_snapshots(args.url)
    if not rows:
        print(json.dumps({"url": args.url, "snapshots": [],
                          "note": "no prior Wayback snapshots — first run is the baseline"}, indent=2))
        return

    rows.sort(key=lambda r: r[0], reverse=True)  # newest first by timestamp
    out_snaps = []
    for ts, original, _code in rows[: args.snapshots]:
        snap_url = f"https://web.archive.org/web/{ts}id_/{original}"
        html = http_get(snap_url)
        if not html:
            out_snaps.append({"timestamp": ts, "archived_url": snap_url, "error": "fetch failed"})
            continue
        text, prices = page_text(html)
        out_snaps.append({
            "timestamp": ts,
            "date": f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}",
            "archived_url": snap_url,
            "prices_found": prices,
            "text_excerpt": text[:6000],
            "text_chars": len(text),
        })

    result = {"url": args.url, "snapshot_count": len(out_snaps), "snapshots": out_snaps}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(out_snaps)} snapshot(s) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
