# Robomotion Skills Schema (v2)

Authoritative reference for the `skills-index.json` manifest, lockfile
format, audit log format, and key rotation policy.

## Core policy statement

> **Robomotion skills are portable instruction bundles. They may describe
> workflows, call vetted Robomotion packages, or reference required
> external CLIs, but they must not ship or execute arbitrary code. Any
> executable capability must be implemented as a Robomotion package and
> distributed through the package repository.**

## Skill role model

Internally each entry has a single-letter `role`. User-visible surfaces
use the full name.

| `role` | Name                        | What it is | Where it lives |
|--------|-----------------------------|------------|----------------|
| `D`    | Documentation Skill         | Markdown-only procedural knowledge. May reference external CLIs that the user already has. No Robomotion package dependency. | `skills.robomotion.io/stable/` |
| `W`    | Package Wrapper Skill       | Documents how to call a vetted Robomotion package via `robomotion <pkg> <cmd>`. Body is **generated** from package node reflection. | `skills.robomotion.io/stable/` |
| `C`    | Package Candidate           | A useful upstream capability blocked on a missing Robomotion package. Filed as a roadmap item, not published. | Issue tracker only |
| `R`    | Rejected Skill              | Ships `scripts/`, requires arbitrary execution, adversarial by design, or fails content/license policy. | `skill-deprecated.yaml` (audit trail) |

Phase 1 publishes only Documentation and Package Wrapper Skills.

## skills-index.json (v2)

```jsonc
{
  "format_version": 2,
  "corpus_version": "2026-05-02",
  "name": "Robomotion Official Skills",
  "description": "Curated skills for Robomotion LLM Agents",
  "signed_by": "<key-id>",
  "policy_versions": ["2026-05-02"],
  "skills": [ /* see entry shape below */ ]
}
```

### Per-entry shape

```jsonc
{
  "name": "test-driven-development",
  "path": "skills/test-driven-development",
  "description": "...",
  "version": "1.1.0",
  "tags": ["..."],
  "license": "MIT",

  "role": "D",                          // D | W only in stable
  "category": "software-development",

  "checksum": "sha256:<hex>",           // of the tarball
  "size_bytes": 12834,

  "compatibility": {
    "robomotion_min_version": "1.9.0",
    "hermes_agent_min_version": "0.3.0",
    "schema_version": 2
  },

  "policy": {
    "profile": "markdown-only",
    "version": "2026-05-02"
  },

  "runtime": {
    "platforms": ["linux/amd64","linux/arm64","darwin/amd64","darwin/arm64","windows/amd64"],
    "requires_packages": [],            // [{namespace, version_spec}]
    "requires_cli": [],                 // [{name, version_spec}]
    "requires_env_vars": []             // soft-fail with hint
  },

  "source": {                           // immutable provenance
    "kind": "upstream-import",          // upstream-import | robomotion-native | user-contrib
    "repo": "github.com/NousResearch/hermes-agent",
    "ref": "v2026.4.23",
    "commit": "<sha>",
    "path": "skills/software-development/test-driven-development",
    "license": "MIT",
    "license_notice_path": "ATTRIBUTION.md#test-driven-development",
    "upstream_equivalent": null         // optional cross-reference for native entries
  },

  "review": {                           // mutable across versions
    "status": "active",                 // active | deprecated | revoked
    "approved_at": "2026-05-02T00:00:00Z",
    "approved_by": "github:faik",
    "review_pr": "https://github.com/.../pull/123",
    "policy_version": "2026-05-02",
    "eval_passed_at": "2026-05-02T00:00:00Z",
    "eval_pass_count": 0,
    "eval_fail_count": 0,
    "content_scan_at": "2026-05-02T00:00:00Z",
    "content_scan_findings": []
  },

  "deprecation": {                      // present only when status != active
    "replaced_by": "...",
    "reason": "...",
    "deprecated_at": "..."
  }
}
```

`source` records *where* the artifact came from. `review` records *why
Robomotion trusts this transformed artifact*. The split lets
`review.status` flip to `revoked` later without rewriting source
provenance.

## SKILL.md template tokens

When the runtime injects a skill's `SKILL.md` into the agent's system
prompt, two tokens are substituted with concrete values **at load time**
— before the prompt reaches the LLM. This avoids the model wasting a
tool call discovering its own skill directory at runtime.

