#!/bin/sh
# robomotion-web group install hook - runs once at image build (CWD = the group root).
# Standard-library Python only: nothing is downloaded. Two short commands are
# put on PATH so the agent never has to locate the skill folder.
set -eu
script="$(pwd)/skills/scrapedo-search/scripts/scrapedo.py"
for pair in web-search:search web-fetch:fetch; do
  name=${pair%%:*}; sub=${pair#*:}
  cat > "/usr/local/bin/$name" <<EOF
#!/bin/sh
export PYTHONDONTWRITEBYTECODE=1
exec python3 "$script" $sub "\$@"
EOF
  chmod 0755 "/usr/local/bin/$name"
done
