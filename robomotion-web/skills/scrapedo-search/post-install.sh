#!/bin/sh
# scrapedo-search install hook - runs once at image build (CWD = the skill folder).
# Standard-library Python only: nothing is downloaded. Two short commands are
# put on PATH so the agent never has to locate the skill folder.
set -eu
script="$(pwd)/scripts/scrapedo.py"
for pair in web-search:search web-fetch:fetch; do
  name=${pair%%:*}; sub=${pair#*:}
  cat > "/usr/local/bin/$name" <<EOF
#!/bin/sh
export PYTHONDONTWRITEBYTECODE=1
exec python3 "$script" $sub "\$@"
EOF
  chmod 0755 "/usr/local/bin/$name"
done
