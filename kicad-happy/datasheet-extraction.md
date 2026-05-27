# Datasheet Extraction Guide

Deep-dive into how kicad-happy turns component datasheet PDFs into structured JSON — what gets extracted, how quality is scored, and how analyzers consume the result.

The **datasheets** skill is the structured-spec layer that sits between the distributor skills (which download PDFs) and the analyzer skills (which consume verified per-part knowledge). If you've ever wanted an analyzer that knows the EN-pin threshold on a specific LDO, the USB peripheral speed on a specific MCU, or the thermal resistance of a specific QFN — this is how it gets there.

## How It Works

```
Distributor skills download PDFs:
  digikey/mouser/lcsc/element14  → <project>/datasheets/<MPN>.pdf

Datasheets skill extracts structure:
  <MPN>.pdf  → page selector  → target pages
             → extractor      → <project>/datasheets/extracted/<MPN>.json
             → scorer         → quality score (0.0-10.0)
             → cache manager  → manifest.json entry
             → verifier       → consistency check vs schematic usage

Analyzer skills consume:
  kicad, emc, spice, thermal, kidoc
    → get_regulator_features(mpn)  → None (miss/stale/low-score) or dict
    → get_mcu_features(mpn)        → None or dict
    → get_pin_function(mpn, pin)   → None or string
```

Each extraction is cached per-project, not globally — two projects with the same MPN can hold different extractions if they pin different datasheet revisions. There is no shared cross-project library.

## When to Extract

Run the extraction pipeline **before** your first design review on a project, and re-run when:

- `datasheets/extracted/` is missing or empty
- A new IC appears in the design without a cached extraction
- The cache manager reports a stale entry (PDF hash changed, extraction version outdated, age > 90 days)
- An analyzer reports `confidence: heuristic` on a claim you expected to be `datasheet-backed` — the extraction may be missing or below the quality threshold

For small designs (< 8 ICs), extract all ICs. For large designs, prioritize ICs that appear in power regulators, opamp circuits, MCU pin analysis, and high-speed interfaces — these are where datasheet-backed confidence has the highest value.

## Example Extraction Output

A per-MPN JSON file looks like this (simplified):

```json
{
  "mpn": "TPS61023DRLR",
  "manufacturer": "Texas Instruments",
  "description": "1A, 5V, 1.2MHz boost converter with 0.5V input",
  "extraction_version": 2,
  "pins": [
    {"number": "1", "name": "SW", "function": "Switch node", "type": "power", "direction": "output"},
    {"number": "2", "name": "GND", "function": "Ground", "type": "ground", "direction": "input"},
    {"number": "3", "name": "FB", "function": "Feedback", "type": "analog", "direction": "input",
     "voltage_operating_max": 6.0, "voltage_abs_max": 7.0},
    {"number": "4", "name": "EN", "function": "Enable", "type": "digital", "direction": "input",
     "required_external": null}
  ],
  "voltage_ratings": {
    "vin_min": 0.5, "vin_max": 5.5, "vin_abs_max": 6.0,
    "vout_max": 5.5
  },
  "features": {
    "topology": "boost",
    "switching_freq_hz": 1200000,
    "en_threshold_v": 0.4,
    "soft_start": true,
    "pg_present": false,
    "internal_compensation": false
  },
  "application_circuits": {
    "input_cap_recommended": "10uF ceramic, X5R or X7R",
    "output_cap_recommended": "22uF ceramic",
    "inductor_recommended": "2.2uH, 1.5A sat current"
  },
  "thermal": {
    "rtheta_ja_cw": 175.0,
    "tj_max_c": 150
  }
}
```

Fields the datasheet doesn't specify are `null`. Downstream analyzers gate on "known vs unknown," not "present vs missing."

## Cache Layout

```
<project>/
  design.kicad_sch
  design.kicad_pcb
  datasheets/
    TPS61023DRLR.pdf          # downloaded by distributor skills
    MP1484EN-LF-Z.pdf
    extracted/
      manifest.json           # extraction manifest (legacy name: index.json)
      TPS61023DRLR.json       # structured extraction
      MP1484EN-LF-Z.json
```

