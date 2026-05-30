#!/usr/bin/env python3
"""blog_feed_monitor.py — Aggregate recent blog posts from one or more sites.

Keyless. Stdlib only (urllib + xml). Implements the robomotion-gtm-skills `blog-feed-monitor`
contract. RSS/Atom is the happy path: for each site URL it discovers
a feed (``<link rel="alternate">`` then common feed paths), fetches and parses RSS 2.0 /
Atom, and applies recency + keyword (OR) filters client-side, deduped by canonical URL.

When a site exposes no feed it falls back to a light scrape of the index page links
(``mode=auto``). ``mode=rss`` disables that fallback; ``mode=hostile`` reserves the
Apify last-resort path documented in the DESIGN (handled by the agent, not this script).

Examples:
  blog_feed_monitor.py --urls https://a.com https://b.com/blog --days 30
  blog_feed_monitor.py --urls https://a.com --keywords "rpa,automation" --output summary
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
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

UA = "robomotion-gtm-skills/blog-feed-monitor (+https://robomotion.io)"
COMMON_FEED_PATHS = [
    "/feed", "/rss", "/atom.xml", "/feed.xml", "/rss.xml",
    "/blog/feed", "/index.xml", "/feed/", "/blog/rss",
]
# very small set of XML namespaces we care about
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                ctype = r.headers.get("Content-Type", "")
                return r.read(), ctype
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


def canonical(url):
    """Strip query/UTM + fragment + trailing slash; lowercase host."""
    if not url:
        return ""
    p = urllib.parse.urlsplit(url.strip())
    netloc = p.netloc.lower()
    path = p.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit((p.scheme or "https", netloc, path, "", ""))


def discover_feeds(base_url):
    """Return candidate feed URLs for a site: <link alternate> hints + common paths."""
    feeds = []
    try:
        body, _ = fetch(base_url)
        text = body.decode("utf-8", "ignore")
    except Exception:
        text = ""
    # <link rel="alternate" type="application/rss+xml|atom+xml" href="...">
    for m in re.finditer(r"<link\b[^>]*>", text, re.IGNORECASE):
        tag = m.group(0)
        if "alternate" in tag.lower() and ("rss+xml" in tag.lower() or "atom+xml" in tag.lower()):
            hm = re.search(r'href\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
            if hm:
                feeds.append(urllib.parse.urljoin(base_url, hm.group(1)))
    for path in COMMON_FEED_PATHS:
        feeds.append(urllib.parse.urljoin(base_url, path))
    # dedup preserving order
    seen, out = set(), []
    for f in feeds:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    # RFC 822 (RSS)
    try:
        dt = parsedate_to_datetime(s)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
    except (TypeError, ValueError, IndexError):
        pass
    # ISO 8601 (Atom)
    iso = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_feed(body, source):
    """Parse RSS 2.0 or Atom XML bytes into normalized post dicts. Returns [] on failure."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return None  # not XML / not a feed
    posts = []
    tag = root.tag.lower()
    if tag.endswith("rss") or root.find("channel") is not None:
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else root.findall(".//item")
        for it in items:
            link = (it.findtext("link") or "").strip()
            posts.append({
                "title": strip_html(it.findtext("title") or ""),
                "url": link,
                "date": it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date") or "",
                "summary": strip_html(it.findtext("description") or "")[:500],
                "source": source,
            })
    elif tag.endswith("feed"):  # Atom
        for entry in root.findall(f"{ATOM_NS}entry"):
            link = ""
            for ln in entry.findall(f"{ATOM_NS}link"):
                rel = ln.get("rel", "alternate")
                if rel == "alternate" or not link:
                    link = ln.get("href", "") or link
            summary = entry.findtext(f"{ATOM_NS}summary") or entry.findtext(f"{ATOM_NS}content") or ""
            posts.append({
                "title": strip_html(entry.findtext(f"{ATOM_NS}title") or ""),
                "url": link.strip(),
                "date": (entry.findtext(f"{ATOM_NS}published")
                         or entry.findtext(f"{ATOM_NS}updated") or ""),
                "summary": strip_html(summary)[:500],
                "source": source,
            })
    else:
        return None
    return posts


