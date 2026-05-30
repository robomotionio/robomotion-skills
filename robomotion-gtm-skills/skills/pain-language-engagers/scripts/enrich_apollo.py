#!/usr/bin/env python3
"""enrich_apollo.py — Apollo TWO-PHASE enrichment for extracted engagers/authors.

Reuses the apollo-lead-finder People Match pattern (X-Api-Key header). For each lead with
a LinkedIn profile_url (and/or name+company), reveal:
  {title, seniority, company, company_domain, company_size, industry, email?}

TWO-PHASE (pain-post authors/engagers often arrive name + headline only, so domain
resolution materially raises the People Match hit rate):
  Phase A — ORG RESOLVE: if a lead has a company name but no domain, resolve the Apollo
            organization (mixed_companies/search) to a primary domain (+ size + industry),
            cached per company name (one lookup per employer).
  Phase B — PEOPLE MATCH: match the person seeded with that domain.

Degrade: with NO APOLLO_API_KEY, pass leads through profile-only (unenriched) so the
pipeline still produces a list — enrichment is additive, never a hard gate.

Email fallback: if Apollo returns no email and DROPCONTACT_API_KEY is set, attempt a
domain+name email via Dropcontact. Off by default; never blocks the pipeline.

Enrich only the SELECTED subset (the agent ranks first); this costs Apollo credits.
Stdlib only.

Example:
  enrich_apollo.py --input engagers.json --limit 100 --output enriched.json
"""
import argparse
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

MATCH_URL = "https://api.apollo.io/api/v1/people/match"
ORG_SEARCH_URL = "https://api.apollo.io/api/v1/mixed_companies/search"
DROPCONTACT_URL = "https://api.dropcontact.io/batch"
MV_URL = "https://api.millionverifier.com/api/v3/"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def verify_email(email):
    """Email deliverability: MillionVerifier if MILLIONVERIFIER_API_KEY set, else keyless
    syntax + MX/A-record check. Returns a result string or '' for empty/unrevealed."""
    if not email or "email_not_unlocked" in email:
        return ""
    mv = os.environ.get("MILLIONVERIFIER_API_KEY", "").strip()
    if mv:
        qs = urllib.parse.urlencode({"api": mv, "email": email})
        try:
            with urllib.request.urlopen(MV_URL + "?" + qs, timeout=30) as r:
                return json.loads(r.read().decode("utf-8")).get("result", "")
        except Exception:
            pass  # fall through to keyless check
    if not EMAIL_RE.match(email):
        return "invalid_syntax"
    try:
        socket.getaddrinfo(email.split("@", 1)[1], None)
        return "ok_syntax_mx"
    except Exception:
        return "no_mx"


def split_name(lead):
    name = (lead.get("name") or "").strip()
    if not name:
        return "", ""
    parts = name.split()
    return parts[0], (" ".join(parts[1:]) if len(parts) > 1 else "")


def post(url, body, key):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "Cache-Control": "no-cache",
                 "X-Api-Key": key, "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return {"_error": f"{e.code}: {e.read().decode('utf-8','ignore')[:200]}"}
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return {"_error": str(e)}


def resolve_org(name, key, cache):
    """Phase A: resolve a company NAME to its Apollo organization (domain, size, industry),
    cached per name. Returns {domain, size, industry} ({} on miss)."""
    if not name:
        return {}
    kn = name.strip().lower()
    if kn in cache:
        return cache[kn]
    data = post(ORG_SEARCH_URL, {"q_organization_name": name, "per_page": 1}, key)
    org = {}
    if "_error" not in data:
        orgs = data.get("organizations") or data.get("accounts") or []
        if orgs:
            o = orgs[0]
            org = {
                "domain": o.get("primary_domain") or o.get("website_url") or "",
                "size": o.get("estimated_num_employees")
                or o.get("organization_num_employees") or "",
                "industry": o.get("industry") or "",
            }
    cache[kn] = org
    return org


