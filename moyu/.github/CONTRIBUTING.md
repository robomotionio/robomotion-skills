# Contributing to Moyu

Thanks for your interest in contributing! Here's how you can help.

## Getting Started

```bash
# Clone the repo
git clone https://github.com/uucz/moyu.git
cd moyu

# Run benchmarks (optional, requires Python 3 + API keys)
pip install -r benchmark/requirements.txt
python benchmark/runner.py --model sonnet-4 --condition moyu-standard --scenario s1 --trial 1
python benchmark/metrics.py
python benchmark/analyze.py
```

## Ways to Contribute

### Add a new platform

1. Create a directory: `<platform>/moyu/SKILL.md`
2. Adapt the skill content to the platform's format (see existing platforms for reference)
3. Add install instructions to all three READMEs (`README.md`, `README.en.md`, `README.ja.md`)
4. Update the supported platforms table in all three READMEs

### Add a new skill variant

1. Create `skills/<variant-name>/SKILL.md`
2. Add a slash command in `commands/<variant-name>.md`
3. Update the variants table in all three READMEs

### Add a new language localization

1. Create `skills/moyu-<lang>/SKILL.md` (translate from `skills/moyu-en/SKILL.md`)
2. Optionally create `cursor/rules/moyu-<lang>.mdc`
3. Add a `README.<lang>.md` (translate from `README.en.md`)
4. Update the language switcher line in all existing READMEs

### Add benchmark scenarios

1. Create a new prompt file in `benchmark/prompts/` (e.g., `s13.txt`)
2. Describe a single, concrete coding task
3. Run the benchmark: `python benchmark/runner.py --scenario s13 --condition control --trial 1`
4. Run with Moyu: `python benchmark/runner.py --scenario s13 --condition moyu-standard --trial 1`
5. Include results in your PR

### Improve prompt wording

The core skills are in `skills/moyu/SKILL.md` (Chinese) and `skills/moyu-en/SKILL.md` (English). Improvements should:

- Keep changes minimal and focused
- Maintain consistency across all language versions
- Follow the Moyu philosophy (practice what we preach)

### Share your Before/After experience

Post in [Discussions > Show and Tell](https://github.com/uucz/moyu/discussions/categories/show-and-tell) with:
- The task you gave your AI
- Code output without Moyu
- Code output with Moyu

## Pull Request Guidelines

- One feature per PR
- Keep diffs small (we practice what we preach)
- Update all three READMEs (ZH, EN, JA) if applicable
- Test skill installation: `claude skill install --url <your-fork> --skill moyu`

## Good First Issues

Look for issues labeled [`good first issue`](https://github.com/uucz/moyu/labels/good%20first%20issue) — these are great starting points for new contributors.
