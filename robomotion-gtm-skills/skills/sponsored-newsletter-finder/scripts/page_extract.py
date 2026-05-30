#!/usr/bin/env python3
"""page_extract.py — Keyless fetch + extract of newsletter / sponsorship pages.

Deterministic discovery helper for sponsored-newsletter-finder. Given one or more URLs
(newsletter About/Advertise pages, or directory listing pages like newsletter.directory /
paved.com / swapstack.co / sparkloop.co), fetches each via urllib with a browser User-Agent
and returns structured content the host agent ranks: title, meta description, headings,
visible text, outbound links, and best-effort signal scrapes (subscriber count, open rate,
CPM/rate hints). NO scoring/ranking here — that's the agent's job.

Stdlib only. Implements step 2-3 of the robomotion-gtm-skills `sponsored-newsletter-finder` contract
. For the discovery search itself, the host agent uses its own web search
(or Robomotion serp); this helper turns chosen URLs into structured data.

Examples:
  page_extract.py --urls https://example.com/advertise https://example.com/about
  page_extract.py --urls-file urls.txt --output ${WORKSPACE}/newsletters_raw.json
"""
import argparse
import html.parser
import json
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills-sponsored-newsletter-finder/1.0)"

SUBS_RE = re.compile(r"([\d][\d,\.]*\s?[KkMm]?)\s*(?:\+?\s*)?(?:subscribers|readers|members)", re.I)
OPEN_RE = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%\s*open\s*rate", re.I)
CPM_RE = re.compile(r"(?:\$|USD)\s?([\d,]+(?:\.\d+)?)\s*(?:CPM|/\s*1?,?000|per\s*thousand)", re.I)
RATE_RE = re.compile(r"(?:\$|USD)\s?([\d,]+(?:\.\d+)?)\s*(?:/|per)\s*(?:send|issue|sponsorship|ad)", re.I)


class _Parser(html.parser.HTMLParser):
    SKIP = {"script", "style", "head", "noscript"}

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_desc = ""
        self.headings = []
        self.text_parts = []
        self.links = []
        self._skip = 0
        self._in_title = False
        self._cur_heading = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and a.get("name", "").lower() == "description":
            self.meta_desc = a.get("content", "") or self.meta_desc
        elif tag in ("h1", "h2", "h3"):
            self._cur_heading = []
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3") and self._cur_heading is not None:
            h = " ".join(self._cur_heading).strip()
            if h:
                self.headings.append(h)
            self._cur_heading = None

    def handle_data(self, data):
        t = data.strip()
        if not t:
            return
        if self._in_title:
            self.title += t
        if self._cur_heading is not None:
            self._cur_heading.append(t)
        if not self._skip:
            self.text_parts.append(t)


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                charset = r.headers.get_content_charset() or "utf-8"
                return r.read().decode(charset, "ignore")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return f"__ERROR__ HTTP {e.code}"
        except urllib.error.URLError as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return f"__ERROR__ {e}"


def first(rx, text):
    m = rx.search(text)
    return m.group(1).strip() if m else ""


def extract(url, body):
    if body.startswith("__ERROR__"):
        return {"url": url, "error": body.replace("__ERROR__ ", "")}
    p = _Parser()
    try:
        p.feed(body)
    except Exception:  # noqa: BLE001
        pass
    text = re.sub(r"[ \t]+", " ", " ".join(p.text_parts))
    base = urlparse(url)
    abs_links = []
    for href in p.links:
        try:
            full = urljoin(url, href)
        except ValueError:
            continue
        if full.startswith("http") and full not in abs_links:
            abs_links.append(full)
    return {
        "url": url,
        "title": p.title.strip(),
        "meta_description": p.meta_desc.strip(),
        "headings": p.headings[:30],
        "text": text[:8000],
        "links": abs_links[:200],
        "signals": {
            "subscribers": first(SUBS_RE, text),
            "open_rate": first(OPEN_RE, text),
            "cpm": first(CPM_RE, text),
            "flat_rate": first(RATE_RE, text),
        },
        "domain": base.netloc,
    }


def main():
    ap = argparse.ArgumentParser(description="Keyless fetch+extract of newsletter/sponsorship pages.")
    ap.add_argument("--urls", nargs="*", default=[], help="one or more URLs to fetch")
    ap.add_argument("--urls-file", default="", help="text file of URLs (one per line)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    urls = list(args.urls)
    if args.urls_file:
        with open(args.urls_file, encoding="utf-8") as f:
            urls += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if not urls:
        sys.exit("ERROR: provide --urls or --urls-file.")

    out = []
    for u in urls:
        out.append(extract(u, fetch(u)))
        time.sleep(0.5)

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(out)} pages -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
