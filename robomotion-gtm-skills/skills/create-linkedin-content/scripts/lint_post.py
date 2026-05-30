#!/usr/bin/env python3
"""lint_post.py — Deterministic self-check for a LinkedIn post draft.

Stdlib only. Implements the mechanical half of the `create-linkedin-content` self-check
(the agent does the voice-match / "meat" / press-release-tone judgement). Checks:
banned-phrase substring match, word count (150-500 LinkedIn default), arrow-bullet
convention (presence of -> / → bullets), a "why this matters" beat, hashtag count (0-2),
and at least one concrete token. Reads the post from a file or stdin.

Exit code is 0 always (advisory); the JSON `pass` field is the gate the agent reads.

Examples:
  lint_post.py --file linkedin-a-builder-story.md
  echo "..." | lint_post.py --voice-guide voice-linkedin.md --banned "synergy,circle back"
"""
import argparse
import json
import re
import sys

DEFAULT_BANNED = [
    "game-changer", "game changer", "unlock", "leverage", "supercharge",
    "revolutionize", "seamless", "elevate", "delve", "in today's world",
    "i'm humbled", "i am humbled", "thrilled to announce", "grateful for",
    "needle-moving", "best-in-class", "synergy", "circle back",
    "low-hanging fruit", "without further ado", "dear connections",
]
WORD_MIN, WORD_MAX = 150, 500
WHY_PATTERNS = [
    r"why this matters", r"why it matters", r"here's why", r"the takeaway",
    r"what this means", r"the point", r"bottom line",
]


def read_post(path):
    if not path or path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as f:
        return f.read()


def strip_frontmatter(text):
    if text.startswith("---"):
        m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
        if m:
            return text[m.end():]
    return text


def banned_from_guide(path):
    out = []
    if not path:
        return out
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return out
    m = re.search(r"(?im)^#+\s*banned phrases?.*?$", text)
    if not m:
        return out
    rest = text[m.end():]
    nxt = re.search(r"(?m)^#+\s", rest)
    block = rest[: nxt.start()] if nxt else rest
    for line in block.splitlines():
        line = line.strip().lstrip("-*•").strip().strip('"').strip("'")
        if line:
            out.extend(p.strip() for p in line.split(",") if p.strip())
    return out


def main():
    ap = argparse.ArgumentParser(description="Deterministic self-check for a LinkedIn post draft.")
    ap.add_argument("--file", default="-", help="post file (default stdin)")
    ap.add_argument("--banned", default="", help="comma-separated extra banned phrases")
    ap.add_argument("--voice-guide", default="", help="voice guide file to pull Banned phrases from")
    ap.add_argument("--word-min", type=int, default=WORD_MIN)
    ap.add_argument("--word-max", type=int, default=WORD_MAX)
    ap.add_argument("--max-hashtags", type=int, default=2)
    args = ap.parse_args()

    raw = read_post(args.file)
    post = strip_frontmatter(raw).strip()
    low = post.lower()

    banned = list(DEFAULT_BANNED)
    banned += [b.strip().lower() for b in args.banned.split(",") if b.strip()]
    banned += [b.lower() for b in banned_from_guide(args.voice_guide)]
    banned = sorted(set(banned))
    hits = sorted({b for b in banned if b and b in low})

    word_count = len(re.findall(r"\S+", post))
    length_ok = args.word_min <= word_count <= args.word_max

    has_arrow_bullets = bool(re.search(r"(?m)^\s*(?:->|→|➜|»)\s+\S", post)) or "→" in post or "->" in post
    has_why = any(re.search(p, low) for p in WHY_PATTERNS)
    hashtags = re.findall(r"(?<!\w)#\w+", post)
    has_meat = bool(re.search(r"\d", post)) or "$" in post

    result = {
        "word_count": word_count,
        "length_ok": length_ok,
        "banned_hits": hits,
        "has_arrow_bullets": has_arrow_bullets,
        "has_why_this_matters": has_why,
        "hashtag_count": len(hashtags),
        "hashtags_ok": len(hashtags) <= args.max_hashtags,
        "has_concrete_token": has_meat,
        "pass": (not hits) and length_ok and has_why and (len(hashtags) <= args.max_hashtags),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
