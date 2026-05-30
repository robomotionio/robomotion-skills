#!/usr/bin/env python3
"""serp_probe.py — keyless SERP-style probe for directional demand/rank signals.

Fetches a results page from a public HTML search endpoint (DuckDuckGo HTML, which
needs no key and is scrape-friendly) and returns the ranked organic results
{position, title, url, snippet}. Used to:
  - confirm a generated keyword variation returns real results (demand proxy),
  - spot-check whether a competitor URL ranks for an implied keyword,
  - run `site:domain` queries as an indexation/coverage proxy.

DETERMINISTIC fetch/parse only. The host agent infers demand/rank from results.
Stdlib only. NOTE: This is a directional signal, NOT measured search volume.
For exact volume/difficulty connect a paid keyword API (no Robomotion package).

Example:
  serp_probe.py --query "best crm for startups" --max-results 10
  serp_probe.py --query "site:competitor.com/vs" --count-only
  serp_probe.py --queries-file variations.json --output probes.json
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

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
ENDPOINT = "https://html.duckduckgo.com/html/"

RESULT_RE = re.compile(
    r'<a[^>]+class="result__a"[^>]+href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>',
    re.I | re.S,
)
SNIPPET_RE = re.compile(r'class="result__snippet"[^>]*>(?P<s>.*?)</a>', re.I | re.S)


def strip_tags(s):
    return html.unescape(re.sub(r"<.*?>", "", s)).strip()


def unwrap_ddg(url):
    """DDG sometimes wraps target URLs in a redirect — extract uddg= param."""
    if "duckduckgo.com/l/" in url or url.startswith("//duckduckgo.com/l/"):
        m = re.search(r"[?&]uddg=([^&]+)", url)
        if m:
            return urllib.parse.unquote(m.group(1))
    if url.startswith("//"):
        return "https:" + url
    return url


def search(query, max_results=10):
    data = urllib.parse.urlencode({"q": query, "kl": "us-en"}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data,
                                 headers={"User-Agent": UA,
                                          "Content-Type": "application/x-www-form-urlencoded"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                body = r.read().decode("utf-8", "ignore")
                break
        except urllib.error.HTTPError as e:
            if e.code in (429, 202) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return []
        except (urllib.error.URLError, TimeoutError):
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return []
    else:
        return []

    results, snippets = [], SNIPPET_RE.findall(body)
    for i, m in enumerate(RESULT_RE.finditer(body)):
        if len(results) >= max_results:
            break
        url = unwrap_ddg(m.group("url"))
        results.append({
            "position": i + 1,
            "title": strip_tags(m.group("title")),
            "url": url,
            "snippet": strip_tags(snippets[i]) if i < len(snippets) else "",
        })
    return results


def main():
    ap = argparse.ArgumentParser(description="Keyless SERP probe (DuckDuckGo HTML).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--query", help="single query string")
    g.add_argument("--queries-file", help="JSON file: array of strings or {suggestions:{seed:[...]}}")
    ap.add_argument("--max-results", type=int, default=10, help="results per query")
    ap.add_argument("--count-only", action="store_true",
                    help="return only the result count (indexation/demand proxy)")
    ap.add_argument("--rank-for", default="",
                    help="domain substring; report its rank position (0=not in top N)")
    ap.add_argument("--delay", type=float, default=1.0, help="delay between queries (s)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    queries = []
    if args.query:
        queries = [args.query]
    else:
        with open(args.queries_file, encoding="utf-8") as f:
            doc = json.load(f)
        if isinstance(doc, list):
            queries = [str(x) for x in doc]
        elif isinstance(doc, dict) and "suggestions" in doc:
            for vs in doc["suggestions"].values():
                queries.extend(vs)
        else:
            sys.exit("ERROR: queries-file must be a JSON array or have a 'suggestions' map.")

    out = []
    for q in queries:
        res = search(q, args.max_results)
        row = {"query": q, "result_count": len(res)}
        if not args.count_only:
            row["results"] = res
        if args.rank_for:
            pos = 0
            for r in res:
                if args.rank_for.lower() in r["url"].lower():
                    pos = r["position"]
                    break
            row["rank_for_domain"] = args.rank_for
            row["rank_position"] = pos  # 0 = not found in top N
        out.append(row)
        time.sleep(args.delay)

    payload = out[0] if (args.query and len(out) == 1) else out
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"{len(out)} queries probed -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
