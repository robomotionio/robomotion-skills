# Robomotion Skills

Curated skills for Robomotion LLM Agents following the [agentskills.io](https://agentskills.io) specification.

## Structure

```
skills-index.json          # Manifest listing all skills
skills/
  pdf/SKILL.md             # PDF processing skill
  security-best-practices/ # Security review & secure coding
  security-threat-model/   # AppSec threat modeling
  yeet/                    # Git stage/commit/push/PR workflow
  figma-implement-design/  # Figma to code translation
  linear/                  # Linear issue management
```

## Adding a Skill

1. Create a folder under `skills/` with your skill name
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and markdown body
3. Add the skill entry to `skills-index.json`

## License

Apache-2.0
