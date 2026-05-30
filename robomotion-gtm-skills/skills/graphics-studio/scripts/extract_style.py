#!/usr/bin/env python3
"""extract_style.py — Derive an ad-hoc graphics-studio style from a reference image.

Deterministic tool (no LLM). It samples the reference image's dominant palette via a
small k-means, infers a light/dark theme + the best accent color, picks readable text /
muted roles, and emits a style object matching the styles.json schema. The host agent can
then refine typography/motifs from the same image with vision, but the numeric palette is
produced here so renders are reproducible.

Prefers Pillow (better decoding of JPG/etc.) and falls back to a pure-stdlib PNG decoder
(8-bit non-interlaced RGB/RGBA) so it runs with no pip install on a PNG.

Usage:
  extract_style.py --image ref.png
  extract_style.py --image ref.jpg --id my-brand --name "My Brand" --k 6 --output style.json
"""
import argparse
import json
import math
import random
import struct
import sys
import zlib
from collections import Counter


# ---------------------------------------------------------------------------
# Image loading
# ---------------------------------------------------------------------------
def load_with_pillow(path):
    from PIL import Image  # type: ignore
    im = Image.open(path).convert("RGB")
    im.thumbnail((160, 160))
    return list(im.getdata())


def load_png_stdlib(path):
    """Minimal PNG (8-bit, non-interlaced) RGB/RGBA decoder — stdlib only."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("ERROR: stdlib decoder supports PNG only; install Pillow for other formats.")
    pos = 8
    width = height = bit_depth = color_type = None
    idat = b""
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk[:10])
        elif ctype == b"IDAT":
            idat += chunk
        elif ctype == b"IEND":
            break
        pos += 12 + length
    if bit_depth != 8 or color_type not in (2, 6):
        sys.exit("ERROR: stdlib decoder needs 8-bit RGB/RGBA PNG; install Pillow.")
    channels = 4 if color_type == 6 else 3
    raw = zlib.decompress(idat)
    stride = width * channels
    pixels = []
    prev = bytearray(stride)
    p = 0
    for _ in range(height):
        ftype = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            x = line[i]
            if ftype == 1:
                line[i] = (x + a) & 0xFF
            elif ftype == 2:
                line[i] = (x + b) & 0xFF
            elif ftype == 3:
                line[i] = (x + ((a + b) >> 1)) & 0xFF
            elif ftype == 4:
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (x + pr) & 0xFF
        prev = line
        # subsample for speed
        for i in range(0, stride, channels * 3):
            pixels.append((line[i], line[i + 1], line[i + 2]))
    return pixels


# ---------------------------------------------------------------------------
# Color math
# ---------------------------------------------------------------------------
def luminance(rgb):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgb_to_hsv(rgb):
    r, g, b = (c / 255 for c in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / d) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / d) + 120) % 360
    else:
        h = (60 * ((r - g) / d) + 240) % 360
    s = 0 if mx == 0 else d / mx
    return h, s, mx


def hexs(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(min(255, max(0, int(round(c)))) for c in rgb))


def kmeans(pixels, k, iters=12, seed=42):
    """Tiny deterministic k-means over RGB pixels. Returns [(centroid, weight)]."""
    rng = random.Random(seed)
    # seed centroids from a deterministic spread of distinct pixels
    uniq = list({p for p in pixels})
    if len(uniq) <= k:
        centroids = uniq[:]
    else:
        centroids = rng.sample(uniq, k)
    centroids = [tuple(float(c) for c in cen) for cen in centroids]
    for _ in range(iters):
        buckets = [[] for _ in centroids]
        for px in pixels:
            best, bd = 0, None
            for ci, cen in enumerate(centroids):
                d = (px[0] - cen[0]) ** 2 + (px[1] - cen[1]) ** 2 + (px[2] - cen[2]) ** 2
                if bd is None or d < bd:
                    bd, best = d, ci
            buckets[best].append(px)
        moved = False
        for ci, bucket in enumerate(buckets):
            if not bucket:
                continue
            nc = tuple(sum(c[j] for c in bucket) / len(bucket) for j in range(3))
            if nc != centroids[ci]:
                moved = True
            centroids[ci] = nc
        if not moved:
            break
    weighted = [(centroids[ci], len(buckets[ci])) for ci in range(len(centroids)) if buckets[ci]]
    weighted.sort(key=lambda t: -t[1])
    return weighted


def mix(rgb, target, t):
    return tuple(rgb[i] + (target[i] - rgb[i]) * t for i in range(3))


def build_style(clusters, style_id, name):
    total = sum(w for _, w in clusters) or 1
    ranked = [(tuple(int(round(c)) for c in cen), w / total) for cen, w in clusters]

    bg = ranked[0][0]
    theme = "dark" if luminance(bg) < 0.4 else "light"

    # accent = the most saturated, reasonably distinct cluster (not the bg)
    def accent_score(rgb):
        h, s, v = rgb_to_hsv(rgb)
        return s * (0.5 + 0.5 * v) * (contrast_ratio(rgb, bg) / 5.0)
    candidates = [c for c, _ in ranked[1:]] or [c for c, _ in ranked]
    accent = max(candidates, key=accent_score)

    # text: pick the cluster with best contrast against bg; fall back to pure black/white
    text_candidates = [c for c, _ in ranked]
    best_text = max(text_candidates, key=lambda c: contrast_ratio(c, bg))
    ideal_text = (245, 245, 240) if theme == "dark" else (20, 22, 28)
    text = best_text if contrast_ratio(best_text, bg) >= 5.0 else ideal_text

    # surface: a slight lift/drop from bg
    surface = mix(bg, (255, 255, 255) if theme == "light" else (255, 255, 255), 0.06) \
        if theme == "light" else mix(bg, (255, 255, 255), 0.08)
    # muted: blend of text toward bg
    muted = mix(text, bg, 0.45)
    primary = text

    style = {
        "id": style_id,
        "name": name,
        "aesthetic": f"extracted-from-reference ({theme})",
        "mood_tags": ["custom", "reference-derived", theme],
        "palette": {
            "bg": hexs(bg),
            "surface": hexs(surface),
            "primary": hexs(primary),
            "accent": hexs(accent),
            "text": hexs(text),
            "muted": hexs(muted),
        },
        "typography": {
            "heading_font": "Inter",
            "body_font": "Inter",
            "font_stack": "'Inter', system-ui, -apple-system, sans-serif",
            "scale_ratio": 1.25,
        },
        "radius": "16px",
        "shadow": "0 8px 30px rgba(0,0,0,0.18)" if theme == "dark"
                  else "0 2px 10px rgba(16,24,40,0.10)",
        "spacing_unit": "8px",
        "motifs": "Ad-hoc style derived from a reference image; agent may refine typography "
                  "and decorative motifs with vision while keeping this palette.",
        "_extraction": {
            "theme": theme,
            "palette_ranked": [{"hex": hexs(c), "share": round(s, 4)} for c, s in ranked],
            "accent_contrast_on_bg": round(contrast_ratio(accent, bg), 2),
            "text_contrast_on_bg": round(contrast_ratio(text, bg), 2),
        },
    }
    return style


def main():
    ap = argparse.ArgumentParser(description="Derive an ad-hoc style from a reference image.")
    ap.add_argument("--image", required=True, help="reference image (PNG works keyless; others need Pillow)")
    ap.add_argument("--id", default="ref-style", help="style id slug (default ref-style)")
    ap.add_argument("--name", default="Reference Style", help="human style name")
    ap.add_argument("--k", type=int, default=6, help="number of palette clusters (default 6)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    try:
        pixels = load_with_pillow(args.image)
        backend = "pillow"
    except ImportError:
        pixels = load_png_stdlib(args.image)
        backend = "stdlib-png"
    except FileNotFoundError:
        sys.exit(f"ERROR: image not found: {args.image}")

    if not pixels:
        sys.exit("ERROR: no pixels decoded from image.")

    clusters = kmeans(pixels, max(2, args.k))
    style = build_style(clusters, args.id, args.name)
    style["_extraction"]["backend"] = backend
    style["_extraction"]["pixels_sampled"] = len(pixels)

    payload = json.dumps(style, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"extracted style '{args.id}' ({backend}, {style['_extraction']['theme']}) -> {args.output}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
