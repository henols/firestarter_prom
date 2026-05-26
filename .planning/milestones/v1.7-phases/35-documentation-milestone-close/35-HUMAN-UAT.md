---
status: complete
phase: 35-documentation-milestone-close
source: [.planning/phases/35-documentation-milestone-close/35-VERIFICATION.md]
started: 2026-05-25T21:17:29Z
updated: 2026-05-26T07:35:00Z
---

## Current Test

[complete — firmware-side PASS on all 3 UATs; §8 OPEN R41-value-in-isolation deferred to v1.8 backlog per Gaps]

## Tests

### 1. UAT-1 — Sideload Phase 35 firmware (3.0.0b5) to operator's Rev 2.0 board; confirm `MSG_OK_REV` report
expected: Detected silkscreen-rev string surfaces in handshake/log. Either `Rev 2.0-class` (R41-equipped) or `rev_unknown` (pre-detect-resistor / guard-gap) is acceptable per the DETECT-FW-02 backward-compat fall-through clause. With Plan 01 CR-01 fix landed (`INPUT` high-Z replaces `INPUT_PULLUP` at `firestarter/include/rurp_hw_rev_utils.h:60-61`), the band math now matches RESEARCH §ADC Voltage Band Math.
why_human: Physical hardware sideload + serial log inspection required. Per memory `feedback_chip_out_before_sideload` — chip OUT of socket before any firmware sideload. Per memory `feedback_verify_port_identity_each_task` — verify `controller:` identity per port at task start.
result: [pass] — Rev 2.0 board on `/dev/ttyACM0` (Uno) reports `OK: Rev 2.0-class, Override HW: Rev 2.0-class` after sideloading `3.0.0b5:uno`. 5/5 boots stable. No `WARN: HW: rev_unknown` emitted (detect lands cleanly in the 4k7 bucket). Evidence: `.planning/v1.7/bench-evidence-35.md` §"Rev 2.0 Board" boot logs 1-5.

