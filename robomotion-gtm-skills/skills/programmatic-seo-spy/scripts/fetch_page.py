#!/usr/bin/env python3
"""fetch_page.py — fetch a URL and extract structured content + SEO signals.

Equivalent of robomotion-serp "Extract Content": returns title, meta description,
headers (h1-h3), paragraph count, word count, lists, internal/external link counts,
image count, JSON-LD / schema.org types present, and canonical/robots meta. Used by:
  - programmatic-seo-spy: template-quality sampling (3-5 pages per pattern),
  - seo-content-audit: deep-analysis of top pages.

DETERMINISTIC parse only (stdlib html.parser). The host agent scores quality dimensions
and brand voice from these stats. Pass multiple --url or a --urls-file.

Example:
  fetch_page.py --url https://example.com/vs/competitor --output page.json
  fetch_page.py --urls-file sample_urls.json --output pages.json
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills-seo/1.0; +content-extract)"


class Extractor(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base = base_url
        self.host = urllib.parse.urlparse(base_url).netloc
        self.title = ""
        self.meta_description = ""
        self.canonical = ""
        self.robots = ""
        self.headers = {"h1": [], "h2": [], "h3": []}
        self.paragraphs = 0
        self.list_items = 0
        self.images = 0
        self.internal_links = 0
        self.external_links = 0
        self.schema_types = []
        self._text_parts = []
        self._cur = None
        self._buf = []
        self._in_script_ld = False
        self._ld_buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._cur, self._buf = "title", []
        elif tag in ("h1", "h2", "h3"):
            self._cur, self._buf = tag, []
        elif tag == "p":
            self.paragraphs += 1
        elif tag == "li":
            self.list_items += 1
        elif tag == "img":
            self.images += 1
        elif tag == "meta":
            name = (a.get("name") or a.get("property") or "").lower()
            if name == "description":
                self.meta_description = a.get("content", "")
            elif name == "robots":
                self.robots = a.get("content", "")
        elif tag == "link" and a.get("rel", "").lower() == "canonical":
            self.canonical = a.get("href", "")
        elif tag == "a" and a.get("href"):
            full = urllib.parse.urljoin(self.base, a["href"])
            netloc = urllib.parse.urlparse(full).netloc
            if netloc and netloc == self.host:
                self.internal_links += 1
            elif netloc:
                self.external_links += 1
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_script_ld = True
            self._ld_buf = []

    def handle_endtag(self, tag):
        if tag == "title" and self._cur == "title":
            self.title = " ".join(self._buf).strip()
            self._cur = None
        elif tag in ("h1", "h2", "h3") and self._cur == tag:
            txt = " ".join(self._buf).strip()
            if txt:
                self.headers[tag].append(txt)
            self._cur = None
        elif tag == "script" and self._in_script_ld:
            self._in_script_ld = False
            blob = "".join(self._ld_buf)
            for m in re.findall(r'"@type"\s*:\s*"([^"]+)"', blob):
                self.schema_types.append(m)

    def handle_data(self, data):
        if self._cur:
            self._buf.append(data.strip())
        if self._in_script_ld:
            self._ld_buf.append(data)
        else:
            t = data.strip()
            if t:
                self._text_parts.append(t)

    def word_count(self):
        return len(re.findall(r"\w+", " ".join(self._text_parts)))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                ctype = r.headers.get("Content-Type", "")
                return r.read().decode("utf-8", "ignore"), ctype, r.getcode()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return None, "", e.code
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return None, "", 0
    return None, "", 0


def extract(url):
    body, ctype, code = fetch(url)
    if not body or "html" not in ctype.lower():
        return {"url": url, "status": code, "ok": False, "note": "no HTML body (JS-rendered? use web-automation)"}
    p = Extractor(url)
    try:
        p.feed(body)
    except Exception as e:
        return {"url": url, "status": code, "ok": False, "note": f"parse error: {e}"}
    return {
        "url": url, "status": code, "ok": True,
        "title": p.title, "meta_description": p.meta_description,
        "canonical": p.canonical, "robots_meta": p.robots,
        "h1": p.headers["h1"], "h2_count": len(p.headers["h2"]),
        "h2": p.headers["h2"][:25], "h3_count": len(p.headers["h3"]),
        "paragraph_count": p.paragraphs, "word_count": p.word_count(),
        "list_item_count": p.list_items, "image_count": p.images,
        "internal_links": p.internal_links, "external_links": p.external_links,
        "schema_types": sorted(set(p.schema_types)),
    }


def main():
    ap = argparse.ArgumentParser(description="Fetch a URL and extract structured content + SEO signals.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", action="append", help="URL to fetch (repeatable)")
    g.add_argument("--urls-file", help="JSON array of URLs or crawl inventory")
    ap.add_argument("--delay", type=float, default=0.5, help="delay between fetches (s)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    if args.url:
        urls = args.url
    else:
        with open(args.urls_file, encoding="utf-8") as f:
            doc = json.load(f)
        if isinstance(doc, dict) and "urls" in doc:
            urls = [r["url"] if isinstance(r, dict) else r for r in doc["urls"]]
        elif isinstance(doc, list):
            urls = [r["url"] if isinstance(r, dict) else r for r in doc]
        else:
            sys.exit("ERROR: --urls-file must be a URL array or crawl inventory.")

    results = []
    for u in urls:
        results.append(extract(u))
        time.sleep(args.delay)

    payload = results[0] if (args.url and len(results) == 1) else results
    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(results)} pages extracted -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