| Token                    | Substituted with                                                    |
|--------------------------|---------------------------------------------------------------------|
| `${HERMES_SKILL_DIR}`    | Absolute path to this skill's directory inside the agent runtime    |
| `${HERMES_SESSION_ID}`   | Current conversation session id (per-turn)                          |

Convention: use `${HERMES_SKILL_DIR}` whenever a skill references one
of its own bundled files. `references/` and `assets/` subdirectories
are the canonical homes for static markdown, examples, and data files
a Documentation Skill might point the model at.

```markdown
## Examples

See the JQL cookbook at `${HERMES_SKILL_DIR}/references/jql.md`.
Sample payloads live under `${HERMES_SKILL_DIR}/assets/`.
```

After substitution the model sees a fully-qualified absolute path and
can reference it directly with `read_file` / `terminal` etc., no
discovery step required.

Notes:

- Tokens that don't resolve (e.g. `${HERMES_SESSION_ID}` when no
  session is bound) are left in the text as-is so authors can spot
  unbound references during review.
- The substitution mirrors upstream Hermes
  (`agent.skill_commands._substitute_template_vars`); skills that use
  these tokens drop unchanged into vanilla `hermes-cli`.
- This does **not** relax the executable-content policy. Role `R`
  skills (those that ship `scripts/` for arbitrary execution) remain
  rejected. The token is for referencing static, declarative
  per-skill content.

## Lockfile format

```json
{
  "format_version": 1,
  "skills": [
    {
      "name": "test-driven-development",
      "version": "1.1.0",
      "checksum": "sha256:<hex>",
      "index_corpus_version": "2026-05-02"
    }
  ]
}
```

`install_skill.py` runs in **locked mode** when `inLockfilePath` is set:
the resolver installs the exact version + checksum recorded, ignoring
the index's current version. Robomotion flows that ship a lockfile
become reproducible across robots.

Lockfile authoring is a Phase 2 deliverable (`roboctl flow lock`).
Phase 1 supports *consuming* lockfiles only.

## Audit log format

`~/.hermes/skills/_robomotion/.audit.log` — one JSON line per
install/uninstall/update event:

```json
{"ts":"2026-05-02T12:34:56Z","action":"install","name":"test-driven-development","version":"1.1.0","sha256":"<hex>","source_url":"https://skills.robomotion.io/stable/skills/test-driven-development-1.1.0.tar.gz","signed_by_key_id":"<8-byte-hex>","robot_id":"r-abc","result":"ok"}
```

Required fields: `ts`, `action`, `name`, `result`. Optional fields:
`version`, `sha256`, `source_url`, `signed_by_key_id`, `robot_id`,
`error`, `error_kind`.

## Key rotation policy

Public minisign key shipped with the `hermes-agent` Robomotion package
at `src/hermes-agent/skills-publisher.pub`. Private key in GitHub
Actions secret `SKILLS_MINISIGN_PRIVATE_KEY` of the
`robomotion-skills` repo.

Rotation procedure:

1. Generate the new keypair locally with
   `minisign -G -p new.pub -s new.key`.
2. Open a PR in `packages-main` that ships **both** the old and the new
   public keys in `src/hermes-agent/skills-publisher.pub` and bumps the
   `hermes-agent` package minor version. The verifier accepts either
   key during the rotation window.
3. Replace `SKILLS_MINISIGN_PRIVATE_KEY` in the `robomotion-skills`
   repo. Republish the index. Verify clients on the new package
   version accept the new signature.
4. After one stable `hermes-agent` release window, drop the old key
   from `skills-publisher.pub` in a follow-up PR. Robots that still
   have the older `hermes-agent` will continue to verify against the
   old signature on the previously-published index, which never
   changes; new index publishes use only the new key.

Compromise procedure: same as above but skip step 1's coordination —
push the new-key-only `hermes-agent` package immediately and revoke
all previously-signed indices via a `revoked_keys` field added to a
break-glass package version.

## Migration from v1

Legacy entries (`format_version: 1` or unset) are tolerated by future
readers as `role: D` with no `compatibility`, no `runtime`, no
`policy`, and `review.status: active` by default. New entries always
ship v2 fields.

`generate_index.py` always emits v2.
