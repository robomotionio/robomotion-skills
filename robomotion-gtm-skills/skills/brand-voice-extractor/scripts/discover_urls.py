#!/usr/bin/env python3
"""discover_urls.py — Enumerate candidate content URLs from a site/blog root.

Keyless, stdlib only. Tries, in order: sitemap.xml (and sitemap index), then a crawl of
same-host links on the root page. Classifies each URL by a crude path heuristic
(blog / case-study / landing / comparison / other) so the agent can pick a diverse
10-20 sample. The agent makes the final selection — this just supplies candidates.

Example:
  discover_urls.py --root https://acme.com/blog --max 200 --output candidates.json
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

UA = "robomotion-gtm-skills/brand-voice-extractor (+https://agentskills.io)"

CLASS_RULES = [
    ("case-study", re.compile(r"/(case-?stud(y|ies)|customers?|success)", re.I)),
    ("comparison", re.compile(r"/(vs|versus|compare|alternative)", re.I)),
    ("blog", re.compile(r"/(blog|posts?|articles?|insights?|resources?|guides?)", re.I)),
    ("landing", re.compile(r"/(product|features?|solutions?|platform|pricing|use-?cases?)", re.I)),
]


def classify(url):
    path = urllib.parse.urlsplit(url).path
    for label, rx in CLASS_RULES:
        if rx.search(path):
            return label
    return "other"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                charset = r.headers.get_content_charset() or "utf-8"
                return r.read().decode(charset, "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("exhausted retries")


def from_sitemap(root, host, limit):
    """Walk sitemap.xml / sitemap index. Returns [] if none found."""
    base = f"{urllib.parse.urlsplit(root).scheme}://{host}"
    urls = []
    queue = [urllib.parse.urljoin(base + "/", "sitemap.xml")]
    seen_sitemaps = set()
    loc_rx = re.compile(r"<loc>\s*([^<]+?)\s*</loc>", re.I)
    while queue and len(urls) < limit:
        sm = queue.pop(0)
        if sm in seen_sitemaps:
            continue
        seen_sitemaps.add(sm)
        try:
            body = fetch(sm)
        except Exception:  # noqa: BLE001
            continue
        locs = [u.strip() for u in loc_rx.findall(body)]
        for loc in locs:
            if loc.endswith(".xml") or "sitemap" in loc.lower():
                if len(seen_sitemaps) < 25:
                    queue.append(loc)
            elif urllib.parse.urlsplit(loc).netloc.endswith(host):
                urls.append(loc)
    return urls


def from_crawl(root, host, limit):
    try:
        html = fetch(root)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERROR: could not fetch root {root}: {e}")
    p = LinkParser()
    p.feed(html)
    urls = []
    for href in p.hrefs:
        absu = urllib.parse.urljoin(root, href.split("#")[0])
        sp = urllib.parse.urlsplit(absu)
        if sp.scheme not in ("http", "https"):
            continue
        if not sp.netloc.endswith(host):
            continue
        urls.append(urllib.parse.urlunsplit((sp.scheme, sp.netloc, sp.path, sp.query, "")))
        if len(urls) >= limit * 3:
            break
    return urls


def main():
    ap = argparse.ArgumentParser(
        description="Enumerate + classify candidate content URLs from a site/blog root.")
    ap.add_argument("--root", required=True, help="site or blog root URL")
    ap.add_argument("--max", type=int, default=200, help="max candidate URLs (default 200)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    host = urllib.parse.urlsplit(args.root).netloc
    if not host:
        sys.exit("ERROR: --root must be an absolute URL (e.g. https://acme.com/blog)")

    urls = from_sitemap(args.root, host, args.max)
    source = "sitemap"
    if len(urls) < 5:
        urls = from_crawl(args.root, host, args.max)
        source = "crawl"

    # dedup preserving order, drop obvious non-content
    seen, candidates = set(), []
    skip_rx = re.compile(r"\.(png|jpe?g|gif|svg|webp|pdf|zip|css|js|ico|xml|json)$|"
                         r"/(tag|tags|category|author|page)/", re.I)
    for u in urls:
        if u in seen or skip_rx.search(u):
            continue
        seen.add(u)
        candidates.append({"url": u, "type": classify(u)})
        if len(candidates) >= args.max:
            break

    by_type = {}
    for c in candidates:
        by_type.setdefault(c["type"], 0)
        by_type[c["type"]] += 1

    out = {"root": args.root, "source": source, "count": len(candidates),
           "by_type": by_type, "candidates": candidates}
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(candidates)} candidates ({source}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
