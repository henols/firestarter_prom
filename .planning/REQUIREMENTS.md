# Requirements: v1.31 — 27C Programming-Algorithm Fidelity (gh#15)

**Defined:** 2026-08-08
**Core Value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single
authoritative dispatch key end to end. v1.31 makes that key drive *programming behaviour*, not just
handler selection, while keeping the pulse width itself a database datum rather than a protocol
constant.

**Source:** [gh#15](https://github.com/henols/firestarter_prom/issues/15) **as corrected** by the
`/gsd-explore` pass of 2026-08-08 (`.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md`,
commit `c60543c5`), retiring ROADMAP Backlog **999.22** (queued as the `v1.27` slot).

---

## Decisions taken at scoping (2026-08-08)

| ID | Decision | Rationale |
|---|---|---|
| **D-01** | **Parameter table over three state machines.** Protocol owns *shape*; the database owns the *pulse*. | Inverts gh#15's "each protocol must own its timing constants". The shipped DB disagrees with all three of gh#15's constants, and minipro ships `protocol_id` and `pulse_delay` as two orthogonal wire fields. |
| **D-02** | **`0x0B` loops pulse→verify with a 50 ms accumulated-energy cap per byte**, no overpulse. | The one-shot-vs-looped question is not answerable from source — minipro never runs the algorithm. `100 × 500 µs = 50 ms` is exactly the classic 2716 total programming time, so both readings are satisfied. |
| **D-03** | **gh#15's corrections are posted early**, before implementation phases land. | Stops anyone implementing `50000 us`. Follows the v1.30 CLOSE-06 pattern: drafted → frozen → operator-approved → posted only on explicit authorization. |
| **D-04** | **`write --pulse-us N` ships**, bounded 1..65535. | C2 establishes the pulse is data; minipro exposes the same override. Directly needed for this milestone's own bench work on a marginal AM27C020. Overrides the value the host already sends — **no new wire field**. |
| **D-05** | **Max-pulse failure hard-fails the block**, reporting the failing address and its pulse count. | Datasheet behaviour — the algorithms fail hard at cap. Fastest failure, shortest HV exposure, and the pulse count is a diagnostic today's code cannot produce. |
| **D-06** | **Golden traces: freeze old, author new, diff deliberately.** | A blanket `--snapshot-update` could mask an unrelated regression behind a legitimate cadence shift. Every changed strobe must be attributable to a named decision. |
| **D-07** | **No `support_status` change in this milestone.** | Same posture as v1.22/v1.23. A timing fix alone does not graduate a chip; graduation is a separate evidence-gated decision. Keeps the claim gate's job simple. |
| **D-08** | **Bench coverage is asymmetric by inventory.** `0x07` required; `0x08`/`0x0B` opportunistic, skipped-with-reason. | Operator inventory, 2026-08-08. Never rubber-stamped. |

## Evidence ceiling — fixed before any code moves

The ~**6.25 V program-VCC** all four vendor algorithms assume for threshold margin is **unreachable on
this shield** — the RURP has no VCC-raise path. This milestone buys *timing / pulse-count / verify*
fidelity and **not** silicon-margin fidelity. It is hardware-bound, best-effort, the same shape as
prior hardware-bound graduations. **gh#15 omits this entirely**, so its acceptance criteria imply a
fidelity unreachable on this hardware and are amended by CLOSE-04.

This change is **not behavior-preserving**: it changes *how* bytes get programmed. Golden traces and
bench-verified write results encoding today's pulse cadence will legitimately shift. Re-baselining is
expected work, not a regression.

---

## v1 Requirements

### Preconditions & Baseline

- [ ] **PREP-01**: `firestarter_app`'s `gsd/v1.30-sdp-surface-retirement` is merged into `origin/beta`
      and the merge is verified (`git merge-base --is-ancestor` exits 0) before any v1.31 host work
      forks — v1.30 is recorded as shipped but its PR was staged and never opened.
- [ ] **PREP-02**: Milestone branches exist in all three repos off their decided bases — firmware off
      `beta` @ `3085084`, app off the updated `beta`, meta off the v1.30 tip — each verified by naming
      the base commit, not assumed.
- [ ] **PREP-03**: A pre-change baseline is committed **before** any `eprom.cpp` edit: the existing
      golden register traces frozen as a historical artifact, per-target flash/RAM usage, and full
      native + host suite counts.
- [ ] **PREP-04**: The live per-protocol `pulse_duration` distribution is re-derived from the shipped
      `chip_database.json` and committed as C2's evidence — measured in this milestone, not restated
      from the seed.

### gh#15 Correction (outward)

- [ ] **ISSUE-01**: A gh#15 comment states C1 (`0x0B` is 500 µs; `50000 us` is the ×100 BUG-2
      fingerprint Phase 57 removed), C2 (pulse width is a database datum, with the PREP-04
      distribution) and C3 (the safe delay helper is for the 75 ms overprogram pulse), each citing its
      evidence by `file:line` or commit.
