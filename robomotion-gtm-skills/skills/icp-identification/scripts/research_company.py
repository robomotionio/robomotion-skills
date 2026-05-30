#!/usr/bin/env python3
"""research_company.py — fetch a company's homepage + same-domain key pages into a text bundle.

Deterministic I/O only (keyless, stdlib urllib + html.parser). NO LLM calls — the host
agent reads the emitted JSON bundle and synthesizes 4-6 buyer personas itself.

Strategy:
  1. Fetch the homepage with a sane User-Agent.
  2. Discover same-domain links whose path/anchor text looks like a high-signal page
     (pricing, about, customers, case-studies, solutions, product, who-it's-for, ...).
  3. Fetch up to --max-pages of those, extract visible text + headings.
  4. Emit one JSON bundle: {company, base_url, pages:[{url, title, headings, text}]}.

The agent then runs steps 2 (signal searches) and 3-7 (segment + persona synthesis) from
its own reasoning + whatever search tool it has.

Example:
  research_company.py --url https://example.com --company "Example" \
      --max-pages 8 --output bundle.json
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

UA = "robomotion-gtm-skills/buyer-persona-generator (+research bot; contact site owner)"

# Path / anchor keywords that mark a high-signal page for persona research.
KEY_HINTS = (
    "pricing", "price", "plans", "about", "customer", "case-stud", "case_stud",
    "casestud", "success", "story", "stories", "solution", "product", "feature",
    "who-it", "who-is-it", "for-", "use-case", "usecase", "industries", "industry",
    "testimonial", "review",
)


class TextExtractor(HTMLParser):
    """Collect visible text + headings, skipping script/style/nav-noise tags."""

    SKIP = {"script", "style", "noscript", "template", "svg", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.in_title = False
        self.in_heading = 0
        self.title = ""
        self.headings = []
        self._chunks = []
        self._cur_heading = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
        elif tag == "title":
            self.in_title = True
        elif tag in ("h1", "h2", "h3"):
            self.in_heading += 1
            self._cur_heading = []

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
        elif tag == "title":
            self.in_title = False
        elif tag in ("h1", "h2", "h3") and self.in_heading:
            self.in_heading -= 1
            h = " ".join(self._cur_heading).strip()
            if h:
                self.headings.append(h)
            self._cur_heading = []

    def handle_data(self, data):
        if self.skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self.in_title and not self.title:
            self.title = text
        if self.in_heading:
            self._cur_heading.append(text)
        self._chunks.append(text)

    def text(self):
        joined = " ".join(self._chunks)
        return re.sub(r"\s+", " ", joined).strip()


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                ctype = r.headers.get("Content-Type", "")
                if "html" not in ctype and "xml" not in ctype and ctype:
                    return None
                raw = r.read(2_000_000)  # 2 MB cap
                charset = r.headers.get_content_charset() or "utf-8"
                return raw.decode(charset, "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return None
    return None


def extract(html):
    p = TextExtractor()
    try:
        p.feed(html)
    except Exception:
        pass
    return p.title, p.headings, p.text()


def discover_links(html, base_url):
    """Return same-domain key-page URLs, scored by hint matches, de-duplicated."""
    base = urllib.parse.urlparse(base_url)
    found = {}
    for m in re.finditer(r'href=["\']([^"\'#]+)["\']', html, re.I):
        href = m.group(1).strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        absu = urllib.parse.urljoin(base_url, href)
        pu = urllib.parse.urlparse(absu)
        if pu.scheme not in ("http", "https"):
            continue
        if pu.netloc.replace("www.", "") != base.netloc.replace("www.", ""):
            continue
        path = (pu.path + " " + (href or "")).lower()
        score = sum(1 for h in KEY_HINTS if h in path)
        if score == 0:
            continue
        clean = pu._replace(query="", fragment="").geturl()
        if clean.rstrip("/") == base_url.rstrip("/"):
            continue
        found[clean] = max(found.get(clean, 0), score)
    return [u for u, _ in sorted(found.items(), key=lambda kv: kv[1], reverse=True)]


def main():
    ap = argparse.ArgumentParser(
        description="Fetch a company homepage + same-domain key pages into a text bundle (keyless).")
    ap.add_argument("--url", required=True, help="company homepage URL")
    ap.add_argument("--company", default="", help="company name (label only)")
    ap.add_argument("--max-pages", type=int, default=8,
                    help="max same-domain key pages to fetch beyond the homepage (default 8)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    url = args.url if args.url.startswith("http") else "https://" + args.url
    home = fetch(url)
    if home is None:
        sys.exit(f"ERROR: could not fetch homepage {url}")

    pages = []
    title, headings, text = extract(home)
    pages.append({"url": url, "title": title, "headings": headings[:40], "text": text[:20000]})

    for link in discover_links(home, url)[: args.max_pages]:
        time.sleep(0.3)  # be polite
        html = fetch(link)
        if not html:
            continue
        t, h, txt = extract(html)
        pages.append({"url": link, "title": t, "headings": h[:40], "text": txt[:20000]})

    bundle = {
        "company": args.company,
        "base_url": url,
        "pages_fetched": len(pages),
        "pages": pages,
    }
    out = json.dumps(bundle, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(pages)} pages -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
