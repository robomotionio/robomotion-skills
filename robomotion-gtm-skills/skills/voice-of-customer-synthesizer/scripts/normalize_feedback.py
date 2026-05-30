#!/usr/bin/env python3
"""normalize_feedback.py — merge scattered feedback sources into one standard-row JSON.

Deterministic I/O only (stdlib, keyless). NO LLM. Reads any combination of feedback CSVs
(support tickets, NPS/CSAT, reviews, churn surveys, feature requests, social mentions,
email threads) plus an optional scraped-reviews JSON, normalizes each into a standard row,
and emits one merged corpus the agent clusters into themes. Sentiment/categorization is the
agent's job (a deterministic keyword pre-tag is added only as a hint).

Each --source is "type=path.csv". CSV headers are matched case-insensitively; the script
looks for: date, customer (or account/company), segment, text (or comment/body/feedback/
review), rating/score, sentiment. Unmatched columns are ignored.

Standard row: {source, type, date, customer, segment, text, rating, sentiment_hint}

Example:
  normalize_feedback.py \
    --source "tickets=tickets.csv" --source "nps=nps.csv" \
    --reviews-json scraped_reviews.json \
    --output corpus.json
"""
import argparse
import csv
import json
import sys

POS = ("love", "great", "excellent", "amazing", "easy", "fast", "helpful", "best",
       "perfect", "fantastic", "intuitive", "recommend", "happy", "awesome")
NEG = ("hate", "terrible", "awful", "slow", "bug", "broken", "confusing", "difficult",
       "frustrating", "frustrated", "worst", "disappointed", "useless", "cancel", "refund",
       "expensive", "crash", "missing", "lacking")


def pick(row, *names):
    for n in names:
        for k, v in row.items():
            if k == n and v:
                return v
    return ""


def sentiment_hint(text, rating):
    if rating is not None:
        try:
            r = float(rating)
            if r >= 4:
                return "positive"
            if r <= 2:
                return "negative"
            return "neutral"
        except (ValueError, TypeError):
            pass
    tl = (text or "").lower()
    pos = sum(1 for w in POS if w in tl)
    neg = sum(1 for w in NEG if w in tl)
    if neg > pos:
        return "negative"
    if pos > neg:
        return "positive"
    return "neutral"


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            yield {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}


def main():
    ap = argparse.ArgumentParser(description="Merge scattered feedback sources into a standard-row corpus.")
    ap.add_argument("--source", action="append", default=[],
                    help='feedback source as "type=path.csv" (repeatable)')
    ap.add_argument("--reviews-json", default="",
                    help="scraped-reviews JSON (from scrape_reviews.py) to merge in")
    ap.add_argument("--output", default="-", help="output corpus JSON (default stdout)")
    args = ap.parse_args()

    if not args.source and not args.reviews_json:
        sys.exit("ERROR: provide at least one --source or --reviews-json.")

    rows = []
    for spec in args.source:
        if "=" not in spec:
            sys.exit(f"ERROR: --source must be 'type=path', got: {spec}")
        typ, _, path = spec.partition("=")
        typ = typ.strip()
        for r in read_csv_rows(path.strip()):
            rating = pick(r, "rating", "score", "nps")
            text = pick(r, "text", "comment", "body", "feedback", "review", "message")
            rating_val = rating if rating != "" else None
            rows.append({
                "source": typ, "type": typ,
                "date": pick(r, "date", "created_at", "timestamp"),
                "customer": pick(r, "customer", "account", "company", "name", "email"),
                "segment": pick(r, "segment", "tier", "plan"),
                "text": text,
                "rating": rating_val,
                "sentiment_hint": sentiment_hint(text, rating_val),
            })

    if args.reviews_json:
        with open(args.reviews_json, encoding="utf-8") as f:
            reviews = json.load(f)
        for rv in reviews if isinstance(reviews, list) else []:
            text = " ".join(x for x in (rv.get("title"), rv.get("body"),
                                        rv.get("pros"), rv.get("cons")) if x)
            rating = rv.get("rating")
            rows.append({
                "source": rv.get("source", "review"), "type": "review",
                "date": rv.get("date", ""),
                "customer": rv.get("reviewer_company", ""),
                "segment": rv.get("reviewer_role", ""),
                "text": text, "rating": rating,
                "sentiment_hint": sentiment_hint(text, rating),
            })

    corpus = {
        "total_items": len(rows),
        "by_source": {s: sum(1 for r in rows if r["source"] == s)
                      for s in sorted({r["source"] for r in rows})},
        "sentiment_hint_distribution": {
            s: sum(1 for r in rows if r["sentiment_hint"] == s)
            for s in ("positive", "neutral", "negative")},
        "items": rows,
    }

    out = json.dumps(corpus, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(rows)} feedback items -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
