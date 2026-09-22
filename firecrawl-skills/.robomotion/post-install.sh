#!/bin/sh
# Firecrawl group install hook - runs once at image build.
#
# Every skill drives the Firecrawl CLI as `npx firecrawl-cli ...` or
# `firecrawl ...`, and the install notes tell the agent to fetch
# `firecrawl-cli@latest` when it is missing. That would run whatever npm
# serves that day. Put the CLI on PATH here, at a pinned version, so neither
# fires: npx finds a global install and runs it instead of downloading one.
set -eu

# The CLI release current at the upstream commit the skills are synced from
# (upstreams.yaml). Bump the two together.
FIRECRAWL_CLI_VERSION=1.23.3

npm install -g --no-fund --no-audit "firecrawl-cli@${FIRECRAWL_CLI_VERSION}"

# The CLI checks npm for a newer release and tells the agent to reinstall
# globally when it finds one; the pin above is the version. The wrapper turns
# that check off, and the login telemetry with it. It takes the place of
# npm's own link, which is what both `firecrawl` and `npx firecrawl-cli` run.
link="$(npm prefix -g)/bin/firecrawl"
[ -L "$link" ] || { echo "firecrawl: $link is not npm's link to the CLI" >&2; exit 1; }
real=$(readlink -f "$link")
cat > /tmp/firecrawl-wrapper <<EOF
#!/bin/sh
export FIRECRAWL_NO_UPDATE_CHECK=1 FIRECRAWL_NO_TELEMETRY=1
exec "$real" "\$@"
EOF
rm -f "$link"
install -m 755 /tmp/firecrawl-wrapper "$link"
rm -f /tmp/firecrawl-wrapper

firecrawl --version
