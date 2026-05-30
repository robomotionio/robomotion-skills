#!/usr/bin/env python3
"""dns_scan.py — DNS-based email/tech-stack recon via `dig` (keyless detection signal #4).

Deterministic. Shells out to `dig` for MX / SPF / DKIM / DMARC / TXT / CNAME and maps:
  - MX hostnames           -> email provider (Google Workspace, M365, Proofpoint, ...)
  - SPF include: targets   -> authorized senders / tools (SendGrid, Marketo, HubSpot, ...)
  - DMARC policy + rua     -> enforcement strength + reporting/monitoring provider
  - DKIM selectors (probed)-> which tools actually sign mail (google, selector1/2, k1, ...)
  - TXT verification tokens -> vendors proving domain ownership (Stripe, Atlassian, ...)
Plus the existing DNS-blacklist checks and cold-outbound-domain probe.

DNS is the highest-signal, zero-cost layer — SPF/DKIM "don't lie". No LLM; the agent
writes the deliverability assessment from this structured output. Requires `dig` on PATH.

Examples:
  dns_scan.py --domain example.com
  dns_scan.py --domain example.com --no-blacklist --output ${WORKSPACE}/dns.json
"""
import argparse
import json
import re
import shutil
import subprocess
import sys

# --- MX hostname substring -> email provider ---------------------------------
MX_MAP = {
    "google.com": "Google Workspace",
    "googlemail.com": "Google Workspace",
    "aspmx.l.google.com": "Google Workspace",
    "outlook.com": "Microsoft 365",
    "protection.outlook.com": "Microsoft 365",
    "mail.protection.outlook.com": "Microsoft 365",
    "pphosted.com": "Proofpoint",
    "ppe-hosted.com": "Proofpoint",
    "mimecast.com": "Mimecast",
    "zoho.com": "Zoho Mail",
    "zoho.eu": "Zoho Mail",
    "fastmail.com": "Fastmail",
    "messagingengine.com": "Fastmail",
    "amazonaws.com": "Amazon SES/WorkMail",
    "amazonses.com": "Amazon SES",
    "secureserver.net": "GoDaddy Email",
    "improvmx.com": "ImprovMX",
    "forwardemail.net": "ForwardEmail",
    "barracudanetworks.com": "Barracuda",
    "cloudflare.net": "Cloudflare Email Routing",
    "mxrecord.io": "Cloudflare Email Routing",
    "yandex.net": "Yandex Mail",
    "ovh.net": "OVH Mail",
    "registrar-servers.com": "Namecheap Private Email",
    "hostedemail.com": "Hosted Email (Open-Xchange)",
    "emailsrvr.com": "Rackspace Email",
}

# --- SPF include: target substring -> tool/sender ----------------------------
SPF_INCLUDE_MAP = {
    "_spf.google.com": "Google Workspace",
    "spf.protection.outlook.com": "Microsoft 365",
    "amazonses.com": "Amazon SES",
    "sendgrid.net": "SendGrid",
    "mailgun.org": "Mailgun",
    "spf.mandrillapp.com": "Mandrill (Mailchimp Transactional)",
    "servers.mcsv.net": "Mailchimp",
    "_spf.salesforce.com": "Salesforce",
    "et._spf.pardot.com": "Pardot (Salesforce)",
    "mktomail.com": "Marketo",
    "mktdns.com": "Marketo",
    "_spf.hubspot.com": "HubSpot",
    "spf.hubspotemail.net": "HubSpot",
    "pphosted.com": "Proofpoint",
    "mimecast.com": "Mimecast",
    "zoho.com": "Zoho Mail",
    "zoho.eu": "Zoho Mail",
    "spf.smtp2go.com": "SMTP2GO",
    "_spf.salesloft.com": "Salesloft",
    "spf.sleadtrack.com": "Smartlead",
    "_spf.instantly.ai": "Instantly",
    "spf.mtasv.net": "Postmark",
    "_spf.intercom.io": "Intercom",
    "spf.mailjet.com": "Mailjet",
    "_spf.brevo.com": "Brevo (Sendinblue)",
    "spf.sendinblue.com": "Brevo (Sendinblue)",
    "_spf.qemailserver.com": "Qualtrics",
    "mail.zendesk.com": "Zendesk",
    "_spf.freshemail.io": "Freshworks",
    "_spf.createsend.com": "Campaign Monitor",
    "cmail19.com": "Campaign Monitor",
    "helpscout.net": "Help Scout",
    "amazonappflow.com": "Amazon AppFlow",
    "_spf.zoho.com": "Zoho",
    "_spf.klaviyo.com": "Klaviyo",
    "klaviyomail.com": "Klaviyo",
    "_spf.customer.io": "Customer.io",
    "mailsenders.netsuite.com": "NetSuite",
    "spf.constantcontact.com": "Constant Contact",
    "spf.protection.sophos.com": "Sophos Email",
    "spf.messagelabs.com": "Symantec MessageLabs",
}

