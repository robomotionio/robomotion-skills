---
name: company-contact-finder
description: Find the decision-makers at a named company for a given set of target titles using a cheapest-first fallback (Apollo People Search when available, keyless LinkedIn-profile search otherwise). Returns contacts with name, title, LinkedIn URL, and location. Use when you have an ICP-fit company and need the humans to reach.
metadata:
  version: 1.0.0
  category: lead-generation
  type: capability
---

# Company Contact Finder

Layered, cheapest-first contact discovery at a specific company. Apollo People Search is
the primary path (free search, no email reveal); a keyless LinkedIn-profile web search is
the degrade when no Apollo key is present.

## When to use

- "Who are the partners / CFOs / VP Finance at [company]?"
- "Find the heads of engineering at [company] and their LinkedIn."
- Downstream of qualification, when a company is ICP-fit and you need the buyer.

## How to run

### Primary — Apollo (when `APOLLO_API_KEY` is set)

```bash
python3 ${SKILL_DIR}/scripts/apollo_people.py \
  --company "Acme Corp" --domain acme.com \
  --titles "CFO,VP Finance,Head of Finance" \
  --num-results 10 \
  --output ${WORKSPACE}/contacts.json
```

`--domain` is optional; without it the script resolves the company name to a domain via
Apollo Org Search. Free People Search returns name/title/LinkedIn/location; email is empty
(reveal it later with `apollo-lead-finder`'s enrich phase if needed).

### Degrade — keyless (no Apollo key)

```bash
python3 ${SKILL_DIR}/scripts/serp_people.py \
  --company "Acme Corp" \
  --titles "CFO,VP Finance" \
  --num-results 10 \
  --output ${WORKSPACE}/contacts.json
```

Runs `site:linkedin.com/in "<company>" "<title>"` searches and returns candidate profile
URLs + result title/snippet. You (the agent) resolve `name` from the snippet.

### Select & dedup (you, the agent)

Read the JSON, dedup by normalized LinkedIn URL, drop off-target titles, trim to
`num_results`, and return a contact table. If `company_linkedin_url` was provided to
disambiguate a common name, prefer profiles whose company matches it.

## Outputs

`contacts.json` — array of `{name, title, company, company_domain, linkedin_url,
location, email, source}`. `email` is empty on both paths (use an enrichment skill to
reveal); LinkedIn-only contacts are returned rather than dropped.

## Credentials / env

- **Required:** none — the keyless serp path runs with no key.
- **Optional:** `APOLLO_API_KEY` (primary cheapest people search). `DROPCONTACT_API_KEY`
  and `PHANTOMBUSTER_API_KEY` (+ LinkedIn cookie) are deeper fallbacks the agent can invoke
  via their own skills when the two bundled paths under-deliver.

## Notes & edge cases

- Layer cheapest-first: run Apollo when keyed; only fall to serp when it isn't, or to fill
  a shortfall. Stop once `num_results` is met.
- The keyless serp path uses a public search endpoint that rate-limits; in production this
  maps to the Robomotion serp Search node + proxy. Space queries; expect lower precision.
- Proxy + throttle any LinkedIn scraping; respect provider rate limits.
- Return LinkedIn-only contacts rather than nothing when enrichment is absent.
