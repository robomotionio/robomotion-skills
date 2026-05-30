#!/usr/bin/env python3
"""ingest_news.py — fetch + extract a news URL (or accept pasted text) for the agent.

Step 1 of news-signal-outreach: pull the article/blog/news page into clean text so the
AGENT can extract entities (companies, people, event type), evaluate ICP fit, and find the
relevance angle. NO LLM here — the script only fetches/cleans. LinkedIn/tweet sources are
JS/auth-walled; for those, run web-automation in a flow (this script returns whatever the
public fetch yields and flags partial content).

Stdlib only.

Examples:
  ingest_news.py --url https://techcrunch.com/2026/01/01/acme-raises-series-b
  ingest_news.py --text-file pasted.txt          # already have the text
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/news-signal-outreach)"


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "ignore")
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


def extract(page):
    title_m = re.search(r"(?is)<title[^>]*>(.*?)</title>", page)
    title = html.unescape(re.sub(r"\s+", " ", title_m.group(1)).strip()) if title_m else ""
    # crude meta description
    desc_m = re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', page)
    description = html.unescape(desc_m.group(1).strip()) if desc_m else ""
    body = re.sub(r"(?is)<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>", " ", page)
    paragraphs = []
    for m in re.finditer(r"(?is)<p[^>]*>(.*?)</p>", body):
        t = html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) > 40:
            paragraphs.append(t)
    full_text = re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", body))).strip()
    return title, description, paragraphs, full_text


def main():
    ap = argparse.ArgumentParser(description="Fetch + extract a news URL (or read pasted text) for the agent.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="news/article/blog URL to fetch")
    g.add_argument("--text-file", help="path to already-pasted news text")
    ap.add_argument("--max-chars", type=int, default=6000, help="cap on full_text (default 6000)")
    ap.add_argument("--output", default="-", help="output JSON path; default stdout")
    args = ap.parse_args()

    partial = False
    if args.url:
        try:
            page = fetch(args.url)
        except Exception as e:
            sys.exit(f"ERROR: fetch failed: {e}. If this is a LinkedIn/tweet/gated source, "
                     f"run the web-automation + cookie path in a Robomotion flow.")
        title, description, paragraphs, full_text = extract(page)
        if len(full_text) < 200:
            partial = True  # likely JS-rendered / gated
        src = args.url
    else:
        full_text = open(args.text_file, encoding="utf-8").read()
        title, description, paragraphs = "", "", [p.strip() for p in full_text.split("\n") if p.strip()]
        src = args.text_file

    result = {
        "source": src,
        "title": title,
        "description": description,
        "paragraphs": paragraphs[:50],
        "full_text": full_text[: args.max_chars],
        "partial_content": partial,
        "note": ("Partial/empty extraction — source is likely JS-rendered or gated; "
                 "use web-automation + session cookie." if partial else ""),
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        print(f"ingested {src} -> {args.output}{' (partial)' if partial else ''}", file=sys.stderr)


if __name__ == "__main__":
    main()
