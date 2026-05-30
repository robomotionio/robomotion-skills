#!/usr/bin/env python3
"""linkedin_lint.py — deterministic char-limit + quality linter for LinkedIn messages.

The AGENT writes the messages; this script only VERIFIES them against each message
type's hard character limit and a few quality rules (banned filler comments, emoji).
No LLM calls, stdlib only.

Char limits per LinkedIn message type:
  connection_request : 200 (free) / 300 (premium)   -- account_tier sets which
  inmail_subject     : 200
  inmail_body        : 1900
  dm / message_request: 8000
  post_comment / comment_reply : 1250

Input: JSON file (or stdin) — one message object or a list:
  {"linkedin_url":"...","name":"...","message_type":"connection_request",
   "account_tier":"free","message":"...", "inmail_subject":"...", "inmail_body":"..."}

Exit 0 if all pass, 1 if any message exceeds its limit.

Example:
  linkedin_lint.py --input messages.json
  cat msgs.json | linkedin_lint.py --output json
"""
import argparse
import json
import re
import sys

LIMITS = {
    "connection_request_free": 200,
    "connection_request_premium": 300,
    "inmail_subject": 200,
    "inmail_body": 1900,
    "dm": 8000,
    "message_request": 8000,
    "post_comment": 1250,
    "comment_reply": 1250,
}

# Low-value comments LinkedIn engagement should never be.
FILLER_COMMENTS = [
    "great post", "great share", "thanks for sharing", "well said", "love this",
    "so true", "100%", "couldn't agree more", "spot on", "this!", "nice post",
    "great content", "amazing", "awesome post",
]

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF]")


def lint_one(m):
    errors, warnings = [], []
    mtype = (m.get("message_type") or "dm").lower()

    def check(label, text, limit):
        n = len(text or "")
        if n == 0:
            warnings.append(f"{label}: empty")
        elif n > limit:
            errors.append(f"{label}: {n} chars > {limit} limit — rewrite to fit (do not truncate)")
        return n

    stats = {"message_type": mtype}

    if mtype == "connection_request":
        tier = (m.get("account_tier") or "free").lower()
        limit = LIMITS["connection_request_premium"] if tier == "premium" else LIMITS["connection_request_free"]
        stats["limit"] = limit
        stats["len"] = check(f"connection_request ({tier})", m.get("message", ""), limit)
    elif mtype == "inmail":
        stats["subject_len"] = check("inmail_subject", m.get("inmail_subject", ""), LIMITS["inmail_subject"])
        stats["body_len"] = check("inmail_body", m.get("inmail_body", ""), LIMITS["inmail_body"])
    elif mtype in ("dm", "message_request"):
        stats["limit"] = LIMITS[mtype]
        stats["len"] = check(mtype, m.get("message", ""), LIMITS[mtype])
    elif mtype in ("post_comment", "comment_reply"):
        text = m.get("message", "")
        stats["limit"] = LIMITS[mtype]
        stats["len"] = check(mtype, text, LIMITS[mtype])
        low = (text or "").strip().lower()
        if low in FILLER_COMMENTS or any(low == f or low == f + "!" for f in FILLER_COMMENTS):
            errors.append(f"{mtype}: filler comment \"{text.strip()}\" — comments must add value")
    else:
        warnings.append(f"unknown message_type '{mtype}'; checked nothing")

    # Emoji is allowed but flagged for CR (where space is tight / tone matters).
    msg_text = m.get("message", "") + " " + m.get("inmail_body", "")
    if mtype == "connection_request" and EMOJI_RE.search(msg_text):
        warnings.append("connection_request contains emoji")

    return errors, warnings, stats


def main():
    ap = argparse.ArgumentParser(description="LinkedIn message char-limit + quality linter (no LLM).")
    ap.add_argument("--input", default="-", help="JSON file (one message or list); default stdin")
    ap.add_argument("--output", default="text", choices=["text", "json"])
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    data = json.loads(raw)
    msgs = data if isinstance(data, list) else [data]

    report, any_error = [], False
    for i, m in enumerate(msgs):
        errs, warns, stats = lint_one(m)
        if errs:
            any_error = True
        report.append({"index": i, "name": m.get("name", ""), "stats": stats,
                       "errors": errs, "warnings": warns, "pass": not errs})

    if args.output == "json":
        json.dump({"pass": not any_error, "messages": report}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        for r in report:
            tag = "PASS" if r["pass"] else "FAIL"
            print(f"[{tag}] {r['name'] or '(no name)'} — {r['stats']}")
            for e in r["errors"]:
                print(f"   ERROR:   {e}")
            for w in r["warnings"]:
                print(f"   warning: {w}")
        print(f"\nOverall: {'PASS' if not any_error else 'FAIL (rewrite over-limit messages)'}")

    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()
