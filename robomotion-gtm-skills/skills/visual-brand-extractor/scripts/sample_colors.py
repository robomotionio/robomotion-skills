#!/usr/bin/env python3
"""sample_colors.py — Extract the dominant colors from a hero screenshot as a numeric
cross-check for the brand palette (resolves ties / confirms accent + theme type).

Deterministic tool only. It returns ranked dominant colors + an inferred theme type
(dark/light) from background luminance; the host agent decides final color ROLES
(bg/text/accent/card) using these numbers plus the CSS signals from extract_brand.mjs.

Prefers Pillow (better quantization) but falls back to a pure-stdlib PNG decoder so it
runs with no pip install when given a PNG (the screenshot extract_brand.mjs writes).

Example:
  sample_colors.py --image hero.png --num-colors 8 --output palette.json
"""
import argparse
import json
import struct
import sys
import zlib
from collections import Counter


def load_with_pillow(path):
    from PIL import Image  # type: ignore
    im = Image.open(path).convert("RGB")
    im.thumbnail((200, 200))
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
        # undo PNG row filters
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
        # subsample to keep it fast (every other pixel)
        for i in range(0, stride, channels * 2):
            pixels.append((line[i], line[i + 1], line[i + 2]))
    return pixels


def quantize(rgb, step=24):
    return tuple((c // step) * step + step // 2 for c in rgb)


def luminance(rgb):
    r, g, b = (c / 255 for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def hexs(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(min(255, max(0, c)) for c in rgb))


def main():
    ap = argparse.ArgumentParser(
        description="Extract ranked dominant colors + theme type from a hero screenshot.")
    ap.add_argument("--image", required=True, help="path to hero screenshot (PNG preferred)")
    ap.add_argument("--num-colors", type=int, default=8, help="how many dominant colors (default 8)")
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

    counter = Counter(quantize(px) for px in pixels)
    total = sum(counter.values())
    ranked = [{
        "hex": hexs(rgb),
        "rgb": list(rgb),
        "share": round(c / total, 4),
        "luminance": round(luminance(rgb), 3),
    } for rgb, c in counter.most_common(args.num_colors)]

    # theme type from the single most-dominant color (usually the background)
    bg = ranked[0]
    theme = "dark" if bg["luminance"] < 0.4 else ("light" if bg["luminance"] > 0.65 else "mixed")

    out = {
        "image": args.image,
        "backend": backend,
        "theme_type_guess": theme,
        "background_guess": bg["hex"],
        "dominant_colors": ranked,
        "note": "Numeric cross-check only — agent assigns final color roles "
                "(bg/text/accent/card) using these + the CSS custom properties.",
    }
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"{len(ranked)} colors ({backend}, theme={theme}) -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
