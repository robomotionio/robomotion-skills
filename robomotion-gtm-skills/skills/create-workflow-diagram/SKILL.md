---
name: create-workflow-diagram
description: Turn a plain-text workflow ("Find leads → Enrich → Qualify → Send") into a FigJam/Miro-style PNG diagram with connected nodes, arrows, emoji icons, and labels — ready for docs, Slack, LinkedIn, or slides. A deterministic parser builds the node/connection model; the agent authors the styled HTML+SVG; the bundled Playwright renderer screenshots it. For process/pipeline/sequence visuals, not org charts or dense flowcharts.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Create Workflow Diagram

Parse a workflow description into positioned nodes + arrows, render to a crisp PNG.
`parse_workflow.py` does the deterministic parsing (step split, emoji-icon assignment,
layout positions); **you (the agent)** author the styled HTML+SVG from that model (cleaning
messy labels to 2–4 words first); `render.mjs` screenshots it at deviceScaleFactor 2.

## When to use

- "Make a diagram for: step → step → step."
- Process / pipeline / sequence visuals (lead-gen flow, onboarding, CI/CD, data pipeline).
- NOT for org charts, dense branching flowcharts, or architecture diagrams; NOT for plain lists.

## Setup (once)

```bash
cd ${SKILL_DIR}/scripts && npm install && npx playwright install chromium
```

## How to run

1. Parse the workflow into a node/connection model:

```bash
python3 ${SKILL_DIR}/scripts/parse_workflow.py \
  --workflow "Find leads -> Enrich -> Qualify -> Send" \
  --layout left-right --size landscape --title "Lead pipeline" \
  --output ${WORKSPACE}/model.json
```

Steps split on `->` / `→` / numbered lists / newlines. Each node gets an emoji `icon`, a
`label`/`detail` split, a `branch` flag (if/or/else), and `x`/`y` positions for the chosen
`--layout` (`left-right` / `top-bottom` / `snake`) at the `--size` canvas
(`landscape 1920×1080` / `square 1080×1080` / `wide 1200×630`). 6+ steps auto-switch to snake.

2. Author the diagram HTML from `model.json`, injecting a preset from `scripts/styles.json`
   (default `figjam-classic`). Place node cards at each node's `x`/`y`; draw SVG arrows along
   `connections`, recomputing endpoints from actual node edges; diverge labeled arrows for
   any `branch` node.
3. Render to PNG:

```bash
node ${SKILL_DIR}/scripts/render.mjs --html ${WORKSPACE}/diagram.html --out ${WORKSPACE}/diagram.png --size landscape
```

`python3 ${SKILL_DIR}/scripts/parse_workflow.py --help` and
`node ${SKILL_DIR}/scripts/render.mjs --help` list all flags.

## Outputs

A single PNG at the chosen canvas size (deviceScaleFactor 2, well under 5MB) plus the HTML
source and the `model.json`.

## Credentials / env

- **Required:** none — parsing + Playwright render are key-free and local.
- **Optional:** **No paid service is applicable** — parse + local render only, no
  external-data step. `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` are not used by any script (the
  agent is the model); listed only because cleaning messy free-text into 2–4-word
  labels/icons is the agent's job. The regex parser works without them.

## Notes & edge cases

- Keep node labels to 2–4 words / max 2 lines; the parser auto-switches to snake for 6+ steps
  to avoid crowding.
- Recompute arrow endpoints from actual node edges to avoid misaligned connectors.
- For branches, diverge two arrows from the decision node with labels ("Qualified" / "Not").
- The renderer waits for `document.fonts.ready`; bump `--wait` if text renders as fallback fonts.
