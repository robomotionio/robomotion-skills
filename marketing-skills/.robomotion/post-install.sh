#!/bin/sh
# Marketing-skills group install hook — runs once at image build (CWD = group root).
#
# Upstream ships its Node CLIs at tools/clis/ (non-standard layout vs. the
# `bin/` convention the launcher auto-PATHs). Wrap each one in a tiny shell
# stub on /usr/local/bin so the model can invoke them by short name
# (e.g. `ga4 query …` instead of `node ${CLAUDE_PLUGIN_ROOT}/tools/clis/ga4.js …`).
set -eu

for f in tools/clis/*.js; do
  [ -e "$f" ] || continue
  name=$(basename "$f" .js)
  cat > "/usr/local/bin/$name" <<EOF
#!/bin/sh
exec node "$(pwd)/$f" "\$@"
EOF
  chmod +x "/usr/local/bin/$name"
done
