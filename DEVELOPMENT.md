# Developing Robomotion Skills

How this repository is built, checked and extended. For the list of skills, see [README.md](README.md). The full porting guide is [how-to-write-or-port-a-skill-to-robomotion.md](how-to-write-or-port-a-skill-to-robomotion.md).

## How the agent uses this repo

The Hermes Agent's launcher reads `index.yaml`, fetches the active skills, builds a per-set Podman image, and exposes the skills to the LLM as system-prompt context inside that container. The Designer reads the same index to let users browse skills and bind their credentials.

## Folder contract

A **unit** is any folder with a `.robomotion/skill.yaml`: a **group** of skills (every unit in this repo today) or a standalone skill. Inside a group, any folder containing `SKILL.md` under `skills/`, `.claude/skills/` or `plugins/<plugin>/skills/` is a skill, at any depth. Discovery is index-driven (`index.yaml`); the launcher's `verifySkillRepo` enumeration is the fallback.

```
<group>/
  .robomotion/          # ours, never taken from upstream
    skill.yaml          # required — title, author, source_url, license, category, summary, tags, version
    LICENSE             # the licence we redistribute the group under
    CHANGELOG.md
    patches/            # optional — our recorded edits to upstream files
    post-install.sh     # optional — group-wide install hook, runs once at image build
    env.yaml            # optional — integration → credential overlay
  skills/<skill-name>/
    SKILL.md            # required — capability + operating notes for the LLM
    post-install.sh     # optional — runs once at container image build time
    pre-run.sh          # optional — runs at every container start
    env.required        # optional — one ENV var name per line (mandatory creds; blocks the run if unbound)
    env.optional        # optional — one ENV var name per line (optional creds/config; never blocks)
    scripts/            # optional — auxiliary helpers the LLM can invoke via terminal
    references/         # optional — additional markdown the LLM can cat at runtime
```

### `.robomotion/`

Our metadata and edits, kept beside the upstream content and never inside it.

- **`skill.yaml`** is the only source `build-index.py` reads for a group; upstream metadata such as `.claude-plugin/plugin.json` is ignored. Every skill in a group takes the group's `version`. Its `summary` is the pack description shown in the README and the Designer.
- **`patches/`** holds every edit we make to upstream files. `sync-upstream.py` applies them after each sync.
- **`post-install.sh`** is where a group's install exceptions go.
- **`env.yaml`** maps a group's integrations to the credentials each one takes, for groups whose skills can use many alternative tools (`marketing-skills`). Per-skill `env.required` / `env.optional` stay the source of truth.

### `SKILL.md`

Knowledge content the LLM reads at run time. Front-matter:

```yaml
---
name: <skill-name>
description: <one-line capability statement>
---
```

The indexer takes `summary:` first and falls back to `description:` (the Agent Skills standard). Followed by capabilities, when-to-use / when-NOT-to-use routing hints, and operating notes. Do NOT put install instructions here — the launcher handles install.

### `post-install.sh`

Runs once at image build. Idempotent. Use for `apt`/`pip`/`npm` installs. The base image already ships python3, node20, jq, git, curl, wget, ca-certs — only add what the skill genuinely needs on top.

### `pre-run.sh`

Runs at every container start. Use for login ceremonies that need fresh credentials.

### `env.required`

One ENV var name per line. Comments (`#`) and blank lines ignored. Designer's Environment tab reads this to drive the Vault-binding UI; the launcher refuses to start an agent run with any required var unbound.

### `env.optional`

Same format as `env.required`, for vars the skill can run **without** (a credential with a sensible default, or config like a path with a fallback). The launcher (`aggregateEnvOptional`) injects these into the sandbox **when bound**, but a missing one **never blocks the run** — only `env.required` gates startup. The Designer surfaces them as non-mandatory bindings in the Environment tab.

Put a var in `env.optional` (not `env.required`) whenever the skill has a real fallback for it — e.g. every `marketing-skills` skill lists its tool credentials here, because each can use any of several alternative tools, or none, so no single key is a prerequisite. Listing such a var as required would wrongly block runs that don't set it.

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

