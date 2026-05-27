# Phase 5: Maggy v2 Multi-Project Dashboard

**Status:** pending
**Priority:** P0 — the user-facing product, enables Phases 8-11
**Effort:** Large
**Dependencies:** Phases 1-4 (all backend modules feed the dashboard)

---

## Scope

Build the Maggy v2 web dashboard: a multi-project command center where developers see inbox, budget, agents, competitive intelligence, and process health — all in one view. This is the "5-second test" UI described in the architecture doc.

## What Gets Built

1. **Multi-project layout**
   - Project switcher (top nav) with health indicators per project
   - Unified inbox across all projects, ranked by urgency
   - Per-project detail views: iCPG drift, Mnemos fatigue, agent status

2. **Dashboard panels**
   - **Inbox** — AI-ranked tickets across GitHub Issues, Asana, Linear, Jira
   - **Budget** — Token spend per provider (green/yellow/red), burn rate trend
   - **Agents** — Active Polyphony containers, current task, model, progress
   - **CIKG** — Competitive landscape, gap map, threat radar
   - **Process health** — CI pass rate, review rounds, CodeRabbit findings trends
   - **Model performance** — Reward heatmap from routing table

3. **One-click execute**
   - Select ticket → auto-select model (from routing table) → spawn Polyphony container
   - Pre-flight: iCPG blast radius → CIKG validation → confirm or adjust

4. **REST API backend**
   - Extend `maggy/maggy/api/routes.py` with endpoints for each panel
   - WebSocket for real-time agent status and budget updates
   - Authentication: local token (single-user default), expandable to org auth

5. **Frontend stack**
   - React + TypeScript + Vite
   - Zustand for state management
   - React Query for server state
   - TailwindCSS for styling
   - Location: `maggy/frontend/`

## Deliverables

- [ ] `maggy/frontend/` — React dashboard application
- [ ] Inbox panel with cross-project ticket aggregation
- [ ] Budget panel with real-time spend tracking
- [ ] Agent status panel with Polyphony container monitoring
- [ ] CIKG panel with competitive landscape visualization
- [ ] Process health panel with trend charts
- [ ] Model performance heatmap
- [ ] One-click ticket execution flow
- [ ] WebSocket endpoints for real-time updates
- [ ] `tests/test_dashboard_api.py` — API endpoint tests

## Success Criteria

- [ ] Developer sees prioritized inbox within 5 seconds of opening
- [ ] Budget status visible at a glance (green/yellow/red)
- [ ] Active agents show real-time progress
- [ ] One-click execute spawns agent with correct model in < 10s
- [ ] Dashboard loads in < 2s on localhost
- [ ] All API tests pass, coverage >= 80%

## Risks

- Multi-project support requires consistent project registration — need project discovery or manual add
- Real-time WebSocket connections may need reconnection logic for long-running sessions
- Frontend scope could expand — keep to mWp, not full feature set
