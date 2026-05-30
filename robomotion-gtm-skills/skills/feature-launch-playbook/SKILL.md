---
name: feature-launch-playbook
description: Turn one feature/product-update spec into a complete, launch-ready kit — changelog entry, email announcement, LinkedIn variants, X thread, in-app banner, and (for major launches) a sales-enablement one-pager — plus a tier-appropriate launch checklist. A reasoning composite: the agent authors every asset; a bundled keyless script scaffolds the folder and gates which assets to produce by launch tier.
metadata:
  version: 1.0.1
  category: content
  type: composite
---

# Feature Launch Playbook

A primarily **pure-reasoning composite**. **You (the agent) author every asset.** The
bundled `init_launch.py` scaffolds the `<feature-slug>/` folder and prints the exact
tier-appropriate asset list + checklist (from `launch_tiers.json`), so you generate only
what the tier calls for.

## When to use

- "We just shipped [feature] — help me launch it."
- "Write launch copy / generate the full launch kit for [update]."
- "Turn this feature spec into marketing assets."

## How to run

1. **Intake** feature (name, description, who benefits, problem solved, headline capability),
   launch (tier 1/2/3, date, CTA, available visuals), and voice (brand voice + anything to
   avoid). Ask via grouped intake if missing.
2. **Scaffold + get the tier plan:**

```bash
python3 ${SKILL_DIR}/scripts/init_launch.py --feature "Advanced Filtering" --tier 1 \
  --output ${WORKSPACE}/content
```

Prints `{slug, folder, assets_to_generate, checklist, kit_path, checklist_path}` and creates
the folder. Tier 1 = full kit; Tier 2 = no sales one-pager; Tier 3 = changelog only.

3. **Messaging foundation** — outcome-driven headline (not feature-driven), subhead (what +
   for whom), proof point, single CTA. See `scripts/launch_tiers.json` → `messaging_foundation`.
4. **Generate each asset** in `assets_to_generate`, using the templates in
   `launch_tiers.json` → `asset_templates`. For the social arms, prefer delegating to
   `create-linkedin-content` and `create-x-content` so posts pass through the user's voice
   guide; use `graphics-studio` / `social-kit` for a launch graphic.
5. **Write** `launch-kit.md` (positioning block + all tier assets) and `checklist.md`
   (owner-assignable tasks) to the scaffolded folder; post as channel attachment. Push assets
   onward (`sendgrid`/`brevo` email, `hubspot`/`salesforce` CRM, `slack`) only if asked.

`python3 ${SKILL_DIR}/scripts/init_launch.py --help` lists all flags.

## Outputs

`launch-kit.md` (positioning + tier-appropriate assets) and `checklist.md`, under a
`<feature-slug>/` folder in the workspace / Agent Teams channel.

## Credentials / env

- **Required:** none. The agent is the core engine; the scaffolding script is keyless. The
  full launch kit (every asset + checklist) is produced key-free — that is the default.
- **Optional (all paid, all with a fallback; none gate the kit):**
  - `SENDGRID_API_KEY` / `BREVO_API_KEY` — If set → actually send the email announcement. If
    not → deliver the announcement copy as a file/handoff for the user to send (the default).
  - `APIFY_API_TOKEN` — delegated voice-guide scraping (`generate-voice-guide`). If set →
    auto-scrape the corpus; if not → paste-text fallback (the default).
  - `UNSPLASH_ACCESS_KEY` (and generative-art keys) — delegated graphic imagery
    (`graphics-studio`). If set → real/generated imagery; if not → keyless picsum/ASCII (the
    default).
  - CRM (`hubspot`/`salesforce`) / Slack push — only if the user opts into that distribution.

## Notes & edge cases

- Headlines must be outcome-driven, not feature-driven ("Find your best leads in seconds",
  not "Introducing Advanced Filtering").
- Respect the launch tier — don't generate a full kit for a Tier-3 bug fix (the script
  enforces this by emitting only the tier's asset list).
- Include a proof point (metric / before-after) whenever one exists; keep the CTA single.
