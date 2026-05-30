#!/usr/bin/env python3
"""linkedin_jobs.py — find LinkedIn job postings by search term + location.

LinkedIn-only raw job sourcing. Auto-selects:
  - Apify LinkedIn jobs actor (structured: salary, job type, full description) when
    APIFY_API_TOKEN is set.
  - Keyless degrade: a public web search over `site:linkedin.com/jobs` returning title +
    URL + snippet (shallower).
Dedups repeated postings of the same role. No cookies. Stdlib only.

Example:
  linkedin_jobs.py --search "Sales Engineer" --location "Remote" --results 25 \
      --output jobs.json
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
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/linkedin-job-scraper)"
LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
SNIP_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")
ACTOR = os.environ.get("APIFY_LINKEDIN_JOBS_ACTOR", "bebity~linkedin-jobs-scraper")


def strip_tags(s):
    return html.unescape(TAG_RE.sub("", s)).strip()


def ddg_unwrap(href):
    if "uddg=" in href:
        p = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if "uddg" in p:
            return urllib.parse.unquote(p["uddg"][0])
    return href


def apify_run(run_input):
    token = os.environ["APIFY_API_TOKEN"]
    url = (f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={urllib.parse.quote(token)}")
    data = json.dumps(run_input).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            print(f"WARN: Apify {e.code}: {e.read().decode('utf-8','ignore')[:200]}", file=sys.stderr)
            return []
        except urllib.error.URLError as e:
            print(f"WARN: Apify network: {e}", file=sys.stderr)
            return []


def normalize_apify(rec):
    return {
        "title": rec.get("title") or rec.get("positionName") or "",
        "company": rec.get("companyName") or rec.get("company") or "",
        "location": rec.get("location") or "",
        "salary": rec.get("salary") or "",
        "job_type": rec.get("contractType") or rec.get("employmentType") or rec.get("jobType") or "",
        "description": (rec.get("description") or rec.get("descriptionText") or "")[:2000],
        "url": rec.get("jobUrl") or rec.get("url") or "",
        "source": "linkedin",
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
        url = ddg_unwrap(href)
        if "linkedin.com/jobs" not in url:
            continue
        out.append({"title": strip_tags(title), "url": url.split("?")[0],
                    "snippet": strip_tags(snips[i]) if i < len(snips) else ""})
    return out


def main():
    ap = argparse.ArgumentParser(description="Find LinkedIn job postings (Apify or keyless serp).")
    ap.add_argument("--search", required=True, help="job title/role/keyword")
    ap.add_argument("--location", default="", help="city/state/Remote")
    ap.add_argument("--results", type=int, default=25)
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    has_apify = bool(os.environ.get("APIFY_API_TOKEN", "").strip())
    jobs, seen = [], set()

    if has_apify:
        run_input = {"title": args.search, "location": args.location, "maxItems": args.results}
        recs = apify_run(run_input)
        rows = [normalize_apify(r) for r in recs if isinstance(r, dict)]
    else:
        rows = []
    if not rows:
        q = f'site:linkedin.com/jobs "{args.search}"'
        if args.location:
            q += f' "{args.location}"'
        rows = [{"title": h["title"], "company": "", "location": args.location, "salary": "",
                 "job_type": "", "description": h["snippet"], "url": h["url"],
                 "source": "linkedin/serp"} for h in ddg_search(q, args.results)]

    for j in rows:
        k = (j["title"].strip().lower(), j["company"].strip().lower(), j["url"])
        if k in seen:
            continue
        seen.add(k)
        jobs.append(j)
        if len(jobs) >= args.results:
            break

    out = json.dumps(jobs[: args.results], ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(jobs)} LinkedIn jobs [{'apify' if has_apify else 'serp'}] -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