Use `_shared/` instead of vendoring the same CLI into many skills. (No group in this repo uses `_shared/` today; vendored groups keep their upstream layout.)

## Classification

- **Pure-knowledge** (no `post-install.sh`, no non-empty `scripts/`) → host mode. No Podman dependency.
- **Install-bearing** (any active skill has install scripts or non-empty `scripts/`, or its group ships `.robomotion/post-install.sh` or `bin/`) → container mode. `build-index.py` classifies the same way as the launcher's `needsSandbox`, so every skill of such a group is indexed `container`.

Mixing is fine: one install-bearing skill puts the whole agent in container mode; pure-knowledge skills work in either mode. `index.yaml` records each skill's `mode`.

## Third-party groups: `upstreams.yaml`

A third-party group is never copied in or edited by hand. `upstreams.yaml`
records, per group, the upstream commit it was built from, and
`sync-upstream.py` is the only thing that writes vendored content:

```
upstream tree at `commit`  -  exclude  +  .robomotion/patches  =  the group folder
```

Ours stay ours: `.robomotion/` and the launcher hooks (`post-install.sh`,
`pre-run.sh`, `env.required`, `env.optional`) are never taken from upstream,
so a project that learns our folder contract cannot plant one.

```sh
python3 sync-upstream.py status            # how far behind each group is
python3 sync-upstream.py sync <group>      # move it to the newest commit that has aged 7 days
python3 sync-upstream.py verify            # CI: the tree is what the manifest says, or fail
python3 scan-skills.py --changed           # tripwires on what a change touches
```

A weekly workflow opens one pull request per group that moved. Its body lists
the upstream commits, the code that can run, and hosts the group never named
before. **A person reads the diff; a clean scan is not an approval.** An edit
to upstream content is a patch file in `.robomotion/patches/`, never an edit
in place: `verify` fails the build on one. A sync whose upstream licence file
changed stops until someone reads it and re-runs with `--accept-license`.

### How a repository gets in

A repository is added when it is popular (skills.sh installs, with GitHub stars and official publishers as secondary signals) **and**:

- it ships a licence that lets us redistribute it (`sync-upstream.py add` refuses a repo without one);
- its skills can do something inside the agent's sandbox;
- `scan-skills.py` finds nothing blocking, or a person has read and accepted each finding in `scan-accepted.yaml`.

A popular repository is not a safe one. Install counts are not a quality or security score, and every group is read before it lands.

### Adding a group

```sh
python3 sync-upstream.py add <group> <repo-url> \
  --title "…" --author "…" --license MIT --category Engineering --summary "…" \
  --include skills LICENSE            # only the folders that hold skills
python3 scan-skills.py <group>        # read every finding; accept or exclude
python3 build-index.py && python3 build-readme.py
bash validate.sh
```

`add` pins the newest upstream commit that has aged 7 days, writes the
group's `.robomotion/` (`skill.yaml`, `LICENSE`, `CHANGELOG.md`) and builds
the folder. Use `--exclude` for skills we can't redistribute or run, and
`--subdir` / `--into` when upstream keeps its skills somewhere other than `skills/`.

### Where a group differs from upstream

