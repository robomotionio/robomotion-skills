---
name: x-follower-scraper
description: Export public X audiences with Xquik X Follower Scraper on Apify. Compare followers, following, verified users, lists, communities, filters, and audience overlap.
metadata:
  version: 1.0.0
  category: research
  type: capability
---

# X Follower Scraper

Export public X audiences through one cost-gated Apify Actor.
Keep source attribution across accounts, lists, communities, and relations.

The skill uses [Xquik X Follower Scraper](https://apify.com/xquik/x-follower-scraper).
Its REST ID is `xquik~x-follower-scraper`.

## When To Use

- Export followers, following, or verified followers.
- Export list members or list subscribers.
- Export public community members.
- Apply audience filters before export.
- Compare audience overlap across several targets.

## Run

```bash
python3 ${SKILL_DIR}/scripts/x_followers.py --handle "<handle>" [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--handle` | none | X handle. Repeat for several targets. |
| `--user-id` | none | Numeric X user ID. Repeat as needed. |
| `--list-id` | none | Numeric X list ID. Repeat as needed. |
| `--community-id` | none | Numeric community ID. Repeat as needed. |
| `--url` | none | Public X target URL. Repeat as needed. |
| `--relation` | `followers` | Relation. Repeat for a multi-relation run. |
| `--max-profiles` | `100` | Run-wide result cap. |
| `--max-per-target` | none | Optional result cap for each target. |
| `--output-mode` | `compact` | Return `compact`, `full`, or `raw`. |
| `--dedupe-mode` | `first` | Use `none`, `first`, or `merge`. |
| `--min-followers` | none | Minimum follower count filter. |
| `--verified-only` | off | Keep verified profiles only. |
| `--bio-contains` | none | Case-insensitive biography filter. |
| `--location-contains` | none | Case-insensitive location filter. |
| `--estimate-only` | off | Preview limits without starting a run. |
| `--yes` | off | Confirm a paid Actor run. |
| `--max-cost-usd` | `1.00` | Hard maximum charge for one run. |
| `--apify-timeout` | `600` | Abort after this many seconds. |
| `--output` | `json` | Return `json` or `summary`. |

## Cost Gate

The script requires `--yes` before any paid run.
Estimate mode requires no token and starts no run.
The helper sends Apify a server-side maximum charge.
It also polls reported usage and every terminal status.
It requests an abort after a budget breach or timeout.

Check the live Actor pricing box before every run.
Apify platform usage may apply separately.
Start with a small result cap.

## Examples

Preview a follower export:

```bash
python3 ${SKILL_DIR}/scripts/x_followers.py \
  --handle "apify" --relation followers \
  --max-profiles 100 --estimate-only
```

Start the approved export:

```bash
python3 ${SKILL_DIR}/scripts/x_followers.py \
  --handle "apify" --relation followers \
  --max-profiles 100 --yes --max-cost-usd 0.50
```

Compare audience overlap:

```bash
python3 ${SKILL_DIR}/scripts/x_followers.py \
  --handle "apify" --handle "openai" \
  --relation followers --dedupe-mode merge \
  --max-per-target 100 --max-profiles 200 \
  --yes --max-cost-usd 1.00 --output summary
```

## Actor Input & Output

The Actor accepts handles, IDs, supported URLs, and repeated relations.
`maxItems` caps the entire run.
`maxItemsPerTarget` can balance depth across several targets.
Merge mode adds source targets, source relations, and overlap counts.
Compact mode returns normalized core fields.
Full and raw modes add optional source detail.

Diagnostic and run-report rows never become profile results.
Summaries rank audience overlap before follower count.

## Environment

`APIFY_API_TOKEN` is required for paid runs.
Keep it in the Robomotion vault binding.
Never expose credentials in output, logs, or URLs.

Collect only public data needed for the stated purpose.
Do not infer sensitive traits or bypass access controls.
Respect privacy rules and platform policies.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
