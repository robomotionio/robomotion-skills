# Phase 1: PiAdapter + Token Budget Manager

**Status:** pending
**Priority:** P0 — critical path (all other phases depend on this)
**Effort:** Large
**Dependencies:** Pi CLI installed (`pip install pi-agent` or equivalent)

---

## Scope

Build the PiAdapter: a unified agent harness that wraps Pi's RPC interface to replace per-CLI adapters (claude, codex, kimi). Add a token budget manager that tracks spend per provider and triggers model rotation on quota/rate-limit events.

## What Gets Built

1. **PiAdapter module** (`maggy/maggy/adapters/pi.py`)
   - RPC bridge over stdin/stdout to a running Pi process
   - Methods: `send_prompt()`, `stream_events()`, `set_model()`, `get_status()`
   - Model registry: provider name, model ID, tier (cheap/medium/premium), daily limit
   - Fallback chain execution: on quota hit, checkpoint via Mnemos, switch to next model

2. **Token budget manager** (`maggy/maggy/budget.py`)
   - Reads/writes `~/.maggy/token-budget.yaml`
   - Tracks `used_today_usd` per provider (resets at midnight local)
   - Emits `budget_warning` at 80% and `budget_exhausted` at 100%
   - Exposes `/api/budget` REST endpoint for dashboard

3. **Model fallback chain**
   - Ordered: Claude → GPT-4o → Gemini → Kimi → DeepSeek → Qwen (local)
   - On quota hit: Mnemos checkpoint → Pi `set_model` → verify task understanding → continue
   - Verification step: new model must confirm it understands the current task before proceeding

4. **Integration with Polyphony containers**
   - Each container starts Pi in RPC mode
   - PiAdapter communicates with Pi inside the container via `docker exec`

## Deliverables

- [ ] `maggy/maggy/adapters/pi.py` — PiAdapter class
- [ ] `maggy/maggy/budget.py` — Token budget manager
- [ ] `maggy/maggy/api/routes_budget.py` — Budget REST endpoints
- [ ] `maggy/config.example.yaml` — Updated with budget + model config
- [ ] `tests/test_pi_adapter.py` — Unit tests (mock Pi RPC)
- [ ] `tests/test_budget.py` — Budget tracking tests
- [ ] Updated `templates/Dockerfile.polyphony` with Pi install

## Success Criteria

- [ ] PiAdapter can send a prompt and receive streaming events from Pi
- [ ] Model switch completes in < 5s with Mnemos checkpoint preserved
- [ ] Budget manager accurately tracks spend within 5% of actual
- [ ] Fallback chain activates automatically on quota hit
- [ ] New model verifies task understanding before continuing
- [ ] All tests pass, coverage >= 80%

## Risks

- Pi RPC protocol may change between versions — pin version in requirements
- Token cost estimation requires per-model pricing data — start with hardcoded table
- Local model (Qwen) requires Ollama running — must handle gracefully when unavailable
