# Installation & Upgrade Guidance

This document is the single reference for installing, upgrading, and troubleshooting
kicad-happy across all supported AI platforms. It is written for AI agents but is
equally useful for humans.

**If you are an AI agent helping a user install or upgrade kicad-happy, read this
file in full before taking any action.** It covers platform-specific quirks,
known bugs, and workarounds that are not obvious from the plugin manifests alone.

Each platform section below is self-contained. Platform maintainers (Codex, Gemini,
Copilot, etc.) are encouraged to add platform-specific notes to their section as
the plugin ecosystem evolves.

---

## Requirements

| Requirement | Details |
|-------------|---------|
| Python | 3.10+ (3.8 EOL Oct 2024; CI tests 3.10 and 3.12) |
| Dependencies | None required. All analysis scripts use Python stdlib only. |
| Optional packages | `requests` (HTTP), `playwright` (JS-heavy PDF sites), `pdftotext` (PDF extraction) |
| Optional system tools | `ngspice` / `LTspice` / `Xyce` (SPICE simulation, auto-detected) |
| KiCad | Not required at runtime. Analyzes saved `.kicad_sch` / `.kicad_pcb` files directly. |
| KiCad versions | 5, 6, 7, 8, 9, 10 (all supported) |

### Python availability by OS

| OS | Default Python | Notes |
|----|---------------|-------|
| Ubuntu 22.04 LTS | 3.10 | Meets minimum |
| Ubuntu 24.04 LTS | 3.12 | Meets minimum |
| Debian 12 (bookworm) | 3.11 | Meets minimum |
| Debian 11 (bullseye) | 3.9 | Below minimum. EOL Aug 2026. Install 3.10+ from backports. |
| Fedora 39+ | 3.12+ | Meets minimum |
| macOS | 3.9.6 (Xcode CLT) | Below minimum. Install via Homebrew: `brew install python@3.12` |
| Windows | None bundled | Install from python.org or Microsoft Store |
| RHEL 9 | 3.9 / 3.11 module | Use `dnf module enable python3.11` |

### Skills included

All 12 skills: `kicad`, `spice`, `emc`, `datasheets`, `bom`, `digikey`, `mouser`,
`lcsc`, `element14`, `jlcpcb`, `pcbway`, `kidoc`.

When installing manually (symlinks or copies), include all 12. The `datasheets` skill
was promoted to top-level in v1.3 and is consumed by kicad, emc, spice, thermal,
and kidoc.

### Optional API credentials

These enable component sourcing and datasheet downloading. The skills work without
them but fall back to web search.

| Service | Environment variable(s) | Auth type |
|---------|------------------------|-----------|
| DigiKey | `DIGIKEY_CLIENT_ID`, `DIGIKEY_CLIENT_SECRET` | OAuth 2.0 |
| Mouser | `MOUSER_SEARCH_API_KEY` | API key |
| element14 | `ELEMENT14_API_KEY` | API key |
| LCSC | None required | Free community API |

---

## Claude Code

### Install (marketplace)

```
/plugin marketplace add aklofas/kicad-happy
/plugin install kicad-happy@kicad-happy
```

After installation, run `/reload-plugins` if skills don't appear immediately.

### Install (manual symlinks)

Use this if the marketplace install fails, or to pin to a specific version.

**macOS / Linux:**

```bash
git clone https://github.com/aklofas/kicad-happy.git
cd kicad-happy
mkdir -p ~/.claude/skills
for skill in kicad spice emc datasheets bom digikey mouser lcsc element14 jlcpcb pcbway kidoc; do
  ln -sf "$(pwd)/skills/$skill" ~/.claude/skills/$skill
done
```

**Windows (PowerShell 7+, Developer Mode enabled):**

```powershell
git clone https://github.com/aklofas/kicad-happy.git
cd kicad-happy
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
"kicad","spice","emc","datasheets","bom","digikey","mouser","lcsc","element14","jlcpcb","pcbway","kidoc" | ForEach-Object {
  New-Item -ItemType SymbolicLink -Path "$HOME\.claude\skills\$_" -Target "$(Get-Location)\skills\$_" -Force | Out-Null
}
```

