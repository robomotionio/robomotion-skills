"""Data models for Mnemos -- MnemoNode, FatigueState, CheckpointNode."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


# --- MnemoNode types ---
MNEMO_TYPES = (
    'goal', 'constraint', 'context', 'working',
    'result', 'skill', 'checkpoint', 'handoff'
)

# --- MnemoNode statuses ---
MNEMO_STATUSES = (
    'active', 'compressed', 'evicted', 'promoted', 'handed_off'
)

# --- MnemoNode origins ---
MNEMO_ORIGINS = (
    'loaded', 'derived', 'tool_result',
    'inherited', 'agent_generated'
)

# --- Fatigue states ---
FATIGUE_STATES = (
    'flow', 'compress', 'pre_sleep', 'rem', 'emergency'
)

# --- Fatigue thresholds ---
FATIGUE_THRESHOLDS = {
    'flow': (0.0, 0.40),
    'compress': (0.40, 0.60),
    'pre_sleep': (0.60, 0.75),
    'rem': (0.75, 0.90),
    'emergency': (0.90, 1.0)
}

# --- Fatigue dimension weights ---
# All 4 dimensions are passively observable from hook data.
# No agent cooperation required.
FATIGUE_WEIGHTS = {
    'token_utilization': 0.40,  # from statusline context_window.used_percentage
    'scope_scatter': 0.25,      # unique dirs in recent tool calls (PreToolUse)
    'reread_ratio': 0.20,       # files Read more than once (PreToolUse)
    'error_density': 0.15       # failed tool calls ratio (PostToolUse)
}

# --- Eviction policies per type ---
# never = GoalNode/ConstraintNode survive all compaction
# compress_first = content replaced with summary before eviction
# evictable = can be evicted when cold
EVICTION_POLICIES = {
    'goal': 'never',
    'constraint': 'never',
    'context': 'evictable',
    'working': 'compress_first',
    'result': 'compress_first',
    'skill': 'compress_first',
    'checkpoint': 'never',
    'handoff': 'never'
}


@dataclass
class MnemoNode:
    """A typed memory node in the MnemoGraph.

    Types and eviction:
        goal        -- never evicted, task's primary objective
        constraint  -- never evicted, invariants and contracts
        context     -- evictable when activation_weight drops
        working     -- compressed first, then evicted
        result      -- compressed first (summary kept), then evicted
        skill       -- compressed first, promotable to persistent
        checkpoint  -- never evicted, serialized session state
        handoff     -- never evicted, task completion summary
    """

    type: str
    task_id: str
    content: str
    id: str = field(default_factory=_uuid)
    summary: str | None = None
    activation_weight: float = 1.0
    status: str = 'active'
    origin: str = 'agent_generated'
    confidence: float = 1.0
    scope_tags: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    last_accessed: str = field(default_factory=_now)
    access_count: int = 0

    @property
    def eviction_policy(self) -> str:
        return EVICTION_POLICIES.get(self.type, 'evictable')

    @property
    def is_evictable(self) -> bool:
        return self.eviction_policy == 'evictable'

    @property
    def is_compressible(self) -> bool:
        return self.eviction_policy == 'compress_first'


@dataclass
class FatigueState:
    """4-dimension fatigue model -- all dimensions passively observable.

    Dimensions (all derived from hook data, no agent cooperation needed):
        token_utilization  -- context_window.used_percentage / 100 (statusline)
        scope_scatter      -- unique dirs in recent tool calls (PreToolUse)
        reread_ratio       -- files Read'd more than once (PreToolUse)
        error_density      -- failed tool calls / total (PostToolUse)

    Composite score = weighted average, mapped to fatigue state.
    """

    token_utilization: float = 0.0
    scope_scatter: float = 0.0
    reread_ratio: float = 0.0
    error_density: float = 0.0
    composite_score: float = 0.0
    state: str = 'flow'
    computed_at: str = field(default_factory=_now)

    @staticmethod
    def score_to_state(score: float) -> str:
        """Map composite fatigue score to named state."""
        if score >= 0.90:
            return 'emergency'
        elif score >= 0.75:
            return 'rem'
        elif score >= 0.60:
            return 'pre_sleep'
        elif score >= 0.40:
            return 'compress'
        else:
            return 'flow'


@dataclass
class CheckpointNode:
    """Serialized session state for resume after compaction or restart.

    Always includes GoalNode content, all ConstraintNodes, current sub-goal.
    Optionally includes iCPG state (active ReasonNode, drift summary).
    """

    task_id: str
    goal: str
    id: str = field(default_factory=_uuid)
    active_constraints: list[str] = field(default_factory=list)
    active_results: list[str] = field(default_factory=list)
    current_subgoal: str = ''
    working_memory: str = ''
    task_narrative: str = ''
    recent_files: list[dict] = field(default_factory=list)
    fatigue_at_checkpoint: float = 0.0
    git_state: dict = field(default_factory=dict)
    icpg_state: dict | None = None
    node_summary: dict = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
