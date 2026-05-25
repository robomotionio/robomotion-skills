# Full port plan: `marketingskills` → `robomotion-skills`

> Plan for porting the entire [marketingskills](https://github.com/coreyhaines31/marketingskills)
> collection (v2.1.0) — all 41 skills **plus** its shared `tools/` CLI library —
> into this repo under a `marketing-skills/` group with a group-scoped `_shared/`.
> Authored 2026-05-25. Status: **executed 2026-05-25** — all 41 skills + 8
> per-category `_shared` libraries ported under `marketing-skills/`; index/README/
> validator updated; `validate.sh` + `build-index.py --check` green. (Sections
> below describe the design as built.)

## 1. Why this is feasible without platform changes

The launcher + loader + designer work that this port depends on is **already
implemented and consistent** on `origin/skills-260525` across all three repos
(verified by reading the branch directly — see [[repos-and-branch-state]]):

- **Launcher** (`packages-main` `origin/skills-260525`, head `1021033f5`): group-scoped
  `_shared` (`sharedGroupCandidates`/`sharedKey`, nearest-ancestor walking),
  `fetchViaIndex` (active-only per-file fetch via `index.json`), Dockerfile emits
  `_shared` first (layer reuse), `_shared/scripts/` flows through `needsSandbox`
  as a pseudo-skill → **container mode**.
- **Loader** (`skill_loader.py`): `${SHARED_DIR}`/`${HERMES_SHARED_DIR}` substitution via
  `local_shared_path` (nearest `_shared`, left literal if none).
- **Designer** (`robomotion` monorepo `origin/skills-260525`, head `4767a6b93`): reads
  `index.json` (one fetch, enumeration fallback), nested skills via `path`/`group`,
  per-skill `env.required`/`env.optional` (ignores `_shared`).
- **Index tooling** (this repo): `build-index.py` already emits `group`, `shared`,
  `files`, `contentHash` and resolves nearest-ancestor `_shared`. No change needed.

So this is a **skills-repo-only** effort. (To run end-to-end tests, check out
`skills-260525` in `packages-main` and the monorepo first.)

## 2. Source inventory (marketingskills v2.1.0)

- **41 skills** under `skills/<name>/` — pure-knowledge (agentskills.io spec:
  `name` + `description` + `metadata.version`). 34 have `references/`; some have
  `evals/`. **5 already ported** here (`cold-email`, `copywriting`, `cro`,
  `marketing-psychology`, `pricing`) → **36 remaining**.
- **`tools/` library**: ~60 zero-dep Node CLIs (`tools/clis/*.js`), 88 integration
  guides (`tools/integrations/*.md`), `tools/REGISTRY.md`, `tools/composio/*`.
- **13–16 skills reference the library** via relative `../../tools/...` paths.

## 3. Target structure

Skills are sub-sub-grouped by category, and **each category carries its own
self-contained `_shared/`** holding the CLIs + guides that category's skills use.
`${SHARED_DIR}` resolves to the **single nearest-ancestor `_shared` (no
cascade)** — verified in launcher `sharedGroupCandidates`, loader
`_shared_group_candidates`, and `build-index.py:nearest_shared` (all walk every
ancestor nearest-first to the repo root). So each category's `_shared` must be
complete on its own; **tools used by multiple categories are duplicated**.

```
marketing-skills/
  paid/
    _shared/
      scripts/      ← ga4.js, google-ads.js, meta-ads.js, linkedin-ads.js, tiktok-ads.js, segment.js
      references/   ← those tools' guides + USING-CLIS.md
    ads/SKILL.md             ${SHARED_DIR} → marketing-skills/paid/_shared
    ad-creative/SKILL.md
  measurement/
    _shared/scripts/  ← ga4.js (dup), mixpanel.js, amplitude.js, posthog.js, segment.js (dup)
    analytics/SKILL.md
    ab-testing/SKILL.md
  email/
    _shared/scripts/  ← resend.js, mailchimp.js, customer-io.js, kit.js, sendgrid.js, klaviyo.js, brevo.js
    emails/SKILL.md
    sms/SKILL.md
  growth/   (referrals, co-marketing, community-marketing, free-tools, lead-magnets, directory-submissions, churn-prevention)
  sales/    (revops, sales-enablement)
  seo/      (seo-audit, ai-seo, programmatic-seo, site-architecture, competitors, schema, aso)
  content/  (copywriting, copy-editing, cold-email, social, image, video, content-strategy)
  conversion/ (cro, signup, onboarding, popups, paywalls)
  strategy/ (product-marketing, marketing-ideas, marketing-psychology, launch, pricing, customer-research, competitor-profiling)
```

(~10 categories covering all 41; exact per-skill assignment + which categories
get a `_shared` finalized in Phase C. Category names are chosen to never equal a
skill name — e.g. your `ads/ga4` example → `paid/_shared/scripts/ga4.js` serving
the `ads` + `ad-creative` skills.)

- **Cross-domain CLIs duplicated where used:** `ga4`, `segment`, `customer-io`,
  `klaviyo`, `crossbeam`, `introw`, `partnerstack`. Small JS files; each
  category's `_shared` content-hashes independently (own image layer).
- **Scale win:** activating one category fetches **only that category's**
  `_shared` (e.g. `analytics` → ~5 CLIs, not ~150) — aligns with the
  "load only the relevant domain" best practice (§10).
- **Knowledge-only categories** (e.g. `strategy`, most of `conversion`) ship **no
  `_shared`** → those skills are host mode unless co-activated with a
  CLI-bearing skill.
- `build-index.py` indexes each skill `group=marketing-skills/<category>`,
  `shared=marketing-skills/<category>/_shared` (or `null`). No tooling change.
- **Migration:** the 5 pilots move repo-root → `marketing-skills/<category>/<name>`.
- **Future-proof:** a category needing private CLIs just gets a `_shared`;
  nearest-ancestor handles the rest, no migration of others.

## 4. Locked decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | **All tool `{TOOL}_API_KEY` vars go in each skill's `env.optional`.** | Marketing skills are advisory; they work with zero keys (the CLI is an enhancement). `env.optional` never blocks; names dedup across skills; Designer shows them non-blocking. Marketing skills should essentially never use `env.required`. |
| D2 | **OAuth access-token CLIs ship as-is; token in `env.optional` + documented expiry caveat.** | Most CLIs use static keys (clean Vault fit). The 6 OAuth-token tools (`ga4`/`GA4_ACCESS_TOKEN`, `meta-ads`/`META_ACCESS_TOKEN`, `google-ads`/`GOOGLE_ADS_TOKEN`, `linkedin-ads`/`LINKEDIN_ACCESS_TOKEN`, `google-search-console`/`GSC_ACCESS_TOKEN`, `tiktok-ads`/`TIKTOK_ACCESS_TOKEN`) get a "token expires — refresh out-of-band" note in their reference. Refresh-token wrappers deferred to a follow-up. |
| D3 | **`.agents/product-marketing.md` cross-skill context: keep the convention, document it's session/working-dir scoped.** | Sandbox has no persistent `.agents/`. The one genuine behavioral delta vs upstream; needs a doc note in `product-marketing` + `USING-CLIS.md`. |
| D4 | **Drop `evals/`.** | Test scaffolding, not runtime knowledge (matches the pilot port). |
| D5 | **Per-category self-contained `_shared`** (skills sub-sub-grouped by category; each category's `_shared` holds its own CLIs + guides; cross-domain CLIs duplicated). | Co-locates tools with the skills that use them; activating one category fetches only its CLIs (not all ~150) — the cleaner scaling story, and aligns with the "load only the relevant domain" best practice (§10). Cost = duplicating ~7 cross-domain CLIs (small JS) + per-category USING-CLIS. Forced by single-nearest `_shared` resolution (no cascade). |

## 5. Per-skill transforms

For every skill:
1. Keep spec front-matter (`name` + `description` + `metadata.version`); **add `tags`**.
2. Rewrite `../../tools/integrations/<t>.md`, `../../tools/REGISTRY.md` → `${SHARED_DIR}/references/...`.
3. Where the skill recommends running a tool that **has a CLI**, add concrete Usage:
   `node ${SHARED_DIR}/scripts/<tool>.js <resource> <action> …`. Tools without a
   ported CLI (MCP-only / SDK-only) stay **reference-only** (link the guide; no runnable line).
4. Rewrite internal `references/<f>.md` links → `${SKILL_DIR}/references/<f>.md`.
5. Declare each referenced CLI's env var(s) in **`env.optional`** (D1).
6. Add `LICENSE` (MIT; Corey Haines original + Robomotion mods) + `CHANGELOG.md`.
7. Drop `evals/` (D4). Keep `references/`.

## 6. Skill → tools → env mapping (the tool-backed skills)

CLI env-var names per the source `tools/clis/README.md` auth table. Only tools
with a ported CLI get a runnable Usage line; ⚠ = OAuth access-token tier (D2);
※ = referenced but **no CLI** (reference-only).

| Skill | Referenced tools | env.optional vars (CLIs only) |
|---|---|---|
| `analytics` | ga4⚠, mixpanel, amplitude, posthog, segment | `GA4_ACCESS_TOKEN`⚠, `MIXPANEL_TOKEN`/`MIXPANEL_API_KEY`/`MIXPANEL_SECRET`, `AMPLITUDE_API_KEY`/`AMPLITUDE_SECRET_KEY`, `SEGMENT_WRITE_KEY`/`SEGMENT_ACCESS_TOKEN` (posthog: CLI per registry) |
| `ads` | ga4⚠, google-ads⚠, meta-ads⚠, linkedin-ads⚠, tiktok-ads⚠, segment | the five `*_ACCESS_TOKEN`/`*_TOKEN` (+ `GOOGLE_ADS_DEVELOPER_TOKEN`/`_CUSTOMER_ID`, `META_AD_ACCOUNT_ID`, `TIKTOK_ADVERTISER_ID`), `SEGMENT_*` |
| `ad-creative` | google-ads⚠, meta-ads⚠, linkedin-ads⚠, tiktok-ads⚠ | same ad-platform token set |
| `emails` | resend, mailchimp, customer-io, kit, sendgrid, nitrosend※ | `RESEND_API_KEY`, `MAILCHIMP_API_KEY`, `CUSTOMERIO_*`, `KIT_API_KEY`/`KIT_API_SECRET`, `SENDGRID_API_KEY` |
| `sms` | klaviyo, brevo, customer-io, twilio※, plivo※, postscript※, attentive※, audiencetap※ | `KLAVIYO_API_KEY`, `BREVO_API_KEY`, `CUSTOMERIO_*` |
| `referrals` | rewardful, tolt, dub-co, mention-me, partnerstack, stripe※, introw※ | `REWARDFUL_API_KEY`, `TOLT_API_KEY`, `DUB_API_KEY`, `MENTIONME_API_KEY`, `PARTNERSTACK_PUBLIC_KEY`/`_SECRET_KEY` |
| `revops` | apollo, clearbit, calendly, savvycal, activecampaign, zapier, hubspot※, salesforce※, crossbeam, introw※ | `APOLLO_API_KEY`, `CLEARBIT_API_KEY`, `CALENDLY_API_KEY`, `SAVVYCAL_API_KEY`, `ACTIVECAMPAIGN_API_KEY`/`_API_URL`, `ZAPIER_API_KEY`, `CROSSBEAM_*` |
| `co-marketing` | crossbeam, partnerstack, introw※ | `CROSSBEAM_*`, `PARTNERSTACK_PUBLIC_KEY`/`_SECRET_KEY` |
| `churn-prevention` | posthog | (posthog CLI) |
| `video` | heygen※, hyperframes | (hyperframes CLI; heygen reference-only) |
| `launch`, `sales-enablement` | introw※ | — (reference-only) |
| `ai-seo` | registry/clis ref only | — |

(Plus 3 skills referencing tools from `references/` subfiles: `content-strategy`,
`customer-research`, `referrals`.) Exact CLI-existence per tool is resolved in
Phase A against the ported `_shared/scripts/` listing.

## 7. Phased execution + checklist

**Phase A — per-category `_shared/` libraries**
- [ ] Compute category → tools mapping (from §6) → category → CLI set (incl. cross-domain dups).
- [ ] For each category with tools: `marketing-skills/<cat>/_shared/scripts/` ← that category's `tools/clis/*.js`; `chmod +x`. (Script the copy from one source of truth so dups stay in sync.)
- [ ] `marketing-skills/<cat>/_shared/references/` ← that category's `tools/integrations/*.md` + a `USING-CLIS.md` copy (+ optional category mini-registry).
- [ ] Author one canonical `USING-CLIS.md` (run via `node ${SHARED_DIR}/scripts/<t>.js`; creds from Vault not `.env`; container mode; MCP/SDK-only tools are reference-only; OAuth-token expiry note; `.agents/product-marketing.md` is session-scoped; **curate a small active set per agent**) — copy into each category `_shared/references/`.
- [ ] Smoke-test every CLI once (dedup by filename): `node --check`, no-arg help, `env -u <KEY> node …` → clean JSON error.
- [ ] No `_shared/post-install.sh` (zero-dep; base image has node20).

**Phase B — restructure the 5 pilots** under `marketing-skills/` (+ optional tool wiring).

**Phase C — port the 36 remaining skills**
- [ ] C1: the ~13 tool-backed skills (`${SHARED_DIR}` proof) — §5 transforms + §6 env.
- [ ] C2: the ~23 knowledge-only skills (mechanical: front-matter `tags`, `${SKILL_DIR}` ref rewrite, LICENSE/CHANGELOG, drop evals).
- [ ] Each: confirm `name:` == folder, host vs container mode is as intended (all host except via shared `_shared` → container when active).

**Phase D — wire-up + verify**
- [ ] `python3 build-index.py` → commit `index.json`.
- [ ] Update `README.md` inventory (note the group + `_shared`).
- [ ] Extend `validate.sh` if needed (e.g. validate `_shared/scripts` are executable + `node --check`).
- [ ] `bash validate.sh && python3 build-index.py --check`.
- [ ] On `skills-260525` checkouts: `go vet ./... && go test ./...` (launcher), `npx tsc --noEmit -p tsconfig.app.json` (designer).

## 8. Risks / open items

- **Cross-domain CLI duplication** (D5): ~7 CLIs duplicated across categories. Mitigate by scripting the copy from `tools/clis/` as the single source of truth (a CI check can diff the dups), so edits never drift. Fetch per activation is now small (one category's CLIs, not ~150).
- **Active-set size** (§9.1): the loader injects full bodies of all active skills. Keep bodies lean + push depth to `references/`; document "curate a small active set per agent."
- **OAuth-token expiry** (D2): documented caveat, not a blocker; refresh wrappers are a follow-up.
- **`product-marketing.md` persistence** (D3): the one real behavioral delta vs upstream — needs the doc note; revisit if a persistent per-agent working dir becomes available.
- **MCP-only / SDK-only tools** (introw, cogny, sparktoro, gong, hubspot, salesforce, stripe, twilio, …): stay reference-only guides; skills already treat them as "read the guide."
- **Attribution/licensing**: MIT both ways; every ported skill keeps an Attribution line + repo `LICENSE`/`CHANGELOG`.

## 9. Best-practice alignment (industry research, May 2026)

Cross-checked the port against current Agent-Skill best practices (Anthropic
authoring guide, agentskills.io spec, the "discovery ceiling" analysis). Findings
and how they shape this port:

**Where Robomotion + this port already align**
- **Progressive disclosure / lean SKILL.md (<500 lines, detail in `references/`,
  one level deep).** The marketing skills are already <500 lines with one-level
  `references/`. Keep it that way; link depth lives in `${SKILL_DIR}/references/`
  and `${SHARED_DIR}/references/` (the model `cat`s on demand).
- **The discovery ceiling is Robomotion's *non-problem*.** Claude Code caps the
  skill-description budget (~1% context / 8 000-char floor → ~32 skills before
  truncation; one user saw only 42 of 63 skills appear). Robomotion sidesteps
  this: the **builder curates the active set in the Designer** and the loader
  injects **only those** — the model never selects among hundreds. This validates
  the Phase-4 "progressive disclosure: NO" call (curation bounds the prompt).
- **Utility scripts over generated code; handle errors, don't punt; JSON out;
  forward slashes.** The ported CLIs already do this (native `fetch`, `{"error"}`,
  `--dry-run`).
- **Domain-organized resources ("load only the relevant domain").** The
  **per-category `_shared`** (D5) is exactly this pattern at the repo level.

**Adjustments this research drives**
1. **Active-set size is the real budget in Robomotion** — the loader injects each
   active skill's **full body** (no lazy body-loading). So the lever is **lean
   bodies + on-demand references**: keep ported SKILL.md tight and push depth into
   `references/`. **Add to README/USING-CLIS: curate a *small* active set per
   agent** (e.g. the 3–6 skills for that agent's job, not all 41).
2. **Descriptions are discovery-critical** — third person, what + when + trigger
   keywords, ≤1024 chars. The marketing `description` fields already do this; keep
   them verbatim as `summary`/`description` (don't trim).
3. **Naming** — keep the collection's consistent lowercase-hyphen noun-phrase
   names; never reuse a name as a category dir (§3).
4. **Evals (D4)** — best practice is *eval-driven authoring*, but that's a build
   -time process, not a runtime artifact. Dropping `evals/` at runtime stays
   correct; **for new first-party skills, adopt eval-driven development** (write
   3 scenarios first). Note in the authoring how-to.
5. **No time-sensitive prose / consistent terminology / give a default + escape
   hatch** — spot-check during Phase C; the tool-choice sections ("use X for…,
   else Y") already follow the default-with-escape-hatch pattern.

(Consideration for the scale-design doc, not this port: even curated active sets
inject full bodies, so a future lightweight in-active-set disclosure — inject
metadata, `cat` the body on demand — could further bound large agents. Out of
scope here.)

## 10. References
- Authoring contract: `how-to-write-or-port-a-skill-to-robomotion.md` (§5 spec-compat, §8 `_shared`, §11e cross-agent port).
- Scale architecture: `docs/skill-system-scale-design.md`.
- Source (pristine, port out of only): `/home/faik/source/marketingskills`.
