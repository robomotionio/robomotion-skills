#!/bin/sh
# OfficeCLI group install hook - runs once at image build.
#
# Every skill drives the `officecli` binary. Upstream installs it by piping
# d.officecli.ai/install.sh into bash, and the binary then updates itself
# once a day from the project's own mirror. Install it here instead: the
# release binary at a pinned version, checked against a hash recorded in
# this file, in a folder the agent's user cannot write. Our patch to the
# skills tells the agent it is already there.
set -eu

# The release current at the upstream commit the skills are synced from
# (upstreams.yaml); its tag is an ancestor of that commit. Bump the version
# and both hashes together, from the release's SHA256SUMS.
OFFICECLI_VERSION=1.0.150
SHA256_X64=faceb42654004f1fa5c40fb0ce641c42b7dc5a2beb270f25971ea6265b7dc227
SHA256_ARM64=93bea35aaa8f153a56a4f6e1a7d22d82aec379e42ce2d45b24b0941dcfd50968

case "$(uname -m)" in
  x86_64 | amd64) asset=officecli-linux-x64 sha=$SHA256_X64 ;;
  aarch64 | arm64) asset=officecli-linux-arm64 sha=$SHA256_ARM64 ;;
  *) echo "officecli: no release binary for $(uname -m)" >&2; exit 1 ;;
esac

# A self-contained .NET binary: nothing to install beside it but ICU, which
# .NET loads for culture data and a slim base image may not carry.
if ! ldconfig -p | grep -q 'libicuuc\.so'; then
  apt-get update -qq
  icu=$(apt-cache pkgnames libicu | grep -E '^libicu[0-9]+(t64)?$' | sort -V | tail -n 1)
  apt-get install -y -qq --no-install-recommends "$icu"
  rm -rf /var/lib/apt/lists/*
fi

mkdir -p /opt/officecli
curl -fsSL --retry 3 -o /opt/officecli/officecli \
  "https://github.com/iOfficeAI/OfficeCLI/releases/download/v${OFFICECLI_VERSION}/${asset}"
echo "$sha  /opt/officecli/officecli" | sha256sum -c -
chmod 755 /opt/officecli /opt/officecli/officecli

# The wrapper is what the agent runs. It turns off the daily self-update and
# the first-run self-install (which would copy the binary and its bundled
# skills into the user's folders). A self-update could not land anyway: it
# writes beside the binary, and /opt/officecli belongs to root.
cat > /usr/local/bin/officecli <<'EOF'
#!/bin/sh
export OFFICECLI_SKIP_UPDATE=1 OFFICECLI_NO_AUTO_INSTALL=1
exec /opt/officecli/officecli "$@"
EOF
chmod 755 /usr/local/bin/officecli

officecli --version
