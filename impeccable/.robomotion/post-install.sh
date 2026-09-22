#!/bin/sh
# impeccable group install hook - runs once at image build (CWD = group root).
#
# The skill drives the impeccable engine, one binary. Upstream's launcher
# (skills/impeccable/scripts/impeccable) downloads it from GitHub on first
# use, into the user's home, checked only against a hash sidecar from the same
# release. Here it is installed at the version the skill pins
# (scripts/VERSION), checked against hashes recorded in this file, on PATH:
# the launcher probes PATH before it would download, so a run fetches nothing.
#
# URL scans (`detect <url>`, a critique of a live site) drive a Chromium. The
# engine looks in IMPECCABLE_BROWSER first; this installs Chrome for Testing's
# headless shell at a pinned version and the wrapper points the engine at it.
set -eu

# The engine version the skill's launcher asks for. Bump with scripts/VERSION.
ENGINE_VERSION=0.1.5
ENGINE_SHA256_X64=cf5231a4b1ae66996c85b033800b1dad0797e590eae2f21ef2579430af187f19
ENGINE_SHA256_ARM64=bc4fa28bc8ccbb018795a99a4ece95ada898a6f1885f14281389d0e6ef2a2f98
CHROME_VERSION=154.0.8037.57
CHROME_SHA256_X64=5a6979d0ab7cf952ea575d35164e7bdce4872b2ced8f8a215c8f8e8eda00ee09
CHROME_SHA256_ARM64=2213770a541c7ea17c900c631bdb6a3cda97ecf5194a34a575f32e54a8f5ab70

IMP=/opt/impeccable
IMP_HOME=$IMP/home

pinned=$(tr -d '[:space:]' < skills/impeccable/scripts/VERSION)
[ "$pinned" = "$ENGINE_VERSION" ] || {
  echo "impeccable: the skill pins engine $pinned, this hook installs $ENGINE_VERSION; bump the pins here" >&2
  exit 1
}

case "$(uname -m)" in
  x86_64|amd64) engine_asset=impeccable-linux-x64; engine_sha=$ENGINE_SHA256_X64
    chrome_dir=linux64; chrome_zip=chrome-headless-shell-linux64.zip; chrome_sha=$CHROME_SHA256_X64 ;;
  aarch64|arm64) engine_asset=impeccable-linux-arm64; engine_sha=$ENGINE_SHA256_ARM64
    chrome_dir=linux-arm64; chrome_zip=chrome-headless-shell-linux-arm64.zip; chrome_sha=$CHROME_SHA256_ARM64 ;;
  *) echo "impeccable: no engine build for $(uname -m)" >&2; exit 1 ;;
esac

# fetch <url> <sha256> <dest>
fetch() {
  mkdir -p "$(dirname "$3")"
  curl -fsSL --retry 3 -o "$3" "$1"
  echo "$2  $3" | sha256sum -c -
}

# The libraries the headless shell links against on Ubuntu 24.04, fonts for
# pages that name none it can load, certutil for the wrapper's proxy CA, and
# unzip for the Chrome archive.
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  unzip libnss3-tools \
  libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 \
  libxkbcommon0 libatspi2.0-0t64 libxcomposite1 libxdamage1 libxfixes3 \
  libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2t64 \
  fonts-liberation fonts-dejavu-core fonts-noto-color-emoji
rm -rf /var/lib/apt/lists/*

fetch "https://github.com/pbakaus/impeccable/releases/download/engine-v${ENGINE_VERSION}/${engine_asset}" \
  "$engine_sha" "$IMP/engine/impeccable"
chmod 755 "$IMP/engine/impeccable"

fetch "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/${chrome_dir}/${chrome_zip}" \
  "$chrome_sha" /tmp/impeccable-chrome.zip
unzip -q /tmp/impeccable-chrome.zip -d "$IMP/chrome"
rm -f /tmp/impeccable-chrome.zip
chrome=$(find "$IMP/chrome" -type f -name chrome-headless-shell | head -n 1)
[ -n "$chrome" ] || { echo "impeccable: no chrome-headless-shell in the archive" >&2; exit 1; }

# The engine keeps its cache and settings under $HOME/.impeccable. The agent's
# terminal runs as the host user, whose home differs per machine, so the
# engine gets a home of its own; any uid writes there, nobody removes
# another's files.
mkdir -p "$IMP_HOME"
chmod -R a+rX "$IMP"
find "$IMP_HOME" -type d -exec chmod 1777 {} +

cat > /tmp/impeccable-wrapper <<EOF
#!/bin/sh
export HOME="$IMP_HOME"
export IMPECCABLE_BROWSER="$chrome"
export IMPECCABLE_NO_UPDATE_CHECK=1 IMPECCABLE_NO_TELEMETRY=1 DO_NOT_TRACK=1

# The agent's sandbox sends every https request through a credential proxy
# that re-signs the traffic, and names the proxy's CA in SSL_CERT_FILE. Chrome
# does not read that variable; it trusts its own roots plus \$HOME/.pki/nssdb,
# so without the CA there a URL scan fails with ERR_CERT_AUTHORITY_INVALID.
# The db is made here, per run, because the CA is the machine's, not the
# image's.
if [ -n "\${SSL_CERT_FILE:-}" ] && [ -r "\$SSL_CERT_FILE" ]; then
  db="\$HOME/.pki/nssdb"
  [ -f "\$db/cert9.db" ] || { mkdir -p "\$db" && certutil -d "sql:\$db" -N --empty-password; }
  certutil -d "sql:\$db" -L -n robomotion-proxy-ca >/dev/null 2>&1 \\
    || certutil -d "sql:\$db" -A -t "C,," -n robomotion-proxy-ca -i "\$SSL_CERT_FILE"
fi

exec "$IMP/engine/impeccable" "\$@"
EOF
install -m 755 /tmp/impeccable-wrapper /usr/local/bin/impeccable
rm -f /tmp/impeccable-wrapper

impeccable engine-probe
