#!/usr/bin/env python3
"""verify_emails.py — deliverability-check a lead list before send.

Uses MillionVerifier (MILLIONVERIFIER_API_KEY) when set. Without a key it falls back to
SYNTAX/MX-style local checks only (format + duplicate detection — NOT a deliverability
guarantee) and flags the reduced confidence. Deterministic, stdlib only.

Input: a CSV with an email column (--email-col, default 'email') or a JSON list of objects.
Output: same rows annotated with email_status (ok|risky|invalid|unknown) + email_result;
optionally drops invalid/risky.

Examples:
  verify_emails.py --input leads.csv --output verified.json
  verify_emails.py --input leads.json --drop-bad --output clean.json
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

MV_URL = "https://api.millionverifier.com/api/v3/"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def load_rows(path, email_col):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    s = raw.lstrip()
    if s.startswith("[") or s.startswith("{"):
        data = json.loads(raw)
        return data if isinstance(data, list) else [data]
    rows = list(csv.DictReader(io.StringIO(raw)))
    return rows


def mv_verify(email, key):
    qs = urllib.parse.urlencode({"api": key, "email": email})
    req = urllib.request.Request(MV_URL + "?" + qs, headers={"User-Agent": "robomotion-gtm-skills/verify"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode("utf-8", "ignore"))
            result = (d.get("result") or "").lower()  # ok / catch_all / unknown / invalid / disposable
            status = {"ok": "ok", "catch_all": "risky", "unknown": "unknown",
                      "disposable": "risky", "invalid": "invalid"}.get(result, "unknown")
            return status, result
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return "unknown", f"http_{e.code}"
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return "unknown", "network_error"
    return "unknown", "retries_exhausted"


def main():
    ap = argparse.ArgumentParser(description="Verify email deliverability (MillionVerifier or local-syntax fallback).")
    ap.add_argument("--input", default="-", help="CSV or JSON list of leads; default stdin")
    ap.add_argument("--email-col", default="email", help="email column/key (default 'email')")
    ap.add_argument("--drop-bad", action="store_true", help="drop invalid/risky rows from output")
    ap.add_argument("--output", default="-", help="output JSON path; default stdout")
    args = ap.parse_args()

    rows = load_rows(args.input, args.email_col)
    key = os.environ.get("MILLIONVERIFIER_API_KEY", "").strip()
    if not key:
        print("WARN: MILLIONVERIFIER_API_KEY unset — local syntax/dedup checks only "
              "(NOT a deliverability guarantee; higher bounce risk).", file=sys.stderr)

    seen, out = set(), []
    n_ok = n_bad = 0
    for r in rows:
        email = (r.get(args.email_col) or "").strip().lower()
        if not email or not EMAIL_RE.match(email):
            r["email_status"], r["email_result"] = "invalid", "bad_syntax"
        elif email in seen:
            r["email_status"], r["email_result"] = "invalid", "duplicate"
        elif key:
            r["email_status"], r["email_result"] = mv_verify(email, key)
            time.sleep(0.1)
        else:
            r["email_status"], r["email_result"] = "unknown", "syntax_ok_unverified"
        if email:
            seen.add(email)
        if r["email_status"] in ("invalid", "risky"):
            n_bad += 1
            if args.drop_bad:
                continue
        else:
            n_ok += 1
        out.append(r)

    print(f"INFO: {n_ok} ok/unknown, {n_bad} invalid/risky"
          f"{' (dropped)' if args.drop_bad else ''}.", file=sys.stderr)

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        print(f"{len(out)} rows -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
