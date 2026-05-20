---
phase: 12
slug: 28-pin-algo-0x07-bench-validation
status: draft
nyquist_compliant: manual-uat
wave_0_complete: false
created: 2026-05-20
---

# Phase 12 — Validation Strategy (Manual UAT Contract)

> **Operator-on-bench phase.** There is NO automated pytest suite. All verification is operator-driven via `firestarter_test.sh` + scope photos + log inspection. This document is the manual-UAT contract that replaces the Nyquist test-mapping pattern for an operator-driven phase.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual UAT — `firestarter_test.sh` is the harness (172 lines, frozen per CONTEXT.md D-02) |
| **Config file** | None — harness reads `firestarter/data/chip_database.json` directly via `firestarter` CLI |
| **Quick run command** | `cd firestarter_app && ./firestarter_test.sh <CHIP_NAME>` (per-cycle; ~5–10 min for 64K density) |
| **Full suite command** | Plans 12-01 + 12-02 + 12-03 executed in sequence by the operator at the bench (3 chips × 2 boards = 6 cycles + 1 PROTO-01 blocked-write capture + 2 PROTO-02 scope photos) |
| **Estimated runtime** | 45–90 min total bench time including chip swaps + scope re-probing for BENCH-05 |

---

## Sampling Rate

- **Per task commit:** No automated test runs. Each task's verification is the operator's PASS/FAIL on the bench plus the corresponding tee'd log line and/or scope photo.
- **Per wave merge:** Each wave is one chip plan (BENCH-01 / BENCH-02 / BENCH-05). Wave-complete = both boards green for that chip + BENCH-RESULTS row written + log files committed.
- **Before `/gsd-verify-work`:** The 5 phase-gate criteria in the "Phase Gate" section below must ALL be true.
- **Max feedback latency:** Operator-paced — each cycle is ~5–10 min; mid-cycle interruption is acceptable (log file is the resume anchor per CONTEXT.md D-14).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Verification Procedure | Evidence Artifact | Status |
|---------|------|------|-------------|------------|-----------------|-----------|------------------------|-------------------|--------|
| 12-04-scaffold | 12-04 | 0 | — (infra) | — | N/A | filesystem | `ls .planning/v1.3-BENCH-RESULTS.md .planning/v1.3/bench-logs/ .planning/v1.3/scope/` returns existing paths | BENCH-RESULTS skeleton + 2 directories | ⬜ pending |
| 12-01-W27C512-uno | 12-01 | 1 | BENCH-01 | — | chip-id-mismatch path enforced by firmware | manual-UAT | Operator runs `./firestarter_test.sh W27C512 2>&1 \| tee ../.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log` on Uno. Log contains "All tests passed". | log file + BENCH-RESULTS row | ⬜ pending |
| 12-01-W27C512-leonardo | 12-01 | 1 | BENCH-01 | — | same | manual-UAT | Same on Leonardo board | log file + BENCH-RESULTS row | ⬜ pending |
| 12-01-protocols-uno | 12-01 | 1 | PROTO-01, PROTO-02 | — | VPP regulator engages 12V ±5% on write | manual-UAT | (a) Grep tee'd log for chip-id line, confirm = 0x0000da08; (b) Scope-capture VPP pin 22 during `firestarter write`, save photo at `.planning/v1.3/scope/uno-vpp-write-2026-05-20.png` | log snippet in row + scope photo | ⬜ pending |
| 12-01-protocols-leonardo | 12-01 | 1 | PROTO-01, PROTO-02 | — | same | manual-UAT | Same on Leonardo (`.planning/v1.3/scope/leonardo-vpp-write-2026-05-20.png`) | log snippet in row + scope photo | ⬜ pending |
| 12-02-SST27SF512-uno | 12-02 | 2 | BENCH-02 | — | same | manual-UAT | `./firestarter_test.sh SST27SF512` on Uno; chip-id = 0x0000bfa4 | log file + BENCH-RESULTS row | ⬜ pending |
| 12-02-SST27SF512-leonardo | 12-02 | 2 | BENCH-02 | — | same | manual-UAT | Same on Leonardo | log file + BENCH-RESULTS row | ⬜ pending |
| 12-02-blocked-write | 12-02 | 2 | PROTO-01 (mismatch leg) | — | firmware refuses write when chip-id ≠ expected | manual-UAT | With SST27SF512 socketed, deliberately run `firestarter write W27C512 data.bin` (no `-f` override). Capture refusal log line `MSG_ERR_CHIP_ID_MISMATCH` or decoded "Chip ID … does not match expected ID". | dedicated PROTO-01 evidence row in BENCH-RESULTS.md | ⬜ pending |
| 12-03-W27C257-uno | 12-03 | 3 | BENCH-05 | — | same | manual-UAT | **Relocate scope probe to pin 1** (DIP28_27256 has VPP on pin 1, NOT pin 22 — Pitfall 1). Run `./firestarter_test.sh W27C257` on Uno; chip-id = 0x0000da02 | log file + BENCH-RESULTS row + (optional) updated scope photo | ⬜ pending |
| 12-03-W27C257-leonardo | 12-03 | 3 | BENCH-05 | — | same | manual-UAT | Same on Leonardo | log file + BENCH-RESULTS row | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements (Plan 12-04 — scaffold, autonomous)