The cache manager (`datasheet_extract_cache.py`) owns the manifest and enforces staleness. An extraction is considered stale if:

- The source PDF's hash has changed
- The extraction's `EXTRACTION_VERSION` is older than the current skill version
- The extraction is older than `DEFAULT_MAX_AGE_DAYS` (90 days)
- The quality score is below `MIN_SCORE` (6.0)

Stale entries are transparently re-extracted on the next sync pass.

## Page Selection

Datasheets can be 10–200+ pages. The page selector (`datasheet_page_selector.py`) identifies 8–15 pages most likely to contain the information an analyzer needs, using a three-strategy cascade:

1. **TOC present** — scans the first 1–3 pages for section headings with page numbers. TOC references to "Pin Configuration", "Absolute Maximum Ratings", "Electrical Characteristics", and "Typical Application" resolve to target pages.
2. **No TOC** — scores every page by keyword density. Pages containing "absolute maximum", "pin configuration", "electrical characteristics", and "application circuit" score highest.
3. **No pdftotext** — falls back to pages 1–5 plus evenly distributed samples.

Default page budget: 10 pages, or 15 for multi-protocol parts (microcontrollers, FPGAs, SoCs). Always includes page 1 and the last page so cover-art and ordering information aren't lost.

## What Gets Extracted

Per-MPN JSON files follow a canonical schema (`EXTRACTION_VERSION` versioned). Major blocks:

| Block | Content |
|-------|---------|
| `identity` | manufacturer, MPN, family, description |
| `pins` | Pin number → {name, function, type, voltage_range, is_power, is_ground} |
| `voltage_ratings` | Absolute max, recommended operating, typical supply |
| `electrical_characteristics` | Per-parameter table (quiescent current, VIH/VIL, GBW, slew rate, etc.) |
| `peripherals` | (MCUs) GPIO count, USB/UART/SPI/I2C counts, ADC bits, protocol speeds |
| `features` | Regulator topology, EN pin behavior, power-good output, thermal pad presence |
| `application_circuits` | Typical external components + values (LDO output cap, MCU decoupling) |
| `spice_specs` | SPICE model coefficients where the datasheet provides them |
| `thermal` | Junction-to-ambient / junction-to-case resistance, max junction temp |

Null is valid — if the datasheet doesn't specify a field, the extraction records `null`. Analyzers gate on "known vs unknown," not "present vs missing."

## Quality Scoring

Every extraction gets a score from 0.0 to 10.0 via a weighted five-dimension rubric (`datasheet_score.py`):

| Dimension | Weight | What it measures |
|-----------|--------|------------------|
| Pin coverage | 35% | Fraction of pins with name, function, and type populated |
| Voltage ratings | 25% | Presence of absolute max and recommended operating ranges |
| Application info | 20% | Typical external components and recommended values present |
| Electrical characteristics | 10% | Parameter count vs expected count for the part category |
| SPICE specs | 10% | Model coefficients present where applicable |

Total = Σ(dimension_score × weight), rounded to one decimal place.

**Thresholds:**
- `MIN_SCORE = 6.0` — below this, analyzers ignore the extraction as insufficient
- `MAX_RETRIES = 3` — an extraction below MIN_SCORE gets retried up to 3 times, keeping the highest-scoring result
- Extractions above 6.0 but below 8.0 are used with reduced confidence weighting

The scorer is conservative — it's easier to refuse an extraction than to mislead an analyzer downstream. A 5.8/10 extraction does not get used; the analyzer falls back to heuristics and reports a confidence drop.

## Consumer API

Analyzer skills don't read `extracted/*.json` directly. They go through helpers in `datasheet_features.py`:

