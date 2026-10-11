# Second-scanner pass: the SaaS-founder roster's skills (2026-10-10)

Every skill the four new hub agents (Customer Support, Sales Development
Rep, Product Manager, Team Lead) load, scanned with Cisco's
`cisco-ai-skill-scanner` (1.0.2 or later, static analyzers, no LLM, no
credentials) in a throwaway `python:3.12-slim` podman container, in
addition to `scan-skills.py`. Every SKILL.md and script was also read.

| Skill | Group | Result |
|---|---|---|
| draft-response, ticket-triage, customer-escalation, kb-article, customer-research | knowledge-work-plugins (customer-support) | safe, INFO only (no license field in the manifest) |
| account-research, draft-outreach, call-prep | knowledge-work-plugins (sales) | safe, INFO only |
| write-spec, synthesize-research, roadmap-update, metrics-review, product-brainstorming, stakeholder-update | knowledge-work-plugins (product-management) | safe, INFO only |
| status-report, risk-assessment | knowledge-work-plugins (operations) | safe, INFO only |
| prospecting, cold-email, product-marketing | marketing-skills | safe, INFO only |
| scrapedo-search | robomotion-web (ours) | see below |

`scrapedo-search`, first pass: a CRITICAL prompt-injection match on a
defensive sentence that quoted an injection phrase (reworded), an
undeclared-network MEDIUM (the SKILL.md now declares it in
`compatibility`). What remains, reviewed and accepted:

- HIGH `CORRELATED_SENSITIVE_NETWORK_FLOW` and MEDIUM
  `DATA_EXFIL_NETWORK_REQUESTS` on `scripts/scrapedo.py`: the script reads
  `SCRAPEDO_TOKEN` and sends it to `https://api.scrape.do/` (a constant; no
  other host is ever contacted with it). That is the skill's job: Scrape.do
  takes its token only as a query parameter. In the sandbox the variable
  holds a vault placeholder that the credential proxy swaps on the way out,
  and the script never prints a URL it requested.
