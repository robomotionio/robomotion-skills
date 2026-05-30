#!/usr/bin/env python3
"""fetch_pages.py — Fetch competing/ranking pages and emit structured content stats.

Keyless. Stdlib only (urllib). Deterministic glue for `content-brief-factory` step 3
(competing-page analysis): given a list of URLs (the top-ranking results the agent gathered
via serp Search), fetch each and extract title, headings, word count, structure stats,
image/link counts, and a freshness hint. The AGENT does the synthesis (gap analysis,
differentiation angle, outline) from these stats + customer-voice mining.

Input: URLs as args, or a JSON file of `[{"url": ...}, ...]` / `["url", ...]` via --input.

Examples:
  fetch_pages.py --urls https://a.com/post https://b.com/guide --output pages.json
  fetch_pages.py --input serp_top10.json --max 5 --output pages.json
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request

UA = "robomotion-gtm-skills/content-brief-factory (+https://robomotion.io)"


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "ignore")
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


def strip_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def analyze(url):
    try:
        body = fetch(url)
    except Exception as e:
        return {"url": url, "error": str(e)[:200]}

    tm = re.search(r"(?is)<title[^>]*>(.*?)</title>", body)
    title = strip_html(tm.group(1)) if tm else ""

    headings = {}
    for level in ("h1", "h2", "h3"):
        hs = [strip_html(m.group(1)) for m in
              re.finditer(rf"(?is)<{level}[^>]*>(.*?)</{level}>", body)]
        headings[level] = [h for h in hs if h][:30]

    main = re.sub(r"(?is)<(script|style|nav|footer|header|aside)\b.*?</\1>", " ", body)
    text = strip_html(main)
    words = len(text.split())
    images = len(re.findall(r"<img\b", body, re.IGNORECASE))
    lists = len(re.findall(r"<(ul|ol)\b", body, re.IGNORECASE))
    links = len(re.findall(r"<a\b[^>]*href", body, re.IGNORECASE))

    # freshness hint from common date metas
    fresh = ""
    dm = re.search(r'(?i)(?:article:published_time|datePublished)["\']?\s*[:=]\s*["\']([^"\']+)', body)
    if dm:
        fresh = dm.group(1)

    # content-type hint from URL/title
    blob = (url + " " + title).lower()
    ctype = "blog-post"
    for needle, label in [("compar", "comparison"), ("vs", "comparison"),
                          ("/docs", "docs"), ("pricing", "pricing"),
                          ("case-stud", "case-study"), ("glossary", "glossary"),
                          ("guide", "guide"), ("template", "template")]:
        if needle in blob:
            ctype = label
            break

    return {
        "url": url,
        "title": title,
        "content_type": ctype,
        "word_count": words,
        "heading_counts": {k: len(v) for k, v in headings.items()},
        "headings": headings,
        "image_count": images,
        "list_count": lists,
        "link_count": links,
        "published_hint": fresh,
    }


def load_urls(args):
    urls = list(args.urls or [])
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("results") or data.get("urls") or []
        for item in data:
            if isinstance(item, str):
                urls.append(item)
            elif isinstance(item, dict) and item.get("url"):
                urls.append(item["url"])
    # dedup preserve order
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def main():
    ap = argparse.ArgumentParser(description="Fetch competing pages -> content stats (keyless).")
    ap.add_argument("--urls", nargs="*", default=[], help="page URLs to analyze")
    ap.add_argument("--input", default="", help="JSON file of URLs / serp results")
    ap.add_argument("--max", type=int, default=5, help="cap pages analyzed (default 5)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    urls = load_urls(args)[: args.max]
    if not urls:
        sys.exit("ERROR: no URLs given (use --urls or --input).")

    pages = []
    for u in urls:
        pages.append(analyze(u))
        time.sleep(0.3)

    ok = [p for p in pages if "error" not in p]
    avg_words = round(sum(p["word_count"] for p in ok) / len(ok), 0) if ok else 0
    out = {"pages": pages, "analyzed": len(ok), "avg_word_count": avg_words}

    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"{len(ok)}/{len(urls)} pages -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
