#!/bin/sh
# scaffold.sh: start an illustrated-video project inside a HyperFrames project.
#
#   sh scaffold.sh <project_dir> <audio_file> <spine.json>
#   sh scaffold.sh <project_dir> - <spine.json>      # a video with no sound
#
# Run it after `hyperframes init <project_dir> --example=blank` and after
# spine.py. It copies the kit, the fonts and the audio in, writes spine.js
# (the spine as a script, so scenes read it with no fetch) and replaces
# index.html with the layered template (back canvas, performance clips,
# front canvas, soundtrack) and a starter scenes.js. Re-running it refreshes
# the kit, fonts and spine.js and leaves index.html and scenes.js alone.
set -eu
dir=$1; audio=$2; spine=$3
here=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$dir/assets/fonts" "$dir/assets/gen" "$dir/assets/perf" "$dir/assets/slices" "$dir/renders" "$dir/out/check"
cp "$here/scripts/paperkit.js" "$dir/assets/paperkit.js"
cp "$here/assets/fonts/"*.ttf "$here/assets/fonts/FONTS.md" "$here/assets/fonts/OFL.txt" "$dir/assets/fonts/"
cp "$here/scripts/howto.js" "$dir/assets/howto.js"
if [ "$audio" = "-" ]; then
  ext=none
else
  ext=${audio##*.}
  [ "$(cd "$(dirname "$audio")" && pwd)/$(basename "$audio")" = "$(cd "$dir/assets" && pwd)/track.$ext" ] || cp "$audio" "$dir/assets/track.$ext"
fi
dur=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['duration'])" "$spine")
{ printf 'window.SPINE = '; cat "$spine"; printf ';\n'; } > "$dir/spine.js"
if [ ! -f "$dir/scenes.js" ]; then
  if [ "$ext" = none ]; then
    sed "s/__DURATION__/$dur/g; /<audio id=\"track\"/d" "$here/templates/index.html" > "$dir/index.html"
  else
    sed "s/__DURATION__/$dur/g; s#assets/track.mp3#assets/track.$ext#" "$here/templates/index.html" > "$dir/index.html"
  fi
  sed "s/__DURATION__/$dur/g" "$here/templates/scenes.js" > "$dir/scenes.js"
  echo "scaffold: $dir ready (index.html, scenes.js, $dur s)"
else
  echo "scaffold: refreshed kit, fonts and spine.js in $dir (scenes kept)"
fi
