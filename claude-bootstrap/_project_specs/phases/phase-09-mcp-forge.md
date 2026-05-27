# Phase 9: MCP Forge Integration (Capability Expansion)

**Status:** pending
**Priority:** P2 — differentiator, not blocking
**Effort:** Large
**Dependencies:** Phase 5 (Maggy v2 UI), mcp_forge module

---

## Scope

When Maggy encounters a capability gap — a tool or integration it doesn't have — it builds one. MCP Forge generates MCP (Model Context Protocol) servers from API documentation, registers the new tools, and makes them available within the same conversation. This is the "I didn't just report the gap, I filled it" feature.

## What Gets Built

1. **Capability gap detection** (`maggy/maggy/forge/detector.py`)
   - Monitor L0/L1 signals for "unresolvable request" patterns
   - Track frequency: if the same gap appears 3+ times in a week, trigger Forge
   - Categories: missing integration (Linear, Notion, Slack), missing tool (screenshot, diagram), missing data source

2. **MCP server generator** (`maggy/maggy/forge/generator.py`)
   - Input: API documentation URL or OpenAPI spec
   - Output: working MCP server with typed tools
   - Steps:
     1. Fetch and parse API docs
     2. Generate tool definitions (name, description, input schema, output schema)
     3. Generate handler implementations (HTTP calls with auth)
     4. Generate tests
     5. Package as installable MCP server

3. **Tool registry** (`maggy/maggy/forge/registry.py`)
   - Register generated MCP servers in Maggy's tool inventory
   - Version tracking: regenerate when API docs change
   - Enable/disable per project
   - Expose via `/api/tools` endpoint

4. **Auto-install pipeline**
   - Generated server → validate → test → register → available in next prompt
   - Rollback: if generated tools fail in practice, disable and flag for human review

5. **L3 integration**
   - Weekly capability gap analysis feeds Forge priorities
   - "Top 3 unresolvable requests this week → generate MCP servers for them"

## Deliverables

- [ ] `maggy/maggy/forge/detector.py` — Capability gap detection
- [ ] `maggy/maggy/forge/generator.py` — MCP server generator
- [ ] `maggy/maggy/forge/registry.py` — Tool registry
- [ ] `maggy/maggy/forge/templates/` — MCP server templates (Python, TypeScript)
- [ ] `maggy/maggy/api/routes_forge.py` — Forge status and trigger endpoints
- [ ] `tests/test_forge_detector.py` — Gap detection tests
- [ ] `tests/test_forge_generator.py` — Server generation tests
- [ ] `tests/test_forge_registry.py` — Registry CRUD tests

## Success Criteria

- [ ] Forge can generate a working MCP server from an OpenAPI spec in < 60s
- [ ] Generated servers pass basic functional tests
- [ ] Tools are available in the next agent prompt after registration
- [ ] Capability gaps decrease by >= 50% after 4 weeks of Forge operation
- [ ] Failed generated tools are auto-disabled and flagged
- [ ] All tests pass, coverage >= 80%

## Risks

- API docs quality varies wildly — Forge may generate broken servers from bad docs
- Auth handling for generated servers is complex (OAuth, API keys, tokens)
- Generated code quality needs review — start with human-in-the-loop, graduate to auto
