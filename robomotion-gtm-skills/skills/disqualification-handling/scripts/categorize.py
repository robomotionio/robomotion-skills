#!/usr/bin/env python3
"""categorize.py — map disqualified-lead sub-verdicts to a handling category + action.

Deterministic routing helper: given each lead's sub-verdict / mismatch_type from the
qualification step, assign a handling category and the routing action. The AGENT still
drafts the actual response copy (via email-drafting) and makes judgement calls on
ambiguous cases — this script only does the rule-based tagging. No LLM, stdlib only.


Categories:
  referral        right-company / wrong-person       -> referral request (highest value)
  nurture         close-but-not-quite (future fit)    -> nurture sequence
  decline         clearly-outside-ICP                 -> polite decline + do-not-contact
  competitor      competitor employee                 -> LOG only, NEVER email
  existing_customer existing customer                 -> route to CS / upsell, never decline

Input JSON/CSV: list of leads with at least {email, company, sub_verdict|mismatch_type}.

Examples:
  categorize.py --input disqualified.json --output tagged.json
"""
import argparse
import csv
import io
import json
import sys

# Keyword -> category rules (checked against sub_verdict / mismatch_type, case-insensitive).
RULES = [
    (["competitor", "rival", "works at competitor"], "competitor"),
    (["existing customer", "current customer", "already a customer", "existing_customer"], "existing_customer"),
    (["wrong person", "wrong-person", "right company", "wrong department", "not decision maker",
      "no authority"], "referral"),
    (["too small", "too early", "not yet", "future", "close", "near-miss", "near miss",
      "wrong stage", "budget later", "timing"], "nurture"),
    (["outside icp", "out of icp", "not a fit", "wrong industry", "wrong geo", "wrong region",
      "disqualified", "no fit"], "decline"),
]

ACTIONS = {
    "referral": "draft a referral-ask email; identify the right persona at the same company",
    "nurture": "add to nurture sequence; draft a soft future-fit intro",
    "decline": "draft a polite decline; add to do-not-contact list",
    "competitor": "LOG for competitive intelligence; do NOT email",
    "existing_customer": "route to CS / account management; do NOT send a decline",
}


def categorize(verdict):
    v = (verdict or "").lower()
    for keywords, cat in RULES:
        if any(k in v for k in keywords):
            return cat
    return "nurture"  # safe default — never ghost, route to nurture


def load(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    s = raw.lstrip()
    if s.startswith("[") or s.startswith("{"):
        d = json.loads(raw)
        return d if isinstance(d, list) else [d]
    return list(csv.DictReader(io.StringIO(raw)))


def main():
    ap = argparse.ArgumentParser(description="Tag disqualified leads with handling category + action (rule-based).")
    ap.add_argument("--input", default="-", help="JSON/CSV leads with sub_verdict/mismatch_type; default stdin")
    ap.add_argument("--verdict-field", default="sub_verdict",
                    help="field holding the verdict (falls back to mismatch_type)")
    ap.add_argument("--output", default="-", help="output JSON path; default stdout")
    args = ap.parse_args()

    leads = load(args.input)
    counts = {}
    for ld in leads:
        verdict = ld.get(args.verdict_field) or ld.get("mismatch_type") or ld.get("verdict", "")
        cat = categorize(verdict)
        ld["handling_category"] = cat
        ld["handling_action"] = ACTIONS[cat]
        ld["referral_target_persona"] = "" if cat != "referral" else "(agent: pick from ICP)"
        counts[cat] = counts.get(cat, 0) + 1

    print("INFO: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())), file=sys.stderr)
    payload = json.dumps(leads, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        open(args.output, "w", encoding="utf-8").write(payload + "\n")
        print(f"{len(leads)} leads tagged -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
