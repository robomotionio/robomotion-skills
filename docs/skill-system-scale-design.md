# Skill system at scale — design (hundreds → thousands of skills)

> Status: **design, for alignment before implementation.** Companion to
> `marketingskills-review-and-skill-system-gaps.md` and the authoring guide.
>
> Goal stated 2026-05-25: the skill system must scale **cleanly** to hundreds or
> thousands of skills — discovery, distribution, and runtime all manageable. This
> doc is the architecture we build toward; new work must fit it.

## 1. What breaks at scale (grounded in today's code)

| # | Bottleneck | Where | Why it fails at 1000s |
|---|---|---|---|
| **B1** | **Browser-side GitHub enumeration** — 1 Contents API call per repo + 1 raw `SKILL.md` fetch per skill (N+1) | Designer `stores/skills.ts: fetchSkills` | Unauthenticated GitHub API = **60 req/h**; thousands of skills = thousands of fetches → instant rate-limit, slow, fragile |
| **B2** | **Whole-repo tarball per agent run** | Launcher `skills.go: ensureArchive` (GitHub `/tarball/<ref>`) | A monorepo of thousands of skills is a huge download for every run; you fetch everything to use one skill |
| **B3** | **Flat repo-root layout** | repo convention; Designer enumerates top-level + one `skills/` level | Thousands of folders in one namespace is unbrowsable and collision-prone |
| **B4** | **All active skills' full `SKILL.md` injected** | Loader `skill_loader.py: load_active_skills` | Many active skills → system-prompt bloat (no progressive disclosure) |
| **B5** | **Client-side browse/search** | Designer marketplace | Searching/paginating thousands client-side is unworkable |

B1 and B2 are the hard blockers — they make "thousands of skills" non-functional today, not just slow.

## 2. Design pillars

### P1 — A generated INDEX, not live enumeration (fixes B1, B3, B5)
Every skill repo ships a machine-generated **`index.json`** (built in CI; `validate.sh` extended to emit it). One fetch per repo replaces the N+1 probing. Entry shape:

```jsonc
{
  "schemaVersion": 1,
  "repo": "robomotionio/robomotion-skills",
  "generatedAt": "2026-05-25T12:00:00Z",
  "skills": [
    {
      "name": "cold-email",
      "path": "marketing-skills/cold-email",   // full path in repo
      "group": "marketing-skills",             // for browse facets / nearest _shared
      "summary": "Write B2B cold emails …",
      "tags": ["cold-email", "outbound"],
      "version": "2.0.0",
      "mode": "host",                          // host|container (precomputed)
      "env": { "required": [], "optional": [] },
      "shared": "marketing-skills/_shared",    // nearest _shared, or null
      "contentHash": "ab12cd34ef56",
      "bundle": "bundles/cold-email@ab12cd34ef56.tar.gz"
    }
  ],
  "shared": [
    { "path": "marketing-skills/_shared", "contentHash": "…", "bundle": "bundles/_shared--marketing-skills@…tar.gz" }
  ]
}
```

The Designer reads the index → browse/search/paginate/env-display with **zero per-skill fetches**. `env` in the index also removes the per-skill `env.required`/`env.optional` fetch the Environment tab does today.

### P2 — Content-addressed per-skill bundles, not whole-repo tarballs (fixes B2)
CI packages **each skill** (and each `_shared`) into a content-addressed tarball (`<name>@<hash>.tar.gz`) referenced by the index. The launcher downloads **only the active skills + their nearest `_shared`** — never the whole repo. Content-addressing → immutable, perfectly cacheable, dedupes identical content across repos/versions. (Fallback for small repos with no bundles: today's whole-repo tarball path.)

### P3 — Hierarchy + namespacing (fixes B3)
Skills live under `skills/<group…>/<skill>` (arbitrary depth). The index carries `path` + `group`; the Designer offers category facets. **`_shared` is resolved nearest-ancestor** within the hierarchy (group-scoped shared library — `marketing-skills/_shared` serves `marketing-skills/*`, repo-root `_shared` is the fallback). Names are display labels; `path` is the unique key.

### P4 — Progressive disclosure in the prompt (fixes B4)
Inject only **`name` + `description`** for active skills (tier 1); the model pulls a skill's full `SKILL.md` on demand via a `skill_view`-style call (tier 2); `references/` on further demand (tier 3). Prompt size stays bounded no matter how many skills are active. (Upstream Hermes has this; Robomotion currently injects full bodies — restore it.)

### P5 — A central registry API (scales B1/B5 beyond per-repo)
A Robomotion-hosted catalog (`/v1/skills.search?q=&category=&tags=&page=`) aggregates repo indexes server-side. The Designer queries the backend, not GitHub — search, ranking, pagination, private repos, millions of skills. Repos stay the source of truth; CI publishes their index to the registry.

### P6 — Content-addressing everywhere (versioning + cache)
Per-skill and per-`_shared` `contentHash` drives: the image cache key, bundle cache, and Designer display. Rebuild/refetch only on change; dedupe identical content.

## 3. How current/in-flight work fits

- **`_shared` nearest-ancestor (in progress)** → P3. Keep the design (group-scoped shared lib); it slots straight in. Implementation paused pending this alignment.
- **`env.required`/`env.optional` per skill** → already scale-friendly (scoped to active). The **index** surfaces them so the Designer stops fetching each file (kills part of B1).
- **agentskills.io front-matter compat** → ingestion of external catalogs into the index.
- **`validate.sh`** → extend in CI to also **emit `index.json`** (and, later, the bundles). Validation and indexing share one pass.
- **`metadata.version` / nested `skills/` discovery** → folded into the indexer (it parses front-matter once, in CI, not per-browse).

## 4. Migration phases (backward compatible)

1. **Index (per-repo). ✅ DONE.** `build-index.py` emits `index.json` (CI drift-checks it via `--check`); the Designer (`stores/skills.ts`) prefers it and the Environment tab reads its `env`, falling back to enumeration when absent. → kills B1/B5, no launcher change.
2. **Nearest-ancestor `_shared` + hierarchy.** Finish the group-scoped shared library; index records `group`/`shared`. → P3.
3. **Content-addressed bundles.** CI emits per-skill bundles; launcher fetches active-only, falls back to whole-repo tarball. → kills B2.
4. **Progressive disclosure.** Loader tier-1/tier-2 injection. → kills B4.
5. **Registry API.** Central catalog; Designer queries backend. → P5.

Each phase is independently shippable and reversible; nothing forces a big-bang rewrite.

## 5. Open decisions (need your call)

- **D1 — Registry vs. per-repo index first?** Per-repo `index.json` is the fast, low-risk first step; the central registry is the end state. Start with the index?
- **D2 — One monorepo vs. many repos** for first-party skills. Index + bundles make a monorepo viable (fetch active-only); many repos shard discovery. Recommendation: monorepo + index + bundles.
- **D3 — Who builds the index/bundles?** CI in each skill repo (recommended) vs. the registry ingesting raw repos.
- **D4 — Progressive disclosure** depends on the agent exposing a `skill_view` tool — confirm we restore that upstream capability.
