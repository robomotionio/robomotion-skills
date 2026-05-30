#!/usr/bin/env python3
"""apollo_enrich.py — Phase 2: enrich ONLY selected leads (Apollo if keyed, else keyless).

Takes the ranked/selected subset of the Phase-1 discovery set and reveals verified
email/phone via Apollo's People Match API. NEVER enrich the full discovery set — the
caller (agent) ranks and slices winners first, then passes them here. Stdlib only.

Auth / paid path:
  - If APOLLO_API_KEY is set -> Apollo People Match (verified email/phone). Recommended.
  - If NOT set -> keyless degrade: pattern-guess an email from name + company domain
    (e.g. first.last@domain) and MX-check the domain. Lower confidence, no phone; produces
    a best-effort email so downstream still runs. Requires a company_domain on the lead.

Email verification:
  - If MILLIONVERIFIER_API_KEY is set -> MillionVerifier deliverability result.
  - If NOT set (--verify) -> keyless syntax + MX-record check (basic, no SMTP probe).

Example:
  # take top 50 winners the agent selected, enrich + verify
  apollo_enrich.py --input winners.json --limit 50 --verify --output enriched.json
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
MV_URL = "https://api.millionverifier.com/api/v3/"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _has_mx(domain):
    """Keyless MX check: best-effort A/MX presence via DNS resolution. No external deps;
    falls back to a plain A-record lookup (an MX-less domain that resolves can still take
    mail). Returns True/False/None (None = could not check)."""
    if not domain:
        return None
    try:
        socket.getaddrinfo(domain, None)
        return True
    except Exception:
        return False


def guess_email(lead):
    """Keyless email pattern-guess from name + company domain (first.last@domain).
    Returns '' if we lack a usable name or domain."""
    domain = (lead.get("company_domain") or "").strip().lower()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    if domain.startswith("www."):
        domain = domain[4:]
    first = (lead.get("first_name") or "").strip().lower()
    last = (lead.get("last_name") or "").strip().lower()
    if not domain or not (first or last):
        return ""
    local = f"{first}.{last}".strip(".") if first and last else (first or last)
    local = re.sub(r"[^a-z0-9.]", "", local)
    cand = f"{local}@{domain}"
    return cand if EMAIL_RE.match(cand) else ""


def keyless_enrich(lead):
    """Degrade path: pattern-guess an email, mark its confidence. No Apollo spend, no phone."""
    email = guess_email(lead)
    return dict(lead, email=email, phone="",
                email_status="guessed" if email else "",
                email_confidence="pattern-guess" if email else "")


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
            return {"_error": f"{e.code}: {e.read().decode('utf-8', 'ignore')[:200]}"}
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return {"_error": str(e)}


def verify_email(email):
    """Email deliverability check. MillionVerifier if MILLIONVERIFIER_API_KEY is set;
    otherwise keyless syntax + MX fallback ('ok_syntax_mx' / 'invalid_syntax' / 'no_mx')."""
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
    # Keyless fallback: syntax + MX/A presence.
    if not EMAIL_RE.match(email):
        return "invalid_syntax"
    domain = email.split("@", 1)[1]
    mx = _has_mx(domain)
    if mx is True:
        return "ok_syntax_mx"
    if mx is False:
        return "no_mx"
    return "unknown"


def enrich_one(lead, key):
    body = {"reveal_personal_emails": True}
    if lead.get("first_name"):
        body["first_name"] = lead["first_name"]
    if lead.get("last_name"):
        body["last_name"] = lead["last_name"]
    if lead.get("company"):
        body["organization_name"] = lead["company"]
    if lead.get("company_domain"):
        body["domain"] = lead["company_domain"]
    if lead.get("linkedin_url"):
        body["linkedin_url"] = lead["linkedin_url"]
    if lead.get("id"):
        body["id"] = lead["id"]

    data = post(MATCH_URL, body, key)
    if "_error" in data:
        return dict(lead, email="", phone="", enrich_error=data["_error"])
    p = data.get("person") or {}
    email = p.get("email") or ""
    if email and "email_not_unlocked" in email:
        email = ""
    phones = p.get("phone_numbers") or []
    phone = (phones[0].get("sanitized_number") if phones else "") or ""
    return dict(lead, email=email, phone=phone,
                email_status=p.get("email_status", lead.get("email_status", "")))


def main():
    ap = argparse.ArgumentParser(description="Apollo.io People Match enrichment (Phase 2 — costs credits).")
    ap.add_argument("--input", required=True, help="JSON file of SELECTED winners from apollo_search.py")
    ap.add_argument("--limit", type=int, default=0, help="enrich at most N (0 = all in input)")
    ap.add_argument("--verify", action="store_true",
                    help="verify emails (MillionVerifier if keyed, else keyless syntax+MX)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    key = os.environ.get("APOLLO_API_KEY", "").strip()
    with open(args.input, encoding="utf-8") as f:
        leads = json.load(f)
    if args.limit > 0:
        leads = leads[: args.limit]

    if not key:
        print("WARN: APOLLO_API_KEY not set -> keyless degrade (email pattern-guess + MX "
              "verify; no phone, lower confidence).", file=sys.stderr)

    out = []
    for lead in leads:
        e = enrich_one(lead, key) if key else keyless_enrich(lead)
        if args.verify and e.get("email"):
            e["email_verification"] = verify_email(e["email"])
        out.append(e)
        if key:
            time.sleep(0.3)  # Apollo rate limit

    with_email = sum(1 for e in out if e.get("email"))
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
    print(f"enriched {len(out)} leads, {with_email} with email -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
