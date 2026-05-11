---
phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
type: discussion-log
date: 2026-05-11
mode: autonomous (no AskUserQuestion — system reminder instructed to make reasonable calls without stopping)
---

# Phase 12 — Discussion Log

This phase was scoped without an interactive question/answer loop. The
user invoked `/gsd:discuss-phase 12` with a session-wide instruction to
work without stopping for clarifying questions ("make the reasonable
call and continue; they'll redirect if needed"). All decisions in
`12-CONTEXT.md` were derived from the artifacts below, not from user
turns.

## Inputs read

- `.planning/PROJECT.md` — Project North Star
- `.planning/REQUIREMENTS.md` — REQ-FW-01..04, REQ-SER-01
- `.planning/STATE.md` — current milestone state, Phase 11 complete
- `.planning/ROADMAP.md` — Phase 12 definition (binary-choice framing in title)
- `.planning/v1.0-MILESTONE-AUDIT.md` — BLOCKER-1, BLOCKER-2 detail, fix options
- `.planning/INTEGRATION-CHECK.md` — line-numbered dispatch trace
- `.planning/codebase/ARCHITECTURE.md` — overall architecture
- `.planning/phases/11-build-db-cleanup/11-CONTEXT.md` — style/format reference
- `firestarter/CLAUDE.md` — firmware dispatch architecture
- `firestarter_app/CLAUDE.md` — Python pipeline
- `firestarter/src/proms/memory.cpp` — current `configure_memory` dispatch
- `firestarter_app/firestarter/database.py` (lines 343-510) — `_map_data`, `convert_to_programmer`
- `firestarter_app/tools/build_db.py` (lines 80-235) — chip emission

## Gray areas considered

### G1 — Fix at C++ side, Python side, or both?

Phase title presented as either/or. The architecturally pure answer
(per PROJECT.md "What Must Be TRUE" #3 and `firestarter/CLAUDE.md`'s
already-documented dispatch table) is C++ side. But the Python
`_map_data` substring branch is independently broken — it produces a
`mem_type` that is wrong for half the DB even after the C++ fix lands.
Reasonable call: **both** — C++ as the architecturally-aligned primary
fix; Python as defense-in-depth that keeps the wire-protocol field
consistent with reality.

Recorded as **D1**.

### G2 — Include BLOCKER-2 (SRAM mis-routing)?

Phase title explicitly enumerates SRAM protocols (0x0E/0x27/0x28/0x29).
The audit flags this as BLOCKER-2 (hardware-stress hazard — VPP
regulator on 5V parts). Reasonable call: **include**. Adds one switch
case in `configure_memory` and one detection rule in `build_db.py`.

Recorded as **D4**.

### G3 — Include WARNING-5 (AT28C256 algo=0x07 override)?

Upstream minipro tags AT28C256 with `0x07` (EPROM_STD), so even after
Phase 12 it will route to `configure_eprom` and assert 12V VPP on a 5V
EEPROM. Fixing requires a per-chip override table — a distinct
mechanism and design question. Reasonable call: **defer**. Recorded
as out-of-scope and listed in Deferred Ideas.

Recorded as **D5**.

### G4 — Protocol 0x35 (FLASH_EEPROM_LIKE) handling?

`0x35` is in `KNOWN_PROTOCOLS` and `firestarter/CLAUDE.md` says it
dispatches to `flash_type_4`. The audit table did not separately
enumerate 0x35 chips (may be zero in current DB). Reasonable call:
**include** the dispatch case anyway — cost is one switch arm and
prevents a future regression if upstream adds 0x35 chips.

Recorded as **D6**.

### G5 — Verification without hardware?

No hardware available in this dev environment. The audit treats
BLOCKER-1 as a wiring problem (it is) — wiring can be verified
statically. Reasonable call: **four-tier static verification** —
JSON-output spot-checks, firmware build, firmware unit test for
dispatch, and a full-DB regression scan asserting every chip has a
valid dispatch path. Hardware verification deferred to a follow-up
phase.

Recorded as **D7**.

### G6 — Dispatch order detail

The new protocol-prefix cases must precede the legacy `mem_type` chain
(so an EPROM with `protocol=0x07` and accidentally `mem_type=2` still
reaches `configure_eprom`). The legacy `mem_type` chain is preserved
as a fallback for `protocol == 0` (unknown protocol / hand-crafted
host JSON). Reasonable call: keep mem_type fallback for backward
compat; new dispatch is documented in D2 step list 1-11.

Recorded as **D2**.

### G7 — Source of truth for the algorithm→mem_type table

The table needs to live somewhere. Options: hardcoded in `_map_data`,
module-level constant in `database.py`, shared with `build_db.py`, or
in `constants.py`. Reasonable call: **module-level constant in
`database.py`** — keeps it close to the dispatch logic, single source
of truth, no premature abstraction.

Recorded inline in **D3**.

## Items left to the researcher / planner

These came up but were not locked in CONTEXT.md because researcher /
planner should answer them with code investigation:

- **Protocol 0x39** is in `KNOWN_PROTOCOLS` (`build_db.py:89`) but
  is not enumerated in the firmware CLAUDE.md dispatch table or in the
  audit BLOCKER-1 table. What's its intended handler? Researcher
  should determine before the table in D3 is finalized.
- **Number of 0x05 and 0x35 chips in the current regenerated DB.** If
  zero, the dispatch cases are forward-compat only. If non-zero, they
  unlock more chips.
- **`flash_type_4.cpp` handler coverage.** Does it actually implement
  the algorithm correctly for the chips that will reach it once
  dispatch is wired? Researcher: confirm by reading the handler.
- **Existing `pio test` harness shape.** D7's dispatch unit test
  proposal assumes a way to mock `firestarter_handle_t` and inspect
  the resulting function-pointer assignment. Researcher: confirm the
  test harness supports this, or propose an alternative.

## Scope-creep redirects

None. The decisions in CONTEXT.md stayed inside the phase title's
explicit scope (BLOCKER-1 protocol set + SRAM protocols). WARNING-5
was actively de-scoped (D5).

## Deferred to roadmap backlog

Listed in CONTEXT.md "Deferred ideas" section:

- AT28C256 algorithm override mechanism (WARNING-5)
- Intel-flash VPP ADC check (WARNING-1)
- EEPROM_POLL chip-ID validation (WARNING-2)
- Wire JSON key rename `vpp` → `vpp_mv` (WARNING-3)
- VERIFICATION.md backfill for Phases 01-10
- Hardware verification of Phase 12 fix
- Dropping `mem_type` from wire protocol entirely

## Confidence

High on the "what" (the bug is precisely documented in the integration
check and audit) and the "where" (line numbers identified). Medium on
the unit-test approach (D7 item 3) — harness shape to be confirmed by
researcher. Medium on the 0x39 handler — to be researched.

If the user wants a different fix layer split (C++-only or
Python-only), or wants WARNING-5 folded in, this CONTEXT.md should be
revisited before `/gsd:plan-phase 12` runs.
