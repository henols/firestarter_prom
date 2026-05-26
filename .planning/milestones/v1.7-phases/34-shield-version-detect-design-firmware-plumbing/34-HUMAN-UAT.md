---
status: partial
phase: 34-shield-version-detect-design-firmware-plumbing
source: [.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-VERIFICATION.md]
started: 2026-05-25T17:05:00Z
updated: 2026-05-25T17:05:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Sideload Phase 34 firmware to operator's Rev 2.0 board and confirm `MSG_OK_REV` report
expected: Detected silkscreen-rev string surfaces in handshake/log. Either `Rev 2.0-class` (if R41-equipped) or `rev_unknown` (if pre-detect-resistor) is acceptable per the backward-compat fall-through clause.
why_human: Physical hardware sideload + serial log inspection required. Acknowledged in `34-06-SUMMARY.md` Phase 35 hand-off. Per memory `feedback_chip_out_before_sideload` — chip OUT of socket before sideload.
result: [pending]

### 2. Sideload Phase 34 firmware to operator's Rev 2.2 board; capture `MSG_OK_REV` report
expected: If R41 = 4k7 (schematic) → reports `Rev 2.0-class`. If R41 = 10k (Anders chat-intel) → reports `Rev 2.3`. The result resolves the §8 OPEN annotation (Phase 35 follow-up #5).
why_human: Resolves a documented OPEN discrepancy through physical hardware measurement.
result: [pending]

### 3. Confirm CR-01 (INPUT_PULLUP active during analogRead) does not silently misclassify on bench
expected: Each board reports a stable per-rev string across multiple boots. If a 4k7-bucket board lands at ADC ≈ 200..220 (the narrow guard gap from CR-02), it would report `rev_unknown` — flagged as known Phase 34 follow-up but does NOT violate SC #4 (rev_unknown fall-through + EEPROM hw_revision override preserved).
why_human: Bench characterisation of real silicon — pull-up shift magnitude is silicon/AVcc-load dependent and cannot be measured statically. Already surfaced as `34-REVIEW.md` CR-01 / CR-02.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
