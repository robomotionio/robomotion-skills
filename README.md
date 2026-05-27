# Robomotion Skills

Curated skill library for the Robomotion **Hermes Agent**. Each skill is a folder containing `SKILL.md` plus optional install/runtime scripts — at the repo root, or nested under a group (e.g. `marketing-skills/<category>/<skill>/`). The agent's launcher fetches the active skill set, builds a per-set Podman image, and exposes the skills to the LLM as system-prompt context inside that container.

## Folder contract

Any folder containing `SKILL.md` is a skill, whether at the repo root or nested under a group directory. Discovery is index-driven (`index.json`); the launcher's `verifySkillRepo` enumeration is the fallback.

```
<skill-name>/
  SKILL.md          # required — capability + operating notes for the LLM
  post-install.sh   # optional — runs once at container image build time
  pre-run.sh        # optional — runs at every container start
  env.required      # optional — one ENV var name per line (mandatory creds; blocks the run if unbound)
  env.optional      # optional — one ENV var name per line (optional creds/config; never blocks)
  scripts/          # optional — auxiliary helpers the LLM can invoke via terminal
  references/       # optional — additional markdown the LLM can cat at runtime
```

### `SKILL.md`

Knowledge content the LLM reads at run time. Front-matter:

```yaml
---
name: <skill-name>
summary: <one-line capability statement>
---
```

Followed by capabilities, when-to-use / when-NOT-to-use routing hints, and operating notes. Do NOT put install instructions here — the launcher handles install.

### `post-install.sh`

Runs once at image build. Idempotent. Use for `apt`/`pip`/`npm` installs. The base image already ships python3, node20, jq, git, curl, wget, ca-certs — only add what the skill genuinely needs on top.

### `pre-run.sh`

Runs at every container start. Use for login ceremonies that need fresh credentials.

### `env.required`

One ENV var name per line. Comments (`#`) and blank lines ignored. Designer's Environment tab reads this to drive the Vault-binding UI; the launcher refuses to start an agent run with any required var unbound.

### `env.optional`

Same format as `env.required`, for vars the skill can run **without** (a credential with a sensible default, or config like a path with a fallback). The launcher (`aggregateEnvOptional`) injects these into the sandbox **when bound**, but a missing one **never blocks the run** — only `env.required` gates startup. The Designer surfaces them as non-mandatory bindings in the Environment tab.

Put a var in `env.optional` (not `env.required`) whenever the skill has a documented fallback for it — e.g. `obsidian` declares `OBSIDIAN_VAULT_PATH` here because it falls back to `~/Documents/Obsidian Vault`. Listing such a var as required would wrongly block runs that don't set it.

### `scripts/`

The LLM invokes scripts here via the `terminal` tool. Pin the path with:

```bash
SKILL_DIR=$(dirname "$(find /opt/robomotion/skills -name SKILL.md -path '*/<name>/*' | head -1)")
python3 "$SKILL_DIR/scripts/foo.py" --bar baz
```

Skills shipping scripts force container mode (the `scripts/` dir is non-empty, classified as install-bearing).

## Shared library (`_shared/`)

A repo may ship **`_shared/`** directories of **code and docs** reused across skills — common CLIs (`_shared/scripts/`), integration guides (`_shared/references/`), and optionally a `_shared/post-install.sh` for shared deps. A skill's **`${SHARED_DIR}`** token resolves to the **nearest `_shared/` walking up its path**, so you can scope a shared library to a group, with the repo root as the fallback:

```
acme-skills/
  _shared/                 # fallback: shared by everything
  marketing-skills/
    _shared/               # shared by marketing-skills/* only (ga4, ahrefs, …)
    cold-email/SKILL.md    # ${SHARED_DIR} → marketing-skills/_shared
    cro/SKILL.md           # ${SHARED_DIR} → marketing-skills/_shared
```

```sh
# In any SKILL.md, regardless of how deep it sits:
node ${SHARED_DIR}/scripts/ga4.js report --property 123
```

- `${SHARED_DIR}` → the nearest `_shared/` up the skill's path (key `<owner>__<repo>__<group>___shared`, or `…___shared` at root); left literal if there's none above it.
- A `_shared/` containing `scripts/` (or a `_shared/post-install.sh`) forces **container mode**, so shared tooling always runs sandboxed.
- Each `_shared/`'s content is hashed into the image cache key, so editing a shared CLI forces a rebuild even on a moving branch.

