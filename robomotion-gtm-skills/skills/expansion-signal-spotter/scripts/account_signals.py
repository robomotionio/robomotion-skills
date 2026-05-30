#!/usr/bin/env python3
"""account_signals.py — keyless per-account expansion-signal sweep over a customer list.

For each account (after min-value / exclusion filtering), runs keyless web searches for
team-growth/hiring, leadership-change, and public-news signals and returns the raw hits for
the AGENT to read and turn into expansion plays + talk tracks. Job-posting and funding
signals are delegated to job-posting-intent / funding-signal-monitor (the agent runs those
and merges). No LLM here. Stdlib only.

Accounts CSV columns (flexible): company, domain, primary_contact_linkedin, tier,
mrr|arr, seats. Filters: --min-account-value (on mrr/arr), --exclude (comma-separated
company names).

Example:
  account_signals.py --accounts accounts.csv --min-account-value 1000 \
      --exclude "ChurnCo,PausedInc" --output signals.json
"""
import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DDG = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/expansion-signal-spotter)"
LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
SNIP_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(s):
    return html.unescape(TAG_RE.sub(" ", s)).strip()


def ddg_unwrap(href):
    if "uddg=" in href:
        p = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if "uddg" in p:
            return urllib.parse.unquote(p["uddg"][0])
    return href


def search(query, limit=5):
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
        out.append({"url": ddg_unwrap(href), "title": strip_tags(title),
                    "snippet": strip_tags(snips[i]) if i < len(snips) else ""})
    return out


def num(v):
    try:
        return float(re.sub(r"[^0-9.]", "", str(v)) or 0)
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description="Keyless per-account expansion-signal sweep.")
    ap.add_argument("--accounts", required=True, help="CSV of customer accounts")
    ap.add_argument("--min-account-value", type=float, default=0, help="filter on mrr/arr")
    ap.add_argument("--exclude", default="", help="comma-separated company names to exclude")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    excludes = {e.strip().lower() for e in args.exclude.split(",") if e.strip()}
    with open(args.accounts, newline="", encoding="utf-8") as f:
        accounts = list(csv.DictReader(f))

    out = []
    for a in accounts:
        company = (a.get("company") or a.get("Company") or "").strip()
        if not company or company.lower() in excludes:
            continue
        value = num(a.get("arr") or a.get("ARR") or a.get("mrr") or a.get("MRR") or 0)
        if args.min_account_value and value < args.min_account_value:
            continue

        sigs = {
            "hiring": search(f'"{company}" hiring OR "we\'re hiring" jobs', 5),
            "leadership": search(f'"{company}" "new VP" OR "appoints" OR "joins as"', 5),
            "news": search(f'"{company}" news', 5),
        }
        time.sleep(1.5)
        out.append({
            "company": company,
            "domain": a.get("domain") or a.get("Domain") or "",
            "tier": a.get("tier") or a.get("Tier") or "",
            "account_value": value,
            "primary_contact_linkedin": a.get("primary_contact_linkedin") or "",
            "web_signals": sigs,
            # agent fills after merging job/funding sub-skill output:
            "signal_stack": [], "expansion_play": "", "talk_track": "", "rank": "",
        })

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(out)} accounts swept (after filters) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
