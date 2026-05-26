---
status: partial
phase: 28-fix-implementation-unit-test-coverage
source: [28-VERIFICATION.md]
started: 2026-05-26T15:30:00Z
updated: 2026-05-26T15:30:00Z
---

## Current Test

[awaiting human testing — Phase 29 v2 bench session]

## Tests

### 1. Phase 29 v2 bench: FIX-03 bench-side close + Plan 28-04 gate evaluation

expected: Leonardo shape returns to structured-data + ~0.44% jitter (Phase 26 baseline). N=5 reads produce collapsed or near-collapsed SHA-256 hashes (NOT 99% zeros / 0.08% jitter). Outcome closes FIX-03 bench-side half and determines whether Plan 28-04 (conditional second revert of `4f205e58`) needs to activate.

result: [pending]

steps:
- Verify port identity per memory `[[feedback_verify_port_identity_each_task]]` — `/dev/ttyACM*` numbers shuffle across USB re-enumeration.
- Chip OUT of socket before sideload per memory `[[feedback_chip_out_before_sideload]]`.
- Sideload `firestarter/v1.6-read-bug` HEAD (`efd203a`) to Leonardo: `cd firestarter && pio run -t upload -e leonardo`.
- Insert W27C512 chip into RURP shield socket.
- Run: `firestarter -p /dev/ttyACM<N> dev consistency-check W27C512 --runs 5`.
- Append outcome to `.planning/v1.6-EVIDENCE.md` §"Phase 29 v2 bench verification (placeholder)" (the H3 placeholder added by Plan 28-03).

gate_decisions:
- If outcome = structured-data + ~0.44% jitter (matching Phase 26 baseline): Plan 28-04 stays parked permanently. FIX-03 bench-side closes successfully. Phase 28 re-iteration verdict confirmed.
- If outcome = zeros-dominant (still ~99% 0x00 + 0.08% jitter): Plan 28-04 activates. Re-run `/gsd-execute-phase 28 --gaps-only` (or manually re-spawn an executor scoped to Plan 28-04) to land the second revert of `4f205e58` and re-evaluate.

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
