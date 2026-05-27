"""CLI entry point for iCPG — Intent-Augmented Code Property Graph."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .bootstrap import bootstrap_from_git
from .contracts import format_contracts, infer_contracts
from .drift import check_all_drift, check_file_drift
from .models import Edge, ReasonNode, _now, _uuid
from .store import ICPGStore
from .symbols import extract_symbols, extract_symbols_from_files
from .vectors import VectorStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='icpg',
        description='iCPG — Intent-Augmented Code Property Graph'
    )
    parser.add_argument(
        '--version', action='version', version=f'icpg {__version__}'
    )
    parser.add_argument(
        '--project', default='.', help='Project directory (default: .)'
    )
    sub = parser.add_subparsers(dest='command')

    # --- init ---
    sub.add_parser('init', help='Initialize .icpg/ directory and database')

    # --- create ---
    p_create = sub.add_parser('create', help='Create a ReasonNode')
    p_create.add_argument('goal', help='Stated purpose (one sentence)')
    p_create.add_argument(
        '--scope', nargs='+', default=[], help='File paths in scope'
    )
    p_create.add_argument('--owner', default='user', help='Owner name')
    p_create.add_argument('--agent', help='Agent identity')
    p_create.add_argument(
        '--type', dest='decision_type', default='task',
        choices=[
            'business_goal', 'arch_decision', 'task',
            'workaround', 'constraint', 'patch'
        ]
    )
    p_create.add_argument('--task-id', help='External task tracker ID')
    p_create.add_argument('--parent', help='Parent ReasonNode ID')
    p_create.add_argument(
        '--infer-contracts', action='store_true',
        help='Use LLM to infer contracts'
    )

    # --- record ---
    p_record = sub.add_parser(
        'record', help='Record symbols from git diff to a ReasonNode'
    )
    p_record.add_argument('--reason', required=True, help='ReasonNode ID')
    p_record.add_argument(
        '--base', default='main', help='Base branch for diff'
    )
    p_record.add_argument(
        '--edge-type', default='CREATES',
        choices=['CREATES', 'MODIFIES'],
        help='Edge type (default: CREATES)'
    )

    # --- query ---
    p_query = sub.add_parser('query', help='Query the reason graph')
    q_sub = p_query.add_subparsers(dest='query_type')

    q_ctx = q_sub.add_parser(
        'context', help='Get ReasonNodes for symbols in a file'
    )
    q_ctx.add_argument('file', help='File path')

    q_blast = q_sub.add_parser(
        'blast', help='Blast radius for a ReasonNode'
    )
    q_blast.add_argument('reason_id', help='ReasonNode ID')

    q_const = q_sub.add_parser(
        'constraints', help='Get invariants/contracts for file'
    )
    q_const.add_argument('file', help='File path')

    q_risk = q_sub.add_parser(
        'risk', help='Risk profile for a symbol'
    )
    q_risk.add_argument('symbol', help='Symbol name')

    q_prior = q_sub.add_parser(
        'prior', help='Search for duplicate/prior intents'
    )
    q_prior.add_argument('goal', help='Goal text to search')
    q_prior.add_argument(
        '--threshold', type=float, default=0.75,
        help='Similarity threshold (0-1, default: 0.75)'
    )

    # --- drift ---
    p_drift = sub.add_parser('drift', help='Drift detection')
    d_sub = p_drift.add_subparsers(dest='drift_action')
    d_sub.add_parser('check', help='Run full drift scan')
    d_file = d_sub.add_parser('file', help='Check drift for a single file (fast)')
    d_file.add_argument('file_path', help='File path to check')
    d_resolve = d_sub.add_parser('resolve', help='Resolve a drift event')
    d_resolve.add_argument('event_id', help='Drift event ID')

    # --- bootstrap ---
    p_boot = sub.add_parser(
        'bootstrap', help='Infer ReasonNodes from git history'
    )
    p_boot.add_argument(
        '--days', type=int, default=90, help='Days of history (default: 90)'
    )
    p_boot.add_argument(
        '--no-llm', action='store_true', help='Skip LLM inference'
    )
    p_boot.add_argument(
        '--verbose', '-v', action='store_true', help='Verbose output'
    )

    # --- status ---
    sub.add_parser('status', help='Show iCPG statistics')

    args = parser.parse_args(argv)
    store = ICPGStore(args.project)

    if args.command == 'init':
        return cmd_init(store)
    elif args.command == 'create':
        return cmd_create(store, args)
    elif args.command == 'record':
        return cmd_record(store, args)
    elif args.command == 'query':
        return cmd_query(store, args)
    elif args.command == 'drift':
        return cmd_drift(store, args)
    elif args.command == 'bootstrap':
        return cmd_bootstrap(store, args)
    elif args.command == 'status':
        return cmd_status(store)
    else:
        parser.print_help()
        return 1


def cmd_init(store: ICPGStore) -> int:
    store.init_db()
    print(f'Initialized iCPG at {store.icpg_dir}')
    print(f'  Database: {store.db_path}')
    print(f'  .gitignore: created')
    return 0


def cmd_create(store: ICPGStore, args) -> int:
    if not store.exists():
        store.init_db()

    reason = ReasonNode(
        goal=args.goal,
        owner=args.owner,
        decision_type=args.decision_type,
        scope=args.scope,
        agent=args.agent,
        task_id=args.task_id,
        parent_id=args.parent,
        source='agent-session' if args.agent else 'manual'
    )

    if args.infer_contracts:
        contracts = infer_contracts(reason, project_dir=args.project)
        reason.preconditions = contracts['preconditions']
        reason.postconditions = contracts['postconditions']
        reason.invariants = contracts['invariants']

    store.create_reason(reason)

    # Index in vector store
    vectors = VectorStore(args.project)
    vectors.add_reason(reason.id, reason.goal, reason.scope)

    print(f'Created ReasonNode: {reason.id}')
    print(f'  Goal: {reason.goal}')
    print(f'  Scope: {", ".join(reason.scope) or "(none)"}')
    if reason.invariants:
        print(f'  Invariants: {len(reason.invariants)}')
    return 0


def cmd_record(store: ICPGStore, args) -> int:
    if not store.exists():
        print('Error: No .icpg/ directory. Run `icpg init` first.', file=sys.stderr)
        return 1

    reason = store.get_reason(args.reason)
    if not reason:
        print(f'Error: ReasonNode {args.reason} not found.', file=sys.stderr)
        return 1

    # Get changed files from git diff
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', args.base],
            capture_output=True, text=True, timeout=10,
            cwd=str(store.project_dir)
        )
        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print('Error: git diff failed.', file=sys.stderr)
        return 1

    if not files:
        print('No changed files found.')
        return 0

    count = 0
    for fp in files:
        full_path = store.project_dir / fp
        if not full_path.exists():
            continue
        syms = extract_symbols(str(full_path))
        for sym in syms:
            store.upsert_symbol(sym)
            edge = Edge(
                from_id=reason.id,
                to_id=sym.id,
                edge_type=args.edge_type,
                confidence=1.0
            )
            store.create_edge(edge)
            count += 1

    # Update reason status
    store.update_reason_status(reason.id, 'executing')

    print(f'Recorded {count} symbols → ReasonNode {args.reason}')
    print(f'  Files: {len(files)}')
    print(f'  Edge type: {args.edge_type}')
    return 0


def cmd_query(store: ICPGStore, args) -> int:
    if not store.exists():
        return 0  # Silent — no DB means no context

    if args.query_type == 'context':
        return _query_context(store, args.file)
    elif args.query_type == 'blast':
        return _query_blast(store, args.reason_id)
    elif args.query_type == 'constraints':
        return _query_constraints(store, args.file)
    elif args.query_type == 'risk':
        return _query_risk(store, args.symbol)
    elif args.query_type == 'prior':
        return _query_prior(store, args)
    else:
        print('Specify a query type: context, blast, constraints, risk, prior')
        return 1


def _resolve_path(store: ICPGStore, file_path: str) -> str:
    """Resolve relative paths to absolute, matching DB storage format."""
    p = Path(file_path)
    if not p.is_absolute():
        p = store.project_dir / p
    return str(p.resolve())


def _query_context(store: ICPGStore, file_path: str) -> int:
    resolved = _resolve_path(store, file_path)
    reasons = store.get_reasons_for_file(resolved)
    if not reasons:
        return 0

    print(f'INTENTS for {file_path}:')
    for r in reasons:
        status_icon = {
            'proposed': '?', 'executing': '>', 'fulfilled': '+',
            'drifted': '!', 'rejected': 'x', 'abandoned': '-'
        }.get(r.status, ' ')
        print(f'  [{status_icon}] {r.id[:8]} — {r.goal}')
        print(f'      Owner: {r.owner} | Status: {r.status}')
        if r.invariants:
            print(f'      Invariants: {len(r.invariants)}')
    return 0


def _query_blast(store: ICPGStore, reason_id: str) -> int:
    blast = store.get_blast_radius(reason_id)
    reason = blast.get('reason')
    if not reason:
        print(f'ReasonNode {reason_id} not found.', file=sys.stderr)
        return 1

    print(f'BLAST RADIUS for {reason.goal}:')
    print(f'  Symbols: {blast["symbol_count"]}')
    for sym in blast['symbols']:
        print(f'    {sym.symbol_type} {sym.name} ({sym.file_path})')
    print(f'  Dependent intents: {blast["dependent_count"]}')
    for dep in blast['dependent_reasons']:
        print(f'    {dep.id[:8]} — {dep.goal}')
    if reason.invariants:
        print(f'  Invariants:')
        for inv in reason.invariants:
            print(f'    - {inv}')
    return 0


def _query_constraints(store: ICPGStore, file_path: str) -> int:
    resolved = _resolve_path(store, file_path)
    constraints = store.get_constraints_for_scope([resolved])
    if not constraints:
        return 0

    print(f'CONSTRAINTS for {file_path}:')
    for c in constraints:
        print(f'  From intent: {c["goal"][:60]}')
        for inv in c['invariants']:
            print(f'    INV: {inv}')
        for post in c['postconditions']:
            print(f'    POST: {post}')
        for pre in c['preconditions']:
            print(f'    PRE: {pre}')
    return 0


def _query_risk(store: ICPGStore, symbol_name: str) -> int:
    profile = store.get_risk_profile(symbol_name)
    if not profile.get('found'):
        return 0

    sym = profile['symbol']
    print(f'RISK PROFILE for {symbol_name}:')
    print(f'  File: {sym.file_path}')
    print(f'  Type: {sym.symbol_type}')
    print(f'  Owners: {", ".join(profile["owners"])}')
    print(f'  Modifications: {profile["modify_count"]}')
    print(f'  Active drift: {"YES" if profile["active_drift"] else "no"}')

    if profile['drift_events']:
        print(f'  Drift history:')
        for de in profile['drift_events'][:5]:
            status = 'resolved' if de.resolved else 'ACTIVE'
            print(f'    [{status}] {de.description} (severity: {de.severity})')
    return 0


def _query_prior(store: ICPGStore, args) -> int:
    vectors = VectorStore(args.project)
    similar = vectors.search_similar(args.goal, threshold=args.threshold)

    if not similar:
        print('No similar prior intents found.')
        return 0

    print(f'SIMILAR INTENTS (threshold: {args.threshold}):')
    for rid, score in similar:
        reason = store.get_reason(rid)
        if reason:
            print(f'  [{score:.2f}] {reason.id[:8]} — {reason.goal}')
            print(f'         Status: {reason.status} | Owner: {reason.owner}')
    return 0


def cmd_drift(store: ICPGStore, args) -> int:
    if not store.exists():
        print('No .icpg/ directory. Run `icpg init` first.', file=sys.stderr)
        return 1

    if args.drift_action == 'check':
        events = check_all_drift(store)
        if not events:
            print('No drift detected.')
            return 0

        # Save new events
        for event in events:
            store.create_drift_event(event)

        print(f'DRIFT DETECTED ({len(events)} events):')
        for e in events:
            dims = ', '.join(e.drift_dimensions)
            print(f'  [{e.severity:.2f}] {e.description}')
            print(f'         Dimensions: {dims}')
        return 0

    elif args.drift_action == 'file':
        resolved = _resolve_path(store, args.file_path)
        events = check_file_drift(store, resolved)
        if not events:
            return 0

        # Persist events
        for event in events:
            store.create_drift_event(event)

        basename = Path(resolved).name
        print(f'DRIFT: {len(events)} symbols drifted in {basename}')
        for e in events:
            sym = store._get_symbol(e.symbol_id)
            name = sym.name if sym else '???'
            dims = ', '.join(
                f'{d}({s:.2f})'
                for d, s in zip(e.drift_dimensions, _drift_scores(e))
            )
            print(f'  [{e.severity:.2f}] {name} — {dims}')
        return 0

    elif args.drift_action == 'resolve':
        store.resolve_drift(args.event_id)
        print(f'Resolved drift event {args.event_id}')
        return 0

    else:
        print('Specify: drift check, drift file <path>, or drift resolve <id>')
        return 1


def _drift_scores(event) -> list[float]:
    """Extract per-dimension scores from drift event description."""
    import re
    scores = []
    for match in re.finditer(r'\w+\((\d+\.\d+)\)', event.description):
        scores.append(float(match.group(1)))
    if not scores:
        scores = [event.severity] * len(event.drift_dimensions)
    return scores


def cmd_bootstrap(store: ICPGStore, args) -> int:
    if not store.exists():
        store.init_db()

    print(f'Bootstrapping iCPG from last {args.days} days of git history...')
    stats = bootstrap_from_git(
        store,
        days=args.days,
        use_llm=not args.no_llm,
        verbose=args.verbose
    )

    print(f'\nBootstrap complete:')
    print(f'  Commit clusters: {stats["clusters"]}')
    print(f'  ReasonNodes created: {stats["reasons_created"]}')
    print(f'  Symbols linked: {stats["symbols_linked"]}')
    if stats.get('skipped'):
        print(f'  Skipped (duplicates): {stats["skipped"]}')
    return 0


def cmd_status(store: ICPGStore) -> int:
    if not store.exists():
        print('No iCPG database found. Run `icpg init` to create one.')
        return 0

    stats = store.get_stats()
    drift = store.get_unresolved_drift()

    print('iCPG STATUS')
    print(f'  ReasonNodes:      {stats["reasons"]}')
    print(f'  Symbols:          {stats["symbols"]}')
    print(f'  Edges:            {stats["edges"]}')
    print(f'  Unresolved drift: {stats["unresolved_drift"]}')

    if drift:
        print(f'\nTop drift events:')
        for d in drift[:5]:
            dims = ', '.join(d.drift_dimensions)
            print(f'  [{d.severity:.2f}] {d.description} ({dims})')

    return 0


if __name__ == '__main__':
    sys.exit(main())
