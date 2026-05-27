# KiDoc — Engineering Documentation (beta)

> **Beta:** KiDoc is an early skill that is being actively developed. The core pipeline works and has been tested against 100+ real projects, but expect rough edges — some figure types may not render cleanly for all designs, narrative context quality varies, and PDF styling is still being refined. Feedback welcome.

KiDoc generates professional engineering documents from KiCad projects. It auto-runs all analyses, renders publication-quality figures, and produces structured documents in PDF, DOCX, ODT, or HTML.

## How it works

KiDoc is a three-stage pipeline:

1. **Scaffold** — Runs analyzers (schematic, PCB, EMC, thermal), renders SVG figures, generates a markdown document with auto-populated data tables and narrative placeholders
2. **Edit** — You (or the LLM) fill in the narrative sections. Data tables regenerate automatically on each run; your prose is preserved between `<!-- GENERATED -->` markers
3. **Render** — Converts the markdown to PDF, DOCX, ODT, or HTML with styled covers, table of contents, and embedded vector figures

## Document types

| Document | Use case | Key sections |
|----------|----------|-------------|
| **HDD** (Hardware Design Description) | Complete system documentation | Power architecture, signal interfaces, analog design, thermal analysis, EMC compliance, PCB layout, BOM, mechanical |
| **CE Technical File** | EU regulatory compliance | Product identification, essential requirements, harmonized standards, risk assessment, Declaration of Conformity |
| **Design Review** | Cross-stage gate review | Analyzer scorecard (fab gate, EMC, thermal), prioritized findings, action items, go/no-go assessment |
| **ICD** (Interface Control Document) | External integrator specs | Per-connector pinouts, electrical characteristics, signal levels, timing |
| **Manufacturing** | Production transfer package | Assembly overview, PCB fab notes, assembly instructions, test procedures |
| **Power Analysis** | Power-focused deep dive | Power distribution, regulator design, thermal margins, sequencing, PDN impedance |
| **Schematic Review** | Schematic-only milestone | System overview, power tree, signal analysis, BOM review |
| **EMC Report** | Pre-compliance findings | EMC risk analysis, per-category findings, mitigation recommendations, test plan |

Custom reports are supported via `--spec custom-report.json` for arbitrary section selection and ordering.

## Auto-generated figures

KiDoc ships 12 figure generators that produce publication-quality SVGs:

| Figure | What it shows |
|--------|--------------|
| **Power tree** | Regulator topology diagram with inductor values, capacitor summaries, output voltages, and efficiency |
| **Architecture** | System block diagram clustered by function — MCU at center, peripherals grouped by domain |
| **Bus topology** | I2C, SPI, UART, CAN network diagrams with device connections and bus parameters |
| **Schematic overview** | Full schematic page renders with component highlights |
| **Schematic crop** | Focused subsystem views — crop to specific components with highlight-nets and dim-others |
| **PCB views** | Layer preset renders: assembly (front/back), routing (front/back/all), power nets |
| **Connector pinouts** | Per-connector pin tables with signal names, types, and directions |
| **Thermal margin** | Junction temperature chart — Tj vs Tj_max for each power-dissipating component |
| **EMC severity** | Risk category severity distribution chart |
| **SPICE validation** | Simulation vs expected scatter plots per subcircuit |
| **Monte Carlo** | Tolerance stack-up distribution histograms with 3-sigma bounds |

Figures auto-regenerate only when underlying data changes (hash-based caching). New figure generators are auto-discovered via the `@register` decorator — drop a new generator in `figures/generators/` and it's available immediately.

## Usage

### Quick start

The simplest path — tell your agent what you want:

> "Generate an HDD for my board at hardware/rev2/"

The agent will run all analyses, generate figures, build the scaffold, fill in narratives, and render to PDF.

### Manual steps

For more control, run the pipeline stages individually:

**1. Generate scaffold** (auto-runs all analyses):
```bash
python3 <kidoc-path>/scripts/kidoc_scaffold.py \
  --project-dir . --type hdd --output reports/HDD.md --analyze
```