```python
from datasheet_features import (
    get_regulator_features,    # → {topology, en_threshold_v, pg_present, vout_range, ...}
    get_mcu_features,          # → {cores, flash_kb, usb, ethernet, adc_bits, ...}
    get_pin_function,          # → "EN" / "VIN" / "SW" / ...
    get_thermal_params,        # → {rja_cw, rjc_cw, tj_max_c}
)

feat = get_regulator_features("TPS61023DRLR")
if feat:
    # Known IC — use verified per-part facts
    threshold = feat.get("en_threshold_v")
else:
    # Miss, stale, or low-score — fall back to heuristic
    threshold = None
```

Every helper returns `None` for cache miss, stale cache, or low quality score. The analyzer is responsible for a heuristic fallback — trust is explicit, not implicit.

## Trust Gates

The extraction pipeline bakes trust into every downstream call:

- **Cache miss** — no extraction exists for the MPN. Helpers return None. Analyzer drops to heuristic with `confidence: "heuristic"`.
- **Stale extraction** — source PDF changed or cache is too old. Same as miss.
- **Low score (< 6.0)** — extraction exists but failed the rubric. Same as miss.
- **Sufficient score (≥ 6.0)** — helpers return the feature dict. Analyzer can emit findings with `confidence: "datasheet-backed"` and `evidence_source: "datasheet_extraction"`.

This is why findings from the schematic analyzer carry a confidence label: you can tell at a glance whether a claim is grounded in the datasheet, inferred heuristically, or cross-checked against both. When a finding says `confidence: datasheet-backed`, it means a scored extraction produced the underlying fact — not a keyword match on the part number.

## Verification

`datasheet_verify.py` cross-checks the extraction against actual usage in the design:

- Extracted pin names vs the nets connected to each pin in the schematic — flags mismatches (e.g., GND pin wired to VCC)
- Extracted voltage ranges vs the power rails feeding the part — flags overvoltage
- Extracted peripherals vs the protocol usage inferred by the analyzer — flags impossible claims (USB 3.0 on a USB 2.0-only MCU)

The verifier runs as part of the normal schematic analyzer pass; findings it raises carry rule-id `XV-DS-*` (cross-verify, datasheet). See the EMC and schematic analyzer output for examples.

## What It Can't Do

- **It doesn't download anything.** PDFs are owned by the distributor skills (`digikey`, `mouser`, `lcsc`, `element14`). If a PDF isn't in `<project>/datasheets/`, the datasheets skill has nothing to work with.
- **It isn't a universal spec library.** Extractions live per-project; there is no shared cross-project cache. Two projects using the same part maintain two extractions. This is intentional — datasheet revisions matter, and a verified extraction for revision A should not quietly get used for revision B.
- **It doesn't interpret marketing claims.** Application notes, reference designs, and "recommended for X" prose are skipped. Only structured tables, pin lists, and electrical characteristics are extracted. A part being marketed for automotive doesn't appear in the extraction; a part with AEC-Q100 grade 1 in the ordering information does.
- **It doesn't guess.** If the datasheet omits a parameter, the extraction records `null` rather than interpolating from the family or copying from a sister part. Downstream analyzers see the gap and fall back.

## Consumers Today

| Analyzer | What it uses |
|----------|--------------|
| `kicad` | Pin functions, regulator topology, MCU peripheral capability, voltage ratings |
| `emc` | SRF data for caps, saturation current for inductors, thermal pad presence |
| `spice` | Behavioral model parameters (GBW, slew rate, input offset) for opamps |
| `thermal` | Junction-to-ambient resistance, max junction temp |
| `kidoc` | Feature tables and pin audits in engineering documentation outputs |

Trust flows outward: the datasheets skill doesn't consume from other skills, only produces for them. This keeps the extraction layer simple and auditable — one skill owns the PDF-to-JSON contract, all other skills read it.

## Promoted from kicad in v1.3

Earlier versions kept extraction scripts under `skills/kicad/scripts/`. In v1.3 the extraction infrastructure became its own top-level skill (`skills/datasheets/`) with its own reference docs (`extraction-schema.md`, `quality-scoring.md`, `field-extraction-guide.md`, `consumer-api.md`). The promotion reflects the expanding consumer surface — once EMC, SPICE, thermal, and kidoc all started depending on verified per-part knowledge, treating it as a `kicad` internal was no longer accurate.