def dropcontact_email(first, last, domain):
    """Optional email fallback when Apollo returns none. Needs DROPCONTACT_API_KEY + domain.
    Best-effort; returns '' on any failure."""
    dk = os.environ.get("DROPCONTACT_API_KEY", "").strip()
    if not dk or not domain or not (first or last):
        return ""
    body = {"data": [{"first_name": first, "last_name": last, "website": domain}],
            "siren": False}
    req = urllib.request.Request(
        DROPCONTACT_URL, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "X-Access-Token": dk})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            out = json.loads(r.read().decode("utf-8"))
        rows = out.get("data") or []
        emails = (rows[0].get("email") if rows else None) or []
        if emails and isinstance(emails, list):
            return emails[0].get("email", "") or ""
    except Exception:
        return ""
    return ""


def enrich_one(lead, key, org_cache):
    fn, ln = split_name(lead)

    # ---- Phase A: org resolve (company name present, domain missing) -------------------
    domain = lead.get("company_domain") or ""
    size = lead.get("company_size") or ""
    industry = lead.get("industry") or ""
    if lead.get("company") and not domain:
        org_r = resolve_org(lead["company"], key, org_cache)
        domain = domain or org_r.get("domain", "")
        size = size or org_r.get("size", "")
        industry = industry or org_r.get("industry", "")

    # ---- Phase B: people match (seeded with resolved domain) ---------------------------
    body = {"reveal_personal_emails": True}
    if fn:
        body["first_name"] = fn
    if ln:
        body["last_name"] = ln
    if lead.get("profile_url"):
        body["linkedin_url"] = lead["profile_url"]
    if lead.get("company"):
        body["organization_name"] = lead["company"]
    if domain:
        body["domain"] = domain

    data = post(MATCH_URL, body, key)
    if "_error" in data:
        return dict(lead, enrich_error=data["_error"],
                    company_domain=lead.get("company_domain", "") or domain,
                    company_size=lead.get("company_size", "") or size,
                    industry=lead.get("industry", "") or industry)
    p = data.get("person") or {}
    org = p.get("organization") or {}
    email = p.get("email") or ""
    if email and "email_not_unlocked" in email:
        email = ""
    final_domain = org.get("primary_domain", "") or org.get("website_url", "") or domain
    if not email:
        email = dropcontact_email(fn, ln, final_domain)
    return dict(lead,
                title=p.get("title", "") or lead.get("title", ""),
                seniority=p.get("seniority", ""),
                company=org.get("name", "") or lead.get("company", ""),
                company_domain=final_domain,
                company_size=org.get("estimated_num_employees", "") or size,
                industry=org.get("industry", "") or industry,
                email=email,
                email_status=p.get("email_status", ""))


def profile_only(lead):
    """Degrade row: keep what extraction gave us, add empty enrichment fields."""
    return dict(lead, title=lead.get("title", lead.get("headline", "")),
                seniority="", company=lead.get("company", ""), company_domain="",
                company_size="", industry="", email="", email_status="",
                enrich_error="no APOLLO_API_KEY (profile-only degrade)")


def main():
    ap = argparse.ArgumentParser(description="Apollo People Match enrichment (degrades profile-only).")
    ap.add_argument("--input", required=True, help="engagers.json from extract_engagers.py")
    ap.add_argument("--limit", type=int, default=0, help="enrich at most N (0 = all)")
    ap.add_argument("--verify", action="store_true",
                    help="verify produced emails (MillionVerifier if keyed, else keyless syntax+MX)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        leads = json.load(f)
    if isinstance(leads, dict):
        sys.exit("ERROR: --input looks like a degrade plan, not extracted leads.")
    if args.limit > 0:
        leads = leads[: args.limit]

    key = os.environ.get("APOLLO_API_KEY", "").strip()
    out = []
    if not key:
        out = [profile_only(l) for l in leads]
        print(f"no APOLLO_API_KEY -> {len(out)} leads passed through profile-only.",
              file=sys.stderr)
    else:
        org_cache = {}
        for lead in leads:
            out.append(enrich_one(lead, key, org_cache))
            time.sleep(0.3)
        with_email = sum(1 for e in out if e.get("email"))
        print(f"enriched {len(out)} leads, {with_email} with email.", file=sys.stderr)

    if args.verify:
        for e in out:
            if e.get("email"):
                e["email_verification"] = verify_email(e["email"])

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")


if __name__ == "__main__":
    main()
