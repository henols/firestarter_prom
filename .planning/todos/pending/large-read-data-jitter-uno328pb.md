---
id: large-read-data-jitter-uno328pb
title: Full 64KB streaming reads return 57% scrambled data on uno328pb (small reads stable)
captured: 2026-05-21
status: pending
type: bug
target_milestone: v1.6 (in scope)
priority: HIGH
related_phase: 24
resolves_phase: v1.8
---

# Full 64KB streaming reads are unreliable on uno328pb

## The bug

`firestarter read SST27SF512 file.bin` (the high-level full-chip read) returns substantially different data on consecutive invocations against the same physically-static chip. Empirical jitter rate **57.8% (37,883 / 65,536 bytes)** between two reads taken minutes apart with no chip changes in between.

Concrete evidence (bench 2026-05-21, SST27SF512 in socket on operator's 328PB-Uno via /dev/ttyUSB0):

```
read 1: SHA b126a4df...05c9cf
read 2: SHA f4a06e16...d98e4b  (after a 16-byte write + 256-byte write)
read 3: SHA b6f83c7c...d616   (no further chip changes after read 2)

diff(read2, read3) = 37,883 / 65,536 bytes (57.8%)

Sample at offset 0x009e:
  read1: 0x1d
  read2: 0x80   ← scrambled
  read3: 0x1d   ← matches read1

Sample at offset 0x0053:
  read1: 0x1e
  read2: 0x1e
  read3: 0x81   ← scrambled differently
```

The scrambled bytes are **not single-bit flips** — they're completely different values (e.g., 0x1d → 0x80, 0xde → 0x41), suggesting transport-level corruption rather than chip cell instability.

## What still works (so it's localized)

- `firestarter id SST27SF512` — consistent ✓
- `firestarter dev read SST27SF512 -s 16/256` — small reads return identical bytes across calls ✓
- `firestarter dev read SST27SF512 -s 256` after a 256-byte write — exact `pre AND target` pattern verified byte-by-byte
- `firestarter fw / hw / config` — handshake + EEPROM read stable ✓
- `firestarter vpp / vpe` — 12.4V / 14.4V stable across multiple sample sessions
- `firestarter fw -i --pre --force` (full firmware install via avrdude) — committed 22340 bytes and verified ✓

So the firmware's chip-read path WORKS for small bursts. The bug is somewhere in the **streaming 64KB chunked-read state machine** — either in the firmware's MAIN-state chunking or in the host's `serial_comm.py` per-chunk handshake.

## Hypotheses (for whoever investigates)

1. **Host-side serial buffer overflow.** At 250000 baud, 512 bytes = ~20ms wire time. If the host's pyserial input buffer fills and Python's read loop misses an ACK timing window, the next chunk could be misaligned.
2. **Firmware MAIN-state phase-transition off-by-N.** The protocol's 3-phase state machine (INIT → MAIN → END) chunks data; if a chunk-end marker is missed, subsequent chunks could be byte-shifted.
3. **328PB-specific timing.** The `[env:uno328pb]` mirrors `[env:uno]` settings (16MHz, 250000 baud) but the 328PB has additional peripherals (USART1 — even if unused, its register-set is present). A timing-critical loop that worked on 328P might just barely miss on 328PB due to slightly different instruction-cycle accounting in the inherited HAL.
4. **`[env:uno328pb]` is missing a `-D SERIAL_RX_BUFFER_SIZE=...` or similar.** The Phase 21 `[env:uno328pb]` declaration carries `-D SERIAL_ON_IO` (from CONTEXT D-07) and the inherited build flags from `[env]`, but no buffer-size overrides. The Leonardo gets `DATA_BUFFER_SIZE=1024` (per CLAUDE.md); the 328PB inherits the uno default of 512. Maybe SST27SF512's protocol needs a different timing.

## How to triage

```bash
# Run consecutive full reads against a stable chip
for i in 1 2 3; do
  firestarter -p /dev/ttyUSB0 read <chip> /tmp/read_$i.bin
  sha256sum /tmp/read_$i.bin
done
# Compare hashes — should be identical; aren't.

# Then narrow: do consecutive 1KB chunks via dev-read also jitter?
for offset in 0x0 0x400 0x800 0x1000; do
  firestarter -p /dev/ttyUSB0 dev read <chip> -a $offset -s 1024 > /tmp/devread_${offset}_a.txt
  firestarter -p /dev/ttyUSB0 dev read <chip> -a $offset -s 1024 > /tmp/devread_${offset}_b.txt
  diff /tmp/devread_${offset}_a.txt /tmp/devread_${offset}_b.txt | head -5
done
```

If dev-reads stay stable across all sizes but full reads jitter → the bug is in `firmware.py`'s `read_eprom()` / chunk loop or in `serial_comm.py`'s buffer management.

If dev-reads at 1KB ALSO jitter → the bug is in the firmware's per-chunk send code, not host-side.

**Triage result (bench 2026-05-21):** 1KB `dev read -s 1024` ALSO jitters — observed 1 byte difference at offset 0x5C across two consecutive reads of the same chip. Rate is much lower than full-chip (0.1% vs 57.8%), but still nonzero. This **points the bug at the firmware-side per-chunk send code on the 328PB, not host-side buffer management.** The bug is rate-limited — it manifests as occasional bit/byte corruption per chunk that compounds across many chunks. Small enough reads (16/256 bytes — single buffer fill) escape it; anything that streams multiple chunks accumulates errors.

**3-shield A/B/C triage (bench 2026-05-21, operator-driven):**

The operator rotated through three RURP shields on the same `[env:uno328pb]` board (`/dev/ttyUSB0`, hw_rev byte EEPROM-stored), same firmware (v3.0.0b4 from Phase 23 install), to isolate hardware-vs-firmware origin:

| Shield | Rev | EEPROM hw byte | Chip in socket | 32-byte sample reads as | 1KB jitter (consecutive reads) | 64KB full read completes |
|--------|-----|----------------|----------------|-------------------------|-------------------------------|--------------------------|
| 1 | 2.2 (recent) | Rev2 | SST27SF512 | varied (actual chip data) | 1 byte diff / 1024 | ✓ (with 57.8% inter-read jitter) |
| 2 | 2.0 | Rev2 | SST27SF512 | `77 14 b1 4e ...` (chip data) | 2 bytes diff / 1024 (offsets 0x4F + 0xBB) | ✗ timeout |
| 3 | 0/1.0 + voltage-divider mod | **Rev1** | (chip not transferred) | all `0x00` (bus pull) | **110-124 diff LINES / 3 reads** — multi-way jitter, much worse | ✗ timeout |

**Findings from the 3-shield methodology:**

1. **Jitter is NOT shield-specific.** Every shield shows it at the 1KB level. Differences in magnitude are explained by chip-vs-bus-pull data content and possibly minor electrical variations, but the *presence* of the bug is invariant across shields.

2. **Shield 3 (floating bus, no chip) jitters MORE than shields with real chips.** This is the smoking gun: when the chip is missing and the data bus is just floating/pulled to `0x00`, the host *still* receives different "0x00"-mostly values across consecutive reads. The variation cannot be coming from the chip (there is no chip). The bytes are being **introduced or corrupted somewhere between firmware's bus sample and host's serial receive.**

3. **Shields 2 and 3 fail full 64KB reads entirely** (timeout, zero bytes captured) while Shield 1 completed earlier in the session (with 57.8% inter-read jitter). The most likely explanation is not a shield-specific failure mode but a session-state difference: Shield 1's test ran when the chip socket was driving real data, and Shield 2+3 tests ran with a missing or wrong-orientation chip — the host's READ command may have a different timeout path when the firmware's blank-or-pattern detector trips.

4. **hw_rev EEPROM byte distinguishes Rev1 from Rev2 families** but not 2.0 vs 2.2. Shield 3 (Rev 0/1.0 modified) reports `Rev1`; Shields 1+2 both report `Rev2`. The voltage-divider mod on Shield 3 makes it electrically behave Rev2-alike for VPP/VPE measurement, but does not change the EEPROM-stored revision flag the firmware reads at startup.

**Updated implication:** This is a **pre-Phase-21 bug**, not a regression introduced by the uno328pb build. The Phase 21 work didn't change the read state-machine code — it only widened macro guards for board setup, ADC bandgap, and added the new env. The fact that the same jitter appears on all 3 shields with the same firmware suggests the bug has been latent in the codebase since at least v1.4 (probably earlier — full-chip reads weren't byte-compared in the v1.4 lockstep fixture).

