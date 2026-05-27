# Phase 4: Extract CIKG from Chief-of-Staff

**Status:** pending
**Priority:** P1 — enables market-validated feature decisions
**Effort:** Medium
**Dependencies:** Supabase access (CIKG data lives in Supabase)

---

## Scope

Extract the Competitive Intelligence Knowledge Graph (CIKG) from the chief-of-staff project into a standalone module within Maggy. CIKG answers "should we build this?" by mapping competitors, features, market segments, and technology trends. It validates new feature ideas against the competitive landscape before engineering begins.

## What Gets Built

1. **CIKG module** (`maggy/maggy/cikg/`)
   - `graph.py` — KnowledgeGraphService: CRUD for nodes and edges
   - `models.py` — Node types: competitor, feature, market_segment, technology, trend, product
   - `queries.py` — `find_gaps()`, `compare_entities()`, `get_landscape()`, `market_score()`
   - `__main__.py` — CLI: `cikg query`, `cikg traverse`, `cikg gaps`

2. **Supabase integration**
   - CIKG persists in Supabase with RLS (Row Level Security)
   - Tables: `cikg_nodes`, `cikg_edges`, `cikg_snapshots`
   - Real-time subscription for dashboard updates

3. **Market scoring algorithm**
   - Input: feature description
   - Output: `gap_count`, `threat_level`, `trend_alignment`, `recommendation`
   - Feeds into Maggy dashboard: "Before you build X, here's the competitive landscape"

4. **CIKG skill**
   - `skills/cikg/SKILL.md` — Instructions for agents to query CIKG before planning
   - Integration point: after ticket selection, before blast radius analysis

## Deliverables

- [ ] `maggy/maggy/cikg/` — Complete CIKG module
- [ ] `maggy/maggy/cikg/graph.py` — KnowledgeGraphService
- [ ] `maggy/maggy/cikg/models.py` — Pydantic node/edge models
- [ ] `maggy/maggy/cikg/queries.py` — Gap analysis and market scoring
- [ ] `maggy/maggy/api/routes_cikg.py` — REST endpoints for dashboard
- [ ] `skills/cikg/SKILL.md` — Agent instructions
- [ ] `tests/test_cikg.py` — Graph operations and scoring tests
- [ ] Supabase migration for CIKG tables

## Success Criteria

- [ ] CIKG can answer "how many competitors have feature X?" in < 500ms
- [ ] Market score correlates with actual feature prioritization decisions
- [ ] Dashboard shows competitive landscape visualization
- [ ] Agents query CIKG before planning new features
- [ ] RLS prevents cross-org data access
- [ ] All tests pass, coverage >= 80%

## Risks

- CIKG data quality depends on regular updates — may need automated scraping pipeline
- Supabase RLS complexity for multi-tenant scenarios