- [ ] **ISSUE-02**: The same comment states the ~6.25 V program-VCC ceiling plainly and proposes the
      specific amendment to gh#15's acceptance criteria that it requires.
- [ ] **ISSUE-03**: The comment is frozen, operator-approved for wording, and posted **only** on
      explicit operator authorization — and posted before any implementation phase lands the new loop.

### Parameter Table

- [ ] **TABLE-01**: A `const` table keyed by `protocol_id` carries rows for `0x07`, `0x08` and `0x0B`
      with `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode` and `vpp_path`.
- [ ] **TABLE-02**: The table has **no pulse-width column** — program pulse width is read from
      `handle->pulse_delay` on every write path.
- [ ] **TABLE-03**: A protocol's constant pulse is consulted **only** when `handle->pulse_delay == 0`,
      and that fallback is exercised by a test rather than asserted.
- [ ] **TABLE-04**: Every value in every row is cited to a named primary datasheet, or carries an
      explicit "no datasheet basis — reasoned from X" note. No unattributed number ships.
- [ ] **TABLE-05**: No new `chip_database.json` field and no second firmware algorithm selector is
      introduced — `protocol_id` remains the sole dispatch key, verified by a gate rather than by
      inspection.

### Per-Byte Program Loop

- [ ] **LOOP-01**: Programming a byte applies **fixed-width** pulses and verifies after each one,
      counting the pulses that byte required — the width does not grow between attempts.
- [ ] **LOOP-02**: `program_mismatched_bytes()`, `verify_and_update_mask()`, the flat
      `NUMBER_OF_RETRIES` block loop and the adaptive `pulse_delay = org + org*retries/20` growth are
      removed from the EPROM write path.
- [ ] **LOOP-03**: Where `overprogram_factor > 0`, a byte that verifies at N pulses then receives an
      overprogram pulse of `3 × N × pulse`, capped at `overprogram_cap_us`.
- [ ] **LOOP-04**: `0x0B` loops pulse→verify with **accumulated program time per byte capped at
      50 ms** and applies no overprogram pulse.
- [ ] **LOOP-05**: A byte that does not verify within `max_pulses` **hard-fails the block** — the write
      aborts, every high-voltage route is disabled, and the failing address plus its pulse count are
      reported.
- [ ] **LOOP-06**: Already-matching bytes and `0xFF` bytes are skipped without emitting a program
      pulse.
- [ ] **LOOP-07**: Long delays use a safe 32-bit helper splitting millisecond and microsecond
      portions; no call path can reach `delayMicroseconds()` with a value above its 16383 µs ceiling.
- [ ] **LOOP-08**: VPE is asserted and settled **once per block**, not per byte, and survives the
      per-byte verify read — with the DIP32 `CTRL_VPP_VPE_DROP_ENABLE`/A16 exception handled
      explicitly rather than inherited by accident.

### High-Voltage Routing

- [ ] **VPP-01**: `0x07` and `0x08` use the regulator + VPE-to-VPP dropping path and `0x0B` the direct
      legacy path, selected by the table's `vpp_path` column.
- [ ] **VPP-02**: **Every** exit from the write path — success, verify failure, max-pulse failure,
      error return — disables every active high-voltage route.
