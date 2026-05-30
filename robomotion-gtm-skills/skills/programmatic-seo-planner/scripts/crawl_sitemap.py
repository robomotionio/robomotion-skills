#!/usr/bin/env python3
"""crawl_sitemap.py — keyless content inventory via sitemap.xml / RSS / blog index.

For a target domain, discover its indexed URLs and titles by:
  1. reading robots.txt for `Sitemap:` directives,
  2. fetching sitemap.xml (recursing sitemap indexes),
  3. falling back to RSS/Atom feeds and a blog-index HTML scrape.

Returns {url, lastmod, title} rows. DETERMINISTIC fetch/parse only — no
classification or clustering (the host agent infers topics/types from titles+URLs).
Stdlib only (urllib + html.parser + xml via regex-free html.parser where possible).

Example:
  crawl_sitemap.py --domain example.com --max-urls 2000 --output inventory.json
  crawl_sitemap.py --domain https://example.com/blog --titles --output inv.json
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

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills-seo/1.0; +sitemap-inventory)"
LOC_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.I | re.S)
LASTMOD_RE = re.compile(r"<lastmod>\s*(.*?)\s*</lastmod>", re.I | re.S)
SITEMAP_BLOCK_RE = re.compile(r"<sitemap>(.*?)</sitemap>", re.I | re.S)
URL_BLOCK_RE = re.compile(r"<url>(.*?)</url>", re.I | re.S)
ITEM_LINK_RE = re.compile(r"<link[^>]*>(.*?)</link>|<link[^>]*href=\"(.*?)\"", re.I | re.S)


def normalize_domain(d):
    d = d.strip()
    if not d.startswith("http"):
        d = "https://" + d
    return d.rstrip("/")


def base_origin(url):
    p = urllib.parse.urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                ctype = r.headers.get("Content-Type", "")
                return r.read().decode("utf-8", "ignore"), ctype
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return None, ""
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return None, ""
    return None, ""


class TitleLinkParser(HTMLParser):
    """Pull <title> and anchor hrefs+text from a blog index page."""
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self.links = []  # (href, text)
        self._cur_href = None
        self._cur_text = []

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self._cur_href = href
                self._cur_text = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._cur_href is not None:
            self.links.append((self._cur_href, " ".join(self._cur_text).strip()))
            self._cur_href = None

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._cur_href is not None:
            self._cur_text.append(data.strip())


def discover_sitemaps(origin):
    found = []
    robots, _ = fetch(origin + "/robots.txt")
    if robots:
        for line in robots.splitlines():
            if line.lower().startswith("sitemap:"):
                found.append(line.split(":", 1)[1].strip())
    if not found:
        found = [origin + "/sitemap.xml", origin + "/sitemap_index.xml"]
    return found


def parse_sitemap(xml, max_urls):
    """Return (child_sitemaps, url_rows)."""
    child = []
    rows = []
    if SITEMAP_BLOCK_RE.search(xml):
        for block in SITEMAP_BLOCK_RE.findall(xml):
            m = LOC_RE.search(block)
            if m:
                child.append(m.group(1))
    for block in URL_BLOCK_RE.findall(xml):
        loc = LOC_RE.search(block)
        if not loc:
            continue
        lm = LASTMOD_RE.search(block)
        rows.append({"url": loc.group(1), "lastmod": lm.group(1) if lm else "", "title": ""})
        if len(rows) >= max_urls:
            break
    if not rows and not child:  # plain <loc> listing
        for loc in LOC_RE.findall(xml):
            rows.append({"url": loc, "lastmod": "", "title": ""})
            if len(rows) >= max_urls:
                break
    return child, rows


def crawl_via_sitemap(origin, max_urls):
    rows, seen_sm, queue = [], set(), discover_sitemaps(origin)
    while queue and len(rows) < max_urls:
        sm = queue.pop(0)
        if sm in seen_sm:
            continue
        seen_sm.add(sm)
        body, _ = fetch(sm)
        if not body:
            continue
        child, urls = parse_sitemap(body, max_urls - len(rows))
        queue.extend(c for c in child if c not in seen_sm)
        rows.extend(urls)
        time.sleep(0.1)
    return rows


def crawl_via_feed(origin, max_urls):
    rows = []
    for path in ("/rss.xml", "/feed", "/feed.xml", "/atom.xml", "/index.xml", "/blog/rss.xml"):
        body, _ = fetch(origin + path)
        if not body or "<item" not in body.lower() and "<entry" not in body.lower():
            continue
        for block in re.findall(r"<(?:item|entry)>(.*?)</(?:item|entry)>", body, re.I | re.S):
            loc = LOC_RE.search(block)
            link = None
            if loc:
                link = loc.group(1)
            else:
                m = re.search(r"<link[^>]*href=\"(.*?)\"", block, re.I) or \
                    re.search(r"<link>(.*?)</link>", block, re.I)
                if m:
                    link = m.group(1)
            tm = re.search(r"<title>(.*?)</title>", block, re.I | re.S)
            if link:
                title = re.sub(r"<.*?>", "", tm.group(1)).strip() if tm else ""
                rows.append({"url": link.strip(), "lastmod": "", "title": title})
            if len(rows) >= max_urls:
                break
        if rows:
            break
    return rows


def crawl_via_index(origin, max_urls):
    rows = []
    for path in ("", "/blog", "/blog/", "/resources", "/learn", "/articles"):
        body, ctype = fetch(origin + path)
        if not body or "html" not in ctype.lower():
            continue
        p = TitleLinkParser()
        try:
            p.feed(body)
        except Exception:
            continue
        host = urllib.parse.urlparse(origin).netloc
        for href, text in p.links:
            full = urllib.parse.urljoin(origin + path + "/", href)
            if urllib.parse.urlparse(full).netloc != host:
                continue
            if full.rstrip("/") == origin.rstrip("/"):
                continue
            rows.append({"url": full.split("#")[0], "lastmod": "", "title": text})
            if len(rows) >= max_urls:
                break
        if rows:
            break
    # dedup
    seen, out = set(), []
    for r in rows:
        if r["url"] not in seen:
            seen.add(r["url"])
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser(description="Keyless content inventory via sitemap/RSS/index.")
    ap.add_argument("--domain", required=True, help="target domain or URL")
    ap.add_argument("--max-urls", type=int, default=2000, help="cap on URLs returned")
    ap.add_argument("--titles", action="store_true",
                    help="fetch each page to extract <title> (slower; only for small sets)")
    ap.add_argument("--title-limit", type=int, default=60, help="max pages to fetch titles for")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    domain = normalize_domain(args.domain)
    origin = base_origin(domain)

    rows = crawl_via_sitemap(origin, args.max_urls)
    method = "sitemap"
    if not rows:
        rows = crawl_via_feed(origin, args.max_urls)
        method = "feed"
    if not rows:
        rows = crawl_via_index(domain, args.max_urls)
        method = "index"

    if args.titles:
        for r in rows[: args.title_limit]:
            if r["title"]:
                continue
            body, ctype = fetch(r["url"])
            if body and "html" in ctype.lower():
                m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
                if m:
                    r["title"] = re.sub(r"\s+", " ", m.group(1)).strip()
            time.sleep(0.1)

    payload = {"domain": domain, "origin": origin, "method": method,
               "count": len(rows), "urls": rows}
    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(rows)} URLs via {method} -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
