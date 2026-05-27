# Phase 3: Mnemos Multi-Model Fatigue Tracking

**Status:** pending
**Priority:** P1 — improves model switch quality
**Effort:** Medium
**Dependencies:** Phase 1 (PiAdapter with model switching)

---

## Scope

Extend Mnemos fatigue tracking to work across multiple models. Currently, Mnemos tracks fatigue for a single Claude session. With multi-model routing, fatigue profiles must be model-normalized so that a checkpoint from Claude can be re-injected into GPT-4o without quality loss.

## What Gets Built

1. **Model-normalized fatigue profiles** (`maggy/maggy/fatigue.py`)
   - Per-model context window sizes and optimal checkpoint thresholds
   - Fatigue score normalized to 0.0-1.0 regardless of model's raw context size
   - Model-specific re-read patterns tracked post-switch

2. **Cross-model checkpoint format**
   - Mnemos checkpoint includes: goal, constraints, progress, working state, file context
   - Checkpoint is model-agnostic (structured data, not model-specific tokens)
   - On model switch: checkpoint serialized → injected as structured prompt to new model
   - Verification step: new model summarizes checkpoint to confirm understanding

3. **Fatigue learning loop**
   - Track `model_switch_recovery_reads` per model pair
   - Learn optimal pre-checkpoint timing per user (currently hardcoded at 0.60 threshold)
   - Feed into L1 task reward: smooth switches = +0.1, rocky switches = -0.3

4. **Updated Mnemos skill**
   - `skills/mnemos/SKILL.md` updated with multi-model fatigue instructions
   - Signal types expanded: `model_switch`, `recovery_read`, `checkpoint_quality`

## Deliverables

- [ ] `maggy/maggy/fatigue.py` — Model-normalized fatigue tracking
- [ ] Updated Mnemos checkpoint format (model-agnostic)
- [ ] `maggy/maggy/services/checkpoint.py` — Cross-model checkpoint serializer
- [ ] `tests/test_fatigue.py` — Fatigue normalization tests
- [ ] `tests/test_checkpoint.py` — Checkpoint round-trip tests (serialize → inject → verify)
- [ ] Updated `skills/mnemos/SKILL.md`

## Success Criteria

- [ ] Fatigue score is comparable across models (0.6 means the same thing for Claude vs GPT-4o)
- [ ] Model switch with checkpoint preserves task understanding in >= 90% of cases
- [ ] Average recovery reads after switch decreases over time as profiles improve
- [ ] User-specific fatigue timing learned after 20+ sessions
- [ ] All tests pass, coverage >= 80%

## Risks

- Model-specific tokenizer differences make fatigue comparison imprecise — use heuristic normalization first
- Checkpoint injection quality varies by model — some models handle structured context better than others
