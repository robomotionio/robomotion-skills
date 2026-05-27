# TODO — Port awesome-agent-skills sub-repos to robomotion-skills

**Goal:** Vendor every external skill collection linked from
https://github.com/VoltAgent/awesome-agent-skills into this repo as its
own group, following the pattern documented in
[how-to-write-or-port-a-skill-to-robomotion.md](how-to-write-or-port-a-skill-to-robomotion.md).

Each entry below is one upstream repo. As each one is vendored:
1. tick the checkbox,
2. note the target group directory in `→ <name>`,
3. for skips, annotate the reason inline (e.g. `(SKIPPED — license: GPL-3.0)`).

**Scope:** 127 repos (deduplicated from upstream README, excluding VoltAgent's own repos and already-vendored `addyosmani/agent-skills`, `coreyhaines31/marketingskills`, `nextlevelbuilder/ui-ux-pro-max-skill`).

## Already vendored (pre-checked)

- [x] `addyosmani/agent-skills` — engineering skills covering the full SDLC → `engineering-skills` (already vendored)
- [x] `coreyhaines31/marketingskills` — marketing skills for the SaaS marketing stack → `marketing-skills` (already vendored)
- [x] `nextlevelbuilder/ui-ux-pro-max-skill` — UI/UX design patterns and best practices → `ui-ux-pro-max-skill` (already vendored)

## Skills by Angular

- [~] `angular/skills` — Generate Angular code and architectural guidance for components, services, reactivity → `angular-skills` (SKIPPED — license: missing)
## Skills by Courier

- [x] `trycourier/courier-skills` — Multi-channel notifications via email, SMS, push, and chat → `courier-skills`
## Skills by Venice.ai

- [x] `veniceai/skills` — API basics, auth modes, pricing, and versioning → `veniceai-skills`
## Advertising Skills by Kim Barrett

- [~] `realkimbarrett/advertising-skills` — Define exactly who the buyer is, what they want, what they've tried, and what's driving their decisions → `advertising-skills` (SKIPPED — license: missing)
## Product Manager Skills by Dean Peters

- [~] `deanpeters/Product-Manager-Skills` — Evaluate channels using unit economics and recommend scale/test/kill decisions → `deanpeters-product-manager-skills` (SKIPPED — license: unclassified (LICENSE))
## Product Management Skills by Pawel Huryn

- [x] `phuryn/pm-skills` — Analyze A/B test results with statistical significance and recommendations → `pm-skills`
## Skills by Resend

- [x] `resend/resend-skills` — Send and manage emails via the Resend API → `resend-skills`
## Skills by Redis

- [x] `redis/agent-skills` — Redis development best practices — data structures, query engine, vector search, caching, and performance optimization → `redis-skills`
## CUDA-Q

- [x] `NVIDIA/skills` — CUDA-Q onboarding guide for installation, test programs, GPU simulation, QPU hardware, and quantum applications → `nvidia-skills`
## Skills by Google Cloud

- [x] `google/skills` — Interact with the Gemini Enterprise Agent Platform Skill Registry to create and search for available skills → `google-skills`
## Vector Databases

- [x] `qdrant/skills` — Agent skills for Qdrant vector search, covering scaling, performance optimization, search quality, monitoring, deployment, model migration, version upgrades, and SDK usage across Python, TypeScript, Rust, Go, .NET, and Java → `qdrant-skills`
## Marketing

- [~] `BrianRWagner/ai-marketing-skills` — 17 marketing frameworks for cold outreach, homepage audit, social cards, and more → `ai-marketing-skills` (SKIPPED — license: missing)
- [x] `AgriciDaniel/claude-seo` — Universal SEO skill for comprehensive website analysis and optimization → `claude-seo`
- [~] `wshuyi/x-article-publisher-skill` — Publish articles to X/Twitter → `x-article-publisher-skill` (REMOVED — non-English or no-description content)
- [x] `CosmoBlk/email-marketing-bible` — 55K-word email marketing guide as an AI skill → `email-marketing-bible`
- [x] `smixs/creative-director-skill` — AI creative director with recursive self-assessment: 20+ methodologies (SIT, TRIZ, Bisociation, SCAMPER, Synectics), 3-axis evaluation calibrated against Cannes/D&AD/HumanKind, 5-phase process from brief to presentation → `creative-director-skill`
- [x] `Xquik-dev/x-twitter-scraper` — Tweet search, profile tweets, follower export, media, posting, replies, MCP → `x-twitter-scraper`
- [x] `Xquik-dev/tweetclaw` — Post tweets, replies, DMs; search, monitor, run giveaways → `tweetclaw`
- [~] `SHADOWPR0/beautiful_prose` — Hard-edged writing style contract for timeless, forceful English prose without AI tics → `beautiful-prose` (SKIPPED — license: missing)
- [x] `blader/humanizer` — Remove signs of AI-generated writing from text, making it sound more natural and human → `humanizer`
- [~] `voidborne-d/humanize-chinese` — Detect and rewrite AI-generated Chinese text; rule-ensemble scoring, 7 style transforms, academic AIGC reduction → `humanize-chinese` (SKIPPED — repo no longer exists on GitHub)
- [x] `MohamedAbdallah-14/unslop` — Removes named AI writing tells (tricolons, em-dash pileups, hedging stacks, sycophancy openers, stock vocab like "delve"/"crucial"). Split lint/rewrite modes for auditing your own text without auto-rewriting. Five intensity levels, MIT → `unslop`
- [x] `Eronred/aso-skills` — 30+ App Store Optimization skills for keyword research, metadata optimization, competitor analysis, creative optimization, and mobile growth strategies via Appeeky API → `aso-skills`
- [~] `degausai/wonda` — AI content creation: images, video, music, audio, editing, publishing → `wonda` (SKIPPED — license: missing)
- [~] `gitroomhq/postiz-agent` — Schedule social media posts across 28+ platforms programmatically → `postiz-agent` (SKIPPED — license: unclassified (LICENSE))
- [x] `indranilbanerjee/digital-marketing-pro` — 150-skill engagement methodology — 12-Part Strategy Flow, 25 specialist agents, EU AI Act Article 50 ready (C2PA signing), 6-platform AEO/GEO incl. Google AI Mode → `digital-marketing-pro`
## Productivity and Collaboration

- [~] `PSPDFKit-labs/nutrient-agent-skill` — Document processing with Nutrient DWS API: convert (PDF/DOCX/XLSX/PPTX/HTML/images), extract text/tables, OCR (20+ languages), redact PII (pattern + AI), watermark, digital signatures, form filling. [MCP server](https://www.npmjs.com/package/@nutrient-sdk/dws-mcp-server) also available → `nutrient-agent-skill` (SKIPPED — license: missing)
- [~] `op7418/NanoBanana-PPT-Skills` — AI-powered PPT generation with document analysis and styled images → `nano-banana-ppt-skills` (SKIPPED — license: missing)
- [x] `zarazhangrui/frontend-slides` — Generate animation-rich HTML presentations with visual style previews → `frontend-slides`
- [~] `gokapso/agent-skills` — Connect WhatsApp, set up webhooks, and send messages → `gokapso-skills` (SKIPPED — license: missing)
- [x] `PleasePrompto/notebooklm-skill` — Interact with NotebookLM for document-based conversations → `notebooklm-skill`
- [x] `obra/superpowers-lab` — Lab environment for Claude superpowers → `superpowers-lab`
- [x] `obra/superpowers` — Generate and explore ideas → `superpowers`
- [~] `op7418/Youtube-clipper-skill` — YouTube clip generation and editing with automated workflows → `youtube-clipper-skill` (REMOVED — non-English or no-description content)
- [x] `ognjengt/founder-skills` — Claude skills for founders with packaged startup workflows → `founder-skills`
- [x] `EveryInc/charlie-cfo-skill` — Bootstrapped CFO financial management inspired by Charlie Munger → `charlie-cfo-skill`
- [~] `openaccountants/openaccountants` — 371 tax classification skills across 134 countries → `openaccountants` (SKIPPED — license: unclassified (LICENSE))
- [x] `wrsmith108/linear-claude-skill` — Manage Linear issues, projects, and teams → `linear-claude-skill`
- [~] `Shpigford/skills` — Generate comprehensive project documentation → `shpigford-skills` (SKIPPED — repo no longer exists on GitHub)
- [~] `hanfang/claude-memory-skill` — Minimal, low-friction hierarchical memory system with background agents and filesystem-based persistence → `claude-memory-skill` (SKIPPED — not a skill collection (no SKILL.md))
- [~] `kreuzberg-dev/kreuzberg` — Extract text, tables, and metadata from 62+ document formats → `kreuzberg` (SKIPPED — license: unclassified (LICENSE))
- [x] `Paramchoudhary/ResumeSkills` — 20 specialized skills for resume optimization, ATS analysis, interview prep, and career transitions → `resume-skills`
- [x] `RoundTable02/tutor-skills` — Transform docs or codebases into Obsidian StudyVaults with interactive quizzes → `tutor-skills`
- [~] `NeoLabHQ/context-engineering-kit` — Applies the famous *The Elements of Style* book principles to make documentation and writing clearer and more professional by eliminating wordiness and improving structure → `context-engineering-kit` (SKIPPED — license: unclassified (LICENSE))
- [x] `ReScienceLab/opc-skills` — Agent skills for solopreneurs with SEO, geo, and LLM tools → `opc-skills`
- [x] `SeanZoR/claude-speed-reader` — Speed read Claude's responses at 600+ WPM using RSVP with Spritz-style ORP highlighting → `claude-speed-reader`
- [x] `Charlie85270/Dorothy` — Orchestrate multiple AI CLI agents with automations and MCP servers → `dorothy`
- [~] `Digidai/product-manager-skills` — Senior PM agent with 30+ frameworks and SaaS metrics → `digidai-product-manager-skills` (SKIPPED — license: unclassified (LICENSE))
- [x] `deusyu/translate-book` — Translate books (PDF/DOCX/EPUB) via parallel sub-agents with resume → `translate-book`
- [x] `mvanhorn/last30days-skill` — Research any topic across Reddit, X, YouTube, HN, Polymarket, and the web, ranked by upvotes, likes, and real money instead of editors → `last30days-skill`
- [x] `santifer/career-ops` — 14-skill collection for AI-powered job search: JD evaluation with A-F scoring, ATS-optimized PDF generation, portal scanners (Greenhouse/Ashby/Lever), interview prep with STAR+R, batch processing, and a Go dashboard TUI → `career-ops`
## Development and Testing

- [~] `robzolkos/skill-rails-upgrade` — Analyze Rails apps and provide upgrade assessments → `skill-rails-upgrade` (SKIPPED — license: missing)
- [x] `antonbabenko/terraform-skill` — Terraform and OpenTofu patterns: testing, modules, state, CI/CD → `terraform-skill`
- [x] `zxkane/aws-skills` — AWS development with infrastructure automation and cloud architecture patterns → `aws-skills`
- [~] `Rootly-AI-Labs/Rootly-MCP-server` — AI-powered incident response with ML similarity matching, solution suggestions, and on-call coordination. Requires [Rootly MCP Server](https://github.com/Rootly-AI-Labs/Rootly-MCP-server) → `rootly-mcp-server` (SKIPPED — not a skill collection (no SKILL.md))
- [x] `conorluddy/ios-simulator-skill` — Control iOS Simulator → `ios-simulator-skill`
- [~] `ramzesenok/iOS-Accessibility-Audit-Skill` — Audit iOS App against Accessibility norms → `ios-accessibility-audit-skill` (SKIPPED — license: missing)
- [x] `truongduy2611/app-store-preflight-skills` — Scan iOS/macOS projects to catch common mistakes that lead to App Store rejection before submission → `app-store-preflight-skills`
- [x] `coderabbitai/skills` — Code review and PR autofix workflows for coding agents → `coderabbitai-skills`
- [x] `sanjay3290/ai-skills` — Execute safe read-only SQL queries against PostgreSQL databases → `ai-skills`
- [~] `jthack/ffuf_claude_skill` — Web fuzzing with ffuf → `ffuf-claude-skill` (SKIPPED — license: missing)
- [x] `lackeyjb/playwright-skill` — Browser automation with Playwright → `lackeyjb-playwright-skill`
- [x] `ibelick/ui-skills` — Opinionated, evolving constraints to guide agents when building interfaces → `ui-skills`
- [x] `muthuishere/hand-drawn-diagrams` — Generate hand-drawn Excalidraw diagrams from a prompt — animated SVG, hosted edit link, and PNG export. Works with Claude Code, Codex, Gemini CLI, and any agent supporting standard skill paths → `hand-drawn-diagrams`
- [x] `ehmo/platform-design-skills` — 300+ design rules from Apple HIG, Material Design 3, and WCAG 2.2 for cross-platform apps → `platform-design-skills`
- [x] `scarletkc/vexor` — Vector-powered CLI for semantic file search with a Claude/Codex skill → `vexor`
- [x] `fvadicamo/dev-agent-skills` — Git and GitHub workflow skills for commits, PRs, and code reviews → `dev-agent-skills`
- [x] `omkamal/pypict-claude-skill` — Pairwise test generation → `pypict-claude-skill`
- [x] `alinaqi/claude-bootstrap` — Opinionated project initialization with security-first guardrails, spec-driven atomic todos, LLM testing patterns, and CLI tool orchestration (gh, vercel, supabase) → `claude-bootstrap`
- [~] `ZhangHanDong/makepad-skills` — Makepad UI development skills for Rust apps: setup, patterns, shaders, packaging, and troubleshooting → `makepad-skills` (SKIPPED — license: missing)
- [x] `massimodeluisa/recursive-decomposition-skill` — Handle long-context tasks (100+ files, 50k+ tokens) through recursive decomposition strategies based on RLM research → `recursive-decomposition-skill`
- [x] `AvdLee/SwiftUI-Agent-Skill` — Modern SwiftUI best practices and iOS 26+ Liquid Glass adoption → `swift-ui-agent-skill`
- [x] `efremidze/swift-patterns-skill` — Modern Swift/SwiftUI best practices → `swift-patterns-skill`
- [~] `Joannis/claude-skills` — Swift Server development guidance with linting tool for best practices → `claude-skills` (SKIPPED — license: missing)
- [x] `rudrankriyam/app-store-connect-cli-skills` — Automate App Store deployments and management using ASC CLI → `app-store-connect-cli-skills`
- [x] `rameerez/claude-code-startup-skills` — Skills for building and running software startups, apps, and SaaS → `claude-code-startup-skills`
- [x] `zscole/model-hierarchy-skill` — Cost-optimized model routing based on task complexity → `model-hierarchy-skill`
- [~] `CloudAI-X/threejs-skills` — Three.js skills for creating 3D elements and interactive experiences → `threejs-skills` (SKIPPED — license: missing)
- [x] `Leonxlnx/taste-skill` — High-agency frontend skill that gives AI good taste with tunable design variance, motion intensity, and visual density to stop generic UI slop → `taste-skill`
- [x] `testdino-hq/playwright-skill` — 70+ production-tested Playwright automation testing patterns: E2E, POM, CI/CD, migrations, CLI → `testdino-hq-playwright-skill`
- [~] `hamelsmu/prompts` — Audit LLM eval pipelines and surface problems → `prompts` (SKIPPED — repo no longer exists on GitHub)
- [x] `uucz/moyu` — Anti-over-engineering skill with 5 variants and 10 platforms → `moyu`
- [x] `mattpocock/skills` — 17 dev workflow skills: PRD writing, TDD, codebase architecture, git guardrails, issue triage, refactoring plans, and more → `mattpocock-skills`
- [x] `mukul975/Anthropic-Cybersecurity-Skills` — 753 cybersecurity skills across 38 domains: cloud security, pentesting, red teaming, DFIR, malware analysis, threat intel, and more (MITRE ATT&CK mapped) → `cybersecurity-skills`
- [x] `wrsmith108/varlock-claude-skill` — Secure environment variable management ensuring secrets are never exposed in Claude sessions, terminals, logs, or git commits → `varlock-claude-skill`
- [x] `yusufkaraaslan/Skill_Seekers` — Automatically convert documentation websites, GitHub repositories, and PDFs into Claude AI skills in minutes → `skill-seekers`
- [~] `NoizAI/skills` — Human-like TTS workflows with local/cloud APIs and app delivery → `noiz-ai-skills` (SKIPPED — license: missing)
- [x] `Kevin7Qi/codex-collab` — Collaborate with Codex from Claude Code → `codex-collab`
- [x] `ethos-link/rails-conventions` — Rails 8 conventions for consistent production code changes → `rails-conventions`
- [~] `ShunsukeHayashi/agent-skill-bus` — Self-improving task orchestration for AI agent systems → `agent-skill-bus` (SKIPPED — repo no longer exists on GitHub)
- [x] `mcollina/skills` — 11 skills by Matteo Collina: Node.js, Fastify, TypeScript, OAuth, Git/GitHub, ESLint neostandard, documentation (Diataxis), Node.js core internals, skill optimizer, and more → `mcollina-skills`
- [x] `Lum1104/Understand-Anything` — Interactive codebase knowledge graphs via multi-agent LLM analysis → `understand-anything`
- [x] `hqhq1025/skill-optimizer` — Diagnose and optimize Agent Skills (SKILL.md) with real session data and research-backed static analysis. Works with Claude Code, Codex, and any Agent Skills-compatible agent → `skill-optimizer`
- [x] `LambdaTest/agent-skills` — TestMu AI (Formerly LambdaTest) Skills is a curated collection of Agent Skills that teach AI coding assistants how to write production-grade test automation → `lambda-test-skills`
- [x] `foryourhealth111-pixel/Vibe-Skills` — A skills governed plug-and-play harness for staged, test-driven skill orchestration → `vibe-skills`
- [x] `metalbear-co/skills` — Skills that let agents code and test against your Kubernetes cluster using mirrord → `metalbear-co-skills`
- [x] `dembrandt/dembrandt-skills` — UX and design system skills: hierarchy, typography, accessibility, interactions → `dembrandt-skills`
## Context Engineering

- [x] `muratcankoylan/Agent-Skills-for-Context-Engineering` — Understand what context is, why it matters, and the anatomy of context in agent systems → `agent-skills-for-context-engineering`
- [x] `k-kolomeitsev/data-structure-protocol` — Graph-based long-term memory skill for AI (LLM) coding agents — faster context, fewer tokens, safer refactors → `data-structure-protocol`
- [x] `awrshift/claude-memory-kit` — Persistent memory with hooks, wiki, and daily synthesis for multi-project workflows → `claude-memory-kit`
## Specialized Domains

- [~] `transloadit/skills` — Transloadit skill collection (6) → `transloadit-skills` (SKIPPED — license: missing)
- [x] `honeydew-ai/honeydew-ai-coding-agents-plugins` — 11 skills for the Honeydew semantic layer over Snowflake, Databricks, and BigQuery: model exploration, entity/relation/attribute/metric/context/domain creation, validation, query, filtering, and workspace branching → `honeydew-ai-coding-agents-plugins`
- [x] `raintree-technology/apple-hig-skills` — Apple Human Interface Guidelines as 14 agent skills covering platforms, foundations, components, patterns, inputs, and technologies for iOS, macOS, visionOS, watchOS, and tvOS → `apple-hig-skills`
- [x] `K-Dense-AI/claude-scientific-skills` — Scientific research and analysis skills → `claude-scientific-skills`
- [~] `NotMyself/claude-win11-speckit-update-skill` — Windows 11 system management → `claude-win11-speckit-update-skill` (REMOVED — non-English or no-description content)
- [~] `jeffersonwarrior/claudisms` — SMS messaging integration → `claudisms` (SKIPPED — repo no longer exists on GitHub)
- [~] `SHADOWPR0/security-bluebook-builder` — Build security Blue Books for sensitive apps → `security-bluebook-builder` (SKIPPED — license: missing)
- [x] `huifer/Claude-Ally-Health` — A health assistant skill for medical information analysis, symptom tracking, and wellness guidance → `claude-ally-health`
- [~] `frmoretto/clarity-gate` — Epistemic quality verification for RAG systems → `clarity-gate` (SKIPPED — license: unclassified (LICENSE))
- [x] `wanshuiyin/Auto-claude-code-research-in-sleep` — Autonomous ML research with cross-model review loops and GPU deployment → `auto-claude-code-research-in-sleep`
- [x] `zechenzhangAGI/AI-research-SKILLs` — 77 AI research skills for model training, inference, and MLOps → `zechenzhang-agi-ai-research-skills`
- [x] `Orchestra-Research/AI-research-SKILLs` — 20-module AI research skill library for model architecture, training, and ML paper writing → `orchestra-research-ai-research-skills`
- [x] `komal-SkyNET/claude-skill-homeassistant` — Supercharge and manage Home Assistant workflows → `claude-skill-homeassistant`
- [x] `more-io/claude-apple-bridges` — Native macOS app access — manage Apple Reminders, Calendar, Contacts, Notes, Mail, and tmux sessions via Swift CLI bridges → `claude-apple-bridges`
- [~] `prompt-security/clawsec` — Security skill suite with drift detection, automated audits, and skill integrity verification → `clawsec` (SKIPPED — license: unclassified (LICENSE))
- [x] `BehiSecc/VibeSec-Skill` — Helps write secure code by preventing common vulnerabilities including IDOR, XSS, SQL injection, SSRF, and weak authentication, approaching code from a bug hunter's perspective → `vibe-sec-skill`
- [~] `lawvable/awesome-legal-skills` — Curated agent skills for automating legal workflows → `awesome-legal-skills` (SKIPPED — license: unclassified (LICENSE))
- [x] `zw008/VMware-AIops` — AI-powered VMware vCenter/ESXi monitoring and operations: inventory queries, health/alarms, VM lifecycle (create, delete, snapshot, clone, migrate), vSAN management, Aria Operations analytics, and scheduled log scanning. Supports Claude Code, Gemini CLI, Codex, Aider, Trae, Kimi, and MCP → `vmware-aiops`
- [x] `video-db/skills` — Realtime and batch video workflows: capture screen/audio, ingest URLs/YouTube/RTSP, transcribe, index, search, generate subtitles, edit timelines, and stream HLS output → `video-db-skills`
- [x] `HeshamFS/materials-simulation-skills` — Agent skills for computational materials science: numerical stability, time-stepping, linear solvers, mesh generation, simulation validation, parameter optimization, and post-processing → `materials-simulation-skills`
- [x] `takechanman1228/claude-ecom` — Ecommerce CSV to business review with KPI decomposition → `claude-ecom`
- [~] `talkstream/ru-text` — Russian text quality: ~1,040 rules for typography, info-style, editorial, UX writing, business correspondence. Cross-platform: Claude Code, Codex CLI, Gemini CLI, Cursor → `ru-text` (REMOVED — non-English or no-description content)
- [x] `helius-labs/core-ai` — Ship Solana apps end-to-end; transaction sending, asset queries, real-time streaming, token swaps, prediction markets, browser wallets, and deep research into protocol internals all powered by Helius APIs, DFlow trading, and Phantom wallet integrations → `core-ai`
- [~] `meodai/skill.color-expert` — Color science expert skill with 286K words of reference material covering OKLCH/OKLAB, palette generation, accessibility/contrast, color naming, pigment mixing, and historical color theory → `skill-color-expert` (SKIPPED — license: unclassified (LICENSE))
- [x] `aklofas/kicad-happy` — AI-powered KiCad electronics design review and analysis → `kicad-happy`
- [x] `bitwize-music-studio/claude-ai-music-skills` — Full-lifecycle AI music album production → `claude-ai-music-skills`
## n8n Automation

- [x] `czlonkowski/n8n-skills` — JavaScript in n8n Code nodes with data access patterns → `n8n-skills`
## Skipped — license / not-a-skill-collection

_Populated as the pass runs. Each entry reproduces the original TODO line plus the skip reason._

- `meodai/skill.color-expert` — Color science expert skill with 286K words of reference material covering OKLCH/OKLAB, palette generation, accessibility/contrast, color naming, pigment mixing, and historical color theory (SKIPPED — license: unclassified (LICENSE))
- `lawvable/awesome-legal-skills` — Curated agent skills for automating legal workflows (SKIPPED — license: unclassified (LICENSE))
- `prompt-security/clawsec` — Security skill suite with drift detection, automated audits, and skill integrity verification (SKIPPED — license: unclassified (LICENSE))
- `frmoretto/clarity-gate` — Epistemic quality verification for RAG systems (SKIPPED — license: unclassified (LICENSE))
- `SHADOWPR0/security-bluebook-builder` — Build security Blue Books for sensitive apps (SKIPPED — license: missing)
- `jeffersonwarrior/claudisms` — SMS messaging integration (SKIPPED — repo no longer exists on GitHub)
- `transloadit/skills` — Transloadit skill collection (6) (SKIPPED — license: missing)
- `ShunsukeHayashi/agent-skill-bus` — Self-improving task orchestration for AI agent systems (SKIPPED — repo no longer exists on GitHub)
- `NoizAI/skills` — Human-like TTS workflows with local/cloud APIs and app delivery (SKIPPED — license: missing)
- `hamelsmu/prompts` — Audit LLM eval pipelines and surface problems (SKIPPED — repo no longer exists on GitHub)
- `CloudAI-X/threejs-skills` — Three.js skills for creating 3D elements and interactive experiences (SKIPPED — license: missing)
- `Joannis/claude-skills` — Swift Server development guidance with linting tool for best practices (SKIPPED — license: missing)
- `ZhangHanDong/makepad-skills` — Makepad UI development skills for Rust apps: setup, patterns, shaders, packaging, and troubleshooting (SKIPPED — license: missing)
- `jthack/ffuf_claude_skill` — Web fuzzing with ffuf (SKIPPED — license: missing)
- `ramzesenok/iOS-Accessibility-Audit-Skill` — Audit iOS App against Accessibility norms (SKIPPED — license: missing)
- `Rootly-AI-Labs/Rootly-MCP-server` — AI-powered incident response with ML similarity matching, solution suggestions, and on-call coordination. Requires [Rootly MCP Server](https://github.com/Rootly-AI-Labs/Rootly-MCP-server) (SKIPPED — not a skill collection (no SKILL.md))
- `robzolkos/skill-rails-upgrade` — Analyze Rails apps and provide upgrade assessments (SKIPPED — license: missing)
- `Digidai/product-manager-skills` — Senior PM agent with 30+ frameworks and SaaS metrics (SKIPPED — license: unclassified (LICENSE))
- `NeoLabHQ/context-engineering-kit` — Applies the famous *The Elements of Style* book principles to make documentation and writing clearer and more professional by eliminating wordiness and improving structure (SKIPPED — license: unclassified (LICENSE))
- `kreuzberg-dev/kreuzberg` — Extract text, tables, and metadata from 62+ document formats (SKIPPED — license: unclassified (LICENSE))
- `hanfang/claude-memory-skill` — Minimal, low-friction hierarchical memory system with background agents and filesystem-based persistence (SKIPPED — not a skill collection (no SKILL.md))
- `Shpigford/skills` — Generate comprehensive project documentation (SKIPPED — repo no longer exists on GitHub)
- `openaccountants/openaccountants` — 371 tax classification skills across 134 countries (SKIPPED — license: unclassified (LICENSE))
- `gokapso/agent-skills` — Connect WhatsApp, set up webhooks, and send messages (SKIPPED — license: missing)
- `op7418/NanoBanana-PPT-Skills` — AI-powered PPT generation with document analysis and styled images (SKIPPED — license: missing)
- `PSPDFKit-labs/nutrient-agent-skill` — Document processing with Nutrient DWS API: convert (PDF/DOCX/XLSX/PPTX/HTML/images), extract text/tables, OCR (20+ languages), redact PII (pattern + AI), watermark, digital signatures, form filling. [MCP server](https://www.npmjs.com/package/@nutrient-sdk/dws-mcp-server) also available (SKIPPED — license: missing)
- `gitroomhq/postiz-agent` — Schedule social media posts across 28+ platforms programmatically (SKIPPED — license: unclassified (LICENSE))
- `degausai/wonda` — AI content creation: images, video, music, audio, editing, publishing (SKIPPED — license: missing)
- `voidborne-d/humanize-chinese` — Detect and rewrite AI-generated Chinese text; rule-ensemble scoring, 7 style transforms, academic AIGC reduction (SKIPPED — repo no longer exists on GitHub)
- `SHADOWPR0/beautiful_prose` — Hard-edged writing style contract for timeless, forceful English prose without AI tics (SKIPPED — license: missing)
- `BrianRWagner/ai-marketing-skills` — 17 marketing frameworks for cold outreach, homepage audit, social cards, and more (SKIPPED — license: missing)
- `deanpeters/Product-Manager-Skills` — Evaluate channels using unit economics and recommend scale/test/kill decisions (SKIPPED — license: unclassified (LICENSE))
- `realkimbarrett/advertising-skills` — Define exactly who the buyer is, what they want, what they've tried, and what's driving their decisions (SKIPPED — license: missing)
- `angular/skills` — Generate Angular code and architectural guidance for components, services, reactivity (SKIPPED — license: missing)
## Follow-ups discovered during the pass

_Populated as the pass runs._
- `nvidia-skills` (`NVIDIA/skills`) uses two-level layout `skills/<category>/<skill>/SKILL.md`. `build-index.py` currently expects single-level; indexer needs to recurse one more level OR we flatten on vendor.
- `google-skills` (`google/skills`) uses two-level layout `skills/<category>/<skill>/SKILL.md`. `build-index.py` currently expects single-level; indexer needs to recurse one more level OR we flatten on vendor.
- `mattpocock-skills` (`mattpocock/skills`) uses two-level layout `skills/<category>/<skill>/SKILL.md`. `build-index.py` currently expects single-level; indexer needs to recurse one more level OR we flatten on vendor.
- `materials-simulation-skills` (`HeshamFS/materials-simulation-skills`) uses two-level layout `skills/<category>/<skill>/SKILL.md`. `build-index.py` currently expects single-level; indexer needs to recurse one more level OR we flatten on vendor.
