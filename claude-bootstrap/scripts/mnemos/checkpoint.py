"""Checkpoint write/load for Mnemos session persistence."""

from __future__ import annotations

import json
import subprocess
import time
from collections import Counter
from pathlib import Path

from .models import CheckpointNode, _now, _uuid
from .signals import read_recent_signals
from .store import MnemosStore


def write_checkpoint(
    store: MnemosStore,
    fatigue_score: float = 0.0,
    icpg_store=None,
    task_id: str | None = None
) -> CheckpointNode:
    """Write a CheckpointNode capturing current MnemoGraph state.

    Always includes: GoalNode content, all ConstraintNodes, current sub-goal.
    Optionally includes: iCPG state, git state, compressed ResultNodes.

    Writes to:
        .mnemos/checkpoint-latest.json  (always overwritten)
        .mnemos/checkpoints/<id>.json   (archived copy)

    Returns the created CheckpointNode.
    """
    # Determine task_id from active GoalNodes
    goal_nodes = store.get_by_type('goal')
    if not task_id and goal_nodes:
        task_id = goal_nodes[0].task_id
    task_id = task_id or 'unknown'

    # Gather goal
    goal_text = '; '.join(n.content for n in goal_nodes) or 'No active goal'

    # Gather constraints (never evicted)
    constraint_nodes = store.get_by_type('constraint')
    constraints = [n.content for n in constraint_nodes]

    # Gather result summaries (compressed or active)
    result_nodes = store.get_by_type('result')
    results = []
    for rn in result_nodes[:20]:  # Cap at 20 most recent
        if rn.summary:
            results.append(rn.summary)
        elif rn.content:
            results.append(rn.content[:200])

    # Current sub-goal from working nodes
    working_nodes = store.get_by_type('working')
    current_subgoal = working_nodes[0].content if working_nodes else ''

    # Working memory
    working_memory = '\n'.join(
        n.content for n in working_nodes[:3]
    )

    # Task narrative and recent files from signals
    narrative, recent_files = build_task_narrative(store.project_dir)

    # Git state
    git_state = _get_git_state(store.project_dir)

    # iCPG state
    icpg_state = None
    if icpg_store and icpg_store.exists():
        icpg_state = _get_icpg_state(icpg_store)

    # Node summary (counts by type and status)
    stats = store.get_stats()
    node_summary = {
        'total': stats['total_nodes'],
        'active': stats['active'],
        'compressed': stats['compressed'],
        'by_type': stats['by_type']
    }

    cp = CheckpointNode(
        id=_uuid(),
        task_id=task_id,
        goal=goal_text,
        active_constraints=constraints,
        active_results=results,
        current_subgoal=current_subgoal,
        working_memory=working_memory,
        task_narrative=narrative,
        recent_files=recent_files,
        fatigue_at_checkpoint=fatigue_score,
        git_state=git_state,
        icpg_state=icpg_state,
        node_summary=node_summary,
        created_at=_now()
    )

    # Persist to DB
    store.save_checkpoint(cp)

    # Write to JSON files
    cp_data = _checkpoint_to_dict(cp)

    # Latest checkpoint (overwrite)
    latest_path = store.mnemos_dir / 'checkpoint-latest.json'
    latest_path.write_text(json.dumps(cp_data, indent=2))

    # Archived copy
    archive_dir = store.mnemos_dir / 'checkpoints'
    archive_dir.mkdir(exist_ok=True)
    archive_path = archive_dir / f'{cp.id}.json'
    archive_path.write_text(json.dumps(cp_data, indent=2))

    return cp


