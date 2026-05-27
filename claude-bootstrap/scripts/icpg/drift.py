"""6-dimension drift detection per RFC Section 6."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .models import DriftEvent, Edge, _now, _uuid
from .store import ICPGStore
from .symbols import extract_symbols


def check_file_drift(store: ICPGStore, file_path: str) -> list[DriftEvent]:
    """Check drift for symbols in a single file only. Fast path for hooks."""
    symbols = store.get_symbols_for_file(file_path)
    events = []
    for sym in symbols:
        event = check_symbol_drift(store, sym.id)
        if event:
            events.append(event)
    return events


def check_all_drift(store: ICPGStore) -> list[DriftEvent]:
    """Full drift scan across all tracked symbols."""
    events = []
    reasons = store.list_reasons()

    for reason in reasons:
        if reason.status in ('rejected', 'abandoned'):
            continue

        creates_edges = store.get_edges_from(reason.id, 'CREATES')
        for edge in creates_edges:
            sym = store._get_symbol(edge.to_id)
            if not sym:
                continue
            event = check_symbol_drift(store, sym.id)
            if event:
                events.append(event)

    return events


def check_symbol_drift(
    store: ICPGStore, symbol_id: str
) -> DriftEvent | None:
    """Check a single symbol for drift across all 6 dimensions."""
    sym = store._get_symbol(symbol_id)
    if not sym:
        return None

    # Find creating reason
    creates_edges = store.get_edges_to(symbol_id, 'CREATES')
    if not creates_edges:
        return None
    reason = store.get_reason(creates_edges[0].from_id)
    if not reason:
        return None

    dimensions = []
    severity_scores = []

    # 1. Spec drift — checksum changed without MODIFIES edge
    spec = _check_spec_drift(store, sym, reason)
    if spec:
        dimensions.append('spec')
        severity_scores.append(spec)

    # 2. Decision drift — postconditions no longer hold
    decision = _check_decision_drift(store, reason)
    if decision:
        dimensions.append('decision')
        severity_scores.append(decision)

    # 3. Ownership drift — >3 different owners
    ownership = _check_ownership_drift(store, sym)
    if ownership:
        dimensions.append('ownership')
        severity_scores.append(ownership)

    # 4. Test drift — VALIDATED_BY tests missing or failing
    test = _check_test_drift(store, reason)
    if test:
        dimensions.append('test')
        severity_scores.append(test)

    # 5. Usage drift — used outside original scope
    usage = _check_usage_drift(store, sym, reason)
    if usage:
        dimensions.append('usage')
        severity_scores.append(usage)

    # 6. Dependency drift — downstream coupling changed
    dep = _check_dependency_drift(store, reason)
    if dep:
        dimensions.append('dependency')
        severity_scores.append(dep)

    if not dimensions:
        return None

    avg_severity = sum(severity_scores) / len(severity_scores)
    desc_parts = [f'{d}({s:.2f})' for d, s in zip(dimensions, severity_scores)]

    return DriftEvent(
        id=_uuid(),
        symbol_id=symbol_id,
        from_reason_id=reason.id,
        drift_dimensions=dimensions,
        severity=round(avg_severity, 2),
        description=f'Drift detected: {", ".join(desc_parts)}',
        detected_at=_now()
    )


def _check_spec_drift(store, sym, reason) -> float | None:
    """Symbol checksum changed since creation without a MODIFIES edge."""
    # Re-extract current symbol
    current_symbols = extract_symbols(sym.file_path)
    current = next((s for s in current_symbols if s.name == sym.name), None)
    if not current:
        return 0.8  # Symbol removed entirely

    if current.checksum != sym.checksum:
        # Check if there's a MODIFIES edge explaining the change
        mod_edges = store.get_edges_to(sym.id, 'MODIFIES')
        if not mod_edges:
            return 0.6  # Changed without explanation
    return None


def _check_decision_drift(store, reason) -> float | None:
    """ReasonNode postconditions no longer hold."""
    if not reason.postconditions:
        return None

    failed = 0
    for predicate in reason.postconditions:
        if not evaluate_predicate(predicate, store.project_dir):
            failed += 1

    if failed > 0:
        return min(1.0, failed / len(reason.postconditions))
    return None


def _check_ownership_drift(store, sym) -> float | None:
    """Symbol touched by >3 different owners."""
    edges = store.get_edges_to(sym.id)
    owners = set()
    for edge in edges:
        reason = store.get_reason(edge.from_id)
        if reason:
            owners.add(reason.owner)

    if len(owners) > 3:
        return min(1.0, (len(owners) - 3) / 5)
    return None


def _check_test_drift(store, reason) -> float | None:
    """VALIDATED_BY tests no longer exist or fail."""
    test_edges = store.get_edges_from(reason.id, 'VALIDATED_BY')
    if not test_edges:
        # No tests linked — mild concern
        return 0.3

    missing = 0
    for edge in test_edges:
        test_sym = store._get_symbol(edge.to_id)
        if not test_sym or not Path(test_sym.file_path).exists():
            missing += 1

    if missing > 0:
        return min(1.0, missing / len(test_edges))
    return None


def _check_usage_drift(store, sym, reason) -> float | None:
    """Symbol imported from scopes outside original ReasonNode scope."""
    if not reason.scope:
        return None

    # Use grep to find imports/usages of the symbol
    try:
        result = subprocess.run(
            ['grep', '-rl', sym.name, '.'],
            capture_output=True, text=True, timeout=5,
            cwd=str(store.project_dir)
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    if result.returncode != 0:
        return None

    usage_files = [
        f.strip().lstrip('./') for f in result.stdout.strip().split('\n')
        if f.strip()
    ]

    out_of_scope = 0
    for uf in usage_files:
        if not any(uf.startswith(s.rstrip('/')) for s in reason.scope):
            out_of_scope += 1

    if out_of_scope > 2:
        return min(1.0, out_of_scope / 10)
    return None


def _check_dependency_drift(store, reason) -> float | None:
    """Downstream REQUIRES reasons have drifted or changed status."""
    req_edges = store.get_edges_to(reason.id, 'REQUIRES')
    if not req_edges:
        return None

    drifted = 0
    for edge in req_edges:
        dep_reason = store.get_reason(edge.from_id)
        if dep_reason and dep_reason.status == 'drifted':
            drifted += 1

    if drifted > 0:
        return min(1.0, drifted / len(req_edges))
    return None


def evaluate_predicate(predicate: str, project_dir: Path) -> bool:
    """Evaluate a single structured predicate against codebase state.

    Supported predicates:
        file_exists("path")
        test_exists("path")
        symbol_count("dir/") <= N
        function_signature("name") == "sig"
    """
    predicate = predicate.strip()

    # file_exists("path")
    m = _match_predicate(predicate, 'file_exists')
    if m:
        return (project_dir / m).exists()

    # test_exists("path")
    m = _match_predicate(predicate, 'test_exists')
    if m:
        return (project_dir / m).exists()

    # symbol_count("dir/") <= N
    import re
    sc = re.match(
        r'symbol_count\("([^"]+)"\)\s*(<=|>=|==|<|>)\s*(\d+)', predicate
    )
    if sc:
        dir_path, op, threshold = sc.group(1), sc.group(2), int(sc.group(3))
        count = _count_symbols_in_dir(project_dir / dir_path)
        return _compare(count, op, threshold)

    # Unrecognized predicate — pass (don't block on unknown)
    return True


def _match_predicate(predicate: str, func_name: str) -> str | None:
    import re
    m = re.match(rf'{func_name}\("([^"]+)"\)', predicate)
    return m.group(1) if m else None


def _count_symbols_in_dir(dir_path: Path) -> int:
    if not dir_path.is_dir():
        return 0
    count = 0
    for f in dir_path.rglob('*'):
        if f.is_file():
            count += len(extract_symbols(str(f)))
    return count


def _compare(value: int, op: str, threshold: int) -> bool:
    ops = {
        '<=': value <= threshold,
        '>=': value >= threshold,
        '==': value == threshold,
        '<': value < threshold,
        '>': value > threshold,
    }
    return ops.get(op, True)
