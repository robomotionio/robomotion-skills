---
name: linkedin-message-writer
description: Research LinkedIn leads (profile + recent posts) and write personalized messages for any LinkedIn message type — connection request, InMail, DM, message request, post comment, or comment reply — respecting each type's character limit, then export tool-ready CSVs. Use given a list of LinkedIn URLs and a goal/angle. The drafting half of linkedin-outreach.
metadata:
  version: 1.0.1
  category: outreach
  type: capability
---

# LinkedIn Message Writer

The **agent writes** each personalized message; the bundled scripts deterministically
**lint character limits** and **export the tool CSV**. Research uses the
`linkedin-profile-post-scraper` capability (Apify, or its keyless Playwright cookie degrade).

## When to use

- "Write LinkedIn messages" / "personalized connection requests / InMails / DMs for these leads."
- Given LinkedIn URLs + a goal/angle, produce per-lead messages.
- The drafting half of `linkedin-outreach`; downstream of `linkedin-commenter-extractor`,
  `linkedin-influencer-discovery`, `kol-discovery`.

## How it works (agent steps)

1. **Intake** leads (LinkedIn URLs), `message_type`, `account_tier` (free/premium — needed
   for connection requests), goal, angle, tone, export tool.
2. **Research each lead** — run `linkedin-profile-post-scraper` on each URL for profile +
   recent posts (Apify if `APIFY_API_TOKEN` set, else web-automation + cookie, else write
   from user-supplied context only). Skip post-scrape for very large lists; personalize on
   headline alone.
3. **Write the message** for the chosen type, leading with the signal/relevance, within the
   per-type limit:
   - connection_request: **200 (free) / 300 (premium)**
   - inmail: subject **200** + body **1900**
   - dm / message_request: **8000**
   - post_comment / comment_reply: **1250** (must add value — never "Great post!")
4. **Lint** the drafts (see below); rewrite — never truncate — anything over limit.
5. (sequence) Order CR -> value-first DM -> social-proof DM -> breakup with timing.
6. **Export** the tool CSV.

## How to run

Lint drafted messages (Python 3 stdlib, no install):

```bash
python3 ${SKILL_DIR}/scripts/linkedin_lint.py --input ${WORKSPACE}/messages.json
```

Message JSON — one object or a list:

```json
{"linkedin_url":"https://www.linkedin.com/in/x","name":"Ada","message_type":"connection_request",
 "account_tier":"free","message":"..."}
```

Export to a tool-ready CSV:

```bash
python3 ${SKILL_DIR}/scripts/export_csv.py --input ${WORKSPACE}/messages.json \
  --tool phantombuster --output ${WORKSPACE}/linkedin_outreach.csv
```

`--tool`: `generic` | `dripify` | `expandi` | `botdog` | `phantombuster`. The linter exits
**1** on any over-limit message (rewrite, don't truncate).

## Outputs

- Per-lead messages `{linkedin_url, name, company, title, message(s), char_count,
  personalization_notes}`, validated against type limits.
- A tool-ready CSV (per-tool column mapping) to workspace / channel attachment.

## Credentials / env

- `env.required`: none. The writing is done by the host agent; the linter + exporter are
  stdlib Python. **No paid service is applicable to the drafting/lint/export steps themselves.**
- `env.optional`: `APIFY_API_TOKEN` — only for the *delegated* research step via
  `linkedin-profile-post-scraper`: **if set → that skill's cookieless Apify actor; else → its
  keyless Playwright `li_at`-cookie degrade, or write from user-supplied context only** (no
  fresh research). The fallback lives in the delegated skill, not here.

## Notes & edge cases

- The connection-request limit is the gatekeeper — strictly 200 (free) / 300 (premium);
  rewrite to fit. Comments must add value, never filler.
- This skill produces the CSV — it does **not** send. Sending is `linkedin-outreach` /
  phantombuster.
- Research depth scales cost (Apify ~credits per profile/post); for huge lists, skip the
  post scrape and personalize on headline only.
