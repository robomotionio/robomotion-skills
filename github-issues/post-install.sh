#!/bin/sh
# Install GitHub's official CLI. Idempotent: skipped on rebuild via the
# image-hash cache when the skill set is unchanged.
set -eu

apt-get update
apt-get install -y --no-install-recommends ca-certificates curl gnupg

curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  > /etc/apt/sources.list.d/github-cli.list

apt-get update
apt-get install -y --no-install-recommends gh
rm -rf /var/lib/apt/lists/*
