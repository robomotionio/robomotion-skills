# How to add a skill to Robomotion

> Walkthrough from a **vanilla `robomotion-skills` repo** to having
> `marketing-skills` (vendored, 41 skills by Corey Haines) running as our
> first production unit. The same pattern applies to any future group or
> single skill.
>
> Audience: anyone adding a skill collection or authoring one. Read §1–§2
> once for the mental model, then follow §3 as a checklist for vendoring,
> §4 for first-party authoring.
>
> **One repo holds everything.** `robomotion-skills` is the single monorepo
> for all skills and skill groups — no submodules, no subtrees, no external
> registry. Once content is in, it's ours. Skills (single `SKILL.md` folders)
> and groups (bundles of related skills) coexist as peer directories at the
> repo root.

---

## 1. Mental model

Two units exist in this repo:

| Unit | What it is | Example |
|---|---|---|
| **Skill** | A single `SKILL.md` folder. Knowledge the model reads at runtime; capability comes from the `terminal` tool (curl / a bundled CLI) or a built-in Hermes toolset. | A standalone skill at the repo root (we have none currently) |
| **Group** | A bundle of related skills under one root. Carries its own metadata, install hooks, env overlay. Marketplace ships **groups**. | `marketing-skills/` (41 skills) |

The repo's **discovery contract** is the `.robomotion/` namespace, present on every group (and on standalone skills):

```
<unit>/
  .robomotion/
    skill.yaml        # REQUIRED — name, version, author, source_url, license, summary
    CHANGELOG.md      # optional — Robomotion-side changelog (what WE shipped and bumped)
    LICENSE           # optional — license file for display (copy from upstream for vendored)
    post-install.sh   # optional — install hook (runs once at image build)
    env.yaml          # optional — env overlay (generated from upstream tool docs)
```

For a **group**, these are *group-level* — all inner skills inherit them. The Designer reads `.robomotion/LICENSE` and `.robomotion/CHANGELOG.md` from the group root and surfaces them for every skill in the group. No per-skill `LICENSE` or `CHANGELOG.md` files.

`.robomotion/` is **ours**. We never read `.claude-plugin/plugin.json` or any other upstream metadata file for logic — that's Claude Code / agentskills.io convention, not ours. Upstream is free to ship whatever; we mirror it byte-for-byte and only ever add inside `.robomotion/`.

Other governing principles:

- **Verbatim vendoring.** Upstream content is **never edited** — no SKILL.md rewrites, no path rewrites, no restructuring into our conventions. Bumps are a manual re-copy + diff; no `git subtree` linkage. All Robomotion additions live inside `.robomotion/`.
- **CLI-favored capability.** The model acts by running CLIs through the `terminal` tool — curl, or a bundled CLI on `$PATH`. MCP only when no usable CLI exists.
- **Three layers of durable state.** Per-agent context goes in **Memory** (`MEMORY.md`), current-turn artifacts in the per-hire **workspace** (`/workspace`), team-shared durable docs in **Agent Teams channel attachments** (`files_upload` / `files_download`). See §5.5 and `docs/agent-files.md`.

---

## 2. The vanilla repo

Before any skill is added, the repo looks like this:

```
robomotion-skills/
  README.md
  validate.sh                 # per-unit contract checker
  build-index.py              # walks .robomotion/skill.yaml → index.yaml
  generate-env-overlay.py     # generator: marketing-skills tool docs → .robomotion/env.yaml
  docs/
    agent-files.md            # Memory + workspace model
    skill-system-scale-design.md
    claude-plugin-support.md  # how vendored groups are staged (the runtime side)
  how-to-write-or-port-a-skill-to-robomotion.md   # this doc
```

No skills yet. Discovery is a no-op (the index is empty). We add the first unit next.

---

## 3. Adding `marketing-skills` (the worked example)

You found [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills): 41 marketing skills, 63 zero-dep Node CLIs in `tools/clis/`, 88 integration guides in `tools/integrations/`, MIT, active maintainer, agentskills.io-spec compliant. This is the kind of collection we want.

Bringing it in is **eight steps**.

