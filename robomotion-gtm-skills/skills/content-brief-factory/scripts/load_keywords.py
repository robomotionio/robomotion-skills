#!/usr/bin/env python3
"""load_keywords.py — Normalize a keyword list and match it against an existing catalog.

Keyless. Stdlib only. Deterministic glue for `content-brief-factory` step 1
(existing-coverage check). Loads 1-50 keywords (CSV, newline list, or comma string),
normalizes them, and — if a `site-content-catalog` JSON is supplied — flags each keyword
as "new" vs "update" by fuzzy-matching its tokens against catalogued page titles/slugs and
lists internal-link candidates. The AGENT decides the final new-vs-update call + the angle.

Examples:
  load_keywords.py --keywords "rpa software,workflow automation" --catalog catalog.json
  load_keywords.py --input keywords.csv --catalog catalog.json --output coverage.json
"""
import argparse
import csv
import json
import re
import sys
import urllib.parse


def load_keywords(args):
    kws = []
    if args.keywords:
        kws.extend(k for k in re.split(r"[,\n]", args.keywords))
    if args.input:
        with open(args.input, newline="", encoding="utf-8") as f:
            sample = f.read()
        if "," in sample.splitlines()[0] if sample.splitlines() else False:
            for row in csv.reader(sample.splitlines()):
                kws.extend(row)
        else:
            kws.extend(sample.splitlines())
    out, seen = [], set()
    for k in kws:
        k = k.strip().strip('"').lower()
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def tokens(s):
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def slug_tokens(url):
    path = urllib.parse.urlsplit(url).path
    return set(re.findall(r"[a-z0-9]+", path.lower()))


def load_catalog(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("pages", [])
    return data


def main():
    ap = argparse.ArgumentParser(description="Normalize keywords + coverage-match a catalog (keyless).")
    ap.add_argument("--keywords", default="", help="comma/newline keyword string")
    ap.add_argument("--input", default="", help="CSV or newline keyword file")
    ap.add_argument("--catalog", default="", help="site-content-catalog JSON for coverage check")
    ap.add_argument("--match-threshold", type=float, default=0.6,
                    help="token-overlap fraction to count as covered (default 0.6)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    keywords = load_keywords(args)
    if not keywords:
        sys.exit("ERROR: no keywords (use --keywords or --input).")
    if len(keywords) > 50:
        print(f"WARNING: {len(keywords)} keywords; capping at 50.", file=sys.stderr)
        keywords = keywords[:50]

    catalog = load_catalog(args.catalog)
    pages = []
    for p in catalog:
        title = p.get("title") or ""
        url = p.get("url") or ""
        pages.append({"url": url, "title": title,
                      "tokens": tokens(title) | slug_tokens(url)})

    results = []
    for kw in keywords:
        kt = tokens(kw)
        best, best_score = None, 0.0
        links = []
        for p in pages:
            if not kt:
                continue
            overlap = len(kt & p["tokens"]) / len(kt)
            if overlap >= 0.3:
                links.append({"url": p["url"], "title": p["title"], "overlap": round(overlap, 2)})
            if overlap > best_score:
                best, best_score = p, overlap
        links.sort(key=lambda x: x["overlap"], reverse=True)
        covered = best_score >= args.match_threshold
        results.append({
            "keyword": kw,
            "recommendation": "update" if covered else "new",
            "best_match": ({"url": best["url"], "title": best["title"],
                            "score": round(best_score, 2)} if best and best_score > 0 else None),
            "internal_link_candidates": links[:8],
        })

    out = {"keyword_count": len(results), "catalog_pages": len(pages), "keywords": results}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"{len(results)} keywords ({sum(1 for r in results if r['recommendation']=='update')} update) "
              f"-> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
