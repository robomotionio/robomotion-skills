#!/usr/bin/env python3
"""lint_post.py — Deterministic self-check for an X post draft.

Stdlib only. Implements the mechanical half of the `create-x-content` self-check (the
agent does the voice-match / "meat" judgement). Checks: banned-phrase substring match,
length (short <280 / long-form range), hashtag count, link count, and presence of at least
one concrete token (digit / $ / known tool-ish word). Reads the post from a file or stdin;
banned phrases from --banned (comma list) and/or a voice-guide file's "Banned phrases"
section.

Exit code is 0 always (advisory); the JSON `pass` field is the gate the agent reads.

Examples:
  lint_post.py --file variant-a.md --banned "game-changer,unlock,leverage"
  echo "..." | lint_post.py --voice-guide voice-x.md --format short
"""
import argparse
import json
import re
import sys

DEFAULT_BANNED = [
    "game-changer", "game changer", "unlock", "leverage", "supercharge",
    "revolutionize", "seamless", "elevate", "delve", "in today's world",
    "i'm humbled", "i am humbled", "thrilled to announce", "needle-moving",
    "best-in-class", "synergy", "circle back", "low-hanging fruit",
]
SHORT_MAX = 280
LONGFORM_MIN = 280
LONGFORM_MAX = 4000


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
    # capture a "Banned phrases" section's bullet/comma items until next heading
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
    ap = argparse.ArgumentParser(description="Deterministic self-check for an X post draft.")
    ap.add_argument("--file", default="-", help="post file (default stdin)")
    ap.add_argument("--banned", default="", help="comma-separated extra banned phrases")
    ap.add_argument("--voice-guide", default="", help="voice guide file to pull Banned phrases from")
    ap.add_argument("--format", default="auto", choices=["auto", "short", "long"],
                    help="short (<280) / long (280-4000) / auto-detect")
    ap.add_argument("--max-hashtags", type=int, default=2, help="hashtag ceiling (default 2)")
    args = ap.parse_args()

    raw = read_post(args.file)
    post = strip_frontmatter(raw).strip()
    low = post.lower()

    banned = list(DEFAULT_BANNED)
    banned += [b.strip().lower() for b in args.banned.split(",") if b.strip()]
    banned += [b.lower() for b in banned_from_guide(args.voice_guide)]
    banned = sorted(set(banned))

    hits = sorted({b for b in banned if b and b in low})

    char_count = len(post)
    fmt = args.format
    if fmt == "auto":
        fmt = "long" if char_count > SHORT_MAX else "short"

    length_ok = (char_count <= SHORT_MAX) if fmt == "short" else (LONGFORM_MIN <= char_count <= LONGFORM_MAX)

    hashtags = re.findall(r"(?<!\w)#\w+", post)
    links = re.findall(r"https?://\S+", post)
    has_meat = bool(re.search(r"\d", post)) or "$" in post

    result = {
        "format": fmt,
        "char_count": char_count,
        "length_ok": length_ok,
        "banned_hits": hits,
        "hashtag_count": len(hashtags),
        "hashtags_ok": len(hashtags) <= args.max_hashtags,
        "link_count": len(links),
        "has_concrete_token": has_meat,
        "pass": (not hits) and length_ok and (len(hashtags) <= args.max_hashtags),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
