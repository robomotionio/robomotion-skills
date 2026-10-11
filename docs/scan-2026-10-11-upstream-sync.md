# Upstream sync and review: every vendored group (2026-10-11)

Every group in `upstreams.yaml` was run through `sync-upstream.py sync <group>`
with the default age rule (the newest upstream commit at least 7 days old),
then read and scanned. Of 38 groups:

- **22 moved** and ship in this PR.
- **7 were synced, read, and reverted** to their old pin for security reasons.
- **2 were synced and reverted** because they need an install-hook bump first.
- **3 did not move** because one of our patches no longer applies.
- **4 were already current.**

Every group also gets its version from upstream now (see [Versions](#versions)).

How the review was done:

- **Reading.** Every changed or new SKILL.md, reference file and script in
  every synced group was read in full, in the diff against origin/main. For
  JSON and CSV data files, the data was checked for URLs, encoded blobs,
  script tags and text aimed at the agent rather than read row by row. A
  clean scan is not an approval.
- **`scan-skills.py`** ran over each whole group, then `--changed origin/main`
  over the PR.
- **Cisco `cisco-ai-skill-scanner`** 2.2.2, as in the 2026-10-10 pass: a
  throwaway `python:3.12-slim` podman container, `--network=none`, the group
  mounted read-only, static plus behavioral analyzers, no LLM, no
  credentials. It scanned each group twice, at its old pin and at the
  proposed commit, so the tables below give what the sync added, not every
  finding the group already had.

## Groups

`old -> new` is the upstream commit and its commit date. The version column
is ours before and upstream's after; "+ N commits" means the pinned commit is
N commits past that release tag.

| Group | Upstream | Old pin | New pin | Version | From | Result |
|---|---|---|---|---|---|---|
| `agent-browser` | vercel-labs/agent-browser | `8c15ff9f71ae` 2026-09-10 | `526157cfd4ec` 2026-10-03 | 1.0.0 -> 0.38.2 | tag v0.38.2 + 1 commits | synced |
| `anthropic-skills` | anthropics/skills | `34040c9c5685` 2026-09-10 | `8a1541c4a3ff` 2026-09-28 | 1.0.0 -> 1.0.0 | .claude-plugin/marketplace.json | synced |
| `awesome-copilot` | github/awesome-copilot | `1899b18da3fa` 2026-09-14 | `143a3d976b3c` 2026-10-02 | 1.0.0 -> 1.0.0 | package.json | synced |
| `aws-skills` | aws/agent-toolkit-for-aws | `7fcb1da17abb` 2026-09-15 | same (`d00d03ae6e48` reverted) | 1.0.0 -> 1.0.0 | .claude-plugin/marketplace.json | **reverted** |
| `azure-skills` | microsoft/azure-skills | `9d46511c1828` 2026-09-11 | same (`74f27068b21b` reverted) | 1.0.0 -> 1.2.46 | tag v1.2.46 | **reverted** |
| `caveman-skills` | JuliusBrussee/caveman | `8bc01d675314` 2026-09-14 | `17b5bff98e86` 2026-10-03 | 1.0.0 -> 3.1.0 | tag v3.1.0 + 20 commits | synced, licence accepted |
| `claude-seo` | AgriciDaniel/claude-seo | `92795530b4cc` 2026-09-11 | same | 2.0.0 -> 2.3.1 | tag v2.3.1 + 2 commits | not moved: patch |
| `cloudflare-skills` | cloudflare/skills | `b052c32bab7d` 2026-09-07 | `41e0d1985894` 2026-10-01 | 1.0.0 -> 1.0.1 | .claude-plugin/plugin.json | synced |
| `elevenlabs-skills` | elevenlabs/skills | `9edcbd4b80ed` 2026-09-09 | `81f1eafc65c9` 2026-10-01 | 1.0.0 -> 81f1eafc65c9 | no version upstream: the commit | synced |
| `emilkowalski-skills` | emilkowalski/skills | `d23d7f88a2e2` 2026-08-21 | `e8a175de22ae` 2026-10-02 | 1.0.0 -> e8a175de22ae | no version upstream: the commit | synced |
| `engineering-skills` | addyosmani/agent-skills | `a1a80d56d1f8` 2026-09-14 | `c45732d20939` 2026-10-03 | 1.0.0 -> 0.6.12 | tag 0.6.12 + 6 commits | synced |
| `financial-services` | anthropics/financial-services | `90912d92c73e` 2026-09-14 | `574ed3624aeb` 2026-09-21 | 1.0.0 -> 0.2.1 | highest of the plugin manifests (4 versions across 6) | synced (no content change) |
| `firecrawl-skills` | firecrawl/skills | `bab52f95ea1c` 2026-09-02 | same (`28c134e85862` reverted) | 1.0.0 -> 0.1.0 | .claude-plugin/plugin.json | **reverted** |
| `gemini-skills` | google-gemini/gemini-skills | `80dd31dda25b` 2026-09-11 | `6fee1bec62d6` 2026-09-23 | 1.0.0 -> 2.1.0 | .claude-plugin/plugin.json | synced |
| `google-agents-cli` | google/agents-cli | `5597738f14b5` 2026-09-01 | `2c3945901e8e` 2026-09-30 | 1.0.0 -> 1.8.0 | tag v1.8.0 | synced |
| `google-skills` | google/skills | `5d9d07bb1ce6` 2026-09-14 | same (`1d77046ad367` reverted) | 1.0.0 -> 0.0.1 | .claude-plugin/marketplace.json | **reverted** |
| `gws-cli` | googleworkspace/cli | `a3768d0e82ad` 2026-03-31 | same | 1.0.0 -> 0.22.5 | tag v0.22.5 + 1 commits | already current |
| `higgsfield-skills` | higgsfield-ai/skills | `d071406147a3` 2026-09-11 | `f83af0bc1d93` 2026-09-26 | 1.0.0 -> 0.13.0 | .claude-plugin/plugin.json | synced |
| `hyperframes` | heygen-com/hyperframes | `d13a89b67072` 2026-09-14 | same | 1.0.0 -> 0.8.39 | tag v0.8.39 | not moved: patch |
| `impeccable` | pbakaus/impeccable | `cb56ed6c19a0` 2026-09-10 | same (`3d0d4df30d27` reverted) | 1.0.0 -> 4.3.1 | tag skill-v4.3.1 + 6 commits | **reverted**: hook |
| `knowledge-work-plugins` | anthropics/knowledge-work-plugins | `e92b5a023648` 2026-09-15 | `8444efcd48f7` 2026-10-01 | 1.0.0 -> 2.0.1 | highest of the plugin manifests (5 versions across 13) | synced |
| `lark-skills` | larksuite/cli | `1bd78144e890` 2026-09-14 | `7beffb086d7f` 2026-09-30 | 1.0.0 -> 1.0.97 | tag v1.0.97 + 2 commits | synced |
| `last30days-skill` | mvanhorn/last30days-skill | `4909c2efb2d9` 2026-09-15 | `5103ba478b38` 2026-09-30 | 1.0.0 -> 3.26.0 | tag v3.26.0 | synced, patches rebased, patch 002 added |
| `marketing-skills` | coreyhaines31/marketingskills | `5b2c0007766c` 2026-09-04 | same | 2.1.0 -> 2.11.1 | tag v2.11.1 | not moved: patch |
| `mattpocock-skills` | mattpocock/skills | `3cca18b368ae` 2026-09-04 | `984a2c023c9f` 2026-09-29 | 1.0.0 -> 1.3.0 | tag v1.3.0 | synced |
| `neon-skills` | neondatabase/agent-skills | `2e0da3a1653b` 2026-09-04 | `9e4a5705922f` 2026-10-03 | 1.0.0 -> 2.1.1 | plugin.json | synced |
| `netlify-skills` | netlify/context-and-tools | `5851a0e75f20` 2026-09-14 | same (`6b2562db404a` reverted) | 1.0.0 -> 1.3.2 | tag v1.3.2 + 1 commits | **reverted** |
| `officecli` | iOfficeAI/OfficeCLI | `5a938d2d111b` 2026-09-15 | same (`b590a433a6a6` reverted) | 1.0.0 -> 1.0.150 | tag v1.0.150 + 4 commits | **reverted**: hook |
| `openai-skills` | openai/skills | `49f948faa925` 2026-06-23 | same | 1.0.0 -> 49f948faa925 | no version upstream: the commit | already current (upstream deprecated) |
| `prisma-skills` | prisma/skills | `1123817e60d1` 2026-09-08 | same (`be16a8740d01` reverted) | 1.0.0 -> 7.9.1 | highest of the SKILL.md versions (5 across 9) | **reverted** |
| `replicate-skills` | replicate/skills | `2f36e415965a` 2026-06-04 | same | 1.0.0 -> 2.0.0 | .claude-plugin/plugin.json | already current |
| `shadcn-skills` | shadcn-ui/ui | `2b3e6d4f8d91` 2026-09-12 | `295a1f114a13` 2026-10-02 | 1.0.0 -> 4.21.1 | tag shadcn@4.21.1 + 3 commits | synced (no content change) |
| `small-business-skills` | anthropics/knowledge-work-plugins | `e92b5a023648` 2026-09-15 | `8444efcd48f7` 2026-10-01 | 1.0.0 -> 1.35.1 | small-business/.claude-plugin/plugin.json | synced (no content change) |
| `supabase-skills` | supabase/agent-skills | `8331f9108451` 2026-08-12 | `c9be0e931b79` 2026-10-02 | 1.0.0 -> 0.1.9 | tag v0.1.9 + 1 commits | synced |
| `superpowers` | obra/superpowers | `b36e0829c6d0` 2026-08-12 | `8ca22dba9a94` 2026-09-25 | 1.0.0 -> 6.4.2 | tag v6.4.2 | synced |
| `taste-skill` | Leonxlnx/taste-skill | `ccbc15639c97` 2026-08-24 | `ce26fc25c0e5` 2026-09-26 | 1.0.0 -> 1.0.0 | .claude-plugin/plugin.json | synced (no content change) |
| `tavily-skills` | tavily-ai/skills | `778122e5f9c6` 2026-09-04 | same | 1.0.0 -> 1.0.0 | .claude-plugin/plugin.json | already current |
| `ui-ux-pro-max-skill` | nextlevelbuilder/ui-ux-pro-max-skill | `d457006301be` 2026-06-23 | same (`477bcb28c981` reverted) | 2.5.0 -> 2.6.2 | tag v2.6.2 | **reverted** |

The two first-party groups, `designer-skills` and `video-skills`, are their
own upstream and keep their versions.

## Reverted: unsafe or suspicious changes

Each group was synced, read, and put back on its old pin with
`sync <group> --to <old pin>`. That rebuilds origin/main's content and only
sets the upstream version. Line numbers are at the proposed commit.

### aws-skills (`d00d03ae6e48`): the agent pipes an unpinned installer into `sh` with the customer's AWS credentials

This is the problem that got `aws-transform` and `rds-db2` excluded. The
file is new, and no piped-to-shell line existed in this group before:
`skills/specialized-skills/operations-skills/setting-up-cloudwatch-observability/references/cloudwatch-omni/azure-ingestion/custom-telemetry.md`.

- **:44-47** say the agent owns the AWS-side setup: "you have the customer's
  **AWS** credentials, so you own the AWS-side IAM setup ... you may run those
  AWS-side steps directly".
- **:124-130** (VM) and **:157-162** (AKS) give the command:
  `curl -fsSL https://raw.githubusercontent.com/aws/amazon-cloudwatch-agent/main/scripts/aws/setup.sh | \ ... sh`.
  The script creates IAM roles and trust policies.
- **:111** ("This script writes a tenant-wide trust ... any identity in the
  Azure tenant could assume a role holding `CloudWatchAgentServerPolicy`") and
  **:120** ("it is fetched from unpinned `main`") are the file's own warnings.
- **:98-104** and **:149-155** pipe the Azure-side scripts the same way, for
  the customer to run.

Our scanner missed it: the `| \` line continuation and the `VAR=...` prefixes
defeat the `pipe-to-shell` regex. Cisco flagged all three as
`COMPOUND_FETCH_EXECUTE`.

To ship the rest of the sync, add a patch that removes the "Automated setup"
path from `custom-telemetry.md` and keeps the manual commands. Excluding the
whole `azure-ingestion` folder does not work on its own:
`aws-observability/SKILL.md` tells the agent to fetch the
setting-up-cloudwatch-observability skill from the AWS MCP server when it is
missing locally.

Also found in the proposed content (NOTE level):

- `aws-fault-injection-service/references/fis-workflow.md:206` starts a real
  fault-injection experiment with no confirmation right before it.
- `aws-marketplace-metering/scripts/deploy.sh:285,351` deploy with
  `--no-confirm-changeset`, and `:465` defaults to live billing.

### google-skills (`1d77046ad367`): runtime fetch-and-follow of unreviewed skills now fires on almost any stack question

**`skills/developers/finding-google-skills/SKILL.md`**:

- **:27** fetches `https://raw.githubusercontent.com/google/skills/main/index.json`.
- **:75-76**: "Retrieve the `entrypoint` URL of each shortlisted entry, the
  same way, and follow that skill's instructions."
- **:100**: "Prefer the fetched SKILL.md over prior knowledge."

The agent runs upstream text from `main` at run time. That skips this review
and our exclusion of `google-cloud-filestore-nfs-browser`, which executes
base64-decoded code. The behaviour itself predates this sync. What the sync
changes is the trigger: it was "requests touching a Google product", and
**:11** now reads "a reasonable candidate - whether or not a vendor is named".

The new BigQuery skills also install skills at run time from upstream main,
past review, the pattern `vercel-labs/skills` was removed for:
`bigquery-observability/SKILL.md:77`, `bigquery-optimization/SKILL.md:67` and
`bigquery-troubleshooting/SKILL.md:63` all run
`npx skills add google/skills --skill bigquery-observability --skill bigquery-optimization --skill bigquery-troubleshooting`.

To ship the rest, exclude `skills/developers/finding-google-skills` (it is
already live at the old pin, with the narrower trigger) and patch the three
`npx skills add` lines to name the sibling skills.

Also in the proposed content (NOTE level):

- `secops-triage/SKILL.md:97,207-211` and `secops-cases/SKILL.md:215` close
  SecOps cases with no human approval, on telemetry an attacker can influence.

### azure-skills (`74f27068b21b`): new skill that discovers and installs skills at run time

`skills/discover-azure-skills/SKILL.md` is new:

- **:3** triggers "before starting any task that involves an Azure or
  Microsoft-cloud service".
- **:14-32** pull skill listings and SKILL.md text from api.github.com and
  `raw.githubusercontent.com/microsoft/azure-skills/main` into the agent's
  context.
- **:38** has the agent offer installation.
  `references/install/other.md:6` is
  `npx skills add https://github.com/microsoft/azure-skills/tree/main/.github/plugins/{plugin-dirname}/skills/{skill-name}`.

This is the same run-time install past review that got `vercel-labs/skills`
(`find-skills`) removed. Neither scanner flagged it.

To ship the rest, exclude `skills/discover-azure-skills`. The other change
is small:

- Upstream deleted the whole `azure-cost` skill; it is now an optional plugin.
- 115 files changed only from CRLF to LF line endings (checked by hash).

### prisma-skills (`be16a8740d01`): skills tell the agent to fetch unpinned skills from GitHub main

- `skills/prisma-database-setup/SKILL.md:12` and `skills/prisma-postgres/SKILL.md:12`
  say "If unavailable, install it from [prisma/skills](https://github.com/prisma/skills/tree/main/...)
  before continuing."
- `skills/prisma-postgres-setup/SKILL.md:40`: "read
  [prisma-orm-setup/SKILL.md](https://github.com/prisma/skills/blob/main/prisma-orm-setup/SKILL.md)
  directly". That points at GitHub main instead of the reviewed copy beside it.

To ship, add a patch in `.robomotion/patches/` that points both at the
vendored sibling skills.

### ui-ux-pro-max-skill (`477bcb28c981`): a new `stack/` folder ships an auto-enabling Claude Code setup into the sandbox

The group vendors the whole upstream repo, so upstream's new `stack/` would
land in every sandbox as group files:

- `stack/.claude/settings.json:3` sets `"enableAllProjectMcpServers": true`,
  and `:9` sets `"Read(//home/**)"`.
- `stack/.mcp.json:5-14` starts three MCP servers with `npx -y` at `@latest`:
  `@playwright/mcp@latest`, `chrome-devtools-mcp@latest`, and `shadcn@latest mcp`.
- `stack/scripts/setup.sh:11,18` runs `npm install` and
  `npx --yes ui-ux-pro-max-cli init --ai claude`.

It is dormant today: no runtime of ours reads a skill folder's `.mcp.json`
or `.claude/settings.json`, and no SKILL.md points at `stack/`. But it is a
standing grant of every MCP server plus all of /home for any tool that does
read it. `scan-skills.py` missed it because the `npx` arguments are a JSON
array. Cisco does not scan the folder, because it is not a skill.

The sync would also break the group:

- `.claude/skills/ui-ux-pro-max/SKILL.md:42` and the other examples call
  `python "${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/scripts/search.py"`.
  That variable is unset in our sandbox.
- Six skill ids lose their `ckm:` prefix (`ckm:banner-design` becomes
  `banner-design`).

To ship:

- Exclude `stack`, plus optionally `gallery`, `projects` and `.github`.
- Patch the `${CLAUDE_PLUGIN_ROOT}` paths.
- Check saved skill bindings for the old ids.

The stored-XSS fixes (#274, #283) and our patch are still in place at the
new commit.

### firecrawl-skills (`28c134e85862`): a silent background report of the user's goal to the vendor

This group's install hook turns telemetry off
(`.robomotion/post-install.sh:26`, `FIRECRAWL_NO_UPDATE_CHECK=1 FIRECRAWL_NO_TELEMETRY=1`).
The new skill `skills/core/firecrawl-alexandria/SKILL.md` adds a separate
feedback channel that the hook does not switch off:

- **:17** "send at most one `firecrawl alexandria feedback` per website".
- **:30** `--objective` is "what you or your user were ultimately trying to
  accomplish".
- **:35, :48, :53** run it with `--silent &` in the background.
- **:25** the opt-out is `FIRECRAWL_NO_ENDPOINT_FEEDBACK=1`, which we do not set.

Separately, `skills/core/firecrawl-search/SKILL.md:48` says "Displayed
pricing is informational, not an extra confirmation gate", so paid provider
tools run without asking.

The skills also use CLI commands newer than the pinned `firecrawl-cli`
1.23.3 (`.robomotion/post-install.sh:13`).

To ship:

- Set `FIRECRAWL_NO_ENDPOINT_FEEDBACK=1` in the hook's wrapper.
- Bump the CLI pin.
- Patch the pricing line.
- Give `firecrawl-alexandria` an `env.optional` with `FIRECRAWL_API_KEY`.

### netlify-skills (`6b2562db404a`): a remote skill installer arrives and moves all 15 skills to container mode

Upstream added its publishing tooling at the repo root:

- `bin/netlify-skills.mjs`, whose `:41` reads
  `const DEFAULT_HOST = 'https://netlify-agent-skills.netlify.app';`.
- `scripts/fetch-skill.mjs`, which fetches skills from that host and writes
  them into `.claude/skills`, `.agents/skills` and `.grok/skills` (`:169-197`,
  `:280-305`). It can mark files executable (`:298`) and delete skill folders
  (`:469-484`).

No skill invokes these, but they are a run-time skill installer that would
sit in the sandbox. Because the group now ships `bin/`, `build-index.py`
(like the launcher) moves all 15 netlify skills from host to container mode.
That changes how every agent using them runs.

To ship, exclude `bin`, `scripts`, `netlify.toml` and `skill-registry.json`.
The skill text itself is a clean docs refresh.

## Reverted: needs an install-hook change first

This PR only moves vendored copies, so these wait for a hook bump.

- **impeccable (`3d0d4df30d27`).** `skills/impeccable/scripts/VERSION` goes
  from 0.1.5 to 0.1.9.
  - `.robomotion/post-install.sh:17` still installs `ENGINE_VERSION=0.1.5`,
    and `:27-29` stop the image build when the two differ, so the image
    would not build.
  - The new references also use engine commands 0.1.5 may lack.
  - Fix: bump `ENGINE_VERSION` and both hashes from a verified engine-v0.1.9
    release, then sync. Keep the check: without it the agent is told to
    `npx impeccable update` at run time.
- **officecli (`b590a433a6a6`).** The hook pins "the release current at the
  upstream commit the skills are synced from" (`.robomotion/post-install.sh:11-15`):
  1.0.150. The new skill text describes 1.0.153 behaviour (for example
  `add --from` row cloning, and exit 2 semantics).
  - Fix: bump `OFFICECLI_VERSION` to 1.0.153 and both hashes from that
    release's SHA256SUMS, then sync.
  - The skill change itself is wording only, and our patch 001 still applies.

Hook pins that are behind but do not block shipping (NOTE):

- `higgsfield-skills` pins `@higgsfield/cli@1.1.26`; upstream's commit "sync
  model ids and params with the CLI" suggests a newer CLI. Model ids are
  resolved on the server.

## Not moved: our patch no longer applies

`sync` stops when a recorded patch does not apply at the newer commit, so
these three stay at their pins. Each was rebuilt at its own pin only to set
its version. To see what conflicts, our patches were rebased onto the new
upstream in a scratch repo with git's three-way merge.

| Group | Would move to | The conflict | What would fix it |
|---|---|---|---|
| `claude-seo` | `c13d8d1170c9` (2026-10-03, v2.4.1 + 13, 67 commits) | `001-prepared-by-robomotion.patch`, one hunk in `scripts/google_report.py`. Upstream changed the report footer to "Report generated by Claude SEO (Google SEO Intelligence Skill)", the line our patch rewrites to say Robomotion. | Refresh that hunk; the rest of the patch merges cleanly. Then `sync claude-seo` and review its 67 commits. |
| `hyperframes` | `2cfbe3d2570c` (2026-10-03, v0.8.116 + 5, 838 commits) | `0001-embedded-captions-image-root.patch`. Upstream moved the CLI lookup our patch edits (in `matte.cjs`, `transcribe.cjs` and `render-and-composite.sh`) into a new shared `skills/embedded-captions/scripts/hf-cli.cjs`. The other six files merge cleanly. | Rewrite the patch against `hf-cli.cjs` so it still finds `/opt/hyperframes/root` (the folder our `post-install.sh` builds), or drop it if the new lookup finds the installed CLI by itself. Then rebuild the image and run an embedded-captions render. This is a rewrite, not a rebase. |
| `marketing-skills` | `42f9fa24eaf6` (2026-10-03, v2.11.17 + 1, 209 commits) | `0001-local-edits.patch`, one hunk in `skills/revops/SKILL.md`. Upstream made the tools table's links absolute GitHub URLs; our patch renames its Zapier row to Robomotion. | Refresh the hunk on the new table, keeping upstream's links and our row. Then `sync marketing-skills` and review its 209 commits. |

## Patch refreshed: last30days-skill

`001-robomotion-sandbox-scrapedo.patch` no longer applied at `5103ba478b38`:
upstream changed lines next to our edits in `SKILL.md` and
`scripts/lib/http.py`.

`002-scrapedo-datacenter-first.patch` is new on this branch. It was taken
from `saas-agents-261010` (commit `be5cc319`) and makes Scrape.do try its
datacenter pool first. A Reddit or YouTube request that comes back blocked is
retried once through the residential pool (`super=true`). `SCRAPEDO_SUPER`
takes auto, 1 or 0.

Both patches were rebased onto the new upstream with git's three-way merge,
with no conflict. Their added and removed lines are byte-identical to
before; only line numbers and context moved, so the behaviour is the same.

The review confirmed the patched behaviour holds at the new commit:

- Every Reddit and YouTube fetch still goes through the patched
  `http.request`, including upstream's new keyless `reddit_search.py` lane,
  which replaces the retired RSS feed.
- `SCRAPEDO_TOKEN` is read only in `scrapedo.py` and sent only to
  `api.scrape.do`.

Two NOTEs:

- The residential retry fires only on an HTTP error status. Reddit can also
  block with a 200 challenge page, which the search lane rejects without
  retrying, so it fails closed. Watch for thin Reddit results in a sandbox
  run.
- One blocked URL can cost up to 4 Scrape.do requests.

## Licence change accepted: caveman-skills

Upstream relicensed the whole repository in Caveman 3.0.0 (commit `921eab8`,
"relicense the whole repo to Apache-2.0"). It was MIT before, with a BSL-1.1
carve-out for the engine directories; now it is Apache-2.0.

Apache-2.0 is permissive, so the sync ran with `--accept-license`. To meet
the licence terms:

- The group now also takes upstream's `NOTICE` and `LICENSE-MIT`. Upstream's
  `LICENSING.md` says the pre-3.0 MIT text must travel with code that was
  contributed under MIT.
- Our `.robomotion/LICENSE`, the `license` field in `skill.yaml` and the
  manifest all say Apache-2.0.

Content changes: the six intensity levels became three skills. `ultracave`
and `megacave` are new; both are pure instructions with
`disable-model-invocation: true`. None of the excluded skills came in, and no
skill we take depends on Caveman Cloud, the CLI, hooks or telemetry.

## Shipped, with what the review recorded

All BLOCKER-level findings are in the reverted groups above. In the 22
groups that ship, these are the NOTEs worth knowing:

- **anthropic-skills**: `claude-api` gains eval-building and preserved-thinking migration guides, plus four scripts under `shared/`.
  - `build-report-lite.mjs` and `runner-scaffold.mjs` are local only and refuse links and hard links. Both BLOCK findings on them were comments explaining that defence, and are accepted.
  - `drop_block_probe.py` reads `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` and sends captured requests to `ANTHROPIC_BASE_URL` (default api.anthropic.com), only with `--yes`.
  - `prefix_diff.py` makes no network calls (it imports argparse, difflib, glob, json, os, re and sys).
  - The scripts sit under `shared/`, not `scripts/`, so the skill stays in host mode while the guides have the agent run them. This is a classification gap worth closing in the launcher and `build-index.py`.
  - None of these environment variables are declared in `env.optional`.
- **cloudflare-skills**: new `basin` (mostly a move of pipelines, R2 Data Catalog and R2 SQL references) and `k2`. 229 of 301 hunks only append `/index.md` to docs links.
  - `skills/cloudflare/SKILL.md:16` installs `cf@latest` globally. The `cf` npm package is Cloudflare's: its maintainers include `wrangler-publisher@cloudflare.com` and its repo is `cloudflare/cf`.
  - `skills/basin/SKILL.md:8` and `skills/k2/SKILL.md:8` point the agent at unmerged cloudflare-docs pull requests (#33850, #33858) for current pages.
- **lark-skills**: 86 files only change a shared link. `lark-slides/references/cli/lark-slides-media-upload.md:90` shows `drive +member-add --perm full_access --yes`, which grants the app's own bot access to one presentation, with the confirmation flag already set.
- **google-agents-cli**: ADK Go and Live (voice) references.
  - The BLOCK at `google-agents-cli-adk-code/SKILL.md:65` was a markdown table row naming the adk.dev docs index, not a pipe to a shell; accepted.
  - `deploy/SKILL.md:88` now allows `agents-cli infra single-project --apply` for observability setup. `agents-cli deploy` still needs human approval (`:86`).
- **neon-skills**: new `neon-auth`, and Getting Started moves to the installed `neon` CLI.
  - `neon/SKILL.md:231` `neon mcp --agent <agent> -y` writes a Neon API key into the agent's user-level MCP config. An MCP install was already there before, as `npx -y add-mcp`.
  - The Claimable Neon path is unchanged for users without an account, and stricter for a failed existing account.
- **superpowers**: new `diagnosing-superpowers`.
  - It reads the harness's session transcripts, writes under `~/.superpowers/`, and searches GitHub issues with symptom terms.
  - It files an issue only after the user approves the exact text. Its triggers are broad; exclude it if transcript access in the sandbox is unwanted.
  - `executing-plans` now ships `scripts/task-start` and `task-done` (git and bash only), so that one skill moves from host to container mode, deliberately.
- **mattpocock-skills**: new `implement-spec`, `pr` and `retro`; `resolving-merge-conflicts` was removed upstream.
  - `retro` searches session logs on the machine.
  - Both `retro` and `implement-spec` run only when the user asks for them (`disable-model-invocation: true`).
- **agent-browser**: a WebMCP-first loop. `skill-data/core/SKILL.md:15` prefers a tool the page itself advertises when it matches the authorised task.
  - Page metadata is treated as untrusted, and consequential calls still need the host's confirmation (`:23`, `:479`).
  - Cisco raised `ACTIVE_REMOTE_ACQUIRE_EXECUTE` (HIGH) on `:15`. Read and accepted.
- **engineering-skills**: content moves into new per-skill references, and the inline security checklist now points at `../../references/security-checklist.md`.
  - That file is upstream's repo-root `references/`, which this group has never taken (`include: skills`). Older skills already pointed there before this sync.
  - Adding `references` to the group's `include` would make those links resolve.
- **emilkowalski-skills** (new `break-ui`, `mobile-native`), **elevenlabs-skills**, **gemini-skills**, **higgsfield-skills**, **knowledge-work-plugins**, **supabase-skills** and **awesome-copilot**: documentation changes only. No new environment variables, hosts, installers or scripts.
- **financial-services**, **shadcn-skills**, **small-business-skills** and **taste-skill**: upstream moved, but nothing this group takes changed.

## Scanner results

### `scan-skills.py`

| Group | Blocking | Warnings | Accepted |
|---|---:|---:|---:|
| agent-browser | 0 | 1 | 0 |
| anthropic-skills | 0 (2 accepted in this PR) | 3 | 2 |
| awesome-copilot | 0 | 3 | 0 |
| caveman-skills | 0 | 0 | 1 |
| cloudflare-skills | 0 | 5 | 0 |
| elevenlabs-skills | 0 | 25 | 2 |
| emilkowalski-skills | 0 | 3 | 1 |
| engineering-skills | 0 | 3 | 0 |
| gemini-skills | 0 | 0 | 0 |
| google-agents-cli | 0 (1 accepted in this PR) | 1 | 1 |
| higgsfield-skills | 0 | 22 | 0 |
| knowledge-work-plugins | 0 | 36 | 0 |
| lark-skills | 0 | 7 | 0 |
| last30days-skill | 0 | 1 | 9 |
| mattpocock-skills | 0 | 0 | 0 |
| neon-skills | 0 | 2 | 0 |
| supabase-skills | 0 | 0 | 0 |
| superpowers | 0 | 0 | 0 |

`scan-skills.py --changed origin/main` over the whole PR finds 0 blocking,
24 warnings and 6 accepted. Every warning that falls on a changed line was
read. They are vendor CLI installs (for example `cf@latest` in
cloudflare-skills) or anti-injection text that matches the stealth pattern
(for example `build-eval.md:227`). Every other
warning is on an unchanged line.

The three BLOCK findings accepted in `scan-accepted.yaml`:

- `anthropic-skills/.../evals/report/build-report-lite.mjs:28` and
  `runner-scaffold.mjs:112`: comments about refusing a planted
  `~/.ssh/id_rsa` link.
- `google-agents-cli/.../google-agents-cli-adk-code/SKILL.md:65`: the docs
  table row.

### Cisco `cisco-ai-skill-scanner` 2.2.2

Severity counts at the old pin and at the new one (C/H/M/L/I), and the
findings that appear only after the sync, MEDIUM and above:

| Group | Old | New | New findings at MEDIUM or above |
|---|---|---|---|
| agent-browser | 0/1/0/0/10 | 0/2/0/0/10 | HIGH `ACTIVE_REMOTE_ACQUIRE_EXECUTE` `skill-data/core/SKILL.md:15` (WebMCP, read: NOTE) |
| anthropic-skills | 1/2/3/9/1 | 3/3/6/9/1 | CRITICAL x2 cross-file chain `drop_block_probe.py` -> `prefix_diff.py`: false positive, `prefix_diff.py` has no network code. HIGH `PROMPT_INJECTION_CONCEALMENT` `shared/evals/build-eval.md:227`: false positive, it tells the agent not to impose a format on the user. MEDIUM x3: undeclared network use in `SKILL.md`, and the two request lines in `drop_block_probe.py` (:420, :428), which send to the Anthropic API as described above |
| awesome-copilot | 0/1/1/0/43 | 0/1/1/0/43 | none |
| caveman-skills | 0/1/0/0/12 | 0/1/0/0/14 | none |
| cloudflare-skills | 0/4/20/1/14 | 0/4/20/1/16 | MEDIUM x2 YARA code-execution on a "Skills install" docs link; MEDIUM Python `requests.post` in a Basin SQL example |
| elevenlabs-skills | 0/1/1/8/1 | same | none |
| emilkowalski-skills | 0/0/0/0/12 | 0/0/0/0/14 | none |
| engineering-skills | 0/2/0/0/25 | same | none |
| gemini-skills | 0/0/0/1/3 | same | none |
| google-agents-cli | 0/1/0/0/7 | 0/1/1/0/7 | MEDIUM Python `requests.post` in an ADK Live example |
| higgsfield-skills | 2/7/6/12/8 | same | none |
| knowledge-work-plugins | 0/0/0/0/127 | same | none |
| lark-skills | 1/0/8/1/28 | 1/0/9/1/28 | MEDIUM deep nesting of references in `lark-apps` |
| last30days-skill | 6/2/29/48/0 | same | none |
| mattpocock-skills | 0/0/0/1/25 | 0/0/0/1/27 | none |
| neon-skills | 0/0/0/0/7 | 0/0/0/0/8 | none |
| supabase-skills | 0/0/0/0/1 | same | none |
| superpowers | 2/0/0/17/14 | 2/0/0/17/15 | none |

For the reverted groups:

- Cisco flagged aws-skills' piped installers (`COMPOUND_FETCH_EXECUTE` x3)
  and ui-ux-pro-max's logo generator (`BEHAVIOR_ENV_VAR_EXFILTRATION`).
  The reading found that generator sends `MUAPI_API_KEY` to whatever result
  URL the server returns, without checking the host. It is dormant: the key
  is not in the skill's `env.optional`.
- It did not flag `finding-google-skills`, `discover-azure-skills`, the
  prisma GitHub pointers, the firecrawl feedback channel, the netlify
  installer, or `stack/`.

### What the scanners missed

The two scanners and the reading disagreed enough to record. Every revert
above came from reading:

- `scan-skills.py`'s `pipe-to-shell` rule does not join `\` line
  continuations, and its `unpinned-install` rule misses `npx skills add`
  without `@latest` and `npx` arguments inside JSON arrays.
- Neither scanner treats "fetch this URL and follow it", or "install this
  skill", as a finding.

## Versions

`sync-upstream.py` now writes every vendored group's `version` from
upstream, and `verify` fails on a hand-typed one. The rule is in
DEVELOPMENT.md under Versions.

- **From a release tag** (19 groups). For example, engineering-skills is
  0.6.12 + 6 commits, matching addyosmani/agent-skills' own tags.
  - Plain `vX.Y.Z` tags are preferred.
  - impeccable and shadcn-skills tag several products, so their series are
    set in `version_tags` (`skill-v*`, `shadcn@*`).
  - caveman also tags `bin-v`, `cli-v` and `pi-v`; the plain series picks
    its 3.x releases.
- **From a manifest** (16 groups), where upstream has no tag:
  - plugin.json, marketplace.json or package.json: 13 groups.
  - The highest of several declared versions: 3 groups.
    - financial-services and knowledge-work-plugins: their plugins' manifests.
    - prisma-skills: its SKILL.md files.
- **The commit's SHA** (3 groups: elevenlabs-skills, emilkowalski-skills,
  openai-skills), because upstream declares no version anywhere.
- **Tag and manifest disagree** (the tag wins):
  - impeccable's `skill-v4.3.1` against plugin.json 4.4.0, at the reverted
    target.
  - ui-ux-pro-max's v2.15.0 against plugin.json 2.13.0, at the reverted
    target.

In `index.yaml`, a skill whose SKILL.md declares its own version (or
`metadata.version`) now shows it, and every other skill shows its group's.
That gives 394 of the 1,046 skills their own version: aws-skills metadata versions such
as "1", google-skills 1.0.x, marketing-skills 2.0.x and so on.

## Index changes

**Added (11):**

- caveman-skills/megacave
- caveman-skills/ultracave
- cloudflare-skills/basin
- cloudflare-skills/k2
- emilkowalski-skills/break-ui
- emilkowalski-skills/mobile-native
- mattpocock-skills/implement-spec
- mattpocock-skills/pr
- mattpocock-skills/retro
- neon-skills/neon-auth
- superpowers/diagnosing-superpowers

**Removed (1):** mattpocock-skills/resolving-merge-conflicts, by upstream.
An agent pinned to an older skills SHA still has it.

**Mode change (1):** superpowers/executing-plans, host -> container.

## Tooling changes in this PR

- **`sync-upstream.py`:**
  - The upstream-version rule, `version_tags`, a dry-run
    `version [--check]` command, a version check in `verify`, and the
    version move in `pr-body`.
  - Tags are fetched with the tracked branch.
  - Fixed: a folder that upstream turns back into a symlink no longer
    leaves the link inside the old folder.
- **`build-index.py`:** per-skill SKILL.md versions, as above.
- **DEVELOPMENT.md and the porting guide:** describe the version rule.
