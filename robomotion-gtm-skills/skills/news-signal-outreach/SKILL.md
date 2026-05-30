---
name: news-signal-outreach
description: The catch-all signal composite — take any news (article, post, announcement, event, regulation, launch, acquisition, layoff, expansion), evaluate whether the companies/people in it fit ICP, identify the connection to the product, find the right people, and draft outreach using the news as the hook. Handles evaluate-only and full-outreach modes. Hands off to cold-email-outreach or linkedin-outreach.
metadata:
  version: 1.0.1
  category: outreach
  type: composite
---

# News Signal Outreach

The long-tail composite. **Scripts ingest** the news and **find contacts**; the **agent
extracts entities, evaluates ICP fit, finds the relevance angle, and drafts**. Many
requests are evaluate-only — stop after the angle and don't draft/send unless asked.

## When to use

- User shares ANY URL/post/article: "is this relevant / a fit / should we reach out?"
- "Came across", "saw this", "found this article" + a company/person.
- Route here only what the four structured composites (funding/hiring/leadership/champion)
  don't own.

## How it works (scripts + agent)

1. **Ingest** — `ingest_news.py --url <link>` fetches + cleans the page (or `--text-file`
   for pasted text). LinkedIn/tweet/gated sources flag `partial_content` -> use
   web-automation + cookie in a flow. **(agent)** extract companies, people, event type.
2. **(agent) Evaluate ICP fit** of each entity; for person-level news, resolve their company
   (web search / Apollo).
3. **(agent) Find the relevance angle** — how the news shifts priorities / opens a window for
   the product. **For evaluate-only requests, stop here** and return fit + angle.
4. **Find people** — `find_contacts.py` (Apollo by domain + persona titles; `--enrich
   --verify`; degrades to pattern-guess).
5. **(agent) Draft** sequences with `email-drafting` using the news as the hook — keep
   personalization deep (Tier 3); these are opportunistic and un-templated.
6. **Hand off** to `cold-email-outreach` / `linkedin-outreach`; request launch approval.

## How to run

```bash
# 1 — ingest the news
python3 ${SKILL_DIR}/scripts/ingest_news.py \
  --url "https://example.com/acme-acquires-foo" --output ${WORKSPACE}/news.json

# 4 — find people (only if proceeding to outreach)
python3 ${SKILL_DIR}/scripts/find_contacts.py \
  --domains ${WORKSPACE}/qualified.json --titles "VP Ops,Head of IT" \
  --per-company 3 --enrich --verify --output ${WORKSPACE}/contacts.json
```

## Outputs

- `news.json` (cleaned content), the agent's `icp-qualified-targets` + `relevance-angles`,
  `contacts.json`, drafted sequences. Evaluate-only: just the qualified targets + angle.

## Credentials / env

- `env.required`: **none.** Ingest is keyless, reasoning/drafting is the agent, and the launch
  step hands off to `cold-email-outreach` (CSV export with no key).
- `env.optional` (all degrade): `APOLLO_API_KEY` — if set → people-finding / company
  resolution; else → keyless serp + pattern-guess. `MILLIONVERIFIER_API_KEY` — if set →
  verify; else → local syntax/dedup (bounce risk). `DROPCONTACT_API_KEY` — email-finding
  fallback. **Send/launch — if a send key (`LEMLIST_API_KEY` / `INSTANTLY_API_KEY` /
  `SENDGRID_API_KEY` / `RESEND_API_KEY`, or `PHANTOMBUSTER_API_KEY` for LinkedIn) is set →
  launch the sequence; else → export a CSV to send manually** (the keyless default).

## Notes & edge cases

- Many requests are evaluate-only — stop after the angle; don't draft/send unless asked.
- LinkedIn/tweet sources need web-automation (JS/anti-bot); some posts are gated and yield
  partial content (degrade to LLM-from-snippet).
- Keep personalization deep — the best of these are un-templated.
