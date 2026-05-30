---
name: lead-qualification
description: A reusable lead-qualification engine. Conversational intake builds a qualification prompt capturing the ICP, then leads are enriched and scored into qualified/disqualified verdicts with confidence scores and reasoning. Prompts persist for reuse and calibration. The scoring sub-skill inside the event, Luma, and signal pipelines.
metadata:
  version: 1.0.0
  category: lead-generation
  type: capability
---

# Lead Qualification

The reusable scoring engine. The agent runs intake to synthesize a qualification prompt,
enriches each lead with the facts the prompt needs, scores in parallel, and persists the
prompt for reuse. Scripts handle prompt persistence + scorecard glue; scoring is the agent's.

## When to use

- "Qualify this lead list against our ICP." / "Score these leads."
- Building a reusable ICP qualification prompt; refining one after results.
- The scoring sub-skill inside event/Luma/signal pipelines.

## How to run

### Mode select

- No prompt referenced → **intake**: ask structured product/ICP/criteria questions and
  synthesize a qualification prompt, then save it.
- Prompt referenced → **reuse**.
- Feedback given → **refine** the saved prompt.

### Save / load / list prompts

```bash
python3 ${SKILL_DIR}/scripts/qual_prompt.py --store ${WORKSPACE}/prompts.json \
  save --name acme_icp --prompt-text "Qualify a lead as QUALIFIED if ..."
python3 ${SKILL_DIR}/scripts/qual_prompt.py --store ${WORKSPACE}/prompts.json load --name acme_icp
python3 ${SKILL_DIR}/scripts/qual_prompt.py --store ${WORKSPACE}/prompts.json list
```

### Enrich (the data the prompt needs)

```bash
python3 ${SKILL_DIR}/scripts/web_research.py --leads ${WORKSPACE}/leads.csv \
  --fetch-pages --output ${WORKSPACE}/research.json
```

Keyless degrade for LinkedIn profile / company facts. With `APOLLO_API_KEY` or
`PHANTOMBUSTER_API_KEY` (+ cookie), prefer those for deeper enrichment.

### Score (you, the agent)

```bash
python3 ${SKILL_DIR}/scripts/qual_prompt.py scaffold --leads ${WORKSPACE}/leads.csv \
  --output ${WORKSPACE}/scorecard.json
```

Fill `verdict` (qualified/disqualified), `confidence`, and `reasoning` per lead against the
prompt. Parallelize scoring; cap concurrency. Reasoning is required per verdict — confidence
without rationale is rejected. Then:

```bash
python3 ${SKILL_DIR}/scripts/qual_prompt.py finalize --scorecard ${WORKSPACE}/scorecard.json \
  --format csv --output ${WORKSPACE}/scored.csv
```

## Outputs

- A scored list: `[{name, company, linkedin_url, verdict, confidence, reasoning}]`.
- The saved/updated qualification prompt (in the prompt store).

## Credentials / env

- **Required:** none — scoring runs on the LLM + serp-derived data.
- **Optional:** `APIFY_API_TOKEN` or `PHANTOMBUSTER_API_KEY` + cookie (LinkedIn enrichment
  depth); `APOLLO_API_KEY` (company/person facts); `ANTHROPIC_API_KEY` only if the scoring
  LLM isn't platform-provided.

## Notes & edge cases

- Persist prompts so they're reusable (reuse mode) and calibratable (refine mode).
- Parallelize scoring for throughput; cap concurrency to respect rate limits.
- Reasoning must be explicit per verdict.
- Without LinkedIn enrichment keys, score on serp-derived facts and lower confidence; note it.
