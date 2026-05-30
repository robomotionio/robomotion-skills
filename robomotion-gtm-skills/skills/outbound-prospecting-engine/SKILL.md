---
name: outbound-prospecting-engine
description: Build and run a complete outbound prospecting system end to end — detect intent signals, research companies, find decision-maker contacts, deduplicate, personalize messaging, launch the campaign, and monitor/iterate. The top-level orchestrator that strings the signal, enrichment, and outreach skills into one repeatable engine. Use when the user wants the whole pipeline, not a single signal or send.
metadata:
  version: 1.0.1
  category: outreach
  type: playbook
---

# Outbound Prospecting Engine

The top-level playbook. It is mostly **agent orchestration** of the other outreach skills,
plus one piece of unique deterministic glue — `contact_cache.py` — that dedups against a
persistent cache so the engine is repeatable without re-spamming.

## When to use

- "Set up outbound prospecting for [client]" / "build a lead gen engine targeting [ICP]" /
  "find and reach out to companies that need [solution]."
- When the user wants the whole pipeline, not a single signal or a single send.

## The pipeline (agent routes each step to a sub-skill)

1. **(agent) Define signal sources** from the client's ICP/motion.
2. **Detect signals (parallel)** — route to the sub-skills:
   - hiring -> `hiring-signal-outreach` (`detect_signal.py --signal hiring`)
   - funding -> `funding-signal-outreach` (`detect_signal.py --signal funding`)
   - LinkedIn posts/commenters -> `linkedin-post-research` + `linkedin-commenter-extractor`
   - news/events/competitor engagers -> `news-signal-outreach` / web-automation
3. **(agent) Qualify & score** against ICP — multi-signal = highest; job-posting + funding =
   strongest intent.
4. **Find contacts** — `find_contacts.py` (Apollo by domain + ICP titles; verify) from a
   sub-skill, for the top companies.
5. **Dedup** — `contact_cache.py` against the persistent cache; contact only the NEW ones,
   skip already-contacted, add the new ones back.
6. **(agent) Personalize** per lead with `email-drafting` (the surfacing signal as "why now").
7. **Launch** — `cold-email-outreach` (lemlist/instantly) and/or `linkedin-outreach`
   (phantombuster/CSV).
8. **(agent) Monitor & iterate** — pull tool metrics, persist history, schedule weekly re-runs
   (platform Cron), report to channel.

## How to run (the glue)

The unique script is the contact-cache dedup — run it between contact-finding and launch:

```bash
python3 ${SKILL_DIR}/scripts/contact_cache.py \
  --new ${WORKSPACE}/found_contacts.json \
  --cache ${WORKSPACE}/contact_cache.json \
  --update --output ${WORKSPACE}/to_contact.json
```

It matches on normalized email + LinkedIn URL, dedups within the batch too, and (with
`--update`) appends the NEW contacts to the cache. Everything else is the sub-skills above,
invoked by the agent at each checkpoint.

## Outputs

- Per cycle: a qualified + deduped lead list with contacts and personalized sequences, a
  launched campaign in the chosen tool, and tracked metrics persisted for iteration; review
  tables to the channel at each checkpoint.

## Credentials / env

- `env.required`: **none.** Signal detection is keyless, qualify/personalize is the agent, and
  the launch step routes to `cold-email-outreach` / `linkedin-outreach` (CSV export with no key).
- `env.optional` (all degrade): `APOLLO_API_KEY` — if set → contact-finding + funding/leadership
  data; else → keyless serp + pattern-guess. `APIFY_API_TOKEN` — if set → LinkedIn/event/
  competitor signal scale; else → serp/web-automation. `DROPCONTACT_API_KEY` — email-finding
  fallback. `MILLIONVERIFIER_API_KEY` — if set → verify; else → local syntax/dedup (bounce
  risk). **Send/launch — if a send key (`LEMLIST_API_KEY` / `INSTANTLY_API_KEY`, or
  `PHANTOMBUSTER_API_KEY` for LinkedIn) is set → launch; else → export a CSV to send manually**
  (the keyless default). Store creds (`SUPABASE_*`, `HUBSPOT_API_KEY`) — if set → durable
  cache/metrics/CRM; else → workspace file-cache CSV ledger.

## Notes & edge cases

- Human checkpoints are mandatory — after qualification, after personalization, and after each
  cycle — gate launches on these.
- The contact cache is what makes this repeatable — always dedup before contact-finding *and*
  before launch; write outcomes back.
- Multi-signal leads convert best — prioritize them; single social mentions are awareness-only.
- Run signal detection weekly; rotate proxy + throttle every scrape source; degrade any missing
  paid enrichment to the keyless backbone and flag reduced fidelity rather than stopping.
