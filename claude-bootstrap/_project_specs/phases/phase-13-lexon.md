# Phase 13: Lexon — Semantic Tool Binding

**Status:** pending
**Priority:** P2 — critical once MCP Forge grows tool count past 50+
**Effort:** Large
**Dependencies:** Phase 9 (MCP Forge) + Phase 12 (Engram for vocabulary persistence)

---

## Scope

Build Lexon: the semantic tool binding layer that routes user intent to the correct tool as tool count scales past the accuracy collapse threshold (50+ tools). Lexon implements a two-tier routing pipeline (fast LLM + multilingual vector retrieval), a three-level terminology map (system/org/user), a confidence-gated disambiguation protocol, and a personalization layer that learns from user behavior. Org-level vocabulary propagates via Mesh.

## What Gets Built

1. **LexonRecord schema** (`maggy/maggy/lexon/record.py`)
   - Binding primitive: phrase → tool with confidence, language, candidates, correction
   - Context snapshot: pointer to active Mnemos ContextNode
   - Logged per invocation for learning and audit

2. **Two-tier router** (`maggy/maggy/lexon/router.py`)
   - Tier A — Fast LLM router: compact tool manifest (name + 1-line description, ~400 tokens for 80 tools), JSON schema constrained to valid tool names, returns 5-7 candidates, target < 300ms
   - Tier B — Multilingual semantic retriever: tool registry indexed by description + example queries + learned synonyms, multilingual-e5-large or equivalent, cosine similarity ranking
   - Union + deduplication: candidates from both tiers merged, score bonus for tools in both

3. **Terminology Map** (`maggy/maggy/lexon/terminology.py`)
   - Three levels: system (built-in), org (team-shared), user (personal)
   - Resolution: user > org > system > router inference
   - NOT bindings: explicit negative matches ("blast" is NOT "delete_all")
   - Context-conditioned: same phrase → different tool based on active entity
   - Org-level entries shareable via Mesh typed memory

4. **Disambiguation protocol** (`maggy/maggy/lexon/disambiguate.py`)
   - Confidence threshold: 0.82 (configurable)
   - Gap threshold: 0.15 between top-2 candidates
   - `clarify_intent` tool: presents 2-3 concrete options in user's language
   - Context collapse: Mnemos ContextNode can resolve ambiguity without asking user
   - Selection captured as high-confidence user-level binding

5. **Personalization layer** (`maggy/maggy/lexon/personalization.py`)
   - 5 implicit learning signals: correction, affirmation, repetition, disambiguation selection, clarification repetition
   - Corrections count double (weight 2.0)
   - After 5+ repetitions of same phrase→tool: promote to high-confidence synonym
   - After 10+ uses with confidence > 0.9: promote to Engram for cross-session persistence
   - 3+ disambiguations on same phrase: escalate to explicit preference prompt

6. **Tool registry indexer**
   - Index all MCP tools, MCP Forge generated tools, and built-in capabilities
   - Generate embeddings per tool: description + example queries + synonyms
   - Re-index on tool registry change (MCP Forge adds a new server)
   - Store in `~/.maggy/lexon_embeddings/`

7. **Dashboard integration**
   - Tool selection accuracy metrics
   - Disambiguation rate trend (should decrease for returning users)
   - Terminology Map browser (view/edit user and org level entries)
   - Top ambiguous phrases needing resolution

## Deliverables

- [ ] `maggy/maggy/lexon/record.py` — LexonRecord dataclass
- [ ] `maggy/maggy/lexon/router.py` — Two-tier routing engine
- [ ] `maggy/maggy/lexon/terminology.py` — Three-level terminology map
- [ ] `maggy/maggy/lexon/disambiguate.py` — Confidence-gated disambiguation
- [ ] `maggy/maggy/lexon/personalization.py` — Implicit learning layer
- [ ] `maggy/maggy/lexon/__init__.py` — Public API
- [ ] `maggy/maggy/api/routes_lexon.py` — REST endpoints
- [ ] `skills/lexon/SKILL.md` — Agent instructions for tool binding
- [ ] Tool registry indexer (embedding generation)
- [ ] `tests/test_lexon_router.py` — Two-tier routing tests
- [ ] `tests/test_lexon_terminology.py` — Terminology Map resolution tests
- [ ] `tests/test_lexon_disambiguate.py` — Disambiguation protocol tests
- [ ] `tests/test_lexon_personalization.py` — Learning signal tests
- [ ] `tests/test_lexon_multilingual.py` — Multilingual routing tests

## Success Criteria

- [ ] Tool selection accuracy > 85% at 80+ tools (measured against ground truth)
- [ ] Disambiguation rate < 15% for users with 50+ interactions
- [ ] Fast LLM router responds in < 300ms
- [ ] Terminology Map correctly resolves user > org > system precedence
- [ ] NOT bindings prevent recurring mis-selections
- [ ] Learned vocabulary persists across sessions via Engram
- [ ] Org-level terms propagate via Mesh to new team members
- [ ] Multilingual queries route correctly without requiring English
- [ ] All tests pass, coverage >= 80%

## Risks

- Embedding model adds a runtime dependency (~500MB model) — consider lazy loading
- Fast LLM router quality depends on model choice — need to benchmark multiple options
- Multilingual embedding quality varies by language — high-resource languages first
- Personalization cold start: new users have elevated disambiguation rates until learned
