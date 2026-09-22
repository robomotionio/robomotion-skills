#!/bin/sh
# Tavily group install hook - runs once at image build.
#
# Every skill drives the `tvly` CLI. Upstream installs it by piping
# cli.tavily.com/install.sh into bash, and `tvly init` / `tvly update` fetch
# newer skills and a newer CLI at run time. Install it here instead, pinned,
# into the image's site-packages that the agent's user cannot write; our
# patch to tavily-cli/SKILL.md tells the agent it is already there.
set -eu

# The CLI release current at the upstream commit the skills are synced from
# (upstreams.yaml). Bump the two together.
TAVILY_CLI_VERSION=0.1.8

pip install --no-cache-dir --break-system-packages "tavily-cli==${TAVILY_CLI_VERSION}"

tvly --version
