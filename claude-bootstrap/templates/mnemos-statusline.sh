#!/bin/bash
# Mnemos Statusline Script — receives context JSON on stdin every API call.
#
# 1. Writes fatigue.json for hooks to read (always)
# 2. Delegates display to ccusage statusline if available (cost + context)
# 3. Falls back to simple context % display if ccusage not installed
#
# Auto-configured by Mnemos via settings.json statusLine.
# Input (stdin JSON): context_window.used_percentage, remaining_percentage, etc.

# Read JSON from stdin — must capture before any piping
INPUT=$(cat)

if [ -z "$INPUT" ]; then
    exit 0
fi

# ─── Step 1: Write fatigue.json (always, fast) ───

python3 -c "
import json, time, os, sys

os.makedirs('.mnemos', exist_ok=True)

raw = '''$(echo "$INPUT" | sed "s/'/'\\\\''/g")'''

try:
    data = json.loads(raw)
except:
    data = {}

cw = data.get('context_window', {})
used_pct = cw.get('used_percentage', 0)
remaining_pct = cw.get('remaining_percentage', 100)
ctx_size = cw.get('context_window_size', 200000)

# Token counts are under current_usage (not top-level)
cu = cw.get('current_usage', {})
used_tokens = (cu.get('input_tokens', 0)
    + cu.get('cache_creation_input_tokens', 0)
    + cu.get('cache_read_input_tokens', 0))
remaining_tokens = max(0, ctx_size - int(ctx_size * used_pct / 100))

fatigue = {
    'used_percentage': used_pct,
    'remaining_percentage': remaining_pct,
    'used_tokens': used_tokens,
    'total_tokens': ctx_size,
    'remaining_tokens': remaining_tokens,
    'total_input_tokens': cw.get('total_input_tokens', 0),
    'total_output_tokens': cw.get('total_output_tokens', 0),
    'timestamp': time.time(),
    'source': 'statusline'
}
with open('.mnemos/fatigue.json', 'w') as f:
    json.dump(fatigue, f)
"

# ─── Step 2: Display — prefer ccusage, fallback to simple ───

if command -v ccusage &>/dev/null; then
    # ccusage statusline gets the same JSON, shows cost + context + burn rate
    echo "$INPUT" | ccusage statusline 2>/dev/null
    if [ $? -eq 0 ]; then
        exit 0
    fi
fi

# Try npx ccusage (slower, only if ccusage not globally installed)
if command -v npx &>/dev/null; then
    echo "$INPUT" | npx --yes ccusage statusline 2>/dev/null
    if [ $? -eq 0 ]; then
        exit 0
    fi
fi

# Fallback: simple context display
python3 -c "
import json
try:
    data = json.loads('''$(echo "$INPUT" | sed "s/'/'\\\\''/g")''')
    cw = data.get('context_window', {})
    used = cw.get('used_percentage', 0)
    if used >= 90: s = ' EMERGENCY'
    elif used >= 75: s = ' WARNING'
    elif used >= 60: s = ' NOTICE'
    elif used >= 40: s = ' ~'
    else: s = ''
    print(f'Ctx:{used:.0f}%{s}')
except:
    print('Ctx:?%')
"

exit 0