| Group | Difference |
|---|---|
| `anthropic-skills/` | Apache-licensed skills only; `docx`, `pdf`, `pptx` and `xlsx` are rights-reserved |
| `caveman-skills/` | MIT-licensed skills only, minus the eight that need Caveman Cloud (its gateway sees a repo's LLM traffic), the `caveman` CLI, or Claude Code's hooks and sub-agents |
| `openai-skills/` | `skills/.curated` only, minus the Figma skills (under Figma's developer terms, not a licence) and four for Codex or Windows apps: `hatch-pet`, `migrate-to-codex`, `chatgpt-apps`, `winui-app`. The Notion skills are MIT and need a Notion MCP server. Upstream is deprecated and the pin is its last commit; its successor, `openai/plugins`, carries none of these skills and has no repository licence, so the group stays here as it is |
| `mattpocock-skills/` | `engineering` and `productivity` folders only |
| `google-skills/` | One skill excluded: it executes base64-decoded code |
| `gws-cli/` | Skills only, not the CLI source |
| `awesome-copilot/` | 47 of 456 skills: those above 10K skills.sh installs (installing the whole pack gives every skill about 9K), minus ten that need a tool, account or IDE the sandbox lacks |
| `marketing-skills/` | Patched; `.robomotion/post-install.sh` wraps `tools/clis/*.js` as short-name commands on `$PATH` |
| `claude-seo/` | Patched: reports say Robomotion; `seo-drift` keeps its baselines in `$CLAUDE_SEO_DRIFT_DIR`, which the image points at `/workspace` so they survive between runs; the Keywords Everywhere client calls the current API (upstream #312). Its Python runtime and Chromium are built at image build |
| `ui-ux-pro-max-skill/` | Patched. Pinned at the commit that fixes the slide generator's stored XSS (upstream #274, with #275 and #283) |
| `hyperframes/` | Chrome, FFmpeg and local voice, caption and matting models installed at image build. `embedded-captions` is patched to find `/opt/hyperframes/root`, a source-checkout-shaped folder the hook builds, since its scripts expect one |
| `higgsfield-skills/` | CLI installed at a pinned version at image build, so the skills never pipe an unpinned installer; its telemetry and update check off. Sign-in is browser OAuth only (no API key), so an agent cannot sign in by itself |
| `knowledge-work-plugins/` | 13 plugins; not `partner-built`, `bio-research`, `cowork-plugin-management`, `pdf-viewer`, or `small-business` (its own group). Product management's `competitive-brief` is left out: marketing's has the same name. No MCP config, plugin manifests or slash commands |
| `small-business-skills/` | The `small-business` plugin of `anthropics/knowledge-work-plugins` as a group of its own, so its `lead-triage` and the sales plugin's keep their own ids |
| `financial-services/` | `plugins/vertical-plugins` only; no hooks, slash commands, MCP config, or the copied `skill-creator`. Patched: `dcf-model` weights WACC on gross debt and its validator checks the WACC band (upstream #340, #337); `ib-check-deck` compares figures within a fiscal period, so a multi-year deck is no longer flagged against itself (#339) |
| `aws-skills/` | `skills/` only, minus `aws-transform` (pipes its CLI installer, runs jobs from `~/.aws`) and `rds-db2` (pipes a bit.ly link into bash) |
| `firecrawl-skills/` | `core` and `workflows` only (`build` is for apps that call Firecrawl); CLI installed at a pinned version at image build, its update check and telemetry off |
| `tavily-skills/` | Patched (setup says the CLI is installed); CLI installed at a pinned version at image build |
| `officecli/` | Patched (setup says the CLI is installed); the release binary is installed at a pinned version and checked by hash, its self-update and self-install off; style-sample `.pptx` files left out |
| `impeccable/` | Engine binary and a headless Chrome installed at pinned versions at image build and checked by hash, so the launcher never downloads the engine on first use |
| `elevenlabs-skills/` | `env.required` added per skill: upstream declares `ELEVENLABS_API_KEY` only in frontmatter (`metadata.openclaw.requires.env`), which `detect-env.py` now reads |
| `last30days-skill/` | The engine's media (`assets/`, `agents/`) and its macOS Keychain and browser sign-in scripts left out. Patched: with `SCRAPEDO_TOKEN` set, Reddit and YouTube go through Scrape.do (`SCRAPEDO_GEO` picks the country), plus `google-trends` (Scrape.do's Google Trends) and `fetch-covers` (video thumbnails and post images); the first-run wizard is skipped in the sandbox. yt-dlp installed at a pinned version at image build (the zipapp, so it trusts the proxy CA) |

### Popular, but not here

| Repository | Why |
|---|---|
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | No licence file |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | No licence file |
| [101-skills/superpowers](https://github.com/101-skills/superpowers) | Unlicensed copy of an unlicensed repo |
| [flowkit-labs/skills](https://github.com/flowkit-labs/skills) | New anonymous repo whose own README installs from a different org |
| [stablyai/orca](https://github.com/stablyai/orca) | Its skills drive the Orca desktop IDE through its own CLI, which no sandbox has. Added, then removed |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) (`find-skills`) | Tells the agent to install any skill from skills.sh at run time (`npx skills add … -g -y`), past this review. Added, then removed |
| [microsoft/skills](https://github.com/microsoft/skills) | About 1.3K skills.sh installs across 213 skills; `azure-skills` covers Azure. Added, then removed |
| [lllllllama/RigorPilot-Skills](https://github.com/lllllllama/RigorPilot-Skills) | Deep-learning paper reproduction; its install count was a four-week spike, then about 50 a week. Added, then removed |
| [ScrapeGraphAI/just-scrape](https://github.com/ScrapeGraphAI/just-scrape) | Single-digit weekly installs; `firecrawl-skills` covers scraping. Added, then removed |
| [runcomfy-com/skills](https://github.com/runcomfy-com/skills) | 364 installs; the popular listings were copies of it. Replicate, Higgsfield and ElevenLabs cover generation. Added, then removed |
| [firecrawl/cli](https://github.com/firecrawl/cli) | No licence file; `firecrawl/skills` carries the same skills under ISC |
| [apify/agent-skills](https://github.com/apify/agent-skills), [browserbase/skills](https://github.com/browserbase/skills) | No licence file |

## Discovery index (`index.yaml`)

A generated **`index.yaml`** at the repo root is the discovery manifest. `build-index.py` builds it from each unit's `.robomotion/skill.yaml`: a `groups[]` list, each with its metadata, a `content_hash`, the group-level `files`, and a `skills[]` row per skill — id, name, path, summary, version, tags, mode, env (`required` / `optional`), `content_hash`, the `files` manifest, and the group's author, source, licence and category copied in. It serves two consumers, so neither has to walk the repo:

- **Designer** reads it to browse/search/show env — one fetch instead of probing every `SKILL.md` over the GitHub API (which rate-limits).
- **Launcher** reads it to fetch **only the active skills** (and the group files they need) file-by-file from `raw.githubusercontent`, instead of downloading the whole-repo tarball.

Both scale to thousands of skills; both fall back to the old behavior when a repo ships no index. See `docs/skill-system-scale-design.md`.

Regenerate it whenever you add or change a skill:

```sh
python3 build-index.py            # writes index.yaml
python3 build-index.py --check    # CI: fails if index.yaml is stale
```

`index.yaml` is committed; CI (`validate.yml`) fails a PR whose index is out of date. The Designer falls back to live enumeration for repos that don't ship an index.

## README inventory (`build-readme.py`)

The pack table and skill lists in `README.md` are generated from `index.yaml`, between the `BEGIN GENERATED` / `END GENERATED` markers. Pack descriptions come from each group's `.robomotion/skill.yaml` `summary`; skill descriptions are the first sentence of each skill's summary. Run it after `build-index.py`:

```sh
python3 build-readme.py            # rewrites the generated part of README.md
python3 build-readme.py --check    # exit 1 if README.md is stale
```

## Authoring checklist

For a first-party skill (third-party groups: see [Adding a group](#adding-a-group)):

1. Pick a kebab-case folder name under a group's `skills/`; it must match the `name:` front-matter. A new group also needs `.robomotion/skill.yaml`, `LICENSE` and `CHANGELOG.md`.
2. Write `SKILL.md`. Capabilities + operating notes + routing hints. Skip install prose.
3. If the skill needs OS packages or libraries, write `post-install.sh` and mark it executable.
4. If it ships helpers the LLM invokes, drop them in `scripts/` and document the invocation pattern in `SKILL.md`.
5. If it needs credentials, list the mandatory ones in `env.required` and any with a fallback in `env.optional`.
6. Bump `version` in the group's `.robomotion/skill.yaml` if you changed an install hook, so the image cache rebuilds.
7. Run `python3 build-index.py && python3 build-readme.py` and commit `index.yaml` and `README.md`.
8. Run `python3 scan-skills.py --changed` and `bash validate.sh`, then open a PR.
