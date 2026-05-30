#!/usr/bin/env python3
"""fetch_url.py — fetch one URL and return its visible text + headings as JSON (keyless).

Deterministic I/O only (stdlib urllib + html.parser). NO LLM. A small helper for pulling a
company/about/news page into the agent's context during meeting research. For JS-heavy or
auth-walled pages (LinkedIn), use web-automation/phantombuster instead (agent-routed).

Example:
  fetch_url.py --url https://example.com/about --output about.json
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

UA = "robomotion-gtm-skills/meeting-brief (+research bot)"


class Extractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "template", "svg", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.in_title = False
        self.in_h = 0
        self.title = ""
        self.headings = []
        self._chunks = []
        self._cur = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "title":
            self.in_title = True
        elif tag in ("h1", "h2", "h3"):
            self.in_h += 1
            self._cur = []

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == "title":
            self.in_title = False
        elif tag in ("h1", "h2", "h3") and self.in_h:
            self.in_h -= 1
            h = " ".join(self._cur).strip()
            if h:
                self.headings.append(h)
            self._cur = []

    def handle_data(self, data):
        if self.skip:
            return
        t = data.strip()
        if not t:
            return
        if self.in_title and not self.title:
            self.title = t
        if self.in_h:
            self._cur.append(t)
        self._chunks.append(t)

    def text(self):
        return re.sub(r"\s+", " ", " ".join(self._chunks)).strip()


def main():
    ap = argparse.ArgumentParser(description="Fetch one URL -> {url,title,headings,text} JSON (keyless).")
    ap.add_argument("--url", required=True, help="URL to fetch")
    ap.add_argument("--max-chars", type=int, default=20000, help="cap on extracted text (default 20000)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    url = args.url if args.url.startswith("http") else "https://" + args.url
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read(2_000_000)
            charset = r.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, "replace")
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR: HTTP {e.code} fetching {url}")
    except urllib.error.URLError as e:
        sys.exit(f"ERROR: network fetching {url}: {e}")

    p = Extractor()
    try:
        p.feed(html)
    except Exception:
        pass
    result = {"url": url, "title": p.title, "headings": p.headings[:40], "text": p.text()[: args.max_chars]}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"fetched {url} -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
