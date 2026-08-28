---
phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig
plan: 05
subsystem: bench, on-device
tags: [bench, on-device, cell-CHIP, leonardo, atmega32u4, rev-2-0, dip28, vpp-12v, parts-1-2, sweep-position, control-arm-arbitration]

requires:
  - phase: 162-01
    provides: "rig-pins.json's 11-part chips map, CHIPS-MAP-DERIVATION.md, PRE-PHASE.md's CLOSE-04 before-count and A3/B2 anchors"
  - phase: 162-02
    provides: "bench/CHIP-EVIDENCE.jsonl's schema and tools/append_chip_evidence.py"
  - phase: 162-04
    provides: "PROCEDURE.md's Chip-sweep step list (C-01..C-09) and render_steps.py --section C"
provides:
  - "bench/cells/CHIP/ opened: PREFLIGHT.md (non-null fw_board_identity proven before any part ran), POT.md (VPP record including a retracted-and-corrected finding), CELL.md (both positions' full record plus the C-08 arbitration and two self-caused-deviation disclosures)"
  - "Two CHIP-EVIDENCE.jsonl rows: CHIP__v133__w27c512 (same, validated — the phase's first measured dev test duration and the real 64 KiB ceiling) and CHIP__v133__w27e512 (diverges, validated)"
  - "One control-arm arbitration row, CHIP__control__w27e512, control_rerun_for=CHIP__v133__w27e512 — SC#4 balanced at 1:1"
  - "append_chip_evidence.py: --pending-readback flag (chip-sweep positions never flash on their own), repeat_policy/read_divergence derivation fixes, and a whole-row required-field self-check added as defense in depth"
affects: [162-06, 162-07, 162-08, 162-09, 162-10]

tech-stack:
  added: []
  patterns:
    - "A chip-sweep position's row is validated against gate_record's FULL record_keys list, not just the four human-supplied fields, immediately after build_row() and before either --dry-run's return or the real write — catches a derivation bug at append time instead of a later, separate full-file gate run"
    - "A firmware flash from this executor's sandboxed Bash tool needs env -C <dir> <cmd>, never cd <dir> && <cmd> nor <cmd> -d <dir> — cwd, exported PATH, and exported shell functions do not persist across this harness's Bash calls, and PlatformIO's own project-config resolution runs unconditionally before any subcommand flag is parsed"
    - "Never pass markdown containing backtick-quoted code snippets to git commit -m as a plain string — bash command-substitutes backtick pairs even inside a quoted -m argument; use git commit -F <file> for any message containing backticks"

