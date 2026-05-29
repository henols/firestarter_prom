# Phase 39: Database Cleanup + chip_resolver - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-27
**Phase:** 39-database-cleanup-chip-resolver
**Areas discussed:** resolve_chip() shape & scope, DATA-02 (pin mapping), Star-import breadth, DATA-04 (constants)

---

## Gray-area selection

Presented 4 phase-specific gray areas (multiSelect) with a recommendation baked
into each. Operator **selected all four** to weigh in on (rather than blanket-
delegate as in Phase 38).

---

## resolve_chip() shape & scope (DATA-01)

| Option | Description | Selected |
|--------|-------------|----------|
| 9 op sites only | resolve_chip(name)->programmer-config dict, raises ChipNotFoundError; replaces read/write/verify/blank/erase/id + 3 dev sites; info/list/search keep their own DB calls | ✓ |
| Also absorb info | resolver returns richer bundle (full+programmer+config+manufacturer) so main.py has zero get_eprom/convert_to_programmer | |
| Return full+programmer | resolver hands back both; 9 sites use programmer half, info reuses both | |

**User's choice:** 9 op sites only (Recommended)
**Notes:** Smallest blast radius; info/list/search have genuinely different
presentation data needs, so folding them in would bloat the resolver contract.
Dispatch catches ChipNotFoundError to preserve exact "EPROM '{name}' not found"
log + exit-1 (still argparse in Phase 39; Click mapping is Phase 41).

---

## DATA-02 — pin mapping: document or merge?

| Option | Description | Selected |
|--------|-------------|----------|
| Docstring-only | pin_conversions (socket-pin→bus-line) and pinouts.json (function→socket-pin) are different composing layers, not duplicates; add docstring, zero behavior change | ✓ |
| Actually consolidate | merge one into the other; touches convert_to_programmer translation path; real behavior risk | |

**User's choice:** Docstring-only (Recommended)
**Notes:** ROADMAP SC#2 already resolved the "two sources of truth" as apparent,
not real. Honors GATE-1.8 (no behavior change).

---

## Star-import breadth (DATA-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit named imports | `from firestarter.constants import COMMAND_READ, ...` per module across all 6 star-importing files; strip ~55 obsolete F403/F405 noqas | ✓ |
| Namespace import | `from firestarter import constants` + prefix every reference; large diff, wrecks git blame | |

**User's choice:** Explicit named imports (Recommended)
**Notes:** All 6 files (ROADMAP SC#3 names only 4, but its repo-wide grep
requires all 6 — incl. firmware.py + hardware.py). Documented deviation. Low
churn at usage sites; best mypy traceability.

---

## DATA-04 — "consolidate constants" scope

| Option | Description | Selected |
|--------|-------------|----------|
| Mark + verify only | add `# Firmware sync: firestarter.h` markers to COMMAND_*/FLAG_* blocks; COMMAND_FW_VERSION already present (0x0D) + parity-tested; don't move codegenerated messages.py | ✓ |
| Physically relocate | move scattered command/flag literals into constants.py; risks breaking codegen drift gate (messages.py is generated) | |

**User's choice:** Mark + verify only (Recommended)
**Notes:** messages.py message-IDs are codegenerated from tools/catalog/messages.toml —
relocating them breaks the CI drift gate. Parity test (real name
`test_revision_constants_parity.py`) must stay green.

---

## Claude's Discretion

- Exact named-import lists per module; module/function docstrings; function order.
- `chip_resolver` signature (DB injection vs construct) — follow Phase 36 de-singleton seam.
- Catch-ChipNotFoundError mechanism (shared helper vs per-site try/except), provided observable behavior is byte-identical.
- `test_chip_resolver.py` coverage shape; plan/wave decomposition.

## Deferred Ideas

- Unifying `FirestarterError` base class → Phase 42.
- Centralized Click error→exit-code mapping for ChipNotFoundError → Phase 41/42.
- Folding info/list/search lookups into a richer resolver → considered and rejected for Phase 39.