# --- DKIM selectors to probe + which tool each implies ------------------------
DKIM_SELECTORS = [
    "google", "selector1", "selector2", "k1", "k2", "k3", "s1", "s2", "dkim",
    "default", "mail", "smtp", "mandrill", "sig1", "scph0", "scph1", "scph1023",
    "pm", "pm-bounces", "mxvault", "zoho", "zohomail", "hs1", "hs2", "hs1-",
    "sendgrid", "sg", "mte1", "mte2", "fdkim", "krs", "litesrv", "everlytickey1",
    "cm", "createsend", "klaviyo", "intercom", "mc1", "amazonses",
]
DKIM_SELECTOR_TOOL = {
    "google": "Google Workspace",
    "selector1": "Microsoft 365",
    "selector2": "Microsoft 365",
    "mandrill": "Mandrill (Mailchimp Transactional)",
    "pm": "Postmark",
    "pm-bounces": "Postmark",
    "scph0": "SparkPost",
    "scph1": "SparkPost",
    "scph1023": "SparkPost",
    "hs1": "HubSpot",
    "hs2": "HubSpot",
    "sendgrid": "SendGrid",
    "sg": "SendGrid",
    "zoho": "Zoho Mail",
    "zohomail": "Zoho Mail",
    "k1": "Mailchimp/Klaviyo (k1)",
    "klaviyo": "Klaviyo",
    "createsend": "Campaign Monitor",
    "cm": "Campaign Monitor",
    "intercom": "Intercom",
    "amazonses": "Amazon SES",
    "mte1": "Marketo",
    "mte2": "Marketo",
}

# --- TXT verification token substring -> vendor (domain-ownership proof) ------
TXT_VERIFICATION_MAP = {
    "google-site-verification": "Google (Search Console / Workspace)",
    "facebook-domain-verification": "Meta / Facebook",
    "stripe-verification": "Stripe",
    "atlassian-domain-verification": "Atlassian (Jira/Confluence)",
    "atlassian-sending-domain-verification": "Atlassian",
    "docusign": "DocuSign",
    "adobe-idp-site-verification": "Adobe",
    "miro-verification": "Miro",
    "slack-domain-verification": "Slack",
    "zoom-domain-verification": "Zoom",
    "asana-domain-verification": "Asana",
    "dropbox-domain-verification": "Dropbox",
    "notion-domain-verification": "Notion",
    "loom-site-verification": "Loom",
    "calendly-site-verification": "Calendly",
    "intercom-verification": "Intercom",
    "hubspot": "HubSpot",
    "pardot": "Pardot (Salesforce)",
    "ahrefs-site-verification": "Ahrefs (SEO)",
    "logmein-verification": "LogMeIn/GoTo",
    "citrix-verification": "Citrix",
    "workplace-domain-verification": "Meta Workplace",
    "mongodb-site-verification": "MongoDB Atlas",
    "stripe-verification": "Stripe",
    "shopify": "Shopify",
    "wix-domain-verification": "Wix",
    "webflow": "Webflow",
    "twilio-domain-verification": "Twilio",
    "segment": "Segment",
    "amazonses": "Amazon SES",
    "open.sleadtrack.com": "Smartlead (tracking)",
    "instantly": "Instantly",
    "apollo": "Apollo",
    "front": "Front",
    "mailgun": "Mailgun",
    "sendgrid": "SendGrid",
    "klaviyo": "Klaviyo",
    "ms=": "Microsoft 365 (verification)",
    "yandex-verification": "Yandex",
}

