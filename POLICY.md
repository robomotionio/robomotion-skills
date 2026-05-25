# Robomotion Skills Validation Policy

Versioned policy profiles applied at publish time. Each entry's
`policy.version` records the profile version it was approved under, so
clients can revalidate when a profile changes.

## Profile: `markdown-only` — version `2026-05-02`

The only profile shipped in Phase 1. Applies to every entry with
`role: D` or `role: W`.

### Rule 1 — File allowlist

The skill's directory tarball may contain only:

| Path                                   | Notes |
|----------------------------------------|-------|
| `SKILL.md`                             | Required. |
| `eval-set.json`                        | Required for D/W. |
| `LICENSE`                              | Required when `source.license` set. |
| `NOTICE`                               | Optional. |
| `references/**`                        | Allowed extensions (see below). |
| `assets/**`                            | Same filter as `references/**`. |
| `templates/**`                         | Same filter as `references/**`. |

Allowed leaf extensions inside `references/`, `assets/`, `templates/`:

- Text/markup: `.md`, `.txt`, `.html`, `.htm`
- LaTeX templates: `.tex`, `.sty`, `.bib`, `.bst`, `.cls`
- Config/data: `.json`, `.yaml`, `.yml`, `.toml`, `.csv`, `.tsv`
- Diagrams as text: `.mmd` (Mermaid), `.puml` (PlantUML), `.dot` (Graphviz)
- Images: `.png`, `.jpg`, `.jpeg`, `.svg`

**Never allowed**: `.pdf` (carries embedded JavaScript and fonts),
`.docx`/`.xlsx`/`.pptx` (Office binary), arbitrary binaries.
| `USAGE.md`                             | Hand-authored notes for `role: W` (optional). |

Rejected outright:

- `scripts/**`
- Any executable file (`.sh`, `.py`, `.js`, `.ts`, `.exe`, `.bat`, `.ps1`, `.bin`, …)
- Hidden files except `.gitkeep`
- Package-manager files (`package.json`, `requirements.txt`,
  `pyproject.toml`, `Cargo.toml`, `go.mod`, …)
- `.env`, credential files
- Symlinks
- Any file outside the single skill root

A `role: D` entry with a `scripts/` directory is rejected as
**mistier** — it should be filed as a Package Candidate or rebuilt as
a Package Wrapper Skill.

### Rule 2 — SKILL.md content scanner

Hard-fail patterns (deny by default; manual reviewer override required
to publish):

- `curl ... | (bash|sh|zsh|fish)`
- `wget ... | (bash|sh|zsh|fish)`
- `pip install` / `pipx install` / `uv pip install`
- `npm install -g` / `yarn global add` / `pnpm install -g`
- `chmod +x`
- `eval(` / `exec(` / `subprocess.`
- `docker run`
- `ssh ` / `scp `
- `rm -rf /`
- "paste your API key" / "enter your password"

Require-CLI-declaration: every backtick-wrapped shell-style invocation
(e.g. `` `gh auth login` ``, `` `git push` ``, `` `himalaya inbox` ``)
must have a matching entry in `runtime.requires_cli`. The validator
extracts referenced CLIs from the markdown body and diffs against the
manifest.

Soft-warn on the presence of any shell language at all — flagged for
reviewer attention, does not fail CI.

### Rule 3 — License whitelist

Allowed: `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`,
`CC-BY-4.0`.

Anything else fails CI unless the entry's
`review.license_exception_pr` URL is set (must point to a merged PR
that records the license review).

### Rule 4 — Frontmatter schema

Validated against `SCHEMA.md`. Required fields per role:

- `role: D` — `name`, `description`, `version`, `license`, `tags`,
  `category`, `policy`, `compatibility`, `source`, `review`.
- `role: W` — same as D plus `runtime.requires_packages`.

Hard-fail when:

- `role` ∉ {`D`, `W`}.
- `role: D` and `scripts/` exists.
- `name` mismatches the skill directory name.
- `category` does not exist as a known category.

### Rule 5 — Eval gate

`python scripts/run_eval.py skills/<name> --type trigger` must pass
for every skill changed in the PR.

Quality eval is a separate **nightly cron** over the corpus, not a
per-PR gate (too expensive to run on every PR).

## Profile lifecycle

A new profile version is cut when any rule changes. Old profile
versions remain valid for entries already approved under them.
Re-validating an old entry under a newer profile is a normal PR with
`review.policy_version` updated.

## Future profiles (not implemented in Phase 1)

- `markdown-with-ssh-allowed` — relaxes Rule 2's `ssh ` deny for
  ops-tooling skills, gated by additional reviewer sign-off.
- `markdown-strict-cli-allowlist` — narrows Rule 2's CLI declaration
  rule to a curated whitelist for security-sensitive deployments.

These extend the model without invalidating prior `markdown-only`
approvals.
