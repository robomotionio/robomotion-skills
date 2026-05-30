#!/usr/bin/env python3
"""email_lint.py — deterministic linter for cold-email copy.

The AGENT writes the copy; this script only VERIFIES it against the hard rules
in the email-drafting contract: subject length, body word
count per touch type, banned phrases, single-CTA, and emoji/all-caps checks.
No LLM calls, stdlib only.

Input: a JSON file (or stdin) — either one draft object or a list of them:
  {"touch_number":1, "send_day":1, "subject":"...", "body":"...",
   "framework":"PAS", "touch_type":"opener"}
touch_type one of: opener (T1), followup, breakup. Defaults to opener.

Exit code 0 if all drafts pass, 1 if any draft has an ERROR-level violation.

Example:
  email_lint.py --input draft.json
  cat sequence.json | email_lint.py --max-subject 50
"""
import argparse
import json
import re
import sys

# Word-count targets per touch type (from the contract: T1 50-90, follow-ups 30-50, breakup 20-40).
WORD_TARGETS = {
    "opener": (50, 90),
    "followup": (30, 50),
    "breakup": (20, 40),
}

# Phrases that flatten cold email; case-insensitive substring match.
BANNED_PHRASES = [
    "quick question", "i hope this email finds you well", "hope you're doing well",
    "just checking in", "just following up", "touch base", "circle back",
    "synergy", "pick your brain", "to whom it may concern", "dear sir or madam",
    "i wanted to reach out", "we are a leading", "world-class", "best-in-class",
    "game-changer", "revolutionary", "cutting-edge", "low-hanging fruit",
]

# CTA detectors — a single clear ask is the rule; multiple distinct asks are flagged.
CTA_PATTERNS = [
    r"\bare you (free|available|open)\b",
    r"\bworth a (chat|call|conversation)\b",
    r"\bopen to (a|chatting|connecting)\b",
    r"\b(book|grab|schedule|set up) (a|some) (call|time|chat|demo|meeting)\b",
    r"\bcan i (send|share|get)\b",
    r"\bwould (you|it) be\b.*\?",
    r"\b(reply|respond|let me know)\b",
    r"\bany interest\b",
]

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF]"
)


def word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def count_ctas(body):
    n = 0
    low = (body or "").lower()
    for pat in CTA_PATTERNS:
        if re.search(pat, low):
            n += 1
    return n


def lint_one(d, max_subject):
    errors, warnings = [], []
    subject = d.get("subject", "") or ""
    body = d.get("body", "") or ""
    ttype = (d.get("touch_type") or "opener").lower()
    if ttype not in WORD_TARGETS:
        ttype = "opener"

    # Subject length (hard rule: < max_subject chars).
    if len(subject) > max_subject:
        errors.append(f"subject {len(subject)} chars > {max_subject} max — rewrite (do not truncate)")
    if not subject.strip():
        warnings.append("empty subject line")

    # Subject all-caps words / emoji.
    if EMOJI_RE.search(subject):
        errors.append("subject contains emoji")
    caps = [w for w in subject.split() if len(w) >= 3 and w.isupper()]
    if caps:
        warnings.append(f"subject has ALL-CAPS word(s): {', '.join(caps)}")

    # Body word count vs touch-type target.
    wc = word_count(body)
    lo, hi = WORD_TARGETS[ttype]
    if wc < lo:
        warnings.append(f"body {wc} words < {lo} target for '{ttype}'")
    elif wc > hi:
        warnings.append(f"body {wc} words > {hi} target for '{ttype}' — tighten")

    # Banned phrases (case-insensitive) in subject+body.
    blob = (subject + "\n" + body).lower()
    hits = [p for p in BANNED_PHRASES if p in blob]
    for p in hits:
        errors.append(f"banned phrase: \"{p}\"")

    # Emoji in body.
    if EMOJI_RE.search(body):
        warnings.append("body contains emoji")

    # CTA count — one is ideal; 0 or >1 flagged.
    n_cta = count_ctas(body)
    if n_cta == 0:
        warnings.append("no clear CTA detected — add one explicit ask")
    elif n_cta > 1:
        warnings.append(f"{n_cta} possible CTAs — keep a single ask")

    return errors, warnings, {"touch_type": ttype, "word_count": wc, "subject_len": len(subject), "cta_count": n_cta}


def main():
    ap = argparse.ArgumentParser(description="Deterministic cold-email copy linter (no LLM).")
    ap.add_argument("--input", default="-", help="JSON file (one draft or a list); default stdin")
    ap.add_argument("--max-subject", type=int, default=50, help="max subject chars (default 50)")
    ap.add_argument("--output", default="text", choices=["text", "json"])
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    data = json.loads(raw)
    drafts = data if isinstance(data, list) else [data]

    report, any_error = [], False
    for i, d in enumerate(drafts):
        errs, warns, stats = lint_one(d, args.max_subject)
        if errs:
            any_error = True
        report.append({
            "index": i,
            "touch_number": d.get("touch_number", i + 1),
            "stats": stats,
            "errors": errs,
            "warnings": warns,
            "pass": not errs,
        })

    if args.output == "json":
        json.dump({"pass": not any_error, "drafts": report}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        for r in report:
            tag = "PASS" if r["pass"] else "FAIL"
            print(f"[{tag}] touch {r['touch_number']} "
                  f"({r['stats']['touch_type']}, {r['stats']['word_count']}w, "
                  f"subj {r['stats']['subject_len']}c, {r['stats']['cta_count']} CTA)")
            for e in r["errors"]:
                print(f"   ERROR:   {e}")
            for w in r["warnings"]:
                print(f"   warning: {w}")
        print(f"\nOverall: {'PASS' if not any_error else 'FAIL (fix ERRORs above)'}")

    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()
