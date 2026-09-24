#!/bin/sh
# inkify.sh: print a generated clip or image in the video's inks.
#
#   sh inkify.sh <in.mp4|in.png> <out> "#EEE6D6 #27306B #F2692E #EE4E9B #F2B632" [dither]
#
# Maps every pixel to the nearest of the given inks (paper first) with an
# ordered dither, so tone turns into print-like dot patterns, then pushes
# near-paper pixels to exactly the paper colour. Over paper, lay the result
# down with mix-blend-mode: multiply and the paper disappears: generated
# footage becomes ink on the page, one world with the drawn scenes.
#
# dither: bayer (default, a regular print screen), sierra2_4a (softer grain)
# or none (flat poster colours).
set -eu
in=$1; out=$2; inks=$3; dither=${4:-bayer}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# The palette: 256 pixels (paletteuse wants exactly that), the inks repeated,
# written byte-exact (ffmpeg's colour source would shift them through YUV).
n=$(python3 - "$tmp/pal.ppm" $inks <<'PY'
import sys
out, inks = sys.argv[1], sys.argv[2:]
rgb = [bytes.fromhex(c.lstrip('#')) for c in inks]
px = b"".join(rgb[i * len(rgb) // 256] for i in range(256))
open(out, "wb").write(b"P6 256 1 255\n" + px)
print(len(rgb))
PY
)

case "$dither" in
  bayer) d="dither=bayer:bayer_scale=2" ;;
  none) d="dither=none" ;;
  *) d="dither=$dither" ;;
esac
case "$in" in
  *.png|*.jpg|*.jpeg|*.webp)
    ffmpeg -v error -y -i "$in" -i "$tmp/pal.ppm" -lavfi "[0:v]eq=contrast=1.12:saturation=1.15[a];[a][1:v]paletteuse=$d:diff_mode=rectangle" -frames:v 1 "$out" ;;
  *)
    ffmpeg -v error -y -i "$in" -i "$tmp/pal.ppm" -lavfi "[0:v]eq=contrast=1.12:saturation=1.15[a];[a][1:v]paletteuse=$d:diff_mode=rectangle,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" \
      -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:v libx264 -crf 16 -preset medium -c:a copy "$out" ;;
esac
echo "inkify: $in → $out ($n inks, $dither)"
