#!/bin/sh
# claude-seo group install hook - runs once at image build (CWD = group root).
#
# The skills are instructions for ~50 Python scripts under scripts/. Without
# their dependencies every one of them fails on import, and the agent falls
# back to describing an audit instead of running one.
#
# requirements.txt is upstream's, pinned and annotated per CVE, and it comes
# in through the reviewed sync like the rest of the group.
set -eu

# WeasyPrint renders the PDF report and needs Pango; the fonts are what the
# report is set in.
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi8 fonts-dejavu-core fonts-liberation
rm -rf /var/lib/apt/lists/*

# The image is built for this agent and thrown away with it, so the system
# interpreter is the right place: the skills call plain `python3`.
pip install --no-cache-dir --break-system-packages -r requirements.txt

# Pages that build themselves in the browser audit as empty without this.
# The browser goes where every user can read it: the image is built as root,
# and the agent's terminal runs as the host user, whose home is elsewhere and
# may not exist. A .pth line runs at every Python start and points Playwright
# there (sitecustomize would not: Ubuntu's own one comes first on the path).
export PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
python3 -m playwright install --with-deps chromium
chmod -R a+rX /opt/ms-playwright
site=$(python3 -c 'import site; print(site.getsitepackages()[0])')
echo 'import os; os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/ms-playwright")' > "$site/robomotion-playwright.pth"