def scrape_index(base_url, source):
    """No-feed fallback: pull anchor links that look like posts from the index page."""
    try:
        body, _ = fetch(base_url)
        text = body.decode("utf-8", "ignore")
    except Exception:
        return []
    posts, seen = [], set()
    for m in re.finditer(r'<a\b[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>',
                         text, re.IGNORECASE | re.DOTALL):
        href, label = m.group(1), strip_html(m.group(2))
        url = urllib.parse.urljoin(base_url, href)
        cu = canonical(url)
        # heuristic: same host, has a multi-segment path, a readable label
        bu = urllib.parse.urlsplit(base_url)
        pu = urllib.parse.urlsplit(url)
        if pu.netloc.lower() != bu.netloc.lower():
            continue
        if len(pu.path.strip("/").split("/")) < 1 or not pu.path.strip("/"):
            continue
        if len(label) < 12 or cu in seen:
            continue
        seen.add(cu)
        posts.append({"title": label, "url": url, "date": "", "summary": "", "source": source})
    return posts


def main():
    ap = argparse.ArgumentParser(description="Aggregate recent blog posts via RSS/Atom (keyless).")
    ap.add_argument("--urls", nargs="+", required=True, help="blog/site URLs (one or many)")
    ap.add_argument("--keywords", default="", help="comma-separated OR filter on title+summary")
    ap.add_argument("--days", type=int, default=30, help="only posts from the last N days (default 30)")
    ap.add_argument("--max-posts", type=int, default=50, help="cap on returned posts (default 50)")
    ap.add_argument("--mode", default="auto", choices=["auto", "rss", "hostile"],
                    help="auto=feed then index scrape; rss=feed only; hostile=agent handles apify")
    ap.add_argument("--output", default="json", choices=["json", "summary"])
    args = ap.parse_args()

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]

    all_posts = []
    errors = []
    for site in args.urls:
        site_posts = None
        for feed_url in discover_feeds(site):
            try:
                body, _ = fetch(feed_url)
            except Exception:
                continue
            parsed = parse_feed(body, site)
            if parsed:
                site_posts = parsed
                break
        if site_posts is None and args.mode == "auto":
            site_posts = scrape_index(site, site)
        if not site_posts:
            errors.append(site)
            continue
        all_posts.extend(site_posts)

    # dedup by canonical url
    seen, deduped = set(), []
    for p in all_posts:
        cu = canonical(p["url"])
        if not cu or cu in seen:
            continue
        seen.add(cu)
        p["canonical_url"] = cu
        deduped.append(p)

    # date filter (keep undated when no feed gave a date)
    def in_window(p):
        dt = parse_date(p.get("date"))
        if dt is None:
            return True
        return dt >= cutoff
    posts = [p for p in deduped if in_window(p)]

    # keyword OR filter
    if keywords:
        def keep(p):
            blob = (p["title"] + " " + p["summary"]).lower()
            return any(k in blob for k in keywords)
        posts = [p for p in posts if keep(p)]

    # sort newest-first (undated sink to bottom)
    def sort_key(p):
        dt = parse_date(p.get("date"))
        return dt or datetime.min.replace(tzinfo=timezone.utc)
    posts.sort(key=sort_key, reverse=True)
    posts = posts[: args.max_posts]

    if args.output == "summary":
        if not posts:
            print("No blog posts matched.")
        for p in posts:
            print(f"- {p['title']}")
            print(f"    {p['url']}  [{p.get('date', '') or 'undated'}]  ({p['source']})")
        if errors:
            print(f"\nSkipped (no feed/index): {', '.join(errors)}", file=sys.stderr)
    else:
        json.dump({"posts": posts, "skipped": errors}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
