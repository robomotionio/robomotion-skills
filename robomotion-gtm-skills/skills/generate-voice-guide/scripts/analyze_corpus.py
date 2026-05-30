#!/usr/bin/env python3
"""analyze_corpus.py — Deterministic stats over a corpus of a person's posts.

Stdlib only. Feeds the `generate-voice-guide` flow: the AGENT writes the actual guide
(persona, dos/don'ts, hook patterns, annotated examples) — this script supplies the
mechanical evidence it reasons over: post count, length distribution, opener patterns,
emoji/hashtag/link usage, and BANNED-PHRASE CANDIDATES derived from *absence* (cliches the
person never uses), per the contract's "derived from actual absence, not a generic
blocklist" rule.

Input: a JSON array of posts (`[{"text": "...", "is_reply": false, "is_retweet": false,
"engagement": 12, "created_at": "..."}]`) or a plain-text file with posts separated by a
blank line or a `---` line. Replies/retweets/quotes are excluded (original voice only).

Examples:
  analyze_corpus.py --input posts.json --platform x
  analyze_corpus.py --input pasted.txt --platform linkedin
"""
import argparse
import json
import re
import sys
from collections import Counter

# generic AI/marketing cliches; any NOT present in the corpus become ban candidates
CLICHE_BANK = [
    "game-changer", "game changer", "unlock", "leverage", "supercharge",
    "revolutionize", "seamless", "elevate", "delve", "in today's world",
    "i'm humbled", "thrilled to announce", "grateful for", "needle-moving",
    "best-in-class", "synergy", "circle back", "low-hanging fruit",
    "without further ado", "at the end of the day", "move the needle",
    "paradigm shift", "deep dive", "north star", "let that sink in",
    "literally", "it's giving", "the future of", "10x your",
]


def load_posts(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    raw_strip = raw.strip()
    if raw_strip.startswith("[") or raw_strip.startswith("{"):
        data = json.loads(raw_strip)
        if isinstance(data, dict):
            data = data.get("posts", [])
        out = []
        for p in data:
            if isinstance(p, str):
                out.append({"text": p})
            else:
                out.append(p)
        return out
    # plain text: split on blank lines or --- separators
    chunks = re.split(r"\n\s*(?:---+\s*)?\n", raw)
    return [{"text": c.strip()} for c in chunks if c.strip()]


def is_original(p):
    if p.get("is_reply") or p.get("is_retweet") or p.get("is_quote") or p.get("is_reshare"):
        return False
    text = (p.get("text") or "").strip()
    if text.startswith("RT @") or text.startswith("@"):
        return False
    return bool(text)


def opener(text):
    first = text.strip().splitlines()[0] if text.strip() else ""
    words = first.split()
    return " ".join(words[:4]).lower()


def main():
    ap = argparse.ArgumentParser(description="Deterministic corpus stats for voice-guide generation.")
    ap.add_argument("--input", required=True, help="JSON array or plain-text posts file")
    ap.add_argument("--platform", default="x", choices=["x", "linkedin"], help="platform label")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    posts = [p for p in load_posts(args.input) if is_original(p)]
    if not posts:
        sys.exit("ERROR: no original posts found (all empty/replies/retweets?).")

    texts = [(p.get("text") or "").strip() for p in posts]
    lengths = [len(t) for t in texts]
    word_lengths = [len(re.findall(r"\S+", t)) for t in texts]

    corpus_low = "\n".join(texts).lower()
    # banned-phrase candidates: cliches the person NEVER uses
    ban_candidates = [c for c in CLICHE_BANK if c not in corpus_low]

    openers = Counter(opener(t) for t in texts if t)
    emoji_re = re.compile(
        "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]"
    )
    emoji_posts = sum(1 for t in texts if emoji_re.search(t))
    hashtag_posts = sum(1 for t in texts if re.search(r"(?<!\w)#\w+", t))
    link_posts = sum(1 for t in texts if re.search(r"https?://", t))
    question_posts = sum(1 for t in texts if "?" in t)
    list_posts = sum(1 for t in texts if re.search(r"(?m)^\s*(?:[-*•]|\d+[.)]|→|->)\s", t))

    n = len(texts)
    result = {
        "platform": args.platform,
        "post_count": n,
        "length_chars": {
            "min": min(lengths), "max": max(lengths),
            "avg": round(sum(lengths) / n, 1),
        },
        "length_words": {
            "min": min(word_lengths), "max": max(word_lengths),
            "avg": round(sum(word_lengths) / n, 1),
        },
        "usage_rates": {
            "emoji": round(emoji_posts / n, 2),
            "hashtags": round(hashtag_posts / n, 2),
            "links": round(link_posts / n, 2),
            "questions": round(question_posts / n, 2),
            "lists": round(list_posts / n, 2),
        },
        "top_openers": openers.most_common(12),
        "banned_phrase_candidates": ban_candidates,
        "note": ("Stats only. The agent authors the voice guide from these + the raw posts: "
                 "persona, dos/don'ts, 5-8 hook patterns, format rules, 4-6 annotated REAL "
                 "examples (quoted verbatim). Banned-phrase candidates are cliches ABSENT "
                 "from the corpus -- confirm before baking in."),
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"analyzed {n} original posts -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
