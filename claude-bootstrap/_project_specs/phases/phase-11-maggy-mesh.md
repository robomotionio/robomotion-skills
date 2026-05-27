# Phase 11: Maggy Mesh — P2P Team Intelligence

**Status:** pending
**Priority:** P2 — differentiator, builds on foundation
**Effort:** Extra Large
**Dependencies:** Phase 5 (Maggy v2 UI), Phase 8 (Process Intelligence signals)

---

## Scope

Connect Maggy instances across a team into a peer-to-peer mesh network. Each Maggy autonomously shares learned intelligence — model scores, workflow patterns, CI remedies, policy proposals — with other Maggys in the same organization. The mesh creates a compound learning effect: `knowledge = n_developers x learning_rate x time x sharing_factor`.

## What Gets Built

### 1. Peer Identity & Discovery (`maggy/maggy/mesh/discovery.py`)
- Stable `peer_id` (UUID) generated on install, stored in `~/.maggy/peer_id`
- mDNS/DNS-SD discovery: announce `_maggy._tcp.local` with port + peer_id
- Manual peer list for cross-subnet/VPN/remote: `mesh.yaml` `manual_peers[]`
- Peer registry: SQLite table tracking known peers, last seen, sync state

### 2. Transport & Auth (`maggy/maggy/mesh/transport.py`)
- WebSocket over TLS (self-signed certs, pinned on first connect)
- Org key authentication: pre-shared secret in `mesh.yaml`
- Handshake: nonce challenge → HMAC-SHA256(nonce, org_key) → verified → connected
- Message signing: every payload signed with HMAC-SHA256(json(payload), org_key)

### 3. Typed Memory Classes (`maggy/maggy/mesh/memory.py`)
- **Scores** (model performance): weighted merge by sample count
- **Patterns** (workflow/CI/PR patterns): union-merge with frequency tracking
- **Policies** (routing thresholds, workflow rules): backtest-gated promotion
- **Gaps** (capability gaps, feature requests): additive accumulation

### 4. Provenance System (`maggy/maggy/mesh/provenance.py`)
- Every shared memory carries: peer_id, peer_name, project_key, language, toolchain, evidence_count, confidence, created_at, last_verified
- Confidence decays with age: `confidence *= 0.95^(days_since_verified)`
- Provenance enables filtering: "only accept Python patterns from peers working on Python projects"

### 5. Sync & Merge Algorithm (`maggy/maggy/mesh/sync.py`)
- Periodic sync: every 15 minutes (configurable)
- Full sync on new peer connect (cold start bootstrap)
- Merge logic per type:
  - Scores: weighted average by sample count
  - Patterns: union-merge, increment frequency if already known
  - Policies: quarantine → backtest on local data → promote if passes
  - Gaps: additive, deduplicate by key
- Anomaly detection: reject values > N standard deviations from local data

### 6. Quarantine System (`maggy/maggy/mesh/quarantine.py`)
- Incoming peer data starts in quarantine (`quarantine.db`)
- Promotion paths:
  - Self-confirmed: local data validates the pattern within quarantine window
  - Crowd-confirmed: 3+ peers independently report the same pattern
  - Human override: user explicitly promotes or rejects
- Quarantine window: 30 days (configurable), then auto-reject if unconfirmed
- Dashboard shows quarantined items with provenance for manual review

### 7. Control Loop Integration
- L1 broadcasts score updates to connected peers after each task
- L2 merges incoming peer data during daily aggregation
- L3 backtests incoming policies against local data before promotion
- L4 proposes cross-team policy changes when team-wide data supports them

### 8. Message Protocol (`maggy/maggy/mesh/protocol.py`)
- Message types: `score_update`, `pattern_share`, `policy_proposal`, `gap_report`, `heartbeat`, `full_sync_request`, `full_sync_response`
- All messages: `{type, peer_id, peer_name, timestamp, payload, signature}`
- Idempotent: duplicate messages (same peer_id + timestamp + key) are ignored

### 9. Cold Start Bootstrap
- New team member installs Maggy → generates peer_id → discovers peers via mDNS
- Requests `full_sync` from first available peer
- Receives all team knowledge (quarantined until locally validated)
- "Day one developer gets collective intelligence immediately"

### 10. Mesh Dashboard Panel
- Connected peers: name, project, last sync, health
- Shared knowledge stats: scores merged, patterns shared, policies proposed
- Quarantine queue: pending items with provenance and promote/reject actions
- Network topology visualization

## Deliverables

- [ ] `maggy/maggy/mesh/discovery.py` — mDNS + manual peer discovery
- [ ] `maggy/maggy/mesh/transport.py` — WebSocket + TLS + HMAC auth
- [ ] `maggy/maggy/mesh/memory.py` — Typed memory classes with merge logic
- [ ] `maggy/maggy/mesh/provenance.py` — Provenance tracking and decay
- [ ] `maggy/maggy/mesh/sync.py` — Sync engine and merge algorithm
- [ ] `maggy/maggy/mesh/quarantine.py` — Quarantine system
- [ ] `maggy/maggy/mesh/protocol.py` — Message types and serialization
- [ ] `maggy/maggy/api/routes_mesh.py` — Mesh status and control endpoints
- [ ] `~/.maggy/mesh.yaml` template — Mesh configuration
- [ ] `tests/test_mesh_discovery.py` — Peer discovery tests
- [ ] `tests/test_mesh_transport.py` — Transport and auth tests
- [ ] `tests/test_mesh_merge.py` — Merge algorithm tests per type
- [ ] `tests/test_mesh_quarantine.py` — Quarantine promotion tests
- [ ] `tests/test_mesh_sync.py` — Full sync and incremental sync tests
- [ ] Dashboard mesh panel

## Success Criteria

- [ ] Two Maggy instances on the same LAN discover each other via mDNS in < 10s
- [ ] Score merge produces weighted average consistent with both peers' data
- [ ] Pattern sharing reduces "rediscovery" of known CI fixes by >= 50%
- [ ] Quarantine prevents unvalidated data from affecting routing decisions
- [ ] Cold start: new peer receives full team knowledge within 60s of first connect
- [ ] Provenance traces every shared item back to originating peer and evidence
- [ ] Anomaly detection blocks scores > 10 standard deviations from local
- [ ] Manual peers work across subnets/VPNs for remote team members
- [ ] All tests pass, coverage >= 80%

## Risks

- mDNS doesn't work on all corporate networks — manual peers as fallback is essential
- Shared secret (org_key) is a single point of compromise — consider per-device keys in future
- Merge conflicts on policies could cause disagreement loops — backtest-gating prevents this
- Large teams (20+ peers) may generate significant sync traffic — add sync throttling
- Poisoned peer data could propagate — quarantine + anomaly detection are the primary defenses

## The Compound Effect

```
Individual Maggy:    knowledge = learning_rate x time
Team Mesh (n peers): knowledge = n x learning_rate x time x sharing_factor

With 5 developers, 6 months usage:
  Individual: 1 x 1.0 x 180 = 180 learning units
  Team mesh:  5 x 1.0 x 180 x 0.8 = 720 learning units (4x)

The sharing_factor (0.8) accounts for context mismatch and quarantine filtering.
Superlinear because peers validate each other's patterns (crowd confirmation).
```