### 3.1 Find — quick gut check

Before you spend a vendoring round, confirm:

- **Permissive license** (MIT / Apache 2.0 / similar).
- **Spec-compliant or close** — skills under `skills/<name>/SKILL.md`, sensible frontmatter (`name`, `description`, `metadata.version`). Doesn't have to be exactly the agentskills.io spec; needs to be navigable.
- **Active and trusted** — recent commits, real author, healthy issue tracker.
- **Self-contained skills** — each `SKILL.md` is useful standalone, doesn't silently depend on a sibling writing a magic file. (Producer/consumer file conventions get mapped to one of three durable layers — Memory, workspace, or channel attachments — see §5.5.)

### 3.2 Vendor — copy the upstream in

We do **not** use `git subtree` / `git submodule` here. They're awkward at scale (100s of collections, each with its own prefix to track), and most collections don't need live upstream tracking — they get bumped once in a while, not continuously.

Plain copy is enough:

```sh
cd robomotion-skills
# clone upstream to a scratch dir
git clone --depth 1 git@github.com:coreyhaines31/marketingskills.git /tmp/marketingskills
# copy in (everything except .git)
rsync -a --exclude=.git /tmp/marketingskills/ marketing-skills/
rm -rf /tmp/marketingskills
```

From this point the files are **ours** — committed to this repo with no live link back to upstream. **Do not touch anything inside** (§1 verbatim rule); edits collide with the next bump.

Bumps are manual: re-clone upstream, `diff -r` against `marketing-skills/`, apply the changes you want, bump `version` in `.robomotion/skill.yaml`. Most collections need this rarely — quarterly at most.

After this step the tree looks like:

```
robomotion-skills/
  marketing-skills/
    .claude-plugin/plugin.json   # upstream's Claude Code marker — we ignore it
    skills/<name>/SKILL.md       # ×41
    tools/clis/<name>.js         # ×63
    tools/integrations/<name>.md # ×88
    LICENSE, README.md, ...
```

### 3.3 Write the group's `.robomotion/skill.yaml`

This is the authoritative metadata for the group. Place it at `marketing-skills/.robomotion/skill.yaml`:

```yaml
schema_version: 1
name: marketing-skills
title: Marketing Skills
type: group                      # 'group' (has skills/) or 'skill' (single SKILL.md)
version: 2.1.0                   # canonical upstream release tag — NOT necessarily what
                                 # upstream's plugin.json or each SKILL.md's metadata.version
                                 # says (those can drift; the release tag is the truth)
author: Corey Haines             # creator credit
source_url: https://github.com/coreyhaines31/marketingskills
license: MIT
summary: 41 marketing skills — copywriting, SEO, paid ads, growth, lifecycle, CRO, and more.
tags: [marketing, copywriting, seo, ads, growth, cro]
```

Notes:

- `version` is **our pin**, matching upstream's canonical release tag. Upstream's own metadata can disagree with itself — marketingskills v2.1.0 has `plugin.json: 1.9.0` and `metadata.version: 2.0.0`/`2.0.1` in various SKILL.md files. The release tag wins; the loader propagates it to every inner skill (see §5.1 *Version inheritance*).
- `author` is the real upstream creator. The Designer renders `by Corey Haines` on skill cards and links the external icon to `source_url`.
- `type: group` tells the indexer to also walk `marketing-skills/skills/<name>/SKILL.md` to discover the inner skills.

### 3.4 Add `.robomotion/LICENSE` and `.robomotion/CHANGELOG.md`

Both are optional but recommended. The Designer surfaces them per-skill in the marketplace.

**LICENSE** — for a vendored group, copy upstream's LICENSE into `.robomotion/LICENSE` so the Designer has a stable path to read from:

```sh
cp marketing-skills/LICENSE marketing-skills/.robomotion/LICENSE
```

Don't *edit* the copy — keep it identical to upstream so we're transparent about whose terms we ship under. We adopt their license (MIT here) for the vendored copy.

**CHANGELOG.md** — this is **our** changelog, not upstream's. It records what *we* shipped: when we vendored, what version we pinned, what we bumped to, any Robomotion-side patches in `.robomotion/`. Example seed:

