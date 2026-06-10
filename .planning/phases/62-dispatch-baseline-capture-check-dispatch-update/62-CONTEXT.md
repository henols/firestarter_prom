# Phase 62: Dispatch Baseline Capture + check_dispatch Update - Context

**Gathered:** 2026-06-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Capture a committed, verifiable snapshot of **current** dispatch behavior before
any v1.12 code changes land, and update `firestarter_app/tools/check_dispatch.py`
so it **models the Phase-64 fail-closed firmware dispatch** — making the regression
gate accurate for every subsequent phase (63–68).

**In scope:**
- A committed reference snapshot of every DB chip's resolved handler (the dispatch
  baseline), plus the representative `protocol==0`/legacy and unknown-protocol cases.
- `check_dispatch.py` `dispatch()` gains explicit `0x35`/`0x39` → `configure_flash4`
  cases (no longer relying on the coincidental `mem_type` fallback) **and** a
  `protocol != 0` → `not_implemented` arm replacing the stale fallback for non-zero
  unrecognized protocols.
- A `not_implemented` list + FAIL assertion in the scan loop; the gate must exit
  with **0 not-implemented chips (PASS)** against the current 743-chip DB.
- All pre-existing `check_dispatch.py` checks stay green (GATE-03 VPP-safety guards,
  SRAM-in-EPROM guard, wire round-trip 743/743).

**Out of scope (later phases / not this phase):**
- Any firmware (`firestarter/`) source or test change — deferred to Phase 64 (DISP/TEST).
- The `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` catalog constant — Phase 63 (WIRE-01).
- Firmware `configure_not_implemented()` + fail-closed `configure_memory` — Phase 64.
- VPP correction / `vpp_mv` regression surface — Phase 66 owns this.

</domain>

<decisions>
## Implementation Decisions

