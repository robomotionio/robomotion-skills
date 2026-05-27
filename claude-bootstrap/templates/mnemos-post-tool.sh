#!/bin/bash
# Mnemos PostToolUse Hook — logs tool outcomes + periodic auto-node creation.
#
# 1. Logs success/failure signal to .mnemos/signals.jsonl
# 2. Detects git commits → creates ResultNode immediately
# 3. Every 25 tool calls → auto-creates nodes from recent activity
# 4. Updates fatigue.json if stale
#
# No set -euo pipefail: hook scripts must be defensive, not strict.
# Timeout: 3 seconds max

if [ ! -d ".mnemos" ]; then
    exit 0
fi

HOOK_INPUT=$(cat 2>/dev/null || true)

if [ -z "$HOOK_INPUT" ]; then
    exit 0
fi

# Write to temp file to avoid shell escaping issues with nested JSON
TMPFILE=$(mktemp /tmp/mnemos-post-XXXXXX.json 2>/dev/null || echo "/tmp/mnemos-post-$$.json")
echo "$HOOK_INPUT" > "$TMPFILE" 2>/dev/null

python3 -c "
import json, sys, time, os, glob
from pathlib import Path

tmpfile = sys.argv[1]
try:
    with open(tmpfile) as f:
        data = json.load(f)
except:
    sys.exit(0)
finally:
    try:
        os.unlink(tmpfile)
    except:
        pass

tool = data.get('tool_name', '')
tool_input = data.get('tool_input', {})
response = data.get('tool_response', {})

# Extract file path
fp = ''
if isinstance(tool_input, dict):
    fp = tool_input.get('file_path', '') or tool_input.get('path', '')

# Determine success
success = True
if isinstance(response, dict):
    if response.get('error') or response.get('is_error'):
        success = False
    if 'exit_code' in response and response['exit_code'] != 0:
        success = False
elif isinstance(response, str):
    if response.startswith('Error:') or 'error' in response[:50].lower():
        success = False

# Append signal
signal = {
    'tool': tool,
    'event': 'post',
    'file_path': fp,
    'success': success,
    'ts': time.time()
}

os.makedirs('.mnemos', exist_ok=True)
with open('.mnemos/signals.jsonl', 'a') as f:
    f.write(json.dumps(signal) + '\n')

# ─── Auto-node creation ───

mnemos_dir = Path('.mnemos')

try:
    from mnemos.auto_nodes import (
        detect_git_commit, create_commit_node,
        should_run, run_auto_add,
    )

    # Immediate: detect git commits
    resp_str = response if isinstance(response, str) else json.dumps(response)
    commit_msg = detect_git_commit(tool, tool_input, resp_str)
    if commit_msg:
        create_commit_node(mnemos_dir, commit_msg)

    # Periodic: every 25 calls, scan and create nodes
    if should_run(mnemos_dir):
        run_auto_add(mnemos_dir)

except ImportError:
    pass
except Exception:
    pass

# ─── Auto-feed token signal from JSONL if fatigue.json is stale ───

fatigue_path = '.mnemos/fatigue.json'
stale = True
try:
    with open(fatigue_path) as f:
        fd = json.load(f)
    if time.time() - fd.get('timestamp', 0) < 60:
        stale = False
except:
    pass

if stale:
    home = os.path.expanduser('~')
    cwd = os.getcwd()
    project_key = cwd.replace('/', '-')
    project_dir = os.path.join(home, '.claude', 'projects', project_key)

    if not os.path.isdir(project_dir):
        for parent in [os.path.dirname(cwd), os.path.dirname(os.path.dirname(cwd))]:
            pk = parent.replace('/', '-')
            pd = os.path.join(home, '.claude', 'projects', pk)
            if os.path.isdir(pd):
                project_dir = pd
                break

    try:
        jsonl_files = sorted(
            glob.glob(os.path.join(project_dir, '*.jsonl')),
            key=os.path.getmtime, reverse=True
        )
        if jsonl_files:
            with open(jsonl_files[0], 'rb') as f:
                f.seek(0, 2)
                pos = f.tell()
                if pos > 0:
                    read_size = min(8192, pos)
                    f.seek(pos - read_size)
                    chunk = f.read().decode('utf-8', errors='replace')
                    lines = chunk.strip().split('\n')
                    last_line = lines[-1]
                    entry = json.loads(last_line)
                    usage = entry.get('message', {}).get('usage', {})
                    if usage:
                        input_tok = usage.get('input_tokens', 0)
                        cache_read = usage.get('cache_read_input_tokens', 0)
                        cache_create = usage.get('cache_creation_input_tokens', 0)
                        total_in_context = input_tok + cache_read + cache_create
                        context_limit = 200000
                        correction = 0.75
                        used_pct = min(100.0, (total_in_context * correction / context_limit) * 100)
                        fatigue_data = {
                            'used_percentage': round(used_pct, 1),
                            'remaining_percentage': round(100 - used_pct, 1),
                            'used_tokens': total_in_context,
                            'total_tokens': context_limit,
                            'remaining_tokens': max(0, context_limit - total_in_context),
                            'timestamp': time.time(),
                            'source': 'jsonl_estimate'
                        }
                        with open(fatigue_path, 'w') as f:
                            json.dump(fatigue_data, f)
    except:
        pass
" "$TMPFILE" 2>/dev/null

# Clean up temp file if python didn't
rm -f "$TMPFILE" 2>/dev/null

exit 0
