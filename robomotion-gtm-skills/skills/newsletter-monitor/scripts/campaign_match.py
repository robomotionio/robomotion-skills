#!/usr/bin/env python3
"""campaign_match.py — Extract buying signals from fetched newsletter messages by keyword
campaign: matched keywords, 200-char context snippets, and nearby company names.

Reads the JSON array produced by imap_fetch.py, case-insensitively substring-matches each
campaign's keywords against the message body, captures a 200-char window around each match,
and heuristically detects nearby company names (capitalized multi-word phrases). Keeps only
messages with >=1 match. Deterministic — the host agent does any digest synthesis. Stdlib only.

Built-in campaigns: acquisitions, sage_intacct, staffing, technology. Override with
--keywords (a single ad-hoc campaign) or --campaigns-file (JSON: [{name,description,keywords[]}]).

Implements step 3-6 of the robomotion-gtm-skills `newsletter-monitor` contract.

Examples:
  campaign_match.py --input ${WORKSPACE}/messages.json --output summary
  campaign_match.py --input msgs.json --campaign acquisitions
  campaign_match.py --input msgs.json --keywords "merger,acquired,acquisition"
"""
import argparse
import json
import re
import sys

BUILTIN = {
    "acquisitions": {
        "description": "M&A / acquisition signals",
        "keywords": ["acquisition", "acquired", "acquires", "merger", "merges",
                     "buyout", "takeover", "to acquire"],
    },
    "sage_intacct": {
        "description": "Sage Intacct migrations / adoption",
        "keywords": ["sage intacct", "intacct migration", "moving to sage",
                     "intacct implementation", "netsuite to intacct"],
    },
    "staffing": {
        "description": "Hiring / staffing changes",
        "keywords": ["hiring", "new hire", "appointed", "joins as", "promoted to",
                     "expands team", "headcount", "layoff", "laid off"],
    },
    "technology": {
        "description": "Technology adoption",
        "keywords": ["implemented", "adopted", "rolled out", "migrated to",
                     "deployed", "selected", "go-live", "digital transformation"],
    },
}

COMPANY_RE = re.compile(r"\b(?:[A-Z][A-Za-z0-9&.'-]+(?:\s+[A-Z][A-Za-z0-9&.'-]+){0,3})"
                        r"(?:\s+(?:Inc|LLC|Ltd|Corp|Corporation|Group|Holdings|Co|Company|Partners|Technologies|Solutions|Systems))?\b")
STOP = {"The", "This", "That", "We", "Our", "You", "Your", "They", "It", "In", "On",
        "For", "And", "But", "With", "As", "To", "Of", "At", "By", "From", "A", "An"}


def load_campaigns(args):
    if args.keywords:
        return {"custom": {"description": "ad-hoc keyword set",
                           "keywords": [k.strip() for k in args.keywords.split(",") if k.strip()]}}
    if args.campaigns_file:
        with open(args.campaigns_file, encoding="utf-8") as f:
            arr = json.load(f)
        return {c["name"]: {"description": c.get("description", ""),
                            "keywords": c.get("keywords", [])} for c in arr}
    if args.campaign:
        if args.campaign not in BUILTIN:
            sys.exit(f"ERROR: unknown campaign '{args.campaign}'. Built-ins: {', '.join(BUILTIN)}")
        return {args.campaign: BUILTIN[args.campaign]}
    return dict(BUILTIN)


def find_companies(window):
    out = []
    for m in COMPANY_RE.finditer(window):
        phrase = m.group(0).strip()
        words = phrase.split()
        if len(words) < 2:
            continue
        if words[0] in STOP:
            phrase = " ".join(words[1:])
            words = words[1:]
        if len(words) >= 2 and phrase not in out:
            out.append(phrase)
    return out[:5]


def scan_message(msg, campaigns):
    body = msg.get("body", "") or ""
    low = body.lower()
    matched_campaigns, matched_keywords, snippets, companies = [], [], [], []
    for cname, cdef in campaigns.items():
        hit = False
        for kw in cdef["keywords"]:
            k = kw.lower()
            idx = low.find(k)
            while idx != -1:
                hit = True
                if kw not in matched_keywords:
                    matched_keywords.append(kw)
                start = max(0, idx - 100)
                end = min(len(body), idx + len(kw) + 100)
                window = body[start:end].replace("\n", " ").strip()
                snippets.append({"campaign": cname, "keyword": kw, "context": window})
                for c in find_companies(window):
                    if c not in companies:
                        companies.append(c)
                idx = low.find(k, idx + len(k))
        if hit:
            matched_campaigns.append(cname)
    if not matched_campaigns:
        return None
    return {
        "message_id": msg.get("message_id", ""),
        "from": msg.get("from", ""),
        "subject": msg.get("subject", ""),
        "date": msg.get("date", ""),
        "matched_campaigns": matched_campaigns,
        "matched_keywords": matched_keywords,
        "context_snippets": snippets[:20],
        "companies_mentioned": companies[:15],
    }


def main():
    ap = argparse.ArgumentParser(description="Match newsletter messages against keyword campaigns.")
    ap.add_argument("--input", required=True, help="JSON array from imap_fetch.py (or - for stdin)")
    ap.add_argument("--campaign", default="", help="run a single built-in campaign")
    ap.add_argument("--keywords", default="", help="ad-hoc comma-separated keywords (overrides campaigns)")
    ap.add_argument("--campaigns-file", default="", help="JSON file of custom campaign defs")
    ap.add_argument("--output", default="json", choices=["json", "summary"])
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    messages = json.loads(raw)
    campaigns = load_campaigns(args)

    results = []
    for msg in messages:
        r = scan_message(msg, campaigns)
        if r:
            results.append(r)

    if args.output == "summary":
        if not results:
            print("No newsletter signals matched.")
            return
        by_campaign = {}
        for r in results:
            for c in r["matched_campaigns"]:
                by_campaign.setdefault(c, []).append(r)
        for cname, rows in by_campaign.items():
            print(f"\n== {cname} ({len(rows)} messages) ==")
            for r in rows:
                print(f"  • {r['subject']}  ({r['from']}, {r['date']})")
                print(f"    keywords: {', '.join(r['matched_keywords'])}")
                if r["companies_mentioned"]:
                    print(f"    companies: {', '.join(r['companies_mentioned'])}")
    else:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
