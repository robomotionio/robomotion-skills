# Phase 14: Event Spine — Canonical Event Flow

**Status:** pending
**Priority:** P2 — enables end-to-end tracing and reward attribution
**Effort:** Medium
**Dependencies:** Phase 12 (Engram) + Phase 13 (Lexon)

---

## Scope

Build the Event Spine: a single ordered event stream that every Maggy component writes to. Eight typed events with a common header enable end-to-end tracing, reward attribution, replay debugging, and self-improvement validation. The Event Spine is the nervous system connecting iCPG, Mnemos, Lexon, Engram, Process Intelligence, and Mesh.

## What Gets Built

1. **Common EventHeader** (`maggy/maggy/event_spine/header.py`)
   - Standard fields: event_id, event_type, task_id, project_id, agent_id, model_id
   - Correlation: confidence, namespace, policy_version, reward_delta
   - Causality: parent_event_id enables event DAG construction
   - Timestamps: ISO 8601

2. **Typed event dataclasses** (`maggy/maggy/event_spine/events.py`)
   - IntentEvent: iCPG ReasonNode decomposition
   - BindingEvent: Lexon tool selection + clarify mode
   - ExecutionEvent: tool invocation input/output/duration
   - MemoryEvent: Mnemos within-task memory write
   - PersistenceEvent: Engram cross-session promotion
   - OutcomeEvent: Process Intelligence success/failure + reward
   - MutationEvent: L2/L3/L4 self-modification
   - MeshEvent: cross-machine sharing + quarantine status

3. **Event emitter API** (`maggy/maggy/event_spine/emitter.py`)
   - `emit(event)` — write to append-only store
   - `query(task_id=, event_type=, project_id=)` — filtered retrieval
   - `trace(task_id)` — return full event chain for a task
   - Thread-safe, async-compatible

4. **SQLite event store** (`maggy/maggy/event_spine/store.py`)
   - Append-only write pattern
   - Indexed on task_id, event_type, project_id, timestamp
   - Retention policy: 90 days live, then archive to JSONL.gz
   - Archive manager for cold storage

## Deliverables

- [ ] `maggy/maggy/event_spine/__init__.py` — Public API
- [ ] `maggy/maggy/event_spine/header.py` — EventHeader dataclass
- [ ] `maggy/maggy/event_spine/events.py` — 8 typed event dataclasses
- [ ] `maggy/maggy/event_spine/emitter.py` — Emission + query API
- [ ] `maggy/maggy/event_spine/store.py` — SQLite store + archive
- [ ] `maggy/maggy/api/routes_events.py` — REST endpoints
- [ ] `tests/test_event_header.py` — Header validation tests
- [ ] `tests/test_event_emitter.py` — Emit + query + trace tests
- [ ] `tests/test_event_store.py` — SQLite persistence + archive tests
- [ ] `tests/test_event_integration.py` — End-to-end event flow tests

## Success Criteria

- [ ] All 8 event types emit correctly with valid headers
- [ ] `trace(task_id)` returns ordered event chain across all types
- [ ] Reward attribution: OutcomeEvent.reward links back to BindingEvent
- [ ] SQLite store handles 10K events/day without performance degradation
- [ ] Archive compresses events older than 90 days to JSONL.gz
- [ ] Event correlation works across iCPG → Lexon → Mnemos → Engram flow
- [ ] All tests pass, coverage >= 80%

## Risks

- High event volume from active teams — batch writes, WAL mode for SQLite
- Event schema versioning as components evolve — include schema_version in header
- Replay fidelity depends on deterministic event ordering — use monotonic timestamps
