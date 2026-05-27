"""Git history inference — bootstrap iCPG from existing commits.

Implements RFC Section 7.2: replay commit history, cluster by PR or
temporal proximity, infer ReasonNodes via LLM, create CREATES/MODIFIES
edges.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .contracts import infer_contracts
from .models import Edge, ReasonNode, _now, _uuid
from .store import ICPGStore
from .symbols import extract_symbols
from .vectors import VectorStore


def bootstrap_from_git(
    store: ICPGStore,
    days: int = 90,
    use_llm: bool = True,
    verbose: bool = False
) -> dict:
    """Infer ReasonNodes from git commit history.

    Returns stats dict: {clusters, reasons_created, symbols_linked, skipped}.
    """
    vectors = VectorStore(str(store.project_dir))
    since = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).strftime('%Y-%m-%d')

    # Step 1: Get commits
    commits = _get_commits(store.project_dir, since)
    if verbose:
        print(f'Found {len(commits)} commits in last {days} days')

    if not commits:
        return {'clusters': 0, 'reasons_created': 0, 'symbols_linked': 0}

    # Step 2: Cluster commits
    clusters = _cluster_commits(commits)
    if verbose:
        print(f'Clustered into {len(clusters)} groups')

    stats = {'clusters': len(clusters), 'reasons_created': 0, 'symbols_linked': 0, 'skipped': 0}

    for cluster in clusters:
        # Step 3: Extract info from cluster
        messages = [c['message'] for c in cluster]
        files_changed = set()
        for c in cluster:
            files_changed.update(c.get('files', []))

        combined_message = '\n'.join(messages)

        # Step 4: Check for duplicates
        similar = vectors.search_similar(combined_message, threshold=0.8)
        if similar:
            stats['skipped'] += 1
            if verbose:
                print(f'  Skipping cluster (duplicate of {similar[0][0]})')
            continue

        # Step 5: Infer ReasonNode
        if use_llm:
            reason = _infer_via_llm(combined_message, list(files_changed))
        else:
            reason = _infer_from_messages(combined_message, list(files_changed))

        if not reason:
            stats['skipped'] += 1
            continue

        # Step 6: Create reason and index
        store.create_reason(reason)
        vectors.add_reason(reason.id, reason.goal, reason.scope)
        stats['reasons_created'] += 1

        if verbose:
            print(f'  Created: {reason.goal[:60]}...')

        # Step 7: Link symbols
        for fp in files_changed:
            full_path = store.project_dir / fp
            if not full_path.exists():
                continue
            syms = extract_symbols(str(full_path))
            for sym in syms:
                store.upsert_symbol(sym)
                edge = Edge(
                    from_id=reason.id,
                    to_id=sym.id,
                    edge_type='CREATES',
                    confidence=0.6
                )
                store.create_edge(edge)
                stats['symbols_linked'] += 1

        # Step 8: Infer contracts (if LLM available)
        if use_llm and not reason.postconditions:
            contracts = infer_contracts(reason, project_dir=str(store.project_dir))
            if any(contracts.values()):
                reason.preconditions = contracts['preconditions']
                reason.postconditions = contracts['postconditions']
                reason.invariants = contracts['invariants']
                # Update in DB
                with store._conn() as conn:
                    conn.execute(
                        """UPDATE reasons SET
                           preconditions = ?, postconditions = ?, invariants = ?
                           WHERE id = ?""",
                        (
                            json.dumps(reason.preconditions),
                            json.dumps(reason.postconditions),
                            json.dumps(reason.invariants),
                            reason.id
                        )
                    )

    return stats


def _get_commits(project_dir: Path, since: str) -> list[dict]:
    """Get commits with messages and changed files."""
    try:
        result = subprocess.run(
            [
                'git', 'log', f'--since={since}',
                '--format=__COMMIT__%n%H%n%an%n%aI%n%s',
                '--name-only'
            ],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_dir)
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

    if result.returncode != 0:
        return []

    commits = []
    raw_blocks = result.stdout.split('__COMMIT__\n')

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        if len(lines) < 4:
            continue

        sha = lines[0].strip()
        author = lines[1].strip()
        date = lines[2].strip()
        message = lines[3].strip()

        # Files come after a blank line separator
        files = []
        past_blank = False
        for line in lines[4:]:
            stripped = line.strip()
            if not stripped:
                past_blank = True
                continue
            if past_blank and stripped:
                files.append(stripped)

        commits.append({
            'sha': sha,
            'author': author,
            'date': date,
            'message': message,
            'files': files
        })

    return commits


def _cluster_commits(
    commits: list[dict], window_hours: int = 2
) -> list[list[dict]]:
    """Cluster commits by temporal proximity."""
    if not commits:
        return []

    clusters = []
    current_cluster = [commits[0]]

    for commit in commits[1:]:
        try:
            prev_date = datetime.fromisoformat(
                current_cluster[-1]['date'].replace('Z', '+00:00')
            )
            curr_date = datetime.fromisoformat(
                commit['date'].replace('Z', '+00:00')
            )
            delta = abs((curr_date - prev_date).total_seconds())

            if delta <= window_hours * 3600:
                current_cluster.append(commit)
            else:
                clusters.append(current_cluster)
                current_cluster = [commit]
        except (ValueError, KeyError):
            clusters.append(current_cluster)
            current_cluster = [commit]

    if current_cluster:
        clusters.append(current_cluster)

    return clusters


def _infer_via_llm(
    messages: str, files: list[str]
) -> ReasonNode | None:
    """Use LLM to infer a ReasonNode from commit messages."""
    scope_str = ', '.join(files[:20])
    prompt = f"""Given these git commit messages, infer the intent/goal.

