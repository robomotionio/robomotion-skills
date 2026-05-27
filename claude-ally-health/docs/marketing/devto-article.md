# Building a Personal Health System with Claude Code CLI

![Claude-Ally-Health Banner](https://via.placeholder.com/1000x400/000000/FFFFFF?text=Claude-Ally-Health)

## Introduction

As developers, we spend countless hours optimizing our code, our workflows, our productivity tools. But how much time do we spend on our most important asset - our health?

I wanted to build a personal health management system that:
1. **Respects my privacy** - no cloud uploads, no data selling
2. **Leverages AI** - intelligent analysis of my health data
3. **Works like I do** - command-line first, automation-friendly

Enter **Claude-Ally-Health** - a personal health information system powered by Claude Code CLI.

## What is Claude Code?

[Claude Code](https://claude.ai/code) is Anthropic's official CLI tool that brings Claude's AI capabilities directly to your terminal. What makes it powerful is its **Skill system** - you can extend it with custom commands and domain-specific knowledge.

This project is a demonstration of how far you can push Claude Code's capabilities.

## Architecture Overview

```
my-his/
├── .claude/
│   ├── commands/      # Slash command definitions
│   │   ├── save-report.md
│   │   ├── medication.md
│   │   ├── interaction.md
│   │   └── consult.md
│   └── specialists/   # AI medical specialists
│       ├── cardiology.md
│       ├── endocrinology.md
│       └── ... (13 total)
├── data/
│   ├── profile.json
│   ├── medications/
│   ├── 生化检查/
│   └── interactions/
```

Each `.md` file in `commands/` defines a CLI command. Here's a simplified example:

```markdown
---
description: Save a medical report
---

Please analyze the uploaded medical report image:
1. Extract all test values and reference ranges
2. Identify abnormal results
3. Save as JSON to data/生化检查/
```

## Key Features

### 1. Medical Report OCR

```bash
/save-report @blood-test.jpg
```

The system:
- Recognizes the image using GLM 4.5V
- Extracts all test values
- Identifies abnormal results
- Saves structured JSON data

### 2. Drug Interaction Detection

```bash
/interaction check
```

Features:
- Drug-drug interactions
- Drug-disease interactions
- 5-level severity system (A/B/C/D/X)
- Evidence-based recommendations

### 3. Multi-Specialist Consultation

```bash
/consult
```

This is where it gets interesting. The system spawns 13 specialist AI agents in parallel:

```
[Cardiology] Analyzing cardiovascular markers...
[Endocrinology] Checking hormonal balance...
[Gastroenterology] Reviewing liver enzymes...
...
[Coordinator] Synthesizing recommendations...
```

Each specialist has domain-specific knowledge and provides targeted insights.

## Technical Implementation

### File-Based Storage

No database needed. Just JSON:

```json
{
  "date": "2024-01-15",
  "testType": "Complete Blood Count",
  "results": [
    {
      "item": "Hemoglobin",
      "value": "14.5",
      "unit": "g/dL",
      "referenceRange": "13.5-17.5",
      "status": "normal"
    }
  ]
}
```

### Multi-Agent Coordination

The consultation system uses a coordinator pattern:

1. **Spawn** all specialists in parallel
2. **Analyze** data from each specialist's perspective
3. **Synthesize** findings into a coherent report
4. **Prioritize** recommendations by urgency

### Privacy by Design

- Zero external API calls for data storage
- All processing happens locally (via Claude Code)
- Standard JSON format for easy export
- MIT licensed - audit the code yourself

## Getting Started

```bash
# Clone the repository
git clone https://github.com/huifer/Claude-Ally-Health.git
cd Claude-Ally-Health/my-his

# Open in Claude Code
claude-code .

# Set up your profile
/profile set 175 70 1990-01-01

# Save your first report
/save-report @path/to/report.jpg
```

## What's Next?

I'm working on:
- [ ] Multi-language support (Chinese, Japanese, German)
- [ ] Web dashboard for visualization
- [ ] Health trend analysis
- [ ] Export to standard EHR formats

## Conclusion

This project is my exploration of two questions:

1. **How can AI help us manage our health data?**
2. **How can we do this without sacrificing privacy?**

The answer, so far, is: **Very well, with the right tools.**

Claude Code's extensibility makes it possible to build sophisticated domain-specific tools. Whether it's health data, project management, or something entirely different - the Skill system lets you mold AI to your needs.

**Check it out:** [GitHub](https://github.com/huifer/Claude-Ally-Health)

**Star it if you find it interesting!** ⭐

---

*Disclaimer: This system is for personal health management only and should not be used as a basis for medical diagnosis.*

## Links

- [GitHub Repository](https://github.com/huifer/Claude-Ally-Health)
- [Documentation](https://github.com/huifer/Claude-Ally-Health#readme)
- [Contributing Guidelines](https://github.com/huifer/Claude-Ally-Health/blob/main/CONTRIBUTING.md)
