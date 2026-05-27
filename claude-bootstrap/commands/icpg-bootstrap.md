# /icpg-bootstrap — Bootstrap from Git History

Infer ReasonNodes from existing git commit history. One-time setup for existing codebases.

---

## Usage

`/icpg-bootstrap [--days N]`

Default: 90 days of history.

---

## Steps

### 1. Initialize iCPG if needed

```bash
icpg init
```

### 2. Run bootstrap

```bash
icpg bootstrap --days 90 --verbose
```

If no LLM API key available:
```bash
icpg bootstrap --days 90 --verbose --no-llm
```

### 3. Show results

```
iCPG BOOTSTRAP COMPLETE
═══════════════════════

History scanned: {N} days ({M} commits)
Commit clusters: {K}
ReasonNodes created: {R}
Symbols linked: {S}
Duplicates skipped: {D}

TOP INFERRED INTENTS:
  1. [0.80] "Add JWT authentication" — 12 symbols, 5 files
  2. [0.75] "Refactor payment processing" — 8 symbols, 3 files
  3. [0.65] "Fix rate limiting bug" — 3 symbols, 2 files
  ...

LOW CONFIDENCE (review recommended):
  - [0.55] "Update dependencies" — may be too generic
  - [0.50] "Misc fixes" — commit message unclear
```

### 4. Offer review

Ask the user:
> {N} ReasonNodes were inferred from git history.
> {M} are low-confidence and may need review.
>
> Would you like to:
> 1. Keep all (proceed with current quality)
> 2. Review low-confidence intents (I'll show each one)
> 3. Run drift scan now (`icpg drift check`)

### 5. Post-bootstrap drift scan

```bash
icpg drift check
```

Show any immediate drift detected.