See [Windows symlink issues](#windows-symlink-issues) if this fails.

### Upgrade

**Known bug:** `/plugin update` does not reliably detect new versions. The update
logic fetches the marketplace repo but does not merge, so it reads stale version
info. Tracked in multiple issues:
[anthropics/claude-code#36317](https://github.com/anthropics/claude-code/issues/36317),
[#29071](https://github.com/anthropics/claude-code/issues/29071),
[#31462](https://github.com/anthropics/claude-code/issues/31462),
[#38271](https://github.com/anthropics/claude-code/issues/38271).

**Workaround — clear cache and reinstall:**

```
rm -rf ~/.claude/plugins/cache/kicad-happy ~/.claude/plugins/marketplaces/kicad-happy
/plugin marketplace add aklofas/kicad-happy
/plugin install kicad-happy@kicad-happy
```

For manual (symlink) installs, just `git pull` in the cloned repo.

### Known issues

- **Duplicate skill loading:** Old plugin versions can remain in the cache directory
  (`~/.claude/plugins/cache/`). Claude Code may load skills from all cached versions,
  not just the active one. If you see duplicate skills, delete stale version
  directories from the cache. See
  [community report](https://www.reddit.com/r/ClaudeAI/comments/1rij9tr/).
- **Uninstall leaves cache on disk:**
  [anthropics/claude-code#35691](https://github.com/anthropics/claude-code/issues/35691).
  Orphaned directories are supposed to auto-clean after 7 days.

### Claude Code-specific notes

<!-- Claude Code maintainers: add platform-specific guidance below this line -->

---

## OpenAI Codex

### Install (recommended: built-in skill installer)

Within a Codex session, mention `$skill-installer` and install the skills from
this repo interactively. This is the most reliable path for Codex because it
installs into Codex's normal global skill location.

Example prompt:

```text
Use $skill-installer to install the kicad-happy skills from https://github.com/aklofas/kicad-happy
```

After installation, restart Codex if the new skills do not appear immediately.

### Install (manual global symlinks)

Codex looks for globally installed skills in `~/.codex/skills/`.

**macOS / Linux:**

```bash
git clone https://github.com/aklofas/kicad-happy.git
cd kicad-happy
mkdir -p ~/.codex/skills
for skill in kicad spice emc datasheets bom digikey mouser lcsc element14 jlcpcb pcbway kidoc; do
  ln -sf "$(pwd)/skills/$skill" ~/.codex/skills/$skill
done
```

**Windows (PowerShell 7+, Developer Mode enabled):**

```powershell
git clone https://github.com/aklofas/kicad-happy.git
cd kicad-happy
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
"kicad","spice","emc","datasheets","bom","digikey","mouser","lcsc","element14","jlcpcb","pcbway","kidoc" | ForEach-Object {
  New-Item -ItemType SymbolicLink -Path "$HOME\.codex\skills\$_" -Target "$(Get-Location)\skills\$_" -Force | Out-Null
}
```

See [Windows symlink issues](#windows-symlink-issues) if this fails.

### Install (repo-local metadata)

This repo also contains `.agents/plugins/marketplace.json` metadata for local
plugin experiments, but that is **not** the primary Codex skill installation
path and should not be described as automatic `.agents/skills/` discovery.
Prefer `$skill-installer` or `~/.codex/skills/`.

### Upgrade

For global symlink installs: `git pull` in the cloned repo (symlinks follow
the live checkout).

For skill-installer installs, use the installer again or reinstall if you need
to move to a newer repo version.

### Known issues

- **SKILL.md description length:** Codex enforces a 1024-character maximum on the
  `description` field in SKILL.md frontmatter. If you see "invalid description:
  exceeds maximum length of 1024 characters", the skill file needs trimming.
  This was fixed in kicad-happy v1.3.0+.
- **Skill not appearing after install:** Restart Codex. Skill discovery is most
  reliable at session startup.
- **`~/.agents/skills` guidance is stale for Codex:** if you see older setup
  docs telling you to install Codex skills into `~/.agents/skills`, treat that
  as outdated. Use `~/.codex/skills` instead.

### Codex-specific notes

<!-- Codex maintainers: add platform-specific guidance below this line -->

---

## GitHub Copilot CLI

### Install (gh skill)

Requires GitHub CLI v2.90.0+ (the `gh skill` command landed April 2026):

```bash
gh skill install aklofas/kicad-happy kicad
gh skill install aklofas/kicad-happy emc
# repeat for each skill, or install all:
for skill in kicad spice emc datasheets bom digikey mouser lcsc element14 jlcpcb pcbway kidoc; do
  gh skill install aklofas/kicad-happy $skill
done
```

Pin to a specific version:

```bash
gh skill install aklofas/kicad-happy kicad --pin v1.3.0
```

### Install (manual symlinks)

Copilot CLI discovers skills from `~/.copilot/skills/`, `~/.claude/skills/`, or
`~/.agents/skills/`:

```bash
git clone https://github.com/aklofas/kicad-happy.git
cd kicad-happy
mkdir -p ~/.agents/skills
for skill in kicad spice emc datasheets bom digikey mouser lcsc element14 jlcpcb pcbway kidoc; do
  ln -sf "$(pwd)/skills/$skill" ~/.agents/skills/$skill
done
```

### Upgrade

```bash
gh skill install aklofas/kicad-happy kicad  # reinstalls latest
```

Or `git pull` for symlink installs.

### Known issues

- **Directory name must match SKILL.md `name` field.** The directory `skills/kicad/`
  must have `name: kicad` in its SKILL.md frontmatter. All kicad-happy skills
  follow this convention.

### Copilot-specific notes

<!-- Copilot maintainers: add platform-specific guidance below this line -->

---

## Google Gemini CLI

kicad-happy is a monorepo with 12 skills under `skills/<name>/SKILL.md`. `gemini skills install <url>` does not recurse, so it fails at the repo root with "No valid skills found". Use one of the approaches below.

### Install (recommended: clone + `gemini skills link`)

`gemini skills link` discovers `SKILL.md` or `*/SKILL.md` one level deep, so point it at the cloned `skills/` directory (not the repo root) to pick up all 12 at once:

```bash
git clone https://github.com/aklofas/kicad-happy.git
gemini skills link ./kicad-happy/skills
```

Add `--scope workspace` to link into the repo-local `.gemini/skills` instead of the user-scope `~/.gemini/skills`.

### Install (per-skill, from git URL)

Use `--path` to install individual skills directly from the repo URL. Requires Gemini CLI from Jan 13 2026 or later (before that, `--path` was rejected with `Unknown arguments: path` — see [#16482](https://github.com/google-gemini/gemini-cli/issues/16482), fixed by [#16537](https://github.com/google-gemini/gemini-cli/pull/16537)).

```bash
# Install all 12 skills:
for skill in kicad spice emc datasheets bom digikey mouser lcsc element14 jlcpcb pcbway kidoc; do
  gemini skills install https://github.com/aklofas/kicad-happy.git --path skills/$skill
done
```

For repo-local (workspace scope):

```bash
gemini skills install https://github.com/aklofas/kicad-happy.git --path skills/kicad --scope workspace
```

### Install (manual symlinks)

If `gemini skills link` is unavailable, symlink directly:

```bash
git clone https://github.com/aklofas/kicad-happy.git
cd kicad-happy
mkdir -p ~/.gemini/skills
for skill in kicad spice emc datasheets bom digikey mouser lcsc element14 jlcpcb pcbway kidoc; do
  ln -sf "$(pwd)/skills/$skill" ~/.gemini/skills/$skill
done
```

### Management & Interactive Mode

You can manage skills from the terminal or interactively using slash commands:

*   **`gemini skills list`** / **`/skills list`**: List all discovered skills.
*   **`gemini skills enable/disable <name>`** / **`/skills enable/disable <name>`**: Toggle a skill.
*   **`/skills reload`**: Refresh the skill registry (use after editing `SKILL.md` or scripts).
*   **`/skills link <path>`**: Link local skills during an active session.

### Skill Tier Precedence

Gemini CLI discovers skills in three tiers with the following precedence:
1.  **Workspace Tier**: `.gemini/skills/` or `.agents/skills/` in the project root.
2.  **User Tier**: `~/.gemini/skills/` or `~/.agents/skills/`.
3.  **Extension Tier**: Bundled within installed extensions.

### Upgrade

For `gemini skills link` installs, `git pull` in the cloned repo and run `/skills reload` — symlinks follow the live checkout.

For `--path` installs, reinstall each skill:

```bash
for skill in kicad spice emc datasheets bom digikey mouser lcsc element14 jlcpcb pcbway kidoc; do
  gemini skills uninstall $skill
  gemini skills install https://github.com/aklofas/kicad-happy.git --path skills/$skill
done
```

### Known issues

- Skill discovery is most stable in v0.25.0+. Ensure your CLI is up to date by running:
  `npm install -g @google/gemini-cli@latest`
- The `--path` flag was broken before Jan 13 2026
  ([#16482](https://github.com/google-gemini/gemini-cli/issues/16482), fixed by
  [#16537](https://github.com/google-gemini/gemini-cli/pull/16537)). Older CLI
  versions reject it with `Unknown arguments: path` — upgrade, or fall back to
  `gemini skills link` / manual symlinks.
- Large skill directories may take a moment to index during initial startup.

### Gemini-specific notes

<!-- Gemini maintainers: add platform-specific guidance below this line -->

---

## Universal installer (npx skills)

[Vercel's `npx skills`](https://github.com/vercel-labs/skills) auto-detects which
AI agents are installed and routes skills to the correct directories:

```bash
npx skills add aklofas/kicad-happy
```

This works across Claude Code, Codex, Copilot, Gemini, Cursor, and others.

---

## Other / unsupported agents

If your agent platform is not listed above, kicad-happy can still work. The skills
are plain directories containing a `SKILL.md` (instructions) and `scripts/`
(Python analysis tools).

### What an agent needs

1. **Read SKILL.md files** — each skill has a `SKILL.md` with YAML frontmatter
   (`name`, `description`, trigger conditions) and detailed usage instructions.
2. **Run Python scripts** — the analysis scripts are standalone CLI tools:
   ```bash
   python3 skills/kicad/scripts/analyze_schematic.py <file>.kicad_sch
   python3 skills/kicad/scripts/analyze_pcb.py <file>.kicad_pcb --full
   python3 skills/emc/scripts/analyze_emc.py -s schematic.json -p pcb.json
   ```
3. **Read JSON output** — all scripts output structured JSON to stdout or a file.
4. **Read reference docs** — `skills/*/references/*.md` contain deep methodology
   guides for interpreting results.

### Minimal integration

Clone the repo and point your agent at the skills directory. Most agents that
support a skills/tools directory can discover them:

```bash
git clone https://github.com/aklofas/kicad-happy.git
```

If your agent uses a custom skill directory, symlink the individual skills there.
The key directories are `skills/<name>/SKILL.md` (instructions) and
`skills/<name>/scripts/` (Python tools).

### Standalone (no agent)

The scripts work without any AI agent:

```bash
python3 skills/kicad/scripts/analyze_schematic.py board.kicad_sch --output sch.json
python3 skills/kicad/scripts/analyze_pcb.py board.kicad_pcb --full --output pcb.json
python3 skills/emc/scripts/analyze_emc.py -s sch.json -p pcb.json --output emc.json
```

### Notes for unsupported agents

<!-- If your agent platform is not listed above, add notes here -->

---

## GitHub Action

Available as a GitHub Action for automated PR reviews. Every push or PR that
touches KiCad files gets a commit status check and a structured review comment.
See [github-action.md](github-action.md) for the full guide.

### Basic workflow

Create `.github/workflows/kicad-review.yml`:

```yaml
name: KiCad Design Review
on:
  push:
    paths: ['**/*.kicad_sch', '**/*.kicad_pcb']
  pull_request:
    paths: ['**/*.kicad_sch', '**/*.kicad_pcb']

permissions:
  contents: read
  pull-requests: write
  statuses: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: sudo apt-get install -y ngspice poppler-utils
      - uses: aklofas/kicad-happy@v1
        id: analysis
      - uses: thollander/actions-comment-pull-request@v3
        if: github.event_name == 'pull_request'
        with:
          file-path: ${{ steps.analysis.outputs.report-path }}
          comment-tag: kicad-happy-review
          mode: upsert
```

What this does:
- Triggers on any push or PR that modifies `.kicad_sch` or `.kicad_pcb` files
- Installs `ngspice` (SPICE simulation) and `poppler-utils` (PDF datasheet extraction)
- Runs the full kicad-happy analysis pipeline (schematic, PCB, EMC, thermal, SPICE)
- Posts a structured review comment on PRs (updates on re-push via `upsert`)
- Sets a commit status check (green/red with findings summary)

### Diff-based PR reviews

Enable `diff-base: true` to show only what changed between the PR and the base
branch — component additions/removals, signal parameter shifts, new/resolved
findings:

```yaml
      - uses: aklofas/kicad-happy@v1
        id: analysis
        with:
          diff-base: true
```

### AI-powered review chains

Chain the deterministic analysis with an AI agent for natural-language review.
The deterministic analysis (schematic, PCB, EMC, thermal) is always free. AI
review costs come from the provider's API.

**Claude (quick review, ~$1-3 per PR):**

```yaml
      - uses: anthropics/claude-code-action@v1
        if: github.event_name == 'pull_request' && env.ANTHROPIC_API_KEY != ''
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          prompt: |
            The kicad-happy deterministic analysis has already been run.
            Read the markdown report at ${{ steps.analysis.outputs.report-path }}.

            Do NOT re-run analysis scripts. Review the findings and:
            1. Verify the top 3-5 IC pinouts against datasheets
            2. Check WARNING findings for accuracy
            3. Note anything the analysis may have missed

            Post a concise summary (under 2000 chars) as a PR comment.
            Focus on actionable findings only.
          claude_args: '--model claude-sonnet-4-6 --max-turns 25'
```

**Codex (alternative):**

```yaml
      - uses: openai/codex-action@v1
        if: github.event_name == 'pull_request' && env.OPENAI_API_KEY != ''
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        with:
          prompt: |
            The kicad-happy deterministic analysis has already been run.
            Read the markdown report at ${{ steps.analysis.outputs.report-path }}.

            Do NOT re-run analysis scripts. Review the findings and:
            1. Verify the top 3-5 IC pinouts against datasheets
            2. Check WARNING findings for accuracy
            3. Note anything the analysis may have missed

            Post a concise summary (under 2000 chars) as a PR comment.
            Focus on actionable findings only.
```

### Secrets setup

| Secret | Where to get it | Required for |
|--------|----------------|-------------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) | Claude AI review |
| `OPENAI_API_KEY` | OpenAI platform dashboard | Codex AI review |
| `DIGIKEY_CLIENT_ID` / `DIGIKEY_CLIENT_SECRET` | [developer.digikey.com](https://developer.digikey.com/) | Datasheet download in CI |
| `MOUSER_SEARCH_API_KEY` | My Mouser → APIs | Datasheet download in CI |

Add secrets in your repo: Settings → Secrets and variables → Actions → New repository secret.

### Action outputs

The `aklofas/kicad-happy@v1` step exposes these outputs for downstream steps:

| Output | Description |
|--------|-------------|
| `report-path` | Path to the markdown report file |
| `schematic-json` | Path to schematic analysis JSON |
| `pcb-json` | Path to PCB analysis JSON (if PCB exists) |
| `emc-json` | Path to EMC analysis JSON (if both schematic and PCB exist) |
| `status` | `pass`, `warn`, or `fail` |
| `findings-count` | Total number of findings |
| `critical-count` | Number of critical/error findings |

---

## Windows symlink issues

Windows symlinks have platform-specific friction:

| Scenario | Works? | Notes |
|----------|--------|-------|
| PowerShell 7+ with Developer Mode | Yes | Recommended approach |
| PowerShell 5.1 (ships with Windows) | No | Does not pass `SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE` even with Developer Mode |
| cmd.exe `mklink /D` with Developer Mode | Yes | Alternative to PowerShell 7 |
| Any shell, elevated (Run as Administrator) | Yes | Works but not ideal for daily use |

**Fallback: use junctions instead of symlinks.** Junctions work for directories
without requiring Developer Mode or elevation:

```powershell
"kicad","spice","emc","datasheets","bom","digikey","mouser","lcsc","element14","jlcpcb","pcbway","kidoc" | ForEach-Object {
  New-Item -ItemType Junction -Path "$HOME\.agents\skills\$_" -Target "$(Get-Location)\skills\$_" -Force | Out-Null
}
```

**Fallback: copy instead of linking.** If symlinks and junctions both fail, copy
the skill directories. Upgrades then require re-copying after `git pull`.

---

## Troubleshooting

### Skills not appearing after install

1. Restart your agent / reload plugins (`/reload-plugins` in Claude Code)
2. Verify the skill directories exist in the expected location for your platform
3. Check that each skill directory contains a `SKILL.md` file with valid YAML frontmatter
4. On Claude Code: check for stale cache in `~/.claude/plugins/cache/`

### Python version errors

If you see `SyntaxError` on `str | None` or `dict[str, int]`:

- Your Python is below 3.10. Check with `python3 --version`.
- Install Python 3.10+ for your OS (see table above).

### Script import errors

All scripts add their own directory to `sys.path`. If you see import errors when
running from a non-standard working directory, use absolute paths:

```bash
python3 /path/to/kicad-happy/skills/kicad/scripts/analyze_schematic.py board.kicad_sch
```

### API credential issues

- DigiKey OAuth requires a registered app at [developer.digikey.com](https://developer.digikey.com/).
  The first auth flow opens a browser for consent. Subsequent calls use a refresh token.
- Mouser and element14 keys are simple API keys — set the env var and go.
- LCSC needs no credentials (uses the jlcsearch community API).
- If no API keys are set, distributor skills fall back to web search guidance.

### KiDoc venv issues

The kidoc skill creates a project-local Python venv on first run for PDF/DOCX/ODT
output (requires `reportlab`, `python-docx`, `odfpy`, `Pillow`, `svglib`,
`matplotlib`). If venv creation fails:

1. Ensure `python3 -m venv` works on your system
2. On Debian/Ubuntu: `sudo apt install python3-venv`
3. HTML output works without the venv (zero dependencies)