This produces `reports/HDD.md` with:
- Auto-populated data tables (component summary, power tree, regulator parameters, etc.)
- Narrative placeholders: `*[Describe the power architecture and design rationale]*`
- Embedded figure references pointing to `reports/figures/*.svg`

**2. Edit the markdown** — replace `*[...]*` placeholders with engineering prose. Your edits are preserved on regeneration.

**3. Build narrative context** (optional — helps the LLM write better prose):
```bash
python3 <kidoc-path>/scripts/kidoc_narrative.py \
  --analysis analysis/schematic.json --report reports/HDD.md
```

This produces focused data slices for each section: key questions to address, relevant data summaries, datasheet notes, and cross-references. Feed this to the LLM for informed narrative generation.

**4. Render to output format:**
```bash
python3 <kidoc-path>/scripts/kidoc_generate.py \
  --project-dir . --format pdf
```

Outputs to `reports/output/` with human-readable filenames like `"Widget Board - Hardware Design Description Rev 1.2.pdf"`.

### Regeneration

Re-run the scaffold after design changes:

```bash
python3 <kidoc-path>/scripts/kidoc_scaffold.py \
  --project-dir . --type hdd --output reports/HDD.md --analyze
```

Data tables between `<!-- GENERATED: section_id -->` markers are updated automatically. Your narrative prose outside these markers is preserved. Figures re-render only if their input data changed.

## Output formats

| Format | SVG handling | Dependencies | Best for |
|--------|-------------|-------------|---------|
| **Markdown** | Image references | Zero | Version control, editing, collaboration |
| **HTML** | Inlined as vector | Zero | Web sharing, self-contained single file |
| **PDF** | Vector (svglib) | Auto-created venv | Formal deliverables, printing |
| **DOCX** | Rasterized 300 DPI | Auto-created venv | Editable handoff to non-technical stakeholders |
| **ODT** | Rasterized 300 DPI | Auto-created venv | OpenDocument compatibility |

PDF/DOCX/ODT rendering requires a project-local venv at `reports/.venv/`, which is auto-created on first run. The venv installs `reportlab`, `svglib`, `python-docx`, and `odfpy` as needed — these never affect your system Python.

## Configuration

KiDoc reads from `.kicad-happy.json` (cascading from project root up to `~/.kicad-happy.json`):

```json
{
  "project": {
    "name": "Widget Board",
    "number": "HW-2024-042",
    "revision": "1.2",
    "company": "Acme Electronics",
    "author": "Jane Smith",
    "market": "eu"
  },
  "reports": {
    "classification": "Company Confidential",
    "branding": {
      "logo": "templates/logo.png",
      "header_left": "{company}",
      "header_right": "{number} Rev {rev}"
    }
  }
}
```

Template variables (`{project}`, `{rev}`, `{company}`, `{number}`, `{author}`, `{classification}`) are resolved in headers, footers, and filenames. User-level defaults in `~/.kicad-happy.json` apply to all projects — project-level configs override them.

## What consumes what

KiDoc consumes analysis outputs from other skills:

```
kicad skill  →  schematic.json, pcb.json     ─┐
emc skill    →  emc.json                      ├→  kidoc scaffold  →  figures + markdown
spice skill  →  spice.json (optional)         │
thermal      →  thermal.json (auto-run)       ─┘
                                                        ↓
                                               kidoc generate  →  PDF / DOCX / HTML
```

All analyses auto-run when the `--analyze` flag is used. For pre-generated analysis JSONs, point `--analysis-dir` to the cache directory.

## Design principles

- **Markdown is the source of truth** — human-editable, version-controllable, diff-friendly
- **Regeneratable data, persistent prose** — data tables update automatically; your writing stays
- **Zero dependencies for scaffold** — analysis, markdown, and SVG generation use stdlib only. Rendering dispatches to a project-local venv
- **Skip, don't stub** — sections with no data are omitted entirely (no empty "N/A" placeholders)
- **Plug-and-play figures** — new figure generators are auto-discovered via `@register` decorator
