#!/usr/bin/env python3
"""jobs.py — search job postings across LinkedIn and Indeed (job-scraper).

Two paths, auto-selected by whether APIFY_API_TOKEN is set:
  - Apify actor (structured fields: salary, seniority, description) when the token is present.
  - Keyless degrade: a public web search (DuckDuckGo HTML) over `site:linkedin.com/jobs` /
    `site:indeed.com` returning title + apply URL + snippet (shallower, no salary/seniority).
Normalizes + dedups across sources by title+company+location. Stdlib only.

No logins or cookies. The Apify token is OPTIONAL — the serp degrade always runs.

Example:
  jobs.py --query "RevOps Manager" --location "United States" \
      --sources linkedin,indeed --num-results 25 --output jobs.json
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DDG = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/job-scraper)"
LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
SNIP_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")

# Public Apify actor ids for LinkedIn / Indeed jobs (override via env if your account differs).
ACTORS = {
    "linkedin": os.environ.get("APIFY_LINKEDIN_JOBS_ACTOR", "bebity~linkedin-jobs-scraper"),
    "indeed": os.environ.get("APIFY_INDEED_JOBS_ACTOR", "misceres~indeed-scraper"),
}


def strip_tags(s):
    return html.unescape(TAG_RE.sub("", s)).strip()


def ddg_unwrap(href):
    if "uddg=" in href:
        p = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if "uddg" in p:
            return urllib.parse.unquote(p["uddg"][0])
    return href


def http_post_json(url, body, timeout=120):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def apify_run(actor, run_input):
    token = os.environ["APIFY_API_TOKEN"]
    url = (f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
           f"?token={urllib.parse.quote(token)}")
    for attempt in range(3):
        try:
            return http_post_json(url, run_input)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            print(f"WARN: Apify {actor} {e.code}: {e.read().decode('utf-8','ignore')[:200]}",
                  file=sys.stderr)
            return []
        except urllib.error.URLError as e:
            print(f"WARN: Apify network: {e}", file=sys.stderr)
            return []


def normalize_apify(rec, source):
    return {
        "title": rec.get("title") or rec.get("positionName") or "",
        "company": rec.get("companyName") or rec.get("company") or "",
        "location": rec.get("location") or rec.get("jobLocation") or "",
        "salary": rec.get("salary") or rec.get("salaryInfo") or "",
        "seniority": rec.get("seniorityLevel") or rec.get("seniority") or "",
        "description": (rec.get("description") or rec.get("descriptionText") or "")[:2000],
        "apply_url": rec.get("jobUrl") or rec.get("url") or rec.get("applyUrl") or "",
        "source": source,
    }


def ddg_search(query, limit):
    data = urllib.parse.urlencode({"q": query}).encode()
    req = urllib.request.Request(DDG, data=data, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "ignore")
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return []
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return []
    else:
        return []
    out, links = [], LINK_RE.findall(body)
    snips = SNIP_RE.findall(body)
    for i, (href, title) in enumerate(links[:limit]):
        out.append({"apply_url": ddg_unwrap(href), "title": strip_tags(title),
                    "snippet": strip_tags(snips[i]) if i < len(snips) else ""})
    return out


def serp_jobs(query, location, company, source, limit):
    site = "linkedin.com/jobs" if source == "linkedin" else "indeed.com"
    q = f'site:{site} "{query}"'
    if location:
        q += f' "{location}"'
    if company:
        q += f' "{company}"'
    rows = []
    for hit in ddg_search(q, limit):
        rows.append({
            "title": hit["title"], "company": company, "location": location,
            "salary": "", "seniority": "", "description": hit["snippet"],
            "apply_url": hit["apply_url"], "source": f"{source}/serp",
        })
    return rows


def dedup_key(j):
    return (j["title"].strip().lower(), j["company"].strip().lower(),
            j["location"].strip().lower())


def main():
    ap = argparse.ArgumentParser(description="Search jobs on LinkedIn + Indeed (Apify or keyless serp).")
    ap.add_argument("--query", required=True, help="keyword / role")
    ap.add_argument("--location", default="", help="city/state/Remote")
    ap.add_argument("--company", default="", help="restrict to a company")
    ap.add_argument("--sources", default="linkedin,indeed", help="comma: linkedin,indeed")
    ap.add_argument("--num-results", type=int, default=25)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    has_apify = bool(os.environ.get("APIFY_API_TOKEN", "").strip())
    jobs, seen = [], set()

    for src in sources:
        if src not in ACTORS:
            continue
        rows = []
        if has_apify:
            run_input = {"title": args.query, "location": args.location,
                         "maxItems": args.num_results}
            if args.company:
                run_input["companyName"] = [args.company]
            recs = apify_run(ACTORS[src], run_input)
            rows = [normalize_apify(r, src) for r in recs if isinstance(r, dict)]
        if not rows:  # no token, or actor returned nothing -> keyless degrade
            rows = serp_jobs(args.query, args.location, args.company, src, args.num_results)
            time.sleep(1.0)
        for j in rows:
            k = dedup_key(j)
            if k in seen:
                continue
            seen.add(k)
            jobs.append(j)
            if len(jobs) >= args.num_results:
                break
        if len(jobs) >= args.num_results:
            break

    out = json.dumps(jobs[: args.num_results], ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        mode = "apify" if has_apify else "serp(keyless)"
        print(f"{len(jobs)} jobs [{mode}] -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
