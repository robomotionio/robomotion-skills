#!/usr/bin/env python3
"""enrich_apollo.py — enrich selected engagers via Apollo (TWO-PHASE, X-Api-Key).

Engine step 3: after dedup + agent selection, resolve firmographics for each engager so
score_icp.py can tier them. Reuses the apollo-lead-finder People Match pattern (X-Api-Key
header). Resolves: title, seniority, company, company_domain, company_size, industry,
and (optionally) a verified email.

TWO-PHASE enrichment (raises hit rate on engagers, who often only carry a name + headline):
  Phase A — ORG RESOLVE: if the engager has a company name but no domain, resolve the
            Apollo organization (mixed_companies/search) to a primary domain. A People
            Match keyed by name + DOMAIN is far more reliable than name alone.
  Phase B — PEOPLE MATCH: match the person for title/seniority/company/size/industry/email,
            seeded with the resolved domain when available.
The org-resolve result is cached per company name so a batch of engagers from the same
employer only costs one organization lookup.

COST-AWARE: this spends Apollo credits — run it only on the deduped / agent-selected
subset, never the full raw extraction. Use --limit as a hard ceiling.

Degrade: if APOLLO_API_KEY is not set, the script PASSES THROUGH every engager unchanged
(profile-only), filling firmographic fields with "" so the downstream scorer still runs.

Email fallback: if Apollo returns no email, set DROPCONTACT_API_KEY to attempt a domain+name
email guess via Dropcontact (same fallback the apollo-lead-finder pattern documents). Off by
default; never blocks the pipeline.

Stdlib only.

Examples:
  # Enrich the deduped, agent-selected winners (caps at 50):
  enrich_apollo.py --input new_engagers.json --limit 50 --reveal-email \
      --output enriched.json

  # No APOLLO_API_KEY -> profile-only pass-through (no spend, no error):
  enrich_apollo.py --input new_engagers.json --output enriched.json
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
            return {"_error": f"{e.code}: {e.read().decode('utf-8', 'ignore')[:200]}"}
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return {"_error": str(e)}


def split_name(engager):
    name = (engager.get("name") or "").strip()
    parts = name.split()
    first = engager.get("first_name") or (parts[0] if parts else "")
    last = engager.get("last_name") or (parts[-1] if len(parts) > 1 else "")
    return first, last


def passthrough(engager):
    """Profile-only enrichment shape when Apollo is unavailable or no match."""
    return dict(engager,
                title=engager.get("title") or engager.get("headline") or "",
                seniority=engager.get("seniority", ""),
                company=engager.get("company", ""),
                company_domain=engager.get("company_domain", ""),
                company_size=engager.get("company_size", ""),
                industry=engager.get("industry", ""),
                email=engager.get("email", ""))


def resolve_org(name, key, cache):
    """Phase A: resolve a company NAME to its Apollo organization (primary domain + size +
    industry). Cached per name so a batch from one employer costs one lookup. Returns a
    dict {domain, size, industry} (empty on miss)."""
    if not name:
        return {}
    key_norm = name.strip().lower()
    if key_norm in cache:
        return cache[key_norm]
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
    cache[key_norm] = org
    return org


def dropcontact_email(first, last, domain):
    """Optional email fallback when Apollo returns none. Needs DROPCONTACT_API_KEY +
    a company domain. Best-effort; returns '' on any failure."""
    dk = os.environ.get("DROPCONTACT_API_KEY", "").strip()
    if not dk or not domain or not (first or last):
        return ""
    body = {"data": [{"first_name": first, "last_name": last, "website": domain}],
            "siren": False}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        DROPCONTACT_URL, data=data, method="POST",
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


def enrich_one(engager, key, reveal_email, org_cache):
    first, last = split_name(engager)

    # ---- Phase A: org resolve (only if we have a company name but no domain) ----------
    domain = engager.get("company_domain") or ""
    org_size = engager.get("company_size") or ""
    org_industry = engager.get("industry") or ""
    if engager.get("company") and not domain:
        org = resolve_org(engager["company"], key, org_cache)
        domain = domain or org.get("domain", "")
        org_size = org_size or org.get("size", "")
        org_industry = org_industry or org.get("industry", "")

    # ---- Phase B: people match (seeded with the resolved domain) -----------------------
    body = {}
    if first:
        body["first_name"] = first
    if last:
        body["last_name"] = last
    if engager.get("profile_url"):
        body["linkedin_url"] = engager["profile_url"]
    if engager.get("company"):
        body["organization_name"] = engager["company"]
    if domain:
        body["domain"] = domain
    if reveal_email:
        body["reveal_personal_emails"] = True
    if not body:
        return passthrough(engager)

    data = post(MATCH_URL, body, key)
    if "_error" in data:
        out = dict(passthrough(engager), enrich_error=data["_error"])
        # keep whatever org-resolve gave us even if people-match failed
        out["company_domain"] = out.get("company_domain") or domain
        out["company_size"] = out.get("company_size") or org_size
        out["industry"] = out.get("industry") or org_industry
        return out
    p = data.get("person") or {}
    if not p:
        out = passthrough(engager)
        out["company_domain"] = out.get("company_domain") or domain
        out["company_size"] = out.get("company_size") or org_size
        out["industry"] = out.get("industry") or org_industry
        return out
    org = p.get("organization") or {}
    email = p.get("email") or ""
    if email and "email_not_unlocked" in email:
        email = ""
    final_domain = (org.get("primary_domain") or org.get("website_url") or domain or "")
    if reveal_email and not email:
        email = dropcontact_email(first, last, final_domain)
    return dict(
        engager,
        title=p.get("title") or engager.get("headline") or engager.get("title", ""),
        seniority=p.get("seniority", ""),
        company=org.get("name") or engager.get("company", ""),
        company_domain=final_domain,
        company_size=org.get("estimated_num_employees")
        or org.get("organization_num_employees", "") or org_size,
        industry=org.get("industry", "") or org_industry,
        email=email,
        email_status=p.get("email_status", ""))


def main():
    ap = argparse.ArgumentParser(description="Apollo People Match enrichment of selected engagers.")
    ap.add_argument("--input", required=True, help="JSON list of (deduped/selected) engagers")
    ap.add_argument("--limit", type=int, default=0, help="enrich at most N (0 = all in input)")
    ap.add_argument("--reveal-email", action="store_true", help="reveal verified email (spends more credits)")
    ap.add_argument("--verify", action="store_true",
                    help="verify produced emails (MillionVerifier if keyed, else keyless syntax+MX)")
    ap.add_argument("--output", default="-")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        engagers = json.load(f)
    if args.limit > 0:
        engagers = engagers[: args.limit]

    key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not key:
        out = [passthrough(e) for e in engagers]
        print("WARN: APOLLO_API_KEY not set -> profile-only pass-through (no enrichment).",
              file=sys.stderr)
    else:
        out, org_cache = [], {}
        for e in engagers:
            out.append(enrich_one(e, key, args.reveal_email, org_cache))
            time.sleep(0.3)

    if args.verify:
        for e in out:
            if e.get("email"):
                e["email_verification"] = verify_email(e["email"])

    with_co = sum(1 for e in out if e.get("company"))
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    print(f"enriched {len(out)} engagers, {with_co} with company -> {args.output}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
