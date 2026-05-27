# Phase 2: Model-Tiered Routing (Blast Score -> Model)

**Status:** pending
**Priority:** P0 — enables intelligent model selection
**Effort:** Medium
**Dependencies:** Phase 1 (PiAdapter), iCPG (blast radius scoring)

---

## Scope

Route tasks to the optimal model based on iCPG blast radius score. High-blast tasks go to premium models, low-blast tasks go to cheap/local models. The routing table is seeded with hardcoded defaults and learns from task reward scores over time (L1 feedback loop).

## What Gets Built

1. **Blast-to-tier mapper** (`maggy/maggy/routing.py`)
   - Input: blast score (0-10) from iCPG, task type (auth, docs, tests, frontend, etc.)
   - Output: ordered list of candidate models
   - Default tiers: 0-3 cheap, 4-6 medium, 7-10 premium
   - Tier boundaries are adjustable via L4 monthly recalibration

2. **Reward table** (`maggy/maggy/scores.py`)
   - SQLite-backed: `model_scores.db`
   - Schema: `(model, task_type, blast_tier) → reward_avg, n_samples, last_updated`
   - Cold start: hardcoded defaults until 30+ samples per triple
   - Decay: `0.95^(days_since_event)` for aging out old data

3. **Routing integration with PiAdapter**
   - Before task execution: query routing table for best model
   - After task completion: update reward table from L1 task reward
   - On model failure mid-task: demote model score, try next in tier

4. **Dashboard widget**
   - Model performance heatmap: `(task_type × blast_tier)` grid with reward colors
   - Routing decisions log: which model was selected and why

## Deliverables

- [ ] `maggy/maggy/routing.py` — Blast-to-model routing logic
- [ ] `maggy/maggy/scores.py` — Reward table with SQLite persistence
- [ ] `maggy/maggy/api/routes_routing.py` — Routing status endpoint
- [ ] `tests/test_routing.py` — Routing decision tests
- [ ] `tests/test_scores.py` — Reward table CRUD + decay tests

## Success Criteria

- [ ] Blast 7+ tasks always routed to Claude or GPT-4o (premium)
- [ ] Blast 0-3 tasks routed to cheapest available model
- [ ] Reward table updates after every task completion
- [ ] After 50+ tasks, routing outperforms random assignment by >= 20%
- [ ] Tier boundaries can be reconfigured without code changes
- [ ] All tests pass, coverage >= 80%

## Risks

- Blast radius scoring requires iCPG to be active on the project — need fallback when iCPG is not initialized
- Initial routing will be suboptimal until reward data accumulates — use conservative defaults
