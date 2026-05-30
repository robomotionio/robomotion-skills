#!/usr/bin/env python3
"""detect_signal.py — keyless signal detection via web search + page extraction.

For each company in a list, runs a configurable set of search queries (funding / hiring /
news / general) against DuckDuckGo HTML (keyless; maps to robomotion-serp Search behind the
platform proxy in production), then fetches the top result pages and returns extracted text
snippets for the AGENT to read and qualify. NO LLM here — the script only fetches; the agent
judges relevance, extracts amount/date/role, confirms recency, and scores.

Stdlib only.

Examples:
  detect_signal.py --companies companies.json --signal funding --per-company 4
  detect_signal.py --companies companies.csv --signal hiring --extra "RPA developer"
"""
import argparse
import csv
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DDG_HTML = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/detect-signal)"

# Query templates per signal type. {c}=company, {d}=domain, {x}=extra term.
SIGNAL_QUERIES = {
    "funding": [
        '"{c}" raised funding',
        '"{c}" series A OR series B OR seed round',
        '"{c}" announces funding investors',
    ],
    "hiring": [
        '"{c}" hiring {x} site:linkedin.com/jobs',
        '"{c}" {x} job site:lever.co OR site:greenhouse.io',
        '"{c}" careers {x}',
    ],
    "news": [
        '"{c}" announcement OR launch OR acquisition OR expansion',
        '"{c}" news {x}',
    ],
    "general": [
        '"{c}" {x}',
        '{c} {x} news',
    ],
    "winback": [
        '"{c}" funding OR raised OR series',
        '"{c}" hiring OR expansion OR launch',
    ],
}


def http(req, timeout=30):
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


def ddg_search(query, limit=4):
    data = urllib.parse.urlencode({"q": query}).encode()
    req = urllib.request.Request(DDG_HTML, data=data, headers={"User-Agent": UA})
    try:
        page = http(req)
    except Exception as e:
        print(f"WARN: search failed '{query}': {e}", file=sys.stderr)
        return []
    out = []
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S):
        href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        if "uddg=" in href:
            href = urllib.parse.unquote(re.sub(r"^.*uddg=", "", href).split("&")[0])
        sm = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', page[m.end():m.end() + 1500], re.S)
        snippet = re.sub(r"<[^>]+>", "", sm.group(1)) if sm else ""
        out.append({"title": html.unescape(title.strip()),
                    "url": href, "snippet": html.unescape(snippet.strip())})
        if len(out) >= limit:
            break
    return out


def extract_page(url, max_chars=2500):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        page = http(req, timeout=25)
    except Exception:
        return ""
    page = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", page)
    text = re.sub(r"(?s)<[^>]+>", " ", page)
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    return text[:max_chars]


def load_companies(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    s = raw.lstrip()
    if s.startswith("[") or s.startswith("{"):
        data = json.loads(raw)
        data = data if isinstance(data, list) else [data]
        return [{"company": d.get("company") or d.get("name", ""), "domain": d.get("domain", "")}
                if isinstance(d, dict) else {"company": str(d), "domain": ""} for d in data]
    out = []
    for row in csv.DictReader(io.StringIO(raw)):
        out.append({"company": row.get("company") or row.get("name", ""),
                    "domain": row.get("domain", "")})
    return out


def main():
    ap = argparse.ArgumentParser(description="Keyless per-company signal detection (search + page extract; no LLM).")
    ap.add_argument("--companies", required=True, help="JSON/CSV list with company (+ optional domain)")
    ap.add_argument("--signal", default="general", choices=sorted(SIGNAL_QUERIES.keys()))
    ap.add_argument("--extra", default="", help="extra term ({x}) e.g. a role for hiring")
    ap.add_argument("--per-company", type=int, default=3, help="results to keep per company (default 3)")
    ap.add_argument("--extract", action="store_true", help="also fetch + extract top result page text")
    ap.add_argument("--output", default="-", help="output JSON path; default stdout")
    args = ap.parse_args()

    companies = load_companies(args.companies)
    templates = SIGNAL_QUERIES[args.signal]
    results = []
    for co in companies:
        c, d = co["company"], co.get("domain", "")
        if not c:
            continue
        hits, seen = [], set()
        for tmpl in templates:
            q = tmpl.format(c=c, d=d, x=args.extra)
            for h in ddg_search(q, limit=args.per_company):
                if h["url"] in seen:
                    continue
                seen.add(h["url"])
                if args.extract:
                    h["page_text"] = extract_page(h["url"])
                hits.append(h)
                if len(hits) >= args.per_company:
                    break
            time.sleep(0.4)
            if len(hits) >= args.per_company:
                break
        results.append({"company": c, "domain": d, "signal": args.signal, "evidence": hits})

    payload = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        print(f"{len(results)} companies -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
