#!/usr/bin/env python3
"""serp_probe.py — Keyless SERP probe for SEO ground-truth signals.

Deterministic, stdlib-only. Runs a web search via the keyless DuckDuckGo HTML endpoint
(html.duckduckgo.com/html) and returns ranked {position, title, url, snippet, domain}.
Two modes the SEO skills need:

  search   — run a query, return ranked organic results. With --target-domain, also report
             the target's rank/URL and the co-ranking competitor domains (ground truth).
  site     — run a `site:<domain>` query to estimate indexed-page footprint and list URLs.

No paid SEO API. This is the free, real SERP-position layer; SimilarWeb traffic estimates
come from render_page.mjs against the SimilarWeb free page. No LLM — the agent synthesizes.

Note: this is a public HTML endpoint and may rate-limit; the script backs off on errors.
A Robomotion deployment swaps this for the robomotion-serp Search node (proxy + geo).

Examples:
  serp_probe.py search --query "best rpa software" --target-domain uipath.com
  serp_probe.py site --domain example.com --max-results 50 --output ${WORKSPACE}/indexed.json
"""
import argparse
import gzip
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ENDPOINT = "https://html.duckduckgo.com/html/"


def http_post(query, timeout=30):
    data = urllib.parse.urlencode({"q": query}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data, headers={
        "User-Agent": UA, "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (202, 429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return None
    return None


RESULT_RE = re.compile(
    r'<a[^>]+class="result__a"[^>]+href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>'
    r'.*?(?:class="result__snippet"[^>]*>(?P<snippet>.*?)</a>)?', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def strip(s):
    return html.unescape(TAG_RE.sub("", s or "")).strip()


def unwrap(url):
    # DDG wraps redirects: /l/?uddg=<encoded>
    if "uddg=" in url:
        m = re.search(r"uddg=([^&]+)", url)
        if m:
            return urllib.parse.unquote(m.group(1))
    if url.startswith("//"):
        return "https:" + url
    return url


def parse_results(htmltext, limit):
    results, seen = [], set()
    for m in RESULT_RE.finditer(htmltext):
        url = unwrap(m.group("url"))
        if not url.startswith("http"):
            continue
        domain = urllib.parse.urlparse(url).netloc.lower().lstrip("www.")
        if url in seen:
            continue
        seen.add(url)
        results.append({
            "position": len(results) + 1,
            "title": strip(m.group("title")),
            "url": url,
            "snippet": strip(m.group("snippet")),
            "domain": domain,
        })
        if len(results) >= limit:
            break
    return results


def norm_domain(d):
    return d.lower().replace("https://", "").replace("http://", "").strip("/").lstrip("www.")


def cmd_search(args):
    text = http_post(args.query)
    if text is None:
        print(json.dumps({"query": args.query, "error": "SERP fetch failed (rate-limited?)",
                          "results": []}, indent=2))
        return
    results = parse_results(text, args.max_results)
    out = {"query": args.query, "result_count": len(results), "results": results}
    if args.target_domain:
        tgt = norm_domain(args.target_domain)
        hit = next((r for r in results if tgt in r["domain"]), None)
        out["target_domain"] = tgt
        out["target_rank"] = hit["position"] if hit else None
        out["target_url"] = hit["url"] if hit else ""
        out["co_ranking_domains"] = sorted({r["domain"] for r in results if tgt not in r["domain"]})
    emit(out, args.output)


def cmd_site(args):
    dom = norm_domain(args.domain)
    text = http_post(f"site:{dom}")
    if text is None:
        print(json.dumps({"domain": dom, "error": "SERP fetch failed (rate-limited?)",
                          "indexed_urls": []}, indent=2))
        return
    results = parse_results(text, args.max_results)
    urls = [r["url"] for r in results if dom in r["domain"]]
    emit({
        "domain": dom,
        "site_query": f"site:{dom}",
        "indexed_url_sample": urls,
        "indexed_sample_count": len(urls),
        "note": "sample of indexed pages from one SERP page; not an exact index count",
    }, args.output)


def emit(obj, output):
    s = json.dumps(obj, ensure_ascii=False, indent=2)
    if output == "-":
        print(s)
    else:
        with open(output, "w", encoding="utf-8") as f:
            f.write(s + "\n")
        print(f"-> {output}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Keyless SERP probe for SEO ground-truth signals.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="run a query, return ranked results (+ target rank)")
    s.add_argument("--query", required=True)
    s.add_argument("--target-domain", default="", help="report this domain's rank + co-rankers")
    s.add_argument("--max-results", type=int, default=30)
    s.add_argument("--output", default="-")
    g = sub.add_parser("site", help="site:<domain> indexed-page footprint sample")
    g.add_argument("--domain", required=True)
    g.add_argument("--max-results", type=int, default=50)
    g.add_argument("--output", default="-")
    args = ap.parse_args()
    {"search": cmd_search, "site": cmd_site}[args.cmd](args)


if __name__ == "__main__":
    main()
