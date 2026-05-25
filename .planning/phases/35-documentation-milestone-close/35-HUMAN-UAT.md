---
status: partial
phase: 35-documentation-milestone-close
source: [.planning/phases/35-documentation-milestone-close/35-VERIFICATION.md]
started: 2026-05-25T21:17:29Z
updated: 2026-05-25T21:17:29Z
---

## Current Test

[awaiting operator bench session]

## Tests

### 1. UAT-1 — Sideload Phase 35 firmware (3.0.0b5) to operator's Rev 2.0 board; confirm `MSG_OK_REV` report
expected: Detected silkscreen-rev string surfaces in handshake/log. Either `Rev 2.0-class` (R41-equipped) or `rev_unknown` (pre-detect-resistor / guard-gap) is acceptable per the DETECT-FW-02 backward-compat fall-through clause. With Plan 01 CR-01 fix landed (`INPUT` high-Z replaces `INPUT_PULLUP` at `firestarter/include/rurp_hw_rev_utils.h:60-61`), the band math now matches RESEARCH §ADC Voltage Band Math.
why_human: Physical hardware sideload + serial log inspection required. Per memory `feedback_chip_out_before_sideload` — chip OUT of socket before any firmware sideload. Per memory `feedback_verify_port_identity_each_task` — verify `controller:` identity per port at task start.
result: [pending]

### 2. UAT-2 — Sideload Phase 35 firmware to operator's Rev 2.2 board; capture `MSG_OK_REV` report + measure R41
expected: `MSG_OK_REV` reports `Rev 2.0-class` (if R41 measures ≈ 4.7 kΩ per upstream schematic) OR `Rev 2.3` (if R41 measures ≈ 10 kΩ per Anders chat-intel). Multimeter measurement of R41 on the physical Rev 2.2 PCB resolves the §8 OPEN annotation in `.planning/v1.7-SHIELD-REVS.md` (Phase 35 follow-up #5). Either outcome closes v1.7 cleanly; the measurement is the operator-attested ground truth.
why_human: Resolves a documented OPEN discrepancy through physical hardware measurement; firmware-side detection alone cannot adjudicate which schematic source is correct without the multimeter reading.
result: [pending]

### 3. UAT-3 — CR-01 misclassification cross-check across multiple boots on both boards
expected: Each board reports a stable per-rev string across ≥ 3 boot cycles. If a 4k7-bucket board lands at ADC ≈ 200..220 (the narrow guard gap from CR-02), `rev_unknown` is acceptable — documented intentional behavior; EEPROM `hw_revision` override (`firestarter rev <N>`) is the escape hatch. Does NOT violate SC #4. The Plan 01 CR-01 fix (high-Z `INPUT` mode) should eliminate the pull-up-induced shift; UAT-3 empirically confirms.
why_human: Bench characterization of real silicon — pull-up shift magnitude is silicon/AVcc-load dependent and cannot be measured statically. Already surfaced as `34-REVIEW.md` CR-01 / CR-02; carried into Phase 35 Wave 2 per D-05.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
