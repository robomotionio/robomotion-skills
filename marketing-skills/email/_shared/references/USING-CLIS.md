# Using the bundled CLIs (Robomotion runtime)

These integration guides and the CLIs in `${SHARED_DIR}/scripts/` are a
**shared library** for the marketing skills in this category. They run inside
the Hermes Agent sandbox via the `terminal` tool.

## Running a CLI

Each CLI is a zero-dependency Node.js script (Node 20 ships in the base image):

```bash
node ${SHARED_DIR}/scripts/<tool>.js <resource> <action> [--flags]
node ${SHARED_DIR}/scripts/<tool>.js            # no args -> usage
node ${SHARED_DIR}/scripts/<tool>.js <cmd> --dry-run   # preview request, creds masked
```

CLIs print **JSON to stdout** (pipe to `jq`); on failure they print
`{"error": "..."}` — never a traceback.

## Credentials

CLIs read credentials from **environment variables** (e.g. `RESEND_API_KEY`).
In Robomotion these are **bound from the Vault**, not a `.env` file — each skill
declares the vars it needs in its own `env.optional`. Reference the var normally
(`$RESEND_API_KEY`); the platform injects it. A skill works as pure knowledge
even with **no** keys bound — the CLI is an enhancement, never required.

**OAuth access tokens expire.** A few tools (GA4, Meta Ads, Google Ads, LinkedIn
Ads, Search Console, TikTok Ads) use short-lived access tokens. Bind a fresh
token; if a call returns 401, the token expired and must be refreshed
out-of-band. (No interactive OAuth runs in the sandbox.)

## Reference-only tools

Some guides describe tools that have **no bundled CLI** (MCP- or SDK-only, e.g.
HubSpot, Salesforce, Stripe, Twilio, introw, posthog). Use those guides as API
references — there is no `${SHARED_DIR}/scripts/<tool>.js` for them.

## Product context

Marketing skills look for `.agents/product-marketing.md` first. In the sandbox
this file is **session/working-dir scoped** (it persists within a run, not
across runs unless your working dir is mounted). The `product-marketing` skill
creates it; create or paste it at the start of a session if other skills need it.