```markdown
# Changelog — marketing-skills

## [2.1.0] — 2026-05-26
- Vendored from coreyhaines31/marketingskills@v2.1.0 (41 skills, 63 zero-dep Node CLIs, 88 integration guides).
- Added `.robomotion/post-install.sh` — wraps `tools/clis/*.js` as short-name commands on `$PATH`.
- Added `.robomotion/env.yaml` — generated env overlay (83 integrations × 41 skills, all-optional).
```

Future bumps add a new entry; the `version` in `.robomotion/skill.yaml` matches the latest entry.

### 3.5 Handle install exceptions — `.robomotion/post-install.sh`

Most vendored groups need nothing here. Marketing-skills needs one exception: its CLI library is at `tools/clis/` (non-standard) instead of `bin/` (the conventional location the platform auto-adds to `$PATH`). Without a wrapper, the model has to type `node ${CLAUDE_PLUGIN_ROOT}/tools/clis/ga4.js …` every time; with one, it can just say `ga4 …`.

```sh
# marketing-skills/.robomotion/post-install.sh
#!/bin/sh
set -eu
# Put tools/clis/*.js on $PATH so the model invokes CLIs by short name.
for f in tools/clis/*.js; do
  name=$(basename "$f" .js)
  cat > "/usr/local/bin/$name" <<EOF
#!/bin/sh
exec node "$(pwd)/$f" "\$@"
EOF
  chmod +x "/usr/local/bin/$name"
done
```

`chmod +x` the file. Runs at image build, CWD = group root. Triggers container mode for any agent that activates a marketing skill.

This file is **the place** for exceptions to the upstream layout. If a vendored group needs a one-time install (`apt`, `pip`, `npm`), it goes here too. Per-skill `post-install.sh` still works (rare for vendored — usually all the exceptions are group-wide).

### 3.6 Generate the env overlay — `.robomotion/env.yaml`

Marketing skills can each speak to several alternative tools (analytics → GA4 *or* Mixpanel *or* Amplitude *or* …). The env overlay lists every possible env var across the group so the launcher and hire wizard can offer them. The launcher's overlay-merge is a roadmap item (not yet wired in 0.13.0); generating the file now means it's ready the moment that lands.

Generated automatically by `generate-env-overlay.py` (skills-repo root):

```sh
python3 generate-env-overlay.py
# → writes marketing-skills/.robomotion/env.yaml
```

The generator walks:
- `marketing-skills/tools/clis/*.js` — extracts `process.env.*` references per integration.
- `marketing-skills/tools/integrations/*.md` — extracts the "## Relevant Skills" section per integration.

Output shape:

```yaml
schema_version: 1
collection: marketing-skills
integrations:
  ga4:
    env_optional: [GA4_ACCESS_TOKEN]
    skills: [ab-testing, analytics, cro, seo-audit]
  # … 83 integrations
skills:
  analytics:
    integrations: [ga4, mixpanel, amplitude, ...]    # 26 entries
    env_optional: [GA4_ACCESS_TOKEN, MIXPANEL_API_KEY, ...]   # 35 entries
  # … 41 skills (26 with credentials, 12 pure-knowledge)
```

Every entry is **optional**. Marketing skills are knowledge; no single tool is a prerequisite. The user only supplies keys for tools they actually have.

### 3.7 Regenerate the index

```sh
python3 build-index.py
```

Walks the repo, reads every `.robomotion/skill.yaml`, and (for `type: group`) walks the contained `skills/<name>/SKILL.md` files. Emits `index.yaml` with a top-level `groups[]` (each carrying its `skill.yaml` data + an inner `skills[]` array) and a `skills[]` for standalone units.

After this step the Designer can discover marketing-skills, render `by Corey Haines` on each card, and link to the upstream source URL.

### 3.8 Validate + commit

```sh
bash validate.sh
git status
git add marketing-skills/.robomotion/ index.yaml README.md
git commit -m "feat(marketing-skills): vendor + Robomotion metadata"
```

`validate.sh` checks that every group has a `.robomotion/skill.yaml`, every inner skill has a `SKILL.md`, bundled CLIs (`tools/clis/*.js`) syntax-check, and the index is in sync.

---

## 4. Variants

### 4.1 First-party group (we author both metadata + skills)

Same layout as a vendored group, but we author everything:

```
<group-name>/
  .robomotion/
    skill.yaml             # author: Robomotion, source_url: this repo
    CHANGELOG.md           # group-level changelog (shared by all inner skills)
    LICENSE                # group-level license (MIT etc.)
    post-install.sh        # optional
    env.yaml               # optional — author by hand if no tool-doc generator applies
  skills/
    <skill-name>/
      SKILL.md             # name, summary, version, tags in frontmatter
      env.required         # optional — mandatory creds
      env.optional         # optional — creds with fallback
      post-install.sh      # optional — per-skill install (rarely needed)
      scripts/             # optional — first-party CLIs invoked via ${SKILL_DIR}
      references/          # optional — extra markdown the model can read on demand
```

Inner skills have **no `LICENSE` or `CHANGELOG.md`** of their own — they inherit from `<group>/.robomotion/`.

`skill.yaml` for a first-party group:

```yaml
schema_version: 1
name: <group-name>
title: <Display Name>
type: group
version: 1.0.0
author: Robomotion
source_url: https://github.com/robomotionio/robomotion-skills/tree/main/<group-name>
license: MIT
summary: …
tags: [...]
```

### 4.2 Single standalone skill (no group)

A standalone skill is its own unit with `.robomotion/skill.yaml` next to its `SKILL.md`:

```
<skill-name>/
  .robomotion/
    skill.yaml             # type: skill
    CHANGELOG.md           # the skill's changelog
    LICENSE                # the skill's license
    post-install.sh        # optional — install hook
    env.yaml               # optional — env overlay
  SKILL.md
  env.required
  env.optional
  scripts/                 # optional
  references/              # optional
```

`skill.yaml` for a standalone skill:

```yaml
schema_version: 1
name: <skill-name>
title: <Display Name>
type: skill
version: 1.0.0
author: Robomotion
source_url: https://github.com/robomotionio/robomotion-skills/tree/main/<skill-name>
license: MIT
summary: …
tags: [...]
```

Whether to make something a group or a standalone skill: **start standalone, promote to a group** when a second related skill arrives. A group exists to share metadata + an install hook + an env overlay; one skill never needs that.

---

## 5. The metadata files in depth

### 5.1 `.robomotion/skill.yaml`

The only **required** file in `.robomotion/`. Fields:

| Field | Required | Notes |
|---|---|---|
| `schema_version` | yes | Currently `1`. |
| `name` | yes | kebab-case identifier; must match the directory name. |
| `title` | yes | Display name shown in the Designer. |
| `type` | yes | `group` (has `skills/`) or `skill` (single SKILL.md). |
| `version` | yes | Semver. For vendored groups: what we pin (not necessarily upstream HEAD). |
| `author` | yes | Creator credit. Upstream author for vendored; `Robomotion` for first-party. |
| `source_url` | yes | Canonical source. Upstream repo for vendored; this repo + path for first-party. |
| `license` | yes | SPDX identifier (e.g. `MIT`, `Apache-2.0`). |
| `summary` | yes | One-sentence description. |
| `tags` | optional | List of strings, for filtering in the Designer. |

**Version inheritance.** For a `type: group` unit, the launcher's skill loader reads `version` from `.robomotion/skill.yaml` and **propagates it to every inner skill at load time**, overriding whatever each `SKILL.md` frontmatter declares. The indexer (`build-index.py`) does the same — every inner-skill row in `index.yaml` carries the group's version, not the upstream frontmatter value. This keeps the entire group on one consistent number (e.g. all 41 marketing skills show `v2.1.0`) and shields us from upstream's per-skill `metadata.version` drift.

### 5.2 `.robomotion/CHANGELOG.md` and `.robomotion/LICENSE`

Both are **group-level** for a group — all inner skills inherit them. For a standalone skill, they live in *its* `.robomotion/`. The Designer reads them from the unit root and surfaces them on every skill card.

- **`CHANGELOG.md`** — *Robomotion-side* log. Records what we shipped: vendoring events, version bumps, patches added inside `.robomotion/`. NOT a copy of upstream's changelog; we're tracking *our* changes to *our* mirror.
- **`LICENSE`** — for a vendored group, a verbatim copy of upstream's LICENSE so the Designer has a stable path. We adopt upstream's terms; don't edit the copy. For first-party, we author it.

No per-skill `LICENSE` / `CHANGELOG.md` inside a group — the group-root files cover all inner skills.

### 5.3 `.robomotion/post-install.sh`

Runs once at image build (per active group). Used for:

- Wrapping a non-standard CLI dir onto `$PATH` (marketing-skills' `tools/clis/`).
- Real OS/pip/npm dependencies the base image lacks.
- Idempotent setup the group needs before any of its skills run.

The container's base image already ships `python3`, `node20`, `jq`, `git`, `curl`, `wget`, `ca-certificates`. Don't re-install those.

A non-zero exit fails the image build. Guard best-effort steps with `|| true`.

### 5.4 `.robomotion/env.yaml`

Group-level env overlay. **Generated**, not hand-edited (for vendored groups where a `tools/integrations/` library exists).

The launcher (roadmap item, not yet wired) reads this at stage time and surfaces each integration's env vars as `env.optional` on every inner skill that lists it.

For first-party groups without an upstream tool library, author `env.yaml` by hand or skip it entirely (per-skill `env.required` / `env.optional` files in each skill folder cover the basics).

### 5.5 Three layers of durable state

A skill that needs to persist something has three places it can live, with different scopes:

| Layer | Mechanism | Scope | Auto-injected? | Right for |
|---|---|---|---|---|
| **Memory** | `MEMORY.md` via the memory tool | One agent-node (same `<robot>/<flow>/<agent>` across restarts) | Yes — every turn | Agent's private durable notes (its own learned facts about this user / its own work style) |
| **Workspace** | `/workspace/<file>` (per-hire bind mount) | One hire instance | No — explicit `cat`/read | Per-hire scratch, transient task artifacts, current-turn outputs |
| **Channel attachment** | `files_upload` to scope=channel | All members (humans + agents) of an Agent Teams channel | ✓ when posted in the inbound message (`msg.files`); on-demand via `files_download` | Team-shared durable docs — briefs, plans, references that flow across roles |

Upstream collections often use a producer/consumer file convention — one skill writes `.agents/<name>.md`, others read it. In Robomotion that pattern is wrong twice over: per-hire `/workspace` is isolated (Copywriter's brief doesn't reach Lifecycle Manager), and there's no platform-wide filesystem that means "team shared state."

The **right primitive for team-shared durable docs is the channel attachment.** Upload the brief (or tracking plan, or competitor matrix) to the team's Agent Teams channel; every member — every other hired agent **and** every human in the channel — can download it. Membership is the ACL. The agent toolkit already exposes `files_upload`, `files_download`, and `get_channel_messages` for exactly this; inbound attachments to a message auto-download into `msg.files` for multimodal LLM input, no manual tool call required.

Vendored skills keep their upstream file path references (verbatim rule — no SKILL.md edits). The runtime resolves them under `/workspace` if a per-hire copy exists; otherwise the skill asks the user inline. The clean upgrade is a Robomotion-side overlay that teaches a vendored skill to check the channel first — that mechanism is documented in `docs/agent-files.md`.

---

## 6. Pitfalls

- **Editing a vendored skill's body.** Collides with the next manual bump (re-copy + diff). The only place we ever add inside the mirror is `<group>/.robomotion/`.
- **Leaving install prose in `SKILL.md`.** "First, `pip install …`" belongs in `post-install.sh`, not the prompt. The launcher handles installs.
- **Putting an optional var in `env.required`.** It will block every run that doesn't bind it. Use `env.optional` when there's a fallback or alternative.
- **Adding `scripts/` to a skill that needs the host filesystem.** `scripts/` forces container mode; a filesystem skill (Obsidian-style) then loses host access. Stay pure-knowledge (no `scripts/`, no `post-install.sh`) if you need host fs.
- **Forgetting to bump `version` in `.robomotion/skill.yaml`** after editing a `post-install.sh`. The container image hash includes the version + post-install content; without a bump the cache may serve a stale build.
- **Inventing filesystem paths for cross-skill state.** Producer-writes-a-file / consumer-reads-it is a brittle side-channel. Pick the right durable layer (§5.5): Memory for per-agent state, channel attachments for team-shared docs.
- **Treating `/workspace` as shared team state.** A hired agent's workspace is per-hire — Copywriter and Lifecycle Manager don't share files there. For state multiple roles or humans need, upload to the team's Agent Teams channel and have other agents `files_download` it. See §5.5.
- **Reaching for MCP first.** Robomotion is CLI-favored. Use a CLI via the `terminal` tool; reach for MCP only when there's no usable CLI.

---

## 7. Reference: files & paths

- `README.md` — repo overview + Inventory table (one row per group).
- `build-index.py` → `index.yaml` — discovery manifest the Designer fetches.
- `generate-env-overlay.py` → `<group>/.robomotion/env.yaml` — env overlay generator (currently scoped to marketing-skills; will generalize).
- `validate.sh` + `.github/workflows/validate.yml` — contract checker + index drift-guard.
- `docs/agent-files.md` — Memory + workspace model (where durable state goes).
- `docs/claude-plugin-support.md` — how vendored groups are staged at runtime (`${CLAUDE_PLUGIN_ROOT}`, structure-preserving extraction, `bin/`→`$PATH`).
- `docs/skill-system-scale-design.md` — index → bundles → registry architecture.

**Launcher (other repo — `packages-main/src/hermes-agent/launcher/`):**

- `skills.go` — reads `index.yaml` (yaml.v3), parses the `groups[]` / `skills[]` schema, fetches active skills + the group's `.robomotion/` + `tools/` per-file. Structure-preserving staging at `<owner>__<repo>__<group-slug>/`.
- `dockerfile.go` — image build. `RUN <group>/.robomotion/post-install.sh` once per active group; includes its content hash in the image key. `bin/` → `$PATH` for the standard Claude-plugin layout.
- `launchplan.go: needsSandbox` — triggers container mode if a group ships `.robomotion/post-install.sh`, `bin/`, or any skill ships `scripts/` / `post-install.sh`.
- `env.go` — `aggregateEnvRequired` / `aggregateEnvOptional` across active skills.

**Skill loader (other repo — `packages-main/src/hermes-agent/nodes/skills/`):**

- `skill_loader.py` — substitutes `${SKILL_DIR}`, `${SESSION_ID}`, `${SHARED_DIR}`, `${CLAUDE_PLUGIN_ROOT}` in SKILL.md before injection. Inherits group `version` from `.robomotion/skill.yaml` for every inner skill, overriding upstream's per-SKILL.md frontmatter.

**Designer (other repo — `robomotion-new-designer/src/`):**

- `stores/skills.ts` — fetches `index.yaml`, builds the Browse-Skills list. Reads `author` + `source_url` per skill.
- `components/skills/SkillCard.tsx` — renders `by {author}` + external-link icon to `source_url`.
- `components/editors/EnvironmentTab.tsx` — surfaces each active skill's `env.required` / `env.optional` (and, once the launcher overlay merge ships, the group's `env.yaml` too).

**Where skills get *used* (other repo — `robomotion-agent-hub`):** hireable agent templates live in `robomotion-agent-hub/<slug>/` — each carries `agent.yaml`, `credentials.yaml`, `assets/<node-guid>/AGENT.md`, `main.ts`, `main.designer.ts`. The flow's Hermes Agent node `optSkills` references skills from this repo by `repoUrl + path + version` (or omits `version` to track `main`). Bumping a role to a newer Hermes Agent package version is a one-line edit in the role's `main.ts`. End-to-end pipeline reference: `<monorepo>/docs/how-skills-work.md`.