def load_checkpoint(
    project_dir: str = '.', path: str | None = None
) -> str | None:
    """Load latest checkpoint and format as context for session injection.

    Returns formatted markdown string, or None if no checkpoint exists.
    """
    if path:
        cp_path = Path(path)
    else:
        cp_path = Path(project_dir).resolve() / '.mnemos' / 'checkpoint-latest.json'

    if not cp_path.exists():
        return None

    try:
        data = json.loads(cp_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    return _format_checkpoint(data)


def _format_checkpoint(data: dict) -> str:
    """Format checkpoint data as structured markdown for context injection."""
    lines = []
    lines.append('## Mnemos Session Resume')
    lines.append(f'Checkpoint: {data.get("id", "unknown")[:8]}')
    lines.append(f'Created: {data.get("created_at", "unknown")}')
    lines.append(f'Fatigue at checkpoint: {data.get("fatigue_at_checkpoint", 0):.2f}')
    lines.append('')

    # Goal
    lines.append('### Goal')
    lines.append(data.get('goal', 'No goal recorded'))
    lines.append('')

    # Constraints
    constraints = data.get('active_constraints', [])
    if constraints:
        lines.append('### Active Constraints (DO NOT VIOLATE)')
        for c in constraints:
            lines.append(f'- {c}')
        lines.append('')

    # What was being worked on (task narrative)
    narrative = data.get('task_narrative', '')
    if narrative:
        lines.append('### What You Were Working On')
        lines.append(narrative)
        lines.append('')

    # Current task
    subgoal = data.get('current_subgoal', '')
    if subgoal:
        lines.append('### Current Sub-Goal')
        lines.append(subgoal)
        lines.append('')

    # Working memory
    working = data.get('working_memory', '')
    if working:
        lines.append('### Working Memory')
        lines.append(working)
        lines.append('')

    # Progress (result summaries)
    results = data.get('active_results', [])
    if results:
        lines.append('### Progress So Far')
        for r in results:
            lines.append(f'- {r}')
        lines.append('')

    # Recent files
    recent = data.get('recent_files', [])
    if recent:
        lines.append('### Key Files (from recent activity)')
        for f in recent[:10]:
            parts = []
            if f.get('edits', 0) > 0:
                parts.append(f'edited {f["edits"]}x')
            if f.get('reads', 0) > 0:
                parts.append(f'read {f["reads"]}x')
            detail = ', '.join(parts) if parts else 'touched'
            lines.append(f'- {f.get("path", "?")} ({detail})')
        lines.append('')

    # Git state
    git = data.get('git_state', {})
    if git.get('branch'):
        lines.append('### Git State')
        lines.append(f'Branch: {git["branch"]}')
        if git.get('uncommitted'):
            lines.append('Uncommitted files:')
            for f in git['uncommitted'][:10]:
                lines.append(f'  - {f}')
        lines.append('')

    # iCPG state
    icpg = data.get('icpg_state')
    if icpg:
        lines.append('### iCPG Context')
        if icpg.get('active_reason'):
            lines.append(f'Active intent: {icpg["active_reason"]}')
        if icpg.get('unresolved_drift'):
            lines.append(f'Unresolved drift: {icpg["unresolved_drift"]}')
        if icpg.get('stats'):
            s = icpg['stats']
            lines.append(
                f'Graph: {s.get("reasons", 0)} intents, '
                f'{s.get("symbols", 0)} symbols'
            )
        lines.append('')

    # Node summary
    summary = data.get('node_summary', {})
    if summary:
        lines.append('### MnemoGraph Summary')
        lines.append(
            f'Nodes: {summary.get("active", 0)} active, '
            f'{summary.get("compressed", 0)} compressed, '
            f'{summary.get("total", 0)} total'
        )
        by_type = summary.get('by_type', {})
        if by_type:
            parts = [f'{t}:{c}' for t, c in by_type.items()]
            lines.append(f'Types: {", ".join(parts)}')

    return '\n'.join(lines)


def _get_git_state(project_dir: Path) -> dict:
    """Get current git branch and uncommitted files."""
    state = {}
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_dir)
        )
        if result.returncode == 0:
            state['branch'] = result.stdout.strip()

        result = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_dir)
        )
        if result.returncode == 0:
            files = [
                f.strip() for f in result.stdout.strip().split('\n')
                if f.strip()
            ]
            state['uncommitted'] = files

        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_dir)
        )
        if result.returncode == 0:
            staged = [
                f.strip() for f in result.stdout.strip().split('\n')
                if f.strip()
            ]
            if staged:
                state['staged'] = staged

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return state


def _get_icpg_state(icpg_store) -> dict:
    """Extract summary iCPG state for checkpoint."""
    state = {}
    try:
        stats = icpg_store.get_stats()
        state['stats'] = stats

        # Find most recent executing reason
        executing = icpg_store.list_reasons(status='executing')
        if executing:
            r = executing[-1]
            state['active_reason'] = f'{r.id[:8]} -- {r.goal}'

        # Unresolved drift count
        drift = icpg_store.get_unresolved_drift()
        state['unresolved_drift'] = len(drift)
    except Exception:
        pass
    return state