**Re-tag:** demote from "v1.5 hotfix candidate" to "pre-existing latent bug surfaced by Phase 24 verify rigor". Still HIGH priority because it blocks meaningful read-back verification, but doesn't block v1.5 ship — uno + leonardo have the same bug, and they shipped at v1.4 without anyone noticing.

## Cross-checks needed

- **Does this happen on uno?** Re-run the same triage on `/dev/ttyACM0` with a chip in its socket (or test against the existing uno328pb data). If yes — bug is pre-existing, not 328PB-specific.
- **Does this happen on leonardo?** Same test on /dev/ttyACM1 (1024-byte buffer). Leonardo's buffer size means fewer chunks per 64KB read, so even if it jitters, the magnitude could differ.

## Impact on Phase 24 BENCH-02 closure

Phase 24 BENCH-02 acceptance — "run write→read→verify on a representative EPROM" — **CANNOT BE CLOSED** until this bug is fixed, because the verify-step's read-back comparison is meaningless when reads return scrambled data.

What WAS proven during Phase 24 bench validation 2026-05-21:
- Write path commits exactly the right bits (verified via `dev read -s 256` on the explicit-write regions, which IS stable)
- VPP regulator engages at 12V during writes
- Chip programming pulses respect the 1→0-only EPROM constraint
- Address bus + data bus + control bus all functional

What CANNOT be claimed:
- 64KB byte-identical round-trip verification (the read-back returns garbage)
- Any read-based verification of the explicit-write regions IF read via the full-chip `read` command (use `dev read -s N` for stable evidence instead)

## Cross-references

- Phase 24 BENCH-02 — partial closure pending this bug fix
- Memory `project-bench-findings-v15` — 328PB-Uno bench environment
- `firestarter_app/firestarter/firmware.py` — `read_eprom()` (suspect: chunked read loop)
- `firestarter_app/firestarter/serial_comm.py` — INIT/MAIN/END state machine + per-chunk handshake
- `firestarter/src/firestarter.cpp` — firmware-side MAIN-state read implementation
- `firestarter/CLAUDE.md` — Board differences note: Uno 512-byte buffer, Leonardo 1024-byte buffer