# --- DMARC rua provider substring -> aggregate-report processor --------------
DMARC_RUA_MAP = {
    "dmarc.postmarkapp.com": "Postmark DMARC",
    "rua.agari.com": "Agari/Fortra",
    "dmarc.cyberint.com": "Cyberint",
    "valimail.com": "Valimail",
    "ruf@": "(forensic reports)",
    "dmarcian": "dmarcian",
    "dmarc-reports": "(self-hosted reports)",
    "ondmarc.com": "OnDMARC (Red Sift)",
    "redsift": "Red Sift OnDMARC",
    "easydmarc": "EasyDMARC",
    "mailhardener": "Mailhardener",
    "fraudmarc": "Fraudmarc",
    "proofpoint": "Proofpoint EFD",
    "mxtoolbox": "MxToolbox DMARC",
}

BLACKLISTS = ["zen.spamhaus.org", "bl.spamcop.net", "b.barracudacentral.org",
              "dnsbl.sorbs.net", "multi.surbl.org"]
OUTBOUND_PREFIXES = ["get", "try", "go", "mail", "email", "hello", "team", "send", "use"]
OUTBOUND_SUFFIXES = ["reach", "mail", "hq", "app", "io", "sales", "outbound"]


def have_dig():
    return shutil.which("dig") is not None


def dig(record_type, name):
    cmd = ["dig", "+short", record_type, name]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return [l.strip() for l in out.stdout.splitlines() if l.strip()]
    except (subprocess.TimeoutExpired, OSError):
        return []


def dig_a(name):
    return dig("A", name)


def _map_substr(value, mapping, found_set, src_label=None):
    """Add mapping hits found as substrings of value into found_set (list of dicts)."""
    vl = value.lower()
    for key, tool in mapping.items():
        if key.lower() in vl:
            found_set.add((tool, key))


def scan_email_auth(domain):
    mx = dig("MX", domain)
    txt = dig("TXT", domain)
    spf = next((t for t in txt if "v=spf1" in t.lower()), "")
    dmarc_txt = dig("TXT", f"_dmarc.{domain}")
    dmarc = next((t for t in dmarc_txt if "v=dmarc1" in t.lower()), "")

    # email provider from MX
    email_providers = set()
    for rec in mx:
        host = rec.split()[-1].rstrip(".").lower() if rec.split() else ""
        for key, prov in MX_MAP.items():
            if key in host:
                email_providers.add(prov)

    # SPF analysis
    spf_includes = re.findall(r"include:([^\s\"]+)", spf)
    spf_redirects = re.findall(r"redirect=([^\s\"]+)", spf)
    spf_all = ""
    m = re.search(r"([~\-\+\?])all", spf)
    if m:
        spf_all = m.group(0)
    spf_senders = set()
    for inc in spf_includes + spf_redirects:
        _map_substr(inc, SPF_INCLUDE_MAP, spf_senders)

    # DMARC parse
    dmarc_policy = dmarc_sp = dmarc_pct = ""
    dmarc_rua = []
    dmarc_rua_providers = set()
    if dmarc:
        pm = re.search(r"\bp=(\w+)", dmarc)
        dmarc_policy = pm.group(1) if pm else ""
        spm = re.search(r"\bsp=(\w+)", dmarc)
        dmarc_sp = spm.group(1) if spm else ""
        pcm = re.search(r"\bpct=(\d+)", dmarc)
        dmarc_pct = pcm.group(1) if pcm else "100"
        dmarc_rua = re.findall(r"rua=([^;]+)", dmarc)
        for r in dmarc_rua:
            _map_substr(r, DMARC_RUA_MAP, dmarc_rua_providers)

    # TXT verification tokens
    txt_vendors = set()
    for t in txt:
        _map_substr(t, TXT_VERIFICATION_MAP, txt_vendors)

    # DKIM selector probe. First detect wildcard *._domainkey (some DNS setups answer
    # EVERY selector) — if a random nonexistent selector resolves, per-selector results
    # are meaningless and must not be mapped to tools.
    dkim_found = []
    dkim_tools = set()
    dkim_wildcard = bool(
        DKIM_SELECTORS and (
            dig("TXT", f"zzqx9w8probe._domainkey.{domain}")
            or dig("CNAME", f"zzqx9w8probe._domainkey.{domain}")))
    if not dkim_wildcard:
        for sel in DKIM_SELECTORS:
            rec = dig("TXT", f"{sel}._domainkey.{domain}") or dig("CNAME", f"{sel}._domainkey.{domain}")
            if rec:
                dkim_found.append(sel)
                if sel in DKIM_SELECTOR_TOOL:
                    dkim_tools.add(DKIM_SELECTOR_TOOL[sel])

    # consolidate vendor signals from DNS
    tools = set()
    tools |= email_providers
    tools |= {t for t, _ in spf_senders}
    tools |= {t for t, _ in txt_vendors}
    tools |= dkim_tools

    # deliverability assessment cues (booleans the agent can read off directly)
    spf_weak = spf_all in ("+all", "?all") or (spf and not spf_all)
    dmarc_enforced = dmarc_policy in ("quarantine", "reject")

    return {
        "mx": mx,
        "email_provider": sorted(email_providers),
        "spf": spf,
        "spf_includes": spf_includes,
        "spf_redirects": spf_redirects,
        "spf_all_qualifier": spf_all,
        "spf_present": bool(spf),
        "spf_senders": sorted({t for t, _ in spf_senders}),
        "dmarc": dmarc,
        "dmarc_policy": dmarc_policy,
        "dmarc_subdomain_policy": dmarc_sp,
        "dmarc_pct": dmarc_pct,
        "dmarc_present": bool(dmarc),
        "dmarc_enforced": dmarc_enforced,
        "dmarc_rua": dmarc_rua,
        "dmarc_rua_providers": sorted({t for t, _ in dmarc_rua_providers}),
        "dkim_selectors_found": dkim_found,
        "dkim_tools": sorted(dkim_tools),
        "dkim_wildcard": dkim_wildcard,
        "txt_records": txt,
        "txt_verifications": sorted({t for t, _ in txt_vendors}),
        "tools_from_dns": sorted(tools),
        "deliverability_flags": {
            "spf_weak_or_missing_all": bool(spf_weak),
            "dmarc_missing": not bool(dmarc),
            "dmarc_monitoring_only": dmarc_policy == "none",
            "dmarc_enforced": dmarc_enforced,
        },
    }


