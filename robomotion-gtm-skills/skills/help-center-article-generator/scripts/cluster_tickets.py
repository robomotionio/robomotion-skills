#!/usr/bin/env python3
"""cluster_tickets.py — Cluster a support-ticket export into ranked topics.

Keyless. Stdlib only. Deterministic glue for `help-center-article-generator` batch mode
step 2: load a ticket CSV (subject/description/resolution), normalize subjects, group
near-duplicate subjects into clusters, rank clusters by frequency, and suggest an article
type per cluster from keyword cues. The AGENT does the LLM clustering refinement + writes
each article; this gives it the frequency-ranked starting point.

CSV columns are auto-detected (subject/title, description/body, resolution/answer).

Examples:
  cluster_tickets.py --input tickets.csv --top 20 --output clusters.json
"""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict

STOPWORDS = set("""a an the to of for and or in on at is are how do i my we our you your can
cannot not with without from this that it when why what where which need help issue problem
error please able unable get got using use used able""".split())

TYPE_CUES = [
    ("troubleshooting", ["error", "not working", "fail", "broken", "can't", "cannot",
                         "won't", "issue", "problem", "fix", "stuck", "crash"]),
    ("getting-started", ["set up", "setup", "get started", "onboard", "install",
                         "sign up", "create account", "first"]),
    ("how-to", ["how to", "how do", "configure", "enable", "change", "add", "connect",
                "export", "import", "integrate"]),
    ("reference", ["what is", "limit", "pricing", "plan", "api", "field", "list of"]),
    ("overview", ["overview", "explain", "difference", "vs", "when to"]),
]


def detect_col(fieldnames, candidates):
    low = {f.lower(): f for f in fieldnames}
    for c in candidates:
        if c in low:
            return low[c]
    for f in fieldnames:
        if any(c in f.lower() for c in candidates):
            return f
    return None


def normalize(s):
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    toks = [t for t in s.split() if t not in STOPWORDS and len(t) > 2]
    return toks


def signature(toks):
    return " ".join(sorted(set(toks))[:5])


def article_type(text):
    low = text.lower()
    for label, cues in TYPE_CUES:
        if any(c in low for c in cues):
            return label
    return "how-to"


def main():
    ap = argparse.ArgumentParser(description="Cluster a support-ticket CSV into ranked topics (keyless).")
    ap.add_argument("--input", required=True, help="ticket export CSV")
    ap.add_argument("--top", type=int, default=20, help="cap on returned clusters (default 20)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            sys.exit("ERROR: empty/headerless CSV.")
        subj_col = detect_col(reader.fieldnames, ["subject", "title", "summary"])
        desc_col = detect_col(reader.fieldnames, ["description", "body", "message", "details"])
        if not subj_col and not desc_col:
            sys.exit("ERROR: could not find a subject/description column.")
        rows = list(reader)

    clusters = defaultdict(lambda: {"count": 0, "examples": [], "tokens": set()})
    for row in rows:
        subject = (row.get(subj_col) or "").strip() if subj_col else ""
        desc = (row.get(desc_col) or "").strip() if desc_col else ""
        text = subject or desc
        if not text:
            continue
        toks = normalize(subject) or normalize(desc)
        if not toks:
            continue
        sig = signature(toks)
        c = clusters[sig]
        c["count"] += 1
        c["tokens"].update(toks)
        if len(c["examples"]) < 4:
            c["examples"].append(text[:160])

    ranked = sorted(clusters.items(), key=lambda kv: kv[1]["count"], reverse=True)[: args.top]
    out_clusters = []
    for i, (sig, c) in enumerate(ranked, 1):
        sample = " ".join(c["examples"])
        out_clusters.append({
            "rank": i,
            "signature": sig,
            "ticket_count": c["count"],
            "suggested_type": article_type(sample),
            "keywords": sorted(c["tokens"])[:12],
            "example_tickets": c["examples"],
        })

    out = {"total_tickets": len(rows), "clusters": out_clusters,
           "columns": {"subject": subj_col, "description": desc_col}}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"{len(out_clusters)} clusters from {len(rows)} tickets -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
