#!/bin/sh
# claude-seo group install hook - runs once at image build (CWD = group root).
#
# The skills run ~50 Python scripts through the pack's own launcher,
# `scripts/claude-seo run <script>`. It runs them in an isolated environment
# that `claude-seo setup` builds: a virtualenv with upstream's pinned,
# per-CVE-annotated requirements.txt and Playwright's Chromium. Without it
# every step answers "Claude SEO runtime is not ready", and the agent falls
# back to describing an audit instead of running one.
#
# Setup keeps that environment in a data folder, by default under the user's
# home. The image is built as root and the agent's terminal runs as the host
# user, whose home is elsewhere and may not exist, so setup runs here into
# /opt/claude-seo and a .pth line points every Python start there.
set -eu

# WeasyPrint renders the PDF report and needs Pango; the fonts are what the
# report is set in.
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi8 fonts-dejavu-core fonts-liberation

export CLAUDE_SEO_DATA_DIR=/opt/claude-seo
mkdir -p "$CLAUDE_SEO_DATA_DIR"
bash scripts/claude-seo setup
# setup installs the browser; these are the system libraries it links against.
"$CLAUDE_SEO_DATA_DIR/.venv/bin/python" -m playwright install-deps chromium
rm -rf /var/lib/apt/lists/*
chmod -R a+rX "$CLAUDE_SEO_DATA_DIR"

# Every Python start (a .pth line imports this module) finds the runtime in
# /opt/claude-seo. The pack's own runtime process also drops the sandbox's
# HTTP proxy: that proxy is the robot's credential proxy on a private
# address, and the pack's SSRF guard (scripts/url_safety.py) refuses any
# proxy that is not public, so every fetch failed with "Refusing configured
# HTTP proxy". Its pages are public and need no secret; other Python
# processes keep the proxy.
site=$(python3 -c 'import site; print(site.getsitepackages()[0])')
cat > "$site/robomotion_claude_seo.py" <<'PY'
import os, sys
os.environ.setdefault("CLAUDE_SEO_DATA_DIR", "/opt/claude-seo")
# seo-drift compares a page with the baseline it saved on an earlier run, so
# the baselines must outlive the container. Upstream keeps them under the
# user's home, which here is the host user's and may not exist; the agent's
# own folder, /workspace, is what survives between runs.
if os.path.isdir("/workspace") and os.access("/workspace", os.W_OK):
    os.environ.setdefault("CLAUDE_SEO_DRIFT_DIR", "/workspace/.claude-seo/drift")
_argv0 = (sys.argv[0] if getattr(sys, "argv", None) else "") or ""
if _argv0.replace("\\", "/").endswith("/scripts/runtime.py") and "claude-seo" in _argv0:
    for _key in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
        os.environ.pop(_key, None)
PY
echo 'import robomotion_claude_seo' > "$site/robomotion-claude-seo.pth"

bash scripts/claude-seo doctor
