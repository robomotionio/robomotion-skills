#!/usr/bin/env python3
"""phantombuster_send.py — launch a LinkedIn connection/message Phantom for a lead batch.

Automated-send path for linkedin-outreach. Needs PHANTOMBUSTER_API_KEY and a LinkedIn
session cookie (li_at) — passed via --session-cookie or LINKEDIN_SESSION_COOKIE env.
The default path for linkedin-outreach is the CSV export (export_csv.py); this script is
the optional API-send path and MUST be throttled to dodge LinkedIn limits/bans.

Deterministic REST only, stdlib.

Examples:
  phantombuster_send.py --agent-id 1234567890 --leads leads.json --dry-run
  phantombuster_send.py --agent-id 1234567890 --leads leads.json --session-cookie "AQED..."
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

LAUNCH_URL = "https://api.phantombuster.com/api/v2/agents/launch"


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


def main():
    ap = argparse.ArgumentParser(description="Launch a LinkedIn Phantom (connection/message) for a lead batch.")
    ap.add_argument("--agent-id", required=True, help="Phantombuster agent (Phantom) id to launch")
    ap.add_argument("--leads", required=True, help="JSON list of {linkedin_url, connection_request, ...}")
    ap.add_argument("--session-cookie", default="", help="LinkedIn li_at cookie (or LINKEDIN_SESSION_COOKIE env)")
    ap.add_argument("--daily-cap", type=int, default=50, help="max profiles per launch (throttle; default 50)")
    ap.add_argument("--dry-run", action="store_true", help="build payload, do not call the API")
    args = ap.parse_args()

    leads = json.load(open(args.leads, encoding="utf-8"))
    if not isinstance(leads, list):
        leads = [leads]
    leads = leads[: args.daily_cap]

    cookie = args.session_cookie or os.environ.get("LINKEDIN_SESSION_COOKIE", "").strip()

    payload = {
        "id": args.agent_id,
        "argument": {
            "sessionCookie": cookie,
            "profiles": [{"profileUrl": l.get("linkedin_url"),
                          "message": l.get("connection_request") or l.get("message", "")}
                         for l in leads if l.get("linkedin_url")],
        },
    }

    if args.dry_run:
        redacted = dict(payload)
        redacted["argument"] = dict(payload["argument"], sessionCookie="<redacted>" if cookie else "<MISSING>")
        json.dump({"dry_run": True, "agent_id": args.agent_id, "profiles": len(payload["argument"]["profiles"]),
                   "payload": redacted}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    key = os.environ.get("PHANTOMBUSTER_API_KEY", "").strip()
    if not key:
        sys.exit("ERROR: PHANTOMBUSTER_API_KEY not set — required for the API-send path "
                 "(use export_csv.py to export a CSV for manual import instead).")
    if not cookie:
        sys.exit("ERROR: LinkedIn session cookie missing (--session-cookie or LINKEDIN_SESSION_COOKIE).")

    headers = {"X-Phantombuster-Key-1": key, "Content-Type": "application/json"}
    st, resp = http("POST", LAUNCH_URL, headers, payload)
    if st >= 300:
        sys.exit(f"ERROR: Phantombuster launch failed [{st}]: {resp}")
    json.dump({"launched": True, "agent_id": args.agent_id,
               "profiles": len(payload["argument"]["profiles"]), "response": resp,
               "note": "Throttle launches; monitor the Phantom for LinkedIn rate limits/challenges."},
              sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
