# Robomotion Skills

Curated skill library for the Robomotion **Hermes Agent**. Each skill is a folder at the repo root containing `SKILL.md` plus optional install/runtime scripts. The agent's launcher fetches the active skill set, builds a per-set Podman image, and exposes the skills to the LLM as system-prompt context inside that container.

## Folder contract

The launcher's `verifySkillRepo` enumerates top-level directories and treats any folder containing `SKILL.md` as a candidate skill.

```
<skill-name>/
  SKILL.md          # required — capability + operating notes for the LLM
  post-install.sh   # optional — runs once at container image build time
  pre-run.sh        # optional — runs at every container start
  env.required      # optional — one ENV var name per line
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

### `scripts/`

The LLM invokes scripts here via the `terminal` tool. Pin the path with:

```bash
SKILL_DIR=$(dirname "$(find /opt/robomotion/skills -name SKILL.md -path '*/<name>/*' | head -1)")
python3 "$SKILL_DIR/scripts/foo.py" --bar baz
```

Skills shipping scripts force container mode (the `scripts/` dir is non-empty, classified as install-bearing).

## Classification

- **Pure-knowledge** (no `post-install.sh`, no non-empty `scripts/`) → host mode. No Podman dependency.
- **Install-bearing** (any active skill has install scripts or non-empty `scripts/`) → container mode.

Mixing is fine: one install-bearing skill puts the whole agent in container mode; pure-knowledge skills work in either mode.

## Inventory

| Skill | Mode | Required env | What it does |
|---|---|---|---|
| `arxiv` | container (script) | — | Search / fetch academic papers from arXiv |
| `excalidraw` | container (script) | — | Generate hand-drawn diagrams; upload to excalidraw.com |
| `github-issues` | container | `GITHUB_TOKEN` | Read, file, comment, close GitHub issues via `gh` |
| `linear` | container (script) | `LINEAR_API_KEY` | Read/write Linear issues via GraphQL |
| `pdf-extract` | container (script) | — | Extract text + tables from PDFs (pymupdf) |
| `polymarket` | container (script) | — | Query Polymarket prediction markets (public, no auth) |

## Authoring checklist

1. Pick a kebab-case folder name; it must match the `name:` front-matter.
2. Write `SKILL.md`. Capabilities + operating notes + routing hints. Skip install prose.
3. If the skill needs OS packages or libraries, write `post-install.sh` and mark it executable.
4. If it ships helpers the LLM invokes, drop them in `scripts/` and document the invocation pattern in `SKILL.md`.
5. If it needs credentials, list them in `env.required`.
6. Open a PR.
