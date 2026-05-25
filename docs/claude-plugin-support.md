# Vendored collections (Claude-Code / agentskills plugins)

> How Robomotion ingests a **third-party skill collection** (an agentskills.io
> collection or Claude-Code plugin) **byte-for-byte** and makes it work at runtime
> — generically, keyed only off the standard `.claude-plugin/plugin.json` marker.
> No per-collection or per-skill code. The next of the "hundreds of skills" is a
> `git subtree` away, not a port.

## The principle

A third-party collection is a **vendored dependency**: mirror it verbatim, never
edit skill bodies, bump it with a re-sync. Anything Robomotion needs that upstream
lacks lives in the platform or beside the mirror — never inside the synced tree.
Capability is **CLI-favored** (bundled CLIs via the `terminal` tool; MCP only when
no usable CLI). See `how-to-write-or-port-a-skill-to-robomotion.md` §10.

## Detection (the one marker)

A directory holding **`.claude-plugin/plugin.json`** is a collection. That's it —
no repo/skill names anywhere in the platform.

## The contract: `index.json` schema v2 (`build-index.py`)

- Per skill: **`plugin`** = nearest ancestor dir that is a collection (or `null`).
- Top-level **`plugins[]`**: each collection's **shared (non-skill) assets** —
  `tools/`, `bin/`, `.claude-plugin/`, root docs (everything under the collection
  root *except* its own `skills/`) — with a `files` manifest + `contentHash`.

## Staging (launcher, `skills.go` `fetchViaIndex`)

For a skill whose entry has `plugin` set, the launcher stages
**structure-preserving** so the skill's *own* repo-relative refs resolve:

```
HERMES_HOME/skills/<owner>__<repo>__<plugin-slug>/     ← collection root (= ${CLAUDE_PLUGIN_ROOT})
  .claude-plugin/plugin.json   tools/…   bin/…         ← shared assets (from plugins[]), staged once
  skills/<name>/SKILL.md …                             ← each ACTIVE skill, nested at its repo-relative path
```

- One **`__plugin__` sentinel** `resolvedSkill` per collection drives a single
  Dockerfile `COPY` + image hash + classification; the nested active skills are
  discovered on disk by the loader, not re-COPYed.
- `pluginKey(owner, repo, pluginPath)` (launcher) == `_plugin_key` (loader) ==
  `<owner>__<repo>__<plugin-slug>` (slug = path with `/`→`--`).
- The loader reads from the **bind-mounted `HERMES_HOME/skills`** in both host and
  container mode; the baked image copy (`/opt/robomotion/skills`) is build/
  post-install only.

## Resolution (loader, `skill_loader.py`)

- **`local_skill_path`** is collection-aware (disk discovery): a skill under a
  staged collection resolves nested; otherwise the existing flat
  `<owner>__<repo>__<name>` layout — so non-collection skills are unaffected.
- **`${CLAUDE_PLUGIN_ROOT}`** / `${HERMES_PLUGIN_ROOT}` → the staged collection root.
- Because verbatim skills keep their own `../../tools/…` refs (we don't rewrite
  them), the rendered section header emits an **install/plugin-root hint** so the
  model resolves those relative paths against the skill's staged path.

## Capability

- **`bin/` → `$PATH`** (standard plugin convention): a collection shipping `bin/`
  forces container mode (`needsSandbox`), and the generated Dockerfile chmod's +
  prepends it to `$PATH` — bare-name CLIs work via the `terminal` tool.
- A collection using a non-standard CLI dir (e.g. marketingskills' `tools/clis/`)
  isn't auto-PATHed; its CLIs run by full path
  (`node ${CLAUDE_PLUGIN_ROOT}/tools/clis/x.js`).
- Credentials: per-skill `env.required`/`env.optional` injected + brokered by the
  credproxy. A verbatim collection without env files carries none; a future
  credential overlay would sit *beside* the mirror, not inside it.

## Status

- ✅ Index contract, launcher staging, loader resolution + `${CLAUDE_PLUGIN_ROOT}`
  + hint, and `bin/`→`$PATH` are implemented and unit-tested
  (`TestFetchViaIndexPlugin`, `TestGenerateDockerfilePluginBinPath`).
- ✅ Chain-verified against the real `marketing-skills/` mirror: `analytics` loads
  and its verbatim `../../tools/integrations/ga4.md` resolves to the staged file.
- ⏳ **Live agent run** (host + container, with an LLM) is the final validation.

## Adding the next collection

1. Vendor it verbatim under a top-level dir (e.g. `git subtree add`), keeping its
   `skills/`, `tools/`, and `.claude-plugin/`.
2. `python3 build-index.py` (it auto-detects the `.claude-plugin` marker).
3. Done — discovery, staging, and resolution are generic.

## Source commits

- `robomotion-skills`: verbatim mirror + `build-index.py` schema v2.
- `packages-main`: `skill_loader.py` (token + paths + hint), `skills.go`
  (collection staging), `dockerfile.go` (COPY + `bin/`→`$PATH`), `launchplan.go`
  (`needsSandbox` `bin/`).
