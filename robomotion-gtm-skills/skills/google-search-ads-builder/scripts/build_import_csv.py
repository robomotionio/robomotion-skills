#!/usr/bin/env python3
"""build_import_csv.py — Validate RSA limits and emit a Google Ads Editor import CSV.

Takes the campaign the agent designed (a JSON tree: campaign -> ad groups -> keywords +
RSA copy) and produces:
  1. a strict validation report (headline <=30 chars, description <=90 chars, <=15 headlines
     and <=4 descriptions per RSA, <=15 keywords/ad group) so the import never rejects rows;
  2. a Google Ads Editor-format CSV ready to import.

Deterministic — no LLM. The agent designs the tree; this only validates + serializes.
Stdlib only.

Input JSON shape:
{
  "campaign": "Brand - Search - US",
  "ad_groups": [
    {
      "name": "Workflow Automation",
      "landing_page": "https://x.com/automation",
      "keywords": [{"text":"workflow automation","match":"phrase"}, ...],
      "negatives": ["free","jobs"],
      "rsas": [
        {"headlines": ["...", ...up to 15], "descriptions": ["...", ...up to 4]}
      ]
    }
  ],
  "campaign_negatives": ["careers","login"]
}

Examples:
  build_import_csv.py --input campaign.json --csv google-ads-import.csv --report report.json
"""
import argparse
import csv
import json
import sys

HEADLINE_MAX = 30
DESC_MAX = 90
MAX_HEADLINES = 15
MAX_DESCS = 4
MAX_KW_PER_GROUP = 15

MATCH_MAP = {
    "broad": ("", ""), "phrase": ('"', '"'), "exact": ("[", "]"),
    "": ("", ""),
}


def validate(tree):
    errors, warnings = [], []
    ag_names = set()
    for ag in tree.get("ad_groups", []):
        name = ag.get("name", "")
        if name in ag_names:
            errors.append(f"duplicate ad group name: {name}")
        ag_names.add(name)
        kws = ag.get("keywords", [])
        if len(kws) > MAX_KW_PER_GROUP:
            warnings.append(f"[{name}] {len(kws)} keywords > recommended {MAX_KW_PER_GROUP}; split the group")
        if not ag.get("landing_page"):
            warnings.append(f"[{name}] missing landing_page")
        for rsa_i, rsa in enumerate(ag.get("rsas", [])):
            hs = rsa.get("headlines", [])
            ds = rsa.get("descriptions", [])
            if len(hs) > MAX_HEADLINES:
                errors.append(f"[{name}] RSA#{rsa_i+1} has {len(hs)} headlines > {MAX_HEADLINES}")
            if len(hs) < 3:
                warnings.append(f"[{name}] RSA#{rsa_i+1} has {len(hs)} headlines (<3 is weak)")
            if len(ds) > MAX_DESCS:
                errors.append(f"[{name}] RSA#{rsa_i+1} has {len(ds)} descriptions > {MAX_DESCS}")
            for h in hs:
                if len(h) > HEADLINE_MAX:
                    errors.append(f"[{name}] headline >{HEADLINE_MAX}: {h!r} ({len(h)})")
            for d in ds:
                if len(d) > DESC_MAX:
                    errors.append(f"[{name}] description >{DESC_MAX}: {d!r} ({len(d)})")
    return {"errors": errors, "warnings": warnings, "ok": not errors}


def emit_csv(tree, path):
    # Google Ads Editor accepts a row-per-entity sheet with a shared column superset.
    cols = ["Campaign", "Ad Group", "Keyword", "Match Type", "Criterion Type",
            "Final URL", "Ad type",
            "Headline 1", "Headline 2", "Headline 3", "Headline 4", "Headline 5",
            "Headline 6", "Headline 7", "Headline 8", "Headline 9", "Headline 10",
            "Headline 11", "Headline 12", "Headline 13", "Headline 14", "Headline 15",
            "Description 1", "Description 2", "Description 3", "Description 4"]
    camp = tree.get("campaign", "Search Campaign")
    rows = []

    for neg in tree.get("campaign_negatives", []):
        r = {c: "" for c in cols}
        r.update({"Campaign": camp, "Keyword": neg, "Criterion Type": "Negative",
                  "Match Type": "Broad"})
        rows.append(r)

    for ag in tree.get("ad_groups", []):
        agn = ag.get("name", "")
        lp = ag.get("landing_page", "")
        for kw in ag.get("keywords", []):
            text = kw.get("text", "")
            match = (kw.get("match", "broad") or "broad").lower()
            lq, rq = MATCH_MAP.get(match, ("", ""))
            r = {c: "" for c in cols}
            r.update({"Campaign": camp, "Ad Group": agn,
                      "Keyword": f"{lq}{text}{rq}", "Match Type": match.capitalize(),
                      "Criterion Type": "Keyword"})
            rows.append(r)
        for neg in ag.get("negatives", []):
            r = {c: "" for c in cols}
            r.update({"Campaign": camp, "Ad Group": agn, "Keyword": neg,
                      "Criterion Type": "Negative", "Match Type": "Broad"})
            rows.append(r)
        for rsa in ag.get("rsas", []):
            r = {c: "" for c in cols}
            r.update({"Campaign": camp, "Ad Group": agn, "Ad type": "Responsive search ad",
                      "Final URL": lp})
            for i, h in enumerate(rsa.get("headlines", [])[:MAX_HEADLINES]):
                r[f"Headline {i+1}"] = h
            for i, d in enumerate(rsa.get("descriptions", [])[:MAX_DESCS]):
                r[f"Description {i+1}"] = d
            rows.append(r)

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description="Validate RSA limits + emit Google Ads Editor CSV.")
    ap.add_argument("--input", required=True, help="campaign tree JSON (designed by the agent)")
    ap.add_argument("--csv", default="", help="output CSV path (Google Ads Editor format)")
    ap.add_argument("--report", default="-", help="validation report JSON path (default stdout)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        tree = json.load(f)

    report = validate(tree)
    if args.csv:
        if report["ok"]:
            n = emit_csv(tree, args.csv)
            report["csv_rows"] = n
            report["csv_path"] = args.csv
        else:
            report["csv_path"] = None
            print("Validation FAILED — CSV not written; fix errors first.", file=sys.stderr)

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report == "-":
        print(payload)
    else:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(payload + "\n")

    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