COMMITS:
{messages[:2000]}

FILES CHANGED:
{scope_str}

Return ONLY a JSON object:
{{
  "goal": "one-sentence description of what this change was trying to achieve",
  "decision_type": "task|business_goal|arch_decision|workaround|constraint|patch",
  "scope": ["file1", "file2"]
}}"""

    # Try Claude CLI
    try:
        result = subprocess.run(
            ['claude', '--print', '-p', prompt],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return _parse_reason_response(result.stdout, files)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try OpenAI
    try:
        import openai
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2
        )
        content = response.choices[0].message.content or ''
        return _parse_reason_response(content, files)
    except Exception:
        pass

    # Fallback
    return _infer_from_messages(messages, files)


def _infer_from_messages(
    messages: str, files: list[str]
) -> ReasonNode | None:
    """Extract ReasonNode from commit messages without LLM."""
    # Use first line as goal
    first_line = messages.split('\n')[0].strip()
    if not first_line:
        return None

    # Detect decision type from conventional commits
    dtype = 'task'
    if first_line.startswith('feat'):
        dtype = 'business_goal'
    elif first_line.startswith('fix'):
        dtype = 'patch'
    elif first_line.startswith('refactor'):
        dtype = 'arch_decision'
    elif first_line.startswith('chore') or first_line.startswith('ci'):
        dtype = 'constraint'

    # Clean up conventional commit prefix
    goal = re.sub(r'^(feat|fix|refactor|chore|ci|docs|test)(\([^)]*\))?:\s*', '', first_line)

    return ReasonNode(
        id=_uuid(),
        goal=goal or first_line,
        decision_type=dtype,
        scope=files[:20],
        owner='git-history',
        source='inferred',
        status='fulfilled',
        created_at=_now()
    )


def _parse_reason_response(
    response: str, fallback_files: list[str]
) -> ReasonNode | None:
    """Parse LLM response into a ReasonNode."""
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(response[start:end])
            return ReasonNode(
                id=_uuid(),
                goal=data.get('goal', ''),
                decision_type=data.get('decision_type', 'task'),
                scope=data.get('scope', fallback_files[:20]),
                owner='git-history',
                source='inferred',
                status='fulfilled',
                created_at=_now()
            )
    except (json.JSONDecodeError, KeyError):
        pass
    return None
