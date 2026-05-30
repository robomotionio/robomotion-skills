#!/usr/bin/env python3
"""pain_filter.py — pain-vs-solution keyword DISCIPLINE (vendored, no cross-skill imports).

The differentiator of pain-language-engagers: keep posts where someone is LIVING the
problem (buyers), drop posts where someone is SELLING/announcing the solution (vendors,
VCs, builders, recruiters, listicle-spammers). Importable as a module by the engager
scripts AND runnable as a CLI to audit a batch of posts.

A post is KEPT iff:
  1. it matches >=1 pain INCLUDE term (substring, case-insensitive) or the pain regex, AND
  2. it does NOT match any EXCLUDE term (vendor/solution/announce/self-promo/hiring/listicle).
The classifier returns matched_pain_terms[] + (when dropped) the exclude reason — so every
decision is auditable.

Default exclude lexicon (override / extend via --exclude-file or extra_excludes):
  announcements / launches / self-promo / hiring / award-brag / listicle / thought-leader
  CTA spam — the language of people SELLING, not SUFFERING.

CLI:
  # classify a JSON array of posts ([{text|postContent, url}]) -> keep/drop with reasons
  pain_filter.py --posts posts.json \
      --pain-terms "manual data entry,copy paste between systems,spreadsheet hell" \
      --pain-regex "still (doing|using).*(manually|by hand)" --output classified.json

  # self-test (ships a known pain post + a known announcement post)
  pain_filter.py --selftest
"""
import argparse
import json
import re
import sys

# --- default exclude lexicon: the language of SOLUTION-SELLERS, not problem-HAVERS -------
DEFAULT_EXCLUDES = [
    # launch / announcement
    "excited to announce", "thrilled to announce", "happy to announce", "proud to announce",
    "pleased to announce", "we just launched", "just launched", "now live", "introducing",
    "we're launching", "we are launching", "launching today", "big news", "announcing",
    "general availability", "now available", "early access", "join the waitlist",
    "product update", "release notes", "changelog", "v2.0", "now in beta", "public beta",
    # self-promo / vendor brag
    "proud to", "honored to", "humbled to", "grateful to share", "delighted to share",
    "check out our", "try our", "book a demo", "request a demo", "get a demo",
    "sign up now", "sign up here", "link in comments", "link in bio", "dm me to",
    "dm for", "comment below and i", "our platform", "our solution", "our product",
    "our tool helps", "we help companies", "we help teams", "helping companies",
    # award / vanity
    "named a leader", "recognized as", "award", "g2 leader", "forbes", "top 10",
    "we won", "we're #1", "ranked #", "fastest growing",
    # hiring / recruiting
    "we're hiring", "we are hiring", "now hiring", "join our team", "open role",
    "open position", "apply now", "job opening", "we're looking for a",
    # listicle / generic thought-leadership spam
    "here are 10", "here are 5", "here are 7", "10 ways", "5 ways", "7 ways",
    "thread 🧵", "a thread", "lessons learned from", "my top tips", "hot take:",
    "unpopular opinion", "agree?", "thoughts?", "repost if",
    # funding / corp news (not a buyer in pain)
    "raised our", "raised a", "series a", "series b", "closed our round", "funding round",
    "acquired by", "we acquired", "partnership with", "proud partner",
]

# Substrings that, if a post matches an exclude but ALSO clearly voices a complaint,
# rescue it (a buyer venting can still say "demo" etc.). Pain wins ties only via regex/terms,
# so we keep this conservative: an explicit first-person frustration cue.
FRUSTRATION_CUES = [
    "i'm so tired of", "i am so tired of", "so frustrated", "frustrating",
    "drives me crazy", "driving me crazy", "pain in the", "nightmare", "hate that",
    "i hate", "why is it still", "why do i still", "can't believe i still",
    "wasting hours", "wasting time", "waste of time", "fed up", "sick of",
]


def _norm_terms(terms):
    out = []
    for t in terms or []:
        t = (t or "").strip().lower()
        if t:
            out.append(t)
    return out


