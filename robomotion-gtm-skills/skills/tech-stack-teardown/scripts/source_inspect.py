#!/usr/bin/env python3
"""source_inspect.py — HTML-source tech detection (keyless detection signal #1).

Deterministic, stdlib-only. Fetches the homepage HTML and matches it against the
signatures.json DB (200+ technologies) via sigdb: script-src patterns, inline
html patterns, meta generator, and Set-Cookie names from the fetch headers.

Each detection carries category + confidence + evidence strings. For JS-injected
tags (loaded via a tag manager), the rendered detector (detect_requests.mjs) and
the headers layer (fetch_headers.py) catch what raw source misses.

Examples:
  source_inspect.py --domain example.com
  source_inspect.py --domain example.com --output ${WORKSPACE}/source.json
"""
import argparse
import gzip
import json
import re
import sys
import urllib.error
import urllib.request

import sigdb

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def fetch_html(domain):
    targets = [domain] if domain.startswith("http") else [f"https://{domain}", f"http://{domain}"]
    for url in targets:
        req = urllib.request.Request(
            url, headers={"User-Agent": UA, "Accept-Encoding": "gzip", "Accept": "text/html,*/*"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    try:
                        raw = gzip.decompress(raw)
                    except OSError:
                        pass
                charset = r.headers.get_content_charset() or "utf-8"
                cookies = []
                for k, v in r.headers.items():
                    if k.lower() == "set-cookie":
                        cookies.append(v.split("=", 1)[0].strip())
                return raw.decode(charset, "replace"), r.geturl(), cookies
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ConnectionError, OSError):
            continue
    return None, "", []


def main():
    ap = argparse.ArgumentParser(description="Detect tools from homepage HTML source (keyless).")
    ap.add_argument("--domain", required=True, help="company domain or URL (e.g. example.com)")
    ap.add_argument("--signatures", default=None, help="path to signatures.json (default: bundled)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    domain = args.domain.strip()
    if not domain.startswith("http"):
        domain = domain.lower().strip("/")
    html, final_url, cookies = fetch_html(domain)
    if html is None:
        print(json.dumps({"domain": domain, "error": "homepage fetch failed",
                          "detected": [], "stats": {"html_chars": 0}}, indent=2))
        return

    techs = sigdb.load_signatures(args.signatures)
    html_hits = sigdb.match_html(html, techs)
    cookie_hits = sigdb.match_cookies(cookies, techs)
    detected = sigdb.merge(html_hits, cookie_hits)

    # account/pixel-ID extraction (cross-company attribution fingerprint).
    # An id_pattern match is itself strong evidence the tech is present, so promote any
    # id-only hit to a detection (mirrors the rendered detector's id_pattern signal).
    id_map = sigdb.extract_account_ids(html, techs)
    cat_of = {t["name"]: t["category"] for t in techs}
    impl_of = {t["name"]: t.get("gtm_implication", "") for t in techs}
    seen = {d["name"] for d in detected}
    for name, info in id_map.items():
        if name not in seen:
            detected.append({
                "name": name, "category": cat_of.get(name, "unknown"),
                "confidence": sigdb._conf({"id_pattern"}),
                "signals": ["id_pattern"], "evidence": [f"id:{info['ids'][0]}"],
                "gtm_implication": impl_of.get(name, ""),
            })
            seen.add(name)
    sigdb.attach_account_ids(detected, id_map)
    detected.sort(key=lambda r: (-r["confidence"], r["category"], r["name"]))
    account_ids = {name: info["ids"] for name, info in id_map.items()}

    tm_present = bool(re.search(r"googletagmanager\.com/gtm\.js|gtm-[a-z0-9]+", html, re.I))
    by_cat = {}
    for d in detected:
        by_cat.setdefault(d["category"], []).append(d["name"])

    result = {
        "domain": domain,
        "final_url": final_url,
        "detected": detected,
        "by_category": by_cat,
        "account_ids": account_ids,
        "tag_manager_present": tm_present,
        "stats": {
            "html_chars": len(html),
            "tools_detected": len(detected),
            "note": ("tag manager present — dynamically-loaded tools may be missing; "
                     "re-check with detect_requests.mjs (rendered requests) and fetch_headers.py"
                     if tm_present else ""),
        },
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"source inspect {domain} -> {args.output} ({len(detected)} detected)", file=sys.stderr)


if __name__ == "__main__":
    main()
