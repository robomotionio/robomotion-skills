---
name: site-content-catalog
description: Crawl a site's sitemap, sitemap index, and RSS/Atom feeds to build a complete content inventory — every page with URL, title, date, content type, and topic cluster — plus publishing-cadence stats and optional deep per-page analysis (word count, images, internal links, has-CTA). No API key. Foundation for SEO audits, content-gap analysis, and brand-voice extraction.
metadata:
  version: 1.0.1
  category: content
  type: capability
---

# Site Content Catalog

Build a content inventory for any domain — keyless. The script discovers pages via
`robots.txt` Sitemap directives, `sitemap.xml` (with sitemap-index recursion), common
sitemap locations, and RSS/Atom feeds; classifies each URL by content type; clusters by
URL slug; computes publishing cadence; and optionally deep-reads the top N pages for stats.

## When to use

- "Catalog all the content on [domain]."
- Before an SEO audit, content-gap analysis, or as `content-brief-factory`'s existing-
  coverage check.
- When you need funnel-stage mapping or publishing-pattern stats for a competitor/own site.

## How to run

Bundled script `scripts/site_catalog.py` (Python 3 stdlib only — no install):

```bash
python3 ${SKILL_DIR}/scripts/site_catalog.py --domain example.com --output ${WORKSPACE}/catalog.json
```

| Flag | Default | Meaning |
|---|---|---|
| `--domain` | (required) | `example.com` or `https://example.com`. |
| `--deep` | `0` | Deep-read the first N catalog URLs for page stats. |
| `--include-non-blog` | `true` | `false` keeps only blog-posts. |
| `--output` | `-` | JSON path (stdout if `-`). |

### Examples

```bash
# Full inventory
python3 ${SKILL_DIR}/scripts/site_catalog.py --domain example.com --output ${WORKSPACE}/catalog.json

# Inventory + deep stats on the first 10 pages
python3 ${SKILL_DIR}/scripts/site_catalog.py --domain example.com --deep 10 --output ${WORKSPACE}/catalog.json
```

## Outputs

JSON `{ summary, pages }`:

- `summary`: `{domain, total_pages, sitemap_found, by_type, by_topic, publishing_cadence}`
  (`sitemap_found: false` is itself a negative SEO signal).
- `pages[]`: `{url, title, date, type, topic_cluster, deep_analysis?}`. `deep_analysis`
  (when `--deep`) carries `{word_count, image_count, internal_link_count, has_cta}`.

The **agent** does the higher-order reasoning the contract calls for: LLM topic clustering
on large sites, classifying ambiguous URLs, and inferring each deep page's target keyword
and funnel stage (TOFU/MOFU/BOFU) from the stats. Produce the markdown summary table from
the JSON for the user.

## Credentials / env

- **Required:** none — sitemap/robots/feeds/HTTP are all keyless.
- **Optional:**
  - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — not used by the script (the agent is the model);
    listed only because the contract's LLM clustering/funnel-inference is the agent's job.
  - `APIFY_API_TOKEN` (paid, with a fallback) — If set → the agent orchestrates an Apify
    extractor for JS-heavy / sitemap-missing sites (better coverage when keyless discovery is
    blocked). If not set → fall back to the keyless sitemap/robots/feeds/HTTP crawl (the
    default). Route large crawls through Robomotion Proxy at the node.

## Notes & edge cases

- Sitemap.xml is the best source; a missing one is a (negative) SEO signal — reported as
  `sitemap_found: false`. RSS only surfaces recent posts, so feeds supplement, not replace.
- Dedup is by canonical URL (tracking params + fragment stripped).
- Deep analysis is capped to `--deep` to control time; the script throttles between pages.
- Type classification is rule-based on URL/title patterns; the agent should re-tag the
  handful of ambiguous URLs.