**Credentials stay per-skill — `_shared/` carries no env.** A skill that calls `${SHARED_DIR}/scripts/ga4.js` declares `GA4_ACCESS_TOKEN` in **its own** `env.required`/`env.optional`. This is deliberate: a shared CLI library can need dozens of credentials, but each skill uses only a few — declaring them per skill means the launcher only requires (and the Designer only shows) the vars the *active* skills actually use, instead of every credential in the library. Across skills the names dedup, so one binding covers all skills that share a CLI.

Use `_shared/` instead of vendoring the same CLI into many skills. (This repo's curated skills are self-contained today; `_shared/` exists for shared-library collections.)

## Classification

- **Pure-knowledge** (no `post-install.sh`, no non-empty `scripts/`) → host mode. No Podman dependency.
- **Install-bearing** (any active skill has install scripts or non-empty `scripts/`) → container mode.

Mixing is fine: one install-bearing skill puts the whole agent in container mode; pure-knowledge skills work in either mode.

## Inventory

| Group | Skills | Author | Source |
|---|---|---|---|
| `marketing-skills/` | 41 | Corey Haines | https://github.com/coreyhaines31/marketingskills |
| `engineering-skills/` | 23 | Addy Osmani | https://github.com/addyosmani/agent-skills |
| `ui-ux-pro-max-skill/` | 7 | NextLevelBuilder | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill |

### Marketing skills (`marketing-skills/`) — vendored verbatim

[marketingskills](https://github.com/coreyhaines31/marketingskills) (41 skills;
agentskills.io spec / Claude Code plugin; MIT) is vendored **byte-for-byte** under
`marketing-skills/` — the upstream `skills/`, `tools/`, and `.claude-plugin/` are
mirrored unchanged, so the collection updates with a plain re-sync
(`git subtree pull` / re-copy) and **no per-skill re-port**. The 41
`marketing-skills/skills/<name>/` folders are each individually selectable.

- **Nothing of ours lives inside the mirror** — no edited bodies, no `${SHARED_DIR}`
  rewrites, no injected `env`/`LICENSE`/`CHANGELOG`/`tags`. `validate.sh` detects a
  vendored collection (an ancestor `.claude-plugin/plugin.json`) and skips the
  per-skill LICENSE/CHANGELOG convention — those are governed by the collection's
  own upstream `LICENSE`. It still `node --check`s the bundled `tools/clis/`.
- **Capability is CLI-favored.** Skills are knowledge; tools come from the bundled
  CLIs in `marketing-skills/tools/clis/` run via the `terminal` tool (MCP only when
  no usable CLI exists). Putting those CLIs on `$PATH`, and injecting tool
  credentials, are **platform/overlay** concerns wired *beside* the mirror — never
  files added to it. See `how-to-write-or-port-a-skill-to-robomotion.md` §10 and
  `docs/agent-files.md`.
- **Bump:** re-sync `marketing-skills/` from upstream, then run `build-index.py`.

## Discovery index (`index.json`)

A generated **`index.json`** at the repo root is the discovery manifest — for each skill: name, path, group, summary, tags, version, mode, env, the nearest `_shared`, a `contentHash`, and the `files` manifest. It serves two consumers, so neither has to walk the repo:

- **Designer** reads it to browse/search/show env — one fetch instead of probing every `SKILL.md` over the GitHub API (which rate-limits).
- **Launcher** reads it to fetch **only the active skills** (+ their nearest `_shared`) file-by-file from `raw.githubusercontent`, instead of downloading the whole-repo tarball.

Both scale to thousands of skills; both fall back to the old behavior when a repo ships no index. See `docs/skill-system-scale-design.md`.

Regenerate it whenever you add or change a skill:

```sh
python3 build-index.py            # writes index.json
python3 build-index.py --check    # CI: fails if index.json is stale
```

`index.json` is committed; CI (`validate.yml`) fails a PR whose index is out of date. The Designer falls back to live enumeration for repos that don't ship an index.

## Authoring checklist

1. Pick a kebab-case folder name; it must match the `name:` front-matter.
2. Write `SKILL.md`. Capabilities + operating notes + routing hints. Skip install prose.
3. If the skill needs OS packages or libraries, write `post-install.sh` and mark it executable.
4. If it ships helpers the LLM invokes, drop them in `scripts/` and document the invocation pattern in `SKILL.md`.
5. If it needs credentials, list the mandatory ones in `env.required` and any with a fallback in `env.optional`.
6. Run `python3 build-index.py` and commit the updated `index.json`.
7. Run `bash validate.sh`, then open a PR.
