#!/usr/bin/env python3
"""scrape_speakers.py — extract speakers from a conference /speakers page (keyless).

Fetches the page HTML and tries multiple extraction strategies, keeping whichever yields
the MOST speakers (never merges conflicting strategies):
  (a) speaker/presenter/faculty/panelist CSS-class cards
  (b) repeated heading+paragraph blocks
  (c) JSON-LD structured data (schema.org Person)
  (d) Sched.com / Sessionize platform embeds (detected, hinted for the browser fallback)

Stdlib only (urllib + html.parser regex). If the page is JS-rendered and extraction is
thin, the SKILL.md routes to the Playwright degrade (scrape_speakers_pw.mjs) or an Apify
actor.

Example:
  scrape_speakers.py --url https://conf.example.com/speakers --conference "ExampleConf" \
      --output json
"""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/conference-speaker-scraper)"
TAG_RE = re.compile(r"<[^>]+>")
JSONLD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
CARD_CLASS_RE = re.compile(
    r'class=["\'][^"\']*(speaker|presenter|faculty|panelist)[^"\']*["\']', re.I)


def strip(s):
    return html.unescape(TAG_RE.sub(" ", s)).strip()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "ignore")


def split_blocks(htmltext, klass):
    """Return rough HTML blocks for elements whose class matches a speaker-card keyword."""
    blocks = []
    for m in re.finditer(
            r'<(div|li|article|section)[^>]*class=["\'][^"\']*' + klass +
            r'[^"\']*["\'][^>]*>(.*?)</\1>', htmltext, re.S | re.I):
        blocks.append(m.group(2))
    return blocks


def strategy_cards(htmltext):
    speakers = []
    for klass in ("speaker", "presenter", "faculty", "panelist"):
        for block in split_blocks(htmltext, klass):
            # name = first heading; title/company = following text
            h = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', block, re.S | re.I)
            name = strip(h.group(1)) if h else ""
            # remaining text after stripping the heading
            rest = strip(re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', "", block, flags=re.S | re.I))
            rest = re.sub(r"\s+", " ", rest)[:300]
            title, company = "", ""
            if "," in rest:
                parts = [p.strip() for p in rest.split(",", 1)]
                title, company = parts[0], parts[1] if len(parts) > 1 else ""
            else:
                title = rest
            if name and len(name) < 80:
                speakers.append({"name": name, "title": title, "company": company, "bio": rest})
        if speakers:
            break
    return speakers


def strategy_headings(htmltext):
    speakers = []
    pat = re.compile(r'<h[23][^>]*>(.*?)</h[23]>\s*<p[^>]*>(.*?)</p>', re.S | re.I)
    for m in pat.finditer(htmltext):
        name = strip(m.group(1))
        body = re.sub(r"\s+", " ", strip(m.group(2)))[:300]
        if name and len(name) < 80 and body:
            title, company = "", ""
            if "," in body:
                title, company = [x.strip() for x in body.split(",", 1)]
            else:
                title = body
            speakers.append({"name": name, "title": title, "company": company, "bio": body})
    return speakers


def strategy_jsonld(htmltext):
    speakers = []
    for block in JSONLD_RE.findall(htmltext):
        try:
            data = json.loads(block.strip())
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        # also descend into @graph / performer / subjectOf arrays
        queue = list(items)
        seen_n = 0
        while queue and seen_n < 5000:
            seen_n += 1
            node = queue.pop()
            if isinstance(node, dict):
                t = node.get("@type", "")
                if (isinstance(t, str) and t == "Person") or (isinstance(t, list) and "Person" in t):
                    speakers.append({
                        "name": node.get("name", ""),
                        "title": node.get("jobTitle", ""),
                        "company": (node.get("worksFor") or {}).get("name", "")
                        if isinstance(node.get("worksFor"), dict) else "",
                        "bio": node.get("description", ""),
                    })
                for v in node.values():
                    if isinstance(v, (list, dict)):
                        queue.append(v)
            elif isinstance(node, list):
                queue.extend(node)
    return [s for s in speakers if s["name"]]


def detect_platform(htmltext):
    if "sched.com" in htmltext or "sessionize.com" in htmltext:
        return "sched/sessionize"
    return ""


def main():
    ap = argparse.ArgumentParser(description="Extract conference speakers (keyless, multi-strategy).")
    ap.add_argument("--url", required=True, help="speakers-page URL")
    ap.add_argument("--conference", default="", help="conference name (else inferred from domain)")
    ap.add_argument("--output", default="json", choices=["json", "csv", "summary"])
    args = ap.parse_args()

    conf = args.conference or re.sub(r"^www\.", "", urllib.parse.urlparse(args.url).netloc)

    try:
        htmltext = fetch(args.url)
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR: fetch {e.code} for {args.url}")
    except Exception as e:
        sys.exit(f"ERROR: fetch failed: {e}")

    strategies = {
        "cards": strategy_cards(htmltext),
        "headings": strategy_headings(htmltext),
        "jsonld": strategy_jsonld(htmltext),
    }
    best_name, best = max(strategies.items(), key=lambda kv: len(kv[1]))
    platform = detect_platform(htmltext)

    speakers = []
    seen = set()
    for s in best:
        key = s["name"].strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        s["conference"] = conf
        speakers.append(s)

    if not speakers:
        print(f"WARN: no speakers extracted via direct strategies (best='{best_name}'). "
              f"{'Platform embed detected: ' + platform + '. ' if platform else ''}"
              f"Route to the Playwright degrade or an Apify actor.", file=sys.stderr)

    if args.output == "summary":
        print(f"# {conf}: {len(speakers)} speakers (strategy={best_name}"
              f"{', platform=' + platform if platform else ''})")
        for s in speakers:
            print(f"- {s['name']} — {s['title']}{' @ ' + s['company'] if s['company'] else ''}")
    elif args.output == "csv":
        import csv
        w = csv.writer(sys.stdout)
        w.writerow(["name", "title", "company", "conference", "bio"])
        for s in speakers:
            w.writerow([s["name"], s["title"], s["company"], s["conference"], s["bio"]])
    else:
        print(json.dumps({"conference": conf, "strategy": best_name, "platform": platform,
                          "speakers": speakers}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