def build_task_narrative(project_dir: str | Path) -> tuple[str, list[dict]]:
    """Build a human-readable task narrative from recent signals.

    Reads signals.jsonl and produces:
    1. A narrative string describing recent activity
    2. A list of recent files with read/edit counts

    Returns:
        (narrative_text, recent_files_list)
    """
    signals = read_recent_signals(str(project_dir), limit=50)
    if not signals:
        return ('', [])

    # Count file interactions
    file_edits: Counter = Counter()
    file_reads: Counter = Counter()
    tool_counts: Counter = Counter()
    error_count = 0
    total_outcomes = 0

    for s in signals:
        tool = s.get('tool', '')
        fp = s.get('file_path', '')
        tool_counts[tool] += 1

        if fp:
            if tool in ('Edit', 'Write'):
                file_edits[fp] += 1
            elif tool == 'Read':
                file_reads[fp] += 1

        if 'success' in s:
            total_outcomes += 1
            if not s['success']:
                error_count += 1

    # Build narrative
    parts = []

    # Most-edited files
    top_edits = file_edits.most_common(5)
    if top_edits:
        edit_parts = []
        for fp, count in top_edits:
            name = Path(fp).name
            edit_parts.append(f'{name} ({count}x)')
        parts.append(f'Editing: {", ".join(edit_parts)}')

    # Most-read files
    top_reads = file_reads.most_common(5)
    if top_reads:
        read_parts = []
        for fp, count in top_reads:
            name = Path(fp).name
            read_parts.append(f'{name} ({count}x)')
        parts.append(f'Reading: {", ".join(read_parts)}')

    # Tool activity
    other_tools = {t: c for t, c in tool_counts.items()
                   if t not in ('Edit', 'Write', 'Read')}
    if other_tools:
        tool_parts = [f'{t}:{c}' for t, c in
                      sorted(other_tools.items(), key=lambda x: -x[1])]
        parts.append(f'Other tools: {", ".join(tool_parts[:5])}')

    # Focus area (most common directory)
    all_files = list(file_edits.keys()) + list(file_reads.keys())
    if all_files:
        dir_counts: Counter = Counter()
        for fp in all_files:
            parent = str(Path(fp).parent)
            # Shorten to relative if possible
            try:
                parent = str(Path(parent).relative_to(Path.cwd()))
            except ValueError:
                pass
            dir_counts[parent] += 1
        top_dir = dir_counts.most_common(1)[0]
        parts.append(f'Focus area: {top_dir[0]}/')

    # Errors
    if error_count > 0:
        parts.append(f'Errors: {error_count}/{total_outcomes} tool calls failed')

    narrative = '. '.join(parts) + '.' if parts else ''

    # Build recent files list
    all_touched = set(file_edits.keys()) | set(file_reads.keys())
    recent_files = []
    for fp in all_touched:
        entry = {'path': fp}
        if file_edits[fp]:
            entry['edits'] = file_edits[fp]
        if file_reads[fp]:
            entry['reads'] = file_reads[fp]
        recent_files.append(entry)
    # Sort by total activity
    recent_files.sort(
        key=lambda x: x.get('edits', 0) + x.get('reads', 0),
        reverse=True
    )

    return (narrative, recent_files[:15])