### Baseline artifact form (GATE-01)
- **D-01:** Capture the dispatch baseline as a **one-time committed reference snapshot**
  (human-readable artifact listing every DB chip's resolved handler), **not** a
  regenerate-and-diff golden gate. The *live* regression pin is the existing firmware
  Unity test (already committed) **plus** the new `not_implemented` FAIL assertion in
  `check_dispatch.py` (0 not-implemented chips). Rationale: this phase is foundational
  and the dispatch logic is small/stable; a full Phase-59-style diff gate is more
  machinery than the dispatch surface warrants. (Considered and rejected: golden
  snapshot + drift-diff gate.)

### Firmware sub-repo touch (GATE-01 / branching)
- **D-02:** Phase 62 is **host-only** — it touches **only the `firestarter_app`
  sub-repo** (`tools/check_dispatch.py` + the committed snapshot artifact). The
  existing firmware native Unity suite
  `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` already pins
  the GATE-01 representative cases — `test_protocol_zero_with_mem_type_eprom_dispatches_eprom`
  (`protocol=0, mem_type=1` → not-ERROR, i.e. legacy fallback intact) and
  `test_unknown_protocol_with_unknown_mem_type_errors` (`protocol=0, mem_type=99` →
  ERROR). It is accepted **as-is** as the GATE-01 firmware baseline (the "or equivalent
  committed artifact" clause). **Do NOT fork the firmware v1.12 branch in Phase 62** —
  defer the firmware fork (off `beta`) to Phase 63/64 where firmware actually changes.
  (Considered and rejected: strengthening the FW Unity test with a pointer-level
  `configure_eprom` assertion now — that work, if wanted, belongs to Phase 64 TEST-01
  where firmware is already open.)
- **Branch action required this phase:** the app sub-repo is currently on
  `v1.11-infoic-decode-correctness`; fork/create the **`v1.12-protocol-dispatch-hardening`**
  branch in `firestarter_app` (off `beta`) before committing Phase 62 work, per the
  branching convention.

### `not_implemented` modeling semantics (GATE-02)
- **D-03:** Mirror the Phase-64 firmware dispatch **exactly — two distinct failure
  buckets**:
  - `protocol == 0` + unrecognized `mem_type` → keep the existing **`"ERROR"`** bucket
    (the unsupported-mem_type path; firmware step 11 → `MSG_ERR_MEM_TYPE_UNSUPPORTED`).
  - `protocol != 0` + unrecognized protocol → the **new `"not_implemented"`** bucket
    (firmware Phase-64 fail-closed arm → `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, 0xBB).
  Keep them separate so the gate's diagnostics stay aligned with firmware's two
  response codes. (Considered and rejected: collapsing both into one bucket.)

### Baseline snapshot scope (GATE-01)
- **D-04:** The snapshot records the **dispatch triple per chip**:
  `part → { algorithm, mem_type, resolved_handler }` — inputs + output that fully
  determine dispatch, self-documenting why each chip routes where. **Exclude `vpp_mv`
  / wire fields** — VPP regression is Phase 66's surface, and `check_dispatch.py`
  already asserts wire `vpp_mv` presence per chip. (Considered and rejected: including
  `vpp_mv`/wire fields, which would conflate the dispatch baseline with the VPP
  baseline and trip on Phase 66's intentional NMOS VPP corrections.)

### Claude's Discretion
- Exact snapshot file format/location and filename (within `firestarter_app`), and the
  precise dispatch-order arrangement of the explicit `0x35`/`0x39` cases vs. the
  `protocol != 0` arm in `check_dispatch.py::dispatch()` — planner/researcher decide,
  constrained by: mirror `memory.cpp::configure_memory` order line-for-line, and the
  `protocol != 0 → not_implemented` arm must sit **after** all explicit protocol cases
  and **before** the `protocol == 0` `mem_type` fallback.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Dispatch source-of-truth (mirror exactly)
- `firestarter/src/proms/memory.cpp` — `configure_memory()` is the dispatch
  source-of-truth; `check_dispatch.py::dispatch()` must mirror its order line-for-line.
- `firestarter/CLAUDE.md` § "Protocol Dispatch" — the canonical 11-step dispatch order
  table + the `0x05/0x35/0x39 → configure_flash4` grouping (0x39 future-proofed, 0 chips).
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — existing
  native Unity baseline; `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` +
  `test_unknown_protocol_with_unknown_mem_type_errors` are the accepted GATE-01 pins.

### Gate + DB pipeline
- `firestarter_app/tools/check_dispatch.py` — the file this phase modifies; existing
  guards to keep green: GATE-03 (`no_vpp_pin` structural + `Flash/EEPROM` type-string +
  DIP28_2764 WARNING-5), SRAM-in-EPROM (BLOCKER-2), WIRE-02 wire round-trip.
- `firestarter_app/tools/build_db.py` — confirms `0x35` (IC2_ALG_ITE, no DIP memory)
  and `0x39` (phantom, no IC2_ALG constant) are **removed** from `KNOWN_PROTOCOLS`
  (lines ~44-45, ~108-111) → no DB chip uses a gap protocol → gate PASSes with 0
  not-implemented.
- `firestarter_app/CLAUDE.md` § "Database Pipeline" — WARNING-5 / GATE-03 guard rationale.

### Milestone planning
- `.planning/ROADMAP.md` § "Phase 62" — goal + 4 success criteria.
- `.planning/REQUIREMENTS.md` — GATE-01, GATE-02 (+ downstream WIRE-01/02, DISP-*, TEST-*).

### Precedent (how prior phases captured/gated baselines)
- `.planning/phases/59-correctness-gate-per-chip-diff-sram-audit/` — Phase 59
  regenerate-and-diff per-chip gate (the *richer* pattern we deliberately did **not**
  adopt for the dispatch baseline; see D-01).
- `.planning/phases/56-snapshot-field-dictionary-corrected-docs/` — Phase 56 pinned-
  snapshot (GATE-01 of v1.11) precedent.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `check_dispatch.py::dispatch()` — already has explicit cases for 0x10/0x0D/0x06/0x05/
  0x07-08-0B/0x0E-27-28-29 and a trailing `mem_type` fallback dict. The change is
  surgical: add `0x35`/`0x39` to the `0x05` arm (→ `configure_flash4`); insert the
  `protocol != 0 → "not_implemented"` arm before the `mem_type` fallback.
- `check_dispatch.py::main()` scan loop — already accumulates per-bucket failure lists
  (`errors`, `sram_in_eprom`, …) with a uniform print + `sys.exit(1)` pattern; add a
  `not_implemented` list following the same shape.
- `test_configure_memory.cpp` — already provides the GATE-01 representative-case pins;
  no new firmware test needed this phase (D-02).

### Established Patterns
- `dispatch()` mirrors `memory.cpp::configure_memory` line-for-line (documented in both
  CLAUDE.md files) — the mirror discipline is the core invariant to preserve.
- Per-chip scan + per-bucket FAIL list + summary PASS line is the gate's idiom.
- `build_db.py` `KNOWN_PROTOCOLS` excludes 0x35/0x39 → the new not_implemented FAIL must
  PASS (0 chips) on today's DB, by construction.

### Integration Points
- `check_dispatch.py` is the regression gate invoked by later phases (63–68) and CI;
  its `not_implemented` arm is the host-side mirror of the Phase-64 firmware guard.
- The committed snapshot artifact lives in `firestarter_app` (host-only this phase).

</code_context>

<specifics>
## Specific Ideas

- The new gate FAIL message for the `not_implemented` bucket should name the offending
  `proto` so a future gap-protocol chip is immediately identifiable (same style as the
  existing `f"{mfg}/{part} proto=0x{proto:02X} …"` lines).
- Snapshot is "dispatch triple" (`algorithm, mem_type, handler`) per D-04 — keep it
  diff-friendly/stable-ordered so a human can eyeball it across milestones even though
  it is not a hard diff gate.

</specifics>

<deferred>
## Deferred Ideas

- **Strengthen firmware Unity dispatch test with pointer-level `configure_eprom`
  assertion** (rather than the current non-ERROR assertion) → Phase 64 (TEST-01), where
  the firmware is already open and `configure_not_implemented()` lands.
- **Golden-snapshot regenerate-and-diff dispatch gate** (Phase-59 style) → not adopted;
  revisit only if dispatch logic grows enough to warrant it.
- **`vpp_mv` / wire-field regression baseline** → Phase 66 (DB VPP correction) owns this.

None of the above are pending todos. The two open todos (avrdude MCU-detection fallback;
COBS frame-level deadline WR-01) were reviewed and are unrelated to Phase 62 scope.

</deferred>

---

*Phase: 62-dispatch-baseline-capture-check-dispatch-update*
*Context gathered: 2026-06-10*
