#!/usr/bin/env python3
"""detect_moves.py — detect job changes among tracked champions/buyers.

For each tracked person, resolve their CURRENT company/title and compare to their
last-known company. If the current company differs, they moved — flag with new
company/title and a promotion heuristic.

Primary path: Apollo people-match (by name + LinkedIn URL) when APOLLO_API_KEY is set
(returns current employer + title). Degrade: keyless serp search ('{name}' "new role" OR
joined) returning evidence for the AGENT to read (lower precision). No LLM in the script.

Stdlib only.

Input people JSON: list of
  {full_name, linkedin_url, email, last_known_company, last_known_title,
   category, relationship_context}

Examples:
  detect_moves.py --people people.json --output movers.json
  detect_moves.py --people people.json --method web_search --output movers.json
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

APOLLO_MATCH = "https://api.apollo.io/api/v1/people/match"
DDG_HTML = "https://html.duckduckgo.com/html/"
UA = "Mozilla/5.0 (compatible; robomotion-gtm-skills/champion-move-outreach)"


def http(req, timeout=30):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("exhausted retries")


def apollo_match(person, key):
    body = {"reveal_personal_emails": False}
    if person.get("linkedin_url"):
        body["linkedin_url"] = person["linkedin_url"]
    if person.get("full_name"):
        body["name"] = person["full_name"]
    req = urllib.request.Request(APOLLO_MATCH, data=json.dumps(body).encode("utf-8"),
                                 method="POST",
                                 headers={"Content-Type": "application/json", "X-Api-Key": key,
                                          "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read().decode("utf-8", "ignore"))
            pp = d.get("person") or {}
            org = pp.get("organization") or {}
            return {"current_company": org.get("name", ""),
                    "current_domain": org.get("primary_domain", ""),
                    "current_title": pp.get("title", ""),
                    "current_email": pp.get("email", "") or "",
                    "email_status": pp.get("email_status", "")}
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            print(f"WARN: Apollo match {e.code} for {person.get('full_name')}", file=sys.stderr)
            return None
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return None
    return None


def serp_evidence(person):
    name = person.get("full_name", "")
    q = f'"{name}" "new role" OR joined OR "excited to announce"'
    data = urllib.parse.urlencode({"q": q}).encode()
    req = urllib.request.Request(DDG_HTML, data=data, headers={"User-Agent": UA})
    try:
        page = http(req)
    except Exception as e:
        print(f"WARN: serp failed for {name}: {e}", file=sys.stderr)
        return []
    out = []
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S):
        href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        if "uddg=" in href:
            href = urllib.parse.unquote(re.sub(r"^.*uddg=", "", href).split("&")[0])
        out.append({"title": html.unescape(title.strip()), "url": href})
        if len(out) >= 4:
            break
    return out


SENIOR = ["chief", "c-suite", "cto", "ceo", "cfo", "cmo", "coo", "vp", "vice president",
          "head of", "director", "svp", "evp"]


def promotion_flag(old_title, new_title):
    o, n = (old_title or "").lower(), (new_title or "").lower()
    o_rank = max([i for i, k in enumerate(SENIOR) if k in o] or [-1])
    n_rank = max([i for i, k in enumerate(SENIOR) if k in n] or [-1])
    # lower index = more senior in this list; promotion if new is more senior
    if n_rank == -1 or o_rank == -1:
        return None
    return n_rank < o_rank


def main():
    ap = argparse.ArgumentParser(description="Detect job changes among tracked champions (Apollo match or serp degrade).")
    ap.add_argument("--people", required=True, help="JSON list of tracked people")
    ap.add_argument("--method", default="auto", choices=["auto", "apollo", "web_search"],
                    help="auto = Apollo if key set else web_search")
    ap.add_argument("--output", default="-", help="output JSON path; default stdout")
    args = ap.parse_args()

    people = json.load(open(args.people, encoding="utf-8"))
    if not isinstance(people, list):
        people = [people]
    key = os.environ.get("APOLLO_API_KEY", "").strip()
    method = args.method
    if method == "auto":
        method = "apollo" if key else "web_search"
    if method == "apollo" and not key:
        print("WARN: APOLLO_API_KEY unset — falling back to web_search evidence.", file=sys.stderr)
        method = "web_search"

    movers = []
    for p in people:
        last_co = (p.get("last_known_company") or "").strip().lower()
        rec = dict(p)
        if method == "apollo":
            cur = apollo_match(p, key)
            time.sleep(0.2)
            if not cur:
                rec["moved"] = None
                rec["detection"] = "apollo_no_match"
                movers.append(rec)
                continue
            rec.update(cur)
            cur_co = (cur["current_company"] or "").strip().lower()
            rec["moved"] = bool(cur_co and last_co and cur_co != last_co)
            rec["promotion"] = promotion_flag(p.get("last_known_title"), cur["current_title"])
            rec["detection"] = "apollo"
        else:
            rec["evidence"] = serp_evidence(p)
            rec["moved"] = None  # agent reads evidence to decide
            rec["detection"] = "web_search"
            time.sleep(0.4)
        movers.append(rec)

    # Surface likely movers first.
    movers.sort(key=lambda r: (r.get("moved") is True), reverse=True)
    payload = json.dumps(movers, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        n_moved = sum(1 for m in movers if m.get("moved") is True)
        print(f"{n_moved} confirmed movers (of {len(movers)} tracked) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