- [ ] `.planning/v1.3-BENCH-RESULTS.md` — skeleton with header + 14-column row schema (per CONTEXT.md D-08) + empty PROTO-01 evidence section + empty PROTO-02 evidence section. Headers-only, no placeholder rows (per RESEARCH.md Open Question Q1).
- [ ] `.planning/v1.3/bench-logs/` directory created (empty; populated by Plans 12-01..03).
- [ ] `.planning/v1.3/scope/` directory created (empty; populated by Plans 12-01..03).
- [ ] Optional sentinel file `.planning/v1.3/bench-logs/.gitkeep` and `.planning/v1.3/scope/.gitkeep` so the empty directories survive git.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full bench cycle on physical chip | BENCH-01 / 02 / 05 | Requires real chip in physical socket + RURP shield + serial-attached Arduino board. Cannot be emulated. | (1) Confirm `firestarter --version` reports installed version. (2) `cd firestarter_app && ./firestarter_test.sh <CHIP>` with chip socketed. (3) Confirm last line of stdout = "All tests passed". (4) Repeat for the other board. (5) Append BENCH-RESULTS row. |
| Chip-ID read against DB | PROTO-01 (match leg) | Real chip yields real signature; comparison value comes from `chip_database.json`. | grep tee'd log for `chip-id` (case-insensitive); confirm hex matches DB value (W27C512=0x0000da08, SST27SF512=0x0000bfa4, W27C257=0x0000da02). Copy 5-line snippet into BENCH-RESULTS row. |
| Chip-ID mismatch → write blocked | PROTO-01 (mismatch leg) | Requires deliberate chip/name mismatch on real hardware to trigger firmware safety stack. | With SST27SF512 socketed, run `firestarter write W27C512 data.bin` (no `-f`). Capture the refusal log line: `MSG_ERR_CHIP_ID_MISMATCH` (0xB9) or decoded "Chip ID … does not match expected ID". Paste into the dedicated PROTO-01 evidence row. |
| VPP regulator engagement | PROTO-02 (engage leg) | Voltage measurement at the chip socket VPP pin; cannot be inferred from firmware logs alone (firmware only knows it asserted the signal, not what voltage was delivered). | Probe DIP socket VPP pin (DIP28_27512 = pin 22; DIP28_27256 = pin 1 — note swap for BENCH-05). Trigger scope on the write cycle. Capture screenshot showing 12V ±5% on the rail with time-base + voltage scale visible. Save as `.planning/v1.3/scope/{board}-vpp-write-{date}.png`. One per board minimum. |
| VPP idle state | PROTO-02 (idle leg) | Same probe, different cycle moment | Optional: capture VPP rail after harness completes, before chip removal. Save as `.planning/v1.3/scope/{board}-vpp-idle-{date}.png`. Confirm voltage = VCC or off. |
| Deferred Phase 08/09 UAT closure | (admin) | These are old human_needed items tracked in STATE.md Deferred Items that close as a byproduct of BENCH-01 passing. | After Plan 12-01 completes, the executor updates the STATE.md Deferred Items table to mark Phase 08 SC#2/SC#3 + Phase 08 HUMAN-UAT.md + Phase 09 Plan-05 Task 3 as resolved (cites BENCH-01 commit hash as the closing evidence). |

---

## Phase Gate (consumed by `/gsd-verify-work`)

Before phase close, ALL of the following MUST be true:

1. **`.planning/v1.3-BENCH-RESULTS.md` exists** with 6 chip-board rows (BENCH-01 uno+leonardo, BENCH-02 uno+leonardo, BENCH-05 uno+leonardo), each with `info` / `write` / `read` / `verify` cells = `OK`.
2. **BENCH-RESULTS.md PROTO-01 evidence row** contains the SST27SF512 blocked-write log snippet showing `MSG_ERR_CHIP_ID_MISMATCH` or decoded "Chip ID … does not match expected ID".
3. **BENCH-RESULTS.md PROTO-02 evidence rows** (one per board) contain measured_vpp_volts within 11.4–12.6V (12V ±5%) with linked scope photo path that resolves to an existing file > 0 bytes.
4. **Per-cycle log files exist** at the paths cited in the BENCH-RESULTS rows. Verify via `ls -l` (file present, size > 0).
5. **STATE.md `Deferred Items` table** no longer shows Phase 08 SC#2/SC#3 or Phase 09 Plan-05 Task 3 as "human_needed" — orchestrator updates these as part of Plan 12-01's commit (CONTEXT.md D-15).

---

## Plan-checker Nyquist gate guidance

When `gsd-plan-checker` runs against the produced plans, the Nyquist verification gate should accept **"manual-only verification"** as the strategy for plans 12-01/02/03. The check should verify:
- Each manual-UAT task references the specific log path or scope photo path that constitutes the evidence.
- The acceptance criteria for each task cite the grep target or filesystem check (e.g. "log contains 'All tests passed'", "photo file exists and size > 0").
- The phase gate criteria 1–5 above are reachable from the plan's tasks.
- Plan 12-04 (scaffold) IS autonomous=true and CAN have automated verification (filesystem assertions).

There is **no acceptable "automated test that would also work"** for hardware-in-the-loop bench validation. Forcing an automated wrapper here would either be a tautological lint of the BENCH-RESULTS.md row format (not load-bearing) or attempt to emulate hardware (out of scope, not feasible). The plan-checker's Dimension 8 Nyquist check accepts this with `nyquist_compliant: manual-uat` in the validation frontmatter.

---

## Validation Sign-Off

- [ ] All bench-cycle tasks reference a specific log path + chip-id grep target + (where applicable) scope photo path
- [ ] No 3 consecutive bench-cycle tasks without manual-UAT evidence (sampling continuity)
- [ ] Plan 12-04 creates the directory structure before any chip plan runs (Wave-0 prereq)
- [ ] No watch-mode flags or attempt-to-automate hardware (out of scope)
- [ ] Phase gate criteria 1–5 reachable from the plan's tasks
- [ ] `nyquist_compliant: manual-uat` set in frontmatter

**Approval:** pending — set to `approved 2026-05-20` once Plan 12-04 lands the scaffold and the plan-checker passes the manual-UAT acceptance for Plans 12-01..03.
