---
status: MISATTRIBUTED — retained for Phase 45 (Bug B / Rev 2.0)
recorded: 2026-06-01
board_actual: Rev 2.0 (confirmed: firmware `hw` → "Rev 2.0-class"; operator correction)
board_claimed_in_files: Modified Rev 0 (INCORRECT)
---

# ⚠ MISATTRIBUTED BENCH DATA — NOT Phase 44 / Bug A evidence

The notes and binaries in this directory were captured on **2026-06-01** during a
Phase 44 (Bug A / Modified Rev 0) bench session, under the **mistaken belief** that
the board on the bench was the Modified Rev 0 shield.

**It was actually a Rev 2.0 shield.** This was established two ways:
1. The firmware's own detection: `firestarter hw` → `Hardware revision: Rev 2.0-class`
   (a Modified Rev 0 detects mid-band as `Rev 2.3` via its 10 kΩ A3 pull-up).
2. Operator correction ("let's use the 2.0 shield" → confirmed bench board was Rev 2.0).

Therefore these files do **NOT** satisfy Phase 44 Plan 04, which requires the
**Modified Rev 0** board. Plan 04 remains **incomplete**; the real Modified Rev 0
baseline has not yet been captured.

## Why retained (not deleted)

The data is genuine and potentially valuable for **Phase 45 (Bug B / Rev 2.0)**:

- N=5 consistency-check on a Rev 2.0 / W27C512 / Leonardo (`/dev/ttyACM0`),
  v1.9 firmware 3.0.0b6, default knobs → **5 distinct SHA-256s** (read FAIL).
- **2.41× A15 upper-address skew** (A15=1 1.892% vs A15=0 0.784% divergent offsets)
  and **32.76% 0xff in the upper half** — i.e. this Rev 2.0 board exhibits a
  strong *Bug-A-like upper-address jitter* signature, not only the expected Bug B
  timing/voltage profile. **Worth investigating in Phase 45.**
- Stable chip-ID misread `0xda01` (expected W27C512 `0xda08`); D0 float-high, D3
  low — a data-bus-integrity anomaly on this Rev 2.0 board.

See `baseline-repro-notes.md` (in this dir) for the full numbers. All board-identity
claims of "Modified Rev 0" inside these files are SUPERSEDED by this README.

## Action items

- [ ] Phase 44 Plan 04 must be re-run on the **actual Modified Rev 0** board.
- [ ] Phase 45 should consume this dir as a Rev 2.0 / W27C512 data point.
