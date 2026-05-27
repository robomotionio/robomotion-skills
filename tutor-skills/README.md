# tutor-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-blue)](https://docs.anthropic.com/en/docs/claude-code)
[![Install with npx skills](https://img.shields.io/badge/npx_skills-add-green)](https://github.com/vercel-labs/skills)

Two [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills that turn any knowledge source into an **Obsidian StudyVault** and then quiz you on it — closing the loop from content to comprehension.

## How It Works

```
  Documents / Code                    Obsidian                    Quiz Session
 ┌──────────────────┐           ┌──────────────────┐          ┌──────────────────┐
 │  PDF, MD, HTML,  │  /tutor   │   StudyVault/    │  /tutor  │  4 questions per  │
 │  EPUB, source    │──setup──▶ │   structured     │────────▶ │  round, graded,   │
 │  code projects   │           │   interlinked    │          │  concept tracking  │
 └──────────────────┘           │   notes + MOC    │          └────────┬─────────┘
                                └──────────────────┘                   │
                                         ▲                             │
                                         └─────── progress updates ────┘
```

## Skills Overview

| Skill | Command | Purpose | Input | Output |
|-------|---------|---------|-------|--------|
| **tutor-setup** | `/tutor-setup` | Generate a StudyVault | Documents or source code | Obsidian vault with notes, dashboards, practice questions |
| **tutor** | `/tutor` | Interactive quiz tutor | An existing StudyVault | Quiz sessions with concept-level progress tracking |

## Quick Start

### One-line install (recommended)

```bash
npx skills add RoundTable02/tutor-skills
```

> Requires [npx skills](https://github.com/vercel-labs/skills) — works with Claude Code, Cursor, Windsurf, and more.

### Manual install

```bash
git clone https://github.com/RoundTable02/tutor-skills.git
cd tutor-skills
./install.sh
```

### Step 1: Generate a StudyVault

```bash
cd ~/study-materials/          # or any source code project
claude
> /tutor-setup
```

### Step 2: Start Quizzing

```bash
claude
> /tutor
```

---

## tutor-setup

Transforms knowledge sources into a structured Obsidian StudyVault. Mode is auto-detected:

| Marker Found | Mode |
|---|---|
| `package.json`, `pom.xml`, `build.gradle`, `Cargo.toml`, `go.mod`, etc. | Codebase Mode |
| No project markers | Document Mode |

### Document Mode

Turns PDFs, text files, web pages, and other sources into comprehensive study notes.

- Auto-scans working directory for source files (PDF, TXT, MD, HTML, EPUB)
- Extracts and analyzes content with verified source mapping
- Generates concept notes with comparison tables, ASCII diagrams, and exam patterns
- Creates practice questions with hidden answers (active recall via fold callouts)
- Builds a dashboard with Map of Content (MOC), Quick Reference, and Exam Traps
- Full interlinking with `[[wiki-links]]` across all notes

**Phases**

| Phase | Name | Description |
|-------|------|-------------|
| D1 | Source Discovery | Scan, extract, and verify source content mapping |
| D2 | Content Analysis | Build topic hierarchy and dependency map |
| D3 | Tag Standard | Define English kebab-case tag registry |
| D4 | Vault Structure | Create numbered folders per topic |
| D5 | Dashboard | MOC, Quick Reference, Exam Traps |
| D6 | Concept Notes | Structured notes with tables, diagrams, callouts |
| D7 | Practice Questions | Active recall with fold callouts (8+ per topic) |
| D8 | Interlinking | Cross-reference all notes with wiki-links |
| D9 | Self-Review | Verify against quality checklist |

**Generated structure**

```
StudyVault/
  00-Dashboard/          # MOC + Quick Reference + Exam Traps
  01-<Topic1>/           # Concept notes + practice questions
  02-<Topic2>/
  ...
```

### Codebase Mode

Generates a new-developer onboarding vault from a source code project.

- Auto-detects tech stack, architecture patterns, and module boundaries
- Traces request flows and data flows end-to-end
- Creates per-module notes with key files, public interfaces, and dependency maps
- Generates onboarding exercises (code reading, configuration, debugging, extension)
- Builds a dashboard with architecture overview, module map, API surface, and getting started guide

**Phases**

| Phase | Name | Description |
|-------|------|-------------|
| C1 | Project Exploration | Scan files, detect tech stack, map layout |
| C2 | Architecture Analysis | Identify patterns, trace flows, map modules |
| C3 | Tag Standard | Define `#arch-*`, `#module-*`, `#pattern-*` registry |
| C4 | Vault Structure | Create dashboard + per-module folders |
| C5 | Dashboard | MOC with module map, API surface, getting started |
| C6 | Module Notes | Purpose, key files, interface, flow, dependencies |
| C7 | Exercises | Code reading, config, debugging, extension tasks |
| C8 | Interlinking | Cross-link all modules and exercises |
| C9 | Self-Review | Verify against quality checklist |

**Generated structure**

```
StudyVault/
  00-Dashboard/          # MOC + Quick Reference + Getting Started
  01-Architecture/       # System overview, request flow, data flow
  02-<Module1>/          # Per-module notes
  03-<Module2>/
  ...
  NN-DevOps/             # Build, deploy, CI/CD
  NN+1-Exercises/        # Onboarding exercises
```

---

## tutor

Interactive quiz tutor that tracks what you know and don't know at the **concept level**. Works with any StudyVault generated by `tutor-setup`.

### Session Types

| Type | When Available | Focus |
|------|----------------|-------|
| Diagnostic | Unmeasured areas (⬜) exist | Broad assessment of new areas |
| Drill weak areas | Weak areas (🟥/🟨) exist | Targeted practice on struggles |
| Choose a section | Always | Study any area on demand |
| Hard-mode review | All areas 🟩/🟦 | Challenge mastered material |

### Quiz Flow

1. Detects your StudyVault and reads the learning dashboard
2. Presents session options based on your current proficiency
3. Delivers 4 questions per round (4 options each, zero hints)
4. Grades answers and explains mistakes
5. Updates concept files and dashboard automatically

### Progress Tracking

Proficiency is tracked per area with emoji badges:

| Badge | Level | Rate |
|-------|-------|------|
| 🟥 | Weak | 0–39% |
| 🟨 | Fair | 40–69% |
| 🟩 | Good | 70–89% |
| 🟦 | Mastered | 90–100% |
| ⬜ | Unmeasured | No data |

Concept-level tracking stores attempts, correct count, last tested date, and error notes for wrong answers — so drill sessions rephrase missed concepts in new contexts.

---

## The Learning Cycle

```
           ┌────────────────────────────┐
           │   /tutor-setup             │
           │   Generate StudyVault      │
           └──────────┬─────────────────┘
                      │
                      ▼
           ┌────────────────────────────┐
           │   Read & review notes      │
           │   in Obsidian              │
           └──────────┬─────────────────┘
                      │
                      ▼
           ┌────────────────────────────┐
           │   /tutor                   │
           │   Take diagnostic quiz     │◀──────────┐
           └──────────┬─────────────────┘           │
                      │                              │
                      ▼                              │
           ┌────────────────────────────┐           │
           │   Review weak areas        │           │
           │   in Obsidian              │           │
           └──────────┬─────────────────┘           │
                      │                              │
                      ▼                              │
           ┌────────────────────────────┐           │
           │   /tutor                   │           │
           │   Drill weak concepts      │───────────┘
           └────────────────────────────┘
```

## Requirements

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- [Obsidian](https://obsidian.md/) (recommended) to open and navigate the generated vault

## Repository Structure

```
tutor-skill/
├── skills/
│   ├── tutor-setup/              # Vault generation skill
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── templates.md
│   │       ├── codebase-workflow.md
│   │       ├── quality-checklist.md
│   │       └── codebase-templates.md
│   └── tutor/                    # Interactive quiz skill
│       ├── SKILL.md
│       └── references/
│           └── quiz-rules.md
├── examples/
├── install.sh
├── uninstall.sh
├── README.md
└── LICENSE
```

## Uninstall

```bash
./uninstall.sh
```

Or manually:

```bash
rm -rf ~/.claude/skills/tutor-setup
rm -rf ~/.claude/skills/tutor
```

## License

[MIT](LICENSE)
