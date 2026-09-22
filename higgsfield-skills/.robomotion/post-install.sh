#!/bin/sh
# Higgsfield group install hook - runs once at image build.
#
# Every skill here says "if `higgsfield` is not on PATH, pipe the installer
# from the CLI repo's main branch into a shell". That would run unpinned,
# unreviewed code at run time. Put the CLI on PATH here, at a pinned version,
# so that line never fires. Bump the version in a reviewed change.
set -eu
npm install -g @higgsfield/cli@1.1.26

# The npm package is a shim: its install script downloads the Go binary for
# this platform and checks it against the checksums.json it ships. Newer npm
# can hold install scripts back ("npm warn install-scripts"), which leaves the
# CLI answering "binary not found"; run the same script directly then.
pkg=$(dirname "$(dirname "$(readlink -f "$(command -v higgsfield)")")")
[ -x "$pkg/vendor/hf" ] || (cd "$pkg" && node install.js)
[ -x "$pkg/vendor/hf" ] || { echo "higgsfield: no CLI binary in $pkg/vendor" >&2; exit 1; }

# The CLI reads opt-outs for its telemetry (it ships a Sentry DSN) and its
# update check; the version is the pin above, so both stay off, as for every
# other CLI this repo installs. npm's two links to it (`higgsfield`, `higgs`)
# become wrappers that set them and run the CLI.
#
# Sign-in is browser OAuth only (`higgsfield auth login`, a loopback
# callback); 1.1.26 reads no API key from the environment, so an agent with no
# browser cannot sign in by itself. The token lives in a credentials file whose
# path HIGGSFIELD_CREDENTIALS_PATH can move.
for name in higgsfield higgs; do
  link=$(command -v "$name")
  [ -L "$link" ] || { echo "higgsfield: $link is not npm's link to the CLI" >&2; exit 1; }
  real=$(readlink -f "$link")
  cat > "/tmp/$name-wrapper" <<EOF
#!/bin/sh
export HIGGSFIELD_DISABLE_TELEMETRY=1 HIGGSFIELD_TELEMETRY=0 HIGGSFIELD_NO_UPDATE_CHECK=1 DO_NOT_TRACK=1
exec "$real" "\$@"
EOF
  rm -f "$link"
  install -m 755 "/tmp/$name-wrapper" "$link"
  rm -f "/tmp/$name-wrapper"
done
higgsfield --version
