#!/usr/bin/env python3
"""pb_profiles.py — scrape LinkedIn profiles via Phantombuster (champion-tracker engine).

Launches a Phantombuster "LinkedIn Profile Scraper" agent over a list of profile URLs and
returns each profile's current company + title (the fields champion-tracker baselines and
diffs). Deterministic I/O only — the agent does the ICP scoring and the baseline diff.

Auth: PHANTOMBUSTER_API_KEY (X-Phantombuster-Key header). The agent must hold a valid
LinkedIn session cookie (li_at) and be configured for the LinkedIn Profile Scraper phantom;
pass its agent id with --agent-id (or PB_PROFILE_AGENT_ID env). Stdlib only.

Modes:
  init  — write a baseline snapshot file (company,title per linkedin_url)
  track — re-scrape, diff vs --baseline, emit only movers (company OR title changed)

Example:
  pb_profiles.py --agent-id 1234567890 --urls champions.csv --mode init \
      --output baseline.json
  pb_profiles.py --agent-id 1234567890 --urls champions.csv --mode track \
      --baseline baseline.json --output movers.json
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

LAUNCH = "https://api.phantombuster.com/api/v2/agents/launch"
FETCH_OUTPUT = "https://api.phantombuster.com/api/v2/agents/fetch-output"
FETCH = "https://api.phantombuster.com/api/v1/agent/{aid}/output"


def api_key():
    k = os.environ.get("PHANTOMBUSTER_API_KEY", "").strip()
    if not k:
        sys.exit("ERROR: PHANTOMBUSTER_API_KEY not set (required — the LinkedIn scrape engine). "
                 "No key -> use the pb_profiles_pw.mjs Playwright degrade.")
    return k


def agent_id(arg):
    aid = (arg or os.environ.get("PB_PROFILE_AGENT_ID", "")).strip()
    if not aid:
        sys.exit("ERROR: --agent-id (or PB_PROFILE_AGENT_ID) required: the configured "
                 "Phantombuster LinkedIn Profile Scraper agent.")
    return aid


def req(url, key, data=None):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(
        url, data=body, method="POST" if data is not None else "GET",
        headers={"X-Phantombuster-Key-1": key, "Content-Type": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Phantombuster {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: network: {e}")


def norm(u):
    if not u:
        return ""
    return u.split("?")[0].rstrip("/").lower().replace("http://", "https://")


def load_urls(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for col in ("linkedin_url", "linkedin", "LinkedIn URL", "linkedinUrl", "url"):
                if row.get(col):
                    rows.append({"linkedin_url": row[col].strip(),
                                 "name": row.get("name", "") or row.get("Name", "")})
                    break
    return rows


def launch_and_wait(key, aid, urls):
    """Launch the agent with the profile list and poll for its JSON output rows."""
    arg = {"profileUrls": urls, "numberOfProfiles": len(urls)}
    res = req(LAUNCH, key, {"id": aid, "argument": arg})
    container = res.get("data", {}).get("containerId") or res.get("containerId")
    # poll fetch-output until the container reports finished
    for _ in range(60):
        time.sleep(5)
        out = req(f"{FETCH_OUTPUT}?id={aid}", key)
        d = out.get("data", {})
        if d.get("containerId") and d.get("containerId") != container:
            continue
        status = (d.get("status") or "").lower()
        if status in ("finished", "stopped") or d.get("output"):
            break
    # the scraped rows land in the agent's result object / S3; the v1 output endpoint
    # returns the agent's stdout which the phantom writes the result JSON path into.
    # Phantoms differ; the caller may also fetch the result CSV/JSON via the returned URL.
    return res, out


def parse_rows(launch_res):
    """Extract {linkedin_url, company, title, name} rows from a phantom result payload.

    Phantombuster result schemas vary by phantom build; we read the common keys and skip
    anything we can't map. The agent can re-map fields if a phantom uses different names.
    """
    rows = []
    payload = launch_res
    # accept either a list of result objects or a wrapper
    if isinstance(payload, dict):
        payload = payload.get("resultObject") or payload.get("data") or payload
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            payload = []
    if not isinstance(payload, list):
        payload = []
    for p in payload:
        if not isinstance(p, dict):
            continue
        url = p.get("linkedinUrl") or p.get("profileUrl") or p.get("query") or ""
        rows.append({
            "linkedin_url": url,
            "name": p.get("fullName") or p.get("name") or "",
            "company": p.get("company") or p.get("companyName") or p.get("currentCompany") or "",
            "title": p.get("jobTitle") or p.get("title") or p.get("headline") or "",
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="Phantombuster LinkedIn profile scrape for champion job-change tracking.")
    ap.add_argument("--agent-id", default="", help="Phantombuster profile-scraper agent id")
    ap.add_argument("--urls", required=True, help="CSV of champions (linkedin_url[,name])")
    ap.add_argument("--mode", choices=["init", "track"], required=True)
    ap.add_argument("--baseline", default="", help="baseline JSON (required for --mode track)")
    ap.add_argument("--results-json", default="",
                    help="optional: path to a phantom result JSON already downloaded "
                         "(skips the live launch; useful when the phantom writes to S3)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    champs = load_urls(args.urls)
    if not champs:
        sys.exit("ERROR: no LinkedIn URLs found in --urls CSV.")
    urls = [c["linkedin_url"] for c in champs]
    name_by = {norm(c["linkedin_url"]): c["name"] for c in champs}

    if args.results_json:
        with open(args.results_json, encoding="utf-8") as f:
            scraped = parse_rows(json.load(f))
    else:
        key = api_key()
        aid = agent_id(args.agent_id)
        launch_res, _ = launch_and_wait(key, aid, urls)
        scraped = parse_rows(launch_res.get("data") if isinstance(launch_res, dict) else launch_res)

    snap = {}
    for r in scraped:
        k = norm(r["linkedin_url"])
        if not k:
            continue
        snap[k] = {
            "linkedin_url": r["linkedin_url"],
            "name": r["name"] or name_by.get(k, ""),
            "company": r["company"],
            "title": r["title"],
        }

    if args.mode == "init":
        out_obj = list(snap.values())
        msg = f"baseline of {len(out_obj)} profiles"
    else:
        if not args.baseline:
            sys.exit("ERROR: --baseline is required for --mode track.")
        with open(args.baseline, encoding="utf-8") as f:
            base = {norm(b["linkedin_url"]): b for b in json.load(f)}
        movers = []
        for k, cur in snap.items():
            old = base.get(k)
            if not old:
                continue
            if (cur["company"].strip().lower() != old.get("company", "").strip().lower()
                    or cur["title"].strip().lower() != old.get("title", "").strip().lower()):
                movers.append({
                    "name": cur["name"], "linkedin_url": cur["linkedin_url"],
                    "old_company": old.get("company", ""), "new_company": cur["company"],
                    "old_title": old.get("title", ""), "new_title": cur["title"],
                    "needs_review": not cur["company"].strip(),  # no usable new-company data
                })
        out_obj = {"movers": movers, "new_baseline": list(snap.values())}
        msg = f"{len(movers)} movers / {len(snap)} re-scraped"

    payload = json.dumps(out_obj, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{msg} -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
