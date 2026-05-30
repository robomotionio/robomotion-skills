#!/usr/bin/env python3
"""crawl_sites.py — crawl the client site + competitor sites once into a reusable bundle.

Deterministic I/O only (keyless, stdlib urllib + html.parser). NO LLM. Captures each
site's homepage + same-domain high-signal pages (pricing, product, solutions, about,
case-studies, blog, docs) so the agent can run scorecard + every head-to-head pass over
the SAME captured content without re-fetching. The agent does all persona scoring and
consolidation.

Example:
  crawl_sites.py \
    --client "Acme=https://acme.com" \
    --competitor "Rival=https://rival.com" --competitor "Other=https://other.com" \
    --max-pages 8 --output sites.json
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

UA = "robomotion-gtm-skills/icp-website-audit (+research bot; contact site owner)"
KEY_HINTS = ("pricing", "price", "plans", "about", "customer", "case-stud", "casestud",
             "success", "story", "stories", "solution", "product", "feature", "docs",
             "documentation", "blog", "industries", "industry", "use-case", "usecase",
             "platform", "why-", "compare", "vs")


class TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "template", "svg", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.in_title = False
        self.in_heading = 0
        self.title = ""
        self.headings = []
        self._chunks = []
        self._cur = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
        elif tag == "title":
            self.in_title = True
        elif tag in ("h1", "h2", "h3"):
            self.in_heading += 1
            self._cur = []

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
        elif tag == "title":
            self.in_title = False
        elif tag in ("h1", "h2", "h3") and self.in_heading:
            self.in_heading -= 1
            h = " ".join(self._cur).strip()
            if h:
                self.headings.append(h)
            self._cur = []

    def handle_data(self, data):
        if self.skip_depth:
            return
        t = data.strip()
        if not t:
            return
        if self.in_title and not self.title:
            self.title = t
        if self.in_heading:
            self._cur.append(t)
        self._chunks.append(t)

    def text(self):
        return re.sub(r"\s+", " ", " ".join(self._chunks)).strip()


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                ctype = r.headers.get("Content-Type", "")
                if ctype and "html" not in ctype and "xml" not in ctype:
                    return None
                raw = r.read(2_000_000)
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


def discover(html, base_url):
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
        path = (pu.path + " " + href).lower()
        score = sum(1 for h in KEY_HINTS if h in path)
        if score == 0:
            continue
        clean = pu._replace(query="", fragment="").geturl()
        if clean.rstrip("/") == base_url.rstrip("/"):
            continue
        found[clean] = max(found.get(clean, 0), score)
    return [u for u, _ in sorted(found.items(), key=lambda kv: kv[1], reverse=True)]


def crawl_site(label, url, max_pages):
    url = url if url.startswith("http") else "https://" + url
    home = fetch(url)
    if home is None:
        return {"label": label, "base_url": url, "error": "could not fetch homepage", "pages": []}
    pages = []
    t, h, txt = extract(home)
    pages.append({"url": url, "title": t, "headings": h[:40], "text": txt[:20000]})
    for link in discover(home, url)[:max_pages]:
        time.sleep(0.3)
        html = fetch(link)
        if not html:
            continue
        t, h, txt = extract(html)
        pages.append({"url": link, "title": t, "headings": h[:40], "text": txt[:20000]})
    return {"label": label, "base_url": url, "pages_fetched": len(pages), "pages": pages}


def parse_spec(spec, kind):
    if "=" not in spec:
        sys.exit(f"ERROR: --{kind} must be 'Name=URL', got: {spec}")
    name, _, url = spec.partition("=")
    return name.strip(), url.strip()


def main():
    ap = argparse.ArgumentParser(description="Crawl client + competitor sites once into a bundle (keyless).")
    ap.add_argument("--client", required=True, help='client as "Name=https://url"')
    ap.add_argument("--competitor", action="append", default=[],
                    help='competitor as "Name=https://url" (repeatable, 1-3)')
    ap.add_argument("--max-pages", type=int, default=8, help="max deep pages per site (default 8)")
    ap.add_argument("--output", default="-", help="output bundle JSON (default stdout)")
    args = ap.parse_args()

    cname, curl = parse_spec(args.client, "client")
    bundle = {"client": crawl_site(cname, curl, args.max_pages), "competitors": []}
    for spec in args.competitor:
        n, u = parse_spec(spec, "competitor")
        bundle["competitors"].append(crawl_site(n, u, args.max_pages))

    out = json.dumps(bundle, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        sites = 1 + len(bundle["competitors"])
        print(f"crawled {sites} sites -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
