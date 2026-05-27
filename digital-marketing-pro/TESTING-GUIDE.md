# Digital Marketing Pro Testing Guide — v3.0.0

Complete testing guide for the Digital Marketing Pro plugin, including the v3.0 12-Part engagement methodology.

---

## Table of Contents

1. [Test Environment Setup](#1-test-environment-setup)
2. [Installation Tests](#2-installation-tests)
3. [Command Tests](#3-command-tests)
4. [Skill Tests](#4-skill-tests)
5. [Agent Tests](#5-agent-tests)
6. [Script Tests](#6-script-tests)
7. [Hook Tests](#7-hook-tests)
8. [MCP Connector Tests](#8-mcp-connector-tests)
9. [Edge Cases & Error Scenarios](#9-edge-cases--error-scenarios)
10. [Regression Checklist](#10-regression-checklist)
11. [Test Priority Order](#11-test-priority-order)
12. [v3.0 Engagement Methodology Tests](#12-v30-engagement-methodology-tests)

---

## 1. Test Environment Setup

### Prerequisites

- **Claude Cowork** or **Claude Code** with plugin support
- At least one brand profile set up (or plan to set up during testing)

### Installation Sources

| Method | URL |
|--------|-----|
| **Marketplace** | `https://github.com/indranilbanerjee/neels-plugins.git` |
| **Direct URL** | `https://github.com/indranilbanerjee/digital-marketing-pro.git` |

### Pre-Test Cleanup

```
# Clear plugin cache (if reinstalling)
rm -rf ~/.claude/plugins/cache/

# Clear brand data (for fresh brand setup test)
# WARNING: Only do this if you want to start fresh
rm -rf ~/.claude-marketing/
```

### Test Brands to Use

| Brand Name | Industry | Purpose |
|-----------|----------|---------|
| "TestBrand Alpha" | B2B SaaS | Primary test brand |
| "HealthFirst Clinic" | Healthcare | Regulated industry test |
| "LocalBiz Cafe" | Local business | Local SEO test |
| "GlobalCorp" | Enterprise | Multi-market/multilingual test |

---

## 2. Installation Tests

### 2.1 Marketplace Installation

**Steps:**
1. In Claude Cowork, go to Settings > Plugins > Add Marketplace
2. Enter URL: `https://github.com/indranilbanerjee/neels-plugins.git`
3. Install `digital-marketing-pro`

**Expected Results:**
- [ ] Marketplace loads without errors
- [ ] DM Pro listed with version 2.5.0
- [ ] Description mentions "25 specialist agents, 10 commands, 149 skills, 68 Python scripts, 14 HTTP connectors"
- [ ] Installation completes without rollback
- [ ] No "Host key verification failed" error (uses HTTPS, not SSH)

**If installation fails:**
- Check `~/.claude/logs/main.log` for `VMCLIRunner` errors
- Look for `virtiofs mount: Plan9 mount failed` (VM instability — retry)
- Look for `EXDEV` errors (known bug #25444)
- Clear `~/.claude/plugins/cache/` and retry

### 2.2 Direct URL Installation

**Steps:**
1. Settings > Plugins > Add Plugin
2. Enter URL: `https://github.com/indranilbanerjee/digital-marketing-pro.git`

**Expected:** Same results as marketplace installation

### 2.3 Session Start Verification

**Test:** Start a new session after installation

**Expected Results:**
- [ ] SessionStart hook fires — setup.py runs `--check-deps --summary`
- [ ] No Python errors or tracebacks
- [ ] 10 top-level commands visible in Customize panel: brand-setup, campaign-plan, seo-audit, content-engine, performance-report, competitor-analysis, email-sequence (v2.5), engagement (v3.0), check + status (v3.2)
- [ ] 149 skills visible in Skills section (141 atomic + 6 v3.0 methodology + 2 v3.2 quality-and-status)
- [ ] 25 agents registered (check for no frontmatter errors in logs)

### 2.4 Plugin Structure Verification

**Expected file counts:**
- [ ] `agents/` — 25 agent .md files (all with YAML frontmatter)
- [ ] `commands/` — 7 command .md files
- [ ] `skills/` — 149 skill directories, each with SKILL.md (141 atomic + 6 v3.0 methodology + 2 v3.2 quality-and-status)
- [ ] `scripts/` — 68 Python scripts (65 v2.x + engagement-state.py v3.0 + dm-status.py + auto-save-insight.py v3.2)
- [ ] `.mcp.json` — 14 HTTP connectors
- [ ] `.mcp.json.example` — 68 npx servers (opt-in for Claude Code)
- [ ] `hooks/hooks.json` — 4 hook events
- [ ] `docs/` — 11 documentation guides
- [ ] `CONNECTORS.md` — Connector reference with `~~category` placeholders

---

## 3. Command Tests

Test all 10 top-level commands visible in the Customize panel (7 v2.5 commands + /digital-marketing-pro:engagement v3.0 + /digital-marketing-pro:check + /digital-marketing-pro:status v3.2).

### 3.1 `/brand-setup`

**Prompt:** "Set up brand: TestBrand Alpha, a B2B SaaS project management tool targeting mid-market companies"

**Expected:**
- [ ] Brand profile created with voice, audience, competitors
- [ ] Files saved to `~/.claude-marketing/TestBrand Alpha/`
- [ ] Context engine loads brand for subsequent commands
- [ ] Industry mapped correctly

### 3.2 `/campaign-plan`

**Prompt:** "Create a Q2 2026 campaign plan for TestBrand Alpha with $50K budget"

**Expected:**
- [ ] Multi-channel plan (SEO, paid, social, email, content)
- [ ] Budget allocation across channels with percentages
- [ ] Timeline with milestones
- [ ] KPI targets per channel
- [ ] Audience segmentation
- [ ] Competitive positioning

### 3.3 `/seo-audit`

**Prompt:** "Run SEO audit for testbrandalpha.com"

**Expected:**
- [ ] Technical health check (Core Web Vitals, crawlability)
- [ ] On-page analysis (meta tags, headings, content)
- [ ] Content gaps identified
- [ ] E-E-A-T assessment
- [ ] Link profile analysis
- [ ] Competitor benchmarking
- [ ] Prioritized recommendations with effort/impact scores

### 3.4 `/content-engine`

**Prompt:** "Write a LinkedIn ad copy for TestBrand Alpha's new AI feature"

**Expected:**
- [ ] Platform-specific ad copy (LinkedIn specs)
- [ ] Brand voice maintained
- [ ] CTA included
- [ ] Character limits respected
- [ ] Multiple variations offered

### 3.5 `/performance-report`

**Prompt:** "Generate monthly performance report for January 2026"

**Expected:**
- [ ] KPI tracking dashboard
- [ ] Trend analysis (MoM, YoY)
- [ ] Anomaly detection
- [ ] Channel-by-channel breakdown
- [ ] Recommendations

### 3.6 `/competitor-analysis`

**Prompt:** "Analyze competitors: Asana, Monday.com, ClickUp"

**Expected:**
- [ ] Content strategy teardown per competitor
- [ ] SEO gap analysis
- [ ] Paid ad analysis
- [ ] Social media benchmarking
- [ ] Pricing/positioning comparison
- [ ] Opportunities matrix

### 3.7 `/email-sequence`

**Prompt:** "Create a 5-email onboarding sequence for new trial users"

**Expected:**
- [ ] 5 emails with subject lines and body copy
- [ ] Timing/cadence recommendations
- [ ] Segmentation rules
- [ ] Deliverability guidance
- [ ] A/B test suggestions for subject lines

---

## 4. Skill Tests

DM Pro has 149 skills (141 atomic + 6 v3.0 methodology skills + 2 v3.2 quality-and-status skills). Test a representative sample from each module.

### Context & Setup Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:help` | (no args) | Shows getting started guide, commands by category, examples, troubleshooting |
| `/digital-marketing-pro:integrations` | (no args) | Shows all 14 HTTP connectors + available connectors by category |
| `/digital-marketing-pro:connect notion` | "Set up Notion" | Step-by-step OAuth instructions |
| `/digital-marketing-pro:switch-brand` | "Switch to HealthFirst" | Brand context changes, subsequent commands use new brand |
| `/digital-marketing-pro:context-engine` | "Load TestBrand Alpha" | Brand profile loaded, context confirmed |
| `/digital-marketing-pro:add-integration` | "Connect my CRM" | Custom connector setup guide |

### SEO & Content Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:keyword-research` | "keyword research for 'AI project management'" | Clusters, search volume, difficulty, intent |
| `/digital-marketing-pro:content-brief` | "brief for 'remote team management'" | Keyword data, outline, competitor analysis |
| `/digital-marketing-pro:tech-seo-audit` | "audit testbrandalpha.com" | Core Web Vitals, crawlability, schema markup |
| `/digital-marketing-pro:content-calendar` | "Q2 content calendar" | Monthly plan with topics, types, channels |
| `/digital-marketing-pro:aeo-audit` | "how does our brand appear in AI answers?" | AI visibility assessment across engines |
| `/digital-marketing-pro:content-decay-scan` | "scan our blog for decay" | Identifies outdated content, stale stats |
| `/digital-marketing-pro:entity-audit` | "audit brand entity consistency" | Knowledge graph, structured data review |
| `/digital-marketing-pro:local-seo-audit` | "audit local SEO for HealthFirst" | GBP, NAP consistency, local citations |
| `/digital-marketing-pro:hreflang-check` | "check hreflang for globalcorp.com" | Tag validation, coverage gaps |

### Paid Advertising & Social Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:media-plan` | "media plan for $30K Google+Meta budget" | Budget split, targeting, bid strategy, timeline |
| `/digital-marketing-pro:ad-creative` | "3 LinkedIn ad variations" | Platform-specific specs, scored variants |
| `/digital-marketing-pro:social-strategy` | "social strategy for LinkedIn and Twitter" | Platform-specific playbooks |
| `/digital-marketing-pro:ab-test-plan` | "A/B test for landing page headline" | Sample size, duration, hypothesis, significance |
| `/digital-marketing-pro:launch-ad-campaign` | "launch Google Ads for product launch" | Campaign structure, targeting, creative |
| `/digital-marketing-pro:retargeting-strategy` | "retargeting plan for trial abandoners" | Audience segments, frequency caps |
| `/digital-marketing-pro:creative-health` | "check creative fatigue" | Fatigue prediction, refresh recommendations |

### Analytics & Reporting Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:analytics-insights` | "KPI framework for SaaS" | Metrics, targets, dashboard design |
| `/digital-marketing-pro:roi-calculator` | "ROI for $50K campaign with 200 leads" | Math correct, assumptions documented |
| `/digital-marketing-pro:budget-optimizer` | "optimize $100K across 5 channels" | Allocation with reasoning, diminishing returns |
| `/digital-marketing-pro:anomaly-scan` | "check for performance anomalies" | Detection methodology, threshold logic |
| `/digital-marketing-pro:attribution-model` | "set up multi-touch attribution" | Model selection, implementation guidance |
| `/digital-marketing-pro:cohort-analysis` | "analyze Q1 acquisition cohorts" | Cohort tables, retention curves |
| `/digital-marketing-pro:performance-check` | "pull live metrics" | Connector status, data freshness |

### Growth & CRO Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:funnel-audit` | "audit our signup funnel" | Drop-off analysis, benchmark comparison |
| `/digital-marketing-pro:landing-page-audit` | "audit our pricing page" | Above-fold, CTA, form, mobile scores |
| `/digital-marketing-pro:growth-engineering` | "design a referral program" | Viral loop, incentives, K-factor |
| `/digital-marketing-pro:cro` | "conversion optimization for checkout" | Hypotheses, test plan, priority score |
| `/digital-marketing-pro:loop-detect` | "find growth loops in our product" | Loop identification, reinforcement analysis |
| `/digital-marketing-pro:pricing-test` | "test pricing strategies" | Willingness-to-pay, conjoint analysis |

### PR & Influencer Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:pr-pitch` | "pitch for product launch" | Pitch template, journalist targets, timing |
| `/digital-marketing-pro:influencer-brief` | "influencer campaign for SaaS" | Discovery criteria, brief, FTC compliance |
| `/digital-marketing-pro:crisis-response` | "handle negative PR about data breach" | Response framework, messaging, channels |
| `/digital-marketing-pro:digital-pr` | "digital PR for link building" | Outreach strategy, asset creation |

### Email & Automation Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:email-sequence` | "win-back sequence for churned users" | Timing, copy, segmentation, triggers |
| `/digital-marketing-pro:send-email-campaign` | "send newsletter to subscribers" | MCP connector check, preview, approval |
| `/digital-marketing-pro:marketing-automation` | "automation workflow for lead nurture" | Trigger logic, branching, scoring |

### Agency Operations Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:client-report` | "client report for January" | Client-facing format, branded |
| `/digital-marketing-pro:exec-summary` | "executive summary for Q4" | C-suite ready, strategic insights |
| `/digital-marketing-pro:agency-dashboard` | "portfolio dashboard" | Multi-client view, aggregate metrics |
| `/digital-marketing-pro:client-onboarding` | "onboard new client FitnessCo" | Kickoff checklist, data requirements |
| `/digital-marketing-pro:team-assign` | "assign SEO tasks to team" | Task breakdown, assignments, deadlines |
| `/digital-marketing-pro:qbr-plan` | "prepare QBR for TestBrand" | Agenda, data requirements, insights |

### Intelligence & Memory Module

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:save-knowledge` | "save that LinkedIn ads work best for us" | Learning stored persistently |
| `/digital-marketing-pro:recall` | "what worked for our LinkedIn campaigns?" | Relevant learnings retrieved |
| `/digital-marketing-pro:search-knowledge` | "find campaign results from Q1" | Search returns relevant entries |
| `/digital-marketing-pro:intelligence-report` | "full intelligence briefing" | Compound learnings, pattern recognition |
| `/digital-marketing-pro:learn` | "SEO traffic grew 40% after content refresh" | Insight stored with context |

### Advanced Skills

| Skill | Test Prompt | Key Checks |
|-------|-------------|------------|
| `/digital-marketing-pro:simulate` | "simulate revenue impact of doubling ad spend" | Revenue model, assumptions, scenarios |
| `/digital-marketing-pro:what-if` | "what if we cut social media budget by 50%?" | Scenario comparison, trade-offs |
| `/digital-marketing-pro:focus-group` | "test messaging with target audience" | Synthetic personas, feedback, insights |
| `/digital-marketing-pro:journey-design` | "design onboarding journey" | Cross-channel touchpoints, timing |
| `/digital-marketing-pro:market-weather` | "marketing weather report" | Macro signals, timing recommendations |
| `/digital-marketing-pro:dark-funnel` | "map invisible buyer journey" | Unmeasured touchpoints, heuristics |

---

## 5. Agent Tests

DM Pro has 25 specialist agents. Verify they register correctly and respond when invoked by skills.

### Agent Registration

**Test:** After installation, verify all 25 agents are listed

**Expected agents (all with valid YAML frontmatter — `name` + `description`):**

| # | Agent | Primary Skills |
|---|-------|---------------|
| 1 | agency-operations | `/digital-marketing-pro:agency-dashboard`, `/digital-marketing-pro:client-report`, `/digital-marketing-pro:team-assign` |
| 2 | analytics-analyst | `/digital-marketing-pro:analytics-insights`, `/digital-marketing-pro:anomaly-scan`, `/digital-marketing-pro:attribution-model` |
| 3 | brand-guardian | `/digital-marketing-pro:eval-content`, brand compliance checks |
| 4 | competitive-intel | `/digital-marketing-pro:competitor-analysis`, `/digital-marketing-pro:share-of-voice` |
| 5 | competitor-intelligence | `/digital-marketing-pro:competitor-monitor`, `/digital-marketing-pro:competitor-alerts` |
| 6 | content-creator | `/digital-marketing-pro:content-engine`, `/digital-marketing-pro:content-brief`, `/digital-marketing-pro:content-repurpose` |
| 7 | crm-manager | `/digital-marketing-pro:crm-sync`, `/digital-marketing-pro:pipeline-update`, `/digital-marketing-pro:lead-import` |
| 8 | cro-specialist | `/digital-marketing-pro:cro`, `/digital-marketing-pro:landing-page-audit`, `/digital-marketing-pro:funnel-audit` |
| 9 | email-specialist | `/digital-marketing-pro:email-sequence`, `/digital-marketing-pro:send-email-campaign` |
| 10 | execution-coordinator | `/digital-marketing-pro:launch-ad-campaign`, `/digital-marketing-pro:publish-blog`, `/digital-marketing-pro:schedule-social` |
| 11 | growth-engineer | `/digital-marketing-pro:growth-engineering`, `/digital-marketing-pro:loop-detect` |
| 12 | influencer-manager | `/digital-marketing-pro:influencer-brief`, `/digital-marketing-pro:influencer-creator` |
| 13 | intelligence-curator | `/digital-marketing-pro:intelligence-report`, `/digital-marketing-pro:learn` |
| 14 | journey-orchestrator | `/digital-marketing-pro:journey-design`, `/digital-marketing-pro:funnel-architect` |
| 15 | localization-specialist | `/digital-marketing-pro:translate-content`, `/digital-marketing-pro:localize-campaign` |
| 16 | market-intelligence | `/digital-marketing-pro:market-weather`, `/digital-marketing-pro:emerging-channels` |
| 17 | marketing-scientist | `/digital-marketing-pro:simulate`, `/digital-marketing-pro:attribution-report` |
| 18 | marketing-strategist | `/digital-marketing-pro:campaign-plan`, `/digital-marketing-pro:launch-plan` |
| 19 | media-buyer | `/digital-marketing-pro:media-plan`, `/digital-marketing-pro:paid-advertising`, `/digital-marketing-pro:budget-tracker` |
| 20 | memory-manager | `/digital-marketing-pro:save-knowledge`, `/digital-marketing-pro:recall`, `/digital-marketing-pro:sync-memory` |
| 21 | performance-monitor-agent | `/digital-marketing-pro:performance-check`, `/digital-marketing-pro:anomaly-scan` |
| 22 | pr-outreach | `/digital-marketing-pro:pr-pitch`, `/digital-marketing-pro:digital-pr`, `/digital-marketing-pro:crisis-response` |
| 23 | quality-assurance | `/digital-marketing-pro:eval-suite`, `/digital-marketing-pro:quality-report` |
| 24 | seo-specialist | `/digital-marketing-pro:seo-audit`, `/digital-marketing-pro:keyword-research`, `/digital-marketing-pro:tech-seo-audit` |
| 25 | social-media-manager | `/digital-marketing-pro:social-strategy`, `/digital-marketing-pro:schedule-social` |

**Checks:**
- [ ] All 25 agents have valid frontmatter (`name` in kebab-case + `description`)
- [ ] No agent registration errors in installation logs
- [ ] Agent names match their file names (e.g., `agency-operations.md` has `name: agency-operations`)

---

## 6. Script Tests

DM Pro has 68 Python scripts (65 v2.x + engagement-state.py v3.0 + dm-status.py + auto-save-insight.py v3.2). Test key scripts that are critical to plugin operation.

### 6.1 Core Scripts

| Script | Trigger | Test | Expected |
|--------|---------|------|----------|
| `setup.py` | SessionStart hook | Start new session | Checks dependencies, prints summary, no errors |
| `connector-status.py` | `/digital-marketing-pro:integrations` | Run integrations command | Lists 14 HTTP + available connectors by category |
| `campaign-tracker.py` | SessionEnd hook | End a session after marketing work | Session insights saved |
| `guidelines-manager.py` | Brand compliance | Set up brand with guidelines | Rules stored and enforced |

### 6.2 Analytics & Reporting Scripts

| Script | Test | Expected |
|--------|------|----------|
| `roi-calculator.py` | Calculate campaign ROI | Correct math, clear assumptions |
| `budget-optimizer.py` | Optimize channel allocation | Allocation with diminishing returns |
| `revenue-simulator.py` | Simulate revenue scenarios | Model outputs, sensitivity analysis |
| `performance-monitor.py` | Check campaign health | Metrics collected, anomalies flagged |

### 6.3 Content & SEO Scripts

| Script | Test | Expected |
|--------|------|----------|
| `content-scorer.py` | Score content quality | Multi-dimension scoring |
| `brand-voice-scorer.py` | Score brand voice alignment | Voice deviation detection |
| `headline-analyzer.py` | Analyze headline effectiveness | Emotional, power, uncommon word scores |
| `keyword-clusterer.py` | Cluster keywords | Groups by intent and topic |
| `schema-generator.py` | Generate schema markup | Valid JSON-LD output |
| `readability-analyzer.py` | Check readability grade | Flesch-Kincaid, grade level |

### 6.4 Compliance & Safety Scripts

| Script | Test | Expected |
|--------|------|----------|
| `hallucination-detector.py` | Scan content for hallucinations | Catches unattributed stats, placeholder URLs |
| `claim-verifier.py` | Verify marketing claims | Evidence-based verification |
| `spam-score-checker.py` | Check email spam score | Score with improvement suggestions |
| `approval-manager.py` | Manage content approvals | Approval workflow tracking |

### 6.5 Social & Email Scripts

| Script | Test | Expected |
|--------|------|----------|
| `social-post-formatter.py` | Format for multiple platforms | Platform-specific output |
| `email-preview.py` | Preview email rendering | HTML preview, client compatibility |
| `email-subject-tester.py` | Test subject line effectiveness | Open rate prediction |
| `utm-generator.py` | Generate UTM parameters | Valid UTM strings, QR code support |

### 6.6 Competitive Intelligence Scripts

| Script | Test | Expected |
|--------|------|----------|
| `competitor-tracker.py` | Track competitor changes | Change detection, alerts |
| `competitor-scraper.py` | Scrape competitor content | Content extraction, structure analysis |
| `narrative-mapper.py` | Map competitive narratives | Positioning landscape |
| `ai-visibility-checker.py` | Check AI search visibility | AI engine response analysis |

---

## 7. Hook Tests

DM Pro has 4 hook events.

### 7.1 SessionStart

**Test:** Start a new session

**Expected:**
- [ ] setup.py runs with `--check-deps --summary`
- [ ] Plugin info printed (version, agent count, skill count)
- [ ] No Python errors or tracebacks

### 7.2 PreToolUse — Write/Edit (Brand Compliance + Hallucination Detection)

**Test:** Generate marketing content that triggers Write/Edit

**Expected checks performed by hook:**
- [ ] File path validation (prevents writing outside marketing directories)
- [ ] Brand voice alignment check
- [ ] Industry compliance verification
- [ ] FTC disclosure check (for sponsored/affiliate content)
- [ ] Hallucination detection:
  - [ ] Unattributed statistics/percentages
  - [ ] Placeholder URLs (example.com, your-site.com)
  - [ ] Unsupported superlatives (#1, best, leading)
  - [ ] Fabricated citations

**Test with intentionally bad content:**

| Bad Content | Expected Detection |
|-------------|-------------------|
| "87% of marketers agree..." (no source) | Flagged — unattributed stat |
| "Visit https://example.com/pricing" | Flagged — placeholder URL |
| "The #1 marketing platform" | Flagged — unsupported superlative |

### 7.3 PreToolUse — MCP Tool Calls (External Platform Safety)

**Test:** Invoke skills that write to external platforms

**Expected checks performed by hook:**
- [ ] Write operations to external platforms require explicit user approval
- [ ] Budget verification before ad spend operations
- [ ] Platform verification before publishing
- [ ] Ad campaigns: budget within brand's stated range
- [ ] Email/SMS: list size and consent compliance checked
- [ ] CRM writes: prevents record overwrites without confirmation

**Test scenarios:**

| Action | Expected |
|--------|----------|
| Publish blog post | Approval prompt before external write |
| Launch ad campaign | Budget verification before platform call |
| Send email campaign | List size and consent check |
| Update CRM records | Overwrite confirmation required |

### 7.4 SessionEnd

**Test:** End a session after doing marketing work

**Expected:**
- [ ] Session insights saved via campaign-tracker.py
- [ ] Guideline violations logged (if any were flagged during session)
- [ ] Key takeaways formatted for review
- [ ] Brand update instructions if learnings discovered

---

## 8. MCP Connector Tests

### 8.1 All 14 HTTP Connectors

| # | Connector | URL | Test Action | Expected |
|---|-----------|-----|------------|----------|
| 1 | **Slack** | `mcp.slack.com/mcp` | Send notification | Message delivered |
| 2 | **Canva** | `mcp.canva.com/mcp` | Generate design | Design created |
| 3 | **Figma** | `mcp.figma.com/mcp` | Access design file | Design data retrieved |
| 4 | **HubSpot** | `mcp.hubspot.com/anthropic` | Read CRM contacts | Contact list returned |
| 5 | **Amplitude** | `mcp.amplitude.com/mcp` | Query analytics | Event data returned |
| 6 | **Notion** | `mcp.notion.com/mcp` | Read a page | Content retrieved |
| 7 | **Ahrefs** | `api.ahrefs.com/mcp/mcp` | Get backlink data | Link profile returned |
| 8 | **Similarweb** | `mcp.similarweb.com` | Get traffic data | Traffic estimates returned |
| 9 | **Klaviyo** | `mcp.klaviyo.com/mcp` | List email campaigns | Campaign data returned |
| 10 | **Google Calendar** | `calendarmcp.googleapis.com/mcp/v1` | Create event | Calendar event created |
| 11 | **Gmail** | `gmailmcp.googleapis.com/mcp/v1` | Draft email | Email draft created |
| 12 | **Stripe** | `mcp.stripe.com/` | Get revenue data | Payment data returned |
| 13 | **Asana** | `mcp.asana.com/sse` | List tasks | Task list returned |
| 14 | **Webflow** | `mcp.webflow.com/sse` | Publish content | Content appears in CMS |

**Note:** Each connector requires OAuth authorization on first use. The Claude platform handles this. Not all testers will have accounts for all services.

### 8.2 Connector Categories

Verify connectors map to the right workflow categories per CONNECTORS.md:

| Category | Connectors | Skills Affected |
|----------|------------|----------------|
| Communication | Slack | `/digital-marketing-pro:send-notification` |
| Design | Canva, Figma | `/digital-marketing-pro:ad-creative`, design assets |
| CRM | HubSpot | `/digital-marketing-pro:crm-sync`, `/digital-marketing-pro:lead-import`, `/digital-marketing-pro:pipeline-update` |
| Analytics | Amplitude | `/digital-marketing-pro:analytics-insights`, `/digital-marketing-pro:performance-check` |
| Knowledge base | Notion | `/digital-marketing-pro:save-knowledge`, brand docs |
| SEO | Ahrefs, Similarweb | `/digital-marketing-pro:seo-audit`, `/digital-marketing-pro:keyword-research`, `/digital-marketing-pro:competitor-analysis` |
| Email marketing | Klaviyo | `/digital-marketing-pro:send-email-campaign` |
| Calendar | Google Calendar | `/digital-marketing-pro:content-calendar` |
| Email | Gmail | `/digital-marketing-pro:send-report`, draft delivery |
| Payments | Stripe | `/digital-marketing-pro:roi-calculator`, revenue data |
| Project management | Asana | `/digital-marketing-pro:team-assign` |
| CMS | Webflow | `/digital-marketing-pro:publish-blog` |

### 8.3 Graceful Degradation

**Test:** Invoke a skill that uses a connector that's NOT authorized/connected

**Expected:**
- [ ] Skill doesn't crash
- [ ] Clear message about which connector is needed
- [ ] Instructions on how to connect it (or suggest `/digital-marketing-pro:connect <name>`)
- [ ] Fallback behavior (manual data input, alternative approach, or skip)
- [ ] Verify-then-guide pattern (never silent failure)

### 8.4 Platform-Level Integrations

**Test:** Verify Google Drive/Docs work through Claude platform integration (Settings > Integrations)

**Note:** Google Analytics, Google Ads, Meta Ads, LinkedIn Ads, and Salesforce have NO HTTP MCP endpoints. These work through skill-guided manual workflows or npx servers (Claude Code only).

---

## 9. Edge Cases & Error Scenarios

### 9.1 Empty/Minimal Input

| Test | Expected |
|------|----------|
| `/digital-marketing-pro:keyword-research` (no keyword) | Asks for keyword/topic |
| `/digital-marketing-pro:campaign-plan` (no details) | Asks for brand, budget, goals |
| `/digital-marketing-pro:seo-audit` (no URL) | Asks for website URL |
| `/digital-marketing-pro:media-plan` (no budget) | Asks for budget and channels |
| `/digital-marketing-pro:email-sequence` (no context) | Asks for goal, audience, trigger |

### 9.2 Brand Context

| Test | Expected |
|------|----------|
| Run skill without active brand | Asks to set up brand or select existing |
| Switch brand mid-session | Context updates, subsequent skills use new brand |
| Run agency skills with single brand | Works with single-client mode, no multi-client features |
| Run multi-client dashboard with 3+ brands | Aggregates across all configured brands |

### 9.3 Special Characters

| Test | Expected |
|------|----------|
| Brand name with apostrophe: "O'Reilly Media" | No path or query issues |
| Competitor URL with special chars | URL encoding handled |
| Keywords with unicode characters | No encoding errors |

### 9.4 Network Failures

| Test | Expected |
|------|----------|
| Run SEO audit without internet | Graceful error, suggests manual data |
| MCP connector timeout | Shows error, suggests retry or fallback |
| Ahrefs/Similarweb returns no data | Skill completes with available data, notes gaps |

### 9.5 Large Data

| Test | Expected |
|------|----------|
| Keyword research with 500+ keywords | Clusters efficiently, no timeout |
| Competitor analysis with 10 competitors | Handles all, may take longer |
| Email sequence with 20 emails | Generates all with consistent quality |
| Campaign plan with $1M+ budget | Handles large numbers, proper formatting |

### 9.6 Conflicting Instructions

| Test | Expected |
|------|----------|
| Brand guidelines say "formal" but user asks for "casual" | Asks for clarification, notes conflict |
| Campaign budget exceeds brand's stated range | Warning about budget mismatch |
| Publish to platform not in brand's approved list | Flags deviation from brand config |

---

## 10. Regression Checklist

Run this after any changes to verify nothing is broken.

### Core Functionality

- [ ] Session start hook fires with setup.py output
- [ ] Brand setup creates profile at `~/.claude-marketing/{brand}/`
- [ ] Context engine loads brand correctly
- [ ] Brand switch works between profiles

### Commands

- [ ] All 10 commands appear in Customize panel (7 v2.5 + /digital-marketing-pro:engagement v3.0 + /digital-marketing-pro:check + /digital-marketing-pro:status v3.2)
- [ ] `/brand-setup` completes full setup flow
- [ ] `/campaign-plan` generates multi-channel plan with budget
- [ ] `/seo-audit` produces comprehensive report
- [ ] `/content-engine` respects brand voice and platform specs
- [ ] `/performance-report` includes all KPI sections
- [ ] `/competitor-analysis` covers all dimensions
- [ ] `/email-sequence` has correct cadence and segmentation

### Skills

- [ ] `/digital-marketing-pro:help` shows complete, accurate information
- [ ] `/digital-marketing-pro:integrations` shows 14 HTTP connectors with correct status
- [ ] All 149 skills respond to invocation (spot check at minimum)
- [ ] Skills handle missing connectors gracefully

### Skill Platform Features

- [ ] Argument hints show in Skills UI when typing `/digital-marketing-pro:` (spot check 3-5 skills)
- [ ] Execution skills (e.g., `/digital-marketing-pro:publish-blog`, `/digital-marketing-pro:send-email-campaign`) cannot be triggered by Claude without explicit user invocation
- [ ] `/digital-marketing-pro:help` has `name: help` in frontmatter (was missing pre-v2.5.1)
- [ ] `skills/campaign-plan/evals/evals.json` exists and is valid JSON with 3 test cases
- [ ] `skills/seo-audit/evals/evals.json` exists and is valid JSON with 2 test cases
- [ ] `skills/content-engine/evals/evals.json` exists and is valid JSON with 3 test cases

### Hooks

- [ ] SessionStart hook fires without errors
- [ ] Brand compliance hook fires on content writes
- [ ] MCP write approval hook fires on external platform calls
- [ ] SessionEnd hook saves session insights

### Versioning Consistency

- [ ] `plugin.json` version = 2.5.1
- [ ] `hooks.json` version string matches
- [ ] `README.md` version = 2.5.1
- [ ] Marketplace entry version = 2.5.1
- [ ] `25 agents` in all descriptions
- [ ] `149 skills` in all descriptions (141 atomic + 6 v3.0 methodology + 2 v3.2 quality-and-status)
- [ ] `10 commands` in all descriptions (7 v2.5 + /digital-marketing-pro:engagement v3.0 + /digital-marketing-pro:check + /digital-marketing-pro:status v3.2)
- [ ] `68 scripts` in all descriptions (65 v2.x + engagement-state.py + dm-status.py + auto-save-insight.py)
- [ ] `14 HTTP connectors` in all descriptions

---

## 11. Test Priority Order

If time is limited, test in this order:

| Priority | Test | Section | Why |
|----------|------|---------|-----|
| 1 | Installation | 2 | Nothing else works without this |
| 2 | `/brand-setup` command | 3.1 | Foundation for all other tests |
| 3 | `/campaign-plan` command | 3.2 | Validates core strategic skill |
| 4 | `/seo-audit` command | 3.3 | Validates technical analysis |
| 5 | `/digital-marketing-pro:help` and `/digital-marketing-pro:integrations` | 4 | Validates help accuracy and connector status |
| 6 | Hook tests (all 4 events) | 7 | Validates compliance guardrails |
| 7 | Key skills (one per module) | 4 | Validates breadth of skill coverage |
| 8 | MCP connectors | 8 | Requires external service accounts |
| 9 | Agent registration | 5 | Verify all 25 registered |
| 10 | Edge cases | 9 | Robustness testing |
| 11 | v3.0 engagement methodology smoke test | 12 | Validates the methodology orchestration end-to-end |

---

## 12. v3.0 Engagement Methodology Tests

The v3.0 release introduces the 12-Part engagement methodology. The new components require their own smoke tests.

### 12.1 engagement-state.py CLI smoke test

This test does not require Claude — it validates the persistence engine directly. Run from a shell:

```bash
# Set up an isolated test workspace
export CLAUDE_PLUGIN_DATA="$(mktemp -d)"
cd /path/to/digital-marketing-pro

# Test 1: Initialise an engagement
python scripts/engagement-state.py init --brand "test-brand" --id "2026-q2"
# Expect: {"status": "ok", "action": "initialised", ...}

# Test 2: Status returns the initialised engagement
python scripts/engagement-state.py status --brand "test-brand" --id "2026-q2"
# Expect: current_part = "1", parts[1].status = "in_progress"

# Test 3: Stone fact intake
python scripts/engagement-state.py add-stone-fact --brand "test-brand" --id "2026-q2" \
  --fact-json '{"category":"company","fact":"Founded 2018","source":"client statement"}'
# Expect: {"status": "ok", "action": "stone_fact_added", "id": "stone-001"}

# Test 4: Opinion hypothesis intake
python scripts/engagement-state.py add-opinion --brand "test-brand" --id "2026-q2" \
  --hypothesis-json '{"category":"positioning","hypothesis":"H","client_evidence":"E","research_question":"Q"}'
# Expect: {"status": "ok", "action": "opinion_added", "id": "opinion-001"}

# Test 5: Mark Part 1 complete; current_part should auto-advance to 2
python scripts/engagement-state.py mark-part-completed --brand "test-brand" --id "2026-q2" --part 1
# Expect: {"status": "ok", "action": "part_completed", "part": "1", "next_part": "2"}

# Test 6: Decision Matrix
python scripts/engagement-state.py decision-matrix --brand "test-brand" --id "2026-q2" \
  --triggers "competitors_changed,positioning_changed"
# Expect: triggered_reruns = ["3.1", "3.2", "3.3", "3.4", "4.1", "4.2"]

# Test 7: Update-Back version bump
python scripts/engagement-state.py bump-version --brand "test-brand" --id "2026-q2" \
  --doc 3.1 --reason "test version bump"
# Expect: {"status": "ok", "version": "v1.0", ...}

# Test 8: File tree shows the engagement structure
python scripts/engagement-state.py file-tree --brand "test-brand" --id "2026-q2"
# Expect: list of paths under the engagement directory

# Test 9: List engagements finds the test engagement
python scripts/engagement-state.py list-engagements
# Expect: at least one engagement with brand="test-brand", engagement_id="2026-q2"

# Cleanup
rm -rf "$CLAUDE_PLUGIN_DATA"
```

All tests must return `status: ok` (or matching expectations). Any non-zero exit code indicates a failure.

### 12.2 Engagement command smoke test (in Claude Code or Cowork)

Within a Claude session with the plugin installed:

| # | Test | Expected behaviour |
|---|------|-------------------|
| 1 | `/digital-marketing-pro:engagement start <brand-slug> 2026-test` | Engagement directory created; Stone vs Opinion intake walked |
| 2 | `/digital-marketing-pro:engagement status` | Status table shown; current part = 1 |
| 3 | `/digital-marketing-pro:engagement file-tree <brand-slug> 2026-test` | Directory tree printed with all 12 part subdirs + reports + LIF |
| 4 | `/digital-marketing-pro:engagement lif-show <brand-slug> 2026-test` | Living Project Instruction File printed |
| 5 | `/digital-marketing-pro:engagement list-engagements` | Test engagement listed |

### 12.3 Methodology skill discovery

Verify that the 6 new methodology skills are discovered by Claude:

```
/digital-marketing-pro:engagement-workflow
/digital-marketing-pro:four-core-documents
/digital-marketing-pro:client-validation-document
/digital-marketing-pro:growth-plan
/digital-marketing-pro:yearly-planner
/digital-marketing-pro:continuous-improvement-loop
```

Each should show its description and not return "command not found."

### 12.4 Context-engine reference doc accessibility

Verify all 23 new reference docs are readable and properly cross-referenced:

```bash
ls skills/context-engine/{engagement-flow-methodology,four-core-documents-spec,two-views-model,decision-matrix-rerun,update-back-rule,stone-vs-opinion,living-instruction-file-spec,five-digital-markets,channel-families,in-market-out-market,decision-framework,unit-economics-framework,actionable-persona-format,b2b-decision-making-unit,three-scenario-forecasting,30-60-90-framework,reporting-cadence,fixed-vs-variable-budget,competitor-3-question-output,india-market-context,growth-plan-template,yearly-planner-template,monthly-report-template}.md
# Expect: all 23 files listed, no "No such file" errors
```

### 12.5 Decision Matrix coverage

Test every Decision Matrix trigger to confirm the engine produces the right re-run set:

| Trigger | Expected re-runs |
|---------|------------------|
| `competitors_changed` | 3.1, 3.2, 3.3, 3.4, 4.1, 4.2 |
| `target_market_changed` | 4.3, 4.4 |
| `audiences_changed` | 3.2, 3.3, 3.4 |
| `positioning_changed` | 3.3 |
| `budget_or_scope_changed` | 3.4 |
| `pricing_or_offering_changed` | 3.1 |
| `unit_economics_changed` | 3.1 |
| `minor_corrections_only` | (empty list — no re-runs) |
| Combined: `competitors_changed,positioning_changed` | 3.1, 3.2, 3.3, 3.4, 4.1, 4.2 (union) |

### 12.6 Backward compatibility regression

After installing v3.0, verify v2.7 still works:

| # | Test | Expected behaviour |
|---|------|-------------------|
| 1 | `/digital-marketing-pro:brand-setup` (existing brand) | Works as before; profile loaded |
| 2 | `/digital-marketing-pro:campaign-plan` (no engagement context) | Works as before; produces campaign brief |
| 3 | `/digital-marketing-pro:content-engine` (no engagement context) | Works as before |
| 4 | `/digital-marketing-pro:competitor-analysis` (no engagement context) | Works as before |
| 5 | SessionStart hook | Brand summary banner prints normally |
| 6 | PreToolUse compliance check | Compliance check runs on Write/Edit |
| 7 | SessionEnd hook | Insights saved to brand profile |

If any v2.7 functionality regresses, that is a critical bug. v3.0 is intended to be purely additive.
