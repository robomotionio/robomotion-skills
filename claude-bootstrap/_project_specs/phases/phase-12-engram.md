# Phase 12: Engram — Cross-Session Memory Persistence

**Status:** pending
**Priority:** P1 — fills the cross-session memory gap
**Effort:** Large
**Dependencies:** Phase 3 (Mnemos multi-model) + Phase 5 (Maggy v2 UI)

---

## Scope

Build Engram: the cross-session memory layer that persists learned knowledge across Maggy sessions. Engram sits between Mnemos (within-task memory) and Mesh (cross-machine sharing), completing the memory lifecycle. It diagnoses amnesia pathologies, enforces namespace isolation between projects, and provides multi-path retrieval across semantic, temporal, causal, and entity dimensions.

## What Gets Built

1. **EngramRecord schema** (`maggy/maggy/engram/record.py`)
   - Core primitive: content, origin, confidence, temporal validity, entity/causal links
   - Origin tracking: source_type, source_id, channel, original_evidence
   - Temporal validity: valid_from, valid_until, superseded_by, decay_rate
   - Memory types: convention, preference, pattern, tool_config, reviewer_preference, codebase_idiom, process_rule

2. **Namespace-isolated store** (`maggy/maggy/engram/store.py`)
   - SQLite-backed: `~/.maggy/engram.db`
   - Per-project namespaces with configurable isolation (strict, readable)
   - Shared namespace for org-wide conventions
   - Confidence decay: `confidence *= (1 - decay_rate)^days_since_verified`
   - CRUD: create, read, update_confidence, supersede, expire

3. **Multi-path retrieval** (`maggy/maggy/engram/retrieval.py`)
   - Four retrieval paths: semantic, temporal, causal, entity
   - Semantic: embedding similarity against EngramRecord content
   - Temporal: recency-weighted, respects validity windows
   - Causal: follows causal_links for cause-effect chains
   - Entity: follows entity_links for file/function associations
   - Merge and rank: `confidence * recency * path_match_score`

4. **Amnesia diagnostics** (`maggy/maggy/engram/diagnostics.py`)
   - 7-dimension AmnesiaProfile per project
   - Dimensions: anterograde, retrograde, temporal, source, interference, context_binding, confabulation
   - Measurement: sample past sessions, label memory retention per dimension
   - L3 integration: weekly analysis triggers encoding rule patches

5. **Mnemos → Engram promotion pipeline**
   - After task completion, scan Mnemos graph for high-confidence memories
   - Promotion criteria: confidence > 0.8, evidence_count >= 3
   - Auto-assign namespace based on active project
   - Auto-populate entity_links from Mnemos file references

6. **Dashboard panel**
   - Per-project Amnesia Score visualization (7-dimension radar chart)
   - EngramRecord browser: search, filter by namespace/type/confidence
   - Memory health trend: is retention improving over time?

## Deliverables

- [ ] `maggy/maggy/engram/record.py` — EngramRecord + Origin + Validity dataclasses
- [ ] `maggy/maggy/engram/store.py` — SQLite persistence with namespace isolation
- [ ] `maggy/maggy/engram/retrieval.py` — Multi-path retrieval engine
- [ ] `maggy/maggy/engram/diagnostics.py` — Amnesia Score computation
- [ ] `maggy/maggy/engram/__init__.py` — Public API
- [ ] `maggy/maggy/api/routes_engram.py` — REST endpoints
- [ ] `skills/engram/SKILL.md` — Agent instructions for memory persistence
- [ ] `~/.maggy/engram_namespaces.yaml` template
- [ ] `tests/test_engram_record.py` — EngramRecord schema tests
- [ ] `tests/test_engram_store.py` — Store CRUD + namespace isolation tests
- [ ] `tests/test_engram_retrieval.py` — Multi-path retrieval tests
- [ ] `tests/test_engram_diagnostics.py` — Amnesia Score computation tests
- [ ] `tests/test_engram_promotion.py` — Mnemos → Engram promotion tests

## Success Criteria

- [ ] EngramRecords persist across Maggy sessions (restart Maggy, memories remain)
- [ ] Namespace isolation prevents cross-project contamination (Project A patterns never appear in Project B queries)
- [ ] Multi-path retrieval finds memories that single-path semantic search misses
- [ ] Amnesia Score is computable per project with all 7 dimensions
- [ ] L3 weekly loop adjusts promotion thresholds based on Amnesia Scores
- [ ] Confidence decay correctly ages out unvalidated memories
- [ ] Session startup time improves as Engram provides pre-loaded context
- [ ] All tests pass, coverage >= 80%

## Risks

- Promotion threshold tuning: too low = noise pollution, too high = useful memories lost
- Multi-path retrieval latency: four parallel queries may be slow — benchmark and optimize
- Embedding model required for semantic retrieval — adds a dependency (FAISS or similar)
