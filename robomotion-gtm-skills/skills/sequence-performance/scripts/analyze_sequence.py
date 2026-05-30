#!/usr/bin/env python3
"""analyze_sequence.py — deterministic sequence metrics, segment benchmarks, reply-category
normalization, and copy-grading signal extraction.

NO LLM. Reads a campaign bundle (from fetch_campaign.py) and computes:
  - overall + per-touch + per-variant open/reply/positive/bounce rates
  - marginal reply contribution per touch
  - a variant statistical-confidence label (by sample size)
  - vs-benchmark deltas against a passed-in benchmark AND a built-in per-segment reference
    table (SMB / MidMarket / Enterprise, cold vs warm) so the agent has an objective bar
  - a reply-category taxonomy normalizer (positive / out_of_office / referral / unsubscribe
    / objection / not_now / other) over any pre-tagged reply categories present in the bundle
  - copy-grading SIGNALS per touch/variant: subject length, CTA presence, personalization
    token count, word count, question/spam-trigger flags

The host agent still does the qualitative work: reading each reply to refine classification,
grading copy A-F, judging lead quality, and writing recommendations. This script only
extracts deterministic signals.

Confidence by sample size (sends): <50 insufficient, 50-149 low, 150-249 moderate,
250+ significant.

Example:
  analyze_sequence.py --bundle bundle.json --outreach-type cold --segment SMB \
     --benchmark-reply-rate 0.03 --benchmark-open-rate 0.40 --output metrics.json
"""
import argparse
import json
import re
import sys

# ---- Built-in per-segment reference benchmarks (industry-typical cold-email rates) -------
# Conservative, widely-cited cold-outbound ranges; warm rows reflect opted-in / nurture.
# rate keys: open, reply, positive (positive-reply rate), bounce_ceiling.
SEGMENT_BENCHMARKS = {
    ("smb", "cold"):        {"open": 0.45, "reply": 0.05, "positive": 0.015, "bounce_ceiling": 0.03},
    ("smb", "warm"):        {"open": 0.55, "reply": 0.12, "positive": 0.05,  "bounce_ceiling": 0.02},
    ("midmarket", "cold"):  {"open": 0.40, "reply": 0.035, "positive": 0.012, "bounce_ceiling": 0.03},
    ("midmarket", "warm"):  {"open": 0.50, "reply": 0.10, "positive": 0.04,  "bounce_ceiling": 0.02},
    ("enterprise", "cold"): {"open": 0.35, "reply": 0.025, "positive": 0.008, "bounce_ceiling": 0.03},
    ("enterprise", "warm"): {"open": 0.45, "reply": 0.08, "positive": 0.03,  "bounce_ceiling": 0.02},
}

# ---- Reply-category taxonomy: canonical buckets + the raw labels that map into them -------
REPLY_TAXONOMY = {
    "positive":      ("positive", "interested", "meeting", "demo", "booked", "call", "yes", "warm"),
    "out_of_office": ("ooo", "out of office", "out-of-office", "auto", "autoreply", "vacation", "away"),
    "referral":      ("referral", "refer", "forwarded", "wrong person", "right person", "redirect"),
    "unsubscribe":   ("unsubscribe", "opt out", "opt-out", "remove", "stop", "do not contact", "gdpr"),
    "objection":     ("objection", "not relevant", "irrelevant", "budget", "price", "competitor",
                      "already have", "using", "no need", "spam", "complaint"),
    "not_now":       ("not now", "later", "next quarter", "circle back", "timing", "follow up", "q3", "q4"),
}

CTA_PATTERNS = (r"\?$", r"are you (free|available|open)", r"do you have", r"worth a",
                r"\b15[- ]min", r"\b30[- ]min", r"book a", r"grab (a|some) time",
                r"how (does|about)", r"would you be", r"open to", r"can we", r"let'?s",
                r"reply", r"calendar", r"schedule", r"hop on", r"chat", r"connect")
PERSONALIZATION_TOKENS = (r"\{\{[^}]+\}\}", r"\{[a-z_]+\}", r"\[[A-Za-z_ ]+\]",
                          r"%[a-z_]+%", r"\bfirst[_ ]?name\b", r"\bcompany\b")