def check_blacklists(domain):
    a = dig_a(domain)
    ip = next((x for x in a if re.match(r"^\d+\.\d+\.\d+\.\d+$", x)), "")
    results = {}
    if not ip:
        return {"ip": "", "note": "no A record IP to check", "listings": {}}
    reversed_ip = ".".join(reversed(ip.split(".")))
    for bl in BLACKLISTS:
        results[bl] = bool(dig_a(f"{reversed_ip}.{bl}"))
    return {"ip": ip, "listings": results, "any_listed": any(results.values())}


def probe_outbound(domain):
    root = domain.split(".")[0]
    tld = domain[len(root):]
    candidates = set()
    for p in OUTBOUND_PREFIXES:
        candidates.add(f"{p}{root}{tld}")
        candidates.add(f"{p}{root}.com")
    for s in OUTBOUND_SUFFIXES:
        candidates.add(f"{root}{s}.com")
    candidates.discard(domain)
    found = []
    for cand in sorted(candidates):
        a = dig_a(cand)
        if a:
            spf_txt = dig("TXT", cand)
            spf = next((t for t in spf_txt if "v=spf1" in t.lower()), "")
            sl = spf.lower()
            found.append({
                "domain": cand, "a_records": a, "spf": spf,
                "likely_cold_outbound": bool("sleadtrack" in sl or "instantly" in sl
                                             or "smartlead" in sl or "_spf.salesloft" in sl),
            })
    return found


def main():
    ap = argparse.ArgumentParser(description="DNS-based email/tech-stack recon via dig (keyless).")
    ap.add_argument("--domain", required=True, help="company apex domain (e.g. example.com)")
    ap.add_argument("--no-blacklist", action="store_true", help="skip DNS-blacklist checks")
    ap.add_argument("--no-outbound", action="store_true", help="skip cold-outbound-domain probing")
    ap.add_argument("--no-dkim", action="store_true", help="skip DKIM selector probing (faster)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    if not have_dig():
        sys.exit("ERROR: `dig` not found on PATH. Install bind/dnsutils to run the DNS layer.")

    domain = args.domain.lower().strip()
    for pre_ in ("https://", "http://"):
        if domain.startswith(pre_):
            domain = domain[len(pre_):]
    domain = domain.strip("/").split("/")[0]

    if args.no_dkim:
        global DKIM_SELECTORS
        DKIM_SELECTORS = []

    result = {"domain": domain, "email_auth": scan_email_auth(domain)}
    if not args.no_blacklist:
        result["blacklists"] = check_blacklists(domain)
    if not args.no_outbound:
        result["outbound_domains"] = probe_outbound(domain)

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"DNS scan {domain} -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
