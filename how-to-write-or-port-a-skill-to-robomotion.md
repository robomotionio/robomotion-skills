# How to write or port a Skill to Robomotion

> The complete guide to authoring a new Agent Skill — or porting one from the
> upstream Hermes Agent (`NousResearch/hermes-agent`) — into this repository
> (`robomotion-skills`), so it runs correctly inside Robomotion's **Hermes
> Agent** node.
>
> Audience: skill authors and anyone porting upstream skills. Read §1–§4 once to
> build the mental model, then use §9 (write new) or §10 (port) as a checklist.

---

## Table of contents

1. [The mental model: capability vs knowledge](#1-the-mental-model-capability-vs-knowledge)
2. [What Robomotion can and cannot port](#2-what-robomotion-can-and-cannot-port)
3. [The runtime pipeline (how a skill reaches the model)](#3-the-runtime-pipeline)
4. [Anatomy of a skill folder](#4-anatomy-of-a-skill-folder)
5. [`SKILL.md` in depth](#5-skillmd-in-depth)
6. [Host mode vs container mode (classification)](#6-host-mode-vs-container-mode)
7. [Credentials: `env.required` and `env.optional`](#7-credentials-envrequired-and-envoptional)
8. [Installs and scripts](#8-installs-and-scripts)
9. [Writing a brand-new skill (step by step)](#9-writing-a-brand-new-skill)
10. [Porting an upstream Hermes skill (step by step)](#10-porting-an-upstream-hermes-skill)
11. [Worked examples](#11-worked-examples)
12. [Testing & verification](#12-testing--verification)
13. [Pitfalls & gotchas](#13-pitfalls--gotchas)
14. [Reference: files & paths](#14-reference-files--paths)

---

## 1. The mental model: capability vs knowledge

Upstream Hermes splits every integration into **two independent halves** that
meet only at tool names:

| | **Plugin** (`plugins/<name>/`) | **Skill** (`skills/<cat>/<name>/`) |
|---|---|---|
| What it is | Executable Python registered as tools | Markdown documentation |
| Provides | **Capability** — the ability to *act* | **Knowledge** — *when & how* to act |
| Runtime | `registry.dispatch(...)` runs it | The model reads it; it never executes |

**Robomotion ships only the knowledge half.** A Robomotion skill is a folder of
Markdown (plus optional helper scripts and install hooks). The agent's
`skill_loader` injects `SKILL.md` into the system prompt; nothing in this repo
registers tools. (See `packages-main/src/hermes-agent/nodes/skills/skill_loader.py`.)

So the capability a ported skill relies on must already exist as one of:

- the generic **`terminal`** tool (run `curl`, or a CLI you ship in `scripts/`), or
- a **built-in Hermes toolset** that Robomotion already exposes (e.g. `file`,
  `web`, `browser`, `vision`, `discord`, …). The authoritative list is
  `_HERMES_INTERNAL_TOOLS` in
  `packages-main/src/hermes-agent/nodes/agent/hermes_agent.py`.

There is no way to add a *new* registered tool from this repo. If a capability
needs one, that's a code change in the Hermes Agent package, not a skill.

---

## 2. What Robomotion can and cannot port

Read the source skill's front-matter and body, then classify it:

| Signal in the source skill | Capability source | Portable here? |
|---|---|---|
| `prerequisites.env_vars` / `prerequisites.commands`, body uses `curl`/CLI | generic `terminal` | ✅ **Yes** — self-contained (e.g. `linear`, `airtable`, `notion`, `github-issues`) |
| Body uses file/web/browser/etc. tools | a built-in toolset | ✅ **Yes, iff** that toolset is in `_HERMES_INTERNAL_TOOLS` (e.g. `obsidian` → `file`) |
| `prerequisites.tools` or `metadata.hermes.requires_tools` | a **plugin's** registered tools | ⚠️ **Only via rewrite** — re-implement the capability as a CLI in `scripts/` (e.g. `spotify` → `scripts/spotify_api.py` over the Web API) |

> **The plugin trap.** A skill whose capability is a plugin's tools is useless if
> you copy only its `SKILL.md` — the model will emit tool calls (`spotify_*`) that
> don't exist and fail at dispatch. Either the toolset is already built into the
> agent, or you **port it to a CLI equivalent** the `terminal` tool can run.

When rewriting a plugin-backed skill to a CLI, also solve auth for a **headless
sandbox**: interactive OAuth (`hermes auth <x>`) won't work. Use vault-bound
credentials (e.g. client id/secret + a refresh token generated once, out-of-band).

---

## 3. The runtime pipeline

What happens between "user toggles a skill on the agent" and "the model can use it":

```
1. Designer (Agent Editor)
   - reads the repo's index.json (ONE fetch) → browse / search / env display
   - writes node config: optSkills [{name, repoUrl, path, version}],
     optActiveSkills ["linear", …], optEnvironmentBindings, optToolsEnvRequired

2. Launcher (per agent run)
   - collectActiveSkills(nodeConfig) → which skills, which repo/path
   - fetchAndExtract: index-driven — download ONLY the active skills + their
     nearest _shared, file-by-file from raw.githubusercontent, into
     HERMES_HOME/skills/<owner>__<repo>__<name>/   (whole-repo tarball = fallback)
   - needsSandbox? → host mode, OR container mode (build image:
     FROM base; COPY skills; RUN post-install.sh — layer-cached)
   - validate required env bound; inject --env (required ∪ optional) via the
     credential proxy; emit LaunchPlan

3. Agent process (skill_loader.py)
   - reads each ACTIVE skill's SKILL.md from its staged path
   - substitutes ${SKILL_DIR} / ${SESSION_ID} / ${SHARED_DIR}
   - injects each body under "## Active Skills" in the system prompt
```

Key facts that shape how you author:

- **Install dir / `${SKILL_DIR}`.** Each skill is extracted to
  `HERMES_HOME/skills/<owner>__<repo>__<name>/` (host) or
  `/opt/robomotion/skills/<owner>__<repo>__<name>/` (container). In `SKILL.md`,
  the token `${SKILL_DIR}` is substituted with that concrete path **before** the
  text reaches the model — so `python3 ${SKILL_DIR}/scripts/foo.py` just works.
  `${SESSION_ID}` is likewise substituted with the current turn's session id.
  (Both `HERMES_SKILL_DIR` / `HERMES_SESSION_ID` long forms also work.)
- **`${SHARED_DIR}`** resolves to the **nearest `_shared/` walking up a skill's
  path** (group-scoped, repo-root as fallback) — see §8 *Shared library*.
- **Discovery + fetch are index-driven.** `index.json` (built by `build-index.py`)
  is the single manifest: the Designer reads it to browse/show env (one fetch, no
  per-`SKILL.md` probing), and the launcher reads it to fetch **only the active
  skills** (+ nearest `_shared`) instead of the whole repo. So add/change a skill
  ⇒ regenerate + commit `index.json`. See `docs/skill-system-scale-design.md`.
- **Only the active set reaches the prompt.** The builder curates an agent's skills
  in the Designer; the loader injects just those — never the whole catalog — so the
  system prompt stays bounded regardless of how many skills exist in the repo.
- **The model reads `SKILL.md` as prose.** It then either runs `curl`/your script
  via the `terminal` tool, or calls a built-in toolset. Write for that audience.
- **`version:` busts the image cache.** The container image hash includes each
  skill's version, so bumping it forces a rebuild even when the git ref is a
  moving branch like `main`. Always bump it when you change a script or
  `post-install.sh`. The version is read from top-level `version:` **or** nested
  `metadata.version` (the agentskills.io spec shape — see §5).

---

## 4. Anatomy of a skill folder

A skill is a single top-level folder in this repo. Its name is **kebab-case** and
**must equal** the `name:` in `SKILL.md`.

```
<skill-name>/
  SKILL.md          # REQUIRED — capability + operating notes for the model
  env.required      # optional — mandatory creds, one VAR per line (blocks run if unbound)
  env.optional      # optional — creds/config with a fallback (never blocks)
  post-install.sh   # optional — runs once at image build (apt/pip/npm)
  pre-run.sh        # optional — runs at every container start (login ceremonies)
  scripts/          # optional — helper CLIs the model invokes via terminal
  references/       # optional — extra markdown the model can read on demand
  CHANGELOG.md      # REQUIRED by repo convention — Keep a Changelog format
  LICENSE           # REQUIRED by repo convention — MIT + attribution
```

Only `SKILL.md` is needed for the launcher to recognize the folder as a skill.
`CHANGELOG.md` and `LICENSE` are repo conventions (every skill here has them).

Beyond the per-skill folder, a repo may also ship one top-level **`_shared/`**
directory (not per-skill) holding code/docs/env reused across its skills — see
§8 *Shared library*.

---

## 5. `SKILL.md` in depth

### Front-matter

```yaml
---
name: linear                 # REQUIRED — kebab-case, == folder name
version: 1.0.0               # REQUIRED — semver; participates in the image cache hash
summary: One-line capability statement.   # what the skill does, in a sentence
tags: ["linear", "issues", "project-management"]
---
```

- Keep front-matter **simple**: the loader uses a minimal YAML parser (scalars,
  inline lists `[a, b]`, one-level block lists). Avoid anchors and deep nesting —
  the one nested field the platform reads is `metadata.version` (see *Cross-agent
  compatibility* below).
- New first-party skills start at `version: 1.0.0` (repo convention), regardless
  of upstream — note the upstream version in `CHANGELOG.md`. Third-party spec
  skills may instead keep their `metadata.version`.
- Drop upstream-only fields (`author`, `license`, `platforms`, `prerequisites`,
  `metadata.hermes.*`). License → `LICENSE` file; required env → `env.required`;
  `prerequisites` is not read by Robomotion's loader.

### Body structure

Follow the same shape as the existing skills so the model gets consistent routing
signals:

```markdown
# <Title>

<1–3 sentence intro: what it does, how it's accessed (curl / which script).>

## Capabilities
- bullet list of what it can do

## Usage
<concrete, copy-pasteable commands. Use ${SKILL_DIR}/scripts/... for shipped CLIs.>

## When to use
- example user requests that should route here

## When NOT to use
- adjacent skills / out-of-scope cases (route elsewhere)

## Operating notes
- failure modes, auth header quirks, rate limits, pagination, gotchas

## Attribution
Adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) `<name>` skill (MIT).
```

Rules:

- **No install prose.** Don't tell the model to `pip install` / `apt-get` / "set
  this env var in `~/.hermes/.env`". Installs go in `post-install.sh`; credentials
  are declared in `env.required` / `env.optional` and bound from the Vault.
- **When-to-use / When-NOT-to-use are not filler.** They are the routing hints
  that make the model pick the right skill. Name adjacent skills explicitly.
- **Operating notes earn their keep.** Put the things models get wrong here: auth
  header format, "check the `errors` array even on HTTP 200", URL-encoding rules,
  "don't retry on 403", pagination cursors.
- Reference extra docs via `${SKILL_DIR}/references/<file>.md`. The loader also
  auto-appends a "Reference docs at: …" line when a `references/` dir exists.

### Cross-agent (agentskills.io) compatibility

Robomotion also accepts the [agentskills.io](https://agentskills.io) /
Claude-plugin front-matter shape, so a spec-compliant third-party skill installs
with little or no rewriting:

- **`description`** is read as a fallback for `summary` in the Designer marketplace.
- **`metadata.version`** (nested) is read as a fallback for top-level `version:`
  by both the launcher (cache key) and the Designer.
- Skills nested under a repo's **`skills/<name>/`** directory are discovered in
  addition to repo-root skills.

So you can drop a spec skill in nearly as-is — the 5 marketing pilots (`cro`,
`copywriting`, `cold-email`, `pricing`, `marketing-psychology`) did exactly this,
keeping `name` + `description` + `metadata.version` and only adding `tags`. Use
the native four-field shape (above) for new first-party skills; rely on these
shims when ingesting third-party spec skills.

---

## 6. Host mode vs container mode

The launcher classifies each agent run (`launcher/launchplan.go: needsSandbox`):

- **Container mode** if **any** active skill ships a `post-install.sh` **or** a
  non-empty `scripts/` directory. The launcher builds a Podman image
  (`FROM` the base image, `COPY` skills, `RUN` each `post-install.sh`) and runs
  the agent inside it.
- **Host mode** otherwise (pure-knowledge skills: just `SKILL.md` + `references/`
  + env files). The agent runs directly on the host; no Podman dependency.

`references/` and `env.*` files do **not** force container mode — only
`post-install.sh` and a non-empty `scripts/` do.

Consequences you must design around:

- **Need to reach the host filesystem?** (e.g. `obsidian` editing a local vault)
  → stay **pure-knowledge / host mode**. Do **not** add a `scripts/` dir, or the
  agent gets containerized and the host files won't be there (unless mounted).
- **Need OS packages, pip libs, or a bundled CLI?** → you're container mode by
  definition; that's fine and expected.
- **Mixing is fine.** One install-bearing skill puts the whole agent in container
  mode; pure-knowledge skills work in either mode (the base image has
  python3/node/curl/jq, so `curl`-based knowledge skills work in the container
  too).

---

## 7. Credentials: `env.required` and `env.optional`

Robomotion never hard-codes secrets in a skill. A skill **declares** the env var
*names* it needs; the user binds each to a **Vault** item in the Designer; the
deskbot resolves them and the launcher injects them into the run.

Two files, same format (one `VAR_NAME` per line; `#` comments and blank lines
ignored; inline `=VALUE` is stripped — declare names only):

| | `env.required` | `env.optional` |
|---|---|---|
| Meaning | Mandatory — the skill can't work without it | Has a sensible fallback / default |
| Launcher | `validateEnvBindings` **blocks the run** if unbound (`secret_unbound`) | **Never blocks**; injected only when bound |
| Injection | injected as `--env` | injected as `--env` when bound (union with required) |
| Designer | Environment tab flags unbound ones (red "won't run") | shown in a separate non-blocking "Optional" section |

**Decision rule:** if the skill has a documented fallback for a var, put it in
`env.optional`; otherwise `env.required`. Example: `obsidian` declares
`OBSIDIAN_VAULT_PATH` in `env.optional` because it falls back to
`~/Documents/Obsidian Vault`. Listing it as required would wrongly block runs
that rely on the default.

Write helpful comments — the Designer doesn't show them, but they document intent
for the next author:

```sh
# Personal API key — generate at https://linear.app/settings/account/security
# under "Personal API keys".
LINEAR_API_KEY
```

How it's wired (for the curious / when debugging):

- **Launcher** `env.go`: `aggregateEnvRequired` / `aggregateEnvOptional` union the
  names across active skills. `main.go` validates **required-only** but injects the
  **union** (`mergeEnvRequired(required, optional)`) via `envFlags`. Tool-declared
  env (`optToolsEnvRequired`) folds into the required set.
- **Designer** `components/editors/EnvironmentTab.tsx` (inside the Agent Editor):
  fetches `env.required` and `env.optional` from
  `raw.githubusercontent.com/<owner>/<repo>/main/<path>/<file>`, renders a Vault +
  item picker per var, and persists `optEnvironmentBindings`
  (`ENV_VAR -> {vault_id, vault_item_id}`) on the node.
- **Security.** For sandboxed (container) runs, the launcher fails closed unless
  the deskbot's **credential proxy** is present: the injected `--env` values are
  vault-reference placeholders, and the proxy substitutes the real secret only on
  the live outbound request. As a skill author you just reference the env var
  normally (`$LINEAR_API_KEY`); the platform handles the rest.

In your `SKILL.md`, reference env vars exactly as the shell sees them
(`-H "Authorization: Bearer $AIRTABLE_API_KEY"`). Don't restate how to set them.

---

## 8. Installs and scripts

### `post-install.sh`

Runs **once at image build** as a cached Docker layer (`dockerfile.go` emits
`RUN .../post-install.sh`). Use it for `apt`/`pip`/`npm` installs.

- Start with `#!/bin/sh` and `set -eu`.
- **Idempotent** and minimal. The base image
  (`gcr.io/robomotion/robomotion-skills-base`) already ships **python3, node20,
  jq, git, curl, wget, ca-certificates** — only add what's genuinely missing.
- A non-zero exit **fails the image build**. If a step is best-effort, guard it
  (`... || true`) — but prefer steps that reliably succeed.

```sh
#!/bin/sh
# PyMuPDF for text + table extraction.
set -eu
pip3 install --no-cache-dir --break-system-packages pymupdf
```

For an OS CLI (the `gh` / GitHub-CLI pattern), see `github-issues/post-install.sh`.

### `pre-run.sh`

Chmod'd at build, executed by the entrypoint at **every container start**. Use it
for login ceremonies that need fresh credentials each run. Most skills don't need
one.

### `scripts/`

Ship a helper CLI the model invokes via the `terminal` tool. Conventions:

- **Stdlib-first.** Prefer zero third-party deps (Python `urllib`, `argparse`,
  `json`) so you don't need a `post-install.sh` — see `arxiv`, `linear`,
  `spotify`. (Shipping `scripts/` still forces container mode regardless.)
- **Pin the path with `${SKILL_DIR}`** in `SKILL.md`:
  `python3 ${SKILL_DIR}/scripts/foo.py --bar baz`.
- **Read credentials from env** (the vars you declared in `env.required`).
- **Print JSON to stdout**, including a clean `{"error": "..."}` on failure — the
  model reads stdout; never let a traceback leak.
- Mark the script executable (`chmod +x`).
- Map upstream failure modes to clear messages (auth revoked, rate limit, "no
  active device", etc.) so the model can react instead of looping.

---

### Shared library (`_shared/`)

When skills share **code/docs**, ship a **`_shared/`** dir (CLIs in
`_shared/scripts/`, guides in `_shared/references/`, optionally a
`_shared/post-install.sh` for shared deps). A skill's **`${SHARED_DIR}`** token
resolves to the **nearest `_shared/` walking up its path** — group-scoped, with
the repo root as fallback:

```
marketing-skills/_shared/     → marketing-skills/* skills
_shared/  (repo root)         → fallback for everything else
```
```sh
node ${SHARED_DIR}/scripts/ga4.js report --property 123
```

- `${SHARED_DIR}` → nearest `_shared/` up the skill's path (key
  `<owner>__<repo>__<group>___shared`, or `…___shared` at root); left literal if none.
- A `_shared/scripts/` (or `_shared/post-install.sh`) forces **container mode**.
- Each `_shared/`'s content is hashed into the image key, so editing a shared CLI rebuilds.

**Env stays per-skill — `_shared/` carries no env.** A shared CLI library can need
dozens of credentials, but each skill uses only a few. So a skill that calls
`${SHARED_DIR}/scripts/ga4.js` declares `GA4_ACCESS_TOKEN` in **its own**
`env.required`/`env.optional` (§7) — never in `_shared/`. The launcher ignores any
`_shared/env.*`; this keeps the run requiring (and the Designer showing) only the
vars the *active* skills use, not the whole library. Names dedup across skills, so
one binding covers every skill that shares a CLI.

Prefer `_shared/` over copying the same CLI into many skills. This is the
mechanism for porting shared-library collections (e.g. a repo of marketing
skills backed by one CLI library) into Robomotion. (Cross-agent front-matter
compatibility, which pairs with this for ingesting spec repos, is covered in §5.)

## 9. Writing a brand-new skill

1. **Pick the capability surface** (§1–§2): `curl` via `terminal`, a built-in
   toolset, or a CLI you ship in `scripts/`.
2. **Create the folder** `mkdir <skill-name>` (kebab-case).
3. **Write `SKILL.md`** with the front-matter and body structure in §5.
4. **Credentials:** add `env.required` (mandatory) and/or `env.optional` (has a
   fallback) with the var names + comments.
5. **Installs:** if you need OS/pip/npm packages, write `post-install.sh`
   (idempotent, minimal).
6. **Scripts:** if you ship a CLI, put it in `scripts/`, make it executable,
   reference it with `${SKILL_DIR}/scripts/...`, and smoke-test it offline.
7. **Add `CHANGELOG.md`** (start at `[1.0.0]`) and **`LICENSE`** (MIT; see an
   existing skill for the two-copyright wording).
8. **Update `README.md`** — add a row to the Inventory table (alphabetical).
9. **Verify** (§12) and open a PR.

---

## 10. Porting an upstream Hermes skill

First confirm it's portable (§2). Then apply this transformation:

| Aspect | Source (`hermes-agent/skills/<cat>/<name>/`) | Ported (`robomotion-skills/<name>/`) |
|---|---|---|
| Location | nested under a category | flattened to repo root; folder == `name:` |
| Front-matter | `name, description, version, author, license, platforms, prerequisites, metadata.hermes.*` | trimmed to `name, version, summary, tags` |
| Version | upstream value | `1.0.0` (note upstream version in CHANGELOG) |
| Install prose | "Setup", `apt`/`pip`/`npm`, "set ENV in `~/.hermes/.env`" **in** SKILL.md | **removed** → `post-install.sh` + `env.required`/`env.optional` |
| Path refs | `~/.hermes/...` / relative `scripts/foo.py` | `${SKILL_DIR}/scripts/foo.py` |
| Body | reference dump | + Capabilities, When-to / When-NOT, Operating notes, Attribution |
| Plugin-tool skill | documents `spotify_*` etc. | **rewrite** as a `scripts/` CLI over the Web API (§2) |
| New files | — | `env.required`/`env.optional`, `post-install.sh`/`pre-run.sh` (if needed), `CHANGELOG.md`, `LICENSE` |
| Kept | `scripts/`, `references/` | same (rewrite path refs to `${SKILL_DIR}`) |

> Porting a **non-Hermes** skill (agentskills.io / Claude-plugin spec, e.g. a
> marketing-skills repo)? You can skip most of the front-matter rewrite — keep
> `name` + `description` + `metadata.version`, add `tags`, rewrite path refs, and
> add `LICENSE`/`CHANGELOG`. See §5 *Cross-agent compatibility* and §11(e). If the
> repo uses a shared CLI library, port it under `_shared/` (§8).

Step by step:

1. Copy the source folder to `robomotion-skills/<name>/` (flatten out the
   category).
2. Rewrite the front-matter to the four-field shape; set `version: 1.0.0`.
3. Move install instructions out of the body: package installs → `post-install.sh`;
   env vars → `env.required` (or `env.optional` if it has a fallback). Delete the
   "Setup" / "Prerequisites" prose.
4. Rewrite every path reference to `${SKILL_DIR}/...`.
5. Restructure the body: add Capabilities, When-to-use, When-NOT-to-use, Operating
   notes, and an Attribution line.
6. If it's a plugin-tool skill, **rewrite the capability** as a stdlib CLI in
   `scripts/` with vault-based headless auth; document its subcommands in Usage.
7. Add `CHANGELOG.md` (record what you changed from upstream) and `LICENSE`.
8. Update `README.md` Inventory.
9. Verify (§12) and open a PR.

---

## 11. Worked examples

All of these live in this repo — read them alongside this section.

### (a) curl + required key → `linear`, `airtable`
Pure `curl` against a REST/GraphQL API. `airtable` ships only `SKILL.md` +
`env.required` (host mode, pure-knowledge); `linear` additionally ships a stdlib
`scripts/linear_api.py` ergonomics wrapper (→ container mode). Both declare a
single required key. Install prose from upstream became `env.required` comments.

### (b) pure-knowledge, no script → `airtable`, `notion`
No `scripts/`, no `post-install.sh` → **host mode**. `notion` was reduced to the
HTTP-API/`curl` path only (upstream's `ntn` CLI + hosted Workers were dropped as a
poor fit for a headless sandbox), and keeps `references/block-types.md`.

### (c) filesystem / host mode + optional env → `obsidian`
Uses the built-in `file` toolset, so it's portable without a script. Deliberately
ships **no** `scripts/` so it stays **host mode** and can reach the real vault on
disk. Declares `OBSIDIAN_VAULT_PATH` in **`env.optional`** (it falls back to a
default path) — the canonical example of when to choose optional over required.

### (d) plugin → CLI rewrite → `spotify`
Upstream `spotify` was a **plugin** exposing `spotify_*` tools — not portable as
prose. Rewritten as `scripts/spotify_api.py`, a stdlib CLI over the Spotify Web
API driven by `terminal`. Headless auth uses vault-bound
`SPOTIFY_CLIENT_ID`/`SPOTIFY_CLIENT_SECRET`/`SPOTIFY_REFRESH_TOKEN` (refresh
flow) instead of interactive OAuth. Container mode (ships a script).

### (e) cross-agent spec port → `cro`, `copywriting`, `cold-email`, `pricing`, `marketing-psychology`
Pure-knowledge skills lifted from [marketingskills](https://github.com/coreyhaines31/marketingskills),
an agentskills.io / Claude-plugin collection. Ported in **native spec
front-matter** (`name` + `description` + `metadata.version`, plus `tags`) to
exercise the §5 compatibility shims — no four-field rewrite. `references/` came
along; `evals/` and the repo's shared CLI library were left out. All host mode.
A repo like this with live tools would carry its CLI library under `_shared/` (§8).

---

## 12. Testing & verification

Before opening a PR, confirm:

```sh
# 1. Folder name matches front-matter `name:`
grep -m1 '^name:' <skill>/SKILL.md      # must equal the directory name

# 2. Classification is what you intend
#    container if post-install.sh OR non-empty scripts/ ; else host
ls <skill>/post-install.sh <skill>/scripts/ 2>/dev/null

# 3. Required files present
ls <skill>/SKILL.md <skill>/CHANGELOG.md <skill>/LICENSE

# 4. env files are name-only, valid identifiers
cat <skill>/env.required <skill>/env.optional 2>/dev/null
```

If you shipped a script:

```sh
python3 -m py_compile <skill>/scripts/*.py        # compiles
python3 <skill>/scripts/foo.py --help             # CLI surface
# error path must print clean JSON, not a traceback:
env -u THE_REQUIRED_KEY python3 <skill>/scripts/foo.py <subcmd>
chmod +x <skill>/scripts/*.py                       # executable bit
```

Also: every command in `SKILL.md`'s Usage section must match the script's actual
flags (a model trusts the docs — wrong examples burn recovery tool calls).

If you changed the **launcher** or **Designer** (e.g. extending the env contract):

```sh
# launcher
cd packages-main/src/hermes-agent/launcher && go vet ./... && go test ./...
# designer
cd robomotion-new-designer && npx tsc --noEmit -p tsconfig.app.json
```

---

## 13. Pitfalls & gotchas

- **Copying a plugin-backed skill's `SKILL.md` verbatim.** The model will call
  tools that don't exist. Rewrite to a CLI (§2, §11d).
- **Leaving install prose in `SKILL.md`.** The launcher handles installs; the body
  should be pure knowledge. Move it to `post-install.sh` / `env.required`.
- **Putting an optional var in `env.required`.** It will block every run that
  doesn't set it. Use `env.optional` when there's a fallback.
- **Adding `scripts/` to a host-only skill.** It forces container mode; a
  filesystem skill (like `obsidian`) then can't see host files.
- **Forgetting to bump `version:`** after editing a script or `post-install.sh` —
  the image cache may serve a stale build on a moving branch.
- **`post-install.sh` that can fail the build.** A non-zero exit aborts the image.
  Keep it reliable; guard best-effort steps.
- **Reinstalling what the base image already has** (python3/node20/jq/git/curl/
  wget/ca-certificates). Don't.
- **Scripts that print tracebacks.** Catch errors and emit `{"error": "..."}`.
- **Hand-encoding URLs / formulas.** Let `python3 -m urllib.parse` do it (see
  `airtable`'s `filterByFormula` pattern).
- **Repo-level `tools/` instead of `_shared/`.** The launcher extracts each skill
  folder in isolation, so a sibling `tools/` dir is never shipped with a skill and
  `../../tools/...` won't resolve. Put shared code in `_shared/` and reference it
  with `${SHARED_DIR}`.
- **`${SHARED_DIR}` left literal at runtime.** It only resolves when the repo
  actually ships a `_shared/` dir; an unresolved token means the dir is missing.

---

## 14. Reference: files & paths

**This repo (`robomotion-skills`)**
- `README.md` — folder contract, classification, inventory, authoring checklist
- `build-index.py` → `index.json` — the discovery manifest the Designer reads
  (regenerate + commit when adding/changing a skill; CI drift-checks it)
- `validate.sh` + `.github/workflows/validate.yml` — contract checker + index drift-guard
- `docs/skill-system-scale-design.md` — the scale architecture (index → bundles → registry)
- `docs/marketingskills-review-and-skill-system-gaps.md` — review + the skill-system roadmap
- existing skills — the canonical examples (`linear`, `airtable`, `notion`,
  `obsidian`, `spotify`, `github-issues`, `arxiv`, the marketing pilots, …)

**Hermes Agent package (`packages-main/src/hermes-agent/`)**
- `nodes/skills/skill_loader.py` — reads `SKILL.md`, substitutes `${SKILL_DIR}` /
  `${SESSION_ID}` / `${SHARED_DIR}` (`local_shared_path`), injects into the prompt
- `nodes/agent/hermes_agent.py` — the node; `_HERMES_INTERNAL_TOOLS` (the
  built-in toolset catalog), curated models, assets
- `launcher/skills.go` — fetch/extract active skills + repo `_shared/`, install
  dir naming, `version:` / `metadata.version` read (`readSkillVersion`),
  `dirContentHash`
- `launcher/launchplan.go` — `needsSandbox` (host vs container classification)
- `launcher/dockerfile.go` — base image, image hash (incl. version + `_shared`
  content), `post-install.sh` / `pre-run.sh` wiring
- `launcher/env.go` — `aggregateEnvRequired` / `aggregateEnvOptional`,
  `validateEnvBindings`, `envFlags`
- `launcher/main.go` — `planFromEnvelope`: validate required-only, inject
  required∪optional, cred-proxy fail-closed gate

**Flow Designer (`robomotion-new-designer/src/`)**
- `stores/skills.ts` — Browse-Skills discovery: front-matter parse (`summary`/
  `description`, `metadata.version`), root + nested `skills/<name>/` enumeration
- `components/editors/LLMAgentEditor.tsx` — the Agent Editor shell
- `components/editors/EnvironmentTab.tsx` — fetches each active skill's
  `env.required`/`env.optional` (per-skill only), renders Vault bindings (required
  gate + optional section)
- `components/editors/ToolsTab.tsx` — internal-tool toggles → `optToolsEnvRequired`

**Product context**
- `robomotion-flow-designer-robots-and-agents.md` — the platform guide (Designer,
  Robots, Vaults §12, security model §25, AI Agents §23)