def format_for_post_compact_injection(
    project_dir: str = '.',
    checkpoint_path: str | None = None
) -> str | None:
    """Format checkpoint as a rich injection block for post-compaction context.

    Called by mnemos-post-compact-inject.sh after compaction is detected.
    Returns a structured block that Claude can parse and resume from.
    """
    if checkpoint_path:
        cp_path = Path(checkpoint_path)
    else:
        cp_path = Path(project_dir).resolve() / '.mnemos' / 'checkpoint-latest.json'

    if not cp_path.exists():
        return None

    try:
        data = json.loads(cp_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    lines = []
    lines.append('=== MNEMOS: CONTEXT RESTORED AFTER COMPACTION ===')
    lines.append('')
    lines.append('Compaction just occurred. Your previous context was summarized.')
    lines.append('Resume from this checkpoint -- DO NOT re-derive information already captured below.')
    lines.append('')

    # Goal
    lines.append('## Goal')
    lines.append(data.get('goal', 'No goal recorded'))
    lines.append('')

    # Constraints
    constraints = data.get('active_constraints', [])
    if constraints:
        lines.append('## Active Constraints (DO NOT VIOLATE)')
        for c in constraints:
            lines.append(f'- {c}')
        lines.append('')

    # Task narrative
    narrative = data.get('task_narrative', '')
    if narrative:
        lines.append('## What You Were Working On')
        lines.append(narrative)
        lines.append('')

    # Current sub-goal
    subgoal = data.get('current_subgoal', '')
    if subgoal:
        lines.append('## Current Sub-Goal')
        lines.append(subgoal)
        lines.append('')

    # Working memory
    working = data.get('working_memory', '')
    if working:
        lines.append('## Working Memory')
        lines.append(working)
        lines.append('')

    # Progress
    results = data.get('active_results', [])
    if results:
        lines.append('## Progress So Far')
        for r in results:
            lines.append(f'- {r}')
        lines.append('')

    # Recent files
    recent = data.get('recent_files', [])
    if recent:
        lines.append('## Key Files (from recent activity)')
        for f in recent[:10]:
            parts = []
            if f.get('edits', 0) > 0:
                parts.append(f'edited {f["edits"]}x')
            if f.get('reads', 0) > 0:
                parts.append(f'read {f["reads"]}x')
            detail = ', '.join(parts) if parts else 'touched'
            lines.append(f'- {f.get("path", "?")} ({detail})')
        lines.append('')

    # Git state
    git = data.get('git_state', {})
    if git.get('branch'):
        lines.append('## Git State')
        lines.append(f'Branch: {git["branch"]}')
        if git.get('uncommitted'):
            lines.append('Uncommitted:')
            for gf in git['uncommitted'][:10]:
                lines.append(f'  - {gf}')
        else:
            lines.append('Working tree clean.')
        lines.append('')

    # iCPG
    icpg = data.get('icpg_state')
    if icpg:
        lines.append('## iCPG Context')
        if icpg.get('active_reason'):
            lines.append(f'Active intent: {icpg["active_reason"]}')
        if icpg.get('unresolved_drift'):
            lines.append(f'Unresolved drift: {icpg["unresolved_drift"]}')
        lines.append('')

    # Checkpoint metadata
    lines.append(f'Checkpoint: {data.get("id", "?")[:8]} at {data.get("created_at", "?")}')
    lines.append(f'Fatigue at checkpoint: {data.get("fatigue_at_checkpoint", 0):.2f}')
    lines.append('')
    lines.append('=== Resume work from this checkpoint. Ask the user to confirm the task if unclear. ===')

    return '\n'.join(lines)


def write_compaction_marker(project_dir: str = '.') -> None:
    """Write the just-compacted marker file for post-compaction detection."""
    marker = Path(project_dir).resolve() / '.mnemos' / 'just-compacted'
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({
        'timestamp': time.time(),
        'reason': 'pre_compact_hook'
    }))


def check_compaction_marker(project_dir: str = '.') -> bool:
    """Check if a fresh compaction marker exists (< 5 minutes old)."""
    marker = Path(project_dir).resolve() / '.mnemos' / 'just-compacted'
    if not marker.exists():
        return False
    try:
        data = json.loads(marker.read_text())
        age = time.time() - data.get('timestamp', 0)
        return age < 300  # 5 minutes
    except (json.JSONDecodeError, OSError):
        return False


def consume_compaction_marker(project_dir: str = '.') -> bool:
    """Atomically consume the compaction marker (rename then delete).

    Returns True if marker was consumed, False if already consumed or missing.
    """
    marker = Path(project_dir).resolve() / '.mnemos' / 'just-compacted'
    consumed = marker.with_suffix('.consumed')
    try:
        marker.rename(consumed)
        consumed.unlink(missing_ok=True)
        return True
    except (OSError, FileNotFoundError):
        return False


def _checkpoint_to_dict(cp: CheckpointNode) -> dict:
    """Serialize CheckpointNode to JSON-safe dict."""
    return {
        'id': cp.id,
        'task_id': cp.task_id,
        'goal': cp.goal,
        'active_constraints': cp.active_constraints,
        'active_results': cp.active_results,
        'current_subgoal': cp.current_subgoal,
        'working_memory': cp.working_memory,
        'task_narrative': cp.task_narrative,
        'recent_files': cp.recent_files,
        'fatigue_at_checkpoint': cp.fatigue_at_checkpoint,
        'git_state': cp.git_state,
        'icpg_state': cp.icpg_state,
        'node_summary': cp.node_summary,
        'created_at': cp.created_at
    }
