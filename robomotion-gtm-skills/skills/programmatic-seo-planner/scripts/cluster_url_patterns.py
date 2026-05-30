#!/usr/bin/env python3
"""cluster_url_patterns.py — bucket crawled URLs into programmatic-SEO patterns.

Takes a crawl_sitemap.py inventory (or a plain URL list) and clusters URLs by path
regex into the standard pSEO pattern types (vs/, integrations/, for-{x}/, use-cases/,
alternatives/, glossary/what-is, templates/examples, tools/calculator, location/),
excluding editorial /blog/, /tag/, /category/ noise.

Per pattern it reports: page count, sample URLs, the inferred varying data axis (the
path segment that changes), and a URL-consistency score. DETERMINISTIC clustering only
— the host agent judges programmatic-vs-editorial, scores template quality, and finds gaps.
Stdlib only.

Example:
  cluster_url_patterns.py --input inventory_comp1.json --output patterns_comp1.json
  cluster_url_patterns.py --urls "https://x.com/vs/a,https://x.com/vs/b"
"""
import argparse
import json
import re
import sys
import urllib.parse
from collections import defaultdict

# (pattern_name, compiled path regex). The varying data axis is the path segment that
# follows the matched pattern keyword (computed in varying_segment()).
PATTERNS = [
    ("vs",            re.compile(r"/(?:vs|compare|comparison)[-/]", re.I)),
    ("alternatives",  re.compile(r"/(?:alternatives?|alternative-to)[-/]", re.I)),
    ("integrations",  re.compile(r"/(?:integrations?|connect|integrate)[-/]", re.I)),
    ("for_industry",  re.compile(r"/(?:for|solutions?)[-/]", re.I)),
    ("use_cases",     re.compile(r"/(?:use-cases?|usecases?)[-/]", re.I)),
    ("templates",     re.compile(r"/(?:templates?|examples?|samples?)[-/]", re.I)),
    ("glossary",      re.compile(r"/(?:glossary|what-is|definitions?|terms?|wiki)[-/]", re.I)),
    ("tools",         re.compile(r"/(?:tools?|calculator|generator|checker)[-/]", re.I)),
    ("location",      re.compile(r"/(?:locations?|cities|near|in)[-/]", re.I)),
]
EDITORIAL = re.compile(r"/(?:blog|news|press|tag|tags|category|categories|author|page/\d+)/", re.I)


def load_urls(args):
    urls = []
    if args.urls:
        urls = [u.strip() for u in args.urls.split(",") if u.strip()]
    else:
        with open(args.input, encoding="utf-8") as f:
            doc = json.load(f)
        if isinstance(doc, dict) and "urls" in doc:
            urls = [r["url"] if isinstance(r, dict) else r for r in doc["urls"]]
        elif isinstance(doc, list):
            urls = [r["url"] if isinstance(r, dict) else r for r in doc]
        else:
            sys.exit("ERROR: --input must be a crawl_sitemap inventory or a URL array.")
    return urls


def varying_segment(path, pattern_root):
    """The path segment AFTER the matched pattern root — the data axis value."""
    segs = [s for s in path.split("/") if s]
    # find the pattern keyword segment, return the next segment
    for i, s in enumerate(segs):
        if re.match(pattern_root, "/" + s + "/", re.I):
            if i + 1 < len(segs):
                return segs[i + 1]
    return segs[-1] if segs else ""


def main():
    ap = argparse.ArgumentParser(description="Cluster URLs into programmatic-SEO patterns.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", help="crawl_sitemap.py inventory JSON or URL-array JSON")
    g.add_argument("--urls", help="comma-separated URLs")
    ap.add_argument("--samples", type=int, default=8, help="sample URLs to keep per pattern")
    ap.add_argument("--include-editorial", action="store_true",
                    help="keep /blog/, /tag/ etc. (default: excluded as editorial noise)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    urls = load_urls(args)
    buckets = defaultdict(list)
    editorial_count = 0
    unmatched = []

    for u in urls:
        path = urllib.parse.urlparse(u).path or "/"
        if not args.include_editorial and EDITORIAL.search(path):
            editorial_count += 1
            continue
        matched = False
        for name, rx in PATTERNS:
            if rx.search(path):
                buckets[name].append(u)
                matched = True
                break
        if not matched:
            unmatched.append(u)

    pattern_report = []
    roots = {n: rx.pattern for n, rx in PATTERNS}
    for name, group in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        axes = set()
        depths = set()
        for u in group:
            p = urllib.parse.urlparse(u).path
            axes.add(varying_segment(p, roots[name]).lower())
            depths.add(len([s for s in p.split("/") if s]))
        consistency = round(1.0 / len(depths), 3) if depths else 0.0  # 1.0 == all same depth
        pattern_report.append({
            "pattern": name,
            "page_count": len(group),
            "distinct_axis_values": len(axes),
            "url_consistency": consistency,  # 1.0 = uniform depth (more programmatic-looking)
            "sample_axis_values": sorted(v for v in axes if v)[: args.samples],
            "sample_urls": group[: args.samples],
        })

    payload = {
        "total_urls": len(urls),
        "editorial_excluded": editorial_count,
        "unmatched_count": len(unmatched),
        "patterns": pattern_report,
        "unmatched_sample": unmatched[: args.samples],
    }
    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(pattern_report)} patterns from {len(urls)} URLs -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