SPAM_TRIGGERS = ("free", "guarantee", "guaranteed", "act now", "limited time", "click here",
                 "buy now", "100%", "risk-free", "cash", "$$$", "winner", "urgent",
                 "no obligation", "amazing", "cheap", "discount")


def rate(num, den):
    return round(num / den, 4) if den else None


def confidence(sends):
    if sends < 50:
        return "insufficient"
    if sends < 150:
        return "low"
    if sends < 250:
        return "moderate"
    return "significant"


def normalize_reply_category(raw):
    """Map a raw/pre-tagged reply category string to a canonical taxonomy bucket."""
    r = (raw or "").strip().lower()
    if not r:
        return "other"
    for canon, needles in REPLY_TAXONOMY.items():
        if any(n in r for n in needles):
            return canon
    return "other"


def grade_copy(subject, body):
    """Deterministic copy SIGNALS (not a letter grade — the agent grades). All keyless regex."""
    subject = subject or ""
    body = body or ""
    blob = (subject + " " + body)
    blob_l = blob.lower()
    word_count = len(re.findall(r"\b\w+\b", body))
    subj_words = len(re.findall(r"\b\w+\b", subject))
    cta = any(re.search(p, blob_l) for p in CTA_PATTERNS)
    pers = sum(len(re.findall(p, blob, flags=re.IGNORECASE)) for p in PERSONALIZATION_TOKENS)
    spam = [t for t in SPAM_TRIGGERS if t in blob_l]
    return {
        "subject_char_len": len(subject),
        "subject_word_len": subj_words,
        "subject_in_ideal_range": 3 <= subj_words <= 7,   # short subjects win in cold outbound
        "body_word_count": word_count,
        "body_in_ideal_range": 50 <= word_count <= 125,    # concise cold body
        "has_cta": cta,
        "personalization_token_count": pers,
        "has_personalization": pers > 0,
        "question_count": blob.count("?"),
        "spam_trigger_hits": spam,
        "spam_trigger_count": len(spam),
    }