- [ ] **VPP-03**: `eprom_check_vpp()` and all write and error paths share one set of routing masks
      rather than duplicating them.
- [ ] **VPP-04**: The firmware over-voltage refusal is unchanged and still blocks, re-verified against
      the existing gate rather than assumed intact.

### Host

- [ ] **HOST-01**: A write whose block exceeds the previous 10 s `DEFAULT_RESPONSE_TIMEOUT` completes
      without a serial timeout.
- [ ] **HOST-02**: The user sees progress during a long write rather than a silent stall.
- [ ] **HOST-03**: A byte that fails at `max_pulses` surfaces as a **program failure naming the
      address**, not as a transport error — the diagnostic survives the failure.
- [ ] **HOST-04**: `firestarter write --pulse-us N` overrides the database pulse for that run, using
      the existing wire field — no new command or wire field is added.
- [ ] **HOST-05**: `--pulse-us` outside `1..65535` is refused with an actionable message **before any
      serial byte is sent**.

### Tests & Build

- [ ] **TEST-01**: Native tests prove `0x07`, `0x08` and `0x0B` each resolve to their own table row.
- [ ] **TEST-02**: Native tests prove fixed-width pulse/verify per byte and that the width does not
      escalate between attempts.
- [ ] **TEST-03**: Native tests prove the overprogram duration derives from the successful byte's
      pulse count and honours `overprogram_cap_us`.
- [ ] **TEST-04**: Native tests prove max-pulse failure aborts the block, reports the address, and
      disables every high-voltage route.
- [ ] **TEST-05**: Native tests prove the `0xFF`/already-matching skips and the
      `pulse_delay == 0` fallback.
- [ ] **TEST-06**: The pre-change golden traces are frozen, new traces are authored for the new
      cadence, and the diff between them is reviewed with **every changed strobe attributable to a
      named decision** — no blanket snapshot update.
- [ ] **TEST-07**: `uno`, `uno328pb`, `leonardo` and `native` all build and pass; the host suite and
      CI-scoped ruff/mypy are clean; dual-repo constants parity holds.
- [ ] **TEST-08**: Per-target flash and RAM delta is measured against the PREP-03 baseline and
      recorded — the Leonardo ceiling is watched, not discovered at the end.

### Bench Validation

- [ ] **BENCH-01**: `0x07` is bench-validated on W27C512 or TMS27C512 via a full write→read→verify on
      Leonardo, recorded with per-run evidence.
- [ ] **BENCH-02**: `0x08` (AM27C020) and `0x0B` (M2716/M2732) are validated **if the parts are
      available**; otherwise each is recorded **skipped-with-reason naming the missing part** — never
      rubber-stamped, never inferred from the `0x07` result.
- [ ] **BENCH-03**: No chip's `support_status` changes in this milestone (D-07).

### Close

- [ ] **CLOSE-01**: A committed claim gate forbids unqualified "datasheet-conformant" /
      "datasheet-correct" / "algorithm-accurate" across all closing artifacts, is **armed against the
      real files**, and has been **seen to fail** on a planted violation.
- [ ] **CLOSE-02**: An honesty ledger pairs every permitted claim with its explicit non-claim, leading
      with the 6.25 V ceiling and the asymmetric bench coverage.
- [ ] **CLOSE-03**: Firmware and host documentation describe the new per-byte algorithm, the parameter
      table, the database-supplied pulse, `--pulse-us`, and the 6.25 V accepted debt.
- [ ] **CLOSE-04**: gh#15's acceptance criteria are reconciled **item by item** — each marked met,
      met-as-corrected (naming the correction), or not-reachable-on-this-hardware (naming the reason).
- [ ] **CLOSE-05**: Release notes describe the programming-behaviour change and the `--pulse-us`
      addition in terms a stranger can act on.

---

## Future Requirements

Deferred. Tracked but not in this roadmap.

