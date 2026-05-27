# Validation Summary

This document describes how kicad-happy is tested and validated. Every change to the analysis engine is verified against a corpus of real-world KiCad projects before release.

*Auto-generated on 2026-04-16 by `generate_validation_md.py`.*

## Why this matters

Hardware design review tools must be trustworthy. A false negative (missed bug) can cost a board respin ($5K-$50K). A false positive (phantom warning) erodes trust until engineers ignore the tool entirely. kicad-happy addresses both through large-scale automated validation that no human reviewer could replicate.

## Test corpus

The [test harness](https://github.com/aklofas/kicad-happy-testharness) contains 5,856 open-source KiCad projects — the kind of designs real engineers actually build.

**Corpus diversity:**

| Dimension | Coverage |
|-----------|----------|
| Project types | Hobby boards, production hardware, motor controllers, RF frontends, battery management systems, IoT devices, audio amplifiers, power supplies, sensor boards, dev kits |
| KiCad versions | KiCad 5, KiCad 6, KiCad 7, KiCad 8, KiCad 9, KiCad 10 |
| File formats | `.kicad_sch` (S-expression), legacy `.sch` (EESchema), `.kicad_pcb` |
| Design complexity | Single-sheet through multi-sheet hierarchical, 2-layer through 6-layer |
| Component counts | 3 to 500+ components per project |
| Net complexity | Simple power supplies to multi-bus digital designs (I2C, SPI, UART, CAN, USB, Ethernet, HDMI) |

**KiCad version distribution:**

| Version | Repos |
|---------|------:|
| KiCad 5 | 2,209 |
| KiCad 6 | 1 |
| KiCad 7 | 9 |
| KiCad 8 | 1,225 |
| KiCad 9 | 1,365 |
| KiCad 10 | 40 |

**Category distribution:**

| Category | Repos |
|----------|------:|
| Miscellaneous KiCad projects | 1,810 |
| Keyboards | 449 |
| Synthesizers / audio | 324 |
| Motor controllers / robotics | 315 |
| LED / display | 304 |
| ESP32 | 294 |
| Arduino recreations | 294 |
| Networking / radio / SDR | 254 |
| Sensor boards / IoT | 250 |
| Retro computing | 235 |
| USB / interface adapters | 214 |
| Power / battery | 207 |
| RP2040 / Raspberry Pi | 192 |
| STM32 | 179 |
| ADC / DAC / measurement | 110 |
| *(other categories)* | 425 |

The corpus is sourced from public GitHub repositories. It is not curated for "easy" designs — it includes incomplete projects, unusual topologies, non-standard conventions, and designs with real bugs.

## What gets tested

Every analysis script runs against every applicable file in the corpus. Nothing is skipped or excluded.

### Crash testing

| Analyzer | Files tested | Success rate |
|----------|-------------|--------------|
| Schematic (`analyze_schematic.py`) | 36,577 | 100% |
| PCB (`analyze_pcb.py`) | 18,745 | 100% |
| Gerber (`analyze_gerbers.py`) | 5,506 | 100% |
| EMC (`analyze_emc.py`) | 36,658 | 100% |
| SPICE (`simulate_subcircuits.py`) | 36,552 | 100% |

A single unhandled exception across any analyzer on any file in the corpus is treated as a release blocker.

### Regression assertions

Hard assertions on known-good output values. If a previously correct result changes, the assertion fails and the change must be investigated.

| Category | Assertion count | Pass rate |
|----------|----------------|-----------|
| **Total** | **2,239,678** | **100%** |

Assertions are seeded from validated output and checked on every run. When analyzer logic changes intentionally (new fields, corrected calculations), affected assertions are re-seeded after manual verification.

## Signal detector coverage

65 active schematic detectors verified against the corpus:

| Detector | Repos with hits |
|----------|----------------|
| audit_rail_sources | 5,214 |
| audit_esd_protection | 5,074 |
| detect_design_observations | 4,951 |
| audit_datasheet_coverage | 4,023 |
| audit_sourcing_gate | 3,962 |
| detect_decoupling | 3,848 |
| validate_pullups | 3,293 |
| audit_connector_ground_distribution | 3,147 |
| audit_led_circuits | 3,019 |
| detect_power_regulators | 2,979 |
| analyze_connectivity | 2,825 |
| detect_rc_filters | 2,579 |
| detect_voltage_dividers | 2,281 |
| detect_transistor_circuits | 2,208 |
| detect_crystal_circuits | 1,852 |
| detect_protection_devices | 1,674 |
| audit_power_pin_dc_paths | 1,605 |
| detect_solder_jumpers | 1,399 |
| suggest_certifications | 1,187 |
| validate_led_resistors | 1,149 |
| detect_label_aliases | 1,119 |
| validate_power_sequencing | 1,049 |
| detect_debug_interfaces | 1,024 |
| detect_wireless_modules | 972 |
| detect_lc_filters | 833 |
| validate_usb_bus | 809 |
| validate_voltage_levels | 802 |
| detect_opamp_circuits | 741 |
| validate_i2c_bus | 475 |
| detect_memory_interfaces | 435 |
| detect_led_drivers | 428 |
| detect_pwm_led_dimming | 423 |
| detect_key_matrices | 423 |
| detect_sensor_interfaces | 373 |
| detect_addressable_leds | 366 |
| detect_level_shifters | 359 |
| detect_buzzer_speakers | 307 |
| detect_adc_circuits | 281 |
| detect_motor_drivers | 274 |
| detect_battery_chargers | 273 |
| detect_rf_matching | 244 |
| detect_reset_supervisors | 237 |
| detect_audio_circuits | 226 |
| detect_clock_distribution | 211 |
| detect_isolation_barriers | 189 |
| detect_power_path | 187 |
| detect_current_sense | 176 |
| detect_rf_chains | 154 |
| validate_feedback_stability | 153 |
| detect_bridge_circuits | 137 |
| validate_can_bus | 136 |
| detect_rtc_circuits | 121 |
| detect_ethernet_interfaces | 119 |
| validate_spi_bus | 111 |
| detect_led_driver_ics | 83 |
| detect_hdmi_dvi_interfaces | 80 |
| detect_headphone_jack | 79 |
| detect_display_interfaces | 55 |
| detect_thermocouple_rtd | 48 |
| detect_energy_harvesting | 47 |
| detect_integrated_ldos | 35 |
| detect_bms_systems | 25 |
| detect_transformer_feedback | 20 |
| detect_lvds_interfaces | 15 |
| detect_i2c_address_conflicts | 12 |

## How to reproduce

Anyone can reproduce the validation:

```bash
# 1. Clone the harness
git clone https://github.com/aklofas/kicad-happy-testharness.git
cd kicad-happy-testharness

# 2. Clone test repos
python3 checkout.py

# 3. Run analyzers (auto-parallelizes across all CPU cores)
python3 run/run_schematic.py --resume
python3 run/run_pcb.py --resume
python3 run/run_emc.py --resume

# 4. Run regression assertions
python3 regression/run_checks.py
```

The harness requires Python 3.8+ and a checkout of the corpus repos. ngspice is optional but recommended for SPICE assertions. Use `--cross-section smoke` for a quick 20-repo validation.

## Issue tracking

All analyzer bugs found during validation are tracked with sequential IDs:

- `KH-001` through `KH-322`: analyzer issues (275 filed, 275 closed, 0 open)
- `TH-001` through `TH-008`: harness infrastructure issues

Each closed issue has a corresponding bugfix regression guard assertion that prevents the bug from returning.

## Numbers at a glance

| Metric | Value |
|--------|-------|
| Repos in corpus | 5,856 |
| Schematic files | 36,577 |
| PCB files | 18,745 |
| Gerber directories | 5,506 |
| EMC analyses | 36,658 |
| SPICE simulations | 36,552 |
| Components parsed | 1,305,560 |
| Nets traced | 2,089,813 |
| Regression assertions | 2,239,678 at 100% |
| Bugfix guards | 76 (100% — no regressions) |
| Closed issues | 275 analyzer + 8 harness |
| Open issues | 0 |
| Schematic detectors | 65 |
