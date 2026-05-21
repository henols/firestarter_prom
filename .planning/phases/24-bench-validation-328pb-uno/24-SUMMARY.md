---
phase: 24-bench-validation-328pb-uno
status: complete
shipped: 2026-05-21
type: operator-on-bench
requirements: [BENCH-01, BENCH-02]
requirements_addressed: [BENCH-01, BENCH-02]
---

# Phase 24: Bench Validation on 328PB-Uno — SUMMARY

## Mode

Operator-on-bench, executed inline during the same session as Phase 23 (2026-05-21). Did not go through formal `/gsd-discuss-phase 24` → `/gsd-plan-phase 24` → `/gsd-execute-phase 24` because the scope was operator-driven hardware testing rather than code work.

## What was proven (and what wasn't)

Full evidence and per-row table in `.planning/v1.5-BENCH-RESULTS.md`.

**BENCH-01 (install end-to-end via app on real silicon):** CLOSED ✓
- Cut v1.5 beta pre-release via merge `v1.5-uno328pb` → `firestarter/beta` push → `beta-build.yml` CI → GitHub Pre-release `3.0.0b4` with three `.hex` artifacts
- Ran `firestarter -p /dev/ttyUSB0 fw -i --pre --force` against 328PB-Uno
- Host downloaded `firestarter_uno328pb.hex` from the pre-release (0.51s)
- avrdude flashed 22,340 bytes via `urclock` programmer @ 115200 baud (5.94s)
- Post-flash handshake reports `version 3.0.0b4, controller uno328pb, port /dev/ttyUSB0`
- Hardware revision Rev2, VPP 12.4-12.5V stable, VPE 14.4V stable

**BENCH-02 (write/read/verify EPROM cycle):** CLOSED with caveat ⚠
- Write path bench-validated on SST27SF512: 16-byte and 256-byte writes commit exactly the right bits (verified byte-for-byte via `dev read` on the written regions, where the read protocol is stable)
- VPP regulator engages correctly at 12V during writes
- Read-back byte-identical verification at full 64KB scale is BLOCKED by a pre-existing read-streaming jitter bug (affects uno + leonardo + uno328pb equally; not a v1.5 regression; surfaced by Phase 24's rigor)

## Key bench finding — `programmer_id="arduino"` was wrong

Phase 23 CONTEXT D-02 documented this as a known contingency. Bench validation 2026-05-21 confirmed: the operator's MiniCore-flashed 328PB-Uno bootloader is **Urclock**, not optiboot. The Phase 23 `_install_with_avrdude` elif branch was patched 1-line from `("atmega328pb", "arduino", 115200)` → `("atmega328pb", "urclock", 115200)` in `firestarter_app/v1.5-uno328pb` commit `c184910`. The matching test assertion in `tests/test_firmware_install.py::test_uno328pb_avrdude_profile_resolution` was updated to pin `urclock`. Full pytest suite still 82/82 PASS.

## Bugs surfaced (filed for v1.6+ backlog, do NOT block v1.5 ship)

1. **`.planning/todos/pending/large-read-data-jitter-uno328pb.md`** (HIGH) — Read streaming jitter affecting all controllers. Definitively shown via 3-shield A/B/C triage to be pre-existing, not v1.5-introduced.
2. **`.planning/todos/pending/w27c512-eeprom-misclassification.md`** (HIGH, operator-tagged "asap") — 8 EEPROMs misclassified as UV-only EPROMs in `chip_database.json`. `firestarter erase <chip>` returns `ERROR: Not supported`. NOT a 1-line fix — needs new firmware dispatch path for "12V VPP write + electrical erase" chips, plus per-chip datasheet audit.
3. **`.planning/todos/pending/avrdude-mcu-detection-fallback.md`** (low) — Host-CLI enhancement for blank-chip recovery. Bench-validated the empirical basis (avrdude reveals MCU type via stderr on signature mismatch).

## Branch state

| Repo | Branch | Tip | Pushed to origin |
|------|--------|-----|------------------|
| `firestarter` | `beta` | `62df517` + CI auto-bump → `3.0.0b4` | ✓ pushed; GitHub Pre-release published |
| `firestarter_app` | `beta` | `75db46e` + CI auto-bump → `3.0.0b4` | ✓ pushed; PyPI pre-release published |
| meta | `v1.5-uno328pb` | (will be advanced by Phase 25) | not pushed (will merge to main at milestone close) |

The actual silicon-flashed chip on the operator's bench at end of session: `firestarter_uno328pb.hex` v3.0.0b4 (board reports `uno328pb`).

## Verdict

Phase 24 is **complete** with the BENCH-02 caveat documented and the underlying bug filed for v1.6. Operator authorized "close the milestone" on 2026-05-21 with the read-jitter and DB-misclassification findings on the open backlog. v1.5 itself is solid; the surfaced bugs are pre-existing and orthogonal to the `uno328pb` work.
