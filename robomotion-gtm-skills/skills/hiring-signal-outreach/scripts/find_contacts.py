#!/usr/bin/env python3
"""find_contacts.py — find decision-maker contacts at qualified companies.

Apollo people-search by company domain + persona titles when APOLLO_API_KEY is set
(free search; enrichment costs credits only with --enrich). Without a key it degrades to
an email-pattern GUESS from the domain (first.last@domain etc.) flagged unverified, so the
pipeline still produces a contact list (lower confidence). Optional MillionVerifier check.

Deterministic — the agent picks personas/titles and selects winners. Stdlib only.


Examples:
  find_contacts.py --domains domains.json --titles "VP Sales,Head of RevOps" --per-company 3
  find_contacts.py --domains acme.com,foo.io --titles "CTO" --enrich --verify
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

APOLLO_SEARCH = "https://api.apollo.io/api/v1/mixed_people/search"
APOLLO_ENRICH = "https://api.apollo.io/api/v1/people/match"
MV_URL = "https://api.millionverifier.com/api/v3/"


def post(url, body, key, timeout=45):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", "X-Api-Key": key,
                                          "Accept": "application/json", "Cache-Control": "no-cache"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"ERROR: Apollo {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit("ERROR: Apollo network error")


def split(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def load_domains(arg):
    if arg.endswith(".json") or arg == "-":
        raw = sys.stdin.read() if arg == "-" else open(arg, encoding="utf-8").read()
        data = json.loads(raw)
        data = data if isinstance(data, list) else [data]
        out = []
        for d in data:
            if isinstance(d, dict):
                out.append({"company": d.get("company") or d.get("name", ""),
                            "domain": d.get("domain", "")})
            else:
                out.append({"company": "", "domain": str(d)})
        return out
    return [{"company": "", "domain": x} for x in split(arg)]


def apollo_search(domain, titles, per_company, key):
    body = {"q_organization_domains": domain, "person_titles": titles,
            "page": 1, "per_page": max(per_company * 2, 10)}
    data = post(APOLLO_SEARCH, body, key)
    out = []
    for p in data.get("people", [])[: per_company]:
        org = p.get("organization") or {}
        out.append({
            "id": p.get("id"), "name": p.get("name", ""),
            "first_name": p.get("first_name", ""), "last_name": p.get("last_name", ""),
            "title": p.get("title", ""), "company": org.get("name", ""),
            "domain": org.get("primary_domain", "") or domain,
            "linkedin_url": p.get("linkedin_url", ""),
            "email": "", "email_status": p.get("email_status", ""), "source": "apollo",
        })
    return out


def apollo_enrich(person, key):
    body = {"id": person["id"], "reveal_personal_emails": False}
    data = post(APOLLO_ENRICH, body, key)
    pp = data.get("person") or {}
    person["email"] = pp.get("email", "") or ""
    person["email_status"] = pp.get("email_status", person.get("email_status", ""))
    return person


def pattern_guess(domain, titles, per_company):
    """Keyless degrade: cannot find real people; emit role-based pattern placeholders."""
    guesses = []
    for t in titles[: per_company]:
        guesses.append({
            "id": None, "name": "", "first_name": "", "last_name": "",
            "title": t, "company": "", "domain": domain,
            "linkedin_url": "", "email": f"<first>.<last>@{domain}",
            "email_status": "pattern_guess_unverified", "source": "pattern-guess",
        })
    return guesses


def mv_verify(email, key):
    import urllib.parse
    if not email or "<" in email:
        return "unknown"
    qs = urllib.parse.urlencode({"api": key, "email": email})
    req = urllib.request.Request(MV_URL + "?" + qs)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8", "ignore"))
        return (d.get("result") or "unknown").lower()
    except Exception:
        return "unknown"


def main():
    ap = argparse.ArgumentParser(description="Find decision-maker contacts (Apollo or pattern-guess degrade).")
    ap.add_argument("--domains", required=True, help="JSON/CSV list or comma-separated domains")
    ap.add_argument("--titles", required=True, help="comma-separated persona/buyer titles")
    ap.add_argument("--per-company", type=int, default=3, help="contacts per company (default 3)")
    ap.add_argument("--enrich", action="store_true", help="reveal verified emails (Apollo credits)")
    ap.add_argument("--verify", action="store_true", help="MillionVerifier check on revealed emails")
    ap.add_argument("--output", default="-", help="output JSON path; default stdout")
    args = ap.parse_args()

    companies = load_domains(args.domains)
    titles = split(args.titles)
    key = os.environ.get("APOLLO_API_KEY", "").strip()
    mv_key = os.environ.get("MILLIONVERIFIER_API_KEY", "").strip()

    if not key:
        print("WARN: APOLLO_API_KEY unset — degrading to email-pattern guesses (unverified, "
              "low confidence). Route no-email contacts to LinkedIn.", file=sys.stderr)

    contacts = []
    for co in companies:
        dom = co.get("domain", "").strip()
        if not dom:
            continue
        if key:
            people = apollo_search(dom, titles, args.per_company, key)
            if args.enrich:
                for p in people:
                    if p.get("id"):
                        apollo_enrich(p, key)
                        time.sleep(0.2)
            if not people:
                people = pattern_guess(dom, titles, args.per_company)
        else:
            people = pattern_guess(dom, titles, args.per_company)
        for p in people:
            if not p.get("company") and co.get("company"):
                p["company"] = co["company"]
            if args.verify and mv_key and p.get("email") and "<" not in p["email"]:
                p["email_verification"] = mv_verify(p["email"], mv_key)
        contacts.extend(people)

    payload = json.dumps(contacts, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        print(f"{len(contacts)} contacts -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