| ID | Requirement | Why deferred |
|---|---|---|
| **FUT-PRESTO** | True PRESTO margin verification for `0x08` | Requires a verify mode the RURP may not be able to expose; documented as not-yet-implemented per gh#15's own allowance. |
| **FUT-VCC** | 6.25 V program-VCC rail | Hardware, not firmware. No VCC-raise path exists on any shield revision. Accepted debt, recorded not attempted. |
| **FUT-MAXPULSE** | Per-part `max_pulses` from primary datasheets | `research/questions.md` leaves this open: Intel's 25 is confirmed but Microchip specifies 10. Rows ship with cited defaults; per-part refinement needs a datasheet sweep. |
| **FUT-OVERPROG-MAP** | Which specific parts need the 3× over-program | The over-program path is correct only for older Intel "Intelligent" parts, not Quick-Pulse/Flashrite/PRESTO. Gated per row here; a per-part map needs the same datasheet sweep. |

## Out of Scope

| Feature | Reason |
|---|---|
| New `chip_database.json` algorithm field | gh#15 is explicit and correct: `protocol_id` stays the single source of truth. The table is keyed by it, not a substitute. |
| Second firmware algorithm selector | Same — one dispatch key, enforced by TABLE-05. |
| A VCC-raise path | Hardware. See FUT-VCC. |
| Changes to erase, blank-check, chip-ID, bus remapping, VPP validation | Unchanged except where required for safe shared cleanup. |
| `support_status` graduations | D-07. Separate evidence-gated decision. |
| Reporting all mismatched ranges on verify | Backlog **999.8** (gh#1). D-05 hard-fails at the first byte; the broader verify-reporting change stays its own item. |
| The `0x0B` one-shot question settled empirically | D-02 settles it by design via the energy cap. A bench measurement would refine the row, not gate the milestone. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PREP-01 | Phase 138 | Pending |
| PREP-02 | Phase 138 | Pending |
| PREP-03 | Phase 138 | Pending |
| PREP-04 | Phase 138 | Pending |
| ISSUE-01 | Phase 139 | Pending |
| ISSUE-02 | Phase 139 | Pending |
| ISSUE-03 | Phase 139 | Pending |
| TABLE-01 | Phase 140 | Pending |
| TABLE-02 | Phase 140 | Pending |
| TABLE-03 | Phase 140 | Pending |
| TABLE-04 | Phase 140 | Pending |
| TABLE-05 | Phase 140 | Pending |
| LOOP-01 | Phase 141 | Pending |
| LOOP-02 | Phase 141 | Pending |
| LOOP-03 | Phase 141 | Pending |
| LOOP-04 | Phase 141 | Pending |
| LOOP-05 | Phase 141 | Pending |
| LOOP-06 | Phase 141 | Pending |
| LOOP-07 | Phase 141 | Pending |
| LOOP-08 | Phase 141 | Pending |
| VPP-01 | Phase 142 | Pending |
| VPP-02 | Phase 142 | Pending |
| VPP-03 | Phase 142 | Pending |
| VPP-04 | Phase 142 | Pending |
| HOST-01 | Phase 143 | Pending |
| HOST-02 | Phase 143 | Pending |
| HOST-03 | Phase 143 | Pending |
| HOST-04 | Phase 143 | Pending |
| HOST-05 | Phase 143 | Pending |
| TEST-01 | Phase 144 | Pending |
| TEST-02 | Phase 144 | Pending |
| TEST-03 | Phase 144 | Pending |
| TEST-04 | Phase 144 | Pending |
| TEST-05 | Phase 144 | Pending |
| TEST-06 | Phase 144 | Pending |
| TEST-07 | Phase 144 | Pending |
| TEST-08 | Phase 144 | Pending |
| BENCH-01 | Phase 145 | Pending |
| BENCH-02 | Phase 145 | Pending |
| BENCH-03 | Phase 145 | Pending |
| CLOSE-01 | Phase 146 | Pending |
| CLOSE-02 | Phase 146 | Pending |
| CLOSE-03 | Phase 146 | Pending |
| CLOSE-04 | Phase 146 | Pending |
| CLOSE-05 | Phase 146 | Pending |

**Coverage:**
- v1 requirements: 45 total
- Mapped to phases: 45
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-08*
*Last updated: 2026-08-08 after roadmap creation (Phases 138-146, 45/45 mapped)*
