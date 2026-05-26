# Review: `marketingskills` & gaps in the Robomotion skill system

> A deep review of [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)
> as a portability stress-test, the gaps it exposes in Robomotion's skill
> system, and the implementation plan to close them.
>
> Companion to `../how-to-write-or-port-a-skill-to-robomotion.md`.

## 1. What the repo is

- A **cross-agent Agent Skills collection** following the [agentskills.io spec](https://agentskills.io)
  (installs to `.agents/skills/`), that also ships as a **Claude Code plugin
  marketplace** (`.claude-plugin/marketplace.json`).
- **41 skills**, every one **`SKILL.md`-only at the skill level** (0 per-skill
  `scripts/`; 34 ship `references/`, 41 ship `evals/`). The skills are **pure
  marketing knowledge** (CRO, copywriting, SEO, ads, lifecycle, pricing, …).
- A **shared, repo-level `tools/` library**: **64 zero-dependency Node CLIs**
  (`tools/clis/*.js`), each reading creds from env vars, supporting `--dry-run`,
  printing JSON — plus `tools/integrations/*.md` guides, `tools/REGISTRY.md`, and
  a Composio/MCP layer for OAuth-heavy SaaS.
- **16 skills cross-reference that shared library** via relative paths like
  `../../tools/integrations/ga4.md` and `../../tools/clis/...`.
- Front-matter is the spec's `name` + `description` (rich, with trigger phrases)
  + `metadata.version`. No top-level `version`, no `summary`/`tags`.

## 2. Portability verdict

**Bucket A — ~25 pure-knowledge skills → directly portable** (host mode), exactly
like the `obsidian`/`notion` ports. Mechanical per-skill work: front-matter
transform, keep `references/`, distill the `description` trigger-phrases into a
"When to use" section, add `CHANGELOG`/`LICENSE`/README row. `evals/` is ignored
harmlessly; the Claude-Code-only `` !`cmd` `` injection isn't in their files.

**Bucket B — the shared 64-CLI execution layer → does NOT port as-is.** This is a
**hard architectural mismatch**, not a per-skill detail:

> Robomotion's launcher extracts **each skill folder in isolation**
> (`skills.go: extractSubtree(archive, skill.Path, dest)` → `<owner>__<repo>__<name>/`).
> A **repo-level sibling `tools/` directory is never extracted** alongside a skill,
> and there is no mechanism to extract a non-skill shared dir. So every
> `../../tools/clis/ga4.js` reference escapes the skill folder and won't resolve
> at runtime.

The marketingskills design is a **monorepo of skills sharing a common library**;
Robomotion's model is **self-contained skill folders**.

## 3. Gaps this exposes (verified against the code)

| # | Gap | Evidence |
|---|---|---|
| **G1** | No shared library across skills | `skills.go` extracts only `skill.Path`; no shared-dir extraction |
| **G2a** | `version` read top-level only; spec nests it under `metadata.version` | `skills.go: readSkillVersion` and Designer `stores/skills.ts:127` both match `^version:` |
| **G2b** | Skills discovered **only at repo root**; spec/Claude repos nest under `skills/<name>` | Designer `stores/skills.ts` enumerates top-level dirs; launcher `verifySkillRepo` same |
| G3 | All active skills' full `SKILL.md` always injected → large libraries bloat the prompt | `skill_loader.py: load_active_skills` appends every active body; no progressive disclosure |
| G4 | Bespoke `post-install.sh` per skill; no declarative deps | `dockerfile.go` only runs `post-install.sh` |
| G5 | A skill can't reach OAuth-heavy SaaS (Composio/MCP) without manual node wiring | MCP is agent-node config, not skill-declarable |
| G6 | No shared "product context" (their `.agents/product-marketing.md`) | n/a in Robomotion |
| G7 | No automated contract validation (they ship `validate-skills.sh`) | n/a in `robomotion-skills` |

**Already handled:** the Designer's marketplace **already** reads `description` as a
fallback for `summary` (`stores/skills.ts:122-123`), so the spec's `description`
field surfaces in Browse Skills today.

## 4. Implementation plan (this effort)

Ordered by value × safety.

### Phase 1 — `metadata.version` compatibility (G2a)
Make both version readers fall back to nested `metadata.version` so spec/Claude
skills get correct cache-busting and version display without a front-matter rewrite.
- Launcher `skills.go: readSkillVersion` — after the top-level scan, also detect a
  `metadata:` block and read its `version:`.
- Designer `stores/skills.ts` — read `metadata.version` when top-level `version` is absent.
- Loader `skill_loader.py` — same fallback for the cosmetic `name@version` title.

### Phase 2 — Nested-layout discovery (G2b)
Discover skills under a `skills/` subdirectory (the spec/Claude convention), in
addition to repo root. Keeps `path` semantics intact (the launcher already extracts
by `path`).
- Designer `stores/skills.ts` — when a repo has a top-level `skills/` dir, enumerate
  its children (and/or honor `.claude-plugin/plugin.json`'s `skills:` pointer).
- Launcher `verifySkillRepo` — mirror the same discovery so server-side validation agrees.

### Phase 3 — Shared repo-level library (G1) — the headline
A repo may ship a top-level **`_shared/`** directory. The launcher extracts it once
per repo and mounts it at a stable path; the loader exposes a **`${SHARED_DIR}`**
token so a `SKILL.md` can call `node ${SHARED_DIR}/clis/ga4.js`.
- `skills.go` — when resolving skills from a repo, also extract `_shared/` to
  `<owner>__<repo>___shared/`; include its content in the image hash.
- `launchplan.go` — a non-empty `_shared/` forces container mode (it ships scripts).
- `dockerfile.go` — COPY `_shared/` to `/opt/robomotion/skills/_shared/`; run an
  optional `_shared/post-install.sh`.
- `skill_loader.py` — substitute `${SHARED_DIR}` (host + container paths).
- **Env stays per-skill.** `_shared/` carries code/docs only; the launcher ignores
  any `_shared/env.*`. A skill that calls a shared CLI declares that CLI's
  credentials in its own `env.required`/`env.optional`, so the run requires (and
  the Designer shows) only the vars the active skills use — not the whole library.

### Phase 4 — Pilot ports
Port ~5 high-value **pure-knowledge** marketing skills (cro, copywriting,
cold-email, pricing, marketing-psychology) to validate the knowledge-bucket flow.

### Phase 5 — Validation (G7)
Add `validate.sh` + a GitHub Action enforcing the folder contract.

### Deferred
G3 (progressive disclosure), G4 (declarative deps), G5 (skill-declared MCP),
G6 (shared product context) — designed here, implemented later.

## 5. Notes on the shared-library credential model
The shared CLIs read many SaaS credentials (`GA4_ACCESS_TOKEN`, `AHREFS_API_KEY`,
…) — but a credential belongs to whichever **skill** uses the CLI, not to the
shared library. So each skill declares the vars its referenced CLIs need in its
**own** `env.required`/`env.optional`; `_shared/` carries no env, and the launcher
ignores any `_shared/env.*`. This is deliberate: a blanket `_shared/env.required`
would make every one of the library's dozens of credentials required for any
skill from the repo — run-blocking and noisy in the Designer. Per-skill keeps the
required set scoped to the active skills (names dedup across skills); values flow
through the existing credential-proxy path, and a `_shared/` that ships scripts
forces container mode so the CLIs run sandboxed.