key-files:
  created:
    - .planning/v1.34/bench/cells/CHIP/PREFLIGHT.md
    - .planning/v1.34/bench/cells/CHIP/POT.md
    - .planning/v1.34/bench/cells/CHIP/CELL.md
    - .planning/v1.34/bench/cells/CHIP/provenance_CHIP__v133__w27c512.json
    - .planning/v1.34/bench/cells/CHIP/provenance_CHIP__v133__w27e512.json
    - .planning/v1.34/bench/cells/CHIP/provenance_CHIP__control__w27e512.json
    - .planning/v1.34/bench/cells/CHIP/READBACK-VERDICT.json
    - .planning/v1.34/bench/cells/CHIP/readback_control/
    - .planning/v1.34/bench/cells/CHIP/readback_control_restore_v133/
    - .planning/v1.34/bench/cells/CHIP/readback_final_confirm/
    - .planning/v1.34/bench/cells/CHIP/reports/CHIP__v133__w27c512.{json,md}
    - .planning/v1.34/bench/cells/CHIP/reports/CHIP__v133__w27e512.{json,md}
    - .planning/v1.34/bench/cells/CHIP/reports/CHIP__control__w27e512.{json,md}
    - .planning/v1.34/bench/cells/CHIP/human-inputs/*.txt, *.json
  modified:
    - .planning/v1.34/bench/CHIP-EVIDENCE.jsonl
    - .planning/v1.34/bench/CHIP-EVIDENCE.md
    - .planning/v1.34/tools/append_chip_evidence.py

key-decisions:
  - "Position 1's C-03 pot finding was corrected mid-plan: the orchestrator's first framing (a ~600 mV drift since Phase 161) was itself wrong — it cited A3/B2's superseded pre-adjustment reading, not its settled state. Retracted in POT.md rather than silently overwritten, with the correct sequence (11.4 V correctly inherited -> mistaken up-adjustment to 11.97 V produced a 12800 mV over-guard reading -> corrected to 11.6 V / 12400 mV, in band) recorded as its own atomic commit"
  - "Position 2 (W27E512) reported outer verdict OK on every step, which on its own would contradict the pre-declared v1.15 Phase 82 stuck-erase-bit disposition. Classified as diverges, not same, because the coordinator's own D-05 test (does the symptom match the recorded disposition) fails: no failure at all is not the symptom reproducing. known_carried was deliberately NOT set to the bare 'no' (nor blindly to 'yes') — its text lays out that whether the defect reproduced is exactly the open question the control-arm arbitration answers"
  - "The divergence characterisation was sharpened once, live, after the coordinator pointed out three internal report indicators (read.reason='read runs diverged', write/verify.fingerprint='indeterminate') consistent with the recorded defect still being present but unreported at the outer verdict layer — corrected from an initial, too-strong 'symptom absent / may have healed' framing to 'OK while internal indicators are consistent with the defect; the report never exports the values that would settle it'"
  - "The control-arm result (also OK, also indeterminate write/verify fingerprints, only the read.reason difference did not reproduce) was reported plainly as NOT a v1.33 regression, per the explicit instruction not to bend the result toward the more dramatic conclusion in either direction. The v1.15 disposition is filed as needing revisiting by Phase 165/166, not adopted as fixed by anything in this milestone"
  - "append_chip_evidence.py's READBACK-VERDICT.json load was unconditional for every position (inherited from the WRV sibling, where every position genuinely flashes-and-reads-back); a chip-sweep position only does that on a divergence. Fixed with an additive --pending-readback flag rather than weakening the check — default behaviour (flag omitted) is byte-for-byte unchanged, and a control-rerun row still hard-requires a real judged read-back"
  - "repeat_policy's healthy-case value was changed from a bare empty string to a descriptive non-blank string, and read_divergence's unconditional None was changed to the schema's own not-measured shape naming the exact host-app export gap — both found live when the orchestrator's own run_gates.sh caught gate_record RED on position 1's row after this executor's checkpoint had (correctly, but incompletely) reported only the render gate as green"
  - "A firmware flash on this executor's sandboxed Bash tool requires env -C <dir> <cmd> — cd as a separate call, -d/-c flags, and a PATH-shim script were all tried and either failed technically (Pitfall 4 fires regardless of -d/-c) or were blocked by the harness's own auto-mode permission classifier (the PATH-shim), which was correctly treated as a stop-and-report signal rather than something to route around further"

patterns-established:
  - "A chip-sweep position's divergence_verdict is judged against the REPORT'S OWN INTERNAL FIELDS (step reason strings, fingerprint buckets), not just the outer OK/BAD verdict — an all-OK report can still diverge from a recorded FAIL disposition if those internal fields are consistent with the original defect"
  - "A control-arm arbitration that returns the SAME result as the diverging v133 row (not a hard FAIL) is an equally valid, equally reportable outcome — it rules out v1.33 attribution rather than confirming it, and must be stated with the same plainness as the more dramatic alternative would have been"

requirements-completed: []

# Coverage omitted per this plan's own explicit instruction: "This plan produces the first two of
# ten positions. It closes none of CHIP-01…CHIP-05 ... Do not mark any CHIP requirement complete
# here." Full ten-position coverage closes only in plan 162-10's reconciliation.

duration: 1h 49m
completed: 2026-08-28
status: complete
---

# Phase 162 Plan 05: Cell CHIP — Session Open, Positions 1-2 (W27C512, W27E512), Control-Arm Arbitration Summary

**Opened the 11-part chip sweep's bench cell on the standing Leonardo + Rev 2.0 rig: W27C512 ran clean (`same`, matching v1.34's own A3/B2 result and v1.16's PASS) and supplied the phase's first real `dev test` duration and 64 KiB ceiling; W27E512 diverged from its pre-declared stuck-erase-bit disposition in a way that needed a full control-arm arbitration — which came back with the SAME result on pre-v1.33 firmware, ruling out a v1.33 regression rather than confirming one.**

## Performance

- **Duration:** 1h 49m
- **Started:** 2026-08-28T21:18:09Z
- **Completed:** 2026-08-28T23:07:00Z
- **Tasks:** 5 of 5 (2 checkpoints, 3 auto; one auto task's divergence required an interleaved control-arm arbitration not itself a numbered task)
- **Files modified:** ~60 (see `key-files`; the bulk is per-position artifacts under `bench/cells/CHIP/`)

## Accomplishments

- Firmware identity proven non-null (`3.0.0b22:leonardo`) before any part ran (CHIP-02's hard pre-flight requirement), after working through a genuine live port-identity shuffle (ttyACM0 -> ACM1 -> ACM0, one transient I/O error) rather than assuming a number.
- Position 1 (W27C512): all six `dev test` steps OK, `divergence_verdict: same`, matching both v1.34 cell A3/B2's own judged full-device result on this exact rig and v1.16 Phase 91's PASS. Supplied the phase's first measured `dev test` total (214s wall-clock) and the real 64 KiB class ceiling (4×214s = 856s), superseding the 500s derived-fallback estimate.
- Position 2 (W27E512): outer verdict OK on all six steps, but the report's own `read.reason` and `write`/`verify.fingerprint` fields are consistent with the recorded v1.15 Phase 82 deterministic stuck-erase-bit disposition still being present and merely unreported — classified `diverges`, not folded into `known_carried`.
- Full C-08 control-arm interleave completed on the same seated, unmoved chip: control firmware flashed and proven by independent read-back (not upload exit code), `dev test` re-run on the control arm, and the same OK-with-indeterminate-fingerprint shape reproduced. Reported plainly: **not a v1.33 regression** — the v1.15 disposition needs revisiting by Phase 165/166 instead. Re-flashed and re-proven back to v1.33.
- `append_chip_evidence.py` gained a genuine defect fix (a whole-row required-field self-check) after the orchestrator's own `run_gates.sh` caught a gate failure this executor's own checkpoint had missed — documented plainly rather than smoothed over.
- SC#4 balances exactly: 1 diverging v133 row, 1 control row. `run_gates.sh` exits 0, 14/14 selftests, 7/7 live gates, `ALL GATES PASSED`, record-shape gate explicitly checked (not just the render gate).

## Task Commits

1. **Task 1: Session open** — `66f38035` (docs) — rig confirmed (Leonardo/ttyACM0, Rev 2.0, W27C512 seated JP4 28-pin), first VPP finding recorded
2. **Task 2: Pre-flight** — `3c9526b0` (docs) — port re-verified by signature, v1.33 arm confirmed, `fw_board_identity` non-null before any part ran
   - C-03 finding (VPP over the high guard) — `4355c99e` (docs)
   - Correction — retracted false drift finding, orchestrator error — `bb6a4754` (docs)
3. **Task 3: Position 1 (W27C512)** — `d7b613f0` (feat) — `dev test` PASS, `same` verdict, 64 KiB ceiling measured
   - Gate fix — `e8e2b56b` (fix) — `repeat_policy`/`read_divergence` corrected at the derivation layer after `run_gates.sh` caught the row RED
4. **Task 4: Chip swap checkpoint** — no code commit (physical action only; recorded inline in Task 5's own commit)
5. **Task 5: Position 2 (W27E512) + C-08 control-arm arbitration** — `bd798f98` (feat) — divergence finding, control-arm re-run, both flashes independently read-back-proven
   - Self-disclosed deviation — `b149caa2` (docs) — a stray `pio` flash caused by a backtick in the prior commit message, investigated and confirmed harmless

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `.planning/v1.34/bench/cells/CHIP/PREFLIGHT.md` — port/arm/identity pre-flight record
- `.planning/v1.34/bench/cells/CHIP/POT.md` — full VPP record for the 12 V group, including the retracted-and-corrected drift finding and the position-1/position-2 firmware readings
- `.planning/v1.34/bench/cells/CHIP/CELL.md` — both positions' full record, the C-08 arbitration, the erase-duration/fast-fail-assumption check, two self-caused-deviation disclosures, and the leave-state declaration
- `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` / `.md` — three new rows (2 primary, 1 control)
- `.planning/v1.34/tools/append_chip_evidence.py` — `--pending-readback` flag, `repeat_policy`/`read_divergence` derivation fixes, whole-row required-field self-check (19 selftest legs pass, 18 prior + 1 new)
- `.planning/v1.34/bench/cells/CHIP/reports/`, `provenance_*.json`, `readback_control/`, `readback_control_restore_v133/`, `readback_final_confirm/`, `human-inputs/`, `logs/` — full per-position and per-flash evidentiary artifacts

## Decisions Made

See `key-decisions` in frontmatter. In prose: this plan surfaced and corrected two of its own mistakes live (a mis-cited VPP baseline, and a gate-failing row) and disclosed a third (a stray flash from a backtick in a commit message) — all three are recorded in the artifacts rather than smoothed over, per this project's standing disclosure convention.

## Deviations from Plan

### Auto-fixed / self-corrected issues

**1. [Rule 1 - Bug] `append_chip_evidence.py`'s unconditional `READBACK-VERDICT.json` load**
- **Found during:** Task 3 (C-04, position 1)
- **Issue:** The tool hard-refused every chip-sweep position because it required a read-back-verdict artifact that only a divergence's `C-08` ever produces.
- **Fix:** Added an additive `--pending-readback` flag; default behaviour unchanged.
- **Files modified:** `.planning/v1.34/tools/append_chip_evidence.py`
- **Committed in:** `d7b613f0`

**2. [Rule 1 - Bug] `repeat_policy`/`read_divergence` derivation bugs, caught by `run_gates.sh` RED**
- **Found during:** post-Task-3 checkpoint, by the orchestrator's own independent gate run (not by this executor)
- **Issue:** `repeat_policy`'s healthy-case value was a bare `""`, and `read_divergence` was an unconditional `None` — both fail `gate_record.check_required_fields`'s universal non-blank rule.
- **Fix:** `repeat_policy` now returns a descriptive non-blank string for the healthy case; `read_divergence` returns the schema's own `not measured — <reason>` shape naming the real host-app export gap (`diagnostic_report.py` never serializes `steps[].divergence`). Added a whole-row self-check as defense in depth.
- **Files modified:** `.planning/v1.34/tools/append_chip_evidence.py`; corrected row re-appended.
- **Committed in:** `e8e2b56b`

**3. [Rule 1 - Bug, self-caused] A backtick in a `git commit -m` string executed as a real command**
- **Found during:** Task 5's own commit
- **Issue:** A markdown code-span inside a plain `-m "..."` string was command-substituted by bash, causing an unintended third `pio run -t upload -e leonardo`.
- **Fix:** Investigated immediately; `firestarter/` was already at the correct v1.33 SHA, so the stray rebuild wrote byte-identical content (confirmed by an extra independent read-back proof, matching whole-flash SHA). No corrective action needed beyond verification. Commit messages containing backticks now go through `git commit -F <file>`.
- **Files modified:** none (verification only); disclosed in `CELL.md`.
- **Committed in:** `b149caa2`

---

**Total deviations:** 3 (2 tool bugs fixed at the correct layer, 1 self-caused process mistake investigated and confirmed harmless).
**Impact on plan:** All three were caught and resolved within this plan's own session, before any position's row was finalized. No scope creep — every fix was scoped to the exact defect found, and no gate, schema, or required-field list was weakened to make a row pass.

## Issues Encountered

- **Live port-identity shuffle** (Task 2): the Leonardo bounced between `/dev/ttyACM0` and `/dev/ttyACM1` across a touch/probe/kill sequence. Worked through by signature re-verification rather than assumed away; the working sequence (touch immediately followed by probe, no interposed command) is the one whose result is authoritative.
- **Bash-tool default timeout aborted `dev test`'s first invocation** (Task 3): the outer harness's 120s default fired before this task's own intended 500s ceiling could. Logged as an executor tooling mistake (not a PD-15 ceiling kill, not a P-H1 rig finding); the clean retry completed normally.
- **The C-08 flash needed a non-obvious invocation shape**: neither cross-call `cd`, nor `-d`/`-c` flags, nor a PATH-shim script (blocked by the harness's own classifier) worked. The working form, confirmed live: `env -C /workspaces/firestarter pio run -t upload -e leonardo`.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 162-06 inherits this plan's leave-state at zero physical cost: Leonardo at `/dev/ttyACM0`, v1.33 arm flashed and independently read-back-proven, W27E512 seated (DIP28, JP4 28-pin, unchanged since Task 4), pot at meter 11.6 V / firmware 12400 mV (in band), Rev 2.0 shield mounted. No blockers. The `diagnostic_report.py` export gaps (`steps[].divergence` never serialized; `total`/`bad`/`bad_pct`/`evidence` behind the `indeterminate` fingerprint bucket dropped before export) and the W27E512 disposition-needs-revisiting finding are both filed in `CELL.md` for Phase 165/166's backlog — not fixed here (D-16 boundary: no product-code changes).

---
*Phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig*
*Completed: 2026-08-28*
