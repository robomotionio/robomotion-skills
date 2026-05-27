# Show HN: Claude-Ally-Health - AI-Native Personal Health System for Developers

I built a personal health data management system powered by Claude Code CLI.

## What is it?

Claude-Ally-Health is a file-based personal health information system that uses Claude Code's command-line tools for data management. Think of it as your personal AI-powered health assistant that runs entirely on your machine.

## Key Features

- **Privacy-First**: Pure file-based storage, no database, no cloud uploads
- **AI Medical Reports**: Intelligent image recognition for medical reports
- **Drug Interaction Detection**: 5-level severity warning system (A/B/C/D/X)
- **Multi-Specialist Consultation**: 13 AI medical specialists working in parallel
- **Radiation Tracking**: Medical radiation dose tracking and management
- **CLI-Based**: No programming required, just commands

## Quick Start

```bash
# Install Claude Code
# Clone the repo
git clone https://github.com/huifer/Claude-Ally-Health.git

# Set up your profile
/profile set 175 70 1990-01-01

# Save a medical report
/save-report /path/to/report.jpg

# Start multi-specialist consultation
/consult
```

## Why I Built It

As a developer, I wanted full control over my health data. Existing solutions either:
- Store data in the cloud (privacy concerns)
- Require complex setup
- Lack intelligent analysis

This project demonstrates how Claude Code can be extended into a powerful domain-specific tool through its Skill system.

## Tech Stack

- Storage: JSON files + filesystem
- CLI: Claude Code Slash Commands
- AI: Multi-agent specialist system
- Vision: Medical report OCR

## What's Next

- [ ] Multi-language support (Chinese, Japanese, German)
- [ ] Web dashboard
- [ ] Mobile app
- [ ] EHR export formats

## Links

- GitHub: https://github.com/huifer/Claude-Ally-Health
- Docs: https://github.com/huifer/Claude-Ally-Health#readme
- License: MIT

Feedback welcome!
