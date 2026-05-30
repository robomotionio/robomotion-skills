#!/usr/bin/env python3
"""fetch_pages.py — Fetch competitor marketing/pricing pages and extract structured text.

Deterministic, stdlib-only (urllib). Given one or more URLs, fetches each page with a
sane User-Agent and extracts a lightweight structured view: title, meta description,
headings (h1-h3), visible paragraphs, list items, internal/external links, and
candidate "claim" lines (hero / value-prop sentences). No LLM, no scoring — the host
agent reads the JSON and synthesizes the battlecard.

For JS-rendered marketing sites where this returns little text, the SKILL.md routes the
agent to the Playwright fallback (render_page.mjs).

Examples:
  fetch_pages.py --url https://competitor.com https://competitor.com/pricing
  fetch_pages.py --url https://competitor.com --output ${WORKSPACE}/competitor_pages.json
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

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills-battlecard/1.0; +https://agentskills.io)"


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-US,en;q=0.9",
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                charset = r.headers.get_content_charset() or "utf-8"
                return raw.decode(charset, "replace"), r.geturl()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                continue
            return None, f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < 2:
                continue
            return None, str(e)
    return None, "exhausted retries"


class Extractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "template", "svg"}
    HEAD = {"h1", "h2", "h3"}

    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base = base_url
        self.title = ""
        self.meta_desc = ""
        self.headings = []
        self.paragraphs = []
        self.list_items = []
        self.links = []
        self._stack = []
        self._buf = []
        self._cur = None  # current capture context tag

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)
        a = dict(attrs)
        if tag == "meta":
            name = (a.get("name") or a.get("property") or "").lower()
            if name in ("description", "og:description") and not self.meta_desc:
                self.meta_desc = (a.get("content") or "").strip()
        elif tag == "a":
            href = a.get("href")
            if href:
                full = urllib.parse.urljoin(self.base, href)
                self.links.append(full)
        if tag in self.HEAD or tag in ("p", "li", "title"):
            self._cur = tag
            self._buf = []

    def handle_endtag(self, tag):
        if self._stack:
            self._stack.pop()
        if tag == self._cur:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if text:
                if tag == "title":
                    self.title = text
                elif tag in self.HEAD:
                    self.headings.append({"level": tag, "text": text})
                elif tag == "p":
                    self.paragraphs.append(text)
                elif tag == "li":
                    self.list_items.append(text)
            self._cur = None
            self._buf = []

    def handle_data(self, data):
        if any(s in self.SKIP for s in self._stack):
            return
        if self._cur:
            self._buf.append(data)


CLAIM_RE = re.compile(
    r"\b(we help|the only|unlike|trusted by|#1|leading|all-in-one|"
    r"built for|the easiest|the fastest|the best|vs\.?|alternative to)\b", re.I)


def extract(html, url):
    p = Extractor(url)
    try:
        p.feed(html)
    except Exception:
        pass
    host = urllib.parse.urlparse(url).netloc
    internal, external = [], []
    seen = set()
    for ln in p.links:
        if ln in seen:
            continue
        seen.add(ln)
        (internal if urllib.parse.urlparse(ln).netloc == host else external).append(ln)
    claims = [h["text"] for h in p.headings if CLAIM_RE.search(h["text"])]
    claims += [s for s in p.paragraphs if CLAIM_RE.search(s)][:20]
    text_len = sum(len(x) for x in p.paragraphs)
    return {
        "url": url,
        "title": p.title,
        "meta_description": p.meta_desc,
        "headings": p.headings[:60],
        "paragraphs": p.paragraphs[:120],
        "list_items": p.list_items[:120],
        "candidate_claims": claims[:30],
        "internal_links": internal[:100],
        "external_links": external[:60],
        "stats": {
            "headings": len(p.headings),
            "paragraphs": len(p.paragraphs),
            "list_items": len(p.list_items),
            "text_chars": text_len,
            "likely_js_rendered": text_len < 400,
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Fetch + extract structured text from competitor pages (keyless).")
    ap.add_argument("--url", nargs="+", required=True, help="one or more URLs to fetch")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    results = []
    for url in args.url:
        html, final = fetch(url)
        if html is None:
            results.append({"url": url, "error": final, "stats": {"text_chars": 0}})
            continue
        results.append(extract(html, final))

    out = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(results)} page(s) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