def classify_post(text, pain_terms, exclude_terms=None, pain_regex=None,
                  frustration_cues=None):
    """Classify one post's text. Returns dict:
       {keep: bool, matched_pain_terms: [...], reason: str}
    pain_regex may be a compiled pattern, a string, or None.
    """
    t = (text or "").lower()
    pain_terms = _norm_terms(pain_terms)
    exclude_terms = _norm_terms(exclude_terms if exclude_terms is not None else DEFAULT_EXCLUDES)
    cues = _norm_terms(frustration_cues if frustration_cues is not None else FRUSTRATION_CUES)

    if isinstance(pain_regex, str) and pain_regex:
        pain_regex = re.compile(pain_regex, re.I)

    matched = [p for p in pain_terms if p in t]
    regex_hit = bool(pain_regex.search(t)) if pain_regex else False
    has_pain = bool(matched) or regex_hit
    if regex_hit and "(regex)" not in matched:
        matched = matched + ["(regex)"]

    if not has_pain:
        return {"keep": False, "matched_pain_terms": [], "reason": "no_pain_match"}

    hit_excludes = [x for x in exclude_terms if x in t]
    if hit_excludes:
        # rescue only if an explicit first-person frustration cue is present
        if any(c in t for c in cues):
            return {"keep": True, "matched_pain_terms": matched,
                    "reason": f"pain_with_frustration_cue (overrode: {hit_excludes[0]})"}
        return {"keep": False, "matched_pain_terms": matched,
                "reason": f"excluded:{hit_excludes[0]}"}

    return {"keep": True, "matched_pain_terms": matched, "reason": "pain_match"}


def post_text(p):
    """Pull text out of a post dict regardless of source actor's field naming."""
    if isinstance(p, str):
        return p
    for k in ("text", "postContent", "content", "commentary", "summary", "description"):
        v = p.get(k)
        if v:
            return v
    return ""


def post_url(p):
    if isinstance(p, dict):
        for k in ("postUrl", "url", "postLink", "link", "shareUrl"):
            if p.get(k):
                return p[k]
    return ""


def load_lines(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


def selftest():
    pain_terms = ["manual data entry", "copy paste between systems", "spreadsheet hell"]
    pain_post = ("Honestly fed up with manual data entry — I spend hours every week doing "
                 "copy paste between systems. There has to be a better way.")
    announce_post = ("Excited to announce we just launched our new automation platform that "
                     "kills manual data entry forever! Book a demo, link in comments.")
    a = classify_post(pain_post, pain_terms)
    b = classify_post(announce_post, pain_terms)
    print("PAIN  post ->", json.dumps(a))
    print("ANNCE post ->", json.dumps(b))
    ok = a["keep"] is True and b["keep"] is False
    print("SELFTEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Pain-vs-solution post filter (auditable).")
    ap.add_argument("--posts", help="JSON array of posts ([{text|postContent,url}] or [str])")
    ap.add_argument("--pain-terms", default="", help="comma-separated pain include terms")
    ap.add_argument("--pain-terms-file", default="", help="file: one pain term per line")
    ap.add_argument("--pain-regex", default="", help="optional pain pattern (Python regex)")
    ap.add_argument("--exclude-file", default="",
                    help="file: one extra exclude term per line (extends defaults)")
    ap.add_argument("--no-default-excludes", action="store_true",
                    help="use ONLY --exclude-file terms (drop the built-in lexicon)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    ap.add_argument("--selftest", action="store_true", help="run built-in pass/fail test")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if not args.posts:
        ap.error("--posts is required (or use --selftest)")

    pain_terms = [t.strip() for t in args.pain_terms.split(",") if t.strip()]
    pain_terms += load_lines(args.pain_terms_file) or []
    excludes = [] if args.no_default_excludes else list(DEFAULT_EXCLUDES)
    excludes += load_lines(args.exclude_file) or []

    with open(args.posts, encoding="utf-8") as f:
        posts = json.load(f)

    rx = re.compile(args.pain_regex, re.I) if args.pain_regex else None
    kept, dropped = [], []
    for p in posts:
        res = classify_post(post_text(p), pain_terms, excludes, rx)
        row = {"url": post_url(p), "text": post_text(p)[:280],
               "matched_pain_terms": res["matched_pain_terms"], "reason": res["reason"]}
        (kept if res["keep"] else dropped).append(row)

    out = {"kept": kept, "dropped": dropped,
           "summary": {"in": len(posts), "kept": len(kept), "dropped": len(dropped)}}
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"kept {len(kept)} / dropped {len(dropped)} of {len(posts)} -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
