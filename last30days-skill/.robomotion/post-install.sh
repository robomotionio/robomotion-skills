#!/bin/sh
# last30days-skill group install hook - runs once at image build (CWD = group root).
#
# The engine (skills/last30days/scripts/last30days.py) is standard-library
# Python 3.12+. YouTube search and comments use yt-dlp, which upstream's
# first-run wizard installs with brew or pip into the user's home; here it is
# installed at a pinned version, checked by hash, so a run installs nothing.
#
# The wizard also extracts browser cookies and installs npm CLIs. None of that
# belongs in a sandbox, so the hook writes the marker the skill's patched
# first-run gate looks for, and the skill goes straight to research.
set -eu

YTDLP_VERSION=2026.08.19
# The zipapp build (`yt-dlp` in the release), not the PyInstaller binaries:
# those bundle certifi and would refuse the sandbox's proxy CA; the zipapp
# runs on the system Python and its trust store.
YTDLP_SHA256=1fa6733c37ea6fb51c99ad8fe785e7b7e5f3246c9b980230329d4fb72ed8d4d6

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' || {
  echo "last30days: the engine needs Python 3.12+, found $(python3 --version 2>&1)" >&2
  exit 1
}

L30=/opt/last30days
mkdir -p "$L30"
curl -fsSL --retry 3 -o "$L30/yt-dlp" \
  "https://github.com/yt-dlp/yt-dlp/releases/download/${YTDLP_VERSION}/yt-dlp"
echo "$YTDLP_SHA256  $L30/yt-dlp" | sha256sum -c -
chmod 0755 "$L30/yt-dlp"

# no-certifi: use the system trust store (where the sandbox's proxy CA is)
# even if certifi happens to be importable. No update check, no config files.
cat > /usr/local/bin/yt-dlp <<EOF
#!/bin/sh
exec python3 $L30/yt-dlp --compat-options no-certifi --ignore-config "\$@"
EOF
chmod 0755 /usr/local/bin/yt-dlp

# Short commands for the engine and the two Robomotion scripts, so the agent
# never has to locate the skill folder.
scripts="$(pwd)/skills/last30days/scripts"
for pair in "last30days:last30days.py" "google-trends:google_trends.py" "fetch-covers:fetch_covers.py"; do
  name=${pair%%:*}; file=${pair#*:}
  cat > "/usr/local/bin/$name" <<EOF
#!/bin/sh
export PYTHONDONTWRITEBYTECODE=1
# Research is kept in the agent's own folder, which outlives the container.
if [ -z "\${LAST30DAYS_MEMORY_DIR:-}" ] && [ -d /workspace ] && [ -w /workspace ]; then
  export LAST30DAYS_MEMORY_DIR=/workspace/last30days
fi
exec python3 "$scripts/$file" "\$@"
EOF
  chmod 0755 "/usr/local/bin/$name"
done

# The skill's first-run gate (patched) treats this file as a finished setup.
mkdir -p /etc/last30days
echo "SETUP_COMPLETE=true" > /etc/last30days/robomotion-ready
chmod -R a+rX /etc/last30days "$L30"

yt-dlp --version
last30days --help > /dev/null
