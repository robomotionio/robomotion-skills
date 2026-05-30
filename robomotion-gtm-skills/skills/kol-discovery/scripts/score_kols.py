#!/usr/bin/env python3
"""score_kols.py — aggregate LinkedIn post data by author and compute a KOL score.

Deterministic aggregation + scoring math (no LLM). Takes a JSON list of posts (the
output shape of linkedin-post-research's post_search.py), groups by author, and emits
a ranked KOL list. The AGENT generates the keywords, runs the post searches, does the
web research, and merges web-researched KOLs — this script only does the math.

Score = engagement (log-scaled total reactions+comments)
      + consistency (post count)
      + quality (avg engagement per post)
      + relevance (distinct keyword breadth)
      + web bonus (if the author also appears in --web-kols).



Examples:
  score_kols.py --posts posts.json --min-posts 2 --min-total-engagement 50 --top-n 50
  score_kols.py --posts posts.json --web-kols web_kols.json --output csv
"""
import argparse
import csv
import json
import math
import sys


def norm_url(u):
    return (u or "").split("?")[0].rstrip("/").lower()


def load_web_kols(path):
    """web_kols.json: list of {name, linkedin_url, source, notes}."""
    if not path:
        return {}, {}
    data = json.load(open(path, encoding="utf-8"))
    by_url, by_name = {}, {}
    for k in data:
        u = norm_url(k.get("linkedin_url"))
        if u:
            by_url[u] = k
        if k.get("name"):
            by_name[k["name"].strip().lower()] = k
    return by_url, by_name


def aggregate(posts):
    authors = {}
    for p in posts:
        key = norm_url(p.get("author_profile_url")) or (p.get("author") or "").strip().lower()
        if not key:
            continue
        a = authors.setdefault(key, {
            "name": p.get("author", ""), "linkedin_url": p.get("author_profile_url", ""),
            "headline": p.get("author_headline", ""), "total_posts": 0,
            "total_reactions": 0, "total_comments": 0, "keywords": set(),
            "top_post_url": "", "top_post_preview": "", "_top_eng": -1,
        })
        if not a["name"] and p.get("author"):
            a["name"] = p["author"]
        if not a["linkedin_url"] and p.get("author_profile_url"):
            a["linkedin_url"] = p["author_profile_url"]
        r = p.get("reactions", 0) or 0
        c = p.get("comments", 0) or 0
        a["total_posts"] += 1
        a["total_reactions"] += r
        a["total_comments"] += c
        if p.get("keyword"):
            a["keywords"].add(p["keyword"])
        eng = r + c
        if eng > a["_top_eng"]:
            a["_top_eng"] = eng
            a["top_post_url"] = p.get("url", "")
            a["top_post_preview"] = (p.get("post_preview") or p.get("full_text", ""))[:200]
    return authors


def score(a, web_by_url, web_by_name):
    total_eng = a["total_reactions"] + a["total_comments"]
    avg_eng = total_eng / a["total_posts"] if a["total_posts"] else 0
    engagement = math.log1p(total_eng) * 10          # log-scaled volume
    consistency = min(a["total_posts"], 20) * 2       # capped post count
    quality = math.log1p(avg_eng) * 5                 # avg engagement
    relevance = len(a["keywords"]) * 3                # keyword breadth
    url = norm_url(a["linkedin_url"])
    name = (a["name"] or "").strip().lower()
    in_web = url in web_by_url or name in web_by_name
    web_bonus = 15 if in_web else 0
    kol_score = round(engagement + consistency + quality + relevance + web_bonus, 2)
    source = "both" if in_web else "post-data"
    return kol_score, round(avg_eng, 1), source


def main():
    ap = argparse.ArgumentParser(description="Aggregate posts by author and score KOLs (deterministic math).")
    ap.add_argument("--posts", required=True, help="JSON list of posts (post_search.py output shape)")
    ap.add_argument("--web-kols", default="", help="JSON list of web-researched KOLs to merge/flag")
    ap.add_argument("--min-posts", type=int, default=1, help="drop authors below this post count")
    ap.add_argument("--min-total-engagement", type=int, default=0, help="drop authors below total reactions+comments")
    ap.add_argument("--top-n", type=int, default=50, help="cap on returned KOLs")
    ap.add_argument("--output", default="json", choices=["json", "csv", "summary"])
    args = ap.parse_args()

    posts = json.load(open(args.posts, encoding="utf-8"))
    web_by_url, web_by_name = load_web_kols(args.web_kols)
    authors = aggregate(posts)

    rows = []
    for a in authors.values():
        total_eng = a["total_reactions"] + a["total_comments"]
        if a["total_posts"] < args.min_posts:
            continue
        if total_eng < args.min_total_engagement:
            continue
        kol_score, avg_eng, source = score(a, web_by_url, web_by_name)
        rows.append({
            "name": a["name"], "linkedin_url": a["linkedin_url"], "headline": a["headline"],
            "kol_score": kol_score, "total_posts": a["total_posts"],
            "total_reactions": a["total_reactions"], "total_comments": a["total_comments"],
            "avg_engagement": avg_eng, "top_post_url": a["top_post_url"],
            "top_post_preview": a["top_post_preview"], "source": source,
        })

    # Web-only KOLs (in web list but no post data) are appended with source=web-research.
    seen_urls = {norm_url(r["linkedin_url"]) for r in rows}
    seen_names = {(r["name"] or "").strip().lower() for r in rows}
    for k in (json.load(open(args.web_kols, encoding="utf-8")) if args.web_kols else []):
        u = norm_url(k.get("linkedin_url"))
        nm = (k.get("name") or "").strip().lower()
        if u in seen_urls or (nm and nm in seen_names):
            continue
        rows.append({
            "name": k.get("name", ""), "linkedin_url": k.get("linkedin_url", ""),
            "headline": k.get("notes", ""), "kol_score": 10.0, "total_posts": 0,
            "total_reactions": 0, "total_comments": 0, "avg_engagement": 0,
            "top_post_url": "", "top_post_preview": "", "source": "web-research",
        })

    rows.sort(key=lambda r: r["kol_score"], reverse=True)
    rows = rows[: args.top_n]
    for i, r in enumerate(rows, 1):
        r["rank"] = i

    if args.output == "summary":
        for r in rows:
            print(f"#{r['rank']:>2} [{r['kol_score']:>6}] {r['name']} "
                  f"({r['total_posts']}p, {r['total_reactions']}r, {r['source']})")
            print(f"     {r['linkedin_url']}")
    elif args.output == "csv":
        cols = ["rank", "name", "linkedin_url", "headline", "kol_score", "total_posts",
                "total_reactions", "total_comments", "avg_engagement", "top_post_url",
                "top_post_preview", "source"]
        w = csv.writer(sys.stdout)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    else:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
