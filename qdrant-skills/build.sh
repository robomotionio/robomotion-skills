#!/usr/bin/env bash
set -euo pipefail

rm -rf public
cp -r skills public

find public -name '*.md' -print0 | xargs -0 sed -i 's|https://search\.qdrant\.tech/md/|/md/|g'

bash scripts/generate_sitemap.sh public
