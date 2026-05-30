#!/usr/bin/env python3
"""source_images.py — Imagery sourcing for graphics-studio.

Three deterministic modes (no LLM):
  1. Unsplash API search    (when UNSPLASH_ACCESS_KEY is set) — real, attributed photos.
  2. Keyless seeded fallback (always works) — deterministic URLs from picsum.photos
     (seeded so the same query/index returns the same image) for stock-style filler.
  3. ASCII art (--ascii TERM) — deterministic block/line ASCII decor, written as text.

Photos are downloaded into an assets dir and local paths are printed (JSON) so the agent
can embed them with relative <img src> in the HTML it authors. If a download fails (e.g.
offline), the remote URL is still reported so the HTML can reference it directly.

Usage:
  source_images.py --query "mountain sunrise" --count 3 --out-dir assets
  source_images.py --query "startup office" --count 2 --width 1080 --height 1350
  source_images.py --ascii rocket --out-dir assets
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request


UNSPLASH_API = "https://api.unsplash.com/search/photos"


def http_json(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def download(url, dest, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "graphics-studio/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def seed_of(query, i):
    h = hashlib.sha1(f"{query}:{i}".encode("utf-8")).hexdigest()[:12]
    return h


def unsplash_search(query, count, key, w, h):
    url = UNSPLASH_API + "?" + urllib.parse.urlencode({
        "query": query, "per_page": count, "orientation": "portrait" if h > w else "landscape"})
    data = http_json(url, headers={"Authorization": f"Client-ID {key}",
                                   "Accept-Version": "v1"})
    results = []
    for item in data.get("results", [])[:count]:
        raw = item["urls"]["raw"]
        sized = raw + ("&" if "?" in raw else "?") + urllib.parse.urlencode(
            {"w": w, "h": h, "fit": "crop", "q": "80"})
        results.append({
            "url": sized,
            "credit": f'Photo by {item["user"]["name"]} on Unsplash',
            "credit_url": item["user"]["links"]["html"],
            "alt": item.get("alt_description") or query,
        })
    return results


def keyless_fallback(query, count, w, h):
    """Deterministic seeded picsum URLs — keyless stock-style filler."""
    out = []
    for i in range(count):
        seed = seed_of(query, i)
        out.append({
            "url": f"https://picsum.photos/seed/{seed}/{w}/{h}",
            "credit": "Lorem Picsum (placeholder)",
            "credit_url": "https://picsum.photos",
            "alt": f"{query} (placeholder {i + 1})",
        })
    return out


# --- ASCII art (deterministic, no deps) ------------------------------------
def ascii_banner(term):
    """Render TERM as a simple deterministic block banner using a 5-row mini font."""
    FONT = {
        " ": ["     "] * 5,
        "default": ["#### ", "#  # ", "#  # ", "#  # ", "#### "],
    }
    rows = ["", "", "", "", ""]
    for ch in term.upper():
        glyph = FONT.get(ch, FONT["default"]) if ch != " " else FONT[" "]
        for r in range(5):
            rows[r] += glyph[r] + " "
    border = "+" + "-" * (len(rows[0]) + 2) + "+"
    body = "\n".join("| " + r + " |" for r in rows)
    return border + "\n" + body + "\n" + border


def ascii_motif(term):
    """A small deterministic decorative motif keyed off the term hash."""
    h = int(hashlib.sha1(term.encode("utf-8")).hexdigest(), 16)
    palette = ["·", "•", "◦", "*", "+", "×", "○", "▪", "◆", "△"]
    rows = []
    for y in range(6):
        line = ""
        for x in range(24):
            v = (h >> ((x + y) % 32)) & 0x7
            line += palette[(v + x + y) % len(palette)] if (h >> (x % 16)) & 1 else " "
        rows.append(line)
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser(description="Source imagery (Unsplash/keyless) or ASCII art.")
    ap.add_argument("--query", help="photo search query")
    ap.add_argument("--ascii", dest="ascii_term", help="render TERM as deterministic ASCII art")
    ap.add_argument("--count", type=int, default=3, help="number of photos (default 3)")
    ap.add_argument("--width", type=int, default=1080, help="target width (default 1080)")
    ap.add_argument("--height", type=int, default=1350, help="target height (default 1350)")
    ap.add_argument("--out-dir", default="assets", help="download/asset dir (default assets)")
    ap.add_argument("--no-download", action="store_true", help="report URLs only, don't fetch")
    ap.add_argument("--output", default="-", help="manifest JSON path (default stdout)")
    args = ap.parse_args()

    if not args.query and not args.ascii_term:
        ap.error("provide --query (photos) and/or --ascii TERM")

    os.makedirs(args.out_dir, exist_ok=True)
    manifest = {"out_dir": args.out_dir, "photos": [], "ascii": None}

    if args.ascii_term:
        art = ascii_banner(args.ascii_term) + "\n\n" + ascii_motif(args.ascii_term)
        path = os.path.join(args.out_dir, f"ascii_{args.ascii_term}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(art + "\n")
        manifest["ascii"] = {"term": args.ascii_term, "path": path}

    if args.query:
        key = os.environ.get("UNSPLASH_ACCESS_KEY")
        source = "unsplash" if key else "keyless-picsum"
        try:
            photos = (unsplash_search(args.query, args.count, key, args.width, args.height)
                      if key else keyless_fallback(args.query, args.count, args.width, args.height))
        except Exception as e:  # network/API failure -> degrade to keyless
            print(f"WARN: {source} failed ({e}); using keyless fallback.", file=sys.stderr)
            source = "keyless-picsum"
            photos = keyless_fallback(args.query, args.count, args.width, args.height)

        manifest["source"] = source
        for i, ph in enumerate(photos):
            local = None
            if not args.no_download:
                dest = os.path.join(args.out_dir, f"img_{seed_of(args.query, i)}.jpg")
                try:
                    download(ph["url"], dest)
                    local = dest
                except Exception as e:
                    print(f"WARN: download failed for {ph['url']} ({e}); HTML can use the URL.",
                          file=sys.stderr)
            manifest["photos"].append({**ph, "local_path": local})

    payload = json.dumps(manifest, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        n = len(manifest["photos"])
        print(f"sourced {n} photo(s){' + ascii' if manifest['ascii'] else ''} -> {args.out_dir}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
