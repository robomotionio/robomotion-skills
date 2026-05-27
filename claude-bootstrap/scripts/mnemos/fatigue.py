"""4-dimension fatigue computation -- all dimensions passively observable.

Every dimension is derived from actual hook data (tool calls, file paths,
errors). No agent cooperation or manual input required.

Signals:
    1. Token utilization  -- statusline writes context_window.used_percentage
    2. Scope scatter      -- PreToolUse logs file paths -> unique dirs ratio
    3. Re-read ratio      -- PreToolUse logs Read calls -> duplicate file ratio
    4. Error density      -- PostToolUse logs success/failure -> error ratio
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import FATIGUE_WEIGHTS, FatigueState, _now
from .signals import (
    compute_error_density,
    compute_reread_ratio,
    compute_scope_scatter,
    read_recent_signals
)


def compute_fatigue(
    context_data: dict,
    project_dir: str = '.'
) -> FatigueState:
    """Compute 4-dimension fatigue score from observable signals.

    Args:
        context_data: Dict with used_percentage (from fatigue.json).
        project_dir: Project directory to read signals from.

    Returns:
        FatigueState with per-dimension scores and composite.
    """
    # Dimension 1: Token utilization (real -- from statusline)
    token_util = min(1.0, context_data.get('used_percentage', 0) / 100)

    # Read behavioral signals from hook log
    signals = read_recent_signals(project_dir)

    # Dimension 2: Scope scatter (real -- from PreToolUse file paths)
    scatter = compute_scope_scatter(signals)

    # Dimension 3: Re-read ratio (real -- from PreToolUse Read calls)
    reread = compute_reread_ratio(signals)

    # Dimension 4: Error density (real -- from PostToolUse outcomes)
    errors = compute_error_density(signals)

    # Weighted composite
    score = (
        FATIGUE_WEIGHTS['token_utilization'] * token_util
        + FATIGUE_WEIGHTS['scope_scatter'] * scatter
        + FATIGUE_WEIGHTS['reread_ratio'] * reread
        + FATIGUE_WEIGHTS['error_density'] * errors
    )
    score = min(1.0, max(0.0, score))

    state = FatigueState.score_to_state(score)

    return FatigueState(
        token_utilization=round(token_util, 4),
        scope_scatter=round(scatter, 4),
        reread_ratio=round(reread, 4),
        error_density=round(errors, 4),
        composite_score=round(score, 4),
        state=state,
        computed_at=_now()
    )


def read_fatigue_file(project_dir: str = '.') -> dict:
    """Read the live fatigue.json written by the statusline script.

    Returns dict with used_percentage, remaining_percentage, timestamp.
    Falls back to empty dict if file missing or corrupt.
    """
    fatigue_path = Path(project_dir).resolve() / '.mnemos' / 'fatigue.json'
    if not fatigue_path.exists():
        return {}
    try:
        return json.loads(fatigue_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def write_fatigue_file(
    project_dir: str, used_pct: float, remaining_pct: float
) -> None:
    """Write fatigue.json for hooks to read. Called by statusline."""
    import time
    mnemos_dir = Path(project_dir).resolve() / '.mnemos'
    mnemos_dir.mkdir(parents=True, exist_ok=True)
    data = {
        'used_percentage': used_pct,
        'remaining_percentage': remaining_pct,
        'timestamp': time.time()
    }
    fatigue_path = mnemos_dir / 'fatigue.json'
    fatigue_path.write_text(json.dumps(data))
