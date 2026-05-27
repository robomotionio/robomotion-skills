# n8n-mcp Skills - Distribution Packages

This folder contains distribution packages for different Claude platforms.

## Available Packages

### For Claude.ai / Claude Desktop (Individual Skills)

Upload each skill separately via Settings > Capabilities > Skills (bottom of page):

- `n8n-expression-syntax-v1.9.0.zip` - n8n expression syntax and common patterns
- `n8n-mcp-tools-expert-v1.9.0.zip` - Expert guide for using n8n-mcp tools (recommended to install first)
- `n8n-workflow-patterns-v1.9.0.zip` - 6 proven workflow architectural patterns
- `n8n-validation-expert-v1.9.0.zip` - Validation error interpretation and fixing
- `n8n-node-configuration-v1.9.0.zip` - Operation-aware node configuration
- `n8n-code-javascript-v1.9.0.zip` - JavaScript in n8n Code nodes
- `n8n-code-python-v1.9.0.zip` - Python in n8n Code nodes

**Installation:**
1. Go to Settings > Capabilities > Skills (bottom of page)
2. Click "Upload Skill"
3. Select one of the skill zip files above
4. Repeat for each skill you want to install

### Complete Bundle (Claude Code only)

- **`n8n-mcp-skills-v1.9.0.zip`** (174 KB) - All 7 skills in one package

> **This bundle is NOT compatible with Claude.ai or Claude Desktop.** It uses a nested `skills/` directory structure required by Claude Code plugins. For Claude.ai/Desktop, use the individual skill zips above.

**Installation:**
```bash
# Claude Code plugin installation
/plugin install czlonkowski/n8n-skills

# Or install from local file
/plugin install /path/to/n8n-mcp-skills-v1.9.0.zip
```

## Which Package Should I Use?

| Platform | Package | What You Get |
|----------|---------|--------------|
| **Claude.ai / Desktop** | Individual zips | 7 skills (upload separately) |
| **Claude Code** | Complete bundle OR individual zips | All 7 skills |
| **Claude API** | Complete bundle | All 7 skills (extract skills/ folder) |

---

## Files in This Directory

```
dist/
├── n8n-code-javascript-v1.9.0.zip        (34 KB)
├── n8n-code-python-v1.9.0.zip            (31 KB)
├── n8n-expression-syntax-v1.9.0.zip      (11 KB)
├── n8n-mcp-skills-v1.9.0.zip             (174 KB)  Claude Code only
├── n8n-mcp-tools-expert-v1.9.0.zip       (19 KB)
├── n8n-node-configuration-v1.9.0.zip     (18 KB)
├── n8n-validation-expert-v1.9.0.zip      (19 KB)
├── n8n-workflow-patterns-v1.9.0.zip      (37 KB)
└── README.md                              (this file)
```

---

## What's Included in Each Package

### Individual Skill Packages (Claude.ai / Desktop / Code)

Each zip contains a skill folder at the root with:
```
<skill-name>/
├── SKILL.md              # Main skill instructions with YAML frontmatter
├── [Reference files]     # Additional documentation and guides
└── README.md             # Skill metadata and statistics
```

### Bundle Package (Claude Code only)

```
.claude-plugin/
  ├── plugin.json      # Claude Code plugin metadata
  └── marketplace.json # Marketplace listing metadata
README.md              # Project overview and documentation
LICENSE                # MIT License
skills/                # All 7 skills in subfolders
  ├── n8n-expression-syntax/
  ├── n8n-mcp-tools-expert/
  ├── n8n-workflow-patterns/
  ├── n8n-validation-expert/
  ├── n8n-node-configuration/
  ├── n8n-code-javascript/
  └── n8n-code-python/
```

## Verification

After installation, test skills by asking:

```
"How do I write n8n expressions?"
  -> Should activate: n8n Expression Syntax

"Find me a Slack node"
  -> Should activate: n8n MCP Tools Expert

"Build a webhook workflow"
  -> Should activate: n8n Workflow Patterns

"How do I access webhook data in a Code node?"
  -> Should activate: n8n Code JavaScript

"Can I use pandas in Python Code node?"
  -> Should activate: n8n Code Python
```

## Requirements

- **n8n-mcp MCP server** installed and configured ([Installation Guide](https://github.com/czlonkowski/n8n-mcp))
- **Claude Pro, Max, Team, or Enterprise** plan (for Claude.ai skills)
- **.mcp.json** configured with n8n-mcp server

## Documentation

For detailed installation instructions, see:
- Main README: `../README.md`
- Installation Guide: `../docs/INSTALLATION.md`
- Usage Guide: `../docs/USAGE.md`

## Troubleshooting

**Claude.ai Error: "Zip must contain exactly one SKILL.md file"**
- Use the individual skill zips, not the bundle
- Each skill must be uploaded separately

**Claude Code: Skills not activating**
- Verify skills are in `~/.claude/skills/` directory
- Check that n8n-mcp MCP server is running
- Reload Claude Code

**Skills not triggering**
- Skills activate based on keywords in your queries
- Try more specific questions matching skill descriptions
- Check that SKILL.md files have correct frontmatter

## License

MIT License - see `../LICENSE` file

## Credits

Conceived by Romuald Czlonkowski - https://www.aiadvisors.pl/en

Part of the [n8n-mcp project](https://github.com/czlonkowski/n8n-mcp).
