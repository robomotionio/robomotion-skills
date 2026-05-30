#!/usr/bin/env python3
"""enrich_apollo.py — Stage 3: enrich engagers via Apollo (TWO-PHASE People Match).

Takes the engager rows from extract_engagers.py and reveals firmographics + (optionally)
email via Apollo's People Match API (X-Api-Key header, same pattern as apollo-lead-finder).
Adds: {title, seniority, company, company_domain, company_size, industry, email?}.

TWO-PHASE (KOL audiences are broad and often arrive name + headline only, so domain
resolution materially raises the People Match hit rate):
  Phase A — ORG RESOLVE: if a row has a company name but no domain, resolve the Apollo
            organization (mixed_companies/search) to a primary domain (+ size + industry),
            cached per company name (one lookup per employer, not per engager).
  Phase B — PEOPLE MATCH: match the person seeded with that domain for
            title/seniority/company/size/industry/email.

DEGRADE: with no APOLLO_API_KEY the script runs profile-only — it passes rows through and
maps the LinkedIn headline into `title` so score_icp.py still has something to work with.
Enrichment costs credits, so enrich ONLY the rows you intend to score/keep (the agent slices
first). Stdlib only.

Email fallback: if Apollo returns no email and DROPCONTACT_API_KEY is set, attempt a
domain+name email via Dropcontact. Off by default; never blocks the pipeline.

Auth: APOLLO_API_KEY (optional — profile-only degrade without it).

Examples:
  enrich_apollo.py --input engagers.json --output enriched.json
  enrich_apollo.py --input engagers.json --limit 100 --reveal-email --output enriched.json
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

# Coarse company-size buckets from Apollo's estimated_num_employees.
def size_bucket(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return ""
    if n <= 10:
        return "1-10"
    if n <= 50:
        return "11-50"
    if n <= 200:
        return "51-200"
    if n <= 500:
        return "201-500"
    if n <= 1000:
        return "501-1000"
    if n <= 5000:
        return "1001-5000"
    return "5000+"


def split_name(full):
    parts = (full or "").split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])


def post(url, body, key):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "Cache-Control": "no-cache",
                 "X-Api-Key": key, "Accept": "application/json"},
    )
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


def profile_only(row):
    """No Apollo key: keep the row, seed `title` from headline so scoring still works."""
    return dict(row,
                title=row.get("title") or row.get("headline") or "",
                seniority=row.get("seniority", ""),
                company=row.get("company", ""),
                company_domain=row.get("company_domain", ""),
                company_size=row.get("company_size", ""),
                industry=row.get("industry", ""),
                enriched=False)


def resolve_org(name, key, cache):
    """Phase A: resolve a company NAME to its Apollo organization (primary domain, size,
    industry), cached per name. Returns {domain, size_raw, industry} ({} on miss)."""
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
                "size_raw": o.get("estimated_num_employees")
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


def enrich_one(row, key, reveal_email, org_cache):
    first, last = split_name(row.get("name", ""))

    # ---- Phase A: org resolve (company name present, domain missing) -------------------
    domain = row.get("company_domain") or ""
    size_raw = row.get("company_size") or ""
    industry = row.get("industry") or ""
    if row.get("company") and not domain:
        org_r = resolve_org(row["company"], key, org_cache)
        domain = domain or org_r.get("domain", "")
        size_raw = size_raw or org_r.get("size_raw", "")
        industry = industry or org_r.get("industry", "")

    # ---- Phase B: people match (seeded with resolved domain) ---------------------------
    body = {"reveal_personal_emails": bool(reveal_email)}
    if first:
        body["first_name"] = first
    if last:
        body["last_name"] = last
    lk = row.get("profile_url") or row.get("linkedin_url")
    if lk:
        body["linkedin_url"] = lk
    if row.get("company"):
        body["organization_name"] = row["company"]
    if domain:
        body["domain"] = domain

    data = post(MATCH_URL, body, key)
    if "_error" in data:
        fallback = dict(profile_only(row), enrich_error=data["_error"])
        fallback["company_domain"] = fallback.get("company_domain") or domain
        fallback["company_size"] = fallback.get("company_size") or size_bucket(size_raw)
        fallback["industry"] = fallback.get("industry") or industry
        return fallback
    p = data.get("person") or {}
    if not p:
        fallback = dict(profile_only(row), enrich_error="no_match")
        fallback["company_domain"] = fallback.get("company_domain") or domain
        fallback["company_size"] = fallback.get("company_size") or size_bucket(size_raw)
        fallback["industry"] = fallback.get("industry") or industry
        return fallback
    org = p.get("organization") or {}
    email = p.get("email") or ""
    if email and "email_not_unlocked" in email:
        email = ""
    final_domain = org.get("primary_domain") or org.get("website_url") or domain or ""
    final_size = org.get("estimated_num_employees")
    out = dict(row,
               title=p.get("title") or row.get("headline") or "",
               seniority=p.get("seniority") or "",
               company=org.get("name") or row.get("company", ""),
               company_domain=final_domain,
               company_size=size_bucket(final_size) or size_bucket(size_raw),
               industry=org.get("industry") or industry,
               enriched=True)
    if reveal_email:
        if not email:
            email = dropcontact_email(first, last, final_domain)
        out["email"] = email
        out["email_status"] = p.get("email_status", "")
    return out


def main():
    ap = argparse.ArgumentParser(description="Apollo People Match enrichment (profile-only degrade).")
    ap.add_argument("--input", required=True, help="engagers.json from extract_engagers.py")
    ap.add_argument("--limit", type=int, default=0, help="enrich at most N (0 = all)")
    ap.add_argument("--reveal-email", action="store_true", help="reveal email (costs more credits)")
    ap.add_argument("--verify", action="store_true",
                    help="verify produced emails (MillionVerifier if keyed, else keyless syntax+MX)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        rows = json.load(f)
    if args.limit > 0:
        rows = rows[: args.limit]

    key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not key:
        print("WARN: APOLLO_API_KEY not set — profile-only degrade (no firmographics/email).",
              file=sys.stderr)
        out = [profile_only(r) for r in rows]
    else:
        out, org_cache = [], {}
        for r in rows:
            out.append(enrich_one(r, key, args.reveal_email, org_cache))
            time.sleep(0.3)

    if args.verify:
        for r in out:
            if r.get("email"):
                r["email_verification"] = verify_email(r["email"])

    n_enriched = sum(1 for r in out if r.get("enriched"))
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"enriched {n_enriched}/{len(out)} (profile-only: {len(out)-n_enriched}) "
              f"-> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
