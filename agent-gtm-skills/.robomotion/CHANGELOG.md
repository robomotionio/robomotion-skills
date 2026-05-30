# Changelog — agent-gtm-skills

## [1.0.1] — 2026-05-30
- Reframed competitor automation-platform references to **Robomotion** (n8n /
  Make / Zapier / Tray.io / Workato) across `gtm-engineering`, `ai-sdr`,
  `solo-founder-gtm`, `content-to-pipeline`. In `gtm-engineering` the
  "n8n vs Make vs Zapier" comparison table + platform decision tree were replaced
  with a "Robomotion as the orchestration layer" section (the skill is advisory —
  it never generated competitor automations). Left factual/comparative references
  intact where substitution would be a false statement (e.g. the `ai-pricing`
  usage-based-pricing example). Robomotion competes with these platforms; the hub
  should not promote them.

## [1.0.0] — 2026-05-30
- Vendored from chadboyda/agent-gtm-skills@main (18 skills: positioning-icp,
  ai-pricing, sales-motion-design, ai-cold-outreach, ai-sdr, lead-enrichment,
  video-outreach, multi-platform-launch, ai-seo, social-selling,
  content-to-pipeline, ai-ugc-ads, paid-creative-ai, expansion-retention,
  partner-affiliate, gtm-engineering, solo-founder-gtm, gtm-metrics).
- Upstream already ships skills at `skills/<name>/SKILL.md`, which matches our
  group discovery contract — **no relocation needed**, copied byte-for-byte.
- Excluded upstream `site/` (a 42 KB marketing landing page, `index.html`) — not
  skill content and referenced by nothing. Everything else (`skills/`, `README.md`,
  `.claude-plugin/marketplace.json`) is vendored verbatim.
- **Pure-knowledge group:** every skill is a single `SKILL.md` playbook with no
  `scripts/`, no `post-install.sh`, and no env vars — so no `env.required` /
  `env.optional` files and no container mode. Cross-references between skills are
  all relational ("## Related Skills" sections), not directive file-pointers, so
  roles need no dependency closure (`optSkills` == `optActiveSkills`).
- License: upstream declares **MIT** in its `README.md` ("## License → MIT") but
  ships no `LICENSE` file. Added `.robomotion/LICENSE` with the canonical MIT text
  attributed to the author so the Designer has a stable license path.
- Added `.robomotion/skill.yaml`, `.robomotion/LICENSE`, this changelog.