### 2. UAT-2 — Sideload Phase 35 firmware to operator's Rev 2.2 board; capture `MSG_OK_REV` report + measure R41
expected: `MSG_OK_REV` reports `Rev 2.0-class` (if R41 measures ≈ 4.7 kΩ per upstream schematic) OR `Rev 2.3` (if R41 measures ≈ 10 kΩ per Anders chat-intel). Multimeter measurement of R41 on the physical Rev 2.2 PCB resolves the §8 OPEN annotation in `.planning/v1.7-SHIELD-REVS.md` (Phase 35 follow-up #5). Either outcome closes v1.7 cleanly; the measurement is the operator-attested ground truth.
why_human: Resolves a documented OPEN discrepancy through physical hardware measurement; firmware-side detection alone cannot adjudicate which schematic source is correct without the multimeter reading.
result: [pass-firmware-side; §8-OPEN-inconclusive-via-A3-GND-method] — Rev 2.2 board on `/dev/ttyUSB0` (plain Uno w/ wrong-FW `uno328pb` build — orthogonal to UAT) reports `OK: Rev 2.0-class` after sideloading `3.0.0b5:uno328pb`. 5/5 boots stable. Operator multimeter A3↔GND header pins, board OFF: **Rev 2.2 = 20 kΩ, Rev 2.0 = 27 kΩ** (2026-05-26). The two-board comparison shows this measurement method does NOT isolate R41 — it includes ATmega input-protection leakage paths to GND with the chip unpowered. R41 in isolation still pending (lift-one-leg measurement or visual inspection of R41 markings). Schematic value (4.7 kΩ) NOT contradicted by these readings. §8 OPEN resolution carried as v1.8 backlog rather than blocking v1.7 close. Evidence: `.planning/v1.7/bench-evidence-35.md` §"R41 measurement attempt" + §"Band-math semantics under Plan 01 INPUT high-Z" (Phase 34 §8 ASCII correction also lands in Wave 4).

### 3. UAT-3 — CR-01 misclassification cross-check across multiple boots on both boards
expected: Each board reports a stable per-rev string across ≥ 3 boot cycles. If a 4k7-bucket board lands at ADC ≈ 200..220 (the narrow guard gap from CR-02), `rev_unknown` is acceptable — documented intentional behavior; EEPROM `hw_revision` override (`firestarter rev <N>`) is the escape hatch. Does NOT violate SC #4. The Plan 01 CR-01 fix (high-Z `INPUT` mode) should eliminate the pull-up-induced shift; UAT-3 empirically confirms.
why_human: Bench characterization of real silicon — pull-up shift magnitude is silicon/AVcc-load dependent and cannot be measured statically. Already surfaced as `34-REVIEW.md` CR-01 / CR-02; carried into Phase 35 Wave 2 per D-05.
result: [pass] — 5 boots × 3 boards (Rev 2.0 / Rev 2.2 / Modified Rev 0 opportunistic) = 15 reads. 100% stable, no `rev_unknown`, no band-flapping. CR-01 INPUT high-Z fix confirmed effective; CR-02 hard-fail-loud `WARN: HW: rev_unknown` emit doesn't fire because no board lands in the `[ADC_BAND_R41_4K7_HIGH=200, ADC_BAND_R41_10K_LOW=220)` guard gap. Bonus finding: Modified Rev 0 detects as `Rev 2.3` (10k bucket) — operator's mod intentionally rewired the divider to 10k. Evidence: `.planning/v1.7/bench-evidence-35.md` §"UAT cross-board summary".

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0
deferred: 1  # UAT-2 §8 OPEN R41-isolation → v1.8 backlog (non-blocking)

## Gaps

- **UAT-2 §8 OPEN R41-value-in-isolation** — operator A3↔GND header-pin readings (Rev 2.0=27 kΩ, Rev 2.2=20 kΩ, board OFF) do NOT isolate R41 because the path includes unpowered-ATmega leakage. **Definitive resolution requires either:** (a) lift one R41 pad (desolder one leg) and measure across — invasive; (b) visually read R41's markings (THT color bands or SMD code) — non-invasive but requires locating R41 on the PCB; (c) carry forward as v1.8 backlog item. **Phase 35 close decision: option (c)** — schematic value (4.7 kΩ) is NOT contradicted by the existing readings, firmware-side detection is verified PASS on both boards, and Wave 4 D-02 threshold widening is moot under Plan 01 INPUT high-Z (band math no longer depends on R41 value). Cross-ref: `bench-evidence-35.md` §"R41 measurement attempt" + §"Band-math semantics under Plan 01 INPUT high-Z".
- **D-06 photos** — operator-decided skip for this milestone close. Photos directories scaffolded by Task 1 stay in place for future milestones; not required for git commit (JPGs gitignored anyway).
- **`/dev/ttyUSB0` wrong-FW persistence** — `firestarter fw -i -b uno` honors existing FW's controller-string auto-detect over `-b` flag. Board still runs `uno328pb` build on plain-Uno silicon. Carry-forward as v1.8 backlog (per memory `[[project_uno328pb_correction]]`); does NOT block Phase 35 close (detect-rev is FW-build-independent).
- **Raw ADC not exposed by FW** — and now moot under Plan 01 INPUT high-Z. Wave 4 threshold "widening" per D-02 is no longer needed; replaced by §8 ASCII correction in Wave 4 documenting the actual band-math semantics (characterizes A3-net composition, not R41 value).
- **Phase 34 §8 ASCII stale** — the §8 ASCII attributes R_top to the MCU internal pull-up, which Plan 01 disabled by switching to INPUT mode. Wave 4 must update §8 ASCII + §9 footnotes to reflect that bands now characterize A3-net composition. Cross-ref: `bench-evidence-35.md` §"Band-math semantics under Plan 01 INPUT high-Z".
