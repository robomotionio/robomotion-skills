# Changelog

All notable changes to kicad-happy are documented here.

This project follows [Semantic Versioning](https://semver.org/). Each release is validated against a [corpus of 5,800+ real-world KiCad projects](VALIDATION.md) before tagging.

---

## v1.3.0 — 2026-04-16

**Theme: Harmonized Analysis + Trust Infrastructure** — 168 commits making every analyzer speak the same format, every finding carry its own provenance, and the whole pipeline uniformly queryable, filterable, and auditable.

### Harmonized output across all analyzers

Every analyzer — schematic, PCB, Gerber, thermal, EMC, cross-analysis, SPICE, lifecycle — now produces the same top-level envelope:

```json
{
  "analyzer_type": "schematic",
  "schema_version": "1.3.0",
  "summary": { "by_severity": {...}, ... },
  "findings": [ {detector, rule_id, category, severity, confidence, ...} ],
  "trust_summary": { "total_findings": N, "by_confidence": {...}, ... }
}
```

The `signal_analysis` wrapper is gone. Subcircuit detections live in the same flat `findings[]` stream as validation checks, DFM rules, and audits. One schema to query, filter, and export.

- `finding_schema.py` — `make_finding()` factory, `Det` constants for all 60+ detectors, `get_findings()` / `group_findings()` consumer helpers
- All 75+ existing detectors migrated to the rich finding format
- 25 consumer files updated for the new layout
- `signal_analysis` wrapper removed from schematic output
- `confidence_map` removed — per-finding `confidence` is now canonical

### Trust infrastructure

Every finding carries its own trust metadata:

- **Confidence taxonomy** — `deterministic`, `heuristic`, `datasheet-backed`. Risk scores weight heuristic findings at 0.5x.
- **Evidence source taxonomy** — `parsed_schematic`, `parsed_pcb`, `datasheet_extraction`, `inference`, `heuristic_matching`, etc.
- **Provenance annotations** — `make_provenance()` calls on all 61 detectors (KH-263 Phase 1). Records which field was used, which datasheet was consulted, which inference chain led to the claim.
- **trust_summary** — rollup on every analyzer output: finding counts by confidence, by evidence source, datasheet coverage percentage.

Consumers (reports, what-if, release gate) now surface trust posture alongside findings.

### New detectors (22 total, across validation, domain, and audit families)

**Validation detectors** (`validation_detectors.py`):
- PU-001 pull-up/pull-down resistor presence
- VM-001 cross-domain voltage mismatch
- PR-001..004 protocol electrical validation (I2C, SPI, CAN, USB)
- PS-001 power sequencing dependency graph
- LR-001 LED resistor sizing
- FS-001 feedback network stability pre-check

**Domain detectors** (`domain_detectors.py`):
- WL-001 wireless modules (WiFi/BLE, LoRa, cellular, GPS)
- TF-001 transformer SMPS feedback (optocoupler + TL431)
- IA-001 I2C address conflicts
- SC-001 supercapacitor / energy harvesting
- PL-001 PWM LED dimming topology
- AH-001 audio headphone jack switch

**Audit detectors** (new pattern — banner-level findings that aggregate evidence across many components):
- SS-001 / SS-002 sourcing-gate audits (MPN coverage, BOM-line coverage)
- DS-001 / DS-002 / DS-003 datasheet-coverage audits
- RS-001 / RS-002 rail-source audit (jumper-aware trace from rails to regulators/sources)
- LB-001 label-alias audit (multi-label nets)
- PP-001 power-pin DC-path audit (IC power pin DC continuity to a rail)
- NT-001 unnamed-net annotation

### PCB intelligence

New `pcb_connectivity.py` — union-find copper connectivity graph built from pads, tracks, vias, and zone fills. Produces per-net island map with gap locations, disconnected pad pairs, and a full component graph (`--full` mode).

Six new cross-domain PCB checks consuming the connectivity graph:
- NR-001 critical net routing near board edges
- RP-002 return path continuity (plane gaps under classified signals)
- TW-001 trace width validation vs current (IPC-2152)
- PS-002 power supply island detection
- VS-002 voltage plane split detection (with signal-crossing analysis)
- DP-005 differential pair routing quality (via/layer/length asymmetry)

Seven new assembly/DFM checks:
- FD-001 fiducial presence
- TE-001 test point coverage
- OR-001 orientation consistency
- SK-001 silkscreen-on-pad overlap
- VP-001 via-in-pad tenting (`--full` only)
- BV-001 board-edge via clearance (`--full` only)
- KO-001 keepout violations

### Stage and audience filtering

All analyzers accept `--stage {schematic|layout|pre_fab|bring_up}` and `--audience {designer|reviewer|manager}` flags. Filter findings to what matters for each review phase. Stage readiness (`pass` / `needs_review` / `needs_work`) reported per phase.

### Datasheet pipeline

The datasheet workflow got its own top-level skill (`skills/datasheets/`), promoted from `skills/kicad/scripts/`:

- Structured per-MPN extraction cache in `datasheets/extracted/<MPN>.json`
- Heuristic page selection with TOC detection and keyword scoring
- Five-dimension quality scoring rubric
- Consumer helper API (`datasheet_features.py`) — returns None on cache miss / stale / low-score
- Cross-check extraction vs schematic usage (consistency verification)
- Trust gates on all consumers (thermal, SPICE, verifier) — extractions below score 6.0 are ignored

### Cross-analysis

`cross_analysis.py` — consumes schematic + PCB JSON, runs six cross-domain checks:
- CC-001 connector current capacity vs trace width
- EG-001 ESD coverage gap analysis
- DA-001 decoupling strategy adequacy
- XV-001 / XV-002 / XV-003 schematic/PCB cross-validation

### KiCad 10 format compatibility

- KH-318 PCB via type detection — fixed decade-old bug where `via["type"]` was always None. Now correctly classifies blind/buried/micro (buried added in KiCad 10 file version 20250926).
- KH-319 `(hide yes)` boolean handling — hidden pins on schematics saved by KiCad 9.0+ now correctly detected.

### Schema hardening (Batch 20)

- `schema_version: "1.3.0"` on every analyzer output
- Severity normalization (removed raw `critical/high/medium/low/info` aliases in favor of canonical severities)
- `confidence_map` field removed (replaced by per-finding `confidence`)
- Legacy `group_findings_legacy()` / `DETECTOR_TO_LEGACY_KEY` removed from first-party code
- `--schema` output synced to match real emitted JSON on all 8 analyzer types
- Deterministic `findings[]` ordering + stable `detection_id` (KH-316)

### Tools

- `summarize_findings.py` — cross-run finding summary. Reads the current analysis run, groups findings by rule_id, prints a severity × count table. `--top`, `--severity`, `--json` flags.
- `export_issues.py` — finding-to-GitHub-Issues export. Structured body, label-based dedup, severity/rule-id filters, dry-run by default.
- `--mpn-list FILE` on all four distributor sync scripts (KH-312) — batch datasheet sync without a KiCad project. Filters via `is_real_mpn()`, de-duplicates, skips blank lines and `#` comments.
- `analyze_thermal.py --schema` — rounds out the `--schema` coverage on all analyzers.

### Bugfixes (33+ KH-* issues closed)

Highlights:

- KH-311, KH-313 — EMC detector crashes on edge-case input
- KH-314 — thermal `--schema` support
- KH-315 — hierarchy_context schema drift
- KH-316 — deterministic findings[] ordering
- KH-317 — XT-001 diff-pair suppression path (session-10 regression)
- KH-318 / KH-319 — KiCad 10 format-compat (above)
- KH-312 — `--mpn-list` batch mode (above)
- KH-283, KH-284, KH-285, KH-286 — PCB analyzer crashes (crystal, netclass, pad position, rich-format migration)
- KH-263 Phase 1 — provenance annotation rollout

See the issue tracker (harness ISSUES.md / FIXED.md) for the complete list with root causes.

### Test corpus

- 5,829 repos, 2M+ regression assertions at 99.98% pass
- 972 unit tests, 0 failures
- Smoke cross-section (27 repos, 16,434 runs) green after KH-318/KH-319
- quick_200 cross-section (275 repos, 411,198 assertions) green
- Schema drift regression test covers all 8 analyzers (permanent since session 10)

### Known limitations shipped with v1.3

- `group_findings_legacy()` removed from first-party code but internal consumers (`what_if.py`, `diff_analysis.py`) still use a compat shim pending v1.4 Priority 0 modernization
- EMC and thermal `summary` retain raw `critical/high/medium/low/info` counts alongside `by_severity` for consumer migration
- Schematic and PCB outputs have deterministic top-level `findings[]` ordering, but nested-list ordering inside findings (e.g., `load_caps` under DO-DET) is not yet fully deterministic — v1.4 item
- `fab_release_gate.py` aggregates 4 analyzers (schematic, PCB, thermal, EMC), not cross_analysis — v1.4 enhancement

---

## v1.2.0 — 2026-04-09

**Theme: Trust + Reach** — 102 commits making the engine trustworthy to teams and reachable from both platforms.

### New skill: kidoc (beta)

Professional engineering documentation from KiCad projects. Auto-runs all analyses, renders schematics and PCB layouts, generates publication-quality figures, and produces markdown scaffolds with auto-updating data sections and narrative placeholders. Early skill with rough edges — actively developed.

- 8 report types: Hardware Design Description, CE Technical File, Design Review, Interface Control Document, Manufacturing Transfer, Schematic Review, Power Analysis, EMC Report
- Custom reports via `--spec` JSON files
- Output formats: PDF (ReportLab), DOCX (python-docx), ODT (odfpy), HTML, Markdown
- Schematic SVG renderer with KiCad-parity colors, font scaling, pin text, net annotations, crop/focus/highlight
- PCB layout renderer with 6 layer presets, net highlighting, crop, annotations
- 12 publication-quality figure generators: power tree, architecture, bus topology, connector pinouts, thermal margin, EMC severity, SPICE validation, Monte Carlo distributions
- Datasheet integration: comparison tables, pin audits, spec summaries
- Narrative engine: per-section context builder with writing guidance
- Hash-based figure caching — unchanged data skips re-render

### New detectors (15 domain-specific)

Extracted domain-specific detectors into `domain_detectors.py` (~4,500 LOC) alongside core `signal_detectors.py` (~3,100 LOC). 40+ total schematic detectors (was 25 in v1.0).

| Detector | What it finds |
|----------|---------------|
| ESD protection audit | Cross-references every external connector with TVS/ESD devices; flags unprotected pins |
| USB-C CC validation | Verifies 5.1k pull-downs on CC1/CC2; detects PD controller ICs as alternative |
| Debug interfaces | Detects SWD/JTAG connectors, verifies MCU connections |
| Power path / load switches | Load switch ICs, ideal diode / power MUX, USB PD controllers |
| ADC signal conditioning | Voltage references, anti-alias filters, input scaling |
| Reset / supervisor | Supervisor ICs, watchdog timers, RC reset circuits |
| Clock distribution | PLL / clock generators, oscillator outputs, reference crystal matching |
| Display / touch | Display drivers, backlight drivers, touch controller ICs |
| Sensor fusion | IMU / accelerometer / gyro / magnetometer / barometer ICs, interrupt connections |
| Level shifters | TXB/TXS ICs, discrete BSS138-based, voltage domain verification |
| Audio circuits | Amplifier ICs, codec chips, speaker impedance matching |
| LED driver ICs | PWM / matrix / constant-current drivers |
| RTC circuits | RTC ICs, backup battery detection, crystal pairing |
| LED lighting audit | Chain tracing (5 hops), current limiting resistor verification, multi-pin exclusion |
| Thermocouple / RTD | Thermocouple amplifiers, RTD interfaces, cold junction compensation |
| Power sequencing | Power-good daisy chains, enable chain validation, cross-rail dependencies |
| LVDS interfaces | FPD-Link, DS90, SN65LVDS families with serializer/deserializer classification |

### First-class Codex support

- `.agents/skills/` with symlinks to all 11 skills for auto-discovery
- `.agents/plugins/marketplace.json` for Codex marketplace browsing
- Enriched `.codex-plugin/plugin.json` with full metadata
- Agent-neutral language across all SKILL.md files and references
- README presents Claude Code and Codex as equal install paths
- GitHub Action docs cover both `claude-code-action` and `codex-action`

### Project config and suppressions

- `.kicad-happy.json` project config: compliance target, derating profile, preferred suppliers, board class, rail overrides, BOM conventions
- Per-finding suppressions with reasons: `suppress: [{rule: "DC-001", ref: "C5", reason: "intentional"}]`
- Suppressed findings listed but marked, not hidden; active vs suppressed counts in summary
- Cascading config: project-level merges with user-level `~/.kicad-happy.json`
- Design intent auto-detection (hobby/consumer/industrial/medical/automotive/aerospace)
- IPC class detection from fab notes with class-aware DFM thresholds

### Report improvements

- **Per-finding confidence labels**: deterministic, datasheet-backed, heuristic, AI-inferred
- **Missing information section**: separates "I don't know" from "there's a problem"
- **Top-risk summary**: top 3 respin risks, bring-up blockers, and manufacturing blockers
- **Fabrication release gate**: 8-category "ready for fab?" check (routing, BOM, DFM, documentation, schematic-PCB consistency, Gerbers, thermal, EMC)

### Schematic-to-PCB cross-verification

New `cross_verify.py` with 7 cross-checks:
- Component reference bidirectional matching (orphans, missing, value mismatches, DNP conflicts)
- Differential pair length matching with per-protocol tolerances (USB 2mm, Ethernet 5mm, HDMI 1mm)
- Differential pair intra-pair skew check per protocol
- Power trace width assessment per regulator output rail
- Decoupling cap placement distance cross-check
- Bus routing advisory (signal lengths, SPI clock-to-data skew)
- Thermal via adequacy check

### Protocol electrical parameter checks

Complete coverage across all major protocols:
- **I2C**: Pull-up rise time validation, speed mode assessment, open-drain VOL compatibility, bus current budget
- **SPI**: Chip select conflict detection, device loading advisory, signal integrity (series termination)
- **UART**: TX/RX crossover verification, RS-232 transceiver detection with charge pump cap check
- **USB**: CC resistor validation (5.1k sink, source levels), D+/D- series resistors, VBUS capacitor sizing
- **Ethernet**: Bob Smith termination detection, magnetics/impedance advisory
- **HDMI**: 100ohm TMDS differential termination check
- **CAN**: 120ohm termination detection

### What-if enhancements

- **Sweep tables**: `R5=1k,2.2k,4.7k,10k` (comma list) and `R5=1k..100k:10` (log range) with markdown table output
- **Tolerance analysis**: `R5=4.7k+-5%` worst-case corner analysis (2^N combinations)
- **Fix suggestions**: `--fix voltage_dividers[0] --target 3.3` with E12/E24/E96 snapping
- **EMC impact preview**: `--emc` runs analyze_emc.py on patched JSON, diffs findings
- **PCB parasitic awareness**: `--pcb` with auto-discovery, trace R/L injection, footprint compatibility

### Detection schema

Centralized all per-detection-type metadata into `detection_schema.py`. Eliminated 4 hard-coded consumer-side registries (`_DERIVED_FIELDS`, `_recalc_derived`, `SIGNAL_REGISTRY`, `PRIMARY_METRIC`). Adding a new detection type is now 1 schema entry instead of 4-file edits.

### Diff analysis improvements

- **Cache integration**: `--analysis-dir` / `--run` for diffing runs from analysis cache
- **Multi-run trends**: `--trend N` shows metric evolution across last N runs
- **Change attribution**: "cutoff_hz changed because R5 went from 1k to 4.7k"
- **Regression detection**: flags new ERC warnings, removed protections, SPICE pass-to-fail, EMC score increases
- **Stable detection IDs**: hash-based `detection_id` on every signal detection for ref-renumbering resilience

### Analysis enrichment (complete)

Phase 1-4 enrichment across schematic, PCB, and EMC outputs:
- Bus electrical parameters: I2C speed mode, voltage, pull-up ohms; CAN termination; bus device dicts with controller field
- Power dissipation for switching regulators (buck/boost/buck-boost with efficiency estimates)
- Crystal load cap validation (target, error%, ok/marginal/out_of_spec)
- ESD device details on connector audit entries
- Decoupling proximity matrix in PCB output
- Switching loop area pre-computation in PCB output (via --schematic flag)
- EMC category summary pre-rollup

### Datasheet verification bridge

New `datasheet_verify.py` bridges extracted datasheet data with schematic analysis:
- Pin voltage abs_max violation (CRITICAL) and operating range exceeded (HIGH/MEDIUM)
- Missing required external components per datasheet pin specs
- Per-IC decoupling verification against application circuit recommendations
- Activates automatically when `datasheets/extracted/` cache exists

### Professional quick wins

- Fab notes completeness check (IPC class, surface finish, thickness, copper weight, material)
- Silkscreen completeness audit (revision, board name, ref visibility, connector labels, polarity)
- BOM lock verification (MPN coverage %, missing MPNs, generic values)
- Connector ground pin distribution (flag >4 signal pins per ground)
- Certification requirement identification (FCC/CE/IEC/UL from detected RF, battery, USB, Ethernet, high voltage)

### Analysis cache integration

All analyzers now support `--analysis-dir` for automatic cache management:
- Timestamped run folders with manifest tracking
- Copy-forward of unchanged outputs between runs
- Automatic new-run vs overwrite-current decision based on diff severity
- Pre-analysis datasheet sync prompt in skill workflow

### Sub-sheet detection (KH-228)

Detection rate improved from 34% to 99% using `.kicad_pro` stem matching as primary heuristic. Zero false positives on root schematics.

### Registry trust & CI

- GitHub Actions CI workflow (py_compile on Python 3.8 + 3.12)
- CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- Dependabot for GitHub Actions version tracking
- SECURITY.md moved to `.github/` for scanner compatibility
- Security architecture documentation in SKILL.md (Snyk W011 mitigation)

### Additional analysis improvements

- **Hierarchical context for sub-sheets**: automatic root schematic discovery and cross-sheet net resolution when analyzing individual sub-sheets
- **Sleep current estimation**: realistic vs worst-case analysis, per-rail breakdown with EN pin detection and GPIO state inference
- **Keepout zone analysis**: surface area calculation, ESD IC decoupling proximity checks, touch pad GND clearance verification
- **Lifecycle audit integration**: wired into analyzer via `--lifecycle` flag, queries 4 distributor APIs
- **Technical debt cleanup**: shared detector helpers (`detector_helpers.py`), hoisted 40+ deferred imports, consolidated duplicate calculations, tightened exception handling
- **`.kicad_pro` / `.kicad_dru` / library table parsing**: net classes, design rules, text variables from project files

### E-series standard values

- E12, E24, E96 decade tables in `kicad_utils.py`
- `snap_to_e_series()` function for component value snapping
- Used by what-if fix suggestions and EMC decoupling recommendations

### Bugfixes (25 issues)

KH-194 through KH-228 — most discovered via automated Layer 3 LLM batch review:

- KH-194: ESD audit "can" word boundary matching "scan"
- KH-195: USBPDSINK01 assertion update for PD controller detection
- KH-196: Bare capacitor values parsed as Farads in inrush/PDN calculations
- KH-197: Key matrix topology false positives (19 boards fixed)
- KH-198: LC filter reference collision in multi-project schematics
- KH-199/200: None rail names crash power_tree and narrative
- KH-204: power_rails uses UUID sheet paths instead of human-readable names
- KH-206: Global labels with different names merged into one net
- KH-207: Legacy KiCad 5 matrix decomposition producing wrong pin positions
- KH-208: Component type classification ignoring lib_id for Connector/Sensor/Motor/CircuitBreaker
- KH-209: Power rails with nnVn naming pattern (3V3, 12V0) classified as signal
- KH-210: SPI chip select detection missing CSN/NCS/SSEL patterns
- KH-211: pin_nets filtering out unnamed nets (hiding sub-sheet connections)
- KH-212: Bare capacitor values <1.0 parsed as Farads instead of microfarads
- KH-213: P-MOSFET detection missing PMOS/P-MOS/P-MOSFET keyword variants
- KH-214: INA2xx power monitors misclassified as opamp circuits
- KH-215: LM2576/LM2596 switching bucks classified as LDO
- KH-216: Multi-unit IC pin_nets showing wrong unit's pins
- KH-217: Crystal frequency parsing case-sensitive (kHZ/MHZ not matched)
- KH-218: Vref heuristic wrong for TPS62912, TPS73601, LM22676
- KH-219: Load switches classified as LDO topology
- KH-220: Active oscillators with custom lib symbols misclassified as connector
- KH-221: Opamp TIA feedback classified as compensator; false voltage dividers
- KH-222: Multi-unit symbol duplication in led_audit/sleep_current/usb_compliance
- KH-223: Power sequencing cascade not resolved (overbar pin name matching)
- KH-224: Multi-unit IC power_domains only showing one unit's rails
- KH-225: Charge pump LM2664 classified as LDO (now charge_pump topology)
- KH-226: NUCLEO dev board module classified as switching regulator
- KH-227: Logic gates misclassified as level_shifter_ic
- KH-228: detect_sub_sheet only identifying 34% of sub-sheets
- AP63357/AP632xx Vref entries added (0.8V)
- EMC IO-001 jumper false positive exclusion

### Validation

- 681,000+ schematic + 517,000+ EMC regression assertions at 100% pass rate
- 5,829 repos, 40+ schematic detectors, 42 EMC rules, 17 SPICE subcircuit types
- 400+ unit tests across 22 test files
- 0 open issues at release
- 102 commits since v1.1.0

---

## v1.1.0 — 2026-04-02

**EMC Pre-Compliance + Analysis Toolkit**

### New skill: EMC pre-compliance

42 rule checks across 17 categories predicting EMC test failures from schematic and PCB data. SPICE-enhanced when ngspice is available. Covers FCC, CISPR, automotive, and military standards.

| Category | Rule IDs |
|----------|----------|
| Ground plane integrity | GP-001, GP-002 |
| Decoupling | DC-001 through DC-005 |
| I/O filtering | IO-001 through IO-003 |
| Switching harmonics | SW-001, SW-002 |
| Clock routing | CK-001 through CK-004 |
| Differential pairs | DP-001, DP-002 |
| PDN impedance | PD-001 through PD-004 |
| ESD paths | ES-001 |
| Via stitching | VS-001 |
| Board edge radiation | BE-001 |
| Thermal-EMC coupling | TE-001 |
| Shielding | SH-001 |
| Crosstalk | XT-001, XT-002 |
| Connector filtering | CF-001 |
| Return path continuity | RP-001 |
| Cavity resonance | CR-001 |
| Component placement | CP-001 |

SPICE enhancements: lumped and distributed PDN impedance sweep, EMI filter insertion loss verification, switching harmonic FFT via Goertzel algorithm, capacitor suggestion verification.

### New analysis tools

- **Monte Carlo tolerance analysis** — `--monte-carlo N` runs N simulations with randomized component values. Reports 3-sigma bounds and per-component sensitivity (Pearson r-squared).
- **Design diff** — compares two analysis JSONs, reports component/signal/EMC/SPICE changes. GitHub Action `diff-base: true` for automatic PR comparison.
- **Thermal hotspot estimation** — junction temperature for LDOs, switching regulators, shunt resistors. Package theta-JA lookup, thermal via correction, proximity warnings. 7 rule IDs (TS-001..005, TP-001..002).
- **What-if parameter sweep** — patches component values, recalculates derived fields, optional SPICE re-simulation.

### Plugin distribution

- Published on official Anthropic Claude Code marketplace
- Install: `/plugin marketplace add aklofas/kicad-happy`

### Code audit (22 fixes)

3 critical, 9 high, 6 medium, 4 low severity fixes discovered during comprehensive code audit:

- **Critical**: Trace inductance formula 25x overestimate, circular board bounding box wrong, inner-layer traces mapped to wrong reference plane
- **High**: PDN target impedance 2x too lenient, Goertzel normalization missing 2x factor, two-digit regulator suffix parser (LM2596-12 read as 1.2V), operator precedence in decoupling shared nets, courtyard shapes silently dropped, GP-002 ignoring 2-layer boards, via stitching counting all vias (not just ground), unknown SMPS skipping EMC checks, Tier 2 functions not using AnalysisContext
- **Medium**: No-connect sheet collision, rail voltage estimation duplication, distributed PDN magnitude addition, PCB --full mode re-parsing, zone fill detection KiCad 9/10, layer alias type guard, ground net name matching, SH-001 INFO noise, DC bias derating

### Validation

- 6,853 EMC analyses across 1,035 repos (zero crashes)
- 96 equations verified against primary sources
- 404,558 regression assertions at 100% pass rate
- 30,646 SPICE simulations

---

## v1.0 — 2026-03-31

**First Stable Release**

The first production-ready release. Every piece of the analysis pipeline — schematic parsing, PCB layout review, Gerber verification, SPICE simulation, datasheet cross-referencing, BOM sourcing, and manufacturing prep — built and tested against 1,035 real-world KiCad projects.

### Schematic analysis

- S-expression parser for KiCad 5-10 `.kicad_sch` and legacy `.sch` files
- 25 subcircuit detectors: regulators (buck/boost/LDO), filters (RC/LC/pi/notch), opamps, H-bridges, rectifier bridges, protection circuits, bus protocols, crystal oscillators, current sense, decoupling, voltage dividers
- Mathematical verification: feedback divider calculations, filter cutoff frequencies, power dissipation, bias current paths
- Voltage derating: ceramic (50%), electrolytic (80%), tantalum capacitors; IC absolute max; resistor power. Commercial, military, and automotive profiles.
- Protocol validation: I2C pull-up value and rise time, SPI chip select counts, UART voltage domain crossing, CAN termination
- Op-amp checks: bias current paths, capacitive output loading, high-impedance feedback, unused channels

### PCB layout analysis

- Footprint parsing, track/via/zone analysis, thermal management, DFM scoring
- Thermal via adequacy per pad
- Impedance calculation from stackup parameters
- Differential pair matching and proximity/crosstalk analysis
- Zone stitching, tombstoning risk, courtyard overlap detection

### SPICE simulation

- Auto-generated testbenches for 17 subcircuit types
- Per-part behavioral models (~100 opamps)
- PCB parasitic injection (trace resistance, via inductance)
- Multi-simulator: ngspice, LTspice, Xyce

### Datasheet infrastructure

- Structured extraction cache with quality scoring (5-dimension rubric)
- Heuristic page selection for large PDFs
- DigiKey API as primary datasheet source (direct PDF URLs)
- SPICE spec integration from extracted data

### Component sourcing

- DigiKey (OAuth 2.0), Mouser (API key), LCSC (jlcsearch, no auth), element14/Newark/Farnell
- Per-supplier order file export, pricing comparison
- Datasheet sync: 96% download success rate across corpus

### Manufacturing

- JLCPCB and PCBWay format export (BOM + CPL)
- Design rule validation per fab house
- Basic vs extended parts classification (JLCPCB)
- Rotation offset tables

### Lifecycle audit

- Component EOL/NRND/obsolescence alerts from 4 distributor APIs
- Temperature grade auditing (commercial/industrial/automotive/military)
- Alternative part suggestions

### Gerber verification

- Layer identification, alignment checks, drill analysis
- Zip archive scanning
- Mixed plating detection, NPTH classification

### GitHub Action

- Automated PR reviews on KiCad file changes
- Two-tier: deterministic analysis (free) + optional AI review via Claude
- Commit status checks with findings summary

### KiCad support

- KiCad 5, 6, 7, 8, 9, 10
- Legacy `.sch` format
- Single-sheet and multi-sheet hierarchical designs
- Integer and string net ID formats (KiCad 10 change)

### Validation

- 1,035 repos, 6,845 schematic files, 3,498 PCB files, 1,050 Gerber directories
- 312,956 components parsed, 531,418 nets traced
- 294,000+ regression assertions at 100% pass rate
- 30,646 SPICE simulations across 17 subcircuit types
