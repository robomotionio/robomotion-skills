#!/bin/sh
# Runs once at image build (CWD = group root). Best-effort; guarded with || true.
set -eu

# Several skills ship Node + Playwright scripts (graphics-studio render; the keyless
# LinkedIn / Product Hunt / review / X / Luma scrape degrades). Install Chromium once.
if command -v npx >/dev/null 2>&1; then
  npm install -g playwright >/dev/null 2>&1 || true
  npx --yes playwright install chromium >/dev/null 2>&1 || true
fi

# Make bundled scripts executable.
find skills -type f \( -name '*.py' -o -name '*.mjs' -o -name '*.sh' \) \
  -exec chmod +x {} \; 2>/dev/null || true

exit 0
