#!/usr/bin/env python3
"""launch_campaign.py — create/launch a cold-email campaign via the chosen provider.

Providers (deterministic REST calls, stdlib only):
  lemlist   -> LEMLIST_API_KEY      (create campaign + add leads)
  instantly -> INSTANTLY_API_KEY    (create campaign + add leads)
  sendgrid  -> SENDGRID_API_KEY      (one-off / single-send to the list)
  resend    -> RESEND_API_KEY        (one-off send to the list)
  generic_csv -> no key; writes a tool-ready import CSV (NOTHING is sent)

The AGENT writes the sequence copy (via email-drafting) and passes it in. This script
only imports leads + sequence and triggers the campaign.

Input:
  --leads      JSON list of {email, first_name, last_name, company, title, ...}
  --sequence   JSON list of {subject, body, send_day} (the drafted touches)
Modes:
  --dry-run    build the request payloads and print them; do NOT call the API

Examples:
  launch_campaign.py --tool lemlist --campaign-name "Q3 RPA" --leads leads.json --sequence seq.json
  launch_campaign.py --tool generic_csv --leads leads.json --sequence seq.json --output import.csv
  launch_campaign.py --tool instantly --campaign-name X --leads l.json --sequence s.json --dry-run
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request


def http(method, url, headers, body=None, timeout=60):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode("utf-8", "ignore")
                return r.status, (json.loads(txt) if txt.strip().startswith(("{", "[")) else txt)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return e.code, e.read().decode("utf-8", "ignore")[:500]
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return 0, f"network: {e}"
    return 0, "retries_exhausted"


def need(var):
    v = os.environ.get(var, "").strip()
    if not v:
        sys.exit(f"ERROR: {var} not set — required to launch via this tool "
                 f"(use --tool generic_csv to export instead of send).")
    return v


def launch_lemlist(name, leads, sequence, dry):
    key = need("LEMLIST_API_KEY")
    import base64
    auth = base64.b64encode(f":{key}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
    plan = {"create_campaign": {"name": name}, "add_leads": len(leads), "sequence_touches": len(sequence)}
    if dry:
        return {"tool": "lemlist", "dry_run": True, "plan": plan}
    st, camp = http("POST", "https://api.lemlist.com/api/campaigns", headers, {"name": name})
    if st >= 300:
        sys.exit(f"ERROR: lemlist create campaign failed [{st}]: {camp}")
    camp_id = camp.get("_id") or camp.get("campaignId") if isinstance(camp, dict) else None
    added = 0
    for ld in leads:
        url = f"https://api.lemlist.com/api/campaigns/{camp_id}/leads"
        st, _ = http("POST", url, headers, {
            "email": ld.get("email"), "firstName": ld.get("first_name", ""),
            "lastName": ld.get("last_name", ""), "companyName": ld.get("company", ""),
        })
        if st < 300:
            added += 1
        time.sleep(0.2)
    return {"tool": "lemlist", "campaign_id": camp_id, "leads_added": added,
            "note": "Sequence steps are configured in the lemlist campaign UI / templates; "
                    "load the drafted touches as steps before enabling."}


def launch_instantly(name, leads, sequence, dry):
    key = need("INSTANTLY_API_KEY")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    plan = {"create_campaign": {"name": name}, "add_leads": len(leads), "sequence_touches": len(sequence)}
    if dry:
        return {"tool": "instantly", "dry_run": True, "plan": plan}
    st, camp = http("POST", "https://api.instantly.ai/api/v2/campaigns", headers, {"name": name})
    if st >= 300:
        sys.exit(f"ERROR: instantly create campaign failed [{st}]: {camp}")
    camp_id = camp.get("id") if isinstance(camp, dict) else None
    st, _ = http("POST", "https://api.instantly.ai/api/v2/leads/list", headers, {
        "campaign": camp_id,
        "leads": [{"email": l.get("email"), "first_name": l.get("first_name", ""),
                   "last_name": l.get("last_name", ""), "company_name": l.get("company", "")}
                  for l in leads],
    })
    return {"tool": "instantly", "campaign_id": camp_id, "leads_post_status": st,
            "note": "Add the drafted sequence steps to the campaign, then activate."}


def launch_oneoff(tool, leads, sequence, dry):
    """sendgrid / resend single-send of touch 1 to each lead."""
    if not sequence:
        sys.exit("ERROR: --sequence is empty; nothing to send.")
    t1 = sequence[0]
    if tool == "sendgrid":
        key = need("SENDGRID_API_KEY")
        sender = os.environ.get("SENDGRID_FROM_EMAIL", "").strip()
        if not sender and not dry:
            sys.exit("ERROR: SENDGRID_FROM_EMAIL not set (verified sender required).")
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        url = "https://api.sendgrid.com/v3/mail/send"
    else:  # resend
        key = need("RESEND_API_KEY")
        sender = os.environ.get("RESEND_FROM_EMAIL", "").strip()
        if not sender and not dry:
            sys.exit("ERROR: RESEND_FROM_EMAIL not set.")
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        url = "https://api.resend.com/emails"

    if dry:
        return {"tool": tool, "dry_run": True, "would_send": len(leads),
                "subject": t1.get("subject", ""), "from": sender or "<set FROM env>"}
    sent = 0
    for ld in leads:
        to = ld.get("email")
        if not to:
            continue
        if tool == "sendgrid":
            body = {"personalizations": [{"to": [{"email": to}]}],
                    "from": {"email": sender}, "subject": t1.get("subject", ""),
                    "content": [{"type": "text/plain", "value": t1.get("body", "")}]}
        else:
            body = {"from": sender, "to": [to], "subject": t1.get("subject", ""),
                    "text": t1.get("body", "")}
        st, _ = http("POST", url, headers, body)
        if st < 300:
            sent += 1
        time.sleep(0.2)
    return {"tool": tool, "sent": sent, "of": len(leads),
            "note": "One-off send of touch 1 only; follow-ups are not scheduled "
                    "(use lemlist/instantly for sequencing)."}


def export_csv(leads, sequence, path):
    cols = ["email", "first_name", "last_name", "company", "title"]
    for i in range(len(sequence)):
        cols += [f"subject_{i+1}", f"body_{i+1}", f"send_day_{i+1}"]
    out = sys.stdout if path == "-" else open(path, "w", newline="", encoding="utf-8")
    w = csv.writer(out)
    w.writerow(cols)
    for ld in leads:
        row = [ld.get(c, "") for c in ("email", "first_name", "last_name", "company", "title")]
        for t in sequence:
            row += [t.get("subject", ""), t.get("body", ""), t.get("send_day", "")]
        w.writerow(row)
    if out is not sys.stdout:
        out.close()
    return {"tool": "generic_csv", "leads": len(leads), "touches": len(sequence),
            "output": path, "note": "NOTHING was sent — import this CSV into your tool manually."}


def main():
    ap = argparse.ArgumentParser(description="Launch a cold-email campaign (lemlist/instantly/sendgrid/resend) or export CSV.")
    ap.add_argument("--tool", required=True,
                    choices=["lemlist", "instantly", "sendgrid", "resend", "generic_csv"])
    ap.add_argument("--campaign-name", default="cold-email-campaign")
    ap.add_argument("--leads", required=True, help="JSON list of leads")
    ap.add_argument("--sequence", required=True, help="JSON list of drafted touches")
    ap.add_argument("--dry-run", action="store_true", help="build payloads, do not call the API")
    ap.add_argument("--output", default="-", help="CSV path for generic_csv tool")
    args = ap.parse_args()

    leads = json.load(open(args.leads, encoding="utf-8"))
    sequence = json.load(open(args.sequence, encoding="utf-8"))
    if not isinstance(leads, list):
        leads = [leads]
    if not isinstance(sequence, list):
        sequence = [sequence]

    if args.tool == "generic_csv":
        result = export_csv(leads, sequence, args.output)
    elif args.tool == "lemlist":
        result = launch_lemlist(args.campaign_name, leads, sequence, args.dry_run)
    elif args.tool == "instantly":
        result = launch_instantly(args.campaign_name, leads, sequence, args.dry_run)
    else:
        result = launch_oneoff(args.tool, leads, sequence, args.dry_run)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
