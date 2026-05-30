#!/usr/bin/env python3
"""site_catalog.py — Crawl a site's sitemap/feeds to build a content inventory.

Keyless. Stdlib only (urllib + xml). Implements the robomotion-gtm-skills `site-content-catalog`
contract.

Discovery order: robots.txt `Sitemap:` lines -> sitemap.xml (+ sitemap-index recursion)
-> common sitemap locations -> RSS/Atom feeds. Each URL is classified by content type
from URL/title patterns (rule-based; the agent does any LLM clustering/ambiguous-case
fixups). Publishing cadence is computed from sitemap lastmod / feed dates.

`--deep N` deep-reads the first N catalog URLs and adds page stats (word count, image
count, internal-link count, has-CTA). The agent infers target keyword + funnel stage.

Examples:
  site_catalog.py --domain example.com --output catalog.json
  site_catalog.py --domain example.com --deep 10 --output catalog.json
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

UA = "robomotion-gtm-skills/site-content-catalog (+https://robomotion.io)"
SM_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
COMMON_SITEMAPS = ["/sitemap.xml", "/sitemap_index.xml", "/sitemap-index.xml", "/sitemap/sitemap.xml"]
COMMON_FEEDS = ["/feed", "/rss.xml", "/atom.xml", "/index.xml", "/blog/feed"]

TYPE_RULES = [
    ("case-study", ["case-study", "case-studies", "customers/", "success-stor"]),
    ("comparison", ["vs-", "-vs-", "/vs/", "comparison", "alternative"]),
    ("pricing", ["pricing", "/plans"]),
    ("changelog", ["changelog", "release-notes", "whats-new", "/changes"]),
    ("docs", ["/docs", "/documentation", "/api", "developer", "/reference"]),
    ("glossary", ["glossary", "/terms/", "/wiki/"]),
    ("integration", ["integration", "/connect/", "/apps/"]),
    ("legal", ["privacy", "terms", "legal", "gdpr", "cookie-policy", "dpa"]),
    ("about", ["/about", "/team", "/careers", "/company", "/contact"]),
    ("resource", ["/resources", "/ebook", "/whitepaper", "/webinar", "/guide", "/templates"]),
    ("blog-post", ["/blog/", "/post/", "/posts/", "/articles/", "/news/"]),
    ("landing-page", []),  # default fallback
]


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("exhausted retries")


def base_url(domain):
    if domain.startswith(("http://", "https://")):
        p = urllib.parse.urlsplit(domain)
        return f"{p.scheme}://{p.netloc}"
    return "https://" + domain.strip("/")


def canonical(url):
    p = urllib.parse.urlsplit(url.strip())
    return urllib.parse.urlunsplit((p.scheme or "https", p.netloc.lower(),
                                    p.path.rstrip("/") or "/", "", ""))


def sitemaps_from_robots(root):
    out = []
    try:
        body = fetch(root + "/robots.txt").decode("utf-8", "ignore")
    except Exception:
        return out
    for line in body.splitlines():
        if line.lower().startswith("sitemap:"):
            out.append(line.split(":", 1)[1].strip())
    return out


def parse_sitemap(body, depth=0):
    """Return (page_entries, child_sitemap_urls). Handles sitemap index recursion."""
    pages, children = [], []
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return pages, children
    tag = root.tag.lower()
    if tag.endswith("sitemapindex"):
        for sm in root.findall(f"{SM_NS}sitemap"):
            loc = sm.findtext(f"{SM_NS}loc")
            if loc:
                children.append(loc.strip())
    elif tag.endswith("urlset"):
        for u in root.findall(f"{SM_NS}url"):
            loc = u.findtext(f"{SM_NS}loc")
            if not loc:
                continue
            pages.append({"url": loc.strip(), "lastmod": (u.findtext(f"{SM_NS}lastmod") or "").strip()})
    return pages, children


def discover(root, max_sitemaps=50):
    seen_sm, queue, pages = set(), [], {}
    queue.extend(sitemaps_from_robots(root))
    for path in COMMON_SITEMAPS:
        queue.append(root + path)
    used_sitemap = False
    while queue and len(seen_sm) < max_sitemaps:
        sm = queue.pop(0)
        if sm in seen_sm:
            continue
        seen_sm.add(sm)
        try:
            body = fetch(sm)
        except Exception:
            continue
        p, children = parse_sitemap(body)
        if p or children:
            used_sitemap = True
        for entry in p:
            cu = canonical(entry["url"])
            if cu not in pages:
                pages[cu] = entry
        for c in children:
            if c not in seen_sm:
                queue.append(c)
    # feeds supplement recent posts
    for fp in COMMON_FEEDS:
        try:
            body = fetch(root + fp)
        except Exception:
            continue
        for u, d in feed_entries(body):
            cu = canonical(u)
            if cu not in pages:
                pages[cu] = {"url": u, "lastmod": d}
    return list(pages.values()), used_sitemap


def feed_entries(body):
    out = []
    try:
        rt = ET.fromstring(body)
    except ET.ParseError:
        return out
    atom = "{http://www.w3.org/2005/Atom}"
    if rt.tag.lower().endswith("feed"):
        for e in rt.findall(f"{atom}entry"):
            link = ""
            for ln in e.findall(f"{atom}link"):
                if ln.get("rel", "alternate") == "alternate":
                    link = ln.get("href", "")
            out.append((link, e.findtext(f"{atom}published") or e.findtext(f"{atom}updated") or ""))
    else:
        for it in rt.findall(".//item"):
            out.append((it.findtext("link") or "", it.findtext("pubDate") or ""))
    return out


def classify(url, title=""):
    blob = (url + " " + title).lower()
    for ctype, needles in TYPE_RULES:
        if any(n in blob for n in needles):
            return ctype
    return "landing-page"


def topic_cluster(url):
    """Coarse cluster = first meaningful path segment."""
    p = urllib.parse.urlsplit(url)
    segs = [s for s in p.path.strip("/").split("/") if s]
    if not segs:
        return "home"
    skip = {"blog", "post", "posts", "articles", "news", "en", "us"}
    for s in segs:
        if s not in skip and not re.fullmatch(r"\d{4}", s):
            return s.replace("-", " ")[:40]
    return segs[0].replace("-", " ")[:40]


def parse_dt(s):
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(s)
        except Exception:
            return None
    if dt and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def strip_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def deep_read(url, root):
    try:
        body = fetch(url).decode("utf-8", "ignore")
    except Exception:
        return {}
    body_only = re.sub(r"(?is)<(script|style|nav|footer|header)\b.*?</\1>", " ", body)
    text = strip_html(body_only)
    words = len(text.split())
    images = len(re.findall(r"<img\b", body, re.IGNORECASE))
    host = urllib.parse.urlsplit(root).netloc.lower()
    internal = 0
    for m in re.finditer(r'href\s*=\s*["\']([^"\']+)["\']', body, re.IGNORECASE):
        h = urllib.parse.urljoin(url, m.group(1))
        if urllib.parse.urlsplit(h).netloc.lower() == host:
            internal += 1
    has_cta = bool(re.search(r"(?i)>\s*(get started|sign up|book a demo|try (it )?free|"
                             r"start (your )?free|contact sales|request (a )?demo)\s*<", body))
    tm = re.search(r"(?is)<title[^>]*>(.*?)</title>", body)
    title = strip_html(tm.group(1)) if tm else ""
    return {"title": title, "word_count": words, "image_count": images,
            "internal_link_count": internal, "has_cta": has_cta}


def main():
    ap = argparse.ArgumentParser(description="Crawl a site's sitemap/feeds into a content inventory (keyless).")
    ap.add_argument("--domain", required=True, help="e.g. example.com or https://example.com")
    ap.add_argument("--deep", type=int, default=0, help="deep-read the first N URLs (page stats)")
    ap.add_argument("--include-non-blog", default="true", choices=["true", "false"],
                    help="also catalog landing/docs/etc. (default true)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    root = base_url(args.domain)
    pages, used_sitemap = discover(root)

    catalog = []
    for entry in pages:
        url = entry["url"]
        ctype = classify(url)
        if args.include_non_blog == "false" and ctype != "blog-post":
            continue
        catalog.append({
            "url": url,
            "title": "",
            "date": entry.get("lastmod", ""),
            "type": ctype,
            "topic_cluster": topic_cluster(url),
        })

    # deep analysis
    for row in catalog[: args.deep]:
        stats = deep_read(row["url"], root)
        if stats.get("title"):
            row["title"] = stats.pop("title")
        else:
            stats.pop("title", None)
        row["deep_analysis"] = stats
        time.sleep(0.2)

    # summary
    by_type = Counter(r["type"] for r in catalog)
    by_topic = Counter(r["topic_cluster"] for r in catalog)
    monthly = defaultdict(int)
    dated = 0
    for r in catalog:
        dt = parse_dt(r["date"])
        if dt:
            dated += 1
            monthly[dt.strftime("%Y-%m")] += 1
    cadence = dict(sorted(monthly.items()))
    per_month = round(dated / len(cadence), 1) if cadence else 0

    summary = {
        "domain": root,
        "total_pages": len(catalog),
        "sitemap_found": used_sitemap,
        "by_type": dict(by_type.most_common()),
        "by_topic": dict(by_topic.most_common(20)),
        "publishing_cadence": {"dated_pages": dated, "by_month": cadence, "avg_per_active_month": per_month},
    }

    out = {"summary": summary, "pages": catalog}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"{len(catalog)} pages (sitemap_found={used_sitemap}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