def main():
    ap = argparse.ArgumentParser(description="Deterministic sequence rates, segment benchmarks, "
                                             "reply taxonomy + copy signals.")
    ap.add_argument("--bundle", required=True, help="campaign bundle JSON from fetch_campaign.py")
    ap.add_argument("--outreach-type", default="cold", choices=["cold", "warm"])
    ap.add_argument("--segment", default="", choices=["", "SMB", "MidMarket", "Enterprise"],
                    help="ICP segment for the built-in benchmark comparison")
    ap.add_argument("--benchmark-reply-rate", type=float, default=0.03)
    ap.add_argument("--benchmark-open-rate", type=float, default=0.40)
    ap.add_argument("--benchmark-bounce-rate", type=float, default=0.03)
    ap.add_argument("--output", default="-", help="output metrics JSON (default stdout)")
    args = ap.parse_args()

    with open(args.bundle, encoding="utf-8") as f:
        bundle = json.load(f)
    m = bundle.get("metrics", {})
    sends = m.get("sends", 0)
    opens = m.get("opens", 0)
    replies = m.get("replies", 0)
    bounces = m.get("bounces", 0)
    positives = m.get("positive_replies", m.get("positives", 0))

    overall = {
        "sends": sends, "opens": opens, "replies": replies, "positive_replies": positives,
        "bounces": bounces,
        "open_rate": rate(opens, sends),
        "reply_rate": rate(replies, sends),
        "positive_rate": rate(positives, sends),
        "positive_of_replies": rate(positives, replies),
        "bounce_rate": rate(bounces, sends),
        "confidence": confidence(sends),
    }
    overall["reply_rate_vs_benchmark"] = (
        None if overall["reply_rate"] is None
        else round(overall["reply_rate"] - args.benchmark_reply_rate, 4))
    overall["open_rate_vs_benchmark"] = (
        None if overall["open_rate"] is None
        else round(overall["open_rate"] - args.benchmark_open_rate, 4))
    overall["bounce_flag"] = (overall["bounce_rate"] is not None
                              and overall["bounce_rate"] > args.benchmark_bounce_rate)

    # ---- per-segment built-in benchmark comparison ----
    segment_comparison = None
    if args.segment:
        ref = SEGMENT_BENCHMARKS.get((args.segment.lower(), args.outreach_type))
        if ref:
            def delta(actual, bench):
                return None if actual is None else round(actual - bench, 4)
            segment_comparison = {
                "segment": args.segment,
                "outreach_type": args.outreach_type,
                "reference": ref,
                "open_rate_vs_segment": delta(overall["open_rate"], ref["open"]),
                "reply_rate_vs_segment": delta(overall["reply_rate"], ref["reply"]),
                "positive_rate_vs_segment": delta(overall["positive_rate"], ref["positive"]),
                "bounce_over_ceiling": (overall["bounce_rate"] is not None
                                        and overall["bounce_rate"] > ref["bounce_ceiling"]),
                "open_verdict": _verdict(overall["open_rate"], ref["open"]),
                "reply_verdict": _verdict(overall["reply_rate"], ref["reply"]),
            }

    def block(rows, label):
        out = []
        total_replies = sum(r.get("replies", 0) for r in rows) or 0
        for r in rows:
            s = r.get("sends", 0)
            rep = r.get("replies", 0)
            pos = r.get("positive_replies", r.get("positives", 0))
            out.append({
                label: r.get(label, ""),
                "sends": s, "opens": r.get("opens", 0), "replies": rep,
                "positive_replies": pos, "bounces": r.get("bounces", 0),
                "open_rate": rate(r.get("opens", 0), s),
                "reply_rate": rate(rep, s),
                "positive_rate": rate(pos, s),
                "marginal_reply_share": rate(rep, total_replies) if total_replies else None,
                "confidence": confidence(s),
            })
        return out

    per_touch = block(m.get("by_touch", []), "touch")
    per_variant = block(m.get("by_variant", []), "variant")

    # ---- reply-category taxonomy normalization ----
    # Counts any pre-tagged category on each reply (bundle.replies[i].category) into canon
    # buckets; the agent refines from raw text but this gives a deterministic skeleton.
    reply_taxonomy = {k: 0 for k in list(REPLY_TAXONOMY) + ["other"]}
    tagged_replies = 0
    for rep in bundle.get("replies", []):
        cat = rep.get("category") or rep.get("label") or rep.get("type")
        if cat:
            tagged_replies += 1
            reply_taxonomy[normalize_reply_category(cat)] += 1
    total_tagged = sum(reply_taxonomy.values())
    reply_taxonomy_pct = ({k: rate(v, total_tagged) for k, v in reply_taxonomy.items()}
                          if total_tagged else None)

    # ---- copy-grading signals per copy entry ----
    copy_signals = []
    for c in bundle.get("copy", []):
        sig = grade_copy(c.get("subject", ""), c.get("body", ""))
        sig["touch"] = c.get("touch", "")
        sig["variant"] = c.get("variant", "")
        copy_signals.append(sig)

    metrics = {
        "campaign": bundle.get("campaign", ""),
        "outreach_type": args.outreach_type,
        "segment": args.segment or None,
        "overall": overall,
        "segment_comparison": segment_comparison,
        "per_touch": per_touch,
        "per_variant": per_variant,
        "reply_taxonomy": {
            "tagged_replies": tagged_replies,
            "counts": reply_taxonomy if total_tagged else None,
            "pct": reply_taxonomy_pct,
        },
        "copy_signals": copy_signals,
        "reply_count_available": len(bundle.get("replies", [])),
        "copy_touches_available": len(bundle.get("copy", [])),
        "data_quality": {
            "has_open_tracking": opens > 0,
            "has_variant_data": bool(per_variant),
            "has_touch_data": bool(per_touch),
            "has_reply_text": bool(bundle.get("replies")),
            "has_positive_tracking": positives > 0,
            "has_tagged_reply_categories": tagged_replies > 0,
            "has_copy": bool(copy_signals),
        },
    }

    out = json.dumps(metrics, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"sequence metrics -> {args.output}", file=sys.stderr)


def _verdict(actual, bench):
    if actual is None:
        return None
    if actual >= bench * 1.2:
        return "above"
    if actual >= bench * 0.8:
        return "at"
    return "below"


if __name__ == "__main__":
    main()
